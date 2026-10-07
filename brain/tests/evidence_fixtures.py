"""Reviewed source fixtures with real artifacts in a disposable evidence root."""
import hashlib
import json
import shutil
from datetime import date, timedelta
from pathlib import Path

import pytest
import source_evidence

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_TEXT = "reviewed scoped source claim."
FIXTURE_FULL_HASH = hashlib.sha256(FIXTURE_TEXT.encode()).hexdigest()


@pytest.fixture(autouse=True)
def captured_evidence_root(tmp_path, monkeypatch):
    root = tmp_path / "packaged-brain"
    shutil.copytree(ROOT / "references/evidence", root / "references/evidence")
    # Substitute only the trusted package root. All production path/hash/text
    # checks still execute against actual regular files, with no bypass flag.
    monkeypatch.setattr(source_evidence, "BRAIN_ROOT", root)
    return root


def reviewed_source(source_id="source-alpha", url="https://developers.google.com/search/docs/alpha"):
    if source_evidence.BRAIN_ROOT == ROOT:
        raise AssertionError("reviewed_source requires the disposable captured_evidence_root fixture")
    today = date.today().isoformat()
    artifact = {
        "schema": source_evidence.EXCERPT_SCHEMA, "document_url": url.split("#", 1)[0],
        "normalized_full_document_sha256": FIXTURE_FULL_HASH,
        "excerpts": [FIXTURE_TEXT],
        "records": [{"source_id": source_id, "source_url": url,
                     "retrieved_on": today, "reviewed_on": today,
                     "review_decision": "confirmed_by_manual_review", "excerpt_index": 0}],
    }
    relative = "references/evidence/fixture/" + hashlib.sha256((source_id + url).encode()).hexdigest() + ".json"
    data = (json.dumps(artifact) + "\n").encode()
    path = source_evidence.BRAIN_ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {
        "id": source_id, "title": source_id, "url": url,
        "source_type": "official", "confidence": "high", "status": "active",
        "claims": ["Reviewed scoped source claim."], "supports_claims": ["Reviewed scoped source claim."],
        "retrieved": today, "last_verified": today,
        "refresh_due": (date.today() + timedelta(days=30)).isoformat(),
        "verification": {
            "decision": "confirmed_by_manual_review", "reviewed_on": today,
            "normalized_content_sha256": FIXTURE_FULL_HASH, "final_url": url,
            "evidence_path": "outputs/fixture-source.txt",
            "evidence_excerpt": "Reviewed scoped source claim.",
            "review_note": "Read the source passage and checked each material component of the scoped claim.",
            "captured_excerpt_path": relative,
            "captured_excerpt_sha256": hashlib.sha256(data).hexdigest(),
        },
    }


def set_review_decision(source, decision):
    """Update an explicitly reviewed synthetic artifact and its bytes hash."""
    source["verification"]["decision"] = decision
    path = source_evidence.BRAIN_ROOT / source["verification"]["captured_excerpt_path"]
    artifact = json.loads(path.read_text())
    record = next(record for record in artifact["records"] if record["source_id"] == source["id"])
    record["review_decision"] = decision
    data = (json.dumps(artifact) + "\n").encode()
    path.write_bytes(data)
    source["verification"]["captured_excerpt_sha256"] = hashlib.sha256(data).hexdigest()
