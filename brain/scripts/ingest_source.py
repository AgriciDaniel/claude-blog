#!/usr/bin/env python3
"""Ingest a local raw source into a vault with path, secret, and YAML guards."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
MAX_BYTES = 10 * 1024 * 1024
FORBIDDEN_SOURCE_NAMES = {".env", ".env.local", ".env.production", "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"}
SECRET_PATTERNS = {
    "private key": re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "openai api key": re.compile(rb"sk-[A-Za-z0-9_-]{20,}"),
    "anthropic api key": re.compile(rb"sk-ant-[A-Za-z0-9_-]{20,}"),
    "github token": re.compile(rb"(ghp|github_pat)_[A-Za-z0-9_]{20,}"),
    "aws key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "google api key": re.compile(rb"AIza[0-9A-Za-z_-]{20,}"),
    "bearer literal": re.compile(rb"Bearer\s+[A-Za-z0-9._-]{24,}"),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest one raw source into a brain vault.")
    parser.add_argument("--vault", required=True)
    parser.add_argument("--file", required=True)
    parser.add_argument("--source-type", default="manual")
    parser.add_argument("--allow-source-root", action="append", default=[], help="Approved local root for source files.")
    parser.add_argument("--json", action="store_true", help="Print a JSON result envelope.")
    args = parser.parse_args(argv)
    vault = Path(args.vault).expanduser().resolve()
    requested_source = Path(args.file).expanduser()
    if requested_source.is_symlink():
        print(f"ERROR: source symlink not allowed: {requested_source}", file=sys.stderr)
        return 2
    source = requested_source.resolve()
    if not (vault / "CODEX.md").exists():
        print(f"ERROR: not a brain vault: {vault}", file=sys.stderr)
        return 2
    if not source.is_file():
        print(f"ERROR: source file not found: {source}", file=sys.stderr)
        return 2
    if not is_allowed_source(source, vault, args.allow_source_root):
        print("ERROR: source file is outside approved roots; pass --allow-source-root for this import", file=sys.stderr)
        return 2
    if source.name in FORBIDDEN_SOURCE_NAMES:
        print(f"ERROR: credential-like source filename is not allowed: {source.name}", file=sys.stderr)
        return 2
    if source.stat().st_size > MAX_BYTES:
        print(f"ERROR: source file too large: {source}", file=sys.stderr)
        return 2
    secret = detect_secret(source)
    if secret:
        print(f"ERROR: refusing to ingest possible secret ({secret}): {source.name}", file=sys.stderr)
        return 2
    raw_dir = vault / ".raw" / "sources"
    raw_dir.mkdir(parents=True, exist_ok=True)
    source_digest = sha256_file(source)
    target = collision_safe_path(raw_dir, source.name, source_digest)
    shutil.copy2(source, target)
    digest = sha256_file(target)
    rel_target = target.relative_to(vault).as_posix()
    source_type = safe_label(args.source_type)
    display_title = safe_title(source.stem)
    update_manifest(vault, rel_target, digest, source_type)
    source_note = collision_safe_path(vault / "wiki" / "sources", f"{display_title}.md", digest)
    source_note.parent.mkdir(parents=True, exist_ok=True)
    rel_note = source_note.relative_to(vault).as_posix()
    source_note.write_text(f"""---
type: {yaml_string("source")}
title: {yaml_string(display_title)}
domain: {yaml_string("claude-blog-brain")}
created: {yaml_string(date.today().isoformat())}
updated: {yaml_string(date.today().isoformat())}
status: {yaml_string("active")}
tags: ["source"]
sources: [{yaml_string(rel_target)}]
---

# {display_title}

## Source

- Path: `{rel_target}`
- Hash: `{digest}`
- Retrieved: {date.today().isoformat()}
- Type: {source_type}

## Compiled Truth

Summarize this source without copying it wholesale.

Related: [[Source Manifest Guide]] | [[wiki/sources/_index|Sources Hub]]
""", encoding="utf-8")
    append_log(vault, f"Ingested source [[{display_title}]] from `{rel_target}`.")
    payload = {"ok": True, "copied": rel_target, "note": rel_note, "sha256": digest}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def is_allowed_source(source: Path, vault: Path, extra_roots: list[str]) -> bool:
    roots = [REPO, vault, *(Path(root).expanduser().resolve() for root in extra_roots)]
    return any(source == root or source.is_relative_to(root) for root in roots)


def detect_secret(path: Path) -> str:
    data = path.read_bytes()
    for name, pattern in SECRET_PATTERNS.items():
        if pattern.search(data):
            return name
    return ""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collision_safe_path(directory: Path, filename: str, digest: str) -> Path:
    safe_name = safe_filename(filename)
    candidate = directory / safe_name
    if not candidate.exists():
        return candidate
    stem = candidate.stem or "source"
    suffix = candidate.suffix
    digest_name = directory / f"{stem}-{digest[:12]}{suffix}"
    if not digest_name.exists():
        return digest_name
    counter = 2
    while True:
        numbered = directory / f"{stem}-{digest[:12]}-{counter}{suffix}"
        if not numbered.exists():
            return numbered
        counter += 1


def safe_filename(value: str) -> str:
    name = Path(value).name
    cleaned = re.sub(r"[^A-Za-z0-9._ -]+", "", name).strip()
    cleaned = cleaned.lstrip(".")
    return cleaned[:120] or "source"


def update_manifest(vault: Path, rel: str, digest: str, source_type: str) -> None:
    path = vault / ".raw" / ".manifest.json"
    data = {"sources": []}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"ERROR: raw manifest must be an object: {path}")
    sources = data.setdefault("sources", [])
    if not isinstance(sources, list):
        raise SystemExit(f"ERROR: raw manifest sources must be a list: {path}")
    data.setdefault("sources", []).append({
        "path": rel,
        "sha256": digest,
        "retrieved": date.today().isoformat(),
        "source_type": source_type,
    })
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    path.chmod(0o600)


def safe_title(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9 _-]+", "", value).strip() or "Source"
    return cleaned[:90]


def safe_label(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9 _.-]+", "", value).strip()
    return cleaned[:60] or "manual"


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def append_log(vault: Path, message: str) -> None:
    log = vault / "wiki" / "log.md"
    if log.exists():
        text = log.read_text(encoding="utf-8").rstrip() + f"\n- {date.today().isoformat()} - {message}\n"
        log.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
