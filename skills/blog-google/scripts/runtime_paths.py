"""Read-only runtime path policy, shipped identically with each integration.

CLAUDE_BLOG_RUNTIME_DIR is an explicit trusted absolute operator/host path.
No override means the original skill-local .venv/data layout. Resolution never
creates directories, expands shell expressions or migrates existing state.
"""

import os
from pathlib import Path
import re
from typing import NamedTuple


class RuntimePaths(NamedTuple):
    root: Path
    venv: Path
    data: Path


def validate_absolute_override(raw: str, path_type=Path):
    """Validate native Path semantics, including Windows drive/UNC anchors."""
    if not raw or raw != raw.strip() or "\x00" in raw:
        raise ValueError("CLAUDE_BLOG_RUNTIME_DIR must be a nonempty absolute path")
    if "$" in raw or re.search(r"%[^%]+%", raw) or raw.startswith("~"):
        raise ValueError("CLAUDE_BLOG_RUNTIME_DIR must be resolved, without shell or host placeholders")
    path = path_type(raw)
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("CLAUDE_BLOG_RUNTIME_DIR must be absolute, without parent traversal")
    return path


def confined_directory(root: Path, *parts: str) -> Path:
    """Refuse linked managed directories and paths outside the selected root."""
    root = root.resolve()
    path = root
    for part in parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("runtime directory must not be a symlink")
        try:
            path.resolve().relative_to(root)
        except ValueError as exc:
            raise ValueError("runtime directory escapes its selected root") from exc
        if path.exists() and not path.is_dir():
            raise ValueError("runtime directory must be a directory")
    return path


def resolve_runtime_paths(skill_dir: Path, integration: str) -> RuntimePaths:
    """Return consistent venv/data roots without any filesystem mutation."""
    if integration not in ("blog-audio", "blog-google", "blog-notebooklm"):
        raise ValueError("unknown runtime integration")
    skill_dir = Path(skill_dir)
    if not skill_dir.is_absolute():
        raise ValueError("trusted installed skill path must be absolute")
    raw = os.environ.get("CLAUDE_BLOG_RUNTIME_DIR")
    if raw is None:
        root = skill_dir.resolve()
    else:
        selected = validate_absolute_override(raw).resolve()
        if selected.exists() and not selected.is_dir():
            raise ValueError("CLAUDE_BLOG_RUNTIME_DIR must be a directory")
        root = confined_directory(selected, integration)
    return RuntimePaths(root, confined_directory(root, ".venv"), confined_directory(root, "data"))
