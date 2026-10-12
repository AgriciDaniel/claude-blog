"""Hardening regressions for blog_preflight.py found in the PR #86 review.

Covers hidden-identity decoys, WebSocket egress during Gate 3, Gate 4
reviewer-contract gaps, linear-time HTML scanning, fail-closed crashes, and
the Gate 5 consistency fixes. Page and review content is treated as untrusted.
"""
from __future__ import annotations

import base64
import importlib.util
import json
import re
import socket
import sys
import threading
import time
import urllib.parse
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def preflight():
    return _load("hardening_preflight", "blog_preflight.py")


@pytest.fixture(scope="module")
def renderer():
    return _load("hardening_renderer", "blog_render.py")


@pytest.fixture(autouse=True)
def isolate_network_probes(preflight, monkeypatch):
    # The renderer emits a publisher footer link; these tests never probe it.
    real_safe_http_url = preflight._safe_http_url

    def safe_http_url(url):
        try:
            urllib.parse.urlsplit(url).port
        except ValueError:
            # Malformed URLs go through the real validator under test.
            return real_safe_http_url(url)
        return True, None

    monkeypatch.setattr(preflight, "_safe_http_url", safe_http_url)
    monkeypatch.setattr(preflight, "_http_head", lambda _url: 200)


def _require_browser():
    browser_api = pytest.importorskip("patchright.sync_api")
    with browser_api.sync_playwright() as runtime:
        if not Path(runtime.chromium.executable_path).is_file():
            pytest.skip("requires matching installed Chromium; no browser download in unit tests")


def _render_fixture(directory, renderer):
    source = directory / "post.md"
    source.write_text(
        "---\ntitle: Fixture title\nslug: post\ndescription: Fixture description\n"
        "date: 2026-10-07\nauthor: Fixture Editor\n"
        "canonical: https://publisher.example/articles/post\n---\n\nA useful article.\n"
    )
    (directory / "hero.png").write_bytes(base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGNoaGj4DwAFhAKAjM1mJgAAAABJRU5ErkJggg=="
    ))
    renderer._render_html(source, directory, "hero.png")
    (directory / "post.pdf").write_bytes(b"%PDF-1.4\n")
    return directory / "post.html"


def _schema_edit(path, edit):
    raw = path.read_text()
    match = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', raw, re.S)
    schema = json.loads(match.group(2))
    edit(schema)
    path.write_text(raw[:match.start(2)] + json.dumps(schema) + raw[match.end(2):])


BYLINE = '<p class="byline"><strong>By Fixture Editor</strong> &middot; 2026-10-07 &middot; 1 min read &middot; 3 words</p>'


def _decoy_page(path, decoy, visible='<p class="meta">By Bob Real <time datetime="2026-10-07">Oct 7</time></p>'):
    """Replace the semantic byline with a non-semantic visible one plus a decoy."""
    html = path.read_text()
    assert BYLINE in html
    path.write_text(html.replace(BYLINE, visible + decoy))


# Each decoy keeps the schema author ("Fixture Editor") in an element that the
# reader cannot see, while the visible byline names someone else.
GEOMETRY_DECOYS = {
    "offscreen-left": '<span class="author" style="position:absolute;left:-9999px">Fixture Editor</span>',
    "offscreen-top": '<span class="author" style="position:absolute;top:-9999px">Fixture Editor</span>',
    "font-size-zero": '<span class="author" style="font-size:0">Fixture Editor</span>',
    "font-size-zero-block": '<span class="author" style="display:block;font-size:0;padding:4px">Fixture Editor</span>',
    "clip-rect": '<span class="author" style="position:absolute;clip:rect(0,0,0,0)">Fixture Editor</span>',
    "text-indent": '<span class="author" style="display:block;text-indent:-9999px">Fixture Editor</span>',
    "zero-area": '<span class="author" style="display:inline-block;width:0;height:0;overflow:hidden">Fixture Editor</span>',
    "scale-zero": '<span class="author" style="display:inline-block;transform:scale(0)">Fixture Editor</span>',
    "clip-path": '<span class="author" style="display:inline-block;clip-path:inset(50%)">Fixture Editor</span>',
    "sr-only": ('<span class="author" style="position:absolute;width:1px;height:1px;overflow:hidden;'
                'clip:rect(0 0 0 0);white-space:nowrap">Fixture Editor</span>'),
    "wrapper-offscreen": ('<div style="position:absolute;left:-9999px">'
                          '<span class="author">Fixture Editor</span></div>'),
    "stylesheet-offscreen": ('<style>.hide-me{position:absolute;left:-9999px}</style>'
                             '<span class="author hide-me">Fixture Editor</span>'),
}


