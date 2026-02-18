#!/usr/bin/env pwsh
# claude-blog uninstaller for Windows
# Cleanly removes all blog skills, agents, templates, and scripts

$ErrorActionPreference = "Stop"

function Write-Color($Color, $Text) {
    Write-Host $Text -ForegroundColor $Color
}

function Main {
    $SkillDir = Join-Path $env:USERPROFILE ".claude" "skills"
    $AgentDir = Join-Path $env:USERPROFILE ".claude" "agents"

    Write-Color Cyan "=== Uninstalling claude-blog ==="
    Write-Host ""

    # Remove main skill (includes references, templates, scripts)
    $blogDir = Join-Path $SkillDir "blog"
    if (Test-Path $blogDir) {
        Remove-Item -Recurse -Force $blogDir
        Write-Color Green "  Removed: $blogDir"
    }

    # Remove sub-skills
    $subSkills = @(
        "blog-write", "blog-rewrite", "blog-analyze", "blog-brief",
        "blog-calendar", "blog-strategy", "blog-outline", "blog-seo-check",
        "blog-schema", "blog-repurpose", "blog-geo", "blog-audit"
    )
    foreach ($skill in $subSkills) {
        $skillPath = Join-Path $SkillDir $skill
        if (Test-Path $skillPath) {
            Remove-Item -Recurse -Force $skillPath
            Write-Color Green "  Removed: $skillPath"
        }
    }

    # Remove agents
    $agents = @("blog-researcher", "blog-writer", "blog-seo", "blog-reviewer")
    foreach ($agent in $agents) {
        $agentPath = Join-Path $AgentDir "$agent.md"
        if (Test-Path $agentPath) {
            Remove-Item -Force $agentPath
            Write-Color Green "  Removed: $agentPath"
        }
    }

    Write-Host ""
    Write-Color Cyan "=== claude-blog uninstalled ==="
    Write-Host ""
    Write-Color Yellow "Restart Claude Code to complete removal."
}

Main
