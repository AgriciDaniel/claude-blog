"""Structure checks for the CI workflows and the browser-required test gate."""
from __future__ import annotations

import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
CI = yaml.safe_load((ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8"))


def _steps(job):
    return CI["jobs"][job]["steps"]


def _all_steps():
    for path in WORKFLOWS:
        workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
        for name, job in workflow["jobs"].items():
            for step in job["steps"]:
                yield path.name, name, step


def test_every_checkout_drops_credentials():
    checkouts = [
        (workflow, job, step) for workflow, job, step in _all_steps()
        if str(step.get("uses", "")).startswith("actions/checkout@")
    ]
    assert checkouts
    for workflow, job, step in checkouts:
        assert step.get("with", {}).get("persist-credentials") is False, f"{workflow}:{job}"


def test_no_step_or_job_may_fail_silently():
    for path in WORKFLOWS:
        assert "continue-on-error" not in path.read_text(encoding="utf-8"), path.name


def test_every_action_is_pinned_to_a_full_commit_sha():
    for workflow, job, step in _all_steps():
        if "uses" in step:
            assert re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", step["uses"]), f"{workflow}:{job}: {step['uses']}"


def test_main_pushes_are_never_cancelled():
    expression = CI["concurrency"]["cancel-in-progress"]
    assert "pull_request" in str(expression)
    assert expression != "true" and expression is not True


def test_test_job_installs_the_browser_and_requires_it():
    job = CI["jobs"]["test"]
    commands = [step.get("run", "") for step in job["steps"]]
    install = next(i for i, cmd in enumerate(commands) if "patchright install" in cmd and "chromium" in cmd)
    run = next(i for i, step in enumerate(job["steps"]) if "pytest" in step.get("run", ""))
    assert install < run
    assert job["steps"][run]["env"]["CLAUDE_BLOG_REQUIRE_BROWSER"] == "1"


def test_test_matrix_covers_current_pythons():
    versions = CI["jobs"]["test"]["strategy"]["matrix"]["python-version"]
    assert {"3.11", "3.12", "3.13", "3.14"} <= set(versions)


def test_every_hash_lock_is_installed_with_hash_checking_on_three_oses():
    job = CI["jobs"]["locked-installs"]
    matrix = job["strategy"]["matrix"]
    assert {"ubuntu-latest", "windows-latest", "macos-latest"} <= set(matrix["os"])
    on_disk = {
        path.relative_to(ROOT).as_posix()
        for path in [ROOT / "requirements.lock", *(ROOT / "skills").glob("*/scripts/requirements.lock")]
    }
    assert on_disk == set(matrix["lock"])
    install = "\n".join(step.get("run", "") for step in job["steps"])
    assert "--require-hashes" in install and "pip check" in install


def test_uv_lock_is_checked_with_a_pinned_uv():
    job = CI["jobs"]["uv-lock-check"]
    commands = "\n".join(step.get("run", "") for step in job["steps"])
    assert re.search(r'"uv==\d+\.\d+\.\d+"', commands)
    assert "uv lock --check" in commands


def test_dependabot_documents_why_uv_ecosystem_is_absent():
    text = (ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
    config = yaml.safe_load(text)
    assert "uv" not in {update["package-ecosystem"] for update in config["updates"]}
    assert "no `uv` ecosystem entry" in text


# The browser-required gate in tests/conftest.py

BROWSER_SKIP = "requires matching installed Chromium; no browser download in unit tests"


def _run_sample(tmp_path: Path, require: bool | None) -> subprocess.CompletedProcess:
    (tmp_path / "conftest.py").write_text((ROOT / "tests" / "conftest.py").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "test_sample.py").write_text(
        textwrap.dedent(
            f"""
            import pytest

            def test_browser_gated():
                pytest.skip({BROWSER_SKIP!r})

            def test_missing_driver():
                pytest.importorskip("patchright_not_installed_here")

            def test_other_skip():
                pytest.skip("symlinks not supported on this filesystem")

            def test_imperative_xfail():
                pytest.xfail({BROWSER_SKIP!r})
            """
        ),
        encoding="utf-8",
    )
    env = {key: value for key, value in os.environ.items() if key != "CLAUDE_BLOG_REQUIRE_BROWSER"}
    if require is not None:
        env["CLAUDE_BLOG_REQUIRE_BROWSER"] = "1" if require else "0"
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-rsf", "-p", "no:cacheprovider", "test_sample.py"],
        cwd=tmp_path, env=env, capture_output=True, text=True, check=False,
    )


def test_browser_skips_stay_skips_by_default(tmp_path):
    result = _run_sample(tmp_path, require=None)
    assert result.returncode == 0, result.stdout
    assert "3 skipped" in result.stdout and "1 xfailed" in result.stdout and "failed" not in result.stdout.replace("xfailed", "")


def test_browser_skips_stay_skips_when_variable_is_not_one(tmp_path):
    result = _run_sample(tmp_path, require=False)
    assert result.returncode == 0, result.stdout


def test_require_browser_turns_browser_skips_into_failures(tmp_path):
    result = _run_sample(tmp_path, require=True)
    assert result.returncode == 1, result.stdout
    assert "FAILED test_sample.py::test_browser_gated" in result.stdout
    assert "FAILED test_sample.py::test_missing_driver" in result.stdout
    assert "patchright install chromium" in result.stdout
    # Unrelated skips and expected failures are left alone.
    assert "FAILED test_sample.py::test_other_skip" not in result.stdout
    assert "FAILED test_sample.py::test_imperative_xfail" not in result.stdout
    assert "2 failed, 1 skipped, 1 xfailed" in result.stdout


def test_real_browser_tests_use_the_skip_reason_the_gate_matches():
    pattern_source = (ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
    assert "requires matching installed chromium" in pattern_source.lower()
    for name in ("test_preflight_hardening.py", "test_runtime_review_repairs.py"):
        assert BROWSER_SKIP in (ROOT / "tests" / name).read_text(encoding="utf-8"), name
