#!/usr/bin/env python3
"""Run bounded, offline initialization smoke checks for optional runtimes.

The caller installs the applicable hash lock before invoking this script.
No API request or browser launch is performed.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent


def smoke_audio() -> dict:
    """Construct the client and exercise the TTS config path offline."""
    from google import genai

    client = genai.Client(api_key="ci-placeholder-not-used")
    try:
        if client.models is None:
            raise RuntimeError("google-genai client did not expose models")
    finally:
        client.close()

    generator_path = (
        ROOT / "skills" / "blog-audio" / "scripts" / "generate_audio.py"
    )
    spec = importlib.util.spec_from_file_location(
        "dependency_smoke_generate_audio", generator_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load generate_audio.py")
    generator = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = generator
    spec.loader.exec_module(generator)

    expected_text = "Offline TTS configuration smoke."
    expected_voice = "Kore"
    expected_model_key = "flash31"
    expected_pcm = b"\x00\x01\x02\x03"
    captured: dict = {}

    class FakeModels:
        @staticmethod
        def generate_content(*, model, contents, config):
            captured.update(
                {
                    "model": model,
                    "contents": contents,
                    "config": config,
                }
            )
            return SimpleNamespace(
                candidates=[
                    SimpleNamespace(
                        content=SimpleNamespace(
                            parts=[
                                SimpleNamespace(
                                    inline_data=SimpleNamespace(data=expected_pcm)
                                )
                            ]
                        )
                    )
                ]
            )

    fake_client = SimpleNamespace(models=FakeModels())
    pcm = generator.generate_single_speaker(
        fake_client,
        expected_text,
        expected_voice,
        expected_model_key,
    )
    if pcm != expected_pcm:
        raise RuntimeError("TTS compatibility path did not return inline PCM")
    if captured.get("model") != generator.MODELS[expected_model_key]:
        raise RuntimeError("TTS compatibility path selected the wrong model")
    if captured.get("contents") != expected_text:
        raise RuntimeError("TTS compatibility path changed the input contents")

    config = captured["config"]
    modalities = [
        str(getattr(item, "value", item)).upper()
        for item in config.response_modalities
    ]
    if "AUDIO" not in modalities:
        raise RuntimeError(f"TTS response modalities did not include AUDIO: {modalities}")
    voice = (
        config.speech_config.voice_config.prebuilt_voice_config.voice_name
    )
    if voice != expected_voice:
        raise RuntimeError(f"TTS compatibility path selected the wrong voice: {voice}")

    return {
        "component": "audio",
        "client_constructed": True,
        "tts_path_exercised": True,
        "model": captured["model"],
        "voice": voice,
        "response_modalities": modalities,
        "inline_pcm_verified": True,
        "network_used": False,
    }


def smoke_browser() -> dict:
    """Start and stop Patchright's driver without downloading a browser."""
    from patchright.sync_api import sync_playwright

    runtime = sync_playwright().start()
    try:
        browser_type = runtime.chromium.name
        if browser_type != "chromium":
            raise RuntimeError(f"unexpected Patchright browser type: {browser_type}")
    finally:
        runtime.stop()
    return {
        "component": "browser",
        "driver_initialized": True,
        "browser_launched": False,
    }


def smoke_preflight() -> dict:
    """Exercise Gate 1 capability discovery with Patchright installed."""
    preflight_path = ROOT / "scripts" / "blog_preflight.py"
    spec = importlib.util.spec_from_file_location(
        "dependency_smoke_blog_preflight", preflight_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load blog_preflight.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    with tempfile.TemporaryDirectory(prefix="claude-blog-preflight-smoke-") as tmp:
        result = module.gate_1_capability_discovery(
            Path(tmp), live_tools=["dependency-smoke"]
        )
    detected = result["capabilities"]["python_deps"]["patchright"]
    if not detected:
        raise RuntimeError("preflight did not detect the installed Patchright module")
    return {
        "component": "preflight",
        "gate_initialized": True,
        "patchright_detected": True,
    }


CHECKS: dict[str, Callable[[], dict]] = {
    "audio": smoke_audio,
    "browser": smoke_browser,
    "preflight": smoke_preflight,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run offline initialization checks for hash-locked dependencies."
    )
    parser.add_argument(
        "--component",
        action="append",
        choices=sorted(CHECKS),
        required=True,
        help="Component to check. Repeat for more than one component.",
    )
    args = parser.parse_args(argv)

    results: list[dict] = []
    errors: list[dict] = []
    for name in dict.fromkeys(args.component):
        try:
            results.append(CHECKS[name]())
        except Exception as exc:
            errors.append(
                {
                    "component": name,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
    report = {
        "status": "pass" if not errors else "fail",
        "results": results,
        "errors": errors,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
