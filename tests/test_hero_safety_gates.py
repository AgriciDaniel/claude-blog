"""generate_hero safety gates: paid opt-in, existing-hero validation, symlinked heroes, paired writes.

No network and no SDK: providers and google.genai are replaced with fakes.
"""

from __future__ import annotations

import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import types
from pathlib import Path

import pytest

PIL = pytest.importorskip("PIL")
from PIL import Image, features  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HERO = ROOT / "scripts" / "generate_hero.py"
KEY_VARS = ("GOOGLE_AI_API_KEY", "GEMINI_API_KEY", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "PIXABAY_API_KEY")


def _image(fmt: str, size=(1200, 630), **save) -> bytes:
    out = io.BytesIO()
    Image.new("RGB", size, (10, 120, 200)).save(out, format=fmt, **save)
    return out.getvalue()


@pytest.fixture()
def hero(monkeypatch):
    for name in (*KEY_VARS, "NANOBANANA_MODEL"):
        monkeypatch.delenv(name, raising=False)
    spec = importlib.util.spec_from_file_location("hero_safety_gates", HERO)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _fake_genai(monkeypatch, data: bytes):
    calls = []

    class Interactions:
        def create(self, model, input, response_format):  # noqa: A002 - SDK name
            calls.append(model)
            return types.SimpleNamespace(output_image=types.SimpleNamespace(data=data))

    class Client:
        def __init__(self, api_key):
            self.interactions = Interactions()

    genai = types.ModuleType("google.genai")
    genai.Client = Client
    google = types.ModuleType("google")
    google.genai = genai
    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.genai", genai)
    return calls


def _openverse(hero, monkeypatch, image: bytes | None = None):
    """Serve one Openverse result; returns the list of provider calls made."""
    calls = []

    def fake_json(url, headers=None):
        calls.append(url)
        if url.startswith(hero.OPENVERSE_API):
            return {"results": [{"url": "https://img.example/good", "title": "T", "creator": "C", "license": "by"}]}
        return None

    monkeypatch.setattr(hero, "_http_get_json", fake_json)
    monkeypatch.setattr(hero, "_download_image", lambda url: image or _image("PNG"))
    return calls


def _no_provider(hero, monkeypatch):
    monkeypatch.setattr(hero, "_http_get_json", lambda *a, **k: pytest.fail("no provider may run"))
    monkeypatch.setattr(hero, "_try_gemini", lambda *a, **k: pytest.fail("no paid call may run"))


def _run(hero, monkeypatch, out_dir, capsys, *extra):
    monkeypatch.setattr(
        sys, "argv",
        ["generate_hero.py", "--topic", "Topic", "--tags", "a,b", "--out", str(out_dir), "--json", *extra],
    )
    code = hero.main()
    captured = capsys.readouterr()
    return code, json.loads(captured.out), captured.err


def _snapshot(directory: Path) -> dict:
    return {
        p.name: (p.readlink() if p.is_symlink() else p.read_bytes() if p.is_file() else "dir")
        for p in directory.iterdir()
    }


# Fix 1: the paid route needs --allow-paid in code, not only in skill docs.

@pytest.mark.parametrize("variable", ["GOOGLE_AI_API_KEY", "GEMINI_API_KEY"])
def test_a_set_key_without_allow_paid_never_calls_gemini(hero, monkeypatch, tmp_path, capsys, variable):
    monkeypatch.setenv(variable, "your-test-key")
    genai_calls = _fake_genai(monkeypatch, _image("PNG"))
    _openverse(hero, monkeypatch)

    code, result, err = _run(hero, monkeypatch, tmp_path / "out", capsys)

    assert code == 0, err
    assert genai_calls == []
    assert result["source"] == "openverse"
    assert result["paid_gemini_skipped"] is True
    assert err.count(hero.PAID_SKIPPED_MESSAGE) == 1
    assert "AI-generated" not in (tmp_path / "out" / "hero-credit.txt").read_text()


