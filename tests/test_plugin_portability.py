"""Portability guardrails: claude-blog must load identically on every surface.

claude-blog ships as one plugin for Claude Cowork, Claude Code, and Claude
Desktop. On all three, the working directory is the *user's* folder and the
plugin lives somewhere opaque. Any bare relative path in a skill file --
``references/x.md``, ``python3 scripts/run.py`` - therefore resolves against
the wrong directory and the skill silently fails.

The fix is ``${CLAUDE_PLUGIN_ROOT}``, which Claude substitutes for the plugin's
install directory. These tests assert that every intra-plugin reference uses it,
that every path it points at actually exists, and that the plugin manifest stays
loadable. Prose in CLAUDE.md drifts; assertions do not.

Stdlib + pytest only. No network, no writes.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
AGENTS_DIR = REPO_ROOT / "agents"
MANIFEST = REPO_ROOT / ".claude-plugin" / "plugin.json"

PLUGIN_VAR = "${CLAUDE_PLUGIN_ROOT}"

# Directories created at runtime rather than shipped in the repo.
RUNTIME_CREATED = {
    "skills/blog/references/personas",
    "skills/blog-persona/references/personas",
    # NotebookLM auth/library fallback for a bare checkout; under a plugin
    # install this state lives in ${CLAUDE_PLUGIN_DATA} instead.
    "skills/blog-notebooklm/data",
}


def _runtime_files() -> list[Path]:
    """Every markdown file Claude actually loads at runtime."""
    return sorted(SKILLS_DIR.rglob("*.md")) + sorted(AGENTS_DIR.rglob("*.md"))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


# ---------------------------------------------------------------------------
# Test 1: no bare intra-plugin paths survive
# ---------------------------------------------------------------------------

# A path is "bare" when it names a plugin directory without the variable in
# front. The leading class rejects a preceding "/" so that the already-correct
# "${CLAUDE_PLUGIN_ROOT}/skills/blog/references/x.md" does not match.
#
# The character class covers every placeholder style used in these files --
# `<type>`, `[type]`, `*` globs - because a path that only differs by its
# placeholder syntax is just as broken at runtime.
PLACEHOLDER = r"A-Za-z0-9_*<>\[\].-"

BARE_ROOTED = re.compile(
    r"(?:^|[^/\w.${-])(skills/blog[a-z-]*/"
    rf"(?:references|templates|scripts|assets|data)/[{PLACEHOLDER}/]*)",
    re.M,
)

# Deliberately NOT flagged: a bare `skills/<name>/SKILL.md`. Naming a skill
# file in prose ("see skills/blog-brand/SKILL.md") is documentation, not an
# instruction to load a path, so it needs no variable.
BARE_RELATIVE = re.compile(
    r"(?:^|[^/\w.${-])((?:references|templates|scripts|data|assets)/"
    rf"[{PLACEHOLDER}]+\.(?:md|json|py))",
    re.M,
)


def test_no_bare_intra_plugin_paths_in_runtime_files() -> None:
    offenders: list[str] = []

    for path in _runtime_files():
        text = _read(path)
        for pattern in (BARE_ROOTED, BARE_RELATIVE):
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                offenders.append(f"{_rel(path)}:{line}: {match.group(1)}")

    assert not offenders, (
        "Bare intra-plugin paths found. In Cowork and Claude Code the working "
        "directory is the user's folder, not the plugin, so these resolve to "
        "nothing. Prefix each with ${CLAUDE_PLUGIN_ROOT}/:\n  - "
        + "\n  - ".join(offenders)
    )


# ---------------------------------------------------------------------------
# Test 2: every ${CLAUDE_PLUGIN_ROOT} target exists
# ---------------------------------------------------------------------------

PLUGIN_REF = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_*<>./-]+)")


def test_every_plugin_root_reference_resolves() -> None:
    offenders: list[str] = []

    for path in _runtime_files():
        text = _read(path)
        for match in PLUGIN_REF.finditer(text):
            target = match.group(1).rstrip(".,)")
            # Strip glob and <placeholder> segments back to a real prefix.
            probe = target.split("*")[0].split("<")[0].split("[")[0].rstrip("/")
            if not probe or probe in RUNTIME_CREATED:
                continue
            if not (REPO_ROOT / probe).exists():
                line = text.count("\n", 0, match.start()) + 1
                offenders.append(f"{_rel(path)}:{line}: {target}")

    assert not offenders, (
        "${CLAUDE_PLUGIN_ROOT} references point at paths that do not exist in "
        "the repo:\n  - " + "\n  - ".join(offenders)
    )


# ---------------------------------------------------------------------------
# Test 3: nothing writes user state into the plugin directory
# ---------------------------------------------------------------------------


def test_no_skill_writes_into_the_plugin_directory() -> None:
    """The plugin directory is read-only in Cowork and replaced on update.

    Saved personas were previously written to
    ``skills/blog/references/personas/``, which would be destroyed by the next
    plugin update. User state belongs in ``${CLAUDE_PLUGIN_DATA}`` or the
    working directory.
    """
    persona_skill = SKILLS_DIR / "blog-persona" / "SKILL.md"
    if not persona_skill.is_file():
        pytest.skip("blog-persona skill not present")

    text = _read(persona_skill)
    assert "${CLAUDE_PLUGIN_DATA}" in text, (
        "blog-persona must save personas under ${CLAUDE_PLUGIN_DATA}, not "
        "inside the plugin directory."
    )
    assert f"{PLUGIN_VAR}/skills/blog-persona/references/personas" not in text, (
        "blog-persona still writes personas into the plugin directory, which "
        "is read-only in Cowork and wiped on every plugin update."
    )


# ---------------------------------------------------------------------------
# Test 4: the plugin manifest is valid and complete
# ---------------------------------------------------------------------------


def test_plugin_manifest_is_valid() -> None:
    assert MANIFEST.is_file(), ".claude-plugin/plugin.json must exist"
    manifest = json.loads(_read(MANIFEST))

    assert manifest.get("name") == "claude-blog"
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", manifest["name"]), (
        "Plugin name must be kebab-case."
    )
    assert re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")), (
        "Plugin version must be semver."
    )
    for field in ("description", "author", "license"):
        assert manifest.get(field), f"plugin.json must declare {field!r}"


def test_user_config_marks_the_api_key_sensitive() -> None:
    """A credential collected through userConfig must go to secure storage."""
    manifest = json.loads(_read(MANIFEST))
    user_config = manifest.get("userConfig", {})
    assert "google_ai_api_key" in user_config, (
        "plugin.json must expose google_ai_api_key so Cowork users can enable "
        "image generation without editing files."
    )
    key = user_config["google_ai_api_key"]
    assert key.get("sensitive") is True, (
        "google_ai_api_key must be marked sensitive so it is masked on input "
        "and held in secure storage rather than plain settings."
    )
    assert key.get("required") is not True, (
        "The API key must stay optional: the plugin's content skills work "
        "without it, and a required credential blocks install."
    )


# ---------------------------------------------------------------------------
# Test 5: the packaged archive is loadable and clean
# ---------------------------------------------------------------------------


def test_package_payload_has_manifest_at_archive_root(tmp_path) -> None:
    """Cowork reads .claude-plugin/plugin.json at the archive root."""
    import subprocess
    import sys
    import zipfile

    script = REPO_ROOT / "scripts" / "package_plugin.py"
    assert script.is_file(), "scripts/package_plugin.py must exist"

    result = subprocess.run(
        [sys.executable, str(script), "--out-dir", str(tmp_path), "--format", "plugin"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=120,
    )
    assert result.returncode == 0, f"packaging failed:\n{result.stderr}"

    archives = list(tmp_path.glob("*.plugin"))
    assert len(archives) == 1, f"expected one .plugin archive, got {archives}"

    with zipfile.ZipFile(archives[0]) as archive:
        names = set(archive.namelist())

    assert ".claude-plugin/plugin.json" in names, (
        "The manifest must sit at the archive root or the upload is rejected."
    )
    assert any(n.endswith("SKILL.md") for n in names), "No skills were packaged"
    assert not any(n.startswith("tests/") for n in names), (
        "Tests must not ship inside the distributed plugin."
    )
    assert not any(n.startswith("brain/") for n in names), (
        "brain/ is bundled project material no skill reads (~5.8 MB); it "
        "must not bloat the distributed plugin."
    )
    assert not any(".git/" in n for n in names), "Git metadata must not ship."


# ---------------------------------------------------------------------------
# Test 6: the security brief only cites tests that exist
# ---------------------------------------------------------------------------


def test_security_review_cites_only_real_tests() -> None:
    """``docs/SECURITY-REVIEW.md`` names the test enforcing each claim.

    That is the document's whole value: a reviewer can check every assertion
    against the suite. A citation that no longer resolves is worse than no
    citation, because it looks verified and is not. This caught a real drift
    when the v2.3.0 port renamed a guardrail and the brief kept the old name.
    """
    brief = REPO_ROOT / "docs" / "SECURITY-REVIEW.md"
    if not brief.is_file():
        pytest.skip("security brief not present")

    defined = set()
    for path in (REPO_ROOT / "tests").glob("test_*.py"):
        defined.update(re.findall(r"^def (test_\w+)", _read(path), re.M))

    # Citations are function names; bare module names (test_security_guardrails)
    # appear as `tests/<module>.py::<function>` and are not functions themselves.
    modules = {p.stem for p in (REPO_ROOT / "tests").glob("test_*.py")}
    cited = {n for n in re.findall(r"\btest_\w+", _read(brief))} - modules

    missing = sorted(cited - defined)
    assert not missing, (
        "docs/SECURITY-REVIEW.md cites tests that do not exist:\n  - "
        + "\n  - ".join(missing)
        + "\nUpdate the brief, or restore the guardrail it names."
    )
