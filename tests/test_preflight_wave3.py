"""Wave 3 gate regressions: stale reviews, static artifact checks, link and message quality.

Every mutation test copies one correct article (tests/fixtures/golden_draft,
a draft that passes all five strict gates), breaks exactly one thing and
asserts the specific message, so each check is proven against the unmutated
draft. Drafts and their HTML are treated as untrusted input.
"""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import shutil
import sys
import time
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "golden_draft"
SLUG = "core-web-vitals-thresholds"

MINIMAL_PDF = (
    b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]>>endobj\n"
    b"trailer<</Root 1 0 R>>\n%%EOF\n"
)


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def preflight():
    return _load("wave3_preflight", "blog_preflight.py")


@pytest.fixture(scope="module")
def renderer():
    return _load("wave3_renderer", "blog_render.py")


@pytest.fixture(scope="module")
def rendered_template(tmp_path_factory, renderer):
    """Render the golden article once; every test copies the result."""
    template = tmp_path_factory.mktemp("wave3-template")
    shutil.copytree(FIXTURE, template, dirs_exist_ok=True)
    renderer._render_html(template / f"{SLUG}.md", template, "hero.webp")
    (template / f"{SLUG}.pdf").write_bytes(MINIMAL_PDF)
    return template


@pytest.fixture
def draft(rendered_template, tmp_path):
    target = tmp_path / "draft"
    shutil.copytree(rendered_template, target)
    return target


@pytest.fixture(autouse=True)
def offline_probes(preflight, monkeypatch, tmp_path):
    """No real network and a private review-state directory for every test."""
    monkeypatch.setenv("CLAUDE_BLOG_REVIEW_STATE_DIR", str(tmp_path / "review-state"))
    monkeypatch.setattr(preflight, "_safe_http_url", lambda _url: (True, None))
    monkeypatch.setattr(preflight, "_http_head", lambda _url: 200)


def _edit(path: Path, old: str, new: str, count: int = 1) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, f"fixture no longer contains {old!r}"
    path.write_text(text.replace(old, new, count), encoding="utf-8")


def _html(draft: Path) -> Path:
    return draft / f"{SLUG}.html"


def _gate2(preflight, draft):
    return preflight.gate_2_format_completeness(draft, SLUG)


def _gate5(preflight, draft):
    return preflight.gate_5_asset_link_integrity(draft, SLUG)


def _has(result, *needles):
    return any(all(n in item for n in needles) for item in result["violations"])


def _review(nonce: str) -> str:
    return (
        "## Quality Review\n\n### Overall Score: 92/100\n\nzero P0 issues found\n\n"
        f"Nonce: {nonce}\nBLOCKING: false (cleared all gates)\n"
    )


# --- The unmutated draft passes ---------------------------------------------


def test_unmutated_draft_passes_gates_2_and_5(preflight, draft):
    assert _gate2(preflight, draft)["passed"], _gate2(preflight, draft)["violations"]
    result = _gate5(preflight, draft)
    assert result["passed"], result["violations"]


def test_gate_2_reports_hero_and_pdf_evidence(preflight, draft):
    result = _gate2(preflight, draft)
    hero = result["hero_checks"][0]
    assert (hero["format"], hero["width"], hero["height"]) == ("WEBP", 1200, 630)
    assert result["pdf_check"]["pages"] == 1
    assert result["artifacts"]["slug"] == SLUG


# --- Gate 4: digests stored at init, stale review is a violation --------------


def _issue_review(preflight, draft):
    nonce = preflight._init_review_nonce(draft)
    (draft / "review.md").write_text(_review(nonce), encoding="utf-8")
    return nonce


def test_gate_4_state_keeps_old_fields_and_adds_per_file_digests(preflight, draft):
    nonce = _issue_review(preflight, draft)
    state = json.loads(preflight._review_state_path(draft).read_text(encoding="utf-8"))
    assert state["nonce"] == nonce and state["draft_digest"] and "created_at" in state
    digests = state["artifact_digests"]
    assert set(digests) == {f"{SLUG}.md", f"{SLUG}.html", f"{SLUG}.pdf", "hero.webp"}
    assert digests[f"{SLUG}.md"] == hashlib.sha256((draft / f"{SLUG}.md").read_bytes()).hexdigest()
    assert preflight.gate_4_content_review(draft)["passed"]


@pytest.mark.parametrize("name", [f"{SLUG}.md", f"{SLUG}.html", f"{SLUG}.pdf", "hero.webp"])
def test_gate_4_blocks_when_any_reviewed_artifact_changes(preflight, draft, name):
    _issue_review(preflight, draft)
    target = draft / name
    target.write_bytes(target.read_bytes() + b"\n ")
    result = preflight.gate_4_content_review(draft)
    assert not result["passed"]
    assert _has(result, "draft changed after the review nonce was issued", name,
                "re-render, re-init the nonce and re-review")
    assert result["stale_artifacts"] == [name]


def test_gate_4_blocks_when_a_reviewed_artifact_is_removed(preflight, draft):
    _issue_review(preflight, draft)
    (draft / "hero.webp").unlink()
    result = preflight.gate_4_content_review(draft)
    assert not result["passed"]
    assert _has(result, "hero.webp", "file removed")


