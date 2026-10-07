"""Source contracts for the Windows ownership engine.

PowerShell is unavailable in the Linux review environment. These tests inspect
structural safety contracts only. The executable native smoke suite lives in
tests/windows/windows_installer_ownership_smoke.ps1 and remains a Windows gate.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "install.ps1"
UNINSTALL = ROOT / "uninstall.ps1"
HELPER = ROOT / "scripts/windows_installer_ownership.ps1"
LEGACY = ROOT / "data/legacy-install-ownership.json"
SMOKE = ROOT / "tests/windows/windows_installer_ownership_smoke.ps1"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _function(source: str, name: str) -> str:
    start = source.index(f"function {name}")
    next_function = source.find("\nfunction ", start + 1)
    return source[start:] if next_function < 0 else source[start:next_function]


def test_wrappers_preserve_public_entrypoints_version_and_profile_defaults() -> None:
    install = _read(INSTALL)
    uninstall = _read(UNINSTALL)
    assert install.startswith("#!/usr/bin/env pwsh")
    assert uninstall.startswith("#!/usr/bin/env pwsh")
    assert '$ClaudeBlogVersion = "2.2.0"' in install
    assert "https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.ps1" in install
    assert 'Join-Path $env:USERPROFILE ".claude"' in install
    assert 'Join-Path $env:USERPROFILE ".claude"' in uninstall
    for override in ("CLAUDE_BLOG_REPO", "CLAUDE_BLOG_REF", "CLAUDE_BLOG_URL"):
        assert override in install


def test_both_wrappers_use_one_shared_ownership_engine() -> None:
    install = _read(INSTALL)
    uninstall = _read(UNINSTALL)
    assert "scripts/windows_installer_ownership.ps1" in install
    assert "Invoke-ClaudeBlogInstall" in install
    assert "Invoke-ClaudeBlogUninstall" in uninstall
    assert ". $OwnershipHelper" in install
    assert ". $OwnershipHelper" in uninstall
    assert "$PackageSkills" not in uninstall
    assert "$AgentFiles" not in uninstall
    assert "$HelperScripts" not in uninstall
    resolver = _function(uninstall, "Resolve-OwnershipHelper")
    assert 'scripts/windows_installer_ownership.ps1' in resolver
    assert 'scripts/windows_installer_ownership.ps1" })' in resolver
    assert "Get-FileHash -LiteralPath $installedHelper -Algorithm SHA256" in resolver
    assert "the installed ownership helper was modified" in resolver


def test_cloned_ref_hands_off_to_its_own_installer() -> None:
    install = _read(INSTALL)
    clone = install.index("git clone --depth 1 --branch $Ref")
    handoff = install.index('$SelectedInstaller = Join-Path $ScriptDir "install.ps1"')
    current_helper = install.index('$OwnershipHelper = Join-Path $ScriptDir "scripts/windows_installer_ownership.ps1"')
    assert clone < handoff < current_helper
    assert "Start-Process -FilePath $HostExecutable" in install[handoff:current_helper]
    assert "selected ref installer failed" in install[handoff:current_helper]
    assert "return" in install[handoff:current_helper]


def test_clone_bootstrap_uses_exclusive_owned_full_guid_root_and_child_checkout() -> None:
    install = _read(INSTALL)
    creator = _function(install, "New-ClaudeBlogOwnedTempRoot")
    cleanup = _function(install, "Remove-ClaudeBlogOwnedTempRoot")
    main = _function(install, "Main")
    assert "NewGuid().ToString('N')" in creator
    assert "^[0-9a-f]{32}$" in creator
    assert "New-Item -ItemType Directory -Path $root -ErrorAction Stop" in creator
    assert "Assert-ClaudeBlogNoReparsePath $temp" in creator
    assert "Assert-ClaudeBlogNoReparsePath $root" in creator
    assert "FileMode]::CreateNew" in creator
    assert ".claude-blog-bootstrap-owner" in creator
    assert '$CheckoutDir = Join-Path $BootstrapRoot "checkout"' in main
    assert "git clone --depth 1 --branch $Ref $Url $CheckoutDir" in main
    assert main.index("$BootstrapOwned = $true") > main.index("$bootstrap = New-ClaudeBlogOwnedTempRoot")
    assert "Substring(0,8)" not in install
    assert "if ($BootstrapOwned)" in main
    assert "Remove-ClaudeBlogOwnedTempRoot $BootstrapRoot $BootstrapToken" in main
    assert ".claude-blog-bootstrap-owner" in cleanup
    assert "ReparsePoint" in cleanup
    assert "Assert-ClaudeBlogNoReparsePath $fullRoot" in cleanup
    assert "invalid ownership evidence" in cleanup
    assert "Remove-Item -LiteralPath $fullRoot -Recurse" in cleanup
    assert '$CheckoutDir = Join-Path $BootstrapRoot "checkout-fallback"' in main
    assert "Remove-Item -LiteralPath $CheckoutDir -Recurse" not in main


def test_pip_log_uses_owned_full_guid_root_and_is_retained_on_failure() -> None:
    install = _read(INSTALL)
    main = _function(install, "Main")
    assert "New-ClaudeBlogOwnedTempRoot 'pip'" in main
    assert 'Join-Path $pipRoot "pip-stderr.log"' in main
    assert "RedirectStandardError $pipLog" in main
    assert "refusing a pre-existing pip log path" in main
    assert "Assert-ClaudeBlogNoReparsePath $pipLog" in main
    assert "See retained log: $pipLog" in main
    assert "else {\n                        $retainPipLog = $false" in main
    assert "if (-not $retainPipLog) { Remove-ClaudeBlogOwnedTempRoot $pipRoot $pipToken }" in main
    assert "claude-blog-pip-$([System.Guid]::NewGuid().ToString('N').Substring(0,8)).log" not in install


def test_receipt_is_versioned_relative_and_hash_backed() -> None:
    helper = _read(HELPER)
    receipt = _function(helper, "ConvertTo-CBReceipt")
    parser = _function(helper, "Read-CBReceipt")
    assert "schema_version = 2" in receipt
    assert "claude-blog-windows-installer" in helper
    assert "path = $relative" in receipt
    assert "sha256 = $Plan[$relative].Sha256" in receipt
    assert "GetFullPath" not in receipt
    assert "duplicate installation receipt path" in parser
    assert "Assert-CBRelativePath" in parser
    assert "$script:CBHex64" in parser


def test_source_discovery_includes_all_python_helpers_and_windows_helper() -> None:
    helper = _read(HELPER)
    discovery = _function(helper, "Get-CBSourcePlan")
    assert "-Filter '*.py'" in discovery
    assert "scripts/$($scriptFile.Name)" in discovery
    assert "skills/blog/scripts/analyze_blog.py" in discovery
    assert "scripts/windows_installer_ownership.ps1" in discovery
    assert "Add-CBPlanFile $plan $windowsHelper" in discovery
    assert "installer_ownership.py" in {p.name for p in (ROOT / "scripts").glob("*.py")}


def test_install_preflights_every_collision_before_transaction_creation() -> None:
    helper = _read(HELPER)
    install = _function(helper, "Invoke-ClaudeBlogInstall")
    transaction = install.index("New-CBTempDirectory")
    collision_loop = install.index("foreach ($relative in @($plan.Keys | Sort-Object))")
    refusal = install.index("refusing to overwrite an unowned existing file")
    assert collision_loop < refusal < transaction
    assert "Assert-CBOwnedFilesCurrent" in install[:transaction]
    assert "managed installation file was modified" in install[:transaction]
    assert "Get-CBSha256" in install[:transaction]
    assert "Copy-Item" not in install[:transaction]
    assert "Remove-Item" not in install[:transaction]


def test_uninstall_preflights_all_hashes_before_backup_or_delete() -> None:
    helper = _read(HELPER)
    uninstall = _function(helper, "Invoke-ClaudeBlogUninstall")
    transaction = uninstall.index("New-CBTempDirectory")
    assert "Assert-CBOwnedFilesCurrent" in uninstall[:transaction]
    assert "Get-CBCompleteLegacyRevision" in uninstall[:transaction]
    assert "Assert-CBProfilePath" in uninstall[:transaction]
    assert "Remove-Item" not in uninstall[:transaction]
    assert uninstall.index("Copy-CBBackupSet") > transaction
    assert uninstall.index("Remove-Item -LiteralPath $target") > transaction


def test_legacy_ownership_uses_exact_path_hash_and_complete_revision() -> None:
    helper = _read(HELPER)
    inventory = json.loads(LEGACY.read_text(encoding="utf-8"))
    assert inventory["schema_version"] == 1
    assert inventory["owner"] == "claude-blog-reviewed-legacy-payload"
    assert len(inventory["revisions"]) >= 2
    assert inventory["files"]
    assert "Read-CBLegacyInventory" in helper
    complete = _function(helper, "Get-CBCompleteLegacyRevision")
    assert "foreach ($relative in @($Inventory.Records.Keys))" in complete
    assert "Get-CBSha256" in complete
    assert "no complete reviewed legacy installation was found" in complete
    assert "Remove-LegacySkill" not in _read(UNINSTALL)
    assert "-Recurse -Force" not in _read(UNINSTALL)


def test_reparse_guards_cover_source_profile_targets_manifest_and_temp() -> None:
    helper = _read(HELPER)
    assert "FileAttributes]::ReparsePoint" in helper
    assert "Assert-CBNoReparseAbsolutePath $root" in _function(helper, "Get-CBSourcePlan")
    assert "Assert-CBProfilePath $profile $target" in _function(helper, "Invoke-ClaudeBlogInstall")
    assert "Assert-CBProfilePath $profile $manifest" in _function(helper, "Invoke-ClaudeBlogInstall")
    assert "Assert-CBProfilePath $profile $target" in _function(helper, "Invoke-ClaudeBlogUninstall")
    temp = _function(helper, "New-CBTempDirectory")
    assert "Assert-CBNoReparseAbsolutePath $base" in temp
    assert "Assert-CBNoReparseAbsolutePath $path" in temp


def test_transaction_has_verified_stage_backup_rollback_and_late_receipt() -> None:
    helper = _read(HELPER)
    install = _function(helper, "Invoke-ClaudeBlogInstall")
    uninstall = _function(helper, "Invoke-ClaudeBlogUninstall")
    assert "staged payload hash mismatch" in install
    assert "backup verification failed" in _function(helper, "Copy-CBBackupSet")
    assert "Restore-CBTransaction" in install
    assert "Restore-CBTransaction" in uninstall
    assert "CLAUDE_BLOG_TEST_FAIL_AFTER_COPY" in install
    assert "CLAUDE_BLOG_TEST_FAIL_AFTER_DELETE" in uninstall
    exclusive = _function(helper, "Copy-CBFileExclusive")
    assert "FileMode]::CreateNew" in exclusive
    assert "FileShare]::None" in exclusive
    assert "Copy-CBFileExclusive" in install
    assert install.index("Move-Item -LiteralPath $manifestTemporary") > install.index("Move-Item -LiteralPath $temporary")
    assert uninstall.index("Remove-Item -LiteralPath $manifest") > uninstall.index("Remove-Item -LiteralPath $target")


def test_uninstall_prunes_only_empty_directories_and_preserves_shared_credentials() -> None:
    helper = _read(HELPER)
    prune = _function(helper, "Remove-CBEmptyParents")
    assert "Get-ChildItem -LiteralPath $directory -Force" in prune
    assert "Remove-Item -LiteralPath $directory -Force" in prune
    assert "-Recurse" not in prune
    uninstall = _read(UNINSTALL)
    assert "Shared Google credentials" in uninstall
    assert "oauth-token.json" not in uninstall
    assert "google-api.json" not in uninstall


def test_native_windows_smoke_is_executable_contract_not_claimed_linux_runtime() -> None:
    source = _read(SMOKE)
    for scenario in (
        "fresh install and idempotent update",
        "modified managed file refusal",
        "unknown collision refusal",
        "malformed receipt refusal",
        "copy rollback",
        "delete rollback",
        "legacy baseline migration",
        "junction refusal",
        "uninstall preserves extras",
        "selected ref installer handoff",
        "bootstrap creation collision preservation",
        "bootstrap clone failure cleanup",
        "legacy CRLF variant refusal",
        "uninstall junction refusal",
        "standalone receipt-backed uninstall",
    ):
        assert scenario in source
    assert "New-Item -ItemType Junction" in source
    assert "2500d4c765034864cede2bf215d00ccd4d7d6fb8" in source
    assert "Invoke-ClaudeBlogInstall" in source
    assert "Invoke-ClaudeBlogUninstall" in source
