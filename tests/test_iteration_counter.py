"""Code-enforced iteration counter tests (VULN-802).

The Blog Delivery Contract allows 3 failed full gate runs per draft; the next
full run exits 2. Only a failed counted run (exit 1 under --strict) counts:
passing runs, --gate runs, --init-review-nonce and --manual-check never do.
The counter lives with the review nonce state outside the draft folder,
keyed the same way, so an agent that can write the draft cannot reset it. A
legacy <draft>/.iteration-count file is ignored.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PREFLIGHT = ROOT / "scripts" / "blog_preflight.py"
sys.path.insert(0, str(ROOT / "scripts"))

import blog_preflight  # noqa: E402


def _make_minimal_draft(tmp: Path) -> Path:
    """A draft that always fails Gate 2 (no html, pdf or hero)."""
    draft = tmp / "post"
    draft.mkdir()
    (draft / "post.md").write_text(
        "---\ntitle: t\ndescription: d\n---\n# t\nbody\n",
        encoding="utf-8",
    )
    return draft


def _env(tmp: Path) -> dict[str, str]:
    env = dict(os.environ)
    env[blog_preflight.REVIEW_STATE_ENV] = str(tmp / "state")
    # A stock key gives Gate 1 a free hero path, so it never probes Openverse.
    env.update({"PEXELS_API_KEY": "your-test-key"})
    return env


def _run_preflight(draft: Path, *extra) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(PREFLIGHT), "--draft", str(draft), *extra]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), env=_env(draft.parent))


def _counter_path(draft: Path) -> Path:
    state = draft.parent / "state"
    digest = blog_preflight._review_state_path(draft).stem
    return state / f"{digest}{blog_preflight.ITERATION_STATE_SUFFIX}"


def _count(draft: Path) -> int:
    path = _counter_path(draft)
    return json.loads(path.read_text(encoding="utf-8"))["runs"] if path.exists() else 0


def _stub_gates(monkeypatch, passing: bool) -> None:
    names = ("gate_1_capability_discovery", "gate_2_format_completeness", "gate_3_visual_verification",
             "gate_4_content_review", "gate_5_asset_link_integrity")
    for n, name in enumerate(names, 1):
        def gate(_draft, n=n, **_kwargs):
            ok = passing or n != 2
            return blog_preflight._gate_result(n, blog_preflight.GATE_NAMES[n], ok, [] if ok else ["fixture"])
        monkeypatch.setattr(blog_preflight, name, gate)


def _main(monkeypatch, draft: Path, *extra) -> int:
    monkeypatch.setenv(blog_preflight.REVIEW_STATE_ENV, str(draft.parent / "state"))
    monkeypatch.setattr(sys, "argv", ["blog_preflight.py", "--draft", str(draft), *extra])
    return blog_preflight.main()


def test_counter_lives_outside_the_draft_keyed_like_the_nonce(tmp_path, monkeypatch):
    draft = _make_minimal_draft(tmp_path)
    monkeypatch.setenv(blog_preflight.REVIEW_STATE_ENV, str(tmp_path / "state"))
    nonce = blog_preflight._review_state_path(draft)
    counter = blog_preflight._iteration_state_path(draft)
    assert counter.parent == nonce.parent
    assert counter.name == nonce.stem + ".iterations.json"
    assert draft not in counter.parents


def test_failed_full_run_counts_and_nothing_is_written_to_the_draft(tmp_path):
    draft = _make_minimal_draft(tmp_path)
    assert _run_preflight(draft).returncode == 1
    assert _count(draft) == 1
    assert not (draft / ".iteration-count").exists()


def test_three_failed_runs_then_the_next_full_run_exits_two(tmp_path):
    draft = _make_minimal_draft(tmp_path)
    for _ in range(3):
        assert _run_preflight(draft).returncode == 1
    assert _count(draft) == 3
    result = _run_preflight(draft, "--json")
    assert result.returncode == 2, result.stderr
    assert "ITERATION CAP EXCEEDED" in result.stderr
    assert "failed 3 full gate runs" in result.stderr
    assert "new write or rewrite" in result.stderr
    capped = json.loads(result.stdout)
    assert capped["iteration_cap_exceeded"] is True and capped["blocked"] is True
    assert _count(draft) == 3


def test_passing_runs_never_count(tmp_path, monkeypatch):
    draft = _make_minimal_draft(tmp_path)
    _stub_gates(monkeypatch, passing=True)
    for _ in range(6):
        assert _main(monkeypatch, draft) == 0
    assert _count(draft) == 0


def test_passing_run_at_the_cap_is_still_refused(tmp_path, monkeypatch):
    draft = _make_minimal_draft(tmp_path)
    _stub_gates(monkeypatch, passing=False)
    for _ in range(3):
        assert _main(monkeypatch, draft) == 1
    _stub_gates(monkeypatch, passing=True)
    assert _main(monkeypatch, draft) == blog_preflight.EXIT_ITERATION_CAP


def test_no_strict_blocked_runs_do_not_count(tmp_path, monkeypatch):
    draft = _make_minimal_draft(tmp_path)
    _stub_gates(monkeypatch, passing=False)
    for _ in range(4):
        assert _main(monkeypatch, draft, "--no-strict") == 0
    assert _count(draft) == 0


def test_manual_check_never_reads_or_changes_the_counter(tmp_path, monkeypatch):
    draft = _make_minimal_draft(tmp_path)
    _stub_gates(monkeypatch, passing=False)
    for _ in range(3):
        _main(monkeypatch, draft)
    assert _count(draft) == 3
    for _ in range(5):
        assert _main(monkeypatch, draft, "--manual-check") == 1
    assert _count(draft) == 3
    _stub_gates(monkeypatch, passing=True)
    assert _main(monkeypatch, draft, "--manual-check") == 0


def test_manual_check_works_with_an_unwritable_state_dir(tmp_path, monkeypatch):
    draft = _make_minimal_draft(tmp_path)
    _stub_gates(monkeypatch, passing=False)
    (tmp_path / "state").write_text("not a directory")
    assert _main(monkeypatch, draft, "--manual-check") == 1
    assert json.loads((draft / "preflight-report.json").read_text())["gates"]


def test_repair_attempt_applies_the_cap_to_single_gate_runs(tmp_path):
    draft = _make_minimal_draft(tmp_path)
    for _ in range(3):
        assert _run_preflight(draft, "--gate", "2", "--repair-attempt").returncode == 1
    assert _run_preflight(draft, "--gate", "2", "--repair-attempt").returncode == 2


def test_single_gate_runs_never_count(tmp_path):
    draft = _make_minimal_draft(tmp_path)
    for _ in range(4):
        assert _run_preflight(draft, "--gate", "2").returncode == 1
    assert not _counter_path(draft).exists()


def test_init_review_nonce_does_not_count(tmp_path):
    draft = _make_minimal_draft(tmp_path)
    result = _run_preflight(draft, "--init-review-nonce")
    assert result.returncode == 0
    assert not _counter_path(draft).exists()


def test_reset_iterations_resets_and_runs_no_gates(tmp_path):
    draft = _make_minimal_draft(tmp_path)
    for _ in range(3):
        _run_preflight(draft)
    (draft / "preflight-report.json").unlink()
    result = _run_preflight(draft, "--reset-iterations")
    assert result.returncode == 0, result.stderr
    assert _count(draft) == 0
    assert not (draft / "preflight-report.json").exists(), "a reset must not run or record gates"
    assert _run_preflight(draft).returncode == 1
    assert _count(draft) == 1


def test_reset_with_init_review_nonce_still_prints_the_nonce(tmp_path):
    draft = _make_minimal_draft(tmp_path)
    for _ in range(3):
        _run_preflight(draft)
    result = _run_preflight(draft, "--reset-iterations", "--init-review-nonce")
    assert result.returncode == 0
    assert len(result.stdout.strip()) == 32
    assert _count(draft) == 0


def test_corrupted_counter_file_counts_as_zero(tmp_path):
    draft = _make_minimal_draft(tmp_path)
    path = _counter_path(draft)
    path.parent.mkdir(parents=True)
    path.write_text("not-json", encoding="utf-8")
    assert _run_preflight(draft).returncode == 1
    assert _count(draft) == 1


def test_legacy_draft_counter_is_ignored(tmp_path):
    """An old <draft>/.iteration-count neither caps nor resets the new counter."""
    draft = _make_minimal_draft(tmp_path)
    (draft / ".iteration-count").write_text("3\n", encoding="utf-8")
    assert _run_preflight(draft).returncode == 1
    assert _count(draft) == 1
    (draft / ".iteration-count").write_text("0\n", encoding="utf-8")
    for _ in range(2):
        _run_preflight(draft)
    assert _run_preflight(draft).returncode == 2


def test_deleting_draft_files_does_not_reset_the_counter(tmp_path):
    draft = _make_minimal_draft(tmp_path)
    for _ in range(3):
        _run_preflight(draft)
    for child in draft.iterdir():
        if child.is_file():
            child.unlink()
    assert _run_preflight(draft).returncode == 2


@pytest.mark.parametrize("json_mode", [False, True])
def test_unwritable_state_dir_fails_cleanly(tmp_path, json_mode):
    draft = _make_minimal_draft(tmp_path)
    (tmp_path / "state").write_text("a file where the state directory should be")
    result = _run_preflight(draft, *(["--json"] if json_mode else []))
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert "repair counter unavailable" in result.stderr
    if json_mode:
        report = json.loads(result.stdout)
        assert report["blocked"] is True and report["iteration_counter_error"] is True
        assert "repair counter unavailable" in report["reason"]


def test_concurrent_failed_runs_never_exceed_the_cap(tmp_path):
    draft = _make_minimal_draft(tmp_path)
    cmd = [sys.executable, str(PREFLIGHT), "--draft", str(draft)]
    procs = [subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
                              cwd=str(ROOT), env=_env(tmp_path)) for _ in range(6)]
    codes = [p.wait(timeout=120) for p in procs]
    for p in procs:
        p.stderr.close()
    assert sorted(codes) == [1, 1, 1, 2, 2, 2]
    assert _count(draft) == 3


@pytest.mark.parametrize("flag,needle", [
    ("--reset-iterations", "new write or rewrite"),
    ("--repair-attempt", "passing runs never count"),
    ("--manual-check", "without reading or changing the repair counter"),
])
def test_counter_flags_help_explains_the_rule(flag, needle):
    result = subprocess.run([sys.executable, str(PREFLIGHT), "--help"], capture_output=True, text=True)
    text = " ".join(result.stdout.split())
    assert flag in text
    assert needle in text
