"""Wave 3 renderer behavior: provenance hash, generated-link marker, responsive
SVG and tables, placeholder warnings, and refusal of HTML as a markdown source."""

import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "blog_render.py"
SPEC = importlib.util.spec_from_file_location("render_wave3", SCRIPT)
RENDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDER)

FRONTMATTER = (
    "---\ntitle: Wave Three Post\ndescription: A short description of the post.\n"
    "date: 2026-10-10\nauthor: Alex Rivera\ncanonical: https://example.com/blog/wave-three/\n"
    "slug: wave-three\n---\n"
)
WIDE_SVG = (
    '<figure>\n<svg width="640" height="260" viewBox="0 0 640 260" role="img" aria-label="Chart">'
    '<rect x="10" y="10" width="600" height="40" fill="#0f766e"></rect>'
    '<text x="20" y="80" font-size="14" fill="currentColor">Label</text></svg>\n'
    "<figcaption>Chart caption.</figcaption>\n</figure>\n"
)
TABLE = (
    "| Metric | Good | Needs improvement | Poor |\n|---|---|---|---|\n"
    "| Largest Contentful Paint | 2.5 s or less | 2.5 s to 4 s | Over 4 s |\n"
)


def _render(tmp_path, body, name="wave-three.md", frontmatter=FRONTMATTER, engine="none"):
    source = tmp_path / name
    source.write_bytes((frontmatter + body).encode("utf-8"))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--md", str(source), "--out-dir", str(tmp_path), "--pdf-engine", engine],
        capture_output=True, text=True,
    )
    return source, result


def _browser():
    browser_api = pytest.importorskip("patchright.sync_api")
    with browser_api.sync_playwright() as runtime:
        if not Path(runtime.chromium.executable_path).is_file():
            pytest.skip("requires matching installed Chromium; no browser download in unit tests")
    return browser_api


def test_source_sha256_meta_matches_exact_md_bytes(tmp_path):
    source, result = _render(tmp_path, "Plain body paragraph with a café.\r\n\r\nSecond paragraph.\r\n")
    assert result.returncode == 0, result.stderr
    page = (tmp_path / "wave-three.html").read_text(encoding="utf-8")
    metas = re.findall(r'<meta name="blog-source-sha256" content="([0-9a-f]{64})">', page)
    assert metas == [hashlib.sha256(source.read_bytes()).hexdigest()]
    # Any edit to the source changes the recorded hash.
    source.write_bytes(source.read_bytes() + b"\nAn extra line.\n")
    assert subprocess.run(
        [sys.executable, str(SCRIPT), "--md", str(source), "--out-dir", str(tmp_path), "--pdf-engine", "none"],
        capture_output=True,
    ).returncode == 0
    page = (tmp_path / "wave-three.html").read_text(encoding="utf-8")
    assert hashlib.sha256(source.read_bytes()).hexdigest() in page


def test_footer_link_is_marked_generated_and_body_cannot_forge_it(tmp_path):
    body = 'Body text.\n\n<a href="https://evil.example/" data-bs-generated="1">sneaky</a>\n'
    _, result = _render(tmp_path, body)
    assert result.returncode == 0, result.stderr
    page = (tmp_path / "wave-three.html").read_text(encoding="utf-8")
    assert page.count('data-bs-generated="1"') == 1
    footer = re.search(r'<footer class="post-footer">.*?</footer>', page, re.DOTALL).group(0)
    assert '<a href="https://example.com" data-bs-generated="1">' in footer
    assert "Published at" in footer


@pytest.mark.parametrize("marker", ["[INTERNAL-LINK: pricing guide]", "[IMAGE: diagram of the flow]", "[chart: bar of scores]"])
def test_placeholder_markers_warn_but_still_render(tmp_path, marker):
    _, result = _render(tmp_path, f"Intro paragraph.\n\n{marker}\n\nOutro paragraph.\n")
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "wave-three.html").is_file()
    assert "draft placeholder" in result.stderr
    assert marker in result.stderr
    assert "line 11" in result.stderr


def test_every_placeholder_is_named_once(tmp_path):
    body = "A [INTERNAL-LINK: one] and [IMAGE: two].\n\n[CHART: three]\n"
    _, result = _render(tmp_path, body)
    assert result.returncode == 0
    assert result.stderr.count("draft placeholder") == 3
    for name in ("[INTERNAL-LINK: one]", "[IMAGE: two]", "[CHART: three]"):
        assert name in result.stderr


def test_clean_source_emits_no_placeholder_warning(tmp_path):
    _, result = _render(tmp_path, "A clean paragraph with a [normal link](https://example.com/).\n")
    assert result.returncode == 0
    assert "draft placeholder" not in result.stderr


