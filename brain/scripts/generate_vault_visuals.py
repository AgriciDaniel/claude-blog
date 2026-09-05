#!/usr/bin/env python3
"""Generate simple vault visual assets from current wiki and source metadata."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def svg_template(note_count: int, link_count: int, source_count: int, deliverable_count: int) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 420" role="img" aria-labelledby="title desc">
<title id="title">Claude Blog Brain relationship map</title>
<desc id="desc">Current source, wiki, gate, and deliverable counts.</desc>
<rect width="980" height="420" fill="#f8fafc"/>
<text x="40" y="58" font-size="28" font-family="Inter,Arial" font-weight="700" fill="#172033">Claude Blog Brain Relationship Map</text>
<g font-family="Inter,Arial" font-size="14" font-weight="700">
<rect x="50" y="130" width="160" height="88" rx="8" fill="#fff" stroke="#586f92" stroke-width="3"/><text x="82" y="164" fill="#172033">Raw Sources</text><text x="110" y="194" fill="#586f92">{source_count}</text>
<rect x="290" y="130" width="160" height="88" rx="8" fill="#fff" stroke="#2f7f87" stroke-width="3"/><text x="324" y="164" fill="#172033">Wiki Memory</text><text x="326" y="194" fill="#2f7f87">{note_count} notes</text>
<rect x="530" y="130" width="160" height="88" rx="8" fill="#fff" stroke="#c85f4d" stroke-width="3"/><text x="560" y="164" fill="#172033">Checks + Gates</text><text x="578" y="194" fill="#c85f4d">{link_count} links</text>
<rect x="770" y="130" width="160" height="88" rx="8" fill="#fff" stroke="#f0b33d" stroke-width="3"/><text x="800" y="164" fill="#172033">Deliverables</text><text x="835" y="194" fill="#946200">{deliverable_count}</text>
</g>
<path d="M210 174 H290 M450 174 H530 M690 174 H770" stroke="#64748b" stroke-width="3"/>
</svg>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate vault visual assets.")
    parser.add_argument("--vault", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print a JSON result envelope.")
    args = parser.parse_args(argv)
    vault = Path(args.vault).expanduser().resolve()
    if not (vault / "CODEX.md").exists():
        raise SystemExit(f"ERROR: not a brain vault: {vault}")
    counts = graph_counts(vault)
    out = vault / "_attachments" / "brain-relationship-map.svg"
    if not args.dry_run:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(svg_template(**counts), encoding="utf-8")
    payload = {"ok": True, "out": out.relative_to(vault).as_posix(), "dry_run": args.dry_run, **counts}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(out)
    return 0


def graph_counts(vault: Path) -> dict[str, int]:
    notes = list((vault / "wiki").rglob("*.md")) if (vault / "wiki").exists() else []
    links = 0
    for path in notes:
        links += len(re.findall(r"!?\[\[([^\]]+)\]\]", path.read_text(encoding="utf-8", errors="replace")))
    manifest_path = vault / ".raw" / ".manifest.json"
    source_count = 0
    if manifest_path.exists():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            sources = data.get("sources", [])
            source_count = len(sources) if isinstance(sources, list) else 0
        except ValueError:
            source_count = 0
    deliverables = len(list((vault / "wiki" / "deliverables").glob("*.md"))) if (vault / "wiki" / "deliverables").exists() else 0
    return {
        "note_count": len(notes),
        "link_count": links,
        "source_count": source_count,
        "deliverable_count": deliverables,
    }


if __name__ == "__main__":
    raise SystemExit(main())
