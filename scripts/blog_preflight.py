#!/usr/bin/env python3
"""Run the Blog Delivery Contract preflight gates against a draft folder.

Implements Gates 1, 2, 3, and 5 of the v1.9.0 Blog Delivery Contract.
Gate 4 (Content Review) is dispatched by the orchestrator as the
blog-reviewer agent; this script only verifies that the agent's output
exists and that its BLOCKING decision is `false`.

Output:
  <draft>/preflight-report.json: machine-readable gate results
  <draft>/capabilities.json: emitted by Gate 1, consumed by 2-5
  <draft>/preview/*.png: emitted by Gate 3 (if patchright installed)

Usage:
    python3 scripts/blog_preflight.py --draft <dir> [--gate N] [--strict] [--json]

  --gate N    Run only the named gate (1-5). Default: all 5 sequentially.
  --strict    Exit 1 if any gate blocks. Default: on. Use --no-strict to
              proceed regardless (logs the bypass loudly).
  --json      Emit the report JSON to stdout in addition to the file.

Exit codes: 0 = all gates passed; 1 = at least one gate blocked
(when --strict). Warnings never block.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Optional

CONTRACT_REF = "skills/blog/references/blog-delivery-contract.md"
REQUIRED_AGENTS = ("blog-reviewer",)
OPTIONAL_AGENTS = ("blog-researcher", "blog-writer", "blog-seo", "blog-translator")
REQUIRED_SCRIPTS = ("scripts/lint_prose.py", "scripts/load_untrusted_root.py", "scripts/analyze_blog.py")
VIEWPORTS = [
    {"name": "mobile", "width": 375, "height": 812},
    {"name": "tablet", "width": 768, "height": 1024},
    {"name": "desktop", "width": 1280, "height": 800},
]
HEAD_TIMEOUT = 10
USER_AGENT = "claude-blog/1.9.0 preflight (+https://github.com/AgriciDaniel/claude-blog)"
URL_ALLOWLIST = ("localhost", "127.0.0.1", "example.com", "example.org")

# VULN-802 code-enforced iteration counter (v1.9.1).
# The contract documents "up to 3 retries before escalating." v1.9.0
# enforced this only as orchestrator prose; any draft-controlled text
# could convince the orchestrator the counter was at 0. v1.9.1 backs the
# claim with a file on disk that survives across preflight invocations.
ITERATION_COUNTER_FILE = ".iteration-count"
MAX_ITERATIONS = 3
EXIT_ITERATION_CAP = 2

# VULN-803 nonce-bound review.md provenance (v1.9.1).
# Before v1.9.1, Gate 4 trusted any writer of <draft>/review.md. A malicious
# sub-skill or prompt-injected sibling agent could satisfy the gate by
# writing one line. v1.9.1 binds the review to a CSPRNG nonce written by
# the orchestrator before agent dispatch; the agent must echo the nonce
# back in review.md. Backwards-compat: drafts initialised before v1.9.1
# (no nonce file) pass with a deprecation warning until v1.10.0.
REVIEW_NONCE_FILE = ".review-nonce"
NONCE_PATTERN = re.compile(r"^Nonce:\s*([0-9a-f]{32})\s*$", re.MULTILINE | re.IGNORECASE)


def _init_review_nonce(draft: Path) -> str:
    """Generate a CSPRNG nonce and write it to <draft>/.review-nonce.

    Returns the nonce hex string. Overwrites any prior nonce so each
    review attempt has fresh provenance.
    """
    import secrets
    nonce = secrets.token_hex(16)
    nonce_path = draft / REVIEW_NONCE_FILE
    import tempfile
    fd, tmp = tempfile.mkstemp(
        dir=str(nonce_path.parent), prefix=f".{nonce_path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(f"{nonce}\n")
        os.replace(tmp, str(nonce_path))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return nonce


def _iteration_check(draft: Path, reset: bool = False) -> int:
    """Read/increment the per-draft iteration counter; refuse past cap.

    Behavior:
      * reset=True: counter is set to 1 (this run counts as iteration 1).
      * reset=False, counter absent or corrupt: counter is set to 1.
      * reset=False, counter at MAX_ITERATIONS: emit stderr message and
        return EXIT_ITERATION_CAP. Caller should sys.exit(2).
      * Otherwise: counter += 1; return 0.

    Fail-soft on corrupt counter file: a non-integer value resets to 1
    rather than refusing to run (an attacker who can write to the draft
    folder has bigger problems; refusing on garbage would be a self-DoS).
    """
    counter_path = draft / ITERATION_COUNTER_FILE
    if reset:
        _atomic_write_counter(counter_path, 1)
        return 0
    try:
        raw = counter_path.read_text(encoding="utf-8").strip()
        current = int(raw)
    except (FileNotFoundError, ValueError, OSError):
        current = 0
    if current >= MAX_ITERATIONS:
        sys.stderr.write(
            f"ITERATION CAP EXCEEDED: this draft has used all {MAX_ITERATIONS} "
            f"preflight iterations. Escalate to the user, or run with "
            f"--reset-iterations after a code change.\n"
        )
        return EXIT_ITERATION_CAP
    _atomic_write_counter(counter_path, current + 1)
    return 0


def _atomic_write_counter(path: Path, value: int) -> None:
    """Atomic write of the integer counter (mkstemp + os.replace)."""
    import tempfile
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(f"{int(value)}\n")
        os.replace(tmp, str(path))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _gate_result(gate: int, name: str, passed: bool, violations: Optional[list] = None, warnings: Optional[list] = None, **kwargs: Any) -> dict:
    return {
        "gate": gate,
        "name": name,
        "passed": passed,
        "violations": violations or [],
        "warnings": warnings or [],
        **kwargs,
    }


def _has_module(name: str) -> bool:
    # find_spec raises ImportError/ValueError for a dotted name whose parent
    # package is absent (e.g. "google.genai" when "google" isn't installed),
    # instead of returning None. Treat any resolution failure as "not present".
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _detect_loaded_mcp() -> list[str]:
    """Best-effort detection. The MCP transport state is not introspectable
    from a subprocess; we report what's declared in .mcp.json. The
    orchestrator's tool availability is the real authority."""
    mcp_path = _project_root() / ".mcp.json"
    if not mcp_path.is_file():
        return []
    try:
        cfg = json.loads(mcp_path.read_text(encoding="utf-8"))
        return list((cfg.get("mcpServers") or {}).keys())
    except Exception:
        return []


