"""Adapter tests for the Claude Blog Brain domain pipeline."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ingest_blog_input import ValidationError, load_blog_input  # noqa: E402
from render_blog_report import render_markdown  # noqa: E402
from synthesize_blog_plan import has_intent_coverage, load_ingested, synthesize  # noqa: E402


FIXTURE = ROOT / "tests" / "fixtures" / "sample-blog-post.json"
PY = sys.executable


def run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def run_script(script: str, *args: str | Path) -> subprocess.CompletedProcess[str]:
    return run_cli([PY, f"scripts/{script}", *(str(arg) for arg in args)])


def assert_ok(proc: subprocess.CompletedProcess[str]) -> None:
    assert proc.returncode == 0, proc.stderr or proc.stdout


def assert_error_envelope(proc: subprocess.CompletedProcess[str]) -> dict[str, object]:
    assert proc.returncode == 2
    payload = json.loads(proc.stdout)
    assert payload["ok"] is False
    assert payload["errors"]
    return payload


def write_ingested(tmp_path: Path) -> Path:
    ingested = tmp_path / "ingested.json"
    proc = run_script("ingest_blog_input.py", FIXTURE, "-o", ingested)
    assert_ok(proc)
    return ingested


def write_plan(tmp_path: Path) -> Path:
    ingested = write_ingested(tmp_path)
    plan = tmp_path / "plan.json"
    proc = run_script("synthesize_blog_plan.py", ingested, "-o", plan)
    assert_ok(proc)
    return plan


def assert_domain_specific_plan(plan: dict[str, object]) -> None:
    assert plan["schema"] == "claude-blog-brain.blog-optimization-plan.v1"
    assert plan["adapter"] == "synthesize_blog_plan"
    assert set(plan["scores"]) >= {"overall", "content", "seo", "eeat", "technical", "ai_citation"}  # type: ignore[index]
    assert "geo_ai_citation_readiness" in plan
    assert "schema_recommendations" in plan
    assert "delivery_contract" in plan
    assert "source_citations" in plan


def assert_domain_specific_report(report: str) -> None:
    assert report.startswith("# Blog Optimization Plan:")
    assert "## Scorecard" in report
    assert "## Delivery Contract" in report
    assert "## GEO and AI Citation Readiness" in report
    assert "## Schema Recommendations" in report
    assert "## Source Citations" in report
    assert "`g-ai-opt-guide`" in report
    assert "`seer-aio-impact-ctr-2026`" in report


def test_blog_adapter_happy_path() -> None:
    record = load_blog_input(FIXTURE)
    plan = synthesize(record)
    report = render_markdown(plan)

    assert record["schema"] == "claude-blog-brain.ingested-blog-post.v1"
    assert record["input"]["target_keyword"] == "AI citation ready blog"
    assert record["provenance"]["source_count"] == 3
    assert_domain_specific_plan(plan)
    assert plan["geo_ai_citation_readiness"]["checks"][0]["name"] == "Passage extractability"
    assert any(item["schema_type"] == "FAQPage caveat" for item in plan["schema_recommendations"])
    assert "<table>" in report
    assert_domain_specific_report(report)
    assert "`g-helpful-content`" in report
    assert "`g-faqpage-sd`" in report


def test_blog_adapter_determinism() -> None:
    first_record = load_blog_input(FIXTURE)
    second_record = load_blog_input(FIXTURE)
    assert first_record == second_record

    first_plan = synthesize(first_record)
    second_plan = synthesize(second_record)
    assert first_plan == second_plan

    first_report = render_markdown(first_plan)
    second_report = render_markdown(second_plan)
    assert first_report == second_report
    assert "--" not in first_report
    assert "\u2014" not in first_report
    assert "\u2013" not in first_report


def test_blog_adapter_invalid_input_error(tmp_path: Path) -> None:
    bad_input = tmp_path / "bad-blog-post.json"
    bad_input.write_text(
        json.dumps(
            {
                "url": "not a url",
                "target_keyword": "AI citation ready blog",
                "locale": "english",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError) as excinfo:
        load_blog_input(bad_input)

    message = str(excinfo.value)
    assert "missing required key: title" in message
    assert "one of body_markdown or body_html is required" in message
    assert "url must be an absolute URI" in message


def test_blog_adapter_rejects_invalid_iso_dates(tmp_path: Path) -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["published_at"] = "2026-02-31"
    payload["frontmatter"]["dateModified"] = "June 10, 2026"
    bad_input = tmp_path / "bad-iso-date-blog-post.json"
    bad_input.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValidationError) as excinfo:
        load_blog_input(bad_input)

    assert "published_at" in str(excinfo.value)
    assert "frontmatter.dateModified" in str(excinfo.value)
    assert "ISO date or date-time" in str(excinfo.value)


def test_blog_adapter_rejects_non_http_url(tmp_path: Path) -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["url"] = "ftp://example.org/post"
    bad_input = tmp_path / "bad-url-blog-post.json"
    bad_input.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValidationError) as excinfo:
        load_blog_input(bad_input)

    assert "url must be an absolute URI" in str(excinfo.value) or "does not match" in str(excinfo.value)


def test_blog_adapter_rejects_wrong_typed_dates(tmp_path: Path) -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["published_at"] = 20260610
    bad_input = tmp_path / "bad-date-blog-post.json"
    bad_input.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValidationError) as excinfo:
        load_blog_input(bad_input)

    assert any(
        "published_at" in error and "string" in error
        for error in excinfo.value.errors
    )


def test_blog_synthesis_rejects_missing_nested_fields(tmp_path: Path) -> None:
    record = load_blog_input(FIXTURE)
    del record["input"]["title"]
    bad_record = tmp_path / "bad-ingested.json"
    bad_record.write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(ValidationError) as excinfo:
        load_ingested(bad_record)

    assert "ingested record missing key: input.title" in str(excinfo.value)


def test_unknown_audit_source_is_operator_supplied_uncited(tmp_path: Path) -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["audit_findings"][0]["source"] = "operator-note"
    bad_source_input = tmp_path / "operator-source-blog-post.json"
    bad_source_input.write_text(json.dumps(payload), encoding="utf-8")

    plan = synthesize(load_blog_input(bad_source_input))
    recommendation = next(item for item in plan["prioritized_recommendations"] if item["id"] == "audit-geo-source-context")

    assert recommendation["source_ids"] == []
    assert recommendation["recommendation"].startswith("operator-supplied (unverified):")
    assert "operator-note" not in {source["id"] for source in plan["source_citations"]}


def test_intent_coverage_does_not_require_exact_target_phrase() -> None:
    assert has_intent_coverage("AI citation ready blog", "Making posts quotable in AI answers", ["AI answers"])
    assert has_intent_coverage("Article schema", "Article schemas for authors and publishers", [])
    assert not has_intent_coverage("art", "article schema markup", [])


def test_ingest_script_cli_valid_output_and_determinism(tmp_path: Path) -> None:
    first = tmp_path / "ingested-first.json"
    second = tmp_path / "ingested-second.json"

    assert_ok(run_script("ingest_blog_input.py", FIXTURE, "-o", first))
    assert_ok(run_script("ingest_blog_input.py", FIXTURE, "-o", second))

    assert first.read_bytes() == second.read_bytes()
    record = json.loads(first.read_text(encoding="utf-8"))
    assert record["schema"] == "claude-blog-brain.ingested-blog-post.v1"
    assert record["adapter"] == "ingest_blog_input"
    assert record["content"]["headings"]
    assert record["signals"]["has_direct_intro_answer"] is True


def test_ingest_script_cli_malformed_input_json_error_envelope(tmp_path: Path) -> None:
    bad_input = tmp_path / "bad-input.json"
    bad_output = tmp_path / "bad-output.json"
    bad_input.write_text('{"title": "Broken"', encoding="utf-8")

    payload = assert_error_envelope(run_script("ingest_blog_input.py", bad_input, "-o", bad_output))

    assert "invalid JSON" in " ".join(str(error) for error in payload["errors"])  # type: ignore[index]
    assert not bad_output.exists()


def test_synthesize_script_cli_valid_output_and_determinism(tmp_path: Path) -> None:
    ingested = write_ingested(tmp_path)
    first = tmp_path / "plan-first.json"
    second = tmp_path / "plan-second.json"

    assert_ok(run_script("synthesize_blog_plan.py", ingested, "-o", first))
    assert_ok(run_script("synthesize_blog_plan.py", ingested, "-o", second))

    assert first.read_bytes() == second.read_bytes()
    plan = json.loads(first.read_text(encoding="utf-8"))
    assert_domain_specific_plan(plan)
    tactic_text = " ".join(item["tactic"] for item in plan["geo_ai_citation_readiness"]["being_cited_tactics"])
    assert "observed association" in tactic_text
    assert "causal or guaranteed" in tactic_text


def test_synthesize_script_cli_malformed_input_json_error_envelope(tmp_path: Path) -> None:
    bad_input = tmp_path / "bad-ingested.json"
    bad_output = tmp_path / "bad-plan.json"
    bad_input.write_text('{"schema": "claude-blog-brain.ingested-blog-post.v1"', encoding="utf-8")

    payload = assert_error_envelope(run_script("synthesize_blog_plan.py", bad_input, "-o", bad_output))

    assert "invalid JSON" in " ".join(str(error) for error in payload["errors"])  # type: ignore[index]
    assert not bad_output.exists()


def test_render_script_cli_valid_output_and_determinism(tmp_path: Path) -> None:
    plan = write_plan(tmp_path)
    first = tmp_path / "report-first.md"
    second = tmp_path / "report-second.md"

    assert_ok(run_script("render_blog_report.py", plan, "-o", first, "--json-errors"))
    assert_ok(run_script("render_blog_report.py", plan, "-o", second, "--json-errors"))

    assert first.read_bytes() == second.read_bytes()
    assert_domain_specific_report(first.read_text(encoding="utf-8"))


def test_render_script_cli_malformed_input_json_error_envelope(tmp_path: Path) -> None:
    bad_plan = tmp_path / "bad-plan.json"
    bad_output = tmp_path / "bad-report.md"
    bad_plan.write_text("{", encoding="utf-8")

    payload = assert_error_envelope(run_script("render_blog_report.py", bad_plan, "-o", bad_output, "--json-errors"))

    assert payload["errors"]
    assert not bad_output.exists()


def test_package_cli_blog_subcommands_write_domain_outputs(tmp_path: Path) -> None:
    ingested = tmp_path / "cli-ingested.json"
    plan = tmp_path / "cli-plan.json"
    report = tmp_path / "cli-report.md"

    assert_ok(run_cli([PY, "-m", "claude_blog_brain", "blog-ingest", str(FIXTURE), "--output", str(ingested)]))
    assert_ok(run_cli([PY, "-m", "claude_blog_brain", "blog-synthesize", str(ingested), "--output", str(plan)]))
    assert_ok(run_cli([PY, "-m", "claude_blog_brain", "blog-report", str(plan), "--output", str(report), "--json-errors"]))

    assert json.loads(ingested.read_text(encoding="utf-8"))["adapter"] == "ingest_blog_input"
    assert_domain_specific_plan(json.loads(plan.read_text(encoding="utf-8")))
    assert_domain_specific_report(report.read_text(encoding="utf-8"))


def test_package_cli_blog_pipeline_is_domain_specific_and_temp_only(tmp_path: Path) -> None:
    out_dir = tmp_path / "pipeline"
    proc = run_cli([PY, "-m", "claude_blog_brain", "blog-pipeline", "--input", str(FIXTURE), "--out-dir", str(out_dir)])
    assert_ok(proc)

    ingested = out_dir / "ingested-blog-post.json"
    plan = out_dir / "blog-optimization-plan.json"
    report = out_dir / "blog-optimization-report.md"
    assert ingested.exists()
    assert plan.exists()
    assert report.exists()
    assert_domain_specific_plan(json.loads(plan.read_text(encoding="utf-8")))
    assert_domain_specific_report(report.read_text(encoding="utf-8"))
    assert str(report) in proc.stdout
