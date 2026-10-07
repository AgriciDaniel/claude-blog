"""Focused regressions for final-review renderer and wrapper findings."""

from __future__ import annotations

import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
RENDERER = ROOT / "scripts" / "blog_render.py"


def load_renderer():
    spec = importlib.util.spec_from_file_location("final_review_renderer", RENDERER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_render_fixture(root: Path) -> Path:
    source = root / "fixture.md"
    source.write_text(
        """---
title: Fixture
description: Final review renderer fixture.
date: 2026-10-07
author: Tester
---

Reader-visible body.
""",
        encoding="utf-8",
    )
    return source


def invoke_renderer(source: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(RENDERER),
            "--md",
            str(source),
            "--out-dir",
            str(output),
            "--pdf-engine",
            "none",
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_renderer_refuses_html_destination_symlink(tmp_path: Path) -> None:
    source = write_render_fixture(tmp_path)
    output = tmp_path / "out"
    output.mkdir()
    victim = output / "victim.html"
    victim.write_text("PRESERVE", encoding="utf-8")
    destination = output / "fixture.html"
    try:
        destination.symlink_to(victim.name)
    except OSError:
        pytest.skip("symlinks not supported on this filesystem")

    result = invoke_renderer(source, output)

    assert result.returncode == 1
    assert "symlink" in result.stderr.lower()
    assert destination.is_symlink()
    assert victim.read_text(encoding="utf-8") == "PRESERVE"


def test_renderer_refuses_symlink_in_output_ancestor(tmp_path: Path) -> None:
    source = write_render_fixture(tmp_path)
    real_output = tmp_path / "real-output"
    nested = real_output / "nested"
    nested.mkdir(parents=True)
    linked_output = tmp_path / "linked-output"
    try:
        linked_output.symlink_to(real_output, target_is_directory=True)
    except OSError:
        pytest.skip("symlinks not supported on this filesystem")

    result = invoke_renderer(source, linked_output / "nested")

    assert result.returncode == 1
    assert "symlink path component" in result.stderr.lower()
    assert not (nested / "fixture.html").exists()


def test_renderer_atomically_replaces_regular_html_output(tmp_path: Path) -> None:
    source = write_render_fixture(tmp_path)
    output = tmp_path / "out"
    output.mkdir()
    destination = output / "fixture.html"
    destination.write_text("old regular output", encoding="utf-8")

    result = invoke_renderer(source, output)

    assert result.returncode == 0, result.stderr
    assert destination.is_file() and not destination.is_symlink()
    assert destination.read_text(encoding="utf-8").startswith("<!DOCTYPE html>")


def test_renderer_refuses_pdf_destination_symlink(monkeypatch, tmp_path: Path) -> None:
    renderer = load_renderer()
    html = tmp_path / "post.html"
    html.write_text("<h1>Fixture</h1>", encoding="utf-8")
    victim = tmp_path / "victim.pdf"
    victim.write_bytes(b"PRESERVE")
    destination = tmp_path / "post.pdf"
    try:
        destination.symlink_to(victim.name)
    except OSError:
        pytest.skip("symlinks not supported on this filesystem")
    monkeypatch.setattr(
        renderer,
        "_render_pdf_to_path",
        lambda *_args: pytest.fail("renderer must reject the destination before rendering"),
    )

    assert renderer._render_pdf(html, destination, "weasyprint") is False
    assert destination.is_symlink()
    assert victim.read_bytes() == b"PRESERVE"


def test_renderer_atomically_promotes_regular_pdf(monkeypatch, tmp_path: Path) -> None:
    renderer = load_renderer()
    html = tmp_path / "post.html"
    html.write_text("<h1>Fixture</h1>", encoding="utf-8")
    destination = tmp_path / "post.pdf"
    destination.write_bytes(b"old")

    def render(_html, temporary, _engine):
        temporary.write_bytes(b"%PDF-1.7\nfixture")
        return True

    monkeypatch.setattr(renderer, "_render_pdf_to_path", render)

    assert renderer._render_pdf(html, destination, "weasyprint") is True
    assert destination.read_bytes() == b"%PDF-1.7\nfixture"
    assert not destination.is_symlink()


def make_google_wrapper_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    skill = tmp_path / "blog-google"
    scripts = skill / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy2(ROOT / "skills/blog-google/scripts/run.py", scripts / "run.py")
    shutil.copy2(ROOT / "skills/blog-google/scripts/runtime_paths.py", scripts / "runtime_paths.py")
    command = scripts / "pagespeed_check.py"
    command.write_text("print('configured-ok')\n", encoding="utf-8")
    lock = scripts / "requirements.lock"
    lock.write_text("fixture lock\n", encoding="utf-8")
    setup_sentinel = skill / "setup-called"
    (scripts / "setup_environment.py").write_text(
        f"from pathlib import Path\nPath({str(setup_sentinel)!r}).write_text('called')\n",
        encoding="utf-8",
    )
    return skill, scripts, setup_sentinel


def install_fixture_interpreter(skill: Path) -> Path:
    interpreter_dir = skill / ".venv" / ("Scripts" if os.name == "nt" else "bin")
    interpreter_dir.mkdir(parents=True)
    executable = interpreter_dir / ("python.exe" if os.name == "nt" else "python")
    try:
        executable.symlink_to(sys.executable)
    except OSError:
        shutil.copy2(sys.executable, executable)
    return executable


def run_google_wrapper(scripts: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(scripts / "run.py"), "pagespeed_check.py"],
        capture_output=True,
        text=True,
        check=False,
    )


def test_google_wrapper_missing_environment_requires_explicit_setup(tmp_path: Path) -> None:
    skill, scripts, setup_sentinel = make_google_wrapper_fixture(tmp_path)

    result = run_google_wrapper(scripts)

    assert result.returncode == 1
    assert "setup required" in result.stdout.lower()
    assert "setup_environment.py" in result.stdout
    assert not setup_sentinel.exists()
    assert not (skill / ".venv").exists()


def test_google_wrapper_stale_environment_requires_explicit_setup(tmp_path: Path) -> None:
    skill, scripts, setup_sentinel = make_google_wrapper_fixture(tmp_path)
    install_fixture_interpreter(skill)
    (skill / ".venv" / ".requirements.stamp").write_text("stale", encoding="utf-8")

    result = run_google_wrapper(scripts)

    assert result.returncode == 1
    assert "missing or stale" in result.stdout.lower()
    assert "setup_environment.py" in result.stdout
    assert not setup_sentinel.exists()


def test_google_wrapper_ready_environment_runs_command(tmp_path: Path) -> None:
    skill, scripts, setup_sentinel = make_google_wrapper_fixture(tmp_path)
    install_fixture_interpreter(skill)
    lock = scripts / "requirements.lock"
    (skill / ".venv" / ".requirements.stamp").write_text(
        hashlib.sha256(lock.read_bytes()).hexdigest(), encoding="utf-8"
    )

    result = run_google_wrapper(scripts)

    assert result.returncode == 0, result.stderr
    assert "configured-ok" in result.stdout
    assert not setup_sentinel.exists()
