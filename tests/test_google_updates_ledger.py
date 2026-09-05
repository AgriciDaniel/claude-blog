"""Contract tests for the primary-source Google updates ledger."""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = REPO_ROOT / "data" / "google-updates.json"
GOOGLE_SKILL_PATH = REPO_ROOT / "skills" / "blog-google" / "SKILL.md"
GOOGLE_CURRENTNESS_PATH = (
    REPO_ROOT / "skills" / "blog-google" / "references" / "search-currentness.md"
)
SCHEMA_SKILL_PATH = REPO_ROOT / "skills" / "blog-schema" / "SKILL.md"
SCHEMA_REFERENCE_PATH = REPO_ROOT / "skills" / "blog" / "references" / "schema-stack.md"
CRAWLER_REFERENCE_PATH = (
    REPO_ROOT / "skills" / "blog" / "references" / "ai-crawler-guide.md"
)
BRAIN_LEDGER_PATH = REPO_ROOT / "brain" / "data" / "google-updates.json"
LANDSCAPE_PATH = (
    REPO_ROOT / "skills" / "blog" / "references" / "google-landscape-2026.md"
)
CURRENTNESS_SCRIPT_PATH = REPO_ROOT / "scripts" / "check_google_currentness.py"
CURRENTNESS_WORKFLOW_PATH = (
    REPO_ROOT / ".github" / "workflows" / "google-currentness.yml"
)


def _load_ledger() -> dict:
    return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))


def _normalized(text: str) -> str:
    return " ".join(text.split())


