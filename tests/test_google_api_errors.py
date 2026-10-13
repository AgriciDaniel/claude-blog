"""Google error diagnostics distinguish configuration from property access."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/blog-google/scripts"


def load_script(name, monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("error_test_" + name, SCRIPTS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class APIError(Exception):
    def __init__(self, reason, status=403, message="Google API request denied"):
        super().__init__(f"{status} {reason}: {message}")
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


@pytest.mark.parametrize("reason", ["accessNotConfigured", "SERVICE_DISABLED", "API_DISABLED"])
@pytest.mark.parametrize("script", ["gsc_query", "gsc_inspect", "indexing_notify"])
def test_disabled_api_does_not_send_operator_to_property_permissions(script, reason, monkeypatch):
    module = load_script(script, monkeypatch)
    service = FailingService(APIError(reason))
    if script == "gsc_query":
        monkeypatch.setattr(module, "_build_gsc_service", lambda: service)
        result = module.query_search_analytics("https://example.com/")
    elif script == "gsc_inspect":
        result = module.inspect_url("https://example.com/post", "https://example.com/", service=service)
    else:
        monkeypatch.setattr(module, "_build_indexing_service", lambda: service)
        result = module.notify_url("https://example.com/post")
    assert "enable" in result["error"].lower()
    assert reason in result["error"]
    assert "Permission denied" not in result["error"]


@pytest.mark.parametrize("reason,word", [
    ("API_KEY_SERVICE_BLOCKED", "restriction"),
    ("BILLING_DISABLED", "billing"),
    ("quotaExceeded", "quota"),
])
def test_actionable_non_permission_reasons(reason, word, monkeypatch):
    auth = load_script("google_auth", monkeypatch)
    message = auth.describe_google_api_error(APIError(reason), "Search Console", "Property permission denied")
    assert word in message.lower()
    assert reason in message
    assert "Property permission denied" not in message


def test_true_permission_error_retains_property_guidance(monkeypatch):
    auth = load_script("google_auth", monkeypatch)
    message = auth.describe_google_api_error(APIError("insufficientPermissions"), "Search Console", "Add the service account to this property")
    assert "Add the service account to this property" in message
    assert "insufficientPermissions" in message


def test_unknown_error_diagnostic_redacts_query_credentials(monkeypatch):
    auth = load_script("google_auth", monkeypatch)
    error = APIError("unknownReason", message="https://api.example.com/?key=fixture-secret&access_token=fixture-token")
    message = auth.describe_google_api_error(error, "Google", "Permission denied")
    assert "unknownReason" in message
    assert "fixture-secret" not in message
    assert "fixture-token" not in message


def test_nlp_rest_error_keeps_disabled_reason(monkeypatch):
    module = load_script("nlp_analyze", monkeypatch)
    payload = json.loads(APIError("SERVICE_DISABLED").content)
    response = SimpleNamespace(status_code=403, json=lambda: payload)
    monkeypatch.setattr(module, "request_with_retries", lambda *args, **kwargs: response)
    result = module.analyze_text("Fixture", api_key="fixture-not-used")
    assert "SERVICE_DISABLED" in result["error"]
    assert "enable" in result["error"].lower()


@pytest.mark.parametrize("reason", ["accessNotConfigured", "SERVICE_DISABLED"])
def test_ga4_disabled_api_is_not_property_access_failure(reason, monkeypatch):
    pytest.importorskip("google.analytics.data_v1beta")
    module = load_script("ga4_report", monkeypatch)

    def fail_report(*args, **kwargs):
        raise APIError(reason)

    monkeypatch.setattr(module, "_build_ga4_client", lambda: SimpleNamespace(run_report=fail_report))
    result = module.organic_traffic_report("123")
    assert reason in result["error"]
    assert "enable" in result["error"].lower()
    assert "Property Access Management" not in result["error"]
