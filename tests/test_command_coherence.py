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

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# Pattern for orchestrator table rows: `| \`/blog X ...\` |`
_SKILL_ROW = re.compile(r"^\|\s*`/blog\s+([\w-]+)", re.MULTILINE)
# Pattern for COMMANDS.md table rows: `| \`X <args>\` | blog-X | ...`
_COMMANDS_ROW = re.compile(r"^\|\s*`(\w[\w-]*)\b", re.MULTILINE)


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


def test_orchestrator_and_commands_md_declare_same_commands() -> None:
    skill_cmds = _extract_skill_commands()
    commands_cmds = _extract_commands_md_commands()
    assert skill_cmds == commands_cmds, (
        f"command sets disagree:\n"
        f"  in SKILL.md but not COMMANDS.md: {skill_cmds - commands_cmds}\n"
        f"  in COMMANDS.md but not SKILL.md: {commands_cmds - skill_cmds}"
    )


def test_orchestrator_has_at_least_28_commands() -> None:
    """Sanity floor: regression guard against a future refactor that
    accidentally deletes commands from the SKILL.md table."""
    skill_cmds = _extract_skill_commands()
    assert len(skill_cmds) >= 28, (
        f"orchestrator commands dropped below floor: {len(skill_cmds)}, "
        f"current set = {sorted(skill_cmds)}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
