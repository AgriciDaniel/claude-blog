"""generate_hero: undecodable images skip to the next provider; an existing hero is kept unless --replace."""

from __future__ import annotations

import importlib.util
import io
import sys
from pathlib import Path

import pytest

PIL = pytest.importorskip("PIL")
from PIL import Image  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HERO = ROOT / "scripts" / "generate_hero.py"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _png(width=40, height=30, color=(10, 120, 200)) -> bytes:
    out = io.BytesIO()
    Image.new("RGB", (width, height), color).save(out, format="PNG")
    return out.getvalue()


def _jpeg() -> bytes:
    out = io.BytesIO()
    Image.new("RGB", (40, 30), (200, 20, 20)).save(out, format="JPEG")
    return out.getvalue()


@pytest.fixture()
def hero(monkeypatch):
    for name in (
        "GOOGLE_AI_API_KEY", "GEMINI_API_KEY", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "PIXABAY_API_KEY",
        "NANOBANANA_MODEL",
    ):
        monkeypatch.delenv(name, raising=False)
    spec = importlib.util.spec_from_file_location("hero_hardening", HERO)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CORRUPT_PNG = PNG_MAGIC + b"this is not a real png stream" * 4


def test_corrupt_bytes_raise_a_skippable_error(hero):
    with pytest.raises(RuntimeError):
        hero._fit_image_bytes(CORRUPT_PNG, 120, 63)
    with pytest.raises(hero._ImageUnusable):
        hero._fit_image_bytes(CORRUPT_PNG, 120, 63)


def test_truncated_image_raises_a_skippable_error(hero):
    with pytest.raises(hero._ImageUnusable):
        hero._fit_image_bytes(_png(400, 300)[:60], 120, 63)


def test_decompression_bomb_is_skippable(hero, monkeypatch):
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 100)
    with pytest.raises(hero._ImageUnusable, match="DecompressionBombError"):
        hero._fit_image_bytes(_png(400, 300), 120, 63)


def test_good_image_is_fitted_to_the_requested_size(hero):
    fitted = hero._fit_image_bytes(_png(), 120, 63)
    assert Image.open(io.BytesIO(fitted)).size == (120, 63)


def _run_main(hero, monkeypatch, tmp_path, capsys, extra=()):
    monkeypatch.setattr(
        sys, "argv",
        ["generate_hero.py", "--topic", "Topic", "--tags", "a,b", "--out", str(tmp_path / "out"),
         "--width", "120", "--height", "63", "--json", *extra],
    )
    code = hero.main()
    return code, capsys.readouterr()


