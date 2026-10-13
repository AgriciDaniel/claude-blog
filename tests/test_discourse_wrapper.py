"""The skill-local discourse_research.py is a thin wrapper over the core script.

The skill documents and runs scripts/discourse_research.py. A second, divergent
302-line copy under skills/blog-discourse/scripts/ used to exist; it is now a
wrapper (same pattern as skills/blog-flow/scripts/sync_flow.py), so there is one
implementation.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "scripts" / "discourse_research.py"
WRAPPER = ROOT / "skills" / "blog-discourse" / "scripts" / "discourse_research.py"

RESULTS = [
    {
        "platform": "reddit",
        "url": "https://example.com/a",
        "title": "Docker compose tips",
        "snippet": "Multi-stage builds cut the image size a lot.",
        "date": "2026-10-01",
    },
    {
        "platform": "hn",
        "url": "https://example.com/b",
        "title": "Docker compose tips discussion",
        "snippet": "Multi-stage builds are the main win for image size.",
        "date": "2026-10-02",
    },
]


def _run(script: Path, *args: str, cwd: Path, env: dict | None = None):
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True, text=True, cwd=cwd, env=env,
    )


def test_wrapper_has_no_second_implementation() -> None:
    source = WRAPPER.read_text(encoding="utf-8")
    assert "def build_brief" not in source
    assert "def load_results" not in source
    assert "def _atomic_write" not in source
    assert "ALLOWED_FIELDS" not in source
    assert len(source.splitlines()) < 90


def test_wrapper_output_matches_core(tmp_path: Path) -> None:
    results = tmp_path / "results.json"
    results.write_text(json.dumps(RESULTS), encoding="utf-8")
    args = ("--input", str(results), "--topic", "docker", "--format", "json")
    core = _run(CORE, *args, cwd=tmp_path)
    wrapper = _run(WRAPPER, *args, cwd=tmp_path)
    assert core.returncode == 0, core.stderr
    assert wrapper.returncode == 0, wrapper.stderr
    assert json.loads(wrapper.stdout) == json.loads(core.stdout)


def test_wrapper_keeps_the_documented_flags() -> None:
    result = _run(WRAPPER, "--help", cwd=ROOT)
    assert result.returncode == 0, result.stderr
    for flag in ("--input", "--topic", "--days", "--output", "--format", "--decomposition"):
        assert flag in result.stdout, flag


def test_wrapper_writes_output_like_the_core(tmp_path: Path) -> None:
    results = tmp_path / "results.json"
    results.write_text(json.dumps(RESULTS), encoding="utf-8")
    out = tmp_path / "DISCOURSE.md"
    result = _run(WRAPPER, "--input", str(results), "--topic", "docker", "--output", str(out), cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert out.read_text(encoding="utf-8").strip()


def test_wrapper_without_core_exits_with_a_pointer(tmp_path: Path) -> None:
    lone = tmp_path / "skills" / "blog-discourse" / "scripts"
    lone.mkdir(parents=True)
    shutil.copyfile(WRAPPER, lone / "discourse_research.py")
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_BLOG_SCRIPTS_DIR"}
    result = _run(lone / "discourse_research.py", "--help", cwd=tmp_path, env=env)
    assert result.returncode == 2
    assert "thin wrapper" in result.stderr
    assert "Traceback" not in result.stderr


def test_wrapper_rejects_a_relative_scripts_dir_override(tmp_path: Path) -> None:
    env = dict(os.environ, CLAUDE_BLOG_SCRIPTS_DIR="relative/scripts")
    result = _run(WRAPPER, "--help", cwd=tmp_path, env=env)
    assert result.returncode == 2
    assert "absolute" in result.stderr
