#!/usr/bin/env pwsh
# claude-blog uninstaller for Windows
# Removes only files proven to be owned by this package.

$ErrorActionPreference = "Stop"

function Write-Color($Color, $Text) { Write-Host $Text -ForegroundColor $Color }

function Assert-NoReparseChain($Path) {
    $full = [System.IO.Path]::GetFullPath($Path)
    $root = [System.IO.Path]::GetPathRoot($full)
    $current = $root
    foreach ($part in @($full.Substring($root.Length).Split([System.IO.Path]::DirectorySeparatorChar) | Where-Object { $_ })) {
        $current = Join-Path $current $part
        if (-not (Test-Path -LiteralPath $current)) { break }
        $item = Get-Item -LiteralPath $current -Force
        if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "unsafe reparse point in ownership helper path: $current"
        }
    }
}

function Resolve-OwnershipHelper($ClaudeDir, $Manifest) {
    if ($PSScriptRoot) {
        $repositoryHelper = Join-Path $PSScriptRoot "scripts/windows_installer_ownership.ps1"
        if (Test-Path -LiteralPath $repositoryHelper -PathType Leaf) {
            Assert-NoReparseChain $repositoryHelper
            return $repositoryHelper
        }
    }
    $installedHelper = Join-Path $ClaudeDir "scripts/windows_installer_ownership.ps1"
    if (-not (Test-Path -LiteralPath $installedHelper -PathType Leaf) -or -not (Test-Path -LiteralPath $Manifest -PathType Leaf)) {
        throw "Windows ownership helper is unavailable. Run uninstall.ps1 from the complete reviewed repository."
    }
    Assert-NoReparseChain $Manifest
    Assert-NoReparseChain $installedHelper
    try { $receipt = Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json -ErrorAction Stop }
    catch { throw "the installed ownership helper cannot be trusted without a valid v2 receipt" }
    if ($receipt.schema_version -ne 2 -or $receipt.owner -ne "claude-blog-windows-installer") {
        throw "the installed ownership helper cannot be trusted without a valid v2 receipt"
    }
    $records = @($receipt.files | Where-Object { $_.path -eq "scripts/windows_installer_ownership.ps1" })
    if ($records.Count -ne 1 -or ([string]$records[0].sha256) -notmatch '^[0-9a-f]{64}$') {
        throw "the v2 receipt does not uniquely prove ownership of the installed helper"
    }
    $actual = (Get-FileHash -LiteralPath $installedHelper -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne ([string]$records[0].sha256).ToLowerInvariant()) {
        throw "the installed ownership helper was modified"
    }
    return $installedHelper
}

function Resolve-LegacyInventory {
    if ($PSScriptRoot) {
        $candidate = Join-Path $PSScriptRoot "data/legacy-install-ownership.json"
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
    }
    return $null
}

function Main {
    $ClaudeDir = Join-Path $env:USERPROFILE ".claude"
    $Manifest = Join-Path $ClaudeDir "claude-blog-manifest.txt"
    Write-Color Cyan "=== Uninstalling claude-blog ==="
    Write-Host ""

    $OwnershipHelper = Resolve-OwnershipHelper $ClaudeDir $Manifest
    $LegacyInventory = Resolve-LegacyInventory
    . $OwnershipHelper
    Invoke-ClaudeBlogUninstall $ClaudeDir $Manifest $LegacyInventory

    Write-Color Yellow "  Shared Google credentials under ~/.config/claude-seo were left intact."
    Write-Host ""
    Write-Color Cyan "=== claude-blog uninstalled ==="
    Write-Host ""
    Write-Color Yellow "Restart Claude Code to complete removal."
}

try { Main }
catch {
    Write-Error "claude-blog uninstall refused without complete ownership proof: $($_.Exception.Message)"
    exit 1
}
