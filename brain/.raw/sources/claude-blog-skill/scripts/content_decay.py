#!/usr/bin/env python3
"""Detect content decay from two Google Search Console page exports.

The default path is offline: pass a current-period JSON export and a matching
previous-period JSON export. Each export may be either a JSON list of rows or a
GSC helper result with a top-level ``rows`` list. Rows should include a page or
url field plus clicks and impressions.

Optional live export path:
    python3 skills/blog-google/scripts/run.py gsc_query --property sc-domain:example.com --dimensions page --json

Usage:
    python3 content_decay.py current.json previous.json
    python3 content_decay.py current.json previous.json --threshold 0.20 --metric clicks
"""

from __future__ import annotations

import argparse
import errno
import json
import math
import os
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any

SEVERITY_RANK = {
    "critical": 3,
    "high": 2,
    "warning": 1,
}
MAX_EXPORT_BYTES = 25 * 1024 * 1024
MAX_EXPORT_ROWS = 100_000


class ContentDecayError(ValueError):
    """Raised when an export cannot be used for content decay analysis."""


def _reject_json_constant(value: str) -> None:
    """Reject JSON constants that are not valid finite JSON numbers."""
    raise ValueError(f"non-finite JSON value is not allowed: {value}")


def _as_number(value: Any, *, metric: str, page: str) -> float:
    """Return value as a nonnegative finite float, using 0 for null values."""
    if value is None:
        return 0.0
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(number):
        raise ContentDecayError(
            f"Metric {metric} for page {page} must be a finite number."
        )
    return max(number, 0.0)


def _read_safely(path: Path, max_bytes: int) -> str:
    """Read a regular non-symlink file with pre and post size caps."""
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    elif path.is_symlink():
        raise ContentDecayError(f"Refusing to follow symlink: {path}")
    try:
        fd = os.open(str(path), flags)
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise ContentDecayError(f"Refusing to follow symlink: {path}") from exc
        raise ContentDecayError(f"Could not read {path}: {exc}") from exc
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise ContentDecayError(f"{path} is not a regular file.")
        if st.st_size > max_bytes:
            raise ContentDecayError(f"{path} exceeds size cap ({st.st_size} > {max_bytes}).")
        data = os.read(fd, max_bytes + 1)
    finally:
        os.close(fd)
    if len(data) > max_bytes:
        raise ContentDecayError(f"{path} exceeds size cap after read ({max_bytes}).")
    return data.decode("utf-8")


def _row_page(row: dict[str, Any]) -> str | None:
    """Extract a page URL from common GSC row shapes."""
    for key in ("page", "url", "URL", "landingPage", "landing_page"):
        value = row.get(key)
        if value:
            return str(value)

    keys = row.get("keys")
    if isinstance(keys, list):
        for value in keys:
            if not value:
                continue
            text = str(value)
            if text.startswith(("http://", "https://", "/")):
                return text
    return None


def load_export(path: str | Path) -> list[dict[str, Any]]:
    """Load a GSC export from a JSON file and return its row list."""
    export_path = Path(path)
    raw = _read_safely(export_path, MAX_EXPORT_BYTES)

    if not raw.strip():
        raise ContentDecayError(f"{export_path} is empty.")

    try:
        data = json.loads(raw, parse_constant=_reject_json_constant)
    except json.JSONDecodeError as exc:
        raise ContentDecayError(f"{export_path} is not valid JSON: {exc.msg}") from exc
    except ValueError as exc:
        raise ContentDecayError(
            f"{export_path} contains a non-finite JSON value: {exc}"
        ) from exc

    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict) and isinstance(data.get("rows"), list):
        rows = data["rows"]
    else:
        raise ContentDecayError(
            f"{export_path} must be a JSON list or an object with a rows list."
        )

    if not rows:
        raise ContentDecayError(f"{export_path} contains no rows.")
    if len(rows) > MAX_EXPORT_ROWS:
        raise ContentDecayError(f"{export_path} row count exceeds cap ({len(rows)} > {MAX_EXPORT_ROWS}).")

    if not all(isinstance(row, dict) for row in rows):
        raise ContentDecayError(f"{export_path} rows must be JSON objects.")

    return rows


