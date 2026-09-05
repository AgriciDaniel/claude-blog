"""Version-coherence regression test.

Asserts that the project version is the same string across all four
canonical surfaces: pyproject.toml, plugin.json, CITATION.cff, and the
orchestrator skills/blog/SKILL.md frontmatter.

Added v1.8.5 (6TH-AUDIT-010): the v1.8.4 release added the same check
as a CI YAML heredoc. Moving the check into pytest gives local devs the
same signal CI produces, so `pytest` before push catches the drift.

Stdlib + pytest only.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _read_pyproject_version() -> str | None:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return m.group(1) if m else None


def _read_plugin_version() -> str | None:
    with open(ROOT / ".claude-plugin" / "plugin.json", encoding="utf-8") as f:
        return json.load(f).get("version")


def _read_citation_version() -> str | None:
    """Strip optional YAML single/double quotes (v1.8.6: 7TH-AUDIT-011)."""
    text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    m = re.search(r'^version:\s*[\'"]?([0-9][^\'"\s]+)[\'"]?', text, re.MULTILINE)
    return m.group(1) if m else None


def _read_skill_md_version() -> str | None:
    text = (ROOT / "skills" / "blog" / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r'^\s*version:\s*"?([^"\s]+)"?', text, re.MULTILINE)
    return m.group(1) if m else None


def test_all_version_surfaces_aligned() -> None:
    """The same version string must appear in pyproject.toml,
    plugin.json, CITATION.cff, and skills/blog/SKILL.md metadata.

    v1.8.4 (5TH-AUDIT-001) found skills/blog/SKILL.md frozen at "1.8.0"
    while every other surface had moved through 1.8.1, 1.8.2, 1.8.3.
    This test prevents that recurring.
    """
    versions = {
        "pyproject.toml": _read_pyproject_version(),
        ".claude-plugin/plugin.json": _read_plugin_version(),
        "CITATION.cff": _read_citation_version(),
        "skills/blog/SKILL.md": _read_skill_md_version(),
    }
    # None should be missing.
    missing = [k for k, v in versions.items() if v is None]
    assert not missing, f"version field could not be extracted from: {missing}"
    unique = set(versions.values())
    assert len(unique) == 1, (
        f"version surfaces disagree:\n"
        + "\n".join(f"  {k}: {v!r}" for k, v in versions.items())
    )


def test_version_string_matches_semver_pattern() -> None:
    """The shared version must be valid semver (X.Y.Z optional pre-release)."""
    version = _read_pyproject_version()
    assert version is not None
    assert re.match(r"^\d+\.\d+\.\d+(-\S+)?$", version), (
        f"version {version!r} does not match semver pattern X.Y.Z[-pre]"
    )


def test_all_sub_skill_versions_match_project_version() -> None:
    """v1.8.6 (7TH-AUDIT-003): every skills/*/SKILL.md `version:` field
    must equal the project version. Pre-v1.8.6, 10 sub-skill SKILL.md
    files had stale per-skill versions (1.0.0, 1.4.0, 1.7.0) that were
    never bumped through the v1.8.x cycle. The version-coherence test
    only covered the orchestrator, missing all 10 sub-skill surfaces.
    """
    target = _read_pyproject_version()
    assert target is not None
    skill_md_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    assert len(skill_md_files) >= 30, (
        f"unexpectedly few SKILL.md files: {len(skill_md_files)}"
    )
    mismatches = []
    for f in skill_md_files:
        text = f.read_text(encoding="utf-8")
        # Match the YAML frontmatter version field; tolerate quote styles.
        m = re.search(
            r'^\s+version:\s*[\'"]?([0-9][^\'"\s]+)[\'"]?',
            text, re.MULTILINE,
        )
        if m is None:
            # Some SKILL.md files may not declare metadata.version at all;
            # that is acceptable. We only flag drift, not absence.
            continue
        if m.group(1) != target:
            mismatches.append((f.relative_to(ROOT), m.group(1)))
    assert not mismatches, (
        f"sub-skill SKILL.md versions disagree with pyproject.toml "
        f"({target}):\n"
        + "\n".join(f"  {p}: {v}" for p, v in mismatches)
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
