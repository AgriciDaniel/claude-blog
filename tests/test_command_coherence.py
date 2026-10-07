"""Command-count coherence regression test.

Asserts that the orchestrator (skills/blog/SKILL.md) and the command
reference (docs/COMMANDS.md) declare the same set of `/blog X` commands.

Added v1.8.5 (6TH-AUDIT-019): the v1.8.4 audit found `README:195` said
"28 user-facing commands" while `docs/COMMANDS.md:3` said "29 ... slash
commands" and `skills/blog/SKILL.md` had 29 rows. This test catches the
class-of-defect on every PR.

Stdlib + pytest only.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# Pattern for orchestrator table rows: `| \`/blog X ...\` |`
_SKILL_ROW = re.compile(r"^\|\s*`/blog\s+([\w-]+)", re.MULTILINE)
# Pattern for COMMANDS.md table rows: `| \`X <args>\` | blog-X | ...`
_COMMANDS_ROW = re.compile(r"^\|\s*`(\w[\w-]*)\b", re.MULTILINE)
_COMMAND_MAPPING_ROW = re.compile(
    r"^\|\s*`([\w-]+)\b[^`]*`\s*\|\s*([\w-]+)\s*\|",
    re.MULTILINE,
)
_ROUTE_ROW = re.compile(r"^\s*-\s+(.+?)\s+→\s+`([\w-]+)`", re.MULTILINE)

EXPECTED_CANONICAL_COMMANDS = {
    "write": "blog-write",
    "rewrite": "blog-rewrite",
    "analyze": "blog-analyze",
    "brief": "blog-brief",
    "calendar": "blog-calendar",
    "strategy": "blog-strategy",
    "outline": "blog-outline",
    "seo-check": "blog-seo-check",
    "schema": "blog-schema",
    "repurpose": "blog-repurpose",
    "geo": "blog-geo",
    "audit": "blog-audit",
    "image": "blog-image",
    "cannibalization": "blog-cannibalization",
    "factcheck": "blog-factcheck",
    "persona": "blog-persona",
    "taxonomy": "blog-taxonomy",
    "notebooklm": "blog-notebooklm",
    "audio": "blog-audio",
    "google": "blog-google",
    "cluster": "blog-cluster",
    "multilingual": "blog-multilingual",
    "translate": "blog-translate",
    "localize": "blog-localize",
    "locale-audit": "blog-locale-audit",
    "flow": "blog-flow",
    "brand": "blog-brand",
    "discourse": "blog-discourse",
    "style": "blog-style",
    "decay": "blog-decay",
}

EXPECTED_ALIASES = {
    "update": "blog-rewrite",
    "plan": "blog-calendar",
    "ideation": "blog-strategy",
    "voice-of-customer": "blog-discourse",
    "social-listening": "blog-discourse",
    "trend-research": "blog-discourse",
    "seo": "blog-seo-check",
    "aeo": "blog-geo",
    "citation": "blog-geo",
    "health": "blog-audit",
    "notebook": "blog-notebooklm",
    "query-notebook": "blog-notebooklm",
    "narrate": "blog-audio",
    "tts": "blog-audio",
    "gsc": "blog-google",
    "psi": "blog-google",
    "pagespeed": "blog-google",
    "crux": "blog-google",
    "cwv": "blog-google",
    "topic-cluster": "blog-cluster",
    "pillar": "blog-cluster",
    "hub-and-spoke": "blog-cluster",
    "international": "blog-multilingual",
    "cultural-adaptation": "blog-localize",
    "translation-audit": "blog-locale-audit",
    "find-leverage-optimize-win": "blog-flow",
}

EXPECTED_TABLE_COMMANDS = {**EXPECTED_CANONICAL_COMMANDS, "update": "blog-rewrite"}
REQUIRED_EVALUATED_ALIASES = {
    "update",
    "plan",
    "ideation",
    "voice-of-customer",
    "seo",
    "aeo",
    "health",
    "notebook",
    "narrate",
    "gsc",
    "topic-cluster",
    "international",
    "cultural-adaptation",
    "translation-audit",
    "find-leverage-optimize-win",
}


def _extract_skill_commands() -> set[str]:
    text = (ROOT / "skills" / "blog" / "SKILL.md").read_text(encoding="utf-8")
    return set(_SKILL_ROW.findall(text))


def _extract_commands_md_commands() -> set[str]:
    text = (ROOT / "docs" / "COMMANDS.md").read_text(encoding="utf-8")
    # The overview table sits between the "## Command Overview" heading
    # and the next "---" separator. Match table rows in that block.
    block = re.search(
        r"## Command Overview.*?^---",
        text, re.DOTALL | re.MULTILINE,
    )
    assert block is not None, "Command Overview section missing from COMMANDS.md"
    cmds = set(_COMMANDS_ROW.findall(block.group(0)))
    cmds.discard("Command")  # the table header column name
    return cmds


def _extract_commands_md_mapping() -> dict[str, str]:
    text = (ROOT / "docs" / "COMMANDS.md").read_text(encoding="utf-8")
    return dict(_COMMAND_MAPPING_ROW.findall(text))


def _extract_router_mapping() -> dict[str, str]:
    text = (ROOT / "skills" / "blog" / "SKILL.md").read_text(encoding="utf-8")
    mapping: dict[str, str] = {}
    for names, target in _ROUTE_ROW.findall(text):
        for name in re.findall(r"`([\w-]+)`", names):
            mapping[name] = target
    return mapping


def test_orchestrator_and_commands_md_declare_same_commands() -> None:
    skill_cmds = _extract_skill_commands()
    commands_cmds = _extract_commands_md_commands()
    assert skill_cmds == commands_cmds, (
        f"command sets disagree:\n"
        f"  in SKILL.md but not COMMANDS.md: {skill_cmds - commands_cmds}\n"
        f"  in COMMANDS.md but not SKILL.md: {commands_cmds - skill_cmds}"
    )


def test_orchestrator_has_exact_supported_commands() -> None:
    """Preserve 30 canonical commands plus the documented update alias row."""
    skill_cmds = _extract_skill_commands()
    assert skill_cmds == set(EXPECTED_TABLE_COMMANDS)


def test_command_reference_preserves_command_to_skill_mapping() -> None:
    assert _extract_commands_md_mapping() == EXPECTED_TABLE_COMMANDS


def test_router_preserves_canonical_and_alias_mappings() -> None:
    mapping = _extract_router_mapping()
    for command, target in {**EXPECTED_CANONICAL_COMMANDS, **EXPECTED_ALIASES}.items():
        assert mapping.get(command) == target, (
            f"router mapping drift for {command!r}: expected {target!r}, "
            f"found {mapping.get(command)!r}"
        )


def test_blog_chart_remains_internal_only() -> None:
    chart = (ROOT / "skills" / "blog-chart" / "SKILL.md").read_text(encoding="utf-8")
    assert re.search(r"^user-invocable:\s*false\s*$", chart, re.MULTILINE)
    assert "chart" not in _extract_skill_commands()


def test_routing_evaluations_cover_every_canonical_command_and_alias_family() -> None:
    evaluations = json.loads((ROOT / "tests" / "evaluations.json").read_text(encoding="utf-8"))
    evaluated = {
        match.group(1)
        for case in evaluations
        if (match := re.match(r"^/blog\s+([\w-]+)\b", case.get("query", "")))
    }
    assert set(EXPECTED_CANONICAL_COMMANDS) <= evaluated
    assert REQUIRED_EVALUATED_ALIASES <= evaluated


def test_routing_evaluations_include_near_miss_negatives_and_recovery() -> None:
    evaluations = json.loads((ROOT / "tests" / "evaluations.json").read_text(encoding="utf-8"))
    names = {case["name"] for case in evaluations}
    assert {
        "negative-blog-theme-debug",
        "negative-blog-parser-code",
        "negative-blog-definition",
        "missing-subcommand-recovery",
        "product-review-evidence-recovery",
    } <= names


def test_orchestrator_description_has_intent_boundary() -> None:
    text = (ROOT / "skills" / "blog" / "SKILL.md").read_text(encoding="utf-8")
    assert "Do not activate merely" in text
    assert "unrelated coding" in text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