@pytest.mark.parametrize("name", sorted(GEOMETRY_DECOYS))
def test_rendered_geometry_decoys_cannot_stand_in_for_the_visible_author(preflight, renderer, tmp_path, name):
    _require_browser()
    path = _render_fixture(tmp_path, renderer)
    _decoy_page(path, GEOMETRY_DECOYS[name])
    result = preflight.gate_3_visual_verification(tmp_path, "post")
    assert not result["passed"], name
    for viewport in ("mobile", "tablet", "desktop"):
        observation = result["per_viewport"][viewport]["result"]
        assert observation["jsonLdVisibleConsistent"] is False
        assert "author" in observation["jsonLdConsistencyMismatches"]
    assert not preflight._rendered_jsonld_handoff(result)["available"]


@pytest.mark.parametrize("name", [
    "offscreen-left", "font-size-zero", "clip-rect", "text-indent", "wrapper-offscreen",
])
def test_rendered_decoys_with_a_valid_handoff_cannot_rescue_gate_5(preflight, renderer, tmp_path, name):
    _require_browser()
    path = _render_fixture(tmp_path, renderer)
    _decoy_page(path, GEOMETRY_DECOYS[name])
    gate_3 = preflight.gate_3_visual_verification(tmp_path, "post")
    handoff = preflight._rendered_jsonld_handoff(gate_3)
    assert not preflight.gate_5_asset_link_integrity(tmp_path, "post", handoff)["passed"]


@pytest.mark.parametrize("name", [
    "offscreen-left", "offscreen-top", "font-size-zero", "clip-rect", "text-indent", "zero-area",
    "scale-zero", "clip-path",
])
def test_source_gate_rejects_inline_style_geometry_decoys(preflight, renderer, tmp_path, name):
    path = _render_fixture(tmp_path, renderer)
    _decoy_page(path, GEOMETRY_DECOYS[name])
    result = preflight.gate_5_asset_link_integrity(tmp_path, "post")
    assert not result["passed"], name
    assert any("does not match visible content" in item and "author" in item for item in result["violations"])


@pytest.mark.parametrize("html", [
    '<h1 style="position:absolute;left:-9999px">Fixture title</h1>',
    '<h1 style="font-size:0">Fixture title</h1>',
])
def test_rendered_headline_decoy_does_not_replace_the_visible_h1(preflight, renderer, tmp_path, html):
    _require_browser()
    path = _render_fixture(tmp_path, renderer)
    text = path.read_text().replace("<h1>Fixture title</h1>", html + "<h1>Another visible title</h1>")
    path.write_text(text)
    result = preflight.gate_3_visual_verification(tmp_path, "post")
    assert not result["passed"]
    assert "headline" in result["per_viewport"]["desktop"]["result"]["jsonLdConsistencyMismatches"]


def test_rendered_date_decoy_does_not_replace_the_visible_date(preflight, renderer, tmp_path):
    _require_browser()
    path = _render_fixture(tmp_path, renderer)
    decoy = '<time itemprop="datePublished" datetime="2026-10-07" style="position:absolute;left:-9999px">Oct 7</time>'
    visible = '<p class="meta"><a rel="author">Fixture Editor</a> <time datetime="1999-01-01">Jan 1</time></p>'
    _decoy_page(path, decoy, visible)
    result = preflight.gate_3_visual_verification(tmp_path, "post")
    assert not result["passed"]
    assert "datePublished" in result["per_viewport"]["desktop"]["result"]["jsonLdConsistencyMismatches"]


@pytest.mark.parametrize("hidden", [
    '<span class="author" style="position:absolute;left:-9999px">Someone Else</span>',
    '<span class="author" style="font-size:0">Someone Else</span>',
    '<span class="author" style="position:absolute;clip:rect(0,0,0,0)">Someone Else</span>',
])
def test_hidden_wrong_author_does_not_break_a_correct_visible_byline(preflight, renderer, tmp_path, hidden):
    _require_browser()
    path = _render_fixture(tmp_path, renderer)
    path.write_text(path.read_text().replace("</header>", hidden + "</header>", 1))
    result = preflight.gate_3_visual_verification(tmp_path, "post")
    assert result["passed"], result["violations"]


