#!/usr/bin/env python3
"""Synthesize starter deliverables from a vault raw-source manifest.

Re-running is safe for hand edits to the Action Roadmap: a section whose text
differs from the generated starter is treated as user-edited and kept, and a
section the user added is kept. A roadmap that is hand-written (neither
generated nor the scaffold template) makes the run stop with a message before
anything is written. Derived reports (Health Scorecard, Weekly Report) are
regenerated from the manifest on each run.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from safe_write import UnsafeWriteError, write_text_safely  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synthesize source-cited starter deliverables.")
    parser.add_argument("--vault", required=True)
    parser.add_argument("--json", action="store_true", help="Print a JSON result envelope.")
    args = parser.parse_args(argv)
    vault = Path(args.vault).expanduser().resolve()
    manifest_path = vault / ".raw" / ".manifest.json"
    if not manifest_path.exists():
        print("ERROR: missing .raw/.manifest.json; run scaffold and ingest first", file=sys.stderr)
        return 2
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sources = manifest.get("sources", [])
    source_rows = "\n".join(f"| `{item.get('path', '')}` | `{item.get('sha256', '')[:12]}` | {item.get('retrieved', '')} |" for item in sources) or "| No sources yet |  |  |"
    roadmap = vault / "wiki" / "deliverables" / "Action Roadmap.md"
    if roadmap.is_file() and not roadmap.is_symlink() and classify_existing(roadmap.read_text(encoding="utf-8")) == "handwritten":
        print(
            "ERROR: wiki/deliverables/Action Roadmap.md has none of the generated or scaffold "
            "sections, so it looks hand-written. Move it aside (or restore its generated "
            "headings) and rerun; nothing was written.",
            file=sys.stderr,
        )
        return 2
    preserved: list[str] = []
    try:
        preserved += write(vault, vault / "wiki" / "deliverables" / "Health Scorecard.md", f"""---
type: "deliverable"
title: "Health Scorecard"
domain: "claude-blog-brain"
created: "{date.today().isoformat()}"
updated: "{date.today().isoformat()}"
status: "draft"
tags: ["deliverable"]
---

# Health Scorecard

## Source Coverage

| Source | Hash | Retrieved |
|---|---|---:|
{source_rows}

## Current Read

This is a source-cited scaffold. Domain-specific conclusions remain blocked
until current trustworthy research is captured in `references/`.

Related: [[Action Roadmap]] | [[Weekly Report]] | [[Source Manifest Guide]]
""")
        preserved += write(vault, vault / "wiki" / "deliverables" / "Action Roadmap.md", f"""---
type: "deliverable"
title: "Action Roadmap"
domain: "claude-blog-brain"
created: "{date.today().isoformat()}"
updated: "{date.today().isoformat()}"
status: "draft"
tags: ["deliverable"]
---

# Action Roadmap

## Immediate Actions

1. Complete source intake.
2. Refresh official/current requirements.
3. Replace scaffold claims with sourced domain notes.

## Approval Gate

Every action requires source, confidence, owner, approval status, and rollback.

Related: [[Approval Queue]] | [[Health Scorecard]] | [[Best Practices Kernel]]
""", preserve_edited=True)
        preserved += write(vault, vault / "wiki" / "reports" / "Weekly Report.md", f"""---
type: "report"
title: "Weekly Report"
domain: "claude-blog-brain"
created: "{date.today().isoformat()}"
updated: "{date.today().isoformat()}"
status: "draft"
tags: ["report"]
---

# Weekly Report

## Summary

Claude Blog Brain is ready for source review. It has {len(sources)} raw source(s) in
the manifest.

## Evidence

- [[Health Scorecard]]
- [[Action Roadmap]]
- [[Source Manifest Guide]]

