#!/usr/bin/env python3
"""Build a DISCOURSE.md brief from pre-collected public discussion results.

The input file must be JSON shaped as either a list of result objects or an
object with a top-level ``results`` list. Every result is treated as untrusted
data. The validator accepts only small strings, http/https URLs, and known
fields so snippets cannot smuggle instructions into the brief generator.

CLI examples:
  python3 scripts/discourse_research.py --input results.json --topic "AI SEO" --output DISCOURSE.md
  python3 scripts/discourse_research.py --input results.json --topic "AI SEO" --format json
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

MAX_FIELD_CHARS = 4000
MAX_RESULTS = 500
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
ALLOWED_FIELDS = {"platform", "url", "title", "snippet", "date", "engagement_proxy"}
HTML_TAGS = re.compile(r"<[^>]*>")


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "topic"


def _resolve_output(path: str, root: Path) -> Path:
    """Resolve an output path under root and refuse symlink writes."""
    target = (root / path).resolve() if not os.path.isabs(path) else Path(path).resolve()
    root = root.resolve()
    if target != root and root not in target.parents:
        raise ValueError(f"Refusing to write outside working directory: {target}")
    if target.exists() and target.is_symlink():
        raise ValueError(f"Refusing to write through symlink: {target}")
    parent = target.parent
    if parent.exists() and parent.is_symlink():
        raise ValueError(f"Refusing to write under symlinked directory: {parent}")
    return target


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with open(tmp, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(tmp, path)
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass


def _validate_text(name: str, value: Any, required: bool = False) -> str | None:
    if value is None:
        if required:
            raise ValueError(f"Missing required field: {name}")
        return None
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string")
    if len(value) > MAX_FIELD_CHARS:
        raise ValueError(f"{name} exceeds {MAX_FIELD_CHARS} characters")
    if CONTROL_CHARS.search(value):
        raise ValueError(f"{name} contains control characters")
    return value.strip()


def _validate_url(value: Any) -> str:
    url = _validate_text("url", value, required=True)
    parsed = urlparse(url or "")
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("url must use http or https")
    if not parsed.netloc:
        raise ValueError("url must include a host")
    return url or ""


def _validate_item(raw: Any, index: int) -> dict[str, str | None]:
    if not isinstance(raw, dict):
        raise ValueError(f"result {index} must be an object")
    unknown = set(raw) - ALLOWED_FIELDS
    if unknown:
        raise ValueError(f"result {index} has unknown fields: {', '.join(sorted(unknown))}")
    return {
        "platform": _validate_text("platform", raw.get("platform")) or "unknown",
        "url": _validate_url(raw.get("url")),
        "title": _validate_text("title", raw.get("title"), required=True) or "Untitled",
        "snippet": _validate_text("snippet", raw.get("snippet")) or "",
        "date": _validate_text("date", raw.get("date")),
        "engagement_proxy": _validate_text("engagement_proxy", raw.get("engagement_proxy")),
    }


def load_results(path: Path) -> list[dict[str, str | None]]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    rows = payload.get("results") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("input must be a list or an object with results[]")
    if len(rows) > MAX_RESULTS:
        raise ValueError(f"input contains {len(rows)} results, max {MAX_RESULTS}")
    return [_validate_item(item, index) for index, item in enumerate(rows, 1)]


def load_decomposition(path: str | None) -> list[str]:
    if not path:
        return []
    p = Path(path)
    with open(p, "r", encoding="utf-8") as handle:
        questions = [line.strip() for line in handle if line.strip()]
    return questions[:20]


def _platform_counts(items: list[dict[str, str | None]]) -> Counter[str]:
    return Counter(str(item.get("platform") or "unknown").lower() for item in items)


def _theme_key(item: dict[str, str | None]) -> str:
    title = str(item.get("title") or "")
    snippet = str(item.get("snippet") or "")
    text = f"{title} {snippet}".lower()
    candidates = re.findall(r"[a-z][a-z0-9]{3,}", text)
    stop = {
        "about", "after", "also", "from", "have", "into", "more", "that",
        "this", "with", "your", "they", "will", "what", "when", "where",
        "which", "their", "there", "would", "could", "should",
    }
    words = [w for w in candidates if w not in stop]
    if not words:
        return str(item.get("platform") or "general").title()
    return " ".join(w.title() for w, _ in Counter(words).most_common(3))


def build_brief(topic: str, days: int, items: list[dict[str, str | None]], questions: list[str]) -> dict[str, Any]:
    platforms = _platform_counts(items)
    clusters: dict[str, list[dict[str, str | None]]] = defaultdict(list)
    for item in items:
        clusters[_theme_key(item)].append(item)

    ranked = sorted(
        clusters.items(),
        key=lambda kv: (len({str(i.get("platform")) for i in kv[1]}), len(kv[1])),
        reverse=True,
    )

    consensus = [
        {"theme": theme, "sources": sources}
        for theme, sources in ranked
        if len({str(i.get("platform")) for i in sources}) > 1
    ][:4]
    new_items = [{"theme": theme, "sources": sources} for theme, sources in ranked[:5]]
    niche = [
        {"theme": theme, "sources": sources}
        for theme, sources in ranked
        if len(sources) == 1
    ][:3]

    return {
        "topic": topic,
        "days": days,
        "generated": date.today().isoformat(),
        "source_count": len(items),
        "platforms": dict(sorted(platforms.items())),
        "decomposition": questions,
        "new_themes": new_items,
        "consensus": consensus,
        "niche": niche,
        "items": items,
    }


def _link(item: dict[str, str | None]) -> str:
    title = str(item.get("title") or "source").replace("[", "(").replace("]", ")")
    return f"[{title}]({item.get('url')})"


def _safe_markdown_text(value: str, limit: int) -> str:
    text = HTML_TAGS.sub("", value).strip()[:limit]
    text = html.escape(text, quote=False)
    return (
        text.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def _theme_paragraph(theme: dict[str, Any]) -> str:
    sources = theme.get("sources", [])
    links = ", ".join(_link(item) for item in sources[:3])
    snippets = [str(item.get("snippet") or "").strip() for item in sources if item.get("snippet")]
    summary = _safe_markdown_text(snippets[0], 280) if snippets else "No snippet was available."
    return f"- **{theme['theme']}**. {summary} Sources: {links}."


def render_markdown(brief: dict[str, Any]) -> str:
    questions = brief.get("decomposition") or ["Primary practitioner discourse", "Counter-perspective", "Recent concrete examples"]
    lines = [
        f"# Discourse Brief: {brief['topic']}",
        "",
        f"> Generated {brief['generated']} via /blog discourse. Window: last {brief['days']} days.",
        f"> Sources scanned: {brief['source_count']} across {len(brief['platforms'])} platforms.",
        "",
        "## Decomposition (the questions this brief answers)",
        "",
    ]
    for index, question in enumerate(questions, 1):
        lines.append(f"{index}. {question}")

    lines.extend(["", f"## What's NEW in the last {brief['days']} days", ""])
    if brief["new_themes"]:
        lines.extend(_theme_paragraph(theme) for theme in brief["new_themes"])
    else:
        lines.append("- Source coverage: insufficient. Reframe the topic or widen the freshness window.")

    lines.extend(["", "## Consensus across platforms", ""])
    if brief["consensus"]:
        lines.extend(_theme_paragraph(theme) for theme in brief["consensus"])
    else:
        lines.append("- No cross-platform consensus found in the supplied results.")

    lines.extend(["", "## Niche / single-source themes", ""])
    if brief["niche"]:
        lines.extend(_theme_paragraph(theme) for theme in brief["niche"])
    else:
        lines.append("- No single-source themes stood out in the supplied results.")

    lines.extend(["", "## Practitioner specifics (commands, configs, links)", ""])
    specifics = [item for item in brief["items"] if re.search(r"`|config|command|how to|setup|step", str(item.get("snippet") or ""), re.I)]
    if specifics:
        lines.extend(
            f"- From {_link(item)}: {_safe_markdown_text(str(item.get('snippet') or ''), 240)}"
            for item in specifics[:5]
        )
    else:
        lines.append("- No concrete commands, configs, or procedural details were visible in snippets.")

    lines.extend(["", "## Source list (cross-platform breakdown)", "", "| Platform | Sources scanned | Useful | Notes |", "|---|---:|---:|---|"])
    for platform, count in brief["platforms"].items():
        lines.append(f"| {platform} | {count} | {count} | SERP snippets only |")

    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a discourse brief from WebSearch results JSON")
    parser.add_argument("--input", required=True, help="Input JSON file from Phase 3")
    parser.add_argument("--topic", required=True, help="Original topic")
    parser.add_argument("--days", type=int, default=30, choices=[30, 90], help="Freshness window")
    parser.add_argument("--output", help="Markdown output path under the current working directory")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Stdout format when --output is omitted")
    parser.add_argument("--decomposition", help="Optional newline-delimited questions file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        items = load_results(Path(args.input))
        questions = load_decomposition(args.decomposition)
        brief = build_brief(args.topic, args.days, items, questions)
        markdown = render_markdown(brief)
        output_path = None
        if args.output:
            root = Path.cwd()
            requested = args.output
            target = _resolve_output(requested, root)
            _atomic_write(target, markdown)
            output_path = str(target)
            print(json.dumps({"status": "success", "output": output_path, "source_count": len(items)}, indent=2))
        elif args.format == "json":
            print(json.dumps({"status": "success", "brief": brief}, indent=2))
        else:
            print(markdown)
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
