#!/usr/bin/env python3
"""Domain synthesis: convert an ingested GEO audit into citation readiness JSON.

The adapter emits deterministic readiness checks, prioritized recommendations,
and source citations from ``references/source-ledger.json``.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from ingest_geo_citation_audit import ValidationError, clean_output_text, clean_structure, write_json


REPO = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = REPO / "references" / "source-ledger.json"
STOPWORDS = {"a", "an", "and", "are", "for", "from", "how", "in", "of", "on", "or", "the", "to", "with"}
PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


class SourceError(ValueError):
    """Raised when a GEO readiness plan references an unknown source ID."""


def load_ingested(path: str | Path) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError([f"invalid JSON at line {exc.lineno}, column {exc.colno}"]) from exc
    if not isinstance(data, dict):
        raise ValidationError(["ingested GEO audit root must be an object"])
    cleaned = clean_structure(data)
    validate_ingested(cleaned)
    return cleaned


def validate_ingested(record: dict[str, Any]) -> None:
    errors: list[str] = []
    if record.get("schema") != "claude-blog-brain.ingested-geo-citation-audit.v1":
        errors.append("ingested GEO audit schema is not supported")
    for key in ("adapter", "input", "provenance", "page_signals", "passages", "signals"):
        if key not in record:
            errors.append(f"ingested GEO audit missing key: {key}")
    if isinstance(record.get("input"), dict):
        for key in ("audit_name", "url", "title", "locale"):
            require_string(record["input"], key, errors, f"input.{key}")
        if not isinstance(record["input"].get("target_queries"), list):
            errors.append("input.target_queries must be a list")
    else:
        errors.append("input must be an object")
    if not isinstance(record.get("passages"), list) or not record.get("passages"):
        errors.append("passages must be a nonempty list")
    if isinstance(record.get("page_signals"), dict):
        for key in ("has_article_schema", "indexable", "preview_allowed", "has_visible_author", "has_modified_date"):
            if not isinstance(record["page_signals"].get(key), bool):
                errors.append(f"page_signals.{key} must be a boolean")
    else:
        errors.append("page_signals must be an object")
    if errors:
        raise ValidationError(dedupe(errors))


def require_string(data: dict[str, Any], key: str, errors: list[str], path: str) -> None:
    if not isinstance(data.get(key), str) or not data.get(key, "").strip():
        errors.append(f"{path} must be a nonempty string")


def dedupe(errors: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for error in errors:
        if error not in seen:
            result.append(error)
            seen.add(error)
    return result


def load_source_index(path: str | Path = DEFAULT_LEDGER) -> dict[str, dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    sources = data.get("sources", [])
    if not isinstance(sources, list):
        raise SourceError("source ledger sources must be a list")
    return {source["id"]: source for source in sources if isinstance(source, dict) and "id" in source}


def synthesize(record: dict[str, Any], *, ledger_path: str | Path = DEFAULT_LEDGER) -> dict[str, Any]:
    record = clean_structure(record)
    validate_ingested(record)
    source_index = load_source_index(ledger_path)
    metrics = build_metrics(record)
    checks = build_checks(record, metrics)
    recommendations = build_recommendations(record, checks)
    source_ids = collect_source_ids(checks, recommendations)
    citations = source_citations(source_ids, source_index)
    plan = {
        "schema": "claude-blog-brain.geo-citation-readiness.v1",
        "adapter": "synthesize_geo_citation_readiness",
        "input": record["input"],
        "provenance": record["provenance"],
        "metrics": metrics,
        "readiness_score": round(sum(item["score"] for item in checks) / len(checks)),
        "checks": checks,
        "recommendations": recommendations,
        "source_citations": citations,
    }
    return clean_structure(plan)


def build_metrics(record: dict[str, Any]) -> dict[str, Any]:
    passages = record["passages"]
    passage_count = max(1, len(passages))
    extractable = sum(1 for passage in passages if passage.get("extractable"))
    cited = sum(1 for passage in passages if int(passage.get("citation_count", 0)) > 0)
    query_terms = [term for query in record["input"].get("target_queries", []) for term in meaningful_terms(query)]
    body_terms = text_term_set(" ".join(passage.get("text", "") for passage in passages))
    entity_terms = text_term_set(" ".join(record.get("entities", [])))
    covered_terms = sorted({term for term in query_terms if term in body_terms or term in entity_terms})
    return {
        "passage_count": len(passages),
        "extractable_passage_count": extractable,
        "extractable_passage_ratio": round(extractable / passage_count, 2),
        "cited_passage_count": cited,
        "cited_passage_ratio": round(cited / passage_count, 2),
        "target_query_term_count": len(set(query_terms)),
        "covered_query_term_count": len(covered_terms),
        "covered_query_terms": covered_terms,
        "entity_count": len(record.get("entities", [])),
    }


def meaningful_terms(value: str) -> list[str]:
    return [term for term in re.findall(r"[a-z0-9]+", value.lower()) if len(term) > 2 and term not in STOPWORDS]


def text_term_set(value: str) -> set[str]:
    terms: set[str] = set()
    for term in meaningful_terms(value):
        terms.add(term)
        if len(term) > 3 and term.endswith("s"):
            terms.add(term[:-1])
    return terms


def build_checks(record: dict[str, Any], metrics: dict[str, Any]) -> list[dict[str, Any]]:
    signals = record["page_signals"]
    entity_score = 100 if metrics["target_query_term_count"] and metrics["covered_query_term_count"] >= metrics["target_query_term_count"] else 65
    crawl_ok = signals["indexable"] and signals["preview_allowed"]
    return [
        check(
            "Passage extractability",
            round(metrics["extractable_passage_ratio"] * 100),
            f"{metrics['extractable_passage_count']} of {metrics['passage_count']} passages are compact, answer-shaped, and punctuation-closed.",
            "Rewrite weak passages as concise answer blocks under descriptive headings.",
            ["ziptie-aio-source-selection", "g-ai-features"],
        ),
        check(
            "Visible citation support",
            round(metrics["cited_passage_ratio"] * 100),
            f"{metrics['cited_passage_count']} of {metrics['passage_count']} passages include visible source citations.",
            "Attach dated, visible citations to extractable factual claims.",
            ["ziptie-aio-source-selection", "g-helpful-content"],
        ),
        check(
            "Entity clarity",
            entity_score,
            f"{metrics['covered_query_term_count']} of {metrics['target_query_term_count']} target query terms are represented in passages or entity fields.",
            "Clarify product, topic, and audience entities in headings, answer blocks, and evidence context.",
            ["ziptie-aio-source-selection", "g-nlp"],
        ),
        check(
            "Schema and crawl eligibility",
            100 if signals["has_article_schema"] and crawl_ok else 55,
            "Article schema, indexability, and preview controls are all ready." if signals["has_article_schema"] and crawl_ok else "Article schema, indexability, or preview controls need review.",
            "Use standard crawl and preview controls with Article or BlogPosting schema where it matches visible page content.",
            ["g-ai-features", "g-intro-sd"],
        ),
        check(
            "Measurement readiness",
            80 if signals["has_modified_date"] else 60,
            "Modified date is present for review tracking." if signals["has_modified_date"] else "Modified date is missing from the supplied page signals.",
            "Monitor AI Overview and AI Mode impressions in Search Console where that reporting is available.",
            ["g-genai-reports"],
        ),
    ]


def check(name: str, score: int, finding: str, recommendation_text: str, source_ids: list[str]) -> dict[str, Any]:
    return {
        "name": name,
        "score": max(0, min(100, score)),
        "status": status_for_score(score),
        "finding": finding,
        "recommendation": recommendation_text,
        "source_ids": source_ids,
    }


def status_for_score(score: int) -> str:
    if score >= 85:
        return "pass"
    if score >= 70:
        return "watch"
    if score >= 50:
        return "revise"
    return "hold"


def build_recommendations(record: dict[str, Any], checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    recs: list[dict[str, Any]] = []
    for item in checks:
        if item["status"] in {"hold", "revise"}:
            recs.append(
                recommendation(
                    "geo-" + slugify(item["name"]),
                    "high" if item["status"] == "hold" else "medium",
                    item["recommendation"],
                    item["source_ids"],
                )
            )
    strategy = record["input"].get("llms_txt_strategy", "unknown")
    if strategy in {"present", "planned"}:
        recs.append(
            recommendation(
                "geo-llms-txt-caveat",
                "high",
                "Do not treat llms.txt as a Google Search, AI Overview, or AI Mode visibility tactic.",
                ["g-ai-opt-guide"],
            )
        )
    recs.append(
        recommendation(
            "geo-separate-ai-mode",
            "medium",
            "Track AI Mode separately from classic organic results and AI Overviews because it is a distinct citation surface.",
            ["blog-aimode", "semrush-ai-mode-comparison"],
        )
    )
    recs.append(
        recommendation(
            "geo-no-guarantee",
            "medium",
            "Treat citation readiness as evidence hygiene, not as a promise of AI Overview, AI Mode, or assistant citation.",
            ["g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice", "g-ai-opt-guide"],
        )
    )
    unique: dict[str, dict[str, Any]] = {}
    for item in recs:
        unique.setdefault(item["id"], item)
    return sorted(unique.values(), key=lambda item: (PRIORITY_ORDER[item["priority"]], item["id"]))


def recommendation(rec_id: str, priority: str, text: str, source_ids: list[str]) -> dict[str, Any]:
    return {
        "id": rec_id,
        "priority": priority,
        "recommendation": text,
        "source_ids": source_ids,
        "rollback_note": "Revert the recommendation if source guidance changes or the page evidence no longer matches.",
    }


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def collect_source_ids(*sections: Any) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if isinstance(value.get("source_ids"), list):
                for source_id in value["source_ids"]:
                    if source_id not in seen:
                        found.append(source_id)
                        seen.add(source_id)
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    for section in sections:
        visit(section)
    return found


def source_citations(source_ids: list[str], source_index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    missing = [source_id for source_id in source_ids if source_id not in source_index]
    if missing:
        raise SourceError("unknown source IDs: " + ", ".join(missing))
    citations: list[dict[str, Any]] = []
    for source_id in source_ids:
        source = source_index[source_id]
        citations.append(
            {
                "id": source_id,
                "title": source.get("title", ""),
                "url": source.get("url", ""),
                "published": source.get("published", source.get("last_updated", "")),
                "retrieved": source.get("retrieved", ""),
                "confidence": source.get("confidence", ""),
            }
        )
    return citations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synthesize a GEO citation readiness JSON report.")
    parser.add_argument("input")
    parser.add_argument("-l", "--ledger", default=str(DEFAULT_LEDGER))
    parser.add_argument("-o", "--output", default="")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable status when writing to a file.")
    args = parser.parse_args(argv)
    try:
        payload = synthesize(load_ingested(args.input), ledger_path=args.ledger)
        write_json(payload, args.output or None)
        if args.output and args.json:
            write_json({"ok": True, "output": str(args.output)}, None)
    except (OSError, ValidationError, SourceError, json.JSONDecodeError) as exc:
        errors = exc.errors if isinstance(exc, ValidationError) else [clean_output_text(str(exc))]
        if args.json:
            write_json({"ok": False, "errors": errors}, None)
        else:
            print(clean_output_text("error: " + "; ".join(errors)), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
