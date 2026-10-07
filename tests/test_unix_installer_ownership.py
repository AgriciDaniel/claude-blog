"""Ownership regressions for the Unix standalone installer."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_REL = Path(".claude/claude-blog-manifest.txt")
LEGACY_BLOG_WRITE = ROOT / "tests/fixtures/legacy-blog-write-v2.2.0.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def environment(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir(exist_ok=True)
    fake_pip = fake_bin / "pip3"
    fake_pip.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    fake_pip.chmod(0o755)
    env = {
        **os.environ,
        "HOME": str(home),
        "PATH": f"{fake_bin}:{os.environ['PATH']}",
    }
    return home, env


def run(script: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", script],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def assert_ok(proc: subprocess.CompletedProcess[str]) -> None:
    assert proc.returncode == 0, proc.stderr or proc.stdout


def install(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    home, env = environment(tmp_path)
    assert_ok(run("install.sh", env))
    return home, env


def test_manifest_records_verified_files_not_directories(tmp_path: Path) -> None:
    home, _ = install(tmp_path)
    manifest_path = home / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["schema_version"] == 2
    assert manifest["owner"] == "claude-blog-unix-installer"
    assert manifest["files"]
    for raw_path, record in manifest["files"].items():
        path = Path(raw_path)
        assert path.is_absolute()
        assert path.is_file()
        assert record["sha256"] == sha256(path)


def test_uninstall_preserves_user_files_and_unknown_surfaces(tmp_path: Path) -> None:
    home, env = install(tmp_path)
    user_note = home / ".claude/skills/blog-write/user/notes.md"
    user_note.parent.mkdir()
    user_note.write_text("preserve me\n", encoding="utf-8")
    unknown_skill = home / ".claude/skills/blog-private/SKILL.md"
    unknown_skill.parent.mkdir()
    unknown_skill.write_text("private skill\n", encoding="utf-8")
    unknown_agent = home / ".claude/agents/blog-private.md"
    unknown_agent.write_text("private agent\n", encoding="utf-8")

    removed = run("uninstall.sh", env)
    assert_ok(removed)
    assert user_note.read_text(encoding="utf-8") == "preserve me\n"
    assert unknown_skill.read_text(encoding="utf-8") == "private skill\n"
    assert unknown_agent.read_text(encoding="utf-8") == "private agent\n"
    assert not (home / ".claude/skills/blog-write/SKILL.md").exists()
    assert not (home / MANIFEST_REL).exists()


def test_clean_installation_uninstalls_cleanly(tmp_path: Path) -> None:
    home, env = install(tmp_path)
    removed = run("uninstall.sh", env)
    assert_ok(removed)
    assert not (home / MANIFEST_REL).exists()
    assert not (home / ".claude/skills/blog-write").exists()
    assert not (home / ".claude/skills/blog").exists()
    assert not (home / ".claude/agents/blog-writer.md").exists()
    assert not (home / ".claude/scripts/analyze_blog.py").exists()


def test_installed_engine_supports_uninstall_without_source_checkout(tmp_path: Path) -> None:
    home, env = install(tmp_path)
    standalone = tmp_path / "standalone-uninstall.sh"
    standalone.write_bytes((ROOT / "uninstall.sh").read_bytes())
    standalone.chmod(0o755)

    removed = run(str(standalone), env)

    assert_ok(removed)
    assert not (home / MANIFEST_REL).exists()
    assert not (home / ".claude/scripts/installer_ownership.py").exists()
    assert not (home / ".claude/skills/blog-write/SKILL.md").exists()


def test_uninstall_without_install_is_idempotent(tmp_path: Path) -> None:
    home, env = environment(tmp_path)
    removed = run("uninstall.sh", env)
    assert_ok(removed)
    assert not (home / ".claude").exists()


def test_downloaded_current_installer_hands_pinned_release_to_its_own_installer(
    tmp_path: Path,
) -> None:
    tag = subprocess.run(
        ["git", "rev-parse", "--verify", "v2.2.0^{commit}"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if tag.returncode != 0:
        pytest.skip("pinned v2.2.0 object is unavailable in this checkout")
    home, env = environment(tmp_path)
    standalone = tmp_path / "downloaded-install.sh"
    shutil.copy2(ROOT / "install.sh", standalone)
    env.update({
        "CLAUDE_BLOG_URL": str(ROOT),
        "CLAUDE_BLOG_REF": "v2.2.0",
    })

    installed = run(str(standalone), env)

    assert_ok(installed)
    skill = home / ".claude/skills/blog-write/SKILL.md"
    assert skill.read_bytes() == LEGACY_BLOG_WRITE.read_bytes()
    manifest = home / MANIFEST_REL
    assert manifest.is_file()
    assert manifest.read_text(encoding="utf-8").splitlines()
    assert not manifest.read_text(encoding="utf-8").lstrip().startswith("{")
    assert "checked out 7b6ca10" in installed.stdout
    assert "installer_ownership.py" not in installed.stderr


def test_repeat_install_preserves_untracked_user_file(tmp_path: Path) -> None:
    home, env = install(tmp_path)
    user_note = home / ".claude/skills/blog-write/user/notes.md"
    user_note.parent.mkdir()
    user_note.write_text("preserve me\n", encoding="utf-8")

    repeated = run("install.sh", env)
    assert_ok(repeated)
    assert user_note.read_text(encoding="utf-8") == "preserve me\n"


def test_modified_managed_file_blocks_update_and_uninstall(tmp_path: Path) -> None:
    home, env = install(tmp_path)
    skill = home / ".claude/skills/blog-write/SKILL.md"
    untouched = home / ".claude/skills/blog-audio/SKILL.md"
    untouched_before = sha256(untouched)
    skill.write_text(skill.read_text(encoding="utf-8") + "\nuser edit\n", encoding="utf-8")

    repeated = run("install.sh", env)
    assert repeated.returncode != 0
    assert "was modified" in repeated.stderr
    assert skill.read_text(encoding="utf-8").endswith("user edit\n")
    assert sha256(untouched) == untouched_before

    removed = run("uninstall.sh", env)
    assert removed.returncode != 0
    assert "was modified" in removed.stderr
    assert skill.exists()
    assert (home / MANIFEST_REL).exists()


def add_v2_traversal(manifest_path: Path, victim: Path, raw_path: str) -> bytes:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"][raw_path] = {
        "sha256": sha256(victim),
        "mode": 0o644,
    }
    poisoned = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    manifest_path.write_bytes(poisoned)
    return poisoned


def test_v2_traversal_blocks_repeat_install_before_mutation(tmp_path: Path) -> None:
    home, env = install(tmp_path)
    manifest = home / MANIFEST_REL
    managed = home / ".claude/skills/blog-write/SKILL.md"
    managed_before = sha256(managed)
    victim = home / "victim.txt"
    victim.write_text("outside profile\n", encoding="utf-8")
    raw_path = f"{home}/.claude/skills/blog/../../../victim.txt"
    manifest_before = add_v2_traversal(manifest, victim, raw_path)

    repeated = run("install.sh", env)

    assert repeated.returncode != 0
    assert "unsafe path" in repeated.stderr
    assert victim.read_text(encoding="utf-8") == "outside profile\n"
    assert sha256(managed) == managed_before
    assert manifest.read_bytes() == manifest_before


def test_v2_traversal_blocks_uninstall_before_mutation(tmp_path: Path) -> None:
    home, env = install(tmp_path)
    manifest = home / MANIFEST_REL
    managed = home / ".claude/skills/blog-write/SKILL.md"
    managed_before = sha256(managed)
    victim = home / "victim.txt"
    victim.write_text("outside profile\n", encoding="utf-8")
    raw_path = f"{home}/.claude/skills/blog/../../../victim.txt"
    manifest_before = add_v2_traversal(manifest, victim, raw_path)

    removed = run("uninstall.sh", env)

    assert removed.returncode != 0
    assert "unsafe path" in removed.stderr
    assert victim.read_text(encoding="utf-8") == "outside profile\n"
    assert sha256(managed) == managed_before
    assert manifest.read_bytes() == manifest_before


def test_duplicate_v2_manifest_key_is_rejected_before_mutation(tmp_path: Path) -> None:
    home, env = install(tmp_path)
    manifest = home / MANIFEST_REL
    managed = home / ".claude/skills/blog-write/SKILL.md"
    managed_before = sha256(managed)
    poisoned = b'{"schema_version":2,"schema_version":2,"owner":"claude-blog-unix-installer","files":{}}\n'
    manifest.write_bytes(poisoned)

    removed = run("uninstall.sh", env)

    assert removed.returncode != 0
    assert "duplicate key" in removed.stderr
    assert sha256(managed) == managed_before
    assert manifest.read_bytes() == poisoned
    assert "uninstalled" not in removed.stdout


@pytest.mark.parametrize("operation", ["install.sh", "uninstall.sh"])
def test_symlinked_manifest_is_rejected_without_touching_target(
    tmp_path: Path, operation: str
) -> None:
    home, env = install(tmp_path)
    manifest = home / MANIFEST_REL
    managed = home / ".claude/skills/blog-write/SKILL.md"
    managed_before = sha256(managed)
    external = tmp_path / "external-manifest.json"
    external.write_bytes(manifest.read_bytes())
    manifest.unlink()
    manifest.symlink_to(external)
    external_before = external.read_bytes()

    result = run(operation, env)

    assert result.returncode != 0
    assert "not a regular file" in result.stderr
    assert manifest.is_symlink()
    assert external.read_bytes() == external_before
    assert sha256(managed) == managed_before
    success = "Installation Complete" if operation == "install.sh" else "uninstalled"
    assert success not in result.stdout


def test_install_refuses_unowned_collision(tmp_path: Path) -> None:
    home, env = environment(tmp_path)
    skill = home / ".claude/skills/blog-write/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("user-owned skill\n", encoding="utf-8")

    installed = run("install.sh", env)
    assert installed.returncode != 0
    assert "unowned existing file" in installed.stderr
    assert skill.read_text(encoding="utf-8") == "user-owned skill\n"
    assert not (home / MANIFEST_REL).exists()


def test_install_rejects_symlinked_home_before_profile_mutation(tmp_path: Path) -> None:
    home, env = environment(tmp_path)
    external = tmp_path / "external-home"
    external.mkdir()
    home.rmdir()
    home.symlink_to(external, target_is_directory=True)

    installed = run("install.sh", env)

    assert installed.returncode != 0
    assert "unsafe ancestor" in installed.stderr
    assert not (external / ".claude").exists()
    assert "Installation Complete" not in installed.stdout


def test_legacy_directory_inventory_removes_only_matching_package_files(
    tmp_path: Path,
) -> None:
    home, env = environment(tmp_path)
    skill_dir = home / ".claude/skills/blog-write"
    skill_dir.mkdir(parents=True)
    installed_skill = skill_dir / "SKILL.md"
    installed_skill.write_bytes(LEGACY_BLOG_WRITE.read_bytes())
    user_note = skill_dir / "user/notes.md"
    user_note.parent.mkdir()
    user_note.write_text("preserve me\n", encoding="utf-8")
    manifest = home / MANIFEST_REL
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(f"{skill_dir}\n", encoding="utf-8")

    removed = run("uninstall.sh", env)
    assert_ok(removed)
    assert not installed_skill.exists()
    assert user_note.read_text(encoding="utf-8") == "preserve me\n"
    assert skill_dir.exists()
    assert not manifest.exists()

    reinstalled = run("install.sh", env)
    assert_ok(reinstalled)
    assert installed_skill.exists()
    assert user_note.read_text(encoding="utf-8") == "preserve me\n"


def test_legacy_inventory_preserves_modified_and_unknown_files(tmp_path: Path) -> None:
    home, env = environment(tmp_path)
    skill_dir = home / ".claude/skills/blog-write"
    skill_dir.mkdir(parents=True)
    modified = skill_dir / "SKILL.md"
    modified.write_text("locally modified\n", encoding="utf-8")
    unknown = skill_dir / "custom.py"
    unknown.write_text("user code\n", encoding="utf-8")
    manifest = home / MANIFEST_REL
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(f"{skill_dir}\n", encoding="utf-8")

    removed = run("uninstall.sh", env)
    assert removed.returncode != 0
    assert "modified or is unknown" in removed.stderr
    assert modified.read_text(encoding="utf-8") == "locally modified\n"
    assert unknown.read_text(encoding="utf-8") == "user code\n"
    assert manifest.exists()
    assert "uninstalled" not in removed.stdout


def test_legacy_modified_file_blocks_update_before_mutation(tmp_path: Path) -> None:
    home, env = environment(tmp_path)
    skill_dir = home / ".claude/skills/blog-write"
    skill_dir.mkdir(parents=True)
    modified = skill_dir / "SKILL.md"
    modified.write_text("locally modified\n", encoding="utf-8")
    manifest = home / MANIFEST_REL
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(f"{skill_dir}\n", encoding="utf-8")
    untouched = modified.read_bytes()
    manifest_before = manifest.read_bytes()

    installed = run("install.sh", env)

    assert installed.returncode != 0
    assert "modified or is unknown" in installed.stderr
    assert modified.read_bytes() == untouched
    assert manifest.read_bytes() == manifest_before
    assert not (home / ".claude/skills/blog-audio/SKILL.md").exists()
    assert "Installation Complete" not in installed.stdout


def test_legacy_symlinked_skill_never_deletes_external_target(tmp_path: Path) -> None:
    home, env = environment(tmp_path)
    external = tmp_path / "external"
    external.mkdir()
    victim = external / "SKILL.md"
    victim.write_bytes(LEGACY_BLOG_WRITE.read_bytes())
    skills = home / ".claude/skills"
    skills.mkdir(parents=True)
    linked = skills / "blog-write"
    linked.symlink_to(external, target_is_directory=True)
    manifest = home / MANIFEST_REL
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(f"{linked}\n", encoding="utf-8")

    removed = run("uninstall.sh", env)
    assert removed.returncode != 0
    assert "unsafe parent" in removed.stderr
    assert linked.is_symlink()
    assert victim.exists()
    assert external.exists()
    assert manifest.exists()
    assert "uninstalled" not in removed.stdout


def test_legacy_symlinked_scope_preserves_external_empty_directory(tmp_path: Path) -> None:
    home, env = environment(tmp_path)
    external = tmp_path / "external-empty"
    external.mkdir()
    skills = home / ".claude/skills"
    skills.mkdir(parents=True)
    linked = skills / "blog-write"
    linked.symlink_to(external, target_is_directory=True)
    manifest = home / MANIFEST_REL
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(f"{linked}\n", encoding="utf-8")
    manifest_before = manifest.read_bytes()

    removed = run("uninstall.sh", env)

    assert removed.returncode != 0
    assert "unsafe parent" in removed.stderr
    assert linked.is_symlink()
    assert external.is_dir()
    assert not any(external.iterdir())
    assert manifest.read_bytes() == manifest_before


def test_known_legacy_install_migrates_to_v2_and_preserves_extra(tmp_path: Path) -> None:
    home, env = environment(tmp_path)
    skill_dir = home / ".claude/skills/blog-write"
    skill_dir.mkdir(parents=True)
    installed_skill = skill_dir / "SKILL.md"
    installed_skill.write_bytes(LEGACY_BLOG_WRITE.read_bytes())
    extra = skill_dir / "user/notes.md"
    extra.parent.mkdir()
    extra.write_text("preserve me\n", encoding="utf-8")
    manifest = home / MANIFEST_REL
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(f"{skill_dir}\n", encoding="utf-8")

    migrated = run("install.sh", env)

    assert_ok(migrated)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["schema_version"] == 2
    assert data["owner"] == "claude-blog-unix-installer"
    assert installed_skill.read_bytes() == (ROOT / "skills/blog-write/SKILL.md").read_bytes()
    assert extra.read_text(encoding="utf-8") == "preserve me\n"

    removed = run("uninstall.sh", env)
    assert_ok(removed)
    assert extra.read_text(encoding="utf-8") == "preserve me\n"
    assert not manifest.exists()

    reinstalled = run("install.sh", env)
    assert_ok(reinstalled)
    assert extra.read_text(encoding="utf-8") == "preserve me\n"


@pytest.mark.parametrize("operation", ["install.sh", "uninstall.sh"])
def test_v2_symlink_ancestor_is_rejected_without_touching_external_directory(
    tmp_path: Path, operation: str
) -> None:
    home, env = install(tmp_path)
    manifest = home / MANIFEST_REL
    manifest_before = manifest.read_bytes()
    skill_dir = home / ".claude/skills/blog-write"
    original_dir = home / ".claude/skills/blog-write.saved"
    skill_dir.rename(original_dir)
    external = tmp_path / "external"
    external.mkdir()
    external_skill = external / "SKILL.md"
    external_skill.write_bytes((original_dir / "SKILL.md").read_bytes())
    skill_dir.symlink_to(external, target_is_directory=True)

    result = run(operation, env)

    assert result.returncode != 0
    assert "unsafe parent" in result.stderr
    assert skill_dir.is_symlink()
    assert external.is_dir()
    assert external_skill.exists()
    assert original_dir.is_dir()
    assert manifest.read_bytes() == manifest_before
    success = "Installation Complete" if operation == "install.sh" else "uninstalled"
    assert success not in result.stdout


def test_legacy_unknown_scope_is_rejected_before_mutation(tmp_path: Path) -> None:
    home, env = environment(tmp_path)
    unknown = home / ".claude/skills/blog-private"
    unknown.mkdir(parents=True)
    note = unknown / "SKILL.md"
    note.write_text("private\n", encoding="utf-8")
    manifest = home / MANIFEST_REL
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(f"{unknown}\n", encoding="utf-8")
    manifest_before = manifest.read_bytes()

    result = run("uninstall.sh", env)

    assert result.returncode != 0
    assert "unreviewed scope" in result.stderr
    assert note.read_text(encoding="utf-8") == "private\n"
    assert manifest.read_bytes() == manifest_before
    assert "uninstalled" not in result.stdout


def test_legacy_migration_rolls_back_payload_and_manifest_on_write_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home, _ = environment(tmp_path)
    profile = home / ".claude"
    skill_dir = profile / "skills/blog-write"
    skill_dir.mkdir(parents=True)
    installed_skill = skill_dir / "SKILL.md"
    installed_skill.write_bytes(LEGACY_BLOG_WRITE.read_bytes())
    manifest = home / MANIFEST_REL
    manifest.write_text(f"{skill_dir}\n", encoding="utf-8")
    manifest_before = manifest.read_bytes()
    skill_before = installed_skill.read_bytes()
    stats = tmp_path / "stats.json"

    module_path = ROOT / "scripts/installer_ownership.py"
    spec = importlib.util.spec_from_file_location("installer_ownership_test", module_path)
    assert spec and spec.loader
    engine = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = engine
    spec.loader.exec_module(engine)
    original_write = engine.ProfileFS.write
    calls = 0

    def fail_after_first_write(self, relative, source, mode):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected write failure")
        return original_write(self, relative, source, mode)

    monkeypatch.setattr(engine.ProfileFS, "write", fail_after_first_write)
    args = Namespace(
        source=str(ROOT),
        profile=str(profile),
        manifest=str(manifest),
        stats=str(stats),
        version="2.2.0",
        legacy_inventory=str(ROOT / "data/legacy-install-ownership.json"),
    )

    with pytest.raises(OSError, match="injected write failure"):
        engine.install(args)

    assert installed_skill.read_bytes() == skill_before
    assert manifest.read_bytes() == manifest_before
    assert not (profile / "skills/blog/SKILL.md").exists()
    assert not stats.exists()


def test_legacy_traversal_is_rejected_before_mutation(tmp_path: Path) -> None:
    home, env = environment(tmp_path)
    skill = home / ".claude/skills/blog-write/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_bytes((ROOT / "skills/blog-write/SKILL.md").read_bytes())
    skill_before = sha256(skill)
    victim = home / "victim.txt"
    victim.write_text("outside profile\n", encoding="utf-8")
    manifest = home / MANIFEST_REL
    manifest.parent.mkdir(parents=True, exist_ok=True)
    raw_path = f"{home}/.claude/skills/blog/../../../victim.txt"
    manifest.write_text(f"{raw_path}\n", encoding="utf-8")
    manifest_before = manifest.read_bytes()

    removed = run("uninstall.sh", env)

    assert removed.returncode != 0
    assert "unsafe path" in removed.stderr
    assert victim.read_text(encoding="utf-8") == "outside profile\n"
    assert sha256(skill) == skill_before
    assert manifest.read_bytes() == manifest_before
