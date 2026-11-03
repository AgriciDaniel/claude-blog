"""setup_environment scripts: pip failures show pip's stderr tail, and pip has a timeout."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("blog-google", "blog-audio", "blog-notebooklm")


def _env(skill: str, tmp_path: Path, monkeypatch):
    scripts = ROOT / "skills" / skill / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location(f"setup_env_{skill}", scripts / "setup_environment.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    env = module.SkillEnvironment()
    venv_dir = tmp_path / "venv"
    venv_dir.mkdir()
    env.venv_dir = venv_dir
    env.venv_pip = venv_dir / "pip"
    env.venv_python = venv_dir / "python"
    return module, env


@pytest.mark.parametrize("skill", SKILLS)
def test_pip_failure_prints_the_stderr_tail(skill, tmp_path, monkeypatch, capsys):
    module, env = _env(skill, tmp_path, monkeypatch)
    stderr = "\n".join(f"noise {i}" for i in range(50)) + "\nERROR: No matching distribution found for nothing"

    def fail(cmd, **kwargs):
        raise subprocess.CalledProcessError(1, cmd, output="", stderr=stderr)

    monkeypatch.setattr(module.subprocess, "run", fail)
    assert env.ensure_venv() is False
    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert "No matching distribution found for nothing" in text
    assert "noise 0\n" not in text  # only the tail, not the whole log


@pytest.mark.parametrize("skill", SKILLS)
def test_pip_runs_with_a_timeout_and_a_timeout_is_a_clean_failure(skill, tmp_path, monkeypatch, capsys):
    module, env = _env(skill, tmp_path, monkeypatch)
    seen = []

    def hang(cmd, **kwargs):
        seen.append(kwargs.get("timeout"))
        raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout"))

    monkeypatch.setattr(module.subprocess, "run", hang)
    assert env.ensure_venv() is False
    assert seen and seen[0] == module.PIP_TIMEOUT_SECONDS
    captured = capsys.readouterr()
    assert "did not finish" in captured.out + captured.err
    assert "Traceback" not in captured.out + captured.err


def test_output_tail_handles_none_bytes_and_long_text():
    spec = importlib.util.spec_from_file_location(
        "setup_env_tail", ROOT / "skills" / "blog-google" / "scripts" / "setup_environment.py"
    )
    # runtime_paths sits beside the script and is imported by it
    import sys

    sys.path.insert(0, str(ROOT / "skills" / "blog-google" / "scripts"))
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(ROOT / "skills" / "blog-google" / "scripts"))
    assert module._output_tail(None) == ""
    assert module._output_tail(b"a\nb") == "a\nb"
    assert module._output_tail("\n".join(str(i) for i in range(100)), lines=3) == "97\n98\n99"
