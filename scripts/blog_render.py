#!/usr/bin/env python3
"""Render a blog post markdown to .html and .pdf deterministically.

Reads a single .md file plus its frontmatter, emits:
  <out-dir>/<slug>.html: self-contained, dark-mode-aware, JSON-LD,
    Open Graph + Twitter Card, references hero.<ext> from the same dir.
  <out-dir>/<slug>.pdf: via patchright `page.pdf()` (preferred) or
    weasyprint fallback (only if patchright is unavailable).

This is the Gate 2 (Format Completeness) implementation of the v1.9.0
Blog Delivery Contract. Same source produces both outputs so they cannot
diverge.

Usage:
    python3 scripts/blog_render.py --md <path.md> --out-dir <dir> \\
        [--pdf-engine playwright|weasyprint|auto] [--json]

Returns 0 on success, 1 on render error or missing required artifact.
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import errno
import os
import re
import stat
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional

MAX_MD_BYTES = 4 * 1024 * 1024  # 4MB cap on a single markdown source
REQUIRED_FRONTMATTER_KEYS = ("title", "description", "date", "author")
# Markdown syntax fingerprints handled by python-markdown but NOT by the
# stdlib fallback in _stdlib_markdown. If the fallback path is taken AND
# any of these patterns appear in the body, the fallback emits a loud
# stderr warning so a silent-lossy render cannot ship undetected.
_LOSSY_FALLBACK_PATTERNS = {
    "table": re.compile(r"^\s*\|.+\|\s*$", re.MULTILINE),
    "footnote": re.compile(r"\[\^[^\]]+\]"),
    "definition_list": re.compile(r"^[^\n:]+\n:\s+", re.MULTILINE),
    "fenced_code_with_language": re.compile(r"^```[a-zA-Z0-9_+-]+", re.MULTILINE),
}
SAFE_LINK_SCHEMES = frozenset({"http", "https", "mailto"})
SAFE_MEDIA_SCHEMES = frozenset({"http", "https"})
DANGEROUS_SCHEMES = frozenset({"javascript", "data", "file", "vbscript"})
VOID_TAGS = frozenset({"br", "hr", "img"})
DROP_CONTENT_TAGS = frozenset({"script", "style", "iframe", "object", "embed", "template"})
ALLOWED_TAGS = frozenset({
    "a", "abbr", "blockquote", "br", "code", "dd", "del", "details", "div",
    "dl", "dt", "em", "figcaption", "figure", "h1", "h2", "h3", "h4", "h5",
    "h6", "hr", "img", "li", "ol", "p", "pre", "span", "strong", "sub",
    "summary", "sup", "table", "tbody", "td", "th", "thead", "tr", "ul",
    "svg", "g", "path", "rect", "circle", "line", "polyline", "polygon",
    "text", "tspan", "title", "desc",
})
GLOBAL_ATTRS = frozenset({"class", "id", "role", "aria-label"})
ALLOWED_ATTRS = {
    "a": frozenset({"href", "title", "rel", "target"}),
    "img": frozenset({"src", "alt", "title", "width", "height", "loading", "decoding"}),
    "svg": frozenset({"viewbox", "width", "height", "xmlns", "fill", "stroke"}),
    "path": frozenset({"d", "fill", "stroke", "stroke-width"}),
    "rect": frozenset({"x", "y", "width", "height", "rx", "ry", "fill", "stroke"}),
    "circle": frozenset({"cx", "cy", "r", "fill", "stroke"}),
    "line": frozenset({"x1", "x2", "y1", "y2", "stroke", "stroke-width"}),
    "polyline": frozenset({"points", "fill", "stroke", "stroke-width"}),
    "polygon": frozenset({"points", "fill", "stroke", "stroke-width"}),
    "text": frozenset({"x", "y", "fill", "font-size", "text-anchor"}),
    "tspan": frozenset({"x", "y", "dx", "dy", "fill", "font-size"}),
    "td": frozenset({"colspan", "rowspan"}),
    "th": frozenset({"colspan", "rowspan", "scope"}),
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#0d9488" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#18181b" media="(prefers-color-scheme: dark)">
<title>{title_escaped}</title>
<meta name="description" content="{description_escaped}">
{canonical_tag}
<meta name="author" content="{author_escaped}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="article">
<meta property="og:title" content="{title_escaped}">
<meta property="og:description" content="{description_escaped}">
{og_url_tag}
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{og_image_alt_escaped}">
<meta property="og:site_name" content="{site_name_escaped}">
<meta property="article:published_time" content="{published_iso}">
<meta property="article:author" content="{author_escaped}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title_escaped}">
<meta name="twitter:description" content="{description_escaped}">
<meta name="twitter:image" content="{og_image}">
<script type="application/ld+json">{json_ld}</script>
<style>{css}</style>
</head>
<body>
<article>
<header>
<p class="kicker">{kicker_escaped}</p>
<h1>{title_escaped}</h1>
<p class="dek">{description_escaped}</p>
<p class="byline"><strong>By {author_escaped}</strong> &middot; {published_human} &middot; {reading_time_min} min read &middot; {word_count} words</p>
</header>
<figure class="hero"><img src="{hero_filename}" alt="{og_image_alt_escaped}" width="1200" height="630"></figure>
{body_html}
<footer class="post-footer"><span>Published at <a href="{site_url_or_dash}">{site_name_escaped}</a></span><span>{published_human} &middot; {author_escaped}</span></footer>
</article>
</body>
</html>
"""

