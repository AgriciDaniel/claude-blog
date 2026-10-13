"""Source contracts for the Windows ownership engine.

PowerShell is unavailable in the Linux review environment. These tests inspect
structural safety contracts only. The executable native smoke suite lives in
tests/windows/windows_installer_ownership_smoke.ps1 and remains a Windows gate.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest


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
    assert '$ClaudeBlogVersion = "2.3.1"' in install
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
    clone = install.index('$clone = Invoke-ClaudeBlogGit $GitCommand @("clone", "--depth"')
    handoff = install.index('$SelectedInstaller = Join-Path $ScriptDir "install.ps1"')
    current_helper = install.index('$OwnershipHelper = Join-Path $ScriptDir "scripts/windows_installer_ownership.ps1"')
    assert clone < handoff < current_helper
    assert "Start-Process -FilePath $HostExecutable" in install[handoff:current_helper]
    assert "selected ref installer failed" in install[handoff:current_helper]
    assert "return" in install[handoff:current_helper]


def test_bootstrap_git_uses_exit_codes_without_powershell_51_stderr_escalation() -> None:
    install = _read(INSTALL)
    resolve_git = _function(install, "Resolve-ClaudeBlogGitApplication")
    invoke_git = _function(install, "Invoke-ClaudeBlogGit")
    main = _function(install, "Main")
    assert "@(Get-Command git -CommandType Application -All -ErrorAction Stop)" in resolve_git
    assert "return $applications[0]" in resolve_git
    assert '$previousErrorActionPreference = $ErrorActionPreference' in invoke_git
    assert '$ErrorActionPreference = "Continue"' in invoke_git
    assert "2>$null" in invoke_git
    assert "$exitCode = $LASTEXITCODE" in invoke_git
    assert "$ErrorActionPreference = $previousErrorActionPreference" in invoke_git
    assert "ExitCode = $exitCode" in invoke_git
    assert "$GitCommand = Resolve-ClaudeBlogGitApplication" in main
    assert "if ($clone.ExitCode -ne 0)" in main
    assert "unable to clone repository (git exit $($clone.ExitCode))" in main
    assert "unable to clone $Url" not in main


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
    assert '@("clone", "--depth", "1", "--branch", $Ref, "--", $Url, $CheckoutDir)' in main
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


def test_native_smoke_avoids_pre_74_binary_pipelines() -> None:
    smoke = _read(SMOKE)
    assert "git -C $RepositoryRoot archive $Baseline | tar" not in smoke
    assert 'git -C $RepositoryRoot archive --format=tar --output $baselineArchive $Baseline' in smoke
    assert "tar -xf $baselineArchive -C $fixture" in smoke
    assert 'Join-Path $RunRoot ("baseline-" + $Baseline + ".tar")' in smoke


def test_native_smoke_covers_duplicate_git_resolution_and_exact_host_cache_lane() -> None:
    smoke = _read(SMOKE)
    assert 'Write-Host "SCENARIO: duplicate Git application resolution"' in smoke
    assert "Import-InstallerFunction $downloadedBootstrap \"Resolve-ClaudeBlogGitApplication\"" in smoke
    assert '@(Get-Command git -CommandType Application -All)' in smoke
    assert '@($resolvedGit).Count -eq 1' in smoke
    assert '"resolver selects first application in PATH"' in smoke
    assert '$env:LOCALAPPDATA = $hostState' not in smoke
    assert '$env:APPDATA = $hostState' not in smoke
    assert '$env:XDG_CACHE_HOME = $hostState' not in smoke
    assert '$env:POWERSHELL_TELEMETRY_OPTOUT = "1"' in smoke
    assert "Compare-Object" not in _function(smoke, "Assert-SnapshotEqual")
    assert '"failed clone does not mutate .claude"' in smoke
    assert '$PowerShellStartupCacheRelativePath = "\\AppData\\Local\\Microsoft\\PowerShell\\StartupProfileData-NonInteractive"' in smoke
    cache_comparison = _function(smoke, "Assert-SnapshotEqualExceptPowerShellStartupCache")
    assert "-eq $PowerShellStartupCacheRelativePath" in cache_comparison
    assert "-ne $PowerShellStartupCacheRelativePath" in cache_comparison
    assert "-like" not in cache_comparison
    assert "-match" not in cache_comparison
    assert "StartsWith" not in cache_comparison
    assert "Assert-SnapshotEqual ($beforeProtectedEntries" in cache_comparison
    assert 'Write-Host "PowerShell startup-cache lane evidence (relative path and SHA-256 only):"' in cache_comparison
    assert 'Write-Host "SCENARIO: exact PowerShell startup-cache allowance"' in smoke
    assert 'Assert-SnapshotEqualExceptPowerShellStartupCache "" ""' in smoke
    assert "StartupProfileData-Interactive=" in smoke
    assert '"\\.claude\\unexpected.txt="' in smoke
    assert "Assert-SnapshotEqualExceptPowerShellStartupCache $failureProfileBefore $failureProfileAfter" in smoke


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


# Force-adopt, deleted managed files, the pip step and git input validation.
# Static contracts first (always run). The executed tests below run the real
# PowerShell engine when pwsh exists (GitHub ubuntu runners ship it). Neither
# replaces the Windows PowerShell 5.1 and junction coverage of the native smoke.

UNIX_ENGINE = ROOT / "scripts/installer_ownership.py"


def test_automatic_variables_are_never_assigned() -> None:
    forbidden = re.compile(r"^\s*\$(input|matches|args|error|pid|home|profile|pwd|host|true|false|null)\s*=", re.IGNORECASE | re.MULTILINE)
    for path in (INSTALL, UNINSTALL, HELPER):
        text = _read(path)
        # $profile pre-dates this change in the engine's two entry points and is
        # a plain local there; every other automatic name is rejected outright.
        hits = [m.group(0).strip() for m in forbidden.finditer(text) if m.group(1).lower() != "profile"]
        assert not hits, f"{path.name} assigns an automatic variable: {hits}"
    def code(name: str) -> str:
        return "\n".join(line for line in _function(_read(HELPER), name).splitlines() if not line.strip().startswith("#"))

    assert not re.search(r"\$(input|output)\b", code("Copy-CBFileExclusive"))
    assert not re.search(r"\$matches\b", code("Get-CBCompleteLegacyRevision"), re.IGNORECASE)


def test_force_adopt_is_declared_validated_and_forwarded() -> None:
    install = _read(INSTALL)
    uninstall = _read(UNINSTALL)
    for source in (install, uninstall):
        assert "[switch]$ForceAdopt" in source
        assert "ValueFromRemainingArguments" in source
        assert '"--force-adopt" { $script:ForceAdoptRequested = $true }' in source
        assert "unknown option: $Argument (supported: -ForceAdopt, --force-adopt, --help)" in source
        assert "exit 2" in source
    assert "$script:ForceAdoptRequested" in _function(install, "Main")
    assert "$ForceAdoptRequested" not in install.split("function Main")[0].replace("$script:ForceAdoptRequested", "")
    handoff = install[install.index("$childArguments"):install.index("$child.ExitCode")]
    assert 'if ($script:ForceAdoptRequested) { $childArguments += "-ForceAdopt" }' in handoff
    assert "Invoke-ClaudeBlogInstall $ScriptDir $ClaudeDir $Manifest $LegacyInventory $ClaudeBlogVersion $script:ForceAdoptRequested" in install
    assert "Invoke-ClaudeBlogUninstall $ClaudeDir $Manifest $LegacyInventory $script:ForceAdoptRequested" in _function(uninstall, "Main")


def test_force_adopt_engine_mirrors_unix_semantics_and_messages() -> None:
    helper = _read(HELPER)
    unix = _read(UNIX_ENGINE)
    install = _function(helper, "Invoke-ClaudeBlogInstall")
    uninstall = _function(helper, "Invoke-ClaudeBlogUninstall")
    state = _function(helper, "Assert-CBOwnedFilesCurrent")
    backup = _function(helper, "Backup-CBModifiedFiles")
    message = _function(helper, "New-CBModifiedFilesMessage")
    assert "$ForceAdopt = $false" in install.split("{", 1)[0]
    assert "$ForceAdopt = $false" in uninstall.split("{", 1)[0]
    # A deleted managed file is tolerated only when forced; a replaced one never.
    assert "if ($Force) { $missing += $relative; continue }" in state
    assert 'throw "managed installation file is missing or replaced: $target"' in state
    assert "Test-CBReparsePoint $item" in state
    assert "if ($modified.Count -gt 0 -and -not $Force)" in state
    # Backup happens after every refusal and before the transaction mutates anything.
    for body in (install, uninstall):
        assert body.index("Backup-CBModifiedFiles $profile $modifiedOwned") < body.index("New-CBTempDirectory")
    assert install.index("refusing to overwrite an unowned existing file") < install.index("Backup-CBModifiedFiles")
    assert "Copy-CBFileExclusive $source $destination" in backup
    assert backup.count("Assert-CBProfilePath $claudeProfile $destination") == 2
    assert "Remove-Item" not in backup
    assert '"yyyyMMdd\'T\'HHmmss\'Z\'"' in backup and "InvariantCulture" in backup
    assert "Backed up modified file: " in backup
    # Same sentences as modified_files_error in the Unix engine.
    for sentence in (
        "Nothing was changed.",
        "installed file(s) differ from what the installer wrote,",
        "so the installer will not overwrite or delete them without your say-so.",
        "Safe steps:",
        "1. Copy any edit you want to keep to a location outside ~/.claude/skills, ~/.claude/agents",
        "and ~/.claude/scripts.",
        "Each modified file is first copied to",
        "3. Re-apply your edits from the backup if you still want them.",
        "Alternatively restore the original file contents and run the same command again.",
        "more modified file(s)",
    ):
        assert sentence in unix, sentence
        assert sentence in message, sentence
    assert "claude-blog-backups" in unix and '"claude-blog-backups"' in helper
    assert "$script:CBModifiedListLimit = 10" in helper and "MODIFIED_LIST_LIMIT = 10" in unix
    assert "reviewed legacy file was modified or is unknown" in install and "reviewed legacy file was modified or is unknown" in uninstall


def test_install_ps1_validates_git_inputs_and_guards_arguments() -> None:
    install = _read(INSTALL)
    main = _function(install, "Main")
    validator = _function(install, "Assert-ClaudeBlogGitInputs")
    assert main.index("Assert-ClaudeBlogGitInputs") < main.index("Invoke-ClaudeBlogGit $GitCommand")
    assert "^[A-Za-z0-9][A-Za-z0-9._/+@-]*$" in validator
    assert "'^-'" in validator and "ext|fd" in validator
    git_calls = re.findall(r'Invoke-ClaudeBlogGit \$GitCommand @\(([^)]*)\)', main)
    clone_calls = [call for call in git_calls if '"clone"' in call]
    assert len(clone_calls) == 2
    for call in clone_calls:
        assert call.index('"--"') < call.index("$Url"), call
    checkout = next(call for call in git_calls if '"checkout"' in call)
    assert checkout.rstrip().endswith('"--"') and "$Ref" in checkout


def test_install_ps1_dependency_step_mirrors_install_sh_and_reports_failure() -> None:
    install = _read(INSTALL)
    main = _function(install, "Main")
    shell = _read(ROOT / "install.sh")
    assert 'CLAUDE_BLOG_SKIP_PIP' in main and 'CLAUDE_BLOG_SKIP_PIP' in shell
    assert '$pipArguments += "--user"' in main and "pip_args=(--user" in shell
    assert "Test-PythonInVirtualEnvironment" in main and "sys.prefix != sys.base_prefix" in install
    assert '"-r", (\'"\' + $reqFile + \'"\')' in main
    assert '"-r",$reqFile' not in install
    failed = main.index('$DependencyStatus = "failed"')
    assert failed < main.index("Skills installed. Python dependencies FAILED") < main.index("Python deps:  FAILED")
    assert main.index("Skills installed. Python dependencies FAILED") < main.index("Installation Complete!")
    assert "The skills are installed; only the optional Python extras are missing." in main
    assert main.count('$DependencyStatus = "failed"') == 2  # pip exit code and pip could not start


def _pwsh() -> str:
    exe = shutil.which("pwsh")
    if not exe:
        pytest.skip("pwsh is not installed; the native Windows smoke remains the executable gate")
    return exe


def test_powershell_sources_parse(tmp_path: Path) -> None:
    exe = _pwsh()
    script = tmp_path / "parse.ps1"
    script.write_text(
        "$bad = 0\n"
        "foreach ($p in $args) {\n"
        "    $e = $null; $t = $null\n"
        "    [System.Management.Automation.Language.Parser]::ParseFile($p, [ref]$t, [ref]$e) | Out-Null\n"
        "    if ($e.Count) { $bad++; foreach ($err in $e) { \"$p`:$($err.Extent.StartLineNumber): $($err.Message)\" } }\n"
        "}\n"
        "exit $bad\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [exe, "-NoProfile", "-NonInteractive", "-File", str(script), str(INSTALL), str(UNINSTALL), str(HELPER), str(SMOKE)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


ENGINE_SCENARIOS = textwrap.dedent(
    r"""
    param($Helper, $Source, $Profile, $Legacy)
    $ErrorActionPreference = 'Stop'
    . $Helper
    $log = @()
    function Step($label, [scriptblock]$block) {
        try { & $block | Out-Null; $script:log += [ordered]@{ step = $label; ok = $true; message = '' } }
        catch { $script:log += [ordered]@{ step = $label; ok = $false; message = $_.Exception.Message } }
    }
    $manifest = Join-Path $Profile 'claude-blog-manifest.txt'
    $skill = Join-Path $Profile 'skills/blog/SKILL.md'
    $agent = Join-Path $Profile 'agents/blog-writer.md'
    $backups = Join-Path $Profile 'claude-blog-backups'
    function Install([bool]$force = $false) { Invoke-ClaudeBlogInstall $Source $Profile $manifest $Legacy '2.2.0' $force | Out-Null }
    function Uninstall([bool]$force = $false) { Invoke-ClaudeBlogUninstall $Profile $manifest $Legacy $force | Out-Null }
    Step 'fresh install' { Install }
    Add-Content -LiteralPath $skill -Value 'user edit'
    Step 'install refuses modified' { Install }
    Step 'uninstall refuses modified' { Uninstall }
    $edited = (Get-Content -LiteralPath $skill -Raw).Contains('user edit')
    Step 'install adopts modified' { Install $true }
    $backupFiles = @(Get-ChildItem -LiteralPath $backups -Recurse -File)
    $backupHoldsEdit = (Get-Content -LiteralPath $backupFiles[0].FullName -Raw).Contains('user edit')
    $replaced = -not (Get-Content -LiteralPath $skill -Raw).Contains('user edit')
    Remove-Item -LiteralPath $agent
    Step 'install refuses deleted' { Install }
    Step 'uninstall refuses deleted' { Uninstall }
    Step 'install tolerates deleted when forced' { Install $true }
    $restored = Test-Path -LiteralPath $agent
    Add-Content -LiteralPath $skill -Value 'second edit'
    Remove-Item -LiteralPath $agent
    Step 'uninstall tolerates modified and deleted when forced' { Uninstall $true }
    $gone = -not (Test-Path -LiteralPath $skill) -and -not (Test-Path -LiteralPath $manifest)
    Step 'reinstall' { Install }
    Add-Content -LiteralPath $skill -Value 'third edit'
    $elsewhere = Join-Path (Split-Path -Parent $Profile) 'elsewhere'
    New-Item -ItemType Directory -Force -Path $elsewhere | Out-Null
    Remove-Item -LiteralPath $backups -Recurse -Force
    New-Item -ItemType SymbolicLink -Path $backups -Target $elsewhere | Out-Null
    Step 'forced backup refuses a linked backup directory' { Install $true }
    $leaked = @(Get-ChildItem -LiteralPath $elsewhere -Force -Recurse).Count
    $kept = (Get-Content -LiteralPath $skill -Raw).Contains('third edit')
    [ordered]@{
        steps = $log; edited_after_refusals = $edited; backup_holds_edit = $backupHoldsEdit; replaced = $replaced
        restored = $restored; gone = $gone; leaked = $leaked; kept_after_link_refusal = $kept
    } | ConvertTo-Json -Depth 4
    """
)


def _mini_source(root: Path) -> Path:
    source = root / "source"
    files = {
        "skills/blog/SKILL.md": "# blog\n",
        "skills/blog/references/a.md": "reference\n",
        "skills/blog-write/SKILL.md": "# write\n",
        "agents/blog-writer.md": "agent\n",
        "scripts/example.py": "print('x')\n",
    }
    for relative, content in files.items():
        target = source / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")
    shutil.copy2(HELPER, source / "scripts/windows_installer_ownership.ps1")
    return source


def test_force_adopt_engine_executes_under_powershell(tmp_path: Path) -> None:
    exe = _pwsh()
    source = _mini_source(tmp_path)
    profile = tmp_path / "home" / ".claude"
    script = tmp_path / "scenarios.ps1"
    script.write_text(ENGINE_SCENARIOS, encoding="utf-8")
    result = subprocess.run(
        [exe, "-NoProfile", "-NonInteractive", "-File", str(script), str(HELPER), str(source), str(profile), str(LEGACY)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout[result.stdout.index("{"):])
    steps = {item["step"]: item for item in report["steps"]}
    for label in ("fresh install", "install adopts modified", "install tolerates deleted when forced",
                  "uninstall tolerates modified and deleted when forced", "reinstall"):
        assert steps[label]["ok"], steps[label]
    modified = steps["install refuses modified"]["message"]
    assert not steps["install refuses modified"]["ok"] and not steps["uninstall refuses modified"]["ok"]
    assert modified.startswith("managed installation file was modified: ")
    assert "pwsh -File ./install.ps1 -ForceAdopt" in modified
    assert "pwsh -File ./uninstall.ps1 -ForceAdopt" in steps["uninstall refuses modified"]["message"]
    assert "claude-blog-backups" in modified and "Nothing was changed." in modified
    assert report["edited_after_refusals"] is True
    assert report["backup_holds_edit"] and report["replaced"]
    for label in ("install refuses deleted", "uninstall refuses deleted"):
        assert not steps[label]["ok"] and "managed installation file is missing or replaced" in steps[label]["message"]
    assert report["restored"] and report["gone"]
    assert not steps["forced backup refuses a linked backup directory"]["ok"]
    assert "reparse point" in steps["forced backup refuses a linked backup directory"]["message"]
    assert report["leaked"] == 0 and report["kept_after_link_refusal"]
