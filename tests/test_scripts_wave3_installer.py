"""Wave 3 regression tests: installer profile paths behind OS-level symlinks."""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("wave3_installer_ownership", ROOT / "scripts" / "installer_ownership.py")
OWNERSHIP = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = OWNERSHIP
SPEC.loader.exec_module(OWNERSHIP)


def _link_to_tmp(tmp_path):
    real = tmp_path / "real" / "var" / "home"
    real.mkdir(parents=True)
    alias = tmp_path / "alias"
    alias.symlink_to(real, target_is_directory=True)
    return real, alias


def test_user_created_symlink_ancestor_is_refused_with_a_clear_message(tmp_path):
    real, alias = _link_to_tmp(tmp_path)
    with pytest.raises(SystemExit) as exc:
        OWNERSHIP.ProfileFS(alias / "user" / ".claude")
    message = str(exc.value)
    assert f"refusing symlinked path component {alias}" in message
    assert "Not a directory" not in message
    assert not (real / "user").exists()


def test_root_owned_alias_under_the_filesystem_root_is_followed(tmp_path, monkeypatch):
    real, alias = _link_to_tmp(tmp_path)
    # Stand in for /home: treat this one link as the trusted root-owned alias.
    original = OWNERSHIP.is_trusted_system_symlink
    monkeypatch.setattr(
        OWNERSHIP, "is_trusted_system_symlink",
        lambda path, link_stat: path == alias or original(path, link_stat),
    )
    fs = OWNERSHIP.ProfileFS(alias / "user" / ".claude")
    assert (real / "user" / ".claude").is_dir()
    assert fs.root == alias / "user" / ".claude"


def test_trusted_rule_requires_root_ownership_directly_under_the_root():
    root_link = SimpleNamespace(st_uid=0)
    user_link = SimpleNamespace(st_uid=os.getuid() or 1000)
    assert OWNERSHIP.is_trusted_system_symlink(Path("/home"), root_link)
    assert not OWNERSHIP.is_trusted_system_symlink(Path("/home"), user_link)
    assert not OWNERSHIP.is_trusted_system_symlink(Path("/home/user/link"), root_link)
    assert not OWNERSHIP.is_trusted_system_symlink(Path("/a/b"), root_link)


def test_symlinked_claude_directory_is_refused_even_if_root_owned(tmp_path, monkeypatch):
    real = tmp_path / "elsewhere"
    real.mkdir()
    home = tmp_path / "home"
    home.mkdir()
    (home / ".claude").symlink_to(real, target_is_directory=True)
    monkeypatch.setattr(OWNERSHIP, "is_trusted_system_symlink", lambda path, link_stat: True)
    with pytest.raises(SystemExit) as exc:
        OWNERSHIP.ProfileFS(home / ".claude")
    assert f"refusing symlinked path component {home / '.claude'}" in str(exc.value)


def test_symlinked_skills_directory_is_refused_with_a_clear_message(tmp_path):
    profile = tmp_path / "profile"
    profile.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (profile / "skills").symlink_to(outside, target_is_directory=True)
    fs = OWNERSHIP.ProfileFS(profile)
    with pytest.raises(SystemExit) as exc:
        fs.parent_fd(PurePosixPath("skills/blog/SKILL.md"), create=True)
    message = str(exc.value)
    assert f"refusing symlinked path component {profile / 'skills'}" in message
    assert "Not a directory" not in message
    assert list(outside.iterdir()) == []


def _real_home_alias():
    home = Path("/home")
    try:
        link = os.lstat(home)
    except OSError:
        return None
    if not home.is_symlink() or link.st_uid != 0:
        return None
    target = Path(os.path.realpath(home))
    try:
        return home / ROOT.resolve().relative_to(target)
    except ValueError:
        return None


@pytest.mark.skipif(_real_home_alias() is None, reason="/home is not a root-owned alias of a path containing this checkout")
def test_profile_behind_the_real_home_alias_is_accepted():
    alias_root = _real_home_alias()
    scratch = Path(tempfile.mkdtemp(prefix=".w3-profile-", dir=ROOT.parent))
    try:
        profile = Path("/home") / scratch.resolve().relative_to(Path(os.path.realpath("/home"))) / "user" / ".claude"
        assert str(profile).startswith("/home/")
        fs = OWNERSHIP.ProfileFS(profile)
        assert (scratch / "user" / ".claude").is_dir()
        assert fs.root == profile
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    assert alias_root is not None


@pytest.mark.skipif(_real_home_alias() is None, reason="/home is not a root-owned alias of a path containing this checkout")
def test_install_and_uninstall_scripts_work_with_home_behind_the_alias(tmp_path):
    scratch = Path(tempfile.mkdtemp(prefix=".w3-home-", dir=ROOT.parent))
    try:
        home = Path("/home") / scratch.resolve().relative_to(Path(os.path.realpath("/home")))
        env = dict(os.environ, HOME=str(home), CLAUDE_BLOG_SKIP_PIP="1")
        installed = subprocess.run(["bash", str(ROOT / "install.sh")], capture_output=True, text=True, env=env, cwd=ROOT)
        assert installed.returncode == 0, installed.stderr
        assert "unsafe parent" not in installed.stderr and "Not a directory" not in installed.stderr
        assert (scratch / ".claude" / "skills" / "blog" / "SKILL.md").is_file()
        removed = subprocess.run(["bash", str(ROOT / "uninstall.sh")], capture_output=True, text=True, env=env, cwd=ROOT)
        assert removed.returncode == 0, removed.stderr
        assert not (scratch / ".claude" / "skills" / "blog" / "SKILL.md").exists()
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def test_shell_wrappers_rewrite_the_cryptic_message(tmp_path):
    """An older installed engine's wording is routed through the clear message."""
    fake = tmp_path / "engine.py"
    fake.write_text(
        "import sys\nsys.stderr.write('ERROR: installation path has an unsafe parent at skills: Not a directory\\n')\nsys.exit(1)\n",
        encoding="utf-8",
    )
    for script in ("install.sh", "uninstall.sh"):
        source = (ROOT / script).read_text(encoding="utf-8")
        start = source.index("run_ownership_engine() {")
        end = source.index("\n}\n", start) + 3
        harness = tmp_path / f"harness-{script}"
        harness.write_text(source[start:end] + f'\nrun_ownership_engine "{fake}"\n', encoding="utf-8")
        result = subprocess.run(["bash", str(harness)], capture_output=True, text=True)
        assert result.returncode == 1
        assert "refusing symlinked path component skills" in result.stderr
        assert "unsafe parent" not in result.stderr
