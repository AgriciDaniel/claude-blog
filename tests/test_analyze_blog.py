"""Tests for the blog quality analyzer script."""

import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import analyze_blog


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------


class TestExtractFrontmatter:
    def test_extracts_yaml_frontmatter(self, sample_blog_post):
        fm = analyze_blog.extract_frontmatter(sample_blog_post)
        assert fm["title"] == "How to Optimize Your Blog for AI Citations"
        assert fm["author"] == "Jane Doe"

    def test_returns_empty_dict_without_frontmatter(self, sample_post_no_frontmatter):
        fm = analyze_blog.extract_frontmatter(sample_post_no_frontmatter)
        assert fm == {}

    def test_strips_quotes_from_values(self):
        content = '---\ntitle: "Quoted Title"\nauthor: \'Single Quoted\'\n---\n'
        fm = analyze_blog.extract_frontmatter(content)
        assert fm["title"] == "Quoted Title"
        assert fm["author"] == "Single Quoted"


class TestStripFrontmatter:
    def test_removes_frontmatter(self, sample_blog_post):
        stripped = analyze_blog.strip_frontmatter(sample_blog_post)
        assert "---" not in stripped.split("\n")[0]
        assert "# How to Optimize" in stripped

    def test_no_frontmatter_returns_unchanged(self, sample_post_no_frontmatter):
        stripped = analyze_blog.strip_frontmatter(sample_post_no_frontmatter)
        assert stripped == sample_post_no_frontmatter


# ---------------------------------------------------------------------------
# Heading analysis
# ---------------------------------------------------------------------------


class TestAnalyzeHeadings:
    def test_counts_heading_levels(self, sample_blog_post):
        result = analyze_blog.analyze_headings(sample_blog_post)
        assert result["h1_count"] == 1
        assert result["h2_count"] >= 3
        assert result["h3_count"] >= 1

    def test_detects_question_headings(self, sample_blog_post):
        result = analyze_blog.analyze_headings(sample_blog_post)
        assert result["h2_question_count"] >= 2
        assert result["h2_question_ratio"] > 0

    def test_clean_hierarchy(self):
        content = "# Title\n\n## Section\n\n### Sub\n\n## Another\n"
        result = analyze_blog.analyze_headings(content)
        assert result["hierarchy_clean"] is True

    def test_dirty_hierarchy(self):
        content = "# Title\n\n### Skipped H2\n\n## Section\n"
        result = analyze_blog.analyze_headings(content)
        assert result["hierarchy_clean"] is False

    def test_empty_content(self):
        result = analyze_blog.analyze_headings("")
        assert result["total"] == 0


# ---------------------------------------------------------------------------
# Paragraph analysis
# ---------------------------------------------------------------------------


class TestAnalyzeParagraphs:
    def test_counts_paragraphs(self, sample_blog_post):
        result = analyze_blog.analyze_paragraphs(sample_blog_post)
        assert result["total_paragraphs"] > 0

    def test_calculates_avg_word_count(self, sample_blog_post):
        result = analyze_blog.analyze_paragraphs(sample_blog_post)
        assert result["avg_word_count"] > 0

    def test_ignores_short_paragraphs(self):
        content = "One.\n\nTwo.\n\nThree words here.\n\n" + (
            "This is a paragraph with enough words to be counted by the analyzer. " * 3
        )
        result = analyze_blog.analyze_paragraphs(content)
        assert result["total_paragraphs"] == 1

    def test_detects_over_150(self):
        long_para = " ".join(["word"] * 160)
        content = f"\n\n{long_para}\n\n"
        result = analyze_blog.analyze_paragraphs(content)
        assert result["over_150_words"] >= 1

    def test_empty_content(self):
        result = analyze_blog.analyze_paragraphs("")
        assert result["total_paragraphs"] == 0
        assert result["avg_word_count"] == 0


# ---------------------------------------------------------------------------
# Image analysis
# ---------------------------------------------------------------------------


