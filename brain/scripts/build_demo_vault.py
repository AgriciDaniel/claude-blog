#!/usr/bin/env python3
"""Build a deterministic sample vault without deleting existing output by default."""
from __future__ import annotations

import argparse
import filecmp
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
PY = sys.executable


def run(args: list[str]) -> None:
    subprocess.run([PY, *args], cwd=REPO, check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Claude Blog Brain sample vault.")
    parser.add_argument("--out", default=str(REPO / "examples" / "sample-vault"))
    parser.add_argument("--force", action="store_true", help="Replace an existing generated demo vault.")
    parser.add_argument("--json", action="store_true", help="Print a JSON result envelope.")
    args = parser.parse_args(argv)
    demo_parent = REPO / "examples"
    demo = Path(args.out).expanduser().resolve()
    default_demo = (demo_parent / "sample-vault").resolve()
    if demo.exists() and not args.force:
        if demo == default_demo:
            raise SystemExit("ERROR: sample vault exists; rerun with --force to replace it")
        raise SystemExit(f"ERROR: output exists; rerun with --force to replace it: {demo}")
    if demo.exists():
        ensure_generated_demo(demo)
        ensure_clean_target(demo)
    with tempfile.TemporaryDirectory(prefix="claude-blog-demo-") as tmp:
        temp_parent = Path(tmp)
        temp_demo = temp_parent / "sample-vault"
        run(["scripts/scaffold_vault.py", "--client", "sample-vault", "--client-name", "Sample Client", "--owner", "Daniel Agrici", "--out-dir", str(temp_parent)])
        run(["scripts/ingest_source.py", "--vault", str(temp_demo), "--file", "tests/fixtures/sample-source.md", "--source-type", "fixture"])
        run(["scripts/synthesize_brain.py", "--vault", str(temp_demo)])
        run(["scripts/generate_vault_visuals.py", "--vault", str(temp_demo)])
        run(["scripts/render_brain_report.py", "--vault", str(temp_demo), "--html-only"])
        run(["scripts/lint_vault.py", "--vault", str(temp_demo)])
        changed = not demo.exists() or not dirs_equal(temp_demo, demo)
        if changed:
            demo.parent.mkdir(parents=True, exist_ok=True)
            if demo.exists():
                shutil.rmtree(demo)
            shutil.copytree(temp_demo, demo)
    payload = {"ok": True, "vault": str(demo), "changed": changed}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(demo)
    return 0


def ensure_generated_demo(path: Path) -> None:
    marker = path / ".raw" / ".manifest.json"
    if not marker.exists() or not (path / "CODEX.md").exists():
        raise SystemExit(f"ERROR: refusing to replace unmarked vault: {path}")
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise SystemExit(f"ERROR: invalid demo marker: {exc}") from exc
    if "scaffold_history" not in data:
        raise SystemExit(f"ERROR: refusing to replace vault without scaffold_history marker: {path}")


def ensure_clean_target(path: Path) -> None:
    if not (REPO / ".git").exists() or not path.is_relative_to(REPO):
        return
    rel = path.relative_to(REPO).as_posix()
    proc = subprocess.run(["git", "diff", "--quiet", "--", rel], cwd=REPO, check=False)
    if proc.returncode:
        raise SystemExit(f"ERROR: clean target required before replacement: {rel}")


def dirs_equal(left: Path, right: Path) -> bool:
    if not right.exists():
        return False
    comparison = filecmp.dircmp(left, right)
    if comparison.left_only or comparison.right_only or comparison.diff_files or comparison.funny_files:
        return False
    return all(dirs_equal(left / child, right / child) for child in comparison.common_dirs)


if __name__ == "__main__":
    raise SystemExit(main())
