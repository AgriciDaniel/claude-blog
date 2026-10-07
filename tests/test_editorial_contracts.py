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