def gate_1_capability_discovery(draft_dir: Path) -> dict:
    """Enumerate available capabilities; write capabilities.json."""
    root = _project_root()
    env_keys = {
        "GOOGLE_AI_API_KEY": bool(os.environ.get("GOOGLE_AI_API_KEY")),
        "UNSPLASH_ACCESS_KEY": bool(os.environ.get("UNSPLASH_ACCESS_KEY")),
        "PEXELS_API_KEY": bool(os.environ.get("PEXELS_API_KEY")),
        "PIXABAY_API_KEY": bool(os.environ.get("PIXABAY_API_KEY")),
    }
    mcp_declared = _detect_loaded_mcp()
    py_deps = {
        "patchright": _has_module("patchright"),
        "playwright": _has_module("playwright"),
        "weasyprint": _has_module("weasyprint"),
        "google.genai": _has_module("google.genai") or _has_module("google_genai"),
        "requests": _has_module("requests"),
        "markdown": _has_module("markdown"),
    }
    project_files = {
        "BRAND.md": (root / "BRAND.md").is_file(),
        "VOICE.md": (root / "VOICE.md").is_file(),
        "DISCOURSE.md": (root / "DISCOURSE.md").is_file(),
    }
    agents = {a: (root / "agents" / f"{a}.md").is_file() for a in REQUIRED_AGENTS + OPTIONAL_AGENTS}
    scripts = {s: (root / s).is_file() for s in REQUIRED_SCRIPTS}

    configured_image_paths = (
        "nanobanana-mcp" in mcp_declared
        or env_keys["GOOGLE_AI_API_KEY"]
        or env_keys["UNSPLASH_ACCESS_KEY"]
        or env_keys["PEXELS_API_KEY"]
        or env_keys["PIXABAY_API_KEY"]
    )
    # Openverse is the no-key fallback at the bottom of the ladder. We do NOT
    # probe its reachability here (network HEAD at gate-1 time is too slow
    # and flaky); we report it as best-effort and let generate_hero.py
    # surface a runtime failure if Openverse is unreachable when invoked.
    image_gen_available = configured_image_paths  # explicit configured paths
    openverse_assumed_available = True            # best-effort fallback

    capabilities = {
        "mcp_declared": mcp_declared,
        "env_keys_present": env_keys,
        "python_deps": py_deps,
        "project_root_files": project_files,
        "agents": agents,
        "scripts": scripts,
        "image_gen_path_available": image_gen_available,
        "openverse_assumed_available": openverse_assumed_available,
    }
    (draft_dir / "capabilities.json").write_text(json.dumps(capabilities, indent=2), encoding="utf-8")

    violations = []
    warnings = []
    if not agents.get("blog-reviewer", False):
        violations.append("blog-reviewer agent missing; cannot enforce Gate 4")
    if not image_gen_available:
        # No configured image path. Openverse is the best-effort fallback but
        # is not probed for reachability here (D1 from v1.9.0 hostile review:
        # do not short-circuit gate-1 with `or True`). Warn loudly so the
        # operator knows the contract will degrade to Openverse-only.
        warnings.append(
            "no configured image-gen path (Banana MCP / GOOGLE_AI_API_KEY / "
            "UNSPLASH_ACCESS_KEY / PEXELS_API_KEY / PIXABAY_API_KEY). "
            "generate_hero.py will fall through to Openverse (no key required) "
            "and fail at runtime if Openverse is unreachable."
        )
    if not py_deps["patchright"] and not py_deps["playwright"]:
        warnings.append("neither patchright nor playwright installed; Gate 3 will warn-and-pass")
    if not py_deps["weasyprint"] and not py_deps["patchright"] and not py_deps["playwright"]:
        warnings.append("no PDF backend installed (patchright/playwright/weasyprint); PDF generation will fail")

    return _gate_result(1, "Capability Discovery", not violations, violations, warnings, capabilities=capabilities)


