#!/usr/bin/env python3
"""Domain importer: normalize a GEO citation audit input JSON.

The adapter reads ``schemas/geo-citation-audit-input.schema.json`` shaped data,
validates passage, citation, and page signal fields, and emits a deterministic
record for AI citation readiness synthesis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


REPO = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO / "schemas" / "geo-citation-audit-input.schema.json"
LOCALE_RE = re.compile(r"^[a-z]{2,3}(-[A-Z]{2})?$")
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")
ROOT_KEYS = {
    "audit_name",
    "url",
    "title",
    "locale",
    "target_queries",
    "passages",
    "page_signals",
    "llms_txt_strategy",
    "source_ids",
}


class ValidationError(ValueError):
    """Raised when a GEO citation audit input cannot be normalized."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


def clean_output_text(value: str) -> str:
    cleaned = value.replace("\u2014", "-").replace("\u2013", "-").replace("\u2212", "-")
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned


def clean_structure(value: Any) -> Any:
    if isinstance(value, str):
        return clean_output_text(value).strip()
    if isinstance(value, list):
        return [clean_structure(item) for item in value]
    if isinstance(value, dict):
        return {str(key): clean_structure(item) for key, item in value.items()}
    return value


def read_json(path: str | Path) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError([f"invalid JSON at line {exc.lineno}, column {exc.colno}"]) from exc
    if not isinstance(data, dict):
        raise ValidationError(["input root must be an object"])
    return clean_structure(data)


def load_schema_id() -> str:
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except OSError:
        return ""
    if isinstance(schema, dict):
        return str(schema.get("$id", ""))
    return ""


def validate_input(data: dict[str, Any]) -> None:
    errors: list[str] = []
    for key in ("audit_name", "url", "title", "locale", "target_queries", "passages", "page_signals"):
        if key not in data:
            errors.append(f"missing required key: {key}")
    unexpected = sorted(set(data) - ROOT_KEYS)
    if unexpected:
        errors.append("unexpected keys: " + ", ".join(unexpected))
    for key in ("audit_name", "url", "title", "locale", "llms_txt_strategy"):
        if key in data and not is_string(data.get(key)):
            errors.append(f"{key} must be a string")
    if is_nonempty_string(data.get("url")) and not is_http_url(data["url"]):
        errors.append("url must be an HTTP(S) URL")
    if is_string(data.get("locale")) and not LOCALE_RE.match(data["locale"]):
        errors.append("locale must match language or language-region")
    if data.get("llms_txt_strategy") not in {"none", "present", "planned", "unknown", None}:
        errors.append("llms_txt_strategy is invalid")
    validate_string_list(data.get("target_queries"), errors, "target_queries", min_items=1)
    validate_passages(data.get("passages"), errors)
    validate_page_signals(data.get("page_signals"), errors)
    validate_string_list(data.get("source_ids", []), errors, "source_ids")
    if errors:
        raise ValidationError(dedupe(errors))


