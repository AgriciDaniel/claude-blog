"""Atlas Cloud provider tests for scripts/generate_hero.py."""
from __future__ import annotations

import importlib.util
import socket
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HERO_PATH = ROOT / "scripts" / "generate_hero.py"
PREFLIGHT_PATH = ROOT / "scripts" / "blog_preflight.py"


@pytest.fixture()
def hero_module():
    name = "generate_hero_atlas_test"
    spec = importlib.util.spec_from_file_location(name, HERO_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def preflight_module():
    name = "blog_preflight_atlas_test"
    spec = importlib.util.spec_from_file_location(name, PREFLIGHT_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_atlas_is_skipped_without_api_key(hero_module, monkeypatch, tmp_path):
    monkeypatch.delenv("ATLASCLOUD_API_KEY", raising=False)
    monkeypatch.setattr(
        hero_module,
        "_http_post_json",
        lambda *args, **kwargs: pytest.fail("Atlas POST should not run without a key"),
    )

    assert hero_module._try_atlas(
        "Topic", [], tmp_path, 1200, 630, hero_module.DEFAULT_ATLAS_MODEL
    ) is None


def test_preflight_reports_atlas_key_without_exposing_value(
    preflight_module, monkeypatch, tmp_path
):
    monkeypatch.setenv("ATLASCLOUD_API_KEY", "secret-value-not-for-output")

    result = preflight_module.gate_1_capability_discovery(tmp_path, live_tools=[])
    capabilities = result["capabilities"]

    assert capabilities["env_keys_present"]["ATLASCLOUD_API_KEY"] is True
    serialized = (tmp_path / "capabilities.json").read_text(encoding="utf-8")
    assert "secret-value-not-for-output" not in serialized


def test_atlas_submits_once_polls_and_writes_hero(hero_module, monkeypatch, tmp_path):
    monkeypatch.setenv("ATLASCLOUD_API_KEY", "test-key")
    submitted = []
    polls = iter(
        [
            {"code": 200, "data": {"status": "processing"}},
            {
                "code": 200,
                "data": {
                    "status": "completed",
                    "outputs": ["https://cdn.example.test/hero.png"],
                },
            },
        ]
    )

    def fake_post(url, payload, headers=None):
        submitted.append((url, payload, headers))
        return {"code": 200, "data": {"id": "prediction-123"}}

    monkeypatch.setattr(hero_module, "_http_post_json", fake_post)
    monkeypatch.setattr(hero_module, "_http_get_json", lambda *args, **kwargs: next(polls))
    monkeypatch.setattr(hero_module, "_download_image", lambda url: b"\x89PNG\r\n\x1a\nimage")
    monkeypatch.setattr(hero_module, "_fit_image_bytes", lambda data, width, height: data)
    monkeypatch.setattr(hero_module.time, "sleep", lambda delay: None)

    model = "google/nano-banana-2-lite/text-to-image"
    result = hero_module._try_atlas(
        "Reliable systems", ["engineering"], tmp_path, 1200, 630, model
    )

    assert len(submitted) == 1
    _, payload, headers = submitted[0]
    assert payload == {
        "model": model,
        "prompt": hero_module._build_prompt(
            "Reliable systems", ["engineering"], 1200, 630
        ),
        "aspect_ratio": "16:9",
        "resolution": "1k",
    }
    assert headers == {"Authorization": "Bearer test-key"}
    assert result == {
        "source": "atlas",
        "model": model,
        "path": str(tmp_path / "hero.png"),
    }
    assert (tmp_path / "hero.png").read_bytes().startswith(b"\x89PNG")
    credit = (tmp_path / "hero-credit.txt").read_text(encoding="utf-8")
    assert "Atlas Cloud" in credit
    assert model in credit


def test_atlas_post_refuses_private_destination(hero_module, monkeypatch):
    monkeypatch.setattr(
        hero_module.socket,
        "gethostbyname",
        lambda host: "127.0.0.1",
    )
    monkeypatch.setattr(
        hero_module._NO_REDIRECT_OPENER,
        "open",
        lambda *args, **kwargs: pytest.fail("private destinations must not be opened"),
    )

    assert hero_module._http_post_json(
        "https://atlas.example.test/api/v1/model/generateImage",
        {"model": "example", "prompt": "example"},
    ) is None


def test_atlas_post_pins_validated_dns(hero_module, monkeypatch):
    public_info = [
        (
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP,
            "",
            ("93.184.216.34", 443),
        )
    ]
    private_info = [
        (
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP,
            "",
            ("169.254.169.254", 443),
        )
    ]
    dns_calls = 0

    def fake_getaddrinfo(host, port, proto=0, *args, **kwargs):
        nonlocal dns_calls
        dns_calls += 1
        return public_info if dns_calls == 1 else private_info

    class FakeResponse:
        status = 200

        def read(self, size=None):
            return b'{"code":200,"data":{"id":"prediction-123"}}'

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_open(request, timeout=None):
        assert hero_module.socket.getaddrinfo(
            "atlas.example.test", 443, proto=socket.IPPROTO_TCP
        ) == public_info
        return FakeResponse()

    monkeypatch.setattr(
        hero_module.socket,
        "gethostbyname",
        lambda host: "93.184.216.34",
    )
    monkeypatch.setattr(hero_module.socket, "getaddrinfo", fake_getaddrinfo)
    monkeypatch.setattr(hero_module._NO_REDIRECT_OPENER, "open", fake_open)

    result = hero_module._http_post_json(
        "https://atlas.example.test/api/v1/model/generateImage",
        {"model": "example", "prompt": "example"},
    )

    assert result == {"code": 200, "data": {"id": "prediction-123"}}
    assert hero_module.socket.getaddrinfo is fake_getaddrinfo


def test_atlas_failed_prediction_stops_without_download(hero_module, monkeypatch, tmp_path):
    monkeypatch.setenv("ATLASCLOUD_API_KEY", "test-key")
    monkeypatch.setattr(
        hero_module,
        "_http_post_json",
        lambda *args, **kwargs: {"code": 200, "data": {"id": "prediction-123"}},
    )
    monkeypatch.setattr(
        hero_module,
        "_http_get_json",
        lambda *args, **kwargs: {"code": 200, "data": {"status": "failed"}},
    )
    monkeypatch.setattr(hero_module.time, "sleep", lambda delay: None)
    monkeypatch.setattr(
        hero_module,
        "_download_image",
        lambda url: pytest.fail("failed predictions must not download an output"),
    )

    assert hero_module._try_atlas(
        "Topic", [], tmp_path, 1200, 630, hero_module.DEFAULT_ATLAS_MODEL
    ) is None


def test_existing_gemini_path_still_precedes_atlas(hero_module, monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(
        hero_module,
        "_try_gemini",
        lambda *args: calls.append("gemini") or {
            "source": "gemini",
            "path": str(tmp_path / "hero.png"),
        },
    )
    monkeypatch.setattr(
        hero_module,
        "_try_atlas",
        lambda *args: calls.append("atlas") or pytest.fail(
            "Atlas should not run after Gemini succeeds"
        ),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["generate_hero.py", "--topic", "Topic", "--out", str(tmp_path)],
    )

    assert hero_module.main() == 0
    assert calls == ["gemini"]
