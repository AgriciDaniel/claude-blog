"""Ensure the shared installer inventories ship and remove every root helper.

Unix coverage executes the real inventory and a disposable profile lifecycle.
Windows coverage checks source contracts; its native smoke remains a separate
gate when PowerShell is unavailable. Neither platform maintains a second
filename list as its authority for deletion.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"


def _list_root_scripts() -> list[str]:
    return sorted(p.name for p in SCRIPTS_DIR.glob("*.py"))


def _unix_inventory():
    spec = importlib.util.spec_from_file_location(
        "installer_sync_ownership", SCRIPTS_DIR / "installer_ownership.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.build_inventory(ROOT)[0]


def test_install_sh_covers_all_root_scripts() -> None:
    wrapper = (ROOT / "install.sh").read_text(encoding="utf-8")
    assert 'scripts/installer_ownership.py" install' in wrapper
    destinations = {str(relative) for relative in _unix_inventory()}
    assert {f"scripts/{name}" for name in _list_root_scripts()} <= destinations
    assert "skills/blog/scripts/analyze_blog.py" in destinations


def test_install_ps1_covers_all_root_scripts() -> None:
    """Static Windows discovery contract, not native installation proof."""
    wrapper = (ROOT / "install.ps1").read_text(encoding="utf-8")
    helper = (SCRIPTS_DIR / "windows_installer_ownership.ps1").read_text(encoding="utf-8")
    assert "Invoke-ClaudeBlogInstall" in wrapper
    assert "scripts/windows_installer_ownership.ps1" in wrapper
    assert "Get-ChildItem -LiteralPath (Join-Path $root 'scripts') -File -Filter '*.py'" in helper
    assert 'Add-CBPlanFile $plan $scriptFile.FullName "scripts/$($scriptFile.Name)"' in helper
    assert "skills/blog/scripts/analyze_blog.py" in helper
    assert "Add-CBPlanFile $plan $windowsHelper 'scripts/windows_installer_ownership.ps1'" in helper


def test_uninstall_sh_removes_all_root_scripts(tmp_path: Path) -> None:
    """Run the real lifecycle with dependency installation stubbed."""
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_pip = fake_bin / "pip3"
    fake_pip.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    fake_pip.chmod(0o755)
    home = tmp_path / "home"
    home.mkdir()
    env = dict(os.environ, HOME=str(home))
    env["PATH"] = os.pathsep.join((str(fake_bin), str(Path(sys.executable).parent), env.get("PATH", "")))
    for script in ("install.sh", "uninstall.sh"):
        process = subprocess.run(["bash", str(ROOT / script)], cwd=ROOT, env=env, capture_output=True, text=True)
        assert process.returncode == 0, process.stderr or process.stdout
        if script == "install.sh":
            manifest = json.loads((home / ".claude/claude-blog-manifest.txt").read_text())
            assert all(str(home / ".claude/scripts" / name) in manifest["files"] for name in _list_root_scripts())
    assert all(not (home / ".claude/scripts" / name).exists() for name in _list_root_scripts())
    assert not (home / ".claude/claude-blog-manifest.txt").exists()


def test_uninstall_ps1_removes_all_root_scripts() -> None:
    """Static Windows receipt contract, not native removal proof."""
    wrapper = (ROOT / "uninstall.ps1").read_text(encoding="utf-8")
    helper = (SCRIPTS_DIR / "windows_installer_ownership.ps1").read_text(encoding="utf-8")
    assert "Invoke-ClaudeBlogUninstall" in wrapper
    assert "scripts/windows_installer_ownership.ps1" in wrapper
    uninstall = helper[helper.index("function Invoke-ClaudeBlogUninstall"):]
    assert "Read-CBReceipt $manifest $profile" in uninstall
    assert "$owned = $receipt.Files" in uninstall
    assert "Assert-CBOwnedFilesCurrent $profile $owned" in uninstall
    assert "foreach ($relative in @($owned.Keys | Sort-Object))" in uninstall
    assert "Remove-Item -LiteralPath $target" in uninstall