def test_gate_4_old_state_with_only_the_aggregate_digest_keeps_the_warning(preflight, draft):
    nonce = "b" * 32
    preflight._atomic_write_json(
        preflight._review_state_path(draft),
        {"draft": str(draft), "nonce": nonce, "draft_digest": preflight._draft_digest(draft), "version": "old"},
    )
    (draft / "review.md").write_text(_review(nonce), encoding="utf-8")
    assert preflight.gate_4_content_review(draft)["passed"]
    _edit(_html(draft), "<body", "<body data-x=1")
    result = preflight.gate_4_content_review(draft)
    assert result["passed"]
    assert any("may be stale" in item for item in result["warnings"])


def test_gate_4_unchanged_draft_passes_after_gates_write_their_own_files(preflight, draft):
    _issue_review(preflight, draft)
    (draft / "capabilities.json").write_text("{}", encoding="utf-8")
    (draft / "preflight-report.json").write_text("{}", encoding="utf-8")
    (draft / "preview").mkdir()
    (draft / "preview" / "mobile-375.png").write_bytes(b"x")
    assert preflight.gate_4_content_review(draft)["passed"]


# --- Gate 2: placeholders ------------------------------------------------------


@pytest.mark.parametrize("marker", ["[INTERNAL-LINK: related guide]", "[IMAGE: hero shot]", "[chart: cwv ranges]"])
def test_gate_2_blocks_placeholders_in_the_source(preflight, draft, marker):
    _edit(draft / f"{SLUG}.md", "## Key takeaways", f"{marker}\n\n## Key takeaways")
    result = _gate2(preflight, draft)
    assert not result["passed"]
    assert _has(result, "draft placeholder", marker.split(":")[0], f"{SLUG}.md line", "re-render")


def test_gate_2_blocks_placeholders_in_the_html(preflight, draft):
    _edit(_html(draft), "<h1>", "<p>[IMAGE: left over]</p><h1>")
    result = _gate2(preflight, draft)
    assert _has(result, "draft placeholder [IMAGE: left over]", f"{SLUG}.html line")


# --- Gate 2: filenames ---------------------------------------------------------


def test_gate_2_blocks_a_non_slug_artifact_name(preflight, draft):
    for suffix in ("md", "html", "pdf"):
        (draft / f"{SLUG}.{suffix}").rename(draft / f"My_Post.{suffix}")
    result = preflight.gate_2_format_completeness(draft, "My_Post")
    assert _has(result, "'My_Post' is not lowercase slug style", "my-post.*")


def test_gate_2_blocks_an_uppercase_hero_name(preflight, draft):
    (draft / "hero.webp").rename(draft / "hero.WEBP")
    result = _gate2(preflight, draft)
    assert _has(result, "hero filename 'hero.WEBP' must be lowercase", "hero.webp")


def test_gate_2_blocks_a_non_slug_local_image_name(preflight, draft):
    _edit(_html(draft), "</article>", '<img src="related/Bad_Name.PNG" alt="x"></article>')
    result = _gate2(preflight, draft)
    assert _has(result, "image filename is not lowercase slug style", "bad-name.png")


# --- Gate 2: hero decode -------------------------------------------------------


def test_gate_2_blocks_a_hero_that_is_not_an_image(preflight, draft):
    (draft / "hero.webp").write_bytes(b"this is not an image at all" * 20)
    result = _gate2(preflight, draft)
    assert _has(result, "hero.webp is not a valid image", "not a PNG, JPEG or WebP image")


def test_gate_2_blocks_a_hero_whose_format_differs_from_its_extension(preflight, draft):
    (draft / "hero.webp").rename(draft / "hero.png")
    result = _gate2(preflight, draft)
    assert _has(result, "hero.png holds WEBP data but its extension says PNG", "rename it to hero.webp")


def test_gate_2_blocks_a_hero_below_the_contract_size(preflight, draft):
    PIL = pytest.importorskip("PIL.Image")
    buffer = io.BytesIO()
    PIL.new("RGB", (800, 400), "teal").save(buffer, "PNG")
    (draft / "hero.webp").unlink()
    (draft / "hero.png").write_bytes(buffer.getvalue())
    result = _gate2(preflight, draft)
    assert _has(result, "hero.png is 800x400", "at least 1200x630")


@pytest.mark.parametrize("cut", [0.5, 0.9])
def test_gate_2_blocks_a_truncated_hero(preflight, draft, cut):
    data = (draft / "hero.webp").read_bytes()
    (draft / "hero.webp").write_bytes(data[: int(len(data) * cut)])
    result = _gate2(preflight, draft)
    assert not result["passed"] and _has(result, "hero.webp is not a valid image")


def test_gate_2_header_only_decode_is_used_and_disclosed_without_pillow(preflight, draft, monkeypatch):
    monkeypatch.setattr(preflight, "_pillow_decode", lambda _data: None)
    result = _gate2(preflight, draft)
    assert result["passed"], result["violations"]
    assert result["hero_checks"][0]["decoder"] == "header"
    assert any("Pillow is not installed" in item for item in result["warnings"])
    (draft / "hero.webp").write_bytes((draft / "hero.webp").read_bytes()[:200])
    assert _has(_gate2(preflight, draft), "hero.webp is not a valid image")


