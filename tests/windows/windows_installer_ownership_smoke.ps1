#!/usr/bin/env pwsh
# Native Windows disposable-profile acceptance suite for the ownership engine.
# Run from a complete repository checkout. It never uses the real USERPROFILE.
param([string]$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path)

$ErrorActionPreference = "Stop"
$Baseline = "2500d4c765034864cede2bf215d00ccd4d7d6fb8"
$Helper = Join-Path $RepositoryRoot "scripts/windows_installer_ownership.ps1"
$LegacyInventory = Join-Path $RepositoryRoot "data/legacy-install-ownership.json"
. $Helper

function Assert-True($Value, $Message) { if (-not $Value) { throw "ASSERTION FAILED: $Message" } }
function Assert-Throws($Action, $Message) {
    $threw = $false
    try { & $Action } catch { $threw = $true }
    if (-not $threw) { throw "ASSERTION FAILED: expected refusal, $Message" }
}
function New-Profile($Root, $Name) {
    $profile = Join-Path $Root $Name
    New-Item -ItemType Directory -Path $profile | Out-Null
    return $profile
}
function Manifest($Profile) { return Join-Path $Profile ".claude/claude-blog-manifest.txt" }
function ClaudeRoot($Profile) { return Join-Path $Profile ".claude" }
function Install-Package($Profile) {
    Invoke-ClaudeBlogInstall $RepositoryRoot (ClaudeRoot $Profile) (Manifest $Profile) $LegacyInventory "2.2.0" | Out-Null
}
function Invoke-DownloadedBootstrap($Script, $Profile, $Url, $Ref, $Identifier) {
    $oldProfile = $env:USERPROFILE
    $oldUrl = $env:CLAUDE_BLOG_URL
    $oldRef = $env:CLAUDE_BLOG_REF
    $oldIdentifier = $env:CLAUDE_BLOG_TEST_BOOTSTRAP_GUID
    try {
        $env:USERPROFILE = $Profile
        $env:CLAUDE_BLOG_URL = $Url
        $env:CLAUDE_BLOG_REF = $Ref
        $env:CLAUDE_BLOG_TEST_BOOTSTRAP_GUID = $Identifier
        $hostExecutable = (Get-Process -Id $PID).Path
        $process = Start-Process -FilePath $hostExecutable -ArgumentList @("-NoProfile", "-File", ('"' + $Script + '"')) -NoNewWindow -Wait -PassThru
        return $process.ExitCode
    } finally {
        $env:USERPROFILE = $oldProfile
        if ($null -eq $oldUrl) { Remove-Item Env:CLAUDE_BLOG_URL -ErrorAction SilentlyContinue } else { $env:CLAUDE_BLOG_URL = $oldUrl }
        if ($null -eq $oldRef) { Remove-Item Env:CLAUDE_BLOG_REF -ErrorAction SilentlyContinue } else { $env:CLAUDE_BLOG_REF = $oldRef }
        if ($null -eq $oldIdentifier) { Remove-Item Env:CLAUDE_BLOG_TEST_BOOTSTRAP_GUID -ErrorAction SilentlyContinue } else { $env:CLAUDE_BLOG_TEST_BOOTSTRAP_GUID = $oldIdentifier }
    }
}
function Snapshot($Path) {
    $items = @()
    if (Test-Path -LiteralPath $Path) {
        foreach ($_ in @(Get-ChildItem -LiteralPath $Path -Recurse -File -Force | Sort-Object FullName)) {
            $items += ($_.FullName.Substring($Path.Length) + '=' + (Get-CBSha256 $_.FullName))
        }
    }
    return ($items -join "`n")
}
function Write-RealLegacyBaseline($Profile, $Fixture) {
    $inventory = Get-Content -LiteralPath $LegacyInventory -Raw | ConvertFrom-Json
    foreach ($property in @($inventory.files.PSObject.Properties)) {
        $record = @($property.Value | Where-Object { $_.revision -eq $Baseline })[0]
        $source = Join-Path $Fixture ([string]$record.source)
        $target = Get-CBTargetPath (ClaudeRoot $Profile) $property.Name
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
        Copy-Item -LiteralPath $source -Destination $target
        Assert-True ((Get-CBSha256 $target) -eq $record.sha256) "baseline fixture hash for $($property.Name)"
    }
}

$RunRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("claude-blog-windows-smoke-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $RunRoot | Out-Null
try {
    $selectedRepo = Join-Path $RunRoot "selected-ref-repo"
    New-Item -ItemType Directory -Path $selectedRepo | Out-Null
    git -C $selectedRepo init --quiet
    git -C $selectedRepo config user.name "Disposable Windows Smoke"
    git -C $selectedRepo config user.email "smoke@example.invalid"
    $sentinelInstaller = @'
param()
$target = Join-Path $env:USERPROFILE "selected-ref-ran.txt"
[System.IO.File]::WriteAllText($target, "selected")
'@
    Set-Content -LiteralPath (Join-Path $selectedRepo "install.ps1") -Value $sentinelInstaller -Encoding UTF8
    git -C $selectedRepo add install.ps1
    git -C $selectedRepo commit --quiet -m "fixture"
    git -C $selectedRepo tag v2.2.0
    $downloadedBootstrap = Join-Path $RunRoot "downloaded-install.ps1"
    Copy-Item -LiteralPath (Join-Path $RepositoryRoot "install.ps1") -Destination $downloadedBootstrap

    Write-Host "SCENARIO: bootstrap creation collision preservation"
    $collisionIdentifier = [Guid]::NewGuid().ToString("N")
    $collisionRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("claude-blog-install-" + $collisionIdentifier)
    New-Item -ItemType Directory -Path $collisionRoot | Out-Null
    $collisionSentinel = Join-Path $collisionRoot "pre-existing-sentinel.txt"
    Set-Content -LiteralPath $collisionSentinel -Value "preserve"
    try {
        $collisionProfile = New-Profile $RunRoot "bootstrap-collision-profile"
        $collisionExit = Invoke-DownloadedBootstrap $downloadedBootstrap $collisionProfile $selectedRepo "v2.2.0" $collisionIdentifier
        Assert-True ($collisionExit -ne 0) "pre-existing bootstrap root is refused"
        Assert-True ((Get-Content -LiteralPath $collisionSentinel -Raw).Trim() -eq "preserve") "pre-existing bootstrap sentinel survives"
    } finally {
        Remove-Item -LiteralPath $collisionRoot -Recurse -Force -ErrorAction SilentlyContinue
    }

    Write-Host "SCENARIO: bootstrap clone failure cleanup"
    $failureIdentifier = [Guid]::NewGuid().ToString("N")
    $failureRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("claude-blog-install-" + $failureIdentifier)
    $failureSentinel = Join-Path $RunRoot "clone-failure-sentinel.txt"
    Set-Content -LiteralPath $failureSentinel -Value "preserve"
    $failureProfile = New-Profile $RunRoot "bootstrap-failure-profile"
    $failureExit = Invoke-DownloadedBootstrap $downloadedBootstrap $failureProfile (Join-Path $RunRoot "missing-repository") "v2.2.0" $failureIdentifier
    Assert-True ($failureExit -ne 0) "failed clone returns nonzero"
    Assert-True (-not (Test-Path -LiteralPath $failureRoot)) "owned failed-clone root is cleaned"
    Assert-True ((Get-Content -LiteralPath $failureSentinel -Raw).Trim() -eq "preserve") "external clone-failure sentinel survives"

    Write-Host "SCENARIO: selected ref installer handoff"
    $bootstrapProfile = New-Profile $RunRoot "selected-ref-profile"
    $handoffIdentifier = [Guid]::NewGuid().ToString("N")
    $bootstrapExit = Invoke-DownloadedBootstrap $downloadedBootstrap $bootstrapProfile $selectedRepo "v2.2.0" $handoffIdentifier
    Assert-True ($bootstrapExit -eq 0) "bootstrap succeeds"
    Assert-True (Test-Path -LiteralPath (Join-Path $bootstrapProfile "selected-ref-ran.txt")) "selected checkout installer executed"
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $bootstrapProfile ".claude"))) "bootstrap did not apply current payload"

    Write-Host "SCENARIO: fresh install and idempotent update"
    $p = New-Profile $RunRoot "fresh"
    Install-Package $p
    $before = Snapshot (ClaudeRoot $p)
    Install-Package $p
    Assert-True ((Snapshot (ClaudeRoot $p)) -eq $before) "idempotent install"

    Write-Host "SCENARIO: standalone receipt-backed uninstall"
    $standaloneProfile = New-Profile $RunRoot "standalone-uninstall-profile"
    Install-Package $standaloneProfile
    $standaloneDir = Join-Path $RunRoot "standalone-uninstaller"
    New-Item -ItemType Directory -Path $standaloneDir | Out-Null
    $standaloneUninstaller = Join-Path $standaloneDir "uninstall.ps1"
    Copy-Item -LiteralPath (Join-Path $RepositoryRoot "uninstall.ps1") -Destination $standaloneUninstaller
    $oldProfile = $env:USERPROFILE
    try {
        $env:USERPROFILE = $standaloneProfile
        $hostExecutable = (Get-Process -Id $PID).Path
        $standalone = Start-Process -FilePath $hostExecutable -ArgumentList @("-NoProfile", "-File", ('"' + $standaloneUninstaller + '"')) -NoNewWindow -Wait -PassThru
        Assert-True ($standalone.ExitCode -eq 0) "standalone uninstall succeeds"
        Assert-True (-not (Test-Path -LiteralPath (Manifest $standaloneProfile))) "standalone uninstall removes receipt last"
    } finally {
        $env:USERPROFILE = $oldProfile
    }

    Write-Host "SCENARIO: modified managed file refusal"
    $managed = Join-Path (ClaudeRoot $p) "skills/blog/SKILL.md"
    Add-Content -LiteralPath $managed -Value "user edit"
    $before = Snapshot (ClaudeRoot $p)
    Assert-Throws { Install-Package $p } "modified install"
    Assert-Throws { Invoke-ClaudeBlogUninstall (ClaudeRoot $p) (Manifest $p) $LegacyInventory } "modified uninstall"
    Assert-True ((Snapshot (ClaudeRoot $p)) -eq $before) "modified bytes and receipt preserved"

    Write-Host "SCENARIO: unknown collision refusal"
    $p = New-Profile $RunRoot "collision"
    $collision = Join-Path (ClaudeRoot $p) "agents/blog-writer.md"
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $collision) | Out-Null
    Set-Content -LiteralPath $collision -Value "unowned"
    $before = Snapshot (ClaudeRoot $p)
    Assert-Throws { Install-Package $p } "unknown agent collision"
    Assert-True ((Snapshot (ClaudeRoot $p)) -eq $before) "collision unchanged"

    Write-Host "SCENARIO: malformed receipt refusal"
    $p = New-Profile $RunRoot "malformed"
    Install-Package $p
    Set-Content -LiteralPath (Manifest $p) -Value '{"schema_version":2,"owner":"claude-blog-windows-installer","files":[{"path":"skills/blog/SKILL.md","sha256":"bad"}]}'
    $before = Snapshot (ClaudeRoot $p)
    Assert-Throws { Invoke-ClaudeBlogUninstall (ClaudeRoot $p) (Manifest $p) $LegacyInventory } "malformed receipt"
    Assert-True ((Snapshot (ClaudeRoot $p)) -eq $before) "malformed receipt causes zero deletion"

    Write-Host "SCENARIO: copy rollback"
    $p = New-Profile $RunRoot "copy-rollback"
    Install-Package $p
    $before = Snapshot (ClaudeRoot $p)
    $env:CLAUDE_BLOG_TEST_FAIL_AFTER_COPY = "2"
    try { Assert-Throws { Install-Package $p } "injected copy failure" }
    finally { Remove-Item Env:CLAUDE_BLOG_TEST_FAIL_AFTER_COPY -ErrorAction SilentlyContinue }
    Assert-True ((Snapshot (ClaudeRoot $p)) -eq $before) "copy rollback restores all bytes"

    Write-Host "SCENARIO: delete rollback"
    $p = New-Profile $RunRoot "delete-rollback"
    Install-Package $p
    $before = Snapshot (ClaudeRoot $p)
    $env:CLAUDE_BLOG_TEST_FAIL_AFTER_DELETE = "2"
    try { Assert-Throws { Invoke-ClaudeBlogUninstall (ClaudeRoot $p) (Manifest $p) $LegacyInventory } "injected delete failure" }
    finally { Remove-Item Env:CLAUDE_BLOG_TEST_FAIL_AFTER_DELETE -ErrorAction SilentlyContinue }
    Assert-True ((Snapshot (ClaudeRoot $p)) -eq $before) "delete rollback restores payload and receipt"

    Write-Host "SCENARIO: uninstall preserves extras"
    $p = New-Profile $RunRoot "extras"
    Install-Package $p
    $extra = Join-Path (ClaudeRoot $p) "skills/blog/user-notes.txt"
    Set-Content -LiteralPath $extra -Value "keep"
    Invoke-ClaudeBlogUninstall (ClaudeRoot $p) (Manifest $p) $LegacyInventory
    Assert-True (Test-Path -LiteralPath $extra -PathType Leaf) "user extra survives"
    Assert-True (-not (Test-Path -LiteralPath (Manifest $p))) "receipt removed after verified uninstall"

    Write-Host "SCENARIO: legacy baseline migration"
    $fixture = Join-Path $RunRoot "baseline"
    New-Item -ItemType Directory -Path $fixture | Out-Null
    git -C $RepositoryRoot archive $Baseline | tar -xf - -C $fixture
    if ($LASTEXITCODE -ne 0) { throw "could not extract real public baseline $Baseline" }
    $p = New-Profile $RunRoot "legacy"
    Write-RealLegacyBaseline $p $fixture
    $extra = Join-Path (ClaudeRoot $p) "skills/blog-write/custom.txt"
    Set-Content -LiteralPath $extra -Value "keep"
    Write-Host "SCENARIO: legacy CRLF variant refusal"
    $legacyChanged = Join-Path (ClaudeRoot $p) "agents/blog-writer.md"
    $legacyBytes = [System.IO.File]::ReadAllBytes($legacyChanged)
    $legacyText = [System.Text.Encoding]::UTF8.GetString($legacyBytes).Replace("`n", "`r`n")
    [System.IO.File]::WriteAllText($legacyChanged, $legacyText, (New-Object System.Text.UTF8Encoding($false)))
    $before = Snapshot (ClaudeRoot $p)
    Assert-Throws { Invoke-ClaudeBlogUninstall (ClaudeRoot $p) (Manifest $p) $LegacyInventory } "CRLF-converted legacy file"
    Assert-True ((Snapshot (ClaudeRoot $p)) -eq $before) "CRLF variant causes zero deletion"
    [System.IO.File]::WriteAllBytes($legacyChanged, $legacyBytes)
    Invoke-ClaudeBlogUninstall (ClaudeRoot $p) (Manifest $p) $LegacyInventory
    Assert-True (Test-Path -LiteralPath $extra) "legacy user extra survives"
    Assert-True (-not (Test-Path -LiteralPath (Join-Path (ClaudeRoot $p) "agents/blog-writer.md"))) "verified legacy file removed"

    Write-Host "SCENARIO: junction refusal"
    $p = New-Profile $RunRoot "junction"
    $outside = Join-Path $RunRoot "outside"
    New-Item -ItemType Directory -Path $outside | Out-Null
    $skillParent = Join-Path (ClaudeRoot $p) "skills"
    New-Item -ItemType Directory -Force -Path $skillParent | Out-Null
    New-Item -ItemType Junction -Path (Join-Path $skillParent "blog") -Target $outside | Out-Null
    Assert-Throws { Install-Package $p } "junction ancestor"
    Assert-True (-not @(Get-ChildItem -LiteralPath $outside -Force)) "junction target untouched"

    Write-Host "SCENARIO: uninstall junction refusal"
    $p = New-Profile $RunRoot "uninstall-junction"
    Install-Package $p
    $outsideBlog = Join-Path $RunRoot "outside-blog"
    Move-Item -LiteralPath (Join-Path (ClaudeRoot $p) "skills/blog") -Destination $outsideBlog
    New-Item -ItemType Junction -Path (Join-Path (ClaudeRoot $p) "skills/blog") -Target $outsideBlog | Out-Null
    $outsideBefore = Snapshot $outsideBlog
    Assert-Throws { Invoke-ClaudeBlogUninstall (ClaudeRoot $p) (Manifest $p) $LegacyInventory } "junction during uninstall"
    Assert-True ((Snapshot $outsideBlog) -eq $outsideBefore) "uninstall junction target untouched"
    Assert-True (Test-Path -LiteralPath (Manifest $p)) "receipt preserved after junction refusal"

    Write-Host "PASS: all native disposable-profile scenarios"
} finally {
    Remove-Item -LiteralPath $RunRoot -Recurse -Force -ErrorAction SilentlyContinue
}
