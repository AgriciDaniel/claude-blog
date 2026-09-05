#!/usr/bin/env python3
"""Domain renderer: turn a topic cluster plan JSON into Markdown.

The report includes a cluster scorecard, internal-link matrix, prioritized
recommendations, rollback notes, and source citations.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

from ingest_topic_cluster_input import clean_output_text, clean_structure, write_json


def load_plan(path: str | Path) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at line {exc.lineno}, column {exc.colno}") from exc
    if not isinstance(data, dict):
        raise ValueError("topic cluster plan root must be an object")
    if data.get("schema") != "claude-blog-brain.topic-cluster-plan.v1":
        raise ValueError("topic cluster plan schema is not supported")
    return clean_structure(data)


def render_markdown(plan: dict[str, Any]) -> str:
    input_data = plan.get("input", {})
    lines: list[str] = [
        f"# Topic Cluster Internal Link Matrix: {text(input_data.get('cluster_name', 'Cluster'))}",
        "",
        f"Primary topic: {text(input_data.get('primary_topic', ''))}",
        f"Locale: {text(input_data.get('locale', ''))}",
        f"Audience: {text(input_data.get('audience', ''))}",
        "",
        "## Cluster Scorecard",
        "",
        "<table>",
        "<thead><tr><th>Check</th><th>Score</th><th>Finding</th><th>Sources</th></tr></thead>",
        "<tbody>",
    ]
    for item in plan.get("cluster_quality", []):
        lines.append(
            "<tr>"
            f"<td>{html.escape(text(item.get('name', '')))}</td>"
            f"<td>{html.escape(text(item.get('score', '')))}</td>"
            f"<td>{html.escape(text(item.get('finding', '')))}</td>"
            f"<td>{html.escape(format_sources(item.get('source_ids', [])))}</td>"
            "</tr>"
        )
    lines.extend(
        [
            "</tbody>",
            "</table>",
            "",
            "## Internal Link Matrix",
            "",
            "<table>",
            "<thead><tr><th>From</th><th>To</th><th>Anchor</th><th>Relationship</th><th>Status</th><th>Priority</th><th>Sources</th></tr></thead>",
            "<tbody>",
        ]
    )
    for row in plan.get("internal_link_matrix", []):
        lines.append(
            "<tr>"
            f"<td>{html.escape(text(row.get('from_title', '')))}</td>"
            f"<td>{html.escape(text(row.get('to_title', '')))}</td>"
            f"<td>{html.escape(text(row.get('anchor', '')))}</td>"
            f"<td>{html.escape(text(row.get('relationship', '')))}</td>"
            f"<td>{html.escape(text(row.get('status', '')))}</td>"
            f"<td>{html.escape(text(row.get('priority', '')))}</td>"
            f"<td>{html.escape(format_sources(row.get('source_ids', [])))}</td>"
            "</tr>"
        )
    lines.extend(["</tbody>", "</table>", "", "## Recommendations", ""])
    for item in plan.get("recommendations", []):
        lines.append(
            f"- **{text(item.get('priority', 'medium')).title()}** "
            f"{text(item.get('recommendation', ''))} "
            f"Sources: {format_sources(item.get('source_ids', []))}. "
            f"Rollback: {text(item.get('rollback_note', 'Review before publishing.'))}"
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
    parser = argparse.ArgumentParser(description="Render a topic cluster internal-link matrix report.")
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
