#!/usr/bin/env python3
"""Pre-commit quality gate for blog posts.

The gate analyzes blog posts with the existing analyzer and fails when a score
is below the configured threshold.

The default threshold of 70 is the analyze_blog.py quality threshold. It is not
the 90-point delivery gate: the independent review in blog_preflight.py
(gate 4) requires an overall score of at least 90 before an article ships.

Path handling is deliberately strict:

- A file named on the command line is never silently skipped. A missing or
  unreadable path is an error, a file without blog frontmatter (a title plus a
  description or date) fails, and a file inside docs/, skills/, tests/,
  templates/ or references/ is still analyzed.
- A directory named on the command line is scanned recursively. The scan skips
  those non-post directories and files without blog frontmatter.
- Hook mode (``--select``) and ``--staged`` receive every changed Markdown file
  from Git or pre-commit, so they apply the filter and skip non-posts.

Exit codes: 0 pass, 1 a post failed the gate, 2 usage error or a path that is
missing or not a file.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

import analyze_blog  # noqa: E402

DEFAULT_THRESHOLD = 70
EXCLUDED_DIRS = {"skills", "docs", "references", "templates", "tests"}
BLOG_SUFFIXES = {".md", ".mdx"}
MIN_THRESHOLD = 1
MAX_THRESHOLD = 100
MISSING_FRONTMATTER = (
    "missing blog frontmatter: a post needs a title plus a description or date"
)


def _path_for_policy(path: Path, root: Path | None = None) -> Path:
    """Return a lexical path relative to root when possible for directory checks."""
    root = Path(os.path.abspath(os.fspath(root or Path.cwd())))
    absolute_path = Path(os.path.abspath(os.fspath(path)))
    try:
        return absolute_path.relative_to(root)
    except ValueError:
        return absolute_path


def is_excluded_path(file_path: str | Path, root: Path | None = None) -> bool:
    """Return True when the path is inside a non-post content tree."""
    policy_path = _path_for_policy(Path(file_path), root)
    parent_parts = {part.lower() for part in policy_path.parts[:-1]}
    return bool(parent_parts & EXCLUDED_DIRS)


def has_blog_frontmatter(file_path: str | Path) -> bool:
    """Return True when a Markdown file has blog post frontmatter keys."""
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")

    frontmatter = analyze_blog.extract_frontmatter(content)
    normalized = {key.lower(): value for key, value in frontmatter.items()}
    return bool(
        normalized.get("title")
        and (normalized.get("description") or normalized.get("date"))
    )


def is_blog_post(file_path: str | Path, root: Path | None = None) -> bool:
    """Return True when a path should be gated as a blog post."""
    path = Path(file_path)
    if path.suffix.lower() not in BLOG_SUFFIXES:
        return False
    if is_excluded_path(path, root):
        return False
    if not path.is_file():
        return False
    try:
        return has_blog_frontmatter(path)
    except (OSError, UnicodeDecodeError):
        return True


def _staged_files() -> list[str]:
    """Read staged file names from Git (deleted files are not gate inputs)."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or "Unable to read staged files"
        raise RuntimeError(message)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _input_error(path: str, reason: str) -> dict[str, Any]:
    """Build a failing result for an explicit path that cannot be checked."""
    message = f"Could not check {path}: {reason}"
    return {
        "file": path,
        "score": 0,
        "passed": False,
        "issues": [{"category": "input", "severity": "high", "issue": message}],
        "error": message,
    }


def _dedupe(paths: list[str]) -> list[str]:
    """Preserve the first occurrence of each path."""
    seen: set[str] = set()
    deduped: list[str] = []
    for path in paths:
        key = str(Path(path).resolve(strict=False))
        if key not in seen:
            seen.add(key)
            deduped.append(path)
    return deduped


def _frontmatter_ok(path: Path) -> bool:
    """Return False only when the file is readable and lacks blog frontmatter."""
    try:
        return has_blog_frontmatter(path)
    except (OSError, UnicodeDecodeError):
        return True


def _top_high_severity_issues(
    issues: list[dict[str, Any]], limit: int = 3
) -> list[dict[str, Any]]:
    return [issue for issue in issues if issue.get("severity") == "high"][:limit]


def _safe_analyze_file(path: Path) -> dict[str, Any]:
    """Run the shared analyzer and convert file read failures into JSON errors."""
    try:
        return analyze_blog.analyze_file(str(path))
    except (OSError, UnicodeDecodeError) as exc:
        return {"error": f"Could not analyze {path}: {exc}"}


