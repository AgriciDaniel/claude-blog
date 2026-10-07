"""Offline contracts for Gemini 3.8 TTS via the Interactions API."""

from __future__ import annotations

import base64
import importlib.util
import io
import sys
import wave
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "skills" / "blog-audio" / "scripts" / "generate_audio.py"


def _load_generator():
    name = "test_audio_interactions38_generator"
    spec = importlib.util.spec_from_file_location(name, GENERATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def generator():
    return _load_generator()


def _wav_bytes(
    pcm: bytes = b"\x00\x01\x02\x03",
    *,
    channels: int = 1,
    sample_rate: int = 24_000,
    sample_width: int = 2,
) -> bytes:
    output = io.BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm)
    return output.getvalue()


class FakeInteractions:
    def __init__(self, wav_data: bytes, *, mime_type: str = "audio/wav"):
        self.wav_data = wav_data
        self.mime_type = mime_type
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        encoded = base64.b64encode(self.wav_data).decode("ascii")
        return SimpleNamespace(
            output_audio=SimpleNamespace(data=encoded, mime_type=self.mime_type)
        )


def test_aliases_are_additive_and_compatibility_default_is_unchanged(generator) -> None:
    assert generator.MODELS == {
        "flash": "gemini-3.1-flash-tts-preview",
        "flash31": "gemini-3.1-flash-tts-preview",
        "flash38": "gemini-3.8-flash-tts",
        "flash-lite38": "gemini-3.8-flash-lite-tts",
        "legacy-flash25": "gemini-2.5-flash-preview-tts",
        "pro": "gemini-2.5-pro-preview-tts",
        "legacy-pro25": "gemini-2.5-pro-preview-tts",
    }


def test_38_prices_change_on_2027_boundary(generator) -> None:
    before = datetime(2026, 12, 31, 23, 59, tzinfo=timezone.utc)
    after = datetime(2027, 1, 1, tzinfo=timezone.utc)

    assert generator.get_token_prices("flash38", before) == (0.50, 9.00)
    assert generator.get_token_prices("flash38", after) == (1.00, 18.00)
    assert generator.get_token_prices("flash-lite38", before) == (0.50, 6.00)
    assert generator.get_token_prices("flash-lite38", after) == (1.00, 12.00)
    assert set(generator.estimate_cost("hello world", "flash38", before)) == {
        "input_tokens_est",
        "output_tokens_est",
        "duration_seconds_est",
        "duration_human_est",
        "cost_estimate",
        "chunk_count_est",
    }


@pytest.mark.parametrize("model", ["flash38", "flash-lite38"])
def test_single_speaker_38_uses_unary_wav_interaction(generator, model: str) -> None:
    pcm = b"\x00\x01\x02\x03"
    interactions = FakeInteractions(_wav_bytes(pcm))
    client = SimpleNamespace(interactions=interactions)

    result = generator.generate_single_speaker(client, "Hello", "Kore", model)

    assert result == pcm
    assert interactions.calls == [
        {
            "model": generator.MODELS[model],
            "input": [
                {
                    "type": "user_input",
                    "content": [{"type": "text", "text": "Hello"}],
                }
            ],
            "response_format": {"type": "audio"},
            "generation_config": {"speech_config": [{"voice": "Kore"}]},
        }
    ]


def test_multi_speaker_38_uses_validated_speech_metadata(generator) -> None:
    pcm = b"\x04\x05\x06\x07"
    interactions = FakeInteractions(_wav_bytes(pcm))
    client = SimpleNamespace(interactions=interactions)

    result = generator.generate_multi_speaker(
        client,
        "Speaker1: Hello there\nSpeaker2: Hi: good to meet you",
        "Puck",
        "Kore",
        "flash38",
    )

    assert result == pcm
    assert interactions.calls[0]["input"] == [
        {
            "type": "user_input",
            "content": [
                {
                    "type": "text",
                    "text": "Hello there",
                    "annotations": [
                        {"type": "speech_metadata", "speaker": "Speaker1"}
                    ],
                },
                {
                    "type": "text",
                    "text": "Hi: good to meet you",
                    "annotations": [
                        {"type": "speech_metadata", "speaker": "Speaker2"}
                    ],
                },
            ],
        }
    ]
    assert interactions.calls[0]["generation_config"] == {
        "speech_config": {
            "speakers": [
                {"speaker": "Speaker1", "voice": "Puck"},
                {"speaker": "Speaker2", "voice": "Kore"},
            ]
        }
    }


@pytest.mark.parametrize(
    "text",
    [
        "An unlabeled line",
        "Speaker3: Unknown speaker",
        "Speaker1:\nSpeaker2: Valid",
    ],
)
def test_multi_speaker_38_rejects_ambiguous_transcripts(generator, text: str) -> None:
    client = SimpleNamespace(interactions=FakeInteractions(_wav_bytes()))
    with pytest.raises(ValueError, match="Speaker1:|Speaker2:"):
        generator.generate_multi_speaker(
            client, text, "Puck", "Kore", "flash38"
        )


@pytest.mark.parametrize(
    ("output_audio", "message"),
    [
        (None, "output_audio.data"),
        (SimpleNamespace(data="!!!!", mime_type="audio/wav"), "base64"),
        (
            SimpleNamespace(
                data=base64.b64encode(b"not a wav").decode("ascii"),
                mime_type="audio/wav",
            ),
            "WAV",
        ),
        (
            SimpleNamespace(
                data=base64.b64encode(_wav_bytes()).decode("ascii"),
                mime_type="audio/l16",
            ),
            "audio/wav",
        ),
    ],
)
def test_38_audio_response_fails_closed(generator, output_audio, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        generator.extract_interaction_wav_pcm(
            SimpleNamespace(output_audio=output_audio)
        )


@pytest.mark.parametrize(
    ("wav_data", "message"),
    [
        (_wav_bytes(channels=2), "mono"),
        (_wav_bytes(sample_rate=16_000), "24000"),
        (_wav_bytes(sample_width=1), "16-bit"),
        (_wav_bytes(pcm=b""), "no audio frames"),
    ],
)
def test_38_wav_format_is_validated(generator, wav_data: bytes, message: str) -> None:
    encoded = base64.b64encode(wav_data).decode("ascii")
    interaction = SimpleNamespace(
        output_audio=SimpleNamespace(data=encoded, mime_type="audio/wav")
    )
    with pytest.raises(ValueError, match=message):
        generator.extract_interaction_wav_pcm(interaction)
