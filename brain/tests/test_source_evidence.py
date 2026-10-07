"""Behavioral regressions for lifecycle, freshness, and reviewed evidence."""
import copy
import importlib
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evidence_fixtures import reviewed_source
from source_evidence import can_support, ledger_errors, source_errors
from verify_source_ledger import offline_check

MODULES = ["synthesize_blog_plan", "synthesize_topic_cluster", "synthesize_geo_citation_readiness"]


@pytest.mark.parametrize("module_name,ingester,loader,fixture", [
    ("synthesize_blog_plan", "ingest_blog_input", "load_blog_input", "sample-blog-post.json"),
    ("synthesize_topic_cluster", "ingest_topic_cluster_input", "load_topic_cluster_input", "sample-topic-cluster-plan.json"),
    ("synthesize_geo_citation_readiness", "ingest_geo_citation_audit", "load_geo_citation_audit", "sample-geo-citation-audit.json"),
])
def test_required_policy_gap_blocks_complete_synthesis(module_name, ingester, loader, fixture, tmp_path):
    # Valid independent evidence for every known ID isolates the lifecycle
    # defect from the real ledger's changing freshness and review schedule.
    original = json.loads((ROOT / "references" / "source-ledger.json").read_text())
    sources = [reviewed_source(source["id"]) for source in original["sources"]]
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"sources": sources}))
    module = importlib.import_module(module_name)
    record = getattr(importlib.import_module(ingester), loader)(ROOT / "tests" / "fixtures" / fixture)
    valid = module.synthesize(record, ledger_path=ledger)
    assert valid["source_citations"]
    required = next(source for source in sources if source["id"] == "g-helpful-content")
    required["status"] = "unverified"
    ledger.write_text(json.dumps({"sources": sources}))
    with pytest.raises(module.SourceError, match="g-helpful-content"):
        module.synthesize(record, ledger_path=ledger)


@pytest.mark.parametrize("module_name", MODULES)
@pytest.mark.parametrize("defect", ["retired", "unverified", "expired", "decision", "hash", "excerpt"])
def test_all_adapters_reject_unavailable_citation(module_name, defect, tmp_path):
    source = reviewed_source()
    if defect in {"retired", "unverified"}:
        source["status"] = defect
    elif defect == "expired":
        source["refresh_due"] = (date.today() - timedelta(days=1)).isoformat()
    elif defect == "decision":
        source["verification"]["decision"] = "unverified"
    elif defect == "hash":
        source["verification"]["normalized_content_sha256"] = "bogus"
    else:
        source["verification"].pop("evidence_excerpt")
    path = tmp_path / "ledger.json"
    path.write_text(json.dumps({"sources": [source]}))
    module = importlib.import_module(module_name)
    index = module.load_source_index(path)
    with pytest.raises(module.SourceError, match="source-alpha"):
        module.source_citations([source["id"]], index)


@pytest.mark.parametrize("module_name", MODULES)
def test_duplicate_source_ids_never_overwrite_reviewed_record(module_name, tmp_path):
    good = reviewed_source()
    other = copy.deepcopy(good)
    other["status"] = "retired"
    path = tmp_path / "ledger.json"
    path.write_text(json.dumps({"sources": [good, other]}))
    module = importlib.import_module(module_name)
    with pytest.raises(module.SourceError, match="duplicate source ID"):
        module.load_source_index(path)


def test_offline_accepts_reasoned_archive_without_invented_dates():
    good = reviewed_source()
    retired = {"id": "old", "status": "retired", "retirement_reason": "Superseded by the reviewed original.", "retired_on": date.today().isoformat(), "replacement_source_ids": [good["id"]]}
    result = offline_check({"sources": [good, retired]}, date.today())
    assert result["status"] == "pass"
    assert result["verified"] == 1
    assert result["evidence_validation"]["captured_artifacts_checked"] is False
    assert result["evidence_validation"]["mode"] == "review_record"
    assert not can_support(retired)
    retired["replacement_source_ids"] = ["missing"]
    assert offline_check({"sources": [good, retired]}, date.today())["status"] == "fail"


