#!/usr/bin/env python3
"""Build release ZIP artifacts after source, path, and secret scans."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
TEXT_SUFFIXES = {".base", ".canvas", ".css", ".csv", ".html", ".json", ".md", ".py", ".sh", ".toml", ".txt", ".yaml", ".yml"}
SKIP_PARTS = {".git", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", "__pycache__", "build", "dist", "venv"}
SKIP_SUFFIXES = {".pyc", ".pyo", ".log"}
FORBIDDEN_ENTRY_NAMES = {".env", ".env.local", ".env.production", ".DS_Store", "Thumbs.db", "workspace.json"}
MAX_SCAN_BYTES = 25 * 1024 * 1024
FORBIDDEN_TEXT_PATTERNS = {
    "local home path": re.compile(rb"(?:/home|/var/home|/Users)/[A-Za-z0-9_.-]+|[A-Za-z]:\\Users\\[A-Za-z0-9_.-]+", re.I),
    "private key": re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "openai api key": re.compile(rb"sk-[A-Za-z0-9_-]{20,}"),
    "anthropic api key": re.compile(rb"sk-ant-[A-Za-z0-9_-]{20,}"),
    "github token": re.compile(rb"(ghp|github_pat)_[A-Za-z0-9_]{20,}"),
    "aws key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "google api key": re.compile(rb"AIza[0-9A-Za-z_-]{20,}"),
    "bearer literal": re.compile(rb"Bearer\s+[A-Za-z0-9._-]{24,}"),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build verified release ZIP artifacts.")
    parser.add_argument("--version", required=True)
    parser.add_argument("--dist-dir", default="dist")
    parser.add_argument("--release-type", default="scaffold", choices=["scaffold", "demo", "market-ready"])
    parser.add_argument("--allow-outside-dist", action="store_true", help="Allow --dist-dir outside the repo for isolated tests.")
    parser.add_argument("--json", action="store_true", help="Print the release manifest JSON after writing artifacts.")
    args = parser.parse_args(argv)
    version = normalize_version(args.version)
    dist = (REPO / args.dist_dir).resolve()
    if dist != REPO and not dist.is_relative_to(REPO) and not args.allow_outside_dist:
        raise SystemExit(f"ERROR: --dist-dir must resolve inside the repo: {dist}")
    dist.mkdir(parents=True, exist_ok=True)
    if args.release_type == "market-ready":
        enforce_market_ready_gate()
    scan_source_tree()
    artifacts = [
        build_zip(dist / f"claude-blog-brain-template-v{version}.zip", REPO / "assets" / "template-brain", "claude-blog-brain-template"),
        build_zip(dist / f"claude-blog-brain-sample-vault-v{version}.zip", REPO / "examples" / "sample-vault", "claude-blog-brain-sample-vault"),
        build_source_zip(dist / f"claude-blog-brain-source-v{version}.zip", version),
    ]
    for artifact in artifacts:
        validate_zip(artifact["path"])
    manifest = {
        "product": "claude-blog-brain",
        "version": version,
        "release_type": args.release_type,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "git_commit": git_commit(),
        "artifacts": [{"file": a["path"].name, "sha256": sha256_file(a["path"]), "bytes": a["path"].stat().st_size, "entries": a["entries"]} for a in artifacts],
        "checks": ["repo source scan passed", "zip entry scan passed", "zip content secret scan passed", "zip content local-path scan passed"],
    }
    manifest_path = dist / "RELEASE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sums = dist / "SHA256SUMS"
    write_sha256s(sums, [*(a["path"] for a in artifacts), manifest_path])
    validate_sha256s(sums)
    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        print(f"Release package built in {dist}")
    return 0


def enforce_market_ready_gate() -> None:
    audit = REPO / "scripts" / "audit_brain.py"
    if not audit.exists():
        raise SystemExit("ERROR: market-ready release blocked: missing scripts/audit_brain.py")
    proc = subprocess.run(
        [sys.executable, str(audit), "--require", "market-ready", "--json"],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode:
        detail = "\n".join(part for part in [proc.stdout.strip(), proc.stderr.strip()] if part)
        raise SystemExit("ERROR: market-ready release blocked by audit:\n" + detail)


def normalize_version(value: str) -> str:
    version = value.strip().removeprefix("v")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise SystemExit("ERROR: --version must look like 0.1.0")
    return version


def should_skip(path: Path) -> bool:
    if set(path.parts) & SKIP_PARTS:
        return True
    if any(part.endswith(".egg-info") for part in path.parts):
        return True
    return path.suffix in SKIP_SUFFIXES


def reject_forbidden_entry(path: Path) -> None:
    if path.name in FORBIDDEN_ENTRY_NAMES:
        raise SystemExit(f"ERROR: forbidden release entry: {path.as_posix()}")
    if path.is_absolute() or ".." in path.parts:
        raise SystemExit(f"ERROR: unsafe release entry: {path.as_posix()}")


def iter_tree(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if should_skip(rel):
            continue
        reject_forbidden_entry(rel)
        if path.is_symlink():
            raise SystemExit(f"ERROR: symlink not allowed: {rel.as_posix()}")
        if path.is_file():
            files.append(path)
    return sorted(files)


def source_files() -> list[Path]:
    if (REPO / ".git").exists():
        reject_dirty_tracked_files()
        reject_untracked_files()
        proc = subprocess.run(["git", "ls-files", "-z", "--cached"], cwd=REPO, capture_output=True, check=False)
        if proc.returncode != 0:
            raise SystemExit(proc.stderr.decode("utf-8", "replace"))
        files = []
        for raw in proc.stdout.split(b"\0"):
            if raw:
                rel = Path(raw.decode("utf-8", "replace"))
                if should_skip(rel):
                    continue
                reject_forbidden_entry(rel)
                path = REPO / rel
                if path.is_symlink():
                    raise SystemExit(f"ERROR: symlink not allowed: {rel.as_posix()}")
                if path.is_file():
                    files.append(path)
        return sorted(files)
    return iter_tree(REPO)


def reject_dirty_tracked_files() -> None:
    dirty: set[str] = set()
    for args in (["git", "diff", "--name-only", "-z"], ["git", "diff", "--name-only", "-z", "--cached"]):
        proc = subprocess.run(args, cwd=REPO, capture_output=True, check=False)
        if proc.returncode != 0:
            raise SystemExit(proc.stderr.decode("utf-8", "replace"))
        dirty.update(raw.decode("utf-8", "replace") for raw in proc.stdout.split(b"\0") if raw)
    blocked = sorted(path for path in dirty if not should_skip(Path(path)))
    if blocked:
        raise SystemExit("ERROR: dirty tracked files would make release non-reproducible: " + ", ".join(blocked[:10]))


def reject_untracked_files() -> None:
    proc = subprocess.run(["git", "ls-files", "-z", "--others", "--exclude-standard"], cwd=REPO, capture_output=True, check=False)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr.decode("utf-8", "replace"))
    untracked = sorted(raw.decode("utf-8", "replace") for raw in proc.stdout.split(b"\0") if raw)
    allowed = [p for p in untracked if not should_skip(Path(p))]
    if allowed:
        raise SystemExit("ERROR: untracked files would make release non-reproducible: " + ", ".join(allowed[:10]))


def scan_source_tree() -> None:
    for path in source_files():
        rel = path.relative_to(REPO)
        if not should_skip(rel):
            scan_file(path, rel.as_posix())


def build_zip(out: Path, source: Path, root_name: str) -> dict[str, object]:
    entries = 0
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in iter_tree(source):
            zf.write(path, (Path(root_name) / path.relative_to(source)).as_posix())
            entries += 1
    return {"path": out, "entries": entries}


def build_source_zip(out: Path, version: str) -> dict[str, object]:
    entries = 0
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in source_files():
            rel = path.relative_to(REPO)
            if not should_skip(rel):
                zf.write(path, (Path(f"claude-blog-brain-v{version}") / rel).as_posix())
                entries += 1
    return {"path": out, "entries": entries}


def validate_zip(path: Path) -> None:
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        if not names:
            raise SystemExit(f"ERROR: empty artifact: {path.name}")
        for name in names:
            rel = Path(name)
            for part in rel.parts:
                reject_forbidden_entry(Path(part))
            if should_skip(rel) or any(part in SKIP_PARTS for part in rel.parts):
                raise SystemExit(f"ERROR: forbidden zip entry in {path.name}: {name}")
            mode = zf.getinfo(name).external_attr >> 16
            if stat.S_ISLNK(mode):
                raise SystemExit(f"ERROR: symlink entry in {path.name}: {name}")
            scan_bytes(zf.read(name), f"{path.name}:{name}", rel.suffix)


def scan_file(path: Path, label: str) -> None:
    size = path.stat().st_size
    if size > MAX_SCAN_BYTES:
        raise SystemExit(f"ERROR: file too large for release scan: {label}")
    scan_bytes(path.read_bytes(), label, path.suffix)


def scan_bytes(data: bytes, label: str, suffix: str) -> None:
    if suffix and suffix not in TEXT_SUFFIXES:
        return
    for name, pattern in FORBIDDEN_TEXT_PATTERNS.items():
        if pattern.search(data):
            raise SystemExit(f"ERROR: {name} found in {label}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_sha256s(path: Path, artifacts: list[Path]) -> None:
    path.write_text("\n".join(f"{sha256_file(a)}  {a.name}" for a in artifacts) + "\n", encoding="utf-8")


def validate_sha256s(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        expected, filename = line.split("  ", 1)
        actual = sha256_file(path.parent / filename)
        if expected != actual:
            raise SystemExit(f"ERROR: checksum mismatch for {filename}")


def git_commit() -> str | None:
    if not (REPO / ".git").exists():
        return None
    proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True, check=False)
    return proc.stdout.strip() if proc.returncode == 0 else None


if __name__ == "__main__":
    raise SystemExit(main())