class TestAnalyzeImages:
    def test_detects_markdown_images(self):
        content = "![Alt text](image.jpg)\n![Another](photo.png)\n"
        result = analyze_blog.analyze_images(content)
        assert result["count"] == 2

    def test_detects_missing_alt_text(self):
        content = "![](image.jpg)\n![Good alt](photo.png)\n"
        result = analyze_blog.analyze_images(content)
        assert result["without_alt_text"] >= 1

    @pytest.mark.parametrize(
        "tag",
        [
            '<img src="/a.webp" alt="Descriptive text" width="1200">',
            "<IMG ALT='Descriptive text' SRC='/a.webp'>",
        ],
    )
    def test_detects_html_alt_text_regardless_of_attribute_order(self, tag):
        result = analyze_blog.analyze_images(tag)
        assert result["count"] == 1
        assert result["with_alt_text"] == 1
        assert result["without_alt_text"] == 0

    def test_no_images(self):
        result = analyze_blog.analyze_images("No images here.")
        assert result["count"] == 0


# ---------------------------------------------------------------------------
# AI content detection
# ---------------------------------------------------------------------------


class TestAISignals:
    def test_detects_ai_phrases(self):
        content = "In today's digital landscape, it's important to note that we must dive into this topic."
        sentences_info = analyze_blog.analyze_sentences(content)
        result = analyze_blog.analyze_ai_signals(content, sentences_info)
        assert result["ai_phrase_count"] > 0

    def test_clean_content_low_signals(self):
        content = "Blog optimization requires structured content. Statistics from Ahrefs show 43% improvement."
        sentences_info = analyze_blog.analyze_sentences(content)
        result = analyze_blog.analyze_ai_signals(content, sentences_info)
        assert result["ai_phrase_count"] == 0


class TestAITriggerWords:
    def test_detects_trigger_words(self):
        text = "We must delve into this multifaceted topic to illuminate the nuanced landscape."
        result = analyze_blog.analyze_ai_trigger_words(text)
        assert result["trigger_count"] > 0
        assert len(result["found"]) > 0

    def test_clean_text(self):
        text = "This article explains how to write better blog posts using data."
        result = analyze_blog.analyze_ai_trigger_words(text)
        assert result["trigger_count"] == 0


# ---------------------------------------------------------------------------
# Citation analysis
# ---------------------------------------------------------------------------


class TestAnalyzeCitations:
    def test_detects_inline_citations(self):
        content = "According to a study (Source, 2025), AI citations increased by 340%."
        result = analyze_blog.analyze_citations(content)
        assert result["total_statistics"] >= 1

    def test_no_statistics(self):
        content = "No numbers or statistics in this text at all."
        result = analyze_blog.analyze_citations(content)
        assert result["total_statistics"] == 0

    def test_tier_classification_uses_hostname_not_substring(self):
        attacker = "https://attacker.example/post?source=nih.gov"
        trusted = "https://www.nih.gov/research"
        assert analyze_blog._classify_source_tier(attacker) == 3
        assert analyze_blog._classify_source_tier(trusted) == 1

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.resmigazete.gov.tr/guidance",
            "https://www.gov.uk/guidance",
            "https://x.edu.au/research",
            "https://y.ac.uk/research",
        ],
    )
    def test_tier_one_includes_non_us_government_and_academic_hosts(self, url):
        assert analyze_blog._classify_source_tier(url) == 1

    @pytest.mark.parametrize(
        "url",
        [
            "https://gov.example.com/post",
            "https://agency.gov.com/post",
            "https://academic.example.com/post?source=gov.uk",
        ],
    )
    def test_tier_one_country_patterns_do_not_match_untrusted_positions(self, url):
        assert analyze_blog._classify_source_tier(url) == 3


# ---------------------------------------------------------------------------
# FAQ analysis
# ---------------------------------------------------------------------------


class TestAnalyzeFAQ:
    def test_detects_faq_section(self, sample_blog_post):
        result = analyze_blog.analyze_faq(sample_blog_post)
        assert result["has_faq_section"] is True
        assert result["faq_item_count"] >= 2

    def test_no_faq(self):
        content = "# Title\n\n## Section\n\nJust regular content."
        result = analyze_blog.analyze_faq(content)
        assert result["has_faq_section"] is False


