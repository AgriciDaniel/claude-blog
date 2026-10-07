#!/usr/bin/env pwsh
# claude-blog installer for Windows
# Installs the blog skill ecosystem to ~/.claude/skills/ and ~/.claude/agents/
#
# Install (download first, then run so you can inspect it):
#   irm https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.ps1 -OutFile install.ps1
#   pwsh -File ./install.ps1

$ErrorActionPreference = "Stop"
$ClaudeBlogVersion = "2.2.0"

function Write-Color($Color, $Text) { Write-Host $Text -ForegroundColor $Color }

function Resolve-ClaudeBlogGitApplication {
    $applications = @(Get-Command git -CommandType Application -All -ErrorAction Stop)
    if ($applications.Count -eq 0) { throw "Git executable was not found" }
    # Get-Command -All returns commands in execution-precedence order. Keep one
    # ApplicationInfo so its Source cannot expand into concatenated paths.
    return $applications[0]
}

function Invoke-ClaudeBlogGit($GitCommand, [string[]]$Arguments, [switch]$CaptureOutput) {
    # Windows PowerShell 5.1 promotes redirected native stderr to an error
    # record. Git writes routine progress there, so use its exit code as the
    # failure signal while this one native invocation is in progress.
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        if ($CaptureOutput) {
            $commandOutput = @(& $GitCommand.Source @Arguments 2>$null)
        } else {
            & $GitCommand.Source @Arguments *> $null
            $commandOutput = @()
        }
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    return [PSCustomObject]@{ ExitCode = $exitCode; Output = $commandOutput }
}

function Assert-ClaudeBlogNoReparsePath($Path) {
    $full = [System.IO.Path]::GetFullPath($Path)
    $root = [System.IO.Path]::GetPathRoot($full)
    $current = $root
    foreach ($part in @($full.Substring($root.Length).Split([System.IO.Path]::DirectorySeparatorChar) | Where-Object { $_ })) {
        $current = Join-Path $current $part
        if (-not (Test-Path -LiteralPath $current)) { break }
        $item = Get-Item -LiteralPath $current -Force
        if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "unsafe reparse point in temporary path: $current"
        }
    }
}

