"""check_google_currentness: wrong-shape feeds exit 3 cleanly, fetches retry once (no network)."""

from __future__ import annotations

import importlib.util
import json
import urllib.error
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "currentness_hardening", ROOT / "scripts" / "check_google_currentness.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

GOOD_STATUS = json.dumps([{"service_name": "Ranking", "begin": "2026-10-01T00:00:00+00:00"}]).encode()
GOOD_RSS = (
    b"<rss><channel><item><pubDate>Mon, 05 Oct 2026 10:00:00 GMT</pubDate></item></channel></rss>"
)


def _ledger(root: Path) -> None:
    (root / "data").mkdir()
    (root / "data" / "google-updates.json").write_text(
        json.dumps(
            {
                "last_verified": "2026-10-20",
                "source_watch": [
                    {"id": key, "url": url, "review_mode": "automated"}
                    for key, url in MODULE.AUTOMATED_SOURCES.items()
                ],
            }
        ),
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    "payload",
    [b'{"incidents": []}', b'["not an object"]', b'[{"service_name": "Ranking", "begin": 5}]', b"[1, 2]"],
)
def test_status_feed_with_wrong_shape_raises_a_clear_value_error(payload):
    with pytest.raises(ValueError, match="official status feed"):
        MODULE.latest_ranking_incident(payload)


def test_rss_with_unparseable_date_raises_a_clear_value_error():
    payload = b"<rss><channel><item><pubDate>not a date</pubDate></item></channel></rss>"
    with pytest.raises(ValueError):
        MODULE.latest_documentation_update(payload)


def test_good_payloads_still_parse():
    assert MODULE.latest_ranking_incident(GOOD_STATUS).isoformat() == "2026-10-01"
    assert MODULE.latest_documentation_update(GOOD_RSS).isoformat() == "2026-10-05"


def _run_main(monkeypatch, tmp_path, capsys, fetch, *extra):
    _ledger(tmp_path)
    monkeypatch.setattr(MODULE, "_fetch", fetch)
    monkeypatch.setattr(
        "sys.argv",
        ["check_google_currentness.py", "--root", str(tmp_path), "--as-of", "2026-10-25", *extra],
    )
    code = MODULE.main()
    return code, capsys.readouterr()


def test_main_exits_3_with_a_message_on_a_wrong_shape_payload(monkeypatch, tmp_path, capsys):
    def fetch(url, timeout):
        return b'{"unexpected": true}' if "incidents" in url else GOOD_RSS

    code, out = _run_main(monkeypatch, tmp_path, capsys, fetch)
    assert code == 3
    assert "unavailable" in out.err and "unexpected shape" in out.err
    assert "Traceback" not in out.err


def test_main_json_reports_unavailable_for_wrong_shape(monkeypatch, tmp_path, capsys):
    def fetch(url, timeout):
        return GOOD_STATUS if "incidents" in url else b"<rss><channel><item><pubDate>nope</pubDate></item></channel></rss>"

    code, out = _run_main(monkeypatch, tmp_path, capsys, fetch, "--json")
    assert code == 3
    assert json.loads(out.out)["status"] == "unavailable"


def test_main_is_current_with_good_payloads(monkeypatch, tmp_path, capsys):
    code, out = _run_main(
        monkeypatch, tmp_path, capsys, lambda url, timeout: GOOD_STATUS if "incidents" in url else GOOD_RSS
    )
    assert code == 0
    assert "current" in out.out


class _Response:
    def __init__(self, body: bytes):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False

    def read(self):
        return self._body


def test_fetch_retries_once_after_a_url_error(monkeypatch):
    calls = []

    def urlopen(request, timeout):
        calls.append(request.full_url)
        if len(calls) == 1:
            raise urllib.error.URLError("temporary failure")
        return _Response(b"ok")

    monkeypatch.setattr(MODULE.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(MODULE.time, "sleep", lambda _seconds: None)
    assert MODULE._fetch("https://example.test/feed", 1.0) == b"ok"
    assert len(calls) == 2


def test_fetch_gives_up_after_the_second_url_error(monkeypatch):
    calls = []

    def urlopen(request, timeout):
        calls.append(1)
        raise urllib.error.URLError("down")

    monkeypatch.setattr(MODULE.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(MODULE.time, "sleep", lambda _seconds: None)
    with pytest.raises(urllib.error.URLError):
        MODULE._fetch("https://example.test/feed", 1.0)
    assert len(calls) == 2
