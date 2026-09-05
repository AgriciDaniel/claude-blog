"""SSRF guard tests for scripts/generate_hero.py:_http_get.

Locks in the fix for VULN-801 (SSRF in hero downloader). The image-URL
sink in `_http_get` must reject:

    1. non-http(s) schemes (file://, ftp://, gopher://, ...)
    2. URLs that resolve to private/loopback/link-local addresses
       (RFC1918, 127.0.0.0/8, 169.254.0.0/16, IPv6 ULA fc00::/7,
       link-local fe80::/10, loopback ::1)
    3. responses larger than MAX_IMAGE_BYTES
    4. automatic redirect-following (must be one-hop only)

Refer to the v1.9.0 audit and the report-generated remediation queue.
"""
from __future__ import annotations

import importlib.util
import socket
import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parent.parent
HERO_PATH = ROOT / "scripts" / "generate_hero.py"


@pytest.fixture(scope="module")
def hero_module():
    spec = importlib.util.spec_from_file_location("generate_hero", HERO_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["generate_hero"] = mod
    spec.loader.exec_module(mod)
    return mod


def _patch_dns(monkeypatch, hero_module, addr: str = "8.8.8.8") -> None:
    monkeypatch.setattr(hero_module.socket, "gethostbyname", lambda host: addr)
    family = socket.AF_INET6 if ":" in addr else socket.AF_INET
    monkeypatch.setattr(
        hero_module.socket,
        "getaddrinfo",
        lambda host, port, proto=0: [(family, socket.SOCK_STREAM, proto, "", (addr, port))],
    )


def test_non_http_scheme_is_refused(hero_module):
    for url in (
        "file:///etc/passwd",
        "ftp://example.com/data",
        "gopher://example.com/",
        "data:text/plain;base64,YWJj",
        "javascript:alert(1)",
        "",
        "not-a-url",
    ):
        assert hero_module._http_get(url) is None, f"expected None for: {url!r}"


def test_private_ipv4_is_refused(hero_module, monkeypatch):
    """URLs resolving to RFC1918 / loopback / link-local must be refused."""
    blocked = [
        ("http://aws-imds.test/", "169.254.169.254"),
        ("http://internal-svc.test/", "10.0.0.5"),
        ("http://lan.test/", "192.168.1.1"),
        ("http://reserved.test/", "172.16.0.1"),
        ("http://loopback.test/", "127.0.0.1"),
    ]
    for url, addr in blocked:
        monkeypatch.setattr(hero_module.socket, "gethostbyname", lambda host, _addr=addr: _addr)
        result = hero_module._http_get(url)
        assert result is None, f"expected None for {url!r} -> {addr}"


def test_private_ipv6_is_refused(hero_module, monkeypatch):
    """ULA fc00::/7, link-local fe80::/10, loopback ::1 must be refused."""
    blocked_v6 = ["::1", "fe80::1", "fc00::1"]
    for addr in blocked_v6:
        monkeypatch.setattr(hero_module.socket, "gethostbyname", lambda host, _addr=addr: _addr)
        assert hero_module._http_get(f"http://test/") is None, (
            f"expected None for IPv6 {addr}"
        )


def test_oversize_response_is_refused(hero_module, monkeypatch):
    """Responses larger than MAX_IMAGE_BYTES return None, not partial bytes."""
    # Verify guard rejects public IP first by mocking resolution to a public IP
    _patch_dns(monkeypatch, hero_module)

    class FakeResp:
        def __init__(self, size):
            self._size = size
        def read(self, n=None):
            if n is None:
                return b"x" * self._size
            return b"x" * min(n, self._size)
        def __enter__(self): return self
        def __exit__(self, *a): return False

    cap = hero_module.MAX_IMAGE_BYTES
    monkeypatch.setattr(hero_module._NO_REDIRECT_OPENER, "open", lambda req, timeout=None: FakeResp(cap + 1))
    assert hero_module._http_get("http://images.unsplash.com/x") is None


def test_size_at_cap_is_accepted(hero_module, monkeypatch):
    """A response exactly at MAX_IMAGE_BYTES still succeeds."""
    _patch_dns(monkeypatch, hero_module)
    cap = hero_module.MAX_IMAGE_BYTES

    class FakeResp:
        def read(self, n=None):
            if n is None:
                return b"x" * cap
            return b"x" * min(n, cap)
        def __enter__(self): return self
        def __exit__(self, *a): return False

    monkeypatch.setattr(hero_module._NO_REDIRECT_OPENER, "open", lambda req, timeout=None: FakeResp())
    out = hero_module._http_get("http://images.unsplash.com/x")
    assert out is not None
    assert len(out) == cap


def test_public_ip_with_normal_response_passes(hero_module, monkeypatch):
    """Sanity check: a legitimate stock-image CDN call (mocked) must succeed."""
    _patch_dns(monkeypatch, hero_module, "151.101.0.81")

    class FakeResp:
        def read(self, n=None):
            payload = b"\xff\xd8\xff\xe0" + b"x" * 1000  # JPEG magic + body
            if n is None:
                return payload
            return payload[:n]
        def __enter__(self): return self
        def __exit__(self, *a): return False

    monkeypatch.setattr(hero_module._NO_REDIRECT_OPENER, "open", lambda req, timeout=None: FakeResp())
    out = hero_module._http_get("https://images.pexels.com/photos/x.jpg")
    assert out is not None
    assert out.startswith(b"\xff\xd8\xff")


def test_dns_failure_is_refused(hero_module, monkeypatch):
    """Unresolvable hostname returns None, not an exception."""
    def _fail(host):
        raise socket.gaierror("not found")
    monkeypatch.setattr(hero_module.socket, "gethostbyname", _fail)
    assert hero_module._http_get("http://nonexistent.invalid/") is None


def test_max_image_bytes_constant_exists(hero_module):
    """The cap must be defined as a module-level constant for auditability."""
    assert hasattr(hero_module, "MAX_IMAGE_BYTES")
    assert 1 * 1024 * 1024 <= hero_module.MAX_IMAGE_BYTES <= 100 * 1024 * 1024, (
        "MAX_IMAGE_BYTES outside reasonable range (1-100 MB)"
    )


def test_allowed_schemes_constant_exists(hero_module):
    """The scheme allowlist must be defined as a module-level constant."""
    assert hasattr(hero_module, "ALLOWED_SCHEMES")
    assert hero_module.ALLOWED_SCHEMES == frozenset({"http", "https"}), (
        "ALLOWED_SCHEMES must be exactly {http, https}"
    )


def test_redirect_response_is_refused(hero_module, monkeypatch):
    _patch_dns(monkeypatch, hero_module)

    class RedirectResp:
        status = 302
        def read(self, n=None):
            return b""
        def __enter__(self): return self
        def __exit__(self, *a): return False

    monkeypatch.setattr(hero_module._NO_REDIRECT_OPENER, "open", lambda req, timeout=None: RedirectResp())
    assert hero_module._http_get("https://images.example/redirect") is None


def test_http_get_does_not_use_default_urlopen(hero_module, monkeypatch):
    _patch_dns(monkeypatch, hero_module)

    class FakeResp:
        status = 200
        def read(self, n=None):
            return b"\xff\xd8\xff\xe0ok"
        def __enter__(self): return self
        def __exit__(self, *a): return False

    monkeypatch.setattr(hero_module.urllib.request, "urlopen", lambda *a, **k: (_ for _ in ()).throw(AssertionError("urlopen used")))
    monkeypatch.setattr(hero_module._NO_REDIRECT_OPENER, "open", lambda req, timeout=None: FakeResp())
    assert hero_module._http_get("https://images.example/photo.jpg") == b"\xff\xd8\xff\xe0ok"


def test_http_get_pins_validated_dns_during_open(hero_module, monkeypatch):
    public_info = [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("93.184.216.34", 443))]
    private_info = [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("169.254.169.254", 443))]
    dns_calls = 0

    def fake_getaddrinfo(host, port, proto=0, *args, **kwargs):
        nonlocal dns_calls
        dns_calls += 1
        return public_info if dns_calls == 1 else private_info

    class FakeResp:
        status = 200
        def read(self, n=None):
            return b"\xff\xd8\xff\xe0ok"
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False

    def fake_open(req, timeout=None):
        pinned = hero_module.socket.getaddrinfo(
            "images.example", 443, proto=socket.IPPROTO_TCP
        )
        assert pinned == public_info
        return FakeResp()

    monkeypatch.setattr(hero_module.socket, "gethostbyname", lambda host: "93.184.216.34")
    monkeypatch.setattr(hero_module.socket, "getaddrinfo", fake_getaddrinfo)
    monkeypatch.setattr(hero_module._NO_REDIRECT_OPENER, "open", fake_open)

    assert hero_module._http_get("https://images.example/photo.jpg") == b"\xff\xd8\xff\xe0ok"
    assert hero_module.socket.getaddrinfo is fake_getaddrinfo


def test_http_get_refusal_log_redacts_query(hero_module, monkeypatch, capsys):
    def fail_dns(host):
        raise socket.gaierror("nope")

    monkeypatch.setattr(hero_module.socket, "gethostbyname", fail_dns)
    assert hero_module._http_get("https://pixabay.com/api/?key=SECRET&q=test") is None
    captured = capsys.readouterr()
    assert "SECRET" not in captured.err
    assert "[redacted]" in captured.err


def test_fit_image_bytes_enforces_requested_dimensions(hero_module):
    from io import BytesIO
    from PIL import Image

    src = BytesIO()
    Image.new("RGB", (40, 80), "red").save(src, format="PNG")
    out = hero_module._fit_image_bytes(src.getvalue(), 120, 60)
    with Image.open(BytesIO(out)) as img:
        assert img.size == (120, 60)