def test_allow_paid_with_a_key_uses_gemini(hero, monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("GEMINI_API_KEY", "your-test-key")
    genai_calls = _fake_genai(monkeypatch, _image("PNG"))
    _no_provider_json = lambda *a, **k: pytest.fail("stock must not run after a Gemini success")  # noqa: E731
    monkeypatch.setattr(hero, "_http_get_json", _no_provider_json)

    code, result, err = _run(hero, monkeypatch, tmp_path / "out", capsys, "--allow-paid")

    assert code == 0, err
    assert genai_calls == [hero.DEFAULT_GEMINI_MODEL]
    assert result["source"] == "gemini" and "paid_gemini_skipped" not in result
    assert hero.PAID_SKIPPED_MESSAGE not in err


def test_no_key_and_no_flag_adds_no_note(hero, monkeypatch, tmp_path, capsys):
    _openverse(hero, monkeypatch)
    code, result, err = _run(hero, monkeypatch, tmp_path / "out", capsys)
    assert code == 0
    assert "paid_gemini_skipped" not in result and hero.PAID_SKIPPED_MESSAGE not in err


def test_setup_error_mentions_allow_paid_and_the_skip(hero, monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("GOOGLE_AI_API_KEY", "your-test-key")
    _fake_genai(monkeypatch, _image("PNG"))
    monkeypatch.setattr(hero, "_http_get_json", lambda *a, **k: None)

    code, result, err = _run(hero, monkeypatch, tmp_path / "out", capsys)

    assert code == 1
    assert result["error"] == "no-image-gen-path"
    assert "--allow-paid" in result["message"]
    assert result["paid_gemini_skipped"] is True
    assert err.count(hero.PAID_SKIPPED_MESSAGE) == 1


def test_kept_existing_hero_prints_no_paid_note(hero, monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("GOOGLE_AI_API_KEY", "your-test-key")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "hero.png").write_bytes(_image("PNG"))
    _no_provider(hero, monkeypatch)
    code, result, err = _run(hero, monkeypatch, out_dir, capsys)
    assert code == 0 and result == {"source": "existing", "path": str(out_dir / "hero.png")}
    assert hero.PAID_SKIPPED_MESSAGE not in err


def test_help_documents_allow_paid():
    result = subprocess.run([sys.executable, str(HERO), "--help"], capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert "--allow-paid" in result.stdout
    assert "--allow-paid" in HERO.read_text(encoding="utf-8").split('"""', 2)[1]


# Fix 2: an existing hero counts only when its bytes are a real image of its extension's format.

def _webp_variants():
    if not features.check("webp"):
        return []
    return [
        ("hero.webp", _image("WEBP", lossless=True)),
        ("hero.webp", _image("WEBP", quality=80)),
        ("hero.webp", _image("WEBP", exif=b"Exif\x00\x00II*\x00\x08\x00\x00\x00\x00\x00")),
    ]


def _jpeg_with_big_app_segments() -> bytes:
    plain = _image("JPEG")
    app = b"\xff\xe2" + (65535).to_bytes(2, "big") + b"\x00" * 65533  # one maximal APP2 segment
    return plain[:2] + app * 3 + plain[2:]


@pytest.mark.parametrize(
    "name,data",
    [
        ("hero.png", _image("PNG")),
        ("hero.jpg", _image("JPEG")),
        ("hero.jpeg", _image("JPEG", progressive=True)),
        ("hero.jpg", _jpeg_with_big_app_segments()),
        *_webp_variants(),
    ],
    ids=lambda v: v if isinstance(v, str) else f"{len(v)}b",
)
def test_valid_heroes_pass_the_header_check(hero, tmp_path, name, data):
    path = tmp_path / name
    path.write_bytes(data)
    assert hero._hero_problem(path) is None


def _png_with_zero_width() -> bytes:
    data = bytearray(_image("PNG"))
    data[16:20] = b"\x00\x00\x00\x00"
    return bytes(data)


@pytest.mark.parametrize(
    "name,data,reason",
    [
        ("hero.png", b"", "empty"),
        ("hero.png", b"placed by the user", "PNG"),
        ("hero.png", b"\x89PNG\r\n\x1a\n", "PNG"),
        ("hero.png", _png_with_zero_width(), "zero"),
        ("hero.png", _image("JPEG"), "PNG"),
        ("hero.jpg", _image("PNG"), "JPEG"),
        ("hero.jpg", b"\xff\xd8\xff\xd9", "JPEG"),
        ("hero.jpg", b"\xff\xd8" + b"\xff" * 4096, "JPEG"),
        ("hero.webp", b"RIFF\x00\x00\x00\x00WEBPJUNK", "WEBP"),
    ],
    ids=lambda v: v if isinstance(v, str) else f"{len(v)}b",
)
def test_invalid_heroes_fail_the_header_check(hero, tmp_path, name, data, reason):
    path = tmp_path / name
    path.write_bytes(data)
    assert reason in hero._hero_problem(path)


def test_a_directory_named_like_a_hero_is_not_one(hero, tmp_path):
    (tmp_path / "hero.png").mkdir()
    assert hero._hero_problem(tmp_path / "hero.png") == "not a regular file"
    assert hero._existing_hero(tmp_path) is None


@pytest.mark.parametrize("name,data", [("hero.png", b""), ("hero.jpg", _image("PNG")), ("hero.webp", b"RIFFjunk")],
    ids=lambda v: v if isinstance(v, str) else f"{len(v)}b",
)
def test_an_invalid_existing_hero_is_replaced_and_reported(hero, monkeypatch, tmp_path, capsys, name, data):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / name).write_bytes(data)
    _openverse(hero, monkeypatch)

    code, result, err = _run(hero, monkeypatch, out_dir, capsys)

    assert code == 0, err
    assert result["source"] == "openverse"
    assert result["replaced_invalid"] == [name]
    assert f"{name} is not a usable hero" in err
    assert sorted(p.name for p in out_dir.iterdir()) == ["hero-credit.txt", "hero.png"]
    assert hero._hero_problem(out_dir / "hero.png") is None


def test_a_valid_existing_jpeg_is_kept(hero, monkeypatch, tmp_path, capsys):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    placed = _image("JPEG")
    (out_dir / "hero.jpg").write_bytes(placed)
    _no_provider(hero, monkeypatch)

    code, result, _err = _run(hero, monkeypatch, out_dir, capsys)

    assert code == 0 and result["source"] == "existing" and "replaced_invalid" not in result
    assert (out_dir / "hero.jpg").read_bytes() == placed


# Fix 3: a symlinked hero.* stops the run before anything is written or deleted.

@pytest.mark.parametrize("extra", [(), ("--replace",)])
@pytest.mark.parametrize("link_name", ["hero.png", "hero.webp"])
def test_a_symlinked_hero_refuses_and_touches_nothing(hero, monkeypatch, tmp_path, capsys, extra, link_name):
    outside = tmp_path / "outside.png"
    outside.write_bytes(_image("PNG"))
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / link_name).symlink_to(outside)
    if link_name != "hero.png":
        (out_dir / "hero.png").write_bytes(_image("PNG"))  # a valid hero beside the link does not help
    (out_dir / "hero-credit.txt").write_text("old credit")
    before = _snapshot(out_dir)
    monkeypatch.setenv("GOOGLE_AI_API_KEY", "your-test-key")
    _no_provider(hero, monkeypatch)

    code, result, err = _run(hero, monkeypatch, out_dir, capsys, "--allow-paid", *extra)

    assert code == 1
    assert result["error"] == "hero-symlink"
    assert link_name in result["message"] and "symlink" in result["message"]
    assert _snapshot(out_dir) == before
    assert outside.read_bytes() == _image("PNG")
    assert hero.PAID_SKIPPED_MESSAGE not in err


# Fix 4: the image and credit land together; a refused credit changes nothing.

def _seed_old_files(out_dir: Path) -> None:
    out_dir.mkdir()
    (out_dir / "hero.png").write_bytes(b"old png")
    (out_dir / "hero.webp").write_bytes(b"old webp")


def test_a_symlinked_credit_leaves_hero_credit_and_siblings_untouched(hero, tmp_path):
    out_dir = tmp_path / "out"
    _seed_old_files(out_dir)
    target = tmp_path / "elsewhere.txt"
    target.write_text("old credit")
    (out_dir / "hero-credit.txt").symlink_to(target)
    before = _snapshot(out_dir)

    with pytest.raises(ValueError, match="symlink"):
        hero._write_hero(out_dir, _image("JPEG"), "new credit")

    assert _snapshot(out_dir) == before
    assert target.read_text() == "old credit"


def test_a_failed_credit_stage_leaves_everything_and_no_temp_files(hero, monkeypatch, tmp_path):
    out_dir = tmp_path / "out"
    _seed_old_files(out_dir)
    (out_dir / "hero-credit.txt").write_text("old credit")
    before = _snapshot(out_dir)
    real_stage = hero._stage_temp

    def stage(path, data):
        if path.name == "hero-credit.txt":
            raise OSError("disk full")
        return real_stage(path, data)

    monkeypatch.setattr(hero, "_stage_temp", stage)
    with pytest.raises(OSError):
        hero._write_hero(out_dir, _image("JPEG"), "new credit")

    assert _snapshot(out_dir) == before


def test_a_successful_write_renames_both_and_leaves_no_temp_files(hero, tmp_path):
    out_dir = tmp_path / "out"
    _seed_old_files(out_dir)
    (out_dir / "hero-credit.txt").write_text("old credit")
    jpeg = _image("JPEG")

    path = hero._write_hero(out_dir, jpeg, "new credit")

    assert path == out_dir / "hero.jpg"
    assert _snapshot(out_dir) == {"hero.jpg": jpeg, "hero-credit.txt": b"new credit"}


@pytest.mark.parametrize("kind", ["symlink", "directory"])
def test_replace_with_an_unwritable_credit_exits_nonzero_before_any_provider(hero, monkeypatch, tmp_path, capsys, kind):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "hero.png").write_bytes(_image("PNG"))
    (out_dir / "hero.webp").write_bytes(_image("PNG"))
    credit = out_dir / "hero-credit.txt"
    if kind == "symlink":
        (tmp_path / "elsewhere.txt").write_text("old credit")
        credit.symlink_to(tmp_path / "elsewhere.txt")
    else:
        credit.mkdir()
    before = _snapshot(out_dir)
    _no_provider(hero, monkeypatch)

    code, result, _err = _run(hero, monkeypatch, out_dir, capsys, "--replace")

    assert code == 1
    assert result["error"] == "output-write-refused"
    assert _snapshot(out_dir) == before


