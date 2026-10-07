#!/usr/bin/env bash
set -euo pipefail

# claude-blog uninstaller
# Removes verified package-owned files and preserves unknown or edited content.

main() {
    local SKILL_DIR="${HOME}/.claude/skills"
    local AGENT_DIR="${HOME}/.claude/agents"
    local MANIFEST="${HOME}/.claude/claude-blog-manifest.txt"
    local SCRIPT_DIR
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
        "installer_ownership.py" "sync_google_updates.py" "validate_public_release.py"
    )
    local agent_files=(
        "blog-researcher.md" "blog-reviewer.md" "blog-seo.md"
        "blog-translator.md" "blog-writer.md"
    )

    # Retain the explicit package inventories for cross-platform sync checks and
    # legacy review. The ownership engine below never applies a wildcard delete.
    : "${SKILL_DIR}" "${AGENT_DIR}" "${package_skills[*]}" "${helper_scripts[*]}" "${agent_files[*]}"

    if [ -f "${BASH_SOURCE[0]:-}" ] && [ -d "$(dirname "${BASH_SOURCE[0]}")/skills/blog" ]; then
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    else
        SCRIPT_DIR=""
    fi

    echo "=== Uninstalling claude-blog ==="
    echo ""

    if ! command -v python3 &>/dev/null; then
        echo "ERROR: python3 3.11+ is required for ownership-safe uninstall." >&2
        return 1
    fi

    if [ -e "${MANIFEST}" ] || [ -L "${MANIFEST}" ]; then
        local OWNERSHIP_ENGINE
        # Bash 3.2 treats an empty array as unset under nounset. Keep the
        # required command arguments in this array for standalone removal too.
        local OWNERSHIP_ARGS=(
            uninstall --profile "${HOME}/.claude" --manifest "${MANIFEST}"
        )
        if [ -n "${SCRIPT_DIR}" ] && [ -f "${SCRIPT_DIR}/scripts/installer_ownership.py" ]; then
            OWNERSHIP_ENGINE="${SCRIPT_DIR}/scripts/installer_ownership.py"
            OWNERSHIP_ARGS+=(--legacy-inventory "${SCRIPT_DIR}/data/legacy-install-ownership.json")
        elif [ -f "${HOME}/.claude/scripts/installer_ownership.py" ]; then
            OWNERSHIP_ENGINE="${HOME}/.claude/scripts/installer_ownership.py"
        else
            echo "ERROR: ownership engine is unavailable; use uninstall.sh from the complete reviewed repository." >&2
            return 1
        fi

        python3 "${OWNERSHIP_ENGINE}" "${OWNERSHIP_ARGS[@]}"
    fi


    echo "  Shared Google credentials under ~/.config/claude-seo were left intact."
    echo ""
    echo "=== claude-blog uninstalled ==="
    echo ""
    echo "Restart Claude Code to complete removal."
}

main "$@"