@pytest.mark.parametrize("mutate", [
    lambda s: s.update(status="mystery"),
    lambda s: s.update(status=[]),
    lambda s: s["verification"].update(decision="fetched"),
    lambda s: s["verification"].update(reviewed_on=(date.today() + timedelta(days=1)).isoformat()),
    lambda s: s["verification"].update(reviewed_on="2026-02-31"),
    lambda s: s["verification"].update(normalized_content_sha256="invalid"),
    lambda s: s["verification"].update(evidence_path="../outside.txt"),
    lambda s: s["verification"].update(evidence_path="C:/outside.txt"),
    lambda s: s["verification"].update(evidence_path="https://example.org/evidence.txt"),
    lambda s: s.update(refresh_due="2000-01-01"),
    lambda s: s.update(supports_claims=["Only an unrelated claim."]),
    lambda s: s.update(published="2099-01-01"),
])
def test_offline_rejects_invalid_review_state(mutate):
    source = reviewed_source()
    mutate(source)
    result = offline_check({"sources": [source]}, date.today())
    assert result["status"] == "fail"
    assert result["verified"] == 0
    assert result["failures"]


def test_qualification_requires_narrowed_supported_scope_and_limits():
    source = reviewed_source()
    source["verification"]["decision"] = "qualified"
    assert source_errors(source)
    source["limitations"] = "Supports only this narrow scope, not product availability in every account."
    assert can_support(source)
    source["claims"].append("Unsupported extra promise.")
    assert not can_support(source)


def test_operator_findings_stay_unverified_with_known_unavailable_id():
    from synthesize_blog_plan import audit_source_ids, apply_audit_findings
    source = reviewed_source()
    source["status"] = "unverified"
    finding = {"id": "x", "category": "content", "severity": "high", "summary": "Supplied claim", "recommendation": "Apply supplied advice", "source": source["id"]}
    assert audit_source_ids(finding, {source["id"]: source}) == []
    class CapturingBuilder:
        def add(self, **kwargs):
            self.item = kwargs
    builder = CapturingBuilder()
    apply_audit_findings({"audit_findings": [finding]}, {"content": builder}, {source["id"]: source})
    assert builder.item["source_ids"] == []
    assert builder.item["recommendation"].startswith("operator-supplied (unverified):")
    source["status"] = "active"
    apply_audit_findings({"audit_findings": [finding]}, {"content": builder}, {source["id"]: source})
    assert builder.item["source_ids"] == [source["id"]]
    assert builder.item["recommendation"].startswith("operator-supplied (unverified):")


def test_retired_records_cannot_pass_official_audit_minimum(tmp_path, monkeypatch):
    import audit_brain
    references = tmp_path / "references"
    references.mkdir()
    sources = [reviewed_source("old-one"), reviewed_source("old-two")]
    for source in sources:
        source.update(status="retired", retired_on=date.today().isoformat(), retirement_reason="Old historical record", replacement_source_ids=["missing"])
    (references / "source-ledger.json").write_text(json.dumps({"sources": sources}))
    monkeypatch.setattr(audit_brain, "REPO", tmp_path)
    ok, score, notes, critical = audit_brain.check_source_ledger(requires_fresh=True)
    assert not ok
    assert any("at least 2 official/primary" in error for error in critical)
    assert any("g-helpful-content" in error for error in critical)


def test_wiki_index_excludes_unreviewed_and_retired_sources(tmp_path):
    from audit_brain import load_source_index
    references = tmp_path / "references"
    references.mkdir()
    active = reviewed_source()
    unavailable = reviewed_source("old")
    unavailable["status"] = "retired"
    (references / "source-ledger.json").write_text(json.dumps({"sources": [active, unavailable]}))
    ids, urls = load_source_index(tmp_path)
    assert ids == {active["id"]}


