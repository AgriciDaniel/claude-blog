#!/usr/bin/env python3
"""Run an isolated end-to-end smoke test for the scaffold and CLI scripts."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
PY = sys.executable
sys.path.insert(0, str(REPO / "scripts"))

from package_release import scan_bytes  # noqa: E402


def run(args: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run([PY, *args], cwd=REPO, text=True, capture_output=True, env={**os.environ, **(env or {})}, check=False)
    if proc.returncode:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise AssertionError(f"command failed: {' '.join(args)}")
    return proc


def run_cmd(args: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(args, cwd=REPO, text=True, capture_output=True, env={**os.environ, **(env or {})}, check=False)
    if proc.returncode:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise AssertionError(f"command failed: {' '.join(args)}")
    return proc


def run_audit_report_only_hermetic() -> None:
    # Audit may evolve to write research outputs. It never runs against the
    # original checkout, so immutable sources need no restore or replacement.
    with tempfile.TemporaryDirectory(prefix="claude-blog-brain-audit-export-") as tmp:
        export = Path(tmp) / "brain"
        shutil.copytree(REPO, export, symlinks=True, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "dist", ".git"))
        for path in export.rglob("*"):
            if path.is_symlink() and not path.resolve().is_relative_to(export):
                raise AssertionError("audit export contains a symlink outside its disposable tree")
        proc = subprocess.run(
            [PY, "scripts/audit_brain.py", "--json", "--report-only", "--no-exec"],
            cwd=export, text=True, capture_output=True, check=False,
        )
        if proc.returncode:
            raise AssertionError(proc.stderr or proc.stdout)


def assert_release_local_path_scan() -> None:
    # Build the malicious samples at runtime so this test file does not itself
    # contain a literal home-path pattern that package_release.py would flag.
    user = b"alice"
    samples = (
        b"/home/" + user + b"/project",
        b"/var/home/" + user + b"/project",
        b"/Users/" + user + b"/project",
        b"C:\\Users\\" + user + b"\\project",
    )
    for sample in samples:
        try:
            scan_bytes(sample, "fixture.txt", ".txt")
        except SystemExit as exc:
            assert "local home path" in str(exc)
        else:
            raise AssertionError(f"local path was not rejected: {sample!r}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run isolated Claude Blog Brain pipeline checks.")
    parser.add_argument("--skip-release", action="store_true", help="Skip package_release checks in dirty worktrees.")
    args = parser.parse_args(argv)
    run(["-m", "compileall", "scripts", "claude_blog_brain", "tests"])
    assert_release_local_path_scan()
    run(["scripts/lint_vault.py", "--vault", "assets/template-brain", "--template"])
    with tempfile.TemporaryDirectory(prefix="claude-blog-brain-test-") as tmp:
        out_dir = Path(tmp) / "vaults"
        run(["scripts/scaffold_vault.py", "--client", "acme", "--client-name", "Acme Co", "--owner", "Test Owner", "--out-dir", str(out_dir)])
        vault = out_dir / "acme"
        run(["scripts/ingest_source.py", "--vault", str(vault), "--file", "tests/fixtures/sample-source.md"])
        run(["scripts/synthesize_brain.py", "--vault", str(vault)])
        run(["scripts/generate_vault_visuals.py", "--vault", str(vault)])
        run(["scripts/render_brain_report.py", "--vault", str(vault), "--html-only"])
        run(["scripts/lint_vault.py", "--vault", str(vault)])
        assert (vault / "weekly-report.html").exists()
        demo = Path(tmp) / "demo-vault"
        run(["scripts/build_demo_vault.py", "--out", str(demo), "--json"])
        assert (demo / "CODEX.md").exists()
        blog_pipeline = Path(tmp) / "blog-pipeline"
        run_cmd([PY, "-m", "claude_blog_brain", "blog-pipeline", "--input", "tests/fixtures/sample-blog-post.json", "--out-dir", str(blog_pipeline)])
        blog_report = blog_pipeline / "blog-optimization-report.md"
        assert blog_report.exists()
        report_text = blog_report.read_text(encoding="utf-8")
        assert "## GEO and AI Citation Readiness" in report_text
        assert "## Schema Recommendations" in report_text
        assert "## Source Citations" in report_text
    run_audit_report_only_hermetic()
    if not args.skip_release:
        with tempfile.TemporaryDirectory(prefix="claude-blog-brain-dist-") as tmp:
            run(["scripts/package_release.py", "--version", "0.2.0", "--release-type", "market-ready", "--dist-dir", tmp, "--allow-outside-dist"])
            assert (Path(tmp) / "RELEASE_MANIFEST.json").exists()
    with tempfile.TemporaryDirectory(prefix="claude-blog-brain-install-") as tmp:
        env = {"CLAUDE_BLOG_BRAIN_INSTALL_HOME": tmp}
        run_cmd(["bash", "install.sh", "--target", "all"], env=env)
        assert (Path(tmp) / ".codex" / "skills" / "claude-blog-brain" / "SKILL.md").exists()
        assert (Path(tmp) / ".openclaw" / "skills" / "claude-blog-brain" / "SKILL.md").exists()
        assert (Path(tmp) / ".agent-skills" / "claude-blog-brain" / "SKILL.md").exists()
        assert (Path(tmp) / ".gemini" / "claude-blog-brain" / "GEMINI.md").exists()
        assert "claude-blog-brain-install:start" in (Path(tmp) / ".gemini" / "GEMINI.md").read_text(encoding="utf-8")
        custom_root = Path(tmp) / "custom-skills"
        run_cmd(["bash", "install.sh", "--target", "custom", "--path", str(custom_root)], env=env)
        assert (custom_root / "claude-blog-brain" / "SKILL.md").exists()
        run_cmd(["bash", "uninstall.sh", "--target", "all"], env=env)
        assert not (Path(tmp) / ".codex" / "skills" / "claude-blog-brain").exists()
        assert not (Path(tmp) / ".gemini" / "claude-blog-brain").exists()
        assert not (Path(tmp) / ".gemini" / "GEMINI.md").exists()
        run_cmd(["bash", "uninstall.sh", "--target", "custom", "--path", str(custom_root)], env=env)
        assert not (custom_root / "claude-blog-brain").exists()
    print("Pipeline tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
