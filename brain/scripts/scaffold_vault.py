#!/usr/bin/env python3
"""Scaffold a client vault from the template with marker-guarded replacement."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import stat
import sys
import tempfile
from datetime import date
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "assets" / "template-brain"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scaffold a client vault from the template brain.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--client-name", default="")
    parser.add_argument("--owner", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print a JSON result envelope.")
    args = parser.parse_args(argv)
    slug = safe_slug(args.client)
    out_dir = Path(args.out_dir).expanduser().resolve()
    vault = out_dir / slug
    if vault.exists() and any(vault.iterdir()) and not args.force:
        print(f"ERROR: vault exists and is not empty: {vault}", file=sys.stderr)
        return 2
    if vault.exists() and args.force:
        require_generated_vault_marker(vault)
    if not TEMPLATE.exists():
        print(f"ERROR: template missing: {TEMPLATE}", file=sys.stderr)
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)
    replacements = {
        "{{date}}": date.today().isoformat(),
        "{{client_slug}}": slug,
        "{{client_name}}": args.client_name or slug,
        "{{owner}}": args.owner,
    }
    with tempfile.TemporaryDirectory(prefix=f".{slug}-build-", dir=out_dir) as tmp:
        temp_vault = Path(tmp) / slug
        copy_template(TEMPLATE, temp_vault, replacements)
        manifest = temp_vault / ".raw" / ".manifest.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({
            "scaffold_history": [{
                "client": slug,
                "client_name": args.client_name or slug,
                "owner": args.owner,
                "created": date.today().isoformat(),
            }],
            "sources": [],
        }, indent=2) + "\n", encoding="utf-8")
        manifest.chmod(0o600)
        if vault.exists():
            shutil.rmtree(vault)
        shutil.copytree(temp_vault, vault)
    if args.json:
        print(json.dumps({"ok": True, "vault": str(vault)}, indent=2, sort_keys=True))
    else:
        print(vault)
    return 0


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug or slug in {".", ".."}:
        raise SystemExit("ERROR: invalid client slug")
    return slug


def copy_template(src: Path, dest: Path, replacements: dict[str, str]) -> None:
    for path in sorted(src.rglob("*")):
        if path.is_dir():
            continue
        if path.is_symlink():
            raise SystemExit(f"ERROR: template symlink not allowed: {path.relative_to(src).as_posix()}")
        rel = path.relative_to(src)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        data = path.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            target.write_bytes(data)
            continue
        for old, new in replacements.items():
            text = text.replace(old, new)
        if target.suffix == ".md":
            text = ensure_frontmatter_defaults(text)
        target.write_text(text, encoding="utf-8")


def ensure_frontmatter_defaults(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---", 4)
    if end == -1:
        return text
    frontmatter = text[4:end].strip("\n")
    body = text[end + 4 :]
    keys = {line.split(":", 1)[0].strip() for line in frontmatter.splitlines() if ":" in line}
    additions: list[str] = []
    if "domain" not in keys:
        additions.append('domain: "claude-blog-brain"')
    if "tags" not in keys:
        additions.append('tags: ["claude-blog-brain"]')
    if not additions:
        return text
    return "---\n" + frontmatter + "\n" + "\n".join(additions) + "\n---" + body


def require_generated_vault_marker(vault: Path) -> None:
    marker = vault / ".raw" / ".manifest.json"
    if not marker.exists() or not (vault / "CODEX.md").exists():
        raise SystemExit(f"ERROR: refusing to replace unmarked vault: {vault}")
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise SystemExit(f"ERROR: invalid vault marker: {exc}") from exc
    if "scaffold_history" not in data:
        raise SystemExit(f"ERROR: refusing to replace vault without scaffold_history marker: {vault}")


if __name__ == "__main__":
    raise SystemExit(main())
