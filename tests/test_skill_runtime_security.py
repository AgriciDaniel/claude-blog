"""Offline regression tests for maintained skill-local runtime boundaries."""

from __future__ import annotations

import hashlib
import importlib.util
import os
import sys
import types
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent


def load_script(monkeypatch: pytest.MonkeyPatch, name: str, relative: str):
    if relative.endswith("/nlp_analyze.py"):
        google_auth = types.ModuleType("google_auth")
        google_auth.describe_google_api_error = lambda error, *args: str(error)
        google_auth.get_api_key = lambda: "offline-key"
        google_auth.request_with_retries = lambda *args, **kwargs: None
        monkeypatch.setitem(sys.modules, "google_auth", google_auth)
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_skill_discourse_atomic_write_does_not_follow_predictable_temp_symlink(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = load_script(
        monkeypatch,
        "skill_discourse",
        "skills/blog-discourse/scripts/discourse_research.py",
    )
    victim = tmp_path / "victim.txt"
    victim.write_text("preserve", encoding="utf-8")
    target = tmp_path / "report.md"
    old_predictable_temp = target.with_name(f".{target.name}.tmp-{os.getpid()}")
    old_predictable_temp.symlink_to(victim)

    module._atomic_write(target, "new report")

    assert victim.read_text(encoding="utf-8") == "preserve"
    assert target.read_text(encoding="utf-8") == "new report"


def configure_flow_fixture(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    module = load_script(
        monkeypatch,
        "skill_sync_flow",
        "skills/blog-flow/scripts/sync_flow.py",
    )
    references = tmp_path / "references"
    references.mkdir()
    lock_file = references / "flow-prompts.lock"
    target = references / "demo.md"
    old = b"reviewed bytes"
    new = b"upstream drift"
    target.write_bytes(old)
    lock_file.write_text(
        f"{hashlib.sha256(old).hexdigest()}  skills/blog-flow/references/demo.md\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "REFERENCES_DIR", references)
    monkeypatch.setattr(module, "LOCK_FILE", lock_file)
    monkeypatch.setattr(module, "LOCK_PREFIX", "skills/blog-flow/references")
    monkeypatch.setattr(module, "SYNC_PATHS", ["references/demo.md"])
    monkeypatch.setattr(module, "_github_token", lambda: None)
    monkeypatch.setattr(module, "_fetch_content", lambda path, ref, token: new)
    return module, target, lock_file, old, new


def test_skill_flow_refuses_lock_drift_before_any_write(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module, target, lock_file, old, _ = configure_flow_fixture(monkeypatch, tmp_path)
    original_lock = lock_file.read_bytes()

    result = module.sync("main", allow_drift=False)

    assert result["status"] == "error"
    assert result["lock_drift"] == ["demo.md"]
    assert "--allow-drift" in result["errors"][0]["error"]
    assert target.read_bytes() == old
    assert lock_file.read_bytes() == original_lock


def test_skill_flow_allow_drift_updates_target_and_lock(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module, target, lock_file, _, new = configure_flow_fixture(monkeypatch, tmp_path)

    result = module.sync("main", allow_drift=True)

    assert result["status"] == "success"
    assert result["lock_drift"] == ["demo.md"]
    assert target.read_bytes() == new
    digest, relative = lock_file.read_text(encoding="utf-8").strip().split("  ", 1)
    assert digest == hashlib.sha256(new).hexdigest()
    assert relative == "skills/blog-flow/references/demo.md"


def test_skill_flow_existing_empty_lock_requires_explicit_drift_acceptance(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module, target, lock_file, old, _ = configure_flow_fixture(monkeypatch, tmp_path)
    lock_file.write_text("", encoding="utf-8")

    result = module.sync("main", allow_drift=False)

    assert result["status"] == "error"
    assert result["lock_drift"] == ["demo.md"]
    assert target.read_bytes() == old
    assert lock_file.read_text(encoding="utf-8") == ""


def test_nlp_pinned_https_connects_to_vetted_ip_and_keeps_sni(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_script(
        monkeypatch,
        "skill_nlp_analyze",
        "skills/blog-google/scripts/nlp_analyze.py",
    )
    calls = {}

    class RawSocket:
        def close(self):
            calls["raw_closed"] = True

    class TLSContext:
        def wrap_socket(self, raw, server_hostname):
            calls["server_hostname"] = server_hostname
            return "tls-socket"

    def connect(address, timeout, source_address):
        calls["address"] = address
        calls["timeout"] = timeout
        return RawSocket()

    monkeypatch.setattr(module.socket, "create_connection", connect)
    connection = module._PinnedHTTPSConnection(
        "public.example", 443, "93.184.216.34", timeout=15
    )
    connection._context = TLSContext()

    connection.connect()

    assert calls["address"] == ("93.184.216.34", 443)
    assert calls["server_hostname"] == "public.example"
    assert connection.sock == "tls-socket"


def test_nlp_host_header_preserves_hostname_and_nondefault_port(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_script(
        monkeypatch,
        "skill_nlp_analyze_host",
        "skills/blog-google/scripts/nlp_analyze.py",
    )
    target = module._FetchTarget(
        url="https://public.example:8443/article",
        scheme="https",
        hostname="public.example",
        port=8443,
        request_target="/article",
        addresses=("93.184.216.34",),
    )

    assert module._host_header(target) == "public.example:8443"


def test_nlp_redirect_is_revalidated_before_second_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_script(
        monkeypatch,
        "skill_nlp_analyze_redirect",
        "skills/blog-google/scripts/nlp_analyze.py",
    )

    def resolve(host, port, type):
        address = "100.64.0.1" if host == "internal.example" else "93.184.216.34"
        return [(2, 1, 6, "", (address, port))]

    requests = []

    def request(target):
        requests.append(target)
        return 302, {"location": "http://internal.example/private"}, b"", "utf-8"

    monkeypatch.setattr(module.socket, "getaddrinfo", resolve)
    monkeypatch.setattr(module, "_request_pinned", request)

    with pytest.raises(ValueError, match="blocked network address"):
        module._fetch_url_text("https://public.example/start")

    assert len(requests) == 1
    assert requests[0].addresses == ("93.184.216.34",)


@pytest.mark.parametrize("blocked_address", ["100.64.0.1", "224.0.0.1"])
def test_nlp_rejects_non_global_shared_and_multicast_addresses(
    monkeypatch: pytest.MonkeyPatch, blocked_address: str
) -> None:
    module = load_script(
        monkeypatch,
        f"skill_nlp_analyze_blocked_{blocked_address}",
        "skills/blog-google/scripts/nlp_analyze.py",
    )
    monkeypatch.setattr(
        module.socket,
        "getaddrinfo",
        lambda host, port, type: [(2, 1, 6, "", (blocked_address, port))],
    )

    with pytest.raises(ValueError, match="blocked network address"):
        module._resolve_fetch_target("https://blocked.example/article")


def test_nlp_successful_fetch_decodes_bounded_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_script(
        monkeypatch,
        "skill_nlp_analyze_success",
        "skills/blog-google/scripts/nlp_analyze.py",
    )
    monkeypatch.setattr(
        module.socket,
        "getaddrinfo",
        lambda host, port, type: [(2, 1, 6, "", ("93.184.216.34", port))],
    )
    monkeypatch.setattr(
        module,
        "_request_pinned",
        lambda target: (200, {"content-type": "text/plain"}, "café".encode(), "utf-8"),
    )

    assert module._fetch_url_text("https://public.example/article") == "café"


def test_nlp_invalid_charset_returns_analyze_url_error_envelope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_script(
        monkeypatch,
        "skill_nlp_analyze_charset",
        "skills/blog-google/scripts/nlp_analyze.py",
    )
    monkeypatch.setattr(
        module.socket,
        "getaddrinfo",
        lambda host, port, type: [(2, 1, 6, "", ("93.184.216.34", port))],
    )
    monkeypatch.setattr(
        module,
        "_request_pinned",
        lambda target: (200, {"content-type": "text/plain"}, b"content", "not-a-charset"),
    )

    result = module.analyze_url("https://public.example/article")

    assert result == {
        "error": (
            "Could not fetch URL: Fetched response declared an unsupported charset: "
            "not-a-charset"
        )
    }
