"""Mechanical security and quality guardrails for the claude-blog repo.

These tests enforce invariants that complement the rules documented in
CLAUDE.md. Rules in prose can drift; assertions in pytest cannot. If any of
these tests fail in CI, a contributor (human or agent) has regressed a
project-wide invariant and must fix the underlying file before merging.

Invariants enforced:

1. No agent grants the ``Bash`` tool in its YAML frontmatter ``tools`` list.
2. No SKILL.md uses the unsupported ``allowed-tools`` frontmatter key.
3. Every skill has a unique ``name`` (no duplicate command routes).
4. ``scripts/sync_flow.py``, when present, contains the required security
   primitives (host allowlist, size cap, ``--dry-run``, ``--ref``, lock file,
   license-header injection, path-traversal guard).
5. Credential write helpers in ``google_auth.py`` produce mode 0o600 files
   (atomic + restrictive perms). Closes audit VULN-002 regression risk.
6. NotebookLM credential helpers contain the chmod 600/700 hardening pattern
   (static-presence check; deeper behavioral test is gated on patchright
   being installed in the dev venv).

Stdlib + pytest only. No network, no writes outside ``tmp_path``.
"""

from __future__ import annotations

import importlib.util
import os
import re
import stat
import sys
import warnings
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


# ---------------------------------------------------------------------------
# Minimal stdlib-only frontmatter parser
# ---------------------------------------------------------------------------
#
# We intentionally avoid PyYAML: it is not a dependency in pyproject.toml and
# the brief forbids new dependencies. The parser is deliberately small and
# only handles the shapes that actually appear in agent and SKILL.md files:
#
#   key: value
#   key: "quoted value"
#   key: >          (folded scalar continued on subsequent indented lines)
#   key:            (followed by a YAML-style list)
#     - item
#     - "item"
#
# Anything more exotic would itself be a code smell in a SKILL.md / agent file
# and is out of scope for these guardrails.

_FRONTMATTER_RE = re.compile(
    r"\A---\s*\n(?P<body>.*?)\n---\s*(?:\n|$)",
    re.DOTALL,
)


def _split_frontmatter(text: str) -> str | None:
    """Return the raw YAML body between the leading ``---`` markers.

    Returns ``None`` if the file does not start with a frontmatter block.
    """
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return None
    return match.group("body")


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> dict | None:
    """Parse the leading YAML frontmatter into a dict.

    Returns ``None`` when no frontmatter block is present so callers can
    distinguish "missing" from "empty".
    """
    body = _split_frontmatter(text)
    if body is None:
        return None

    result: dict = {}
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        # Skip blank lines and comments at the top level.
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        # Only top-level keys (no leading whitespace) start a new entry.
        if raw[:1] in (" ", "\t"):
            i += 1
            continue

        if ":" not in raw:
            i += 1
            continue

        key, _, rest = raw.partition(":")
        key = key.strip()
        rest = rest.strip()

        # Folded scalar: collect indented continuation lines as a string.
        if rest in (">", "|", ">-", "|-"):
            collected: list[str] = []
            i += 1
            while i < len(lines) and (
                lines[i].startswith((" ", "\t")) or not lines[i].strip()
            ):
                collected.append(lines[i].strip())
                i += 1
            result[key] = " ".join(part for part in collected if part)
            continue

        # YAML-style list on subsequent indented lines.
        if rest == "":
            items: list[str] = []
            i += 1
            while i < len(lines) and (
                lines[i].startswith((" ", "\t")) or not lines[i].strip()
            ):
                line = lines[i]
                line_stripped = line.strip()
                if line_stripped.startswith("- "):
                    items.append(_strip_quotes(line_stripped[2:].strip()))
                elif line_stripped == "-":
                    items.append("")
                # Ignore nested mapping continuations.
                i += 1
            if items:
                result[key] = items
            else:
                # Empty value with no list. Record as None rather than fabricate.
                result[key] = None
            continue

        # Inline list: key: [a, b, c]
        if rest.startswith("[") and rest.endswith("]"):
            inner = rest[1:-1].strip()
            if inner:
                result[key] = [_strip_quotes(p.strip()) for p in inner.split(",")]
            else:
                result[key] = []
            i += 1
            continue

        # Plain scalar.
        result[key] = _strip_quotes(rest)
        i += 1

    return result


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 1: No agent grants the Bash tool
# ---------------------------------------------------------------------------


