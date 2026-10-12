"""Symlink guard scope and SSRF address policy for the renderer and hero script.

Covers two review findings:

1. The output-path symlink guard refused any symlink in any ancestor, so a
   host where /home -> var/home (or macOS /tmp -> private/tmp) could not use
   --out-dir under it. Trusted system aliases (root-owned, directly under the
   filesystem root) are now allowed; symlinks created below them, anywhere in
   the output tree, or at the leaf are still refused.
2. generate_hero used the is_private/is_reserved flags, which let CGNAT
   (100.64.0.0/10, Tailscale) and deprecated site-local fec0::/10 through.
   It now uses ipaddress is_global semantics like blog_preflight.
"""

from __future__ import annotations

import importlib.util
import json
import os
import socket
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RENDERER = ROOT / "scripts" / "blog_render.py"
HERO = ROOT / "scripts" / "generate_hero.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def renderer():
    return _load("pathsafety_renderer", RENDERER)


@pytest.fixture(scope="module")
def hero():
    return _load("pathsafety_hero", HERO)


def _home_is_system_alias() -> bool:
    home = Path("/home")
    try:
        info = home.lstat()
    except OSError:
        return False
    return home.is_symlink() and info.st_uid == 0


needs_home_alias = pytest.mark.skipif(
    not _home_is_system_alias(), reason="/home is not a root-owned symlink on this host"
)


def _symlink(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=target.is_dir())
    except OSError:
        pytest.skip("symlinks not supported on this filesystem")


def _fixture_md(root: Path) -> Path:
    source = root / "post.md"
    source.write_text(
        "---\ntitle: Fixture\ndescription: Path safety fixture.\ndate: 2026-10-07\n"
        "author: Tester\n---\n\nReader-visible body.\n",
        encoding="utf-8",
    )
    return source


def _run_renderer(renderer, monkeypatch, source: Path, out_dir: Path) -> int:
    monkeypatch.setattr(
        sys, "argv",
        ["blog_render.py", "--md", str(source), "--out-dir", str(out_dir), "--pdf-engine", "none"],
    )
    return renderer.main()


# --- Item 1: symlink guard scope -------------------------------------------


@needs_home_alias
def test_renderer_allows_trusted_system_alias_ancestor(renderer):
    renderer._reject_symlink_components(Path("/home/pathsafety-absent-user/out"))


@needs_home_alias
def test_hero_allows_trusted_system_alias_ancestor(hero):
    assert hero._symlink_component(Path("/home/pathsafety-absent-user/out")) is None


def test_renderer_renders_under_trusted_alias_ancestor(renderer, hero, tmp_path, monkeypatch, capsys):
    """Simulate a host alias such as /home by trusting one tmp symlink."""
    real = tmp_path / "real"
    (real / "posts").mkdir(parents=True)
    alias = tmp_path / "alias"
    _symlink(alias, real)
    alias_dir = alias / "posts"
    trusted = Path(os.path.abspath(alias))
    monkeypatch.setattr(
        renderer, "_is_trusted_system_symlink", lambda path, st: path == trusted, raising=False
    )
    monkeypatch.setattr(
        hero, "_is_trusted_system_symlink", lambda path: path == trusted, raising=False
    )
    source = _fixture_md(tmp_path)

    assert _run_renderer(renderer, monkeypatch, source, alias_dir) == 0
    assert (real / "posts" / "post.html").is_file()
    assert hero._symlink_component(alias_dir / "hero.png") is None


def test_renderer_still_refuses_untrusted_ancestor_symlink(renderer, tmp_path, monkeypatch, capsys):
    real = tmp_path / "real"
    (real / "posts").mkdir(parents=True)
    _symlink(tmp_path / "alias", real)
    source = _fixture_md(tmp_path)

    assert _run_renderer(renderer, monkeypatch, source, tmp_path / "alias" / "posts") == 1
    assert "symlink path component" in capsys.readouterr().err.lower()
    assert not (real / "posts" / "post.html").exists()


def test_renderer_refuses_symlink_below_output_root(renderer, tmp_path, monkeypatch, capsys):
    out = tmp_path / "out"
    out.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    _symlink(out / "sub", outside)
    source = _fixture_md(tmp_path)

    assert _run_renderer(renderer, monkeypatch, source, out / "sub") == 1
    assert "symlink" in capsys.readouterr().err.lower()
    assert list(outside.iterdir()) == []


def test_renderer_refuses_symlinked_leaf_even_with_trusted_ancestors(renderer, tmp_path, monkeypatch, capsys):
    out = tmp_path / "out"
    out.mkdir()
    victim = out / "victim.html"
    victim.write_text("PRESERVE", encoding="utf-8")
    _symlink(out / "post.html", victim)
    source = _fixture_md(tmp_path)

    assert _run_renderer(renderer, monkeypatch, source, out) == 1
    assert victim.read_text(encoding="utf-8") == "PRESERVE"


def test_hero_refuses_symlink_below_root_and_leaf(hero, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    _symlink(out / "sub", outside)
    assert hero._symlink_component(out / "sub" / "hero.png") == out / "sub"
    with pytest.raises(ValueError, match="symlink output path component"):
        hero._atomic_write_bytes(out / "sub" / "hero.png", b"x")
    leaf = out / "hero.png"
    _symlink(leaf, outside / "target.png")
    assert hero._symlink_component(leaf) == leaf


def test_trusted_alias_rule_requires_root_owner_and_filesystem_root_parent(hero, tmp_path):
    link = tmp_path / "alias"
    _symlink(link, tmp_path)
    # A user-created link is never trusted, wherever it lives.
    assert hero._is_trusted_system_symlink(link) is False


# --- Item 2: SSRF address policy -------------------------------------------


@pytest.mark.parametrize(
    "addr",
    [
        "100.64.0.1",
        "100.100.100.100",
        "fec0::1",
        "::ffff:10.0.0.1",
        "::ffff:127.0.0.1",
        "169.254.169.254",
        "10.0.0.5",
        "192.168.1.1",
        "127.0.0.1",
        "::1",
        "fe80::1",
        "fc00::1",
        "0.0.0.0",
        "224.0.0.1",
        "not-an-ip",
        "",
    ],
)
def test_non_public_addresses_are_blocked(hero, addr):
    assert hero._is_blocked_address(addr) is True


@pytest.mark.parametrize("addr", ["8.8.8.8", "151.101.0.81", "2606:4700:4700::1111", "::ffff:8.8.8.8"])
def test_public_addresses_remain_allowed(hero, addr):
    assert hero._is_blocked_address(addr) is False


@pytest.mark.parametrize("addr", ["100.64.0.1", "100.100.100.100", "fec0::1", "::ffff:10.0.0.1"])
def test_http_get_refuses_cgnat_site_local_and_mapped(hero, monkeypatch, addr):
    monkeypatch.setattr(hero.socket, "gethostbyname", lambda host: addr)
    family = socket.AF_INET6 if ":" in addr else socket.AF_INET
    monkeypatch.setattr(
        hero.socket, "getaddrinfo",
        lambda host, port, proto=0: [(family, socket.SOCK_STREAM, proto, "", (addr, port))],
    )
    assert hero._http_get("http://internal.test/x.png") is None
    assert hero._validate_url("http://internal.test/x.png") is False
    assert hero._is_private_address("internal.test") is True