def _load_currentness_module():
    spec = importlib.util.spec_from_file_location(
        "google_currentness_test", CURRENTNESS_SCRIPT_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_google_updates_ledger_shape_and_currentness() -> None:
    ledger = _load_ledger()

    assert ledger["schema_version"] == 2
    assert date.fromisoformat(ledger["last_verified"]) >= date(2026, 8, 25)
    assert isinstance(ledger["verified"], list) and ledger["verified"]
    assert isinstance(ledger["unverified"], list)
    assert "must never change scoring" in ledger["policy"]
    assert "Event timing never proves site impact" in ledger["policy"]
    assert "Source conflicts remain explicit" in ledger["policy"]

    watches = {item["id"]: item for item in ledger["source_watch"]}
    assert watches["search-status"]["review_mode"] == "automated"
    assert watches["search-docs-updates"]["review_mode"] == "automated"
    assert watches["search-console-anomalies"]["review_mode"] == "manual"
    assert watches["google-ads-release-notes"]["review_mode"] == "manual"
    assert watches["google-ads-client-support"]["review_mode"] == "manual"


def test_verified_entries_use_unique_ids_and_google_owned_sources() -> None:
    ledger = _load_ledger()
    entries = ledger["verified"]
    ids = [entry["id"] for entry in entries]

    assert len(ids) == len(set(ids))
    for entry in entries:
        required = {
            "id",
            "event_date",
            "title",
            "source_url",
            "category",
            "applicability",
            "affected_components",
            "summary",
        }
        assert required <= set(entry)
        assert set(entry) <= required | {
            "additional_source_urls",
            "evidence_status",
        }
        date.fromisoformat(entry["event_date"])
        assert entry["affected_components"]
        source_urls = [entry["source_url"], *entry.get("additional_source_urls", [])]
        for source_url in source_urls:
            host = urlparse(source_url).hostname
            assert host in {
                "blog.google",
                "developers.google.com",
                "status.search.google.com",
                "support.google.com",
            }
        assert entry.get("evidence_status", "confirmed") in {
            "confirmed",
            "confirmed-data-anomaly",
            "confirmed-event-pending-impact",
            "confirmed-with-source-conflict",
        }


def test_ledger_covers_current_search_contracts() -> None:
    ledger_text = LEDGER_PATH.read_text(encoding="utf-8")

    for contract in (
        "FAQ rich results are no longer shown",
        "up to two weeks",
        "Instagram, TikTok, X, and YouTube",
        "no dedicated API",
        "not ranking factors",
        "first 2MB",
        "Back-button hijacking",
        "August 2026 spam update",
        "logging errors",
        "fake reviews",
        "Python client 31.2.0",
    ):
        assert contract in ledger_text


def test_platform_availability_conflict_keeps_both_google_sources() -> None:
    ledger = _load_ledger()
    entry = next(
        item
        for item in ledger["verified"]
        if item["id"] == "search-console-platform-properties-2026-07-29"
    )

    assert entry["evidence_status"] == "confirmed-with-source-conflict"
    assert "globally available" in entry["summary"]
    assert "still says gradual rollout" in entry["summary"]
    assert entry["additional_source_urls"] == [
        "https://support.google.com/webmasters/answer/17148418?hl=en-GB"
    ]


def test_brain_ledger_is_an_exact_projection_of_the_canonical_ledger() -> None:
    assert BRAIN_LEDGER_PATH.read_bytes() == LEDGER_PATH.read_bytes()


def test_currentness_evaluator_distinguishes_current_and_refresh_required() -> None:
    module = _load_currentness_module()
    ledger = _load_ledger()

    current = module.evaluate(
        ledger,
        as_of=date(2026, 9, 24),
        max_age_days=31,
        source_dates={
            "search-docs-updates": date(2026, 8, 20),
            "search-status": date(2026, 8, 18),
        },
    )
    assert current["status"] == "current"

    newer_source = module.evaluate(
        ledger,
        as_of=date(2026, 8, 26),
        max_age_days=31,
        source_dates={"search-status": date(2026, 8, 26)},
    )
    assert newer_source["status"] == "refresh_required"
    assert "newer than" in newer_source["reasons"][0]

    stale = module.evaluate(
        ledger,
        as_of=date(2026, 9, 26),
        max_age_days=31,
        source_dates={},
    )
    assert stale["status"] == "refresh_required"
    assert "32 days old" in stale["reasons"][0]


def test_currentness_parsers_read_official_feed_shapes() -> None:
    module = _load_currentness_module()
    status_payload = json.dumps(
        [
            {
                "service_name": "Serving",
                "begin": "2026-08-24T00:00:00+00:00",
            },
            {
                "service_name": "Ranking",
                "begin": "2026-08-18T16:27:00+00:00",
            },
        ]
    ).encode()
    rss_payload = b"""<?xml version='1.0'?>
    <rss><channel><item>
      <pubDate>Thu, 20 Aug 2026 00:00:00 +0000</pubDate>
    </item></channel></rss>"""

    assert module.latest_ranking_incident(status_payload) == date(2026, 8, 18)
    assert module.latest_documentation_update(rss_payload) == date(2026, 8, 20)


def test_currentness_checker_rejects_untrusted_automated_source_urls() -> None:
    module = _load_currentness_module()
    ledger = _load_ledger()
    ledger["source_watch"][0]["url"] = "http://127.0.0.1/private"

    try:
        module._automated_sources(ledger)
    except ValueError as exc:
        assert "not allowlisted" in str(exc)
    else:
        raise AssertionError("untrusted automated source URL was accepted")


def test_scheduled_currentness_workflow_is_read_only() -> None:
    workflow = CURRENTNESS_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "schedule:" in workflow and "workflow_dispatch:" in workflow
    assert "contents: read" in workflow
    assert "check_google_currentness.py" in workflow
    assert "sync_google_updates.py --root . --check" in workflow
    assert "issues: write" not in workflow
    assert "contents: write" not in workflow


def test_unverified_entries_cannot_masquerade_as_verified() -> None:
    ledger = _load_ledger()
    verified_ids = {entry["id"] for entry in ledger["verified"]}
    unverified_ids = {entry["id"] for entry in ledger["unverified"]}

    assert verified_ids.isdisjoint(unverified_ids)


def test_schema_guidance_matches_current_google_contract() -> None:
    guidance = _normalized(
        "\n".join(
            (
                SCHEMA_SKILL_PATH.read_text(encoding="utf-8"),
                SCHEMA_REFERENCE_PATH.read_text(encoding="utf-8"),
            )
        )
    )

    assert "earns no SEO or AI-readiness credit" in guidance
    assert "one question with user-submitted answers" in guidance
    assert "Course Info" in guidance and "Course list" in guidance
    assert "PracticeProblem" in guidance
    assert "Dataset Search" in guidance
    assert "present in the rendered DOM" in guidance
    assert "40-60 words" not in guidance
    assert "AI citation support" not in guidance


def test_google_currentness_guidance_preserves_api_boundaries() -> None:
    guidance = _normalized(
        "\n".join(
            (
                GOOGLE_SKILL_PATH.read_text(encoding="utf-8"),
                GOOGLE_CURRENTNESS_PATH.read_text(encoding="utf-8"),
            )
        )
    )

    assert "Wait at least one full week" in guidance
    assert "Web Search, Images, Video mode, and News tab separately" in guidance
    assert "PENDING_REEVALUATION" in guidance
    assert "up to two weeks" in guidance
    assert "Do not promise clicks or queries" in guidance
    assert "Instagram, TikTok, X, and YouTube" in guidance
    assert "not a ranking signal" in guidance
    assert "SOURCE_CONFLICT" in guidance
    assert "PENDING_OBSERVATION" in guidance
    assert "fake reviews" in guidance
    assert "Python client 31.2.0" in guidance


def test_google_landscape_excludes_unsourced_market_and_recovery_claims() -> None:
    landscape = LANDSCAPE_PATH.read_text(encoding="utf-8")

    assert "machine-readable\nsource of truth" in landscape
    assert "Search Console Measurement Anomalies" in landscape
    assert "Review Integrity" in landscape
    assert "Source conflict" in landscape
    for unsupported in (
        "70.85%",
        "900M weekly users",
        "11.4% conversion rate",
        "Partial Helpful Content recoveries",
        "AI Overview Ads",
    ):
        assert unsupported not in landscape


def test_crawler_guidance_requires_behavioral_evidence_and_byte_visibility() -> None:
    guidance = _normalized(CRAWLER_REFERENCE_PATH.read_text(encoding="utf-8"))

    assert "first 2MB" in guidance
    assert "not a ranking factor" in guidance
    assert "Legitimate History API use is not a violation by itself" in guidance
    assert "Do not remove the hash" in guidance
    assert "do not force" in guidance
    assert "not injected via JavaScript" not in guidance
