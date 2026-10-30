#!/usr/bin/env python3
"""Validate repository-local references and FLOW prompt locks.

The checker is intentionally conservative: a referenced local path or a
FLOW-lock mismatch is an error, while an unreferenced resource is only an
advisory warning. It never changes the repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

SCANNED_ROOTS = ("docs", "skills", "agents", ".github")
RESOURCE_ROOTS = ("docs", "skills", "agents", "scripts")
EXPLICIT_PATH_RE = re.compile(
    r"`((?:skills|agents|scripts|docs)/[A-Za-z0-9_./-]+)`"
)
RELATIVE_RESOURCE_RE = re.compile(
    r"`((?:references|scripts|templates|assets)/[A-Za-z0-9_./-]+)`"
)
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
FLOW_LOCK = Path("skills/blog-flow/references/flow-prompts.lock")
NON_LOAD_BEARING_EXPLICIT_SOURCES = {
    "docs/CONTRIBUTORS.md",
    "docs/MCP-INTEGRATION.md",
    "docs/TODO.md",
}
PLACEHOLDER_TARGETS = {
    "url",
    "blog-url",
    "filename.md",
    "pillar.md",
    "x.md",
}


def _markdown_sources(root: Path) -> list[Path]:
    sources = [root / "README.md", root / "CLAUDE.md"]
    for directory in SCANNED_ROOTS:
        base = root / directory
        if base.is_dir():
            sources.extend(base.rglob("*.md"))
    return sorted({path for path in sources if path.is_file()})


def _normalise_link(source: Path, raw: str, root: Path) -> Path | None:
    target = raw.strip().split(maxsplit=1)[0].strip("<>")
    if (
        not target
        or target.startswith(("#", "/", "http://", "https://", "mailto:"))
        or "{" in target
        or "*" in target
        or "[" in target
        or "]" in target
        or "<" in target
        or ">" in target
    ):
        return None
    target = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if not target or Path(target).name.lower() in PLACEHOLDER_TARGETS:
        return None
    return (source.parent / target).resolve()


def _repo_relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _mark_target(root: Path, target: Path, referenced: set[str]) -> None:
    referenced.add(_repo_relative(root, target))
    if target.is_dir():
        for child in target.rglob("*"):
            if child.is_file() and "__pycache__" not in child.parts:
                referenced.add(_repo_relative(root, child))


def _skill_base(source: Path, root: Path) -> Path | None:
    for parent in source.parents:
        if parent == root.parent:
            break
        if (parent / "SKILL.md").is_file():
            return parent
        if parent == root:
            break
    return None


def _resolve_resource(root: Path, base: Path, raw: str) -> Path:
    local = (base / raw).resolve()
    if local.exists():
        return local
    repository = (root / raw).resolve()
    return repository if repository.exists() else local


def _reference_errors(root: Path) -> tuple[list[dict], set[str]]:
    errors: list[dict] = []
    referenced: set[str] = set()
    for source in _markdown_sources(root):
        raw_text = source.read_text(encoding="utf-8")
        text = raw_text
        # Examples in fenced code routinely use placeholder paths. They are
        # commands or output templates, not repository reference edges.
        text = re.sub(r"^```.*?^```", "", text, flags=re.MULTILINE | re.DOTALL)
        for raw in MARKDOWN_LINK_RE.findall(text):
            target = _normalise_link(source, raw, root)
            if target is None:
                continue
            rel = _repo_relative(root, target)
            if target.exists():
                _mark_target(root, target, referenced)
            else:
                errors.append(
                    {
                        "kind": "missing_markdown_target",
                        "source": source.relative_to(root).as_posix(),
                        "target": rel,
                    }
                )
        source_rel = source.relative_to(root).as_posix()
        if source_rel in NON_LOAD_BEARING_EXPLICIT_SOURCES:
            continue
        for raw in EXPLICIT_PATH_RE.findall(text):
            if (
                raw.endswith("active-persona.json")
                or Path(raw).name.lower() in PLACEHOLDER_TARGETS
            ):
                continue
            target = (root / raw).resolve()
            if not target.exists() and raw.startswith("scripts/"):
                # A skill reference may use its own directory as the path
                # base, for example blog-audio/references -> ../scripts.
                for parent in source.parents:
                    candidate = (parent / raw).resolve()
                    if candidate.exists():
                        target = candidate
                        break
            rel = _repo_relative(root, target)
            if target.exists():
                _mark_target(root, target, referenced)
            elif raw.endswith("/"):
                # Runtime-created directories such as persona stores are not
                # missing tracked resources.
                continue
            else:
                errors.append(
                    {
                        "kind": "missing_explicit_path",
                        "source": source.relative_to(root).as_posix(),
                        "target": raw,
                    }
                )

        # Resource paths inside runnable examples still establish discovery
        # edges when the target exists. Validate only prose paths above, but
        # use the raw source here so real command examples reduce orphan noise.
        base = _skill_base(source, root)
        if base is not None:
            for raw in RELATIVE_RESOURCE_RE.findall(text):
                target = _resolve_resource(root, base, raw)
                if target.exists():
                    _mark_target(root, target, referenced)
                elif not raw.endswith("/"):
                    errors.append(
                        {
                            "kind": "missing_skill_relative_path",
                            "source": source_rel,
                            "target": _repo_relative(root, target),
                        }
                    )
            for raw in RELATIVE_RESOURCE_RE.findall(raw_text):
                target = _resolve_resource(root, base, raw)
                if target.exists():
                    _mark_target(root, target, referenced)

        # Agent names are normally documented as Task targets rather than file
        # paths. Resolve those names to the tracked agent definition.
        for agent in (root / "agents").glob("*.md"):
            if re.search(rf"\b{re.escape(agent.stem)}\b", raw_text):
                _mark_target(root, agent.resolve(), referenced)

    # Wrapper dispatch tables and imports often name per-skill resources by
    # basename. Scope this discovery to each skill so generic names do not
    # suppress warnings across unrelated packages.
    for skill in (root / "skills").glob("*"):
        if not skill.is_dir() or not (skill / "SKILL.md").is_file():
            continue
        sources = [
            path
            for path in skill.rglob("*")
            if path.is_file() and path.suffix in {".md", ".py"}
        ]
        texts = {
            path: path.read_text(encoding="utf-8", errors="replace")
            for path in sources
        }
        for resource_dir in ("references", "scripts", "templates", "assets"):
            base = skill / resource_dir
            if not base.is_dir():
                continue
            for resource in base.rglob("*"):
                if not resource.is_file() or resource.name == "__init__.py":
                    continue
                needles = {resource.name}
                if resource.suffix == ".py":
                    needles.add(resource.stem)
                if any(
                    any(needle in source_text for needle in needles)
                    for source_path, source_text in texts.items()
                    if source_path != resource
                ):
                    _mark_target(root, resource.resolve(), referenced)

    # Root helpers are referenced from skill command examples by basename.
    # Treat those documented names as edges even when the installed path is
    # selected at runtime.
    markdown_corpus = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in _markdown_sources(root)
    )
    for helper in (root / "scripts").glob("*.py"):
        if helper.name in markdown_corpus or helper.stem in markdown_corpus:
            _mark_target(root, helper.resolve(), referenced)
    return errors, referenced


def _flow_lock_errors(root: Path) -> tuple[list[dict], set[str]]:
    errors: list[dict] = []
    referenced: set[str] = set()
    lock_path = root / FLOW_LOCK
    if not lock_path.is_file():
        return [
            {
                "kind": "missing_flow_lock",
                "source": FLOW_LOCK.as_posix(),
                "target": FLOW_LOCK.as_posix(),
            }
        ], referenced

    for line_number, line in enumerate(
        lock_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = re.fullmatch(r"([0-9a-f]{64})\s{2,}(.+)", stripped)
        if not match:
            errors.append(
                {
                    "kind": "invalid_flow_lock_entry",
                    "source": FLOW_LOCK.as_posix(),
                    "line": line_number,
                }
            )
            continue
        expected, raw_path = match.groups()
        target = (root / raw_path).resolve()
        rel = _repo_relative(root, target)
        referenced.add(rel)
        if not target.is_file():
            errors.append(
                {
                    "kind": "missing_flow_prompt",
                    "source": FLOW_LOCK.as_posix(),
                    "line": line_number,
                    "target": raw_path,
                }
            )
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(
                {
                    "kind": "flow_lock_digest_mismatch",
                    "source": FLOW_LOCK.as_posix(),
                    "line": line_number,
                    "target": raw_path,
                    "expected": expected,
                    "actual": actual,
                }
            )
    return errors, referenced


def _orphan_warnings(root: Path, referenced: set[str]) -> list[dict]:
    candidates: set[str] = set()
    for directory in RESOURCE_ROOTS:
        base = root / directory
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.name == "__init__.py":
                continue
            if path.suffix not in {".md", ".py", ".json", ".html"}:
                continue
            rel = path.relative_to(root).as_posix()
            if rel.endswith("/SKILL.md") or rel in {
                "docs/COMMANDS.md",
                "docs/ARCHITECTURE.md",
                "scripts/consistency_check.py",
                "scripts/validate_public_release.py",
            }:
                continue
            candidates.add(rel)
    return [
        {"kind": "orphan_resource", "target": path}
        for path in sorted(candidates - referenced)
    ]


def check(root: Path) -> dict:
    root = root.resolve()
    errors, referenced = _reference_errors(root)
    flow_errors, flow_referenced = _flow_lock_errors(root)
    errors.extend(flow_errors)
    referenced.update(flow_referenced)
    warnings = _orphan_warnings(root, referenced)
    return {
        "status": "pass" if not errors else "fail",
        "root": str(root),
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
            "references_verified": len(referenced),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate local references, FLOW locks, and orphan resources."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON.")
    args = parser.parse_args(argv)
    report = check(args.root)
    print(json.dumps(report, indent=None if args.compact else 2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
