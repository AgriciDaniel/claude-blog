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

uninstall_action() {
  local mode="$1" dir="$2"
  python3 - "${mode}" "${dir}" <<'PY'
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path, PurePosixPath

MODE, DIRECTORY_RAW = sys.argv[1:]
DIRECTORY = Path(DIRECTORY_RAW)
MARKER = ".claude-blog-brain-install.json"
OWNER = "claude-blog-brain-installer"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def safe_relative(value: object) -> str:
    if not isinstance(value, str):
        fail("installation manifest contains a non-string path")
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or value == MARKER:
        fail(f"installation manifest contains an unsafe path: {value!r}")
    return value


def load_and_validate() -> dict[str, str] | None:
    if not DIRECTORY.exists() and not DIRECTORY.is_symlink():
        return None
    if DIRECTORY.is_symlink() or not DIRECTORY.is_dir():
        fail(f"installation target is not a real directory: {DIRECTORY}")
    marker = DIRECTORY / MARKER
    if marker.is_symlink() or not marker.is_file():
        fail(f"refusing to remove unmarked installation target: {DIRECTORY}")
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        fail(f"invalid installation ownership metadata at {marker}: {exc}")
    if data.get("schema_version") != 1 or data.get("owner") != OWNER:
        fail(f"unrecognized installation ownership metadata at {marker}")
    files = data.get("managed_files")
    if not isinstance(files, dict) or not files:
        fail(f"installation ownership metadata has no managed files: {marker}")
    normalized: dict[str, str] = {}
    for raw_path, expected in files.items():
        rel = safe_relative(raw_path)
        if not isinstance(expected, str) or len(expected) != 64:
            fail(f"installation manifest has an invalid hash for {rel}")
        path = DIRECTORY / Path(*PurePosixPath(rel).parts)
        current = DIRECTORY
        for part in PurePosixPath(rel).parts[:-1]:
            current = current / part
            if current.is_symlink():
                fail(f"managed path traverses a symlink: {current}")
        if path.is_symlink() or not path.is_file():
            fail(f"managed installation file is missing or replaced: {path}")
        if sha256(path) != expected:
            fail(f"managed installation file was modified: {path}")
        normalized[rel] = expected
    return normalized


def remove_from_copy(root: Path, managed: dict[str, str]) -> None:
    for rel in sorted(managed, key=lambda value: len(PurePosixPath(value).parts), reverse=True):
        (root / Path(*PurePosixPath(rel).parts)).unlink()
    (root / MARKER).unlink()
    directories: set[Path] = set()
    for rel in managed:
        directory = (root / Path(*PurePosixPath(rel).parts)).parent
        while directory != root and directory.is_relative_to(root):
            directories.add(directory)
            directory = directory.parent
    for directory in sorted(directories, key=lambda value: len(value.parts), reverse=True):
        if directory != root:
            try:
                directory.rmdir()
            except OSError:
                pass


def uninstall(managed: dict[str, str]) -> bool:
    temporary = Path(tempfile.mkdtemp(prefix=f".{DIRECTORY.name}.uninstall-", dir=DIRECTORY.parent))
    temporary.rmdir()
    backup = DIRECTORY.parent / f".{DIRECTORY.name}.backup-{uuid.uuid4().hex}"
    preserved = False
    try:
        shutil.copytree(DIRECTORY, temporary, symlinks=True)
        remove_from_copy(temporary, managed)
        preserved = any(temporary.iterdir())
        os.replace(DIRECTORY, backup)
        try:
            if preserved:
                os.replace(temporary, DIRECTORY)
        except BaseException:
            if backup.exists() and not DIRECTORY.exists():
                os.replace(backup, DIRECTORY)
            raise
        shutil.rmtree(backup)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return preserved


managed = load_and_validate()
if MODE == "apply" and managed is not None:
    print("preserved-user-files" if uninstall(managed) else "removed-clean-installation")
elif MODE not in {"apply", "preflight"}:
    fail(f"unknown uninstaller mode: {MODE}")
PY
}

remove_one() {
  local dir="$1" result
  if [ ! -e "${dir}" ] && [ ! -L "${dir}" ]; then
    echo "Claude Blog Brain is not installed at ${dir}"
    return
  fi
  result="$(uninstall_action apply "${dir}")"
  if [ "${result}" = "preserved-user-files" ]; then
    echo "Removed managed Claude Blog Brain files from ${dir}; preserved user files"
  else
    echo "Removed ${dir}"
  fi
}

loader_action() {
  local mode="$1" loader="$2"
  python3 - "${mode}" "${loader}" <<'PY'
from __future__ import annotations

import os
import stat
import sys
import tempfile
from pathlib import Path

mode, loader_raw = sys.argv[1:]
loader = Path(loader_raw)
start = b"<!-- claude-blog-brain-install:start -->"
end = b"<!-- claude-blog-brain-install:end -->"
block = start + b"\n@./claude-blog-brain/GEMINI.md\n" + end


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def atomic_write(data: bytes) -> None:
    mode = stat.S_IMODE(loader.stat().st_mode)
    descriptor, temporary_raw = tempfile.mkstemp(prefix=f".{loader.name}.", dir=loader.parent)
    temporary = Path(temporary_raw)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
        temporary.chmod(mode)
        os.replace(temporary, loader)
    finally:
        if temporary.exists():
            temporary.unlink()


exists = loader.exists() or loader.is_symlink()
if exists and (loader.is_symlink() or not loader.is_file()):
    fail(f"Gemini loader is not a regular file: {loader}")
data = loader.read_bytes() if exists else b""
start_count = data.count(start)
end_count = data.count(end)
block_count = data.count(block)
if start_count or end_count:
    if start_count != 1 or end_count != 1 or block_count != 1:
        fail(f"Gemini loader has malformed, duplicate, or modified ownership markers: {loader}")

if mode == "apply" and block_count == 1:
    remaining = data.replace(block, b"", 1)
    if remaining:
        atomic_write(remaining)
    else:
        loader.unlink()
    print("removed-owned-block")
elif mode == "apply":
    print("no-owned-block")
elif mode not in {"apply", "preflight"}:
    fail(f"unknown Gemini loader mode: {mode}")
PY
}

remove_gemini_loader() {
  local loader="${base_home}/.gemini/GEMINI.md" result
  if [ -e "${loader}" ] || [ -L "${loader}" ]; then
    result="$(loader_action apply "${loader}")"
    if [ "${result}" = "removed-owned-block" ]; then
      echo "Claude Blog Brain Gemini loader cleaned at ${loader}"
    fi
  fi
}

remove_gemini() {
  local dir="${base_home}/.gemini/claude-blog-brain"
  remove_one "${dir}"
  remove_gemini_loader
}

if [ "${target}" = "all" ]; then
  for name in codex claude agents openclaw portable; do
    uninstall_action preflight "$(target_dir "${name}")"
  done
  uninstall_action preflight "${base_home}/.gemini/claude-blog-brain"
  loader_action preflight "${base_home}/.gemini/GEMINI.md"
  for name in codex claude agents openclaw portable; do
    remove_one "$(target_dir "${name}")"
  done
  remove_gemini
elif [ "${target}" = "gemini" ]; then
  uninstall_action preflight "${base_home}/.gemini/claude-blog-brain"
  loader_action preflight "${base_home}/.gemini/GEMINI.md"
  remove_gemini
else
  uninstall_action preflight "$(target_dir "${target}")"
  remove_one "$(target_dir "${target}")"
fi
