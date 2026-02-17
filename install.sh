#!/usr/bin/env bash
set -euo pipefail

# claude-blog installer
# Installs the blog skill ecosystem to ~/.claude/skills/ and ~/.claude/agents/
#
# One-command install:
#   curl -sL https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.sh | bash

main() {
    local SKILL_DIR="${HOME}/.claude/skills"
    local AGENT_DIR="${HOME}/.claude/agents"
    local SCRIPT_DIR
    local TEMP_DIR=""

    echo ""
    echo "  ╔══════════════════════════════════════╗"
    echo "  ║         claude-blog Installer        ║"
    echo "  ║  Blog Content Engine for Claude Code ║"
    echo "  ╚══════════════════════════════════════╝"
    echo ""

    # Determine source directory (local clone or piped from curl)
    if [ -f "${BASH_SOURCE[0]:-}" ] && [ -d "$(dirname "${BASH_SOURCE[0]}")/blog" ]; then
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    else
        echo "→ Cloning claude-blog..."
        TEMP_DIR="$(mktemp -d)"
        trap 'rm -rf "${TEMP_DIR}"' EXIT
        git clone --depth 1 https://github.com/AgriciDaniel/claude-blog.git "${TEMP_DIR}/claude-blog" 2>/dev/null
        SCRIPT_DIR="${TEMP_DIR}/claude-blog"
    fi

    # Check prerequisites
    if ! command -v python3 &>/dev/null; then
        echo "WARNING: python3 not found. The analyze_blog.py script requires Python 3.12+."
        echo "         Install with: sudo apt install python3"
        echo ""
    fi

    # Create directories
    echo "→ Creating directories..."
    mkdir -p "${SKILL_DIR}/blog/references"
    mkdir -p "${SKILL_DIR}/blog/templates"
    mkdir -p "${SKILL_DIR}/blog/scripts"
    for skill in blog-write blog-rewrite blog-analyze blog-brief blog-calendar blog-strategy blog-outline blog-seo-check blog-schema blog-repurpose blog-geo blog-audit; do
        mkdir -p "${SKILL_DIR}/${skill}"
    done
    mkdir -p "${AGENT_DIR}"

    # Copy main skill
    echo "→ Installing main skill: blog..."
    cp "${SCRIPT_DIR}/blog/SKILL.md" "${SKILL_DIR}/blog/SKILL.md"

    # Copy references
    echo "→ Installing reference files..."
    if ls "${SCRIPT_DIR}/blog/references/"*.md &>/dev/null; then
        cp "${SCRIPT_DIR}/blog/references/"*.md "${SKILL_DIR}/blog/references/"
    fi

    # Copy templates
    if ls "${SCRIPT_DIR}/blog/templates/"*.md &>/dev/null; then
        echo "→ Installing content templates..."
        cp "${SCRIPT_DIR}/blog/templates/"*.md "${SKILL_DIR}/blog/templates/"
    fi

    # Copy sub-skills
    echo "→ Installing sub-skills..."
    for skill_dir in "${SCRIPT_DIR}/skills/"*/; do
        skill_name="$(basename "${skill_dir}")"
        if [ -f "${skill_dir}SKILL.md" ]; then
            cp "${skill_dir}SKILL.md" "${SKILL_DIR}/${skill_name}/SKILL.md"
            echo "  + ${skill_name}"
        fi
    done

    # Copy agents
    echo "→ Installing agents..."
    for agent_file in "${SCRIPT_DIR}/agents/"*.md; do
        if [ -f "${agent_file}" ]; then
            agent_name="$(basename "${agent_file}")"
            cp "${agent_file}" "${AGENT_DIR}/${agent_name}"
            echo "  + ${agent_name%.md}"
        fi
    done

    # Copy scripts
    echo "→ Installing scripts..."
    cp "${SCRIPT_DIR}/scripts/analyze_blog.py" "${SKILL_DIR}/blog/scripts/analyze_blog.py"
    chmod +x "${SKILL_DIR}/blog/scripts/analyze_blog.py"

    # Install Python dependencies
    if [ -f "${SCRIPT_DIR}/requirements.txt" ] && command -v pip3 &>/dev/null; then
        echo "→ Installing Python dependencies..."
        pip3 install --quiet --break-system-packages -r "${SCRIPT_DIR}/requirements.txt" 2>/dev/null || \
        pip3 install --quiet -r "${SCRIPT_DIR}/requirements.txt" 2>/dev/null || \
        echo "  Skipped: Install manually with 'pip3 install -r requirements.txt'"
    fi

    echo ""
    echo "  ╔══════════════════════════════════════╗"
    echo "  ║       Installation Complete!         ║"
    echo "  ╚══════════════════════════════════════╝"
    echo ""
    echo "  Installed:"
    echo "    Main skill:   blog/ (orchestrator + references + templates)"
    echo "    Sub-skills:   12 commands"
    echo "    Agents:       4 specialists"
    echo "    Scripts:      analyze_blog.py"
    echo ""
    echo "  Commands available:"
    echo "    /blog write <topic>        Write a new blog post"
    echo "    /blog rewrite <file>       Optimize an existing blog post"
    echo "    /blog analyze <file>       Audit blog quality (0-100 score)"
    echo "    /blog brief <topic>        Generate a content brief"
    echo "    /blog calendar             Generate an editorial calendar"
    echo "    /blog strategy <niche>     Blog strategy and topic ideation"
    echo "    /blog outline <topic>      SERP-informed outline generation"
    echo "    /blog seo-check <file>     Post-writing SEO validation"
    echo "    /blog schema <file>        Generate JSON-LD schema markup"
    echo "    /blog repurpose <file>     Repurpose for other platforms"
    echo "    /blog geo <file>           AI citation optimization audit"
    echo "    /blog audit [directory]    Full-site blog health assessment"
    echo ""
    echo "  Restart Claude Code to activate the new skill."
}

main "$@"
