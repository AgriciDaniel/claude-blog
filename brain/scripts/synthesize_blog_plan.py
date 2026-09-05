#!/usr/bin/env python3
"""Domain synthesis: convert an ingested blog record into an optimization plan.

The adapter emits a deterministic JSON plan with five quality categories,
GEO and AI citation readiness, schema recommendations, source-backed tactics,
and a delivery contract verdict for a blog post.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from ingest_blog_input import ValidationError, clean_structure, count_words


REPO = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = REPO / "references" / "source-ledger.json"
CATEGORY_ORDER = ("content", "seo", "eeat", "technical", "ai_citation")
CATEGORY_LABELS = {
    "content": "Content",
    "seo": "SEO",
    "eeat": "E-E-A-T",
    "technical": "Technical",
    "ai_citation": "AI Citation",
}
AUDIT_CATEGORY_MAP = {
    "content": "content",
    "seo": "seo",
    "eeat": "eeat",
    "technical": "technical",
    "schema": "technical",
    "geo": "ai_citation",
    "distribution": "ai_citation",
    "delivery": "content",
    "multilingual": "seo",
}
AUDIT_PENALTY = {"critical": 28, "high": 18, "medium": 10, "low": 4}
PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
STOPWORDS = {"a", "an", "and", "are", "as", "for", "how", "in", "of", "on", "or", "the", "to", "with"}


class SourceError(ValueError):
    """Raised when a plan references a source ID absent from the source ledger."""


class CategoryBuilder:
    def __init__(self, category: str) -> None:
        self.category = category
        self.score = 100
        self.findings: list[dict[str, Any]] = []
        self.recommendations: list[dict[str, Any]] = []

    def add(
        self,
        *,
        finding: str,
        recommendation: str,
        source_ids: list[str],
        penalty: int,
        priority: str,
        rec_id: str,
    ) -> None:
        self.score -= penalty
        self.findings.append(
            {
                "finding": finding,
                "impact": priority,
                "source_ids": source_ids,
            }
        )
        self.recommendations.append(
            {
                "id": rec_id,
                "category": self.category,
                "priority": priority,
                "recommendation": recommendation,
                "source_ids": source_ids,
            }
        )

    def result(self) -> dict[str, Any]:
        score = max(0, min(100, self.score))
        if not self.findings:
            self.findings.append(
                {
                    "finding": f"No blocking {CATEGORY_LABELS[self.category]} issue found in the supplied record.",
                    "impact": "low",
                    "source_ids": [],
                }
            )
        return {
            "category": self.category,
            "label": CATEGORY_LABELS[self.category],
            "score": score,
            "status": score_status(score),
            "findings": self.findings,
            "recommendations": self.recommendations,
        }


def load_ingested(path: str | Path) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError([f"invalid JSON at line {exc.lineno}, column {exc.colno}"]) from exc
    if not isinstance(data, dict):
        raise ValidationError(["ingested record root must be an object"])
    required = {"schema", "adapter", "input", "provenance", "content", "signals"}
    missing = sorted(required - set(data))
    if missing:
        raise ValidationError(["ingested record missing keys: " + ", ".join(missing)])
    if data.get("schema") != "claude-blog-brain.ingested-blog-post.v1":
        raise ValidationError(["ingested record schema is not supported"])
    cleaned = clean_structure(data)
    validate_ingested_record(cleaned)
    return cleaned


def validate_ingested_record(record: dict[str, Any]) -> None:
    errors: list[str] = []
    if record.get("schema") != "claude-blog-brain.ingested-blog-post.v1":
        errors.append("ingested record schema is not supported")
    require_string(record, "adapter", errors, required=True)
    input_data = require_object(record, "input", errors)
    provenance = require_object(record, "provenance", errors)
    require_object(record, "frontmatter", errors)
    require_object(record, "author", errors)
    dates = require_object(record, "dates", errors)
    content = require_object(record, "content", errors)
    signals = require_object(record, "signals", errors)
    require_list(record, "sources", errors)
    audit_findings = require_list(record, "audit_findings", errors)

    if input_data is not None:
        for key in ("title", "url", "target_keyword", "locale"):
            require_string(input_data, key, errors, required=True, prefix="input")
        require_string(input_data, "platform", errors, prefix="input")
        require_string_list(input_data, "secondary_keywords", errors, prefix="input")
    if provenance is not None:
        for key in ("input_name", "input_sha256", "body_sha256", "schema_path", "schema_id", "body_format", "source_url"):
            require_string(provenance, key, errors, required=True, prefix="provenance")
        require_int(provenance, "source_count", errors, required=True, prefix="provenance")
        require_int(provenance, "audit_finding_count", errors, required=True, prefix="provenance")
        if provenance.get("body_format") not in {"markdown", "html", None}:
            errors.append("provenance.body_format must be markdown or html")
    if dates is not None:
        require_string(dates, "published_at", errors, required=True, prefix="dates")
        require_string(dates, "modified_at", errors, required=True, prefix="dates")
    if content is not None:
        for key in ("body_text", "intro"):
            require_string(content, key, errors, required=True, prefix="content")
        require_int(content, "word_count", errors, required=True, prefix="content")
        headings = require_list(content, "headings", errors, prefix="content")
        sections = require_list(content, "sections", errors, prefix="content")
        require_string_list(content, "links", errors, prefix="content")
        validate_headings(headings, errors)
        validate_sections(sections, errors)
    if signals is not None:
        for key in (
            "has_meta_description",
            "has_author",
            "has_author_bio",
            "has_dates",
            "has_modified_date",
            "has_direct_intro_answer",
            "has_article_schema",
            "has_faq_schema",
            "has_canonical_tag",
            "has_noindex",
            "has_first_hand_evidence",
        ):
            require_bool(signals, key, errors, required=True, prefix="signals")
        require_int(signals, "meta_description_length", errors, required=True, prefix="signals")
    validate_audit_findings(audit_findings, errors)
    if errors:
        raise ValidationError(dedupe_errors(errors))


def require_object(data: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any] | None:
    if key not in data:
        errors.append(f"ingested record missing key: {key}")
        return None
    if not isinstance(data[key], dict):
        errors.append(f"{key} must be an object")
        return None
    return data[key]


def require_list(data: dict[str, Any], key: str, errors: list[str], prefix: str = "") -> list[Any] | None:
    path = f"{prefix}.{key}" if prefix else key
    if key not in data:
        errors.append(f"ingested record missing key: {path}")
        return None
    if not isinstance(data[key], list):
        errors.append(f"{path} must be a list")
        return None
    return data[key]


def require_string(
    data: dict[str, Any],
    key: str,
    errors: list[str],
    *,
    required: bool = False,
    prefix: str = "",
) -> None:
    path = f"{prefix}.{key}" if prefix else key
    if key not in data:
        if required:
            errors.append(f"ingested record missing key: {path}")
        return
    if not isinstance(data[key], str):
        errors.append(f"{path} must be a string")


def require_string_list(data: dict[str, Any], key: str, errors: list[str], prefix: str = "") -> None:
    path = f"{prefix}.{key}" if prefix else key
    if key not in data:
        errors.append(f"ingested record missing key: {path}")
        return
    if not isinstance(data[key], list) or not all(isinstance(item, str) for item in data[key]):
        errors.append(f"{path} must be a list of strings")


def require_int(
    data: dict[str, Any],
    key: str,
    errors: list[str],
    *,
    required: bool = False,
    prefix: str = "",
) -> None:
    path = f"{prefix}.{key}" if prefix else key
    if key not in data:
        if required:
            errors.append(f"ingested record missing key: {path}")
        return
    if not isinstance(data[key], int) or isinstance(data[key], bool):
        errors.append(f"{path} must be an integer")


def require_bool(
    data: dict[str, Any],
    key: str,
    errors: list[str],
    *,
    required: bool = False,
    prefix: str = "",
) -> None:
    path = f"{prefix}.{key}" if prefix else key
    if key not in data:
        if required:
            errors.append(f"ingested record missing key: {path}")
        return
    if not isinstance(data[key], bool):
        errors.append(f"{path} must be a boolean")


def validate_headings(headings: list[Any] | None, errors: list[str]) -> None:
    if headings is None:
        return
    for index, heading in enumerate(headings, start=1):
        if not isinstance(heading, dict):
            errors.append(f"content.headings #{index} must be an object")
            continue
        require_int(heading, "level", errors, required=True, prefix=f"content.headings #{index}")
        require_string(heading, "text", errors, required=True, prefix=f"content.headings #{index}")


def validate_sections(sections: list[Any] | None, errors: list[str]) -> None:
    if sections is None:
        return
    for index, section in enumerate(sections, start=1):
        if not isinstance(section, dict):
            errors.append(f"content.sections #{index} must be an object")
            continue
        require_string(section, "heading", errors, required=True, prefix=f"content.sections #{index}")
        require_string(section, "opening", errors, required=True, prefix=f"content.sections #{index}")
        require_int(section, "word_count", errors, required=True, prefix=f"content.sections #{index}")


def validate_audit_findings(findings: list[Any] | None, errors: list[str]) -> None:
    if findings is None:
        return
    for index, finding in enumerate(findings, start=1):
        if not isinstance(finding, dict):
            errors.append(f"audit_findings #{index} must be an object")
            continue
        for key in ("id", "category", "severity", "summary"):
            require_string(finding, key, errors, required=True, prefix=f"audit_findings #{index}")
        for key in ("recommendation", "source"):
            require_string(finding, key, errors, prefix=f"audit_findings #{index}")
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


def load_source_index(path: str | Path = DEFAULT_LEDGER) -> dict[str, dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    sources = data.get("sources", [])
    if not isinstance(sources, list):
        raise SourceError("source ledger sources must be a list")
    return {source["id"]: source for source in sources if isinstance(source, dict) and "id" in source}


def synthesize(record: dict[str, Any], *, ledger_path: str | Path = DEFAULT_LEDGER) -> dict[str, Any]:
    record = clean_structure(record)
    validate_ingested_record(record)
    source_index = load_source_index(ledger_path)
    quality = build_quality_read(record, source_index)
    geo = build_geo_readiness(record)
    schema_recs = build_schema_recommendations(record)
    prioritized = prioritize_recommendations(quality, schema_recs, geo)
    scores = {item["category"]: item["score"] for item in quality}
    overall = round(sum(scores.values()) / len(scores))
    delivery = build_delivery_contract(record, scores, prioritized, overall)
    source_ids = collect_source_ids(quality, schema_recs, geo, prioritized, delivery)
    citations = source_citations(source_ids, source_index)
    plan = {
        "schema": "claude-blog-brain.blog-optimization-plan.v1",
        "adapter": "synthesize_blog_plan",
        "input": {
            "title": record["input"]["title"],
            "url": record["input"]["url"],
            "target_keyword": record["input"]["target_keyword"],
            "locale": record["input"]["locale"],
        },
        "provenance": {
            "input_name": record["provenance"].get("input_name", ""),
            "input_sha256": record["provenance"].get("input_sha256", ""),
            "body_sha256": record["provenance"].get("body_sha256", ""),
            "source_count": record["provenance"].get("source_count", 0),
            "body_format": record["provenance"].get("body_format", ""),
        },
        "scores": {
            "overall": overall,
            **scores,
        },
        "quality_read": quality,
        "geo_ai_citation_readiness": geo,
        "schema_recommendations": schema_recs,
        "prioritized_recommendations": prioritized,
        "delivery_contract": delivery,
        "source_citations": citations,
    }
    return clean_structure(plan)


def build_quality_read(record: dict[str, Any], source_index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    builders = {category: CategoryBuilder(category) for category in CATEGORY_ORDER}
    apply_content_checks(record, builders["content"])
    apply_seo_checks(record, builders["seo"])
    apply_eeat_checks(record, builders["eeat"])
    apply_technical_checks(record, builders["technical"])
    apply_ai_citation_checks(record, builders["ai_citation"])
    apply_audit_findings(record, builders, source_index)
    return [builders[category].result() for category in CATEGORY_ORDER]


def apply_content_checks(record: dict[str, Any], builder: CategoryBuilder) -> None:
    word_count = int(record["content"].get("word_count", 0))
    h2_count = sum(1 for heading in record["content"].get("headings", []) if heading.get("level") == 2)
    source_count = int(record["provenance"].get("source_count", 0))
    signals = record.get("signals", {})
    if word_count < 700:
        builder.add(
            finding=f"The body has {word_count} words, which is light for this optimization review.",
            recommendation="Expand the post with original examples, dated evidence, and concrete reader takeaways.",
            source_ids=["g-helpful-content"],
            penalty=18,
            priority="medium",
            rec_id="content-expand-evidence",
        )
    if h2_count < 2:
        builder.add(
            finding=f"The post exposes {h2_count} H2 sections.",
            recommendation="Add a clear H2 structure so each major reader question has its own section.",
            source_ids=["g-helpful-content"],
            penalty=14,
            priority="medium",
            rec_id="content-add-h2-structure",
        )
    if not signals.get("has_direct_intro_answer"):
        builder.add(
            finding="The opening paragraph does not answer the target query directly.",
            recommendation="Open with a concise answer to the target query before adding nuance and examples.",
            source_ids=["g-helpful-content", "ziptie-aio-source-selection"],
            penalty=14,
            priority="high",
            rec_id="content-answer-first-intro",
        )
    if source_count < 2:
        builder.add(
            finding=f"The record includes {source_count} dated evidence sources.",
            recommendation="Add at least two dated, trustworthy sources for claims that guide publishing decisions.",
            source_ids=["g-helpful-content"],
            penalty=18,
            priority="high",
            rec_id="content-add-dated-sources",
        )
    if not signals.get("has_modified_date"):
        builder.add(
            finding="No modified date is present in the input record.",
            recommendation="Expose the last reviewed or modified date when the post includes current SEO or AI search guidance.",
            source_ids=["g-helpful-content"],
            penalty=8,
            priority="low",
            rec_id="content-add-modified-date",
        )


def apply_seo_checks(record: dict[str, Any], builder: CategoryBuilder) -> None:
    target = record["input"]["target_keyword"]
    secondary = record["input"].get("secondary_keywords", [])
    title = record["input"]["title"].lower()
    body = record["content"].get("body_text", "").lower()
    heading_text = " ".join(heading.get("text", "") for heading in record["content"].get("headings", [])).lower()
    if not has_intent_coverage(target, title, secondary):
        builder.add(
            finding="The title does not clearly cover the target query intent or close entity variants.",
            recommendation="Align the title with the primary query while keeping it useful for readers.",
            source_ids=["g-helpful-content"],
            penalty=18,
            priority="high",
            rec_id="seo-title-query-alignment",
        )
    if not has_intent_coverage(target, body, secondary):
        builder.add(
            finding="The body copy does not clearly cover the target query intent or close entity variants.",
            recommendation="Use the query intent, named entities, and natural variants in the opening and relevant explanatory copy.",
            source_ids=["g-helpful-content"],
            penalty=18,
            priority="high",
            rec_id="seo-body-query-alignment",
        )
    if not has_intent_coverage(target, heading_text, secondary):
        builder.add(
            finding="No heading clearly reflects the target query intent or a close variant.",
            recommendation="Add one reader-useful heading that reflects the target query or a close intent variant.",
            source_ids=["g-helpful-content"],
            penalty=10,
            priority="medium",
            rec_id="seo-heading-intent",
        )
    if not record["signals"].get("has_meta_description"):
        builder.add(
            finding="No meta description was supplied in frontmatter.",
            recommendation="Write a concise description that states the answer, audience, and differentiator.",
            source_ids=["g-helpful-content"],
            penalty=10,
            priority="medium",
            rec_id="seo-meta-description",
        )
    if not record["content"].get("links"):
        builder.add(
            finding="No links were detected in the supplied body.",
            recommendation="Add useful internal or external links where they help readers verify claims or continue the task.",
            source_ids=["g-helpful-content"],
            penalty=8,
            priority="low",
            rec_id="seo-add-useful-links",
        )


def apply_eeat_checks(record: dict[str, Any], builder: CategoryBuilder) -> None:
    signals = record.get("signals", {})
    if not signals.get("has_author"):
        builder.add(
            finding="No author name is available from author metadata or frontmatter.",
            recommendation="Add author identity and accountability signals for editorial trust.",
            source_ids=["g-helpful-content", "g-qrg-full"],
            penalty=22,
            priority="high",
            rec_id="eeat-add-author",
        )
    if not signals.get("has_author_bio"):
        builder.add(
            finding="No author bio was supplied.",
            recommendation="Add a short author bio that explains relevant experience without overstating credentials.",
            source_ids=["g-helpful-content", "g-qrg-full"],
            penalty=10,
            priority="medium",
            rec_id="eeat-author-bio",
        )
    if not signals.get("has_dates"):
        builder.add(
            finding="No publish or modified date is available.",
            recommendation="Add visible date metadata so readers can judge freshness.",
            source_ids=["g-helpful-content", "g-qrg-full"],
            penalty=12,
            priority="medium",
            rec_id="eeat-date-metadata",
        )
    if not signals.get("has_first_hand_evidence"):
        builder.add(
            finding="The body does not show obvious first-hand examples, tests, or original observations.",
            recommendation="Add first-hand examples, test notes, screenshots, or editorial rationale where the topic calls for trust.",
            source_ids=["g-helpful-content", "g-qrg-full"],
            penalty=12,
            priority="medium",
            rec_id="eeat-first-hand-evidence",
        )


def apply_technical_checks(record: dict[str, Any], builder: CategoryBuilder) -> None:
    signals = record.get("signals", {})
    body_format = record.get("provenance", {}).get("body_format", "")
    if signals.get("has_noindex"):
        builder.add(
            finding="The supplied body includes a noindex signal.",
            recommendation="Remove noindex from indexable blog templates before publication.",
            source_ids=["g-block-indexing"],
            penalty=35,
            priority="critical",
            rec_id="technical-remove-noindex",
        )
    if body_format == "html" and not signals.get("has_canonical_tag"):
        builder.add(
            finding="The HTML body does not expose a canonical tag.",
            recommendation="Verify the rendered page emits a canonical signal that matches the intended URL.",
            source_ids=["g-canonical"],
            penalty=8,
            priority="low",
            rec_id="technical-canonical-check",
        )
    if body_format == "markdown":
        builder.add(
            finding="The adapter received Markdown, so rendered HTML parity cannot be checked here.",
            recommendation="Verify rendered mobile content parity, canonical output, and structured data in the publishing build.",
            source_ids=["g-mobile-first", "g-intro-sd"],
            penalty=8,
            priority="low",
            rec_id="technical-rendered-html-check",
        )
    if not signals.get("has_article_schema"):
        builder.add(
            finding="No Article or BlogPosting schema was detected in the supplied body.",
            recommendation="Add Article or BlogPosting JSON-LD in the rendered page with coherent author and publisher entities.",
            source_ids=["g-intro-sd", "g-search-gallery"],
            penalty=12,
            priority="medium",
            rec_id="technical-article-schema",
        )


def apply_ai_citation_checks(record: dict[str, Any], builder: CategoryBuilder) -> None:
    readiness = compute_geo_metrics(record)
    signals = record.get("signals", {})
    source_count = int(record["provenance"].get("source_count", 0))
    if readiness["section_count"] == 0:
        builder.add(
            finding="No H2 sections were available for passage extraction.",
            recommendation="Create answer-first H2 sections that can stand alone when quoted or summarized.",
            source_ids=["ziptie-aio-source-selection", "g-ai-features"],
            penalty=28,
            priority="high",
            rec_id="ai-create-extractable-sections",
        )
    elif readiness["extractable_section_count"] < max(1, readiness["section_count"] // 2):
        builder.add(
            finding=f"{readiness['extractable_section_count']} of {readiness['section_count']} H2 sections open with compact answer passages.",
            recommendation="Rewrite important H2 openings as direct, self-contained answers with source context.",
            source_ids=["ziptie-aio-source-selection", "g-ai-features"],
            penalty=22,
            priority="high",
            rec_id="ai-improve-passage-extractability",
        )
    if readiness["entity_coverage"] < 0.75:
        builder.add(
            finding=f"Entity coverage is {readiness['entity_coverage']:.2f} across target and secondary terms.",
            recommendation="Clarify named entities, product nouns, and topic variants in headings and first paragraphs.",
            source_ids=["ziptie-aio-source-selection"],
            penalty=14,
            priority="medium",
            rec_id="ai-entity-coverage",
        )
    if source_count < 2:
        builder.add(
            finding=f"The post has {source_count} evidence sources for extractable claims.",
            recommendation="Attach visible citations to claims that AI systems may extract.",
            source_ids=["ziptie-aio-source-selection", "g-ai-features"],
            penalty=18,
            priority="high",
            rec_id="ai-visible-citations",
        )
    if not signals.get("has_article_schema"):
        builder.add(
            finding="Article schema is not detected in the supplied body.",
            recommendation="Use Article schema for entity clarity, but do not invent special AI schema or Google-only AI files.",
            source_ids=["g-intro-sd", "g-ai-opt-guide"],
            penalty=10,
            priority="medium",
            rec_id="ai-schema-entity-clarity",
        )


def apply_audit_findings(
    record: dict[str, Any],
    builders: dict[str, CategoryBuilder],
    source_index: dict[str, dict[str, Any]],
) -> None:
    for finding in record.get("audit_findings", []):
        category = AUDIT_CATEGORY_MAP.get(finding.get("category", ""), "content")
        severity = finding.get("severity", "low")
        source_ids = audit_source_ids(finding, source_index)
        recommendation = finding.get("recommendation") or "Resolve the supplied audit finding before publication."
        if not source_ids:
            recommendation = mark_operator_supplied(recommendation)
        builders[category].add(
            finding=f"Input audit finding {finding.get('id')}: {finding.get('summary')}",
            recommendation=recommendation,
            source_ids=source_ids,
            penalty=AUDIT_PENALTY.get(severity, 4),
            priority=severity,
            rec_id=f"audit-{finding.get('id', 'finding')}",
        )


def audit_source_ids(
    finding: dict[str, Any],
    source_index: dict[str, dict[str, Any]],
) -> list[str]:
    source = finding.get("source", "")
    if isinstance(source, str) and source in source_index:
        return [source]
    return []


def mark_operator_supplied(recommendation: str) -> str:
    marker = "operator-supplied (unverified)"
    if recommendation.lower().startswith(marker):
        return recommendation
    return f"{marker}: {recommendation}"


def has_intent_coverage(target: str, text: str, secondary_terms: list[str]) -> bool:
    text_terms = text_term_set(text)
    target_terms = meaningful_terms(target)
    if not target_terms:
        return True
    if term_coverage(target_terms, text_terms) >= 0.6:
        return True
    for term in secondary_terms:
        terms = meaningful_terms(term)
        if terms and term_coverage(terms, text_terms) >= 0.75:
            return True
    return False


def meaningful_terms(value: str) -> list[str]:
    return [term for term in re.findall(r"[a-z0-9]+", value.lower()) if len(term) > 2 and term not in STOPWORDS]


def text_term_set(value: str) -> set[str]:
    terms: set[str] = set()
    for term in meaningful_terms(value):
        terms.add(term)
        if len(term) > 3 and term.endswith("s"):
            terms.add(term[:-1])
    return terms


def term_coverage(terms: list[str], text_terms: set[str]) -> float:
    if not terms:
        return 1.0
    hits = 0
    for term in terms:
        variants = {term}
        if len(term) > 3 and term.endswith("s"):
            variants.add(term[:-1])
        if any(variant in text_terms for variant in variants):
            hits += 1
    return hits / len(terms)


def compute_geo_metrics(record: dict[str, Any]) -> dict[str, Any]:
    sections = record["content"].get("sections", [])
    extractable = [section for section in sections if is_extractable_opening(section.get("opening", ""))]
    terms = entity_terms(record)
    body = record["content"].get("body_text", "").lower()
    body_terms = text_term_set(body)
    present = [term for term in terms if term_coverage(meaningful_terms(term), body_terms) >= 0.75]
    word_count = max(1, int(record["content"].get("word_count", 0)))
    term_hits = sum(sum(1 for token in meaningful_terms(term) if token in body_terms) for term in terms)
    coverage = round(len(present) / len(terms), 2) if terms else 0.0
    return {
        "section_count": len(sections),
        "extractable_section_count": len(extractable),
        "entity_terms": terms,
        "covered_entity_terms": present,
        "entity_coverage": coverage,
        "entity_mentions_per_1000_words": round((term_hits / word_count) * 1000, 2),
    }


def entity_terms(record: dict[str, Any]) -> list[str]:
    terms: list[str] = [record["input"]["target_keyword"]]
    terms.extend(record["input"].get("secondary_keywords", []))
    cleaned: list[str] = []
    seen: set[str] = set()
    for term in terms:
        compact = " ".join(str(term).split())
        key = compact.lower()
        if compact and key not in seen:
            cleaned.append(compact)
            seen.add(key)
    return cleaned


def is_extractable_opening(opening: str) -> bool:
    words = count_words(opening)
    return 12 <= words <= 80 and opening.endswith((".", "?", "!"))


def build_geo_readiness(record: dict[str, Any]) -> dict[str, Any]:
    metrics = compute_geo_metrics(record)
    signals = record.get("signals", {})
    passage_status = "pass" if metrics["extractable_section_count"] >= max(1, metrics["section_count"] // 2) else "revise"
    entity_status = "pass" if metrics["entity_coverage"] >= 0.75 else "revise"
    schema_status = "pass" if signals.get("has_article_schema") else "revise"
    checks = [
        {
            "name": "Passage extractability",
            "status": passage_status,
            "evidence": f"{metrics['extractable_section_count']} of {metrics['section_count']} H2 sections have compact answer openings.",
            "recommendation": "Make each important H2 opening a direct answer with enough context to stand alone.",
            "source_ids": ["ziptie-aio-source-selection", "g-ai-features"],
        },
        {
            "name": "Entity density",
            "status": entity_status,
            "evidence": f"{metrics['entity_mentions_per_1000_words']} tracked entity mentions per 1000 words.",
            "recommendation": "Use target entities naturally in headings, openings, examples, and source-backed explanations.",
            "source_ids": ["ziptie-aio-source-selection"],
        },
        {
            "name": "Article schema check",
            "status": schema_status,
            "evidence": "Article or BlogPosting schema detected." if signals.get("has_article_schema") else "Article or BlogPosting schema not detected.",
            "recommendation": "Prefer Article or BlogPosting JSON-LD for blog posts and keep it consistent with visible content.",
            "source_ids": ["g-intro-sd", "g-search-gallery"],
        },
    ]
    tactics = [
        {
            "priority": "high",
            "tactic": "Put the answer, entity, and source context in the first paragraph under each important H2.",
            "source_ids": ["ziptie-aio-source-selection"],
        },
        {
            "priority": "medium",
            "tactic": "Measure AI Overview and AI Mode visibility in Search Console where the reporting is available.",
            "source_ids": ["g-genai-reports"],
        },
        {
            "priority": "medium",
            "tactic": "Treat citation inclusion as a visibility hypothesis because one cited study reports an observed association between AI Overview citation and higher clicks per impression; do not present it as causal or guaranteed.",
            "source_ids": ["seer-aio-impact-ctr-2026"],
        },
        {
            "priority": "low",
            "tactic": "Do not recommend llms.txt as a Google Search, AI Overview, or AI Mode visibility tactic.",
            "source_ids": ["g-ai-opt-guide"],
        },
    ]
    return {
        "score": round((status_score(passage_status) + status_score(entity_status) + status_score(schema_status)) / 3),
        "metrics": metrics,
        "checks": checks,
        "being_cited_tactics": tactics,
    }


def build_schema_recommendations(record: dict[str, Any]) -> list[dict[str, Any]]:
    signals = record.get("signals", {})
    recs = [
        {
            "schema_type": "Article or BlogPosting",
            "priority": "high",
            "recommendation": "Use Article or BlogPosting JSON-LD as the primary blog schema, including headline, author, publisher, dates, image when available, and canonical URL alignment.",
            "source_ids": ["g-intro-sd", "g-search-gallery"],
            "status": "present" if signals.get("has_article_schema") else "missing",
        },
        {
            "schema_type": "Person and Organization",
            "priority": "medium",
            "recommendation": "Connect author and publisher entities to the Article graph when those entities are visible on the page.",
            "source_ids": ["g-intro-sd", "schema-org-type"],
            "status": "review",
        },
        {
            "schema_type": "FAQPage caveat",
            "priority": "medium",
            "recommendation": "Do not sell FAQPage as a rich result tactic because FAQ rich results are retired; keep visible Q and A content only when it helps readers.",
            "source_ids": ["g-faqpage-sd"],
            "status": "caveat",
        },
    ]
    if signals.get("has_faq_schema"):
        recs.append(
            {
                "schema_type": "FAQPage cleanup",
                "priority": "high",
                "recommendation": "Review FAQPage markup and remove any promise that it will earn Google FAQ rich results.",
                "source_ids": ["g-faqpage-sd"],
                "status": "review",
            }
        )
    return recs


def prioritize_recommendations(
    quality: list[dict[str, Any]],
    schema_recs: list[dict[str, Any]],
    geo: dict[str, Any],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for category in quality:
        items.extend(category.get("recommendations", []))
    for rec in schema_recs:
        if rec["status"] != "present":
            items.append(
                {
                    "id": f"schema-{slugify(rec['schema_type'])}",
                    "category": "schema",
                    "priority": rec["priority"],
                    "recommendation": rec["recommendation"],
                    "source_ids": rec["source_ids"],
                }
            )
    for tactic in geo.get("being_cited_tactics", []):
        items.append(
            {
                "id": f"geo-{slugify(tactic['tactic'])[:48]}",
                "category": "ai_citation",
                "priority": tactic["priority"],
                "recommendation": tactic["tactic"],
                "source_ids": tactic["source_ids"],
            }
        )
    unique: dict[str, dict[str, Any]] = {}
    for item in items:
        key = item["recommendation"].lower()
        if key not in unique:
            unique[key] = item
    return sorted(
        unique.values(),
        key=lambda item: (
            PRIORITY_ORDER.get(item.get("priority", "low"), 9),
            CATEGORY_ORDER.index(item["category"]) if item["category"] in CATEGORY_ORDER else len(CATEGORY_ORDER),
            item["id"],
        ),
    )


def build_delivery_contract(
    record: dict[str, Any],
    scores: dict[str, int],
    recommendations: list[dict[str, Any]],
    overall: int,
) -> dict[str, Any]:
    audit_findings = record.get("audit_findings", [])
    has_critical = any(item.get("severity") == "critical" for item in audit_findings)
    has_high = any(item.get("severity") == "high" for item in audit_findings)
    lowest_score = min(scores.values())
    if has_critical or lowest_score < 55 or overall < 60:
        verdict = "hold before publish"
    elif has_high or lowest_score < 75 or overall < 80:
        verdict = "revise before publish"
    else:
        verdict = "pass with monitoring"
    required = [
        item["recommendation"]
        for item in recommendations
        if item.get("priority") in {"critical", "high"}
    ][:5]
    if not required and verdict != "pass with monitoring":
        required = [recommendations[0]["recommendation"]] if recommendations else []
    confidence = "high" if int(record["provenance"].get("source_count", 0)) >= 2 and record["signals"].get("has_dates") else "medium"
    return {
        "verdict": verdict,
        "overall_score": overall,
        "lowest_category_score": lowest_score,
        "confidence": confidence,
        "required_before_publish": required,
        "guardrails": [
            {
                "rule": "Advisory only; this plan is not a ranking or AI citation guarantee.",
                "source_ids": ["g-ai-opt-guide"],
            }
        ],
    }


def score_status(score: int) -> str:
    if score >= 85:
        return "pass"
    if score >= 75:
        return "watch"
    if score >= 55:
        return "revise"
    return "hold"


def status_score(status: str) -> int:
    return {"pass": 100, "watch": 80, "revise": 55, "hold": 25}.get(status, 55)


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
                "retrieved": source.get("retrieved", ""),
                "published": source.get("published", source.get("date", "")),
                "confidence": source.get("confidence", ""),
            }
        )
    return citations


def write_json(payload: dict[str, Any], output: str | Path | None) -> None:
    text = json.dumps(clean_structure(payload), indent=2, sort_keys=True) + "\n"
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synthesize a blog optimization plan JSON.", add_help=False)
    parser.add_argument("input")
    parser.add_argument("-l", dest="ledger", default=str(DEFAULT_LEDGER))
    parser.add_argument("-o", dest="output")
    parser.add_argument("-h", action="help")
    args = parser.parse_args(argv)
    try:
        plan = synthesize(load_ingested(args.input), ledger_path=args.ledger)
        write_json(plan, args.output)
    except (OSError, ValidationError, SourceError) as exc:
        errors = exc.errors if isinstance(exc, ValidationError) else [str(exc)]
        write_json({"ok": False, "errors": errors}, None)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
