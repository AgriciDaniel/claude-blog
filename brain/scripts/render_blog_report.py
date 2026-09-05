#!/usr/bin/env python3
"""Domain renderer: turn a blog optimization plan JSON into Markdown.

The report includes a scorecard table, prioritized recommendations, GEO and AI
citation readiness, schema recommendations, delivery verdict, and source
citations from the plan.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

from ingest_blog_input import clean_output_text, clean_structure


def load_plan(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("plan root must be an object")
    if data.get("schema") != "claude-blog-brain.blog-optimization-plan.v1":
        raise ValueError("plan schema is not supported")
    return clean_structure(data)


def render_markdown(plan: dict[str, Any]) -> str:
    title = text(plan.get("input", {}).get("title", "Blog post"))
    lines: list[str] = [
        f"# Blog Optimization Plan: {title}",
        "",
        f"URL: {text(plan.get('input', {}).get('url', ''))}",
        f"Target keyword: {text(plan.get('input', {}).get('target_keyword', ''))}",
        f"Locale: {text(plan.get('input', {}).get('locale', ''))}",
        "",
        "## Scorecard",
        "",
        *render_scorecard(plan),
        "",
        "## Delivery Contract",
        "",
    ]
    contract = plan.get("delivery_contract", {})
    lines.extend(
        [
            f"- Verdict: **{text(contract.get('verdict', 'review'))}**",
            f"- Overall score: {contract.get('overall_score', plan.get('scores', {}).get('overall', 'n/a'))}",
            f"- Confidence: {text(contract.get('confidence', 'medium'))}",
        ]
    )
    required = contract.get("required_before_publish", [])
    if required:
        lines.append("- Required before publish:")
        for item in required:
            lines.append(f"  - {text(item)}")
    lines.extend(["", "## Prioritized Recommendations", ""])
    recommendations = plan.get("prioritized_recommendations", [])
    if recommendations:
        for item in recommendations:
            lines.append(
                f"- **{text(item.get('priority', 'medium')).title()}** "
                f"{label_for_category(item.get('category', 'content'))}: "
                f"{text(item.get('recommendation', ''))} "
                f"Sources: {format_sources(item.get('source_ids', []))}"
            )
    else:
        lines.append("- No recommendations emitted.")
    lines.extend(["", "## GEO and AI Citation Readiness", ""])
    geo = plan.get("geo_ai_citation_readiness", {})
    lines.append(f"Readiness score: {geo.get('score', 'n/a')}")
    lines.append("")
    for check in geo.get("checks", []):
        lines.append(f"- **{text(check.get('name', 'Check'))}**: {text(check.get('status', 'review'))}")
        lines.append(f"  Evidence: {text(check.get('evidence', ''))}")
        lines.append(f"  Recommendation: {text(check.get('recommendation', ''))}")
        lines.append(f"  Sources: {format_sources(check.get('source_ids', []))}")
    tactics = geo.get("being_cited_tactics", [])
    if tactics:
        lines.extend(["", "Being-cited tactics:"])
        for tactic in tactics:
            lines.append(
                f"- **{text(tactic.get('priority', 'medium')).title()}** "
                f"{text(tactic.get('tactic', ''))} "
                f"Sources: {format_sources(tactic.get('source_ids', []))}"
            )
    lines.extend(["", "## Schema Recommendations", ""])
    for item in plan.get("schema_recommendations", []):
        lines.append(
            f"- **{text(item.get('schema_type', 'Schema'))}** "
            f"({text(item.get('status', 'review'))}, {text(item.get('priority', 'medium'))}): "
            f"{text(item.get('recommendation', ''))} "
            f"Sources: {format_sources(item.get('source_ids', []))}"
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


def render_scorecard(plan: dict[str, Any]) -> list[str]:
    rows = [
        "<table>",
        "<thead><tr><th>Category</th><th>Score</th><th>Status</th><th>Top finding</th></tr></thead>",
        "<tbody>",
    ]
    for item in plan.get("quality_read", []):
        findings = item.get("findings", [])
        finding = findings[0].get("finding", "") if findings else ""
        rows.append(
            "<tr>"
            f"<td>{html.escape(text(item.get('label', item.get('category', ''))))}</td>"
            f"<td>{html.escape(str(item.get('score', 'n/a')))}</td>"
            f"<td>{html.escape(text(item.get('status', 'review')))}</td>"
            f"<td>{html.escape(text(finding))}</td>"
            "</tr>"
        )
    rows.extend(["</tbody>", "</table>"])
    return rows


def label_for_category(category: str) -> str:
    labels = {
        "content": "Content",
        "seo": "SEO",
        "eeat": "E-E-A-T",
        "technical": "Technical",
        "ai_citation": "AI Citation",
        "schema": "Schema",
    }
    return labels.get(str(category), "Content")


def format_sources(source_ids: list[str]) -> str:
    if not source_ids:
        return "none"
    return ", ".join(f"`{text(source_id)}`" for source_id in source_ids)


def text(value: Any) -> str:
    return clean_output_text(str(value))


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
    parser = argparse.ArgumentParser(description="Render a blog optimization plan as Markdown.", add_help=False)
    parser.add_argument("input")
    parser.add_argument("-o", dest="output")
    parser.add_argument("--json-errors", action="store_true")
    parser.add_argument("-h", action="help")
    args = parser.parse_args(argv)
    try:
        write_markdown(render_markdown(load_plan(args.input)), args.output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        if args.json_errors:
            print(json.dumps({"ok": False, "errors": [clean_output_text(str(exc))]}, indent=2, sort_keys=True))
        else:
            print(clean_output_text(f"error: {exc}"), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
