"""Static regression checks for the planning, locale, and context skill contracts."""

from __future__ import annotations

import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent

SKILLS = (
    "blog-localize", "blog-locale-audit", "blog-taxonomy", "blog-brand",
    "blog-discourse", "blog-style", "blog-decay", "blog-persona",
    "blog-repurpose", "blog-geo", "blog-schema", "blog-seo-check", "blog-brief",
    "blog-outline", "blog-calendar", "blog-strategy", "blog-cannibalization",
    "blog-factcheck",
)


def _skill(name: str) -> str:
    return (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


def _flat(name: str) -> str:
    return re.sub(r"\s+", " ", _skill(name))


def _description(name: str) -> str:
    match = re.search(r"^description:\s*>?\s*\n?(.*?)^user-invocable:", _skill(name), re.S | re.M)
    if match is None:  # single-line description
        match = re.search(r"^description:\s*(.+)$", _skill(name), re.M)
    assert match, name
    return re.sub(r"\s+", " ", match.group(1)).strip()


@pytest.mark.parametrize("name", SKILLS)
def test_skill_stays_under_line_cap_and_states_scope(name: str) -> None:
    assert len(_skill(name).splitlines()) < 500
    description = _description(name)
    assert len(description) < 1536
    if name not in {"blog-outline"}:
        assert re.search(r"\bNot for\b|\bnot a\b|\bnot for\b", description, re.I), name


def test_taxonomy_has_consent_and_write_gate() -> None:
    text = _flat("blog-taxonomy")
    assert "## Consent and write gate" in _skill("blog-taxonomy")
    for needle in (
        "Dry run (default)",
        "Explicit approval",
        "Replace semantics",
        "No deletes, merges, renames, or hierarchy changes",
        "Credentials by name only",
        "untrusted data",
        "Stay on the confirmed host",
        "rollback record",
    ):
        assert needle in text, needle
    assert "?limit=all" not in text
    # Shopify mutation takes variables, not interpolated strings.
    assert "$tags: [String!]" in _skill("blog-taxonomy")


@pytest.mark.parametrize("name", ["blog-brief", "blog-strategy", "blog-discourse", "blog-brand", "blog-calendar"])
def test_project_root_context_loads_only_through_fenced_helper(name: str) -> None:
    text = _flat(name)
    assert "Auto-loaded Project-Root Context" in text
    assert not re.search(r"load it before starting brief generation\. Treat", text)
    assert not re.search(r"load it for cross-platform discourse signal alongside this skill's authority-source planning\. Treat", text)
    assert "reads `DISCOURSE.md` at the start of the downstream command" not in text


def test_brief_names_real_discourse_sections() -> None:
    text = _skill("blog-brief")
    assert "Contrarian takes" not in text
    assert "Niche / single-source themes" in text


@pytest.mark.parametrize("name", ["blog-geo", "blog-schema", "blog-seo-check", "blog-factcheck", "blog-repurpose", "blog-cannibalization"])
def test_post_content_is_declared_untrusted(name: str) -> None:
    assert "untrusted" in _flat(name).lower()


def test_repurpose_does_not_invite_invented_experience() -> None:
    text = _flat("blog-repurpose")
    assert "as if reporting results" not in text
    assert "After analyzing 500 campaigns, here's what actually drives ROI" not in text
    assert "Start with a personal story, observation, or contrarian take" not in text
    assert "[YOUR EXPERIENCE:" in text
    assert "Never invent a personal story" in text
    assert "rolling out gradually" not in text


def test_factcheck_states_limits_and_evidence_rule() -> None:
    text = _flat("blog-factcheck")
    assert "What this skill can and cannot verify" in text
    assert "Never mark a claim VERIFIED" in text
    assert "could not fetch" in text
    assert "gemini-3.1-flash-tts" not in text


def test_decay_states_heuristic_and_url_normalization() -> None:
    text = _flat("blog-decay")
    assert "screening heuristic" in text
    assert "URL normalization matters" in text
    assert "50,000 rows per day" in text


def test_style_and_persona_do_not_claim_authorship_detection() -> None:
    for name in ("blog-style", "blog-persona"):
        text = _flat(name)
        assert re.search(r"not authorship (detection|attribution)", text, re.I), name


def test_style_decay_discourse_geo_use_trusted_absolute_script_paths() -> None:
    for name in ("blog-style", "blog-decay", "blog-discourse", "blog-geo"):
        text = _skill(name)
        assert '${CLAUDE_BLOG_SCRIPTS_DIR:-${CLAUDE_SKILL_DIR}/../../scripts}' in text, name
        assert re.search(r'case "\$BLOG_SCRIPT_DIR" in /\*\)', text), name


def test_discourse_does_not_overwrite_silently() -> None:
    text = _skill("blog-discourse")
    assert not re.search(r"--days 30 \\\n\s+--output DISCOURSE\.md", text)
    assert '--output "<chosen output path>"' in text


def test_locale_skills_integrate_with_one_contract_run_per_locale() -> None:
    sentence = (
        "When invoked by blog-multilingual (orchestrated mode), skip the delivery "
        "contract; blog-multilingual runs it once per locale on the final text."
    )
    assert sentence in _skill("blog-localize")
    audit = _flat("blog-locale-audit")
    assert "read-only and is not a delivery step" in audit
    assert not re.search(r"\| `x-default` \|[^|]*\|\s*Critical", _skill("blog-locale-audit"))
    assert "`es-419`" in audit


def test_schema_follows_current_google_support() -> None:
    text = _flat("blog-schema")
    assert "2026-05-07" in text
    assert "articleBody" in text and '"articleBody"' not in _skill("blog-schema")
    assert "userInteractionCount" not in text
    assert "blog_render.py" in text
    assert "single question" in text or "one question" in text


def test_geo_separates_crawler_purposes() -> None:
    text = _flat("blog-geo")
    for bot in ("OAI-SearchBot", "GPTBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "PerplexityBot", "Perplexity-User"):
        assert bot in text, bot
    assert "Page size | Reasonable page size within AI crawler limits" not in _skill("blog-geo")


def test_cannibalization_requires_spend_approval_and_has_no_stale_price() -> None:
    text = _flat("blog-cannibalization")
    assert "~$0.01" not in text
    assert "Spend approval" in text
    assert "approves that count" in text


def test_calendar_has_no_unverified_report_release_dates() -> None:
    text = _flat("blog-calendar")
    assert "Gartner Hype Cycle (August)" not in text
    assert "Ahrefs Annual State of SEO (typically Q1)" not in text
