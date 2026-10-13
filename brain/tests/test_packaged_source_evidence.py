"""Packaged evidence must be reproducible bytes, not an inline assertion."""
import copy
import hashlib
import importlib
import json
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import source_evidence
from evidence_fixtures import captured_evidence_root, reviewed_source
from verify_source_ledger import offline_check

MODULES = ["synthesize_blog_plan", "synthesize_topic_cluster", "synthesize_geo_citation_readiness"]


def artifact_path(source):
    return source_evidence.BRAIN_ROOT / source["verification"]["captured_excerpt_path"]


def rewrite_artifact(source, change):
    path = artifact_path(source)
    artifact = json.loads(path.read_text())
    change(artifact)
    data = (json.dumps(artifact) + "\n").encode()
    path.write_bytes(data)
    source["verification"]["captured_excerpt_sha256"] = hashlib.sha256(data).hexdigest()


def corrupt(source, defect):
    verification = source["verification"]
    if defect == "missing":
        artifact_path(source).unlink()
    elif defect == "forged-bytes":
        artifact_path(source).write_text('{"forged": true}')
    elif defect == "zero-artifact-hash":
        verification["captured_excerpt_sha256"] = "0" * 64
    elif defect == "zero-document-hash":
        verification["normalized_content_sha256"] = "0" * 64
        rewrite_artifact(source, lambda a: a.update(normalized_full_document_sha256="0" * 64))
    elif defect == "forged-excerpt":
        verification["evidence_excerpt"] = "Fabricated text absent from the reviewed capture."
    elif defect == "provenance-hash":
        rewrite_artifact(source, lambda a: a.update(normalized_full_document_sha256="b" * 64))
    elif defect == "provenance-url":
        rewrite_artifact(source, lambda a: a.update(document_url="https://developers.google.com/unreviewed"))
    elif defect == "provenance-review":
        rewrite_artifact(source, lambda a: a["records"][0].update(reviewed_on="2000-01-01"))
    elif defect == "review-decision":
        verification["decision"] = "corrected"
    elif defect == "empty-provenance-id":
        rewrite_artifact(source, lambda a: a["records"].append({"source_id": ""}))
    elif defect == "duplicate-provenance-id":
        rewrite_artifact(source, lambda a: a["records"].extend([{"source_id": "other"}, {"source_id": "other"}]))
    elif defect == "quote-budget":
        rewrite_artifact(source, lambda a: a["excerpts"].append(" ".join(f"word{i}" for i in range(26))))
    elif defect == "escape":
        verification["captured_excerpt_path"] = "references/evidence/../../outside.json"
    elif defect == "absolute":
        verification["captured_excerpt_path"] = str(artifact_path(source))
    elif defect == "outside-lane":
        verification["captured_excerpt_path"] = "tests/fixtures/source.json"
    elif defect == "symlink-leaf":
        path = artifact_path(source)
        outside = path.parents[3] / "outside.json"
        path.rename(outside)
        path.symlink_to(outside)
    elif defect == "symlink-ancestor":
        folder = artifact_path(source).parent
        outside = folder.parent.parent.parent / "outside-directory"
        folder.rename(outside)
        folder.symlink_to(outside, target_is_directory=True)
    else:
        raise AssertionError(defect)


DEFECTS = ["missing", "forged-bytes", "zero-artifact-hash", "zero-document-hash",
           "forged-excerpt", "provenance-hash", "provenance-url", "provenance-review",
           "review-decision", "empty-provenance-id", "duplicate-provenance-id", "quote-budget", "escape", "absolute", "outside-lane", "symlink-leaf", "symlink-ancestor"]


@pytest.mark.parametrize("defect", DEFECTS)
def test_offline_gate_rejects_missing_or_unbound_physical_evidence(defect):
    source = reviewed_source()
    assert offline_check({"sources": [source]}, date.today())["status"] == "pass"
    corrupt(source, defect)
    result = offline_check({"sources": [source]}, date.today())
    assert result["status"] == "fail"
    assert result["verified"] == 0
    assert any("captured excerpt" in error or "captured_excerpt" in error or "normalized_content_sha256" in error for error in result["failures"])


@pytest.mark.parametrize("module_name", MODULES)
@pytest.mark.parametrize("defect", ["missing", "forged-bytes", "zero-document-hash", "forged-excerpt", "review-decision", "symlink-ancestor"])
def test_all_adapters_require_matching_physical_excerpt(module_name, defect, tmp_path):
    source = reviewed_source()
    ledger = tmp_path / "ledger.json"
    module = importlib.import_module(module_name)
    ledger.write_text(json.dumps({"sources": [source]}))
    assert module.source_citations([source["id"]], module.load_source_index(ledger))
    corrupt(source, defect)
    ledger.write_text(json.dumps({"sources": [source]}))
    with pytest.raises(module.SourceError, match="source-alpha"):
        module.source_citations([source["id"]], module.load_source_index(ledger))


