#!/usr/bin/env python3
"""Domain importer: normalize a blog post input JSON for Claude Blog Brain.

The adapter reads ``schemas/blog-post-input.schema.json`` shaped data, validates
the fields used by the domain pipeline, and emits a deterministic JSON record
with provenance hashes, extracted headings, links, sections, dates, author
signals, and schema hints.
"""
from __future__ import annotations

import argparse
import hashlib
import html.parser
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    from jsonschema import Draft7Validator as JsonSchemaDraft7Validator
    from jsonschema import FormatChecker as JsonSchemaFormatChecker
except ImportError:  # pragma: no cover - exercised when optional dependency is absent.
    JsonSchemaDraft7Validator = None  # type: ignore[assignment]
    JsonSchemaFormatChecker = None  # type: ignore[assignment]


REPO = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO / "schemas" / "blog-post-input.schema.json"
REQUIRED_KEYS = ("title", "url", "target_keyword", "locale")
ALLOWED_KEYS = {
    "title",
    "url",
    "body_markdown",
    "body_html",
    "frontmatter",
    "target_keyword",
    "secondary_keywords",
    "locale",
    "platform",
    "author",
    "published_at",
    "modified_at",
    "sources",
    "audit_findings",
}
LOCALE_RE = re.compile(r"^[a-z]{2,3}(-[A-Z]{2})?$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})?)?$")
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")
MARKDOWN_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
HTML_HEADING_RE = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
HTML_HREF_RE = re.compile(r"""href=["']([^"']+)["']""", re.IGNORECASE)
MD_LINK_RE = re.compile(r"\[[^\]]+\]\((https?://[^)\s]+)\)")
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


