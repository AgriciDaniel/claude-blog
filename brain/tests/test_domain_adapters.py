"""Subprocess tests for topic cluster and GEO domain adapters."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
TOPIC_FIXTURE = ROOT / "tests" / "fixtures" / "sample-topic-cluster-plan.json"
GEO_FIXTURE = ROOT / "tests" / "fixtures" / "sample-geo-citation-audit.json"


def run_cli(args: list[str | Path]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(arg) for arg in args], cwd=ROOT, text=True, capture_output=True, check=False)


def run_script(script: str, *args: str | Path) -> subprocess.CompletedProcess[str]:
    return run_cli([PY, f"scripts/{script}", *args])


def assert_ok(proc: subprocess.CompletedProcess[str]) -> None:
    assert proc.returncode == 0, proc.stderr or proc.stdout


def assert_error_envelope(proc: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    assert proc.returncode == 2
    payload = json.loads(proc.stdout)
    assert payload["ok"] is False
    assert payload["errors"]
    return payload


def assert_clean_report(report: str) -> None:
    assert "\u2014" not in report
    assert "\u2013" not in report
    assert "--" not in report


def assert_all_sources_cited(plan: dict[str, Any]) -> None:
    citation_ids = {source["id"] for source in plan["source_citations"]}
    assert citation_ids
    for section_name in ("recommendations", "checks", "cluster_quality", "internal_link_matrix"):
        for item in plan.get(section_name, []):
            if "source_ids" in item:
                assert item["source_ids"], item
                assert set(item["source_ids"]) <= citation_ids


def test_topic_cluster_scripts_valid_deterministic_output_and_citations(tmp_path: Path) -> None:
    first_ingested = tmp_path / "topic-ingested-first.json"
    second_ingested = tmp_path / "topic-ingested-second.json"
    assert_ok(run_script("ingest_topic_cluster_input.py", TOPIC_FIXTURE, "-o", first_ingested))
    assert_ok(run_script("ingest_topic_cluster_input.py", TOPIC_FIXTURE, "-o", second_ingested))
    assert first_ingested.read_bytes() == second_ingested.read_bytes()

    ingested = json.loads(first_ingested.read_text(encoding="utf-8"))
    assert ingested["schema"] == "claude-blog-brain.ingested-topic-cluster.v1"
    assert ingested["adapter"] == "ingest_topic_cluster_input"
    assert ingested["signals"]["spoke_count"] == 3

    first_plan = tmp_path / "topic-plan-first.json"
    second_plan = tmp_path / "topic-plan-second.json"
    assert_ok(run_script("synthesize_topic_cluster.py", first_ingested, "-o", first_plan))
    assert_ok(run_script("synthesize_topic_cluster.py", first_ingested, "-o", second_plan))
    assert first_plan.read_bytes() == second_plan.read_bytes()

    plan = json.loads(first_plan.read_text(encoding="utf-8"))
    assert plan["schema"] == "claude-blog-brain.topic-cluster-plan.v1"
    assert plan["adapter"] == "synthesize_topic_cluster"
    assert plan["internal_link_matrix"]
    assert plan["recommendations"]
    assert_all_sources_cited(plan)

    first_report = tmp_path / "topic-report-first.md"
    second_report = tmp_path / "topic-report-second.md"
    assert_ok(run_script("render_topic_cluster_report.py", first_plan, "-o", first_report))
    assert_ok(run_script("render_topic_cluster_report.py", first_plan, "-o", second_report))
    assert first_report.read_bytes() == second_report.read_bytes()
    report = first_report.read_text(encoding="utf-8")
    assert report.startswith("# Topic Cluster Internal Link Matrix:")
    assert "## Internal Link Matrix" in report
    assert "`dfs-labs`" in report
    assert "`g-helpful-content`" in report
    assert_clean_report(report)


def test_topic_cluster_malformed_input_json_error_envelope(tmp_path: Path) -> None:
    bad_input = tmp_path / "bad-topic.json"
    bad_output = tmp_path / "bad-topic-output.json"
    bad_input.write_text('{"cluster_name": "Broken"', encoding="utf-8")

    payload = assert_error_envelope(
        run_script("ingest_topic_cluster_input.py", bad_input, "-o", bad_output, "--json")
    )

    assert "invalid JSON" in " ".join(str(error) for error in payload["errors"])
    assert not bad_output.exists()


def test_geo_scripts_valid_deterministic_output_and_citations(tmp_path: Path) -> None:
    first_ingested = tmp_path / "geo-ingested-first.json"
    second_ingested = tmp_path / "geo-ingested-second.json"
    assert_ok(run_script("ingest_geo_citation_audit.py", GEO_FIXTURE, "-o", first_ingested))
    assert_ok(run_script("ingest_geo_citation_audit.py", GEO_FIXTURE, "-o", second_ingested))
    assert first_ingested.read_bytes() == second_ingested.read_bytes()

    ingested = json.loads(first_ingested.read_text(encoding="utf-8"))
    assert ingested["schema"] == "claude-blog-brain.ingested-geo-citation-audit.v1"
    assert ingested["adapter"] == "ingest_geo_citation_audit"
    assert ingested["signals"]["passage_count"] == 3

    first_plan = tmp_path / "geo-plan-first.json"
    second_plan = tmp_path / "geo-plan-second.json"
    assert_ok(run_script("synthesize_geo_citation_readiness.py", first_ingested, "-o", first_plan))
    assert_ok(run_script("synthesize_geo_citation_readiness.py", first_ingested, "-o", second_plan))
    assert first_plan.read_bytes() == second_plan.read_bytes()

    plan = json.loads(first_plan.read_text(encoding="utf-8"))
    assert plan["schema"] == "claude-blog-brain.geo-citation-readiness.v1"
    assert plan["adapter"] == "synthesize_geo_citation_readiness"
    assert plan["readiness_score"] < 100
    assert plan["recommendations"]
    assert_all_sources_cited(plan)

    first_report = tmp_path / "geo-report-first.md"
    second_report = tmp_path / "geo-report-second.md"
    assert_ok(run_script("render_geo_citation_report.py", first_plan, "-o", first_report))
    assert_ok(run_script("render_geo_citation_report.py", first_plan, "-o", second_report))
    assert first_report.read_bytes() == second_report.read_bytes()
    report = first_report.read_text(encoding="utf-8")
    assert report.startswith("# GEO Citation Readiness Report:")
    assert "## Readiness Checks" in report
    assert "`g-ai-opt-guide`" in report
    assert "`ziptie-aio-source-selection`" in report
    assert_clean_report(report)


def test_geo_malformed_input_json_error_envelope(tmp_path: Path) -> None:
    bad_input = tmp_path / "bad-geo.json"
    bad_output = tmp_path / "bad-geo-output.json"
    bad_input.write_text('{"audit_name": "Broken"', encoding="utf-8")

    payload = assert_error_envelope(
        run_script("ingest_geo_citation_audit.py", bad_input, "-o", bad_output, "--json")
    )

    assert "invalid JSON" in " ".join(str(error) for error in payload["errors"])
    assert not bad_output.exists()


def test_package_cli_new_adapter_subcommands_write_domain_outputs(tmp_path: Path) -> None:
    topic_ingested = tmp_path / "cli-topic-ingested.json"
    topic_plan = tmp_path / "cli-topic-plan.json"
    topic_report = tmp_path / "cli-topic-report.md"
    assert_ok(run_cli([PY, "-m", "claude_blog_brain", "cluster-ingest", TOPIC_FIXTURE, "--output", topic_ingested]))
    assert_ok(run_cli([PY, "-m", "claude_blog_brain", "cluster-synthesize", topic_ingested, "--output", topic_plan]))
    assert_ok(run_cli([PY, "-m", "claude_blog_brain", "cluster-report", topic_plan, "--output", topic_report]))
    assert json.loads(topic_plan.read_text(encoding="utf-8"))["schema"] == "claude-blog-brain.topic-cluster-plan.v1"
    assert "Topic Cluster Internal Link Matrix" in topic_report.read_text(encoding="utf-8")

    geo_ingested = tmp_path / "cli-geo-ingested.json"
    geo_plan = tmp_path / "cli-geo-plan.json"
    geo_report = tmp_path / "cli-geo-report.md"
    assert_ok(run_cli([PY, "-m", "claude_blog_brain", "geo-ingest", GEO_FIXTURE, "--output", geo_ingested]))
    assert_ok(run_cli([PY, "-m", "claude_blog_brain", "geo-synthesize", geo_ingested, "--output", geo_plan]))
    assert_ok(run_cli([PY, "-m", "claude_blog_brain", "geo-report", geo_plan, "--output", geo_report]))
    assert json.loads(geo_plan.read_text(encoding="utf-8"))["schema"] == "claude-blog-brain.geo-citation-readiness.v1"
    assert "GEO Citation Readiness Report" in geo_report.read_text(encoding="utf-8")


def test_package_cli_new_pipelines_are_domain_specific(tmp_path: Path) -> None:
    topic_dir = tmp_path / "topic-pipeline"
    topic_proc = run_cli([PY, "-m", "claude_blog_brain", "cluster-pipeline", "--input", TOPIC_FIXTURE, "--out-dir", topic_dir])
    assert_ok(topic_proc)
    topic_report = topic_dir / "topic-cluster-internal-link-matrix.md"
    assert topic_report.exists()
    assert "Topic Cluster Internal Link Matrix" in topic_report.read_text(encoding="utf-8")
    assert str(topic_report) in topic_proc.stdout

    geo_dir = tmp_path / "geo-pipeline"
    geo_proc = run_cli([PY, "-m", "claude_blog_brain", "geo-pipeline", "--input", GEO_FIXTURE, "--out-dir", geo_dir])
    assert_ok(geo_proc)
    geo_report = geo_dir / "geo-citation-readiness-report.md"
    assert geo_report.exists()
    assert "GEO Citation Readiness Report" in geo_report.read_text(encoding="utf-8")
    assert str(geo_report) in geo_proc.stdout
