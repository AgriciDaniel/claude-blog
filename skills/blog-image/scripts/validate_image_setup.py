#!/usr/bin/env python3
"""
Validate that nanobanana-mcp is properly configured for claude-blog.

Checks project .mcp.json first, then falls back to global ~/.claude/settings.json.

Checks:
1. Config file has the MCP entry
2. API key is present
3. Node.js/npx is available
4. Output directory exists or can be created

Usage:
    python3 validate_image_setup.py
    python3 validate_image_setup.py --json
"""

import argparse
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
SET_MODEL_ALIASES = {
    "flash": "set_model alias for gemini-3.1-flash-image-preview",
    "pro": "set_model alias for gemini-3-pro-image-preview",
}
PINNED_PACKAGE_ENV_MODELS = {
    "gemini-3.1-flash-image-preview": (
        "accepted by pinned package, but shut down on 2026-06-25; "
        "use gemini-3.1-flash-image through direct API or a newer MCP package"
    ),
    "gemini-3-pro-image-preview": (
        "accepted by pinned package, but shut down on 2026-06-25; "
        "use gemini-3-pro-image through direct API or a newer MCP package"
    ),
}
DIRECT_API_MODELS = {
    "gemini-3.1-flash-image": "Nano Banana 2 direct API ID",
    "gemini-3-pro-image": "Nano Banana Pro direct API ID",
    "gemini-3.1-flash-lite-image": "Nano Banana Lite direct API ID",
    "gemini-2.5-flash-image": "Nano Banana Original direct API ID",
}
DEPRECATED_MODEL_REPLACEMENTS = {
    "gemini-3.1-flash-image-preview": (
        "deprecated on 2026-05-28 and shut down on 2026-06-25; "
        "use gemini-3.1-flash-image"
    ),
    "gemini-3-pro-image-preview": (
        "deprecated on 2026-05-28 and shut down on 2026-06-25; "
        "use gemini-3-pro-image"
    ),
    "gemini-2.5-flash-image-preview": (
        "shut down on 2026-01-15; use gemini-2.5-flash-image"
    ),
    "gemini-2.0-flash-exp": (
        "shut down on 2026-06-01; use gemini-3.1-flash-image"
    ),
    "imagen-4.0-fast-generate-001": (
        "deprecated on 2026-06-15 and shuts down on 2026-08-17; "
        "use gemini-3.1-flash-image"
    ),
    "imagen-4.0-generate-001": (
        "deprecated on 2026-06-15 and shuts down on 2026-08-17; "
        "use gemini-3.1-flash-image"
    ),
    "imagen-4.0-ultra-generate-001": (
        "deprecated on 2026-06-15 and shuts down on 2026-08-17; "
        "use gemini-3.1-flash-image"
    ),
}
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


def validate_nanobanana_model(model: str) -> tuple:
    """Validate NANOBANANA_MODEL against the pinned MCP package contract."""
    model = (model or "").strip()
    if not model:
        return False, (
            f"(not set - pinned {PINNED_PACKAGE} defaults to "
            f"{PINNED_PACKAGE_DEFAULT_MODEL}, which shut down on 2026-06-25)"
        )
    if model in SET_MODEL_ALIASES:
        return False, (
            f"{model} ({SET_MODEL_ALIASES[model]}; aliases are accepted only by "
            "the set_model MCP tool, not by NANOBANANA_MODEL)"
        )
    if model in PINNED_PACKAGE_ENV_MODELS:
        return False, f"{model} ({PINNED_PACKAGE_ENV_MODELS[model]})"
    if model in DIRECT_API_MODELS:
        return False, (
            f"{model} ({DIRECT_API_MODELS[model]}; pinned {PINNED_PACKAGE} does not "
            "accept stable direct API IDs as NANOBANANA_MODEL)"
        )
    if model in DEPRECATED_MODEL_REPLACEMENTS:
        return False, f"{model} (WARNING: {DEPRECATED_MODEL_REPLACEMENTS[model]})"
    if "-preview" in model:
        return False, (
            f"{model} (WARNING: preview image models are deprecated or shut down; "
            "use stable direct API IDs outside this pinned MCP package)"
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
            print(json.dumps({"status": "error", "checks": checks}, indent=2))
        else:
            print("\nRun: python3 skills/blog-image/scripts/setup_image_mcp.py")
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
        }, indent=2))
        return 0 if passed == total else 1

    print(f"\n{'=' * 48}")
    print(f"Results: {passed}/{total} checks passed")

    if passed == total:
        print("Status: Ready to generate blog images!")
        return 0
    else:
        print("Status: Some checks failed. Fix the issues above.")
        print("Setup: python3 skills/blog-image/scripts/setup_image_mcp.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
