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

install_action() {
  local mode="$1" dest="$2"
  python3 - "${mode}" "${source_dir}" "${dest}" <<'PY'
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path, PurePosixPath

MODE, SOURCE_RAW, DEST_RAW = sys.argv[1:]
SOURCE = Path(SOURCE_RAW)
DEST = Path(DEST_RAW)
MARKER = ".claude-blog-brain-install.json"
OWNER = "claude-blog-brain-installer"
TOP_FILES = (
    "SKILL.md", "AGENTS.md", "CLAUDE.md", "GEMINI.md", "README.md",
    "LICENSE", "CHANGELOG.md", "RELEASE_CHECKLIST.md",
)
TREES = ("scripts", "assets/template-brain", "references", "docs")


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


def source_files() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for name in TOP_FILES:
        path = SOURCE / name
        if path.is_file():
            result[name] = path
    for tree in TREES:
        root = SOURCE / tree
        for path in sorted(root.rglob("*")):
            if path.is_symlink():
                fail(f"source installation tree contains a symlink: {path}")
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            result[path.relative_to(SOURCE).as_posix()] = path
    return result


def load_owned_manifest() -> dict[str, str] | None:
    if not DEST.exists() and not DEST.is_symlink():
        return None
    if DEST.is_symlink() or not DEST.is_dir():
        fail(f"installation target is not a real directory: {DEST}")
    marker = DEST / MARKER
    if marker.is_symlink() or not marker.is_file():
        fail(f"refusing to overwrite unmarked installation target: {DEST}")
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
    for raw_path, raw_hash in files.items():
        rel = safe_relative(raw_path)
        if not isinstance(raw_hash, str) or len(raw_hash) != 64:
            fail(f"installation manifest has an invalid hash for {rel}")
        normalized[rel] = raw_hash
    return normalized


def target_path(rel: str) -> Path:
    path = DEST / Path(*PurePosixPath(rel).parts)
    current = DEST
    for part in PurePosixPath(rel).parts[:-1]:
        current = current / part
        if current.is_symlink():
            fail(f"managed path traverses a symlink: {current}")
        if current.exists() and not current.is_dir():
            fail(f"managed path parent is not a directory: {current}")
    return path


def validate_existing(previous: dict[str, str] | None, incoming: dict[str, Path]) -> None:
    if previous is None:
        return
    for rel, expected in previous.items():
        path = target_path(rel)
        if path.is_symlink() or not path.is_file():
            fail(f"managed installation file is missing or replaced: {path}")
        if sha256(path) != expected:
            fail(f"managed installation file was modified: {path}")
    for rel in incoming:
        path = target_path(rel)
        if rel not in previous and (path.exists() or path.is_symlink()):
            fail(f"incoming managed file would overwrite a user file: {path}")


def remove_managed(root: Path, managed: dict[str, str]) -> None:
    for rel in sorted(managed, key=lambda value: len(PurePosixPath(value).parts), reverse=True):
        path = root / Path(*PurePosixPath(rel).parts)
        if path.exists() or path.is_symlink():
            path.unlink()
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


def install(previous: dict[str, str] | None, incoming: dict[str, Path]) -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{DEST.name}.install-", dir=DEST.parent))
    temporary.rmdir()
    backup = DEST.parent / f".{DEST.name}.backup-{uuid.uuid4().hex}"
    try:
        if previous is None:
            temporary.mkdir(mode=0o700)
        else:
            shutil.copytree(DEST, temporary, symlinks=True)
            remove_managed(temporary, previous)
        managed_hashes: dict[str, str] = {}
        for rel, source in incoming.items():
            target = temporary / Path(*PurePosixPath(rel).parts)
            if target.exists() or target.is_symlink():
                fail(f"incoming managed file would overwrite a preserved user file: {target}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            target.chmod(source.stat().st_mode & 0o700)
            managed_hashes[rel] = sha256(target)
        marker = temporary / MARKER
        marker.write_text(json.dumps({
            "schema_version": 1,
            "owner": OWNER,
            "managed_files": dict(sorted(managed_hashes.items())),
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        marker.chmod(0o600)
        if previous is not None:
            os.replace(DEST, backup)
        try:
            os.replace(temporary, DEST)
        except BaseException:
            if previous is not None and backup.exists() and not DEST.exists():
                os.replace(backup, DEST)
            raise
        if backup.exists():
            shutil.rmtree(backup)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


incoming = source_files()
if not incoming:
    fail("source installation surface is empty")
previous = load_owned_manifest()
validate_existing(previous, incoming)
if MODE == "apply":
    install(previous, incoming)
elif MODE != "preflight":
    fail(f"unknown installer mode: {MODE}")
PY
}

install_one() {
  local dest="$1"
  install_action apply "${dest}"
  echo "Claude Blog Brain installed to ${dest}"
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
    loader.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(loader.stat().st_mode) if loader.exists() else 0o600
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

if mode == "apply" and block_count == 0:
    atomic_write(data + block)
elif mode not in {"apply", "preflight"}:
    fail(f"unknown Gemini loader mode: {mode}")
PY
}

install_gemini() {
  local dest="${base_home}/.gemini/claude-blog-brain"
  local loader="${base_home}/.gemini/GEMINI.md"
  install_one "${dest}"
  loader_action apply "${loader}"
  echo "Claude Blog Brain Gemini loader updated at ${loader}"
}

if [ "${target}" = "all" ]; then
  for name in codex claude agents openclaw portable; do
    install_action preflight "$(target_dir "${name}")"
  done
  install_action preflight "${base_home}/.gemini/claude-blog-brain"
  loader_action preflight "${base_home}/.gemini/GEMINI.md"
  for name in codex claude agents openclaw portable; do
    install_one "$(target_dir "${name}")"
  done
  install_gemini
elif [ "${target}" = "gemini" ]; then
  install_action preflight "${base_home}/.gemini/claude-blog-brain"
  loader_action preflight "${base_home}/.gemini/GEMINI.md"
  install_gemini
else
  install_action preflight "$(target_dir "${target}")"
  install_one "$(target_dir "${target}")"
fi
