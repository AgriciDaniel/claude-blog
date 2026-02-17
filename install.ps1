#!/usr/bin/env pwsh
# claude-blog installer for Windows
# Installs the blog skill ecosystem to ~/.claude/skills/ and ~/.claude/agents/

$ErrorActionPreference = "Stop"

function Write-Color($Color, $Text) {
    Write-Host $Text -ForegroundColor $Color
}

function Main {
    Write-Color Cyan @"

   ╔══════════════════════════════════════╗
   ║         claude-blog Installer        ║
   ║  Blog Content Engine for Claude Code ║
   ╚══════════════════════════════════════╝

"@

    $SkillDir = Join-Path $env:USERPROFILE ".claude" "skills"
    $AgentDir = Join-Path $env:USERPROFILE ".claude" "agents"
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

    # Check prerequisites
    try {
        $null = Get-Command python3 -ErrorAction Stop
    } catch {
        try {
            $null = Get-Command python -ErrorAction Stop
        } catch {
            Write-Color Yellow "WARNING: Python not found. The analyze_blog.py script requires Python 3.12+."
        }
    }

    # Create directories
    Write-Color White "Creating directories..."
    $dirs = @(
        (Join-Path $SkillDir "blog" "references"),
        (Join-Path $SkillDir "blog" "templates"),
        (Join-Path $SkillDir "blog" "scripts"),
        "blog-write", "blog-rewrite", "blog-analyze", "blog-brief",
        "blog-calendar", "blog-strategy", "blog-outline", "blog-seo-check",
        "blog-schema", "blog-repurpose", "blog-geo", "blog-audit"
    )

    New-Item -ItemType Directory -Force -Path (Join-Path $SkillDir "blog" "references") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $SkillDir "blog" "templates") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $SkillDir "blog" "scripts") | Out-Null
    New-Item -ItemType Directory -Force -Path $AgentDir | Out-Null

    foreach ($skill in @("blog-write", "blog-rewrite", "blog-analyze", "blog-brief", "blog-calendar", "blog-strategy", "blog-outline", "blog-seo-check", "blog-schema", "blog-repurpose", "blog-geo", "blog-audit")) {
        New-Item -ItemType Directory -Force -Path (Join-Path $SkillDir $skill) | Out-Null
    }

    # Copy main skill
    Write-Color White "Installing main skill: blog..."
    Copy-Item (Join-Path $ScriptDir "blog" "SKILL.md") (Join-Path $SkillDir "blog" "SKILL.md") -Force

    # Copy references
    Write-Color White "Installing reference files..."
    Copy-Item (Join-Path $ScriptDir "blog" "references" "*.md") (Join-Path $SkillDir "blog" "references") -Force

    # Copy templates
    if (Test-Path (Join-Path $ScriptDir "blog" "templates")) {
        Write-Color White "Installing content templates..."
        Copy-Item (Join-Path $ScriptDir "blog" "templates" "*.md") (Join-Path $SkillDir "blog" "templates") -Force
    }

    # Copy sub-skills
    Write-Color White "Installing sub-skills..."
    Get-ChildItem -Directory (Join-Path $ScriptDir "skills") | ForEach-Object {
        $skillName = $_.Name
        $src = Join-Path $_.FullName "SKILL.md"
        $dst = Join-Path $SkillDir $skillName "SKILL.md"
        if (Test-Path $src) {
            Copy-Item $src $dst -Force
            Write-Color Green "  + $skillName"
        }
    }

    # Copy agents
    Write-Color White "Installing agents..."
    Get-ChildItem -File (Join-Path $ScriptDir "agents" "*.md") | ForEach-Object {
        Copy-Item $_.FullName (Join-Path $AgentDir $_.Name) -Force
        Write-Color Green "  + $($_.BaseName)"
    }

    # Copy scripts
    Write-Color White "Installing scripts..."
    Copy-Item (Join-Path $ScriptDir "scripts" "analyze_blog.py") (Join-Path $SkillDir "blog" "scripts" "analyze_blog.py") -Force

    # Install Python dependencies
    Write-Color White "Installing Python dependencies..."
    $reqFile = Join-Path $ScriptDir "requirements.txt"
    if (Test-Path $reqFile) {
        try {
            & python3 -m pip install --quiet -r $reqFile 2>$null
            Write-Color Green "  Python dependencies installed."
        } catch {
            try {
                & python -m pip install --quiet -r $reqFile 2>$null
                Write-Color Green "  Python dependencies installed."
            } catch {
                Write-Color Yellow "  Skipped: Install manually with 'pip install -r requirements.txt'"
            }
        }
    }

    # Summary
    Write-Color Cyan @"

   ╔══════════════════════════════════════╗
   ║       Installation Complete!         ║
   ╚══════════════════════════════════════╝

"@

    Write-Color White "Installed:"
    Write-Color Green "  Main skill:   blog/ (orchestrator + 12 references + 12 templates)"
    Write-Color Green "  Sub-skills:   12 commands"
    Write-Color Green "  Agents:       4 specialists"
    Write-Color Green "  Scripts:      analyze_blog.py"
    Write-Color White ""
    Write-Color White "Commands available:"
    Write-Color Cyan  "  /blog write <topic>        Write a new blog post"
    Write-Color Cyan  "  /blog rewrite <file>       Optimize an existing blog post"
    Write-Color Cyan  "  /blog analyze <file>       Audit blog quality (0-100 score)"
    Write-Color Cyan  "  /blog brief <topic>        Generate a content brief"
    Write-Color Cyan  "  /blog calendar             Generate an editorial calendar"
    Write-Color Cyan  "  /blog strategy <niche>     Blog strategy and topic ideation"
    Write-Color Cyan  "  /blog outline <topic>      Generate a SERP-informed outline"
    Write-Color Cyan  "  /blog seo-check <file>     Post-writing SEO validation"
    Write-Color Cyan  "  /blog schema <file>        Generate JSON-LD schema markup"
    Write-Color Cyan  "  /blog repurpose <file>     Repurpose content for other platforms"
    Write-Color Cyan  "  /blog geo <file>           AI citation optimization audit"
    Write-Color Cyan  "  /blog audit [directory]    Full-site blog health assessment"
    Write-Color White ""
    Write-Color Yellow "Restart Claude Code to activate the new skill."
}

Main
