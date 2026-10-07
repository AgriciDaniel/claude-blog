"""Focused regressions for the October 2026 runtime review."""

from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import shutil
import subprocess
import sys
import types
import urllib.error
import urllib.parse
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def preflight():
    return _load("runtime_preflight", "scripts/blog_preflight.py")


@pytest.fixture()
def hero():
    return _load("runtime_hero", "scripts/generate_hero.py")


def test_gate_3_without_renderer_blocks_strict_but_no_strict_preserves_blocked_report(
    tmp_path: Path,
) -> None:
    # -S omits site-packages, which makes both optional browser renderers
    # unavailable without altering the configured test environment.
    strict = subprocess.run(
        [
            sys.executable,
            "-S",
            str(ROOT / "scripts" / "blog_preflight.py"),
            "--draft",
            str(tmp_path),
            "--gate",
            "3",
            "--strict",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert strict.returncode == 1, strict.stderr
    strict_report = json.loads((tmp_path / "preflight-report.json").read_text())
    assert strict_report["blocked"] is True
    assert strict_report["gates"][0]["passed"] is False

    bypass = subprocess.run(
        [
            sys.executable,
            "-S",
            str(ROOT / "scripts" / "blog_preflight.py"),
            "--draft",
            str(tmp_path),
            "--gate",
            "3",
            "--no-strict",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert bypass.returncode == 0, bypass.stderr
    assert "contract bypassed" in bypass.stderr
    bypass_report = json.loads((tmp_path / "preflight-report.json").read_text())
    assert bypass_report["blocked"] is True
    assert bypass_report["strict"] is False


def test_http_head_falls_back_to_bounded_get(preflight, monkeypatch) -> None:
    public_info = [(2, 1, 6, "", ("93.184.216.34", 443))]
    monkeypatch.setattr(
        preflight,
        "_resolve_public_http_url",
        lambda _url: (True, None, "example.com", 443, public_info),
    )
    calls: list[tuple[str, str | None]] = []

    class Response:
        status = 206
        headers = {}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, size):
            assert size == 1
            return b"x"

    class Opener:
        def open(self, request, timeout=None):
            method = request.get_method()
            calls.append((method, request.headers.get("Range")))
            if method == "HEAD":
                raise urllib.error.HTTPError(
                    request.full_url, 405, "Method Not Allowed", {}, None
                )
            return Response()

    monkeypatch.setattr(preflight, "_PREFLIGHT_NO_REDIRECT_OPENER", Opener())

    assert preflight._http_head("https://example.com/post") == 206
    assert calls == [("HEAD", None), ("GET", "bytes=0-0")]


def test_http_head_accepts_only_validated_redirect(preflight, monkeypatch) -> None:
    public_info = [(2, 1, 6, "", ("93.184.216.34", 443))]
    monkeypatch.setattr(
        preflight,
        "_resolve_public_http_url",
        lambda _url: (True, None, "example.com", 443, public_info),
    )

    class Opener:
        def open(self, request, timeout=None):
            raise urllib.error.HTTPError(
                request.full_url,
                302,
                "Found",
                {"Location": "https://redirect.example/final"},
                None,
            )

    monkeypatch.setattr(preflight, "_PREFLIGHT_NO_REDIRECT_OPENER", Opener())
    monkeypatch.setattr(preflight, "_safe_http_url", lambda _url: (True, None))
    assert preflight._http_head("https://example.com/post") == 302

    monkeypatch.setattr(
        preflight,
        "_safe_http_url",
        lambda _url: (False, "resolved address is not public"),
    )
    assert preflight._http_head("https://example.com/post") == 0


def _write_gate_5_fixture(directory: Path, external_url: str) -> None:
    (directory / "post.md").write_text("# Fixture\n", encoding="utf-8")
    (directory / "post.pdf").write_bytes(b"%PDF-1.4\n")
    (directory / "hero.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (directory / "post.html").write_text(
        '<!doctype html><html><head>'
        '<link rel="canonical" href="https://example.com/post">'
        '<meta property="og:image" content="hero.png">'
        '<script type="application/ld+json">'
        '{"@type":"BlogPosting","headline":"Fixture","image":"hero.png",'
        '"datePublished":"2026-10-07","author":{"name":"Tester"},"wordCount":2}'
        '</script></head><body><article>'
        f'<a href="{external_url}">source</a> word'
        '</article></body></html>',
        encoding="utf-8",
    )



@pytest.mark.parametrize("status, expected", [(200, True), (206, True), (302, True), (403, False)])
def test_external_image_validation_is_safe_and_does_not_crash(preflight, monkeypatch, tmp_path: Path, status: int, expected: bool) -> None:
    _write_gate_5_fixture(tmp_path, "https://example.com/source")
    html = tmp_path / "post.html"
    html.write_text(html.read_text().replace("</article>", '<img src="https://example.com/image.png" alt="Fixture"></article>'))
    monkeypatch.setattr(preflight, "_safe_http_url", lambda _url: (True, None))
    monkeypatch.setattr(preflight, "_http_head", lambda url: status if url.endswith(".png") else 200)
    result = preflight.gate_5_asset_link_integrity(tmp_path)
    assert result["passed"] is expected
    if not expected:
        assert any("img src returned 403" in violation for violation in result["violations"])


def test_external_links_allowed_is_exact_and_limited_to_403_405(
    preflight, monkeypatch, tmp_path: Path
) -> None:
    allowed_url = "https://blocked.example/source"
    _write_gate_5_fixture(tmp_path, allowed_url)
    (tmp_path / "external-links.allowed").write_text(
        f"# Documented publisher block\n{allowed_url}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(preflight, "_safe_http_url", lambda _url: (True, None))
    monkeypatch.setattr(preflight, "_http_head", lambda _url: 403)

    allowed = preflight.gate_5_asset_link_integrity(tmp_path)
    assert allowed["passed"] is True
    assert any("documented 403" in warning for warning in allowed["warnings"])

    (tmp_path / "external-links.allowed").write_text(
        "https://blocked.example/different\n",
        encoding="utf-8",
    )
    unlisted = preflight.gate_5_asset_link_integrity(tmp_path)
    assert unlisted["passed"] is False
    assert any("link returned 403" in item for item in unlisted["violations"])

    (tmp_path / "external-links.allowed").write_text(
        f"{allowed_url}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(preflight, "_http_head", lambda _url: 500)
    server_error = preflight.gate_5_asset_link_integrity(tmp_path)
    assert server_error["passed"] is False
    assert any("link returned 500" in item for item in server_error["violations"])


def test_external_links_allowed_never_bypasses_url_safety(
    preflight, monkeypatch, tmp_path: Path
) -> None:
    url = "http://metadata.example/latest"
    _write_gate_5_fixture(tmp_path, url)
    (tmp_path / "external-links.allowed").write_text(f"{url}\n", encoding="utf-8")
    monkeypatch.setattr(
        preflight,
        "_safe_http_url",
        lambda _url: (False, "resolved address is not public"),
    )
    monkeypatch.setattr(
        preflight,
        "_http_head",
        lambda _url: pytest.fail("unsafe URL must not be probed"),
    )

    result = preflight.gate_5_asset_link_integrity(tmp_path)
    assert result["passed"] is False
    assert any("URL safety policy" in item for item in result["violations"])


def test_openverse_uses_canonical_host_and_progressively_broader_queries(
    hero, monkeypatch, tmp_path: Path
) -> None:
    calls: list[str] = []

    def fake_json(url: str):
        calls.append(url)
        if len(calls) == 1:
            return {"results": []}
        return {
            "results": [
                {
                    "url": "https://images.example/hero.jpg",
                    "title": "Fixture",
                    "creator": "Creator",
                    "license": "by",
                    "source": "fixture",
                }
            ]
        }

    jpeg = b"\xff\xd8\xfffixture"
    monkeypatch.setattr(hero, "_http_get_json", fake_json)
    monkeypatch.setattr(hero, "_download_image", lambda _url: jpeg)
    monkeypatch.setattr(hero, "_fit_image_bytes", lambda data, _w, _h: data)

    result = hero._try_openverse(
        "WordPress Caching Layers Explained",
        ["wordpress", "caching", "performance"],
        tmp_path,
        1200,
        630,
    )

    assert hero.OPENVERSE_API == "https://api.openverse.org/v1/images/"
    assert result is not None and result["path"].endswith("hero.jpg")
    assert len(calls) == 2
    assert all(url.startswith(hero.OPENVERSE_API) for url in calls)
    first_query = urllib.parse.parse_qs(urllib.parse.urlsplit(calls[0]).query)["q"][0]
    second_query = urllib.parse.parse_qs(urllib.parse.urlsplit(calls[1]).query)["q"][0]
    assert first_query == "WordPress Caching Layers Explained wordpress caching performance"
    assert second_query == "wordpress caching performance"


def test_gemini_requests_jpeg_and_names_output_from_actual_bytes(
    hero, monkeypatch, tmp_path: Path
) -> None:
    captured: dict = {}
    jpeg = b"\xff\xd8\xfffixture"

    class Interactions:
        def create(self, **kwargs):
            captured.update(kwargs)
            return types.SimpleNamespace(
                output_image=types.SimpleNamespace(data=jpeg)
            )

    class Client:
        def __init__(self, api_key):
            captured["api_key"] = api_key
            self.interactions = Interactions()

    fake_genai = types.SimpleNamespace(Client=Client)
    fake_google = types.ModuleType("google")
    fake_google.genai = fake_genai
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)
    monkeypatch.setenv("GOOGLE_AI_API_KEY", "test-key")
    monkeypatch.setattr(hero, "_fit_image_bytes", lambda data, _w, _h: data)

    result = hero._try_gemini("Fixture", [], tmp_path, 1200, 630, "test-model")

    assert result is not None and result["path"].endswith("hero.jpg")
    assert captured["response_format"]["mime_type"] == "image/jpeg"
    assert (tmp_path / "hero.jpg").read_bytes() == jpeg


@pytest.mark.parametrize("extension", ["jpg", "jpeg", "webp"])
def test_renderer_discovers_supported_non_png_hero(
    extension: str, tmp_path: Path
) -> None:
    source = tmp_path / "fixture.md"
    source.write_text(
        """---
title: Fixture
description: Renderer hero discovery fixture.
date: 2026-10-07
author: Tester
---

Reader-visible body.
""",
        encoding="utf-8",
    )
    (tmp_path / f"hero.{extension}").write_bytes(b"fixture")

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "blog_render.py"),
            "--md",
            str(source),
            "--out-dir",
            str(tmp_path),
            "--pdf-engine",
            "none",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    rendered = (tmp_path / "fixture.html").read_text(encoding="utf-8")
    assert f'<img src="hero.{extension}"' in rendered


def test_batch_recurses_layouts_and_skips_artifacts_and_symlink_escape(
    monkeypatch, tmp_path: Path
) -> None:
    analyzer = _load("runtime_analyzer", "scripts/analyze_blog.py")
    included = [
        "app/blog/next-post/page.mdx",
        "src/content/blog/astro-post.md",
        "content/posts/hugo-post/index.md",
    ]
    excluded = [
        "node_modules/pkg/readme.md",
        "vendor/pkg/readme.md",
        "dist/rendered.html",
        "outputs/review/report.md",
        "artifacts/export/post.html",
    ]
    for relative in included + excluded:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Fixture\n", encoding="utf-8")

    outside = tmp_path.parent / f"{tmp_path.name}-outside.md"
    outside.write_text("# Outside\n", encoding="utf-8")
    try:
        (tmp_path / "escaped.md").symlink_to(outside)
    except OSError:
        pass

    def fake_analyze(path: str) -> dict:
        return {
            "file": path,
            "score": {"total": 75},
            "paragraphs": {"total_word_count": 10},
        }

    monkeypatch.setattr(analyzer, "analyze_file", fake_analyze)
    result = analyzer._process_batch(tmp_path, "name")
    found = {
        Path(item["file"]).relative_to(tmp_path).as_posix()
        for item in result["results"]
    }
    assert found == set(included)
    assert result["count"] == len(included)
    assert [item["file"] for item in result["results"]] == sorted(
        item["file"] for item in result["results"]
    )


@pytest.mark.parametrize("supporting_type", ["Organization", "BreadcrumbList"])
def test_schema_full_credit_requires_article_person_and_supporting_type(
    supporting_type: str, tmp_path: Path
) -> None:
    analyzer = _load(f"runtime_schema_{supporting_type}", "scripts/analyze_blog.py")
    post = tmp_path / f"schema-{supporting_type}.md"
    post.write_text(
        """---
title: Evidence Review
author: Jane Doe
---
# Evidence Review

## Evidence

Reader-visible evidence.

<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
  {"@type":"Article","author":{"@type":"Person","name":"Jane Doe"}},
  {"@type":"SUPPORT_TYPE"}
]}
</script>
""".replace("SUPPORT_TYPE", supporting_type),
        encoding="utf-8",
    )

    result = analyzer.analyze_file(str(post))
    schema_points = result["score"]["category_details"]["technical_elements"][
        "breakdown"
    ]["schema"]
    assert schema_points == 4
    assert schema_points <= 4


def test_indonesian_profile_is_declared_only_and_recognizes_supported_signals(
    tmp_path: Path,
) -> None:
    analyzer = _load("runtime_indonesian", "scripts/analyze_blog.py")
    body = """# Audit Iklan Google

## Jawaban singkat

**Iklan Google boros** adalah kondisi ketika biaya keluar tanpa hasil.

## Metode

Kami mengaudit 40 akun klien sepanjang 2025 dan mencatat 3 pola.

Lihat [tentang kami](/tentang-kami) dan [hubungi kami](/kontak).
"""
    declared = tmp_path / "declared.md"
    declared.write_text(
        "---\ntitle: Audit Iklan Google\nauthor: Tim Oasisme\nlang: id\n---\n" + body,
        encoding="utf-8",
    )
    undeclared = tmp_path / "undeclared.md"
    undeclared.write_text(
        "---\ntitle: Audit Iklan Google\nauthor: Tim Oasisme\n---\n" + body,
        encoding="utf-8",
    )

    result = analyzer.analyze_file(str(declared))
    assert result["language"] == "id"
    assert result["readability"]["reading_model"] == "flesch"
    assert result["ai_citation_readiness"]["has_tldr"] is True
    assert result["ai_citation_readiness"]["entity_definitions"] >= 1
    assert result["originality"]["methodology_count"] >= 1
    assert result["originality"]["unsupported_experience_claims"] == 0
    assert analyzer.analyze_file(str(undeclared))["language"] == "en"


def test_runtime_wrappers_require_explicit_setup_without_installing(
    monkeypatch, tmp_path: Path
) -> None:
    audio = _load("runtime_audio_runner", "skills/blog-audio/scripts/run.py")
    notebook = _load(
        "runtime_notebook_runner", "skills/blog-notebooklm/scripts/run.py"
    )
    missing_python = tmp_path / "missing" / "python"
    monkeypatch.setattr(audio, "get_venv_python", lambda: missing_python)
    monkeypatch.setattr(notebook, "get_venv_python", lambda: missing_python)
    monkeypatch.setattr(
        audio.subprocess,
        "run",
        lambda *_args, **_kwargs: pytest.fail("audio runner must not install"),
    )
    monkeypatch.setattr(
        notebook.subprocess,
        "run",
        lambda *_args, **_kwargs: pytest.fail("notebook runner must not install"),
    )

    assert audio.ensure_venv() is None
    with pytest.raises(SystemExit) as exc:
        notebook.ensure_venv()
    assert exc.value.code == 1


@pytest.mark.parametrize(
    ("source", "script_name"),
    [
        ("skills/blog-audio/scripts/run.py", "voices.py"),
        ("skills/blog-notebooklm/scripts/run.py", "ask_question.py"),
    ],
)
def test_fresh_wrapper_command_never_creates_environment(
    source: str, script_name: str, tmp_path: Path
) -> None:
    skill = tmp_path / Path(source).parts[-3]
    scripts = skill / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy2(ROOT / source, scripts / "run.py")
    shutil.copy2((ROOT / source).with_name("runtime_paths.py"), scripts / "runtime_paths.py")
    (scripts / script_name).write_text("print('should not run')\n", encoding="utf-8")
    (scripts / "requirements.lock").write_text("fixture\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(scripts / "run.py"), script_name],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "setup required" in (result.stdout + result.stderr).lower()
    assert not (skill / ".venv").exists()


@pytest.mark.parametrize(
    ("source", "script_name", "needs_stamp"),
    [
        ("skills/blog-audio/scripts/run.py", "voices.py", False),
        ("skills/blog-notebooklm/scripts/run.py", "ask_question.py", True),
    ],
)
def test_configured_wrapper_still_runs_existing_environment(
    source: str, script_name: str, needs_stamp: bool, tmp_path: Path
) -> None:
    skill = tmp_path / Path(source).parts[-3]
    scripts = skill / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy2(ROOT / source, scripts / "run.py")
    shutil.copy2((ROOT / source).with_name("runtime_paths.py"), scripts / "runtime_paths.py")
    (scripts / script_name).write_text("print('configured-ok')\n", encoding="utf-8")
    lock = scripts / "requirements.lock"
    lock.write_text("fixture\n", encoding="utf-8")
    interpreter = skill / ".venv" / ("Scripts" if os.name == "nt" else "bin")
    interpreter.mkdir(parents=True)
    executable = interpreter / ("python.exe" if os.name == "nt" else "python")
    try:
        executable.symlink_to(sys.executable)
    except OSError:
        shutil.copy2(sys.executable, executable)
    if needs_stamp:
        (skill / ".venv" / ".requirements.stamp").write_text(
            hashlib.sha256(lock.read_bytes()).hexdigest(),
            encoding="utf-8",
        )

    result = subprocess.run(
        [sys.executable, str(scripts / "run.py"), script_name],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "configured-ok" in result.stdout


def test_notebook_setup_run_mode_does_not_call_mutating_setup(monkeypatch) -> None:
    setup = _load(
        "runtime_notebook_setup",
        "skills/blog-notebooklm/scripts/setup_environment.py",
    )
    environment = setup.SkillEnvironment()
    monkeypatch.setattr(environment, "runtime_ready", lambda: False)
    monkeypatch.setattr(
        environment,
        "ensure_venv",
        lambda: pytest.fail("--run must not trigger environment setup"),
    )

    assert environment.run_script("ask_question.py", ["question"]) == 1


def test_weasyprint_70_fetcher_preserves_local_asset_boundary(monkeypatch, tmp_path: Path) -> None:
    renderer = _load("runtime_weasy70", "scripts/blog_render.py")
    page = tmp_path / "post.html"
    page.write_text("<h1>Fixture</h1>")
    hero = tmp_path / "hero.png"
    hero.write_bytes(b"fixture")
    outside = tmp_path.parent / "unowned-image.png"
    captured = {}

    class URLFetcher:
        def __init__(self, **kwargs):
            captured["options"] = kwargs
        def fetch(self, url, headers=None):
            captured["fetched"] = url
            return b"fixture"

    class HTML:
        def __init__(self, *, filename, url_fetcher):
            self.fetcher = url_fetcher
        def write_pdf(self, target):
            assert self.fetcher.fetch(hero.as_uri()) == b"fixture"
            for refused in ("https://example.com/image.png", outside.as_uri()):
                with pytest.raises(ValueError, match="blocked external PDF asset"):
                    self.fetcher.fetch(refused)
            Path(target).write_bytes(b"%PDF-1.7\nfixture")

    package = types.ModuleType("weasyprint")
    package.HTML = HTML
    urls = types.ModuleType("weasyprint.urls")
    urls.URLFetcher = URLFetcher
    monkeypatch.setitem(sys.modules, "weasyprint", package)
    monkeypatch.setitem(sys.modules, "weasyprint.urls", urls)
    assert renderer._render_pdf(page, tmp_path / "post.pdf", "weasyprint") is True
    assert captured["fetched"] == hero.as_uri()
    assert captured["options"] == {"allowed_protocols": ("file",), "allow_redirects": False, "fail_on_errors": True}
