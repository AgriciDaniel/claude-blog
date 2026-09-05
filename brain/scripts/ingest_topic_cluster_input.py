#!/usr/bin/env python3
"""Domain importer: normalize a topic cluster plan input JSON.

The adapter reads ``schemas/topic-cluster-input.schema.json`` shaped data,
validates the hub, spoke, and existing-link fields used by the cluster pipeline,
and emits a deterministic JSON record for internal-link matrix synthesis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


REPO = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO / "schemas" / "topic-cluster-input.schema.json"
LOCALE_RE = re.compile(r"^[a-z]{2,3}(-[A-Z]{2})?$")
WORD_RE = re.compile(r"[A-Za-z0-9]+")
ROOT_KEYS = {
    "cluster_name",
    "primary_topic",
    "locale",
    "audience",
    "objective",
    "hub",
    "spokes",
    "existing_links",
    "entity_terms",
    "source_ids",
}


class ValidationError(ValueError):
    """Raised when a topic cluster input cannot be normalized."""

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
    for key in ("cluster_name", "primary_topic", "locale", "hub", "spokes"):
        if key not in data:
            errors.append(f"missing required key: {key}")
    unexpected = sorted(set(data) - ROOT_KEYS)
    if unexpected:
        errors.append("unexpected keys: " + ", ".join(unexpected))
    for key in ("cluster_name", "primary_topic", "locale", "audience", "objective"):
        if key in data and not is_string(data.get(key)):
            errors.append(f"{key} must be a string")
    if is_string(data.get("locale")) and not LOCALE_RE.match(data["locale"]):
        errors.append("locale must match language or language-region")
    validate_hub(data.get("hub"), errors)
    validate_spokes(data.get("spokes"), errors)
    validate_existing_links(data.get("existing_links", []), errors)
    validate_string_list(data.get("entity_terms", []), errors, "entity_terms")
    validate_string_list(data.get("source_ids", []), errors, "source_ids")
    if errors:
        raise ValidationError(dedupe(errors))


def validate_hub(value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append("hub must be an object")
        return
    unexpected = sorted(set(value) - {"title", "url", "target_keyword"})
    if unexpected:
        errors.append("hub unexpected keys: " + ", ".join(unexpected))
    for key in ("title", "url", "target_keyword"):
        if not is_nonempty_string(value.get(key)):
            errors.append(f"hub.{key} must be a nonempty string")
    if is_nonempty_string(value.get("url")) and not is_http_url(value["url"]):
        errors.append("hub.url must be an HTTP(S) URL")


def validate_spokes(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("spokes must be an array")
        return
    if len(value) < 2:
        errors.append("spokes must include at least two pages")
    seen_ids: set[str] = set()
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            errors.append(f"spokes #{index} must be an object")
            continue
        unexpected = sorted(set(item) - {"id", "title", "url", "target_keyword", "intent", "stage", "priority", "source_ids"})
        if unexpected:
            errors.append(f"spokes #{index} unexpected keys: " + ", ".join(unexpected))
        for key in ("id", "title", "url", "target_keyword", "intent"):
            if not is_nonempty_string(item.get(key)):
                errors.append(f"spokes #{index}.{key} must be a nonempty string")
        if is_nonempty_string(item.get("id")):
            if item["id"] in seen_ids:
                errors.append(f"spokes #{index}.id must be unique")
            seen_ids.add(item["id"])
        if is_nonempty_string(item.get("url")) and not is_http_url(item["url"]):
            errors.append(f"spokes #{index}.url must be an HTTP(S) URL")
        if "stage" in item and not is_string(item.get("stage")):
            errors.append(f"spokes #{index}.stage must be a string")
        if item.get("priority") not in {"critical", "high", "medium", "low", None}:
            errors.append(f"spokes #{index}.priority is invalid")
        validate_string_list(item.get("source_ids", []), errors, f"spokes #{index}.source_ids")


def validate_existing_links(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("existing_links must be an array")
        return
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            errors.append(f"existing_links #{index} must be an object")
            continue
        unexpected = sorted(set(item) - {"from_url", "to_url", "anchor"})
        if unexpected:
            errors.append(f"existing_links #{index} unexpected keys: " + ", ".join(unexpected))
        for key in ("from_url", "to_url"):
            if not is_nonempty_string(item.get(key)):
                errors.append(f"existing_links #{index}.{key} must be a nonempty string")
            elif not is_http_url(item[key]):
                errors.append(f"existing_links #{index}.{key} must be an HTTP(S) URL")
        if "anchor" in item and not is_string(item.get("anchor")):
            errors.append(f"existing_links #{index}.anchor must be a string")


def validate_string_list(value: Any, errors: list[str], path: str) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{path} must be an array of strings")


def is_string(value: Any) -> bool:
    return isinstance(value, str)


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def dedupe(errors: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for error in errors:
        if error not in seen:
            result.append(error)
            seen.add(error)
    return result


def normalize_url(value: str) -> str:
    parsed = urlparse(value.strip())
    path = parsed.path.rstrip("/") or "/"
    return parsed._replace(path=path, fragment="").geturl()


def normalize_text(value: Any) -> str:
    return " ".join(str(value).split())


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


def normalize_page(page_id: str, page: dict[str, Any], role: str) -> dict[str, Any]:
    return {
        "id": page_id,
        "role": role,
        "title": normalize_text(page["title"]),
        "url": normalize_url(page["url"]),
        "target_keyword": normalize_text(page["target_keyword"]),
        "intent": normalize_text(page.get("intent", "")),
        "stage": normalize_text(page.get("stage", "")),
        "priority": page.get("priority", "medium") or "medium",
        "source_ids": normalize_terms(page.get("source_ids", []) or []),
    }


def normalize_links(links: list[dict[str, Any]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for link in links:
        item = {
            "from_url": normalize_url(link["from_url"]),
            "to_url": normalize_url(link["to_url"]),
            "anchor": normalize_text(link.get("anchor", "")),
        }
        key = (item["from_url"], item["to_url"], item["anchor"].lower())
        if key not in seen:
            normalized.append(item)
            seen.add(key)
    return sorted(normalized, key=lambda item: (item["from_url"], item["to_url"], item["anchor"].lower()))


def duplicate_keywords(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[str]] = {}
    for page in pages:
        key = " ".join(token.lower() for token in WORD_RE.findall(page["target_keyword"]))
        groups.setdefault(key, []).append(page["id"])
    return [
        {"target_keyword": key, "page_ids": ids}
        for key, ids in sorted(groups.items())
        if key and len(ids) > 1
    ]


def link_signals(hub: dict[str, Any], spokes: list[dict[str, Any]], links: list[dict[str, str]]) -> dict[str, Any]:
    hub_url = hub["url"]
    edges = {(link["from_url"], link["to_url"]) for link in links}
    orphan_spokes = [
        spoke["id"]
        for spoke in spokes
        if (hub_url, spoke["url"]) not in edges and (spoke["url"], hub_url) not in edges
    ]
    return {
        "spoke_count": len(spokes),
        "existing_link_count": len(links),
        "hub_outbound_count": sum(1 for link in links if link["from_url"] == hub_url),
        "hub_inbound_count": sum(1 for link in links if link["to_url"] == hub_url),
        "orphan_spoke_ids": orphan_spokes,
        "duplicate_target_keywords": duplicate_keywords([hub, *spokes]),
    }


def normalize_topic_cluster(data: dict[str, Any], *, source_name: str, raw_bytes: bytes) -> dict[str, Any]:
    validate_input(data)
    hub = normalize_page("hub", data["hub"], "hub")
    spokes = sorted(
        [normalize_page(item["id"], item, "spoke") for item in data["spokes"]],
        key=lambda item: item["id"],
    )
    links = normalize_links(data.get("existing_links", []) or [])
    entity_terms = normalize_terms(data.get("entity_terms", []) or [])
    source_ids = normalize_terms(data.get("source_ids", []) or [])
    for page in spokes:
        source_ids = normalize_terms([*source_ids, *page.get("source_ids", [])])
    return {
        "schema": "claude-blog-brain.ingested-topic-cluster.v1",
        "adapter": "ingest_topic_cluster_input",
        "input": {
            "cluster_name": normalize_text(data["cluster_name"]),
            "primary_topic": normalize_text(data["primary_topic"]),
            "locale": normalize_text(data["locale"]),
            "audience": normalize_text(data.get("audience", "")),
            "objective": normalize_text(data.get("objective", "")),
        },
        "provenance": {
            "input_name": Path(source_name).name,
            "input_sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "schema_path": "schemas/topic-cluster-input.schema.json",
            "schema_id": load_schema_id(),
            "page_count": len(spokes) + 1,
        },
        "hub": hub,
        "spokes": spokes,
        "existing_links": links,
        "entity_terms": entity_terms,
        "source_ids": source_ids,
        "signals": link_signals(hub, spokes, links),
    }


def load_topic_cluster_input(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    raw = source.read_bytes()
    return normalize_topic_cluster(read_json(source), source_name=source.name, raw_bytes=raw)


def write_json(payload: dict[str, Any], output: str | Path | None = None) -> None:
    text = json.dumps(clean_structure(payload), indent=2, sort_keys=True) + "\n"
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize a topic cluster plan input JSON.")
    parser.add_argument("input")
    parser.add_argument("-o", "--output", default="")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable status when writing to a file.")
    args = parser.parse_args(argv)
    try:
        payload = load_topic_cluster_input(args.input)
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