def test_audit_default_source_gate_rejects_fabricated_record(tmp_path, monkeypatch):
    import audit_brain
    ledger = json.loads((ROOT / "references/source-ledger.json").read_text())
    references = tmp_path / "references"
    references.mkdir()
    (references / "source-ledger.json").write_text(json.dumps(ledger))
    monkeypatch.setattr(audit_brain, "REPO", tmp_path)
    assert audit_brain.check_source_ledger(requires_fresh=True)[0]
    source = next(s for s in ledger["sources"] if s["status"] == "active")
    source["verification"].update(normalized_content_sha256="0" * 64,
                                  evidence_excerpt="fabricated evidence text that was never fetched",
                                  evidence_path="nonexistent/fabricated-capture.txt")
    (references / "source-ledger.json").write_text(json.dumps(ledger))
    ok, score, notes, critical = audit_brain.check_source_ledger(requires_fresh=True)
    assert not ok
    assert any(source["id"] in error for error in critical)


def test_excerpt_scope_does_not_claim_full_document_availability_or_entailment():
    source = reviewed_source()
    source["verification"]["evidence_path"] = "nonexistent/separate-full-document.txt"
    result = offline_check({"sources": [source]}, date.today())
    assert result["status"] == "pass"
    assert result["evidence_validation"]["captured_artifacts_checked"] is True
    assert result["evidence_validation"]["excerpt_integrity_checked"] is True
    assert result["evidence_validation"]["full_capture_checked"] is False
    assert result["evidence_validation"]["full_document_artifacts_checked"] is False
    assert result["evidence_validation"]["semantic_entailment_checked"] is False


def test_normalized_agreement_and_retirement_do_not_invent_capture_requirements():
    source = reviewed_source()
    source["verification"]["evidence_excerpt"] = "  REVIEWED\n scoped  source claim. "
    assert source_evidence.can_support(source)
    retired = {"id": "retired", "status": "retired", "retired_on": date.today().isoformat(),
               "retirement_reason": "Replaced with the original reviewed document.",
               "replacement_source_ids": [source["id"]]}
    assert offline_check({"sources": [source, retired]}, date.today())["status"] == "pass"
    source["status"] = "unverified"
    source["unverified_reason"] = "Review withdrawn"
    artifact_path(source).unlink()
    assert not source_evidence.can_support(source)
    assert offline_check({"sources": [source, retired]}, date.today())["status"] == "fail"


def test_document_quote_limit_cannot_be_split_across_artifacts():
    first = reviewed_source("first")
    second = reviewed_source("second")
    second["verification"]["evidence_excerpt"] = " ".join(f"different{i}" for i in range(23))
    rewrite_artifact(second, lambda a: a.update(excerpts=[second["verification"]["evidence_excerpt"]]))
    assert source_evidence.can_support(first)
    assert source_evidence.can_support(second)
    result = offline_check({"sources": [first, second]}, date.today())
    assert result["status"] == "fail"
    assert any("aggregate 25-word" in error for error in result["failures"])


def test_unsupported_secure_file_operations_fail_closed(monkeypatch):
    source = reviewed_source()
    monkeypatch.setattr(source_evidence.os, "supports_dir_fd", set())
    result = offline_check({"sources": [source]}, date.today())
    assert result["status"] == "fail"
    assert any("unavailable on this platform" in error for error in result["failures"])


def set_packaged_text(source, excerpts, *, referenced_indices=None, extra_records=None):
    """Build real artifact bytes, including deliberately invalid quote fixtures."""
    artifact = json.loads(artifact_path(source).read_text())
    artifact["excerpts"] = excerpts
    record = artifact["records"][0]
    indices = referenced_indices if referenced_indices is not None else [0]
    record["excerpt_index"] = indices[0]
    artifact["records"] = [record, *(extra_records or [])]
    source["verification"]["evidence_excerpt"] = excerpts[indices[0]]
    data = (json.dumps(artifact) + "\n").encode()
    artifact_path(source).write_bytes(data)
    source["verification"]["captured_excerpt_sha256"] = hashlib.sha256(data).hexdigest()


def share_artifact(first, second):
    artifact = json.loads(artifact_path(first).read_text())
    other = json.loads(artifact_path(second).read_text())
    artifact["records"].extend(other["records"])
    data = (json.dumps(artifact) + "\n").encode()
    artifact_path(first).write_bytes(data)
    for source in (first, second):
        source["verification"].update(
            captured_excerpt_path=first["verification"]["captured_excerpt_path"],
            captured_excerpt_sha256=hashlib.sha256(data).hexdigest())


