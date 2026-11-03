"""Renderer hardening: portable symlink refusal, HTML-safe JSON-LD, canonical validation."""

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "blog_render.py"
SPEC = importlib.util.spec_from_file_location("render_hardening", SCRIPT)
RENDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDER)


def _source(title="Hardening Post", canonical="https://example.com/blog/hardening/"):
    return (
        f"---\ntitle: {title}\ndescription: A short description of the post.\n"
        f"date: 2026-10-10\nauthor: Alex Rivera\ncanonical: {canonical}\nslug: hardening\n---\n\n"
        "Body text for the hardening post.\n"
    )


def _run(tmp_path, text):
    source = tmp_path / "hardening.md"
    source.write_bytes(text.encode("utf-8"))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--md", str(source), "--out-dir", str(tmp_path), "--pdf-engine", "none"],
        capture_output=True, text=True,
    )
    return result


def test_read_works_without_o_nofollow(monkeypatch, tmp_path):
    """Windows has no os.O_NOFOLLOW; the reader must still work and still refuse symlinks."""
    monkeypatch.delattr(os, "O_NOFOLLOW", raising=False)
    plain = tmp_path / "plain.md"
    plain.write_text("hello", encoding="utf-8")
    assert RENDER._read_md_bytes_safely(plain) == b"hello"
    link = tmp_path / "link.md"
    try:
        link.symlink_to(plain)
    except OSError:
        pytest.skip("symlinks unavailable")
    with pytest.raises(ValueError, match="symlink"):
        RENDER._read_md_bytes_safely(link)


def test_read_refuses_symlink_with_o_nofollow(tmp_path):
    plain = tmp_path / "plain.md"
    plain.write_text("hello", encoding="utf-8")
    link = tmp_path / "link.md"
    try:
        link.symlink_to(plain)
    except OSError:
        pytest.skip("symlinks unavailable")
    with pytest.raises(ValueError, match="symlink"):
        RENDER._read_md_bytes_safely(link)


def test_json_ld_escapes_html_significant_characters():
    fm = {"title": "<!--<script>alert(1)</script> & more", "author": "A", "date": "2026-10-10"}
    out = RENDER._build_json_ld(fm, 10, "https://example.com/hero.png")
    assert "<" not in out and ">" not in out and "&" not in out
    assert json.loads(out)["headline"] == fm["title"]


def test_rendered_page_keeps_hostile_title_inert(tmp_path):
    result = _run(tmp_path, _source(title='"<!--<script>x</script> & y"'))
    assert result.returncode == 0, result.stderr
    page = (tmp_path / "hardening.html").read_text(encoding="utf-8")
    block = re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.DOTALL).group(1)
    assert "<!--" not in block and "<script" not in block
    assert json.loads(block)["headline"] == "<!--<script>x</script> & y"


@pytest.mark.parametrize("canonical", ["http:", "https://", "ftp://example.com/x", "/relative/path", "example.com/post"])
def test_bad_canonical_gives_a_clear_error_not_a_traceback(tmp_path, canonical):
    result = _run(tmp_path, _source(canonical=f'"{canonical}"'))
    assert result.returncode == 1
    assert "canonical" in result.stderr
    assert "Traceback" not in result.stderr and "IndexError" not in result.stderr


def test_valid_canonical_still_renders(tmp_path):
    result = _run(tmp_path, _source())
    assert result.returncode == 0, result.stderr
