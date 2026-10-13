"""Wave 3 regression tests: quality_gate.py must fail closed."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "quality_gate.py"
FIXTURES = Path(__file__).parent / "fixtures"

sys.path.insert(0, str(ROOT / "scripts"))
import quality_gate  # noqa: E402


def _run(*args, cwd=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=cwd,
    )


def test_missing_explicit_path_is_an_error(tmp_path):
    result = _run(str(tmp_path / "posts" / "nope.md"))
    assert result.returncode != 0
    assert "does not exist" in result.stdout
    assert "passed: no blog posts" not in result.stdout


def test_missing_explicit_path_json_reports_error(tmp_path):
    result = _run(str(tmp_path / "nope.md"), "--format", "json")
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert "does not exist" in payload["error"]


def test_post_without_title_and_description_fails(tmp_path):
    post = tmp_path / "bare.md"
    post.write_text("# Just a heading\n\nBody text without frontmatter.\n", encoding="utf-8")
    result = _run(str(post))
    assert result.returncode == 1
    assert "missing blog frontmatter" in result.stdout


@pytest.mark.parametrize("subdir", ["docs", "skills", "tests", "templates", "references"])
def test_explicit_file_in_excluded_dir_is_still_checked(tmp_path, subdir):
    post = tmp_path / subdir / "post.md"
    post.parent.mkdir()
    post.write_text((FIXTURES / "blog_fail.md").read_text(encoding="utf-8"), encoding="utf-8")
    result = _run(str(post))
    assert result.returncode == 1
    assert "post.md" in result.stdout


def test_directory_scan_still_skips_excluded_dirs_and_non_posts(tmp_path):
    good = tmp_path / "posts" / "a.md"
    good.parent.mkdir()
    good.write_text((FIXTURES / "blog_pass.md").read_text(encoding="utf-8"), encoding="utf-8")
    skipped = tmp_path / "docs" / "b.md"
    skipped.parent.mkdir()
    skipped.write_text((FIXTURES / "blog_fail.md").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "notes.md").write_text("# notes\n", encoding="utf-8")
    result = _run(str(tmp_path), "--format", "json", cwd=tmp_path)
    payload = json.loads(result.stdout)
    assert [Path(item["file"]).name for item in payload["checked"]] == ["a.md"]
    assert result.returncode == 0


def test_select_mode_skips_non_posts_for_the_pre_commit_hook(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# readme\n", encoding="utf-8")
    result = _run("--select", str(readme), cwd=tmp_path)
    assert result.returncode == 0
    assert "no blog posts to check" in result.stdout
    assert _run("--select", str(tmp_path / "gone.md"), cwd=tmp_path).returncode == 2


@pytest.mark.parametrize("value", ["0", "-5", "101", "abc"])
def test_nonsensical_thresholds_are_rejected(tmp_path, value):
    post = tmp_path / "p.md"
    post.write_text((FIXTURES / "blog_fail.md").read_text(encoding="utf-8"), encoding="utf-8")
    result = _run(str(post), "--threshold", value)
    assert result.returncode == 2
    assert "threshold" in result.stderr


def test_threshold_zero_no_longer_passes_everything(tmp_path):
    post = tmp_path / "p.md"
    post.write_text((FIXTURES / "blog_fail.md").read_text(encoding="utf-8"), encoding="utf-8")
    assert _run(str(post), "--threshold", "0").returncode != 0


def test_no_paths_and_no_staged_is_a_usage_error():
    assert _run().returncode == 2


def test_help_names_the_analyzer_threshold_not_the_delivery_gate():
    text = " ".join(_run("--help").stdout.split())
    assert "analyze_blog.py quality" in text
    assert "90-point delivery gate" in text
    assert "analyze_blog.py quality threshold" in quality_gate.__doc__


# ---- lint_prose.py fails closed -------------------------------------------

LINTER = ROOT / "scripts" / "lint_prose.py"


def _lint(root, *extra):
    return subprocess.run(
        [sys.executable, str(LINTER), "--root", str(root), *extra],
        capture_output=True, text=True, check=False,
    )


def test_lint_prose_fails_on_an_undecodable_tracked_file(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "ok.md").write_text("Clean prose.\n", encoding="utf-8")
    (tmp_path / "docs" / "bad.md").write_bytes(b"caf\xe9 \xff\xfe broken bytes\n")
    result = _lint(tmp_path)
    assert result.returncode == 2
    assert "docs/bad.md" in result.stderr
    assert "could not be decoded" in result.stdout
    assert "Traceback" not in result.stderr
    as_json = json.loads(_lint(tmp_path, "--format", "json").stdout)
    assert as_json["ok"] is False and as_json["unreadable"][0].startswith("docs/bad.md")


def test_lint_prose_violations_still_win_over_unreadable(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "bad.md").write_bytes(b"\xff\xfe\n")
    (tmp_path / "docs" / "dash.md").write_text("bad " + chr(0x2014) + " dash\n", encoding="utf-8")
    assert _lint(tmp_path).returncode == 1


def test_lint_prose_missing_root_is_an_error(tmp_path):
    result = _lint(tmp_path / "nonexistent")
    assert result.returncode == 2
    assert "not a directory" in result.stderr


def test_lint_prose_docstring_cites_a_real_document():
    text = LINTER.read_text(encoding="utf-8")
    assert ".github/CONTRIBUTING.md" in text
    assert (ROOT / ".github" / "CONTRIBUTING.md").is_file()
    assert " per\nCONTRIBUTING.md" not in text


# ---- content_decay.py ------------------------------------------------------

DECAY = ROOT / "scripts" / "content_decay.py"


def _decay_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location("wave3_content_decay", DECAY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _decay_rows(page, clicks, impressions=100):
    return [{"page": page, "clicks": clicks, "impressions": impressions}]


def test_decay_matches_urls_that_differ_only_by_slash_case_or_fragment():
    decay = _decay_module()
    previous = _decay_rows("https://Example.com/Post/", 100)
    current = _decay_rows("HTTPS://example.COM/Post#section", 100)
    report = decay.analyze_decay(current, previous)
    assert report["decays"] == []  # same page, no decline, not "dropped out"
    assert report["summary"]["current_pages"] == 1


def test_decay_keeps_query_strings_as_distinct_pages():
    decay = _decay_module()
    assert decay.normalize_page("https://example.com/p?id=1") != decay.normalize_page("https://example.com/p?id=2")
    assert decay.normalize_page("https://example.com/p/?id=1#x") == "https://example.com/p?id=1"
    assert decay.normalize_page("/blog/post/") == "/blog/post"
    assert decay.normalize_page("/") == "/"
    assert decay.normalize_page("https://example.com/") == "https://example.com"


def test_decay_real_drop_is_still_reported_after_normalization():
    decay = _decay_module()
    report = decay.analyze_decay(
        _decay_rows("https://example.com/post", 10), _decay_rows("https://example.com/post/", 100))
    assert report["decays"][0]["page"] == "https://example.com/post"


@pytest.mark.parametrize("value,expected", [("1,234", 1234.0), (" 12 ", 12.0), ("1,234.5", 1234.5), (7, 7.0), (None, 0.0)])
def test_decay_parses_thousands_separators(value, expected):
    decay = _decay_module()
    assert decay._as_number(value, metric="clicks", page="/p") == expected


@pytest.mark.parametrize("value", ["abc", "12abc", "1,23", "", "1.234,5", True, [5]])
def test_decay_rejects_unparseable_metrics_instead_of_zeroing(value):
    decay = _decay_module()
    with pytest.raises(decay.ContentDecayError, match="clicks"):
        decay._as_number(value, metric="clicks", page="/p")


def test_decay_cli_reports_bad_metric_and_bad_files_as_json_errors(tmp_path):
    good = tmp_path / "good.json"
    good.write_text(json.dumps(_decay_rows("https://example.com/a", 5)), encoding="utf-8")
    bad_metric = tmp_path / "bad.json"
    bad_metric.write_text(json.dumps(_decay_rows("https://example.com/a", "n/a")), encoding="utf-8")
    binary = tmp_path / "binary.json"
    binary.write_bytes(b"[\xff\xfe]")
    locked = tmp_path / "locked.json"
    locked.write_text("[]", encoding="utf-8")
    locked.chmod(0)
    for argv in ((good, bad_metric), (binary, good), (locked, good)):
        result = subprocess.run(
            [sys.executable, str(DECAY), *map(str, argv)], capture_output=True, text=True)
        if argv[0] is locked and os.access(locked, os.R_OK):
            continue  # running as a user that ignores file modes
        assert result.returncode == 1, result.stderr
        assert "Traceback" not in result.stderr
        assert "error" in json.loads(result.stdout)
    locked.chmod(0o600)


# ---- blog_hygiene.py ---------------------------------------------------------

import blog_hygiene as bh  # noqa: E402


def test_hygiene_never_lazy_loads_the_first_or_priority_images():
    html = (
        '<img src="hero.png" alt="h"><img src="b.png" alt="b" fetchpriority="high">'
        '<img class="card hero-image hero" src="c.png" alt="c"><img src="d.png" alt="d">'
    )
    out, count = bh.fix_html_lazy_loading(html)
    assert count == 1
    assert out.count('loading="lazy"') == 1
    assert '<img loading="lazy" src="d.png" alt="d">' in out
    assert '<img src="hero.png" alt="h">' in out


def test_hygiene_hero_class_on_a_later_image_is_left_alone():
    html = '<img src="a.png" alt="a"><img class="hero" src="b.png" alt="b"><img src="c.png" alt="c">'
    out, count = bh.fix_html_lazy_loading(html)
    assert count == 1 and 'class="hero" src="b.png"' in out and "<img class=\"hero\"" in out


def test_hygiene_ignores_img_text_in_pre_code_and_comments():
    html = (
        '<img src="hero.png" alt="h">'
        '<pre><code>&lt;p&gt;<img src="in-pre.png"></code></pre>'
        '<!-- <img src="in-comment.png"> -->'
        '<p>Use <code><img src="in-code.png"></code> inline.</p>'
        '<img src="real.png" alt="r">'
    )
    out, count = bh.fix_html_lazy_loading(html)
    assert count == 1
    assert 'src="in-pre.png">' in out and 'loading="lazy" src="in-pre' not in out
    assert 'loading="lazy" src="in-comment' not in out
    assert 'loading="lazy" src="in-code' not in out
    assert '<img loading="lazy" src="real.png" alt="r">' in out
    assert bh.find_missing_alt(html) == []  # the sample tags in code are not reported


def test_hygiene_first_image_is_the_first_real_one_not_one_in_a_comment():
    html = '<!-- <img src="x.png"> --><img src="hero.png" alt="h"><img src="b.png" alt="b">'
    out, count = bh.fix_html_lazy_loading(html)
    assert count == 1 and '<img src="hero.png" alt="h">' in out


def test_hygiene_unclosed_pre_protects_to_the_end():
    out, count = bh.fix_html_lazy_loading('<img src="h.png" alt="h"><pre><img src="a.png">')
    assert count == 0


def test_hygiene_cli_binary_input_is_a_json_error(tmp_path):
    page = tmp_path / "page.html"
    page.write_bytes(b"<img src='a.png'>\xff\xfe")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "blog_hygiene.py"), "--html", str(page)],
        capture_output=True, text=True)
    assert result.returncode == 2
    assert "Traceback" not in result.stderr
    assert "error" in json.loads(result.stdout)


# ---- style_learn.py ----------------------------------------------------------

STYLE = ROOT / "scripts" / "style_learn.py"


def _style(*args):
    return subprocess.run([sys.executable, str(STYLE), *map(str, args)], capture_output=True, text=True)


def test_style_learn_missing_path_exits_nonzero_and_keeps_voice_md(tmp_path):
    voice = tmp_path / "VOICE.md"
    voice.write_text("precious voice\n", encoding="utf-8")
    result = _style(tmp_path / "nope", "--output", voice, "--format", "markdown")
    assert result.returncode == 2
    assert "path not found" in result.stderr
    assert voice.read_text(encoding="utf-8") == "precious voice\n"


def test_style_learn_zero_posts_exits_nonzero_and_keeps_voice_md(tmp_path):
    empty = tmp_path / "posts"
    empty.mkdir()
    (empty / "notes.csv").write_text("not a post\n", encoding="utf-8")
    voice = tmp_path / "VOICE.md"
    voice.write_text("precious voice\n", encoding="utf-8")
    result = _style(empty, "--output", voice, "--format", "markdown")
    assert result.returncode == 1
    assert "no readable sample posts" in result.stderr
    assert voice.read_text(encoding="utf-8") == "precious voice\n"
    assert _style(empty).stdout == ""  # no empty profile on stdout either


def test_style_learn_with_posts_still_succeeds(tmp_path):
    post = tmp_path / "a.md"
    post.write_text("---\ntitle: A\n---\n\nThis is a sentence about writing clearly. Short ones help.\n", encoding="utf-8")
    assert _style(post).returncode == 0


# ---- cognitive_load.py -------------------------------------------------------

COGNITIVE = ROOT / "scripts" / "cognitive_load.py"


def _cognitive(*args):
    return subprocess.run([sys.executable, str(COGNITIVE), *map(str, args)], capture_output=True, text=True)


def test_cognitive_load_binary_input_is_a_clean_error(tmp_path):
    binary = tmp_path / "bad.md"
    binary.write_bytes(b"## H\n\xff\xfe\n")
    result = _cognitive(binary)
    assert result.returncode == 2
    assert "Traceback" not in result.stderr
    assert "not valid UTF-8" in result.stderr
    assert "error" in json.loads(result.stdout)


def test_cognitive_load_unreadable_input_is_a_clean_error(tmp_path):
    locked = tmp_path / "locked.md"
    locked.write_text("## H\n\ntext\n", encoding="utf-8")
    locked.chmod(0)
    try:
        if os.access(locked, os.R_OK):
            pytest.skip("running as a user that ignores file modes")
        result = _cognitive(locked)
    finally:
        locked.chmod(0o600)
    assert result.returncode == 2
    assert "Traceback" not in result.stderr


def test_cognitive_load_docstring_thresholds_match_the_code():
    import importlib.util

    spec = importlib.util.spec_from_file_location("wave3_cognitive", COGNITIVE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The boundary values the docstring promises, taken from the real classifier.
    assert module.classify(1.5, 1.5, 2.5) == "healthy"
    assert module.classify(1.51, 1.5, 2.5) == "borderline"
    assert module.classify(2.5, 1.5, 2.5) == "borderline"
    doc = module.__doc__
    assert "<= 1.5 healthy" in doc and "> 1.5 to 2.5 borderline" in doc
    assert "<= 3 healthy, > 3 to 6 borderline, > 6 overloaded" in doc
    source = COGNITIVE.read_text(encoding="utf-8")
    for call in ("classify(new_entity_density, 3, 6)", "classify(numeric_claim_density, 3, 5)",
                 "classify(clause_depth, 1.5, 2.5)"):
        assert call in source


# ---- ai_citation_score.py ------------------------------------------------------

AI_SCORE = ROOT / "scripts" / "ai_citation_score.py"


@pytest.mark.parametrize("content", ["", "---\ntitle: Only frontmatter\n---\n", "   \n\n"])
def test_ai_citation_score_empty_input_is_an_error_not_a_score(tmp_path, content):
    page = tmp_path / "empty.md"
    page.write_text(content, encoding="utf-8")
    result = subprocess.run([sys.executable, str(AI_SCORE), str(page)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "No analyzable text" in json.loads(result.stdout)["error"]


def test_ai_citation_score_real_post_still_scores_and_keeps_the_alias(tmp_path):
    page = tmp_path / "post.md"
    page.write_text((FIXTURES / "blog_pass.md").read_text(encoding="utf-8"), encoding="utf-8")
    result = subprocess.run([sys.executable, str(AI_SCORE), str(page)], capture_output=True, text=True)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["overall"] > 18
    assert data["overall_probability"] == data["overall"]
    assert "DEPRECATED alias" in AI_SCORE.read_text(encoding="utf-8")


# ---- check_secrets.py ----------------------------------------------------------

import importlib.util as _ilu  # noqa: E402

_SECRETS_SPEC = _ilu.spec_from_file_location("wave3_check_secrets", ROOT / "scripts" / "check_secrets.py")
SECRETS = _ilu.module_from_spec(_SECRETS_SPEC)
_SECRETS_SPEC.loader.exec_module(SECRETS)
KEYWORD = {"type": "Secret Keyword"}


@pytest.mark.parametrize("line", [
    'api_key = "YOUR_API_KEY"',
    "GOOGLE_AI_API_KEY=your-key-here",
    '  "password": "YOUR_PASSWORD",',
    'token = "..."',
    'headers = {"Authorization": "Bearer YOUR_TOKEN"}',
    'export GEMINI_API_KEY="/path/to/key"',
])
def test_placeholder_value_is_adjudicated(line):
    assert SECRETS.is_adjudicated("docs/x.md", KEYWORD, line)


# Built from pieces so this file never contains a scannable secret-shaped line.
_NEGATIVE_TEMPLATES = [
    '{k} = "{v}"  # replace with YOUR_KEY later',
    '{k} = "{v}"  # your-old-value was rotated',
    '{k} = "{v}"; other_{k} = "YOUR_OTHER"',
    '# YOUR_KEY goes here: {k} = "{v}"',
    '{k} = "{v}" # /path/to/file',
]


@pytest.mark.parametrize("template", _NEGATIVE_TEMPLATES)
def test_marker_elsewhere_on_the_line_does_not_clear_a_real_secret(template):
    line = template.format(k="sec" + "ret", v="s3cr3t" + "value99")
    assert not SECRETS.is_adjudicated("docs/x.md", KEYWORD, line)


def test_stripe_and_slack_tokens_are_forbidden_patterns(tmp_path, monkeypatch):
    monkeypatch.setattr(SECRETS, "ROOT", tmp_path)
    (tmp_path / "a.txt").write_text("key " + "sk_" + "live_" + "A1" * 12 + "\n")
    (tmp_path / "b.txt").write_text("tok " + "xox" + "b-1234567890-abcdefghij\n")
    labels = {f["type"] for f in SECRETS.scan_forbidden_values()}
    assert {"Stripe key", "Slack token"} <= labels


def test_secret_scan_skips_local_virtualenvs(monkeypatch):
    """A contributor's .venv is not source and must not trip the entropy scan."""
    seen = {}

    class Done:
        returncode = 0
        stdout = '{"results": {}}'
        stderr = ""

    def fake_run(command, **kwargs):
        seen["command"] = command
        return Done()

    monkeypatch.setattr(SECRETS.subprocess, "run", fake_run)
    SECRETS.run_detect_secrets()
    excludes = [seen["command"][i + 1] for i, arg in enumerate(seen["command"]) if arg == "--exclude-files"]
    assert any(".venv" in pattern and "node_modules" in pattern for pattern in excludes)


def test_git_revision_field_is_adjudicated_but_a_bare_hex_secret_is_not():
    hex_finding = {"type": "Hex High Entropy String"}
    revision = '  "revision": "' + "ab12" * 10 + '",'
    assert SECRETS.is_adjudicated("plugins/x/dev/types-source.json", hex_finding, revision)
    bare = '  "token": "' + "ab12" * 10 + '",'
    assert not SECRETS.is_adjudicated("plugins/x/dev/types-source.json", hex_finding, bare)
