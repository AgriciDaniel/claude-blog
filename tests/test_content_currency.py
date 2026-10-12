"""Regression tests for content currency, attribution, and fallback reporting."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REFS = SKILLS / "blog" / "references"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_landscape_baseline_is_september_2026_spam_update() -> None:
    text = _read(REFS / "google-landscape-2026.md")
    assert "## September 2026 Baseline" in text
    assert "September 24 to October 8" in text
    assert "Verified against Google-owned sources on 2026-10-11" in text
    assert "## August 2026 Baseline" not in text


def test_schema_stack_does_not_list_qapage_as_deprecated() -> None:
    text = _read(REFS / "schema-stack.md")
    instead = text.split("### What to Use Instead", 1)[1].split("---", 1)[0]
    table_rows = [line for line in instead.splitlines() if line.startswith("|")]
    assert not any(row.startswith("| QAPage") for row in table_rows)
    assert "| QAPage | Supported narrow use |" in text


def test_unsourced_statistics_are_gone() -> None:
    corpus = "\n".join(
        _read(p)
        for p in list(REFS.glob("*.md"))
        + [SKILLS / "blog-write" / "SKILL.md"]
    )
    for banned in ("25.1%", "43.4%", "159%", "Stratabeat", "Animalz", "266%", "317%"):
        assert banned not in corpus, banned
    rules = _read(REFS / "content-rules.md")
    assert "124%" in rules and "one test site" in rules
    geo = _read(REFS / "geo-optimization.md")
    assert "AI Overviews" in geo and "107,352" in geo and "classic rankings" in geo


def test_case_study_template_marks_invented_metrics() -> None:
    text = _read(SKILLS / "blog" / "templates" / "case-study.md")
    assert text.count("ILLUSTRATIVE, REPLACE WITH REAL DATA") >= 6


def test_helpful_content_authorship_guidance_is_present() -> None:
    eeat = _read(REFS / "eeat-signals.md")
    assert "Authorship Integrity" in eeat
    assert "2026-10-05" in eeat and "deception" in eeat
    landscape = _read(REFS / "google-landscape-2026.md")
    assert "Helpful-content page update (2026-10-05)" in landscape
    assert "2026-09-16" in landscape and "2026-10-01" in landscape
    assert "2026-10-05" in _read(REFS / "quality-scoring.md")


def test_subject_led_patterns_are_described_and_referenced() -> None:
    slop = _read(REFS / "ai-slop-detection.md")
    assert "Subject-led sentence patterns" in slop
    assert "unproven" in slop
    for path in (
        SKILLS / "blog-write" / "SKILL.md",
        ROOT / "agents" / "blog-writer.md",
        ROOT / "agents" / "blog-reviewer.md",
    ):
        assert "ubject-led sentence patterns" in _read(path), path


def test_sub_skill_fallbacks_are_reported_not_silent() -> None:
    write = _read(SKILLS / "blog-write" / "SKILL.md")
    assert "Fallback report" in write
    assert len(write.splitlines()) < 500
    assert "Falls back silently" not in write
    for name in ("blog-image", "blog-audio", "blog-notebooklm"):
        text = _read(SKILLS / name / "SKILL.md")
        assert "return silently" not in text.lower(), name
        assert "one-line" in text, name
    assert "Fallbacks and skips" in _read(
        SKILLS / "blog-write" / "references" / "delivery.md"
    )


def test_contributors_credit_reimplemented_upstream_prs() -> None:
    text = _read(ROOT / "docs" / "CONTRIBUTORS.md")
    for handle, pr in (
        ("andrewtpham", "83"),
        ("joachimBrindeau", "82"),
        ("imong8", "73"),
        ("Hi-2025-Be", "90"),
    ):
        assert handle in text
        assert f"/pull/{pr}" in text