def test_no_bash_tool_in_any_agent_frontmatter() -> None:
    """No ``agents/*.md`` may list ``Bash`` in its ``tools`` frontmatter field.

    Agents that omit ``tools`` entirely receive the default tool surface,
    which is a separate concern handled elsewhere. Files without parseable
    frontmatter are reported as a pytest warning rather than a failure so
    drafts and READMEs do not break CI.
    """
    if not AGENTS_DIR.is_dir():
        pytest.skip(f"agents directory missing at {AGENTS_DIR}")

    agent_files = sorted(AGENTS_DIR.glob("*.md"))
    assert agent_files, f"No agent .md files found under {AGENTS_DIR}"

    offenders: list[str] = []
    for path in agent_files:
        text = _read(path)
        fm = parse_frontmatter(text)
        if fm is None:
            warnings.warn(
                f"Agent {path.relative_to(REPO_ROOT)} has no parseable "
                "frontmatter; skipping Bash check for this file.",
                stacklevel=1,
            )
            continue

        tools = fm.get("tools")
        if tools is None:
            # No tools field => default tool access. Out of scope.
            continue

        # Normalise to a list of strings for inspection.
        if isinstance(tools, str):
            tool_items = [t.strip() for t in tools.split(",")]
        elif isinstance(tools, list):
            tool_items = [str(t).strip() for t in tools]
        else:
            tool_items = []

        # Strip wrapping quotes that may survive if YAML had `"Bash"` or `'Bash'`.
        normalised = [_strip_quotes(t) for t in tool_items]

        if "Bash" in normalised:
            offenders.append(str(path.relative_to(REPO_ROOT)))

    assert not offenders, (
        "Found agents granting the `Bash` tool in their frontmatter. "
        "Agents must not have shell access. Remove `Bash` from the `tools:` "
        "list in:\n  - " + "\n  - ".join(offenders)
    )


# ---------------------------------------------------------------------------
# Test 2: No SKILL.md uses the invalid `allowed-tools` field
# ---------------------------------------------------------------------------


def test_no_allowed_tools_field_in_skills() -> None:
    """``allowed-tools`` is not a valid Claude Code SKILL.md frontmatter key.

    Per CLAUDE.md, valid fields are: name, description, user-invokable,
    argument-hint, compatibility, license, metadata, disable-model-invocation.
    Setting ``allowed-tools`` silently does nothing and signals confusion
    with the Claude Code agent / settings schema.
    """
    if not SKILLS_DIR.is_dir():
        pytest.skip(f"skills directory missing at {SKILLS_DIR}")

    skill_files = sorted(SKILLS_DIR.rglob("SKILL.md"))
    assert skill_files, f"No SKILL.md files found under {SKILLS_DIR}"

    offenders: list[str] = []
    for path in skill_files:
        text = _read(path)
        fm = parse_frontmatter(text)
        if fm is None:
            warnings.warn(
                f"Skill {path.relative_to(REPO_ROOT)} has no parseable "
                "frontmatter; cannot check allowed-tools.",
                stacklevel=1,
            )
            continue

        if "allowed-tools" in fm:
            offenders.append(str(path.relative_to(REPO_ROOT)))

    assert not offenders, (
        "Found SKILL.md files using the invalid `allowed-tools` frontmatter "
        "key. This field is not part of the Claude Code SKILL.md spec and is "
        "silently ignored. Remove it from:\n  - " + "\n  - ".join(offenders)
    )


