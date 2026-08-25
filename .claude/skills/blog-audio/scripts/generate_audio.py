#!/usr/bin/env python3
"""
Blog Audio Generator - Gemini TTS
Converts prepared text to speech using Google's Gemini TTS models.

The SDK calls below use the generate_content compatibility path. Prefer the
Interactions API for new Gemini 3.1 TTS features when the installed SDK
supports it.

Usage:
    python3 scripts/run.py generate_audio.py --text "Hello world" --voice Charon --json
    python3 scripts/run.py generate_audio.py --text-file article.txt --voice Puck --voice2 Kore --json
    python3 scripts/run.py generate_audio.py --text "Test" --dry-run --json
"""

import argparse
import base64
import html
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import struct
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

# All 30 Gemini TTS prebuilt voices
VOICES = {
    "Zephyr": "Bright", "Puck": "Upbeat", "Charon": "Informative",
    "Kore": "Firm", "Fenrir": "Excitable", "Leda": "Youthful",
    "Orus": "Firm", "Aoede": "Breezy", "Callirrhoe": "Easy-going",
    "Autonoe": "Bright", "Enceladus": "Breathy", "Iapetus": "Clear",
    "Umbriel": "Easy-going", "Algieba": "Smooth", "Despina": "Smooth",
    "Erinome": "Clear", "Algenib": "Gravelly", "Rasalgethi": "Informative",
    "Laomedeia": "Upbeat", "Achernar": "Soft", "Alnilam": "Firm",
    "Schedar": "Even", "Gacrux": "Mature", "Pulcherrima": "Forward",
    "Achird": "Friendly", "Zubenelgenubi": "Casual", "Vindemiatrix": "Gentle",
    "Sadachbia": "Lively", "Sadaltager": "Knowledgeable", "Sulafat": "Warm",
}

MODELS = {
    "flash": "gemini-3.1-flash-tts-preview",
    "flash31": "gemini-3.1-flash-tts-preview",
    "legacy-flash25": "gemini-2.5-flash-preview-tts",
    "pro": "gemini-2.5-pro-preview-tts",
    "legacy-pro25": "gemini-2.5-pro-preview-tts",
}

# Audio constants (Gemini TTS output format)
SAMPLE_RATE = 24000  # 24kHz
SAMPLE_WIDTH = 2     # 16-bit (2 bytes per sample)
CHANNELS = 1         # Mono

# Cost per 1M tokens. Audio output tokens are billed at 25 tokens per second.
COST_PER_1M_OUTPUT = {
    "flash": 20.0,
    "flash31": 20.0,
    "legacy-flash25": 10.0,
    "pro": 20.0,
    "legacy-pro25": 20.0,
}
COST_PER_1M_INPUT = {
    "flash": 1.0,
    "flash31": 1.0,
    "legacy-flash25": 0.50,
    "pro": 1.0,
    "legacy-pro25": 1.0,
}
AUDIO_TOKENS_PER_SECOND = 25
MAX_INPUT_TOKENS = 8192
CHUNK_TARGET_TOKENS = 7800
MAX_TEXT_FILE_BYTES = 1_000_000
TEXT_FILE_EXTENSIONS = {
    ".csv",
    ".htm",
    ".html",
    ".log",
    ".markdown",
    ".md",
    ".rst",
    ".text",
    ".tsv",
    ".txt",
}


def _path_contains_symlink(path: Path, root: Path) -> bool:
    """Return True if path or any existing parent below root is a symlink."""
    current = path if path.exists() or path.is_symlink() else path.parent
    current = current.absolute()
    root = root.absolute()
    while current != current.parent:
        if current.is_symlink():
            return True
        if current == root:
            return False
        current = current.parent
    return False


