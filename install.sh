#!/usr/bin/env bash
set -euo pipefail

# claude-blog installer
#
# Installs claude-blog as a *plugin directory* at ~/.claude/skills/claude-blog/.
# Claude auto-discovers any folder containing .claude-plugin/plugin.json under a
# skills directory and loads it as a plugin, which is what makes
# ${CLAUDE_PLUGIN_ROOT} resolve inside the skill files. Since v2.3.0 every
# intra-plugin reference uses that variable, so the plugin layout is the only
# layout that works: the installed tree is byte-identical to the repository and
# to what Claude Cowork installs.
#
# Reviewed install (recommended -- you can read everything before it runs):
#   git clone https://github.com/AgriciDaniel/claude-blog.git
#   cd claude-blog && ./install.sh
#
# One-command install:
#   curl -sL https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.sh | bash
#
# This script copies files and, only if you opt in with CLAUDE_BLOG_INSTALL_DEPS=1,
# installs Python packages. It never writes credentials and never edits your shell
# config. Set CLAUDE_BLOG_REF to a tag or SHA for a pinned install.

# Declared outside main() so the EXIT trap can access it after main() returns
TEMP_DIR=""
readonly CLAUDE_BLOG_VERSION="2.3.0"

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
    local CLAUDE_DIR="${HOME}/.claude"
    local SKILL_DIR="${CLAUDE_DIR}/skills"
    local AGENT_DIR="${CLAUDE_DIR}/agents"
    local PLUGIN_DIR="${SKILL_DIR}/claude-blog"
    local MANIFEST="${CLAUDE_DIR}/claude-blog-manifest.txt"
    local SCRIPT_DIR

    echo ""
    echo "  ╔══════════════════════════════════════╗"
    echo "  ║         claude-blog Installer        ║"
    echo "  ║   Blog Content Engine for Claude     ║"
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

    if [ ! -f "${SCRIPT_DIR}/.claude-plugin/plugin.json" ]; then
        echo "ERROR: ${SCRIPT_DIR} is not a claude-blog checkout (no .claude-plugin/plugin.json)." >&2
        return 1
    fi

    # Check prerequisites. The content skills need none of this; only the
    # script-backed ones (/blog analyze, /blog google, preflight gates) do.
    if ! command -v python3 &>/dev/null; then
        echo "NOTE: python3 not found. Writing, briefs, outlines, schema and"
        echo "      translation still work. Scoring and Google data need Python 3.11+."
        echo ""
    elif ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
        local python3_version
        python3_version="$(python3 -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null || echo unknown)"
        echo "WARNING: python3 ${python3_version} found. The scripts require Python 3.11+."
        echo ""
    fi

    # A pre-2.3.0 flat install shadows the plugin, and its skill files still use
    # the old non-portable relative paths.
    if [ -f "${SKILL_DIR}/blog/SKILL.md" ]; then
        echo "→ Found a pre-2.3.0 flat install at ${SKILL_DIR}/blog/"
        echo "  It will shadow this plugin install. Clear it with ./uninstall.sh,"
        echo "  which removes both layouts, then re-run this installer."
        echo ""
    fi

    echo "→ Installing plugin to ${PLUGIN_DIR}..."
    rm -rf "${PLUGIN_DIR}"
    mkdir -p "${PLUGIN_DIR}" "${CLAUDE_DIR}"

    # Copy the plugin payload: everything Claude loads at runtime and nothing
    # else. brain/ and branding/ are bundled project material that no skill
    # reads (brain/ alone is ~5.8 MB); tests/ and .github/ are development only.
    local item
    for item in .claude-plugin mcp-servers.json skills agents scripts data LICENSE NOTICE README.md; do
        if [ -d "${SCRIPT_DIR}/${item}" ]; then
            copy_tree "${SCRIPT_DIR}/${item}" "${PLUGIN_DIR}/${item}"
        elif [ -f "${SCRIPT_DIR}/${item}" ]; then
            cp "${SCRIPT_DIR}/${item}" "${PLUGIN_DIR}/${item}"
        fi
    done

    # Root helper scripts ship inside the plugin. Skills invoke them as
    # "${CLAUDE_PLUGIN_ROOT}"/scripts/*.py, so unlike pre-2.3.0 there is no
    # second copy under ~/.claude/scripts to keep in sync.
    local script_name
    local root_script_count=0
    for script_path in "${PLUGIN_DIR}/scripts/"*.py; do
        [ -f "${script_path}" ] || continue
        script_name="$(basename "${script_path}")"
        chmod +x "${script_path}"
        echo "  + scripts/${script_name}"
        root_script_count=$((root_script_count + 1))
    done
    find "${PLUGIN_DIR}/skills" -type f -name '*.py' -exec chmod +x {} + 2>/dev/null || true

    # The reviewed Google update ledger (data/google-updates.json) ships inside
    # the plugin and is read at ${CLAUDE_PLUGIN_ROOT}/data/google-updates.json.
    if [ ! -f "${PLUGIN_DIR}/data/google-updates.json" ]; then
        echo "ERROR: data/google-updates.json missing from the install." >&2
        return 1
    fi

    local skill_count sub_skill_count agent_count
    skill_count="$(find "${PLUGIN_DIR}/skills" -name SKILL.md | wc -l | tr -d ' ')"
    sub_skill_count="$(find "${PLUGIN_DIR}/skills" -mindepth 2 -maxdepth 2 -name SKILL.md \
        ! -path "${PLUGIN_DIR}/skills/blog/SKILL.md" | wc -l | tr -d ' ')"
    agent_count="$(find "${PLUGIN_DIR}/agents" -name '*.md' | wc -l | tr -d ' ')"

    if [ "${skill_count}" -lt 30 ]; then
        echo "ERROR: installed only ${skill_count} skills; the install looks incomplete." >&2
        return 1
    fi

    # One directory, one manifest line. Uninstall removes the tree.
    printf '%s\n' "${PLUGIN_DIR}" >"${MANIFEST}"

    # Python dependencies are OPT-IN. An installer that silently installs
    # packages into a user's environment fails security review, and no content
    # skill needs them.
    if [ "${CLAUDE_BLOG_INSTALL_DEPS:-}" = "1" ]; then
        if [ -f "${SCRIPT_DIR}/requirements.txt" ] && command -v pip3 &>/dev/null; then
            echo "→ Installing Python dependencies (CLAUDE_BLOG_INSTALL_DEPS=1)..."
            local pip_log
            pip_log="$(mktemp -t claude-blog-pip-XXXXXX.log)"
            if pip3 install --quiet -r "${SCRIPT_DIR}/requirements.txt" 2>"${pip_log}"; then
                rm -f "${pip_log}"
            else
                echo "  WARNING: pip install failed. See log: ${pip_log}"
                echo "  First error: $(head -n1 "${pip_log}" 2>/dev/null || echo '(empty)')"
            fi
        fi
    fi

    echo ""
    echo "  ╔══════════════════════════════════════╗"
    echo "  ║       Installation Complete!         ║"
    echo "  ╚══════════════════════════════════════╝"
    echo ""
    echo "  Installed at: ${PLUGIN_DIR}"
    echo "    Skills:       ${skill_count} ($(count_files "${PLUGIN_DIR}/skills/blog/references") references, $(count_files "${PLUGIN_DIR}/skills/blog/templates") templates)"
    echo "    Sub-skills:   ${sub_skill_count} installed"
    echo "    Agents:       ${agent_count} specialists"
    echo "    Scripts:      ${root_script_count} root-level + per-skill scripts"
    echo "    Manifest:     ${MANIFEST}"
    echo ""
    echo "  Commands available:"
    print_commands "${SCRIPT_DIR}/skills/blog/SKILL.md"
    echo ""
    echo "  Optional extras (nothing runs until you configure them):"
    echo "    Readability grades:  pip3 install -r requirements.txt"
    echo "                         (or re-run with CLAUDE_BLOG_INSTALL_DEPS=1)"
    echo "    /blog google setup   PageSpeed, Search Console, GA4"
    echo "    /blog image setup    Gemini image generation"
    echo "    /blog audio setup    Gemini TTS narration"
    echo "    Requires: Google AI API key (free at https://aistudio.google.com/apikey)"
    echo ""
    echo "  Restart Claude Code to activate the plugin."
    echo ""
    if [ -d "${AGENT_DIR}" ] && ls "${AGENT_DIR}"/blog-*.md &>/dev/null; then
        echo "  Note: legacy agents remain at ${AGENT_DIR}/blog-*.md."
        echo "        The plugin ships its own; remove the old copies to avoid duplicates."
        echo ""
    fi
}

main "$@"
