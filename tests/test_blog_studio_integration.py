"""Run the real engine scripts the way the Blog Studio plugin does.

plugins/blog-studio/hooks/register.ts runs blog_preflight.py with
``--draft <d> --strict --json --tools-json <list> --project-root <root>`` and then
blog_studio_status.py with ``--project-root`` and ``--expected-run``. These tests
spawn both scripts as subprocesses and validate the output with a Python mirror
of ``parseStatus`` in hooks/logic.ts and the report checks in hooks/register.ts.

Chromium and network gates cannot run in a unit test, so the passing case runs
the real CLI through a small harness that stubs gates 2 to 5 only. Gate 1, the
argument parsing, project anchoring, evidence capture, report writing and the
status script are all real. The blocked case runs fully unpatched.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
HEX32 = re.compile(r"^[0-9a-f]{32}$")
LABELS = {"passed", "blocked", "partial", "stale", "unverified", "error"}

pytestmark = pytest.mark.skipif(
    not all(hasattr(os, name) for name in ("O_NOFOLLOW", "O_DIRECTORY", "fchdir")),
    reason="project-contained execution needs Unix directory descriptors",
)

HARNESS = """
import sys
sys.path.insert(0, sys.argv[1])
import blog_preflight as p

def make(n):
    def gate(d, **kwargs):
        if n == 3:
            (d / "preview").mkdir(exist_ok=True)
            (d / "preview" / "desktop-1280.png").write_bytes(b"fixture screenshot")
        extra = {"score": 95} if n == 4 else {}
        return p._gate_result(n, p.GATE_NAMES[n], True, [], **extra)
    return gate

