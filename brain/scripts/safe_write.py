"""Symlink-safe atomic text writes for the brain scripts.

A default output path such as ``<vault>/weekly-report.html`` can be replaced by
a symlink to any file the user owns. Writing through it would overwrite that
file. ``write_text_safely`` refuses a symlinked destination, refuses symlinked
directories between a confining root and the destination, and writes through a
same-directory temporary file (created exclusively, never following links)
that is renamed into place, so a reader never sees a partial file.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path


class UnsafeWriteError(ValueError):
    """Raised when a destination would be written through a symlink."""


def _reject_linked_components(root: Path, parent: Path) -> None:
    """Refuse any symlink between root (inclusive) and parent (inclusive)."""
    root_abs = Path(os.path.abspath(root))
    parent_abs = Path(os.path.abspath(parent))
    try:
        relative = parent_abs.relative_to(root_abs)
    except ValueError:
        return
    current = root_abs
    for part in ("",) + relative.parts:
        if part:
            current = current / part
        if current.is_symlink():
            raise UnsafeWriteError(f"refusing symlinked path component: {current}")


def write_text_safely(path: Path, text: str, *, root: Path | None = None, mkdir: bool = True) -> None:
    """Atomically write text to path without following symlinks."""
    path = Path(os.path.abspath(path))
    if root is not None:
        _reject_linked_components(Path(root), path.parent)
    if path.is_symlink():
        raise UnsafeWriteError(f"refusing to write through symlink: {path}")
    if path.is_dir():
        raise UnsafeWriteError(f"destination is a directory: {path}")
    if mkdir:
        path.parent.mkdir(parents=True, exist_ok=True)
    if root is not None:
        _reject_linked_components(Path(root), path.parent)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except BaseException:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        raise