def validate_passages(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("passages must be an array")
        return
    if not value:
        errors.append("passages must include at least one passage")
    seen_ids: set[str] = set()
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            errors.append(f"passages #{index} must be an object")
            continue
        unexpected = sorted(set(item) - {"id", "heading", "text", "entities", "citations"})
        if unexpected:
            errors.append(f"passages #{index} unexpected keys: " + ", ".join(unexpected))
        for key in ("id", "heading", "text"):
            if not is_nonempty_string(item.get(key)):
                errors.append(f"passages #{index}.{key} must be a nonempty string")
        if is_nonempty_string(item.get("id")):
            if item["id"] in seen_ids:
                errors.append(f"passages #{index}.id must be unique")
            seen_ids.add(item["id"])
        validate_string_list(item.get("entities", []), errors, f"passages #{index}.entities")
        validate_citations(item.get("citations", []), errors, f"passages #{index}.citations")


def validate_citations(value: Any, errors: list[str], path: str) -> None:
    if not isinstance(value, list):
        errors.append(f"{path} must be an array")
        return
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            errors.append(f"{path} #{index} must be an object")
            continue
        unexpected = sorted(set(item) - {"title", "url", "published", "retrieved"})
        if unexpected:
            errors.append(f"{path} #{index} unexpected keys: " + ", ".join(unexpected))
        for key in ("title", "url", "retrieved"):
            if not is_nonempty_string(item.get(key)):
                errors.append(f"{path} #{index}.{key} must be a nonempty string")
        if is_nonempty_string(item.get("url")) and not is_http_url(item["url"]):
            errors.append(f"{path} #{index}.url must be an HTTP(S) URL")
        for key in ("published", "retrieved"):
            if key in item and is_string(item.get(key)) and item[key] and not is_iso_date(item[key]):
                errors.append(f"{path} #{index}.{key} must be an ISO date")


def validate_page_signals(value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append("page_signals must be an object")
        return
    expected = {"has_article_schema", "indexable", "preview_allowed", "has_visible_author", "has_modified_date"}
    unexpected = sorted(set(value) - expected)
    if unexpected:
        errors.append("page_signals unexpected keys: " + ", ".join(unexpected))
    for key in sorted(expected):
        if key not in value:
            errors.append(f"page_signals.{key} is required")
        elif not isinstance(value[key], bool):
            errors.append(f"page_signals.{key} must be a boolean")


def validate_string_list(value: Any, errors: list[str], path: str, min_items: int = 0) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        errors.append(f"{path} must be an array of nonempty strings")
        return
    if len(value) < min_items:
        errors.append(f"{path} must include at least {min_items} item")


def is_string(value: Any) -> bool:
    return isinstance(value, str)


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def is_iso_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def dedupe(errors: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for error in errors:
        if error not in seen:
            result.append(error)
            seen.add(error)
    return result


def normalize_text(value: Any) -> str:
    return " ".join(str(value).split())


def normalize_url(value: str) -> str:
    parsed = urlparse(value.strip())
    path = parsed.path.rstrip("/") or "/"
    return parsed._replace(path=path, fragment="").geturl()


def normalize_terms(values: list[str]) -> list[str]:
    terms: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned = normalize_text(value)
        key = cleaned.lower()
        if cleaned and key not in seen:
            terms.append(cleaned)
            seen.add(key)
    return terms


def count_words(value: str) -> int:
    return len(WORD_RE.findall(value))


def normalize_citations(items: list[dict[str, Any]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for item in items:
        normalized.append(
            {
                "title": normalize_text(item["title"]),
                "url": normalize_url(item["url"]),
                "published": normalize_text(item.get("published", "")),
                "retrieved": normalize_text(item["retrieved"]),
            }
        )
    return sorted(normalized, key=lambda item: (item["title"].lower(), item["url"]))


def normalize_passage(item: dict[str, Any]) -> dict[str, Any]:
    text = normalize_text(item["text"])
    word_count = count_words(text)
    citations = normalize_citations(item.get("citations", []) or [])
    return {
        "id": normalize_text(item["id"]),
        "heading": normalize_text(item["heading"]),
        "text": text,
        "word_count": word_count,
        "extractable": 12 <= word_count <= 80 and text.endswith((".", "?", "!")),
        "entities": normalize_terms(item.get("entities", []) or []),
        "citations": citations,
        "citation_count": len(citations),
    }


def normalize_geo_audit(data: dict[str, Any], *, source_name: str, raw_bytes: bytes) -> dict[str, Any]:
    validate_input(data)
    passages = sorted([normalize_passage(item) for item in data["passages"]], key=lambda item: item["id"])
    signals = data["page_signals"]
    all_entities = normalize_terms([entity for passage in passages for entity in passage["entities"]])
    return {
        "schema": "claude-blog-brain.ingested-geo-citation-audit.v1",
        "adapter": "ingest_geo_citation_audit",
        "input": {
            "audit_name": normalize_text(data["audit_name"]),
            "url": normalize_url(data["url"]),
            "title": normalize_text(data["title"]),
            "locale": normalize_text(data["locale"]),
            "target_queries": normalize_terms(data["target_queries"]),
            "llms_txt_strategy": normalize_text(data.get("llms_txt_strategy", "unknown") or "unknown"),
        },
        "provenance": {
            "input_name": Path(source_name).name,
            "input_sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "schema_path": "schemas/geo-citation-audit-input.schema.json",
            "schema_id": load_schema_id(),
            "passage_count": len(passages),
        },
        "page_signals": {
            "has_article_schema": bool(signals["has_article_schema"]),
            "indexable": bool(signals["indexable"]),
            "preview_allowed": bool(signals["preview_allowed"]),
            "has_visible_author": bool(signals["has_visible_author"]),
            "has_modified_date": bool(signals["has_modified_date"]),
        },
        "passages": passages,
        "entities": all_entities,
        "source_ids": normalize_terms(data.get("source_ids", []) or []),
        "signals": {
            "passage_count": len(passages),
            "extractable_passage_count": sum(1 for passage in passages if passage["extractable"]),
            "cited_passage_count": sum(1 for passage in passages if passage["citation_count"] > 0),
            "entity_count": len(all_entities),
            "target_query_count": len(data["target_queries"]),
        },
    }


def load_geo_citation_audit(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    raw = source.read_bytes()
    return normalize_geo_audit(read_json(source), source_name=source.name, raw_bytes=raw)


def write_json(payload: dict[str, Any], output: str | Path | None = None) -> None:
    text = json.dumps(clean_structure(payload), indent=2, sort_keys=True) + "\n"
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize a GEO citation audit input JSON.")
    parser.add_argument("input")
    parser.add_argument("-o", "--output", default="")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable status when writing to a file.")
    args = parser.parse_args(argv)
    try:
        payload = load_geo_citation_audit(args.input)
        write_json(payload, args.output or None)
        if args.output and args.json:
            write_json({"ok": True, "output": str(args.output)}, None)
    except (OSError, ValidationError) as exc:
        errors = exc.errors if isinstance(exc, ValidationError) else [clean_output_text(str(exc))]
        if args.json:
            write_json({"ok": False, "errors": errors}, None)
        else:
            print(clean_output_text("error: " + "; ".join(errors)), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
