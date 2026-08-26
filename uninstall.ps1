#!/usr/bin/env pwsh
# claude-blog uninstaller for Windows
# Cleanly removes all blog skills, agents, templates, and scripts

$ErrorActionPreference = "Stop"

function Write-Color($Color, $Text) {
    Write-Host $Text -ForegroundColor $Color
}

function Main {
    $SkillDir = Join-Path (Join-Path $env:USERPROFILE ".claude") "skills"
    $AgentDir = Join-Path (Join-Path $env:USERPROFILE ".claude") "agents"

    Write-Color Cyan "=== Uninstalling claude-blog ==="
    Write-Host ""

    # Remove main skill (includes references, templates, scripts)
    $blogDir = Join-Path $SkillDir "blog"
    if (Test-Path $blogDir) {
        Remove-Item -Recurse -Force $blogDir
        Write-Color Green "  Removed: $blogDir"
    }

    # Remove sub-skills via glob (closes audit VULN-035: prior static array
    # was stale and missed v1.7.0 sub-skills like blog-cluster, blog-flow,
    # blog-multilingual, blog-translate, blog-localize, blog-locale-audit,
    # blog-notebooklm, blog-audio, blog-google. The glob pattern is the
    # same approach uninstall.sh already uses.)
    if (Test-Path $SkillDir) {
        Get-ChildItem -Path $SkillDir -Directory -Filter "blog-*" | ForEach-Object {
            Remove-Item -Recurse -Force $_.FullName
            Write-Color Green "  Removed: $($_.FullName)"
        }
    }

    # Remove agents via glob (closes VULN-035: blog-translator was missing
    # from the static list).
    if (Test-Path $AgentDir) {
        Get-ChildItem -Path $AgentDir -Filter "blog-*.md" | ForEach-Object {
            Remove-Item -Force $_.FullName
            Write-Color Green "  Removed: $($_.FullName)"
        }
    }

    # Remove root-level scripts copied to ~/.claude/scripts/ by install.ps1
    # (v1.8.6: install.ps1 now copies all scripts/*.py to that location).
    $ClaudeScriptsDir = Join-Path $env:USERPROFILE ".claude\scripts"
    $helperScripts = @("analyze_blog.py", "blog_preflight.py", "blog_render.py", "blog_hygiene.py",
                        "cognitive_load.py", "discourse_research.py", "generate_hero.py",
                        "load_untrusted_root.py", "lint_prose.py", "sync_flow.py",
                        "ai_citation_score.py", "content_decay.py", "quality_gate.py", "style_learn.py",
                        "check_google_currentness.py", "check_secrets.py", "consistency_check.py", "dependency_smoke.py",
                        "sync_google_updates.py", "validate_public_release.py")
    foreach ($s in $helperScripts) {
        $scriptPath = Join-Path $ClaudeScriptsDir $s
        if (Test-Path $scriptPath) {
            Remove-Item -Force $scriptPath -ErrorAction SilentlyContinue
            Write-Color Green "  Removed: $scriptPath"
        }
    }
    if ((Test-Path $ClaudeScriptsDir) -and -not (Get-ChildItem $ClaudeScriptsDir -ErrorAction SilentlyContinue)) {
        Remove-Item $ClaudeScriptsDir -Force -ErrorAction SilentlyContinue
    }

    # Shared Google credentials may be used by other installed skills.
    # claude-blog does not own them, so uninstall must leave them intact.
    Write-Color Yellow "  Shared Google credentials under ~/.config/claude-seo were left intact."

    Write-Host ""
    Write-Color Cyan "=== claude-blog uninstalled ==="
    Write-Host ""
    Write-Color Yellow "Restart Claude Code to complete removal."
}

Main
