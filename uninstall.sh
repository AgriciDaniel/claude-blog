#!/usr/bin/env bash
set -euo pipefail

# claude-blog uninstaller
# Cleanly removes all blog skills, agents, templates, and scripts

main() {
    local SKILL_DIR="${HOME}/.claude/skills"
    local AGENT_DIR="${HOME}/.claude/agents"

    echo "=== Uninstalling claude-blog ==="
    echo ""

    # Remove main skill (includes references, templates, scripts)
    if [ -d "${SKILL_DIR}/blog" ]; then
        rm -rf "${SKILL_DIR}/blog"
        echo "  Removed: ${SKILL_DIR}/blog/"
    fi

    # Remove sub-skills
    for skill in blog-write blog-rewrite blog-analyze blog-brief blog-calendar blog-strategy blog-outline blog-seo-check blog-schema blog-repurpose blog-geo blog-audit; do
        if [ -d "${SKILL_DIR}/${skill}" ]; then
            rm -rf "${SKILL_DIR}/${skill}"
            echo "  Removed: ${SKILL_DIR}/${skill}/"
        fi
    done

    # Remove agents
    for agent in blog-researcher blog-writer blog-seo blog-reviewer; do
        if [ -f "${AGENT_DIR}/${agent}.md" ]; then
            rm -f "${AGENT_DIR}/${agent}.md"
            echo "  Removed: ${AGENT_DIR}/${agent}.md"
        fi
    done

    echo ""
    echo "=== claude-blog uninstalled ==="
    echo ""
    echo "Restart Claude Code to complete removal."
}

main "$@"