CSS = """
:root{--bg:#fafaf9;--surface:#fff;--text:#1c1917;--muted:#57534e;--soft:#78716c;--accent:#0d9488;--accent-soft:#ccfbf1;--accent-deep:#115e59;--border:#e7e5e4;--code-bg:#f5f5f4;--warn:#b91c1c;--shadow:0 1px 3px rgba(0,0,0,.06),0 4px 12px rgba(0,0,0,.04)}
@media (prefers-color-scheme:dark){:root{--bg:#18181b;--surface:#27272a;--text:#fafafa;--muted:#a1a1aa;--soft:#71717a;--accent:#2dd4bf;--accent-soft:#134e4a;--accent-deep:#99f6e4;--border:#3f3f46;--code-bg:#1f1f23;--warn:#fca5a5;--shadow:0 1px 3px rgba(0,0,0,.4),0 4px 12px rgba(0,0,0,.3)}}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.65;margin:0;font-size:17px;-webkit-font-smoothing:antialiased}
article{max-width:740px;margin:0 auto;padding:3rem 1.5rem 5rem}
.kicker{font-family:ui-monospace,"SF Mono",Monaco,monospace;font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin:0 0 .85rem;font-weight:600}
h1{font-size:clamp(2rem,5vw,2.85rem);line-height:1.12;letter-spacing:-.025em;margin:0 0 1.1rem;font-weight:800}
.dek{color:var(--muted);font-size:clamp(1.05rem,2.5vw,1.2rem);line-height:1.5;margin:0 0 1.75rem;max-width:60ch}
.byline{color:var(--soft);font-size:.875rem;font-family:ui-monospace,monospace;margin:0 0 2.5rem}
.byline strong{color:var(--text);font-weight:600}
.hero{margin:0 0 2.5rem;background:var(--surface);border:1px solid var(--border);border-radius:14px;overflow:hidden;box-shadow:var(--shadow)}
.hero img{display:block;width:100%;height:auto;aspect-ratio:1200/630;object-fit:cover}
h2{font-size:clamp(1.4rem,3vw,1.75rem);line-height:1.22;letter-spacing:-.015em;margin:3rem 0 1rem;font-weight:700;scroll-margin-top:1rem}
h3{font-size:1.2rem;margin:2rem 0 .75rem;font-weight:700}
p{margin:0 0 1.25rem}
a{color:var(--accent);text-decoration-thickness:1px;text-underline-offset:3px}
a:hover{color:var(--accent-deep)}
code{font-family:ui-monospace,"SF Mono",Monaco,monospace;font-size:.9em;background:var(--code-bg);border:1px solid var(--border);padding:.1em .4em;border-radius:4px}
pre{background:var(--code-bg);border:1px solid var(--border);border-radius:8px;padding:1rem;overflow-x:auto;font-size:.875rem}
pre code{background:none;border:none;padding:0}
blockquote{border-left:3px solid var(--accent);padding:.4rem 0 .4rem 1.25rem;margin:0 0 1.5rem;color:var(--muted)}
ul,ol{margin:0 0 1.25rem;padding-left:1.5rem}
li{margin:.35rem 0}
strong{font-weight:700;color:var(--text)}
img{max-width:100%;height:auto}
.post-footer{margin-top:4rem;padding-top:2rem;border-top:1px solid var(--border);font-size:.875rem;color:var(--muted);font-family:ui-monospace,monospace;display:flex;flex-wrap:wrap;gap:.6rem 1.5rem;justify-content:space-between}
.post-footer a{color:var(--accent);text-decoration:none}
::selection{background:var(--accent);color:var(--bg)}
@media print{body{background:#fff;color:#000;font-size:11pt}article{max-width:none;padding:0 1rem}.hero{box-shadow:none}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""


def _slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9\s\-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-") or "post"


def _is_safe_url(value: str, *, media: bool = False) -> bool:
    """Return True when a URL is safe for an HTML attribute."""
    value = html_lib.unescape(value).strip()
    if not value:
        return False
    parsed = urllib.parse.urlparse(value)
    scheme = parsed.scheme.lower()
    if scheme in DANGEROUS_SCHEMES:
        return False
    if not scheme:
        return not value.startswith(("//", "\\"))
    if media:
        return scheme in SAFE_MEDIA_SCHEMES
    return scheme in SAFE_LINK_SCHEMES


def _safe_attr(value: object) -> str:
    return html_lib.escape(str(value), quote=True)


class _BodySanitizer(HTMLParser):
    """Small allowlist sanitizer for markdown-rendered body HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.out: list[str] = []
        self.drop_depth = 0

    def _clean_attrs(self, tag: str, attrs: list[tuple[str, str | None]]) -> str:
        allowed = ALLOWED_ATTRS.get(tag, frozenset()) | GLOBAL_ATTRS
        clean: list[str] = []
        for raw_name, raw_value in attrs:
            name = raw_name.lower()
            if name.startswith("on") or name not in allowed:
                continue
            if raw_value is None:
                continue
            value = raw_value.strip()
            if name in {"href", "src"} and not _is_safe_url(value, media=(name == "src")):
                continue
            clean.append(f'{name}="{_safe_attr(value)}"')
        return (" " + " ".join(clean)) if clean else ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in DROP_CONTENT_TAGS:
            self.drop_depth += 1
            return
        if self.drop_depth:
            return
        if tag not in ALLOWED_TAGS:
            return
        attr_text = self._clean_attrs(tag, attrs)
        self.out.append(f"<{tag}{attr_text}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if self.drop_depth or tag not in ALLOWED_TAGS:
            return
        attr_text = self._clean_attrs(tag, attrs)
        self.out.append(f"<{tag}{attr_text}>")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in DROP_CONTENT_TAGS and self.drop_depth:
            self.drop_depth -= 1
            return
        if self.drop_depth or tag not in ALLOWED_TAGS or tag in VOID_TAGS:
            return
        self.out.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if not self.drop_depth:
            self.out.append(html_lib.escape(data, quote=False))

    def handle_entityref(self, name: str) -> None:
        if not self.drop_depth:
            self.out.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if not self.drop_depth:
            self.out.append(f"&#{name};")


def _sanitize_body_html(raw_html: str) -> str:
    sanitizer = _BodySanitizer()
    sanitizer.feed(raw_html)
    sanitizer.close()
    return "".join(sanitizer.out)


def _validate_hero_filename(name: str) -> str:
    if "/" in name or "\\" in name or Path(name).name != name:
        raise ValueError("hero filename must be a basename in the output directory")
    if not re.fullmatch(r"[A-Za-z0-9._-]+\.(?:png|jpg|jpeg|webp)", name, re.IGNORECASE):
        raise ValueError("hero filename must be hero.<png|jpg|jpeg|webp> style raster asset")
    return name


def _parse_frontmatter(raw: str) -> tuple[dict, str]:
    """Minimal YAML frontmatter parser. Supports flat key: value and simple lists."""
    if not raw.startswith("---"):
        return {}, raw
    end = raw.find("\n---", 3)
    if end == -1:
        return {}, raw
    fm_text = raw[3:end].strip("\n")
    body = raw[end + 4:].lstrip("\n")
    fm: dict = {}
    current_list_key: Optional[str] = None
    for line in fm_text.split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and current_list_key:
            fm.setdefault(current_list_key, []).append(line[4:].strip().strip('"').strip("'"))
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if not value:
                current_list_key = key
                fm[key] = []
            else:
                current_list_key = None
                fm[key] = value.strip('"').strip("'")
    return fm, body


def _markdown_to_html(body: str) -> str:
    """Convert markdown body to HTML. Uses python-markdown if installed,
    else a minimal stdlib subset (ATX headings, paragraphs, code, links,
    emphasis, lists, blockquotes, hr, images)."""
    try:
        import markdown  # type: ignore
        return _sanitize_body_html(markdown.markdown(body, extensions=["extra", "sane_lists"]))
    except ImportError:
        return _sanitize_body_html(_stdlib_markdown(body))


def _stdlib_markdown(body: str) -> str:
    lines = body.split("\n")
    out: list[str] = []
    in_code = False
    code_buf: list[str] = []
    para_buf: list[str] = []
    in_list = False
    list_tag = "ul"

    def flush_para():
        if para_buf:
            text = " ".join(para_buf).strip()
            if text:
                out.append(f"<p>{_inline(text)}</p>")
            para_buf.clear()

    def flush_list():
        nonlocal in_list
        if in_list:
            out.append(f"</{list_tag}>")
            in_list = False

    for line in lines:
        stripped = line.rstrip()
        if stripped.startswith("```"):
            if in_code:
                out.append("<pre><code>" + html_lib.escape("\n".join(code_buf)) + "</code></pre>")
                code_buf.clear()
                in_code = False
            else:
                flush_para()
                flush_list()
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue
        if not stripped:
            flush_para()
            flush_list()
            continue
        h = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if h:
            flush_para()
            flush_list()
            level = len(h.group(1))
            out.append(f"<h{level}>{_inline(h.group(2))}</h{level}>")
            continue
        if stripped.startswith("> "):
            flush_para()
            flush_list()
            out.append(f"<blockquote><p>{_inline(stripped[2:])}</p></blockquote>")
            continue
        if stripped in ("---", "***", "___"):
            flush_para()
            flush_list()
            out.append("<hr>")
            continue
        ol_match = re.match(r"^\d+\.\s+(.+)$", stripped)
        ul_match = re.match(r"^[-*+]\s+(.+)$", stripped)
        if ul_match or ol_match:
            flush_para()
            new_tag = "ol" if ol_match else "ul"
            if in_list and list_tag != new_tag:
                flush_list()
            if not in_list:
                list_tag = new_tag
                out.append(f"<{list_tag}>")
                in_list = True
            content = (ol_match or ul_match).group(1)
            out.append(f"<li>{_inline(content)}</li>")
            continue
        para_buf.append(stripped)

    flush_para()
    flush_list()
    return "\n".join(out)


def _inline(text: str) -> str:
    """Inline markdown: code, bold, italic, links, images. Operates on
    text where the outer block (heading/paragraph/li) is already established."""
    # Escape HTML first, including quotes so attribute replacements cannot break out.
    text = html_lib.escape(text, quote=True)

    def image_repl(match: re.Match[str]) -> str:
        alt = match.group(1)
        url = html_lib.unescape(match.group(2))
        if not _is_safe_url(url, media=True):
            return alt
        return f'<img src="{_safe_attr(url)}" alt="{_safe_attr(html_lib.unescape(alt))}">'

    def link_repl(match: re.Match[str]) -> str:
        label = match.group(1)
        url = html_lib.unescape(match.group(2))
        if not _is_safe_url(url):
            return label
        return f'<a href="{_safe_attr(url)}">{label}</a>'

    # Images: ![alt](url)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", image_repl, text)
    # Links: [text](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, text)
    # Inline code: `code`
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Bold: **text**
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # Italic: *text*
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def _build_json_ld(fm: dict, word_count: int, og_image_url: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": fm.get("title", ""),
        "description": fm.get("description", ""),
        "image": og_image_url,
        "datePublished": fm.get("date", ""),
        "dateModified": fm.get("date", ""),
        "author": {"@type": "Person", "name": fm.get("author", "")},
        "wordCount": word_count,
        "keywords": ", ".join(fm.get("tags", [])) if isinstance(fm.get("tags"), list) else fm.get("tags", ""),
        "inLanguage": fm.get("lang", "en"),
    }
    if fm.get("canonical"):
        data["mainEntityOfPage"] = {"@type": "WebPage", "@id": fm["canonical"]}
    # HTML-safe JSON encoding: escape "</" as "<\/" so an attacker who controls
    # a frontmatter value (e.g. title) cannot inject a literal "</script>" that
    # would break out of the surrounding <script type="application/ld+json">
    # block and execute arbitrary JS. "\/" is a valid JSON escape for "/",
    # so the embedded JSON remains semantically identical for any parser.
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def _read_md_safely(path: Path) -> str:
    """Read a markdown source with symlink refusal + size cap. Mirrors the
    O_NOFOLLOW pattern used by scripts/load_untrusted_root.py for project-
    root files so a caller cannot redirect the renderer at an attacker-
    chosen target via symlink."""
    try:
        fd = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as e:
        if e.errno in (errno.ELOOP, errno.EMLINK):
            raise ValueError(f"refusing to follow symlink: {path}")
        raise
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise ValueError(f"not a regular file: {path}")
        if st.st_size > MAX_MD_BYTES:
            raise ValueError(f"source markdown exceeds {MAX_MD_BYTES} bytes")
        data = os.read(fd, MAX_MD_BYTES + 1)
    finally:
        os.close(fd)
    if len(data) > MAX_MD_BYTES:
        raise ValueError(f"source markdown exceeds {MAX_MD_BYTES} bytes")
    return data.decode("utf-8")


def _validate_frontmatter(fm: dict, body: str) -> None:
    """Reject empty body or missing required frontmatter keys. The renderer
    must not silently produce a content-less HTML shell with a title taken
    from the filename stem (F1, F2 from the v1.9.0 hostile review)."""
    missing = [k for k in REQUIRED_FRONTMATTER_KEYS if not str(fm.get(k, "")).strip()]
    if missing:
        raise ValueError(
            f"missing or empty required frontmatter key(s): {missing}. "
            f"Required: {list(REQUIRED_FRONTMATTER_KEYS)}."
        )
    if not body.strip():
        raise ValueError(
            "markdown body is empty (after frontmatter). The renderer refuses "
            "to produce a content-less HTML shell."
        )


def _warn_if_stdlib_fallback_is_lossy(body: str) -> None:
    """If python-markdown is not importable AND the body contains syntax the
    stdlib fallback drops on the floor (tables, footnotes, def lists,
    language-tagged fenced code blocks), emit a loud stderr warning so the
    user notices the fidelity loss instead of shipping silently-lossy HTML."""
    try:
        import markdown  # noqa: F401  # type: ignore
        return  # python-markdown handles all of these
    except ImportError:
        pass
    hits = []
    for name, pattern in _LOSSY_FALLBACK_PATTERNS.items():
        if pattern.search(body):
            hits.append(name)
    if hits:
        print(
            "WARN: python-markdown not installed; the stdlib fallback will "
            f"drop or mis-render: {sorted(hits)}. Install with "
            "`pip install -e .[presentation]` for full fidelity.",
            file=sys.stderr,
        )


def _render_html(md_path: Path, out_dir: Path, hero_filename: str) -> Path:
    hero_filename = _validate_hero_filename(hero_filename)
    raw = _read_md_safely(md_path)
    fm, body = _parse_frontmatter(raw)
    _validate_frontmatter(fm, body)
    _warn_if_stdlib_fallback_is_lossy(body)

    body_html = _markdown_to_html(body)
    # Strip a leading <h1> from the body if the template already provides
    # the title as H1 from frontmatter (prevents duplicate-H1 SEO defect).
    # Use .*? with DOTALL so inline formatting (<strong>, <em>, <code>) inside
    # the H1 is still recognised; count=1 so only the leading H1 is stripped,
    # never a legitimate mid-document H1.
    body_html = re.sub(r"\A\s*<h1\b[^>]*>.*?</h1>\s*", "", body_html, count=1, flags=re.DOTALL)
    # Word count from rendered visible text. Must match what Gate 5 measures
    # from <article> so the wordCount injected into JSON-LD does not drift
    # past the 5% tolerance and falsely block delivery. Gate 5's _MetaParser
    # in blog_preflight.py excludes <code> content; we exclude <pre>/<code>
    # blocks here too. Counting code-block tokens as prose words causes
    # ~15-20% over-count on docs that contain code samples (real defect
    # caught by the v1.9.0 audit's end-to-end test).
    visible_text = re.sub(r"<pre[^>]*>.*?</pre>", " ", body_html, flags=re.DOTALL)
    visible_text = re.sub(r"<code[^>]*>.*?</code>", " ", visible_text, flags=re.DOTALL)
    visible_text = re.sub(r"<[^>]+>", " ", visible_text)
    visible_text = html_lib.unescape(visible_text)
    word_count = len(re.findall(r"\b\w+\b", visible_text))
    reading_time = max(1, word_count // 200)

    canonical = fm.get("canonical", "")
    title = fm.get("title", md_path.stem)
    site_name = fm.get("site_name") or (canonical.split("/")[2] if canonical.startswith("http") else "")
    site_url = "/".join(canonical.split("/")[:3]) if canonical.startswith("http") else ""
    og_image = canonical.rstrip("/") + "/" + hero_filename if canonical else hero_filename

    rendered = HTML_TEMPLATE.format(
        lang=_safe_attr(fm.get("lang", "en")),
        title_escaped=_safe_attr(title),
        description_escaped=_safe_attr(fm.get("description", "")),
        canonical_tag=f'<link rel="canonical" href="{_safe_attr(canonical)}">' if canonical else "",
        author_escaped=_safe_attr(fm.get("author", "Anonymous")),
        og_url_tag=f'<meta property="og:url" content="{_safe_attr(canonical)}">' if canonical else "",
        og_image=_safe_attr(og_image),
        og_image_alt_escaped=_safe_attr(fm.get("og_image_alt", title)),
        site_name_escaped=_safe_attr(site_name or "Blog"),
        published_iso=_safe_attr(fm.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))),
        published_human=_safe_attr(fm.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))),
        reading_time_min=reading_time,
        word_count=word_count,
        kicker_escaped=_safe_attr(fm.get("kicker") or (fm.get("tags")[0].title() if isinstance(fm.get("tags"), list) and fm.get("tags") else "Article")),
        hero_filename=_safe_attr(hero_filename),
        body_html=body_html,
        site_url_or_dash=_safe_attr(site_url or "#"),
        json_ld=_build_json_ld(fm, word_count, og_image),
        css=CSS,
    )

    slug = _slugify(str(fm.get("slug") or title))
    out_root = out_dir.resolve()
    out_html = (out_root / f"{slug}.html").resolve(strict=False)
    out_html.relative_to(out_root)
    if out_html.exists() and out_html.is_symlink():
        raise ValueError(f"refusing to overwrite symlink: {out_html}")
    out_html.write_text(rendered, encoding="utf-8")
    return out_html


