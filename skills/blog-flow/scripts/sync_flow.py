#!/usr/bin/env python3
"""Thin wrapper that runs the core FLOW sync (scripts/sync_flow.py).

There is one sync implementation. This file only locates the core script and
forwards the command line, so the flags, the fetch paths (docs/...), the CC BY
4.0 header, the drift gate and the exit codes are identical to the core:

  python3 sync_flow.py --references-dir /abs/persistent/root [--dry-run]
          [--ref <commit-sha>] [--allow-drift] [--resolve-references]

The core script is found at ``CLAUDE_BLOG_SCRIPTS_DIR`` when that variable
names an absolute directory, otherwise at ``<skills dir>/../scripts`` relative
to this file (the plugin layout and the standalone ``~/.claude`` layout both
satisfy this). If it cannot be found the wrapper exits 2 with a pointer.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

_CORE = None


def core_path() -> Path:
    """Return the core sync script path (not yet verified to exist)."""
    override = os.environ.get("CLAUDE_BLOG_SCRIPTS_DIR")
    if override:
        base = Path(override)
        if not base.is_absolute() or ".." in base.parts:
            raise ValueError("CLAUDE_BLOG_SCRIPTS_DIR must be a resolved absolute path")
    else:
        base = Path(__file__).resolve().parents[3] / "scripts"
    return base / "sync_flow.py"


def load_core():
    """Import the core implementation once and return the module."""
    global _CORE
    if _CORE is not None:
        return _CORE
    path = core_path()
    if not path.is_file() or path.resolve() == Path(__file__).resolve():
        raise FileNotFoundError(path)
    spec = importlib.util.spec_from_file_location("claude_blog_sync_flow_core", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _CORE = module
    return module


def main(argv: list[str] | None = None) -> int:
    try:
        core = load_core()
    except (FileNotFoundError, ValueError) as exc:
        print(
            "ERROR: this is a thin wrapper and the core scripts/sync_flow.py was "
            f"not found ({exc}). Run the core script from the claude-blog "
            "install directly, or set CLAUDE_BLOG_SCRIPTS_DIR to its absolute "
            "scripts directory.",
            file=sys.stderr,
        )
        return 2
    return core.main(argv)


if __name__ == "__main__":
    sys.exit(main())
