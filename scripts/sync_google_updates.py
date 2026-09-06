#!/usr/bin/env python3
"""Synchronize the canonical Google update ledger into the Blog Brain."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


CANONICAL_PATH = Path("data/google-updates.json")
PROJECTION_PATHS = (Path("brain/data/google-updates.json"),)


def sync(root: Path, *, check: bool) -> list[str]:
    canonical = root / CANONICAL_PATH
    if not canonical.is_file():
        raise FileNotFoundError(f"canonical ledger not found: {canonical}")
    if canonical.is_symlink():
        raise OSError(f"canonical ledger must not be a symlink: {canonical}")

    expected = canonical.read_bytes()
    drifted: list[str] = []
    for relative in PROJECTION_PATHS:
        target = root / relative
        if target.is_symlink():
            raise OSError(f"projection target must not be a symlink: {target}")
        if not target.is_file() or target.read_bytes() != expected:
            drifted.append(relative.as_posix())
            if not check:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(expected)
    return drifted


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize generated Google ledger projections."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report projection drift without writing files.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    try:
        drifted = sync(root, check=args.check)
    except (FileNotFoundError, OSError) as exc:
        print(f"google ledger sync unavailable: {exc}", file=sys.stderr)
        return 3

    if args.check and drifted:
        print("google ledger projection drift: " + ", ".join(drifted))
        return 2
    if drifted:
        print("updated Google ledger projections: " + ", ".join(drifted))
    else:
        print("Google ledger projections are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