def _render_pdf(html_path: Path, out_pdf: Path, engine: str) -> bool:
    """Render html_path to out_pdf via the chosen engine. Returns True on
    success, False on failure (no exception raised; caller decides)."""
    asset_root = html_path.parent.resolve()

    def _local_asset_allowed(url: str) -> bool:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme in ("http", "https"):
            return False
        if parsed.scheme == "file":
            try:
                path = Path(urllib.request.url2pathname(parsed.path)).resolve()
                path.relative_to(asset_root)
                return not path.is_symlink()
            except ValueError:
                return False
        return parsed.scheme in ("", "about", "data")

    if engine in ("auto", "playwright"):
        sync_playwright = None
        try:
            from patchright.sync_api import sync_playwright  # type: ignore
        except ImportError:
            try:
                from playwright.sync_api import sync_playwright  # type: ignore
            except ImportError:
                pass
        if sync_playwright is not None:
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch()
                    page = browser.new_page()
                    def route_guard(route):
                        if _local_asset_allowed(route.request.url):
                            route.continue_()
                        else:
                            route.abort()
                    page.route("**/*", route_guard)
                    page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
                    page.pdf(path=str(out_pdf), format="A4", print_background=True)
                    browser.close()
                return True
            except Exception as e:
                print(f"[render] playwright/patchright failed: {e}", file=sys.stderr)
                if engine == "playwright":
                    return False
    if engine in ("auto", "weasyprint"):
        try:
            from weasyprint import HTML, default_url_fetcher  # type: ignore
            def fetcher(url: str, *args, **kwargs):
                if not _local_asset_allowed(url):
                    raise ValueError(f"blocked external PDF asset: {url}")
                return default_url_fetcher(url, *args, **kwargs)
            HTML(filename=str(html_path), url_fetcher=fetcher).write_pdf(str(out_pdf))
            return True
        except Exception as e:
            print(f"[render] weasyprint failed: {e}", file=sys.stderr)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--md", required=True, help="Path to markdown source file")
    parser.add_argument("--out-dir", required=True, help="Output directory for .html and .pdf")
    parser.add_argument("--hero", default="hero.png", help="Hero image filename (relative to out-dir)")
    parser.add_argument("--pdf-engine", choices=["auto", "playwright", "weasyprint", "none"], default="auto")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    # Do NOT call .resolve() here: that would silently follow symlinks before
    # _read_md_safely (which uses O_NOFOLLOW) gets a chance to refuse them.
    # Use .absolute() to get an unambiguous path that preserves symlink ID.
    md_path = Path(args.md).absolute()
    if not md_path.is_file() and not md_path.is_symlink():
        print(f"ERROR: {md_path} not a file", file=sys.stderr)
        return 1
    raw_out_dir = Path(args.out_dir)
    if raw_out_dir.exists() and raw_out_dir.is_symlink():
        print(f"ERROR: refusing symlink output directory: {raw_out_dir}", file=sys.stderr)
        return 1
    out_dir = raw_out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        html_path = _render_html(md_path, out_dir, args.hero)
    except Exception as e:
        print(f"ERROR: html render failed: {e}", file=sys.stderr)
        return 1

    result = {"html": str(html_path), "pdf": None}
    if args.pdf_engine != "none":
        pdf_path = html_path.with_suffix(".pdf")
        if _render_pdf(html_path, pdf_path, args.pdf_engine):
            result["pdf"] = str(pdf_path)
        else:
            print("ERROR: PDF render requested but no PDF artifact was produced", file=sys.stderr)
            if args.json:
                print(json.dumps(result))
            return 1

    if args.json:
        print(json.dumps(result))
    else:
        print(f"OK: {html_path}")
        if result["pdf"]:
            print(f"OK: {result['pdf']}")
        else:
            print("WARN: PDF render skipped or failed", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