def aggregate_pages(
    rows: list[dict[str, Any]], *, required_metric: str | None = None
) -> dict[str, dict[str, float]]:
    """Aggregate GSC rows by page and sum clicks and impressions."""
    pages: dict[str, dict[str, float]] = {}
    for row in rows:
        page = _row_page(row)
        if not page:
            continue
        if required_metric is not None and required_metric not in row:
            raise ContentDecayError(
                f"Row for page {page} is missing selected metric column: {required_metric}."
            )
        if page not in pages:
            pages[page] = {"clicks": 0.0, "impressions": 0.0}
        pages[page]["clicks"] += _as_number(
            row.get("clicks"), metric="clicks", page=page
        )
        pages[page]["impressions"] += _as_number(
            row.get("impressions"), metric="impressions", page=page
        )
    return pages


def classify_severity(decline: float) -> str:
    """Classify decline severity using fixed content decay thresholds."""
    if decline >= 0.60:
        return "critical"
    if decline >= 0.40:
        return "high"
    return "warning"


def _decline(previous: float, current: float) -> float:
    if previous <= 0:
        return 0.0
    return max((previous - current) / previous, 0.0)


def recommend_action(
    *,
    metric: str,
    threshold: float,
    severity: str,
    dropped_out: bool,
    current: dict[str, float],
    previous: dict[str, float],
) -> tuple[str, str]:
    """Return a recommended action and a short reason."""
    previous_clicks = previous.get("clicks", 0.0)
    previous_impressions = previous.get("impressions", 0.0)
    current_metric = current.get(metric, 0.0)
    previous_metric = previous.get(metric, 0.0)
    metric_decline = _decline(previous_metric, current_metric)

    if (
        previous_clicks <= 3
        and previous_impressions <= 100
        and metric_decline >= threshold
    ):
        return (
            "prune",
            "The page had low prior demand, so pruning may be better than a rewrite.",
        )

    if dropped_out:
        return (
            "consolidate/redirect",
            "The page disappeared from the current export, so merge or redirect it if a stronger page exists.",
        )

    if metric == "clicks" and previous_impressions > 0:
        impression_decline = _decline(
            previous_impressions, current.get("impressions", 0.0)
        )
        if impression_decline < threshold:
            return (
                "investigate query shift",
                "Clicks fell while impressions held up, which can point to ranking, CTR, or query mix changes.",
            )

    if severity == "critical" and current_metric <= max(1.0, previous_metric * 0.10):
        return (
            "consolidate/redirect",
            "The loss is severe enough that consolidation may recover value faster than a light refresh.",
        )

    return (
        "refresh/update content",
        "The page still has measurable demand, so update the content, title, internal links, and freshness signals.",
    )


def analyze_decay(
    current_rows: list[dict[str, Any]],
    previous_rows: list[dict[str, Any]],
    *,
    threshold: float = 0.20,
    metric: str = "clicks",
) -> dict[str, Any]:
    """Compare two GSC exports and return a structured content decay report."""
    if metric not in {"clicks", "impressions"}:
        raise ContentDecayError("Metric must be clicks or impressions.")
    if not math.isfinite(threshold) or threshold < 0 or threshold > 1:
        raise ContentDecayError("Threshold must be between 0 and 1.")

    current_pages = aggregate_pages(current_rows, required_metric=metric)
    previous_pages = aggregate_pages(previous_rows, required_metric=metric)

    if not current_pages:
        raise ContentDecayError("Current export has no usable page rows.")
    if not previous_pages:
        raise ContentDecayError("Previous export has no usable page rows.")

    decays: list[dict[str, Any]] = []

    for page, previous in previous_pages.items():
        current = current_pages.get(page, {"clicks": 0.0, "impressions": 0.0})
        previous_metric = previous.get(metric, 0.0)
        current_metric = current.get(metric, 0.0)
        dropped_out = page not in current_pages

        if previous_metric <= 0:
            continue

        decline = _decline(previous_metric, current_metric)
        if decline < threshold and not dropped_out:
            continue

        severity = classify_severity(decline)
        action, reason = recommend_action(
            metric=metric,
            threshold=threshold,
            severity=severity,
            dropped_out=dropped_out,
            current=current,
            previous=previous,
        )
        decays.append(
            {
                "page": page,
                "severity": severity,
                "decline": round(decline, 4),
                "decline_percent": round(decline * 100, 1),
                "metric": metric,
                "current_metric": round(current_metric, 2),
                "previous_metric": round(previous_metric, 2),
                "current_clicks": round(current.get("clicks", 0.0), 2),
                "previous_clicks": round(previous.get("clicks", 0.0), 2),
                "current_impressions": round(current.get("impressions", 0.0), 2),
                "previous_impressions": round(previous.get("impressions", 0.0), 2),
                "dropped_out": dropped_out,
                "recommended_action": action,
                "action_reason": reason,
            }
        )

    decays.sort(
        key=lambda row: (
            SEVERITY_RANK[row["severity"]],
            row["decline"],
            row["previous_metric"],
        ),
        reverse=True,
    )

    return {
        "metric": metric,
        "threshold": threshold,
        "summary": {
            "current_pages": len(current_pages),
            "previous_pages": len(previous_pages),
            "flagged_pages": len(decays),
            "dropped_out_pages": sum(1 for row in decays if row["dropped_out"]),
            "total_current_metric": round(
                sum(page.get(metric, 0.0) for page in current_pages.values()), 2
            ),
            "total_previous_metric": round(
                sum(page.get(metric, 0.0) for page in previous_pages.values()), 2
            ),
        },
        "decays": decays,
    }


