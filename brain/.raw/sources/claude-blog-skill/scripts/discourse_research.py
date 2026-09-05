#!/usr/bin/env python3
"""
Discourse Research: Synthesis Helper for /blog discourse

Consumes a JSON file of pre-gathered SERP / WebSearch results and produces:
1. A DISCOURSE.md brief at the requested output path
2. Structured JSON on stdout (when --format json)

This script does NOT call any external APIs or perform searches. It expects the
search to have been performed upstream (by Claude via WebSearch, or by another
process) and the results to be passed in as JSON.

Adapted from the methodology of last30days-skill v3.2.1 (Matt Van Horn, MIT,
github.com/mvanhorn/last30days-skill). The upstream uses platform APIs; this
script uses pre-gathered WebSearch results.

Input JSON schema:
    [
      {
        "platform": "reddit" | "hackernews" | "x" | "youtube" | "devto" | "medium"
                  | "github" | "stackoverflow" | "substack" | "web",
        "url": "https://...",
        "title": "Title as visible in SERP / source",
        "snippet": "Snippet text",
        "date": "YYYY-MM-DD" | null,
        "engagement_proxy": "upvotes / likes / views as visible" | null
      },
      ...
    ]

Usage:
    python3 discourse_research.py --input results.json --topic "topic" \\
        --days 30 --output DISCOURSE.md
    python3 discourse_research.py --input results.json --topic "topic" \\
        --format json     # prints JSON brief to stdout, no file output
    python3 discourse_research.py --input - --topic "topic" --days 90   # stdin

Output JSON schema:
    {
      "topic": "...",
      "window_days": 30,
      "generated": "YYYY-MM-DD",
      "platform_breakdown": { "reddit": N, "x": M, ... },
      "themes_new": [ { "theme": "...", "claim": "...", "sources": [...] } ],
      "themes_consensus": [ { "theme": "...", "claim": "...", "sources": [...] } ],
      "themes_contrarian": [ ... ],
      "specifics": [ ... ],
      "source_count": N,
      "useful_count": M
    }

The script enforces LAW 2 (no invented titles - titles come verbatim from
input data; never paraphrased), LAW 3 (no em-dashes in output), and LAW 5
(every source is rendered as inline markdown link [name](url)).
"""

from __future__ import annotations

import argparse
import datetime as dt
import errno
import json
import math
import os
import re
import stat
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PLATFORM_LABELS = {
    "reddit": "Reddit",
    "hackernews": "Hacker News",
    "hn": "Hacker News",
    "x": "X / Twitter",
    "twitter": "X / Twitter",
    "youtube": "YouTube",
    "devto": "dev.to",
    "dev.to": "dev.to",
    "medium": "Medium",
    "github": "GitHub",
    "stackoverflow": "Stack Overflow",
    "substack": "Substack",
    "bluesky": "Bluesky",
    "web": "Web",
}

# Stopwords for theme keyword extraction
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "in", "on", "at", "of", "for",
    "to", "with", "by", "as", "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those", "it", "its", "they", "them", "their",
    "i", "you", "he", "she", "we", "us", "our", "my", "your", "his", "her",
    "from", "into", "out", "up", "down", "all", "any", "each", "more", "most",
    "some", "such", "no", "not", "only", "own", "same", "so", "than", "too",
    "very", "can", "will", "just", "don", "should", "now", "about",
}

EM_DASH_REPLACEMENTS = {
    "\u2014": " - ",   # unicode em-dash
    "\u2013": " - ",   # unicode en-dash
    "\x20--\x20": " - ",  # ASCII double-hyphen (LAW 3); space-flanked only
}


def strip_em_dashes(text: str) -> str:
    """Apply LAW 3: no em-dashes or en-dashes in output."""
    for old, new in EM_DASH_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


# ---------------------------------------------------------------------------
# Parsing input
# ---------------------------------------------------------------------------

MAX_INPUT_BYTES = 25 * 1024 * 1024   # 25 MB cap on results JSON (DoS guard)
MAX_DECOMP_BYTES = 256 * 1024        # 256 KB cap on decomposition file
MAX_ITEMS = 10_000                   # cap on items in results array
MAX_STDIN_BYTES = 25 * 1024 * 1024   # cap on stdin reads
MAX_JSON_DEPTH = 50                  # max nesting depth (defends against deeply-nested DoS, CWE-674)

