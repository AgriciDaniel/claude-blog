"""youtube_search keeps the Google error reason instead of blaming a disabled API.

Issue #65 follow-up: the other Google helpers already use
describe_google_api_error; youtube_search still keyed on the "403" substring.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/blog-google/scripts"


def load_script(name, monkeypatch):
    pytest.importorskip("googleapiclient.discovery")
    monkeypatch.syspath_prepend(str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("yt_error_test_" + name, SCRIPTS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class APIError(Exception):
    def __init__(self, reason, status=403, message="Google API request denied"):
        super().__init__(f"<HttpError {status} when requesting https://example.test/?key=fixture-secret: {message}>")
        self.resp = SimpleNamespace(status=status)
        self.content = json.dumps({"error": {
            "code": status, "message": message,
            "errors": [{"reason": reason}],
            "details": [{"@type": "type.googleapis.com/google.rpc.ErrorInfo", "reason": reason}],
        }}).encode()


class FailingService:
    def __init__(self, error):
        self.error = error

    def __getattr__(self, _name):
        return self

    def __call__(self, *args, **kwargs):
        return self

    def execute(self):
        raise self.error


def run(module, monkeypatch, function, error):
    monkeypatch.setattr(module, "_build_youtube_service", lambda api_key=None: FailingService(error))
    return getattr(module, function)("fixture")


CALLS = ["search_videos", "get_video_details", "get_channel_info"]


@pytest.mark.parametrize("function", CALLS)
@pytest.mark.parametrize("reason", ["API_KEY_SERVICE_BLOCKED", "BILLING_DISABLED", "forbidden"])
def test_403_for_other_reasons_is_not_reported_as_disabled_api(function, reason, monkeypatch):
    module = load_script("youtube_search", monkeypatch)
    error = run(module, monkeypatch, function, APIError(reason))["error"]
    assert reason in error
    assert "Ensure the API is enabled" not in error
    assert "fixture-secret" not in error


@pytest.mark.parametrize("function", CALLS)
@pytest.mark.parametrize("reason", ["accessNotConfigured", "SERVICE_DISABLED", "API_DISABLED"])
def test_disabled_api_keeps_reason_and_enable_guidance(function, reason, monkeypatch):
    module = load_script("youtube_search", monkeypatch)
    error = run(module, monkeypatch, function, APIError(reason))["error"]
    assert reason in error
    assert "enable" in error.lower()


def test_quota_error_keeps_reason_and_daily_quota_note(monkeypatch):
    module = load_script("youtube_search", monkeypatch)
    error = run(module, monkeypatch, "search_videos", APIError("quotaExceeded", status=403))["error"]
    assert "quotaExceeded" in error
    error = run(module, monkeypatch, "search_videos", APIError("rateLimitExceeded", status=429))["error"]
    assert "rateLimitExceeded" in error
    assert "10,000" in error


def test_video_and_channel_errors_redact_credentials(monkeypatch):
    module = load_script("youtube_search", monkeypatch)
    for function in ("get_video_details", "get_channel_info"):
        error = run(module, monkeypatch, function, APIError("unknownReason", status=500))["error"]
        assert "unknownReason" in error
        assert "fixture-secret" not in error
