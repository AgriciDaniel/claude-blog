"""Wave 3 regression tests: FLOW sync drift gate, wrapper and offline errors."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "scripts" / "sync_flow.py"
WRAPPER = ROOT / "skills" / "blog-flow" / "scripts" / "sync_flow.py"
COMMITTED_REFS = ROOT / "skills" / "blog-flow" / "references"
DEAD_PROXY = "http://127.0.0.1:9"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Day(datetime.date):
    value = datetime.date(2026, 1, 1)

    @classmethod
    def today(cls):
        return cls.value


def _fake_datetime(module):
    class Fake:
        date = _Day

    module.datetime = Fake


@pytest.fixture
def core(tmp_path, monkeypatch):
    module = _load(CORE, f"wave3_sync_{id(tmp_path)}")
    package = tmp_path / "package"
    monkeypatch.setattr(module, "script_root", lambda: package)
    monkeypatch.setattr(module, "PROMPT_STAGES", ["find"])
    monkeypatch.setattr(module, "_base_headers", lambda: {})
    monkeypatch.setattr(
        module, "list_markdown_files",
        lambda *a: [("docs/09-prompts/find/test.md", "test.md")],
    )
    monkeypatch.setattr(
        module, "fetch_file", lambda path, ref, headers: f"# upstream\n\nbody of {path}\n"
    )
    _fake_datetime(module)
    module.package = package
    module.refs = package / "skills" / "blog-flow" / "references"
    return module


def _sync(module, **kwargs):
    options = dict(ref="x", dry_run=False, allow_drift=False, references_dir=None)
    options.update(kwargs)
    return module.sync(argparse.Namespace(**options))


def _snapshot(directory: Path):
    return {
        str(p.relative_to(directory)): p.read_bytes()
        for p in directory.rglob("*") if p.is_file()
    }


def _lock_entries(lock: Path):
    return dict(
        reversed(line.split("  ", 1))
        for line in lock.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    )


def test_identical_upstream_is_not_drift_when_the_date_changes(core):
    _Day.value = datetime.date(2026, 1, 1)
    _sync(core)
    before = _snapshot(core.refs)
    _Day.value = datetime.date(2026, 1, 2)
    result = _sync(core)  # no allow_drift: a daily date change must not block
    assert result["updated"] == [] and result["added"] == []
    assert _snapshot(core.refs) == before
    assert b"2026-01-01" in (core.refs / "flow-framework.md").read_bytes()


def test_real_upstream_change_is_still_drift(core):
    _sync(core)
    core.fetch_file = lambda path, ref, headers: "# changed\n"
    with pytest.raises(SystemExit) as exc:
        _sync(core)
    assert exc.value.code == 2


def test_header_has_license_link_and_modification_notice(core):
    _sync(core)
    first = (core.refs / "flow-framework.md").read_text(encoding="utf-8").splitlines()[0]
    assert "CC BY 4.0" in first
    assert "https://creativecommons.org/licenses/by/4.0/" in first
    assert "Modified from the original; see source" in first
    assert chr(0x2014) not in first


def test_legacy_committed_lock_hashes_stay_valid_and_date_blind(tmp_path, monkeypatch, capsys):
    """The committed lock (hash of the dated file) must keep working unchanged."""
    module = _load(CORE, "wave3_sync_legacy")
    package = tmp_path / "package"
    refs = package / "skills" / "blog-flow" / "references"
    shutil.copytree(COMMITTED_REFS, refs)
    before = _snapshot(refs)
    monkeypatch.setattr(module, "script_root", lambda: package)
    monkeypatch.setattr(module, "_base_headers", lambda: {})
    _fake_datetime(module)
    _Day.value = datetime.date(2030, 5, 5)
    lock = refs / "flow-prompts.lock"
    entries = _lock_entries(lock)
    # Every committed lock entry verifies against its file and normalizes.
    for rel, digest in entries.items():
        assert module._baseline_normalized(lock, rel, digest) is not None, rel

    def upstream_for(source):
        relative = source.split("docs/", 1)[1]
        if relative.startswith("01-framework/"):
            local = refs / "flow-framework.md"
        elif relative.startswith("10-references/"):
            local = refs / "bibliography.md"
        else:
            local = refs / "prompts" / relative.split("09-prompts/", 1)[1]
        return module.strip_sync_header(local.read_text(encoding="utf-8"))

    def fake_list(path, ref, headers):
        stage = path.rsplit("/", 1)[1]
        return [
            (f"{path}/{p.name}", p.name)
            for p in sorted((refs / "prompts" / stage).glob("*.md"))
        ]

    monkeypatch.setattr(module, "fetch_file", lambda s, r, h: upstream_for(s))
    monkeypatch.setattr(module, "list_markdown_files", fake_list)
    # The generated prompts README is rebuilt from the prompt files, so it is
    # the one entry allowed to differ; everything else must be date-blind.
    _sync(module, dry_run=True)
    drift = [
        line.strip() for line in capsys.readouterr().err.splitlines()
        if line.strip().startswith(("CHANGED", "ADDED", "REMOVED"))
    ]
    assert drift == ["CHANGED skills/blog-flow/references/prompts/README.md"]
    assert _snapshot(refs) == before  # dry run writes nothing


def test_normalization_ignores_header_and_date_only(core):
    body = "# t\n\ntext\n"
    old = (
        "<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->\n"
        "<!-- Synced from FLOW on 2026-04-27 -->\n" + body
    )
    new = core.inject_license_header(body, "2030-01-01")
    assert core.normalized_sha256(old) == core.normalized_sha256(new)
    assert core.normalized_sha256(old) == hashlib.sha256(body.encode()).hexdigest()
    assert core.normalized_sha256(old + "x") != core.normalized_sha256(new)


def _offline_env():
    env = dict(os.environ)
    for name in ("HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy"):
        env[name] = DEAD_PROXY
    env["NO_PROXY"] = ""
    env["no_proxy"] = ""
    env.pop("GITHUB_TOKEN", None)
    return env


@pytest.mark.parametrize("script", [CORE, WRAPPER])
def test_dry_run_without_network_is_a_clear_nonzero_error(script, tmp_path):
    refs = tmp_path / "persistent"
    result = subprocess.run(
        [sys.executable, str(script), "--dry-run", "--references-dir", str(refs)],
        capture_output=True, text=True, env=_offline_env(), cwd=tmp_path, timeout=60,
    )
    assert result.returncode == 3, result.stderr
    assert "Traceback" not in result.stderr
    assert "could not reach api.github.com" in result.stderr
    assert not refs.exists()


def test_wrapper_without_core_exits_with_a_pointer(tmp_path):
    lone = tmp_path / "skills" / "blog-flow" / "scripts"
    lone.mkdir(parents=True)
    shutil.copyfile(WRAPPER, lone / "sync_flow.py")
    result = subprocess.run(
        [sys.executable, str(lone / "sync_flow.py"), "--resolve-references"],
        capture_output=True, text=True, cwd=tmp_path,
        env={k: v for k, v in os.environ.items() if k != "CLAUDE_BLOG_SCRIPTS_DIR"},
    )
    assert result.returncode == 2
    assert "thin wrapper" in result.stderr
    assert "Traceback" not in result.stderr


def test_wrapper_has_no_second_implementation():
    source = WRAPPER.read_text(encoding="utf-8")
    assert "api.github.com" not in source
    assert 'default="main"' not in source
    assert "SYNC_PATHS" not in source
    assert len(source.splitlines()) < 90


def test_wrapper_resolve_matches_core(tmp_path):
    persistent = tmp_path / "persistent"
    persistent.mkdir()
    for script in (CORE, WRAPPER):
        result = subprocess.run(
            [sys.executable, str(script), "--resolve-references",
             "--references-dir", str(persistent)],
            capture_output=True, text=True, cwd=tmp_path,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == str(persistent)
