"""Focused contracts for the retained FLOW prompt projection."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FLOW = ROOT / "skills" / "blog-flow" / "references"
PROMPTS = FLOW / "prompts"
LOCK = FLOW / "flow-prompts.lock"


def _task_contract(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text.split("## Use This When", 1)[1].split("## See Also", 1)[0]


def _differentiated_prompt_paths() -> list[Path]:
    paths = sorted((PROMPTS / "find").glob("*.md")) + sorted(
        (PROMPTS / "optimize").glob("*.md")
    )
    return [
        path
        for path in paths
        if path.name != "ai-detector-test-follow-up-prompt.md"
    ]


def test_named_find_and_optimize_prompts_have_distinct_task_contracts() -> None:
    duplicates: dict[str, list[str]] = defaultdict(list)
    prompt_paths = _differentiated_prompt_paths()

    for path in prompt_paths:
        normalized = " ".join(_task_contract(path).split()).casefold()
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        duplicates[digest].append(path.relative_to(PROMPTS).as_posix())

    repeated = [paths for paths in duplicates.values() if len(paths) > 1]
    assert repeated == [], f"duplicate FLOW task contracts: {repeated}"


def test_named_prompts_declare_inputs_decisions_and_outputs() -> None:
    for path in _differentiated_prompt_paths():
        contract = _task_contract(path)
        assert "## Task Inputs" in contract, path
        assert "## Decisions" in contract, path
        assert "## Required Output" in contract, path
        assert "Use only supplied evidence" in contract, path


def test_representative_prompts_require_task_specific_evidence() -> None:
    expected = {
        "find/keyword-research-prompt.md": (
            "query and intent map",
            "cannibalization risks",
            "validation queue",
        ),
        "find/prompt-audience-avatar.md": (
            "evidence-backed reader profile",
            "jobs and objections",
            "evidence register",
        ),
        "optimize/ctr-audit-prompt.md": (
            "dated GSC query-page data",
            "confounder register",
            "rollback rule",
        ),
        "optimize/schema-prompt-1.md": (
            "visible content",
            "Schema.org validity",
            "JSON-LD brief",
        ),
        "optimize/paa-question-rewording-prompt.md": (
            "paa questions with date and market",
            "duplicate decisions",
            "answer briefs",
        ),
        "optimize/technical-audit-prompt.md": (
            "http, crawl, rendered html",
            "reproduction",
            "post-fix checks",
        ),
    }
    for relative, phrases in expected.items():
        text = (PROMPTS / relative).read_text(encoding="utf-8").casefold()
        for phrase in phrases:
            assert phrase.casefold() in text, f"{relative} missing {phrase!r}"


def test_flow_prompt_lock_matches_retained_files() -> None:
    entries: dict[str, str] = {}
    for line in LOCK.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        digest, separator, relative = line.partition("  ")
        assert separator == "  "
        entries[relative] = digest

    for relative, expected in entries.items():
        path = ROOT / relative
        assert path.is_file(), relative
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, relative


def test_flow_attribution_and_retained_dates_are_preserved() -> None:
    attribution = (
        "<!-- (c) Daniel Agrici, FLOW "
        "(https://github.com/AgriciDaniel/flow), CC BY 4.0 -->"
    )
    for path in _differentiated_prompt_paths():
        text = path.read_text(encoding="utf-8")
        assert text.startswith(attribution), path
        assert "<!-- Synced from FLOW on 2026-04-27 -->" in text, path
        assert "updated: 2026-04-25" in text, path
