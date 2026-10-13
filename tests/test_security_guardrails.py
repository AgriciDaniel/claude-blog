"""Mechanical security and quality guardrails for the claude-blog repo.

These tests enforce invariants that complement the rules documented in
CLAUDE.md. Rules in prose can drift; assertions in pytest cannot. If any of
these tests fail in CI, a contributor (human or agent) has regressed a
project-wide invariant and must fix the underlying file before merging.

Invariants enforced:

1. No agent grants the ``Bash`` tool in its YAML frontmatter ``tools`` list.
2. No SKILL.md grants permission preapprovals (intentional project policy).
3. Every skill has a unique ``name`` (no duplicate command routes).
4. ``scripts/sync_flow.py``, when present, contains the required security
   primitives (host allowlist, size cap, ``--dry-run``, ``--ref``, lock file,
   license-header injection, path-traversal guard).
5. Credential write helpers in ``google_auth.py`` produce mode 0o600 files
   (atomic + restrictive perms). Closes audit VULN-002 regression risk.
6. NotebookLM credential helpers contain the chmod 600/700 hardening pattern
   (static-presence check; deeper behavioral test is gated on patchright
   being installed in the dev venv).

PyYAML + pytest. No network, no writes outside ``tmp_path``.
"""

from __future__ import annotations

import importlib.util
import os
import re
import stat
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / "agents"
SKILLS_DIR = REPO_ROOT / "skills"
SYNC_FLOW_PATH = REPO_ROOT / "scripts" / "sync_flow.py"
GOOGLE_AUTH_PATH = REPO_ROOT / "skills" / "blog-google" / "scripts" / "google_auth.py"
NOTEBOOKLM_AUTH_MANAGER_PATH = (
    REPO_ROOT / "skills" / "blog-notebooklm" / "scripts" / "auth_manager.py"
)
NOTEBOOKLM_BROWSER_UTILS_PATH = (
    REPO_ROOT / "skills" / "blog-notebooklm" / "scripts" / "browser_utils.py"
)


# All metadata checks share the real YAML parser and policy authority.
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from validate_skills import parse_frontmatter, validate_bundle, validate_frontmatter


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 1: No agent grants the Bash tool
# ---------------------------------------------------------------------------


def test_no_bash_tool_in_any_agent_frontmatter() -> None:
    """Agent tools is an allowlist; every maintained agent excludes Bash."""
    paths = sorted(AGENTS_DIR.glob("*.md"))
    assert paths
    for path in paths:
        errors = validate_frontmatter(parse_frontmatter(_read(path)), agent=True)
        assert not errors, f"{path}: {errors}"


def test_no_skill_permission_preapprovals_project_policy() -> None:
    """allowed-tools is host-valid, but this project ships no preapproval grants."""
    paths = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    assert paths
    for path in paths:
        errors = validate_frontmatter(parse_frontmatter(_read(path)))
        assert not errors, f"{path}: {errors}"


# ---------------------------------------------------------------------------
# Test 3: Skill names are globally unique
# ---------------------------------------------------------------------------


def test_unique_skill_names_and_command_routes() -> None:
    """Use the common bundle validator for names, routes and project policy."""
    assert validate_bundle(REPO_ROOT) == []


def _check_pattern(source: str, *patterns: str) -> bool:
    """Return True when at least one of ``patterns`` appears in ``source``."""
    return any(p in source for p in patterns)


def test_sync_flow_security_invariants() -> None:
    """``scripts/sync_flow.py`` must encode key security primitives in source.

    These are checked by reading the script as text rather than executing it,
    so the test never makes network calls and never spawns the script. If
    the script does not yet exist, the test skips so it can land before the
    sync flow does.
    """
    if not SYNC_FLOW_PATH.exists():
        pytest.skip("sync_flow.py not yet present")

    source = _read(SYNC_FLOW_PATH)

    # Each entry: human label -> tuple of acceptable substrings (any match wins).
    invariants: dict[str, tuple[str, ...]] = {
        "host allowlist references api.github.com": ("api.github.com",),
        "explicit host validator (function or constant)": (
            "_validate_github_url",
            "_ALLOWED_HOST",
            "ALLOWED_HOST",
            "validate_github_url",
        ),
        "size cap on downloaded payloads (~5 MiB)": (
            "_SIZE_LIMIT",
            "SIZE_LIMIT",
            "5 * 1024 * 1024",
            "5242880",
        ),
        "--dry-run flag wired into argparse": ("--dry-run",),
        "--ref flag for SHA pinning": ("--ref",),
        "lock file written for synced prompts": (
            "flow-prompts.lock",
            "LOCK_REL",
        ),
        "license-header injection (CC BY 4.0 / Daniel Agrici)": (
            "CC BY 4.0",
            "Daniel Agrici",
        ),
        "path-traversal guard on resolved paths": (
            "is_relative_to",
            ".resolve()",
            'reject "..',
            "'..'",
            '".."',
        ),
    }

    missing = [
        label
        for label, patterns in invariants.items()
        if not _check_pattern(source, *patterns)
    ]

    assert not missing, (
        f"scripts/sync_flow.py is missing required security primitives. "
        f"Add the following before merging:\n  - " + "\n  - ".join(missing)
    )