# ---------------------------------------------------------------------------
# Test 3: Skill names are globally unique
# ---------------------------------------------------------------------------


def test_unique_skill_names_and_command_routes() -> None:
    """Every skill must declare a unique ``name`` value.

    Duplicate names collide on the slash-command route surface and one of
    the skills will be unreachable. ``argument-hint`` collisions are
    permitted (multiple skills can share the same hint shape) and are not
    a failure here, but duplicate ``name`` values always are.
    """
    if not SKILLS_DIR.is_dir():
        pytest.skip(f"skills directory missing at {SKILLS_DIR}")

    skill_files = sorted(SKILLS_DIR.rglob("SKILL.md"))
    assert skill_files, f"No SKILL.md files found under {SKILLS_DIR}"

    name_to_paths: dict[str, list[str]] = {}
    missing_name: list[str] = []

    for path in skill_files:
        text = _read(path)
        fm = parse_frontmatter(text)
        if fm is None:
            warnings.warn(
                f"Skill {path.relative_to(REPO_ROOT)} has no parseable "
                "frontmatter; cannot check name uniqueness.",
                stacklevel=1,
            )
            continue

        name = fm.get("name")
        if not name or not isinstance(name, str):
            missing_name.append(str(path.relative_to(REPO_ROOT)))
            continue

        name_to_paths.setdefault(name, []).append(str(path.relative_to(REPO_ROOT)))

    duplicate_messages = [
        f"Duplicate skill name '{name}' found at " + " and ".join(paths)
        for name, paths in sorted(name_to_paths.items())
        if len(paths) > 1
    ]

    failure_lines: list[str] = []
    if duplicate_messages:
        failure_lines.append("Skill name collisions:")
        failure_lines.extend(f"  - {msg}" for msg in duplicate_messages)
    if missing_name:
        failure_lines.append(
            "SKILL.md files missing a `name:` frontmatter field:"
        )
        failure_lines.extend(f"  - {p}" for p in missing_name)

    assert not failure_lines, "\n".join(failure_lines)


# ---------------------------------------------------------------------------
# Test 4: sync_flow.py security invariants
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Test 8: Every user-invokable SKILL.md has complete frontmatter
# ---------------------------------------------------------------------------


def test_user_invokable_skills_have_complete_frontmatter() -> None:
    """Every user-invokable SKILL.md must declare ``description``,
    ``argument-hint``, and ``license`` in frontmatter.

    This test was added after a meta-audit found 15 user-invokable skills
    missing one or both of ``argument-hint`` / ``license``, a class issue
    that the chair's verifier (a single-skill check on blog-rewrite) had
    missed. Static-presence test using the project's stdlib-only frontmatter
    parser; no PyYAML dependency added.
    """
    if not SKILLS_DIR.is_dir():
        pytest.skip(f"skills directory missing at {SKILLS_DIR}")

    skill_files = sorted(SKILLS_DIR.rglob("SKILL.md"))
    assert skill_files, f"No SKILL.md files found under {SKILLS_DIR}"

    required_for_user_invokable = ("description", "argument-hint", "license")
    offenders: list[str] = []

    for path in skill_files:
        text = _read(path)
        fm = parse_frontmatter(text)
        if fm is None:
            warnings.warn(
                f"Skill {path.relative_to(REPO_ROOT)} has no parseable "
                "frontmatter; cannot check completeness.",
                stacklevel=1,
            )
            continue

        # Skip non-user-invokable skills (internal helpers like blog-chart).
        # Treat missing user-invokable as opt-out (the project rule is
        # explicit declaration; absence means "not a slash command").
        user_inv = fm.get("user-invokable")
        is_user_invokable = (
            user_inv is True
            or (isinstance(user_inv, str) and user_inv.lower() == "true")
        )
        if not is_user_invokable:
            continue

        missing = [field for field in required_for_user_invokable if field not in fm]
        if missing:
            offenders.append(
                f"{path.relative_to(REPO_ROOT)}: missing {missing}"
            )

    assert not offenders, (
        "User-invokable SKILL.md files are missing required frontmatter "
        "fields. Every user-invokable skill MUST declare description, "
        "argument-hint, and license:\n  - " + "\n  - ".join(offenders)
    )


