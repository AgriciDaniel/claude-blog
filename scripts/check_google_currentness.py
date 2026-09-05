#!/usr/bin/env python3
"""Check the reviewed Google ledger against official machine-readable feeds."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any


LEDGER_PATH = Path("data/google-updates.json")
AUTOMATED_SOURCES = {
    "search-status": "https://status.search.google.com/incidents.json",
    "search-docs-updates": (
        "https://developers.google.com/search/updates/search_docs_updates.rss"
    ),
}


def _fetch(url: str, timeout: float) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "claude-blog-currentness-check/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def latest_ranking_incident(payload: bytes) -> date:
    incidents = json.loads(payload)
    dates = [
        datetime.fromisoformat(item["begin"]).date()
        for item in incidents
        if item.get("service_name") == "Ranking" and item.get("begin")
    ]
    if not dates:
        raise ValueError("official status feed has no Ranking incidents")
    return max(dates)


def latest_documentation_update(payload: bytes) -> date:
    root = ET.fromstring(payload)
    dates = [
        parsedate_to_datetime(item.text).date()
        for item in root.findall("./channel/item/pubDate")
        if item.text
    ]
    if not dates:
        raise ValueError("official documentation feed has no dated items")
    return max(dates)


def evaluate(
    ledger: dict[str, Any],
    *,
    as_of: date,
    max_age_days: int,
    source_dates: dict[str, date],
) -> dict[str, Any]:
    verified_on = date.fromisoformat(ledger["last_verified"])
    age_days = (as_of - verified_on).days
    reasons: list[str] = []
    if age_days < 0:
        reasons.append("ledger last_verified is in the future")
    if age_days > max_age_days:
        reasons.append(
            f"ledger review is {age_days} days old, limit is {max_age_days}"
        )
    for source_id, source_date in sorted(source_dates.items()):
        if source_date > verified_on:
            reasons.append(
                f"{source_id} has a {source_date.isoformat()} event newer than "
                f"the {verified_on.isoformat()} ledger review"
            )

    return {
        "status": "refresh_required" if reasons else "current",
        "as_of": as_of.isoformat(),
        "last_verified": verified_on.isoformat(),
        "age_days": age_days,
        "max_age_days": max_age_days,
        "official_source_dates": {
            key: value.isoformat() for key, value in sorted(source_dates.items())
        },
        "reasons": reasons,
    }


def _automated_sources(ledger: dict[str, Any]) -> dict[str, str]:
    sources = {
        item["id"]: item["url"]
        for item in ledger.get("source_watch", [])
        if item.get("review_mode") == "automated"
    }
    missing = AUTOMATED_SOURCES.keys() - sources.keys()
    if missing:
        raise ValueError(
            "ledger is missing automated source watches: " + ", ".join(sorted(missing))
        )
    changed = [
        source_id
        for source_id, expected_url in AUTOMATED_SOURCES.items()
        if sources[source_id] != expected_url
    ]
    if changed:
        raise ValueError(
            "ledger automated source URL is not allowlisted: "
            + ", ".join(sorted(changed))
        )
    return sources


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare Google ledger review dates with official feeds."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--max-age-days", type=int, default=31)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Check review age without accessing official feeds.",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.max_age_days < 1:
        parser.error("--max-age-days must be positive")

    try:
        ledger = json.loads(
            (args.root.resolve() / LEDGER_PATH).read_text(encoding="utf-8")
        )
        source_dates: dict[str, date] = {}
        if not args.offline:
            sources = _automated_sources(ledger)
            source_dates = {
                "search-status": latest_ranking_incident(
                    _fetch(sources["search-status"], args.timeout)
                ),
                "search-docs-updates": latest_documentation_update(
                    _fetch(sources["search-docs-updates"], args.timeout)
                ),
            }
        report = evaluate(
            ledger,
            as_of=args.as_of,
            max_age_days=args.max_age_days,
            source_dates=source_dates,
        )
    except (
        FileNotFoundError,
        json.JSONDecodeError,
        KeyError,
        OSError,
        TypeError,
        ValueError,
        ET.ParseError,
        urllib.error.URLError,
    ) as exc:
        report = {"status": "unavailable", "error": str(exc)}
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(f"Google currentness check unavailable: {exc}", file=sys.stderr)
        return 3

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Google currentness: {report['status']}")
        for reason in report["reasons"]:
            print(f"- {reason}")
    return 2 if report["status"] == "refresh_required" else 0


if __name__ == "__main__":
    raise SystemExit(main())
