"""Tests for the AI citation readiness heuristic."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import ai_citation_score


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "ai_citation_score.py"
FRONTMATTER_BOUNDARY = "-" * 3


HIGH_QUALITY_POST = f"""{FRONTMATTER_BOUNDARY}
title: AI Citation Optimization Benchmarks for 2026
description: An evidence-backed editorial readiness fixture for Google, Perplexity, and ChatGPT citation surfaces.
author: Jane Doe
date: 2026-01-15
lastUpdated: 2026-06-20
{FRONTMATTER_BOUNDARY}

# AI Citation Optimization Benchmarks for 2026

TL;DR: AI citation optimization works best when a post gives a direct answer, cites authoritative sources, defines entities, and keeps data fresh.

## AI citation readiness factors

**AI citation readiness** is an internal editorial review of observable page
signals, not the estimated chance that an answer engine will cite a page. This
fixture names its topic, provides self-contained context, and links claims to
sources such as [NIH publishing guidance](https://nih.gov/example-ai-citations)
and a [Stanford research resource](https://stanford.edu/example-study). It uses
clear sections, stable terminology, and a summary list without treating any
single format as an answer-engine requirement.

## How should sources be added?

Every statistic should sit beside its source. A 2026 newsroom sample found 41% more citations when articles linked to primary data [Reuters analysis](https://reuters.com/example-ai-study). A public health review found 33% fewer hallucinated summaries when sources were named near the claim [CDC guidance](https://cdc.gov/example-guidance).

- Define the core entity.
- Put the direct answer first.
- Refresh the date when facts change.

## FAQ

### What is a citable passage?

A citable passage is a short, self-contained answer that names the topic, explains the claim, and includes enough context for reuse.

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "AI Citation Optimization Benchmarks for 2026",
  "author": {{"@type": "Person", "name": "Jane Doe"}},
  "dateModified": "2026-06-20"
}}
</script>
"""


THIN_POST = """# Short Update

This post says AI citations matter. It has no source links, no schema, and no clear answer structure.
"""


def _write_post(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_scores_have_expected_shape(tmp_path):
    post = _write_post(tmp_path, "high.md", HIGH_QUALITY_POST)
    result = ai_citation_score.score_file(post)

    assert isinstance(result["overall"], int)
    assert 0 <= result["overall"] <= 100
    assert set(result["engines"]) == {"ai_overview", "perplexity", "chatgpt"}
    assert isinstance(result["factors"], dict)
    assert isinstance(result["recommendations"], list)
    assert result["methodology"] == "internal_ai_citation_readiness_heuristic"
    assert result["calibrated_probability"] is False
    assert result["overall_probability"] == result["overall"]

    for engine_result in result["engines"].values():
        assert isinstance(engine_result["score"], int)
        assert 0 <= engine_result["score"] <= 100


def test_scoring_is_deterministic(tmp_path):
    post = _write_post(tmp_path, "high.md", HIGH_QUALITY_POST)

    first = ai_citation_score.score_file(post)
    second = ai_citation_score.score_file(post)

    assert first == second


def test_high_quality_fixture_scores_higher_than_thin_fixture(tmp_path):
    high_post = _write_post(tmp_path, "high.md", HIGH_QUALITY_POST)
    thin_post = _write_post(tmp_path, "thin.md", THIN_POST)

    high_score = ai_citation_score.score_file(high_post)["overall"]
    thin_score = ai_citation_score.score_file(thin_post)["overall"]

    assert high_score > thin_score


def test_invalid_utf8_file_returns_structured_error(tmp_path):
    bad_post = tmp_path / "bad.md"
    bad_post.write_bytes(b"# Bad\n\xff\n")

    result = ai_citation_score.score_file(bad_post)

    assert "error" in result
    assert "Could not analyze" in result["error"]


def test_invalid_utf8_cli_exits_cleanly_with_json_error(tmp_path):
    bad_post = tmp_path / "bad.md"
    bad_post.write_bytes(b"# Bad\n\xff\n")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(bad_post)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert "error" in payload
    assert "Could not analyze" in payload["error"]
    assert "Traceback" not in result.stderr


def test_legacy_length_and_faq_signals_do_not_change_score():
    analysis = {
        "file": "post.md",
        "frontmatter": {"title": "Clear title"},
        "headings": {"h2_count": 3, "hierarchy_clean": True},
        "schema": {"has_blogposting": True, "has_person": True, "schema_count": 2},
        "citations": {
            "inline_citations": 3,
            "paren_citations": 0,
            "sourced_statistics": 2,
            "unsourced_statistics": 0,
            "unique_sources": 3,
            "tier_counts": {1: 2, 2: 1},
        },
        "ai_citation_readiness": {
            "self_contained_sections": 2,
            "evidence_backed_sections": 3,
            "purpose_statement": True,
            "entity_definitions": 2,
            "has_robots_restriction": False,
            "table_count": 1,
            "list_count": 3,
            "citable_passages": 0,
        },
        "structured_data": {
            "table_count": 1,
            "ordered_list_items": 3,
            "unordered_list_items": 0,
        },
        "engagement": {"example_count": 2},
        "images": {"count": 1, "without_alt_text": 0},
        "charts": {"chart_count": 1},
        "faq": {"has_faq_section": False, "faq_item_count": 0},
        "freshness": {"has_date": False, "has_last_updated": False},
    }
    with_legacy_signals = json.loads(json.dumps(analysis))
    with_legacy_signals["ai_citation_readiness"]["citable_passages"] = 12
    with_legacy_signals["faq"] = {"has_faq_section": True, "faq_item_count": 8}
    with_legacy_signals["freshness"] = {"has_date": True, "has_last_updated": True}
    with_legacy_signals["headings"]["h2_question_ratio"] = 1.0

    assert ai_citation_score.score_analysis(analysis)["overall"] == (
        ai_citation_score.score_analysis(with_legacy_signals)["overall"]
    )


@pytest.mark.parametrize("schema_type", ["FAQPage", "HowTo", "SpecialAnnouncement"])
def test_ineligible_schema_types_add_no_readiness_points(schema_type):
    baseline = {
        "frontmatter": {},
        "headings": {},
        "schema": {"schemas_found": [], "schema_count": 0},
        "citations": {},
        "ai_citation_readiness": {},
        "structured_data": {},
        "engagement": {},
        "images": {},
        "charts": {},
    }
    with_ineligible_schema = json.loads(json.dumps(baseline))
    with_ineligible_schema["schema"] = {
        "schemas_found": [schema_type],
        "schema_count": 1,
        "has_faqpage": schema_type == "FAQPage",
    }

    baseline_result = ai_citation_score.score_analysis(baseline)
    schema_result = ai_citation_score.score_analysis(with_ineligible_schema)

    assert schema_result["factors"]["ai_overview"]["article_schema"]["points"] == 0
    assert schema_result["overall"] == baseline_result["overall"]


def test_markdown_labels_score_as_heuristic(tmp_path):
    post = _write_post(tmp_path, "high.md", HIGH_QUALITY_POST)
    rendered = ai_citation_score._format_markdown(ai_citation_score.score_file(post))

    assert "AI Citation Readiness Heuristic" in rendered
    assert "Overall probability:" not in rendered
    assert "not a calibrated citation probability" in rendered
