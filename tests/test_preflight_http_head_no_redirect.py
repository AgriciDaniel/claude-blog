"""Gate 5 _http_head must not follow redirects (VULN-804, v1.9.1).

A draft containing <a href="http://attacker.example/?to=internal-host">
should not turn preflight into an unauthenticated outbound proxy for
the attacker. urllib's default behavior follows 30x redirects; the
no-redirect opener in this fix refuses on the first hop.
"""
from __future__ import annotations

import importlib.util
import json
import socket
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PREFLIGHT = ROOT / "scripts" / "blog_preflight.py"


@pytest.fixture(scope="module")
def preflight_module():
    spec = importlib.util.spec_from_file_location("blog_preflight_m", PREFLIGHT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["blog_preflight_m"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_http_head_non_http_scheme_returns_zero(preflight_module):
    """VULN-002 defense-in-depth: file:// / data:// / etc. return 0."""
    for url in (
        "file:///etc/passwd",
        "ftp://example.com/",
        "javascript:alert(1)",
        "data:text/plain;base64,YWJj",
        "",
        "no-scheme",
    ):
        assert preflight_module._http_head(url) == 0, (
            f"expected 0 for non-http(s) URL: {url!r}"
        )


def test_http_head_uses_no_redirect_opener(preflight_module):
    """The opener used for HEAD must refuse redirects."""
    opener = preflight_module._PREFLIGHT_NO_REDIRECT_OPENER
    # Walk the handler chain; one of them must be the no-redirect class.
    handlers = opener.handlers
    refusers = [
        h for h in handlers
        if isinstance(h, preflight_module._PreflightNoRedirectHandler)
    ]
    assert len(refusers) == 1, (
        f"expected exactly one no-redirect handler in the opener, got {len(refusers)}"
    )


def test_no_redirect_handler_returns_none_on_30x(preflight_module):
    """Every 30x method on the handler returns None (= refuse)."""
    handler = preflight_module._PreflightNoRedirectHandler()
    for code, method in (
        (301, "http_error_301"),
        (302, "http_error_302"),
        (303, "http_error_303"),
        (307, "http_error_307"),
        (308, "http_error_308"),
    ):
        result = getattr(handler, method)(None, None, code, "msg", {})
        assert result is None, f"expected None from {method}, got {result!r}"


def test_http_head_refuses_private_resolved_ip(preflight_module, monkeypatch):
    called = False

    def fake_getaddrinfo(host, port, proto=0):
        return [(socket.AF_INET, socket.SOCK_STREAM, proto, "", ("169.254.169.254", port))]

    def fake_open(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("network opener must not be called for private IP")

    monkeypatch.setattr(preflight_module.socket, "getaddrinfo", fake_getaddrinfo)
    monkeypatch.setattr(preflight_module._PREFLIGHT_NO_REDIRECT_OPENER, "open", fake_open)

    assert preflight_module._http_head("http://metadata.example/latest") == 0
    assert called is False


def test_allowlist_does_not_bypass_url_safety(preflight_module, tmp_path, monkeypatch):
    """Draft allowlist may skip reachability only after URL safety passes."""
    (tmp_path / "post.md").write_text("---\ntitle: x\n---\nbody\n", encoding="utf-8")
    (tmp_path / "post.pdf").write_bytes(b"%PDF-1.4\n")
    (tmp_path / "hero.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (tmp_path / "preflight-allowlist.json").write_text(
        json.dumps({"hosts": ["metadata.example"]}),
        encoding="utf-8",
    )
    (tmp_path / "post.html").write_text(
        '<!DOCTYPE html><html><head>'
        '<link rel="canonical" href="https://example.com/post">'
        '<meta property="og:image" content="hero.png">'
        '<script type="application/ld+json">'
        '{"@type":"BlogPosting","headline":"x","image":"hero.png",'
        '"datePublished":"2026-07-09","author":{"name":"x"},"wordCount":1}'
        '</script></head><body><article>'
        '<a href="http://metadata.example/latest">x</a>'
        'word</article></body></html>',
        encoding="utf-8",
    )

    def fake_getaddrinfo(host, port, proto=0):
        return [(socket.AF_INET, socket.SOCK_STREAM, proto, "", ("169.254.169.254", port))]

    monkeypatch.setattr(preflight_module.socket, "getaddrinfo", fake_getaddrinfo)

    result = preflight_module.gate_5_asset_link_integrity(tmp_path)
    assert result["passed"] is False
    assert any("URL safety policy" in v for v in result["violations"])


def test_http_head_pins_validated_dns_during_open(preflight_module, monkeypatch):
    public_info = [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("93.184.216.34", 80))]
    private_info = [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("169.254.169.254", 80))]
    dns_calls = 0

    def fake_getaddrinfo(host, port, proto=0, *args, **kwargs):
        nonlocal dns_calls
        dns_calls += 1
        return public_info if dns_calls == 1 else private_info

    class FakeResp:
        status = 200
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False

    def fake_open(req, timeout=None):
        pinned = preflight_module.socket.getaddrinfo(
            "rebind.example", 80, proto=socket.IPPROTO_TCP
        )
        assert pinned == public_info
        return FakeResp()

    monkeypatch.setattr(preflight_module.socket, "getaddrinfo", fake_getaddrinfo)
    monkeypatch.setattr(preflight_module._PREFLIGHT_NO_REDIRECT_OPENER, "open", fake_open)

    assert preflight_module._http_head("http://rebind.example/path") == 200
    assert preflight_module.socket.getaddrinfo is fake_getaddrinfo
