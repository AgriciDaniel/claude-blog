"""Static regression checks for public editorial and routing contracts."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_skill_entrypoints_do_not_execute_project_relative_helpers() -> None:
    offenders: list[str] = []
    pattern = re.compile(r"python3\s+(?:scripts/|skills/)")
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        if pattern.search(path.read_text(encoding="utf-8")):
            offenders.append(path.relative_to(ROOT).as_posix())
    assert not offenders, (
        "skill entrypoints must resolve executable helpers from trusted absolute "
        f"install roots, found relative commands in: {offenders}"
    )


def test_analyzer_and_delivery_thresholds_remain_distinct() -> None:
    quality_gate = _read("scripts/quality_gate.py")
    contract = _read("skills/blog/references/blog-delivery-contract.md")
    reviewer = _read("agents/blog-reviewer.md")
    assert "DEFAULT_THRESHOLD = 70" in quality_gate
    assert "90/100" in contract
    assert re.search(r"zero\s+P0|Any P0", contract, re.IGNORECASE)
    assert "Nonce:" in reviewer
    assert "BLOCKING:" in reviewer


def test_p1_is_not_declared_an_absolute_ship_blocker() -> None:
    rubric = _read("skills/blog/references/editorial-heuristics.md")
    assert "P1 (ship-blocker)" not in rubric
    assert "P1 (urgent remediation)" in rubric
    assert "P0 is the only" in rubric


def test_schema_heuristic_matches_existing_analyzer_allocation() -> None:
    reference = _read("skills/blog/references/quality-scoring.md")
    reviewer = _read("agents/blog-reviewer.md")
    analyze_skill = _read("skills/blog-analyze/SKILL.md")
    for text in (reference, reviewer, analyze_skill):
        assert "Article or BlogPosting" in text
        assert "Person" in text
        assert re.search(r"either Organization or BreadcrumbList", text)
    assert "not a Google requirement" in reference
    assert "not a Google requirement" in reviewer


def test_editorial_guidance_has_no_fixed_media_inventory() -> None:
    paths = (
        "skills/blog-write/SKILL.md",
        "skills/blog-rewrite/SKILL.md",
        "skills/blog/references/content-rules.md",
        "skills/blog/references/quality-scoring.md",
    )
    combined = "\n".join(_read(path) for path in paths)
    forbidden = (
        "Find 8-12 current statistics",
        "Find 3-5 inline images",
        "Target 2-4 charts",
        "2-3 embeds with",
        "every 300-500 words",
        "Fewer than 8 sourced statistics",
        "Fewer than 2 charts",
        "Fewer than 3 images",
    )
    for phrase in forbidden:
        assert phrase not in combined
    assert "Do not use a word-count interval or media quota" in combined


def test_evidence_bound_templates_define_nonfabricating_recovery() -> None:
    templates = (
        "skills/blog/templates/product-review.md",
        "skills/blog/templates/case-study.md",
        "skills/blog/templates/roundup.md",
        "skills/blog/templates/data-research.md",
    )
    for path in templates:
        text = _read(path)
        assert "Evidence gate" in text
        assert "evidence-needs brief" in text
    writer = _read("skills/blog-write/SKILL.md")
    assert "Check template evidence before selection" in writer
    assert "do not simulate it" in writer


def test_final_locale_workflows_require_independent_delivery_review() -> None:
    for path in (
        "skills/blog-translate/SKILL.md",
        "skills/blog-localize/SKILL.md",
        "skills/blog-multilingual/SKILL.md",
    ):
        text = _read(path)
        assert "--init-review-nonce" in text
        assert "--strict" in text
        assert "90+/100" in text
        assert "zero P0" in text
        assert "draft-blocked" in text


def test_capability_entrypoints_document_nonmutating_ordinary_commands() -> None:
    notebook = _read("skills/blog-notebooklm/SKILL.md")
    audio = _read("skills/blog-audio/SKILL.md")
    for text in (notebook, audio):
        assert re.search(r"nonmutating\s+capability check", text)
        assert "Only" in text and "setup" in text
        assert "CLAUDE_BLOG_SKILLS_DIR" in text


def test_subject_and_voice_take_precedence_over_generic_phrase_lists() -> None:
    writer = _read("agents/blog-writer.md")
    rewrite = _read("skills/blog-rewrite/SKILL.md")
    assert "actual subject" in writer
    assert "not banned phrases" in writer
    assert "Do not perform blanket substitutions" in rewrite


# ---------------------------------------------------------------------------
# Wave 3: one canonical delivery sequence and the docs that must match it
# ---------------------------------------------------------------------------

SEQUENCE_DOCS = (
    "skills/blog/references/blog-delivery-contract.md",
    "skills/blog/SKILL.md",
    "skills/blog-write/SKILL.md",
    "skills/blog-rewrite/SKILL.md",
    "skills/blog-write/references/delivery.md",
)


def _order(text: str, needles: list[str]) -> list[int]:
    positions = []
    for needle in needles:
        index = text.find(needle)
        assert index >= 0, f"missing {needle!r}"
        positions.append(index)
    return positions


def test_every_write_path_doc_runs_render_then_nonce_then_review_then_gates() -> None:
    for path in SEQUENCE_DOCS:
        text = _read(path)
        if path.endswith("blog-delivery-contract.md"):
            text = text.split("## Canonical delivery sequence", 1)[1]
        if path.endswith("blog-write/SKILL.md") or path.endswith("blog-rewrite/SKILL.md"):
            text = text.split("Delivery Contract Enforcement", 1)[1]
        # The command lines (not the prose mentions) must appear in this order.
        render = text.find('blog_render.py" --md')
        nonce = text.find("--init-review-nonce --draft")
        assert render >= 0 and nonce >= 0, path
        review = text.find("blog-reviewer", nonce)
        assert review >= 0, path
        gates = text.find("--strict", review)
        assert render < nonce < review < gates, path


def test_docs_state_orchestrator_saves_review_and_edits_invalidate_it() -> None:
    for path in SEQUENCE_DOCS:
        text = _read(path)
        assert re.search(r"verbatim", text), f"{path} must say the orchestrator saves review.md verbatim"
        assert re.search(r"re-render", text, re.IGNORECASE), path
        assert re.search(r"re-init|new nonce|fresh nonce", text, re.IGNORECASE), path
        assert "re-review" in text or "new review" in text or "fresh review" in text, path
    reviewer = _read("agents/blog-reviewer.md")
    assert "You have no Write tool" in reviewer
    assert "orchestrator saves it" in reviewer


def test_contract_documents_known_nonce_limit() -> None:
    contract = _read("skills/blog/references/blog-delivery-contract.md")
    assert "does not stop a" in contract and "same user" in contract


def test_no_relative_helper_commands_in_references_or_agents() -> None:
    pattern = re.compile(r"python3\s+(?:\./)?(?:scripts/|skills/)")
    offenders = []
    # Owned here: the shared blog references, the write/chart references, agents.
    candidates = (
        list((ROOT / "skills" / "blog" / "references").glob("*.md"))
        + list((ROOT / "skills" / "blog-write" / "references").glob("*.md"))
        + list((ROOT / "skills" / "blog-chart" / "references").glob("*.md"))
        + list((ROOT / "agents").glob("*.md"))
    )
    for path in candidates:
        if pattern.search(path.read_text(encoding="utf-8")):
            offenders.append(path.relative_to(ROOT).as_posix())
    assert not offenders, f"relative helper commands in: {offenders}"


def test_docs_do_not_hotlink_or_scrape_stock_cdns() -> None:
    banned = ("cdn.pixabay.com", "images.unsplash.com", "site:pixabay.com", "site:unsplash.com", "site:pexels.com")
    paths = [
        "skills/blog-write/references/delivery.md",
        "skills/blog-write/SKILL.md",
        "skills/blog/references/visual-media.md",
    ]
    for path in paths:
        text = _read(path)
        for needle in banned:
            assert needle not in text, f"{path} contains {needle}"
    researcher = _read("agents/blog-researcher.md")
    # The researcher may name what it must not do, but never instruct it.
    assert "do not scrape stock sites" in researcher
    assert re.search(r"Never mark\s+an image \"Verified\"", researcher)
    assert "Image Density Calculation" not in researcher
    assert "1 per 133 words" not in researcher
    assert "Mark each image as Verified (HTTP 200)" not in researcher


def test_markers_are_resolved_by_orchestrator_not_writer_agent() -> None:
    writer = _read("agents/blog-writer.md")
    assert "cannot call skills" in writer
    assert re.search(r"Never write\s+or edit anything outside that folder", writer)
    contract = _read("skills/blog/references/blog-delivery-contract.md")
    assert re.search(r"cannot call\s+skills or helpers", contract)
    write = _read("skills/blog-write/SKILL.md")
    assert "The `blog-writer` agent cannot call" in write
    assert "They must not reach the render" in write
    assert "The user (or a follow-up pass) will resolve" not in write
    assert "Resolve [INTERNAL-LINK] placeholders" not in _read("skills/blog-write/references/delivery.md")


def test_threshold_table_is_single_source_and_matches_scripts() -> None:
    scoring = _read("skills/blog/references/quality-scoring.md")
    assert "### Thresholds (single source of truth)" in scoring
    for fragment in ("Delivery gate", "Strategy target", "Pre-commit gate", "Audit buckets", "| 70 |"):
        assert fragment in scoring, fragment
    quality_gate = _read("scripts/quality_gate.py")
    assert "DEFAULT_THRESHOLD = 70" in quality_gate
    # The rating-band table is not restated anywhere else.
    for path in ("skills/blog-analyze/SKILL.md", "agents/blog-reviewer.md", "skills/blog-rewrite/SKILL.md"):
        assert "| 80-89 | Strong |" not in _read(path), path
    assert "80-89 | Strong | Minor polish, ready for publication" not in scoring
    # Category maxima in the doc agree with what Gate 4 enforces.
    import importlib.util

    spec = importlib.util.spec_from_file_location("bp_for_maxima", ROOT / "scripts" / "blog_preflight.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    maxima = module.REVIEW_CATEGORY_MAX
    assert list(maxima.values()) == [30, 25, 15, 15, 15]
    for name, maximum in maxima.items():
        assert re.search(rf"{re.escape(name)} \(({maximum}) points?\)", scoring), name
        assert f"| {name} | [N] | {maximum} |" in _read("agents/blog-reviewer.md"), name


def test_draft_stage_rule_defines_na_normalization_and_cap() -> None:
    scoring = _read("skills/blog/references/quality-scoring.md")
    assert "Draft-stage scoring" in scoring
    assert "points earned / points applicable * category maximum" in scoring
    assert "overall is the sum of the five reported category scores" in scoring
    assert "more than 20 of the 100 points" in scoring
    reviewer = _read("agents/blog-reviewer.md")
    assert "draft-stage scoring rule" in reviewer
    assert "too little draft evidence to score" in reviewer
    # The old rule forbade any N/A reweighting, which made 90 unreachable for drafts.
    assert "Do not award those points or change the 100-point denominator" not in reviewer


def test_no_stale_image_model_ids_in_blog_docs() -> None:
    paths = [
        "skills/blog-write/SKILL.md",
        "skills/blog-rewrite/SKILL.md",
        "skills/blog/references/blog-delivery-contract.md",
        "skills/blog/references/visual-media.md",
        "agents/blog-researcher.md",
    ]
    for path in paths:
        text = _read(path)
        assert "gemini-3" not in text, path
        assert "flash-image" not in text, path


def test_seo_agent_agrees_with_seo_check_skill() -> None:
    agent = _read("agents/blog-seo.md")
    skill = _read("skills/blog-seo-check/SKILL.md")
    assert "2-4 sentences" not in agent
    assert "No stop words" not in agent
    assert 'rel="nofollow" for sponsored' not in agent
    assert 'rel="sponsored"' in agent and 'rel="sponsored"' in skill
    assert "Do not remove necessary words" in agent
    assert "Natural language" in skill  # the skill rule the agent now mirrors


def test_hub_has_no_footer_contradiction_and_no_forced_chart_diversity() -> None:
    hub = _read("skills/blog/SKILL.md")
    assert "AI Marketing Hub footer" not in hub
    assert "## Community Footer" not in hub
    assert "Each chart must be a different type" not in hub
    assert "Use the same chart type twice" not in hub
    for path in ("skills/blog-write/SKILL.md", "skills/blog-rewrite/SKILL.md"):
        assert "no repeated types per post" not in _read(path), path
    visual = _read("skills/blog/references/visual-media.md")
    assert "Diversity is mandatory" not in visual
    assert "Target 2-4 charts" not in visual


def test_update_mode_and_rewrite_style_are_conditional() -> None:
    rewrite = _read("skills/blog-rewrite/SKILL.md")
    assert "4. Update `lastUpdated` in frontmatter" not in rewrite
    assert "only when the change is substantive" in rewrite
    assert "**Eliminate em dashes**" not in rewrite
    assert "Em dashes (opt-in)" in rewrite and "Contractions (opt-in)" in rewrite
    assert "Contractions used naturally throughout" not in rewrite


def test_chart_schema_is_documented_and_ids_are_unique_by_contract() -> None:
    schema = _read("skills/blog-chart/references/chart-input-schema.md")
    generator = _read("skills/blog-chart/scripts/generate_chart_svg.py")
    types = set(re.findall(r'"(\w+)": "\1"', generator))
    assert types >= {"donut", "line", "lollipop", "area", "radar"}
    for chart_type in ("horizontal_bar", "grouped_bar", "donut", "line", "lollipop", "area", "radar"):
        assert chart_type in schema, chart_type
    for field in ("`type`", "`title`", "`id`", "`source`", "`data`", "`series`", "`label`", "`value`", "`--root`"):
        assert field in schema, field
    assert "distinct `id`" in schema
    chart = _read("skills/blog-chart/SKILL.md")
    assert "chart-input-schema.md" in chart
    assert "Enforces chart type diversity" not in chart
    assert "Use when user says" not in chart
    assert "Agents cannot call it" in chart


def test_descriptions_are_narrow_and_non_overlapping() -> None:
    def description(path: str) -> str:
        text = _read(path)
        match = re.search(r"^description:\s*>\s*\n((?:  .*\n)+)", text, re.MULTILINE)
        assert match, path
        return " ".join(match.group(1).split())

    assert '"write about"' not in description("skills/blog-write/SKILL.md")
    analyze = description("skills/blog-analyze/SKILL.md")
    audit = description("skills/blog-audit/SKILL.md")
    assert '"audit blog"' not in analyze and "blog health check" not in analyze
    assert "blog-audit" in analyze
    assert '"audit blog"' not in audit and "blog-analyze" in audit


def test_analyze_runs_analyzer_first_with_real_flags_and_batch_order() -> None:
    skill = _read("skills/blog-analyze/SKILL.md")
    script = _read("scripts/analyze_blog.py")
    assert "Run the analyzer first" in skill
    for flag in ("--batch", "--sort", "--format", "--category", "--fix", "--output"):
        assert f"`{flag}" in skill, flag
        assert f"'{flag}'" in script, flag
    assert "highest first" in skill and "-r.get('score', {}).get('total', 0)" in script
    assert "skill modes handled here, not script" in skill and "'--rubric'" not in script
    assert "ascending by default" not in skill
    audit = _read("skills/blog-audit/SKILL.md")
    assert "highest score first" in audit
    assert "`metadata`" not in audit


def test_reviewer_effort_field_cites_current_subagent_docs() -> None:
    reviewer = _read("agents/blog-reviewer.md")
    assert re.search(r"^effort: high$", reviewer, re.MULTILINE)
    assert "https://code.claude.com/docs/en/sub-agents" in reviewer
    assert "2026-10-12" in reviewer


def test_skills_reading_content_declare_untrusted_data() -> None:
    for path in (
        "skills/blog-write/SKILL.md",
        "skills/blog-rewrite/SKILL.md",
        "skills/blog-analyze/SKILL.md",
        "skills/blog-audit/SKILL.md",
        "skills/blog-chart/SKILL.md",
        "agents/blog-seo.md",
        "agents/blog-reviewer.md",
        "agents/blog-writer.md",
    ):
        text = _read(path).lower()
        assert "untrusted" in text, path
    hub = _read("skills/blog/SKILL.md")
    assert "load_untrusted_root.py" in hub and "Outer-nonce authority" in hub
    for path in (
        "skills/blog-write/SKILL.md",
        "skills/blog-rewrite/SKILL.md",
        "skills/blog-analyze/SKILL.md",
        "skills/blog-audit/SKILL.md",
    ):
        assert "Untrusted-Data Contract" in _read(path), path


def test_skill_entrypoints_stay_under_500_lines() -> None:
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        assert len(path.read_text(encoding="utf-8").splitlines()) < 500, path


def _fill_reviewer_template(nonce: str) -> str:
    """Turn the reviewer Output Format template into a concrete passing report."""
    agent = _read("agents/blog-reviewer.md")
    block = agent.split("## Output Format", 1)[1].split("```markdown\n", 1)[1].split("\n```", 1)[0]
    scores = {"Content Quality": 26, "SEO Optimization": 24, "E-E-A-T Signals": 14,
              "Technical Elements": 14, "AI Citation Readiness": 14}
    for name, value in scores.items():
        block = re.sub(rf"^(\| {re.escape(name)} \| )\[N\]( \|)", rf"\g<1>{value}\2", block, flags=re.MULTILINE)
    block = block.replace("### Overall Score: [N]/100", "### Overall Score: 92/100")
    block = block.replace("[N]/100 overall", "92/100 overall")
    block = re.sub(r"Nonce: \[[^\]]*\]", f"Nonce: {nonce}", block)
    return re.sub(r"\[[^\]\n]*\]", "ok", block)


def test_reviewer_output_template_passes_gate_4_when_followed_literally(tmp_path, monkeypatch) -> None:
    import importlib.util

    monkeypatch.setenv("CLAUDE_BLOG_REVIEW_STATE_DIR", str(tmp_path / "state"))
    spec = importlib.util.spec_from_file_location("bp_template_check", ROOT / "scripts" / "blog_preflight.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    draft = tmp_path / "draft"
    draft.mkdir()
    (draft / "post.md").write_text("# Post\n", encoding="utf-8")
    nonce = module._init_review_nonce(draft)
    report = _fill_reviewer_template(nonce)
    # The affirmative clearance line and every Gate 4 field come from the template itself.
    assert "\nzero P0 issues found\n" in report
    (draft / "review.md").write_text(report, encoding="utf-8")
    result = module.gate_4_content_review(draft)
    assert result["passed"], result["violations"]
    assert result["score"] == 92


def test_orchestrated_mode_detection_line_is_identical_in_locale_skills() -> None:
    sentence = "Orchestrated mode is signaled by the literal line `Mode: orchestrated` at the top of the invocation."
    for name in ("blog-translate", "blog-localize", "blog-multilingual"):
        assert sentence in " ".join(_read(f"skills/{name}/SKILL.md").split()), name
    localize = _read("skills/blog-localize/SKILL.md")
    assert "Generate or reuse a locale-appropriate hero" not in localize
    assert "`blog-image` cost and consent gate" in localize


def test_frontmatter_contract_matches_renderer_and_write_template() -> None:
    contract = _read("skills/blog/references/blog-delivery-contract.md")
    section = contract.split("## Required frontmatter", 1)[1].split("## Gate 1", 1)[0]
    renderer = _read("scripts/blog_render.py")
    required = re.search(r"REQUIRED_FRONTMATTER_KEYS = \(([^)]*)\)", renderer).group(1)
    for key in re.findall(r'"(\w+)"', required):
        assert f"| `{key}` | Yes" in section, key
    for key in ("canonical", "slug", "site_name", "lang", "og_image_alt", "tags", "kicker"):
        assert f"`{key}`" in section, key
    assert "file stem is the artifact stem" in " ".join(section.split())
    write = _read("skills/blog-write/SKILL.md")
    template = write.split("#### 5a. Frontmatter", 1)[1].split("```", 2)[1]
    for key in ("title", "description", "date", "author", "canonical", "slug", "lang", "og_image_alt", "tags"):
        assert re.search(rf"^{key}:", template, re.MULTILINE), key
    assert "Phase 5.5" not in write


def test_contract_preview_names_and_openverse_licenses_match_scripts() -> None:
    contract = _read("skills/blog/references/blog-delivery-contract.md")
    for name in ("mobile-375.png", "tablet-768.png", "desktop-1280.png", "desktop-1280-dark.png"):
        assert name in contract, name
    assert "preview/<width>.png" not in contract
    assert "license=cc0,by,by-sa" in contract and '"license": "cc0,by,by-sa"' in _read("scripts/generate_hero.py")
    assert "BY-SA images require visible attribution" in contract
    assert "hero-credit.txt" in _read("skills/blog-write/SKILL.md")
    assert "copy every locally referenced image" in " ".join(_read("skills/blog-rewrite/SKILL.md").split()) or \
        "every locally referenced image" in _read("skills/blog-rewrite/SKILL.md")
