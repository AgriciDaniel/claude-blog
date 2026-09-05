#!/usr/bin/env python3
"""Domain renderer: turn GEO citation readiness JSON into Markdown.

The report includes readiness metrics, passage-level checks, prioritized
recommendations, rollback notes, and source citations.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

from ingest_geo_citation_audit import clean_output_text, clean_structure, write_json


def load_plan(path: str | Path) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at line {exc.lineno}, column {exc.colno}") from exc
    if not isinstance(data, dict):
        raise ValueError("GEO citation readiness root must be an object")
    if data.get("schema") != "claude-blog-brain.geo-citation-readiness.v1":
        raise ValueError("GEO citation readiness schema is not supported")
    return clean_structure(data)


def render_markdown(plan: dict[str, Any]) -> str:
    input_data = plan.get("input", {})
    metrics = plan.get("metrics", {})
    lines: list[str] = [
        f"# GEO Citation Readiness Report: {text(input_data.get('audit_name', 'Audit'))}",
        "",
        f"URL: {text(input_data.get('url', ''))}",
        f"Title: {text(input_data.get('title', ''))}",
        f"Locale: {text(input_data.get('locale', ''))}",
        f"Readiness score: {text(plan.get('readiness_score', 'n/a'))}",
        "",
        "## Metrics",
        "",
        f"- Extractable passages: {metrics.get('extractable_passage_count', 0)} of {metrics.get('passage_count', 0)}",
        f"- Cited passages: {metrics.get('cited_passage_count', 0)} of {metrics.get('passage_count', 0)}",
        f"- Covered query terms: {metrics.get('covered_query_term_count', 0)} of {metrics.get('target_query_term_count', 0)}",
        f"- Entity count: {metrics.get('entity_count', 0)}",
        "",
        "## Readiness Checks",
        "",
        "<table>",
        "<thead><tr><th>Check</th><th>Score</th><th>Status</th><th>Finding</th><th>Sources</th></tr></thead>",
        "<tbody>",
    ]
    for item in plan.get("checks", []):
        lines.append(
            "<tr>"
            f"<td>{html.escape(text(item.get('name', '')))}</td>"
            f"<td>{html.escape(text(item.get('score', '')))}</td>"
            f"<td>{html.escape(text(item.get('status', '')))}</td>"
            f"<td>{html.escape(text(item.get('finding', '')))}</td>"
            f"<td>{html.escape(format_sources(item.get('source_ids', [])))}</td>"
            "</tr>"
        )
    lines.extend(["</tbody>", "</table>", "", "## Recommendations", ""])
    for item in plan.get("recommendations", []):
        lines.append(
            f"- **{text(item.get('priority', 'medium')).title()}** "
            f"{text(item.get('recommendation', ''))} "
            f"Sources: {format_sources(item.get('source_ids', []))}. "
            f"Rollback: {text(item.get('rollback_note', 'Review if source guidance changes.'))}"
        )
    lines.extend(["", "## Source Citations", ""])
    for source in plan.get("source_citations", []):
        lines.append(
            f"- `{text(source.get('id', 'source'))}`: "
            f"{text(source.get('title', 'Untitled'))}. "
            f"Published: {text(source.get('published', 'n/a'))}. "
            f"Retrieved: {text(source.get('retrieved', 'n/a'))}. "
            f"{text(source.get('url', ''))}"
        )
    report = "\n".join(lines).rstrip() + "\n"
    return assert_clean_output(report)


def text(value: Any) -> str:
    return clean_output_text(str(value))


def format_sources(source_ids: list[str]) -> str:
    if not source_ids:
        return "none"
    return ", ".join(f"`{text(source_id)}`" for source_id in source_ids)


def assert_clean_output(value: str) -> str:
    cleaned = clean_output_text(value)
    if "\u2014" in cleaned or "\u2013" in cleaned or "--" in cleaned:
        raise ValueError("rendered report contains a disallowed dash sequence")
    return cleaned


def write_markdown(markdown: str, output: str | Path | None) -> None:
    if output:
        Path(output).write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a GEO citation readiness Markdown report.")
    parser.add_argument("input")
    parser.add_argument("-o", "--output", default="")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable status when writing to a file.")
    args = parser.parse_args(argv)
    try:
        report = render_markdown(load_plan(args.input))
        write_markdown(report, args.output or None)
        if args.output and args.json:
            write_json({"ok": True, "output": str(args.output)}, None)
    except (OSError, ValueError) as exc:
        if args.json:
            write_json({"ok": False, "errors": [clean_output_text(str(exc))]}, None)
        else:
            print(clean_output_text(f"error: {exc}"), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