def test_current_wiki_cannot_cite_retired_evidence_but_archive_can(tmp_path, monkeypatch):
    import audit_brain
    references = tmp_path / "references"
    references.mkdir()
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    active = reviewed_source("replacement")
    retired = {"id": "old", "url": "https://developers.google.com/search/docs/retired", "status": "retired", "retired_on": date.today().isoformat(), "retirement_reason": "Replaced by reviewed original", "replacement_source_ids": ["replacement"]}
    (references / "source-ledger.json").write_text(json.dumps({"sources": [active, retired]}))
    note = wiki / "History.md"
    note.write_text("---\nstatus: active\n---\nCurrent advice cites `old`.\n")
    monkeypatch.setattr(audit_brain, "REPO", tmp_path)
    assert not audit_brain.check_citations()[0]
    assert any("old" in item for item in audit_brain.check_citations()[3])
    note.write_text("---\nstatus: archived\n---\nHistorical withdrawn source `old`.\n")
    assert audit_brain.check_citations()[0]


@pytest.mark.parametrize("module_name,renderer_name", [
    ("synthesize_blog_plan", "render_blog_report"),
    ("synthesize_topic_cluster", "render_topic_cluster_report"),
    ("synthesize_geo_citation_readiness", "render_geo_citation_report"),
])
def test_qualified_citations_preserve_narrow_scope_and_render_limits(module_name, renderer_name):
    source = reviewed_source()
    source["verification"]["decision"] = "qualified"
    source["limitations"] = "Practitioner editorial heuristic, no validated citation gain."
    module = importlib.import_module(module_name)
    citations = module.source_citations([source["id"]], {source["id"]: source})
    assert citations[0]["supported_claims"] == source["supports_claims"]
    assert citations[0]["limitations"] == source["limitations"]
    renderer = importlib.import_module(renderer_name)
    # Render a genuine adapter plan, then substitute the specifically qualified
    # citation to exercise the actual public report path for every renderer.
    choices = {
        "synthesize_blog_plan": ("ingest_blog_input", "load_blog_input", "sample-blog-post.json"),
        "synthesize_topic_cluster": ("ingest_topic_cluster_input", "load_topic_cluster_input", "sample-topic-cluster-plan.json"),
        "synthesize_geo_citation_readiness": ("ingest_geo_citation_audit", "load_geo_citation_audit", "sample-geo-citation-audit.json"),
    }
    ingester, loader, fixture = choices[module_name]
    record = getattr(importlib.import_module(ingester), loader)(ROOT / "tests" / "fixtures" / fixture)
    plan = module.synthesize(record)
    plan["source_citations"] = citations
    report = renderer.render_markdown(plan)
    assert "Qualified scope:" in report
    assert source["limitations"] in report
    assert source["supports_claims"][0] in report


def setup_live_review(tmp_path, monkeypatch, sources, decisions, evidence=None, dispositions=None):
    import verify_source_ledger as verifier
    ledger = tmp_path / "ledger.json"
    review = tmp_path / "review.json"
    ledger.write_text(json.dumps({"sources": sources, "last_verified": "2000-01-01"}))
    review.write_text(json.dumps({"reviewed_on": date.today().isoformat(), **decisions, "evidence": evidence or {}, "dispositions": dispositions or {}}))
    monkeypatch.setattr(verifier, "REPO", tmp_path)
    monkeypatch.setattr(verifier, "LEDGER_PATH", ledger)
    return verifier, ledger, ["--review-file", "review.json", "--apply"]


def test_retirement_does_not_fetch_or_fabricate_retrieval(tmp_path, monkeypatch, capsys):
    original = reviewed_source("old")
    replacement = reviewed_source("replacement")
    verifier, path, args = setup_live_review(tmp_path, monkeypatch, [original, replacement], {"retired": ["old"]}, dispositions={"old": {"retirement_reason": "Redundant historical secondary", "replacement_source_ids": ["replacement"]}})
    def forbidden_fetch(url):
        raise AssertionError("retirement must not fetch")
    monkeypatch.setattr(verifier, "fetch_source", forbidden_fetch)
    assert verifier.main(args) == 0
    ledger = json.loads(path.read_text())
    retired = ledger["sources"][0]
    assert retired["verification"] == original["verification"]
    assert retired["retrieved"] == original["retrieved"]
    assert retired["status"] == "retired"
    assert json.loads(capsys.readouterr().out)["unique_urls"] == 0


