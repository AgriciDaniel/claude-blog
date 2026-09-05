#!/usr/bin/env python3
"""Pre-commit quality gate for blog posts.

The gate filters incoming Markdown and MDX paths to likely blog posts, analyzes
those posts with the existing analyzer, and fails when a score is below the
configured threshold.
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
    """Read staged file names from Git."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or "Unable to read staged files"
        raise RuntimeError(message)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


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


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""
    parser = argparse.ArgumentParser(
        description="Block commits when selected blog posts score below threshold."
    )
    parser.add_argument("files", nargs="*", help="Markdown or MDX files to check")
    parser.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_THRESHOLD,
        help="Minimum accepted analyzer score",
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

    paths = list(args.files)
    if args.staged:
        try:
            paths.extend(_staged_files())
        except RuntimeError as exc:
            print(f"Blog quality gate error: {exc}", file=sys.stderr)
            return 2

    selected = [
        path
        for path in _dedupe(paths)
        if is_blog_post(path, root=Path.cwd())
    ]
    results = [analyze_post(path, args.threshold) for path in selected]
    failures = [result for result in results if not result["passed"]]

    if args.format == "json":
        print(_format_json(results, failures, args.threshold))
    else:
        print(_format_text(results, failures, args.threshold))

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
