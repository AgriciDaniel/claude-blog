"""Security regression tests for v1.8.0 defenses.

Covers:
1. Path traversal: scripts must refuse to read symlinks.
2. DoS: scripts must enforce MAX_*_BYTES size caps.
3. JSON schema: discourse_research.py must reject malformed input items.
4. Output path: discourse_research.py must refuse overwriting symlinks.
5. Prompt-injection guard: skills/blog/SKILL.md must instruct the orchestrator
   to fence project-root files (BRAND.md / VOICE.md / DISCOURSE.md).

Stdlib + pytest only. No network. All file ops use tmp_path.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
COGNITIVE = ROOT / "scripts" / "cognitive_load.py"
DISCOURSE = ROOT / "scripts" / "discourse_research.py"


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


# ---------------------------------------------------------------------------
# Path traversal / symlink refusal
# ---------------------------------------------------------------------------


def test_cognitive_load_refuses_symlink_input(tmp_path: Path) -> None:
    """A symlink as input must be refused (CWE-59 defense)."""
    real_target = tmp_path / "real.md"
    real_target.write_text("## section\nbody\n", encoding="utf-8")
    symlink = tmp_path / "link.md"
    os.symlink(real_target, symlink)
    result = _run([sys.executable, str(COGNITIVE), str(symlink)])
    assert result.returncode != 0
    assert "symlink" in result.stderr.lower()


def test_discourse_research_refuses_symlink_input(tmp_path: Path) -> None:
    real_target = tmp_path / "real.json"
    real_target.write_text("[]", encoding="utf-8")
    symlink = tmp_path / "link.json"
    os.symlink(real_target, symlink)
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(symlink),
        "--topic", "test",
        "--format", "json",
    ])
    assert result.returncode != 0
    assert "symlink" in result.stderr.lower()


def test_discourse_research_refuses_symlink_output(tmp_path: Path) -> None:
    """An existing-symlink as --output must be refused so attacker symlinks
    cannot redirect writes to /etc/cron.d or similar."""
    real_target = tmp_path / "real_target.md"
    real_target.write_text("placeholder\n", encoding="utf-8")
    symlink_output = tmp_path / "DISCOURSE.md"
    os.symlink(real_target, symlink_output)
    inp = tmp_path / "results.json"
    inp.write_text("[]", encoding="utf-8")
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(inp),
        "--topic", "test",
        "--output", str(symlink_output),
    ])
    assert result.returncode != 0
    assert "symlink" in result.stderr.lower()


def test_discourse_research_refuses_nonexistent_output_dir(tmp_path: Path) -> None:
    inp = tmp_path / "results.json"
    inp.write_text("[]", encoding="utf-8")
    bogus_dir = tmp_path / "does" / "not" / "exist"
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(inp),
        "--topic", "test",
        "--output", str(bogus_dir / "DISCOURSE.md"),
    ])
    assert result.returncode != 0
    assert "directory does not exist" in result.stderr.lower()


# ---------------------------------------------------------------------------
# DoS: size caps
# ---------------------------------------------------------------------------


def test_cognitive_load_refuses_oversize_input(tmp_path: Path) -> None:
    """An input file over MAX_INPUT_BYTES (10MB) must be refused."""
    big = tmp_path / "huge.md"
    # 11 MB of zeros
    big.write_bytes(b"# title\n" + b"x" * (11 * 1024 * 1024))
    result = _run([sys.executable, str(COGNITIVE), str(big)])
    assert result.returncode != 0
    assert "size cap" in result.stderr.lower()


def test_discourse_research_refuses_oversize_input(tmp_path: Path) -> None:
    """Write a real 26 MB JSON array; the script must refuse before parsing.

    Earlier versions of this test wrote a fixture that fell short of 25 MB
    on most systems and triggered pytest.skip, giving false coverage. Now
    we write a 26 MB-guaranteed payload by repeating a 27-byte item enough
    times to exceed the cap. The hard assertion at the end ensures the
    skip path can never silently re-enter.
    """
    big = tmp_path / "huge.json"
    item = b'{"k":"' + b"a" * 25 + b'"},'  # 34 bytes including comma
    repeats = (26 * 1024 * 1024) // len(item) + 100  # comfortably over 26 MB
    big.write_bytes(b"[" + item * repeats + b'{"k":"end"}]')
    assert big.stat().st_size > 25 * 1024 * 1024, (
        f"fixture too small ({big.stat().st_size} bytes); cannot test the cap"
    )
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(big),
        "--topic", "test",
        "--format", "json",
    ])
    assert result.returncode != 0
    assert "size cap" in result.stderr.lower()


# ---------------------------------------------------------------------------
# v1.8.1 regression tests: parse_engagement, RecursionError, type confusion,
# URL/title injection, specifics recency, overloaded-classification strictness
# ---------------------------------------------------------------------------


def test_parse_engagement_does_not_match_kmb_in_english_words(tmp_path: Path) -> None:
    """Regression for FIND-001: 'engagement_proxy: 5 best ideas' must NOT
    return 5 billion. Common English words starting with k/m/b after numbers
    were silently inflating engagement by orders of magnitude in v1.8.0.
    """
    import datetime as dt
    today = dt.date.today()
    recent = (today - dt.timedelta(days=5)).isoformat()
    inp = tmp_path / "kmb_traps.json"
    items = [
        {"platform": "reddit", "url": "https://reddit.com/a", "title": "A",
         "snippet": "Snippet A", "date": recent, "engagement_proxy": "5 best ideas"},
        {"platform": "reddit", "url": "https://reddit.com/b", "title": "B",
         "snippet": "Snippet B", "date": recent, "engagement_proxy": "10 books read"},
        {"platform": "reddit", "url": "https://reddit.com/c", "title": "C",
         "snippet": "Snippet C", "date": recent, "engagement_proxy": "200 buy"},
        {"platform": "reddit", "url": "https://reddit.com/d", "title": "D",
         "snippet": "Snippet D", "date": recent, "engagement_proxy": "1.5k upvotes"},
    ]
    inp.write_text(json.dumps(items), encoding="utf-8")
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(inp), "--topic", "kmb regression",
        "--format", "json",
    ])
    assert result.returncode == 0, f"stderr={result.stderr!r}"
    # The buggy parser would have made "5 best" score 5,000,000,000 vs the
    # correctly-suffixed "1.5k" at 1,500, ranking the bug version FIRST.
    # With the fix, "1.5k upvotes" parses to 1500 (anchored k) and beats
    # "5 best ideas" (suffix-anchor rejects 'b' → 5). The brief still runs
    # without engagement-driven catastrophe.
    brief = json.loads(result.stdout)
    assert brief["source_count"] == 4
    # No item should be silently inflated to billions in the breakdown
    assert "platform_breakdown" in brief


def test_discourse_research_refuses_deeply_nested_json(tmp_path: Path) -> None:
    """Regression for FIND-002: a JSON whose array depth exceeds
    MAX_JSON_DEPTH must be refused with a nesting-cap error before any
    recursion danger downstream.
    """
    inp = tmp_path / "deep.json"
    # Build a 200-deep nested array of integers (valid JSON, just deeply
    # nested). MAX_JSON_DEPTH=50 in the script, so 200 must trigger the cap.
    nested = "0"
    for _ in range(200):
        nested = "[" + nested + "]"
    payload = (
        '[{"platform":"web","url":"https://example.com","title":"T",'
        f'"snippet":"deep","extra":{nested}}}]'
    )
    inp.write_text(payload, encoding="utf-8")
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(inp), "--topic", "depth regression",
    ])
    assert result.returncode != 0
    err = result.stderr.lower()
    assert ("nesting depth" in err or "recursion" in err), (
        f"expected nesting / recursion message; got: {result.stderr!r}"
    )


def test_discourse_research_rejects_non_string_required_fields(tmp_path: Path) -> None:
    """Regression for FIND-003: a schema-valid item with non-string types
    on required fields must be rejected, not silently propagate to .lower()
    or .strip() crashes downstream.
    """
    inp = tmp_path / "wrong_types.json"
    payload = '[{"platform":"reddit","url":"https://example.com","title":12345,"snippet":"ok"}]'
    inp.write_text(payload, encoding="utf-8")
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(inp), "--topic", "type-confusion regression",
    ])
    assert result.returncode != 0
    assert "must be string" in result.stderr.lower()


def test_discourse_research_rejects_non_http_url_scheme(tmp_path: Path) -> None:
    """Regression for FIND-019: javascript:/file:/data: URLs must be refused
    at item-validation time. Defense-in-depth: render_inline_link _also_
    drops them, but rejecting at validation prevents them entering the
    pipeline at all.
    """
    for scheme_payload in (
        '"url":"javascript:alert(1)"',
        '"url":"file:///etc/passwd"',
        '"url":"data:text/html;base64,PHA+"',
    ):
        inp = tmp_path / "bad_url.json"
        payload = (
            '[{"platform":"reddit",' + scheme_payload
            + ',"title":"T","snippet":"S"}]'
        )
        inp.write_text(payload, encoding="utf-8")
        result = _run([
            sys.executable, str(DISCOURSE),
            "--input", str(inp), "--topic", "url-scheme regression",
        ])
        assert result.returncode != 0, f"accepted {scheme_payload!r}"
        assert "url scheme" in result.stderr.lower()


def test_discourse_research_sanitizes_brackets_in_title(tmp_path: Path) -> None:
    """Regression for FIND-004: a title containing `]` would terminate the
    markdown link early and let an attacker inject a clickable link. The
    attacker URL is allowed to appear as ESCAPED literal text (markdown
    parsers will render it as plain text inside the safe.com link), but
    it must NOT form a separate clickable `](URL)` pattern.
    """
    import datetime as dt
    import re as _re
    today = dt.date.today()
    recent = (today - dt.timedelta(days=2)).isoformat()
    inp = tmp_path / "bracket_inj.json"
    payload = json.dumps([{
        "platform": "reddit",
        "url": "https://safe.com/a",
        "title": "Innocent [escape](https://attacker.com) text",
        "snippet": "Also [evil-in-snippet](https://attacker.com/2) here",
        "date": recent,
    }])
    inp.write_text(payload, encoding="utf-8")
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(inp), "--topic", "bracket-injection regression",
        "--format", "json",
    ])
    assert result.returncode == 0, f"stderr={result.stderr!r}"
    brief = json.loads(result.stdout)
    md = brief["markdown"]
    # The safe URL must be the clickable target.
    assert "(https://safe.com/a)" in md
    # No UNESCAPED markdown-link pointing to attacker.com may exist.
    # Pattern: `]( ... attacker.com ... )` where the `]` is NOT preceded
    # by a backslash. The (?<!\\) lookbehind enforces escape detection.
    unescaped_attacker_link = _re.search(
        r"(?<!\\)\]\([^)]*attacker\.com[^)]*\)", md
    )
    assert unescaped_attacker_link is None, (
        f"attacker URL forms an unescaped clickable link: "
        f"{unescaped_attacker_link.group()!r} in:\n{md}"
    )


def test_discourse_research_escapes_raw_html_text(tmp_path: Path) -> None:
    """SERP title, snippet, and platform text must not render raw HTML."""
    import datetime as dt
    today = dt.date.today()
    recent = (today - dt.timedelta(days=2)).isoformat()
    inp = tmp_path / "raw_html.json"
    payload = json.dumps([{
        "platform": "web<script>alert(1)</script>",
        "url": "https://safe.example/source",
        "title": "Title <b>bad</b> & more",
        "snippet": "config <img src=x onerror=alert(1)> & details",
        "date": recent,
    }])
    inp.write_text(payload, encoding="utf-8")
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(inp), "--topic", "raw html regression",
        "--format", "json",
    ])
    assert result.returncode == 0, f"stderr={result.stderr!r}"
    md = json.loads(result.stdout)["markdown"]
    assert "<b>bad</b>" not in md
    assert "<img src=x" not in md
    assert "<script>alert(1)</script>" not in md
    assert "Title &lt;b&gt;bad&lt;/b&gt; &amp; more" in md
    assert "config &lt;img src=x onerror=alert(1)&gt; &amp; details" in md


def test_skill_md_documents_untrusted_data_contract(tmp_path: Path) -> None:
    """DOCUMENTATION-PRESENCE regression guard for skills/blog/SKILL.md.

    This is NOT a behavioral test. It asserts the markdown contract has not
    been silently weakened by a future edit. It verifies the orchestrator
    instruction file contains the load-bearing terms.

    For the BEHAVIORAL test of the v1.8.3 nonce defense (proves nonces are
    actually generated and unique per load), see
    tests/test_load_untrusted_root.py - that test exercises
    scripts/load_untrusted_root.py directly. The helper is the code-enforced
    layer; this test is the doc-presence layer.
    """
    orchestrator = (ROOT / "skills" / "blog" / "SKILL.md").read_text(encoding="utf-8")
    # Load-bearing phrases that MUST be present
    must_have_exact = [
        "Untrusted-Data Contract",
        "indirect prompt-injection",
        "Sanitize",
        "nonce",  # v1.8.2 per-load random nonce hardening
        "secrets.token_hex",  # specifies the nonce-generation API
        "load_untrusted_root.py",  # v1.8.3 code-enforced helper reference
        "OUTERMOST",  # v1.8.4 outer-nonce authority instruction (5TH-AUDIT-006)
    ]
    for phrase in must_have_exact:
        assert phrase in orchestrator, (
            f"Untrusted-Data Contract weakened: missing load-bearing phrase {phrase!r}"
        )
    must_have_caseinsensitive = [
        "tool-boundary",
        "platform-enforced",  # v1.8.3 honesty: explicit enforcement-class
        "code-enforced",       # v1.8.3 honesty: explicit enforcement-class
        "must",                 # at least one MUST imperative
    ]
    low = orchestrator.lower()
    for phrase in must_have_caseinsensitive:
        assert phrase in low, (
            f"Untrusted-Data Contract weakened: missing load-bearing phrase {phrase!r}"
        )
    # Anti-phrases that must NOT appear (would indicate weakening)
    forbidden = [
        "fence is advisory",
        "may be relaxed",
        "skip fencing",
        "trusted by default",
    ]
    for phrase in forbidden:
        assert phrase not in low, (
            f"Untrusted-Data Contract weakened: contains escape-hatch {phrase!r}"
        )


def test_load_untrusted_root_helper_exists() -> None:
    """The v1.8.3 nonce defense is code-enforced via a Python helper.
    If the helper file is removed, the defense degrades to instruction-only
    (the v1.8.2 state). This test surfaces such a regression.
    """
    helper = ROOT / "scripts" / "load_untrusted_root.py"
    assert helper.exists(), (
        "scripts/load_untrusted_root.py missing; v1.8.3 nonce defense "
        "would silently degrade to instruction-only. See "
        "tests/test_load_untrusted_root.py for behavioral coverage."
    )


# ---------------------------------------------------------------------------
# JSON schema validation
# ---------------------------------------------------------------------------


def test_discourse_research_rejects_non_array_input(tmp_path: Path) -> None:
    inp = tmp_path / "not_array.json"
    inp.write_text('{"not": "an array"}', encoding="utf-8")
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(inp),
        "--topic", "test",
    ])
    assert result.returncode != 0
    assert "must be a json array" in result.stderr.lower()


def test_discourse_research_rejects_item_missing_required_fields(tmp_path: Path) -> None:
    inp = tmp_path / "malformed.json"
    inp.write_text(json.dumps([{"platform": "reddit"}]), encoding="utf-8")  # missing url/title/snippet
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(inp),
        "--topic", "test",
    ])
    assert result.returncode != 0
    assert "missing required fields" in result.stderr.lower()


def test_discourse_research_rejects_too_many_items(tmp_path: Path) -> None:
    """MAX_ITEMS cap prevents pathological clustering complexity."""
    items = [
        {"platform": "web", "url": f"https://x.com/{i}", "title": f"t{i}", "snippet": "s"}
        for i in range(10_001)
    ]
    inp = tmp_path / "too_many.json"
    inp.write_text(json.dumps(items), encoding="utf-8")
    result = _run([
        sys.executable, str(DISCOURSE),
        "--input", str(inp),
        "--topic", "test",
    ])
    assert result.returncode != 0
    assert "exceeds cap" in result.stderr.lower()


# ---------------------------------------------------------------------------
# Prompt-injection guard documentation (orchestrator contract)
# ---------------------------------------------------------------------------


def test_orchestrator_has_untrusted_data_contract() -> None:
    """skills/blog/SKILL.md must document the project-root file fencing contract.

    Regression guard: if this section is ever removed or weakened, the
    indirect prompt-injection defense for BRAND.md / VOICE.md / DISCOURSE.md
    auto-load is gone. The section must mention all three files and the
    'untrusted-data' / 'fence' concepts.
    """
    orchestrator = (ROOT / "skills" / "blog" / "SKILL.md").read_text(encoding="utf-8")
    assert "Untrusted-Data Contract" in orchestrator, (
        "skills/blog/SKILL.md is missing the 'Untrusted-Data Contract' section "
        "that fences project-root files against prompt injection."
    )
    for f in ("BRAND.md", "VOICE.md", "DISCOURSE.md"):
        assert f in orchestrator, f"orchestrator does not mention {f}"
    # Must instruct fencing
    assert "BEGIN UNTRUSTED PROJECT-ROOT CONTEXT" in orchestrator, (
        "orchestrator does not specify the fence-block format for untrusted "
        "project-root content."
    )
    # Must instruct sanitization
    assert "ignore previous" in orchestrator.lower(), (
        "orchestrator does not list the 'ignore previous' injection pattern "
        "in its sanitization scan."
    )


def test_security_md_documents_t12() -> None:
    """SECURITY.md must include the T12 trust boundary (project-root auto-load)."""
    sec = (ROOT / ".github" / "SECURITY.md").read_text(encoding="utf-8")
    assert "T12" in sec, "SECURITY.md missing T12 trust boundary"
    assert "BRAND.md" in sec and "DISCOURSE.md" in sec, (
        "SECURITY.md T12 section missing references to BRAND.md / DISCOURSE.md"
    )


# ---------------------------------------------------------------------------
# License compliance (regression guard)
# ---------------------------------------------------------------------------


def test_notice_file_exists_and_credits_apache_sources() -> None:
    """NOTICE file must exist and credit impeccable (Apache 2.0)."""
    notice = ROOT / "NOTICE"
    assert notice.exists(), "NOTICE file is missing (required for Apache 2.0 attribution)"
    text = notice.read_text(encoding="utf-8")
    assert "impeccable" in text, "NOTICE does not credit impeccable"
    assert "Paul Bakaus" in text, "NOTICE does not credit Paul Bakaus"
    assert "Apache License" in text or "Apache 2.0" in text, (
        "NOTICE does not reference the Apache License"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