def test_a_credit_refused_at_write_time_keeps_the_old_files(hero, monkeypatch, tmp_path, capsys):
    out_dir = tmp_path / "out"
    _seed_old_files(out_dir)
    (out_dir / "hero-credit.txt").write_text("old credit")
    before = _snapshot(out_dir)
    _openverse(hero, monkeypatch, image=_image("JPEG"))
    real_stage = hero._stage_temp

    def stage(path, data):
        if path.name == "hero-credit.txt":
            raise OSError("credit refused")
        return real_stage(path, data)

    monkeypatch.setattr(hero, "_stage_temp", stage)
    code, result, _err = _run(hero, monkeypatch, out_dir, capsys, "--replace")

    assert code == 1
    assert result["error"] == "output-write-refused"
    assert _snapshot(out_dir) == before


# Review follow-up: never overwrite a valid hand-placed hero; same size bar as the gates;
# every write target is checked before any provider (paid or free) runs.

def test_minimum_matches_the_delivery_gates(hero):
    text = (ROOT / "scripts" / "blog_preflight.py").read_text(encoding="utf-8")
    width = re.search(r"^HERO_MIN_WIDTH\s*=\s*(\d+)", text, re.MULTILINE)
    height = re.search(r"^HERO_MIN_HEIGHT\s*=\s*(\d+)", text, re.MULTILINE)
    assert width and height, "blog_preflight.py no longer defines HERO_MIN_WIDTH/HERO_MIN_HEIGHT"
    assert (hero.HERO_MIN_WIDTH, hero.HERO_MIN_HEIGHT) == (int(width.group(1)), int(height.group(1)))