@pytest.mark.parametrize("fmt,suffix,options", [
    ("PNG", ".png", {}), ("JPEG", ".jpg", {}), ("WEBP", ".webp", {}), ("WEBP", ".webp", {"lossless": True}),
])
def test_raster_header_parser_agrees_with_pillow(preflight, fmt, suffix, options):
    PIL = pytest.importorskip("PIL.Image")
    buffer = io.BytesIO()
    PIL.new("RGB", (1234, 567), "navy").save(buffer, fmt, **options)
    info = preflight._raster_info(buffer.getvalue())
    assert (info["format"], info["width"], info["height"]) == (fmt, 1234, 567)
    assert "error" not in info


# --- Gate 2: PDF ---------------------------------------------------------------


def test_gate_2_blocks_a_pdf_that_is_not_a_pdf(preflight, draft):
    (draft / f"{SLUG}.pdf").write_bytes(b"<html>oops</html>")
    assert _has(_gate2(preflight, draft), f"{SLUG}.pdf does not start with %PDF")


def test_gate_2_blocks_a_pdf_with_no_pages(preflight, draft):
    (draft / f"{SLUG}.pdf").write_bytes(b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\n%%EOF\n")
    assert _has(_gate2(preflight, draft), f"{SLUG}.pdf has no pages")


def test_gate_2_blocks_a_truncated_pdf(preflight, draft):
    (draft / f"{SLUG}.pdf").write_bytes(MINIMAL_PDF.replace(b"%%EOF\n", b""))
    assert _has(_gate2(preflight, draft), f"{SLUG}.pdf is truncated", "%%EOF")


def test_pdf_page_count_reads_pages_inside_compressed_object_streams(preflight):
    inner = b"<</Type /Page /Parent 2 0 R>>"
    packed = zlib.compress(inner)
    data = b"%PDF-1.5\n4 0 obj<</Type/ObjStm/Filter/FlateDecode>>stream\n" + packed + b"\nendstream endobj\n%%EOF"
    assert preflight._pdf_page_count(data) == 1


# --- Gate 2: renderer source hash ---------------------------------------------


def test_gate_2_blocks_html_without_the_source_hash_meta(preflight, draft):
    text = _html(draft).read_text(encoding="utf-8")
    start = text.index('<meta name="blog-source-sha256"')
    _html(draft).write_text(text[:start] + text[text.index(">", start) + 1:], encoding="utf-8")
    result = _gate2(preflight, draft)
    assert _has(result, f'{SLUG}.html has no <meta name="blog-source-sha256">', "blog_render.py")


def test_gate_2_blocks_html_rendered_from_different_source_bytes(preflight, draft):
    (draft / f"{SLUG}.md").write_bytes((draft / f"{SLUG}.md").read_bytes() + b"\nAn edit after rendering.\n")
    result = _gate2(preflight, draft)
    assert _has(result, "rendered from different source bytes", "sha256 of", f"{SLUG}.md", "blog_render.py")


def test_source_hash_uses_raw_bytes_not_decoded_text(preflight, draft, renderer):
    # CRLF line endings change the bytes, so a render of the LF file must not match them.
    source = draft / f"{SLUG}.md"
    source.write_bytes(source.read_bytes().replace(b"\n", b"\r\n"))
    assert _has(_gate2(preflight, draft), "rendered from different source bytes")
    renderer._render_html(source, draft, "hero.webp")
    assert _gate2(preflight, draft)["passed"]


# --- Gate 2: active content ----------------------------------------------------


ACTIVE_CASES = {
    "script": ("<h1>", '<script src="x.js"></script><h1>', ["<script", "x.js", "only script allowed"]),
    "inline-script": ("<h1>", "<script>alert(1)</script><h1>", ["<script> element"]),
    "onclick": ("<h1>", '<h1 onclick="go()">', ["inline event handler onclick", "<h1>"]),
    "javascript-href": ("</article>", '<a href=" JaVa\tScript:alert(1)">x</a></article>', ["javascript: URL", "href"]),
    "iframe": ("</article>", '<iframe src="https://e.example/"></iframe></article>', ["<iframe", "not allowed"]),
    "object": ("</article>", '<object data="a.swf"></object></article>', ["<object"]),
    "embed": ("</article>", '<embed src="a.swf"></article>', ["<embed"]),
    "frame": ("</article>", '<frame src="a.html"></article>', ["<frame"]),
    "svg-script": ("<svg ", "<svg id=\"x\" ", None),
}


@pytest.mark.parametrize("name", [n for n in ACTIVE_CASES if n != "svg-script"])
def test_gate_2_blocks_active_content(preflight, draft, name):
    old, new, needles = ACTIVE_CASES[name]
    _edit(_html(draft), old, new)
    result = _gate2(preflight, draft)
    assert not result["passed"]
    assert _has(result, "active content in", *needles), result["violations"]


def test_gate_2_blocks_script_inside_inline_svg_and_names_the_svg(preflight, draft):
    _edit(_html(draft), "</svg>", '<script>steal()</script></svg>')
    result = _gate2(preflight, draft)
    assert _has(result, "<script> element inside inline SVG", "<svg>")


def test_gate_2_blocks_event_handler_inside_inline_svg(preflight, draft):
    _edit(_html(draft), "</svg>", '<rect id="r1" width="1" height="1" onload="x()"/></svg>')
    result = _gate2(preflight, draft)
    assert _has(result, "onload", "<rect#r1>", "inside inline SVG")


def test_gate_2_blocks_svg_animation_that_targets_a_javascript_url(preflight, draft):
    _edit(_html(draft), "</svg>", '<a><set attributeName="href" to="javascript:alert(1)"/></a></svg>')
    assert _has(_gate2(preflight, draft), "javascript: URL", 'to="javascript:alert(1)"')


def test_gate_2_allows_json_ld_and_the_renderer_table_wrapper(preflight, draft):
    wrapper = '<div class="table-wrap" role="region" aria-label="Table" tabindex="0"><table><tr><td>1</td></tr></table></div></article>'
    _edit(_html(draft), "</article>", wrapper)
    result = _gate2(preflight, draft)
    assert result["passed"], result["violations"]


def test_gate_2_active_content_reports_are_capped(preflight, draft):
    _edit(_html(draft), "</article>", "".join(f'<p onclick="a{i}()">x</p>' for i in range(12)) + "</article>")
    result = _gate2(preflight, draft)
    assert sum("inline event handler" in v for v in result["violations"]) == preflight.REPORT_LIMIT
    assert _has(result, "... and 7 more")


# --- Gate 2: document structure ------------------------------------------------


STRUCTURE_CASES = {
    "no-lang": ('<html lang="en">', "<html>", ["<html> has no lang attribute", 'lang="en"']),
    "no-title": (f"<title>Core Web Vitals Thresholds Explained</title>", "", ["<title> is missing or empty"]),
    "no-description": (None, None, ["<meta name=\"description\"> is missing or empty", "70 to 165"]),
    "no-h1": ("<h1>", "<h2>", ["no <h1> in the document"]),
    "two-h1": ("<h2", "<h1", ["<h1> elements found", "demote"]),
    "heading-skip": ("<h3", "<h5", ["heading level skips from <h2> to <h5>", "use <h3>"]),
    "no-og-title": ('<meta property="og:title"', '<meta property="x:title"', ['<meta property="og:title"', "missing or empty"]),
    "no-og-description": ('<meta property="og:description"', '<meta property="x:description"', ['"og:description"']),
    "no-og-image": ('<meta property="og:image" ', '<meta property="x:image" ', ['"og:image"']),
    "noindex": ('content="index, follow, max-image-preview:large"', 'content="noindex, nofollow"', ["blocks indexing", "noindex"]),
    "no-alt": (' alt="', ' data-alt="', ["has no alt attribute", "<img"]),
}


@pytest.mark.parametrize("name", sorted(STRUCTURE_CASES))
def test_gate_2_structure_violations(preflight, draft, name):
    old, new, needles = STRUCTURE_CASES[name]
    text = _html(draft).read_text(encoding="utf-8")
    if name == "no-description":
        import re
        text = re.sub(r'<meta name="description" content="[^"]*">', "", text, count=1)
    elif name == "no-h1":
        text = text.replace("</h1>", "</h2>", 1).replace(old, new, 1)
    elif name == "no-title":
        import re
        text = re.sub(r"<title>.*?</title>", "", text, count=1)
    elif name == "two-h1":
        text = text.replace(old, new, 1).replace("</h2>", "</h1>", 1)
    elif name == "heading-skip":
        assert "<h3" in text, "fixture needs an h3 for this case"
        text = text.replace(old, new, 1).replace("</h3>", "</h5>", 1)
    else:
        assert old in text, old
        text = text.replace(old, new, 1)
    _html(draft).write_text(text, encoding="utf-8")
    result = _gate2(preflight, draft)
    assert not result["passed"]
    assert _has(result, *needles), result["violations"]


def test_gate_2_warns_on_description_length_and_empty_alt(preflight, draft):
    import re
    text = _html(draft).read_text(encoding="utf-8")
    text = re.sub(r'(<meta name="description" content=")[^"]*(">)', r"\1Too short\2", text, count=1)
    text = text.replace("</article>", '<img src="hero.webp" alt=""></article>', 1)
    _html(draft).write_text(text, encoding="utf-8")
    result = _gate2(preflight, draft)
    assert result["passed"], result["violations"]
    assert any("is 9 characters; aim for 70 to 165" in w for w in result["warnings"])
    assert any("empty alt text" in w and "role=\"presentation\"" in w for w in result["warnings"])


@pytest.mark.parametrize("attrs", [' role="presentation"', ' aria-hidden="true"'])
def test_gate_2_accepts_empty_alt_for_decorative_images(preflight, draft, attrs):
    _edit(_html(draft), "</article>", f'<img src="hero.webp" alt=""{attrs}></article>')
    result = _gate2(preflight, draft)
    assert result["passed"], result["violations"]
    assert not any("empty alt" in w for w in result["warnings"])


# --- Gate 5: links ---------------------------------------------------------------


def test_gate_5_does_not_fetch_the_renderer_footer_link(preflight, draft, monkeypatch):
    fetched = []
    monkeypatch.setattr(preflight, "_http_head", lambda url: fetched.append(url) or 200)
    result = _gate5(preflight, draft)
    assert result["passed"]
    assert result["generated_links_skipped"] == 1
    assert "https://example.com" not in fetched
    assert "https://web.dev/articles/lcp" in fetched


def test_gate_5_still_fetches_a_flagged_link_outside_the_footer(preflight, draft, monkeypatch):
    fetched = []
    monkeypatch.setattr(preflight, "_http_head", lambda url: fetched.append(url) or 200)
    _edit(_html(draft), "</article>", '<a href="https://forged.example/x" data-bs-generated="1">x</a></article>')
    _gate5(preflight, draft)
    assert "https://forged.example/x" in fetched


def test_gate_5_validates_the_scheme_of_a_generated_footer_link(preflight, draft):
    _edit(_html(draft), 'href="https://example.com" data-bs-generated="1"',
          'href="javascript:alert(1)" data-bs-generated="1"')
    result = _gate5(preflight, draft)
    assert _has(result, "non-http(s) URL scheme", "javascript:alert(1)")


def test_gate_5_refuses_a_generated_link_to_a_private_address_literal(preflight, draft):
    _edit(_html(draft), 'href="https://example.com" data-bs-generated="1"',
          'href="http://10.0.0.5/" data-bs-generated="1"')
    result = _gate5(preflight, draft)
    assert _has(result, "link refused by URL safety policy", "http://10.0.0.5/", "not public")


def test_gate_5_names_network_failures_and_how_to_tell(preflight, draft, monkeypatch):
    def failing_head(url):
        preflight._HTTP_FAILURE_REASONS[url] = "DNS lookup failed"
        return 0
    monkeypatch.setattr(preflight, "_http_head", failing_head)
    result = _gate5(preflight, draft)
    assert _has(result, "could not be checked (DNS lookup failed)", "network or DNS problem", "curl -I")
    assert any("failed at the network level" in w for w in result["warnings"])


def test_gate_5_dns_failure_before_fetch_is_labeled_as_possibly_network(preflight, draft, monkeypatch):
    monkeypatch.setattr(preflight, "_safe_http_url", lambda _url: (False, "DNS resolution failed: [Errno -3]"))
    result = _gate5(preflight, draft)
    assert _has(result, "could not be resolved", "DNS resolution failed", "network or DNS problem")
    assert not _has(result, "refused by URL safety policy")


def test_gate_5_non_public_address_is_still_a_policy_refusal(preflight, draft, monkeypatch):
    monkeypatch.setattr(preflight, "_safe_http_url", lambda _url: (False, "resolved address is not public: 10.0.0.1"))
    result = _gate5(preflight, draft)
    assert _has(result, "link refused by URL safety policy", "not public")
    assert not any("network or DNS" in item for item in result["violations"])


def test_gate_5_http_error_is_not_called_a_network_problem(preflight, draft, monkeypatch):
    monkeypatch.setattr(preflight, "_http_head", lambda _url: 404)
    result = _gate5(preflight, draft)
    assert _has(result, "link returned 404")
    assert not any("network or DNS" in item for item in result["violations"])


def test_http_probe_records_why_a_request_failed(preflight, monkeypatch):
    import socket
    import urllib.error
    monkeypatch.setattr(preflight, "_resolve_public_http_url", lambda url: (True, None, "x.example", 443, []))

    class Opener:
        def open(self, *_args, **_kwargs):
            raise urllib.error.URLError(socket.gaierror(-2, "Name or service not known"))

    monkeypatch.setattr(preflight, "_PREFLIGHT_NO_REDIRECT_OPENER", Opener())
    preflight._HTTP_FAILURE_REASONS.clear()
    assert preflight._http_request_status("https://x.example/", method="HEAD") == (0, None)
    assert preflight._HTTP_FAILURE_REASONS["https://x.example/"] == "DNS lookup failed"


# --- Messages --------------------------------------------------------------------


def test_missing_canonical_is_reported_first_in_gate_5(preflight, draft):
    import re
    text = re.sub(r'<link rel="canonical"[^>]*>', "", _html(draft).read_text(encoding="utf-8"), count=1)
    _html(draft).write_text(text, encoding="utf-8")
    result = _gate5(preflight, draft)
    assert result["violations"][0].startswith("no <link rel=canonical> in document")
    assert "canonical: https://" in result["violations"][0] and "og_image_alt" in result["violations"][0]


def test_identity_report_shows_schema_and_visible_values(preflight, draft):
    _edit(_html(draft), '"headline": "Core Web Vitals Thresholds Explained"', '"headline": "A Different Headline"')
    result = _gate5(preflight, draft)
    assert _has(result, "JSON-LD does not match visible content", "headline",
                'schema "A Different Headline"', 'visible "Core Web Vitals Thresholds Explained"')


def test_identity_report_for_author_names_both_sides(preflight, draft):
    _edit(_html(draft), '"author": {"@type": "Person", "name": "Alex Rivera"}',
          '"author": {"@type": "Person", "name": "Someone Else"}')
    result = _gate5(preflight, draft)
    assert _has(result, "author (schema", "someone else", "alex rivera")


def test_identity_image_mismatch_hints_at_the_missing_canonical(preflight, draft):
    import re
    html = _html(draft).read_text(encoding="utf-8")
    html = re.sub(r'<link rel="canonical"[^>]*>', "", html, count=1)
    html = html.replace(
        '"image": "https://example.com/blog/core-web-vitals-thresholds/hero.webp"',
        '"image": "https://example.com/other.webp"',
    )
    parser = preflight._MetaParser()
    parser.feed(html)
    nodes, _errors = preflight._parse_jsonld_blocks(parser.json_ld_blocks)
    post = next(node for node in nodes if preflight._is_blogposting_node(node))
    schema, visible = preflight._jsonld_identity_report(html, post, nodes)["image"]
    assert "other.webp" in schema
    assert "no <link rel=canonical>" in visible and "set it first" in visible


def test_svg_overflow_message_names_the_element(preflight):
    text = preflight._describe_overflows([
        {"containerSelector": "svg#cwv-chart", "childSelector": "text.label", "content": "LCP good", "overflowPx": 14},
        {"container": "FIGURE", "tag": "IMG", "content": ""},
    ])
    assert 'text.label "LCP good" overflows svg#cwv-chart by 14px' in text
    assert "img overflows figure" in text
    assert "Shrink or reflow" in text


# --- Performance -----------------------------------------------------------------


@pytest.mark.parametrize("payload", [
    "<img " * 60_000,
    "<svg><script>" * 20_000,
    '<a href="javascript:' * 20_000,
    "<!--" * 30_000,
    "<h1><h2><h3>" * 20_000,
])
def test_document_audit_is_linear_on_hostile_markup(preflight, payload):
    started = time.monotonic()
    preflight._audit_document(payload)
    preflight._placeholder_hits("[IMAGE" * 100_000)
    assert time.monotonic() - started < 5


def test_pdf_scan_is_bounded_on_hostile_streams(preflight):
    data = b"%PDF-1.5\n" + b"stream\n" * 50_000 + b"endstream " * 50_000 + b"%%EOF"
    started = time.monotonic()
    preflight._pdf_page_count(data)
    assert time.monotonic() - started < 5


def test_structure_findings_are_reported_by_gate_2_not_gate_5(preflight, draft):
    _edit(_html(draft), '<html lang="en">', "<html>")
    assert _has(_gate2(preflight, draft), "<html> has no lang attribute")
    assert not _has(_gate5(preflight, draft), "<html> has no lang attribute")


# --- Gate 2: rendered body integrity (M25) ---------------------------------------


def test_gate_2_blocks_a_claim_edited_in_the_html_only(preflight, draft):
    _edit(_html(draft), "Fix the slowest metric first", "Ignore the slowest metric first")
    result = _gate2(preflight, draft)
    assert not result["passed"]
    assert _has(result, "rendered HTML body was edited after render", f"edit {SLUG}.md", "blog_render.py")


def test_gate_2_ignores_edits_outside_the_rendered_body(preflight, draft):
    _edit(_html(draft), "<footer", "<!-- note --><footer")
    assert _gate2(preflight, draft)["passed"]


def test_gate_2_blocks_html_without_the_body_hash_meta(preflight, draft):
    text = _html(draft).read_text(encoding="utf-8")
    start = text.index('<meta name="blog-body-sha256"')
    _html(draft).write_text(text[:start] + text[text.index(">", start) + 1:], encoding="utf-8")
    result = _gate2(preflight, draft)
    assert _has(result, 'no <meta name="blog-body-sha256">', "edited after render")


@pytest.mark.parametrize("marker", ["<!--bs-body:start-->", "<!--bs-body:end-->"])
def test_gate_2_blocks_html_with_a_stripped_body_marker(preflight, draft, marker):
    _edit(_html(draft), marker, "")
    assert _has(_gate2(preflight, draft), "missing its bs-body start/end markers")


@pytest.mark.parametrize("marker", ["<!--bs-body:start-->", "<!--bs-body:end-->"])
def test_gate_2_blocks_a_repeated_body_marker_as_ambiguous(preflight, draft, marker):
    _edit(_html(draft), "</article>", f"{marker}<p>smuggled</p></article>")
    assert _has(_gate2(preflight, draft), "repeated bs-body markers", "ambiguous")


def test_gate_2_body_hash_survives_platform_line_endings(preflight, draft):
    path = _html(draft)
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    assert not _has(_gate2(preflight, draft), "body was edited")


def test_gate_2_accepts_a_body_that_quotes_the_marker_text(preflight, renderer, draft):
    source = draft / f"{SLUG}.md"
    source.write_bytes(source.read_bytes() + b"\nThe renderer wraps the body in `<!--bs-body:start-->` and `<!--bs-body:end-->`.\n")
    renderer._render_html(source, draft, "hero.webp")
    text = _html(draft).read_text(encoding="utf-8")
    assert text.count("<!--bs-body:start-->") == 1 and text.count("<!--bs-body:end-->") == 1
    assert "&lt;!--bs-body:start--&gt;" in text
    assert not _has(_gate2(preflight, draft), "body")


# --- Gate 3: hidden text in the article body (M35) ----------------------------------


def _require_browser():
    browser_api = pytest.importorskip("patchright.sync_api")
    with browser_api.sync_playwright() as runtime:
        if not Path(runtime.chromium.executable_path).is_file():
            pytest.skip("requires matching installed Chromium; no browser download in unit tests")


def _gate3_with_body_insert(preflight, renderer, draft, markup):
    """Render with extra author-level markup in the body, bypassing the sanitizer on purpose."""
    path = _html(draft)
    text = path.read_text(encoding="utf-8")
    # Keep the body hash valid so only Gate 3 is under test.
    text = text.replace("<!--bs-body:end-->", markup + "<!--bs-body:end-->", 1)
    path.write_text(text, encoding="utf-8")
    return preflight.gate_3_visual_verification(draft, SLUG)


STUFFED = "cheap seo services best seo agency buy backlinks cheap seo services best seo agency buy backlinks cheap"


def test_gate_3_golden_draft_has_no_hidden_text(preflight, renderer, draft):
    _require_browser()
    result = preflight.gate_3_visual_verification(draft, SLUG)
    assert result["passed"], result["violations"]
    assert not any("not rendered" in w for w in result["warnings"])
    assert result["per_viewport"]["desktop"]["result"]["hiddenText"]["chars"] == 0


@pytest.mark.parametrize("name,markup", [
    ("display-none", f'<div id="kw" style="display:none">{STUFFED}</div>'),
    ("font-size-zero", f'<p class="kw" style="font-size:0">{STUFFED}</p>'),
    ("off-screen", f'<p id="kw" style="position:absolute;left:-9999px">{STUFFED}</p>'),
    ("visibility-hidden", f'<p id="kw" style="visibility:hidden">{STUFFED}</p>'),
    ("opacity-zero", f'<p id="kw" style="opacity:0">{STUFFED}</p>'),
    ("clipped", f'<p id="kw" style="position:absolute;clip:rect(0,0,0,0)">{STUFFED}</p>'),
])
def test_gate_3_blocks_stuffed_hidden_text(preflight, renderer, draft, name, markup):
    _require_browser()
    result = _gate3_with_body_insert(preflight, renderer, draft, markup)
    assert not result["passed"]
    assert _has(result, "characters of article text", "not rendered", "kw", "cheap seo services"), result["violations"]


def test_gate_3_blocks_hidden_text_from_three_small_elements(preflight, renderer, draft):
    _require_browser()
    markup = "".join(f'<span id="h{i}" style="display:none">word{i}</span>' for i in range(3))
    result = _gate3_with_body_insert(preflight, renderer, draft, markup)
    assert not result["passed"] and _has(result, "3 element(s)", "#h0")


def test_gate_3_warns_below_the_hidden_text_threshold(preflight, renderer, draft):
    _require_browser()
    result = _gate3_with_body_insert(preflight, renderer, draft, '<span id="tiny" style="display:none">just a note</span>')
    assert result["passed"], result["violations"]
    assert any("11 characters" in w and "span#tiny" in w for w in result["warnings"])


def test_gate_3_allows_a_closed_details_and_decorative_svg(preflight, renderer, draft):
    _require_browser()
    markup = (
        f"<details><summary>More</summary><p>{STUFFED}</p></details>"
        f'<svg aria-hidden="true" width="120" height="30"><text x="2" y="16">Decor</text></svg>'
        "<template><p>inert template text</p></template><noscript><p>fallback</p></noscript>"
    )
    result = _gate3_with_body_insert(preflight, renderer, draft, markup)
    assert result["passed"], result["violations"]
    assert not any("not rendered" in w for w in result["warnings"])


# --- Artifact naming from the documented minimal frontmatter ---------------------


def test_minimal_frontmatter_renders_artifacts_named_after_the_md_stem(preflight, renderer, tmp_path):
    source = tmp_path / "image-formats.md"
    source.write_text(
        '---\ntitle: "Choosing Between Image Formats for Fast Pages"\ndescription: "How to pick an image format for speed."\n'
        'date: "2026-10-12"\nauthor: "Alex Rivera"\ncanonical: "https://example.com/blog/image-formats/"\n---\n\n'
        "Pick the format by content type.\n\n## Why it matters\n\nBytes decide speed.\n",
        encoding="utf-8",
    )
    shutil.copy(FIXTURE / "hero.webp", tmp_path / "hero.webp")
    html = renderer._render_html(source, tmp_path, "hero.webp")
    assert html.name == "image-formats.html"
    (tmp_path / "image-formats.pdf").write_bytes(MINIMAL_PDF)
    result = preflight.gate_2_format_completeness(tmp_path)
    assert result["passed"], result["violations"]
    assert result["artifacts"]["slug"] == "image-formats"


def test_frontmatter_slug_still_wins_over_the_file_stem(renderer, tmp_path):
    source = tmp_path / "some-draft.md"
    source.write_text(
        "---\ntitle: T\ndescription: D\ndate: 2026-10-12\nauthor: A\nslug: Chosen Name\n---\n\nBody text.\n",
        encoding="utf-8",
    )
    assert renderer._render_html(source, tmp_path, "hero.png").name == "chosen-name.html"


def test_underscored_file_stem_becomes_a_slug(renderer, tmp_path):
    source = tmp_path / "image_formats.v2.md"
    source.write_text("---\ntitle: T\ndescription: D\ndate: 2026-10-12\nauthor: A\n---\n\nBody text.\n", encoding="utf-8")
    assert renderer._render_html(source, tmp_path, "hero.png").name == "image-formats-v2.html"


def test_gate_2_names_the_stems_it_found_and_the_fix(preflight, draft):
    (draft / f"{SLUG}.html").rename(draft / "other-name.html")
    result = preflight.gate_2_format_completeness(draft)
    assert _has(result, "no slug-matched", f"md: ['{SLUG}']", "html: ['other-name']", "set `slug:`", "blog_render.py")


def test_gate_5_missing_canonical_names_the_frontmatter_keys(preflight, draft):
    import re
    text = re.sub(r'<link rel="canonical"[^>]*>', "", _html(draft).read_text(encoding="utf-8"), count=1)
    _html(draft).write_text(text, encoding="utf-8")
    first = _gate5(preflight, draft)["violations"][0]
    assert "`canonical: https://" in first
    for key in ("og:url", "site_name", "slug", "lang", "og_image_alt", "kicker", "tags"):
        assert key in first


# --- Hero JPEG trailers ------------------------------------------------------------


def _jpeg_bytes(width=1200, height=630):
    PIL = pytest.importorskip("PIL.Image")
    buffer = io.BytesIO()
    PIL.new("RGB", (width, height), "teal").save(buffer, "JPEG")
    return buffer.getvalue()


@pytest.mark.parametrize("with_pillow", [True, False])
def test_gate_2_accepts_a_jpeg_hero_with_a_large_trailer(preflight, draft, monkeypatch, with_pillow):
    if not with_pillow:
        monkeypatch.setattr(preflight, "_pillow_decode", lambda _data: None)
    (draft / "hero.webp").unlink()
    (draft / "hero.jpg").write_bytes(_jpeg_bytes() + b"<x:xmpmeta>" + b"A" * 4096)
    result = _gate2(preflight, draft)
    assert not _has(result, "hero.jpg"), result["violations"]


@pytest.mark.parametrize("with_pillow", [True, False])
def test_gate_2_still_rejects_a_truncated_jpeg_hero(preflight, draft, monkeypatch, with_pillow):
    if not with_pillow:
        monkeypatch.setattr(preflight, "_pillow_decode", lambda _data: None)
    data = _jpeg_bytes()
    (draft / "hero.webp").unlink()
    (draft / "hero.jpg").write_bytes(data[: len(data) // 2])
    assert _has(_gate2(preflight, draft), "hero.jpg")


# --- Iteration cap keeps the diagnostic --------------------------------------------


def _run_main(preflight, monkeypatch, draft, *extra):
    monkeypatch.setattr(sys, "argv", ["blog_preflight.py", "--draft", str(draft), "--gate", "2", *extra])
    return preflight.main()


def test_iteration_cap_keeps_the_last_diagnostic_and_stays_blocked(preflight, draft, monkeypatch):
    _edit(draft / f"{SLUG}.md", "## Key takeaways", "[IMAGE: todo]\n\n## Key takeaways")
    (draft / "preflight-report.json").unlink(missing_ok=True)
    for _ in range(3):
        assert _run_main(preflight, monkeypatch, draft, "--repair-attempt") == 1
    report = json.loads((draft / "preflight-report.json").read_text(encoding="utf-8"))
    assert report["gates"] and report["blocked"]
    assert _run_main(preflight, monkeypatch, draft, "--repair-attempt") == preflight.EXIT_ITERATION_CAP
    capped = json.loads((draft / "preflight-report.json").read_text(encoding="utf-8"))
    assert capped["blocked"] is True and capped["incomplete"] is True
    assert capped["iteration_cap_exceeded"] is True
    assert capped["gates"] == []
    assert any("draft placeholder" in v for g in capped["previous_gates"] for v in g["violations"])
    # A later crash-safety placeholder keeps carrying the diagnostic.
    assert _run_main(preflight, monkeypatch, draft, "--repair-attempt") == preflight.EXIT_ITERATION_CAP
    again = json.loads((draft / "preflight-report.json").read_text(encoding="utf-8"))
    assert again["previous_gates"] == capped["previous_gates"]


def test_a_crashed_run_leaves_an_incomplete_blocked_report(preflight, draft, monkeypatch):
    assert _run_main(preflight, monkeypatch, draft) == 0
    passing = json.loads((draft / "preflight-report.json").read_text(encoding="utf-8"))
    assert passing["blocked"] is False
    monkeypatch.setattr(preflight, "_iteration_check", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(RuntimeError):
        _run_main(preflight, monkeypatch, draft)
    report = json.loads((draft / "preflight-report.json").read_text(encoding="utf-8"))
    assert report["blocked"] is True and report["incomplete"] is True and report["gates"] == []
    assert report["previous_gates"] == passing["gates"]


# --- Console errors name the resource ------------------------------------------------


def test_gate_3_console_error_names_the_missing_resource(preflight, renderer, draft):
    _require_browser()
    result = _gate3_with_body_insert(preflight, renderer, draft, '<img src="missing-figure.png" alt="Missing">')
    assert not result["passed"]
    assert _has(result, "console error(s)", "missing-figure.png"), result["violations"]


# --- lastUpdated does not disturb the identity checks ----------------------------------


def test_rendered_post_with_last_updated_passes_gates_2_3_and_5(preflight, renderer, draft):
    _require_browser()
    source = draft / f"{SLUG}.md"
    text = source.read_text(encoding="utf-8")
    source.write_text(text.replace("slug: core-web-vitals-thresholds\n", "slug: core-web-vitals-thresholds\nlastUpdated: 2026-11-02\n", 1), encoding="utf-8")
    renderer._render_html(source, draft, "hero.webp")
    page = _html(draft).read_text(encoding="utf-8")
    assert '"dateModified": "2026-11-02"' in page and "Updated" in page
    assert _gate2(preflight, draft)["passed"]
    assert _gate5(preflight, draft)["passed"]
    result = preflight.gate_3_visual_verification(draft, SLUG)
    assert result["passed"], result["violations"]