def _resolve_under_cwd(path_value: str, label: str, must_exist: bool) -> Path:
    """Resolve a path under the current working directory."""
    root = Path.cwd().resolve()
    candidate = Path(path_value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate

    if _path_contains_symlink(candidate, root):
        raise ValueError(f"{label} must not use symlinks")

    try:
        resolved = candidate.resolve(strict=must_exist)
    except FileNotFoundError as exc:
        raise ValueError(f"{label} not found: {path_value}") from exc

    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Refusing {label} outside working directory: {path_value}") from exc

    return resolved


def read_text_file(path_value: str) -> str:
    """Read a bounded text file from the current working directory."""
    path = _resolve_under_cwd(path_value, "text file", must_exist=True)
    if not path.is_file():
        raise ValueError(f"Text file is not a regular file: {path_value}")
    size = path.stat().st_size
    if size > MAX_TEXT_FILE_BYTES:
        raise ValueError(f"Text file exceeds {MAX_TEXT_FILE_BYTES} bytes: {path_value}")

    mime_type, _ = mimetypes.guess_type(path.name)
    is_text_mime = bool(mime_type and mime_type.startswith("text/"))
    if path.suffix.lower() not in TEXT_FILE_EXTENSIONS and not is_text_mime:
        raise ValueError("Text file must use a text extension or text MIME type")

    return path.read_text(encoding="utf-8")


def resolve_output_path(path_value: str) -> Path:
    """Resolve a writable output path under the current working directory."""
    return _resolve_under_cwd(path_value, "output path", must_exist=False)


def estimate_cost(text: str, model: str) -> dict:
    """Estimate generation cost from text length."""
    char_count = len(text)
    input_tokens = char_count / 4  # rough: 1 token ~ 4 chars
    # Output tokens scale with audio duration; ~150 words/min speech
    word_count = len(text.split())
    duration_minutes = word_count / 150
    duration_seconds = duration_minutes * 60
    # Rough output token estimate based on audio duration
    output_tokens = duration_seconds * AUDIO_TOKENS_PER_SECOND

    input_cost = (input_tokens / 1_000_000) * COST_PER_1M_INPUT[model]
    output_cost = (output_tokens / 1_000_000) * COST_PER_1M_OUTPUT[model]
    total_cost = input_cost + output_cost

    return {
        "input_tokens_est": int(input_tokens),
        "output_tokens_est": int(output_tokens),
        "duration_seconds_est": int(duration_seconds),
        "duration_human_est": f"{int(duration_minutes)}:{int(duration_seconds % 60):02d}",
        "cost_estimate": f"${total_cost:.3f}",
        "chunk_count_est": len(split_text_for_tts(text)),
    }


def estimate_input_tokens(text: str) -> int:
    """Estimate Gemini input tokens from text length."""
    return max(1, int(len(text) / 4))


def split_text_for_tts(text: str, max_tokens: int = CHUNK_TARGET_TOKENS) -> list[str]:
    """Split long text into TTS-safe chunks without cutting words."""
    if estimate_input_tokens(text) <= max_tokens:
        return [text]

    max_chars = max_tokens * 4
    chunks = []
    current = []
    current_len = 0

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            words = paragraph.split()
            for word in words:
                word_len = len(word) + 1
                if current and current_len + word_len > max_chars:
                    chunks.append(" ".join(current).strip())
                    current = []
                    current_len = 0
                current.append(word)
                current_len += word_len
            continue

        add_len = len(paragraph) + 2
        if current and current_len + add_len > max_chars:
            chunks.append("\n\n".join(current).strip())
            current = []
            current_len = 0
        current.append(paragraph)
        current_len += add_len

    if current:
        separator = "\n\n" if any("\n" in item for item in current) else " "
        chunks.append(separator.join(current).strip())
    return [chunk for chunk in chunks if chunk]


def pcm_to_wav(pcm_data: bytes, output_path: str):
    """Write raw PCM data as a WAV file."""
    num_samples = len(pcm_data) // SAMPLE_WIDTH
    data_size = num_samples * SAMPLE_WIDTH * CHANNELS
    byte_rate = SAMPLE_RATE * CHANNELS * SAMPLE_WIDTH
    block_align = CHANNELS * SAMPLE_WIDTH

    with open(output_path, "wb") as f:
        # RIFF header
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_size))
        f.write(b"WAVE")
        # fmt chunk
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))            # chunk size
        f.write(struct.pack("<H", 1))             # PCM format
        f.write(struct.pack("<H", CHANNELS))
        f.write(struct.pack("<I", SAMPLE_RATE))
        f.write(struct.pack("<I", byte_rate))
        f.write(struct.pack("<H", block_align))
        f.write(struct.pack("<H", SAMPLE_WIDTH * 8))
        # data chunk
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        f.write(pcm_data)


