#!/usr/bin/env python3
"""
Cognitive Load Analyzer for Long-Form Blog Content

Measures concepts-per-section to identify overloaded H2 sections that exceed
the working-memory ceiling (~4 items, Cowan 2001). Companion to analyze_blog.py.

Adapted from cognitive-load theory (Sweller 1988) and the impeccable plugin's
UI cognitive-load model (Paul Bakaus, Apache 2.0, github.com/pbakaus/impeccable).

Usage:
    python3 cognitive_load.py <file>                    # Default JSON output
    python3 cognitive_load.py <file> --format markdown  # Markdown heatmap
    python3 cognitive_load.py <file> --jargon <path>    # Custom jargon list

Signals measured per H2 section:
    - new_entity_density:    Capitalized multi-word phrases not seen in prior sections, per 100 words
    - numeric_claim_density: Numbers (percentages, counts, currencies, dates), per 100 words
    - jargon_introduction:   Domain terms from the jargon list not yet defined
    - forward_reference:     Phrases like "as we will see," "discussed below"
    - avg_clause_depth:      Subordinate-clause markers per sentence (avg)
    - load_score:            Composite 0-100; higher = more loaded

Thresholds (per cognitive-load.md):
    new_entity_density:   1-3 healthy, 4-6 borderline, 7+ overloaded
    numeric_claim_density: 1-3 healthy, 4-5 borderline, 6+ overloaded
    jargon_introduction:  0-1 healthy, 2-3 borderline, 4+ overloaded
    forward_reference:    0 healthy, 1 borderline, 2+ overloaded
    avg_clause_depth:     <1.5 healthy, 1.5-2.5 borderline, >2.5 overloaded
"""

from __future__ import annotations

import argparse
import errno
import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Default jargon list (extendable via --jargon)
# ---------------------------------------------------------------------------

DEFAULT_JARGON = {
    "schema markup", "structured data", "e-e-a-t", "geo", "aeo",
    "burstiness", "ttr", "type-token ratio", "core web vitals", "lcp",
    "cls", "inp", "json-ld", "hreflang", "canonical", "robots.txt",
    "indexability", "crawlability", "passage-level citability", "answer-first",
    "flow framework", "evidence triple", "tier 1", "tier 2", "tier 3",
    "intrinsic load", "extraneous load", "germane load",
}

FORWARD_REFERENCE_PATTERNS = [
    r"\bas (we|i) (will|shall) (see|discuss|cover|explore)\b",
    r"\b(discussed|covered|explained|detailed) (below|later|further)\b",
    r"\blater in this (post|article|guide|section)\b",
    r"\bwe('|'')ll (see|cover|discuss|return to)\b",
    r"\bmore on this (later|below|in a moment)\b",
    r"\bcoming up\b",
]

# Clause-depth markers split into two weighted pools (FIND-013 + v1.8.3
# corrections). Three corrections vs v1.8.2:
#   CODE-AUDIT-401: previously counted `(` AND `)` at 0.3 each, double-charging
#     each parenthetical pair (0.6 per pair). Now count only `(` (single
#     opener marks the boundary).
#   CODE-AUDIT-402: previously used " word " substring matching, which missed
#     sentence-start fronted clauses ("While X happens, Y...") because there
#     is no leading space before "While". Now use word-boundary regex.
PUNCTUATION_MARKERS = [",", ";", "("]  # `)` removed: avoid double-count
SUBORDINATOR_WORDS = [
    "which", "that", "who", "whose",
    "although", "though", "unless", "whereas",
    "because", "since", "while", "when", "where",
    "if", "until", "before", "after",
]
# Match each subordinator as a whole word anywhere in the sentence, including
# sentence start ("While X happens..." and "... happens while X" both count).
_SUBORDINATOR_RE = re.compile(
    r"\b(?:" + "|".join(SUBORDINATOR_WORDS) + r")\b",
    re.IGNORECASE,
)
PUNCTUATION_WEIGHT = 0.3
SUBORDINATOR_WEIGHT = 1.0

# Currency, percentage, integer/decimal, year-like, ordinal numeric patterns
NUMERIC_RE = re.compile(
    r"\$\d[\d,]*(?:\.\d+)?[bmkBMK]?|"  # currency
    r"\d+(?:\.\d+)?\s*%|"               # percentage
    r"\b(?:19|20|21)\d{2}\b|"           # year (1900-2199)
    r"\b\d+(?:\.\d+)?(?:st|nd|rd|th)?\b"
)

# Entity detector: matches Title-Case multi-word phrases OR all-caps acronyms.
# Adding the acronym branch closes the FIND-014 false-negative where tech-blog
# posts (the target corpus) were under-counted because phrases like "NASA",
# "IBM", "GPT-4", "JSON", "REST", "API", "LLM" never matched.
ENTITY_RE = re.compile(
    r"\b(?:"
    r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}"        # Title Case (1-4 words)
    r"|[A-Z]{2,}(?:[-\d][A-Z0-9]+)*"             # all-caps acronyms (NASA, GPT-4)
    r")\b"
)