# ---------------------------------------------------------------------------
# Freshness analysis
# ---------------------------------------------------------------------------


class TestAnalyzeFreshness:
    def test_detects_dates(self):
        fm = {"date": "2026-01-15", "lastUpdated": "2026-02-10"}
        result = analyze_blog.analyze_freshness(fm)
        assert result["has_date"] is True
        assert result["has_last_updated"] is True

    def test_no_dates(self):
        result = analyze_blog.analyze_freshness({})
        assert result["has_date"] is False
        assert result["has_last_updated"] is False


# ---------------------------------------------------------------------------
# Readability analysis
# ---------------------------------------------------------------------------


class TestAnalyzeReadability:
    def test_flesch_score(self, sample_blog_post):
        stripped = analyze_blog.strip_frontmatter(sample_blog_post)
        result = analyze_blog.analyze_readability(stripped)
        assert "flesch_reading_ease" in result

    def test_reading_time(self, sample_blog_post):
        stripped = analyze_blog.strip_frontmatter(sample_blog_post)
        result = analyze_blog.analyze_readability(stripped)
        assert result["reading_time_minutes"] > 0

    def test_turkish_uses_atesman_instead_of_flesch(self):
        text = (
            "Bu yazı açık ve anlaşılır bir yöntem sunar. "
            "Okur her adımı kolayca izler ve sonucu değerlendirir. "
            "Kısa örnekler uygulamayı daha anlaşılır hale getirir."
        )
        result = analyze_blog.analyze_readability(text, "tr")

        assert result["reading_model"] == "atesman"
        assert "atesman_reading_ease" in result
        assert "flesch_reading_ease" not in result


def test_plain_text_cleanup_excludes_non_prose_payloads():
    content = """
Visible sentence.

| Header | Value |
| --- | --- |
| fake sentence with forty repeated repeated repeated repeated words | 10 |

```json
{"fake": "code sentence that must not count"}
```

<svg><title>Very long chart title that must not count</title></svg>

- Useful visible list item.
"""
    cleaned = analyze_blog._plain_text_for_analysis(content)

    assert "Visible sentence" in cleaned
    assert "Useful visible list item" in cleaned
    assert "fake sentence" not in cleaned
    assert "code sentence" not in cleaned
    assert "chart title" not in cleaned


def test_turkish_profile_detects_summary_trust_and_supported_experience(tmp_path):
    post = """---
title: Kaynak İncelemesi
description: Kaynak incelemesi doğrulama yöntemini açıklar.
author: Ayşe Yılmaz
lang: tr-TR
---
# Kaynak İncelemesi

## Özet

Bu inceleme karar vermeyi kolaylaştırır.

## Yöntem

Kendi kayıtlarımızdan derlediğimiz 120 sonucu sayım yöntemiyle karşılaştırdık.

## Güven

[Biz kimiz](/biz-kimiz) ve [İletişim](/iletisim) sayfalarını inceleyin.
"""
    path = tmp_path / "turkish.md"
    path.write_text(post, encoding="utf-8")

    result = analyze_blog.analyze_file(str(path))

    assert result["language"] == "tr"
    assert result["readability"]["reading_model"] == "atesman"
    assert result["ai_citation_readiness"]["has_tldr"] is True
    assert result["originality"]["first_person_count"] >= 1
    assert result["originality"]["methodology_count"] >= 1
    assert result["originality"]["unsupported_experience_claims"] == 0
    assert result["score"]["category_details"]["eeat_signals"]["breakdown"]["trust"] == 3


# ---------------------------------------------------------------------------
# Sentence analysis
# ---------------------------------------------------------------------------


class TestAnalyzeSentences:
    def test_detects_over_25_word_sentences(self):
        long = "This is a very " + "very " * 20 + "long sentence that goes on and on."
        short = "Short one."
        text = f"{long} {short}"
        result = analyze_blog.analyze_sentences(text)
        assert result["over_25_count"] >= 1

    def test_burstiness(self):
        text = "Short. Also short. This one is a bit longer than the others. Tiny."
        result = analyze_blog.analyze_sentences(text)
        assert "burstiness" in result


