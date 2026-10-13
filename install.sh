#!/usr/bin/env bash
set -euo pipefail

# claude-blog installer
# Installs the blog skill ecosystem to ~/.claude/skills/ and ~/.claude/agents/
#
# Verified local install:
#   bash install.sh [--force-adopt]
# Download and verify this file with the README checksum instructions first.
# Set CLAUDE_BLOG_REF to a full commit SHA (preferred) or a release tag: the
# cloned revision supplies the installer that does the work, so the digest of
# this wrapper alone does not pin what runs.
#
#   --force-adopt           Replace installed files that were edited after
#                           install. Each one is first copied to
#                           ~/.claude/claude-blog-backups/<timestamp>/.
#   CLAUDE_BLOG_SKIP_PIP=1  Skip the optional Python dependency step.
# Source: https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.sh

TEMP_DIR=""
INSTALL_STATS_FILE=""
readonly CLAUDE_BLOG_VERSION="2.3.1"

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
    # Table cells escape a literal pipe as \| (for example "[generate\|edit]").
    # Protect those with a placeholder before splitting on the real columns.
    awk '
        /^\| `\/blog / {
            line = $0
            gsub(/\\[|]/, "\001", line)
            split(line, cells, "|")
            cmd = cells[2]
            desc = cells[3]
            gsub(/`/, "", cmd)
            gsub(/\001/, "|", cmd)
            gsub(/\001/, "|", desc)
            gsub(/^[ \t]+|[ \t]+$/, "", cmd)
            gsub(/^[ \t]+|[ \t]+$/, "", desc)
            printf "    %-38s %s\n", cmd, desc
        }
    ' "${skill_md}"
}

print_python_help() {
    cat <<'HELP'
  How to get Python 3.11 or newer:
    macOS: the stock /usr/bin/python3 from Apple's command line tools is too old (3.9 or older).
           Install a current Python, for example:  brew install python@3.12
           (or use the python.org installer, or: uv python install 3.12),
           then open a NEW terminal and check that `python3 --version` shows 3.11+.
    Linux: install it with your package manager, for example
           sudo apt install python3.12   or   sudo dnf install python3.12
    If a newer interpreter is already installed under another name (python3.12),
    put its directory first on PATH so that `python3` resolves to it, then re-run.
HELP
}

# The ownership engine prints "refusing symlinked path component <path>" for a
# symlinked profile directory. Older installed copies of the engine print the
# cryptic "unsafe parent at skills: Not a directory"; rewrite that into the
# same clear message so users always see which directory is the problem.
run_ownership_engine() {
    local errors status=0
    errors="$(mktemp -t claude-blog-ownership-err.XXXXXX)"
    python3 "$@" 2>"${errors}" || status=$?
    if [ -s "${errors}" ]; then
        sed -E \
            -e 's#ERROR: installation path has an unsafe parent at ([^:]+): Not a directory#ERROR: refusing symlinked path component \1 (a directory in the Claude profile is a symlink, not a real directory)#' \
            -e 's#ERROR: Claude profile path has an unsafe ancestor at ([^:]+): Not a directory#ERROR: refusing symlinked path component \1#' \
            "${errors}" >&2
    fi
    rm -f "${errors}"
    return "${status}"
}

install_payload() {
    local source_dir="$1" claude_dir="$2" manifest="$3" stats="$4" force_adopt="$5"
    local force_args=()
    if [ "${force_adopt}" = "1" ]; then
        force_args=(--force-adopt)
    fi
    # Preserve the public standalone payload contracts for audit tests:
    # ${SKILL_DIR}/blog/data/google-updates.json
    # scripts/*.py
    run_ownership_engine "${source_dir}/scripts/installer_ownership.py" install \
        --source "${source_dir}" \
        --profile "${claude_dir}" \
        --manifest "${manifest}" \
        --stats "${stats}" \
        --version "${CLAUDE_BLOG_VERSION}" \
        --legacy-inventory "${source_dir}/data/legacy-install-ownership.json" \
        ${force_args[@]+"${force_args[@]}"}
}

# Optional Python dependencies. Uses the same interpreter that was version
# checked (python3 -m pip, never a stray pip3), never sudo, and never
# --break-system-packages. Failure is a warning: the install itself is complete.
install_python_dependencies() {
    local requirements="$1"
    [ -f "${requirements}" ] || return 0
    if [ "${CLAUDE_BLOG_SKIP_PIP:-}" = "1" ]; then
        echo "→ Skipping Python dependencies (CLAUDE_BLOG_SKIP_PIP=1)."
        return 0
    fi
    if ! python3 -m pip --version &>/dev/null; then
        echo "→ Skipping Python dependencies: pip is not available for $(command -v python3)."
        echo "  Install them later in a virtual environment (see below)."
        print_venv_help
        return 0
    fi
    echo "→ Installing Python dependencies..."
    local pip_args=(--quiet -r "${requirements}")
    local in_venv=0
    if python3 -c 'import sys; raise SystemExit(0 if sys.prefix != sys.base_prefix else 1)' >/dev/null 2>&1; then
        in_venv=1
    else
        pip_args=(--user "${pip_args[@]}")
    fi
    local pip_log
    pip_log="$(mktemp -t claude-blog-pip-XXXXXX.log)"
    if python3 -m pip install "${pip_args[@]}" 2>"${pip_log}"; then
        rm -f "${pip_log}"
        if [ "${in_venv}" = "0" ]; then
            echo "  Installed into your user site-packages (pip --user), not system-wide."
        fi
        return 0
    fi
    echo "  WARNING: pip install failed. The skills are installed; only the optional Python extras are missing."
    echo "  Log: ${pip_log}"
    echo "  First error: $(head -n1 "${pip_log}" 2>/dev/null || echo '(empty)')"
    if grep -qi "externally-managed-environment" "${pip_log}" 2>/dev/null; then
        echo "  This Python is externally managed (PEP 668), so pip refuses to install into it."
    fi
    print_venv_help
}

