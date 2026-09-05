#!/usr/bin/env python3
"""Package claude-blog for upload to Claude Cowork.

Cowork installs plugins either from a marketplace or from a direct upload.
This produces the upload artifact: a zip of exactly the files Claude loads at
runtime, with the plugin manifest at the archive root.

    python3 scripts/package_plugin.py
    python3 scripts/package_plugin.py --out-dir dist --format both

Output is written to ``dist/`` by default:

    dist/claude-blog-<version>.plugin   # upload this in Cowork
    dist/claude-blog-<version>.zip      # identical bytes, .zip extension

Stdlib only. Reads the repo and writes the archive; no network, and nothing
outside ``--out-dir`` is touched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# What ships. Anything not listed here is development scaffolding that the
# runtime never reads: tests, CI config, lockfiles, demo GIFs, docs sources.
PAYLOAD = [
    ".claude-plugin",
    "mcp-servers.json",
    "skills",
    "agents",
    "scripts",
    "data",          # google-updates.json ledger, read at runtime
    "LICENSE",
    "NOTICE",
    "README.md",
]

# Deliberately excluded: brain/ and branding/ are bundled project material that
# no skill reads and the installers do not ship (brain/ alone is ~5.8 MB), plus
# tests/, .github/ and docs sources.

# Never package these, wherever they appear in the tree.
EXCLUDE_NAMES = {
    "__pycache__",
    ".DS_Store",
    ".pytest_cache",
    ".venv",
    "venv",
    "node_modules",
    ".git",
}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".log"}

# Credential-shaped files must never end up in a distributable archive.
SECRET_NAMES = {
    "google-api.json",
    "oauth-token.json",
    "oauth_client.json",
    "service_account.json",
    "credentials.json",
    ".env",
}
SECRET_SUFFIXES = {".pem", ".key", ".p12"}


def plugin_version() -> str:
    manifest = json.loads(
        (REPO_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    return str(manifest.get("version", "0.0.0"))


def should_skip(path: Path) -> bool:
    if any(part in EXCLUDE_NAMES for part in path.parts):
        return True
    return path.suffix in EXCLUDE_SUFFIXES


def is_secret(path: Path) -> bool:
    return path.name in SECRET_NAMES or path.suffix in SECRET_SUFFIXES


def collect() -> list[Path]:
    files: list[Path] = []
    for entry in PAYLOAD:
        source = REPO_ROOT / entry
        if not source.exists():
            continue
        if source.is_file():
            files.append(source)
            continue
        files.extend(p for p in sorted(source.rglob("*")) if p.is_file())
    return [p for p in files if not should_skip(p)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir", default="dist", help="Output directory (default: dist)"
    )
    parser.add_argument(
        "--format",
        choices=("plugin", "zip", "both"),
        default="both",
        help="Archive extension to emit (default: both)",
    )
    args = parser.parse_args()

    files = collect()
    if not files:
        print("ERROR: no payload files found; run from the repo root.", file=sys.stderr)
        return 1

    leaked = [p.relative_to(REPO_ROOT) for p in files if is_secret(p)]
    if leaked:
        print(
            "ERROR: refusing to package credential-shaped files:\n  "
            + "\n  ".join(str(p) for p in leaked),
            file=sys.stderr,
        )
        return 2

    version = plugin_version()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    primary = out_dir / f"claude-blog-{version}.plugin"

    with zipfile.ZipFile(primary, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(REPO_ROOT).as_posix())

    digest = hashlib.sha256(primary.read_bytes()).hexdigest()
    outputs = [primary]

    if args.format in ("zip", "both"):
        mirror = out_dir / f"claude-blog-{version}.zip"
        shutil.copyfile(primary, mirror)
        outputs.append(mirror)
    if args.format == "zip":
        primary.unlink()
        outputs.remove(primary)

    size_kb = outputs[0].stat().st_size / 1024
    print(f"Packaged claude-blog {version}: {len(files)} files, {size_kb:.0f} KB")
    for path in outputs:
        print(f"  {path}")
    print(f"  sha256: {digest}")
    print("\nInstall in Cowork: Plugins > Add plugin > Upload, then pick the .plugin file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