# ---------------------------------------------------------------------------
# Test 9: the shipped MCP config carries no credential (v2.3.0, Cowork port)
# ---------------------------------------------------------------------------


def test_shipped_mcp_config_carries_no_literal_credential() -> None:
    """``mcp-servers.json`` is committed and shipped inside the plugin, so a
    literal credential here would be published to every user.

    Values must stay ``${...}`` placeholders that Claude resolves at runtime
    from secure storage (``userConfig``) or the environment.

    The file is deliberately not named ``.mcp.json``: that filename is also read
    as a *project-scoped* config, so a contributor working in this repo would
    have Claude try to launch it with ``${CLAUDE_PLUGIN_ROOT}`` unresolved.
    Keeping the distributed name distinct also lets ``.gitignore`` keep its
    blanket ``.mcp.json`` rule with no exception.
    """
    import json as _json

    mcp_path = REPO_ROOT / "mcp-servers.json"
    assert mcp_path.is_file(), "mcp-servers.json must exist at the plugin root"

    config = _json.loads(_read(mcp_path))
    servers = config.get("mcpServers", {})
    assert servers, "mcp-servers.json must declare at least one MCP server"

    offenders: list[str] = []
    for name, server in servers.items():
        for key, value in (server.get("env") or {}).items():
            if not isinstance(value, str):
                continue
            unresolved = value.startswith("${") and value.endswith("}")
            if not unresolved and value.strip():
                offenders.append(f"{name}.env.{key} = {value!r}")

    assert not offenders, (
        "mcp-servers.json contains literal env values where only `${...}` "
        "placeholders are allowed:\n  - " + "\n  - ".join(offenders)
    )

    manifest = _json.loads(_read(REPO_ROOT / ".claude-plugin" / "plugin.json"))
    assert manifest.get("mcpServers") == "./mcp-servers.json", (
        "plugin.json must point `mcpServers` at ./mcp-servers.json, otherwise "
        "the server is never registered for plugin installs."
    )


def test_mcp_server_is_opt_in_via_launcher() -> None:
    """Enabling the plugin must not download or run third-party code.

    A plugin's MCP servers start as soon as the plugin is enabled. Pointing the
    config straight at ``npx @ycse/nanobanana-mcp`` would mean every install
    fetches and executes a third-party npm package unprompted - a reasonable
    thing for a security review to reject. The launcher gates that behind a
    configured API key and pins an exact version.
    """
    import json as _json

    config = _json.loads(_read(REPO_ROOT / "mcp-servers.json"))
    for name, server in config.get("mcpServers", {}).items():
        argv = [server.get("command", "")] + list(server.get("args") or [])
        joined = " ".join(argv)
        assert "npx" not in joined, (
            f"MCP server {name!r} invokes npx directly. Route it through "
            "scripts/nanobanana-launcher.mjs so it stays opt-in."
        )

    launcher = REPO_ROOT / "scripts" / "nanobanana-launcher.mjs"
    assert launcher.is_file(), "scripts/nanobanana-launcher.mjs must exist"
    source = _read(launcher)

    assert re.search(r"@ycse/nanobanana-mcp@\d+\.\d+\.\d+", source), (
        "The launcher must pin an exact nanobanana version, never `latest`."
    )
    assert "shell: false" in source, (
        "The launcher must spawn with shell:false so argv is never handed to "
        "a shell."
    )
    assert "serveInert" in source, (
        "With no API key the launcher must serve an inert MCP session (zero "
        "tools) rather than exiting, so the client does not report the plugin "
        "as a failed connection on every session."
    )
    assert "tools: []" in source or '"tools": []' in source or "tools/list" in source, (
        "The inert path must answer tools/list with an empty tool set."
    )
