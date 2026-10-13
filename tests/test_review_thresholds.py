"""Compatibility boundaries for quality and independent delivery review."""
from pathlib import Path
import importlib.util
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

@pytest.mark.parametrize("score,threshold,passed", [(69,70,False),(70,70,True),(70,71,False),(90,90,True)])
def test_configurable_quality_gate_boundaries(monkeypatch, score, threshold, passed):
    gate = load("boundary_quality", "scripts/quality_gate.py")
    monkeypatch.setattr(gate, "_safe_analyze_file", lambda path: {"score":{"total":score,"issues":[]}})
    assert gate.DEFAULT_THRESHOLD == 70
    assert gate.analyze_post("post.md", threshold)["passed"] is passed

@pytest.mark.parametrize("score,clearance,passed", [(89,"zero P0 issues",False),(90,"zero P0 issues",True),(90,"",False),(90,"zero P0 issues\nP0: unresolved fabricated statistic",False)])
def test_delivery_score_and_explicit_p0_clearance(monkeypatch, tmp_path, score, clearance, passed):
    gate = load("boundary_preflight", "scripts/blog_preflight.py")
    monkeypatch.setenv("CLAUDE_BLOG_REVIEW_STATE_DIR", str(tmp_path / "state"))
    draft = tmp_path / "draft"; draft.mkdir()
    nonce = gate._init_review_nonce(draft)
    (draft / "review.md").write_text(f"Overall Score: {score}/100\n{clearance}\nNonce: {nonce}\nBLOCKING: false (review decision)\n")
    assert gate.gate_4_content_review(draft)["passed"] is passed


@pytest.mark.parametrize("mutation", [
    "negated-clearance", "qualified-clearance", "duplicate-score",
    "conflicting-score", "duplicate-nonce", "conflicting-nonce",
    "missing-reason", "blank-reason", "duplicate-decision",
])
def test_delivery_rejects_ambiguous_review_fields(monkeypatch, tmp_path, mutation):
    gate = load("ambiguous_preflight", "scripts/blog_preflight.py")
    monkeypatch.setenv("CLAUDE_BLOG_REVIEW_STATE_DIR", str(tmp_path / "state"))
    draft = tmp_path / "draft"; draft.mkdir()
    nonce = gate._init_review_nonce(draft)
    review = f"Overall Score: 90/100\nzero P0 issues\nNonce: {nonce}\nBLOCKING: false (controlled review)\n"
    changes = {
        "negated-clearance": ("zero P0 issues", "There are not zero P0 issues."),
        "qualified-clearance": ("zero P0 issues", "zero P0 issues except an unresolved claim"),
        "duplicate-score": ("Overall Score: 90/100", "Overall Score: 90/100\nOverall Score: 90/100"),
        "conflicting-score": ("Overall Score: 90/100", "Overall Score: 90/100\nOverall Score: 89/100"),
        "duplicate-nonce": (f"Nonce: {nonce}", f"Nonce: {nonce}\nNonce: {nonce}"),
        "conflicting-nonce": (f"Nonce: {nonce}", f"Nonce: {nonce}\nNonce: {'0' * 32}"),
        "missing-reason": ("BLOCKING: false (controlled review)", "BLOCKING: false"),
        "blank-reason": ("BLOCKING: false (controlled review)", "BLOCKING: false ( )"),
        "duplicate-decision": ("BLOCKING: false (controlled review)", "BLOCKING: false (first)\nBLOCKING: false (second)"),
    }
    before, after = changes[mutation]
    (draft / "review.md").write_text(review.replace(before, after))
    assert gate.gate_4_content_review(draft)["passed"] is False


@pytest.mark.parametrize("clearance,reason", [
    ("zero P0 issues found", "controlled review"),
    ("No P0.", "controlled review"),
    ("- zero P0 issues remain", "controlled review"),
    ("", "cleared all gates; 92/100 overall, no P0"),
    ("zero P0 issues\nResolved P0: historical defect fixed", "controlled review"),
])
def test_delivery_accepts_affirmative_legacy_review_forms(monkeypatch, tmp_path, clearance, reason):
    gate = load("affirmative_preflight", "scripts/blog_preflight.py")
    monkeypatch.setenv("CLAUDE_BLOG_REVIEW_STATE_DIR", str(tmp_path / "state"))
    draft = tmp_path / "draft"; draft.mkdir()
    nonce = gate._init_review_nonce(draft)
    (draft / "review.md").write_text(f"Overall Score: 92/100\n{clearance}\nNonce: {nonce}\nBLOCKING: false ({reason})\n")
    assert gate.gate_4_content_review(draft)["passed"] is True