print_venv_help() {
    echo "  Install the extras in a virtual environment instead (never with sudo):"
    echo "    python3 -m venv ~/.claude-blog-venv"
    echo "    ~/.claude-blog-venv/bin/python -m pip install -r requirements.txt"
    echo "  Run the helper scripts with ~/.claude-blog-venv/bin/python, or activate it first."
    echo "  To skip this step on later runs: CLAUDE_BLOG_SKIP_PIP=1 ./install.sh"
}

main() {
    local SKILL_DIR="${HOME}/.claude/skills"
    local CLAUDE_DIR="${HOME}/.claude"
    local MANIFEST="${CLAUDE_DIR}/claude-blog-manifest.txt"
    local SCRIPT_DIR
    local FORCE_ADOPT=0

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
        # Same rules as install.ps1: refuse values git could read as options or
        # alternate transports, and refs that are not plain branch/tag/SHA names.
        if ! printf '%s' "${repo}" | LC_ALL=C grep -Eq '^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9._-]+$'; then
            echo "ERROR: CLAUDE_BLOG_REPO must look like owner/name (got '${repo}')." >&2
            return 1
        fi
        if ! printf '%s' "${ref}" | LC_ALL=C grep -Eq '^[A-Za-z0-9][A-Za-z0-9._/+@-]*$' \
            || [[ "${ref}" == *..* || "${ref}" == */ || "${ref}" == *.lock ]]; then
            echo "ERROR: CLAUDE_BLOG_REF must be a commit SHA, tag or branch name (got '${ref}')." >&2
            return 1
        fi
        if [[ "${url}" == -* || "${url}" == ext::* || "${url}" == fd::* ]] || printf '%s' "${url}" | LC_ALL=C grep -q '[[:cntrl:]]'; then
            echo "ERROR: CLAUDE_BLOG_URL must be a normal git URL (got an unsafe value)." >&2
            return 1
        fi
        echo "→ Cloning claude-blog from ${repo} (${ref})..."
        TEMP_DIR="$(mktemp -d)"
        trap 'rm -rf "${TEMP_DIR}"' EXIT
        if ! command -v git &>/dev/null; then
            echo "ERROR: git is required to download the installer payload. Install git, or clone the repository yourself, check out the release, and run ./install.sh from the checkout." >&2
            return 1
        fi
        if ! git clone --depth 1 --branch "${ref}" -- "${url}" "${TEMP_DIR}/claude-blog" 2>/dev/null; then
            rm -rf "${TEMP_DIR}/claude-blog"
            if ! git clone -- "${url}" "${TEMP_DIR}/claude-blog" 2>/dev/null \
                || ! git -C "${TEMP_DIR}/claude-blog" checkout --detach "${ref}" >/dev/null 2>&1; then
                echo "ERROR: could not fetch ${url} at ref '${ref}'. Check the network, the repository name and that the ref exists, or clone the repository yourself, check out the ref, and run ./install.sh from the checkout." >&2
                return 1
            fi
        fi
        SCRIPT_DIR="${TEMP_DIR}/claude-blog"
        echo "  + checked out $(git -C "${SCRIPT_DIR}" rev-parse --short HEAD)"
        if [ "${ref}" = "main" ]; then
            echo "  Tip: set CLAUDE_BLOG_REF to a full commit SHA (preferred) or a release tag for a pinned install."
            echo "  The revision cloned here supplies the installer that runs next; the wrapper's own digest does not cover it."
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

    # Options are validated here, by the revision that actually runs, so a
    # newer wrapper can forward options that an older release does not know.
    local arg
    for arg in "$@"; do
        case "${arg}" in
            --force-adopt) FORCE_ADOPT=1 ;;
            -h|--help)
                sed -n '/^# Verified local install:/,/^$/p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
                return 0
                ;;
            *)
                echo "ERROR: unknown option: ${arg} (supported: --force-adopt, --help)" >&2
                return 2
                ;;
        esac
    done

    if ! command -v python3 &>/dev/null; then
        echo "ERROR: python3 3.11+ is required for ownership-safe installation, and python3 was not found on PATH." >&2
        print_python_help >&2
        return 1
    fi
    if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
        local python3_version python3_path
        python3_version="$(python3 -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null || echo unknown)"
        python3_path="$(command -v python3)"
        echo "ERROR: python3 ${python3_version} (${python3_path}) found; python3 3.11+ is required for ownership-safe installation." >&2
        print_python_help >&2
        return 1
    fi

    if [ -L "${CLAUDE_DIR}" ]; then
        echo "ERROR: refusing symlinked Claude profile: ${CLAUDE_DIR}" >&2
        return 1
    fi
    INSTALL_STATS_FILE="$(mktemp -t claude-blog-install-stats.XXXXXX)"
    trap 'if [ -n "${INSTALL_STATS_FILE}" ]; then rm -f "${INSTALL_STATS_FILE}"; fi; if [ -n "${TEMP_DIR}" ]; then rm -rf "${TEMP_DIR}"; fi' EXIT
    install_payload "${SCRIPT_DIR}" "${CLAUDE_DIR}" "${MANIFEST}" "${INSTALL_STATS_FILE}" "${FORCE_ADOPT}"

    local sub_skill_count agent_count root_script_count
    read -r sub_skill_count agent_count root_script_count < <(
        python3 - "${INSTALL_STATS_FILE}" <<'PY'
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
print(data["sub_skill_count"], data["agent_count"], data["root_script_count"])
PY
    )

    install_python_dependencies "${SCRIPT_DIR}/requirements.txt"

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
