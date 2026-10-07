#!/usr/bin/env bash
set -euo pipefail

# claude-blog installer
# Installs the blog skill ecosystem to ~/.claude/skills/ and ~/.claude/agents/
#
# Verified local install:
#   bash install.sh
# Download and verify this file with the README checksum instructions first.
# Source: https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.sh

TEMP_DIR=""
INSTALL_STATS_FILE=""
readonly CLAUDE_BLOG_VERSION="2.2.0"

count_files() {
    local path="$1"
    [ -d "${path}" ] || {
        echo 0
        return
    }
    find "${path}" -type d -name '__pycache__' -prune -o -type f ! -name '*.pyc' -print | wc -l | tr -d ' '
}

print_commands() {
    local skill_md="$1"
    if [ ! -f "${skill_md}" ]; then
        return
    fi
    awk -F'|' '
        /^\| `\/blog / {
            cmd=$2
            desc=$3
            gsub(/`/, "", cmd)
            gsub(/\\\|/, "|", cmd)
            gsub(/^[ \t]+|[ \t]+$/, "", cmd)
            gsub(/^[ \t]+|[ \t]+$/, "", desc)
            printf "    %-38s %s\n", cmd, desc
        }
    ' "${skill_md}"
}

install_payload() {
    local source_dir="$1" claude_dir="$2" manifest="$3" stats="$4"
    # Preserve the public standalone payload contracts for audit tests:
    # ${SKILL_DIR}/blog/data/google-updates.json
    # scripts/*.py
    python3 "${source_dir}/scripts/installer_ownership.py" install \
        --source "${source_dir}" \
        --profile "${claude_dir}" \
        --manifest "${manifest}" \
        --stats "${stats}" \
        --version "${CLAUDE_BLOG_VERSION}" \
        --legacy-inventory "${source_dir}/data/legacy-install-ownership.json"
}

main() {
    local SKILL_DIR="${HOME}/.claude/skills"
    local CLAUDE_DIR="${HOME}/.claude"
    local MANIFEST="${CLAUDE_DIR}/claude-blog-manifest.txt"
    local SCRIPT_DIR

    echo ""
    echo "  ╔══════════════════════════════════════╗"
    echo "  ║         claude-blog Installer        ║"
    echo "  ║  Blog Content Engine for Claude Code ║"
    echo "  ╚══════════════════════════════════════╝"
    echo ""
    echo "  Release: ${CLAUDE_BLOG_VERSION}"
    echo ""

    if [ -f "${BASH_SOURCE[0]:-}" ] && [ -d "$(dirname "${BASH_SOURCE[0]}")/skills/blog" ]; then
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    else
        local repo="${CLAUDE_BLOG_REPO:-AgriciDaniel/claude-blog}"
        local ref="${CLAUDE_BLOG_REF:-main}"
        local url="${CLAUDE_BLOG_URL:-https://github.com/${repo}.git}"
        echo "→ Cloning claude-blog from ${repo} (${ref})..."
        TEMP_DIR="$(mktemp -d)"
        trap 'rm -rf "${TEMP_DIR}"' EXIT
        if ! git clone --depth 1 --branch "${ref}" "${url}" "${TEMP_DIR}/claude-blog" 2>/dev/null; then
            git clone "${url}" "${TEMP_DIR}/claude-blog" 2>/dev/null
            git -C "${TEMP_DIR}/claude-blog" checkout --detach "${ref}" >/dev/null 2>&1
        fi
        SCRIPT_DIR="${TEMP_DIR}/claude-blog"
        echo "  + checked out $(git -C "${SCRIPT_DIR}" rev-parse --short HEAD)"
        if [ "${ref}" = "main" ]; then
            echo "  Tip: set CLAUDE_BLOG_REF to a tag or commit SHA for a pinned install."
        fi
        local selected_installer="${SCRIPT_DIR}/install.sh"
        if [ -L "${selected_installer}" ] || [ ! -f "${selected_installer}" ]; then
            echo "ERROR: selected checkout does not contain a regular install.sh: ${selected_installer}" >&2
            return 1
        fi
        # The selected revision owns its payload layout and installation
        # behavior. This keeps advertised pinned refs compatible when an older
        # release predates the current ownership engine.
        bash "${selected_installer}" "$@"
        return
    fi

    if ! command -v python3 &>/dev/null; then
        echo "ERROR: python3 3.11+ is required for ownership-safe installation." >&2
        return 1
    fi
    if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
        local python3_version
        python3_version="$(python3 -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null || echo unknown)"
        echo "ERROR: python3 ${python3_version} found; python3 3.11+ is required for ownership-safe installation." >&2
        return 1
    fi

    if [ -L "${CLAUDE_DIR}" ]; then
        echo "ERROR: refusing symlinked Claude profile: ${CLAUDE_DIR}" >&2
        return 1
    fi
    INSTALL_STATS_FILE="$(mktemp -t claude-blog-install-stats.XXXXXX)"
    trap 'if [ -n "${INSTALL_STATS_FILE}" ]; then rm -f "${INSTALL_STATS_FILE}"; fi; if [ -n "${TEMP_DIR}" ]; then rm -rf "${TEMP_DIR}"; fi' EXIT
    install_payload "${SCRIPT_DIR}" "${CLAUDE_DIR}" "${MANIFEST}" "${INSTALL_STATS_FILE}"

    local sub_skill_count agent_count root_script_count
    read -r sub_skill_count agent_count root_script_count < <(
        python3 - "${INSTALL_STATS_FILE}" <<'PY'
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
print(data["sub_skill_count"], data["agent_count"], data["root_script_count"])
PY
    )

    if [ -f "${SCRIPT_DIR}/requirements.txt" ] && command -v pip3 &>/dev/null; then
        echo "→ Installing Python dependencies..."
        local pip_log
        pip_log="$(mktemp -t claude-blog-pip-XXXXXX.log)"
        if pip3 install --quiet -r "${SCRIPT_DIR}/requirements.txt" 2>"${pip_log}"; then
            rm -f "${pip_log}"
        else
            echo "  WARNING: pip install failed."
            echo "  See log: ${pip_log}"
            echo "  First error: $(head -n1 "${pip_log}" 2>/dev/null || echo '(empty)')"
            echo "  Manual install: pip3 install -r requirements.txt"
        fi
        echo "  Tip: Consider using a virtual environment: python3 -m venv .venv && source .venv/bin/activate"
    fi

    echo ""
    echo "  ╔══════════════════════════════════════╗"
    echo "  ║       Installation Complete!         ║"
    echo "  ╚══════════════════════════════════════╝"
    echo ""
    echo "  Installed:"
    echo "    Main skill:   blog/ (orchestrator + $(count_files "${SKILL_DIR}/blog/references") references + $(count_files "${SKILL_DIR}/blog/templates") templates)"
    echo "    Sub-skills:   ${sub_skill_count} installed"
    echo "    Agents:       ${agent_count} specialists"
    echo "    Scripts:      ${root_script_count} root-level + per-skill scripts"
    echo "    Manifest:     ${MANIFEST}"
    echo ""
    echo "  Commands available:"
    print_commands "${SCRIPT_DIR}/skills/blog/SKILL.md"
    echo ""
    echo "  Optional: AI Features (same API key for both)"
    echo "    /blog image setup             Configure Gemini image generation"
    echo "    /blog audio setup             Configure Gemini TTS audio narration"
    echo "    Requires: Google AI API key (free at https://aistudio.google.com/apikey)"
    echo ""
    echo "  Restart Claude Code to activate the new skill."
}

main "$@"
