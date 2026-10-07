"""Explicit reviewed source fixtures, independent of the volatile real ledger."""
from datetime import date, timedelta


def reviewed_source(source_id="source-alpha", url="https://developers.google.com/search/docs/alpha"):
    today = date.today().isoformat()
    return {
        "id": source_id, "title": source_id, "url": url,
        "source_type": "official", "confidence": "high", "status": "active",
        "claims": ["Reviewed scoped source claim."], "supports_claims": ["Reviewed scoped source claim."],
        "retrieved": today, "last_verified": today,
        "refresh_due": (date.today() + timedelta(days=30)).isoformat(),
        "verification": {
            "decision": "confirmed_by_manual_review", "reviewed_on": today,
            "normalized_content_sha256": "a" * 64,
            "evidence_path": "outputs/fixture-source.txt",
            "evidence_excerpt": "Reviewed scoped source claim.",
            "review_note": "Read the source passage and checked each material component of the scoped claim.",
        },
    }
