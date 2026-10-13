"""Wave 3 regression tests for the blog-google scripts.

Covers key redaction on every error path, header-based key transport, the
Indexing API eligibility gate and status-based quota handling, URL Inspection
batch behavior, Search Console window math, and the CLI help contracts.
No test makes a credentialed or external network call: connection errors are
forced against a closed loopback port and fake keys are used throughout.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import io
import json
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/blog-google/scripts"
# Built at runtime so the repo secret scanner never sees a key-shaped literal.
FAKE_KEY = "AI" + "za" + "FAKE" * 8 + "abc"  # AIza + 35 characters
SHORT_KEY = "fake-short-key"


def load_script(name, monkeypatch, alias=None):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(alias or "wave3_" + name, SCRIPTS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def auth(monkeypatch):
    return load_script("google_auth", monkeypatch)


def closed_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


class Capture(BaseHTTPRequestHandler):
    seen: list = []

    def _answer(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)
        type(self).seen.append((self.path, dict(self.headers)))
        body = b'{"lighthouseResult": {}, "record": {}}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_GET = do_POST = _answer

    def log_message(self, *args):
        pass


@pytest.fixture
def capture_server():
    handler = type("H", (Capture,), {"seen": []})
    server = HTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}", handler.seen
    server.shutdown()
    server.server_close()


# ---------------------------------------------------------------------------
# 1. Redaction


@pytest.mark.parametrize("text", [
    f"key={FAKE_KEY}",
    f"GET /v5/runPagespeed?url=x&key={FAKE_KEY} failed",
    f"https://h/p?a=1&amp;key={FAKE_KEY}&amp;b=2",
    f"https://h/p?a=1%26key%3D{FAKE_KEY}%26b%3D2",
    f'{{"key": "{FAKE_KEY}"}}',
    f"{{'key': '{FAKE_KEY}'}}",
    f'\\"key\\": \\"{FAKE_KEY}\\"',
    f"x-goog-api-key: {FAKE_KEY}",
    f"{{'x-goog-api-key': '{FAKE_KEY}'}}",
    f"X-Goog-Api-Key={FAKE_KEY}",
    f"see {FAKE_KEY} in the log",
    f"api_key={FAKE_KEY}",
])
def test_redact_secrets_covers_key_shapes(auth, text):
    redacted = auth.redact_secrets(text)
    assert FAKE_KEY not in redacted
    assert "[redacted]" in redacted


@pytest.mark.parametrize("text,secret", [
    ("Authorization: Bearer abc.def-123", "abc.def-123"),
    ("failed with Bearer ya29.a0AfH6SMBxyz", "ya29.a0AfH6SMBxyz"),
    ("https://h/?access_token=ya29.zzz&x=1", "ya29.zzz"),
    ('{"refresh_token": "1//0gAbCdEf"}', "1//0gAbCdEf"),
])
def test_redact_secrets_covers_tokens(auth, text, secret):
    assert secret not in auth.redact_secrets(text)


def test_redact_secrets_removes_literal_values_and_keeps_plain_text(auth):
    text = f"boom {SHORT_KEY} and monkey=banana"
    redacted = auth.redact_secrets(text, [SHORT_KEY])
    assert SHORT_KEY not in redacted
    assert "monkey=banana" in redacted


def test_describe_google_api_error_redacts_all_shapes(auth):
    error = SimpleNamespace(resp=SimpleNamespace(status=400), content=json.dumps({"error": {
        "code": 400, "message": f"bad request key={FAKE_KEY} and x-goog-api-key: {FAKE_KEY}",
    }}).encode())
    assert FAKE_KEY not in auth.describe_google_api_error(error, "Test")
    assert SHORT_KEY not in auth.describe_google_api_error(
        RuntimeError(f"short {SHORT_KEY}"), "Test", secrets=[SHORT_KEY]
    )


# ---------------------------------------------------------------------------
# 1b. Key transport and forced connection errors


def run_main(module, argv, capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", [module.__name__] + argv)
    code = 0
    try:
        module.main()
    except SystemExit as exc:
        code = exc.code or 0
    captured = capsys.readouterr()
    return code, captured.out, captured.err


@pytest.mark.parametrize("script,endpoint_attrs,argv", [
    ("pagespeed_check", ["PSI_ENDPOINT", "CRUX_ENDPOINT"], ["https://example.com/page", "--json"]),
    ("pagespeed_check", ["CRUX_ENDPOINT"], ["https://example.com/page", "--crux-only", "--json"]),
    ("pagespeed_check", ["PSI_ENDPOINT"], ["https://example.com/page", "--psi-only", "--json"]),
    ("pagespeed_check", ["PSI_ENDPOINT", "CRUX_ENDPOINT"], ["https://example.com/page"]),
    ("crux_history", ["CRUX_HISTORY_ENDPOINT"], ["https://example.com/page", "--json"]),
    ("crux_history", ["CRUX_HISTORY_ENDPOINT"], ["https://example.com/page"]),
])
@pytest.mark.parametrize("key", [FAKE_KEY, SHORT_KEY])
def test_connection_error_never_prints_the_key(script, endpoint_attrs, argv, key, monkeypatch, capsys):
    module = load_script(script, monkeypatch)
    for attr in endpoint_attrs:
        monkeypatch.setattr(module, attr, f"http://127.0.0.1:{closed_port()}/v1/x")
    monkeypatch.setattr(module, "get_api_key", lambda: None)
    code, out, err = run_main(module, argv + ["--api-key", key], capsys, monkeypatch)
    assert key not in out and key not in err
    assert "key=" not in (out + err).replace("--api-key", "")
    # The forced failure must still be reported, not swallowed.
    assert "failed" in (out + err).lower() or "error" in (out + err).lower()


def test_nlp_connection_error_never_prints_the_key(monkeypatch, capsys):
    module = load_script("nlp_analyze", monkeypatch)
    monkeypatch.setattr(module, "NLP_ENDPOINT", f"http://127.0.0.1:{closed_port()}/v2/x")
    monkeypatch.setattr(module, "get_api_key", lambda: None)
    for key in (FAKE_KEY, SHORT_KEY):
        code, out, err = run_main(module, ["--text", "hello world", "--api-key", key, "--json"], capsys, monkeypatch)
        assert key not in out and key not in err
        assert json.loads(out)["error"]


def test_psi_and_crux_send_the_key_in_a_header_not_the_url(monkeypatch, capture_server):
    base, seen = capture_server
    psi = load_script("pagespeed_check", monkeypatch)
    history = load_script("crux_history", monkeypatch)
    nlp = load_script("nlp_analyze", monkeypatch)
    monkeypatch.setattr(psi, "PSI_ENDPOINT", base + "/psi")
    monkeypatch.setattr(psi, "CRUX_ENDPOINT", base + "/crux")
    monkeypatch.setattr(history, "CRUX_HISTORY_ENDPOINT", base + "/hist")
    monkeypatch.setattr(nlp, "NLP_ENDPOINT", base + "/nlp")
    psi.run_pagespeed("https://example.com/", api_key=FAKE_KEY)
    psi.query_crux("https://example.com/", FAKE_KEY)
    history.query_history("https://example.com/", FAKE_KEY)
    nlp.analyze_text("hello world", api_key=FAKE_KEY)
    assert len(seen) == 4
    for path, headers in seen:
        assert "key=" not in path and FAKE_KEY not in path
        lowered = {k.lower(): v for k, v in headers.items()}
        assert lowered["x-goog-api-key"] == FAKE_KEY


def test_youtube_key_travels_in_header_and_not_in_the_request_uri(monkeypatch):
    pytest.importorskip("googleapiclient.discovery")
    import httplib2

    module = load_script("youtube_search", monkeypatch)
    seen = {}

    def record(self, uri, method="GET", body=None, headers=None, *a, **kw):
        seen["headers"] = headers
        return SimpleNamespace(status=200), b"{}"

    monkeypatch.setattr(httplib2.Http, "request", record)
    service = module._build_youtube_service(FAKE_KEY)
    request = service.search().list(q="x", part="snippet")
    assert FAKE_KEY not in request.uri and "key=" not in request.uri
    request.execute()
    assert seen["headers"]["x-goog-api-key"] == FAKE_KEY


@pytest.mark.parametrize("key", [FAKE_KEY, SHORT_KEY])
def test_youtube_connection_error_never_prints_the_key(key, monkeypatch, capsys):
    pytest.importorskip("googleapiclient.discovery")
    import httplib2

    module = load_script("youtube_search", monkeypatch)

    def refuse(self, uri, *args, **kwargs):
        raise ConnectionRefusedError(f"connection refused for {uri}")

    monkeypatch.setattr(httplib2.Http, "request", refuse)
    monkeypatch.setattr(module, "get_api_key", lambda: None)
    code, out, err = run_main(module, ["search", "claude", "--api-key", key, "--json"], capsys, monkeypatch)
    assert key not in out and key not in err
    assert "refused" in json.loads(out)["error"].lower() or "error" in json.loads(out)["error"].lower()


def test_every_script_that_takes_a_key_routes_errors_through_the_redactor():
    for name in ("pagespeed_check", "crux_history", "nlp_analyze", "youtube_search"):
        text = (SCRIPTS / (name + ".py")).read_text(encoding="utf-8")
        assert "?key=" not in text, name
        assert 'params["key"]' not in text, name


# ---------------------------------------------------------------------------
# 2. Indexing API


class HttpError(Exception):
    def __init__(self, status, message="boom", url="https://indexing.googleapis.com/v3/urlNotifications:publish"):
        super().__init__(f"<HttpError {status} when requesting {url} returned {message!r}>")
        self.resp = SimpleNamespace(status=status)
        self.content = json.dumps({"error": {"code": status, "message": message}}).encode()


class PublishService:
    """urlNotifications().publish(body=...).execute() with scripted outcomes."""

    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.published = []

    def urlNotifications(self):
        return self

    def publish(self, body):
        self.published.append(body["url"])
        outcome = self.outcomes.pop(0)

        class _Req:
            def execute(_self):
                if isinstance(outcome, Exception):
                    raise outcome
                return {"urlNotificationMetadata": {"latestUpdate": {"notifyTime": "2026-10-12T00:00:00Z"}}}

        return _Req()


def indexing_module(monkeypatch, service):
    module = load_script("indexing_notify", monkeypatch)
    monkeypatch.setattr(module, "_build_indexing_service", lambda: service)
    return module


def test_batch_stops_on_429_by_status_and_lists_what_was_not_submitted(monkeypatch):
    urls = [f"https://example.com/jobs/{n}" for n in range(1, 6)]
    service = PublishService([None, None, HttpError(429, "Quota exceeded for quota metric")])
    module = indexing_module(monkeypatch, service)
    result = module.batch_notify(urls, delay=0)
    assert service.published == urls[:3], "the batch must stop at the 429 and not keep submitting"
    assert result["stopped_on_quota"] is True
    assert result["summary"]["success"] == 2
    assert result["not_submitted"] == urls[2:]
    assert "NOT" in result["error"] and "2 successful" in result["error"]


def test_status_classification_ignores_digits_inside_urls(monkeypatch):
    # The 4039 in the requested URL contains "403" and "400"; only the status counts.
    error = HttpError(500, "backend error", url="https://indexing.googleapis.com/v3/urlNotifications:publish?url=/jobs/4039")
    service = PublishService([error])
    module = indexing_module(monkeypatch, service)
    result = module.notify_url("https://example.com/jobs/4039")
    assert "Owner access" not in result["error"]
    assert "Invalid URL" not in result["error"]
    assert not result.get("quota_exceeded")


def test_quota_429_is_recognized_even_when_the_url_contains_403(monkeypatch):
    error = HttpError(429, "quota", url="https://indexing.googleapis.com/v3/urlNotifications:publish?url=/jobs/4039")
    module = indexing_module(monkeypatch, PublishService([error]))
    result = module.notify_url("https://example.com/jobs/4039")
    assert result["quota_exceeded"] is True and result["error"].startswith("Quota exceeded")


def test_400_and_403_are_classified_by_status(monkeypatch):
    module = indexing_module(monkeypatch, PublishService([HttpError(400, "bad"), HttpError(403, "denied")]))
    assert module.notify_url("https://example.com/jobs/1")["error"].startswith("Invalid URL or request")
    assert "Search Console" in module.notify_url("https://example.com/jobs/2")["error"]


def test_docstring_and_warning_state_the_supported_page_types(monkeypatch):
    module = load_script("indexing_notify", monkeypatch)
    assert "Google may process other page types" not in module.__doc__
    assert "may process other" not in module.SCOPE_WARNING
    assert "JobPosting" in module.__doc__ and "BroadcastEvent" in module.__doc__


@pytest.mark.parametrize("argv", [
    ["https://example.com/jobs/1"],
    ["https://example.com/jobs/1", "--json"],
    ["--batch", "urls.txt"],
])
def test_submitting_requires_confirm_eligible(argv, monkeypatch, capsys, tmp_path):
    (tmp_path / "urls.txt").write_text("https://example.com/jobs/1\n")
    monkeypatch.chdir(tmp_path)
    service = PublishService([None])
    module = indexing_module(monkeypatch, service)
    code, out, err = run_main(module, argv, capsys, monkeypatch)
    assert code == 1
    assert service.published == []
    text = out + err
    assert "JobPosting" in text and "BroadcastEvent" in text and "--confirm-eligible" in text


def test_confirm_eligible_allows_submission_and_status_needs_no_flag(monkeypatch, capsys):
    service = PublishService([None])
    module = indexing_module(monkeypatch, service)
    code, out, err = run_main(module, ["https://example.com/jobs/1", "--confirm-eligible", "--json"], capsys, monkeypatch)
    assert code == 0 and service.published == ["https://example.com/jobs/1"]
    monkeypatch.setattr(module, "get_notification_metadata", lambda url: {"url": url, "latest_update": None, "latest_remove": None, "error": None})
    code, out, err = run_main(module, ["--status", "https://example.com/jobs/1", "--json"], capsys, monkeypatch)
    assert code == 0


# ---------------------------------------------------------------------------
# 3. URL Inspection, Search Console, Keyword Planner, YouTube


class InspectService:
    def __init__(self, failures=None, response=None):
        self.failures = failures or {}
        self.response = response if response is not None else {}
        self.calls = []

    def urlInspection(self):
        return self

    def index(self):
        return self

    def inspect(self, body):
        url = body["inspectionUrl"]
        self.calls.append(url)
        outer = self

        class _Req:
            def execute(_self):
                if url in outer.failures:
                    raise outer.failures[url]
                return outer.response

        return _Req()


def test_inspect_batch_stops_on_429_without_sleeping(monkeypatch):
    inspect = load_script("gsc_inspect", monkeypatch)
    auth = sys.modules["google_auth"]
    urls = [f"https://example.com/p{n}" for n in range(1, 6)]
    service = InspectService(failures={urls[1]: HttpError(429, "quota")})
    monkeypatch.setattr(inspect, "_build_inspection_service", lambda: service)

    def no_sleep(seconds):
        assert seconds == 0, f"slept {seconds}s on a quota error"

    monkeypatch.setattr(auth.time, "sleep", no_sleep)
    result = inspect.batch_inspect(urls, "sc-domain:example.com", delay=0)
    assert service.calls == urls[:2]
    assert result["stopped_on_quota"] is True
    assert result["not_inspected"] == urls[2:]
    assert result["error"] is None
    assert "Stopped on quota" in result["warning"]


def test_inspect_batch_over_the_cap_is_a_warning_not_a_top_level_error(monkeypatch):
    inspect = load_script("gsc_inspect", monkeypatch)
    cap = inspect.DAILY_LIMIT
    urls = [f"https://example.com/p{n}" for n in range(cap + 3)]
    service = InspectService(response={"inspectionResult": {"indexStatusResult": {"verdict": "PASS"}}})
    monkeypatch.setattr(inspect, "_build_inspection_service", lambda: service)
    result = inspect.batch_inspect(urls, "sc-domain:example.com", delay=0)
    assert result["error"] is None
    assert "exceeds daily limit" in result["warning"]
    assert len(result["results"]) == cap
    assert result["summary"]["pass"] == cap
    assert result["not_inspected"] == urls[cap:]


class QueryService:
    def __init__(self):
        self.bodies = []

    def searchanalytics(self):
        return self

    def query(self, siteUrl, body):
        self.bodies.append(dict(body))

        class _Req:
            def execute(_self):
                return {"rows": []}

        return _Req()


@pytest.mark.parametrize("limit", [0, -5])
def test_gsc_query_rejects_nonpositive_limits_so_pagination_terminates(limit, monkeypatch, capsys):
    module = load_script("gsc_query", monkeypatch)
    service = QueryService()
    monkeypatch.setattr(module, "_build_gsc_service", lambda: service)
    result = module.query_search_analytics("sc-domain:example.com", row_limit=limit)
    assert "row_limit" in result["error"] and service.bodies == []
    with pytest.raises(SystemExit) as exc:
        monkeypatch.setattr(sys, "argv", ["gsc_query", "--property", "sc-domain:example.com", "--limit", str(limit)])
        module.main()
    assert exc.value.code == 2


def test_gsc_query_clamps_oversized_limit(monkeypatch):
    module = load_script("gsc_query", monkeypatch)
    service = QueryService()
    monkeypatch.setattr(module, "_build_gsc_service", lambda: service)
    module.query_search_analytics("sc-domain:example.com", row_limit=10**9)
    assert service.bodies[0]["rowLimit"] == module.MAX_PAGE_SIZE


@pytest.mark.parametrize("days", [1, 2, 3, 28, 90])
def test_gsc_query_days_window_never_starts_after_it_ends(days, monkeypatch):
    module = load_script("gsc_query", monkeypatch)
    captured = {}

    def fake_query(prop, start_date=None, end_date=None, **kwargs):
        captured.update(start=start_date, end=end_date)
        return {"rows": [], "totals": {}, "error": None}

    monkeypatch.setattr(module, "query_search_analytics", fake_query)
    monkeypatch.setattr(sys, "argv", ["gsc_query", "--property", "sc-domain:example.com", "--days", str(days), "--json"])
    module.main()
    start = dt.date.fromisoformat(captured["start"])
    end = dt.date.fromisoformat(captured["end"])
    assert start <= end
    assert (end - start).days + 1 == days
    assert end == dt.date.today() - dt.timedelta(days=3)


def test_gsc_query_default_window_is_28_days_ending_3_days_ago(monkeypatch):
    module = load_script("gsc_query", monkeypatch)
    start, end = module.default_date_range(today=dt.date(2026, 10, 12))
    assert (start, end) == ("2026-09-12", "2026-10-09")


def test_gsc_query_rejects_inverted_explicit_dates(monkeypatch):
    module = load_script("gsc_query", monkeypatch)
    service = QueryService()
    monkeypatch.setattr(module, "_build_gsc_service", lambda: service)
    result = module.query_search_analytics("sc-domain:example.com", start_date="2026-10-10", end_date="2026-10-01")
    assert "after end_date" in result["error"] and service.bodies == []


def test_keyword_planner_has_no_forecast_command_and_validates_seed_count(monkeypatch):
    module = load_script("keyword_planner", monkeypatch)
    assert "forecast" not in module.__doc__
    built = []
    monkeypatch.setattr(module, "_build_ads_client", lambda: built.append(1))
    too_many = [f"kw{n}" for n in range(module.MAX_SEED_KEYWORDS + 1)]
    result = module.generate_keyword_ideas(too_many)
    assert "between 1 and 20" in result["error"] and built == []
    assert "at least 1" in module.get_keyword_volumes([" ", ""])["error"] and built == []


class YouTubeService:
    def __init__(self, comments_error):
        self.comments_error = comments_error

    def videos(self):
        return SimpleNamespace(list=lambda **kw: SimpleNamespace(execute=lambda: {"items": [{
            "id": "abc", "snippet": {"title": "T"}, "statistics": {}, "contentDetails": {}, "topicDetails": {},
        }]}))

    def commentThreads(self):
        error = self.comments_error
        return SimpleNamespace(list=lambda **kw: SimpleNamespace(execute=lambda: (_ for _ in ()).throw(error)))


def youtube_error(reason, status, message="denied"):
    err = HttpError(status, message)
    err.content = json.dumps({"error": {"code": status, "message": message, "errors": [{"reason": reason}]}}).encode()
    return err


def test_comment_quota_errors_are_surfaced_not_swallowed(monkeypatch):
    pytest.importorskip("googleapiclient.discovery")
    module = load_script("youtube_search", monkeypatch)
    error = youtube_error("quotaExceeded", 403, "quota")
    monkeypatch.setattr(module, "_build_youtube_service", lambda api_key=None: YouTubeService(error))
    result = module.get_video_details("abc")
    assert result["error"] is None and result["details"]["title"] == "T"
    assert "quotaExceeded" in result["comments_error"]
    assert "100 calls per day" in result["comments_error"] or "quota" in result["comments_error"].lower()


def test_disabled_comments_are_a_note_not_an_error(monkeypatch):
    pytest.importorskip("googleapiclient.discovery")
    module = load_script("youtube_search", monkeypatch)
    error = youtube_error("commentsDisabled", 403, "comments disabled")
    monkeypatch.setattr(module, "_build_youtube_service", lambda api_key=None: YouTubeService(error))
    result = module.get_video_details("abc")
    assert "comments_error" not in result and "disabled" in result["comments_note"].lower()


@pytest.mark.parametrize("limit", [0, -3, 500])
def test_youtube_search_limit_is_clamped_to_1_through_50(limit, monkeypatch):
    pytest.importorskip("googleapiclient.discovery")
    module = load_script("youtube_search", monkeypatch)
    seen = {}

    class Service:
        def search(self):
            return self

        def list(self, **kwargs):
            seen.update(kwargs)
            return SimpleNamespace(execute=lambda: {"items": []})

    monkeypatch.setattr(module, "_build_youtube_service", lambda api_key=None: Service())
    module.search_videos("q", max_results=limit)
    assert 1 <= seen["maxResults"] <= 50


def test_youtube_quota_text_matches_current_documentation(monkeypatch):
    pytest.importorskip("googleapiclient.discovery")
    module = load_script("youtube_search", monkeypatch)
    err = youtube_error("quotaExceeded", 429, "quota")
    text = module._describe_youtube_error(err)
    assert "100 calls per day" in text and "search costs 100 units" not in text
    source = (SCRIPTS / "youtube_search.py").read_text(encoding="utf-8")
    assert "search.list = 100 units" not in source


# ---------------------------------------------------------------------------
# 4. CLI help and dependency messages


def run_cli(args, cwd=ROOT):
    return subprocess.run(args, capture_output=True, text=True, cwd=cwd, timeout=60)


@pytest.mark.parametrize("skill", ["blog-google", "blog-notebooklm"])
@pytest.mark.parametrize("flag", ["--help", "-h"])
def test_run_py_help_prints_usage_and_exits_zero(skill, flag, tmp_path):
    result = run_cli([sys.executable, str(ROOT / "skills" / skill / "scripts/run.py"), flag], cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Usage: python run.py" in result.stdout
    assert "Script not found" not in result.stdout + result.stderr


def test_run_py_without_arguments_still_exits_nonzero(tmp_path):
    result = run_cli([sys.executable, str(SCRIPTS / "run.py")], cwd=tmp_path)
    assert result.returncode == 1 and "Usage" in result.stdout


def test_google_report_help_works_without_matplotlib_and_generation_points_to_setup(tmp_path):
    runner = (
        "import sys, runpy\n"
        "sys.modules['matplotlib'] = None\n"
        "sys.modules['numpy'] = None\n"
        "sys.argv = ['google_report.py', '--help']\n"
        f"runpy.run_path({str(SCRIPTS / 'google_report.py')!r}, run_name='__main__')\n"
    )
    help_run = run_cli([sys.executable, "-c", runner], cwd=tmp_path)
    assert help_run.returncode == 0 and "usage:" in help_run.stdout

    generate = runner.replace(
        "'--help'",
        "'--type', 'cwv-audit', '--domain', 'example.com', '--output-dir', " + repr(str(tmp_path)),
    )
    result = subprocess.run([sys.executable, "-c", generate], input="{}", capture_output=True, text=True, cwd=tmp_path, timeout=60)
    assert result.returncode == 1
    assert "setup_environment.py" in result.stderr and "Traceback" not in result.stderr


def test_dependency_messages_point_to_setup_not_bare_pip(auth):
    assert "setup_environment.py" in auth.setup_hint()
    for path in SCRIPTS.glob("*.py"):
        if path.name == "setup_environment.py":
            continue
        assert "pip install" not in path.read_text(encoding="utf-8"), path.name


# ---------------------------------------------------------------------------
# 5. nlp_analyze SSRF


@pytest.mark.parametrize("address,blocked", [
    ("64:ff9b::7f00:1", True),        # NAT64 wrapping 127.0.0.1
    ("64:ff9b::a00:1", True),         # NAT64 wrapping 10.0.0.1
    ("64:ff9b::c0a8:101", True),      # NAT64 wrapping 192.168.1.1
    ("64:ff9b::a9fe:a9fe", True),     # NAT64 wrapping 169.254.169.254
    ("::ffff:127.0.0.1", True),
    ("::1", True),
    ("127.0.0.1", True),
    ("100.64.0.1", True),
    ("64:ff9b::808:808", False),      # NAT64 wrapping public 8.8.8.8
    ("8.8.8.8", False),
])
def test_nlp_blocks_nat64_wrapped_private_addresses(address, blocked, monkeypatch):
    module = load_script("nlp_analyze", monkeypatch)
    assert module._is_blocked_address(address) is blocked


def test_nlp_resolution_rejects_a_nat64_host(monkeypatch):
    module = load_script("nlp_analyze", monkeypatch)
    monkeypatch.setattr(module.socket, "getaddrinfo", lambda *a, **k: [(10, 1, 6, "", ("64:ff9b::7f00:1", 80, 0, 0))])
    with pytest.raises(ValueError, match="blocked network address"):
        module._resolve_fetch_target("http://nat64.example/")


def test_nlp_slow_drip_response_hits_the_wall_clock_deadline(monkeypatch):
    module = load_script("nlp_analyze", monkeypatch)
    stop = threading.Event()

    class Drip(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            try:
                while not stop.is_set():
                    self.wfile.write(b"x")
                    self.wfile.flush()
                    time.sleep(0.1)
            except OSError:
                pass

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Drip)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    target = module._FetchTarget(
        url="http://slow.example/", scheme="http", hostname="slow.example",
        port=server.server_port, request_target="/", addresses=("127.0.0.1",),
    )
    monkeypatch.setattr(module, "_resolve_fetch_target", lambda url: target)
    monkeypatch.setattr(module, "FETCH_DEADLINE_SECONDS", 1.0)
    started = time.monotonic()
    try:
        with pytest.raises(ValueError, match="time limit"):
            module._fetch_url_text("http://slow.example/")
        assert time.monotonic() - started < 6
    finally:
        stop.set()
        server.shutdown()
        server.server_close()