def test_failed_fetch_preserves_evidence_and_global_date(tmp_path, monkeypatch, capsys):
    source = reviewed_source()
    verifier, path, args = setup_live_review(tmp_path, monkeypatch, [source], {"confirmed_by_manual_review": [source["id"]]})
    def failed_fetch(url):
        raise ValueError("unavailable")
    monkeypatch.setattr(verifier, "fetch_source", failed_fetch)
    assert verifier.main(args) == 1
    ledger = json.loads(path.read_text())
    assert ledger["sources"][0]["verification"] == source["verification"]
    assert ledger["sources"][0]["retrieval_attempts"][0]["status"] == "failed"
    assert ledger["last_verified"] == "2000-01-01"
    assert ledger["status"] == "partial-review"


@pytest.mark.parametrize("decision", ["confirmed_by_content", "confirmed_by_manual_review", "corrected"])
def test_successful_fetch_alone_cannot_advance_review(tmp_path, monkeypatch, decision):
    source = reviewed_source()
    source["verification"]["reviewed_on"] = "2000-01-01"
    source["retrieved"] = source["last_verified"] = "2000-01-01"
    decisions = {decision: {source["id"]: {}} if decision == "corrected" else [source["id"]]}
    verifier, path, args = setup_live_review(tmp_path, monkeypatch, [source], decisions)
    monkeypatch.setattr(verifier, "fetch_source", lambda url: {"text": "reviewed scoped source claim.", "normalized_content_sha256": "a" * 64})
    assert verifier.main(args) == 1
    result = json.loads(path.read_text())
    assert result["sources"][0]["verification"] == source["verification"]
    assert result["last_verified"] == "2000-01-01"


def test_partial_success_updates_only_reviewed_record(tmp_path, monkeypatch):
    first, second = reviewed_source("first"), reviewed_source("second")
    for source in (first, second):
        source["verification"]["reviewed_on"] = "2000-01-01"
        source["retrieved"] = source["last_verified"] = "2000-01-01"
        source["refresh_due"] = "2000-02-01"
    evidence = {"first": {"normalized_content_sha256": "a" * 64, "evidence_path": "outputs/source.txt", "evidence_excerpt": "reviewed scoped source claim.", "review_note": "Read and verified the complete scoped source claim."}}
    verifier, path, args = setup_live_review(tmp_path, monkeypatch, [first, second], {"confirmed_by_manual_review": ["first"]}, evidence=evidence)
    monkeypatch.setattr(verifier, "fetch_source", lambda url: {"text": "reviewed scoped source claim.", "normalized_content_sha256": "a" * 64, "http_status": 200, "final_url": url, "content_type": "text/plain", "reviewable_text_bytes": 27})
    assert verifier.main(args) == 1
    ledger = json.loads(path.read_text())
    assert ledger["sources"][0]["verification"]["reviewed_on"] == date.today().isoformat()
    assert ledger["sources"][1] == second
    assert ledger["last_verified"] == "2000-01-01"


def test_low_overlap_cannot_be_content_confirmed_even_with_retrieval_evidence(tmp_path, monkeypatch):
    source = reviewed_source()
    source["claims"] = source["supports_claims"] = ["Quantum certification guarantees revenue increases."]
    evidence = {source["id"]: {"normalized_content_sha256": "a" * 64, "evidence_path": "outputs/source.txt", "evidence_excerpt": "reviewed scoped source claim.", "review_note": "Reviewed the source and recorded the supported scoped sentence."}}
    verifier, path, args = setup_live_review(tmp_path, monkeypatch, [source], {"confirmed_by_content": [source["id"]]}, evidence=evidence)
    monkeypatch.setattr(verifier, "fetch_source", lambda url: {"text": "reviewed scoped source claim.", "normalized_content_sha256": "a" * 64})
    assert verifier.main(args) == 1
    assert json.loads(path.read_text())["sources"][0] == source
