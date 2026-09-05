"""Installer-sync regression test.

Asserts that every root-level script in `scripts/*.py` is referenced
in `install.sh` AND `install.ps1`, so adding a new helper to the repo
without wiring it through the installer is caught at PR time.

Added v1.8.6 (7TH-AUDIT-001): the v1.8.0..v1.8.3 helpers (cognitive_load,
discourse_research, load_untrusted_root, lint_prose, sync_flow) were
never copied by install.sh / install.ps1, so the "code-enforced" v1.8.3
security narrative was non-functional for any marketplace/curl-pipe
install. This test prevents the same regression class.

Stdlib + pytest only.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
INSTALL_SH = ROOT / "install.sh"
INSTALL_PS1 = ROOT / "install.ps1"


def _list_root_scripts() -> list[str]:
    """Return the basenames of all root-level Python scripts to ship."""
    return sorted(p.name for p in SCRIPTS_DIR.glob("*.py"))


def test_install_sh_covers_all_root_scripts() -> None:
    """install.sh must reference every scripts/*.py file by basename OR
    use a glob like `scripts/*.py` that picks them all up."""
    sh = INSTALL_SH.read_text(encoding="utf-8")
    # Accept either a glob covering all scripts, or each by name.
    if 'scripts/"*.py' in sh or 'scripts/*.py' in sh or '"$SCRIPT_DIR/scripts/"*.py' in sh:
        # Glob form covers all scripts implicitly.
        return
    missing = [name for name in _list_root_scripts() if name not in sh]
    assert not missing, (
        f"install.sh does not reference these root scripts (will not be "
        f"shipped to end users): {missing}.\n"
        f"Either name each script in install.sh or use a glob like "
        f"`for f in scripts/*.py; do ... done`."
    )


def test_install_ps1_covers_all_root_scripts() -> None:
    """install.ps1 (Windows installer) must mirror install.sh coverage."""
    ps1 = INSTALL_PS1.read_text(encoding="utf-8")
    # Accept Get-ChildItem glob OR per-name reference.
    if "*.py" in ps1 and "scripts" in ps1:
        # Glob form. Verify it's actually reading from scripts/.
        return
    missing = [name for name in _list_root_scripts() if name not in ps1]
    assert not missing, (
        f"install.ps1 does not reference these root scripts: {missing}.\n"
        f"Use Get-ChildItem with a *.py glob or name each script explicitly."
    )


def test_uninstall_sh_removes_all_root_scripts() -> None:
    """uninstall.sh must remove every script install.sh copied. The
    helper-scripts array in uninstall.sh must list every scripts/*.py."""
    sh = (ROOT / "uninstall.sh").read_text(encoding="utf-8")
    missing = [name for name in _list_root_scripts() if name not in sh]
    assert not missing, (
        f"uninstall.sh does not remove these root scripts (will leak after "
        f"uninstall): {missing}.\n"
        f"Add them to the helper_scripts array in uninstall.sh."
    )


def test_uninstall_ps1_removes_all_root_scripts() -> None:
    """uninstall.ps1 mirrors uninstall.sh."""
    ps1 = (ROOT / "uninstall.ps1").read_text(encoding="utf-8")
    missing = [name for name in _list_root_scripts() if name not in ps1]
    assert not missing, (
        f"uninstall.ps1 does not remove these root scripts: {missing}.\n"
        f"Add them to the $helperScripts array in uninstall.ps1."
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