# ---------------------------------------------------------------------------
# Link analysis
# ---------------------------------------------------------------------------


class TestAnalyzeLinks:
    def test_counts_internal_and_external(self):
        content = "[internal](/about) and [external](https://example.com/page)"
        result = analyze_blog.analyze_links(content)
        assert result["internal_count"] >= 1
        assert result["external_count"] >= 1

    def test_no_links(self):
        result = analyze_blog.analyze_links("No links here.")
        assert result["internal_count"] == 0
        assert result["external_count"] == 0


# ---------------------------------------------------------------------------
# Schema analysis
# ---------------------------------------------------------------------------


class TestAnalyzeSchema:
    def test_detects_json_ld(self, sample_post_with_schema):
        result = analyze_blog.analyze_schema(sample_post_with_schema)
        assert result["schema_count"] >= 1
        assert result["has_blogposting"] is True

    def test_no_schema(self):
        result = analyze_blog.analyze_schema("# Simple post\n\nNo schema here.")
        assert result["schema_count"] == 0

    def test_detects_graph_and_list_valued_schema_types(self):
        content = """
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {"@type": "BlogPosting", "author": {"@type": "Person"}},
    {"@type": ["BreadcrumbList", "Thing"]}
  ]
}
</script>
"""
        result = analyze_blog.analyze_schema(content)

        assert result["schemas_found"] == [
            "BlogPosting",
            "Person",
            "BreadcrumbList",
            "Thing",
        ]
        assert result["has_blogposting"] is True
        assert result["has_person"] is True
        assert result["has_breadcrumblist"] is True

    def test_graph_detection_does_not_require_beautifulsoup(self, monkeypatch):
        monkeypatch.setattr(analyze_blog, "HAS_BS4", False)
        content = """
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[{"@type":"BlogPosting"}]}
</script>
"""

        result = analyze_blog.analyze_schema(content)

        assert result["schemas_found"] == ["BlogPosting"]
        assert result["has_blogposting"] is True

    @pytest.mark.parametrize("schema_type", ["FAQPage", "HowTo", "SpecialAnnouncement"])
    def test_ineligible_schema_does_not_raise_technical_schema_score(
        self, tmp_path, schema_type
    ):
        base = """---
title: Source Review
author: Jane Doe
---
# Source Review

## Evidence

This review links [primary guidance](https://example.gov/guidance).
"""
        schema = f"""
<script type="application/ld+json">
{{"@context": "https://schema.org", "@type": "{schema_type}"}}
</script>
"""
        base_path = tmp_path / "base.md"
        schema_path = tmp_path / "schema.md"
        base_path.write_text(base, encoding="utf-8")
        schema_path.write_text(base + schema, encoding="utf-8")

        base_result = analyze_blog.analyze_file(str(base_path))
        schema_result = analyze_blog.analyze_file(str(schema_path))

        assert schema_result["score"]["category_details"]["technical_elements"][
            "breakdown"
        ]["schema"] == base_result["score"]["category_details"][
            "technical_elements"
        ]["breakdown"]["schema"]


# ---------------------------------------------------------------------------
# Self-promotion analysis
# ---------------------------------------------------------------------------


class TestAnalyzeSelfPromotion:
    def test_no_promotions(self):
        result = analyze_blog.analyze_self_promotion("Generic content without brands.")
        assert result["exceeds_limit"] is False
        assert result["self_promotion_patterns"] == 0

    def test_returns_expected_keys(self):
        result = analyze_blog.analyze_self_promotion("Some content.", brand_name="Acme")
        assert "self_promotion_patterns" in result
        assert "exceeds_limit" in result


# ---------------------------------------------------------------------------
# Passive voice analysis
# ---------------------------------------------------------------------------


class TestAnalyzePassiveVoice:
    def test_detects_passive(self):
        text = "The report was written by the team. The data was analyzed carefully."
        result = analyze_blog.analyze_passive_voice(text)
        assert result["passive_count"] >= 1

    def test_active_voice(self):
        text = "The team wrote the report. Analysts reviewed the data."
        result = analyze_blog.analyze_passive_voice(text)
        assert result["passive_count"] == 0


