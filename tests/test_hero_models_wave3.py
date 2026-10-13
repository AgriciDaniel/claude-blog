"""Hero generation defaults and the paid-model fallback ladder.

Google's image-generation docs call gemini-3.1-flash-image the previous
generation and recommend gemini-nano-banana-2.1 for new projects. The ladder
must not keep retrying other models after an error no model can fix (key,
billing or quota), and it must accept either documented key variable.
"""

from __future__ import annotations

import base64
import importlib.util
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HERO = ROOT / "scripts" / "generate_hero.py"

# A valid 1x1 PNG, base64 encoded.
PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


def _load():
    spec = importlib.util.spec_from_file_location("hero_models_wave3", HERO)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def hero(monkeypatch):
    monkeypatch.delenv("NANOBANANA_MODEL", raising=False)
    return _load()


def _fake_genai(monkeypatch, behaviours):
    """Install a fake google.genai whose interactions.create follows `behaviours`."""
    calls = []

    class Interactions:
        def create(self, model, input, response_format):  # noqa: A002 - SDK name
            calls.append(model)
            outcome = behaviours.get(model, RuntimeError("model unavailable"))
            if isinstance(outcome, Exception):
                raise outcome
            return types.SimpleNamespace(output_image=types.SimpleNamespace(data=outcome))

    class Client:
        def __init__(self, api_key):
            self.api_key = api_key
            self.interactions = Interactions()

    genai = types.ModuleType("google.genai")
    genai.Client = Client
    google = types.ModuleType("google")
    google.genai = genai
    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.genai", genai)
    return calls


def test_default_model_is_the_current_recommended_image_model(hero):
    assert hero.DEFAULT_GEMINI_MODEL == "gemini-nano-banana-2.1"
    assert hero.GEMINI_IMAGE_MODELS[0] == "gemini-nano-banana-2.1"
    assert "gemini-3.1-flash-image" in hero.GEMINI_IMAGE_MODELS


def test_environment_override_still_wins(monkeypatch):
    monkeypatch.setenv("NANOBANANA_MODEL", "gemini-3-pro-image")
    assert _load().DEFAULT_GEMINI_MODEL == "gemini-3-pro-image"


def test_gemini_api_key_variable_is_accepted(hero, monkeypatch, tmp_path):
    monkeypatch.delenv("GOOGLE_AI_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key-for-test")
    calls = _fake_genai(monkeypatch, {"gemini-nano-banana-2.1": PNG_1X1})
    result = hero._try_gemini("topic", ["tag"], tmp_path, 1200, 630, hero.DEFAULT_GEMINI_MODEL)
    assert calls == ["gemini-nano-banana-2.1"]
    assert result and result["model"] == "gemini-nano-banana-2.1"


def test_no_key_means_no_call(hero, monkeypatch, tmp_path):
    monkeypatch.delenv("GOOGLE_AI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    calls = _fake_genai(monkeypatch, {})
    assert hero._try_gemini("topic", [], tmp_path, 1200, 630, hero.DEFAULT_GEMINI_MODEL) is None
    assert calls == []


@pytest.mark.parametrize(
    "message",
    [
        "429 RESOURCE_EXHAUSTED: quota exceeded",
        "403 PERMISSION_DENIED",
        "400 API key not valid. Please pass a valid API key.",
        "billing account disabled",
    ],
)
def test_unfixable_errors_stop_the_ladder(hero, monkeypatch, tmp_path, message):
    monkeypatch.setenv("GOOGLE_AI_API_KEY", "fake-key-for-test")
    calls = _fake_genai(monkeypatch, {"gemini-nano-banana-2.1": RuntimeError(message)})
    assert hero._try_gemini("topic", [], tmp_path, 1200, 630, hero.DEFAULT_GEMINI_MODEL) is None
    assert calls == ["gemini-nano-banana-2.1"]


def test_model_specific_errors_still_fall_back_to_the_next_model(hero, monkeypatch, tmp_path):
    monkeypatch.setenv("GOOGLE_AI_API_KEY", "fake-key-for-test")
    calls = _fake_genai(
        monkeypatch,
        {
            "gemini-nano-banana-2.1": RuntimeError("model not found"),
            "gemini-3.1-flash-image": PNG_1X1,
        },
    )
    result = hero._try_gemini("topic", [], tmp_path, 1200, 630, hero.DEFAULT_GEMINI_MODEL)
    assert calls[:2] == ["gemini-nano-banana-2.1", "gemini-3.1-flash-image"]
    assert result and result["model"] == "gemini-3.1-flash-image"


def test_error_text_never_contains_the_key(hero, monkeypatch, tmp_path, capsys):
    # Built at runtime so the repo secret scanner never sees a key-shaped literal.
    fake_value = "AI" + "za" + "FAKE" * 8 + "abc"
    monkeypatch.setenv("GOOGLE_AI_API_KEY", fake_value)
    _fake_genai(monkeypatch, {"gemini-nano-banana-2.1": RuntimeError(f"bad request key={fake_value}")})
    hero._try_gemini("topic", [], tmp_path, 1200, 630, hero.DEFAULT_GEMINI_MODEL)
    captured = capsys.readouterr()
    assert fake_value not in captured.out + captured.err