@pytest.mark.parametrize(
    "invalid_name,invalid_data,valid_name,valid_fmt",
    [
        ("hero.png", b"", "hero.jpg", "JPEG"),
        ("hero.png", _image("PNG", size=(800, 400)), "hero.jpg", "JPEG"),
        ("hero.webp", b"RIFFjunk", "hero.png", "PNG"),
        ("hero.jpg", _image("JPEG", size=(1199, 630)), "hero.jpeg", "JPEG"),
    ],
)
def test_a_valid_hero_beside_an_invalid_one_is_kept_and_nothing_is_spent(
    hero, monkeypatch, tmp_path, capsys, invalid_name, invalid_data, valid_name, valid_fmt
):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    placed = _image(valid_fmt)
    (out_dir / valid_name).write_bytes(placed)
    (out_dir / invalid_name).write_bytes(invalid_data)
    (out_dir / "hero-credit.txt").write_text("user credit")
    monkeypatch.setenv("GOOGLE_AI_API_KEY", "your-test-key")
    _no_provider(hero, monkeypatch)

    code, result, err = _run(hero, monkeypatch, out_dir, capsys, "--allow-paid")

    assert code == 0, err
    assert result == {
        "source": "existing", "path": str(out_dir / valid_name), "replaced_invalid": [invalid_name],
    }
    assert f"removing {invalid_name}" in err
    assert _snapshot(out_dir) == {valid_name: placed, "hero-credit.txt": b"user credit"}