def gate_2_format_completeness(draft_dir: Path) -> dict:
    """Verify .md, .html, .pdf, hero.<ext> all exist."""
    mds = list(draft_dir.glob("*.md"))
    htmls = list(draft_dir.glob("*.html"))
    pdfs = list(draft_dir.glob("*.pdf"))
    heroes = list(draft_dir.glob("hero.*"))
    review = draft_dir / "review.md"

    violations = []
    if not mds:
        violations.append("no .md source found")
    if not htmls:
        violations.append("no .html artifact found (run scripts/blog_render.py)")
    if not pdfs:
        violations.append("no .pdf artifact found (run scripts/blog_render.py)")
    hero_files = [h for h in heroes if h.name != "hero-credit.txt" and h.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
    if not hero_files:
        violations.append("no hero.<png|jpg|jpeg|webp> found (run scripts/generate_hero.py)")

    return _gate_result(
        2, "Format Completeness", not violations, violations, [],
        artifacts={
            "md": [str(p.name) for p in mds],
            "html": [str(p.name) for p in htmls],
            "pdf": [str(p.name) for p in pdfs],
            "hero": [str(p.name) for p in hero_files],
            "review_present": review.is_file(),
        },
    )


def gate_3_visual_verification(draft_dir: Path) -> dict:
    """Render the .html via patchright (or playwright); screenshot at 3
    widths; check SVG bboxes, dark mode, console errors, JSON-LD."""
    sync_playwright = None
    backend = None
    try:
        from patchright.sync_api import sync_playwright  # type: ignore
        backend = "patchright"
    except ImportError:
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
            backend = "playwright"
        except ImportError:
            pass
    if sync_playwright is None:
        return _gate_result(
            3, "Visual Verification", True, [],
            ["neither patchright nor playwright installed; skipping visual checks. Run pip install -e .[presentation] to enable."],
        )

    htmls = list(draft_dir.glob("*.html"))
    if not htmls:
        return _gate_result(3, "Visual Verification", False, ["no .html artifact to verify"])

    html_path = htmls[0]
    preview_dir = draft_dir / "preview"
    preview_dir.mkdir(exist_ok=True)

    violations = []
    warnings = [f"backend: {backend}"]
    per_viewport: dict = {}

    bbox_check_js = """
() => {
  const overflows = [];
  const svgs = document.querySelectorAll('svg');
  svgs.forEach((svg, i) => {
    const svgBox = svg.getBoundingClientRect();
    const desc = svg.querySelectorAll('text, path, rect, image, circle, line');
    desc.forEach((child) => {
      const r = child.getBoundingClientRect();
      const margin = 2;
      if (r.left < svgBox.left - margin || r.right > svgBox.right + margin ||
          r.top < svgBox.top - margin || r.bottom > svgBox.bottom + margin) {
        overflows.push({svgIndex: i, tag: child.tagName, content: (child.textContent||'').slice(0,40),
          childBox:{l:r.left,r:r.right,t:r.top,b:r.bottom},
          svgBox:{l:svgBox.left,r:svgBox.right,t:svgBox.top,b:svgBox.bottom}});
      }
    });
  });
  const bg = getComputedStyle(document.body).backgroundColor;
  const jsonLd = document.querySelector('script[type="application/ld+json"]');
  let jsonLdValid = false, jsonLdType = null, jsonLdMissingFields = [];
  if (jsonLd) {
    try {
      const obj = JSON.parse(jsonLd.textContent);
      jsonLdValid = true;
      jsonLdType = obj['@type'];
      const required = ['headline','image','datePublished','author'];
      jsonLdMissingFields = required.filter(k => !obj[k]);
    } catch (e) { jsonLdValid = false; }
  }
  return {overflows, bg, jsonLdValid, jsonLdType, jsonLdMissingFields};
}
""".strip()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for vp in VIEWPORTS:
                context = browser.new_context(viewport={"width": vp["width"], "height": vp["height"]})
                page = context.new_page()
                console_errors: list[str] = []
                page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
                page.goto(f"file://{html_path.resolve()}", wait_until="networkidle", timeout=30_000)
                page.screenshot(path=str(preview_dir / f"{vp['name']}-{vp['width']}.png"), full_page=True)
                result = page.evaluate(bbox_check_js)
                per_viewport[vp["name"]] = {"result": result, "console_errors": console_errors}
                if result["overflows"]:
                    violations.append(f"{vp['name']}: {len(result['overflows'])} SVG overflow(s)")
                if console_errors:
                    violations.append(f"{vp['name']}: {len(console_errors)} console error(s)")
                if not result["jsonLdValid"]:
                    violations.append(f"{vp['name']}: JSON-LD invalid or missing")
                elif result["jsonLdType"] != "BlogPosting":
                    violations.append(f"{vp['name']}: JSON-LD @type != BlogPosting")
                elif result["jsonLdMissingFields"]:
                    violations.append(f"{vp['name']}: JSON-LD missing fields: {result['jsonLdMissingFields']}")
                context.close()

            # Dark mode pass at desktop width
            context = browser.new_context(viewport={"width": 1280, "height": 800}, color_scheme="dark")
            page = context.new_page()
            page.goto(f"file://{html_path.resolve()}", wait_until="networkidle", timeout=30_000)
            dark_bg = page.evaluate("() => getComputedStyle(document.body).backgroundColor")
            light_bg = per_viewport["desktop"]["result"]["bg"]
            page.screenshot(path=str(preview_dir / "desktop-1280-dark.png"), full_page=True)
            if dark_bg == light_bg:
                violations.append(f"dark mode did not change background color (still {dark_bg})")
            per_viewport["desktop-dark"] = {"bg": dark_bg, "light_bg": light_bg}
            context.close()
            browser.close()
    except Exception as e:
        return _gate_result(3, "Visual Verification", False, [f"patchright runtime error: {e}"])

    return _gate_result(3, "Visual Verification", not violations, violations, warnings, per_viewport=per_viewport)


class _MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.imgs: list[str] = []
        self.links: list[str] = []
        self.codes: list[str] = []
        self.og_image: Optional[str] = None
        self.canonical: Optional[str] = None
        self.json_ld_blocks: list[str] = []
        self._in_jsonld = False
        self._in_article = False
        self._in_code = False
        self._in_header = False
        self._in_footer = False
        self.article_text_chars = 0

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "img" and d.get("src"):
            self.imgs.append(d["src"])
        elif tag == "a" and d.get("href"):
            self.links.append(d["href"])
        elif tag == "meta" and d.get("property") == "og:image" and d.get("content"):
            self.og_image = d["content"]
        elif tag == "link" and d.get("rel") == "canonical" and d.get("href"):
            self.canonical = d["href"]
        elif tag == "script" and d.get("type") == "application/ld+json":
            self._in_jsonld = True
        elif tag == "article":
            self._in_article = True
        elif tag == "header":
            self._in_header = True
        elif tag == "footer":
            self._in_footer = True
        elif tag == "code":
            self._in_code = True

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_jsonld = False
        elif tag == "article":
            self._in_article = False
        elif tag == "header":
            self._in_header = False
        elif tag == "footer":
            self._in_footer = False
        elif tag == "code":
            self._in_code = False

    def handle_data(self, data):
        if self._in_jsonld:
            self.json_ld_blocks.append(data)
        if self._in_code and self._in_article:
            self.codes.append(data.strip())
        # Count body-only words: exclude <header> (title, byline), <footer>
        # (site/date), and <code> blocks. Aligned with blog_render.py's
        # wordCount semantics so Gate 5 catches real drift, not template
        # boilerplate (v1.9.0 audit fix).
        if (self._in_article and not self._in_code
                and not self._in_header and not self._in_footer):
            self.article_text_chars += len(re.findall(r"\b\w+\b", data))


class _PreflightNoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Refuse automatic redirect-following in Gate 5 link checks (VULN-804).

    Default urllib follows 30x silently; a draft containing a redirect
    chain via attacker.example -> 169.254.169.254 would let preflight
    probe internal hosts. Refuse on the first hop; treat as broken link.
    """
    def http_error_301(self, req, fp, code, msg, headers):  # noqa: D401
        return None
    http_error_302 = http_error_301
    http_error_303 = http_error_301
    http_error_307 = http_error_301
    http_error_308 = http_error_301


_PREFLIGHT_NO_REDIRECT_OPENER = urllib.request.build_opener(_PreflightNoRedirectHandler())


def _http_head(url: str) -> int:
    """HEAD request that refuses to follow redirects (VULN-804)."""
    # VULN-002 (v1.9.1): explicit scheme check inside _http_head as
    # defense-in-depth. The upstream call site is supposed to filter
    # already, but matching the policy here closes the gap.
    if not url.startswith(("http://", "https://")):
        return 0
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
        with _PREFLIGHT_NO_REDIRECT_OPENER.open(req, timeout=HEAD_TIMEOUT) as resp:
            return resp.status
    except Exception:
        return 0


def _is_allowed_unreachable(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    return any(part in parsed.netloc for part in URL_ALLOWLIST)


def gate_5_asset_link_integrity(draft_dir: Path) -> dict:
    """Verify all <img> resolve, all <a> return 200, schema validates,
    word count within +/-5%."""
    htmls = list(draft_dir.glob("*.html"))
    if not htmls:
        return _gate_result(5, "Asset + Link Integrity", False, ["no .html artifact to verify"])

    html_path = htmls[0]
    raw = html_path.read_text(encoding="utf-8")
    parser = _MetaParser()
    parser.feed(raw)

    violations = []
    warnings = []

    # img src resolution
    for src in parser.imgs:
        if src.startswith("http://") or src.startswith("https://"):
            if _is_allowed_unreachable(src):
                continue
            if _http_head(src) != 200:
                warnings.append(f"img src returned non-200: {src}")
        else:
            local = (draft_dir / src).resolve()
            if not local.exists():
                violations.append(f"img src not on disk: {src}")

    # og:image specifically must resolve to a local hero.<ext> when canonical points to a host
    if parser.og_image:
        if parser.og_image.startswith(("http://", "https://")):
            hero_files = list(draft_dir.glob("hero.*"))
            hero_files = [h for h in hero_files if h.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
            if not hero_files:
                violations.append(f"og:image declared {parser.og_image} but no hero.<ext> exists locally")

    # canonical present
    if not parser.canonical:
        warnings.append("no <link rel=canonical> in document")

    # External links: explicit http/https allowlist. Other schemes (file://,
    # gopher://, ftp://, javascript:) are flagged as violations rather than
    # silently skipped (S3 from v1.9.0 hostile review). Relative/anchor links
    # without a scheme are left to Gate 5's img-src check above.
    for href in parser.links:
        if href.startswith(("http://", "https://")):
            if _is_allowed_unreachable(href):
                continue
            status = _http_head(href)
            if status == 0 or status >= 400:
                warnings.append(f"link returned {status}: {href}")
            continue
        if "://" in href or href.startswith(("javascript:", "data:", "vbscript:")):
            violations.append(
                f"non-http(s) URL scheme is not allowed in published links: {href}"
            )

    # JSON-LD validation
    json_ld_ok = False
    declared_word_count: Optional[int] = None
    if parser.json_ld_blocks:
        try:
            obj = json.loads("".join(parser.json_ld_blocks))
            json_ld_ok = True
            required = ("headline", "image", "datePublished", "author")
            missing = [k for k in required if not obj.get(k)]
            if missing:
                violations.append(f"JSON-LD missing required fields: {missing}")
            declared_word_count = obj.get("wordCount")
        except json.JSONDecodeError as e:
            violations.append(f"JSON-LD invalid: {e}")
    else:
        violations.append("no JSON-LD <script> block present")

    # word count match
    if declared_word_count is not None:
        actual = parser.article_text_chars
        if actual > 0:
            diff_pct = abs(declared_word_count - actual) / actual * 100
            if diff_pct > 5:
                violations.append(f"JSON-LD wordCount {declared_word_count} differs from actual {actual} by {diff_pct:.1f}%")

    return _gate_result(
        5, "Asset + Link Integrity", not violations, violations, warnings,
        imgs=parser.imgs, links_checked=len(parser.links),
        json_ld_valid=json_ld_ok, declared_word_count=declared_word_count,
        actual_word_count=parser.article_text_chars,
    )


def gate_4_content_review(draft_dir: Path) -> dict:
    """Check that the blog-reviewer agent has run and emitted review.md
    with `BLOCKING: false` AND a matching Nonce (v1.9.1).

    Nonce-bound provenance (VULN-803, v1.9.1):
      * If <draft>/.review-nonce exists, review.md MUST contain a line
        `Nonce: <matching-32-hex>` (case-insensitive, anchored to line).
        Missing or mismatched -> gate fails with explicit violation.
      * If <draft>/.review-nonce is absent, the gate emits a deprecation
        warning and falls back to v1.9.0 behavior (BLOCKING line only).
        This preserves backwards compatibility for drafts created before
        v1.9.1. v1.10.0 will make the nonce mandatory.
    """
    review = draft_dir / "review.md"
    if not review.is_file():
        return _gate_result(
            4, "Content Review", False,
            ["review.md absent; orchestrator must dispatch blog-reviewer agent before preflight Gate 4"],
        )
    text = review.read_text(encoding="utf-8")

    # Nonce check (v1.9.1)
    nonce_warnings: list[str] = []
    nonce_path = draft_dir / REVIEW_NONCE_FILE
    if nonce_path.is_file():
        try:
            expected_nonce = nonce_path.read_text(encoding="utf-8").strip().lower()
        except OSError as e:
            return _gate_result(
                4, "Content Review", False,
                [f"failed to read {REVIEW_NONCE_FILE}: {e}"],
            )
        if not re.fullmatch(r"[0-9a-f]{32}", expected_nonce):
            return _gate_result(
                4, "Content Review", False,
                [f"{REVIEW_NONCE_FILE} contents are not a 32-hex nonce"],
            )
        nonce_match = NONCE_PATTERN.search(text)
        if not nonce_match:
            return _gate_result(
                4, "Content Review", False,
                [
                    "review.md is missing the `Nonce: <hex>` line required for v1.9.1+ "
                    "provenance. The orchestrator must include the nonce from "
                    f"{REVIEW_NONCE_FILE} in the blog-reviewer agent's output."
                ],
            )
        actual_nonce = nonce_match.group(1).lower()
        if actual_nonce != expected_nonce:
            return _gate_result(
                4, "Content Review", False,
                [
                    "review.md Nonce does not match "
                    f"{REVIEW_NONCE_FILE}; provenance check failed (potential "
                    "review.md forgery)."
                ],
            )
    else:
        nonce_warnings.append(
            f"{REVIEW_NONCE_FILE} not found; falling back to v1.9.0 BLOCKING-only "
            "gate (deprecation: v1.10.0 will make the nonce mandatory). Run "
            "`blog_preflight.py --init-review-nonce --draft <dir>` before dispatching "
            "the blog-reviewer agent."
        )

    m = re.search(r"^BLOCKING:\s*(true|false)\s*(?:\((.*?)\))?\s*$", text, re.IGNORECASE | re.MULTILINE)
    if not m:
        return _gate_result(
            4, "Content Review", False,
            ["review.md present but no `BLOCKING: true|false` line found at end of scorecard"],
            nonce_warnings,
        )
    blocking = m.group(1).lower() == "true"
    reason = (m.group(2) or "").strip()
    if blocking:
        return _gate_result(
            4, "Content Review", False,
            [f"reviewer blocked: {reason or 'see review.md'}"],
            nonce_warnings,
            blocking=True, reason=reason,
        )
    return _gate_result(
        4, "Content Review", True, [], nonce_warnings,
        blocking=False, reason=reason,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--draft", required=True, help="Draft folder containing the .md/.html/.pdf/hero artifacts")
    parser.add_argument("--gate", type=int, choices=[1, 2, 3, 4, 5], help="Run only this gate (default: all)")
    parser.add_argument("--strict", dest="strict", action="store_true", default=True)
    parser.add_argument("--no-strict", dest="strict", action="store_false")
    parser.add_argument("--json", action="store_true", help="Emit report JSON to stdout")
    parser.add_argument(
        "--reset-iterations",
        action="store_true",
        help="Reset the per-draft iteration counter to 1 (this run counts as the first).",
    )
    parser.add_argument(
        "--init-review-nonce",
        action="store_true",
        help=(
            "Generate a fresh CSPRNG nonce and write it to <draft>/.review-nonce, "
            "then exit. The orchestrator runs this before dispatching the "
            "blog-reviewer agent; Gate 4 verifies the agent's review.md contains "
            "the matching nonce (VULN-803, v1.9.1)."
        ),
    )
    args = parser.parse_args()

    draft = Path(args.draft).resolve()
    if not draft.is_dir():
        print(f"ERROR: {draft} is not a directory", file=sys.stderr)
        return 1

    if args.init_review_nonce:
        nonce = _init_review_nonce(draft)
        print(nonce)
        return 0

    # VULN-802 (v1.9.1): code-enforced iteration cap. Refuse past MAX_ITERATIONS.
    iteration_exit = _iteration_check(draft, reset=args.reset_iterations)
    if iteration_exit != 0:
        return iteration_exit

    gates = [
        (1, gate_1_capability_discovery),
        (2, gate_2_format_completeness),
        (3, gate_3_visual_verification),
        (4, gate_4_content_review),
        (5, gate_5_asset_link_integrity),
    ]
    if args.gate:
        gates = [(n, fn) for (n, fn) in gates if n == args.gate]

    results: list[dict] = []
    blocked = False
    for n, fn in gates:
        r = fn(draft)
        results.append(r)
        if not r["passed"]:
            blocked = True

    report = {
        "draft": str(draft),
        "strict": args.strict,
        "blocked": blocked,
        "gates": results,
    }
    (draft / "preflight-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(report))
    else:
        for r in results:
            mark = "PASS" if r["passed"] else "FAIL"
            print(f"[{mark}] Gate {r['gate']}: {r['name']}")
            for v in r.get("violations", []):
                print(f"       violation: {v}")
            for w in r.get("warnings", []):
                print(f"       warning:   {w}")
        if blocked and not args.strict:
            print("WARNING: contract bypassed via --no-strict; do not publish without manual review.", file=sys.stderr)

    if blocked and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
