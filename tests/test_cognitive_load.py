"""Smoke tests for scripts/cognitive_load.py.

Covers:
1. Happy path: a markdown post with H2 sections produces a valid JSON report
   with per-section load scores and a healthy overall verdict.
2. Empty input: a file with no H2 sections still produces parseable JSON
   without crashing.
3. Overloaded path: a synthetically dense section is flagged as overloaded.

Stdlib only. No network. Subprocess invocation matches the documented CLI.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "cognitive_load.py"


def _run(post_path: Path) -> dict:
    """Invoke the CLI with --format json and return the parsed payload."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(post_path), "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"non-zero exit: stderr={result.stderr!r}"
    return json.loads(result.stdout)


def test_happy_path_low_load(tmp_path: Path) -> None:
    """A plain post with simple sections should be classified Healthy."""
    post = tmp_path / "happy.md"
    post.write_text(
        "---\ntitle: Test\n---\n\n"
        "## Why This Matters\n\n"
        "Most readers want simple explanations. We keep things short. "
        "We use plain words and one idea per paragraph.\n\n"
        "## What To Do\n\n"
        "Start with the obvious step. Watch what happens. Adjust if needed.\n",
        encoding="utf-8",
    )
    report = _run(post)
    assert report["verdict"] in {"Healthy", "Moderate"}
    assert report["section_count"] >= 2
    assert report["overall_load"] >= 0


def test_empty_post_no_crash(tmp_path: Path) -> None:
    """A post with no H2 sections must not crash and must return JSON."""
    post = tmp_path / "empty.md"
    post.write_text("Just one paragraph with no headings.\n", encoding="utf-8")
    report = _run(post)
    assert "verdict" in report
    assert "sections" in report
    assert isinstance(report["sections"], list)


def test_overloaded_section_flagged(tmp_path: Path) -> None:
    """A dense section with many entities, numerics, and jargon should be flagged."""
    post = tmp_path / "dense.md"
    body = (
        "## Methodology\n\n"
        "We tested Acme Corp, Globex Inc, Initech Systems, Umbrella Labs, "
        "Hooli Networks, Pied Piper Tech, Stark Industries, Wayne Enterprises, "
        "and 7 other firms in 2024. Adoption hit 87.3%, retention reached "
        "92.1%, churn dropped to 3.5%, NPS reached 67. Schema markup, "
        "structured data, e-e-a-t, geo, aeo, burstiness, ttr, hreflang, "
        "canonical, robots.txt, indexability all moved together, which is "
        "what we will see later when we discuss the second-order analysis, "
        "though as we will see in the next section the results vary, since "
        "while X happened also Y emerged because the underlying patterns shifted.\n"
    )
    post.write_text(body, encoding="utf-8")
    report = _run(post)
    methodology = next(
        s for s in report["sections"] if "Methodology" in s["heading"]
    )
    assert methodology["load_score"] > 0
    assert methodology["new_entities"] >= 5
    assert methodology["numeric_claims"] >= 4


# ---------------------------------------------------------------------------
# v1.8.3 algorithmic regression tests (FIND-013, FIND-014, FIND-015)
# ---------------------------------------------------------------------------


