#!/usr/bin/env python3
"""
AI Citation Probability Scoring.

Usage:
    python3 ai_citation_score.py FILE
    python3 ai_citation_score.py FILE with format json or markdown
    python3 ai_citation_score.py FILE with engine all, ai_overview, perplexity, or chatgpt
    python3 ai_citation_score.py DIR in batch mode

Scoring model:
    Each engine receives a 0-100 probability score from signals produced by
    analyze_blog.analyze_file. Google AI Overview weights passage extractability,
    answer-first structure, entity clarity, schema, freshness, and clean headings.
    Perplexity weights source citations, tier 1 and tier 2 authority, sourced
    statistics, freshness, and citation diversity. ChatGPT weights clean structure,
    TLDR, Q&A pairs, entity definitions, extractable lists or tables, and
    readability. Overall score is a weighted blend: ai_overview 40 percent,
    perplexity 35 percent, and chatgpt 25 percent.
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
    freshness = analysis.get("freshness", {})
    paragraphs = analysis.get("paragraphs", {})

    citable_passages = _to_int(ai_ready.get("citable_passages"))
    passage_points = _count_points(citable_passages, [(1, 12), (2, 20), (3, 26), (4, 30)])

    qa_pairs = _to_int(ai_ready.get("qa_pairs"))
    question_ratio = _to_float(headings.get("h2_question_ratio"))
    answer_points = min(12, qa_pairs * 4)
    answer_points += min(5, int(round(question_ratio * 5)))
    if ai_ready.get("has_tldr"):
        answer_points += 3
    answer_points = min(20, answer_points)

    entity_definitions = _to_int(ai_ready.get("entity_definitions"))
    entity_points = _count_points(entity_definitions, [(1, 7), (2, 12), (3, 15)])

    schema_points = 0
    if schema.get("has_blogposting"):
        schema_points += 12
    elif _to_int(schema.get("schema_count")) > 0:
        schema_points += 5
    if schema.get("has_person"):
        schema_points += 2
    if schema.get("has_faqpage"):
        schema_points += 1
    schema_points = min(15, schema_points)

    freshness_points = 0
    if freshness.get("has_last_updated"):
        freshness_points += 7
    if freshness.get("has_date"):
        freshness_points += 3

    h2_count = _to_int(headings.get("h2_count"))
    heading_points = 0
    if headings.get("hierarchy_clean"):
        heading_points += 4
    heading_points += _count_points(h2_count, [(1, 2), (3, 4)])
    if _to_int(paragraphs.get("max_word_count")) <= 180 and _to_int(paragraphs.get("total_paragraphs")) > 0:
        heading_points += 2
    heading_points = min(10, heading_points)

    factors = {
        "passage_extractability": _factor(
            passage_points,
            30,
            {
                "citable_passages_120_to_180_words": citable_passages,
                "target": "self-contained 130-170 word passages",
            },
        ),
        "answer_first_structure": _factor(
            answer_points,
            20,
            {
                "qa_pairs": qa_pairs,
                "h2_question_ratio": question_ratio,
                "has_tldr": bool(ai_ready.get("has_tldr")),
            },
        ),
        "entity_clarity": _factor(
            entity_points,
            15,
            {"entity_definitions": entity_definitions},
        ),
        "article_schema": _factor(
            schema_points,
            15,
            {
                "has_blogposting_or_article": bool(schema.get("has_blogposting")),
                "has_person": bool(schema.get("has_person")),
                "has_faqpage": bool(schema.get("has_faqpage")),
            },
        ),
        "freshness": _factor(
            freshness_points,
            10,
            {
                "has_date": bool(freshness.get("has_date")),
                "has_last_updated": bool(freshness.get("has_last_updated")),
            },
        ),
        "clean_headings": _factor(
            heading_points,
            10,
            {
                "h2_count": h2_count,
                "hierarchy_clean": bool(headings.get("hierarchy_clean")),
                "max_paragraph_words": _to_int(paragraphs.get("max_word_count")),
            },
        ),
    }

    score = sum(factor["points"] for factor in factors.values())
    return {"score": _clamp_score(score), "factors": factors}


def _score_perplexity(analysis: dict[str, Any]) -> dict[str, Any]:
    citations = analysis.get("citations", {})
    freshness = analysis.get("freshness", {})

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
    statistic_points = _count_points(sourced_statistics, [(1, 7), (2, 12), (3, 16), (4, 20)])
    statistic_points = max(0, statistic_points - min(6, unsourced_statistics * 2))

    freshness_points = 0
    if freshness.get("has_last_updated"):
        freshness_points += 10
    if freshness.get("has_date"):
        freshness_points += 5

    unique_sources = _to_int(citations.get("unique_sources"))
    diversity_points = _count_points(unique_sources, [(1, 3), (2, 6), (3, 10)])

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
            20,
            {
                "sourced_statistics": sourced_statistics,
                "unsourced_statistics": unsourced_statistics,
            },
        ),
        "recency_freshness": _factor(
            freshness_points,
            15,
            {
                "has_date": bool(freshness.get("has_date")),
                "has_last_updated": bool(freshness.get("has_last_updated")),
            },
        ),
        "citation_diversity": _factor(
            diversity_points,
            10,
            {"unique_sources": unique_sources},
        ),
    }

    score = sum(factor["points"] for factor in factors.values())
    return {"score": _clamp_score(score), "factors": factors}


def _score_chatgpt(analysis: dict[str, Any]) -> dict[str, Any]:
    ai_ready = analysis.get("ai_citation_readiness", {})
    headings = analysis.get("headings", {})
    paragraphs = analysis.get("paragraphs", {})
    structured_data = analysis.get("structured_data", {})
    readability = analysis.get("readability", {})
    sentences = analysis.get("sentences", {})
    faq = analysis.get("faq", {})

    h2_count = _to_int(headings.get("h2_count"))
    clean_points = _count_points(h2_count, [(1, 3), (3, 8)])
    if headings.get("hierarchy_clean"):
        clean_points += 6
    if _to_int(paragraphs.get("max_word_count")) <= 140 and _to_int(paragraphs.get("total_paragraphs")) > 0:
        clean_points += 5
    if _to_float(paragraphs.get("in_range_ratio")) >= 0.35:
        clean_points += 3
    if _to_int(paragraphs.get("total_word_count")) >= 600:
        clean_points += 3
    clean_points = min(25, clean_points)

    tldr_points = 15 if ai_ready.get("has_tldr") else 0

    qa_pairs = _to_int(ai_ready.get("qa_pairs"))
    faq_items = _to_int(faq.get("faq_item_count"))
    qa_points = min(20, qa_pairs * 5 + faq_items * 2 + (4 if faq.get("has_faq_section") else 0))

    entity_definitions = _to_int(ai_ready.get("entity_definitions"))
    entity_points = _count_points(entity_definitions, [(1, 7), (2, 12), (3, 15)])

    table_count = max(_to_int(ai_ready.get("table_count")), _to_int(structured_data.get("table_count")))
    list_items = (
        _to_int(ai_ready.get("list_count"))
        + _to_int(structured_data.get("unordered_list_items"))
        + _to_int(structured_data.get("ordered_list_items"))
    )
    extract_points = min(15, table_count * 5 + _count_points(list_items, [(3, 4), (6, 7), (10, 10)]))

    flesch = _to_float(readability.get("flesch_reading_ease"))
    avg_sentence = _to_float(sentences.get("avg_length"))
    over_20_pct = _to_float(sentences.get("over_20_pct"))
    readability_points = 0
    if 45 <= flesch <= 80:
        readability_points += 4
    if 10 <= avg_sentence <= 24:
        readability_points += 3
    if over_20_pct <= 25:
        readability_points += 2
    if _to_int(sentences.get("very_long_count")) == 0:
        readability_points += 1

    factors = {
        "clean_structure": _factor(
            clean_points,
            25,
            {
                "h2_count": h2_count,
                "hierarchy_clean": bool(headings.get("hierarchy_clean")),
                "max_paragraph_words": _to_int(paragraphs.get("max_word_count")),
                "word_count": _to_int(paragraphs.get("total_word_count")),
            },
        ),
        "tldr_presence": _factor(
            tldr_points,
            15,
            {"has_tldr": bool(ai_ready.get("has_tldr"))},
        ),
        "qa_pairs": _factor(
            qa_points,
            20,
            {
                "qa_pairs": qa_pairs,
                "faq_item_count": faq_items,
                "has_faq_section": bool(faq.get("has_faq_section")),
            },
        ),
        "entity_definitions": _factor(
            entity_points,
            15,
            {"entity_definitions": entity_definitions},
        ),
        "extractable_lists_tables": _factor(
            extract_points,
            15,
            {"table_count": table_count, "list_items": list_items},
        ),
        "readability": _factor(
            readability_points,
            10,
            {
                "flesch_reading_ease": flesch,
                "avg_sentence_length": avg_sentence,
                "sentences_over_20_pct": over_20_pct,
            },
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
        result["probability"] = result["score"]
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
            "Create three self-contained 130-170 word passages with a 40-60 word direct answer after question H2s.",
            [("ai_overview", "passage_extractability"), ("ai_overview", "answer_first_structure")],
        ),
        (
            "Add BlogPosting or Article JSON-LD with author and dateModified fields.",
            [("ai_overview", "article_schema")],
        ),
        (
            "Source every statistic and add at least three unique tier 1 or tier 2 citations.",
            [
                ("perplexity", "source_citations"),
                ("perplexity", "source_authority"),
                ("perplexity", "sourced_statistics"),
                ("perplexity", "citation_diversity"),
            ],
        ),
        (
            "Refresh the post metadata with date and lastUpdated fields.",
            [("ai_overview", "freshness"), ("perplexity", "recency_freshness")],
        ),
        (
            "Add a TLDR block, Q&A headings, and bold term definitions near the top.",
            [
                ("chatgpt", "tldr_presence"),
                ("chatgpt", "qa_pairs"),
                ("chatgpt", "entity_definitions"),
            ],
        ),
        (
            "Add tables or lists that summarize methods, numbers, and decisions.",
            [("chatgpt", "extractable_lists_tables")],
        ),
        (
            "Tighten headings and paragraph length so sections are easy to scan.",
            [("ai_overview", "clean_headings"), ("chatgpt", "clean_structure")],
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
        "overall_probability": overall,
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
        f"## AI Citation Probability: {file_name}",
        "",
        f"Overall probability: {result.get('overall', 0)}/100",
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
    parser = argparse.ArgumentParser(description="AI citation probability scorer")
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