function New-ClaudeBlogOwnedTempRoot($Purpose, $Identifier) {
    if ($Purpose -notin @('install', 'pip')) { throw "invalid temporary directory purpose" }
    $suffix = if ($Identifier) { $Identifier.ToLowerInvariant() } else { [System.Guid]::NewGuid().ToString('N') }
    if ($suffix -notmatch '^[0-9a-f]{32}$') { throw "invalid bootstrap directory identifier" }
    $temp = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
    Assert-ClaudeBlogNoReparsePath $temp
    $root = Join-Path $temp ("claude-blog-" + $Purpose + "-" + $suffix)
    New-Item -ItemType Directory -Path $root -ErrorAction Stop | Out-Null
    Assert-ClaudeBlogNoReparsePath $root
    $token = [System.Guid]::NewGuid().ToString('N')
    $marker = Join-Path $root ".claude-blog-bootstrap-owner"
    $stream = $null
    try {
        $stream = [System.IO.File]::Open($marker, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($token)
        $stream.Write($bytes, 0, $bytes.Length)
    } catch {
        Remove-Item -LiteralPath $root -Force -ErrorAction SilentlyContinue
        throw
    } finally {
        if ($stream) { $stream.Dispose() }
    }
    return [PSCustomObject]@{ Root = $root; Token = $token }
}

function Remove-ClaudeBlogOwnedTempRoot($Root, $Token) {
    if (-not $Root -or -not $Token -or -not (Test-Path -LiteralPath $Root -PathType Container)) { return }
    $fullRoot = [System.IO.Path]::GetFullPath($Root).TrimEnd('\', '/')
    $tempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd('\', '/')
    if (-not (Split-Path -Parent $fullRoot).Equals($tempRoot, [System.StringComparison]::OrdinalIgnoreCase) -or
        (Split-Path -Leaf $fullRoot) -notmatch '^claude-blog-(install|pip)-[0-9a-f]{32}$') {
        Write-Warning "refusing to clean an unexpected bootstrap path: $fullRoot"
        return
    }
    try { Assert-ClaudeBlogNoReparsePath $fullRoot }
    catch {
        Write-Warning "refusing to clean an unsafe bootstrap path: $fullRoot"
        return
    }
    $rootItem = Get-Item -LiteralPath $fullRoot -Force
    if (($rootItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        Write-Warning "refusing to clean a reparse-point bootstrap path: $fullRoot"
        return
    }
    $marker = Join-Path $fullRoot ".claude-blog-bootstrap-owner"
    if (-not (Test-Path -LiteralPath $marker -PathType Leaf)) {
        Write-Warning "refusing to clean a bootstrap path without its ownership marker: $fullRoot"
        return
    }
    $markerItem = Get-Item -LiteralPath $marker -Force
    try { $markerToken = [System.IO.File]::ReadAllText($marker) }
    catch {
        Write-Warning "refusing to clean an unreadable bootstrap ownership marker: $fullRoot"
        return
    }
    if (($markerItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0 -or $markerToken -ne $Token) {
        Write-Warning "refusing to clean a bootstrap path with invalid ownership evidence: $fullRoot"
        return
    }
    Remove-Item -LiteralPath $fullRoot -Recurse -Force -ErrorAction SilentlyContinue
}

function Count-Files($Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return 0 }
    return @(Get-ChildItem -LiteralPath $Path -Recurse -File | Where-Object {
        $_.FullName -notmatch '[\\/]+__pycache__[\\/]+' -and $_.Name -notlike '*.pyc'
    }).Count
}

function Test-Python311($PythonCommand) {
    try {
        & $PythonCommand.Source -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" *> $null
        return $LASTEXITCODE -eq 0
    } catch { return $false }
}

function Get-PythonVersion($PythonCommand) {
    try { return (& $PythonCommand.Source -c "import sys; print('%d.%d.%d' % sys.version_info[:3])" 2>$null).Trim() }
    catch { return "unknown" }
}

function Print-Commands($SkillMd) {
    if (-not (Test-Path -LiteralPath $SkillMd)) { return }
    Get-Content -LiteralPath $SkillMd | ForEach-Object {
        if ($_ -match '^\|\s*`/blog\s+([^`]+)`\s*\|\s*([^|]+)\|') {
            $cmd = ("/blog " + $Matches[1]).Replace('\|', '|').Trim()
            Write-Color Cyan ("    {0,-38} {1}" -f $cmd, $Matches[2].Trim())
        }
    }
}

function Main {
    Write-Color Cyan @"

   ╔══════════════════════════════════════╗
   ║         claude-blog Installer        ║
   ║  Blog Content Engine for Claude Code ║
   ╚══════════════════════════════════════╝

"@
    Write-Color White "Release: $ClaudeBlogVersion"
    Write-Color White ""

    $BootstrapRoot = $null
    $BootstrapToken = $null
    $BootstrapOwned = $false
    try {
        if ($PSScriptRoot -and (Test-Path -LiteralPath (Join-Path $PSScriptRoot "skills/blog"))) {
            $ScriptDir = $PSScriptRoot
        } else {
            $Repo = if ($env:CLAUDE_BLOG_REPO) { $env:CLAUDE_BLOG_REPO } else { "AgriciDaniel/claude-blog" }
            $Ref = if ($env:CLAUDE_BLOG_REF) { $env:CLAUDE_BLOG_REF } else { "main" }
            $Url = if ($env:CLAUDE_BLOG_URL) { $env:CLAUDE_BLOG_URL } else { "https://github.com/$Repo.git" }
            Write-Color White "Cloning claude-blog from $Repo ($Ref)..."
            $bootstrap = New-ClaudeBlogOwnedTempRoot 'install' $env:CLAUDE_BLOG_TEST_BOOTSTRAP_GUID
            $BootstrapRoot = $bootstrap.Root
            $BootstrapToken = $bootstrap.Token
            $BootstrapOwned = $true
            $CheckoutDir = Join-Path $BootstrapRoot "checkout"
            Assert-ClaudeBlogNoReparsePath $BootstrapRoot
            $GitCommand = Resolve-ClaudeBlogGitApplication
            $clone = Invoke-ClaudeBlogGit $GitCommand @("clone", "--depth", "1", "--branch", $Ref, $Url, $CheckoutDir)
            if ($clone.ExitCode -ne 0) {
                $CheckoutDir = Join-Path $BootstrapRoot "checkout-fallback"
                Assert-ClaudeBlogNoReparsePath $BootstrapRoot
                $clone = Invoke-ClaudeBlogGit $GitCommand @("clone", $Url, $CheckoutDir)
                if ($clone.ExitCode -ne 0) { throw "unable to clone repository (git exit $($clone.ExitCode))" }
                $checkout = Invoke-ClaudeBlogGit $GitCommand @("-C", $CheckoutDir, "checkout", "--detach", $Ref)
                if ($checkout.ExitCode -ne 0) { throw "unable to check out requested ref (git exit $($checkout.ExitCode))" }
            }
            $ScriptDir = $CheckoutDir
            $revParse = Invoke-ClaudeBlogGit $GitCommand @("-C", $ScriptDir, "rev-parse", "--short", "HEAD") -CaptureOutput
            if ($revParse.ExitCode -ne 0) { throw "unable to identify checked out revision (git exit $($revParse.ExitCode))" }
            $CheckedOut = ($revParse.Output -join "`n").Trim()
            Write-Color Green "  + checked out $CheckedOut"
            if ($Ref -eq "main") { Write-Color Yellow "  Tip: set CLAUDE_BLOG_REF to a tag or commit SHA for a pinned install." }

            # The selected ref owns its installation semantics. This also keeps
            # pinned older refs working when they predate the current ownership
            # helper or reviewed legacy inventory.
            $SelectedInstaller = Join-Path $ScriptDir "install.ps1"
            if (-not (Test-Path -LiteralPath $SelectedInstaller -PathType Leaf)) {
                throw "selected ref does not contain install.ps1: $Ref"
            }
            Assert-ClaudeBlogNoReparsePath $SelectedInstaller
            $HostExecutable = (Get-Process -Id $PID).Path
            $child = Start-Process -FilePath $HostExecutable -ArgumentList @("-NoProfile", "-File", ('"' + $SelectedInstaller + '"')) -NoNewWindow -Wait -PassThru
            if ($child.ExitCode -ne 0) { throw "selected ref installer failed with exit $($child.ExitCode)" }
            return
        }

        $OwnershipHelper = Join-Path $ScriptDir "scripts/windows_installer_ownership.ps1"
        $LegacyInventory = Join-Path $ScriptDir "data/legacy-install-ownership.json"
        if (-not (Test-Path -LiteralPath $OwnershipHelper -PathType Leaf)) { throw "Windows ownership helper is missing: $OwnershipHelper" }
        if (-not (Test-Path -LiteralPath $LegacyInventory -PathType Leaf)) { throw "Reviewed legacy ownership inventory is missing: $LegacyInventory" }
        . $OwnershipHelper

        $PythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
        if (-not $PythonCmd) { $PythonCmd = Get-Command python -ErrorAction SilentlyContinue }
        if (-not $PythonCmd) {
            Write-Color Yellow "WARNING: Python not found. The scripts require Python 3.11+."
        } elseif (-not (Test-Python311 $PythonCmd)) {
            Write-Color Yellow "WARNING: Python $(Get-PythonVersion $PythonCmd) found. The scripts require Python 3.11+."
        }

        $ClaudeDir = Join-Path $env:USERPROFILE ".claude"
        $Manifest = Join-Path $ClaudeDir "claude-blog-manifest.txt"
        Write-Color White "Preflighting ownership and staging package files..."
        $Stats = Invoke-ClaudeBlogInstall $ScriptDir $ClaudeDir $Manifest $LegacyInventory $ClaudeBlogVersion

        Write-Color White "Installing Python dependencies..."
        $reqFile = Join-Path $ScriptDir "requirements.txt"
        if (Test-Path -LiteralPath $reqFile) {
            if ($PythonCmd) {
                $pipTemp = New-ClaudeBlogOwnedTempRoot 'pip' $env:CLAUDE_BLOG_TEST_PIP_GUID
                $pipRoot = $pipTemp.Root
                $pipToken = $pipTemp.Token
                $pipLog = Join-Path $pipRoot "pip-stderr.log"
                $retainPipLog = $true
                try {
                    Assert-ClaudeBlogNoReparsePath $pipRoot
                    if (Test-Path -LiteralPath $pipLog) { throw "refusing a pre-existing pip log path: $pipLog" }
                    $proc = Start-Process -FilePath $PythonCmd.Source -ArgumentList @("-m","pip","install","--quiet","-r",$reqFile) -RedirectStandardError $pipLog -NoNewWindow -Wait -PassThru
                    Assert-ClaudeBlogNoReparsePath $pipLog
                    if ($proc.ExitCode -eq 0) {
                        Write-Color Green "  Python dependencies installed."
                        $retainPipLog = $false
                    } else {
                        Write-Color Yellow "  WARNING: pip install failed (exit $($proc.ExitCode))."
                        Write-Color Yellow "  See retained log: $pipLog"
                        Write-Color Yellow "  Manual install: pip install -r requirements.txt"
                    }
                } catch {
                    Write-Color Yellow "  WARNING: pip could not be started: $($_.Exception.Message)"
                    if (Test-Path -LiteralPath $pipLog -PathType Leaf) {
                        try {
                            Assert-ClaudeBlogNoReparsePath $pipLog
                            Write-Color Yellow "  See retained log: $pipLog"
                        } catch {
                            Write-Color Yellow "  The pip log path was unsafe and was not opened."
                        }
                    } else {
                        $retainPipLog = $false
                    }
                    Write-Color Yellow "  Manual install: pip install -r requirements.txt"
                } finally {
                    if (-not $retainPipLog) { Remove-ClaudeBlogOwnedTempRoot $pipRoot $pipToken }
                }
            } else {
                Write-Color Yellow "  Skipped: Python not found. Manual install: pip install -r requirements.txt"
            }
        }

        $SkillDir = Join-Path $ClaudeDir "skills"
        Write-Color Cyan @"

   ╔══════════════════════════════════════╗
   ║       Installation Complete!         ║
   ╚══════════════════════════════════════╝

"@
        Write-Color White "Installed:"
        Write-Color Green "  Main skill:   blog/ (orchestrator + $(Count-Files (Join-Path $SkillDir 'blog/references')) references + $(Count-Files (Join-Path $SkillDir 'blog/templates')) templates)"
        Write-Color Green "  Sub-skills:   $($Stats.SubSkillCount) installed"
        Write-Color Green "  Agents:       $($Stats.AgentCount) specialists"
        Write-Color Green "  Scripts:      $($Stats.RootScriptCount) root-level + per-skill scripts"
        Write-Color Green "  Manifest:     $Manifest"
        Write-Color White ""
        Write-Color White "Commands available:"
        Print-Commands (Join-Path $ScriptDir "skills/blog/SKILL.md")
        Write-Color White ""
        Write-Color White "Optional: AI Features (same API key for both)"
        Write-Color Cyan  "  /blog image setup             Configure Gemini image generation"
        Write-Color Cyan  "  /blog audio setup             Configure Gemini TTS audio narration"
        Write-Color White "  Requires: Google AI API key (free at https://aistudio.google.com/apikey)"
        Write-Color White ""
        Write-Color Yellow "Restart Claude Code to activate the new skill."
    } finally {
        if ($BootstrapOwned) { Remove-ClaudeBlogOwnedTempRoot $BootstrapRoot $BootstrapToken }
    }
}

try { Main }
catch {
    Write-Error "claude-blog installation failed before ownership could be committed: $($_.Exception.Message)"
    exit 1
}
