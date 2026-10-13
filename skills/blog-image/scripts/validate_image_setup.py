#!/usr/bin/env python3
"""
Validate that nanobanana-mcp is properly configured for claude-blog.

Checks project .mcp.json first, then falls back to global ~/.claude/settings.json.

The pinned package (@ycse/nanobanana-mcp@1.1.1, the newest release) can only
call two preview models that Google shut down on 2026-06-25, so a configured
MCP server cannot generate images today. The validator reports that accurately
and recommends the direct API path (scripts/generate_hero.py) with the current
model IDs from https://ai.google.dev/gemini-api/docs/models (checked 2026-10-12).

Checks:
1. Config file has the MCP entry
2. API key is present
3. NANOBANANA_MODEL is a value the package accepts and Google still serves
4. Node.js/npx is available
5. Output directory exists or can be created

Usage:
    python3 validate_image_setup.py
    python3 validate_image_setup.py --json
"""

import argparse
import datetime
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

MCP_NAME = "nanobanana-mcp"
OUTPUT_DIR = Path.home() / "Documents" / "nanobanana_generated"
GLOBAL_SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
PINNED_PACKAGE = "@ycse/nanobanana-mcp@1.1.1"
PINNED_PACKAGE_DEFAULT_MODEL = "gemini-3.1-flash-image-preview"
# Sources, fetched 2026-10-12:
#   https://ai.google.dev/gemini-api/docs/models        (current model IDs)
#   https://ai.google.dev/gemini-api/docs/deprecations  (shutdown dates)
#   @ycse/nanobanana-mcp@1.1.1 dist/index.js: VALID_MODELS lists exactly the two
#   preview IDs below; any other NANOBANANA_MODEL silently falls back to the
#   default. 1.1.1 is the newest published release.
PREVIEW_SHUTDOWN = datetime.date(2026, 6, 25)
SET_MODEL_ALIASES = {
    "flash": "set_model alias for gemini-3.1-flash-image-preview",
    "pro": "set_model alias for gemini-3-pro-image-preview",
}
# Models the pinned package accepts in NANOBANANA_MODEL, with Google's shutdown date.
PINNED_PACKAGE_ENV_MODELS = {
    "gemini-3.1-flash-image-preview": (PREVIEW_SHUTDOWN, "gemini-nano-banana-2.1"),
    "gemini-3-pro-image-preview": (PREVIEW_SHUTDOWN, "gemini-3-pro-image"),
}
# Current direct-API IDs (models page, 2026-10-12).
DIRECT_API_MODELS = {
    "gemini-nano-banana-2.1": "Nano Banana 2.1 direct API ID (released 2026-10-06)",
    "gemini-3.1-flash-image": "Nano Banana 2 direct API ID",
    "gemini-3-pro-image": "Nano Banana Pro direct API ID",
    "gemini-3.1-flash-lite-image": "Nano Banana 2 Lite direct API ID",
    "gemini-2.5-flash-image": (
        "Nano Banana (original) direct API ID, shutdown announced for 2027-03-15"
    ),
}
# scripts/generate_hero.py allowlists these; gemini-nano-banana-2.1 is newest on
# Google's models page but is not in that allowlist yet.
RECOMMENDED_DIRECT_MODEL = "gemini-3.1-flash-image"
DEPRECATED_MODEL_REPLACEMENTS = {
    "gemini-2.5-flash-image-preview": (
        "shut down on 2026-01-15; use gemini-nano-banana-2.1"
    ),
    "gemini-2.0-flash-preview-image-generation": (
        "shut down on 2025-11-14; use gemini-nano-banana-2.1"
    ),
    "imagen-4.0-fast-generate-001": (
        "shut down on 2026-08-17; use gemini-nano-banana-2.1"
    ),
    "imagen-4.0-generate-001": (
        "shut down on 2026-08-17; use gemini-nano-banana-2.1"
    ),
    "imagen-4.0-ultra-generate-001": (
        "shut down on 2026-08-17; use gemini-nano-banana-2.1"
    ),
}
RECOMMENDATION = (
    f"Use the direct Gemini API path instead: scripts/generate_hero.py with "
    f"{RECOMMENDED_DIRECT_MODEL} (default), gemini-3.1-flash-lite-image or "
    f"gemini-3-pro-image (Google also lists the newer gemini-nano-banana-2.1). The pinned {PINNED_PACKAGE} can only call the preview "
    f"models gemini-3.1-flash-image-preview and gemini-3-pro-image-preview, which "
    f"shut down on {PREVIEW_SHUTDOWN.isoformat()}, and no newer release exists "
    "(sources: https://ai.google.dev/gemini-api/docs/models and "
    "https://ai.google.dev/gemini-api/docs/deprecations, checked 2026-10-12)."
)
PLACEHOLDER_RE = re.compile(r"^\$\{([A-Za-z_][A-Za-z0-9_]*)\}$")