Related: [[Reporting Workflow]] | [[Approval Queue]]
""")
    except (UnsafeWriteError, HandWrittenNote, OSError) as exc:
        print(f"ERROR: cannot write deliverables: {exc}", file=sys.stderr)
        return 2
    if preserved:
        print("Kept user-edited section(s): " + ", ".join(preserved), file=sys.stderr)
    append_log(vault, "Synthesized source-cited starter deliverables.")
    payload = {"ok": True, "vault": str(vault), "sources": len(sources), "preserved_sections": preserved}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("Synthesis complete")
    return 0


SECTION_RE = re.compile(r"^## .*$", re.M)


def split_sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Split markdown into the preamble and (heading line, body) pairs."""
    marks = list(SECTION_RE.finditer(text))
    if not marks:
        return text, []
    sections = []
    for index, mark in enumerate(marks):
        end = marks[index + 1].start() if index + 1 < len(marks) else len(text)
        sections.append((mark.group(0), text[mark.end():end]))
    return text[:marks[0].start()], sections


def merge_generated(existing: str, generated: str, preserve_edited: bool) -> tuple[str, list[str]]:
    """Merge a regenerated note into an existing one, keeping user work.

    Returns the merged text and the headings that were kept from the existing
    file (edited generated sections when preserve_edited is set, plus sections
    the generator does not produce).
    """
    old_pre, old_sections = split_sections(existing)
    new_pre, new_sections = split_sections(generated)
    old_by_heading = dict(old_sections)
    known = {heading for heading, _ in new_sections}
    kept: list[str] = []
    created = re.search(r'^created: .*$', old_pre, re.M)
    if created:
        new_pre = re.sub(r'^created: .*$', lambda _m: created.group(0), new_pre, count=1, flags=re.M)
    merged = new_pre
    for heading, body in new_sections:
        old_body = old_by_heading.get(heading)
        if preserve_edited and old_body is not None and old_body.strip() != body.strip():
            body = old_body
            kept.append(heading.removeprefix("## "))
        merged += heading + body
    for heading, body in old_sections:
        if heading not in known:
            if not merged.endswith("\n\n"):
                merged = merged.rstrip("\n") + "\n\n"
            merged += heading + body
            kept.append(heading.removeprefix("## "))
    return merged, kept


class HandWrittenNote(ValueError):
    """The existing note is neither a generated starter nor the scaffold template."""


GENERATED_MARKERS = ("## Immediate Actions", "## Approval Gate")
SCAFFOLD_MARKERS = ("## Roadmap construction rules", "## Next 30 Days")


def classify_existing(text: str) -> str:
    """Return generated, scaffold or handwritten for an existing Action Roadmap."""
    headings = {mark.group(0) for mark in SECTION_RE.finditer(text)}
    if headings & set(GENERATED_MARKERS):
        return "generated"
    if headings & set(SCAFFOLD_MARKERS):
        return "scaffold"
    return "handwritten"


def write(vault: Path, path: Path, text: str, preserve_edited: bool = False) -> list[str]:
    """Write a generated note, keeping user-edited content. Returns kept headings.

    With preserve_edited, a note that already holds generated sections is merged
    (edited sections and user-added sections survive), the untouched scaffold
    template is replaced as before, and a note that is neither is refused.
    """
    text = text.rstrip() + "\n"
    kept: list[str] = []
    if preserve_edited and path.is_file() and not path.is_symlink():
        existing = path.read_text(encoding="utf-8")
        kind = classify_existing(existing)
        if kind == "handwritten":
            raise HandWrittenNote(
                f"{path.relative_to(vault).as_posix()} has none of the generated or scaffold "
                "sections, so it looks hand-written. Move it aside (or restore its generated "
                "headings) and rerun; nothing was overwritten."
            )
        if kind == "generated":
            text, kept = merge_generated(existing, text, True)
            text = text.rstrip() + "\n"
    write_text_safely(path, text, root=vault)
    return kept


def append_log(vault: Path, message: str) -> None:
    log = vault / "wiki" / "log.md"
    if log.exists():
        log.write_text(log.read_text(encoding="utf-8").rstrip() + f"\n- {date.today().isoformat()} - {message}\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
