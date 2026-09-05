#!/usr/bin/env python3
"""Lint Obsidian vault structure, frontmatter, raw manifest, and wikilinks."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
DEFAULT_VAULT = REPO / "assets" / "template-brain"
REQUIRED_FRONTMATTER = {"type", "title", "domain", "status", "created", "updated", "tags"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ALLOWED_STATUSES = {"active", "draft", "seed", "archived", "review"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint a brain vault.")
    parser.add_argument("--vault", default=str(DEFAULT_VAULT))
    parser.add_argument("--template", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print structured diagnostics.")
    args = parser.parse_args(argv)
    vault = Path(args.vault).expanduser().resolve()
    is_template = args.template or vault == DEFAULT_VAULT.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    for rel in ["CODEX.md", "README.md", "shipping-rules.md", ".raw/.manifest.json", "wiki/hot.md", "wiki/index.md", "wiki/overview.md", "wiki/log.md", "wiki/meta/Start Here.md", "wiki/meta/dashboard.md"]:
        if not (vault / rel).exists():
            errors.append(f"missing {rel}")
    check_raw_manifest(vault, errors)
    graph = vault / ".obsidian" / "graph.json"
    if graph.exists():
        data = json.loads(graph.read_text(encoding="utf-8"))
        if len(data.get("colorGroups") or []) < 4:
            errors.append("graph.json has fewer than 4 color groups")
    notes = list((vault / "wiki").rglob("*.md")) if (vault / "wiki").exists() else []
    stems = {p.stem.lower(): p for p in notes}
    rels = {p.relative_to(vault).with_suffix("").as_posix().lower(): p for p in notes}
    incoming = {p: 0 for p in notes}
    outgoing = {p: 0 for p in notes}
    duplicate_stems: dict[str, list[str]] = {}
    for path in notes:
        duplicate_stems.setdefault(path.stem.lower(), []).append(path.relative_to(vault).as_posix())
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            errors.append(f"missing frontmatter: {path.relative_to(vault)}")
        else:
            validate_frontmatter(vault, path, text, errors, warnings, template=is_template)
        if re.search(r"\{\{(?!date|owner|client_slug|client_name)[^}]+\}\}|__[A-Z0-9_]+__|\bTODO\b", text):
            errors.append(f"unresolved placeholder in {path.relative_to(vault)}")
        if any(part in {"deliverables", "reports"} for part in path.parts) and "[[" not in text and ".raw/" not in text and "sha256" not in text.lower():
            errors.append(f"deliverable/report lacks source citation: {path.relative_to(vault)}")
        for raw in re.findall(r"!?\[\[([^\]]+)\]\]", text):
            raw_target = raw.split("|", 1)[0].split("#", 1)[0].strip()
            target = raw_target.replace(".md", "").replace(".canvas", "").strip()
            if not target:
                continue
            outgoing[path] += 1
            key = target.lower()
            if key in stems:
                incoming[stems[key]] += 1
            elif key in rels:
                incoming[rels[key]] += 1
            elif not safe_link_exists(vault, raw_target):
                errors.append(f"dead wikilink in {path.relative_to(vault)}: {raw}")
    zero_in = [p.relative_to(vault).as_posix() for p in notes if incoming[p] == 0]
    zero_out = [p.relative_to(vault).as_posix() for p in notes if outgoing[p] == 0]
    if zero_in:
        warnings.append("zero incoming wiki notes: " + ", ".join(zero_in[:20]))
    if zero_out:
        warnings.append("zero outgoing wiki notes: " + ", ".join(zero_out[:20]))
    for stem, paths in duplicate_stems.items():
        if stem != "_index" and len(paths) > 1:
            errors.append(f"duplicate note stem {stem}: {', '.join(paths)}")
    if args.json:
        print(json.dumps({"ok": not errors, "diagnostics": diagnostics(errors, warnings)}, indent=2, sort_keys=True))
    else:
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("Vault lint passed" if not errors else "Vault lint failed")
    return 1 if errors else 0


def validate_frontmatter(vault: Path, path: Path, text: str, errors: list[str], warnings: list[str], *, template: bool) -> None:
    rel = path.relative_to(vault).as_posix()
    frontmatter = frontmatter_block(text)
    if frontmatter is None:
        errors.append(f"invalid frontmatter fence: {rel}")
        return
    fields = parse_frontmatter(frontmatter)
    missing = sorted(REQUIRED_FRONTMATTER - set(fields))
    if missing:
        target = warnings if template else errors
        target.append(f"frontmatter missing {', '.join(missing)}: {rel}")
    status = str(fields.get("status", "")).strip().strip("\"'")
    if status and status not in ALLOWED_STATUSES:
        errors.append(f"frontmatter invalid status {status}: {rel}")
    for key in ("created", "updated"):
        value = str(fields.get(key, "")).strip().strip("\"'")
        if value and not DATE_RE.match(value) and "{{date}}" not in value:
            errors.append(f"frontmatter invalid {key} date: {rel}")
    tags = fields.get("tags")
    if tags is not None and not str(tags).strip().startswith("["):
        errors.append(f"frontmatter tags must be an array: {rel}")


def frontmatter_block(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    return text[4:end]


def parse_frontmatter(frontmatter: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if not line.strip() or line.lstrip().startswith("-") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def safe_link_exists(vault: Path, raw_target: str) -> bool:
    raw_target = raw_target.strip()
    normalized = raw_target.replace(".md", "").replace(".canvas", "").strip()
    if not normalized or any(char in normalized for char in "*?[]{}"):
        return False
    candidate = Path(normalized)
    if candidate.is_absolute() or ".." in candidate.parts:
        return False
    possibilities = [
        vault / normalized,
        vault / f"{normalized}.md",
        vault / f"{normalized}.canvas",
        vault / "wiki" / f"{normalized}.md",
        vault / "wiki" / f"{normalized}.canvas",
        vault / "_attachments" / raw_target,
        vault / "wiki" / "canvases" / raw_target,
    ]
    if any(path.exists() for path in possibilities):
        return True
    if "/" in raw_target or "\\" in raw_target:
        return False
    search_root = vault / "wiki"
    if not search_root.exists():
        return False
    names = {raw_target, f"{normalized}.md", f"{normalized}.canvas"}
    return any(path.name in names for path in search_root.rglob("*"))


def diagnostics(errors: list[str], warnings: list[str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for severity, items in (("error", errors), ("warning", warnings)):
        for item in items:
            rows.append({
                "severity": severity,
                "code": diagnostic_code(item),
                "file": diagnostic_file(item),
                "line": None,
                "message": item,
            })
    return rows


def diagnostic_code(message: str) -> str:
    if "frontmatter" in message:
        return "FRONTMATTER"
    if "wikilink" in message:
        return "WIKILINK"
    if "raw manifest" in message:
        return "RAW_MANIFEST"
    return "VAULT"


def diagnostic_file(message: str) -> str:
    if ": " in message:
        return message.rsplit(": ", 1)[-1].split(": ", 1)[0]
    return ""


def check_raw_manifest(vault: Path, errors: list[str]) -> None:
    manifest_path = vault / ".raw" / ".manifest.json"
    if not manifest_path.exists():
        return
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        errors.append(f"invalid raw manifest: {exc}")
        return
    sources = data.get("sources", [])
    if not isinstance(sources, list):
        errors.append("raw manifest sources must be a list")
        return
    seen_paths: set[str] = set()
    for index, entry in enumerate(sources, start=1):
        label = f"raw manifest source #{index}"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        rel = entry.get("path")
        expected = entry.get("sha256")
        if not isinstance(rel, str) or not rel.strip():
            errors.append(f"{label} missing path")
            continue
        rel = rel.strip()
        if rel in seen_paths:
            errors.append(f"duplicate raw manifest path: {rel}")
        seen_paths.add(rel)
        if rel.startswith("/") or ".." in Path(rel).parts:
            errors.append(f"{label} has unsafe path: {rel}")
            continue
        source = vault / rel
        if not source.is_file():
            errors.append(f"{label} missing file: {rel}")
            continue
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            errors.append(f"{label} missing valid sha256")
            continue
        if sha256_file(source) != expected:
            errors.append(f"{label} sha256 mismatch: {rel}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
