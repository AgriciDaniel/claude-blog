"""Wave 3 regression tests: verify_source_ledger fetch encoding and apply output."""

from __future__ import annotations

import gzip
import json
import sys
import zlib
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BRAIN = ROOT / "brain"
sys.path.insert(0, str(BRAIN / "scripts"))
sys.path.insert(0, str(BRAIN / "tests"))
import verify_source_ledger as verifier  # noqa: E402
from evidence_fixtures import FIXTURE_FULL_HASH, captured_evidence_root, reviewed_source  # noqa: E402,F401


def test_fetch_asks_for_identity_encoding_and_decodes_gzip(monkeypatch):
    import test_source_transport as transport

    page = "<html><body><main>Schema Product type</main></body></html>".encode()
    packed = gzip.compress(page)
    monkeypatch.setattr(verifier.socket, "getaddrinfo", lambda *a, **k: transport.addresses())
    calls = transport.install_connections(monkeypatch, [transport.Response(
        headers={"content-type": "text/html", "content-encoding": "gzip"},
        chunks=[packed, b""],
    )])
    result = verifier.fetch_source("https://public.example/Product")
    assert calls[0]["headers"]["Accept-Encoding"] == "identity"
    assert result["text"] == "schema product type"
    assert result["bytes"] == len(packed)


def test_decode_body_handles_deflate_unknown_and_bombs():
    raw = b"hello " * 50
    assert verifier.decode_body(zlib.compress(raw), "deflate") == raw
    assert verifier.decode_body(gzip.compress(raw), "gzip") == raw
    assert verifier.decode_body(raw, "") == raw
    assert verifier.decode_body(raw, "identity") == raw
    with pytest.raises(ValueError, match="unsupported Content-Encoding"):
        verifier.decode_body(raw, "br")
    with pytest.raises(ValueError, match="invalid gzip"):
        verifier.decode_body(b"not gzip", "gzip")


def _applied_manual_review(tmp_path, monkeypatch):
    from test_source_evidence import setup_live_review

    source = reviewed_source()
    source["verification"]["reviewed_on"] = "2000-01-01"
    source["retrieved"] = source["last_verified"] = "2000-01-01"
    source["refresh_due"] = "2000-02-01"
    reviewed = {source["id"]: {
        "normalized_content_sha256": FIXTURE_FULL_HASH,
        "evidence_path": "outputs/source.txt",
        "evidence_excerpt": "reviewed scoped source claim.",
        "review_note": "Read and verified the complete scoped source claim.",
        **{key: source["verification"][key] for key in ("captured_excerpt_path", "captured_excerpt_sha256")},
    }}
    mod, ledger, args = setup_live_review(
        tmp_path, monkeypatch, [source], {"confirmed_by_manual_review": [source["id"]]}, evidence=reviewed)
    monkeypatch.setattr(mod, "fetch_source", lambda url: {
        "text": "reviewed scoped source claim.",
        "normalized_content_sha256": FIXTURE_FULL_HASH,
        "http_status": 200, "final_url": url, "content_type": "text/plain", "reviewable_text_bytes": 27})
    code = mod.main(args)
    return code, json.loads(ledger.read_text())


def test_apply_writes_the_documented_status_spelling(tmp_path, monkeypatch):
    code, ledger = _applied_manual_review(tmp_path, monkeypatch)
    assert code == 0
    assert ledger["status"] == "research-reviewed"


def test_manual_review_records_carry_no_automated_match_fields(tmp_path, monkeypatch):
    _, ledger = _applied_manual_review(tmp_path, monkeypatch)
    verification = ledger["sources"][0]["verification"]
    assert verification["decision"] == "confirmed_by_manual_review"
    assert verification["reviewed_on"] == date.today().isoformat()
    assert "claim_token_coverage" not in verification
    assert "missing_numeric_literals" not in verification


def test_audit_cited_set_comes_from_non_archived_notes_and_urls(tmp_path):
    import audit_brain

    alpha = reviewed_source("alpha-src", "https://developers.google.com/search/docs/alpha")
    beta = reviewed_source("beta-src", "https://developers.google.com/search/docs/beta/")
    gamma = reviewed_source("gamma-src", "https://developers.google.com/search/docs/gamma")
    delta = reviewed_source("delta-src", "https://developers.google.com/search/docs/delta")
    (tmp_path / "references" / "canon").mkdir(parents=True)
    (tmp_path / "references" / "source-ledger.json").write_text(
        json.dumps({"sources": [alpha, beta, gamma, delta]}))
    (tmp_path / "wiki" / "archive").mkdir(parents=True)
    (tmp_path / "SKILL.md").write_text("Cites alpha-src by id.\n")
    (tmp_path / "references" / "canon" / "001.md").write_text("See <https://DEVELOPERS.google.com/search/docs/beta> too.\n")
    (tmp_path / "wiki" / "live.md").write_text("---\nstatus: active\n---\nNo citations here.\n")
    (tmp_path / "wiki" / "old.md").write_text("---\nstatus: archived\n---\nCites gamma-src.\n")
    (tmp_path / "wiki" / "archive" / "older.md").write_text("Cites delta-src.\n")
    assert audit_brain.cited_source_ids(tmp_path) == {"alpha-src", "beta-src"}


def test_audit_keeps_the_required_citation_floor():
    import audit_brain

    assert "g-helpful-content" in audit_brain.REQUIRED_CITATION_IDS
    assert len(audit_brain.REQUIRED_CITATION_IDS) == 20
