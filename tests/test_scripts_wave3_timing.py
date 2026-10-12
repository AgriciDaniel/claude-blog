"""Wave 3 regression tests: unclosed Markdown link syntax must not go quadratic."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FRONT = "---\ntitle: Timing\ndescription: Pathological input.\ndate: 2026-01-01\n---\n\n# Timing\n\n"
# Measured after the fix: about 1 s for 20,000 repeats. Before it, the first two
# payloads took over 15 s and style_learn did not finish in minutes.
PAYLOADS = {
    "open-bracket": "[" * 20000,
    "image-open": "![" * 20000,
    "link-open": "[x](" * 20000,
    "image-link-open": "![x](" * 20000,
}
LIMIT = 20  # seconds; a quadratic regression blows far past this


def _post(tmp_path, payload):
    path = tmp_path / "post.md"
    path.write_text(FRONT + payload + "\n", encoding="utf-8")
    return path


def _run(code, *args, cwd=None):
    start = time.monotonic()
    result = subprocess.run(
        [sys.executable, "-c", code, *map(str, args)],
        capture_output=True, text=True, timeout=LIMIT, cwd=cwd,
    )
    return result, time.monotonic() - start


@pytest.mark.parametrize("name", PAYLOADS)
def test_analyze_blog_is_time_bounded(tmp_path, name):
    post = _post(tmp_path, PAYLOADS[name])
    code = f"import sys; sys.path.insert(0, {str(SCRIPTS)!r}); import analyze_blog; analyze_blog.analyze_file(sys.argv[1])"
    result, elapsed = _run(code, post)
    assert result.returncode == 0, result.stderr[-500:]
    assert elapsed < LIMIT


@pytest.mark.parametrize("name", PAYLOADS)
def test_ai_citation_score_is_time_bounded(tmp_path, name):
    post = _post(tmp_path, PAYLOADS[name])
    code = f"import sys; sys.path.insert(0, {str(SCRIPTS)!r}); import ai_citation_score; ai_citation_score.score_file(sys.argv[1])"
    result, elapsed = _run(code, post)
    assert result.returncode == 0, result.stderr[-500:]


@pytest.mark.parametrize("name", PAYLOADS)
def test_quality_gate_is_time_bounded(tmp_path, name):
    post = _post(tmp_path, PAYLOADS[name])
    code = f"import sys; sys.path.insert(0, {str(SCRIPTS)!r}); import quality_gate; sys.exit(quality_gate.main([sys.argv[1], '--format', 'json']))"
    result, _ = _run(code, post)
    assert result.returncode in (0, 1), result.stderr[-500:]  # finished, pass or fail


@pytest.mark.parametrize("name", PAYLOADS)
def test_style_learn_is_time_bounded(tmp_path, name):
    post = _post(tmp_path, PAYLOADS[name])
    code = f"import sys; sys.path.insert(0, {str(SCRIPTS)!r}); import style_learn; style_learn.learn_style([sys.argv[1]])"
    result, _ = _run(code, post)
    assert result.returncode == 0, result.stderr[-500:]
