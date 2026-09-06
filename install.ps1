#!/usr/bin/env pwsh
# claude-blog installer for Windows
# Installs the blog skill ecosystem to ~/.claude/skills/ and ~/.claude/agents/
#
# Install (download first, then run so you can inspect it):
#   irm https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.ps1 -OutFile install.ps1
#   pwsh -File ./install.ps1

$ErrorActionPreference = "Stop"
$ClaudeBlogVersion = "2.3.0"

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

    # Install as a plugin directory. Claude auto-discovers any folder holding
    # .claude-plugin/plugin.json under a skills directory and loads it as a
    # plugin, which is what makes ${CLAUDE_PLUGIN_ROOT} resolve inside the skill
    # files. Since v2.3.0 every intra-plugin reference uses that variable, so
    # this is the only layout that works.
    $PluginDir = Join-Path $SkillDir "claude-blog"

    if (Test-Path (Join-Path (Join-Path $SkillDir "blog") "SKILL.md")) {
        Write-Color Yellow "Found a pre-2.3.0 flat install at $SkillDir\blog\"
        Write-Color Yellow "  It will shadow this plugin install. Clear it with ./uninstall.ps1,"
        Write-Color Yellow "  which removes both layouts, then re-run this installer."
        Write-Color White ""
    }

    Write-Color White "Installing plugin to $PluginDir..."
    if (Test-Path $PluginDir) { Remove-Item -Recurse -Force $PluginDir }
    New-Item -ItemType Directory -Force -Path $PluginDir | Out-Null

    # Payload only: everything Claude loads at runtime and nothing else.
    # brain/ and branding/ are bundled project material no skill reads.
    foreach ($item in @(".claude-plugin", "mcp-servers.json", "skills", "agents", "scripts", "data", "LICENSE", "NOTICE", "README.md")) {
        $src = Join-Path $ScriptDir $item
        if (Test-Path -LiteralPath $src -PathType Container) {
            Copy-Tree $src (Join-Path $PluginDir $item)
        } elseif (Test-Path -LiteralPath $src) {
            Copy-Item -LiteralPath $src -Destination (Join-Path $PluginDir $item) -Force
        }
    }

    # Root helper scripts ship inside the plugin. Skills invoke them as
    # ${CLAUDE_PLUGIN_ROOT}/scripts/*.py, so unlike pre-2.3.0 there is no second
    # copy under ~/.claude/scripts to keep in sync.
    $RootScripts = @(Get-ChildItem -File (Join-Path (Join-Path $PluginDir "scripts") "*.py"))
    $RootScriptCount = $RootScripts.Count
    foreach ($RootScript in $RootScripts) {
        Write-Color Green "  + scripts/$($RootScript.Name)"
    }

    # The reviewed Google update ledger (data/google-updates.json) ships inside
    # the plugin and is read at ${CLAUDE_PLUGIN_ROOT}/data/google-updates.json.
    $LedgerPath = Join-Path (Join-Path $PluginDir "data") "google-updates.json"
    if (-not (Test-Path -LiteralPath $LedgerPath)) {
        throw "data/google-updates.json missing from the install."
    }

    $SkillCount = @(Get-ChildItem -Path (Join-Path $PluginDir "skills") -Filter "SKILL.md" -Recurse).Count
    $AgentCount = @(Get-ChildItem -Path (Join-Path $PluginDir "agents") -Filter "*.md").Count
    if ($SkillCount -lt 30) {
        throw "Installed only $SkillCount skills; the install looks incomplete."
    }

    # One directory, one manifest line. Uninstall removes the tree.
    $Manifest = Join-Path (Join-Path $env:USERPROFILE ".claude") "claude-blog-manifest.txt"
    Set-Content -LiteralPath $Manifest -Value $PluginDir


    # Install Python dependencies (closes audit VULN-507/804: capture stderr
    # to a logfile instead of swallowing it).
    $reqFile = Join-Path $ScriptDir "requirements.txt"
    if (($env:CLAUDE_BLOG_INSTALL_DEPS -eq "1") -and (Test-Path $reqFile)) {
        Write-Color White "Installing Python dependencies (CLAUDE_BLOG_INSTALL_DEPS=1)..."
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

    Write-Color White "Installed at: $PluginDir"
    Write-Color Green "  Skills:       $SkillCount ($(Count-Files (Join-Path (Join-Path (Join-Path $PluginDir "skills") "blog") "references")) references, $(Count-Files (Join-Path (Join-Path (Join-Path $PluginDir "skills") "blog") "templates")) templates)"
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
    Write-Color Yellow "Restart Claude Code to activate the plugin."
}

Main