def test_two_21_word_artifacts_cannot_hide_40_words_outside_inline_excerpts():
    first, second = reviewed_source("first"), reviewed_source("second")
    first_twenty = " ".join(f"alpha{i}" for i in range(20))
    second_twenty = " ".join(f"beta{i}" for i in range(20))
    set_packaged_text(first, ["alpha", first_twenty])
    set_packaged_text(second, ["beta", second_twenty])
    # Exact reviewer repro: two files of 21 words each but two inline words.
    for source in (first, second):
        artifact = json.loads(artifact_path(source).read_text())
        assert sum(len(text.split()) for text in artifact["excerpts"]) == 21
        assert len(source["verification"]["evidence_excerpt"].split()) == 1
        assert not source_evidence.can_support(source)
    result = offline_check({"sources": [first, second]}, date.today())
    assert result["status"] == "fail"
    assert any("aggregate 25-word" in error for error in result["failures"])
    assert any("provenance index coverage" in error for error in result["failures"])


def test_unused_excerpt_rejected_even_below_document_word_limit():
    source = reviewed_source()
    set_packaged_text(source, ["reviewed scoped source claim.", "unused short quotation"])
    assert not source_evidence.can_support(source)
    result = offline_check({"sources": [source]}, date.today())
    assert result["status"] == "fail"
    assert any("provenance index coverage" in error for error in result["failures"])


@pytest.mark.parametrize("binding", ["unknown", "known-other-path", "retired"])
def test_every_artifact_record_must_bind_active_source_to_that_exact_path(binding):
    first, second = reviewed_source("first"), reviewed_source("second")
    extra = copy.deepcopy(json.loads(artifact_path(second).read_text())["records"][0])
    if binding == "unknown":
        extra["source_id"] = "unknown"
        sources = [first]
    else:
        sources = [first, second]
        if binding == "retired":
            second.update(status="retired", retired_on=date.today().isoformat(),
                          retirement_reason="Historical reference", replacement_source_ids=["first"])
    set_packaged_text(first, ["reviewed scoped source claim."], extra_records=[extra])
    assert source_evidence.can_support(first)  # structural/index checks alone are insufficient
    result = offline_check({"sources": sources}, date.today())
    assert result["status"] == "fail"
    assert any("not a known active ledger source" in error or "not bound to this artifact path" in error for error in result["failures"])


def test_multi_source_single_artifact_passes_and_counts_real_text_once():
    first, second = reviewed_source("first"), reviewed_source("second")
    text = " ".join(f"shared{i}" for i in range(21))
    set_packaged_text(first, [text])
    set_packaged_text(second, [text])
    share_artifact(first, second)
    assert source_evidence.can_support(first) and source_evidence.can_support(second)
    result = offline_check({"sources": [first, second]}, date.today())
    assert result["status"] == "pass"
    assert result["verified"] == 2


def test_shared_artifact_cannot_group_sources_from_different_documents():
    first = reviewed_source("first")
    second = reviewed_source("second", "https://developers.google.com/search/docs/other-document")
    share_artifact(first, second)
    result = offline_check({"sources": [first, second]}, date.today())
    assert result["status"] == "fail"
    assert any("document URL mismatch" in error for error in result["failures"])


def test_fully_bound_distinct_artifacts_preserve_aggregate_boundary():
    first, second = reviewed_source("first"), reviewed_source("second")
    set_packaged_text(first, [" ".join(f"first{i}" for i in range(20))])
    set_packaged_text(second, [" ".join(f"second{i}" for i in range(5))])
    assert offline_check({"sources": [first, second]}, date.today())["status"] == "pass"
    set_packaged_text(second, [" ".join(f"second{i}" for i in range(6))])
    result = offline_check({"sources": [first, second]}, date.today())
    assert result["status"] == "fail"
    assert any("aggregate 25-word" in error for error in result["failures"])


@pytest.mark.parametrize("module_name", MODULES)
def test_all_adapters_reject_aggregate_artifact_budget_overflow(module_name, tmp_path):
    first, second = reviewed_source("first"), reviewed_source("second")
    set_packaged_text(first, [" ".join(f"first{i}" for i in range(21))])
    set_packaged_text(second, [" ".join(f"second{i}" for i in range(21))])
    assert source_evidence.can_support(first) and source_evidence.can_support(second)
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"sources": [first, second]}))
    module = importlib.import_module(module_name)
    index = module.load_source_index(ledger)
    with pytest.raises(module.SourceError, match="aggregate 25-word"):
        module.source_citations([first["id"]], index)


def test_unreferenced_and_historical_files_are_outside_active_artifact_coverage():
    active = reviewed_source("active")
    historical = reviewed_source("historical")
    historical.update(status="retired", retired_on=date.today().isoformat(),
                      retirement_reason="Preserved historical source", replacement_source_ids=["active"])
    old_verification = copy.deepcopy(historical["verification"])
    artifact_path(historical).write_text("Historical file deliberately outside active coverage.")
    unreferenced = source_evidence.BRAIN_ROOT / "references/evidence/fixture/unreferenced.json"
    unreferenced.write_text(json.dumps({"records": [{"source_id": "unknown"}],
                                        "excerpts": [" ".join(f"unused{i}" for i in range(100))]}))
    result = offline_check({"sources": [active, historical]}, date.today())
    assert result["status"] == "pass"
    assert result["verified"] == 1
    assert historical["verification"] == old_verification
    assert not source_evidence.can_support(historical)