class ValidationError(ValueError):
    """Raised when a blog post input cannot be normalized."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


class _HTMLTextExtractor(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
            return
        if tag in {"p", "br", "div", "section", "article", "li", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1
            return
        if tag in {"p", "div", "section", "article", "li", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        return normalize_space("\n".join(self.parts))


def clean_output_text(value: str) -> str:
    cleaned = value.replace("\u2014", "-").replace("\u2013", "-").replace("\u2212", "-")
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned


def clean_structure(value: Any) -> Any:
    if isinstance(value, str):
        return clean_output_text(value)
    if isinstance(value, list):
        return [clean_structure(item) for item in value]
    if isinstance(value, dict):
        return {str(key): clean_structure(item) for key, item in value.items()}
    return value


def normalize_space(value: str) -> str:
    lines = [" ".join(line.split()) for line in clean_output_text(value).splitlines()]
    collapsed: list[str] = []
    last_blank = False
    for line in lines:
        blank = not line
        if blank and last_blank:
            continue
        collapsed.append(line)
        last_blank = blank
    return "\n".join(collapsed).strip()


def read_json(path: str | Path) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError([f"invalid JSON at line {exc.lineno}, column {exc.colno}"]) from exc
    if not isinstance(data, dict):
        raise ValidationError(["input root must be an object"])
    return clean_structure(data)


def load_input_schema() -> dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    if not isinstance(schema, dict):
        raise ValidationError(["blog post input schema root must be an object"])
    return schema


def validate_against_schema(data: dict[str, Any]) -> list[str]:
    schema = load_input_schema()
    if JsonSchemaDraft7Validator is not None:
        format_checker = JsonSchemaFormatChecker() if JsonSchemaFormatChecker is not None else None
        validator = JsonSchemaDraft7Validator(schema, format_checker=format_checker)
        return dedupe_errors(
            [format_schema_error(error) for error in sorted(validator.iter_errors(data), key=schema_error_sort_key)]
        )
    return manual_schema_errors(data, schema)


def schema_error_sort_key(error: Any) -> tuple[str, str]:
    path = ".".join(str(part) for part in error.absolute_path)
    return (path, str(error.message))


def format_schema_error(error: Any) -> str:
    path = ".".join(str(part) for part in error.absolute_path)
    if error.validator == "required" and isinstance(error.instance, dict):
        missing = sorted(set(error.validator_value) - set(error.instance))
        if len(missing) == 1:
            key = f"{path}.{missing[0]}" if path else missing[0]
            return f"missing required key: {key}"
    if error.validator == "anyOf" and not path:
        return "one of body_markdown or body_html is required"
    prefix = f"{path}: " if path else ""
    return prefix + str(error.message)


def manual_schema_errors(data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    properties = schema.get("properties", {})
    for key in schema.get("required", []):
        if key not in data:
            errors.append(f"missing required key: {key}")
    unexpected = sorted(set(data) - set(properties))
    if unexpected:
        errors.append("unexpected keys: " + ", ".join(unexpected))
    if "body_markdown" not in data and "body_html" not in data:
        errors.append("one of body_markdown or body_html is required")

    check_string_fields(data, ("title", "url", "body_markdown", "body_html", "target_keyword", "locale", "platform", "published_at", "modified_at"), errors)
    check_iso_date_fields(data, ("published_at", "modified_at"), errors)
    if "frontmatter" in data:
        if not isinstance(data["frontmatter"], dict):
            errors.append("frontmatter must be an object")
        else:
            check_string_fields(data["frontmatter"], ("description", "author", "date", "dateModified", "category", "coverImage"), errors, "frontmatter")
            check_iso_date_fields(data["frontmatter"], ("date", "dateModified"), errors, "frontmatter")
            if "tags" in data["frontmatter"] and not is_string_list(data["frontmatter"]["tags"]):
                errors.append("frontmatter.tags must be an array of strings")
    if "secondary_keywords" in data and not is_string_list(data["secondary_keywords"]):
        errors.append("secondary_keywords must be an array of strings")
    if "author" in data:
        manual_author_schema_errors(data["author"], errors)
    if "sources" in data:
        manual_sources_schema_errors(data["sources"], errors)
    if "audit_findings" in data:
        manual_audit_finding_schema_errors(data["audit_findings"], errors)
    return dedupe_errors(errors)


def check_string_fields(data: dict[str, Any], fields: tuple[str, ...], errors: list[str], prefix: str = "") -> None:
    for key in fields:
        if key in data and not isinstance(data[key], str):
            path = f"{prefix}.{key}" if prefix else key
            errors.append(f"{path} must be a string")


def check_iso_date_fields(data: dict[str, Any], fields: tuple[str, ...], errors: list[str], prefix: str = "") -> None:
    for key in fields:
        if key in data and isinstance(data[key], str) and data[key] and not is_iso_date_or_datetime(data[key]):
            path = f"{prefix}.{key}" if prefix else key
            errors.append(f"{path} must be an ISO date or date-time")


def manual_author_schema_errors(author: Any, errors: list[str]) -> None:
    if not isinstance(author, dict):
        errors.append("author must be an object")
        return
    check_string_fields(author, ("name", "url", "bio"), errors, "author")
    if "sameAs" in author and not is_string_list(author["sameAs"]):
        errors.append("author.sameAs must be an array of strings")


def manual_sources_schema_errors(sources: Any, errors: list[str]) -> None:
    if not isinstance(sources, list):
        errors.append("sources must be an array")
        return
    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            errors.append(f"sources #{index} must be an object")
            continue
        for key in ("url", "title", "retrieved"):
            if key not in source:
                errors.append(f"sources #{index} missing {key}")
        check_string_fields(source, ("url", "title", "publisher", "published", "retrieved", "confidence"), errors, f"sources #{index}")
        check_iso_date_fields(source, ("published", "retrieved"), errors, f"sources #{index}")
        if "supports_claims" in source and not is_string_list(source["supports_claims"]):
            errors.append(f"sources #{index} supports_claims must be an array of strings")


def manual_audit_finding_schema_errors(findings: Any, errors: list[str]) -> None:
    if not isinstance(findings, list):
        errors.append("audit_findings must be an array")
        return
    for index, finding in enumerate(findings, start=1):
        if not isinstance(finding, dict):
            errors.append(f"audit_findings #{index} must be an object")
            continue
        for key in ("id", "category", "severity", "summary"):
            if key not in finding:
                errors.append(f"audit_findings #{index} missing {key}")
        check_string_fields(finding, ("id", "category", "severity", "summary", "recommendation", "source"), errors, f"audit_findings #{index}")
        if finding.get("severity") not in {"critical", "high", "medium", "low", None}:
            errors.append(f"audit_findings #{index} severity is invalid")


def dedupe_errors(errors: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for error in errors:
        if error not in seen:
            deduped.append(error)
            seen.add(error)
    return deduped


def validate_input(data: dict[str, Any]) -> None:
    errors: list[str] = validate_against_schema(data)
    for key in REQUIRED_KEYS:
        if key not in data:
            errors.append(f"missing required key: {key}")
    unexpected = sorted(set(data) - ALLOWED_KEYS)
    if unexpected:
        errors.append("unexpected keys: " + ", ".join(unexpected))
    body_markdown = data.get("body_markdown")
    body_html = data.get("body_html")
    if not is_nonempty_string(body_markdown) and not is_nonempty_string(body_html):
        errors.append("one of body_markdown or body_html is required")
    for key in ("title", "url", "target_keyword", "locale"):
        if key in data and not is_nonempty_string(data.get(key)):
            errors.append(f"{key} must be a nonempty string")
    if is_nonempty_string(data.get("url")) and not is_uri(data["url"]):
        errors.append("url must be an absolute URI")
    if is_nonempty_string(data.get("locale")) and not LOCALE_RE.match(data["locale"]):
        errors.append("locale must match language or language-region")
    if body_markdown is not None and not is_nonempty_string(body_markdown):
        errors.append("body_markdown must be a nonempty string when present")
    if body_html is not None and not is_nonempty_string(body_html):
        errors.append("body_html must be a nonempty string when present")
    if "frontmatter" in data and not isinstance(data["frontmatter"], dict):
        errors.append("frontmatter must be an object")
    if isinstance(data.get("frontmatter"), dict):
        check_iso_date_fields(data["frontmatter"], ("date", "dateModified"), errors, "frontmatter")
    if "secondary_keywords" in data and not is_string_list(data["secondary_keywords"]):
        errors.append("secondary_keywords must be an array of strings")
    if "platform" in data and not isinstance(data["platform"], str):
        errors.append("platform must be a string")
    if "author" in data:
        validate_author(data["author"], errors)
    if "sources" in data:
        validate_sources(data["sources"], errors)
    if "audit_findings" in data:
        validate_audit_findings(data["audit_findings"], errors)
    check_iso_date_fields(data, ("published_at", "modified_at"), errors)
    if errors:
        raise ValidationError(dedupe_errors(errors))


def validate_author(author: Any, errors: list[str]) -> None:
    if not isinstance(author, dict):
        errors.append("author must be an object")
        return
    for key in ("name", "url", "bio"):
        if key in author and not isinstance(author[key], str):
            errors.append(f"author.{key} must be a string")
    if is_nonempty_string(author.get("url")) and not is_uri(author["url"]):
        errors.append("author.url must be an absolute URI")
    if "sameAs" in author:
        if not is_string_list(author["sameAs"]):
            errors.append("author.sameAs must be an array of URI strings")
        else:
            for item in author["sameAs"]:
                if not is_uri(item):
                    errors.append("author.sameAs entries must be absolute URIs")
                    break


def validate_sources(sources: Any, errors: list[str]) -> None:
    if not isinstance(sources, list):
        errors.append("sources must be an array")
        return
    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            errors.append(f"sources #{index} must be an object")
            continue
        for key in ("url", "title", "retrieved"):
            if not is_nonempty_string(source.get(key)):
                errors.append(f"sources #{index} missing {key}")
        if is_nonempty_string(source.get("url")) and not is_uri(source["url"]):
            errors.append(f"sources #{index} url must be an absolute URI")
        check_iso_date_fields(source, ("published", "retrieved"), errors, f"sources #{index}")
        if "supports_claims" in source and not is_string_list(source["supports_claims"]):
            errors.append(f"sources #{index} supports_claims must be an array of strings")


def validate_audit_findings(findings: Any, errors: list[str]) -> None:
    if not isinstance(findings, list):
        errors.append("audit_findings must be an array")
        return
    for index, finding in enumerate(findings, start=1):
        if not isinstance(finding, dict):
            errors.append(f"audit_findings #{index} must be an object")
            continue
        for key in ("id", "category", "severity", "summary"):
            if not is_nonempty_string(finding.get(key)):
                errors.append(f"audit_findings #{index} missing {key}")
        if finding.get("severity") not in {"critical", "high", "medium", "low", None}:
            errors.append(f"audit_findings #{index} severity is invalid")


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def is_uri(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def is_iso_date_or_datetime(value: str) -> bool:
    if not ISO_DATE_RE.match(value):
        return False
    try:
        if "T" in value or " " in value:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            date.fromisoformat(value)
    except ValueError:
        return False
    return True


def html_to_text(value: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(value)
    parser.close()
    return parser.text()


def strip_tags(value: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(value)
    parser.close()
    return " ".join(parser.text().split())


def extract_headings(data: dict[str, Any], body_format: str) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    if body_format == "markdown":
        for line in data.get("body_markdown", "").splitlines():
            match = MARKDOWN_HEADING_RE.match(line)
            if match:
                headings.append({"level": len(match.group(1)), "text": normalize_space(match.group(2))})
    else:
        for match in HTML_HEADING_RE.finditer(data.get("body_html", "")):
            headings.append({"level": int(match.group(1)), "text": normalize_space(strip_tags(match.group(2)))})
    return [heading for heading in headings if heading["text"]]


def extract_markdown_sections(markdown: str) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in markdown.splitlines():
        match = MARKDOWN_HEADING_RE.match(line)
        if match and len(match.group(1)) == 2:
            if current:
                sections.append(finalize_section(current))
            current = {"heading": normalize_space(match.group(2)), "lines": []}
            continue
        if current is not None:
            current["lines"].append(line)
    if current:
        sections.append(finalize_section(current))
    return sections


def finalize_section(section: dict[str, Any]) -> dict[str, Any]:
    body = normalize_space("\n".join(section["lines"]))
    paragraphs = [part.strip() for part in body.split("\n") if part.strip() and not part.startswith("#")]
    opening = paragraphs[0] if paragraphs else ""
    return {
        "heading": section["heading"],
        "opening": opening,
        "word_count": count_words(body),
    }


def extract_links(data: dict[str, Any]) -> list[str]:
    candidates: list[str] = []
    candidates.extend(match.group(1) for match in MD_LINK_RE.finditer(data.get("body_markdown", "")))
    candidates.extend(match.group(1) for match in HTML_HREF_RE.finditer(data.get("body_html", "")))
    links: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        cleaned = clean_output_text(item).strip()
        if cleaned and cleaned not in seen:
            links.append(cleaned)
            seen.add(cleaned)
    return links


def count_words(value: str) -> int:
    return len(WORD_RE.findall(value))


def has_direct_answer(value: str, target_keyword: str) -> bool:
    first = first_paragraph(value).lower()
    target_terms = [term for term in re.split(r"\s+", target_keyword.lower()) if len(term) > 2]
    return 35 <= len(first) <= 420 and any(term in first for term in target_terms)


def first_paragraph(value: str) -> str:
    for part in re.split(r"\n\s*\n|\n", value):
        cleaned = part.strip()
        if cleaned and not cleaned.startswith("#"):
            return cleaned
    return ""


def has_any(value: str, needles: tuple[str, ...]) -> bool:
    lower = value.lower()
    return any(needle in lower for needle in needles)


def normalize_audit_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        findings,
        key=lambda item: (
            SEVERITY_ORDER.get(item.get("severity", "low"), 9),
            item.get("category", ""),
            item.get("id", ""),
        ),
    )


def normalize_blog_input(data: dict[str, Any], *, source_name: str, raw_bytes: bytes | None = None) -> dict[str, Any]:
    validate_input(data)
    body_format = "markdown" if is_nonempty_string(data.get("body_markdown")) else "html"
    raw_body = data.get("body_markdown") if body_format == "markdown" else data.get("body_html")
    assert isinstance(raw_body, str)
    body_text = normalize_space(raw_body if body_format == "markdown" else html_to_text(raw_body))
    headings = extract_headings(data, body_format)
    sections = extract_markdown_sections(data.get("body_markdown", "")) if body_format == "markdown" else []
    frontmatter = data.get("frontmatter", {}) or {}
    author = data.get("author", {}) or {}
    sources = data.get("sources", []) or []
    audit_findings = normalize_audit_findings(data.get("audit_findings", []) or [])
    schema = load_input_schema()
    input_bytes = raw_bytes if raw_bytes is not None else json.dumps(data, sort_keys=True).encode("utf-8")
    raw_lower = raw_body.lower()
    title = data["title"].strip()
    target_keyword = data["target_keyword"].strip()
    meta_description = str(frontmatter.get("description", "")).strip()
    published_at = data.get("published_at") or frontmatter.get("date") or ""
    modified_at = data.get("modified_at") or frontmatter.get("dateModified") or ""
    author_name = author.get("name") or frontmatter.get("author") or ""
    body_words = count_words(body_text)
    first_hand_markers = (
        "we tested",
        "i tested",
        "case study",
        "original data",
        "our data",
        "field notes",
        "example",
    )

    return {
        "schema": "claude-blog-brain.ingested-blog-post.v1",
        "adapter": "ingest_blog_input",
        "input": {
            "title": title,
            "url": data["url"].strip(),
            "target_keyword": target_keyword,
            "secondary_keywords": sorted({item.strip() for item in data.get("secondary_keywords", []) if item.strip()}),
            "locale": data["locale"].strip(),
            "platform": data.get("platform", "").strip(),
        },
        "provenance": {
            "input_name": Path(source_name).name,
            "input_sha256": hashlib.sha256(input_bytes).hexdigest(),
            "body_sha256": hashlib.sha256(raw_body.encode("utf-8")).hexdigest(),
            "schema_path": "schemas/blog-post-input.schema.json",
            "schema_id": schema.get("$id", ""),
            "body_format": body_format,
            "source_url": data["url"].strip(),
            "source_count": len(sources),
            "audit_finding_count": len(audit_findings),
        },
        "frontmatter": frontmatter,
        "author": author,
        "dates": {
            "published_at": str(published_at),
            "modified_at": str(modified_at),
        },
        "content": {
            "body_text": body_text,
            "intro": first_paragraph(body_text),
            "word_count": body_words,
            "headings": headings,
            "sections": sections,
            "links": extract_links(data),
        },
        "signals": {
            "has_meta_description": bool(meta_description),
            "meta_description_length": len(meta_description),
            "has_author": bool(str(author_name).strip()),
            "has_author_bio": bool(str(author.get("bio", "")).strip()),
            "has_dates": bool(str(published_at).strip() or str(modified_at).strip()),
            "has_modified_date": bool(str(modified_at).strip()),
            "has_direct_intro_answer": has_direct_answer(body_text, target_keyword),
            "has_article_schema": "@type" in raw_lower and ("article" in raw_lower or "blogposting" in raw_lower),
            "has_faq_schema": "faqpage" in raw_lower,
            "has_canonical_tag": "rel=\"canonical\"" in raw_lower or "rel='canonical'" in raw_lower,
            "has_noindex": "noindex" in raw_lower,
            "has_first_hand_evidence": has_any(body_text, first_hand_markers),
        },
        "sources": sources,
        "audit_findings": audit_findings,
    }


def load_blog_input(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    raw_bytes = source.read_bytes()
    data = read_json(source)
    return normalize_blog_input(data, source_name=source.name, raw_bytes=raw_bytes)


def write_json(payload: dict[str, Any], output: str | Path | None) -> None:
    text = json.dumps(clean_structure(payload), indent=2, sort_keys=True) + "\n"
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize a blog post input JSON.", add_help=False)
    parser.add_argument("input")
    parser.add_argument("-o", dest="output")
    parser.add_argument("-h", action="help")
    args = parser.parse_args(argv)
    try:
        write_json(load_blog_input(args.input), args.output)
    except (OSError, ValidationError) as exc:
        errors = exc.errors if isinstance(exc, ValidationError) else [str(exc)]
        write_json({"ok": False, "errors": errors}, None)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
