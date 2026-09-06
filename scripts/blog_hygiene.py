#!/usr/bin/env python3
"""blog_hygiene.py: deterministic, judgment-free structural hygiene for blog drafts.

Applies only fixes that never need editorial judgment, so it is safe to run
automatically. It is an OPTIONAL helper, not a delivery-contract gate: it never
blocks delivery and always exits 0 on a successful run.

Fixes:
  1. HTML: add loading="lazy" to <img> tags that lack a loading attribute.
  2. HTML: report (never invent) <img> tags missing alt text.
  3. Markdown: insert an idempotent Table of Contents before the first body H2
     on posts over the word threshold (default 2000) when none is present.

Safety:
  - Refuses symlinked inputs and non-regular files; only rewrites the file passed.
  - Default is dry-run (report only). Pass --apply to write changes back.

Output: a JSON object on stdout. Exit code 0 on success, 2 on usage/IO error.

Usage:
    python3 scripts/blog_hygiene.py --md post.md [--html post.html] [--apply]
    python3 scripts/blog_hygiene.py --html post.html --apply
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

TOC_BEGIN = "<!-- blog-hygiene:toc:begin -->"
TOC_END = "<!-- blog-hygiene:toc:end -->"
DEFAULT_TOC_HEADING = "In this article"


def slugify(text: str) -> str:
    """Convert heading text to a GitHub-style anchor slug (ASCII, lowercase)."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text


def fix_html_lazy_loading(html: str) -> tuple[str, int]:
    """Add loading="lazy" to <img> tags missing a loading attribute. Pure."""
    count = 0

    def _add_lazy(m: "re.Match[str]") -> str:
        nonlocal count
        tag = m.group(0)
        if re.search(r"\bloading\s*=", tag, re.IGNORECASE):
            return tag
        count += 1
        # insert right after the "<img" token (first 4 chars of the match)
        return tag[:4] + ' loading="lazy"' + tag[4:]

    result = re.sub(r"<img\b[^>]*>", _add_lazy, html, flags=re.IGNORECASE | re.DOTALL)
    return result, count


def find_missing_alt(html: str) -> list[str]:
    """Return srcs of <img> tags missing an alt attribute (cannot auto-fix)."""
    missing: list[str] = []
    for m in re.finditer(r"<img\b([^>]*)>", html, re.IGNORECASE | re.DOTALL):
        attrs = m.group(1)
        if not re.search(r"\balt\s*=", attrs, re.IGNORECASE):
            src_m = re.search(r'\bsrc\s*=\s*["\']([^"\']+)["\']', attrs, re.IGNORECASE)
            missing.append(src_m.group(1) if src_m else "(unknown)")
    return missing


def split_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter_including_fences_or_empty, body)."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            nl = text.find("\n", end + 1)
            if nl != -1:
                return text[: nl + 1], text[nl + 1:]
    return "", text


def count_words(body: str) -> int:
    """Word count of body with HTML tags and markdown punctuation stripped."""
    clean = re.sub(r"<[^>]+>", " ", body)
    clean = re.sub(r"[*_`#\[\]()>~]", " ", clean)
    return len(clean.split())


def extract_h2s(body: str) -> list[tuple[str, str]]:
    """Return [(heading_text, anchor_slug)] for each ATX H2, skipping code fences."""
    out: list[tuple[str, str]] = []
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^## +(.+?)\s*#*\s*$", line)
        if m:
            heading = m.group(1).strip()
            slug = slugify(heading)
            if slug:
                out.append((heading, slug))
    return out


def toc_present(text: str) -> bool:
    """True if a TOC (this tool's marker or a common manual one) already exists."""
    if TOC_BEGIN in text:
        return True
    lowered = text.lower()
    return any(
        marker in lowered
        for marker in ("## table of contents", "## contents", "**in this article", "**table of contents")
    )


def build_toc(h2s: list[tuple[str, str]], heading: str = DEFAULT_TOC_HEADING) -> str:
    """Build an idempotent, marker-wrapped markdown TOC block."""
    lines = [TOC_BEGIN, f"**{heading}:**", ""]
    lines += [f"- [{text}](#{slug})" for text, slug in h2s]
    lines += ["", TOC_END, ""]
    return "\n".join(lines)


def insert_toc(md: str, min_words: int = 2000, heading: str = DEFAULT_TOC_HEADING) -> tuple[str, bool]:
    """Insert a TOC before the first body H2 when long enough and none present."""
    front, body = split_frontmatter(md)
    if toc_present(body) or count_words(body) < min_words:
        return md, False
    h2s = extract_h2s(body)
    if len(h2s) < 2:
        return md, False
    first = re.search(r"^## +", body, re.MULTILINE)
    if not first:
        return md, False
    toc = build_toc(h2s, heading) + "\n"
    new_body = body[: first.start()] + toc + body[first.start():]
    return front + new_body, True


def _read_safely(path: Path) -> str:
    if path.is_symlink():
        raise OSError(f"refusing to read symlink: {path}")
    if not path.is_file():
        raise OSError(f"not a regular file: {path}")
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        fh = os.fdopen(fd, "r", encoding="utf-8")
    except Exception:
        os.close(fd)
        raise
    with fh:
        return fh.read()


def _write_safely(path: Path, data: str) -> None:
    if path.is_symlink():
        raise OSError(f"refusing to write through symlink: {path}")
    path.write_text(data, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Deterministic blog draft hygiene (optional; never blocks).")
    ap.add_argument("--md", type=Path, help="Markdown draft (TOC insertion).")
    ap.add_argument("--html", type=Path, help="Rendered HTML (lazy-loading + alt report).")
    ap.add_argument("--apply", action="store_true", help="Write changes back (default: dry-run).")
    ap.add_argument("--min-words", type=int, default=2000, help="TOC word threshold (default 2000).")
    ap.add_argument("--toc-heading", default=DEFAULT_TOC_HEADING, help="TOC heading label.")
    args = ap.parse_args(argv)

    if not args.md and not args.html:
        ap.error("provide at least one of --md or --html")

    result: dict[str, object] = {
        "lazy_fixed": 0, "alt_missing": [], "toc_inserted": False,
        "applied": bool(args.apply), "changed_files": [], "warnings": [],
    }
    try:
        if args.html:
            html = _read_safely(args.html)
            new_html, n = fix_html_lazy_loading(html)
            result["lazy_fixed"] = n
            result["alt_missing"] = find_missing_alt(new_html)
            if args.apply and new_html != html:
                _write_safely(args.html, new_html)
                result["changed_files"].append(str(args.html))
        if args.md:
            md = _read_safely(args.md)
            new_md, inserted = insert_toc(md, args.min_words, args.toc_heading)
            result["toc_inserted"] = inserted
            if args.apply and inserted:
                _write_safely(args.md, new_md)
                result["changed_files"].append(str(args.md))
    except OSError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stdout)
        return 2

    if result["alt_missing"]:
        result["warnings"].append(f"{len(result['alt_missing'])} <img> tag(s) missing alt text; add manually.")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