# --- WebSocket egress ------------------------------------------------------


def _count_connections():
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen(8)
    server.settimeout(0.2)
    state = {"connections": 0, "stop": False}

    def accept_loop():
        while not state["stop"]:
            try:
                connection, _addr = server.accept()
            except (socket.timeout, OSError):
                continue
            state["connections"] += 1
            connection.close()

    thread = threading.Thread(target=accept_loop, daemon=True)
    thread.start()
    return server, state, thread


def test_gate_3_never_opens_a_websocket_to_loopback(preflight, renderer, tmp_path):
    _require_browser()
    server, state, thread = _count_connections()
    try:
        port = server.getsockname()[1]
        path = _render_fixture(tmp_path, renderer)
        script = f'<script>try{{new WebSocket("ws://127.0.0.1:{port}/draft")}}catch(e){{}}</script>'
        path.write_text(path.read_text().replace("</body>", script + "</body>"))
        preflight.gate_3_visual_verification(tmp_path, "post")
        time.sleep(0.5)
    finally:
        state["stop"] = True
        thread.join(timeout=2)
        server.close()
    assert state["connections"] == 0


def test_every_gate_3_context_blocks_service_workers():
    source = (ROOT / "scripts" / "blog_preflight.py").read_text()
    gate = source[source.index("def gate_3_visual_verification"):source.index("def _rendered_jsonld_handoff")]
    assert gate.count("new_context(") == 2
    assert gate.count('service_workers="block"') == 2
    assert gate.count("_guard_context_network(") == 2


# --- Gate 4 reviewer contract -----------------------------------------------


def _review(nonce, clearance="zero P0 issues found", overall=92, categories="", reason="cleared all gates"):
    return (
        "## Quality Review: Fixture\n"
        f"### Overall Score: {overall}/100 - Exceptional\n"
        f"{categories}"
        f"{clearance}\n"
        f"Nonce: {nonce}\n"
        f"BLOCKING: false ({reason})\n"
    )


TABLE_92 = (
    "| Category | Score | Max | Notes |\n"
    "|----------|-------|-----|-------|\n"
    "| Content Quality | 28 | 30 | strong |\n"
    "| SEO Optimization | 23 | 25 | strong |\n"
    "| E-E-A-T Signals | 14 | 15 | strong |\n"
    "| Technical Elements | 14 | 15 | strong |\n"
    "| AI Citation Readiness | 13 | 15 | strong |\n"
)