H2_RE = re.compile(r"^(##\s+.+)$", re.MULTILINE)


def strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter if present."""
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    return text[end + 4 :]


def split_sections(text: str) -> list[tuple[str, str]]:
    """Split markdown into [(heading, body), ...] by H2."""
    text = strip_frontmatter(text)
    parts = H2_RE.split(text)
    if len(parts) < 2:
        return [("(no H2 sections)", text)]
    intro = parts[0].strip()
    sections: list[tuple[str, str]] = []
    if intro:
        sections.append(("(intro)", intro))
    i = 1
    while i < len(parts):
        heading = parts[i].lstrip("#").strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        sections.append((heading, body.strip()))
        i += 2
    return sections


def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def count_sentences(text: str) -> int:
    sentences = re.split(r"[.!?]+\s+", text)
    return max(1, len([s for s in sentences if s.strip()]))


_COMMON_OPENERS = frozenset({
    # Pronouns and demonstratives
    "The", "This", "That", "These", "Those", "It", "We", "You", "They",
    "I", "He", "She", "Me", "Him", "Her", "Us", "Them",
    # Subordinators / interrogatives
    "If", "When", "While", "Where", "How", "What", "Why", "Who",
    "Until", "Unless", "Although", "Though", "Because", "Since",
    # Ordinals and adverbs
    "First", "Second", "Third", "Next", "Then", "Now", "Here", "There",
    "Most", "Some", "All", "Every", "Each", "Both", "Many", "Few",
    "Always", "Never", "Often", "Sometimes",
    # Conjunctions and prepositions
    "And", "Or", "But", "For", "Yet", "So", "With", "Without",
    "From", "To", "By", "At", "In", "On", "Over", "Under",
    "Through", "Across", "Around", "Between", "Among",
    # Modals and auxiliaries used at sentence start
    "Can", "Could", "Should", "Would", "Will", "Shall", "May", "Might", "Must",
    # Months
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
    "Jan", "Feb", "Mar", "Apr", "Jun", "Jul", "Aug", "Sep", "Sept", "Oct", "Nov", "Dec",
    # Weekdays
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun",
    # Common imperative openers in how-to prose
    "Let", "Take", "Use", "Make", "Run", "Try", "See", "Note", "Add",
    "Consider", "Imagine", "Suppose",
})

# All-caps tokens that are common-English words, not entities.
_ALLCAPS_NOISE = frozenset({"US", "UK", "OK", "I", "A", "USA"})


def find_entities(text: str) -> set[str]:
    """Title-Case multi-word phrases AND all-caps acronyms. Filters
    obvious non-entities (sentence-leading single-word openers like
    "May" / "From" / "Let" used as pronouns/conjunctions/imperatives,
    common all-caps words like 'US' / 'OK').

    The v1.8.3 correction (CODE-AUDIT-403): only filter when the WHOLE
    phrase is a single token matching an opener. Previously, the filter
    dropped multi-word entities like "May Tech Co" because the first
    token "May" was in _COMMON_OPENERS; now multi-word phrases survive
    the filter (they are likely real entities, not sentence openers).
    """
    found = ENTITY_RE.findall(text)
    out: set[str] = set()
    for e in found:
        if len(e) <= 2:
            continue
        tokens = e.split()
        # Filter single-token openers ("May arrived early." -> drop "May").
        # Keep multi-token phrases ("May Tech Co launched" -> keep).
        if len(tokens) == 1 and tokens[0] in _COMMON_OPENERS:
            continue
        if e.isupper() and e in _ALLCAPS_NOISE:
            continue
        out.add(e)
    return out


def count_numeric_claims(text: str) -> int:
    return len(NUMERIC_RE.findall(text))


def count_jargon_introductions(text: str, jargon: set[str], seen: set[str]) -> int:
    """Count jargon terms appearing for the first time in this section."""
    lower = text.lower()
    introductions = 0
    for term in jargon:
        pattern = r"(?<![a-z0-9])" + re.escape(term.lower()) + r"(?![a-z0-9])"
        if re.search(pattern, lower) and term not in seen:
            introductions += 1
            seen.add(term)
    return introductions


def count_forward_references(text: str) -> int:
    lower = text.lower()
    total = 0
    for pattern in FORWARD_REFERENCE_PATTERNS:
        total += len(re.findall(pattern, lower))
    return total


def avg_clause_depth(text: str) -> float:
    """Average weighted clause-marker count per sentence.

    Subordinator words (which, that, who, because, while, when, if, ...)
    score SUBORDINATOR_WEIGHT (1.0) each, matched as whole words via regex
    so sentence-start fronted clauses are detected. Punctuation boundaries
    (comma, semicolon, opening paren) score PUNCTUATION_WEIGHT (0.3) each.
    The weighting prevents enumeration commas ("red, white, and blue")
    from inflating the metric (FIND-013, v1.8.3 corrections).
    """
    sentences = re.split(r"[.!?]+\s+", text)
    sentences = [s for s in sentences if s.strip()]
    if not sentences:
        return 0.0
    total = 0.0
    for sentence in sentences:
        for marker in PUNCTUATION_MARKERS:
            total += sentence.count(marker) * PUNCTUATION_WEIGHT
        total += len(_SUBORDINATOR_RE.findall(sentence)) * SUBORDINATOR_WEIGHT
    return round(total / len(sentences), 2)


def classify(value: float, healthy_max: float, borderline_max: float) -> str:
    if value <= healthy_max:
        return "healthy"
    if value <= borderline_max:
        return "borderline"
    return "overloaded"


def score_section(
    body: str,
    prior_entities: set[str],
    seen_jargon: set[str],
    jargon: set[str],
) -> dict[str, Any]:
    words = count_words(body)
    if words == 0:
        return {
            "words": 0, "new_entities": 0, "new_entity_density": 0.0,
            "numeric_claims": 0, "numeric_claim_density": 0.0,
            "jargon_introductions": 0, "forward_references": 0,
            "avg_clause_depth": 0.0, "load_score": 0,
            "verdict": "empty", "flags": [],
        }
    entities = find_entities(body)
    new_entities = entities - prior_entities
    prior_entities.update(new_entities)

    def per_100(n: int) -> float:
        return round(n * 100 / words, 2)

    new_entity_density = per_100(len(new_entities))
    numeric_claims = count_numeric_claims(body)
    numeric_claim_density = per_100(numeric_claims)
    jargon_intros = count_jargon_introductions(body, jargon, seen_jargon)
    forward_refs = count_forward_references(body)
    clause_depth = avg_clause_depth(body)

    signals = [
        ("entity", classify(new_entity_density, 3, 6)),
        ("numeric", classify(numeric_claim_density, 3, 5)),
        ("jargon", classify(float(jargon_intros), 1, 3)),
        ("forward_ref", classify(float(forward_refs), 0, 1)),
        ("clause_depth", classify(clause_depth, 1.5, 2.5)),
    ]
    weight = {"overloaded": 25, "borderline": 10, "healthy": 0}
    load_score = min(100, sum(weight[level] for _, level in signals))
    overloaded_signals = [name for name, level in signals if level == "overloaded"]
    if load_score >= 50 or len(overloaded_signals) >= 2:
        verdict = "overloaded"
    elif load_score >= 25:
        verdict = "borderline"
    else:
        verdict = "healthy"

    return {
        "words": words,
        "new_entities": len(new_entities),
        "new_entity_density": new_entity_density,
        "numeric_claims": numeric_claims,
        "numeric_claim_density": numeric_claim_density,
        "jargon_introductions": jargon_intros,
        "forward_references": forward_refs,
        "avg_clause_depth": clause_depth,
        "load_score": load_score,
        "verdict": verdict,
        "flags": overloaded_signals,
    }


def analyze(path: Path, jargon: set[str]) -> dict[str, Any]:
    # Use TOCTOU-resistant read instead of path.read_text() (closes the
    # check-vs-read race that the prior validation left open).
    text = _read_safely(path, MAX_INPUT_BYTES, "Input file")
    sections = split_sections(text)
    prior_entities: set[str] = set()
    seen_jargon: set[str] = set()
    results: list[dict[str, Any]] = []
    for heading, body in sections:
        scored = score_section(body, prior_entities, seen_jargon, jargon)
        scored["heading"] = heading
        results.append(scored)

    total_words = sum(r["words"] for r in results)
    overall_load = (
        round(sum(r["load_score"] * r["words"] for r in results) / total_words, 1)
        if total_words else 0
    )
    overloaded = [r for r in results if r["verdict"] == "overloaded"]
    borderline = [r for r in results if r["verdict"] == "borderline"]

    if overall_load >= 50:
        verdict = "Overloaded"
    elif overall_load >= 25:
        verdict = "Moderate"
    else:
        verdict = "Healthy"

    return {
        "file": str(path),
        "overall_load": overall_load,
        "verdict": verdict,
        "section_count": len(results),
        "overloaded_section_count": len(overloaded),
        "borderline_section_count": len(borderline),
        "sections": results,
    }


def format_markdown(report: dict[str, Any]) -> str:
    out = [
        f"## Cognitive Load Heatmap: {Path(report['file']).name}",
        "",
        f"Overall load: {report['overall_load']} / 100 ({report['verdict']})",
        "",
        "| Section (H2) | Words | Load | Entities/100 | Numerics/100 | Jargon | Forward refs | Avg clauses |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for sec in report["sections"]:
        out.append(
            f"| {sec['heading'][:60]} | {sec['words']} | {sec['load_score']} | "
            f"{sec['new_entity_density']} | {sec['numeric_claim_density']} | "
            f"{sec['jargon_introductions']} | {sec['forward_references']} | "
            f"{sec['avg_clause_depth']} |"
        )
    overloaded = [s for s in report["sections"] if s["verdict"] == "overloaded"]
    if overloaded:
        out.extend(["", "### Overloaded sections (P1)"])
        for sec in overloaded:
            flags = ", ".join(sec["flags"]) or "composite load"
            out.append(f"- **{sec['heading']}**: {flags}. Split or scaffold.")
    return "\n".join(out)


MAX_INPUT_BYTES = 10 * 1024 * 1024  # 10 MB cap on any input file (DoS guard)
MAX_JARGON_BYTES = 1 * 1024 * 1024   # 1 MB cap on jargon list


def _read_safely(path: Path, max_bytes: int, label: str) -> str:
    """Read a path with TOCTOU-resistant defenses.

    Uses os.open(O_NOFOLLOW) where available (POSIX) to atomically refuse
    symlinks AND prevent a swap between the check and the read (CWE-367).
    On Windows (no O_NOFOLLOW), falls back to is_symlink check; small TOCTOU
    window remains but symlink refusal still applies.

    Refuses: missing files, symlinks (CWE-59), non-regular files
    (FIFOs/devices/sockets), oversize inputs (DoS).
    Does NOT confine input to a base directory; the caller is responsible
    for overall path safety. Returns decoded UTF-8 string.
    Raises ValueError or FileNotFoundError on failure.
    """
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    else:
        if path.is_symlink():
            raise ValueError(
                f"{label} is a symlink; refusing to follow for safety: {path}"
            )
    try:
        fd = os.open(str(path), flags)
    except FileNotFoundError as e:
        raise ValueError(f"{label} not found: {path}") from e
    except OSError as e:
        if e.errno == errno.ELOOP:
            raise ValueError(
                f"{label} is a symlink; refusing to follow for safety: {path}"
            ) from e
        raise ValueError(f"{label} could not be opened safely: {path} ({e})") from e
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise ValueError(f"{label} is not a regular file: {path}")
        if st.st_size > max_bytes:
            raise ValueError(
                f"{label} exceeds size cap ({st.st_size} bytes > {max_bytes}): {path}"
            )
        with os.fdopen(fd, "r", encoding="utf-8") as f:
            fd = -1
            data = f.read(max_bytes + 1)
    finally:
        if fd != -1:
            try:
                os.close(fd)
            except OSError:
                pass
    if len(data.encode("utf-8")) > max_bytes:
        raise ValueError(f"{label} exceeds size cap after read ({max_bytes}): {path}")
    return data


def _validate_input_path(path: Path, max_bytes: int, label: str) -> Path:
    """Refuses symlinks (CWE-59), non-regular files, and oversize inputs (DoS).

    Does NOT confine input to a base directory; the caller is responsible
    for overall path safety. Retained for callers that only need a validated
    Path object. Prefer _read_safely() for new code (closes TOCTOU window
    via O_NOFOLLOW where available).
    """
    if not path.exists():
        raise ValueError(f"{label} not found: {path}")
    if path.is_symlink():
        raise ValueError(
            f"{label} is a symlink; refusing to follow for safety: {path}"
        )
    if not path.is_file():
        raise ValueError(f"{label} is not a regular file: {path}")
    size = path.stat().st_size
    if size > max_bytes:
        raise ValueError(
            f"{label} exceeds size cap ({size} bytes > {max_bytes}): {path}"
        )
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("file", help="Path to markdown / MDX file")
    parser.add_argument(
        "--format", choices=["json", "markdown"], default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--jargon", type=Path, default=None,
        help="Path to newline-delimited jargon list to add to defaults",
    )
    args = parser.parse_args()

    try:
        path = _validate_input_path(Path(args.file), MAX_INPUT_BYTES, "Input file")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    jargon = set(DEFAULT_JARGON)
    if args.jargon:
        try:
            jargon_text = _read_safely(
                args.jargon, MAX_JARGON_BYTES, "Jargon file"
            )
            jargon.update(
                line.strip().lower()
                for line in jargon_text.splitlines()
                if line.strip()
            )
        except ValueError as e:
            print(f"Warning: {e}; proceeding with default jargon.", file=sys.stderr)

    report = analyze(path, jargon)
    if args.format == "markdown":
        print(format_markdown(report))
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
