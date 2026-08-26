#!/usr/bin/env bash
set -euo pipefail

# claude-blog uninstaller
# Cleanly removes all blog skills, agents, templates, and scripts

main() {
    local SKILL_DIR="${HOME}/.claude/skills"
    local AGENT_DIR="${HOME}/.claude/agents"
    local MANIFEST="${HOME}/.claude/claude-blog-manifest.txt"
    local package_skills=(
        "blog-analyze" "blog-audio" "blog-audit" "blog-brand" "blog-brief"
        "blog-calendar" "blog-cannibalization" "blog-chart" "blog-cluster"
        "blog-decay" "blog-discourse" "blog-factcheck" "blog-flow" "blog-geo"
        "blog-google" "blog-image" "blog-locale-audit" "blog-localize"
        "blog-multilingual" "blog-notebooklm" "blog-outline" "blog-persona"
        "blog-repurpose" "blog-rewrite" "blog-schema" "blog-seo-check"
        "blog-strategy" "blog-style" "blog-taxonomy" "blog-translate"
        "blog-write"
    )
    local helper_scripts=(
        "analyze_blog.py" "blog_preflight.py" "blog_render.py" "blog_hygiene.py" "cognitive_load.py"
        "discourse_research.py" "generate_hero.py" "load_untrusted_root.py"
        "lint_prose.py" "sync_flow.py"
        "ai_citation_score.py" "content_decay.py" "quality_gate.py" "style_learn.py"
        "check_google_currentness.py" "check_secrets.py" "consistency_check.py" "dependency_smoke.py"
        "sync_google_updates.py" "validate_public_release.py"
    )
    local agent_files=(
        "blog-researcher.md" "blog-reviewer.md" "blog-seo.md"
        "blog-translator.md" "blog-writer.md"
    )

    is_known_helper() {
        local base
        base="$(basename "$1")"
        local s
        for s in "${helper_scripts[@]}"; do
            [ "${base}" = "${s}" ] && return 0
        done
        return 1
    }

    safe_remove_path() {
        local path="$1"
        [ -n "${path}" ] || return 0
        case "${path}" in
            "${SKILL_DIR}/blog"|${SKILL_DIR}/blog-*)
                rm -rf "${path}"
                echo "  Removed: ${path}"
                ;;
            ${AGENT_DIR}/blog-*.md)
                rm -f "${path}"
                echo "  Removed: ${path}"
                ;;
            ${HOME}/.claude/scripts/*.py)
                if is_known_helper "${path}"; then
                    rm -f "${path}"
                    echo "  Removed: ${path}"
                fi
                ;;
        esac
    }

    echo "=== Uninstalling claude-blog ==="
    echo ""

    if [ -f "${MANIFEST}" ]; then
        while IFS= read -r installed_path; do
            safe_remove_path "${installed_path}"
        done <"${MANIFEST}"
        rm -f "${MANIFEST}"
        echo "  Removed: ${MANIFEST}"
    else
        # Legacy installs before v1.11.0 had no manifest. Use the package
        # allowlist instead of deleting every user-owned blog-* skill.
        safe_remove_path "${SKILL_DIR}/blog"

        local skill
        for skill in "${package_skills[@]}"; do
            safe_remove_path "${SKILL_DIR}/${skill}"
        done

        local agent
        for agent in "${agent_files[@]}"; do
            safe_remove_path "${AGENT_DIR}/${agent}"
        done
    fi

    local s
    for s in "${helper_scripts[@]}"; do
        if [ -f "${HOME}/.claude/scripts/${s}" ]; then
            rm -f "${HOME}/.claude/scripts/${s}"
            echo "  Removed: ${HOME}/.claude/scripts/${s}"
        fi
    done
    # Remove the dir if empty (defensive: don't nuke if user has other tools)
    if [ -d "${HOME}/.claude/scripts" ] && [ -z "$(ls -A "${HOME}/.claude/scripts" 2>/dev/null)" ]; then
        rmdir "${HOME}/.claude/scripts" 2>/dev/null || true
    fi

    echo "  Shared Google credentials under ~/.config/claude-seo were left intact."

    echo ""
    echo "=== claude-blog uninstalled ==="
    echo ""
    echo "Restart Claude Code to complete removal."
}

main "$@"
