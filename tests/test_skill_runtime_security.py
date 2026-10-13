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
        google_auth.describe_google_api_error = lambda error, *args, **kwargs: str(error)
        google_auth.get_api_key = lambda: "offline-key"
        google_auth.api_key_headers = lambda key: {"x-goog-api-key": key}
        google_auth.safe_exception_text = lambda error, *secrets: str(error)
        google_auth.setup_hint = lambda: "run the setup script"
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
    tmp_path: Path
) -> None:
    """The bundled wrapper delegates to the core, whose temp file name is random."""
    import json
    import subprocess

    results = tmp_path / "results.json"
    results.write_text(json.dumps([{
        "platform": "reddit",
        "url": "https://example.com/post",
        "title": "A post",
        "snippet": "A snippet about the topic.",
        "date": "2026-10-01",
    }]), encoding="utf-8")
    victim = tmp_path / "victim.txt"
    victim.write_text("preserve", encoding="utf-8")
    target = tmp_path / "report.md"
    for predictable in (
        target.with_name(f".{target.name}.tmp-{os.getpid()}"),
        target.with_name(f"{target.name}.tmp"),
    ):
        predictable.symlink_to(victim)

    wrapper = ROOT / "skills/blog-discourse/scripts/discourse_research.py"
    result = subprocess.run(
        [sys.executable, str(wrapper), "--input", str(results), "--topic", "topic",
         "--output", str(target)],
        capture_output=True, text=True, cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    assert victim.read_text(encoding="utf-8") == "preserve"
    assert target.exists() and not target.is_symlink()


def configure_flow_fixture(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Seed a reviewed bundle through the bundled wrapper's core implementation."""
    import argparse

    wrapper = load_script(
        monkeypatch,
        "skill_sync_flow",
        "skills/blog-flow/scripts/sync_flow.py",
    )
    module = wrapper.load_core()
    package = tmp_path / "package"
    references = package / "skills" / "blog-flow" / "references"
    state = {"text": "reviewed bytes\n"}
    monkeypatch.setattr(module, "script_root", lambda: package)
    monkeypatch.setattr(module, "STATIC_FILES", [("docs/demo.md", "demo.md")])
    monkeypatch.setattr(module, "PROMPT_STAGES", [])
    monkeypatch.setattr(module, "_base_headers", lambda: {})
    monkeypatch.setattr(module, "fetch_file", lambda path, ref, headers: state["text"])

    def sync(**kwargs):
        options = dict(ref="main", dry_run=False, allow_drift=False, references_dir=None)
        options.update(kwargs)
        return module.sync(argparse.Namespace(**options))

    sync()
    target = references / "demo.md"
    lock_file = references / "flow-prompts.lock"
    old = target.read_bytes()
    state["text"] = "upstream drift\n"
    return module, sync, target, lock_file, old


def test_skill_flow_refuses_lock_drift_before_any_write(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, sync, target, lock_file, old = configure_flow_fixture(monkeypatch, tmp_path)
    original_lock = lock_file.read_bytes()

    with pytest.raises(SystemExit) as exc:
        sync(allow_drift=False)

    assert exc.value.code == 2
    assert target.read_bytes() == old
    assert lock_file.read_bytes() == original_lock


def test_skill_flow_allow_drift_updates_target_and_lock(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, sync, target, lock_file, _ = configure_flow_fixture(monkeypatch, tmp_path)

    result = sync(allow_drift=True)

    assert result["updated"] == ["skills/blog-flow/references/demo.md"]
    assert b"upstream drift" in target.read_bytes()
    locked = dict(
        reversed(line.split("  ", 1))
        for line in lock_file.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    )
    rel = "skills/blog-flow/references/demo.md"
    assert locked[rel] == hashlib.sha256(target.read_bytes()).hexdigest()


def test_skill_flow_existing_empty_lock_requires_explicit_drift_acceptance(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, sync, target, lock_file, old = configure_flow_fixture(monkeypatch, tmp_path)
    lock_file.write_text("", encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        sync(allow_drift=False)

    assert exc.value.code == 2
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