@pytest.fixture
def gate4(preflight, monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_BLOG_REVIEW_STATE_DIR", str(tmp_path / "state"))
    draft = tmp_path / "draft"
    draft.mkdir()
    nonce = preflight._init_review_nonce(draft)

    def run(**kwargs):
        (draft / "review.md").write_text(_review(nonce, **kwargs))
        return preflight.gate_4_content_review(draft)

    run.draft = draft
    run.nonce = nonce
    return run


@pytest.mark.parametrize("clearance,reason", [
    ("zero P0 issues found\nThere are 3 P0s remain unresolved", "cleared all gates"),
    ("zero P0 issues found", "3 P0s remain"),
    ("zero P0 issues found\n- 2 p0s outstanding", "cleared all gates"),
])
def test_gate_4_rejects_plural_p0_mentions(gate4, clearance, reason):
    result = gate4(clearance=clearance, reason=reason)
    assert not result["passed"]
    assert any("P0" in item for item in result["violations"])


@pytest.mark.parametrize("clearance", ["zero P0s found", "No P0s.", "- no P0s remain"])
def test_gate_4_accepts_plural_zero_clearance(gate4, clearance):
    assert gate4(clearance=clearance)["passed"]


def test_gate_4_rejects_category_scores_that_contradict_the_overall(gate4):
    result = gate4(categories="Content Quality: 3/30\n", overall=91)
    assert not result["passed"]
    assert any("inconsistent with its category scores" in item for item in result["violations"])


def test_gate_4_rejects_full_table_whose_sum_differs_from_the_overall(gate4):
    result = gate4(categories=TABLE_92, overall=96)
    assert not result["passed"]
    assert any("inconsistent with its category scores" in item for item in result["violations"])


def test_gate_4_rejects_category_over_its_rubric_maximum(gate4):
    result = gate4(categories="Content Quality: 35/30\n", overall=92)
    assert not result["passed"]
    assert any("exceeds its maximum" in item for item in result["violations"])


def test_gate_4_rejects_category_with_a_foreign_maximum(gate4):
    result = gate4(categories="Content Quality: 28/40\n", overall=92)
    assert not result["passed"]
    assert any("rubric maximum" in item for item in result["violations"])


def test_gate_4_rejects_conflicting_category_scores(gate4):
    result = gate4(categories="Content Quality: 28/30\nContent Quality: 12/30\n", overall=92)
    assert not result["passed"]
    assert any("conflicting Content Quality" in item for item in result["violations"])


@pytest.mark.parametrize("categories,overall", [
    (TABLE_92, 92),
    ("Content Quality: 28/30\nSEO Optimization: 23/25\n", 92),
    ("Content Quality (30 pts): 28\n", 92),
    ("", 92),
])
def test_gate_4_accepts_consistent_or_absent_category_scores(gate4, categories, overall):
    result = gate4(categories=categories, overall=overall)
    assert result["passed"], result["violations"]


def test_gate_4_blocks_when_the_draft_changed_after_the_nonce_was_issued(preflight, gate4):
    draft = gate4.draft
    (draft / "post.html").write_text("<html>first</html>")
    # Re-issue so the stored digest covers the first version of the artifact.
    nonce = preflight._init_review_nonce(draft)
    (draft / "review.md").write_text(_review(nonce))
    fresh = preflight.gate_4_content_review(draft)
    assert fresh["passed"] and fresh["warnings"] == []
    (draft / "post.html").write_text("<html>second</html>")
    stale = preflight.gate_4_content_review(draft)
    assert not stale["passed"]
    assert any("draft changed after the review nonce was issued: post.html" in item for item in stale["violations"])


def test_gate_4_state_without_a_digest_stays_unchecked(preflight, monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_BLOG_REVIEW_STATE_DIR", str(tmp_path / "state"))
    draft = tmp_path / "draft"
    draft.mkdir()
    (draft / "post.html").write_text("<html></html>")
    preflight._atomic_write_json(
        preflight._review_state_path(draft), {"draft": str(draft), "nonce": "a" * 32, "version": "old"}
    )
    (draft / "review.md").write_text(_review("a" * 32))
    result = preflight.gate_4_content_review(draft)
    assert result["passed"] and result["warnings"] == []


# --- Linear-time scanning ---------------------------------------------------


@pytest.mark.parametrize("unit", [b"<script>", b"<meta ", b"<style>", b"<script ", b"data:"])
def test_googlebot_prefix_check_is_linear_on_unterminated_tags(preflight, unit):
    raw = unit * 30000
    started = time.perf_counter()
    result = preflight._googlebot_html_prefix_check(raw)
    elapsed = time.perf_counter() - started
    # Quadratic regexes needed 10 to 20 seconds here; a linear scan needs milliseconds.
    assert elapsed < 3, f"{unit!r} took {elapsed:.1f}s"
    assert result["critical_after_cutoff"] == []


def test_googlebot_prefix_check_still_counts_inline_blocks_and_late_critical_tags(preflight):
    filler = b"<script>" + b"x" * 300_000 + b"</script>"
    raw = filler + b"<!-- pad -->" * 200_000 + b'<title>t</title><link rel="canonical" href="https://a.example/">'
    result = preflight._googlebot_html_prefix_check(raw)
    assert result["inline_bloat_bytes"] >= 300_000
    assert "title" in result["critical_after_cutoff"]
    assert "canonical" in result["critical_after_cutoff"]
    early = b'<title>t</title><meta name="description" content="d"><script type="application/ld+json">{}</script><main>x</main>'
    assert preflight._googlebot_html_prefix_check(early)["critical_after_cutoff"] == []


# --- Fail-closed crashes ----------------------------------------------------


@pytest.mark.parametrize("url", ["http://x:abc/", "http://[::1/", "https://host:99999999/"])
def test_malformed_url_is_a_failed_link_not_a_crash(preflight, renderer, tmp_path, url):
    path = _render_fixture(tmp_path, renderer)
    path.write_text(path.read_text().replace("</article>", f'<footer><a href="{url}">bad</a></footer></article>', 1))
    result = preflight.gate_5_asset_link_integrity(tmp_path, "post")
    assert not result["passed"]
    assert any("refused by URL safety policy" in item for item in result["violations"])


@pytest.mark.parametrize("content", ["[]", '"discover"', "null", "3"])
def test_non_object_targets_file_is_ignored_with_a_warning(preflight, renderer, tmp_path, content):
    path = _render_fixture(tmp_path, renderer)
    (tmp_path / "preflight-targets.json").write_text(content)
    result = preflight.gate_5_asset_link_integrity(tmp_path, "post")
    assert result["passed"], result["violations"]
    assert any("preflight-targets.json ignored" in item for item in result["warnings"])


def _run_main(preflight, monkeypatch, draft, *extra):
    monkeypatch.setattr(sys, "argv", ["blog_preflight.py", "--draft", str(draft), *extra])
    return preflight.main()


STALE_PASS = {"draft": "x", "strict": True, "blocked": False, "gates": [{"gate": 5, "passed": True}]}


def test_crashing_gate_becomes_a_failed_gate_and_a_fresh_report(preflight, monkeypatch, tmp_path, capsys):
    (tmp_path / "preflight-report.json").write_text(json.dumps(STALE_PASS))

    def boom(*_args, **_kwargs):
        raise RuntimeError("synthetic crash")

    monkeypatch.setattr(preflight, "gate_5_asset_link_integrity", boom)
    assert _run_main(preflight, monkeypatch, tmp_path, "--gate", "5") == 1
    report = json.loads((tmp_path / "preflight-report.json").read_text())
    assert report["blocked"] is True
    assert report["gates"][0]["gate"] == 5 and report["gates"][0]["passed"] is False
    assert "synthetic crash" in report["gates"][0]["violations"][0]


def test_iteration_cap_cannot_leave_a_stale_passing_report(preflight, monkeypatch, tmp_path, capsys):
    (tmp_path / "preflight-report.json").write_text(json.dumps(STALE_PASS))
    (tmp_path / ".iteration-count").write_text("3\n")
    assert _run_main(preflight, monkeypatch, tmp_path, "--repair-attempt") == preflight.EXIT_ITERATION_CAP
    report = json.loads((tmp_path / "preflight-report.json").read_text())
    assert report["blocked"] is True and report["incomplete"] is True
    assert "iteration cap" in report["reason"]


def test_interrupted_run_leaves_a_blocked_placeholder_report(preflight, monkeypatch, tmp_path):
    (tmp_path / "preflight-report.json").write_text(json.dumps(STALE_PASS))

    def interrupted(_draft):
        raise KeyboardInterrupt

    monkeypatch.setattr(preflight, "gate_4_content_review", interrupted)
    with pytest.raises(KeyboardInterrupt):
        _run_main(preflight, monkeypatch, tmp_path, "--gate", "4")
    report = json.loads((tmp_path / "preflight-report.json").read_text())
    assert report["blocked"] is True and report["incomplete"] is True


# --- Gate 5 consistency -----------------------------------------------------


def test_declared_word_count_is_checked_when_the_page_has_no_article(preflight, renderer, tmp_path):
    path = _render_fixture(tmp_path, renderer)
    path.write_text(path.read_text().replace("<article>", "<div>").replace("</article>", "</div>"))
    _schema_edit(path, lambda schema: schema.update(wordCount=99999))
    result = preflight.gate_5_asset_link_integrity(tmp_path, "post")
    assert not result["passed"]
    assert any("wordCount 99999 cannot be verified" in item for item in result["violations"])


def test_declared_word_count_is_checked_against_main_without_an_article(preflight, renderer, tmp_path):
    path = _render_fixture(tmp_path, renderer)
    path.write_text(path.read_text().replace("<article>", "<main>").replace("</article>", "</main>"))
    assert preflight.gate_5_asset_link_integrity(tmp_path, "post")["passed"]
    _schema_edit(path, lambda schema: schema.update(wordCount=99999))
    result = preflight.gate_5_asset_link_integrity(tmp_path, "post")
    assert not result["passed"]
    assert any("wordCount 99999 differs" in item for item in result["violations"])


def test_declared_word_count_is_checked_against_an_empty_article(preflight, renderer, tmp_path):
    path = _render_fixture(tmp_path, renderer)
    html = path.read_text()
    path.write_text(html.replace("A useful article.", ""))
    _schema_edit(path, lambda schema: schema.update(wordCount=500))
    result = preflight.gate_5_asset_link_integrity(tmp_path, "post")
    assert not result["passed"]
    assert any("wordCount 500 differs from actual 0" in item for item in result["violations"])


def test_non_utf8_html_reports_the_encoding_problem(preflight, renderer, tmp_path):
    path = _render_fixture(tmp_path, renderer)
    path.write_bytes(path.read_bytes() + b"\xff\xfe")
    result = preflight.gate_5_asset_link_integrity(tmp_path, "post")
    assert not result["passed"]
    assert any("not valid UTF-8" in item for item in result["violations"])


def test_mailto_links_are_allowed_like_the_renderer_allows_them(preflight, renderer, tmp_path):
    assert "mailto" in renderer.SAFE_LINK_SCHEMES
    path = _render_fixture(tmp_path, renderer)
    path.write_text(path.read_text().replace("</article>", '<footer><a href="mailto:editor@publisher.example">mail</a></footer></article>', 1))
    result = preflight.gate_5_asset_link_integrity(tmp_path, "post")
    assert result["passed"], result["violations"]


@pytest.mark.parametrize("href", ["javascript:alert(1)", "data:text/html,x", "tel:+15550100"])
def test_other_non_http_schemes_stay_rejected(preflight, renderer, tmp_path, href):
    path = _render_fixture(tmp_path, renderer)
    path.write_text(path.read_text().replace("</article>", f'<footer><a href="{href}">x</a></footer></article>', 1))
    assert not preflight.gate_5_asset_link_integrity(tmp_path, "post")["passed"]


def test_legacy_allowlist_file_is_reported_as_ignored(preflight, renderer, tmp_path):
    _render_fixture(tmp_path, renderer)
    (tmp_path / "preflight-allowlist.json").write_text(json.dumps({"hosts": ["example.invalid"]}))
    result = preflight.gate_5_asset_link_integrity(tmp_path, "post")
    assert any("preflight-allowlist.json is no longer read" in item for item in result["warnings"])


def _breadcrumb():
    return ('<script type="application/ld+json">{"@context":"https://schema.org",'
            '"@type":"BreadcrumbList","itemListElement":[]}</script>')


def test_second_valid_json_ld_block_is_parsed_on_its_own(preflight, renderer, tmp_path):
    path = _render_fixture(tmp_path, renderer)
    text = path.read_text()
    path.write_text(text.replace("</head>", _breadcrumb() + "</head>", 1))
    assert preflight.gate_5_asset_link_integrity(tmp_path, "post")["passed"]
    # The BlogPosting may also come second.
    first = re.search(r'<script type="application/ld\+json">.*?</script>', text, re.S)
    reordered = text.replace(first.group(0), "").replace("</head>", _breadcrumb() + first.group(0) + "</head>", 1)
    path.write_text(reordered)
    assert preflight.gate_5_asset_link_integrity(tmp_path, "post")["passed"]


def test_invalid_second_json_ld_block_is_named(preflight, renderer, tmp_path):
    path = _render_fixture(tmp_path, renderer)
    path.write_text(path.read_text().replace(
        "</head>", '<script type="application/ld+json">{not json}</script></head>', 1))
    result = preflight.gate_5_asset_link_integrity(tmp_path, "post")
    assert not result["passed"]
    assert any("block 2 of 2 invalid" in item for item in result["violations"])


def test_rendered_gate_accepts_a_second_json_ld_block(preflight, renderer, tmp_path):
    _require_browser()
    path = _render_fixture(tmp_path, renderer)
    path.write_text(path.read_text().replace("</head>", _breadcrumb() + "</head>", 1))
    result = preflight.gate_3_visual_verification(tmp_path, "post")
    assert result["passed"], result["violations"]


def test_reset_iterations_help_matches_the_behaviour(preflight, tmp_path):
    import subprocess
    help_text = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "blog_preflight.py"), "--help"],
        capture_output=True, text=True, check=True,
    ).stdout
    flat = " ".join(help_text.split())
    assert "counter to 0" in flat
    (tmp_path / ".iteration-count").write_text("2\n")
    preflight._iteration_check(tmp_path, reset=True)
    assert (tmp_path / ".iteration-count").read_text().strip() == "0"
