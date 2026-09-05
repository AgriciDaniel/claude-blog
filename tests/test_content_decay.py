"""Tests for the content decay detection script."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import content_decay


ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"
SCRIPT = ROOT / "scripts" / "content_decay.py"


def _fixture(name: str) -> list[dict]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_analyze_decay_flags_threshold_dropouts_and_actions():
    report = content_decay.analyze_decay(
        _fixture("gsc_current.json"),
        _fixture("gsc_previous.json"),
    )

    assert report["summary"]["flagged_pages"] == 4
    assert report["summary"]["dropped_out_pages"] == 1

    by_page = {row["page"]: row for row in report["decays"]}
    assert "https://example.com/stable" not in by_page

    refresh = by_page["https://example.com/refresh-me"]
    assert refresh["severity"] == "high"
    assert refresh["decline_percent"] == 40.0
    assert refresh["recommended_action"] == "refresh/update content"

    query_shift = by_page["https://example.com/query-shift"]
    assert query_shift["severity"] == "critical"
    assert query_shift["recommended_action"] == "investigate query shift"

    drop_out = by_page["https://example.com/drop-out"]
    assert drop_out["dropped_out"] is True
    assert drop_out["recommended_action"] == "consolidate/redirect"

    prune = by_page["https://example.com/prune-me"]
    assert prune["recommended_action"] == "prune"


def test_analyze_decay_sorts_by_severity_then_decline():
    report = content_decay.analyze_decay(
        _fixture("gsc_current.json"),
        _fixture("gsc_previous.json"),
    )

    severities = [row["severity"] for row in report["decays"]]
    assert severities[:3] == ["critical", "critical", "critical"]
    assert severities[-1] == "high"
    assert report["decays"][0]["decline"] >= report["decays"][1]["decline"]


def test_load_export_accepts_gsc_rows_object(tmp_path: Path):
    export = tmp_path / "gsc.json"
    export.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "keys": ["https://example.com/from-keys"],
                        "clicks": 3,
                        "impressions": 40,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    rows = content_decay.load_export(export)
    pages = content_decay.aggregate_pages(rows)
    assert pages["https://example.com/from-keys"]["clicks"] == 3


def test_load_export_rejects_non_finite_json(tmp_path: Path):
    export = tmp_path / "nan.json"
    export.write_text(
        '[{"page": "https://example.com/nan", "clicks": NaN, "impressions": 10}]',
        encoding="utf-8",
    )

    with pytest.raises(content_decay.ContentDecayError, match="non-finite"):
        content_decay.load_export(export)


def test_load_export_refuses_symlink(tmp_path: Path):
    real = tmp_path / "real.json"
    real.write_text('[{"page": "https://example.com", "clicks": 1, "impressions": 1}]', encoding="utf-8")
    link = tmp_path / "current.json"
    try:
        link.symlink_to(real)
    except OSError:
        pytest.skip("symlinks not supported on this filesystem")
    with pytest.raises(content_decay.ContentDecayError, match="symlink"):
        content_decay.load_export(link)


def test_analyze_decay_rejects_non_finite_metric_value():
    current_rows = [
        {"page": "https://example.com/nan", "clicks": float("nan"), "impressions": 10}
    ]
    previous_rows = [
        {"page": "https://example.com/nan", "clicks": 10, "impressions": 20}
    ]

    with pytest.raises(content_decay.ContentDecayError, match="finite number"):
        content_decay.analyze_decay(current_rows, previous_rows)


def test_analyze_decay_rejects_page_missing_selected_metric():
    current_rows = [
        {"page": "https://example.com/missing", "impressions": 10}
    ]
    previous_rows = [
        {"page": "https://example.com/missing", "clicks": 10, "impressions": 20}
    ]

    with pytest.raises(content_decay.ContentDecayError, match="missing selected metric"):
        content_decay.analyze_decay(current_rows, previous_rows, metric="clicks")


def test_markdown_output_contains_table_and_recommendations():
    report = content_decay.analyze_decay(
        _fixture("gsc_current.json"),
        _fixture("gsc_previous.json"),
    )

    markdown = content_decay.format_markdown(report)
    assert "# Content Decay Report" in markdown
    assert "| Severity | Page | Previous | Current | Decline | Dropped out | Recommendation |" in markdown
    assert "investigate query shift" in markdown
    assert "https://example.com/drop-out" in markdown


def test_markdown_output_escapes_table_cells():
    page = "https://example.com/a|b\\c\nnext"
    report = content_decay.analyze_decay(
        [{"page": page, "clicks": 1, "impressions": 90}],
        [{"page": page, "clicks": 10, "impressions": 100}],
    )

    markdown = content_decay.format_markdown(report)

    assert "https://example.com/a\\|b\\\\c\\nnext" in markdown
    assert page not in markdown


def test_low_prior_demand_alone_does_not_recommend_prune():
    action, _reason = content_decay.recommend_action(
        metric="clicks",
        threshold=0.20,
        severity="warning",
        dropped_out=False,
        current={"clicks": 2.0, "impressions": 30.0},
        previous={"clicks": 2.0, "impressions": 30.0},
    )

    assert action != "prune"


def test_cli_writes_json_output(tmp_path: Path):
    output = tmp_path / "report.json"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(FIXTURES / "gsc_current.json"),
            str(FIXTURES / "gsc_previous.json"),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["summary"]["flagged_pages"] == 4
    assert report["decays"][0]["severity"] == "critical"


def test_cli_empty_input_returns_json_error(tmp_path: Path):
    empty = tmp_path / "empty.json"
    empty.write_text("[]", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(empty),
            str(FIXTURES / "gsc_previous.json"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert "error" in payload
    assert "contains no rows" in payload["error"]
