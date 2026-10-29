"""google_auth hardening: portable chmod and a robust loopback OAuth callback (no network)."""

from __future__ import annotations

import importlib.util
import os
import socket
import stat
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "blog-google" / "scripts"


@pytest.fixture
def auth(monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("hardening_google_auth", SCRIPTS / "google_auth.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _get(port: int, query: str) -> int:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/?{query}", timeout=5) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code


def _listen_in_thread(auth, state, port, timeout=10.0):
    box = {}

    def run():
        box["code"] = auth._listen_for_oauth_code(state, timeout=timeout, port=port)

    thread = threading.Thread(target=run)
    thread.start()
    for _ in range(100):  # wait until the server accepts connections
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                break
        time.sleep(0.05)
    return thread, box


def test_write_secret_atomic_works_without_fchmod(auth, tmp_path, monkeypatch):
    monkeypatch.delattr(os, "fchmod", raising=False)
    target = tmp_path / "cfg" / "token.json"
    auth._write_secret_atomic(str(target), '{"a": 1}')
    assert target.read_text() == '{"a": 1}'
    if os.name == "posix":
        assert stat.S_IMODE(target.stat().st_mode) == 0o600


def test_callback_ignores_bad_requests_and_waits_for_the_valid_code(auth):
    port = _free_port()
    thread, box = _listen_in_thread(auth, "good-state", port)
    assert _get(port, "state=wrong&code=evil") == 403
    assert _get(port, "state=good-state") == 400  # valid state but no code: keep waiting
    assert _get(port, "") == 403
    assert thread.is_alive()
    assert _get(port, "state=good-state&code=the-code") == 200
    thread.join(timeout=10)
    assert box["code"] == "the-code"


def test_callback_returns_none_at_the_deadline(auth):
    port = _free_port()
    started = time.monotonic()
    assert auth._listen_for_oauth_code("s", timeout=0.3, port=port) is None
    assert time.monotonic() - started < 5


def test_callback_reports_a_busy_port_as_oserror(auth):
    with socket.socket() as holder:
        holder.bind(("127.0.0.1", 0))
        holder.listen(1)
        with pytest.raises(OSError):
            auth._listen_for_oauth_code("s", timeout=0.2, port=holder.getsockname()[1])


def test_run_oauth_flow_prints_a_clear_message_when_the_port_is_busy(auth, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(auth, "_load_oauth_client", lambda _path: {"client_id": "id", "client_secret": "s"})
    monkeypatch.setattr(auth, "_open_browser", lambda _url: None)

    def busy(*_args, **_kwargs):
        raise OSError(98, "Address already in use")

    monkeypatch.setattr(auth, "_listen_for_oauth_code", busy)
    with pytest.raises(SystemExit) as exc:
        auth.run_oauth_flow("client.json")
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "8085" in err and "Address already in use" in err