def find_project_mcp_json() -> Path:
    """Find the project-level .mcp.json by looking for .claude-plugin/plugin.json."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        candidate = current / ".claude-plugin" / "plugin.json"
        if candidate.exists():
            return current / ".mcp.json"
        parent = current.parent
        if parent == current:
            break
        current = parent
    current = Path.cwd()
    for _ in range(10):
        candidate = current / ".claude-plugin" / "plugin.json"
        if candidate.exists():
            return current / ".mcp.json"
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def check(label: str, passed: bool, detail: str = "", results: list = None, quiet: bool = False) -> bool:
    status = "PASS" if passed else "FAIL"
    msg = f"  [{status}] {label}"
    if detail:
        msg += f" - {detail}"
    if results is not None:
        results.append({"label": label, "passed": passed, "detail": detail})
    if not quiet:
        print(msg)
    return passed


def _supported_model_list() -> str:
    return ", ".join(sorted(PINNED_PACKAGE_ENV_MODELS))


def _package_model_status(model: str, today: datetime.date) -> tuple:
    """Return (ok, detail) for a model ID the pinned package accepts."""
    shutdown, replacement = PINNED_PACKAGE_ENV_MODELS[model]
    if today < shutdown:
        return True, f"{model} (accepted by pinned {PINNED_PACKAGE}; shuts down on {shutdown.isoformat()})"
    return False, (
        f"{model} (accepted by pinned {PINNED_PACKAGE}, but Google shut it down on "
        f"{shutdown.isoformat()}; its replacement {replacement} is not accepted by "
        "this package)"
    )


def validate_nanobanana_model(model: str, today: datetime.date = None) -> tuple:
    """Validate NANOBANANA_MODEL against the pinned MCP package contract.

    Returns (ok, detail). ok is True only when the package accepts the value
    and Google still serves that model on ``today`` (default: the real date).
    """
    today = today or datetime.date.today()
    model = (model or "").strip()
    if not model:
        ok, detail = _package_model_status(PINNED_PACKAGE_DEFAULT_MODEL, today)
        return ok, f"(not set, pinned package default) {detail}"
    if model in SET_MODEL_ALIASES:
        return False, (
            f"{model} ({SET_MODEL_ALIASES[model]}; aliases are accepted only by "
            "the set_model MCP tool, not by NANOBANANA_MODEL)"
        )
    if model in PINNED_PACKAGE_ENV_MODELS:
        return _package_model_status(model, today)
    if model in DIRECT_API_MODELS:
        return False, (
            f"{model} ({DIRECT_API_MODELS[model]}; usable through the direct API "
            f"path, but pinned {PINNED_PACKAGE} ignores it and falls back to "
            f"{PINNED_PACKAGE_DEFAULT_MODEL})"
        )
    if model in DEPRECATED_MODEL_REPLACEMENTS:
        return False, f"{model} (WARNING: {DEPRECATED_MODEL_REPLACEMENTS[model]})"
    if "-preview" in model:
        return False, (
            f"{model} (WARNING: preview image models are deprecated or shut down; "
            f"use a stable direct API ID such as {RECOMMENDED_DIRECT_MODEL})"
        )
    return False, f"{model} (unsupported by pinned {PINNED_PACKAGE}; accepts: {_supported_model_list()})"


def find_mcp_config() -> tuple:
    """Find MCP config. Returns (config_dict, path_label, error)."""
    # Try project .mcp.json first
    project_path = find_project_mcp_json()
    if project_path and project_path.exists():
        try:
            with open(project_path) as f:
                config = json.load(f)
            if MCP_NAME in config.get("mcpServers", {}):
                return config, f"project .mcp.json ({project_path})", None
        except json.JSONDecodeError as exc:
            return None, None, (
                f"Invalid JSON in project .mcp.json ({project_path}): "
                f"line {exc.lineno}, column {exc.colno}"
            )
        except OSError as exc:
            return None, None, f"Cannot read project .mcp.json ({project_path}): {exc}"

    # Fallback to global settings
    if GLOBAL_SETTINGS_PATH.exists():
        try:
            with open(GLOBAL_SETTINGS_PATH) as f:
                config = json.load(f)
            if MCP_NAME in config.get("mcpServers", {}):
                return config, f"global settings ({GLOBAL_SETTINGS_PATH})", None
        except json.JSONDecodeError as exc:
            return None, None, (
                f"Invalid JSON in global settings ({GLOBAL_SETTINGS_PATH}): "
                f"line {exc.lineno}, column {exc.colno}"
            )
        except OSError as exc:
            return None, None, f"Cannot read global settings ({GLOBAL_SETTINGS_PATH}): {exc}"

    return None, None, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate nanobanana-mcp setup")
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    args = parser.parse_args()
    quiet = args.json
    checks = []

    if not quiet:
        print("claude-blog - Image Generation Setup Validation")
        print("=" * 48)
    results = []

    # 1-2. Find and load config
    config, config_label, config_error = find_mcp_config()

    if config_error:
        results.append(check("MCP config parseable", False, config_error, checks, quiet))
        if args.json:
            print(json.dumps({"status": "error", "checks": checks}, indent=2))
        else:
            print(f"\n{RECOMMENDATION}")
        return 1

    if config is None:
        results.append(check(
            "MCP config found",
            False,
            "Not found in project .mcp.json or global settings.json",
            checks,
            quiet,
        ))
        if args.json:
            print(json.dumps({
                "status": "error",
                "checks": checks,
                "recommendation": RECOMMENDATION,
            }, indent=2))
        else:
            print(f"\n{RECOMMENDATION}")
            print("MCP setup (limited to the shut-down preview models): "
                  "python3 skills/blog-image/scripts/setup_image_mcp.py")
        return 1

    results.append(check("MCP config found", True, config_label, checks, quiet))

    # 3. MCP entry exists
    servers = config.get("mcpServers", {})
    has_mcp = MCP_NAME in servers
    results.append(check(f"MCP server '{MCP_NAME}' configured", has_mcp, results=checks, quiet=quiet))

    if has_mcp:
        mcp = servers[MCP_NAME]

        # 4. Command is npx
        results.append(check(
            "Command is 'npx'",
            mcp.get("command") == "npx",
            mcp.get("command", "(missing)"),
            checks,
            quiet,
        ))

        # 5. Package is correct (accepts pinned versions like @ycse/nanobanana-mcp@1.1.1)
        mcp_args = mcp.get("args", [])
        has_pkg = any(
            isinstance(a, str) and a.startswith("@ycse/nanobanana-mcp")
            for a in mcp_args
        )
        is_pinned = any(
            isinstance(a, str) and a.startswith("@ycse/nanobanana-mcp@")
            for a in mcp_args
        )
        pkg_detail = str(mcp_args)
        if has_pkg and not is_pinned:
            pkg_detail += " (WARNING: not version-pinned - supply chain risk)"
        results.append(check(
            "Package is @ycse/nanobanana-mcp",
            has_pkg,
            pkg_detail,
            checks,
            quiet,
        ))

        # 6. API key present
        env = mcp.get("env", {})
        key = env.get("GOOGLE_AI_API_KEY", "")
        key_set = bool(key)
        placeholder_match = PLACEHOLDER_RE.match(key or "")
        if placeholder_match:
            var_name = placeholder_match.group(1)
            resolved = bool(os.environ.get(var_name))
            results.append(check(
                "GOOGLE_AI_API_KEY is set",
                resolved,
                f"{key} resolves from environment" if resolved else f"{var_name} is not exported",
                checks,
                quiet,
            ))
        else:
            # Closes audit VULN-032: length-only display, no prefix/suffix leak.
            display = f"<{len(key)} chars, set>" if key_set else "(empty)"
            results.append(check(
                "GOOGLE_AI_API_KEY is set",
                key_set,
                display,
                checks,
                quiet,
            ))

        # 7. Model configured. The pinned package does not support stable image IDs.
        model = env.get("NANOBANANA_MODEL", "")
        model_ok, model_detail = validate_nanobanana_model(model)
        results.append(check(
            "NANOBANANA_MODEL is supported",
            model_ok,
            model_detail,
            checks,
            quiet,
        ))

    # 8. Node.js/npx available
    has_npx = shutil.which("npx") is not None
    results.append(check(
        "npx is available in PATH",
        has_npx,
        shutil.which("npx") or "not found - install Node.js 18+",
        checks,
        quiet,
    ))

    # 9. Output directory
    if OUTPUT_DIR.exists():
        try:
            with tempfile.NamedTemporaryFile(
                dir=OUTPUT_DIR,
                prefix=".validate-",
                suffix=".tmp",
                delete=True,
            ):
                pass
            results.append(check("Output directory writable", True, str(OUTPUT_DIR), checks, quiet))
        except OSError as e:
            results.append(check("Output directory writable", False, str(e), checks, quiet))
    else:
        parent_ok = OUTPUT_DIR.parent.exists() and os.access(OUTPUT_DIR.parent, os.W_OK)
        results.append(check(
            "Output directory parent writable",
            parent_ok,
            f"{OUTPUT_DIR} will be created by generation" if parent_ok else str(OUTPUT_DIR.parent),
            checks,
            quiet,
        ))

    # Summary
    passed = sum(1 for r in results if r)
    total = len(results)
    if args.json:
        print(json.dumps({
            "status": "success" if passed == total else "error",
            "passed": passed,
            "total": total,
            "checks": checks,
            **({} if passed == total else {"recommendation": RECOMMENDATION}),
        }, indent=2))
        return 0 if passed == total else 1

    print(f"\n{'=' * 48}")
    print(f"Results: {passed}/{total} checks passed")

    if passed == total:
        print("Status: Ready to generate blog images!")
        return 0
    else:
        print("Status: Some checks failed. Fix the issues above.")
        print(RECOMMENDATION)
        return 1


if __name__ == "__main__":
    sys.exit(main())