p.gate_2_format_completeness = make(2)
p.gate_3_visual_verification = make(3)
p.gate_4_content_review = make(4)
p.gate_5_asset_link_integrity = make(5)
sys.argv = ["blog_preflight.py"] + sys.argv[2:]
raise SystemExit(p.main())
"""


def parse_status(raw: str) -> dict:
    """Mirror of parseStatus in plugins/blog-studio/hooks/logic.ts."""
    assert len(raw) <= 1024 * 1024
    x = json.loads(raw)
    assert isinstance(x, dict)
    assert x["schema_version"] == 1 and x["status"] in LABELS
    assert type(x["passed_count"]) is int and 0 <= x["passed_count"] <= 5
    assert isinstance(x["gates"], list) and len(x["gates"]) <= 5
    assert isinstance(x["artifacts"], list) and len(x["artifacts"]) <= 8192
    assert isinstance(x["diagnostics"], list) and len(x["diagnostics"]) <= 200
    assert x["checked_at"] is None or isinstance(x["checked_at"], str)
    seen = set()
    for g in x["gates"]:
        assert type(g["gate"]) is int and 1 <= g["gate"] <= 5 and g["gate"] not in seen
        assert isinstance(g["name"], str) and type(g["passed"]) is bool
        assert isinstance(g["violations"], list) and isinstance(g["warnings"], list)
        assert all(isinstance(v, str) for v in g["violations"] + g["warnings"])
        assert g["score"] is None or (type(g["score"]) in (int, float) and 0 <= g["score"] <= 100)
        seen.add(g["gate"])
    assert x["passed_count"] == sum(g["passed"] for g in x["gates"])
    assert all(isinstance(v, str) for v in x["artifacts"] + x["diagnostics"])
    if x["status"] == "passed":
        assert len(x["gates"]) == 5 and all(g["passed"] and not g["violations"] for g in x["gates"])
        assert any(g["gate"] == 4 and g["score"] is not None and g["score"] >= 90 for g in x["gates"])
        assert isinstance(x.get("run_id"), str) and HEX32.match(x["run_id"])
        assert isinstance(x["checked_at"], str)
    return x


def check_report(report: dict, draft: Path, exit_code: int) -> str:
    """Mirror of the report checks in register.ts perform(); returns the run id."""
    run_id = (report.get("evidence") or {}).get("run_id")
    assert report["strict"] is True and report["draft"] == str(draft)
    assert type(report["blocked"]) is bool and exit_code in (0, 1) and (exit_code == 0) != report["blocked"]
    assert isinstance(run_id, str) and HEX32.match(run_id)
    return run_id


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    draft = root / "drafts" / "post"
    draft.mkdir(parents=True)
    for name in ("post.md", "post.html", "post.pdf", "hero.webp", "review.md"):
        (draft / name).write_text("fixture " + name)
    env = {**os.environ, "CLAUDE_BLOG_REVIEW_STATE_DIR": str(tmp_path / "verifier")}
    return root, draft, env


def preflight(root, draft, env, *, patched, extra=()):
    argv = [sys.executable]
    argv += ["-c", HARNESS, str(SCRIPTS)] if patched else [str(SCRIPTS / "blog_preflight.py")]
    argv += ["--draft", str(draft), "--strict", "--json", "--tools-json", "[]", "--project-root", str(root), *extra]
    proc = subprocess.run(argv, cwd=root, env=env, capture_output=True, text=True, timeout=120)
    return proc, json.loads(proc.stdout)


def status(root, draft, env, run_id=None):
    argv = [sys.executable, str(SCRIPTS / "blog_studio_status.py"), "--draft", str(draft), "--project-root", str(root)]
    if run_id:
        argv += ["--expected-run", run_id]
    proc = subprocess.run(argv, cwd=root, env=env, capture_output=True, text=True, timeout=60)
    return proc, parse_status(proc.stdout)


def test_real_scripts_pass_then_go_stale_after_the_article_changes(project):
    root, draft, env = project
    proc, report = preflight(root, draft, env, patched=True)
    assert proc.returncode == 0, proc.stderr
    run_id = check_report(report, draft, proc.returncode)
    assert report["evidence"]["requested_gates"] == report["evidence"]["completed_gates"] == [1, 2, 3, 4, 5]
    assert report["evidence"]["inputs_unchanged"] is True

    proc, passed = status(root, draft, env, run_id)
    assert proc.returncode == 0, proc.stderr
    assert passed["status"] == "passed" and passed["run_id"] == run_id and passed["passed_count"] == 5
    assert "post.md" in passed["artifacts"] and "capabilities.json" in passed["artifacts"]

    (draft / "post.md").write_text("edited after the check")
    proc, stale = status(root, draft, env, run_id)
    assert proc.returncode == 0
    assert stale["status"] == "stale" and stale["passed_count"] == 5
    assert "Article inputs" in stale["diagnostics"][0]


def test_real_unpatched_preflight_blocks_and_status_agrees(project):
    root, draft, env = project
    proc, report = preflight(root, draft, env, patched=False)
    assert proc.returncode == 1
    run_id = check_report(report, draft, proc.returncode)
    assert report["blocked"] is True and [g["gate"] for g in report["gates"]][-1] in (1, 2)
    proc, blocked = status(root, draft, env, run_id)
    assert proc.returncode == 0
    assert blocked["status"] == "blocked" and blocked["run_id"] == run_id
    assert any(not g["passed"] and g["violations"] for g in blocked["gates"])


def test_real_single_gate_run_is_partial(project):
    root, draft, env = project
    proc, report = preflight(root, draft, env, patched=False, extra=("--gate", "1"))
    run_id = check_report(report, draft, proc.returncode)
    assert status(root, draft, env, run_id)[1]["status"] == "partial"


def test_expected_run_mismatch_is_an_error_status(project):
    root, draft, env = project
    proc, report = preflight(root, draft, env, patched=True)
    assert proc.returncode == 0
    other = "0" * 32 if report["evidence"]["run_id"] != "0" * 32 else "f" * 32
    proc, wrong = status(root, draft, env, other)
    assert proc.returncode == 1
    assert wrong["status"] == "error" and "run_id" not in wrong
    assert "does not match" in wrong["diagnostics"][0]


def test_iteration_cap_exit_stays_additive_and_never_passes(project):
    root, draft, env = project
    assert preflight(root, draft, env, patched=True)[0].returncode == 0
    (draft / ".iteration-count").write_text("3\n")
    argv = [sys.executable, str(SCRIPTS / "blog_preflight.py"), "--draft", str(draft), "--strict", "--json",
            "--tools-json", "[]", "--project-root", str(root), "--repair-attempt"]
    proc = subprocess.run(argv, cwd=root, env=env, capture_output=True, text=True, timeout=60)
    assert proc.returncode == 2 and "ITERATION CAP EXCEEDED" in proc.stderr
    marker = json.loads((draft / "preflight-report.json").read_text())
    assert marker["draft"] == str(draft) and marker["incomplete"] is True
    assert status(root, draft, env)[1]["status"] == "blocked"


def test_preflight_without_project_root_still_works_and_adds_evidence(project):
    root, draft, env = project
    argv = [sys.executable, str(SCRIPTS / "blog_preflight.py"), "--draft", str(draft), "--strict", "--json",
            "--tools-json", "[]", "--gate", "1"]
    proc = subprocess.run(argv, cwd=root, env=env, capture_output=True, text=True, timeout=60)
    report = json.loads(proc.stdout)
    assert proc.returncode == 0 and report["draft"] == str(draft.resolve())
    assert HEX32.match(report["evidence"]["run_id"])


def test_isolated_mode_and_relative_dot_paths_still_anchor_and_record_evidence(project):
    # `python3 -I` drops the script directory from sys.path, and `--project-root .`
    # is how a user runs it from the project; neither may lose evidence or be refused.
    root, draft, env = project
    relative = str(draft.relative_to(root))
    argv = [sys.executable, "-I", str(SCRIPTS / "blog_preflight.py"), "--draft", "./" + relative, "--strict",
            "--json", "--tools-json", "[]", "--project-root", ".", "--gate", "1"]
    proc = subprocess.run(argv, cwd=root, env=env, capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    run_id = check_report(json.loads(proc.stdout), draft, proc.returncode)
    argv = [sys.executable, "-I", str(SCRIPTS / "blog_studio_status.py"), "--draft", "./" + relative,
            "--project-root", ".", "--expected-run", run_id]
    proc = subprocess.run(argv, cwd=root, env=env, capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    assert parse_status(proc.stdout)["status"] == "partial"


def test_project_root_outside_the_draft_is_refused(project, tmp_path):
    root, draft, env = project
    other = tmp_path / "other"
    other.mkdir()
    argv = [sys.executable, str(SCRIPTS / "blog_preflight.py"), "--draft", str(draft), "--strict", "--json",
            "--project-root", str(other)]
    proc = subprocess.run(argv, cwd=root, env=env, capture_output=True, text=True, timeout=60)
    assert proc.returncode == 1 and "refused" in proc.stderr
    assert not (draft / "preflight-report.json").exists()