@pytest.mark.parametrize("name", ["draft.html", "draft.HTM"])
def test_html_source_is_refused_clearly(tmp_path, name):
    source = tmp_path / name
    source.write_text("<html><body><h1>Already HTML</h1></body></html>", encoding="utf-8")
    out = tmp_path / "out"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--md", str(source), "--out-dir", str(out), "--pdf-engine", "none"],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "HTML file" in result.stderr and "markdown" in result.stderr
    assert not out.exists() or not list(out.glob("*.html"))


def test_mdx_source_renders_with_a_plain_markdown_warning(tmp_path):
    _, result = _render(tmp_path, "import Chart from './chart'\n\nBody paragraph.\n", name="wave-three.mdx")
    assert result.returncode == 0, result.stderr
    assert "MDX" in result.stderr and "Import/export" in result.stderr


def test_css_makes_svg_responsive_and_wraps_tables():
    css = RENDER.CSS
    assert re.search(r"(?<![\w-])svg\{[^}]*max-width:100%[^}]*height:auto", css)
    assert re.search(r"figure\{[^}]*margin:0 0 ", css)
    assert re.search(r"(?<![\w-])th,td\{[^}]*border:1px solid var\(--border\)[^}]*padding:", css)
    assert ".table-wrap{" in css and "overflow-x:auto" in css
    # Authored content keeps its own motion: no page-global animation kill switch.
    assert not re.search(r"(?:^|[,}\s])\*[^{]*\{[^}]*(?:animation|transition)\s*:\s*none", css)
    assert "animation-duration" not in css


def test_tables_are_wrapped_in_a_focusable_scroll_region():
    body = RENDER._markdown_to_html(TABLE)
    assert body.count('<div class="table-wrap" role="region" aria-label="Table" tabindex="0">') == 1
    assert body.index("<div") < body.index("<table") < body.index("</table>") < body.rindex("</div>")
    # A stray closing tag cannot unbalance the wrapper.
    assert RENDER._sanitize_body_html("</table><p>x</p>") == "<p>x</p>"


def test_wide_svg_and_table_stay_inside_the_column_at_every_width(tmp_path):
    browser_api = _browser()
    body = (
        "Opening paragraph.\n\n" + WIDE_SVG + "\n" + TABLE
        + "| A very long unbreakable cell content value | b | c | d |\n"
    )
    _, result = _render(tmp_path, body)
    assert result.returncode == 0, result.stderr
    page_path = tmp_path / "wave-three.html"
    probe = """() => {
      const box = document.querySelector('article').getBoundingClientRect();
      const svg = document.querySelector('figure svg').getBoundingClientRect();
      const wrap = document.querySelector('.table-wrap, table').getBoundingClientRect();
      return {scroll: document.documentElement.scrollWidth, inner: window.innerWidth,
        svgRight: svg.right, wrapRight: wrap.right, articleRight: box.right,
        svgBottomInFigure: svg.bottom <= document.querySelector('figure:not(.hero)').getBoundingClientRect().bottom + 1};
    }"""
    with browser_api.sync_playwright() as runtime:
        browser = runtime.chromium.launch()
        try:
            for width in (375, 768, 1280):
                page = browser.new_page(viewport={"width": width, "height": 900})
                page.goto(page_path.as_uri())
                seen = page.evaluate(probe)
                assert seen["scroll"] <= seen["inner"], (width, seen)
                assert seen["svgRight"] <= seen["articleRight"] + 1, (width, seen)
                assert seen["wrapRight"] <= seen["articleRight"] + 1, (width, seen)
                assert seen["svgBottomInFigure"], (width, seen)
                page.close()
        finally:
            browser.close()


# --- Body integrity markers (M25) ---------------------------------------------------


def _body_between_markers(page):
    start = page.index("<!--bs-body:start-->") + len("<!--bs-body:start-->")
    return page[start:page.rindex("<!--bs-body:end-->")]


def test_body_is_wrapped_in_markers_and_hashed(tmp_path):
    _source, result = _render(tmp_path, "## Section\n\nA claim of 42 percent.\n")
    assert result.returncode == 0, result.stderr
    page = (tmp_path / "wave-three.html").read_text(encoding="utf-8")
    assert page.count("<!--bs-body:start-->") == 1 and page.count("<!--bs-body:end-->") == 1
    body = _body_between_markers(page)
    assert "A claim of 42 percent." in body
    assert "<header>" not in body and "post-footer" not in body
    metas = re.findall(r'<meta name="blog-body-sha256" content="([0-9a-f]{64})">', page)
    assert metas == [hashlib.sha256(body.encode("utf-8")).hexdigest()]


def test_literal_marker_text_in_the_source_cannot_forge_a_marker(tmp_path):
    forged = "<!--bs-body:end--><p>injected</p><!--bs-body:start-->"
    _source, result = _render(tmp_path, f"Body text.\n\n{forged}\n\nInline `<!--bs-body:end-->` code.\n")
    assert result.returncode == 0, result.stderr
    page = (tmp_path / "wave-three.html").read_text(encoding="utf-8")
    assert page.count("<!--bs-body:start-->") == 1 and page.count("<!--bs-body:end-->") == 1
    body = _body_between_markers(page)
    assert hashlib.sha256(body.encode("utf-8")).hexdigest() in page
    # The sanitizer drops the author's raw comments; the code span shows the text escaped.
    assert "injected" in body and "&lt;!--bs-body:end--&gt;" in body