def test_an_undersized_hero_alone_is_replaced_and_the_reason_is_reported(hero, monkeypatch, tmp_path, capsys):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "hero.png").write_bytes(_image("PNG", size=(800, 400)))
    _openverse(hero, monkeypatch)

    code, result, err = _run(hero, monkeypatch, out_dir, capsys)

    assert code == 0, err
    assert result["source"] == "openverse" and result["replaced_invalid"] == ["hero.png"]
    assert "800x400 is below the 1200x630 delivery minimum" in err
    assert hero._hero_problem(out_dir / "hero.png") is None


def test_an_uppercase_hero_name_is_not_read(hero, tmp_path):
    (tmp_path / "hero.PNG").write_bytes(_image("PNG"))
    assert hero._hero_problem(tmp_path / "hero.PNG") == "unsupported extension"


@pytest.mark.parametrize("extra", [(), ("--replace",)])
def test_a_directory_hero_target_is_refused_before_the_paid_call(hero, monkeypatch, tmp_path, capsys, extra):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "hero.png").mkdir()
    monkeypatch.setenv("GOOGLE_AI_API_KEY", "your-test-key")
    genai_calls = _fake_genai(monkeypatch, _image("PNG"))
    monkeypatch.setattr(hero, "_http_get_json", lambda *a, **k: pytest.fail("no provider may run"))
    before = _snapshot(out_dir)

    code, result, _err = _run(hero, monkeypatch, out_dir, capsys, "--allow-paid", *extra)

    assert code == 1
    assert result["error"] == "output-write-refused" and "hero.png" in result["message"]
    assert genai_calls == []
    assert _snapshot(out_dir) == before


@pytest.mark.skipif(os.name != "posix" or os.geteuid() == 0, reason="needs POSIX permissions as a non-root user")
def test_an_unwritable_hero_target_is_refused_before_the_paid_call(hero, monkeypatch, tmp_path, capsys):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    old = out_dir / "hero.webp"
    old.write_bytes(_image("PNG"))  # wrong format for .webp, so it is invalid and would be replaced
    old.chmod(0o444)
    monkeypatch.setenv("GEMINI_API_KEY", "your-test-key")
    genai_calls = _fake_genai(monkeypatch, _image("PNG"))
    monkeypatch.setattr(hero, "_http_get_json", lambda *a, **k: pytest.fail("no provider may run"))
    try:
        code, result, _err = _run(hero, monkeypatch, out_dir, capsys, "--allow-paid")
    finally:
        old.chmod(0o644)

    assert code == 1
    assert result["error"] == "output-write-refused" and "unwritable" in result["message"]
    assert genai_calls == []
    assert sorted(p.name for p in out_dir.iterdir()) == ["hero.webp"]
