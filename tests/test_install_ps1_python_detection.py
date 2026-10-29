"""install.ps1 must not accept the first python on PATH blindly (Microsoft Store stubs)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = (ROOT / "install.ps1").read_text(encoding="utf-8")


def _function(name: str) -> str:
    start = INSTALL.index(f"function {name}")
    end = INSTALL.find("\nfunction ", start + 1)
    return INSTALL[start:] if end < 0 else INSTALL[start:end]


def test_main_uses_the_validating_finder_not_a_bare_get_command() -> None:
    main = _function("Main")
    assert "$PythonCmd = Find-Python311" in main
    assert "Get-Command python3" not in main
    assert "Get-Command python " not in main


def test_finder_tries_python_python3_and_py_and_tests_each() -> None:
    finder = _function("Find-Python311")
    assert '@("python", "python3", "py")' in finder
    assert "Test-Python311 $candidate" in finder
    assert "-CommandType Application" in finder
    # Falls back to the first candidate so the existing warning paths still work.
    assert "return $first" in finder
