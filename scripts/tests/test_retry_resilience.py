import pytest
from unittest.mock import MagicMock
from scripts.retry_utils import retry_with_backoff

class FakeHttpError(Exception):
    def __init__(self, status):
        self.status_code = status

def test_retry_success_after_rate_limit(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    mock_func = MagicMock(side_effect=[FakeHttpError(429), FakeHttpError(429), {"rows": []}])
    
    decorated = retry_with_backoff(retries=3, initial_delay=0.1)(mock_func)
    result = decorated()

    assert result == {"rows": []}
    assert mock_func.call_count == 3

def test_retry_raises_non_retryable_error(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    mock_func = MagicMock(side_effect=FakeHttpError(404))
    
    decorated = retry_with_backoff(retries=3)(mock_func)
    with pytest.raises(FakeHttpError):
        decorated()

    assert mock_func.call_count == 1
