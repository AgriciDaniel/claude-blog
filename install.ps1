#!/usr/bin/env pwsh
# claude-blog installer for Windows
# Installs the blog skill ecosystem to ~/.claude/skills/ and ~/.claude/agents/
#
# Install (download first, then run so you can inspect it):
#   irm https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.ps1 -OutFile install.ps1
#   pwsh -File ./install.ps1

$ErrorActionPreference = "Stop"
$ClaudeBlogVersion = "2.2.0"

function Write-Color($Color, $Text) {
    Write-Host $Text -ForegroundColor $Color
}

function Copy-Tree($Source, $Destination) {
    if (-not (Test-Path -LiteralPath $Source)) {
        return
    }
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    $sourceRoot = (Resolve-Path -LiteralPath $Source).Path.TrimEnd('\', '/')
    Get-ChildItem -LiteralPath $Source -Recurse -File | Where-Object {
        $_.FullName -notmatch '[\\/]+__pycache__[\\/]+' -and $_.Name -notlike '*.pyc'
    } | ForEach-Object {
        $relative = $_.FullName.Substring($sourceRoot.Length).TrimStart('\', '/')
        $target = Join-Path $Destination $relative
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
        Copy-Item -LiteralPath $_.FullName -Destination $target -Force
    }
}

function Count-Files($Path) {
    if (-not (Test-Path -LiteralPath $Path)) {
        return 0
    }
    return @(Get-ChildItem -LiteralPath $Path -Recurse -File | Where-Object {
        $_.FullName -notmatch '[\\/]+__pycache__[\\/]+' -and $_.Name -notlike '*.pyc'
    }).Count
}

function Test-Python311($PythonCommand) {
    try {
        & $PythonCommand.Source -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" *> $null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Get-PythonVersion($PythonCommand) {
    try {
        return (& $PythonCommand.Source -c "import sys; print('%d.%d.%d' % sys.version_info[:3])" 2>$null).Trim()
    } catch {
        return "unknown"
    }
}

function Print-Commands($SkillMd) {
    if (-not (Test-Path -LiteralPath $SkillMd)) {
        return
    }
    Get-Content -LiteralPath $SkillMd | ForEach-Object {
        if ($_ -match '^\|\s*`/blog\s+([^`]+)`\s*\|\s*([^|]+)\|') {
            $cmd = ("/blog " + $Matches[1]).Replace('\|', '|').Trim()
            $desc = $Matches[2].Trim()
            Write-Color Cyan ("    {0,-38} {1}" -f $cmd, $desc)
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

    $SkillDir = Join-Path (Join-Path $env:USERPROFILE ".claude") "skills"
    $AgentDir = Join-Path (Join-Path $env:USERPROFILE ".claude") "agents"
    $TempDir = $null

    # Determine source directory (local clone or piped from irm)
    if ($PSScriptRoot -and (Test-Path (Join-Path (Join-Path $PSScriptRoot "skills") "blog"))) {
        $ScriptDir = $PSScriptRoot
    } else {
        $Repo = if ($env:CLAUDE_BLOG_REPO) { $env:CLAUDE_BLOG_REPO } else { "AgriciDaniel/claude-blog" }
        $Ref = if ($env:CLAUDE_BLOG_REF) { $env:CLAUDE_BLOG_REF } else { "main" }
        $Url = if ($env:CLAUDE_BLOG_URL) { $env:CLAUDE_BLOG_URL } else { "https://github.com/$Repo.git" }
        Write-Color White "Cloning claude-blog from $Repo ($Ref)..."
        $TempDir = Join-Path ([System.IO.Path]::GetTempPath()) "claude-blog-install-$([System.Guid]::NewGuid().ToString('N').Substring(0,8))"
        git clone --depth 1 --branch $Ref $Url $TempDir 2>$null
        if ($LASTEXITCODE -ne 0) {
            git clone $Url $TempDir 2>$null
            git -C $TempDir checkout --detach $Ref *> $null
        }
        $ScriptDir = $TempDir
        $CheckedOut = git -C $ScriptDir rev-parse --short HEAD
        Write-Color Green "  + checked out $CheckedOut"
        if ($Ref -eq "main") {
            Write-Color Yellow "  Tip: set CLAUDE_BLOG_REF to a tag or commit SHA for a pinned install."
        }
    }

    # Check prerequisites
    $PythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
    if (-not $PythonCmd) { $PythonCmd = Get-Command python -ErrorAction SilentlyContinue }
    if (-not $PythonCmd) {
        Write-Color Yellow "WARNING: Python not found. The scripts require Python 3.11+."
    } elseif (-not (Test-Python311 $PythonCmd)) {
        $PythonVersion = Get-PythonVersion $PythonCmd
        Write-Color Yellow "WARNING: Python $PythonVersion found. The scripts require Python 3.11+."
    }

    # Create directories
    Write-Color White "Creating directories..."
    New-Item -ItemType Directory -Force -Path (Join-Path (Join-Path $SkillDir "blog") "references") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path (Join-Path $SkillDir "blog") "templates") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path (Join-Path $SkillDir "blog") "scripts") | Out-Null
    New-Item -ItemType Directory -Force -Path $AgentDir | Out-Null

    # Copy main skill
    Write-Color White "Installing main skill: blog..."
    Copy-Item (Join-Path (Join-Path (Join-Path $ScriptDir "skills") "blog") "SKILL.md") (Join-Path (Join-Path $SkillDir "blog") "SKILL.md") -Force

    # Copy references
    Write-Color White "Installing reference files..."
    Copy-Tree (Join-Path (Join-Path (Join-Path $ScriptDir "skills") "blog") "references") (Join-Path (Join-Path $SkillDir "blog") "references")

    # Copy templates
    if (Test-Path (Join-Path (Join-Path (Join-Path $ScriptDir "skills") "blog") "templates")) {
        Write-Color White "Installing content templates..."
        Copy-Tree (Join-Path (Join-Path (Join-Path $ScriptDir "skills") "blog") "templates") (Join-Path (Join-Path $SkillDir "blog") "templates")
    }

    # Preserve the repository's data/google-updates.json ledger inside the
    # standalone blog skill payload.
    $GoogleLedger = Join-Path (Join-Path $ScriptDir "data") "google-updates.json"
    if (Test-Path -LiteralPath $GoogleLedger) {
        Write-Color White "Installing Google update ledger..."
        $BlogDataDir = Join-Path (Join-Path $SkillDir "blog") "data"
        New-Item -ItemType Directory -Force -Path $BlogDataDir | Out-Null
        Copy-Item -LiteralPath $GoogleLedger -Destination (Join-Path $BlogDataDir "google-updates.json") -Force
    }

    # Copy sub-skills (auto-discovers all skill directories)
    Write-Color White "Installing sub-skills..."
    $SubSkillCount = 0
    $SkillEntries = @(Get-ChildItem -Directory (Join-Path $ScriptDir "skills"))
    foreach ($SkillEntry in $SkillEntries) {
        $skillName = $SkillEntry.Name
        if ($skillName -eq "blog") { continue }
        $skillDst = Join-Path $SkillDir $skillName
        New-Item -ItemType Directory -Force -Path $skillDst | Out-Null

        # Copy SKILL.md
        $src = Join-Path $SkillEntry.FullName "SKILL.md"
        if (Test-Path $src) {
            Copy-Item $src (Join-Path $skillDst "SKILL.md") -Force
            Write-Color Green "  + $skillName"
            $SubSkillCount++
        }

        foreach ($payloadDir in @("references", "scripts", "assets", "templates")) {
            Copy-Tree (Join-Path $SkillEntry.FullName $payloadDir) (Join-Path $skillDst $payloadDir)
        }
    }

    # Create personas directory for blog-persona
    New-Item -ItemType Directory -Force -Path (Join-Path (Join-Path (Join-Path $SkillDir "blog") "references") "personas") | Out-Null

    # Copy agents
    Write-Color White "Installing agents..."
    $AgentCount = 0
    $AgentFiles = @(Get-ChildItem -File (Join-Path (Join-Path $ScriptDir "agents") "*.md"))
    foreach ($AgentFile in $AgentFiles) {
        Copy-Item $AgentFile.FullName (Join-Path $AgentDir $AgentFile.Name) -Force
        Write-Color Green "  + $($AgentFile.BaseName)"
        $AgentCount++
    }

    # Copy scripts (v1.8.6: ALL root-level scripts, not just analyze_blog.py).
    # Closes 7TH-AUDIT-001: the v1.8.0+ helpers (cognitive_load,
    # discourse_research, load_untrusted_root, lint_prose, sync_flow) were
    # never shipped, breaking the v1.8.3 code-enforced contract for end users.
    Write-Color White "Installing scripts..."
    $ClaudeScriptsDir = Join-Path $env:USERPROFILE ".claude\scripts"
    if (-not (Test-Path $ClaudeScriptsDir)) {
        New-Item -ItemType Directory -Force -Path $ClaudeScriptsDir | Out-Null
    }
    $RootScriptCount = 0
    $RootScripts = @(Get-ChildItem -File (Join-Path (Join-Path $ScriptDir "scripts") "*.py"))
    foreach ($RootScript in $RootScripts) {
        Copy-Item $RootScript.FullName (Join-Path $ClaudeScriptsDir $RootScript.Name) -Force
        if ($RootScript.Name -eq "analyze_blog.py") {
            Copy-Item $RootScript.FullName (Join-Path (Join-Path (Join-Path $SkillDir "blog") "scripts") $RootScript.Name) -Force
        }
        Write-Color Green "  + scripts/$($RootScript.Name)"
        $RootScriptCount++
    }

    # Install Python dependencies (closes audit VULN-507/804: capture stderr
    # to a logfile instead of swallowing it).
    Write-Color White "Installing Python dependencies..."
    $reqFile = Join-Path $ScriptDir "requirements.txt"
    if (Test-Path $reqFile) {
        $pipLog = Join-Path ([System.IO.Path]::GetTempPath()) "claude-blog-pip-$([System.Guid]::NewGuid().ToString('N').Substring(0,8)).log"
        # Resolve python: prefer python3, fall back to python. Avoid the `??`
        # null-coalescing operator (PowerShell 7+ only) so this works on the
        # default Windows PowerShell 5.1.
        $pipCmd = $PythonCmd
        if ($pipCmd) {
            $proc = Start-Process -FilePath $pipCmd.Source -ArgumentList @("-m","pip","install","--quiet","-r",$reqFile) -RedirectStandardError $pipLog -NoNewWindow -Wait -PassThru
            if ($proc.ExitCode -eq 0) {
                Write-Color Green "  Python dependencies installed."
                Remove-Item -Force $pipLog -ErrorAction SilentlyContinue
            } else {
                Write-Color Yellow "  WARNING: pip install failed (exit $($proc.ExitCode))."
                Write-Color Yellow "  See log: $pipLog"
                Write-Color Yellow "  Manual install: pip install -r requirements.txt"
            }
        } else {
            Write-Color Yellow "  Skipped: Python not found. Manual install: pip install -r requirements.txt"
        }
    }

    # Cleanup temp directory if used
    if ($TempDir -and (Test-Path $TempDir)) {
        Remove-Item -Recurse -Force $TempDir
    }

    # Summary
    Write-Color Cyan @"

   ╔══════════════════════════════════════╗
   ║       Installation Complete!         ║
   ╚══════════════════════════════════════╝

"@

    Write-Color White "Installed:"
    Write-Color Green "  Main skill:   blog/ (orchestrator + $(Count-Files (Join-Path (Join-Path $SkillDir "blog") "references")) references + $(Count-Files (Join-Path (Join-Path $SkillDir "blog") "templates")) templates)"
    Write-Color Green "  Sub-skills:   $SubSkillCount installed"
    Write-Color Green "  Agents:       $AgentCount specialists"
    Write-Color Green "  Scripts:      $RootScriptCount root-level + per-skill scripts"
    Write-Color White ""
    Write-Color White "Commands available:"
    Print-Commands (Join-Path (Join-Path (Join-Path $ScriptDir "skills") "blog") "SKILL.md")
    Write-Color White ""
    Write-Color White "Optional: AI Features (same API key for both)"
    Write-Color Cyan  "  /blog image setup             Configure Gemini image generation"
    Write-Color Cyan  "  /blog audio setup             Configure Gemini TTS audio narration"
    Write-Color White "  Requires: Google AI API key (free at https://aistudio.google.com/apikey)"
    Write-Color White ""
    Write-Color Yellow "Restart Claude Code to activate the new skill."
}

Main
