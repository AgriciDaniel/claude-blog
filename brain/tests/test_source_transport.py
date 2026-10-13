"""Offline proofs that ledger fetches bind DNS validation to direct HTTPS."""
import hashlib
import socket
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_source_ledger as verifier

PUBLIC = "93.184.216.34"


def addresses(ip=PUBLIC, port=443):
    return [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", (ip, port))]


class Response:
    def __init__(self, status=200, headers=None, chunks=None):
        self.status = status
        self.headers = headers or {"content-type": "text/plain; charset=utf-8"}
        self.chunks = iter(chunks or [b"Reviewed scoped source claim.", b""])

    def getheader(self, name, default=None):
        return self.headers.get(name.lower(), default)

    def read1(self, size):
        return next(self.chunks, b"")


def install_connections(monkeypatch, responses):
    calls = []
    replies = iter(responses)

    class Connection:
        def __init__(self, host, port, pinned, *, timeout):
            assert pinned == addresses()
            assert 0 < timeout <= 30
            self.sock = None
            self.response = next(replies)
            calls.append({"host": host, "port": port, "addresses": pinned})
            self.call = calls[-1]

        def request(self, method, target, headers):
            self.call.update(method=method, target=target, headers=headers)

        def getresponse(self):
            return self.response

        def close(self):
            self.call["closed"] = True

    monkeypatch.setattr(verifier, "PinnedHTTPSConnection", Connection)
    return calls


def test_direct_connection_pins_validated_ip_without_re_resolving_and_preserves_sni(monkeypatch):
    lookups = []
    connected = []
    wrapped = []

    def dns(host, port, **kwargs):
        lookups.append(host)
        return addresses() if len(lookups) == 1 else addresses("127.0.0.1")

    class Raw:
        def settimeout(self, timeout):
            assert 0 < timeout <= 30

        def connect(self, sockaddr):
            connected.append(sockaddr)

        def close(self):
            pass

    monkeypatch.setattr(verifier.socket, "getaddrinfo", dns)
    host, port, pinned = verifier.validate_public_https("https://public.example/proof")
    connection = verifier.PinnedHTTPSConnection(host, port, pinned, timeout=30)
    monkeypatch.setattr(verifier.socket, "socket", lambda *args: Raw())

    def wrap(raw, *, server_hostname):
        wrapped.append(server_hostname)
        return raw

    connection._context = SimpleNamespace(wrap_socket=wrap)
    connection.connect()
    connection.close()
    assert lookups == ["public.example"]
    assert connected == [(PUBLIC, 443)]
    assert wrapped == ["public.example"]


def test_fetch_ignores_proxy_environment_and_retains_user_agent_and_hash(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:9999")
    monkeypatch.setenv("ALL_PROXY", "http://127.0.0.1:9999")
    monkeypatch.setitem(sys.modules, "requests", SimpleNamespace(
        Session=lambda: pytest.fail("must not consult an environment-trusting session")))
    lookups = []

    def dns(host, port, **kwargs):
        lookups.append((host, port))
        return addresses()

    monkeypatch.setattr(verifier.socket, "getaddrinfo", dns)
    calls = install_connections(monkeypatch, [Response()])
    result = verifier.fetch_source("https://public.example/path?q=1#fragment")
    assert lookups == [("public.example", 443)]
    assert calls[0]["host"] == "public.example"
    assert calls[0]["target"] == "/path?q=1"
    assert calls[0]["headers"]["User-Agent"] == "Mozilla/5.0 ClaudeBlogSourceAudit/1.0"
    assert calls[0]["closed"]
    assert result["text"] == "reviewed scoped source claim."
    assert result["normalized_content_sha256"] == hashlib.sha256(result["text"].encode()).hexdigest()


@pytest.mark.parametrize("destination", ["https://private.example/proof", "/again"])
def test_redirect_private_or_rebound_dns_refused_before_private_connection(monkeypatch, destination):
    lookups = []

    def dns(host, port, **kwargs):
        lookups.append(host)
        return addresses() if len(lookups) == 1 else addresses("127.0.0.1")

    monkeypatch.setattr(verifier.socket, "getaddrinfo", dns)
    calls = install_connections(monkeypatch, [Response(302, {"location": destination})])
    with pytest.raises(ValueError, match="non-public"):
        verifier.fetch_source("https://public.example/initial")
    assert len(calls) == 1
    assert calls[0]["addresses"] == addresses()
    assert calls[0]["closed"]
    assert len(lookups) == 2


def test_each_public_redirect_is_separately_validated_and_connection_closed(monkeypatch):
    lookups = []
    monkeypatch.setattr(verifier.socket, "getaddrinfo", lambda host, port, **kw: lookups.append(host) or addresses())
    calls = install_connections(monkeypatch, [Response(307, {"location": "https://second.example/final"}), Response()])
    result = verifier.fetch_source("https://first.example/initial")
    assert lookups == ["first.example", "second.example"]
    assert [call["host"] for call in calls] == lookups
    assert all(call["closed"] for call in calls)
    assert result["final_url"] == "https://second.example/final"


@pytest.mark.parametrize("ip", ["127.0.0.1", "10.0.0.1", "169.254.169.254", "192.0.2.1", "224.0.0.1", "::1", "fc00::1"])
def test_any_nonpublic_dns_address_blocks_all_connections(monkeypatch, ip):
    monkeypatch.setattr(verifier.socket, "getaddrinfo", lambda *a, **kw: addresses() + addresses(ip))
    monkeypatch.setattr(verifier, "PinnedHTTPSConnection", lambda *a, **kw: pytest.fail("unsafe address was connected"))
    with pytest.raises(ValueError, match="non-public"):
        verifier.fetch_source("https://public.example/proof")


# Build the credential-bearing URL at runtime without storing a credential literal.
@pytest.mark.parametrize("url", ["http://public.example/a", "https://" + "user" + ":" + "secret" + "@public.example/a", "https://localhost/a", "https://public.example:99999/a"])
def test_invalid_url_rejected_before_dns_or_connection(monkeypatch, url):
    monkeypatch.setattr(verifier.socket, "getaddrinfo", lambda *a, **kw: pytest.fail("unsafe URL reached DNS"))
    with pytest.raises(ValueError):
        verifier.fetch_source(url)


def test_direct_connection_rechecks_pin_without_using_private_socket(monkeypatch):
    connection = verifier.PinnedHTTPSConnection("public.example", 443, addresses("127.0.0.1"), timeout=30)
    monkeypatch.setattr(verifier.socket, "socket", lambda *a: pytest.fail("private socket created"))
    with pytest.raises(ValueError, match="not public"):
        connection.connect()


@pytest.mark.parametrize("problem", ["size", "missing-location", "status", "redirect-loop", "timeout"])
def test_bounded_failures_close_connections(monkeypatch, problem):
    monkeypatch.setattr(verifier.socket, "getaddrinfo", lambda *a, **kw: addresses())
    if problem == "size":
        monkeypatch.setattr(verifier, "MAX_BYTES", 3)
        replies = [Response(chunks=[b"four"])]
    elif problem == "missing-location":
        replies = [Response(302, {"other": "x"})]
    elif problem == "status":
        replies = [Response(503)]
    elif problem == "redirect-loop":
        replies = [Response(302, {"location": "/again"}) for _ in range(7)]
    else:
        ticks = iter([0, 0, 31])
        monkeypatch.setattr(verifier.time, "monotonic", lambda: next(ticks))
        replies = [Response()]
    calls = install_connections(monkeypatch, replies)
    with pytest.raises((ValueError, TimeoutError)):
        verifier.fetch_source("https://public.example/proof")
    assert calls and all(call["closed"] for call in calls)
