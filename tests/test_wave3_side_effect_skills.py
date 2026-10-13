"""Static regression checks for the paid, credentialed, and multi-skill text contracts.

Covers blog-image, blog-audio, blog-notebooklm, blog-google, blog-cluster,
blog-flow, and the multilingual chain (blog-multilingual, blog-translate,
blog-localize). Facts were verified against primary sources on 2026-10-12.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"

SIDE_EFFECT = ("blog-image", "blog-audio", "blog-notebooklm", "blog-google")
GENERIC_TRIGGERS = (
    "voice", "narration", "tts", "notebook", "keyword research", "tone",
    "google data", "page speed", "core web vitals", "search console", "ga4",
    "text to speech", "narrate blog",
)
EM_DASH = chr(0x2014)


def _skill(name: str) -> str:
    return (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")


def _ref(name: str, relative: str) -> str:
    return (SKILLS_DIR / name / relative).read_text(encoding="utf-8")


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def _description(name: str) -> str:
    text = _skill(name)
    match = re.search(r"^description:\s*>?\s*\n(.*?)^user-invocable:", text, re.S | re.M)
    assert match, name
    return _flat(match.group(1)).strip()


def _frontmatter(name: str) -> str:
    return _skill(name).split("---", 2)[1]


def _all_text(name: str) -> str:
    parts = []
    for path in sorted((SKILLS_DIR / name).rglob("*.md")):
        if "scripts" in path.parts:
            continue
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


# ---------------------------------------------------------------- shared gate

@pytest.mark.parametrize("name", SIDE_EFFECT)
def test_side_effect_skills_keep_model_invocation_and_narrow_triggers(name: str) -> None:
    # disable-model-invocation: true would block the Skill tool, which the /blog hub
    # uses to reach these sub-skills (code.claude.com/docs/en/skills, 2026-10-12).
    assert "disable-model-invocation" not in _frontmatter(name)
    description = _description(name)
    assert len(description) < 1536
    quoted = [q.lower() for q in re.findall(r'"([^"]+)"', description)]
    for phrase in quoted:
        assert phrase not in GENERIC_TRIGGERS, (name, phrase)


@pytest.mark.parametrize("name", SIDE_EFFECT)
def test_side_effect_skills_open_with_a_cost_and_consent_gate(name: str) -> None:
    text = _skill(name)
    flat = _flat(text)
    assert "## Cost and consent gate (mandatory, read first)" in text
    # The gate precedes the command table and every workflow section.
    gate = text.index("## Cost and consent gate")
    for later in ("## Quick Reference", "## Generation Workflow", "## Query Workflow"):
        if later in text:
            assert gate < text.index(later), (name, later)
    assert "explicit yes" in flat
    assert "FIRST" in text
    assert "Fallbacks and skips" in text
    assert len(text.splitlines()) < 500


# ----------------------------------------------------------------- blog-image

def test_image_default_route_is_the_direct_api_script_with_real_flags() -> None:
    text = _skill("blog-image")
    flat = _flat(text)
    assert 'generate_hero.py" --topic' in text
    for flag in ("--topic", "--tags", "--out", "--width", "--height", "--model", "--json"):
        assert flag in text, flag
    assert "${CLAUDE_BLOG_SCRIPTS_DIR:-${CLAUDE_SKILL_DIR}/../../scripts}" in text
    assert "Default: direct API" in text
    assert "at your own risk" in flat
    # No relative script invocation anywhere in the skill text.
    assert not re.search(r"python3 (?!\")scripts/generate_hero\.py", _all_text("blog-image"))
    # The MCP is demoted: not advertised as the skill's package in the frontmatter.
    assert "\nmetadata:" in _frontmatter("blog-image") and "\n  mcp-package:" not in _frontmatter("blog-image")
    assert "**Direct API (default).**" in text


def test_image_model_facts_match_googles_pages() -> None:
    models = _flat(_ref("blog-image", "references/gemini-models.md"))
    assert "gemini-nano-banana-2.1" in models
    assert "Previous Generation" in models
    assert "names `gemini-nano-banana-2.1` as the replacement" in models
    assert "2027-03-15" in models
    assert "$0.0336 (1K), $0.0504 (2K), $0.113 (4K)" in models
    assert "Recommended - Speed + Quality" not in models
    mcp = _flat(_ref("blog-image", "references/mcp-tools.md"))
    assert "optional, at your own risk" in mcp
    assert "2026-06-25" in mcp


# ----------------------------------------------------------------- blog-audio

def test_audio_uses_current_tts_ids_and_correct_language_claims() -> None:
    text = _skill("blog-audio")
    flat = _flat(text)
    assert "--model flash38" in text
    assert "--model flash \\" not in text and "--model pro \\" not in text
    assert "gemini-3.8-flash-tts" in text and "gemini-3.8-flash-lite-tts" in text
    assert "2026-11-17" in text
    assert "GEMINI_API_KEY" in text and "GOOGLE_AI_API_KEY" in text
    assert "setup_environment.py" in text
    assert "--max-chunks" in text and "default 12" in flat
    assert "sudo apt" not in text
    everything = _all_text("blog-audio")
    assert "80+" not in everything
    assert "over 130 languages" in flat


# ------------------------------------------------------------ blog-notebooklm

def test_notebooklm_uses_gemini_notebook_names_hosts_and_explicit_setup() -> None:
    skill = _flat(_skill("blog-notebooklm"))
    assert "Gemini Notebook" in skill and "notebook.google.com" in skill
    assert "301" in skill
    assert "at most 3 follow-ups" in skill
    assert "50/day" not in skill and "50 queries/day" not in skill
    for relative in ("references/troubleshooting.md", "references/commands.md"):
        text = _ref("blog-notebooklm", relative)
        assert not re.search(r"python3 scripts/run\.py", text), relative
        assert "installs Chrome automatically" not in text, relative
        assert "rm -rf .venv" not in text, relative
        assert "Auto-recreates" not in text, relative
        assert "NOTEBOOKLM_RUN" in text, relative
    assert "No implicit installs" in _ref("blog-notebooklm", "references/troubleshooting.md")


# ----------------------------------------------------------------- blog-google

def test_google_youtube_quota_is_search_list_own_bucket() -> None:
    skill = _flat(_skill("blog-google"))
    quotas = _flat(_ref("blog-google", "references/rate-limits-quotas.md"))
    api = _flat(_ref("blog-google", "references/api-reference.md"))
    for text in (skill, quotas, api):
        assert "100 units per search" not in text
        assert "| `search.list` | 100 units |" not in text
        assert "own" in text and "100 calls" in text
    assert "own quota bucket" in skill or "own bucket" in skill


def test_google_index_is_ineligible_for_blog_posts_and_needs_confirmation() -> None:
    text = _skill("blog-google")
    flat = _flat(text)
    section = text[text.index("### `/blog google index <url>`"):text.index("## GA4 Traffic")]
    assert "NOT eligible" in section
    assert "JobPosting" in section and "BroadcastEvent" in section
    assert "--confirm-eligible" in section
    assert "second explicit yes" in _flat(section)
    assert "Submit URL to Indexing API" not in text
    assert "blog posts are ineligible" in flat


def test_google_auth_setup_uses_least_privilege_and_trusted_paths() -> None:
    auth = _ref("blog-google", "references/auth-setup.md")
    assert "**Full** (read-only) or **Owner**" not in auth
    assert "Do not grant **Owner**" in auth
    assert "Restricted" in auth
    assert "python3 scripts/google_auth.py" not in auth
    assert 'blog-google/scripts/run.py" google_auth --check' in auth
    assert "setup_environment.py" in auth
    skill = _skill("blog-google")
    assert "sudo apt install" not in skill
    assert "1,200 QPM per site and per user; 40,000 QPM per project | 30M QPD per project" in skill
    assert "| 1,200 QPM/site | 30M QPD |" not in skill
    current = _ref("blog-google", "references/search-currentness.md")
    assert "python3 scripts/check_google_currentness.py" not in current


# ---------------------------------------------------------------- blog-cluster

def test_cluster_defers_to_the_delivery_contract() -> None:
    skill = _skill("blog-cluster")
    flat = _flat(skill)
    refs = _flat(_ref("blog-cluster", "references/execution-workflow.md"))
    assert "<seed> 2026" not in skill
    assert "<current year>" in skill
    assert "append `2026`" not in _ref("blog-cluster", "references/semantic-clustering.md")
    # One hero per post, created by blog-write's contract: no second blog-image call.
    assert "call `/blog image generate`" not in skill
    assert "Do not call `/blog image`" in skill
    assert "Optional hero image" not in skill
    assert "One-time cost question" in skill
    assert "HERO: gemini" in skill and "stock-only" in skill
    # Delivered posts are never edited in place.
    assert "BEFORE the contract runs" in skill
    assert "cluster-link-patches.md" in skill and "cluster-link-patches.md" in refs
    assert "re-init the review nonce" in flat
    assert "Scan all previously written posts" not in skill


# ------------------------------------------------------------ multilingual chain

ORCHESTRATED = (
    "When invoked by blog-multilingual (orchestrated mode), skip the delivery "
    "contract; blog-multilingual runs it once per locale on the final text."
)


def test_orchestrated_mode_wording_is_identical_in_all_three_skills() -> None:
    for name in ("blog-translate", "blog-localize", "blog-multilingual"):
        assert ORCHESTRATED in _flat(_skill(name)), name
    for name in ("blog-multilingual", "blog-translate"):
        assert "Mode: orchestrated" in _skill(name), name


def test_multilingual_runs_exactly_one_canonical_sequence_per_locale() -> None:
    text = _skill("blog-multilingual")
    phase6 = text[text.index("### Phase 6"):text.index("### Phase 7")]
    assert "exactly one run per locale" in phase6
    assert "ONLY delivery-contract run" in phase6
    for step in ("Visuals", "Render", "Init nonce", "Review", "Gates", "Loop"):
        assert step in phase6, step
    assert "review.md" in phase6
    # Translate's standalone contract follows the same canonical sequence.
    translate = _skill("blog-translate")
    phase7 = translate[translate.index("### Phase 7"):translate.index("### Phase 8")]
    assert "review.md" in phase7 and "Loop" in phase7 and "Visuals" in phase7
    assert "pending (contract deferred" in phase7


def test_hreflang_code_rules_match_examples_and_google() -> None:
    text = _skill("blog-multilingual")
    flat = _flat(text)
    assert not re.search(r"--languages de,fr,es(\s|`)", text)
    assert "never a region by itself" in flat
    assert "localized-versions" in text
    assert '"hreflang": "de-DE"' not in text
    translate = _flat(_skill("blog-translate"))
    assert "never a region by itself" in translate
    # Save-path ambiguity: exactly one output root per run.
    assert "Exactly one output root applies per run" in _skill("blog-translate")


# ------------------------------------------------------------------- blog-flow

def test_flow_attribution_has_license_link_and_modification_notice() -> None:
    text = _skill("blog-flow")
    flat = _flat(text)
    assert text.count("https://creativecommons.org/licenses/by/4.0/") >= 2
    assert flat.count("Prompts were modified from the original for blog use.") >= 2
    assert "Do not omit or shorten the attribution" in text
    assert "not verbatim upstream copies" in flat
    assert "Network write" in text and "explicit yes" in flat
    assert "Do not omit or modify the attribution" not in text


@pytest.mark.parametrize("name", (
    "blog-image", "blog-audio", "blog-notebooklm", "blog-google", "blog-cluster",
    "blog-flow", "blog-multilingual", "blog-translate",
))
def test_touched_skills_stay_under_the_line_cap_and_have_no_em_dash(name: str) -> None:
    assert len(_skill(name).splitlines()) < 500
    assert EM_DASH not in _all_text(name)
