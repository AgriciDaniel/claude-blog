"""Behavioral contracts for current Google Search guidance."""

from __future__ import annotations

import datetime as dt
import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT_PATH = ROOT / "scripts" / "blog_preflight.py"
GSC_SCRIPT_DIR = ROOT / "skills" / "blog-google" / "scripts"
GSC_INSPECT_PATH = GSC_SCRIPT_DIR / "gsc_inspect.py"
GSC_RUNNER_PATH = GSC_SCRIPT_DIR / "run.py"


@pytest.fixture(scope="module")
def preflight():
    spec = importlib.util.spec_from_file_location("blog_preflight_google_contract", PREFLIGHT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def gsc_inspect():
    sys.path.insert(0, str(GSC_SCRIPT_DIR))
    try:
        spec = importlib.util.spec_from_file_location(
            "gsc_inspect_google_contract", GSC_INSPECT_PATH
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(GSC_SCRIPT_DIR))


@pytest.fixture(scope="module")
def gsc_runner():
    spec = importlib.util.spec_from_file_location(
        "gsc_runner_google_contract", GSC_RUNNER_PATH
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _critical_html() -> bytes:
    return (
        b"<title>Fixture</title>"
        b'<meta name="description" content="Fixture">'
        b'<link rel="canonical" href="https://example.com/post">'
        b'<script type="application/ld+json">{"@type":"BlogPosting"}</script>'
        b"<article>Primary content</article>"
    )


def test_googlebot_check_flags_only_critical_content_after_cutoff(preflight) -> None:
    filler = b"x" * preflight.GOOGLEBOT_HTML_BYTE_LIMIT
    hidden = preflight._googlebot_html_prefix_check(filler + _critical_html())
    visible = preflight._googlebot_html_prefix_check(_critical_html() + filler)

    assert set(hidden["critical_after_cutoff"]) == {
        "title",
        "meta",
        "canonical",
        "json_ld",
        "main_content",
    }
    assert hidden["violations"] == []
    assert len(hidden["warnings"]) == 5
    assert visible["critical_after_cutoff"] == []
    assert visible["violations"] == []
    assert visible["warnings"] == []


def test_googlebot_check_warns_on_inline_bloat_without_ranking_claim(preflight) -> None:
    payload = (
        b"<style>"
        + b"x" * (preflight.INLINE_BLOAT_WARNING_BYTES + 1)
        + b"</style>"
        + _critical_html()
    )
    result = preflight._googlebot_html_prefix_check(payload)

    assert result["violations"] == []
    assert len(result["warnings"]) == 1
    assert "not a ranking factor" in result["warnings"][0]


def test_gate_5_warns_without_blocking_on_first_2mb_visibility(
    preflight, tmp_path: Path
) -> None:
    slug = "cutoff-fixture"
    (tmp_path / f"{slug}.md").write_text("# Fixture\n", encoding="utf-8")
    (tmp_path / f"{slug}.pdf").write_bytes(b"%PDF-1.4\n")
    critical = (
        '<title>Fixture</title>'
        '<meta name="description" content="Fixture">'
        '<link rel="canonical" href="https://example.com/post">'
        '<script type="application/ld+json">'
        '{"@type":"BlogPosting","headline":"Fixture","image":"hero.jpg",'
        '"datePublished":"2026-07-23","author":{"name":"Tester"},"wordCount":2}'
        "</script><article>Primary content</article>"
    )
    (tmp_path / f"{slug}.html").write_text(
        "x" * preflight.GOOGLEBOT_HTML_BYTE_LIMIT + critical,
        encoding="utf-8",
    )

    result = preflight.gate_5_asset_link_integrity(tmp_path, slug)

    assert result["passed"] is True
    assert set(result["googlebot_byte_check"]["critical_after_cutoff"]) == {
        "title",
        "meta",
        "canonical",
        "json_ld",
        "main_content",
    }
    assert not any("first-2MB cutoff" in item for item in result["violations"])
    assert sum("first-2MB cutoff" in item for item in result["warnings"]) == 5


def _rendered_gate_3_result(*, consistent: bool = True) -> dict:
    rendered = {
        "jsonLdValid": True,
        "jsonLdType": "BlogPosting",
        "jsonLdMissingFields": [],
        "jsonLdVisibleConsistent": consistent,
        "jsonLdConsistencyMismatches": [] if consistent else ["headline"],
        "jsonLdWordCount": 3,
    }
    return {
        "passed": True,
        "per_viewport": {
            name: {"result": dict(rendered)}
            for name in ("mobile", "tablet", "desktop")
        },
    }


def _write_dynamic_jsonld_artifacts(tmp_path: Path, slug: str) -> None:
    (tmp_path / f"{slug}.md").write_text("# Fixture\n", encoding="utf-8")
    (tmp_path / f"{slug}.pdf").write_bytes(b"%PDF-1.4\n")
    (tmp_path / f"{slug}.html").write_text(
        '<title>Fixture</title><meta name="description" content="Fixture">'
        '<link rel="canonical" href="https://example.com/post">'
        "<script>const node=document.createElement('script');"
        "node.type='application/'+'ld+json';"
        "node.textContent=JSON.stringify({"
        "'@type':'BlogPosting','headline':'Fixture','image':'hero.jpg',"
        "'datePublished':'2026-07-23','author':{'name':'Tester'},'wordCount':3"
        "});document.head.appendChild(node);</script>"
        "<article><h1>Fixture</h1>Primary content</article>",
        encoding="utf-8",
    )


def test_gate_5_accepts_conclusive_rendered_dom_jsonld(
    preflight, tmp_path: Path
) -> None:
    slug = "dynamic-schema"
    _write_dynamic_jsonld_artifacts(tmp_path, slug)
    handoff = preflight._rendered_jsonld_handoff(_rendered_gate_3_result())

    result = preflight.gate_5_asset_link_integrity(
        tmp_path,
        slug,
        rendered_schema_validation=handoff,
    )

    assert result["passed"] is True
    assert result["json_ld_valid"] is True
    assert result["schema_validation_source"] == "rendered_dom"
    assert any("rendered DOM" in item for item in result["warnings"])


def test_gate_5_rejects_dynamic_jsonld_when_rendered_validation_is_inconclusive(
    preflight, tmp_path: Path
) -> None:
    slug = "dynamic-schema"
    _write_dynamic_jsonld_artifacts(tmp_path, slug)
    handoff = preflight._rendered_jsonld_handoff(
        _rendered_gate_3_result(consistent=False)
    )

    assert handoff["available"] is False
    result = preflight.gate_5_asset_link_integrity(
        tmp_path,
        slug,
        rendered_schema_validation=handoff,
    )
    assert result["passed"] is False
    assert any("no source JSON-LD" in item for item in result["violations"])


def test_discover_checks_require_explicit_target_or_data_signal(
    preflight, tmp_path: Path
) -> None:
    parser = preflight._MetaParser()
    parser.feed(
        '<html><head><meta property="og:image" content="hero.jpg">'
        '<meta property="og:image:width" content="640">'
        '<meta property="og:image:height" content="360"></head></html>'
    )

    enabled, warning = preflight._discover_target_signal(tmp_path)
    inactive = preflight._discover_preflight_check(parser, enabled)
    assert warning is None
    assert inactive == {"enabled": False, "warnings": []}

    (tmp_path / preflight.PREFLIGHT_TARGETS_FILE).write_text(
        '{"targets":["discover"]}\n', encoding="utf-8"
    )
    enabled, warning = preflight._discover_target_signal(tmp_path)
    active = preflight._discover_preflight_check(parser, enabled)
    assert warning is None
    assert active["enabled"] is True
    assert any("1200px" in item for item in active["warnings"])
    assert any("max-image-preview:large" in item for item in active["warnings"])


def test_history_api_syntax_alone_never_triggers_back_button_violation(preflight) -> None:
    syntax_only = preflight._classify_back_button_behavior(
        {
            "history_api_syntax_detected": True,
            "attempted_back": False,
            "returned_to_previous": False,
        }
    )
    obstructed = preflight._classify_back_button_behavior(
        {
            "history_api_syntax_detected": False,
            "attempted_back": True,
            "observation_complete": True,
            "returned_to_previous": False,
        }
    )

    assert syntax_only["violation"] is None
    assert syntax_only["obstructed"] is False
    assert obstructed["violation"]
    assert obstructed["obstructed"] is True


def test_back_button_timeout_is_inconclusive_not_a_violation(preflight) -> None:
    result = preflight._classify_back_button_behavior(
        {
            "attempted_back": True,
            "observation_complete": False,
            "returned_to_previous": False,
            "error": "navigation timeout",
        }
    )

    assert result["checked"] is True
    assert result["conclusive"] is False
    assert result["obstructed"] is False
    assert result["violation"] is None


@pytest.mark.parametrize("age_days", [0, 7, 14])
def test_recent_correct_canonical_fix_is_pending(gsc_inspect, age_days: int) -> None:
    today = dt.date(2026, 7, 23)
    result = gsc_inspect.classify_canonical_reevaluation(
        inspection_url="https://example.com/new",
        google_canonical="https://example.com/old",
        user_canonical="https://example.com/new",
        fix_date=today - dt.timedelta(days=age_days),
        today=today,
    )

    assert result["classification"] == "PENDING_REEVALUATION"
    assert result["pending_reevaluation"] is True
    assert result["implementation_correct"] is True


def test_old_or_incorrect_canonical_fix_is_not_pending(gsc_inspect) -> None:
    today = dt.date(2026, 7, 23)
    old = gsc_inspect.classify_canonical_reevaluation(
        inspection_url="https://example.com/new",
        google_canonical="https://example.com/old",
        user_canonical="https://example.com/new",
        fix_date=today - dt.timedelta(days=15),
        today=today,
    )
    incorrect = gsc_inspect.classify_canonical_reevaluation(
        inspection_url="https://example.com/new",
        google_canonical="https://example.com/old",
        user_canonical="https://example.com/wrong",
        fix_date=today,
        today=today,
    )

    assert old["classification"] == "MISMATCH"
    assert old["pending_reevaluation"] is False
    assert incorrect["classification"] == "MISMATCH"
    assert incorrect["implementation_correct"] is False
    assert incorrect["pending_reevaluation"] is False


def test_inspection_keeps_google_verdict_and_adds_pending_classification(
    gsc_inspect, monkeypatch
) -> None:
    response = {
        "inspectionResult": {
            "indexStatusResult": {
                "verdict": "FAIL",
                "googleCanonical": "https://example.com/old",
                "userCanonical": "https://example.com/new",
            }
        }
    }

    class _Request:
        pass

    class _Index:
        def inspect(self, body):
            assert body["inspectionUrl"] == "https://example.com/new"
            return _Request()

    class _UrlInspection:
        def index(self):
            return _Index()

    class _Service:
        def urlInspection(self):
            return _UrlInspection()

    monkeypatch.setattr(gsc_inspect, "execute_with_retries", lambda request: response)
    result = gsc_inspect.inspect_url(
        "https://example.com/new",
        "sc-domain:example.com",
        service=_Service(),
        canonical_fix_date="2026-07-20",
        today=dt.date(2026, 7, 23),
    )

    assert result["verdict"] == "FAIL"
    assert result["canonical"]["classification"] == "PENDING_REEVALUATION"
    assert result["canonical"]["pending_reevaluation"] is True


def test_google_runner_forwards_canonical_reevaluation_flags(
    gsc_runner, monkeypatch
) -> None:
    captured: dict[str, list[str]] = {}

    class _Completed:
        returncode = 0

    def fake_run(command):
        captured["command"] = [str(part) for part in command]
        return _Completed()

    monkeypatch.setattr(gsc_runner, "ensure_venv", lambda: Path("/venv/bin/python"))
    monkeypatch.setattr(gsc_runner.subprocess, "run", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run.py",
            "gsc_inspect",
            "https://example.com/new",
            "--canonical-fix-date",
            "2026-07-20",
            "--expected-canonical",
            "https://example.com/new",
        ],
    )

    with pytest.raises(SystemExit) as exc:
        gsc_runner.main()

    assert exc.value.code == 0
    assert captured["command"][-4:] == [
        "--canonical-fix-date",
        "2026-07-20",
        "--expected-canonical",
        "https://example.com/new",
    ]
