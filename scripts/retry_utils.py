import time
import random
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry_with_backoff(
    retries=4,
    initial_delay=1.0,
    backoff_factor=2.0,
    jitter=True,
    retryable_status_codes=(429, 500, 502, 503, 504)
):
    """
    Exponential backoff decorator with jitter for API calls.
    Specifically handles rate limits (HTTP 429) and transient server errors.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    status_code = getattr(getattr(exc, "resp", None), "status", None)
                    if status_code is None and hasattr(exc, "status_code"):
                        status_code = exc.status_code

                    # Agar retryable error nahi hai ya aakhri attempt hai, to error throw karein
                    if attempt == retries or (status_code and status_code not in retryable_status_codes):
                        logger.error(f"Execution failed on attempt {attempt}/{retries}: {exc}")
                        raise

                    sleep_time = delay * (1 + random.uniform(0, 0.1) if jitter else 1)
                    logger.warning(
                        f"Retryable error ({status_code or type(exc).__name__}) on attempt {attempt}/{retries}. "
                        f"Retrying in {sleep_time:.2f}s..."
                    )
                    time.sleep(sleep_time)
                    delay *= backoff_factor
            return func(*args, **kwargs)
        return wrapper
    return decorator