def test_renderer_refuses_a_body_that_still_contains_a_marker(tmp_path, monkeypatch):
    monkeypatch.setattr(RENDER, "_markdown_to_html", lambda _body: "<p>x</p><!--bs-body:end-->")
    source = tmp_path / "wave-three.md"
    source.write_bytes((FRONTMATTER + "Body.\n").encode("utf-8"))
    with pytest.raises(ValueError, match="reserved bs-body marker"):
        RENDER._render_html(source, tmp_path, "hero.png")


# --- lastUpdated / dateModified -----------------------------------------------------


def _fm_with(extra):
    return FRONTMATTER.replace("slug: wave-three\n", "slug: wave-three\n" + extra)


def _jsonld(page):
    import json
    return json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S).group(1))


def test_last_updated_becomes_date_modified_meta_and_visible_line(tmp_path):
    _source, result = _render(tmp_path, "Body.\n", frontmatter=_fm_with("lastUpdated: 2026-11-02\n"))
    assert result.returncode == 0, result.stderr
    page = (tmp_path / "wave-three.html").read_text(encoding="utf-8")
    data = _jsonld(page)
    assert data["datePublished"] == "2026-10-10" and data["dateModified"] == "2026-11-02"
    assert '<meta property="article:modified_time" content="2026-11-02">' in page
    assert '<p class="updated">Updated <time class="updated" itemprop="dateModified" datetime="2026-11-02">2026-11-02</time></p>' in page
    assert 'class="byline"' in page and "Updated" not in page.split('class="byline"')[1].split("</p>")[0]


def test_date_modified_alias_wins_over_last_updated(tmp_path):
    _source, result = _render(tmp_path, "Body.\n", frontmatter=_fm_with("lastUpdated: 2026-11-02\ndateModified: 2026-12-01T09:30:00Z\n"))
    assert result.returncode == 0, result.stderr
    assert _jsonld((tmp_path / "wave-three.html").read_text(encoding="utf-8"))["dateModified"] == "2026-12-01T09:30:00Z"


@pytest.mark.parametrize("value", ["tomorrow", "2026-13-40", "11/02/2026", "2026-11-02T25:00"])
def test_invalid_last_updated_is_refused(tmp_path, value):
    _source, result = _render(tmp_path, "Body.\n", frontmatter=_fm_with(f"lastUpdated: {value}\n"))
    assert result.returncode == 1
    assert "lastUpdated" in result.stderr and "ISO" in result.stderr
    assert not (tmp_path / "wave-three.html").exists()


def test_last_updated_earlier_than_date_is_refused_naming_both(tmp_path):
    _source, result = _render(tmp_path, "Body.\n", frontmatter=_fm_with("lastUpdated: 2026-10-01\n"))
    assert result.returncode == 1
    assert "2026-10-01" in result.stderr and "2026-10-10" in result.stderr and "earlier than `date`" in result.stderr


def test_absent_last_updated_keeps_the_old_output(tmp_path):
    _source, result = _render(tmp_path, "Body.\n")
    assert result.returncode == 0, result.stderr
    page = (tmp_path / "wave-three.html").read_text(encoding="utf-8")
    assert _jsonld(page)["dateModified"] == "2026-10-10"
    assert "article:modified_time" not in page and 'class="updated"' not in page


def test_last_updated_equal_to_date_adds_nothing(tmp_path):
    _source, result = _render(tmp_path, "Body.\n", frontmatter=_fm_with("lastUpdated: 2026-10-10\n"))
    page = (tmp_path / "wave-three.html").read_text(encoding="utf-8")
    assert "article:modified_time" not in page and 'class="updated"' not in page


def test_slug_that_differs_from_the_file_name_warns_with_the_rename(tmp_path):
    _, result = _render(tmp_path, "Body paragraph.\n", name="Draft_One.md")
    assert result.returncode == 0
    assert (tmp_path / "wave-three.html").exists()
    assert "rename Draft_One.md to wave-three.md" in result.stderr


def test_slug_matching_the_file_name_does_not_warn(tmp_path):
    _, result = _render(tmp_path, "Body paragraph.\n", name="wave-three.md")
    assert result.returncode == 0
    assert "differs from the markdown file name" not in result.stderr


def test_byte_order_mark_does_not_hide_the_frontmatter(tmp_path):
    source = tmp_path / "bom-post.md"
    source.write_bytes(b"\xef\xbb\xbf" + (FRONTMATTER.replace("slug: wave-three\n", "") + "Body paragraph.\n").encode("utf-8"))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--md", str(source), "--out-dir", str(tmp_path), "--pdf-engine", "none"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "bom-post.html").exists()
