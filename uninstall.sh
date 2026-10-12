#!/usr/bin/env bash
set -euo pipefail

# claude-blog uninstaller
# Removes verified package-owned files and preserves unknown or edited content.
#
#   bash uninstall.sh [--force-adopt]
#
#   --force-adopt  Also remove installed files that were edited after install.
#                  Each edited file is first copied to
#                  ~/.claude/claude-blog-backups/<timestamp>/.

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

main() {
    local SKILL_DIR="${HOME}/.claude/skills"
    local AGENT_DIR="${HOME}/.claude/agents"
    local MANIFEST="${HOME}/.claude/claude-blog-manifest.txt"
    local SCRIPT_DIR
    local FORCE_ADOPT=0
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

    local arg
    for arg in "$@"; do
        case "${arg}" in
            --force-adopt) FORCE_ADOPT=1 ;;
            -h|--help)
                sed -n '/^# claude-blog uninstaller/,/^$/p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
                return 0
                ;;
            *)
                echo "ERROR: unknown option: ${arg} (supported: --force-adopt, --help)" >&2
                return 2
                ;;
        esac
    done

    if [ -f "${BASH_SOURCE[0]:-}" ] && [ -d "$(dirname "${BASH_SOURCE[0]}")/skills/blog" ]; then
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    else
        SCRIPT_DIR=""
    fi

    echo "=== Uninstalling claude-blog ==="
    echo ""

    if ! command -v python3 &>/dev/null; then
        echo "ERROR: python3 3.11+ is required for ownership-safe uninstall." >&2
        echo "  On macOS install a current Python (for example: brew install python@3.12) and open a new terminal." >&2
        return 1
    fi

    if [ ! -e "${MANIFEST}" ] && [ ! -L "${MANIFEST}" ]; then
        echo "  No installation manifest found at ${MANIFEST}."
        echo "  Nothing was removed: this uninstaller only deletes files that a manifest proves it installed."
        echo "  - Installed as a Claude Code plugin? Remove it with:  /plugin uninstall claude-blog@agricidaniel-blog"
        echo "  - Installed by an older release, or the manifest was deleted? Files under ~/.claude/skills/blog*,"
        echo "    ~/.claude/agents/blog-*.md and ~/.claude/scripts/ are left untouched. Review them yourself"
        echo "    before deleting anything; a name prefix alone does not prove ownership."
        return 0
    fi

    local OWNERSHIP_ENGINE
    # Bash 3.2 treats an empty array as unset under nounset. Keep the
    # required command arguments in this array for standalone removal too.
    local OWNERSHIP_ARGS=(
        uninstall --profile "${HOME}/.claude" --manifest "${MANIFEST}"
    )
    if [ "${FORCE_ADOPT}" = "1" ]; then
        OWNERSHIP_ARGS+=(--force-adopt)
    fi
    if [ -n "${SCRIPT_DIR}" ] && [ -f "${SCRIPT_DIR}/scripts/installer_ownership.py" ]; then
        OWNERSHIP_ENGINE="${SCRIPT_DIR}/scripts/installer_ownership.py"
        OWNERSHIP_ARGS+=(--legacy-inventory "${SCRIPT_DIR}/data/legacy-install-ownership.json")
    elif [ -f "${HOME}/.claude/scripts/installer_ownership.py" ]; then
        OWNERSHIP_ENGINE="${HOME}/.claude/scripts/installer_ownership.py"
    else
        echo "ERROR: ownership engine is unavailable; use uninstall.sh from the complete reviewed repository." >&2
        return 1
    fi

    run_ownership_engine "${OWNERSHIP_ENGINE}" "${OWNERSHIP_ARGS[@]}"

    echo "  Shared Google credentials under ~/.config/claude-seo were left intact."
    echo ""
    echo "=== claude-blog uninstalled ==="
    echo ""
    echo "Restart Claude Code to complete removal."
}

main "$@"
