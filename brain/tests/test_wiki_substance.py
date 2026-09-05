"""Tests for wiki substance scoring."""
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_brain import check_wiki_substance  # noqa: E402


def write_source_ledger(root: Path, sources: dict[str, str]) -> None:
    references = root / "references"
    references.mkdir(parents=True)
    payload = {
        "sources": [
            {"id": source_id, "url": url}
            for source_id, url in sorted(sources.items())
        ]
    }
    (references / "source-ledger.json").write_text(json.dumps(payload), encoding="utf-8")


def unique_words(seed: str, count: int = 135) -> str:
    return " ".join(f"{seed}-substance-{index}" for index in range(count))


def write_spoke(
    root: Path,
    folder: str,
    title: str,
    source_ids: list[str],
    body: str,
    source_urls: list[str] | None = None,
) -> Path:
    path = root / "wiki" / folder / f"{title}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    citations = ", ".join(source_ids)
    source_url_block = ""
    if source_urls:
        quoted_urls = "\n".join(f'  - "{source_url}"' for source_url in source_urls)
        source_url_block = f"source_urls:\n{quoted_urls}\n"
    path.write_text(
        f"""---
type: spoke
title: "{title}"
domain: "Fixture Domain"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [fixture, active]
{source_url_block}---
{body}

Source ledger IDs: {citations}
""",
        encoding="utf-8",
    )
    return path


def clean_body(title: str, seed: str) -> str:
    return f"""# {title}

## {title} Evidence Table

| Check | Specific action |
|---|---|
| {seed} proof | Record dated evidence before the recommendation is used. |

## {title} Operating Notes

{unique_words(seed)}
"""


def cloned_body(title: str) -> str:
    shared = unique_words("shared-clone", 150)
    return f"""# {title}

## Shared Evidence Table

| Check | Specific action |
|---|---|
| clone proof | Record dated evidence before the recommendation is used. |

## Shared Operating Notes

{shared}
"""


def test_clean_distinct_spoke_set_passes(tmp_path: Path) -> None:
    sources = {
        "g-intro-sd-2026-note": "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data",
        "g-intro-sd": "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data",
        "g-search-gallery-2026-note": "https://developers.google.com/search/docs/appearance/structured-data/search-gallery",
        "g-search-gallery": "https://developers.google.com/search/docs/appearance/structured-data/search-gallery",
        "schema-full": "https://schema.org/docs/full.html",
        "w3c-jsonld": "https://www.w3.org/TR/json-ld11/",
    }
    write_source_ledger(tmp_path, sources)
    shared_set = ["g-intro-sd", "g-search-gallery", "schema-full", "w3c-jsonld"]
    shared_urls = [sources[source_id] for source_id in shared_set]
    write_spoke(tmp_path, "schema", "Article Schema", shared_set, clean_body("Article Schema", "article-schema"), shared_urls)
    write_spoke(tmp_path, "schema", "Product Schema", shared_set, clean_body("Product Schema", "product-schema"), shared_urls)
    write_spoke(tmp_path, "schema", "Video Schema", shared_set, clean_body("Video Schema", "video-schema"), shared_urls)
    write_spoke(tmp_path, "schema", "Breadcrumb Schema", shared_set, clean_body("Breadcrumb Schema", "breadcrumb-schema"), shared_urls)

    ok, score, notes, critical, details = check_wiki_substance(tmp_path)

    assert ok is True
    assert score == 100
    assert notes == []
    assert critical == []
    assert details["metrics"]["spoke_count"] == 4
    assert details["metrics"]["near_duplicate_pairs"] == 0
    assert details["metrics"]["table_or_procedure_coverage"] == 1.0
    assert details["metrics"]["specific_citation_coverage"] == 1.0
    assert details["metrics"]["generic_bundle_reuse"] == 0
    assert details["metrics"]["density_floor"] >= 120


def test_identical_large_citation_set_reuse_fails_generic_bundle(tmp_path: Path) -> None:
    sources = {
        "source-alpha": "https://example.org/source-alpha",
        "source-beta": "https://example.org/source-beta",
        "source-delta": "https://example.org/source-delta",
        "source-epsilon": "https://example.org/source-epsilon",
        "source-gamma": "https://example.org/source-gamma",
        "source-zeta": "https://example.org/source-zeta",
    }
    write_source_ledger(tmp_path, sources)
    shared_set = [
        "source-alpha",
        "source-beta",
        "source-delta",
        "source-epsilon",
        "source-gamma",
        "source-zeta",
    ]
    write_spoke(tmp_path, "concepts", "Bundle One", shared_set, clean_body("Bundle One", "bundle-one"))
    write_spoke(tmp_path, "writing", "Bundle Two", shared_set, clean_body("Bundle Two", "bundle-two"))
    write_spoke(tmp_path, "schema", "Bundle Three", shared_set, clean_body("Bundle Three", "bundle-three"))
    write_spoke(tmp_path, "eeat", "Bundle Four", shared_set, clean_body("Bundle Four", "bundle-four"))

    ok, score, notes, critical, details = check_wiki_substance(tmp_path)

    assert ok is False
    assert score < 100
    assert critical == []
    assert details["metrics"]["generic_bundle_reuse"] == 4
    assert details["metrics"]["specific_citation_coverage"] == 0.0
    assert details["offenders"]["generic_bundle_reuse"]["source_ids"] == sorted(shared_set)
    assert len(details["offenders"]["generic_bundle_reuse"]["paths"]) == 4
    assert any("generic source bundle reused by 4 spoke notes" == note for note in notes)


def test_near_duplicate_spoke_pair_fails_with_critical(tmp_path: Path) -> None:
    sources = {
        "source-alpha": "https://example.org/source-alpha",
        "source-beta": "https://example.org/source-beta",
        "source-gamma": "https://example.org/source-gamma",
    }
    write_source_ledger(tmp_path, sources)
    write_spoke(tmp_path, "concepts", "Clone One", ["source-alpha", "source-beta"], cloned_body("Clone One"))
    write_spoke(tmp_path, "writing", "Clone Two", ["source-alpha", "source-beta"], cloned_body("Clone Two"))
    write_spoke(tmp_path, "schema", "Distinct Note", ["source-alpha", "source-gamma"], clean_body("Distinct Note", "distinct"))

    ok, score, notes, critical, details = check_wiki_substance(tmp_path)

    assert ok is False
    assert score <= 40
    assert details["metrics"]["near_duplicate_pairs"] == 1
    assert critical
    assert "wiki_substance near_duplicate_pairs=1" in critical[0]
    pair_paths = details["offenders"]["near_duplicate_pairs"][0]["paths"]
    assert "wiki/concepts/Clone One.md" in pair_paths
    assert "wiki/writing/Clone Two.md" in pair_paths
    assert any("near duplicate spoke pairs: 1" == note for note in notes)
