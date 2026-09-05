#!/usr/bin/env python3
"""Report which claude-blog capabilities are available in the current runtime.

Skills call this before attempting anything that needs Python packages,
credentials, or an MCP server, so Claude can say "this needs X here" instead of
surfacing a stack trace. Run it as:

    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/runtime_capabilities.py" --json
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/runtime_capabilities.py" --check google

Stdlib only. Read-only: no network, no writes, no credential values printed --
only whether a credential is present.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import shutil
import sys
from pathlib import Path

PLUGIN_ROOT = Path(
    os.environ.get("CLAUDE_PLUGIN_ROOT") or Path(__file__).resolve().parent.parent
)

GOOGLE_CONFIG = Path(
    os.path.expanduser("~/.config/claude-seo/google-api.json")
)


def _has_module(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def _detect_surface() -> str:
    """Best-effort guess at which Claude surface we are running on.

    Purely advisory - used to phrase guidance, never to gate behaviour. When we
    cannot tell, say so rather than guessing wrong.
    """
    if os.environ.get("CLAUDE_COWORK") or os.environ.get("COWORK_SESSION_ID"):
        return "cowork"
    if os.environ.get("CLAUDE_CODE_ENTRYPOINT") or os.environ.get("CLAUDECODE"):
        return "claude-code"
    return "unknown"


def _persona_store() -> dict[str, object]:
    data_dir = os.environ.get("CLAUDE_PLUGIN_DATA")
    if data_dir:
        return {"path": str(Path(data_dir) / "personas"), "kind": "plugin-data"}
    return {"path": str(Path.cwd() / ".claude-blog" / "personas"), "kind": "working-dir"}


def capabilities() -> dict[str, object]:
    python_ok = sys.version_info >= (3, 11)

    checks: dict[str, object] = {
        "surface": _detect_surface(),
        "platform": platform.system().lower(),
        "python": {
            "version": platform.python_version(),
            "supported": python_ok,
            "note": "" if python_ok else "claude-blog scripts require Python 3.11+.",
        },
        "plugin_root": str(PLUGIN_ROOT),
        "plugin_root_readable": (PLUGIN_ROOT / "skills").is_dir(),
        "persona_store": _persona_store(),
    }

    # --- /blog analyze : the only script path most users ever touch.
    checks["analyze"] = {
        "available": python_ok
        and (PLUGIN_ROOT / "scripts/analyze_blog.py").is_file(),
        "optional_deps": {
            "textstat": _has_module("textstat"),
            "beautifulsoup4": _has_module("bs4"),
        },
        "degrades_to": "Heuristic scoring without readability grades when "
        "textstat is missing.",
    }

    # --- /blog google : needs the google-api client stack plus a credential.
    google_deps = {
        "requests": _has_module("requests"),
        "googleapiclient": _has_module("googleapiclient"),
        "google.auth": _has_module("google.auth"),
    }
    has_google_credential = bool(
        os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        or GOOGLE_CONFIG.is_file()
    )
    checks["google"] = {
        "available": python_ok and all(google_deps.values()) and has_google_credential,
        "deps": google_deps,
        "credential_present": has_google_credential,
        "config_path": str(GOOGLE_CONFIG),
        "degrades_to": "Run `/blog google setup`. On a hosted Cowork session "
        "without a persistent home directory, supply credentials through "
        "environment variables instead of the config file.",
    }

    # --- /blog image : opt-in MCP server, desktop only.
    image_key = (os.environ.get("GOOGLE_AI_API_KEY") or "").strip()
    if image_key.startswith("${") and image_key.endswith("}"):
        image_key = ""
    checks["image"] = {
        "available": bool(image_key) and shutil.which("node") is not None,
        "api_key_present": bool(image_key),
        "node_present": shutil.which("node") is not None,
        "degrades_to": "Claude writes the image brief and an alt-text-ready "
        "prompt instead of generating a file. Local MCP servers run in Claude "
        "Desktop and Claude Code only - not in Cowork on web or mobile.",
    }

    # --- /blog audio : Gemini TTS over HTTPS, no MCP.
    checks["audio"] = {
        "available": python_ok and bool(image_key) and _has_module("requests"),
        "api_key_present": bool(image_key),
        "degrades_to": "Claude produces the narration script; generating the "
        "audio file needs a Google AI API key.",
    }

    # --- /blog notebooklm : browser automation, local surfaces only.
    checks["notebooklm"] = {
        "available": python_ok and _has_module("patchright"),
        "deps": {"patchright": _has_module("patchright")},
        "degrades_to": "Browser automation needs a local browser and an "
        "interactive Google sign-in. Unavailable on hosted/sandboxed sessions; "
        "use /blog factcheck with web search instead.",
    }

    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        metavar="CAPABILITY",
        help="Report a single capability (analyze, google, image, audio, notebooklm).",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit JSON (default when piped)."
    )
    args = parser.parse_args()

    report = capabilities()
    if args.check:
        if args.check not in report:
            print(
                json.dumps({"error": f"unknown capability: {args.check}"}, indent=2)
            )
            return 2
        report = {args.check: report[args.check], "surface": report["surface"]}

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
