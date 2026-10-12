#!/usr/bin/env python3
"""Build a deterministic sample vault without deleting existing output by default.

``--force`` only replaces a vault that this script generated: it must carry the
``.demo-vault`` marker file, and it must hold no file the generator would not
produce (a note a user added makes the run refuse). Any other scaffolded vault
is refused, so ``--out <real vault> --force`` can never delete user content.
"""
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
DEMO_MARKER = ".demo-vault"
DEMO_MARKER_TEXT = json.dumps({"demo_only": True, "generator": "scripts/build_demo_vault.py"}, sort_keys=True) + "\n"


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
        (temp_demo / DEMO_MARKER).write_text(DEMO_MARKER_TEXT, encoding="utf-8")
        if demo.exists():
            ensure_no_user_files(temp_demo, demo)
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
    demo_marker = path / DEMO_MARKER
    if demo_marker.is_symlink() or not demo_marker.is_file():
        raise SystemExit(
            f"ERROR: refusing to replace {path}: it has no {DEMO_MARKER} marker, so it is "
            "not a generated demo vault. Pick an empty --out or remove it yourself."
        )
    try:
        marked = json.loads(demo_marker.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise SystemExit(f"ERROR: invalid {DEMO_MARKER} marker: {exc}") from exc
    if not isinstance(marked, dict) or marked.get("demo_only") is not True:
        raise SystemExit(f"ERROR: refusing to replace {path}: {DEMO_MARKER} is not a demo-only marker")
    marker = path / ".raw" / ".manifest.json"
    if not marker.exists() or not (path / "CODEX.md").exists():
        raise SystemExit(f"ERROR: refusing to replace unmarked vault: {path}")
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise SystemExit(f"ERROR: invalid demo marker: {exc}") from exc
    if "scaffold_history" not in data:
        raise SystemExit(f"ERROR: refusing to replace vault without scaffold_history marker: {path}")


def ensure_no_user_files(fresh: Path, existing: Path) -> None:
    """Refuse when the existing demo holds files the generator never writes."""
    fresh_files = {p.relative_to(fresh).as_posix() for p in fresh.rglob("*") if not p.is_dir()}
    extra = sorted(
        p.relative_to(existing).as_posix()
        for p in existing.rglob("*")
        if not p.is_dir() and p.relative_to(existing).as_posix() not in fresh_files
    )
    if extra:
        shown = ", ".join(extra[:5]) + (" ..." if len(extra) > 5 else "")
        raise SystemExit(
            f"ERROR: refusing to replace {existing}: it holds {len(extra)} file(s) the demo "
            f"generator did not create ({shown}). Move them out first."
        )


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
