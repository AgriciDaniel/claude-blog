"""Blog Delivery Contract coherence regression test (v1.9.0).

Asserts that the contract spec at `skills/blog/references/blog-delivery-contract.md`
stays in sync with its implementation across scripts, skills, and the
reviewer agent. Same shape as v1.8.5's test_command_coherence and v1.8.6's
test_installer_sync. The contract is the source of truth; this test fails
loudly on drift.

The class of defect this prevents: contract documents Gate N but Gate N
is not actually wired into blog_preflight.py, or blog-reviewer.md does
not emit the BLOCKING line the contract requires, or blog-write/SKILL.md
forgets to mention the contract. Each is a Category-3 contradiction
between redundant surfaces.

Stdlib + pytest only.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT / "skills" / "blog" / "references" / "blog-delivery-contract.md"
PREFLIGHT_PATH = ROOT / "scripts" / "blog_preflight.py"
RENDER_PATH = ROOT / "scripts" / "blog_render.py"
HERO_PATH = ROOT / "scripts" / "generate_hero.py"
WRITE_SKILL = ROOT / "skills" / "blog-write" / "SKILL.md"
REWRITE_SKILL = ROOT / "skills" / "blog-rewrite" / "SKILL.md"
ORCHESTRATOR = ROOT / "skills" / "blog" / "SKILL.md"
REVIEWER = ROOT / "agents" / "blog-reviewer.md"
PYPROJECT = ROOT / "pyproject.toml"


def test_contract_file_exists() -> None:
    assert CONTRACT_PATH.is_file(), f"Delivery contract missing: {CONTRACT_PATH}"


def test_contract_declares_all_five_gates() -> None:
    text = CONTRACT_PATH.read_text(encoding="utf-8")
    expected = [
        "Gate 1: Capability Discovery",
        "Gate 2: Format Completeness",
        "Gate 3: Visual Verification",
        "Gate 4: Content Review",
        "Gate 5: Asset Existence + Link Integrity",
    ]
    for name in expected:
        assert name in text, f"Contract missing section: {name}"


def test_contract_declares_hero_image_ladder() -> None:
    text = CONTRACT_PATH.read_text(encoding="utf-8")
    rungs = ("Banana MCP", "Gemini", "Premium stock", "Openverse")
    for rung in rungs:
        assert rung in text, f"Contract missing hero ladder rung: {rung}"


def test_contract_declares_iteration_cap() -> None:
    text = CONTRACT_PATH.read_text(encoding="utf-8")
    assert "3 iteration" in text or "three iteration" in text or "max 3" in text.lower(), \
        "Contract must declare the 3-iteration cap"


def test_contract_declares_score_threshold() -> None:
    """The contract must declare BOTH the numeric 90 threshold and the P0
    filter in load-bearing context (not just somewhere on the page).
    Tightened in v1.9.0 hostile-review fix D2."""
    text = CONTRACT_PATH.read_text(encoding="utf-8")
    # Look for either "< 90", "≥ 90", or "90/100" within 60 chars of "P0" or
    # "BLOCK", to ensure the threshold is in the right context not in passing.
    threshold_patterns = [
        re.compile(r"(?:<|≥|>=|score)\s*90\b", re.IGNORECASE),
        re.compile(r"\b90/100\b"),
        re.compile(r"\bbelow\s*90\b", re.IGNORECASE),
    ]
    assert any(p.search(text) for p in threshold_patterns), (
        "Contract must declare the 90/100 threshold in load-bearing context "
        "(e.g. '< 90', 'score 90', '90/100', 'below 90')"
    )
    assert re.search(r"P0\b.*BLOCK|BLOCK.*P0|zero\s+P0", text, re.IGNORECASE), (
        "Contract must declare the zero-P0 blocking filter"
    )


def test_preflight_script_exists_and_has_cli() -> None:
    assert PREFLIGHT_PATH.is_file(), "scripts/blog_preflight.py missing"
    result = subprocess.run(
        [sys.executable, str(PREFLIGHT_PATH), "--help"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    for flag in ("--draft", "--gate", "--strict", "--no-strict", "--json"):
        assert flag in result.stdout, f"blog_preflight.py missing CLI flag: {flag}"


def test_render_script_exists_and_has_cli() -> None:
    assert RENDER_PATH.is_file(), "scripts/blog_render.py missing"
    result = subprocess.run(
        [sys.executable, str(RENDER_PATH), "--help"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    for flag in ("--md", "--out-dir", "--pdf-engine"):
        assert flag in result.stdout, f"blog_render.py missing CLI flag: {flag}"


def test_hero_script_exists_and_has_cli() -> None:
    assert HERO_PATH.is_file(), "scripts/generate_hero.py missing"
    result = subprocess.run(
        [sys.executable, str(HERO_PATH), "--help"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    for flag in ("--topic", "--out"):
        assert flag in result.stdout, f"generate_hero.py missing CLI flag: {flag}"


def test_preflight_implements_all_named_gates() -> None:
    """Every gate named in the contract must have a corresponding function
    in blog_preflight.py."""
    text = PREFLIGHT_PATH.read_text(encoding="utf-8")
    for fn in ("gate_1_capability_discovery", "gate_2_format_completeness",
               "gate_3_visual_verification", "gate_4_content_review",
               "gate_5_asset_link_integrity"):
        assert f"def {fn}" in text, f"blog_preflight.py missing function: {fn}"


def test_blog_write_skill_references_contract() -> None:
    text = WRITE_SKILL.read_text(encoding="utf-8")
    assert "blog-delivery-contract.md" in text, \
        "blog-write/SKILL.md must reference the delivery contract"
    assert "blog_preflight.py" in text, \
        "blog-write/SKILL.md must call blog_preflight.py"
    assert "blog-reviewer" in text, \
        "blog-write/SKILL.md must dispatch blog-reviewer"


def test_blog_rewrite_skill_references_contract() -> None:
    text = REWRITE_SKILL.read_text(encoding="utf-8")
    assert "blog-delivery-contract.md" in text, \
        "blog-rewrite/SKILL.md must reference the delivery contract"
    assert "blog_preflight.py" in text, \
        "blog-rewrite/SKILL.md must call blog_preflight.py"


def test_orchestrator_references_contract() -> None:
    text = ORCHESTRATOR.read_text(encoding="utf-8")
    assert "blog-delivery-contract.md" in text, \
        "skills/blog/SKILL.md must reference the delivery contract"
    assert re.search(r"\b6\.5\b|Step 6\.5", text), \
        "skills/blog/SKILL.md must declare Step 6.5 (Delivery Contract Enforcement)"


def test_reviewer_emits_blocking_line() -> None:
    text = REVIEWER.read_text(encoding="utf-8")
    assert "BLOCKING:" in text, \
        "agents/blog-reviewer.md must emit a `BLOCKING:` line in its scorecard"
    assert "Blocking Decision" in text or "Blocking decision" in text, \
        "agents/blog-reviewer.md must document the blocking decision rules"


def test_pyproject_declares_presentation_group() -> None:
    text = PYPROJECT.read_text(encoding="utf-8")
    assert "presentation" in text, \
        "pyproject.toml must declare an optional-deps `presentation` group"
    for dep in ("patchright", "weasyprint"):
        assert dep in text, \
            f"pyproject.toml `presentation` group must include {dep}"


def test_installers_ship_all_new_scripts() -> None:
    """The 3 new v1.9.0 scripts must be uninstall-aware (install.sh uses a
    glob, but uninstall.sh enumerates explicitly)."""
    uninstall_sh = (ROOT / "uninstall.sh").read_text(encoding="utf-8")
    uninstall_ps1 = (ROOT / "uninstall.ps1").read_text(encoding="utf-8")
    for script in ("blog_preflight.py", "blog_render.py", "generate_hero.py"):
        assert script in uninstall_sh, f"uninstall.sh missing {script}"
        assert script in uninstall_ps1, f"uninstall.ps1 missing {script}"


# ---------------------------------------------------------------------------
# Functional regression tests (v1.9.0 hostile-review fix D3).
# These tests actually invoke the scripts against synthesized fixtures and
# assert observable behaviour. They would have caught S1 (XSS), F1 (empty
# markdown), and F3 (H1 inline formatting) before review.
# ---------------------------------------------------------------------------

_VALID_FRONTMATTER = (
    '---\n'
    'title: "Fixture"\n'
    'description: "x"\n'
    'date: 2026-05-17\n'
    'author: "x"\n'
    '---\n'
)


def _render(tmp_path: Path, md_body: str, title: str = "Fixture") -> tuple[int, str, str, list[Path]]:
    """Invoke blog_render.py against a synthesized .md; return
    (returncode, stdout, stderr, list-of-html-files-emitted)."""
    md = tmp_path / "fixture.md"
    md.write_text(
        f'---\ntitle: "{title}"\ndescription: "x"\ndate: 2026-05-17\nauthor: "x"\n---\n{md_body}',
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(RENDER_PATH), "--md", str(md), "--out-dir", str(tmp_path),
         "--pdf-engine", "none"],
        capture_output=True, text=True, check=False,
    )
    htmls = list(tmp_path.glob("*.html"))
    return result.returncode, result.stdout, result.stderr, htmls


def test_xss_via_jsonld_is_escaped(tmp_path: Path) -> None:
    """S1 regression: a frontmatter title containing </script> must NOT
    appear unescaped in the rendered HTML's JSON-LD block."""
    rc, stdout, stderr, htmls = _render(
        tmp_path, "body content",
        title='x</script><script>alert(1)</script>',
    )
    assert rc == 0, f"render failed: rc={rc} stderr={stderr}"
    assert len(htmls) == 1
    rendered = htmls[0].read_text(encoding="utf-8")
    assert "</script><script>alert" not in rendered, (
        "XSS regression: an unescaped </script> from frontmatter title broke "
        "out of the JSON-LD <script> block."
    )
    # And confirm the JSON-LD still parses to the original headline string.
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', rendered, re.DOTALL)
    assert m, "JSON-LD block not present"
    parsed = json.loads(m.group(1))
    assert parsed.get("headline") == 'x</script><script>alert(1)</script>', (
        "JSON-LD headline should round-trip the original string after HTML-safe escape"
    )


