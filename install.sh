#!/usr/bin/env bash
set -euo pipefail

# claude-blog installer
# Installs the blog skill ecosystem to ~/.claude/skills/ and ~/.claude/agents/
#
# One-command install:
#   curl -sL https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.sh | bash

# Declared outside main() so the EXIT trap can access it after main() returns
TEMP_DIR=""
readonly CLAUDE_BLOG_VERSION="2.2.0"

copy_tree() {
    local src="$1"
    local dest="$2"
    [ -d "${src}" ] || return 0
    mkdir -p "${dest}"
    while IFS= read -r -d '' rel_path; do
        mkdir -p "${dest}/$(dirname "${rel_path}")"
        cp "${src}/${rel_path}" "${dest}/${rel_path}"
    done < <(
        cd "${src}" &&
            find . -type d -name '__pycache__' -prune -o -type f ! -name '*.pyc' -print0
    )
}

count_files() {
    local path="$1"
    [ -d "${path}" ] || {
        echo 0
        return
    }
    find "${path}" -type d -name '__pycache__' -prune -o -type f ! -name '*.pyc' -print | wc -l | tr -d ' '
}

record_install() {
    local manifest="$1"
    local path="$2"
    printf '%s\n' "${path}" >>"${manifest}"
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

main() {
    local SKILL_DIR="${HOME}/.claude/skills"
    local AGENT_DIR="${HOME}/.claude/agents"
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

    # Determine source directory (local clone or piped from curl)
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
    fi

    # Check prerequisites
    if ! command -v python3 &>/dev/null; then
        echo "WARNING: python3 not found. The scripts require Python 3.11+."
        echo "         Install with: sudo apt install python3"
        echo ""
    elif ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
        local python3_version
        python3_version="$(python3 -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null || echo unknown)"
        echo "WARNING: python3 ${python3_version} found. The scripts require Python 3.11+."
        echo "         Install Python 3.11+ before running scoring, preflight, render, hero, and lint helpers."
        echo ""
    fi

    # Create directories
    echo "→ Creating directories..."
    mkdir -p "${CLAUDE_DIR}"
    mkdir -p "${SKILL_DIR}/blog/references"
    mkdir -p "${SKILL_DIR}/blog/templates"
    mkdir -p "${SKILL_DIR}/blog/scripts"
    mkdir -p "${AGENT_DIR}"
    : >"${MANIFEST}.tmp"

    # Copy main skill
    echo "→ Installing main skill: blog..."
    cp "${SCRIPT_DIR}/skills/blog/SKILL.md" "${SKILL_DIR}/blog/SKILL.md"
    record_install "${MANIFEST}.tmp" "${SKILL_DIR}/blog"

    # Copy references
    echo "→ Installing reference files..."
    copy_tree "${SCRIPT_DIR}/skills/blog/references" "${SKILL_DIR}/blog/references"

    # Copy templates
    if [ -d "${SCRIPT_DIR}/skills/blog/templates" ]; then
        echo "→ Installing content templates..."
        copy_tree "${SCRIPT_DIR}/skills/blog/templates" "${SKILL_DIR}/blog/templates"
    fi

    # Ship the reviewed Google update ledger with the main skill. The source
    # stays at data/google-updates.json in the repository; standalone installs
    # receive it under the self-contained blog skill directory.
    if [ -f "${SCRIPT_DIR}/data/google-updates.json" ]; then
        echo "→ Installing Google update ledger..."
        mkdir -p "${SKILL_DIR}/blog/data"
        cp "${SCRIPT_DIR}/data/google-updates.json" "${SKILL_DIR}/blog/data/google-updates.json"
    fi

    # Copy sub-skills (auto-discovers all skill directories)
    echo "→ Installing sub-skills..."
    local sub_skill_count=0
    local expected_sub_skill_count=0
    for skill_dir in "${SCRIPT_DIR}/skills/"*/; do
        skill_name="$(basename "${skill_dir}")"
        [ "$skill_name" = "blog" ] && continue
        [ -f "${skill_dir}SKILL.md" ] && expected_sub_skill_count=$((expected_sub_skill_count + 1))
        # VULN-IAC-003 (v1.9.1): defense-in-depth name validation. The
        # repo is single-owner and a clean clone cannot produce odd names,
        # but a tampered repo with a symlink like `skills/../../etc` would
        # hand us '..' here. Refuse anything outside the expected charset
        # rather than mkdir + cp into the parent. Spell out the accepted
        # characters instead of using a locale-sensitive regex range.
        case "$skill_name" in
            ''|*[!abcdefghijklmnopqrstuvwxyz0123456789-]*)
                echo "  ! refusing skill with unexpected name: ${skill_name}" >&2
                continue
                ;;
        esac
        mkdir -p "${SKILL_DIR}/${skill_name}"
        if [ -f "${skill_dir}SKILL.md" ]; then
            cp "${skill_dir}SKILL.md" "${SKILL_DIR}/${skill_name}/SKILL.md"
            echo "  + ${skill_name}"
            record_install "${MANIFEST}.tmp" "${SKILL_DIR}/${skill_name}"
            sub_skill_count=$((sub_skill_count + 1))
        fi
        for payload_dir in references scripts assets templates; do
            copy_tree "${skill_dir}${payload_dir}" "${SKILL_DIR}/${skill_name}/${payload_dir}"
        done
        if [ -d "${SKILL_DIR}/${skill_name}/scripts" ]; then
            find "${SKILL_DIR}/${skill_name}/scripts" -type f -name '*.py' -exec chmod +x {} +
        fi
    done
    if [ "${sub_skill_count}" -ne "${expected_sub_skill_count}" ]; then
        echo "ERROR: installed ${sub_skill_count} of ${expected_sub_skill_count} sub-skills." >&2
        echo "       Installation is incomplete; review the refusal messages above." >&2
        return 1
    fi

    # Create personas directory for blog-persona
    mkdir -p "${SKILL_DIR}/blog/references/personas"

    # Copy agents
    echo "→ Installing agents..."
    local agent_count=0
    for agent_file in "${SCRIPT_DIR}/agents/"*.md; do
        if [ -f "${agent_file}" ]; then
            agent_name="$(basename "${agent_file}")"
            cp "${agent_file}" "${AGENT_DIR}/${agent_name}"
            record_install "${MANIFEST}.tmp" "${AGENT_DIR}/${agent_name}"
            echo "  + ${agent_name%.md}"
            agent_count=$((agent_count + 1))
        fi
    done

    # Copy scripts (v1.8.6: ALL root-level scripts, not just analyze_blog.py).
    # Before v1.8.6 the installer only copied analyze_blog.py, leaving the
    # v1.8.0+ helpers (cognitive_load, discourse_research, load_untrusted_root,
    # lint_prose, sync_flow) absent on the user's machine. This broke the
    # v1.8.3 "code-enforced" untrusted-data contract for every marketplace
    # / curl-pipe install (closes 7TH-AUDIT-001).
    echo "→ Installing scripts..."
    mkdir -p "${SKILL_DIR}/blog/scripts"
    mkdir -p "${HOME}/.claude/scripts"
    local script_name
    local root_script_count=0
    for script_path in "${SCRIPT_DIR}/scripts/"*.py; do
        [ -f "${script_path}" ] || continue
        script_name="$(basename "${script_path}")"
        # Copy to ~/.claude/scripts/ (canonical install location) AND to the
        # blog-skill scripts dir (legacy callers of analyze_blog.py).
        cp "${script_path}" "${HOME}/.claude/scripts/${script_name}"
        chmod +x "${HOME}/.claude/scripts/${script_name}"
        record_install "${MANIFEST}.tmp" "${HOME}/.claude/scripts/${script_name}"
        if [ "${script_name}" = "analyze_blog.py" ]; then
            cp "${script_path}" "${SKILL_DIR}/blog/scripts/${script_name}"
            chmod +x "${SKILL_DIR}/blog/scripts/${script_name}"
        fi
        echo "  + scripts/${script_name}"
        root_script_count=$((root_script_count + 1))
    done
    mv "${MANIFEST}.tmp" "${MANIFEST}"

    # Install Python dependencies (closes audit VULN-507/804: capture stderr
    # to a logfile instead of swallowing it. Operator can diagnose failures.)
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
