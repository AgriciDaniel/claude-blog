#!/usr/bin/env bash
set -euo pipefail

target="codex"
custom_path=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --target) target="${2:?}"; shift 2 ;;
    --path) custom_path="${2:?}"; shift 2 ;;
    -h|--help) echo "Usage: ./uninstall.sh [--target codex|claude|agents|gemini|openclaw|portable|custom|all] [--path DIR]"; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; exit 2 ;;
  esac
done

case "${target}" in codex|claude|agents|gemini|openclaw|portable|custom|all) ;; *) echo "ERROR: invalid target" >&2; exit 2 ;; esac
if [ "${target}" = "custom" ] && [ -z "${custom_path}" ]; then
  echo "ERROR: --target custom requires --path" >&2
  exit 2
fi
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

remove_one() {
  local dir="$1"
  if [ -d "${dir}" ]; then
    rm -rf "${dir}"
    echo "Removed ${dir}"
  else
    echo "Claude Blog Brain is not installed at ${dir}"
  fi
}

remove_gemini() {
  local dir="${base_home}/.gemini/claude-blog-brain"
  local loader="${base_home}/.gemini/GEMINI.md"
  remove_one "${dir}"
  if [ -f "${loader}" ]; then
    python - "${loader}" <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
start = "<!-- claude-blog-brain-install:start -->"
end = "<!-- claude-blog-brain-install:end -->"
text = path.read_text(encoding="utf-8")
pattern = f"\n*{re.escape(start)}.*?{re.escape(end)}\n*"
new_text = re.sub(pattern, "\n", text, flags=re.S).strip()
if new_text:
    path.write_text(new_text + "\n", encoding="utf-8")
else:
    path.unlink()
PY
    echo "Claude Blog Brain Gemini loader cleaned at ${loader}"
  fi
}

if [ "${target}" = "all" ]; then
  for name in codex claude agents openclaw portable; do
    remove_one "$(target_dir "${name}")"
  done
  remove_gemini
elif [ "${target}" = "gemini" ]; then
  remove_gemini
else
  remove_one "$(target_dir "${target}")"
fi
