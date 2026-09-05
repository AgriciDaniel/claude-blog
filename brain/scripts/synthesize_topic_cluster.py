#!/usr/bin/env python3
"""Domain synthesis: convert an ingested topic cluster into a link matrix plan.

The adapter emits deterministic JSON with a hub and spoke internal-link matrix,
cluster quality signals, prioritized recommendations, and source citations from
``references/source-ledger.json``.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from ingest_topic_cluster_input import ValidationError, clean_output_text, clean_structure, write_json


REPO = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = REPO / "references" / "source-ledger.json"
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "from",
    "how",
    "in",
    "into",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}
PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


class SourceError(ValueError):
    """Raised when a topic cluster plan references an unknown source ID."""


def load_ingested(path: str | Path) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError([f"invalid JSON at line {exc.lineno}, column {exc.colno}"]) from exc
    if not isinstance(data, dict):
        raise ValidationError(["ingested topic cluster root must be an object"])
    cleaned = clean_structure(data)
    validate_ingested(cleaned)
    return cleaned


def validate_ingested(record: dict[str, Any]) -> None:
    errors: list[str] = []
    if record.get("schema") != "claude-blog-brain.ingested-topic-cluster.v1":
        errors.append("ingested topic cluster schema is not supported")
    for key in ("adapter", "input", "provenance", "hub", "spokes", "existing_links", "signals"):
        if key not in record:
            errors.append(f"ingested topic cluster missing key: {key}")
    if isinstance(record.get("input"), dict):
        for key in ("cluster_name", "primary_topic", "locale"):
            require_string(record["input"], key, errors, f"input.{key}")
    else:
        errors.append("input must be an object")
    if isinstance(record.get("hub"), dict):
        validate_page(record["hub"], errors, "hub")
    else:
        errors.append("hub must be an object")
    if isinstance(record.get("spokes"), list):
        if len(record["spokes"]) < 2:
            errors.append("spokes must include at least two pages")
        for index, spoke in enumerate(record["spokes"], start=1):
            validate_page(spoke, errors, f"spokes #{index}")
    else:
        errors.append("spokes must be a list")
    if not isinstance(record.get("existing_links"), list):
        errors.append("existing_links must be a list")
    if errors:
        raise ValidationError(dedupe(errors))


def validate_page(page: Any, errors: list[str], path: str) -> None:
    if not isinstance(page, dict):
        errors.append(f"{path} must be an object")
        return
    for key in ("id", "role", "title", "url", "target_keyword"):
        require_string(page, key, errors, f"{path}.{key}")


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
    matrix = build_link_matrix(record)
    recommendations = build_recommendations(record, matrix)
    scorecard = build_scorecard(record, matrix)
    source_ids = collect_source_ids(matrix, recommendations, scorecard)
    citations = source_citations(source_ids, source_index)
    plan = {
        "schema": "claude-blog-brain.topic-cluster-plan.v1",
        "adapter": "synthesize_topic_cluster",
        "input": record["input"],
        "provenance": record["provenance"],
        "cluster_quality": scorecard,
        "internal_link_matrix": matrix,
        "recommendations": recommendations,
        "source_citations": citations,
    }
    return clean_structure(plan)


def build_link_matrix(record: dict[str, Any]) -> list[dict[str, Any]]:
    hub = record["hub"]
    spokes = record["spokes"]
    existing = {(link.get("from_url", ""), link.get("to_url", "")) for link in record.get("existing_links", [])}
    rows: list[dict[str, Any]] = []
    for spoke in spokes:
        rows.append(matrix_row(hub, spoke, spoke["target_keyword"], "hub to spoke", (hub["url"], spoke["url"]) in existing))
        rows.append(matrix_row(spoke, hub, record["input"]["primary_topic"], "spoke to hub", (spoke["url"], hub["url"]) in existing))
    for source in spokes:
        for target in spokes:
            if source["id"] == target["id"]:
                continue
            overlap = shared_term_count(source, target)
            if overlap >= 2:
                rows.append(
                    matrix_row(
                        source,
                        target,
                        target["target_keyword"],
                        f"spoke support overlap {overlap}",
                        (source["url"], target["url"]) in existing,
                        priority="medium",
                    )
                )
    unique: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (row["from_url"], row["to_url"], row["relationship"])
        unique.setdefault(key, row)
    return sorted(unique.values(), key=lambda item: (item["from_id"], item["to_id"], item["relationship"]))


def matrix_row(
    source: dict[str, Any],
    target: dict[str, Any],
    anchor: str,
    relationship: str,
    exists: bool,
    *,
    priority: str = "high",
) -> dict[str, Any]:
    return {
        "from_id": source["id"],
        "from_title": source["title"],
        "from_url": source["url"],
        "to_id": target["id"],
        "to_title": target["title"],
        "to_url": target["url"],
        "anchor": anchor,
        "relationship": relationship,
        "status": "present" if exists else "missing",
        "priority": "low" if exists else priority,
        "source_ids": ["dfs-labs", "g-helpful-content"],
    }


def shared_term_count(left: dict[str, Any], right: dict[str, Any]) -> int:
    left_terms = terms_for_page(left)
    right_terms = terms_for_page(right)
    return len(left_terms & right_terms)


def terms_for_page(page: dict[str, Any]) -> set[str]:
    value = " ".join(str(page.get(key, "")) for key in ("title", "target_keyword", "intent", "stage"))
    return {token for token in re.findall(r"[a-z0-9]+", value.lower()) if len(token) > 2 and token not in STOPWORDS}


def build_recommendations(record: dict[str, Any], matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    recs: list[dict[str, Any]] = []
    missing_hub = [row for row in matrix if row["relationship"] == "hub to spoke" and row["status"] == "missing"]
    missing_spoke = [row for row in matrix if row["relationship"] == "spoke to hub" and row["status"] == "missing"]
    if missing_hub:
        recs.append(
            recommendation(
                "cluster-add-hub-to-spoke-links",
                "high",
                "Add hub links to every spoke so the cluster page routes readers into each specific intent path.",
                ["dfs-labs", "g-helpful-content"],
            )
        )
    if missing_spoke:
        recs.append(
            recommendation(
                "cluster-add-spoke-to-hub-links",
                "high",
                "Add spoke links back to the hub so each specific article reinforces the primary topic page.",
                ["dfs-labs", "g-helpful-content"],
            )
        )
    duplicates = record.get("signals", {}).get("duplicate_target_keywords", [])
    if duplicates:
        recs.append(
            recommendation(
                "cluster-resolve-duplicate-intent",
                "high",
                "Separate duplicate target keywords by intent, consolidate overlapping pages, or assign one canonical hub path.",
                ["dfs-labs", "g-helpful-content"],
            )
        )
    if not record.get("entity_terms"):
        recs.append(
            recommendation(
                "cluster-add-entity-map",
                "medium",
                "Add tracked entity terms so the cluster can be reviewed for topical coverage beyond exact keywords.",
                ["g-nlp", "g-helpful-content"],
            )
        )
    if any(row["status"] == "missing" and row["relationship"].startswith("spoke support") for row in matrix):
        recs.append(
            recommendation(
                "cluster-add-supporting-spoke-links",
                "medium",
                "Add supporting links between overlapping spokes when the link helps readers continue the same task.",
                ["dfs-labs", "g-helpful-content"],
            )
        )
    recs.append(
        recommendation(
            "cluster-measure-query-overlap",
            "medium",
            "Measure query and page performance by URL before treating the cluster map as validated.",
            ["g-gsc-api", "dfs-labs"],
        )
    )
    return sorted(recs, key=lambda item: (PRIORITY_ORDER[item["priority"]], item["id"]))


def recommendation(rec_id: str, priority: str, text: str, source_ids: list[str]) -> dict[str, Any]:
    return {
        "id": rec_id,
        "priority": priority,
        "recommendation": text,
        "source_ids": source_ids,
        "rollback_note": "Remove or revise the link if it does not help readers continue the task.",
    }


def build_scorecard(record: dict[str, Any], matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    missing = sum(1 for row in matrix if row["status"] == "missing")
    total = max(1, len(matrix))
    coverage = round(((total - missing) / total) * 100)
    orphan_count = len(record.get("signals", {}).get("orphan_spoke_ids", []))
    duplicate_count = len(record.get("signals", {}).get("duplicate_target_keywords", []))
    return [
        {
            "name": "Internal link coverage",
            "score": coverage,
            "finding": f"{total - missing} of {total} recommended links are already present.",
            "source_ids": ["dfs-labs", "g-helpful-content"],
        },
        {
            "name": "Orphan spoke risk",
            "score": max(0, 100 - orphan_count * 25),
            "finding": f"{orphan_count} spokes have no hub relationship in the supplied links.",
            "source_ids": ["g-helpful-content"],
        },
        {
            "name": "Intent separation",
            "score": 100 if duplicate_count == 0 else 60,
            "finding": f"{duplicate_count} duplicate target keyword groups were detected.",
            "source_ids": ["dfs-labs", "g-helpful-content"],
        },
    ]


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
    parser = argparse.ArgumentParser(description="Synthesize a topic cluster internal-link matrix JSON.")
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