def test_markdown_body_html_is_sanitized(tmp_path: Path) -> None:
    rc, _stdout, stderr, htmls = _render(
        tmp_path,
        '<script>alert(1)</script>\n'
        '<p onclick="alert(2)">Safe text</p>\n'
        '<img src="https://example.com/x.jpg" alt="bad" onerror="alert(4)">\n'
        '[bad](javascript:alert(3))\n'
        '![bad](data:text/html,evil)\n',
    )
    assert rc == 0, f"render failed: {stderr}"
    rendered = htmls[0].read_text(encoding="utf-8")
    assert "<script>alert" not in rendered.lower()
    assert "alert(1)" not in rendered.lower()
    assert "onclick" not in rendered.lower()
    assert "javascript:" not in rendered.lower()
    assert "data:text/html" not in rendered.lower()
    assert "onerror" not in rendered.lower()
    assert "alert(4)" not in rendered.lower()


def test_empty_md_is_rejected(tmp_path: Path) -> None:
    """F1 regression: empty markdown source must NOT produce empty HTML."""
    md = tmp_path / "empty.md"
    md.write_text("", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(RENDER_PATH), "--md", str(md), "--out-dir", str(tmp_path),
         "--pdf-engine", "none"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode != 0, "empty .md must fail with non-zero exit"
    assert "required frontmatter" in result.stderr or "empty" in result.stderr.lower()


def test_missing_frontmatter_keys_rejected(tmp_path: Path) -> None:
    """F2 regression: missing required frontmatter keys must fail loudly."""
    md = tmp_path / "partial.md"
    md.write_text('---\ntitle: "t"\n---\nbody\n', encoding="utf-8")  # missing date/desc/author
    result = subprocess.run(
        [sys.executable, str(RENDER_PATH), "--md", str(md), "--out-dir", str(tmp_path),
         "--pdf-engine", "none"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode != 0
    assert "missing" in result.stderr.lower()


def test_h1_strip_handles_inline_formatting(tmp_path: Path) -> None:
    """F3 regression: H1 with **bold** must still be deduplicated."""
    rc, _, stderr, htmls = _render(tmp_path, "# Title with **bold** word\nbody")
    assert rc == 0, f"render failed: {stderr}"
    rendered = htmls[0].read_text(encoding="utf-8")
    h1_count = len(re.findall(r"<h1\b", rendered))
    assert h1_count == 1, f"expected exactly 1 H1, got {h1_count}"


def test_symlink_to_md_is_refused(tmp_path: Path) -> None:
    """S2 regression: renderer must refuse to follow symlinks."""
    real = tmp_path / "real.md"
    real.write_text(_VALID_FRONTMATTER + "body\n", encoding="utf-8")
    link = tmp_path / "link.md"
    try:
        link.symlink_to(real)
    except OSError:
        pytest.skip("symlinks not supported on this filesystem")
    result = subprocess.run(
        [sys.executable, str(RENDER_PATH), "--md", str(link), "--out-dir", str(tmp_path),
         "--pdf-engine", "none"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode != 0
    assert "symlink" in result.stderr.lower()


def test_preflight_gate_2_blocks_on_missing_hero(tmp_path: Path) -> None:
    """Gate 2 regression: a draft folder without a hero.<ext> must FAIL
    Gate 2 (Format Completeness)."""
    (tmp_path / "post.md").write_text(_VALID_FRONTMATTER + "body\n", encoding="utf-8")
    (tmp_path / "post.html").write_text("<html></html>", encoding="utf-8")
    (tmp_path / "post.pdf").write_bytes(b"%PDF-1.4\n")
    # NOTE: no hero.<ext>
    result = subprocess.run(
        [sys.executable, str(PREFLIGHT_PATH), "--draft", str(tmp_path),
         "--gate", "2", "--no-strict"],
        capture_output=True, text=True, check=False,
    )
    assert "FAIL" in result.stdout and "Gate 2" in result.stdout
    assert "hero" in result.stdout.lower()


def test_preflight_gate_5_flags_non_http_scheme_as_violation(tmp_path: Path) -> None:
    """S3 regression: Gate 5 must flag file://, javascript:, data: links as
    violations rather than silently skipping them."""
    (tmp_path / "post.md").write_text(_VALID_FRONTMATTER + "body\n", encoding="utf-8")
    (tmp_path / "post.html").write_text(
        '<!DOCTYPE html><html><head>'
        '<link rel="canonical" href="https://example.com/post">'
        '<meta property="og:image" content="hero.png">'
        '<script type="application/ld+json">'
        '{"@type":"BlogPosting","headline":"x","image":"x","datePublished":"x",'
        '"author":{"name":"x"},"wordCount":1}'
        '</script></head><body><article>'
        '<a href="file:///etc/passwd">x</a>'
        '<a href="javascript:alert(1)">y</a>'
        'word</article></body></html>',
        encoding="utf-8",
    )
    (tmp_path / "post.pdf").write_bytes(b"%PDF-1.4\n")
    (tmp_path / "hero.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (tmp_path / "review.md").write_text("BLOCKING: false (test)", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(PREFLIGHT_PATH), "--draft", str(tmp_path),
         "--gate", "5", "--no-strict"],
        capture_output=True, text=True, check=False,
    )
    assert "non-http(s) URL scheme" in result.stdout
    assert "file:///etc/passwd" in result.stdout
    assert "javascript:" in result.stdout


def test_preflight_gate_2_rejects_symlink_artifact(tmp_path: Path) -> None:
    real = tmp_path / "real.md"
    real.write_text(_VALID_FRONTMATTER + "body\n", encoding="utf-8")
    link = tmp_path / "post.md"
    try:
        link.symlink_to(real)
    except OSError:
        pytest.skip("symlinks not supported on this filesystem")
    (tmp_path / "post.html").write_text("<html></html>", encoding="utf-8")
    (tmp_path / "post.pdf").write_bytes(b"%PDF-1.4\n")
    (tmp_path / "hero.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    result = subprocess.run(
        [sys.executable, str(PREFLIGHT_PATH), "--draft", str(tmp_path),
         "--gate", "2", "--no-strict"],
        capture_output=True, text=True, check=False,
    )
    assert "FAIL" in result.stdout and "Gate 2" in result.stdout
    assert "symlink artifact" in result.stdout


def test_preflight_gate_1_rejects_symlink_capabilities_output(tmp_path: Path) -> None:
    target = tmp_path / "capabilities-target.json"
    target.write_text("keep\n", encoding="utf-8")
    link = tmp_path / "capabilities.json"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlinks not supported on this filesystem")

    result = subprocess.run(
        [sys.executable, str(PREFLIGHT_PATH), "--draft", str(tmp_path),
         "--gate", "1", "--no-strict"],
        capture_output=True, text=True, check=False,
    )
    assert "FAIL" in result.stdout and "Gate 1" in result.stdout
    assert "capabilities.json write refused" in result.stdout
    assert target.read_text(encoding="utf-8") == "keep\n"


def test_preflight_rejects_symlink_report_output(tmp_path: Path) -> None:
    (tmp_path / "post.md").write_text(_VALID_FRONTMATTER + "body\n", encoding="utf-8")
    (tmp_path / "post.html").write_text("<html></html>", encoding="utf-8")
    (tmp_path / "post.pdf").write_bytes(b"%PDF-1.4\n")
    (tmp_path / "hero.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    target = tmp_path / "report-target.json"
    target.write_text("keep\n", encoding="utf-8")
    link = tmp_path / "preflight-report.json"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlinks not supported on this filesystem")

    result = subprocess.run(
        [sys.executable, str(PREFLIGHT_PATH), "--draft", str(tmp_path),
         "--gate", "2", "--no-strict"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 1
    assert "preflight-report.json write refused" in result.stderr
    assert target.read_text(encoding="utf-8") == "keep\n"


# ---------------------------------------------------------------------------
# Coherence test for the reference count across redundant surfaces (v1.9.0
# hostile-review fix for C1 / C2). Same shape as test_version_coherence.
# ---------------------------------------------------------------------------

def test_reference_count_coherence() -> None:
    """The number declared in skills/blog/SKILL.md must agree with the
    actual count in skills/blog/references/, and with the count claimed in
    docs/ARCHITECTURE.md and CLAUDE.md."""
    refs_dir = ROOT / "skills" / "blog" / "references"
    actual = sum(1 for p in refs_dir.iterdir() if p.is_file() and p.suffix == ".md")

    skill_text = (ROOT / "skills" / "blog" / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"Load on-demand as needed \((\d+) references", skill_text)
    assert m, "skills/blog/SKILL.md must declare reference count in the 'Load on-demand' line"
    declared_skill = int(m.group(1))
    assert declared_skill == actual, (
        f"skills/blog/SKILL.md says {declared_skill} references; filesystem has {actual}"
    )

    arch_text = (ROOT / "docs" / "ARCHITECTURE.md").read_text(encoding="utf-8")
    m = re.search(r"(\d+) references in `skills/blog/references/`", arch_text)
    assert m, "docs/ARCHITECTURE.md must declare reference count"
    declared_arch = int(m.group(1))
    assert declared_arch == actual, (
        f"docs/ARCHITECTURE.md says {declared_arch}; filesystem has {actual}"
    )

    claude_text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    m = re.search(r"(\d+) reference docs", claude_text)
    assert m, "CLAUDE.md must declare reference doc count"
    declared_claude = int(m.group(1))
    assert declared_claude == actual, (
        f"CLAUDE.md says {declared_claude}; filesystem has {actual}"
    )


def test_render_wordcount_matches_gate5_semantics(tmp_path: Path) -> None:
    """blog_render.py's wordCount injected into JSON-LD must use the SAME
    counting algorithm as blog_preflight.py Gate 5 (exclude <code> and
    <pre> content). v1.9.0 audit caught a 18.4% drift on docs containing
    code samples because render counted code-block tokens as prose words
    but preflight excluded them. Mismatch caused Gate 5 to fire as a
    false-positive blocker on every doc with code fences.
    """
    md = tmp_path / "with-code.md"
    # NB: explicit `+` before the multiplied string prevents Python's implicit
    # adjacent-literal concatenation from greedy-grabbing the entire literal
    # block and multiplying it by 5 (which would duplicate the frontmatter).
    md.write_text(
        (
            "---\n"
            "title: \"WordCount Coherence Fixture\"\n"
            "description: \"Tests render/preflight wordCount agreement.\"\n"
            "date: \"2026-05-18\"\n"
            "author: \"Test\"\n"
            "---\n"
            "\n"
        )
        + ("This is a paragraph with ten ordinary prose words. " * 5)
        + (
            "\n\n"
            "```python\n"
            "# A code block with many tokens that must NOT be counted as prose.\n"
            "def excluded():\n"
            "    return ['lots', 'of', 'tokens', 'inside', 'code', 'fences']\n"
            "```\n"
            "\n"
            "Closing prose paragraph.\n"
        ),
        encoding="utf-8",
    )
    out = tmp_path / "out"
    out.mkdir()
    result = subprocess.run(
        [sys.executable, str(RENDER_PATH), "--md", str(md),
         "--out-dir", str(out), "--pdf-engine", "none"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, f"render failed: {result.stderr}"
    html_path = out / "wordcount-coherence-fixture.html"
    assert html_path.exists(), f"render did not produce expected HTML: {list(out.iterdir())}"
    html = html_path.read_text(encoding="utf-8")
    m = re.search(r'"wordCount":\s*(\d+)', html)
    assert m, "JSON-LD must declare a wordCount"
    declared = int(m.group(1))
    # Hand-counted prose words in the fixture: 5 repetitions of an 11-word
    # sentence (55) + "Closing prose paragraph" (3) = 58. The code block must
    # NOT contribute. Allow generous slack for edge cases in tokenizing the
    # comment markers/punctuation; the only test is "didn't count the code".
    assert declared < 70, (
        f"declared wordCount={declared} suggests code-block content was "
        f"counted as prose. Expected ~58, max ~70."
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