# ---------------------------------------------------------------------------
# Transition words
# ---------------------------------------------------------------------------


class TestAnalyzeTransitionWords:
    def test_detects_transitions(self):
        text = "First, set up your blog. However, you should also consider SEO. Therefore, optimize early."
        result = analyze_blog.analyze_transition_words(text)
        assert result["transition_count"] >= 2

    def test_no_transitions(self):
        text = "Set up blog. Consider SEO. Optimize."
        result = analyze_blog.analyze_transition_words(text)
        assert result["transition_count"] == 0


# ---------------------------------------------------------------------------
# File analysis (integration)
# ---------------------------------------------------------------------------


class TestAnalyzeFile:
    def test_analyzes_real_file(self, tmp_path, sample_blog_post):
        post_file = tmp_path / "test-post.md"
        post_file.write_text(sample_blog_post)
        result = analyze_blog.analyze_file(str(post_file))
        assert "score" in result
        assert "headings" in result
        assert result["score"]["total"] >= 0

    def test_nonexistent_file(self):
        result = analyze_blog.analyze_file("/nonexistent/file.md")
        assert "error" in result

    def test_style_diagnostics_do_not_change_quality_score(self, tmp_path):
        base = """---
title: Evidence Based Content Review for Product Teams
description: A sourced review that explains how product teams evaluate content decisions with transparent evidence and practical examples.
author: Jane Doe
---
# Evidence Based Content Review

## Evidence review process

**Evidence review** is a documented check of a claim, its source, and its
practical implication. For example, teams can compare a public benchmark with
their own measurements and cite the [NIH](https://nih.gov/research) when a
health claim depends on primary guidance.

## Decision record

The decision record states what changed and why. It links the source, names the
assumption, and gives reviewers a useful example.
"""
        styled = base.replace(
            "The decision record states what changed and why.",
            "Furthermore, delve into the robust landscape with care.",
        )
        base_path = tmp_path / "base.md"
        styled_path = tmp_path / "styled.md"
        base_path.write_text(base, encoding="utf-8")
        styled_path.write_text(styled, encoding="utf-8")

        base_result = analyze_blog.analyze_file(str(base_path))
        styled_result = analyze_blog.analyze_file(str(styled_path))

        assert (
            base_result["score"]["category_details"]["content_quality"]["breakdown"]["grammar_antipattern"]
            == styled_result["score"]["category_details"]["content_quality"]["breakdown"]["grammar_antipattern"]
        )
        assert styled_result["ai_trigger_words"]["trigger_count"] > 0
        assert styled_result["ai_signals"]["likely_ai"] is None
        issue_text = " ".join(item["issue"] for item in styled_result["score"]["issues"]).lower()
        assert "trigger word" not in issue_text

    def test_faq_last_updated_and_padding_do_not_add_ai_points(self, tmp_path):
        base = """---
title: Evidence Based Content Review for Product Teams
description: A sourced review that explains how product teams evaluate content decisions with transparent evidence and practical examples.
author: Jane Doe
date: 2026-07-01
---
# Evidence Based Content Review

## Evidence review process

**Evidence review** is a documented check with a public source
[NIH](https://nih.gov/research) and a practical example for editors.

## Decision record

The record explains the decision and links [CDC guidance](https://cdc.gov/guidance).

## Publication check

Editors verify the claim, source, and reader action before publication.
"""
        padded = base.replace(
            "date: 2026-07-01",
            "date: 2026-07-01\nlastUpdated: 2026-07-23",
        ) + "\n## FAQ\n\n### Is this required?\n\n" + " ".join(["padding"] * 150)
        base_path = tmp_path / "base.md"
        padded_path = tmp_path / "padded.md"
        base_path.write_text(base, encoding="utf-8")
        padded_path.write_text(padded, encoding="utf-8")

        base_result = analyze_blog.analyze_file(str(base_path))
        padded_result = analyze_blog.analyze_file(str(padded_path))

        assert (
            base_result["score"]["categories"]["ai_citation_readiness"]
            == padded_result["score"]["categories"]["ai_citation_readiness"]
        )
        assert padded_result["methodology"]["calibrated_probability"] is False

    def test_neutral_sourced_article_is_not_told_to_claim_testing(self, tmp_path):
        post = """---
title: Neutral Source Review for Editorial Teams
description: A neutral and sourced explanation of editorial review methods for teams that need transparent, practical publishing decisions.
author: Jane Doe
---
# Neutral Source Review

## Source selection

Editors use primary guidance from the [CDC](https://cdc.gov/guidance) and
document how each source supports the page.

## Reader decision

The review explains the tradeoff with a concrete example and a clear next step.
"""
        path = tmp_path / "neutral.md"
        path.write_text(post, encoding="utf-8")

        result = analyze_blog.analyze_file(str(path))
        issue_text = " ".join(item["issue"] for item in result["score"]["issues"]).lower()

        assert "add \"we tested\"" not in issue_text
        assert "in our experience" not in issue_text
        assert "word count" not in issue_text

    def test_paragraph_padding_metric_does_not_change_score(self, tmp_path, sample_blog_post):
        post_file = tmp_path / "post.md"
        post_file.write_text(sample_blog_post, encoding="utf-8")
        analysis = analyze_blog.analyze_file(str(post_file))
        padded_metrics = copy.deepcopy(analysis)
        padded_metrics["paragraphs"]["max_word_count"] += 1_000
        padded_metrics["paragraphs"]["over_100_words"] += 1
        padded_metrics["paragraphs"]["over_150_words"] += 1

        baseline_score = analyze_blog.calculate_score(analysis)
        padded_score = analyze_blog.calculate_score(padded_metrics)

        assert padded_score["total"] == baseline_score["total"]
        assert padded_score["category_details"]["content_quality"]["breakdown"][
            "structure"
        ] == baseline_score["category_details"]["content_quality"]["breakdown"][
            "structure"
        ]
        assert padded_score["category_details"]["technical_elements"]["breakdown"][
            "mobile"
        ] == baseline_score["category_details"]["technical_elements"]["breakdown"][
            "mobile"
        ]

    def test_seo_length_number_and_exact_keyword_padding_add_no_points(self, tmp_path):
        base = """---
title: Evidence Review
description: Evidence review explains source decisions for editors.
author: Jane Doe
---
# Evidence Review

## Source decisions

Evidence review helps editors connect each material claim to supporting
guidance and explain the reader's next decision.
"""
        variants = {
            "base.md": base,
            "number.md": base.replace(
                "source decisions for editors.",
                "source decisions for editors in 2026.",
            ),
            "title-length.md": base.replace(
                "title: Evidence Review",
                "title: Evidence Review: Evidence Review for Evidence Review",
            ),
            "keyword.md": base.replace(
                "author: Jane Doe",
                "author: Jane Doe\nkeyword: evidence review",
            ).replace(
                "Evidence review helps editors",
                "Evidence review. Evidence review helps editors",
            ),
        }
        results = {}
        for name, content in variants.items():
            path = tmp_path / name
            path.write_text(content, encoding="utf-8")
            results[name] = analyze_blog.analyze_file(str(path))

        base_seo = results["base.md"]["score"]["category_details"][
            "seo_optimization"
        ]
        assert base_seo["breakdown"]["title"] == 4
        assert base_seo["breakdown"]["headings"] == 5
        assert base_seo["breakdown"]["keyword_placement"] == 4
        assert base_seo["breakdown"]["meta_description"] == 3
        for name in ("number.md", "title-length.md", "keyword.md"):
            seo = results[name]["score"]["category_details"]["seo_optimization"]
            assert seo["score"] == base_seo["score"]
            assert seo["breakdown"]["title"] == base_seo["breakdown"]["title"]
            assert seo["breakdown"]["keyword_placement"] == base_seo["breakdown"][
                "keyword_placement"
            ]
            assert seo["breakdown"]["meta_description"] == base_seo["breakdown"][
                "meta_description"
            ]