def _escape_markdown_cell(value: Any) -> str:
    """Escape table cell characters that can break markdown table structure."""
    text = str(value)
    text = text.replace("\\", "\\\\")
    text = text.replace("|", "\\|")
    text = text.replace("\r\n", "\\n")
    text = text.replace("\n", "\\n")
    text = text.replace("\r", "\\n")
    return text


def format_markdown(report: dict[str, Any]) -> str:
    """Render a content decay report as markdown."""
    summary = report["summary"]
    metric = report["metric"]
    threshold = report["threshold"] * 100
    lines = [
        "# Content Decay Report",
        "",
        f"Metric: `{metric}`",
        f"Threshold: {threshold:.0f}%",
        f"Flagged pages: {summary['flagged_pages']}",
        f"Dropped out pages: {summary['dropped_out_pages']}",
        "",
    ]

    if not report["decays"]:
        lines.append("No pages met the decay threshold.")
        return "\n".join(lines) + "\n"

    lines.extend(
        [
            "| Severity | Page | Previous | Current | Decline | Dropped out | Recommendation |",
            "| --- | --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for row in report["decays"]:
        dropped = "yes" if row["dropped_out"] else "no"
        lines.append(
            "| {severity} | {page} | {previous:g} | {current:g} | {decline:.1f}% | {dropped} | {action} |".format(
                severity=_escape_markdown_cell(row["severity"]),
                page=_escape_markdown_cell(row["page"]),
                previous=row["previous_metric"],
                current=row["current_metric"],
                decline=row["decline_percent"],
                dropped=_escape_markdown_cell(dropped),
                action=_escape_markdown_cell(row["recommended_action"]),
            )
        )

    return "\n".join(lines) + "\n"


def write_output(text: str, output_path: str | None) -> None:
    """Write text to a path or stdout."""
    if output_path:
        out = Path(output_path)
        if out.exists() and out.is_symlink():
            raise ContentDecayError(f"Output path is a symlink: {out}")
        if not out.parent.exists():
            raise ContentDecayError(f"Output directory does not exist: {out.parent}")
        fd, tmp = tempfile.mkstemp(dir=str(out.parent), prefix=f".{out.name}.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(text)
            os.replace(tmp, out)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
    else:
        print(text, end="")


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""
    parser = argparse.ArgumentParser(
        description="Detect quarter-over-quarter content decay from GSC exports."
    )
    parser.add_argument("current", help="Current-period GSC performance export")
    parser.add_argument("previous", help="Previous-period GSC performance export")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.20,
        help="Minimum decline ratio to flag, default 0.20",
    )
    parser.add_argument(
        "--metric",
        choices=["clicks", "impressions"],
        default="clicks",
        help="Metric to compare, default clicks",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format, default json",
    )
    parser.add_argument("--output", help="Write report to this path")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the content decay CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        current_rows = load_export(args.current)
        previous_rows = load_export(args.previous)
        report = analyze_decay(
            current_rows,
            previous_rows,
            threshold=args.threshold,
            metric=args.metric,
        )
    except ContentDecayError as exc:
        print(json.dumps({"error": str(exc)}, indent=2, allow_nan=False))
        return 1

    if args.format == "markdown":
        output = format_markdown(report)
    else:
        output = json.dumps(report, indent=2, allow_nan=False) + "\n"
    try:
        write_output(output, args.output)
    except ContentDecayError as exc:
        print(json.dumps({"error": str(exc)}, indent=2, allow_nan=False))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
