"""Code-enforced iteration counter tests (VULN-802, v1.9.1).

The 5-gate Blog Delivery Contract documents 'up to 3 retries before
escalating' but v1.9.0 enforced it only as orchestrator prose. This
suite locks in the file-backed counter at <draft>/.iteration-count
that survives across preflight invocations.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PREFLIGHT = ROOT / "scripts" / "blog_preflight.py"


def _make_minimal_draft(tmp: Path) -> Path:
    """Create a draft folder skeleton sufficient for preflight to run.

    Note: preflight will likely fail Gate 1-5 on this minimal draft.
    That's intentional; the counter test only cares about iteration
    bookkeeping, not gate outcomes.
    """
    draft = tmp / "post"
    draft.mkdir()
    (draft / "post.md").write_text(
        "---\ntitle: t\ndescription: d\n---\n# t\nbody\n",
        encoding="utf-8",
    )
    return draft


def _run_preflight(draft: Path, *extra) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(PREFLIGHT), "--draft", str(draft), "--no-strict", *extra]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))


def test_normal_run_does_not_create_counter(tmp_path):
    draft = _make_minimal_draft(tmp_path)
    assert not (draft / ".iteration-count").exists()
    _run_preflight(draft)
    assert not (draft / ".iteration-count").exists()


def test_first_repair_attempt_creates_counter_at_one(tmp_path):
    draft = _make_minimal_draft(tmp_path)
    _run_preflight(draft, "--repair-attempt")
    counter_file = draft / ".iteration-count"
    assert counter_file.exists()
    assert counter_file.read_text(encoding="utf-8").strip() == "1"


def test_three_runs_accumulate_to_three(tmp_path):
    draft = _make_minimal_draft(tmp_path)
    for _ in range(3):
        _run_preflight(draft, "--repair-attempt")
    assert (draft / ".iteration-count").read_text(encoding="utf-8").strip() == "3"


def test_fourth_run_exits_with_code_two(tmp_path):
    draft = _make_minimal_draft(tmp_path)
    for _ in range(3):
        _run_preflight(draft, "--repair-attempt")
    result = _run_preflight(draft, "--repair-attempt")
    assert result.returncode == 2, (
        f"expected exit 2 (iteration cap), got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "ITERATION CAP" in result.stderr.upper() or "iteration" in result.stderr.lower()


def test_reset_iterations_flag_resets_counter(tmp_path):
    draft = _make_minimal_draft(tmp_path)
    for _ in range(3):
        _run_preflight(draft, "--repair-attempt")
    # 4th would refuse; --reset-iterations clears and allows a fresh run.
    result = _run_preflight(draft, "--reset-iterations", "--repair-attempt")
    assert result.returncode != 2, (
        f"--reset-iterations should allow a fresh run, got exit {result.returncode}"
    )
    assert (draft / ".iteration-count").read_text(encoding="utf-8").strip() == "1"


def test_corrupted_counter_file_resets_to_one(tmp_path):
    """Tampered counter file (non-int) is treated as 0 and run proceeds.

    Fail-soft: an attacker who can write to the draft folder already has
    bigger problems (can write review.md, modify the .md). Refusing to
    run on garbage counter would create a self-DoS vector.
    """
    draft = _make_minimal_draft(tmp_path)
    (draft / ".iteration-count").write_text("not-an-int", encoding="utf-8")
    result = _run_preflight(draft, "--repair-attempt")
    assert result.returncode != 2
    assert (draft / ".iteration-count").read_text(encoding="utf-8").strip() == "1"


def test_counter_not_incremented_on_reset_run(tmp_path):
    """--reset-iterations without repair leaves counter at 0."""
    draft = _make_minimal_draft(tmp_path)
    _run_preflight(draft, "--reset-iterations")
    assert (draft / ".iteration-count").read_text(encoding="utf-8").strip() == "0"
