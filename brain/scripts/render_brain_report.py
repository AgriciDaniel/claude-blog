#!/usr/bin/env python3
"""Render the vault weekly report to HTML with safe output path handling."""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
LOCAL_PATH = re.compile(r"(?:/home|/var/home|/Users)/[A-Za-z0-9_.-]+|[A-Za-z]:\\Users\\[A-Za-z0-9_.-]+", re.I)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render the weekly report as HTML.")
    parser.add_argument("--vault", required=True)
    parser.add_argument("--out", default="")
    parser.add_argument("--html-only", action="store_true")
    parser.add_argument("--unsafe-write", action="store_true", help="Allow --out outside the vault or repo.")
    parser.add_argument("--json", action="store_true", help="Print a JSON result envelope.")
    args = parser.parse_args(argv)
    vault = Path(args.vault).expanduser().resolve()
    report = vault / "wiki" / "reports" / "Weekly Report.md"
    if not report.exists():
        return error("report not found; run synthesize first", args.json)
    out = Path(args.out).expanduser().resolve() if args.out else vault / "weekly-report.html"
    if not args.unsafe_write and not is_safe_output(out, vault):
        return error(f"--out must stay inside the vault or repo: {out}", args.json)
    html_text = markdown_to_html(report.read_text(encoding="utf-8"))
    html_text = LOCAL_PATH.sub("[local-path-redacted]", html_text)
    out.write_text(html_text, encoding="utf-8")
    if args.json:
        print(json.dumps({"ok": True, "out": str(out)}, indent=2, sort_keys=True))
    else:
        print(out)
    return 0


def error(message: str, as_json: bool) -> int:
    if as_json:
        print(json.dumps({"ok": False, "errors": [message]}, indent=2, sort_keys=True))
    else:
        print("ERROR: " + message, file=sys.stderr)
    return 2


def is_safe_output(out: Path, vault: Path) -> bool:
    return out == vault or out.is_relative_to(vault) or out == REPO or out.is_relative_to(REPO)


def markdown_to_html(text: str) -> str:
    body = []
    for line in text.splitlines():
        if line.startswith("---"):
            continue
        if line.startswith("# "):
            body.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            body.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("- "):
            body.append(f"<li>{html.escape(line[2:])}</li>")
        elif line.strip():
            body.append(f"<p>{html.escape(line)}</p>")
    return "<!doctype html><meta charset='utf-8'><title>Weekly Report</title><body>" + "\n".join(body) + "</body>\n"


if __name__ == "__main__":
    raise SystemExit(main())