# Scoring weights (documented for future recalibration; see score_item())
RECENCY_WEIGHT = 60.0            # recency contributes up to 60 of 100
ENGAGEMENT_WEIGHT = 40.0         # engagement contributes up to 40 of 100
ENGAGEMENT_LOG_FLOOR = 10        # engagement<10 treated as 10 (log-smoothing)
ENGAGEMENT_LOG_SCALE = 8.0       # 8 pts per order of magnitude

# String field length caps (defend against megabyte-string DoS and renderer abuse)
MAX_STRING_FIELD = 4_000

REQUIRED_FIELDS = {"platform", "url", "title", "snippet"}
OPTIONAL_FIELDS = {"date", "engagement_proxy"}
ALLOWED_URL_SCHEMES = ("http://", "https://")


def _read_safely(path: Path, max_bytes: int, label: str) -> str:
    """Read a path with TOCTOU-resistant defenses.

    Uses os.open(O_NOFOLLOW) where available (POSIX) to atomically refuse
    symlinks AND prevent a swap between the check and the read (CWE-367).
    On Windows (no O_NOFOLLOW), falls back to is_symlink check; small TOCTOU
    window remains but symlink refusal still applies.

    Refuses: missing files, symlinks (CWE-59), non-regular files
    (FIFOs/devices/sockets), oversize inputs (DoS).
    Returns decoded UTF-8 string. Caller must catch ValueError / FileNotFoundError.
    """
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    else:  # Windows: do best-effort symlink check first (TOCTOU residual)
        if path.is_symlink():
            raise ValueError(
                f"{label} is a symlink; refusing to follow for safety: {path}"
            )
    try:
        fd = os.open(str(path), flags)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"{label} not found: {path}") from e
    except OSError as e:
        if e.errno == errno.ELOOP:  # O_NOFOLLOW hit a symlink
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
            fd = -1  # ownership transferred to file object
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

    Does NOT confine input to a base directory; the caller is responsible for
    overall path safety. Kept for callers that only need a validated Path
    object; new callers should prefer _read_safely() which closes the TOCTOU
    window via O_NOFOLLOW.
    """
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")
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


def _check_json_depth(obj: Any, max_depth: int, current: int = 0) -> None:
    """Refuse pathologically-nested JSON (CWE-674). Recursion-error guard.

    Walks the tree iteratively where possible; raises ValueError once any
    container's nesting exceeds max_depth.
    """
    if current > max_depth:
        raise ValueError(f"JSON nesting depth exceeds cap ({max_depth})")
    if isinstance(obj, dict):
        for v in obj.values():
            _check_json_depth(v, max_depth, current + 1)
    elif isinstance(obj, list):
        for v in obj:
            _check_json_depth(v, max_depth, current + 1)


def _validate_output_path(path_str: str) -> Path:
    """Validate an output path. Refuses overwriting symlinks; ensures parent dir exists."""
    out = Path(path_str)
    if out.exists() and out.is_symlink():
        raise ValueError(
            f"Output path is a symlink; refusing to overwrite for safety: {out}"
        )
    if out.exists() and not out.is_file():
        raise ValueError(f"Output path exists but is not a regular file: {out}")
    if not out.parent.exists():
        raise ValueError(f"Output directory does not exist: {out.parent}")
    return out


def _validate_item(item: Any, index: int) -> dict[str, Any]:
    """Validate one result item against the JSON schema.

    Enforces: object shape, required fields present, string types on required
    fields, URL scheme http/https only, and length caps (defends FIND-003 type
    confusion, FIND-004/019 markdown/URL injection, oversized-string DoS).
    Returns a NEW dict with truncated/whitespace-collapsed string fields.
    """
    if not isinstance(item, dict):
        raise ValueError(
            f"Result item {index} is not an object: got {type(item).__name__}"
        )
    missing = REQUIRED_FIELDS - set(item.keys())
    if missing:
        raise ValueError(
            f"Result item {index} missing required fields: {sorted(missing)}"
        )
    out: dict[str, Any] = {}
    for field in REQUIRED_FIELDS:
        v = item[field]
        if not isinstance(v, str):
            raise ValueError(
                f"Result item {index} field {field!r} must be string, got "
                f"{type(v).__name__}"
            )
        if len(v) > MAX_STRING_FIELD:
            raise ValueError(
                f"Result item {index} field {field!r} exceeds {MAX_STRING_FIELD} chars"
            )
        # Collapse control characters that break markdown rendering
        out[field] = "".join(c for c in v if c == "\n" or ord(c) >= 0x20)
    # URL scheme allowlist (defends FIND-019 javascript:/file:/data: URLs)
    if not out["url"].lower().startswith(ALLOWED_URL_SCHEMES):
        raise ValueError(
            f"Result item {index} url scheme must be http or https: {out['url'][:80]!r}"
        )
    # Optional fields pass-through with type-relaxed handling downstream
    for field in OPTIONAL_FIELDS:
        if field in item:
            out[field] = item[field]
    return out


def load_results(input_path: str) -> list[dict[str, Any]]:
    """Load and validate a JSON array of result objects.

    Source: file path or stdin ('-'). Enforces size cap, JSON-depth cap,
    schema, and item count to defend against DoS and malformed-input crashes.
    """
    if input_path == "-":
        raw = sys.stdin.read(MAX_STDIN_BYTES + 1)
        if len(raw) > MAX_STDIN_BYTES:
            raise ValueError(f"stdin input exceeds size cap ({MAX_STDIN_BYTES} bytes)")
    else:
        raw = _read_safely(Path(input_path), MAX_INPUT_BYTES, "Input file")
        if len(raw) > MAX_INPUT_BYTES:
            raise ValueError(
                f"Input file exceeds size cap ({MAX_INPUT_BYTES} bytes)"
            )
    if not raw.strip():
        return []
    try:
        data = json.loads(raw)
    except RecursionError as e:  # FIND-002: deeply-nested JSON
        raise ValueError(
            "JSON exceeds Python parser recursion limit (deeply-nested input)"
        ) from e
    if not isinstance(data, list):
        raise ValueError("Input must be a JSON array of result objects.")
    if len(data) > MAX_ITEMS:
        raise ValueError(
            f"Result array length {len(data)} exceeds cap ({MAX_ITEMS})"
        )
    # CWE-674 depth guard (catches deep-nesting attacks that don't trip the
    # parser limit but would still exhaust recursion in user-side processing)
    for item in data:
        _check_json_depth(item, MAX_JSON_DEPTH)
    return [_validate_item(item, i) for i, item in enumerate(data)]


def parse_date(value: Any) -> dt.date | None:
    """Parse a date string. ISO 8601 only ('YYYY-MM-DD') plus 'YYYY/MM/DD'
    and the unambiguous 'Mon DD, YYYY' form. Ambiguous slash-formats like
    '02/03/2026' (US dd/mm vs European mm/dd) are explicitly NOT accepted
    to prevent ~30-day drift in freshness classification (FIND-016).
    """
    if not value:
        return None
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%b %d, %Y"):
            try:
                return dt.datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue
    return None


def parse_engagement(value: Any) -> int:
    """Best-effort numeric parse of engagement strings like '1.2k', '450 upvotes'.

    Defenses (FIND-001 + CODE-AUDIT-406 v1.8.3 hardening):
    * Anchored suffix [kmb] (digit-immediate-letter, terminal at token end)
      to prevent '5 best ideas' parsing as 5,000,000,000.
    * Negative numbers return 0 (engagement is conventionally non-negative;
      a leading `-` likely means "deleted" or "[score hidden]"; abs() would
      silently invert sign).
    * Scientific notation ('1.5e6') is not supported by the regex and
      returns 0 (silent fallback was wrong; explicit rejection is safer).
    * Numeric inputs are clamped to >= 0.
    """
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        n = int(value)
        return max(0, n)
    s = str(value).lower().replace(",", "")
    # Reject explicit negatives before regex pickup ('-3 upvotes' -> 0).
    if re.search(r"-\s*\d", s):
        return 0
    # Reject scientific notation entirely (the [kmb] suffix regex would
    # otherwise match the mantissa and ignore the exponent, producing
    # nonsense scores like '1.5e6 papers' -> 1).
    if re.search(r"\d+(?:\.\d+)?e[+-]?\d+", s):
        return 0
    # Anchored suffix: digit-immediate-letter, terminated by non-alnum or end-of-token.
    m = re.search(r"\b(\d+(?:\.\d+)?)([kmb])?(?![a-z0-9])", s)
    if not m:
        return 0
    n = float(m.group(1))
    suffix = m.group(2) or ""
    multiplier = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}.get(suffix, 1)
    return int(n * multiplier)


# ---------------------------------------------------------------------------
# Scoring and theming
# ---------------------------------------------------------------------------


def score_item(item: dict[str, Any], today: dt.date, window_days: int) -> float:
    """Combined recency + engagement score in [0, 100].

    Recency contributes up to RECENCY_WEIGHT (60). Engagement contributes up
    to ENGAGEMENT_WEIGHT (40) on a log scale (ENGAGEMENT_LOG_FLOOR=10 means
    engagement<10 is treated as 10).
    """
    date = parse_date(item.get("date"))
    if date is None:
        recency_score = RECENCY_WEIGHT * 0.5
    elif date > today:
        recency_score = 0.0
    else:
        age_days = (today - date).days
        if age_days > window_days * 3:
            recency_score = 0.0
        else:
            recency_score = max(
                0.0, RECENCY_WEIGHT * (1 - age_days / (window_days * 3))
            )

    engagement = parse_engagement(item.get("engagement_proxy"))
    if engagement == 0:
        engagement_score = 5.0  # unknown engagement: middling-low
    else:
        engagement_score = min(
            ENGAGEMENT_WEIGHT,
            ENGAGEMENT_LOG_SCALE
            * math.log10(max(ENGAGEMENT_LOG_FLOOR, engagement)),
        )
    return round(recency_score + engagement_score, 1)


def extract_theme_keywords(text: str, topic_tokens: set[str], top_n: int = 5) -> list[str]:
    """Extract candidate theme keywords from a title or snippet."""
    words = re.findall(r"\b[A-Za-z][A-Za-z0-9\-]{2,}\b", text.lower())
    candidates = [
        w for w in words
        if w not in STOPWORDS and w not in topic_tokens and len(w) >= 4
    ]
    seen = set()
    out = []
    for w in candidates:
        if w not in seen:
            seen.add(w)
            out.append(w)
        if len(out) >= top_n:
            break
    return out


CLUSTER_MIN_SIZE_FOR_MULTI_KEYWORD = 2  # 2+ shared keywords required for groups of size >= 2


def cluster_by_theme(
    items: list[dict[str, Any]],
    topic: str,
) -> list[dict[str, Any]]:
    """Bucket items by shared keyword themes.

    v1.8.3 corrections vs v1.8.2 (FIND-017 + CODE-AUDIT-404 + 405):
    * Build an inverted keyword index once, so cohesion check is
      O(n * unique_kw_per_item) instead of O(n^2). At MAX_ITEMS=10000 with
      ~5 kws per item, this is ~50k ops vs ~100M.
    * Items with empty or duplicate URLs use synthetic per-index keys so
      keyword maps no longer collide (the v1.8.2 bug produced phantom
      cohesion for unscraped/syndicated items).
    """
    topic_tokens = set(topic.lower().split())
    # item_key -> set of keywords for that specific item
    item_keywords: dict[str, set[str]] = {}
    # keyword -> set of item_keys carrying that keyword (inverted index)
    keyword_to_keys: dict[str, set[str]] = defaultdict(set)
    # item_key -> the item dict (preserves ordering for emit)
    key_to_item: dict[str, dict[str, Any]] = {}
    # keyword -> ordered list of item_keys (preserves emit order)
    keyword_to_keys_ordered: dict[str, list[str]] = defaultdict(list)

    # Track first-seen URLs so duplicates get synthetic per-index keys
    # instead of colliding in item_keywords (CODE-AUDIT-405). Empty URLs
    # always use synthetic keys.
    seen_urls: set[str] = set()
    for idx, item in enumerate(items):
        text = f"{item.get('title', '')} {item.get('snippet', '')}"
        kws = set(extract_theme_keywords(text, topic_tokens))
        url = item.get("url") or ""
        if url and url not in seen_urls:
            seen_urls.add(url)
            key = url
        else:
            key = f"_synthetic_{idx}"
        item_keywords[key] = kws
        key_to_item[key] = item
        for kw in kws:
            if key not in keyword_to_keys[kw]:
                keyword_to_keys[kw].add(key)
                keyword_to_keys_ordered[kw].append(key)

    clusters: list[dict[str, Any]] = []
    used_keys: set[str] = set()
    for kw, ordered_keys in sorted(
        keyword_to_keys_ordered.items(),
        key=lambda kv: (-len(kv[1]), kv[0]),
    ):
        unique_keys = [k for k in ordered_keys if k not in used_keys]
        if not unique_keys:
            continue
        if len(unique_keys) >= CLUSTER_MIN_SIZE_FOR_MULTI_KEYWORD:
            cohesive_keys = _filter_cohesive_indexed(
                unique_keys, kw, item_keywords, keyword_to_keys
            )
            # v1.8.3 FIND-017 strict interpretation: if multi-item group fails
            # cohesion, do NOT emit a multi-item cluster on this keyword.
            # Skip; items remain unassigned and can singleton-cluster later
            # on a different keyword that genuinely binds them.
            #
            # TRADEOFF (v1.8.4 5TH-AUDIT-011 documentation): when N items
            # share ONLY the primary keyword (no secondary overlap), the
            # multi-item cluster is dropped entirely. Each item becomes a
            # singleton on a DIFFERENT keyword. Net effect: the shared
            # keyword disappears from the themes view. This is the strict
            # interpretation of cohesion: a one-keyword overlap is NOT
            # enough signal to call something a "theme". The alternative
            # (lax: emit anyway on one-keyword overlap) re-introduces
            # phantom-clustering. We chose strict. If a future requirement
            # surfaces that the shared keyword should still be noted, add
            # an "incidental_overlap" bucket separate from themes_new /
            # themes_consensus / themes_niche.
            if not cohesive_keys:
                continue
            unique_keys = cohesive_keys
        for k in unique_keys:
            used_keys.add(k)
        clusters.append({
            "theme": kw,
            "items": [key_to_item[k] for k in unique_keys],
        })
    return clusters


def _filter_cohesive_indexed(
    candidate_keys: list[str],
    primary_kw: str,
    item_keywords: dict[str, set[str]],
    keyword_to_keys: dict[str, set[str]],
) -> list[str]:
    """O(n * unique_kw_per_item) cohesion filter using the inverted index.

    An item joins a multi-item cluster only if it shares at least one
    NON-primary keyword with another item already in the candidate set.
    """
    candidate_set = set(candidate_keys)
    out: list[str] = []
    for key in candidate_keys:
        secondary_kws = item_keywords.get(key, set()) - {primary_kw}
        cohesive = False
        for kw in secondary_kws:
            # Items sharing this keyword, intersected with the candidate set,
            # minus self. If non-empty, this item has a partner.
            partners = (keyword_to_keys.get(kw, set()) & candidate_set) - {key}
            if partners:
                cohesive = True
                break
        if cohesive:
            out.append(key)
    return out


_SPECIFICS_KEYWORD_RE = re.compile(
    r"\b(command|config|setup|fix|workaround|how to|step|version)\b"
    r"|```"          # fenced code block
    r"|`[^`\n]+`",   # inline code span (bounded, not lone backtick)
    re.IGNORECASE,
)


def _is_recent(item: dict[str, Any], today: dt.date, window_days: int) -> bool:
    d = parse_date(item.get("date"))
    if d is None or d > today:
        return False
    return (today - d).days <= window_days


def classify_clusters(
    clusters: list[dict[str, Any]],
    today: dt.date,
    window_days: int,
) -> dict[str, list[dict[str, Any]]]:
    """Sort clusters into NEW / CONSENSUS / NICHE / SPECIFICS buckets.

    NICHE was previously labeled "contrarian" but the rule (singleton cluster)
    does not detect opposition, only isolation. Renamed for honesty (FIND-023).
    Specifics now applies its own recency filter (FIND-006) instead of
    inheriting the bucket-level filter, and uses a stricter regex that
    requires whole-word keywords or actual code-fence syntax (FIND-008).
    """
    new_themes = []
    consensus_themes = []
    niche_themes = []
    specifics = []

    for cluster in clusters:
        platforms = {i.get("platform") for i in cluster["items"]}
        item_count = len(cluster["items"])
        recent_count = sum(
            1 for i in cluster["items"] if _is_recent(i, today, window_days)
        )
        if recent_count >= 2 and len(platforms) >= 2:
            consensus_themes.append(cluster)
        elif recent_count >= 1 and item_count == 1:
            niche_themes.append(cluster)
        elif recent_count >= 1:
            new_themes.append(cluster)
        # FIND-006: specifics MUST be recent (the brief is freshness-promised).
        for i in cluster["items"]:
            if not _is_recent(i, today, window_days):
                continue
            if _SPECIFICS_KEYWORD_RE.search(i.get("snippet", "") or ""):
                specifics.append(i)

    seen = set()
    specifics_unique = []
    for s in specifics:
        u = s.get("url")
        if u and u not in seen:
            seen.add(u)
            specifics_unique.append(s)
        if len(specifics_unique) >= 5:
            break

    return {
        "new": new_themes[:5],
        "consensus": consensus_themes[:4],
        "niche": niche_themes[:3],
        "specifics": specifics_unique,
    }


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _safe_link_text(text: str) -> str:
    """Sanitize markdown-link display text. Collapses whitespace, escapes
    brackets that would terminate the link, drops control characters.
    Defends FIND-004 (markdown link injection via `]` in title) and FIND-010
    (link corruption via embedded newlines).
    """
    if not text:
        return ""
    # Collapse all whitespace runs (incl. \n, \r, \t) into single spaces.
    collapsed = " ".join(text.split())
    # Escape the markdown-link terminator and the backslash that could be
    # used to bypass the escape.
    return collapsed.replace("\\", "\\\\").replace("]", r"\]").replace("[", r"\[")


def _safe_markdown_text(text: str) -> str:
    """Escape Markdown control characters in user-supplied headings and lists."""
    cleaned = strip_em_dashes(" ".join(str(text).split()))
    return (
        cleaned.replace("\\", "\\\\")
        .replace("[", r"\[")
        .replace("]", r"\]")
        .replace("|", r"\|")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _safe_link_url(url: str) -> str | None:
    """Validate a URL for safe markdown-link rendering.
    Returns the url if it is http/https; None otherwise (FIND-019).
    Also rejects URLs containing whitespace or a literal `)` that would
    truncate the link in renderers.
    """
    if not url:
        return None
    if not url.lower().startswith(ALLOWED_URL_SCHEMES):
        return None
    if any(c in url for c in (" ", "\t", "\n", "\r", ")", "(")):
        return None
    return url


def render_inline_link(item: dict[str, Any]) -> str:
    """LAW 5: every citation as [name](url). LAW 2: never invent titles.

    Sanitizes title (FIND-004 / FIND-010) and validates URL scheme (FIND-019)
    so a hostile SERP item cannot inject a clickable javascript:/file:/data:
    link or break markdown rendering with bracket characters in the title.
    """
    raw_url = item.get("url") or ""
    raw_title = item.get("title") or item.get("platform") or "source"
    platform = item.get("platform", "")
    label = PLATFORM_LABELS.get(platform, platform.capitalize()) if platform else ""
    name = _safe_link_text(raw_title)[:80]
    if label and label.lower() not in name.lower():
        name = f"{name} ({_safe_link_text(label)})"
    safe_url = _safe_link_url(raw_url)
    if not safe_url:
        return name
    return f"[{name}]({safe_url})"


def _safe_snippet(text: str) -> str:
    """Sanitize snippet text for inline rendering inside markdown prose.

    Escapes markdown link syntax (`[` and `]`) so a snippet containing
    `[evil](https://attacker.com)` cannot inject a clickable link into the
    brief (FIND-004 defense in depth for snippets, not just titles).
    Strips em-dashes (LAW 3) and clamps to 200 chars.
    """
    if not text:
        return ""
    cleaned = strip_em_dashes(text)[:200].strip()
    return cleaned.replace("\\", "\\\\").replace("]", r"\]").replace("[", r"\[")


def render_cluster_paragraph(cluster: dict[str, Any]) -> str:
    items = cluster["items"]
    theme = cluster["theme"].replace("-", " ").title()
    sources = ", ".join(render_inline_link(i) for i in items[:3])
    sample_snippet = _safe_snippet(items[0].get("snippet") or "")
    if sample_snippet:
        body = f"{sample_snippet} Cited in {sources}."
    else:
        body = f"Cited across {sources}."
    return f"- **{theme}.** {body}"


def _render_header(topic: str, generated: dt.date, window_days: int,
                   item_count: int, platforms_used: int) -> list[str]:
    return [
        f"# Discourse Brief: {_safe_markdown_text(topic)}",
        "",
        f"> Generated {generated.isoformat()} via /blog discourse. "
        f"Window: last {window_days} days. "
        f"Sources scanned: {item_count} across {platforms_used} platforms.",
        "",
    ]


def _render_decomposition(decomposition: list[str] | None) -> list[str]:
    if not decomposition:
        return []
    lines = ["## Decomposition", ""]
    for i, q in enumerate(decomposition, 1):
        lines.append(f"{i}. {_safe_markdown_text(q)}")
    lines.append("")
    return lines


def _render_cluster_section(
    heading: str,
    clusters: list[dict[str, Any]],
    empty_message: str,
) -> list[str]:
    lines = [heading, ""]
    if clusters:
        for cluster in clusters:
            lines.append(render_cluster_paragraph(cluster))
    else:
        lines.append(f"- {empty_message}")
    lines.append("")
    return lines


def _render_specifics(specifics: list[dict[str, Any]]) -> list[str]:
    lines = ["## Practitioner specifics (commands, configs, links)", ""]
    if specifics:
        for item in specifics:
            snippet = _safe_snippet(item.get("snippet") or "")[:160]
            lines.append(f"- {render_inline_link(item)}: {snippet}")
    else:
        lines.append("- No concrete practitioner specifics surfaced in the window.")
    lines.append("")
    return lines


def render_markdown(
    topic: str,
    window_days: int,
    generated: dt.date,
    buckets: dict[str, list[dict[str, Any]]],
    items: list[dict[str, Any]],
    decomposition: list[str] | None,
) -> str:
    """Assemble the DISCOURSE.md brief from bucket data.

    Decomposed into small section helpers (FIND-021) so future format
    tweaks (rearranging sections, swapping helpers, adding a new bucket)
    do not require touching a 70-line monolith.
    """
    platform_counts: dict[str, int] = defaultdict(int)
    for item in items:
        platform_counts[item.get("platform") or "web"] += 1
    platforms_used = len([p for p, c in platform_counts.items() if c > 0])

    lines: list[str] = []
    lines.extend(_render_header(topic, generated, window_days, len(items), platforms_used))
    lines.extend(_render_decomposition(decomposition))
    lines.extend(_render_cluster_section(
        f"## What's NEW in the last {window_days} days",
        buckets["new"],
        "No distinctly new themes detected in the window. Consider widening to --days 90.",
    ))
    lines.extend(_render_cluster_section(
        "## Consensus across platforms",
        buckets["consensus"],
        "No cross-platform consensus themes detected.",
    ))
    lines.extend(_render_cluster_section(
        "## Niche / single-source themes",
        buckets["niche"],
        "None surfaced. Absence is honest; do not invent contrarian takes.",
    ))
    lines.extend(_render_specifics(buckets["specifics"]))

    lines.append("## Source breakdown")
    lines.append("")
    lines.append("| Platform | Sources scanned |")
    lines.append("|---|---|")
    for platform, count in sorted(platform_counts.items(), key=lambda kv: -kv[1]):
        label = PLATFORM_LABELS.get(platform, platform.capitalize())
        lines.append(f"| {label} | {count} |")
    lines.append("")
    return strip_em_dashes("\n".join(lines))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_brief(
    items: list[dict[str, Any]],
    topic: str,
    window_days: int,
    today: dt.date,
    decomposition: list[str] | None = None,
) -> dict[str, Any]:
    """Build the structured-JSON brief."""
    for item in items:
        item["_score"] = score_item(item, today, window_days)
    items_sorted = sorted(items, key=lambda i: -i.get("_score", 0))

    clusters = cluster_by_theme(items_sorted, topic)
    buckets = classify_clusters(clusters, today, window_days)
    markdown = render_markdown(topic, window_days, today, buckets, items_sorted, decomposition)

    def cluster_summary(c: dict[str, Any]) -> dict[str, Any]:
        return {
            "theme": c["theme"],
            "item_count": len(c["items"]),
            "sources": [
                {"platform": i.get("platform"), "url": i.get("url"), "title": i.get("title")}
                for i in c["items"][:3]
            ],
        }

    platform_breakdown: dict[str, int] = defaultdict(int)
    for item in items_sorted:
        platform_breakdown[item.get("platform") or "web"] += 1

    return {
        "topic": topic,
        "window_days": window_days,
        "generated": today.isoformat(),
        "source_count": len(items_sorted),
        "platform_breakdown": dict(platform_breakdown),
        "themes_new": [cluster_summary(c) for c in buckets["new"]],
        "themes_consensus": [cluster_summary(c) for c in buckets["consensus"]],
        "themes_niche": [cluster_summary(c) for c in buckets["niche"]],
        "specifics_count": len(buckets["specifics"]),
        "markdown": markdown,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--input", required=True, help="Path to results JSON, or '-' for stdin")
    parser.add_argument("--topic", required=True, help="Original topic string")
    parser.add_argument("--days", type=int, default=30, help="Freshness window in days (default 30)")
    parser.add_argument("--output", default=None, help="Path to write DISCOURSE.md (default: stdout markdown)")
    parser.add_argument(
        "--format", choices=["markdown", "json"], default="markdown",
        help="Output format when not writing to --output",
    )
    parser.add_argument(
        "--decomposition", default=None,
        help="Optional path to a newline-delimited file of decomposition questions",
    )
    args = parser.parse_args()

    if args.days < 1:
        print("Error: --days must be at least 1", file=sys.stderr)
        return 2

    try:
        items = load_results(args.input)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"Error: input is not valid JSON: {e}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    decomposition: list[str] | None = None
    if args.decomposition:
        try:
            decomp_path = _validate_input_path(
                Path(args.decomposition), MAX_DECOMP_BYTES, "Decomposition file"
            )
            decomp_text = _read_safely(decomp_path, MAX_DECOMP_BYTES, "Decomposition file")
            decomposition = [
                line.strip()
                for line in decomp_text.splitlines()
                if line.strip()
            ]
        except (FileNotFoundError, ValueError) as e:
            print(f"Warning: {e}; proceeding without decomposition.", file=sys.stderr)

    brief = build_brief(items, args.topic, args.days, dt.date.today(), decomposition)

    if args.output:
        try:
            out_path = _validate_output_path(args.output)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 2
        # Atomic write (FIND-018): write to sibling .tmp then os.replace.
        # Avoids partial DISCOURSE.md if the process is killed mid-write.
        tmp_fd, tmp_path = tempfile.mkstemp(
            prefix=out_path.name + ".",
            suffix=".tmp",
            dir=str(out_path.parent),
        )
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as tmp_f:
                tmp_f.write(brief["markdown"])
            os.replace(tmp_path, out_path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
        print(json.dumps({k: v for k, v in brief.items() if k != "markdown"}, indent=2))
    elif args.format == "json":
        print(json.dumps(brief, indent=2))
    else:
        print(brief["markdown"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