def _import_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("cognitive_load", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_enumeration_commas_do_not_inflate_clause_depth():
    """FIND-013 regression: enumeration sentences must not be flagged as
    high clause-depth. The v1.8.2 fix split markers into weighted pools
    (PUNCTUATION_WEIGHT=0.3); v1.8.3 removed `)` from punctuation and
    moved subordinator detection to regex so sentence-start clauses count.
    """
    mod = _import_module()
    # Pure enumeration: 3 commas per sentence, no subordinators.
    text = (
        "We tested red, white, and blue. "
        "Then green, yellow, and orange. "
        "Finally black, brown, gray, and purple."
    )
    # 4 commas avg per sentence * 0.3 = 1.2 (still below 1.5 = healthy ceiling).
    assert mod.avg_clause_depth(text) < 1.5, (
        f"enumeration commas over-weighted: got "
        f"{mod.avg_clause_depth(text)} (expected < 1.5)"
    )


def test_sentence_start_subordinator_detected():
    """CODE-AUDIT-402 regression: a sentence beginning with 'While' / 'Because'
    must register the subordinator. v1.8.2 substring-match missed these
    (no leading space). v1.8.3 word-boundary regex catches them."""
    mod = _import_module()
    text = "While I was thinking I saw it. Because of that, I left."
    # 2 subordinators across 2 sentences -> avg 1.0 (just SUBORDINATOR_WEIGHT)
    # plus 1 comma -> 0.3, total ~ 1.15. Without the fix it would be ~0.15.
    assert mod.avg_clause_depth(text) >= 0.9, (
        f"sentence-start subordinator missed: got "
        f"{mod.avg_clause_depth(text)} (expected >= 0.9)"
    )


def test_parenthetical_not_double_counted():
    """CODE-AUDIT-401 regression: a single parenthetical scores 0.3, not 0.6."""
    mod = _import_module()
    text = "Read the docs (carefully)."
    # 1 sentence, 1 opening paren = 0.3 (closing paren no longer counted).
    assert abs(mod.avg_clause_depth(text) - 0.3) < 0.01, (
        f"parenthetical double-counted: got {mod.avg_clause_depth(text)}"
    )


def test_all_caps_acronyms_are_captured():
    """FIND-014 regression: NASA, IBM, JSON, REST, API must register as
    entities. Pre-v1.8.1, the entity regex required lowercase chars after
    the initial capital, missing all acronyms."""
    mod = _import_module()
    ents = mod.find_entities(
        "NASA published a JSON spec. IBM extended REST endpoints. "
        "The API consumed GPT-4 output."
    )
    # Need at least 3 of {NASA, JSON, IBM, REST, API, GPT-4}
    found_acronyms = ents & {"NASA", "JSON", "IBM", "REST", "API", "GPT-4"}
    assert len(found_acronyms) >= 3, (
        f"all-caps acronym detection regressed: only found {ents}"
    )


def test_single_word_opener_filtered_but_multiword_entity_kept():
    """FIND-015 + CODE-AUDIT-403 regression: 'May arrived early.' must NOT
    register 'May' as an entity (single-token opener). But 'May Tech Co'
    MUST survive (multi-word phrase starting with an opener-eligible word
    is likely a real entity)."""
    mod = _import_module()
    # Single-token opener filtered.
    ents = mod.find_entities("May arrived early. From here, it works.")
    assert "May" not in ents, f"single-token 'May' leaked: {ents}"
    assert "From" not in ents, f"single-token 'From' leaked: {ents}"
    # Multi-word entity preserved.
    ents2 = mod.find_entities(
        "May Tech Co launched their product. Take Two Interactive shipped."
    )
    # Multi-word phrases starting with an opener should survive.
    found_phrases = {e for e in ents2 if e.startswith(("May ", "Take "))}
    assert len(found_phrases) >= 1, (
        f"multi-word entities starting with opener-eligible word dropped: "
        f"{ents2}"
    )


def test_overloaded_section_load_score_threshold(tmp_path: Path) -> None:
    """Strengthened version of test_overloaded_section_flagged:
    assert load_score >= 50 (the overloaded threshold) instead of just > 0."""
    post = tmp_path / "dense2.md"
    post.write_text(
        "## Methodology\n\n"
        "We tested Acme Corp, Globex Inc, Initech Systems, Umbrella Labs, "
        "Hooli Networks, Pied Piper Tech, Stark Industries, Wayne Enterprises "
        "in 2024. Adoption hit 87.3%, retention reached 92.1%, churn dropped "
        "to 3.5%, NPS reached 67. Schema markup, structured data, e-e-a-t, "
        "geo, aeo, burstiness, ttr, hreflang, canonical, robots.txt all "
        "moved together, which is what we will see later when we discuss the "
        "second-order analysis, though as we will see in the next section.\n",
        encoding="utf-8",
    )
    report = _run(post)
    section = next(s for s in report["sections"] if "Methodology" in s["heading"])
    assert section["load_score"] >= 50, (
        f"overloaded threshold (50) not met: got {section['load_score']}"
    )
    assert section["verdict"] == "overloaded", (
        f"verdict not 'overloaded': got {section['verdict']!r}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