def atomic_write_wav(pcm_data: bytes, output_path: Path) -> None:
    """Write a WAV file atomically."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{output_path.stem}.",
        suffix=".wav",
        dir=str(output_path.parent),
    )
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        pcm_to_wav(pcm_data, str(tmp_path))
        os.replace(tmp_path, output_path)
    finally:
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except OSError:
            pass


def wav_to_mp3(wav_path: Path, mp3_path: Path) -> bool:
    """Convert WAV to MP3 using FFmpeg. Returns True on success."""
    if not shutil.which("ffmpeg"):
        return False
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{mp3_path.stem}.",
        suffix=".mp3",
        dir=str(mp3_path.parent),
    )
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame",
             "-b:a", "192k", "-ar", "24000", "-ac", "1", str(tmp_path)],
            check=True, capture_output=True,
        )
        os.replace(tmp_path, mp3_path)
        return True
    except subprocess.CalledProcessError:
        return False
    finally:
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except OSError:
            pass


def extract_audio_data(response) -> bytes:
    """Extract raw PCM audio bytes from Gemini TTS response.
    The SDK returns inline_data.data as bytes (raw PCM), not base64."""
    data = response.candidates[0].content.parts[0].inline_data.data
    if isinstance(data, bytes):
        return data
    # Fallback: if it's a base64 string (older SDK versions)
    return base64.b64decode(data)


def generate_single_speaker(client, text: str, voice: str, model: str) -> bytes:
    """Generate audio with a single voice via the compatibility API."""
    from google.genai import types

    response = client.models.generate_content(
        model=MODELS[model],
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice
                    )
                )
            ),
        ),
    )
    return extract_audio_data(response)


def generate_multi_speaker(client, text: str, voice1: str, voice2: str, model: str) -> bytes:
    """Generate audio with two speakers via the compatibility API."""
    from google.genai import types

    response = client.models.generate_content(
        model=MODELS[model],
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker="Speaker1",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice1
                                )
                            ),
                        ),
                        types.SpeakerVoiceConfig(
                            speaker="Speaker2",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice2
                                )
                            ),
                        ),
                    ]
                )
            ),
        ),
    )
    return extract_audio_data(response)


def generate_audio_chunks(client, text: str, voice1: str, voice2: str, model: str) -> tuple[bytes, int]:
    """Generate one or more TTS chunks and stitch the raw PCM bytes."""
    chunks = split_text_for_tts(text)
    audio_parts = []
    for chunk in chunks:
        if estimate_input_tokens(chunk) > MAX_INPUT_TOKENS:
            raise ValueError("Prepared text chunk exceeds the 8,192 token TTS input limit")
        if voice2:
            audio_parts.append(generate_multi_speaker(client, chunk, voice1, voice2, model))
        else:
            audio_parts.append(generate_single_speaker(client, chunk, voice1, model))
    return b"".join(audio_parts), len(chunks)


def output_result(data: dict, as_json: bool):
    """Print result in JSON or human-readable format."""
    if as_json:
        print(json.dumps(data, indent=2))
    else:
        if data["status"] == "success":
            print(f"\n{'=' * 50}")
            print(f"  Audio generated successfully!")
            print(f"{'=' * 50}")
            print(f"  File:     {data['path']}")
            print(f"  Format:   {data['format']}")
            print(f"  Duration: {data['duration_human']}")
            print(f"  Voice:    {data['voice']}")
            print(f"  Model:    {data['model']}")
            print(f"  Cost:     ~{data['cost_estimate']}")
            print(f"\n  Embed HTML:")
            print(f"  {data['embed_html']}")
            print(f"{'=' * 50}\n")
        elif data["status"] == "dry_run":
            print(f"\n  Dry run estimate:")
            print(f"  Duration: ~{data['duration_human_est']}")
            print(f"  Cost:     ~{data['cost_estimate']}")
            print(f"  Model:    {data['model']}")
            print(f"  Voice:    {data['voice']}")
        else:
            print(f"\n  Error: {data.get('error', 'Unknown error')}")


def main():
    parser = argparse.ArgumentParser(description="Generate audio from text using Gemini TTS")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Text to convert to speech")
    group.add_argument("--text-file", help="Path to text file")

    parser.add_argument("--voice", default="Charon", help="Primary voice (default: Charon)")
    parser.add_argument("--voice2", help="Second voice for dialogue mode")
    parser.add_argument("--model", choices=sorted(MODELS), default="flash", help="TTS model")
    parser.add_argument("--output", help="Output file path (default: auto-generated)")
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    parser.add_argument("--dry-run", action="store_true", help="Estimate cost without generating")

    args = parser.parse_args()

    # Validate voice names
    for voice_arg in [args.voice, args.voice2]:
        if voice_arg and voice_arg not in VOICES:
            result = {"status": "error", "error": f"Unknown voice: {voice_arg}. Valid voices: {', '.join(sorted(VOICES.keys()))}"}
            output_result(result, args.json)
            return 1

    # Read text
    if args.text_file:
        try:
            text = read_text_file(args.text_file).strip()
        except (OSError, UnicodeDecodeError, ValueError) as e:
            result = {"status": "error", "error": f"Text file rejected: {e}"}
            output_result(result, args.json)
            return 1
    else:
        text = args.text.strip()

    if not text:
        result = {"status": "error", "error": "Empty text provided"}
        output_result(result, args.json)
        return 1

    # Dry run - estimate only
    if args.dry_run:
        est = estimate_cost(text, args.model)
        result = {
            "status": "dry_run",
            "model": args.model,
            "voice": args.voice,
            "voice2": args.voice2,
            "text_length": len(text),
            "word_count": len(text.split()),
            "input_tokens_est": estimate_input_tokens(text),
            **est,
        }
        output_result(result, args.json)
        return 0

    # Check API key
    api_key = os.environ.get("GOOGLE_AI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        result = {"status": "error", "error": "GOOGLE_AI_API_KEY not set. Get one at https://aistudio.google.com/apikey"}
        output_result(result, args.json)
        return 1

    # Generate audio
    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        if not args.json:
            print(f"Generating audio ({args.model} model, voice: {args.voice})...")

        pcm_data, chunk_count = generate_audio_chunks(
            client, text, args.voice, args.voice2, args.model
        )

    except Exception as e:
        result = {"status": "error", "error": f"Gemini TTS API error: {str(e)}"}
        output_result(result, args.json)
        return 1

    # Calculate duration
    num_samples = len(pcm_data) // SAMPLE_WIDTH
    duration_seconds = num_samples / SAMPLE_RATE
    duration_min = int(duration_seconds // 60)
    duration_sec = int(duration_seconds % 60)
    duration_human = f"{duration_min}:{duration_sec:02d}"

    try:
        # Determine output path
        if args.output:
            output_path = resolve_output_path(args.output)
        else:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = resolve_output_path(f"audio_{ts}.mp3")

        # Write WAV, then convert to MP3
        wav_path = resolve_output_path(str(output_path.with_suffix(".wav")))
        atomic_write_wav(pcm_data, wav_path)

        final_format = "wav"
        final_path = wav_path

        if output_path.suffix.lower() in (".mp3", ""):
            mp3_path = resolve_output_path(str(output_path.with_suffix(".mp3")))
            if wav_to_mp3(wav_path, mp3_path):
                wav_path.unlink()  # Remove generated WAV after MP3 succeeds
                final_path = mp3_path
                final_format = "mp3"
            else:
                if not args.json:
                    print("  Warning: FFmpeg not found. Output is WAV (install ffmpeg for MP3).")
                final_path = wav_path
                final_format = "wav"
        elif output_path.suffix.lower() == ".wav":
            final_path = wav_path
            final_format = "wav"
    except (OSError, ValueError) as e:
        result = {"status": "error", "error": f"Output path rejected: {e}"}
        output_result(result, args.json)
        return 1

    # Build embed HTML
    rel_path = html.escape(final_path.relative_to(Path.cwd().resolve()).as_posix(), quote=True)
    mime = "audio/mpeg" if final_format == "mp3" else "audio/wav"
    embed_html = (
        f'<audio controls preload="metadata">'
        f'<source src="{rel_path}" type="{mime}">'
        f'Your browser does not support the audio element.</audio>'
    )

    # Cost estimate
    est = estimate_cost(text, args.model)

    result = {
        "status": "success",
        "path": str(Path(final_path).resolve()),
        "format": final_format,
        "duration_seconds": int(duration_seconds),
        "duration_human": duration_human,
        "voice": args.voice,
        "voice2": args.voice2,
        "model": args.model,
        "model_id": MODELS[args.model],
        "chunk_count": chunk_count,
        "embed_html": embed_html,
        "cost_estimate": est["cost_estimate"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    output_result(result, args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
