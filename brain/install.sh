#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: ./install.sh [--target codex|claude|agents|gemini|openclaw|portable|custom|all] [--path DIR]

Installs the Claude Blog Brain skill surface.
Use --target custom --path <agent-skill-root> for Hermes or another runtime
when its official skill root is known.
Set CLAUDE_BLOG_BRAIN_INSTALL_HOME to test against a temporary home directory.
USAGE
}

target="codex"
custom_path=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --target) target="${2:?}"; shift 2 ;;
    --path) custom_path="${2:?}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "${target}" in codex|claude|agents|gemini|openclaw|portable|custom|all) ;; *) echo "ERROR: invalid target" >&2; exit 2 ;; esac
if [ "${target}" = "custom" ] && [ -z "${custom_path}" ]; then
  echo "ERROR: --target custom requires --path" >&2
  exit 2
fi

source_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
base_home="${CLAUDE_BLOG_BRAIN_INSTALL_HOME:-${HOME}}"

target_dir() {
  case "$1" in
    codex) echo "${base_home}/.codex/skills/claude-blog-brain" ;;
    claude) echo "${base_home}/.claude/skills/claude-blog-brain" ;;
    agents) echo "${base_home}/.agents/skills/claude-blog-brain" ;;
    openclaw) echo "${base_home}/.openclaw/skills/claude-blog-brain" ;;
    portable) echo "${base_home}/.agent-skills/claude-blog-brain" ;;
    custom) echo "${custom_path%/}/claude-blog-brain" ;;
  esac
}

copy_tree() {
  local src="$1" dest="$2"
  mkdir -p "${dest}"
  (cd "${src}" && find . -type f ! -path '*/__pycache__/*' ! -name '*.pyc' -print0 | while IFS= read -r -d '' file; do
    mkdir -p "${dest}/$(dirname "${file}")"
    cp "${file}" "${dest}/${file}"
  done)
}

install_one() {
  local dest="$1"
  rm -rf "${dest}"
  mkdir -p "${dest}"
  for file in SKILL.md AGENTS.md CLAUDE.md GEMINI.md README.md LICENSE CHANGELOG.md RELEASE_CHECKLIST.md; do
    if [ -f "${source_dir}/${file}" ]; then
      cp "${source_dir}/${file}" "${dest}/${file}"
    fi
  done
  copy_tree "${source_dir}/scripts" "${dest}/scripts"
  copy_tree "${source_dir}/assets/template-brain" "${dest}/assets/template-brain"
  copy_tree "${source_dir}/references" "${dest}/references"
  copy_tree "${source_dir}/docs" "${dest}/docs"
  chmod -R go-rwx "${dest}"
  echo "Claude Blog Brain installed to ${dest}"
}

install_gemini() {
  local dest="${base_home}/.gemini/claude-blog-brain"
  local loader="${base_home}/.gemini/GEMINI.md"
  install_one "${dest}"
  mkdir -p "$(dirname "${loader}")"
  python - "${loader}" "@./claude-blog-brain/GEMINI.md" <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
import_line = sys.argv[2]
start = "<!-- claude-blog-brain-install:start -->"
end = "<!-- claude-blog-brain-install:end -->"
block = f"{start}\n{import_line}\n{end}"
text = path.read_text(encoding="utf-8") if path.exists() else ""
pattern = f"{re.escape(start)}.*?{re.escape(end)}"
if re.search(pattern, text, flags=re.S):
    text = re.sub(pattern, block, text, flags=re.S)
else:
    text = (text.rstrip() + "\n\n" + block + "\n").lstrip()
path.write_text(text, encoding="utf-8")
PY
  echo "Claude Blog Brain Gemini loader updated at ${loader}"
}

if [ "${target}" = "all" ]; then
  for name in codex claude agents openclaw portable; do
    install_one "$(target_dir "${name}")"
  done
  install_gemini
elif [ "${target}" = "gemini" ]; then
  install_gemini
else
  install_one "$(target_dir "${target}")"
fi