# ---------------------------------------------------------------------------
# Test 5: google_auth._write_secret_atomic produces mode 0o600 files
# ---------------------------------------------------------------------------


def _load_module(module_name: str, path: Path):
    """Load a Python module from an absolute path without polluting sys.modules."""
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_google_auth_write_secret_atomic_sets_mode_0600(tmp_path) -> None:
    """``_write_secret_atomic`` MUST produce a file at mode 0o600.

    This is the regression gate for audit VULN-002 (OAuth refresh token +
    client_secret were previously written at default umask, mode 0644).
    Skipped on Windows where POSIX mode bits are not enforced.
    """
    if not GOOGLE_AUTH_PATH.exists():
        pytest.skip("google_auth.py not present at expected path")
    if os.name == "nt":
        pytest.skip("POSIX mode bits not enforced on Windows")

    google_auth = _load_module("_test_google_auth", GOOGLE_AUTH_PATH)
    helper = getattr(google_auth, "_write_secret_atomic", None)
    assert helper is not None, (
        "google_auth._write_secret_atomic helper is missing. "
        "It is required to enforce atomic, mode-0600 credential writes."
    )

    target = tmp_path / "subdir" / "secret.json"
    helper(str(target), '{"refresh_token": "test-value"}')

    assert target.exists(), "secret file was not created"
    mode = stat.S_IMODE(target.stat().st_mode)
    assert mode == 0o600, (
        f"_write_secret_atomic produced mode {oct(mode)}, expected 0o600. "
        "Audit VULN-002 regression: any local user could read tokens."
    )
    # Parent directory should be 0o700 too (owner-only traversal).
    parent_mode = stat.S_IMODE(target.parent.stat().st_mode)
    assert parent_mode == 0o700, (
        f"_write_secret_atomic parent dir mode is {oct(parent_mode)}, "
        "expected 0o700."
    )


# ---------------------------------------------------------------------------
# Test 6: NotebookLM credential helpers contain chmod hardening pattern
# ---------------------------------------------------------------------------


def test_notebooklm_credential_files_contain_chmod_hardening() -> None:
    """``auth_manager.py`` and ``browser_utils.py`` must call chmod 600/700.

    Static-presence test (no module import) so it runs without ``patchright``
    being installed. Behavioral test for the chmod helper would require the
    skill's local ``.venv`` and is intentionally not run in base CI.

    Closes audit VULN-004 regression risk: NotebookLM session cookies
    (Google ``__Secure-1PSID``/``SAPISID``) MUST be written user-private.
    """
    targets = {
        "auth_manager.py": NOTEBOOKLM_AUTH_MANAGER_PATH,
        "browser_utils.py": NOTEBOOKLM_BROWSER_UTILS_PATH,
    }

    missing: list[str] = []
    for label, path in targets.items():
        if not path.exists():
            pytest.skip(f"{label} not present at expected path")
        source = _read(path)
        # Require either explicit chmod 600+700 calls OR at least one
        # call site of `_harden_perms(` (parenthesis distinguishes call from
        # mere definition; the helper is useless if defined-but-never-called).
        has_chmod_600 = "0o600" in source
        has_chmod_700 = "0o700" in source
        # Count helper calls (paren after name). The `def _harden_perms(`
        # line counts as a call by this regex, so require >= 2 occurrences:
        # 1 for the def, at least 1 for an actual call.
        helper_uses = source.count("_harden_perms(")
        has_helper_call = helper_uses >= 2  # def + at least 1 call

        if not (has_chmod_600 and has_chmod_700) and not has_helper_call:
            missing.append(
                f"{label}: missing chmod 600/700 calls AND no _harden_perms "
                "call site found (def alone does not satisfy the gate). "
                "Add explicit chmod after every credential write."
            )

    assert not missing, (
        "NotebookLM credential files are missing chmod 600/700 hardening:\n  - "
        + "\n  - ".join(missing)
    )


# ---------------------------------------------------------------------------
# Test 7: .mcp.json is gitignored (closes VULN-003)
# ---------------------------------------------------------------------------


def test_mcp_json_is_gitignored() -> None:
    """``.gitignore`` must list ``.mcp.json`` to prevent committed-secret risk.

    The audit VULN-003 finding: ``.gitignore`` previously excluded ``.env``
    and ``*.key`` but NOT ``.mcp.json``. The setup script defaults could
    write a literal API key into a tracked file, leaking on next ``git add``.
    """
    gitignore = REPO_ROOT / ".gitignore"
    assert gitignore.exists(), ".gitignore must exist at repo root"
    text = _read(gitignore)
    assert ".mcp.json" in text, (
        "VULN-003 regression: .gitignore must include `.mcp.json` to block "
        "accidental commit of MCP server configs that may carry inline "
        "GOOGLE_AI_API_KEY values."
    )


def test_user_invocable_skills_have_complete_frontmatter() -> None:
    """Explicit user-invocable and required fields are repository policy.

    The native host defaults a missing user-invocable to true. The common
    validator reports missing declarations rather than treating them as opt-out.
    """
    assert validate_bundle(REPO_ROOT) == []