def analyze_post(file_path: str | Path, threshold: int) -> dict[str, Any]:
    """Analyze a selected post and return gate-oriented result data."""
    path = Path(file_path)
    result = _safe_analyze_file(path)
    error_message = result.get("error")
    if "error" not in result and not _frontmatter_ok(path):
        error_message = MISSING_FRONTMATTER
        result = {"error": error_message}
    if "error" in result:
        score = 0
        issues = [
            {
                "category": "analyzer",
                "severity": "high",
                "issue": error_message,
            }
        ]
    else:
        score = result["score"]["total"]
        issues = result["score"].get("issues", [])

    output = {
        "file": str(path),
        "score": score,
        "passed": score >= threshold,
        "issues": _top_high_severity_issues(issues),
    }
    if error_message:
        output["error"] = error_message
    return output


def _format_text(results: list[dict[str, Any]], failures: list[dict[str, Any]], threshold: int) -> str:
    if not failures:
        if results:
            return f"Blog quality gate passed: {len(results)} post(s) checked."
        return "Blog quality gate passed: no blog posts to check."

    lines = [
        f"Blog quality gate failed: {len(failures)} post(s) below score {threshold}.",
    ]
    for failure in failures:
        lines.append(f"{failure['file']}: score {failure['score']}/100")
        if failure.get("error"):
            lines.append(f"  {failure['error']}")
        if failure["issues"]:
            for issue in failure["issues"]:
                lines.append(
                    f"  [{issue.get('severity', 'high')}] "
                    f"{issue.get('category', 'general')}: {issue.get('issue', '')}"
                )
        else:
            lines.append("  No high severity issues reported.")
    return "\n".join(lines)


def _format_json(
    results: list[dict[str, Any]], failures: list[dict[str, Any]], threshold: int
) -> str:
    errors = [result["error"] for result in results if result.get("error")]
    payload = {
        "threshold": threshold,
        "checked": results,
        "failures": failures,
    }
    if errors:
        payload["error"] = "; ".join(errors)
    return json.dumps(payload, indent=2, sort_keys=True)


def _threshold_arg(value: str) -> int:
    """Parse --threshold and reject values that would make the gate meaningless."""
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"threshold must be an integer, got {value!r}")
    if not MIN_THRESHOLD <= number <= MAX_THRESHOLD:
        raise argparse.ArgumentTypeError(
            f"threshold must be between {MIN_THRESHOLD} and {MAX_THRESHOLD}, got {number}"
        )
    return number


def expand_directory(directory: Path) -> list[str]:
    """Scan a directory for posts, skipping non-post trees and non-post files."""
    found: list[str] = []
    for candidate in sorted(directory.rglob("*")):
        if candidate.suffix.lower() in BLOG_SUFFIXES and is_blog_post(
            candidate, root=directory
        ):
            found.append(str(candidate))
    return found


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Block commits when blog posts score below the analyzer quality "
            f"threshold (default {DEFAULT_THRESHOLD}, the analyze_blog.py quality "
            "threshold, not the 90-point delivery gate in blog_preflight.py). "
            "Files named on the command line are always checked; directories "
            "are scanned."
        )
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Markdown or MDX files (always checked) or directories (scanned)",
    )
    parser.add_argument(
        "--threshold",
        type=_threshold_arg,
        default=DEFAULT_THRESHOLD,
        help=(
            f"Minimum accepted analyzer score, {MIN_THRESHOLD} to {MAX_THRESHOLD} "
            f"(default {DEFAULT_THRESHOLD}, the analyzer quality threshold)"
        ),
    )
    parser.add_argument(
        "--select",
        action="store_true",
        help=(
            "Hook mode: treat the listed files as candidates and skip those that "
            "are not blog posts (for pre-commit, which passes every Markdown file)"
        ),
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Also check Markdown and MDX files staged in Git",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the quality gate and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    explicit: list[str] = []
    candidates: list[str] = []
    problems: list[dict[str, Any]] = []
    for raw in args.files:
        path = Path(raw)
        if path.is_dir():
            candidates.extend(expand_directory(path))
        elif args.select:
            if not path.exists():
                problems.append(_input_error(raw, "path does not exist"))
            else:
                candidates.append(raw)
        elif not path.exists():
            problems.append(_input_error(raw, "path does not exist"))
        elif not path.is_file():
            problems.append(_input_error(raw, "path is not a file or directory"))
        else:
            explicit.append(raw)

    if args.staged:
        try:
            candidates.extend(_staged_files())
        except RuntimeError as exc:
            print(f"Blog quality gate error: {exc}", file=sys.stderr)
            return 2

    if not args.files and not args.staged:
        parser.error("no files given: name Markdown files or directories, or pass --staged")

    selected = list(explicit)
    selected.extend(
        path for path in candidates if is_blog_post(path, root=Path.cwd())
    )
    selected = _dedupe(selected)
    results = [analyze_post(path, args.threshold) for path in selected]
    results.extend(problems)
    failures = [result for result in results if not result["passed"]]

    if args.format == "json":
        print(_format_json(results, failures, args.threshold))
    else:
        print(_format_text(results, failures, args.threshold))

    if problems:
        return 2
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
