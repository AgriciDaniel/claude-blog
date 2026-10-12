"""Wave 3 regression tests for blog-audio generate_audio.py.

Covers the Gemini TTS default model and deprecation handling, API key sourcing,
the per-run chunk cap, and secret redaction on the SDK error path. All offline:
the google-genai SDK is replaced by a fake module and keys are fake.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "skills" / "blog-audio" / "scripts" / "generate_audio.py"
# Built at runtime so the repo secret scanner never sees a key-shaped literal.
FAKE_KEY = "AI" + "za" + "FAKE" * 8 + "abc"  # AIza + 35 characters
SHORT_KEY = "fake-short-key"


@pytest.fixture
def generator():
    name = "test_audio_wave3_generator"
    spec = importlib.util.spec_from_file_location(name, GENERATOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    yield module
    sys.modules.pop(name, None)


@pytest.fixture
def clean_env(monkeypatch):
    for name in ("GOOGLE_AI_API_KEY", "GEMINI_API_KEY"):
        monkeypatch.delenv(name, raising=False)


def run_main(module, argv, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["generate_audio.py"] + argv)
    code = module.main()
    captured = capsys.readouterr()
    return code, captured.out, captured.err


class FakeGenai:
    """Stands in for google.genai: records the key and fails like a real SDK error."""

    def __init__(self, monkeypatch, message):
        self.clients = []
        self.calls = 0
        outer = self

        class Models:
            def generate_content(self, **kwargs):
                outer.calls += 1
                raise RuntimeError(message)

        class Interactions:
            def create(self, **kwargs):
                outer.calls += 1
                raise RuntimeError(message)

        class Client:
            def __init__(self, api_key=None):
                outer.clients.append(api_key)
                self.models = Models()
                self.interactions = Interactions()

        module = types.ModuleType("google.genai")
        module.Client = Client
        google = sys.modules.get("google") or types.ModuleType("google")
        monkeypatch.setitem(sys.modules, "google", google)
        monkeypatch.setitem(sys.modules, "google.genai", module)
        monkeypatch.setattr(google, "genai", module, raising=False)


def test_default_model_is_the_stable_38_flash_alias(generator, clean_env, monkeypatch, capsys):
    code, out, err = run_main(generator, ["--text", "hello", "--dry-run", "--json"], monkeypatch, capsys)
    assert code == 0
    data = json.loads(out)
    assert data["model"] == "flash38"
    assert generator.MODELS[data["model"]] == "gemini-3.8-flash-tts"
    assert "deprecated" not in err.lower()
    assert data["deprecation_warning"] is None


@pytest.mark.parametrize("alias", ["flash", "flash31", "pro", "legacy-flash25", "legacy-pro25"])
def test_legacy_aliases_still_work_and_warn_with_the_shutdown_date(generator, clean_env, alias, monkeypatch, capsys):
    code, out, err = run_main(generator, ["--text", "hello", "--model", alias, "--dry-run", "--json"], monkeypatch, capsys)
    assert code == 0
    assert json.loads(out)["status"] == "dry_run"
    assert "2026-11-17" in err and alias in err and "deprecated" in err
    assert generator.MODELS[alias] in err


def test_stable_38_aliases_do_not_warn(generator, clean_env, monkeypatch, capsys):
    for alias in ("flash38", "flash-lite38"):
        code, out, err = run_main(generator, ["--text", "hello", "--model", alias, "--dry-run"], monkeypatch, capsys)
        assert code == 0 and err == ""


def test_deprecation_text_changes_after_the_shutdown_date(generator):
    before = generator.deprecation_warning("flash", datetime(2026, 10, 12, tzinfo=timezone.utc))
    after = generator.deprecation_warning("flash", datetime(2026, 11, 18, tzinfo=timezone.utc))
    assert "is scheduled to shut down on 2026-11-17" in before
    assert "was scheduled to shut down on 2026-11-17" in after and "may no longer work" in after
    assert generator.deprecation_warning("flash38") is None


@pytest.mark.parametrize("env_name", ["GOOGLE_AI_API_KEY", "GEMINI_API_KEY"])
def test_either_api_key_variable_is_accepted(generator, clean_env, env_name, monkeypatch, capsys):
    fake = FakeGenai(monkeypatch, "boom")
    monkeypatch.setenv(env_name, FAKE_KEY)
    code, out, err = run_main(generator, ["--text", "hello", "--json"], monkeypatch, capsys)
    assert code == 1
    assert fake.clients == [FAKE_KEY], "the SDK client must be created from the environment key"
    assert fake.calls == 1, "the default model must reach the Interactions API call"


def test_missing_key_message_names_both_variables(generator, clean_env, monkeypatch, capsys):
    code, out, err = run_main(generator, ["--text", "hello", "--json"], monkeypatch, capsys)
    assert code == 1
    message = json.loads(out)["error"]
    assert "GOOGLE_AI_API_KEY" in message and "GEMINI_API_KEY" in message


def test_the_key_cannot_be_passed_as_an_argument(generator, clean_env, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["generate_audio.py", "--text", "x", "--api-key", FAKE_KEY])
    with pytest.raises(SystemExit) as exc:
        generator.main()
    assert exc.value.code == 2


@pytest.mark.parametrize("key", [FAKE_KEY, SHORT_KEY])
@pytest.mark.parametrize("as_json", [True, False])
def test_forced_sdk_error_never_prints_the_key(generator, clean_env, key, as_json, monkeypatch, capsys):
    message = (
        f"403 PERMISSION_DENIED for https://generativelanguage.googleapis.com/v1beta/models/x:generateContent"
        f"?key={key} headers {{'x-goog-api-key': '{key}'}} Bearer {key} raw {key}"
    )
    FakeGenai(monkeypatch, message)
    monkeypatch.setenv("GEMINI_API_KEY", key)
    argv = ["--text", "hello", "--model", "flash38"] + (["--json"] if as_json else [])
    code, out, err = run_main(generator, argv, monkeypatch, capsys)
    assert code == 1
    assert key not in out and key not in err
    assert "Gemini TTS API error" in out


@pytest.mark.parametrize("text", [
    f"key={FAKE_KEY}",
    f"/x?a=1&amp;key={FAKE_KEY}",
    f"/x?a=1%26key%3D{FAKE_KEY}",
    f'{{"key": "{FAKE_KEY}"}}',
    f"x-goog-api-key: {FAKE_KEY}",
    f"Bearer {FAKE_KEY}",
    f"access_token={FAKE_KEY}",
    f"bare {FAKE_KEY}",
])
def test_redact_secrets_covers_key_shapes(generator, text):
    assert FAKE_KEY not in generator.redact_secrets(text)


def big_text(chunks_worth: int) -> str:
    paragraph = ("word " * 6000).strip()  # about 30,000 characters, under one chunk
    return "\n\n".join([paragraph] * chunks_worth)


def test_runs_over_the_chunk_cap_are_refused_before_any_api_call(generator, clean_env, monkeypatch, capsys):
    fake = FakeGenai(monkeypatch, "boom")
    monkeypatch.setenv("GOOGLE_AI_API_KEY", FAKE_KEY)
    text = big_text(60)
    assert len(generator.split_text_for_tts(text)) > generator.DEFAULT_MAX_CHUNKS
    code, out, err = run_main(generator, ["--text", text, "--json"], monkeypatch, capsys)
    assert code == 1
    data = json.loads(out)
    assert "billed API calls" in data["error"] and "--max-chunks" in data["error"]
    assert data["chunk_count_est"] > 12
    assert fake.clients == [] and fake.calls == 0


def test_raising_max_chunks_allows_the_run_to_start(generator, clean_env, monkeypatch, capsys):
    fake = FakeGenai(monkeypatch, "boom")
    monkeypatch.setenv("GOOGLE_AI_API_KEY", FAKE_KEY)
    text = big_text(60)
    count = len(generator.split_text_for_tts(text))
    code, out, err = run_main(generator, ["--text", text, "--json", "--max-chunks", str(count)], monkeypatch, capsys)
    assert code == 1 and "Gemini TTS API error" in json.loads(out)["error"]
    assert fake.clients == [FAKE_KEY] and fake.calls == 1


def test_dry_run_reports_the_cap_without_refusing(generator, clean_env, monkeypatch, capsys):
    code, out, err = run_main(generator, ["--text", big_text(60), "--dry-run", "--json"], monkeypatch, capsys)
    data = json.loads(out)
    assert code == 0 and data["over_chunk_cap"] is True and data["max_chunks"] == 12


def test_max_chunks_must_be_positive(generator, clean_env, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["generate_audio.py", "--text", "x", "--max-chunks", "0"])
    with pytest.raises(SystemExit) as exc:
        generator.main()
    assert exc.value.code == 2
