#!/usr/bin/env python3
"""
AI Citation Readiness Heuristic.

Usage:
    python3 ai_citation_score.py FILE
    python3 ai_citation_score.py FILE with format json or markdown
    python3 ai_citation_score.py FILE with engine all, ai_overview, perplexity, or chatgpt
    python3 ai_citation_score.py DIR in batch mode

Scoring model:
    Each engine receives a 0-100 internal readiness score from observable
    editorial and technical signals produced by analyze_blog.analyze_file.
    These scores are not calibrated probabilities and do not predict whether
    any answer engine will cite a page. Overall score is a weighted blend:
    ai_overview 40 percent, perplexity 35 percent, and chatgpt 25 percent.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import sys; sys.path.insert(0, str(Path(__file__).resolve().parent)); import analyze_blog


ENGINE_WEIGHTS: dict[str, float] = {
    "ai_overview": 0.40,
    "perplexity": 0.35,
    "chatgpt": 0.25,
}

ENGINE_LABELS: dict[str, str] = {
    "ai_overview": "AI Overview",
    "perplexity": "Perplexity",
    "chatgpt": "ChatGPT",
}

ALL_ENGINES = tuple(ENGINE_WEIGHTS.keys())
LONG_FLAG = "-" * 2


def _to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _clamp_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def _tier_count(tier_counts: dict[Any, Any], tier: int) -> int:
    return _to_int(tier_counts.get(tier, tier_counts.get(str(tier), 0)))


def _factor(points: int, max_points: int, signal: Any) -> dict[str, Any]:
    points = max(0, min(max_points, int(points)))
    return {
        "points": points,
        "max_points": max_points,
        "signal": signal,
    }


def _count_points(count: int, bands: list[tuple[int, int]]) -> int:
    score = 0
    for threshold, points in bands:
        if count >= threshold:
            score = points
    return score


def _score_ai_overview(analysis: dict[str, Any]) -> dict[str, Any]:
    ai_ready = analysis.get("ai_citation_readiness", {})
    headings = analysis.get("headings", {})
    schema = analysis.get("schema", {})
    citations = analysis.get("citations", {})
    frontmatter = analysis.get("frontmatter", {})
    structured_data = analysis.get("structured_data", {})
    engagement = analysis.get("engagement", {})
    images = analysis.get("images", {})
    charts = analysis.get("charts", {})

    inline_citations = _to_int(citations.get("inline_citations"))
    sourced_statistics = _to_int(citations.get("sourced_statistics"))
    unsourced_statistics = _to_int(citations.get("unsourced_statistics"))
    source_points = _count_points(inline_citations, [(1, 8), (2, 12), (3, 15)])
    if sourced_statistics > 0 and unsourced_statistics == 0:
        source_points += 10
    elif sourced_statistics > 0:
        source_points += 5
    elif unsourced_statistics == 0:
        source_points += 5
    source_points = max(0, min(25, source_points - min(10, unsourced_statistics * 2)))

    purpose_points = 0
    if frontmatter.get("title"):
        purpose_points += 5
    if ai_ready.get("purpose_statement"):
        purpose_points += 5
    if headings.get("hierarchy_clean"):
        purpose_points += 4
    if _to_int(headings.get("h2_count")) >= 1:
        purpose_points += 2
    entity_definitions = _to_int(ai_ready.get("entity_definitions"))
    purpose_points += _count_points(entity_definitions, [(1, 2), (2, 4)])
    purpose_points = min(20, purpose_points)

    self_contained = _to_int(ai_ready.get("self_contained_sections"))
    usefulness_points = _count_points(self_contained, [(1, 6), (2, 10), (3, 12)])
    usefulness_points += _count_points(_to_int(engagement.get("example_count")), [(1, 4), (2, 6)])
    structures = (
        _to_int(structured_data.get("table_count"))
        + _to_int(structured_data.get("ordered_list_items"))
        + _to_int(structured_data.get("unordered_list_items"))
    )
    usefulness_points += _count_points(structures, [(1, 1), (3, 2)])
    usefulness_points = min(20, usefulness_points)

    schema_points = 0
    if schema.get("has_blogposting"):
        schema_points += 10
    if schema.get("has_person"):
        schema_points += 3
    if schema.get("has_organization") or schema.get("has_breadcrumblist"):
        schema_points += 2
    schema_points = min(15, schema_points)

    crawl_points = 0 if ai_ready.get("has_robots_restriction") else 10
    media_count = _to_int(images.get("count")) + _to_int(charts.get("chart_count"))
    media_points = _count_points(media_count, [(1, 5), (2, 8), (3, 10)])
    if _to_int(images.get("without_alt_text")) > 0:
        media_points = max(0, media_points - 2)

    factors = {
        "source_fidelity": _factor(
            source_points,
            25,
            {
                "inline_citations": inline_citations,
                "sourced_statistics": sourced_statistics,
                "unsourced_statistics": unsourced_statistics,
            },
        ),
        "purpose_and_entity_clarity": _factor(
            purpose_points,
            20,
            {
                "has_title": bool(frontmatter.get("title")),
                "purpose_statement": bool(ai_ready.get("purpose_statement")),
                "hierarchy_clean": bool(headings.get("hierarchy_clean")),
                "entity_definitions": entity_definitions,
            },
        ),
        "reader_usefulness": _factor(
            usefulness_points,
            20,
            {
                "self_contained_sections": self_contained,
                "examples": _to_int(engagement.get("example_count")),
                "useful_structures": structures,
            },
        ),
        "article_schema": _factor(
            schema_points,
            15,
            {
                "has_blogposting_or_article": bool(schema.get("has_blogposting")),
                "has_person": bool(schema.get("has_person")),
                "has_organization": bool(schema.get("has_organization")),
                "has_breadcrumblist": bool(schema.get("has_breadcrumblist")),
                "schema_count": _to_int(schema.get("schema_count")),
            },
        ),
        "crawlability": _factor(
            crawl_points,
            10,
            {"has_robots_restriction": bool(ai_ready.get("has_robots_restriction"))},
        ),
        "relevant_media": _factor(
            media_points,
            10,
            {
                "media_count": media_count,
                "images_without_alt": _to_int(images.get("without_alt_text")),
            },
        ),
    }

    score = sum(factor["points"] for factor in factors.values())
    return {"score": _clamp_score(score), "factors": factors}


def _score_perplexity(analysis: dict[str, Any]) -> dict[str, Any]:
    citations = analysis.get("citations", {})
    ai_ready = analysis.get("ai_citation_readiness", {})
    engagement = analysis.get("engagement", {})

    inline_citations = _to_int(citations.get("inline_citations"))
    parenthetical_citations = _to_int(citations.get("paren_citations"))
    total_citations = inline_citations + parenthetical_citations
    citation_points = _count_points(total_citations, [(1, 8), (2, 15), (3, 22), (5, 30)])

    tier_counts = citations.get("tier_counts", {})
    tier_1 = _tier_count(tier_counts, 1)
    tier_2 = _tier_count(tier_counts, 2)
    authority_points = 0
    if tier_1 >= 2:
        authority_points += 18
    elif tier_1 == 1:
        authority_points += 14
    if tier_2 >= 2:
        authority_points += 7
    elif tier_2 == 1:
        authority_points += 4
    authority_points = min(25, authority_points)

    sourced_statistics = _to_int(citations.get("sourced_statistics"))
    unsourced_statistics = _to_int(citations.get("unsourced_statistics"))
    if sourced_statistics == 0 and unsourced_statistics == 0:
        statistic_points = 15
    else:
        statistic_points = _count_points(sourced_statistics, [(1, 10), (2, 16), (3, 21), (4, 25)])
    statistic_points = max(0, statistic_points - min(10, unsourced_statistics * 3))

    unique_sources = _to_int(citations.get("unique_sources"))
    diversity_points = _count_points(unique_sources, [(1, 3), (2, 6), (3, 10)])
    usefulness_points = _count_points(
        _to_int(ai_ready.get("evidence_backed_sections")),
        [(1, 4), (2, 7), (3, 8)],
    )
    usefulness_points += _count_points(_to_int(engagement.get("example_count")), [(1, 1), (2, 2)])
    usefulness_points = min(10, usefulness_points)

    factors = {
        "source_citations": _factor(
            citation_points,
            30,
            {
                "inline_citations": inline_citations,
                "parenthetical_citations": parenthetical_citations,
                "total_citations": total_citations,
            },
        ),
        "source_authority": _factor(
            authority_points,
            25,
            {"tier_1_sources": tier_1, "tier_2_sources": tier_2},
        ),
        "sourced_statistics": _factor(
            statistic_points,
            25,
            {
                "sourced_statistics": sourced_statistics,
                "unsourced_statistics": unsourced_statistics,
            },
        ),
        "citation_diversity": _factor(
            diversity_points,
            10,
            {"unique_sources": unique_sources},
        ),
        "reader_usefulness": _factor(
            usefulness_points,
            10,
            {
                "evidence_backed_sections": _to_int(ai_ready.get("evidence_backed_sections")),
                "examples": _to_int(engagement.get("example_count")),
            },
        ),
    }

    score = sum(factor["points"] for factor in factors.values())
    return {"score": _clamp_score(score), "factors": factors}


def _score_chatgpt(analysis: dict[str, Any]) -> dict[str, Any]:
    ai_ready = analysis.get("ai_citation_readiness", {})
    headings = analysis.get("headings", {})
    structured_data = analysis.get("structured_data", {})
    citations = analysis.get("citations", {})
    engagement = analysis.get("engagement", {})
    frontmatter = analysis.get("frontmatter", {})

    source_points = _count_points(_to_int(citations.get("inline_citations")), [(1, 8), (2, 15), (3, 20)])
    if _to_int(citations.get("unsourced_statistics")) == 0:
        source_points += 5
    source_points = min(25, source_points)

    purpose_points = 0
    if frontmatter.get("title"):
        purpose_points += 5
    if ai_ready.get("purpose_statement"):
        purpose_points += 5
    if headings.get("hierarchy_clean"):
        purpose_points += 5
    if _to_int(headings.get("h2_count")) >= 1:
        purpose_points += 5

    utility_points = _count_points(
        _to_int(ai_ready.get("self_contained_sections")),
        [(1, 7), (2, 12), (3, 15)],
    )
    utility_points += _count_points(_to_int(engagement.get("example_count")), [(1, 3), (2, 5)])
    utility_points = min(20, utility_points)

    entity_definitions = _to_int(ai_ready.get("entity_definitions"))
    entity_points = _count_points(entity_definitions, [(1, 7), (2, 12), (3, 15)])

    table_count = max(_to_int(ai_ready.get("table_count")), _to_int(structured_data.get("table_count")))
    list_items = (
        _to_int(ai_ready.get("list_count"))
        + _to_int(structured_data.get("unordered_list_items"))
        + _to_int(structured_data.get("ordered_list_items"))
    )
    extract_points = min(10, table_count * 4 + _count_points(list_items, [(3, 3), (6, 6)]))
    crawl_points = 0 if ai_ready.get("has_robots_restriction") else 10

    factors = {
        "source_fidelity": _factor(
            source_points,
            25,
            {
                "inline_citations": _to_int(citations.get("inline_citations")),
                "unsourced_statistics": _to_int(citations.get("unsourced_statistics")),
            },
        ),
        "purpose_clarity": _factor(
            purpose_points,
            20,
            {
                "has_title": bool(frontmatter.get("title")),
                "purpose_statement": bool(ai_ready.get("purpose_statement")),
                "hierarchy_clean": bool(headings.get("hierarchy_clean")),
            },
        ),
        "reader_utility": _factor(
            utility_points,
            20,
            {
                "self_contained_sections": _to_int(ai_ready.get("self_contained_sections")),
                "examples": _to_int(engagement.get("example_count")),
            },
        ),
        "entity_definitions": _factor(
            entity_points,
            15,
            {"entity_definitions": entity_definitions},
        ),
        "extractable_lists_tables": _factor(
            extract_points,
            10,
            {"table_count": table_count, "list_items": list_items},
        ),
        "crawlability": _factor(
            crawl_points,
            10,
            {"has_robots_restriction": bool(ai_ready.get("has_robots_restriction"))},
        ),
    }

    score = sum(factor["points"] for factor in factors.values())
    return {"score": _clamp_score(score), "factors": factors}


def _engine_results(analysis: dict[str, Any]) -> dict[str, dict[str, Any]]:
    scored = {
        "ai_overview": _score_ai_overview(analysis),
        "perplexity": _score_perplexity(analysis),
        "chatgpt": _score_chatgpt(analysis),
    }
    for engine, result in scored.items():
        result["weight"] = ENGINE_WEIGHTS[engine]
        result["readiness_score"] = result["score"]
    return scored


def _overall_score(engine_results: dict[str, dict[str, Any]]) -> int:
    weighted = sum(engine_results[engine]["score"] * ENGINE_WEIGHTS[engine] for engine in ALL_ENGINES)
    return _clamp_score(weighted)


def _gap(engine_results: dict[str, dict[str, Any]], engine: str, factor: str) -> int:
    item = engine_results.get(engine, {}).get("factors", {}).get(factor, {})
    return max(0, _to_int(item.get("max_points")) - _to_int(item.get("points")))


def _build_recommendations(
    engine_results: dict[str, dict[str, Any]],
    selected_engines: tuple[str, ...],
) -> list[dict[str, Any]]:
    single_engine = len(selected_engines) == 1

    candidates = [
        (
            "Make important sections self-contained and support their reusable claims with primary sources or transparent original evidence.",
            [
                ("ai_overview", "source_fidelity"),
                ("ai_overview", "reader_usefulness"),
                ("perplexity", "reader_usefulness"),
                ("chatgpt", "source_fidelity"),
                ("chatgpt", "reader_utility"),
            ],
        ),
        (
            "Add accurate BlogPosting or Article JSON-LD with author details and applicable "
            "visible dates; use dateModified only after a substantive update.",
            [("ai_overview", "article_schema")],
        ),
        (
            "Support material claims with sufficient relevant, authoritative "
            "sources; use source count and diversity only when the topic "
            "requires them.",
            [
                ("perplexity", "source_citations"),
                ("perplexity", "source_authority"),
                ("perplexity", "sourced_statistics"),
                ("perplexity", "citation_diversity"),
            ],
        ),
        (
            "Clarify the page purpose, use stable entity names, and make the heading hierarchy match the reader's task.",
            [
                ("ai_overview", "purpose_and_entity_clarity"),
                ("chatgpt", "purpose_clarity"),
                ("chatgpt", "entity_definitions"),
            ],
        ),
        (
            "Add tables or lists that summarize methods, numbers, and decisions.",
            [("chatgpt", "extractable_lists_tables")],
        ),
        (
            "Add relevant diagrams, screenshots, or charts with descriptive alternative text when they improve understanding.",
            [("ai_overview", "relevant_media")],
        ),
    ]

    ranked: list[dict[str, Any]] = []
    for text, factor_refs in candidates:
        impact = 0.0
        for engine, factor in factor_refs:
            if engine not in selected_engines:
                continue
            weight = 1.0 if single_engine else ENGINE_WEIGHTS[engine]
            impact += _gap(engine_results, engine, factor) * weight
        if impact > 0:
            ranked.append({"recommendation": text, "estimated_impact": int(round(impact))})

    ranked.sort(key=lambda item: (-item["estimated_impact"], item["recommendation"]))
    return ranked[:3]


def score_analysis(analysis: dict[str, Any], engine: str = "all") -> dict[str, Any]:
    if "error" in analysis:
        return {"error": analysis["error"]}
    if engine != "all" and engine not in ALL_ENGINES:
        return {"error": f"Unknown engine: {engine}"}

    all_results = _engine_results(analysis)
    selected_engines = ALL_ENGINES if engine == "all" else (engine,)
    visible_results = {name: all_results[name] for name in selected_engines}
    overall = _overall_score(all_results) if engine == "all" else visible_results[engine]["score"]

    return {
        "file": analysis.get("file", ""),
        "overall": overall,
        # Deprecated compatibility alias. This value is a readiness heuristic,
        # not a calibrated probability.
        "overall_probability": overall,
        "methodology": "internal_ai_citation_readiness_heuristic",
        "calibrated_probability": False,
        "model_weights": ENGINE_WEIGHTS,
        "engine_filter": engine,
        "engines": visible_results,
        "factors": {name: visible_results[name]["factors"] for name in selected_engines},
        "recommendations": _build_recommendations(all_results, selected_engines),
    }


def score_file(file_path: str | Path, engine: str = "all") -> dict[str, Any]:
    try:
        analysis = analyze_blog.analyze_file(str(file_path))
    except (OSError, UnicodeDecodeError) as exc:
        analysis = {"error": f"Could not analyze {file_path}: {exc}"}
    return score_analysis(analysis, engine=engine)


def _process_batch(directory: Path, engine: str) -> dict[str, Any]:
    files: list[Path] = []
    for pattern in ("*.md", "*.mdx", "*.html"):
        files.extend(sorted(directory.glob(pattern)))

    results = [score_file(path, engine=engine) for path in sorted(files)]
    return {
        "batch": True,
        "count": len(results),
        "engine_filter": engine,
        "model_weights": ENGINE_WEIGHTS,
        "methodology": "internal_ai_citation_readiness_heuristic",
        "calibrated_probability": False,
        "results": results,
    }


def _format_markdown(result: dict[str, Any]) -> str:
    if "error" in result:
        return f"## Error\n\n{result['error']}"
    if result.get("batch"):
        parts = [_format_markdown(item) for item in result.get("results", [])]
        return "\n\n".join(parts)

    file_name = Path(str(result.get("file", ""))).name
    lines = [
        f"## AI Citation Readiness Heuristic: {file_name}",
        "",
        f"Overall readiness: {result.get('overall', 0)}/100",
        "",
        "This is an internal editorial heuristic, not a calibrated citation probability.",
        "",
        "### Engine Scores",
    ]

    for engine, details in result.get("engines", {}).items():
        lines.append(f"- {ENGINE_LABELS.get(engine, engine)}: {details.get('score', 0)}/100")

    for engine, details in result.get("engines", {}).items():
        lines.extend(["", f"### {ENGINE_LABELS.get(engine, engine)} Factors"])
        for name, factor in details.get("factors", {}).items():
            label = name.replace("_", " ").title()
            lines.append(f"- {label}: {factor.get('points', 0)}/{factor.get('max_points', 0)}")

    lines.extend(["", "### Recommendations"])
    recommendations = result.get("recommendations", [])
    if recommendations:
        for item in recommendations:
            lines.append(f"- {item['recommendation']} Impact {item['estimated_impact']}")
    else:
        lines.append("- No score-lifting recommendations found.")

    return "\n".join(lines)


def _write_or_print(output: str, output_path: str | None) -> None:
    if output_path:
        analyze_blog._safe_write_text(output_path, output)
        print(f"Wrote report to {output_path}", file=sys.stderr)
    else:
        print(output)


def _json_error(message: str) -> str:
    return json.dumps({"error": message}, sort_keys=True)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="AI citation readiness heuristic")
    parser.add_argument("input", help="Blog file path or directory")
    parser.add_argument(f"{LONG_FLAG}format", choices=["json", "markdown"], default="json", help="Output format")
    parser.add_argument(f"{LONG_FLAG}engine", choices=["all", *ALL_ENGINES], default="all", help="Engine view")
    parser.add_argument(f"{LONG_FLAG}output", help="Output file path")
    parser.add_argument(f"{LONG_FLAG}batch", action="store_true", help="Score every markdown or html file in a directory")
    args = parser.parse_args(argv)

    path = Path(args.input)
    if not path.exists():
        print(_json_error(f"File not found: {args.input}"))
        sys.exit(1)

    if path.is_dir():
        if not args.batch:
            print(_json_error(f"Directory input requires batch mode: {args.input}"))
            sys.exit(1)
        result = _process_batch(path, args.engine)
    elif path.is_file():
        result = score_file(path, engine=args.engine)
    else:
        print(_json_error(f"File not found: {args.input}"))
        sys.exit(1)

    if "error" in result:
        print(json.dumps(result, sort_keys=True))
        sys.exit(1)

    if args.format == "markdown":
        _write_or_print(_format_markdown(result), args.output)
    else:
        _write_or_print(json.dumps(result, indent=2, sort_keys=True), args.output)


if __name__ == "__main__":
    main()
