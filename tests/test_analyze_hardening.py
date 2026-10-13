"""Hostile JSON-LD and batch isolation for scripts/analyze_blog.py.

Fixture content is untrusted: a single malformed page must neither crash its
own analysis nor abort a whole --batch run, and disclosing a method must not
lower the originality score (upstream PR #90, Hi-2025-Be).
"""

import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import analyze_blog


def _html(jsonld: str) -> str:
    return (
        "<!doctype html><html lang=\"en\"><head><title>Fixture post</title>"
        f"<script type=\"application/ld+json\">{jsonld}</script></head>"
        "<body><article><h1>Fixture post</h1><p>Plain body text for the fixture.</p>"
        "</article></body></html>"
    )


GOOD_MD = "---\ntitle: Good post\ndescription: A fine post.\n---\n\n## Section\n\nSome body text here.\n"


# --- Item 3: @type guard and RecursionError --------------------------------


@pytest.mark.parametrize("bad_type", ["5", "null", "true", "{\"a\": 1}", "[5, null, {\"x\": 1}]", "1.5"])
def test_non_string_jsonld_type_does_not_raise(tmp_path, bad_type):
    page = tmp_path / "bad.html"
    page.write_text(
        _html('{"@type": %s, "headline": "Typed headline"}' % bad_type), encoding="utf-8"
    )
    result = analyze_blog.analyze_file(str(page))
    assert "error" not in result
    assert result["schema"]["schema_count"] == 0


def test_list_jsonld_type_keeps_string_members(tmp_path):
    page = tmp_path / "mixed.html"
    page.write_text(
        _html('{"@type": ["BlogPosting", 5, null], "description": "Mixed description"}'),
        encoding="utf-8",
    )
    result = analyze_blog.analyze_file(str(page))
    assert "error" not in result
    assert result["schema"]["schemas_found"] == ["BlogPosting"]
    assert result["frontmatter"]["description"] == "Mixed description"


def test_deeply_nested_jsonld_is_ignored_not_fatal(tmp_path):
    depth = 20000
    nested = "[" * depth + "]" * depth
    page = tmp_path / "deep.html"
    page.write_text(_html(nested), encoding="utf-8")
    result = analyze_blog.analyze_file(str(page))
    assert "error" not in result
    assert result["schema"]["schema_count"] == 0


def test_analyze_schema_survives_deep_nesting_in_fallback_parser(monkeypatch):
    monkeypatch.setattr(analyze_blog, "HAS_BS4", False)
    depth = 20000
    content = _html("[" * depth + "]" * depth)
    assert analyze_blog.analyze_schema(content)["schema_count"] == 0


def test_batch_continues_past_bad_file_and_reports_its_error(tmp_path, monkeypatch):
    (tmp_path / "a-good.md").write_text(GOOD_MD, encoding="utf-8")
    (tmp_path / "b-bad.html").write_text(_html('{"@type": 5}'), encoding="utf-8")
    (tmp_path / "c-good.md").write_text(GOOD_MD, encoding="utf-8")
    real = analyze_blog.analyze_file

    def flaky(file_path):
        if file_path.endswith("b-bad.html"):
            raise RuntimeError("simulated analyzer crash")
        return real(file_path)

    monkeypatch.setattr(analyze_blog, "analyze_file", flaky)
    batch = analyze_blog._process_batch(tmp_path, "name")

    assert batch["count"] == 3
    by_name = {Path(item["file"]).name: item for item in batch["results"]}
    assert "error" not in by_name["a-good.md"] and "error" not in by_name["c-good.md"]
    assert "simulated analyzer crash" in by_name["b-bad.html"]["error"]


def test_batch_with_hostile_jsonld_end_to_end(tmp_path):
    (tmp_path / "a.md").write_text(GOOD_MD, encoding="utf-8")
    (tmp_path / "b.html").write_text(_html('{"@type": 5}'), encoding="utf-8")
    (tmp_path / "c.html").write_text(_html("[" * 20000 + "]" * 20000), encoding="utf-8")
    batch = analyze_blog._process_batch(tmp_path, "name")
    assert batch["count"] == 3
    assert all("score" in item for item in batch["results"])
    json.dumps(batch)


# --- Item 4: methodology bonus never replaces the synthesis floor ----------
# Equivalent of upstream PR #90 test_methodology_section_never_lowers_originality.


def test_methodology_section_never_lowers_originality(tmp_path, sample_blog_post):
    post_file = tmp_path / "post.md"
    post_file.write_text(sample_blog_post, encoding="utf-8")
    analysis = analyze_blog.analyze_file(str(post_file))
    # A sourced explainer with an example and no evidence tags earns the synthesis floor.
    analysis["originality"]["evidence_marker_count"] = 0
    analysis["citations"]["unique_sources"] = 2
    analysis["engagement"]["example_count"] = 1
    without_method = copy.deepcopy(analysis)
    without_method["originality"]["methodology_count"] = 0
    with_method = copy.deepcopy(analysis)
    with_method["originality"]["methodology_count"] = 1

    def originality(metrics):
        score = analyze_blog.calculate_score(metrics)
        return score["category_details"]["content_quality"]["breakdown"]["originality"]

    assert originality(without_method) == 3
    assert originality(with_method) == min(5, originality(without_method) + 1)