def test_corrupt_stock_image_skips_to_the_next_provider(hero, monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("UNSPLASH_ACCESS_KEY", "fake")

    def fake_json(url, headers=None):
        if url.startswith(hero.UNSPLASH_API):
            return {"results": [{"urls": {"regular": "https://img.example/bad"}, "user": {"name": "U"}}]}
        if url.startswith(hero.OPENVERSE_API):
            return {"results": [{"url": "https://img.example/good", "title": "T", "creator": "C", "license": "by"}]}
        return None

    monkeypatch.setattr(hero, "_http_get_json", fake_json)
    monkeypatch.setattr(hero, "_download_image", lambda url: CORRUPT_PNG if url.endswith("bad") else _png())

    code, out = _run_main(hero, monkeypatch, tmp_path, capsys)

    assert code == 0, out.out + out.err
    assert '"source": "openverse"' in out.out
    assert "decoded" in out.err or "image" in out.err
    assert (tmp_path / "out" / "hero.png").is_file()
    assert "Unsplash" not in (tmp_path / "out" / "hero-credit.txt").read_text()


def test_every_provider_corrupt_exits_1_with_the_setup_message_not_write_refused(hero, monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("UNSPLASH_ACCESS_KEY", "fake")
    monkeypatch.setattr(
        hero, "_http_get_json",
        lambda url, headers=None: {"results": [{"urls": {"regular": "https://img.example/bad"}, "url": "https://img.example/bad"}]},
    )
    monkeypatch.setattr(hero, "_download_image", lambda url: CORRUPT_PNG)

    code, out = _run_main(hero, monkeypatch, tmp_path, capsys)

    assert code == 1
    assert "no-image-gen-path" in out.out
    assert "output-write-refused" not in out.out


def test_write_errors_are_still_reported_as_write_refused(hero, monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("UNSPLASH_ACCESS_KEY", "fake")
    monkeypatch.setattr(
        hero, "_http_get_json",
        lambda url, headers=None: {"results": [{"urls": {"regular": "https://img.example/good"}, "user": {}}]},
    )
    monkeypatch.setattr(hero, "_download_image", lambda url: _png())

    def refuse(path, data):
        raise OSError("disk full")

    monkeypatch.setattr(hero, "_stage_temp", refuse)
    code, out = _run_main(hero, monkeypatch, tmp_path, capsys)

    assert code == 1
    assert "output-write-refused" in out.out


def test_successful_write_removes_stale_sibling_heroes(hero, tmp_path):
    for name in ("hero.png", "hero.jpeg", "hero.webp"):
        (tmp_path / name).write_bytes(b"stale")
    other = tmp_path / "hero-credit.txt"
    other.write_text("keep")
    unrelated = tmp_path / "hero2.png"
    unrelated.write_bytes(b"keep")

    path = hero._write_hero(tmp_path, _jpeg(), "new credit")

    assert path == tmp_path / "hero.jpg"
    assert other.read_text() == "new credit"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["hero-credit.txt", "hero.jpg", "hero2.png"]


def test_failed_write_keeps_the_existing_hero(hero, monkeypatch, tmp_path):
    (tmp_path / "hero.png").write_bytes(b"existing")

    def refuse(path, data):
        raise OSError("disk full")

    monkeypatch.setattr(hero, "_stage_temp", refuse)
    with pytest.raises(OSError):
        hero._write_hero(tmp_path, _jpeg(), "credit")
    assert (tmp_path / "hero.png").read_bytes() == b"existing"


def test_rewriting_the_same_extension_replaces_in_place(hero, tmp_path):
    (tmp_path / "hero.png").write_bytes(b"old")
    path = hero._write_hero(tmp_path, _png(), "credit")
    assert path == tmp_path / "hero.png"
    assert path.read_bytes() == _png()


def test_a_hero_already_in_the_folder_is_kept_and_no_provider_runs(hero, monkeypatch, tmp_path, capsys):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    placed = _png(1200, 630)
    (out_dir / "hero.png").write_bytes(placed)
    monkeypatch.setenv("UNSPLASH_ACCESS_KEY", "fake")
    monkeypatch.setattr(hero, "_http_get_json", lambda *a, **k: pytest.fail("no provider may run"))

    code, out = _run_main(hero, monkeypatch, tmp_path, capsys)

    assert code == 0
    assert '"source": "existing"' in out.out
    assert (out_dir / "hero.png").read_bytes() == placed
    assert sorted(p.name for p in out_dir.iterdir()) == ["hero.png"]


def test_replace_generates_a_new_hero_and_removes_the_old_one(hero, monkeypatch, tmp_path, capsys):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "hero.webp").write_bytes(b"old")  # invalid too; --replace runs either way
    monkeypatch.setattr(
        hero, "_http_get_json",
        lambda url, headers=None: {"results": [{"url": "https://img.example/good", "title": "T", "creator": "C", "license": "by"}]},
    )
    monkeypatch.setattr(hero, "_download_image", lambda url: _png())

    code, out = _run_main(hero, monkeypatch, tmp_path, capsys, extra=("--replace",))

    assert code == 0, out.out + out.err
    assert '"source": "openverse"' in out.out
    assert (out_dir / "hero.png").is_file() and not (out_dir / "hero.webp").exists()
