"""Behavioral tests for scripts/lint_prose.py.

The v1.8.4 release shipped lint_prose.py to CI with zero behavioral test
coverage (6TH-AUDIT-005). This test suite exercises the linter's core
state machine: code-fence toggling, inline backtick masking, YAML
frontmatter handling, allowlist application, and the violation set
(em-dash U+2014, en-dash U+2013, ASCII space-double-hyphen-space).

Stdlib + pytest only. No network.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LINTER = ROOT / "scripts" / "lint_prose.py"


def _import_linter():
    spec = importlib.util.spec_from_file_location("lint_prose", LINTER)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _run_cli(root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(LINTER), "--root", str(root), *extra],
        capture_output=True, text=True, check=False,
    )


# ---------------------------------------------------------------------------
# Core violation detection
# ---------------------------------------------------------------------------


def test_clean_file_has_zero_violations(tmp_path: Path):
    mod = _import_linter()
    f = tmp_path / "doc.md"
    f.write_text("# Title\n\nNormal prose with commas, semicolons, and colons.\n",
                 encoding="utf-8")
    assert mod.lint_file(f) == []


def test_em_dash_in_prose_flagged(tmp_path: Path):
    mod = _import_linter()
    f = tmp_path / "doc.md"
    f.write_text("# Title\n\nThis is bad \u2014 really bad.\n", encoding="utf-8")
    violations = mod.lint_file(f)
    assert len(violations) == 1
    assert violations[0][1] == "\u2014"
    assert violations[0][0] == 3  # line 3


def test_en_dash_in_prose_flagged(tmp_path: Path):
    mod = _import_linter()
    f = tmp_path / "doc.md"
    f.write_text("Range 1\u201340 not allowed.\n", encoding="utf-8")
    violations = mod.lint_file(f)
    assert len(violations) == 1
    assert violations[0][1] == "\u2013"


def test_ascii_double_hyphen_in_prose_flagged(tmp_path: Path):
    mod = _import_linter()
    f = tmp_path / "doc.md"
    f.write_text("Bad use" + "\x20--\x20" + "like this.\n", encoding="utf-8")
    violations = mod.lint_file(f)
    assert len(violations) == 1
    assert violations[0][1] == "\x20--\x20"


# ---------------------------------------------------------------------------
# Code fence + backtick masking
# ---------------------------------------------------------------------------


def test_em_dash_inside_triple_backtick_fence_not_flagged(tmp_path: Path):
    mod = _import_linter()
    f = tmp_path / "doc.md"
    f.write_text(
        "# Title\n\n"
        "```\n"
        "code with \u2014 em-dash inside\n"
        "```\n",
        encoding="utf-8",
    )
    assert mod.lint_file(f) == []


def test_em_dash_inside_inline_backtick_not_flagged(tmp_path: Path):
    mod = _import_linter()
    f = tmp_path / "doc.md"
    f.write_text("The `\u2014` character is forbidden in prose.\n", encoding="utf-8")
    assert mod.lint_file(f) == []


def test_em_dash_outside_backtick_on_same_line_still_flagged(tmp_path: Path):
    """A line with an em-dash inside backticks AND another outside must
    still flag the outside one."""
    mod = _import_linter()
    f = tmp_path / "doc.md"
    f.write_text("Use `\u2014` (em-dash) sparingly \u2014 actually, never.\n",
                 encoding="utf-8")
    violations = mod.lint_file(f)
    assert len(violations) == 1, f"expected 1, got {violations}"


def test_tilde_fence_also_recognized(tmp_path: Path):
    """`~~~` is an alternative markdown fence delimiter."""
    mod = _import_linter()
    f = tmp_path / "doc.md"
    f.write_text(
        "~~~\n"
        "em-dash \u2014 inside tilde fence\n"
        "~~~\n",
        encoding="utf-8",
    )
    assert mod.lint_file(f) == []


# ---------------------------------------------------------------------------
# YAML frontmatter + allowlist
# ---------------------------------------------------------------------------


def test_frontmatter_delimiters_not_misparsed_as_violations(tmp_path: Path):
    """`---` in YAML frontmatter must not trip the ASCII double-hyphen check
    (frontmatter delimiter is 3 dashes, no surrounding spaces)."""
    mod = _import_linter()
    f = tmp_path / "doc.md"
    f.write_text(
        "---\n"
        "name: example\n"
        "description: prose without violations\n"
        "---\n"
        "\n"
        "Body text.\n",
        encoding="utf-8",
    )
    assert mod.lint_file(f) == []


def test_frontmatter_scalar_fields_are_linted(tmp_path: Path):
    """Scalar frontmatter prose is subject to prose rules."""
    mod = _import_linter()
    f = tmp_path / "doc.md"
    f.write_text(
        "---\n"
        "description: this is \u2014 fine in frontmatter\n"
        "---\n"
        "\n"
        "Body text.\n",
        encoding="utf-8",
    )
    violations = mod.lint_file(f)
    assert len(violations) == 1
    assert violations[0][0] == 2


def test_test_files_are_not_whole_file_allowlisted(tmp_path: Path):
    """Intentional fixtures must encode forbidden characters, not bypass files."""
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_discourse_research.py").write_text(
        '"""\nintentional \u2014 em-dash\n"""\n', encoding="utf-8"
    )
    result = _run_cli(tmp_path)
    assert "test_discourse_research.py" in result.stdout
    assert result.returncode == 1


# ---------------------------------------------------------------------------
# CLI behaviour
# ---------------------------------------------------------------------------


def test_cli_clean_repo_returns_zero(tmp_path: Path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "x.py").write_text(
        "# clean prose\nx = 1\n", encoding="utf-8"
    )
    result = _run_cli(tmp_path)
    assert result.returncode == 0
    assert "OK" in result.stdout


def test_cli_dirty_repo_returns_one(tmp_path: Path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "bad.py").write_text(
        '"""Bad: em-dash \u2014 in docstring."""\n', encoding="utf-8"
    )
    result = _run_cli(tmp_path)
    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "bad.py" in result.stdout


def test_cli_reports_file_and_line(tmp_path: Path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "doc.md").write_text(
        "Line one is clean.\n"
        "Line two has \u2014 em-dash.\n",
        encoding="utf-8",
    )
    result = _run_cli(tmp_path)
    assert result.returncode == 1
    assert "docs/doc.md:2" in result.stdout


def test_cli_json_output(tmp_path: Path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "doc.md").write_text("Bad \u2014 prose.\n", encoding="utf-8")
    result = _run_cli(tmp_path, "--format", "json")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["violations"][0]["path"] == "docs/doc.md"


# ---------------------------------------------------------------------------
# Edge cases (6TH-AUDIT-006, 6TH-AUDIT-007 from prior audit; documented)
# ---------------------------------------------------------------------------


def test_crlf_line_endings_handled(tmp_path: Path):
    """Files written with Windows CRLF line endings must still be parsed
    correctly. The linter splits on \\n via splitlines()."""
    mod = _import_linter()
    f = tmp_path / "doc.md"
    # Encode literal em-dash via utf-8 to avoid bytes-literal ASCII restriction.
    f.write_bytes(b"# Title\r\n\r\nProse " + "\u2014".encode("utf-8") + b" em-dash\r\n")
    violations = mod.lint_file(f)
    assert len(violations) == 1


def test_double_backtick_span_masks_inner_chars(tmp_path: Path):
    """6TH-AUDIT-007 regression: ``content with ` and \u2014 em-dash`` is a
    valid markdown double-backtick code span. The em-dash inside must
    not be flagged. v1.8.4 single-backtick regex matched the empty span
    between two opening backticks, leaving the em-dash exposed."""
    mod = _import_linter()
    f = tmp_path / "doc.md"
    f.write_text(
        "Use `` `code with \u2014 em-dash` `` in prose.\n",
        encoding="utf-8",
    )
    assert mod.lint_file(f) == [], (
        "em-dash inside double-backtick span leaked through (6TH-AUDIT-007)"
    )


def test_nested_fence_delimiters_tracked_independently(tmp_path: Path):
    """6TH-AUDIT-006 regression: a ``` fence inside a ~~~ fence must
    not close the ~~~ fence. v1.8.4 used a single boolean toggle so
    nested or differently-delimited fences confused the state machine."""
    mod = _import_linter()
    f = tmp_path / "doc.md"
    f.write_text(
        "~~~\n"
        "outer fence body \u2014 em-dash here is hidden\n"
        "```\n"
        "inner pseudo-fence \u2014 em-dash also hidden\n"
        "```\n"
        "still inside outer \u2014 em-dash hidden\n"
        "~~~\n"
        "Now outside; em-dash here IS flagged: \u2014\n",
        encoding="utf-8",
    )
    violations = mod.lint_file(f)
    # Only the line AFTER the closing ~~~ should be flagged.
    assert len(violations) == 1, f"expected 1, got {violations}"
    assert violations[0][0] == 8


def test_four_backtick_fence_preserves_inner_three_backticks(tmp_path: Path):
    """7TH-AUDIT-013 regression: per CommonMark, a 4-backtick fence is
    closed only by 4+ backticks. An inner 3-backtick line is content,
    not a fence boundary. v1.8.5 used `startswith("```")` which matched
    both 3 and 4 backticks; nested fence inside ```` was closed
    prematurely, exposing em-dashes."""
    mod = _import_linter()
    f = tmp_path / "doc.md"
    f.write_text(
        "````\n"
        "outer 4-backtick fence \u2014 em-dash hidden\n"
        "```\n"
        "inner 3-backtick content \u2014 also hidden (still inside outer)\n"
        "```\n"
        "still inside outer \u2014 hidden\n"
        "````\n"
        "Now outside; em-dash flagged: \u2014\n",
        encoding="utf-8",
    )
    violations = mod.lint_file(f)
    assert len(violations) == 1, (
        f"4-backtick fence regression: expected 1 violation, got {violations}"
    )
    assert violations[0][0] == 8


def test_unclosed_fence_at_eof_does_not_crash(tmp_path: Path):
    """A markdown file with an unclosed code fence at EOF should not
    raise; the linter should treat the unclosed fence's content as
    inside-fence (silenced) and just exit cleanly."""
    mod = _import_linter()
    f = tmp_path / "doc.md"
    f.write_text(
        "Some prose.\n"
        "```\n"
        "unclosed code with \u2014 em-dash\n"
        "(no closing fence)\n",
        encoding="utf-8",
    )
    # Should not raise; should treat post-fence content as suppressed.
    violations = mod.lint_file(f)
    # Em-dash is inside the unclosed fence so it's suppressed.
    assert all(v[0] != 3 for v in violations)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
