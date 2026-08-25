#!/usr/bin/env python3
"""
Google API credential management for Claude SEO.

Loads and validates credentials for Google Search Console, PageSpeed Insights,
CrUX, Indexing API, and GA4. Supports service accounts, OAuth web credentials
with token refresh, API keys, and environment variable fallbacks.

Usage:
    python google_auth.py --check                  # Check all credentials
    python google_auth.py --check gsc              # Check specific service
    python google_auth.py --check --json            # JSON output
    python google_auth.py --setup                   # Show setup instructions
    python google_auth.py --tier                    # Show detected credential tier
    python google_auth.py --auth --creds /path/to/client_secret.json  # OAuth browser flow
"""

import argparse
import json
import os
import random
import secrets
import sys
import tempfile
import time
from typing import Optional

CONFIG_PATH = os.path.expanduser("~/.config/claude-seo/google-api.json")
TOKEN_PATH = os.path.expanduser("~/.config/claude-seo/oauth-token.json")

# Service-to-scope mapping
SCOPES = {
    "gsc_readonly": "https://www.googleapis.com/auth/webmasters.readonly",
    "gsc_write": "https://www.googleapis.com/auth/webmasters",
    "indexing": "https://www.googleapis.com/auth/indexing",
    "ga4": "https://www.googleapis.com/auth/analytics.readonly",
}

# Which services need which auth type
SERVICE_AUTH = {
    "psi": "api_key",
    "crux": "api_key",
    "crux_history": "api_key",
    "youtube": "api_key",
    "nlp": "api_key",
    "gsc": "oauth_or_sa",
    "indexing": "oauth_or_sa",
    "ga4": "oauth_or_sa",
    "keywords": "ads",
}

OAUTH_REDIRECT_URI = "http://127.0.0.1:8085"


def _write_secret_atomic(path: str, content: str) -> None:
    """Atomically write `content` to `path` with mode 0o600.

    Uses tempfile in same dir + os.replace for atomicity (no partial writes
    on crash). Sets restrictive file mode before writing payload.
    """
    # Bare-filename safety: os.path.dirname returns "" if path has no dir
    # component. Pass that to mkstemp(dir="") and it errors with FileNotFoundError.
    parent = os.path.dirname(path) or "."
    os.makedirs(parent, mode=0o700, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=parent, prefix=".tmp-")
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(content)
        os.replace(tmp, path)
        os.chmod(path, 0o600)  # belt-and-braces if file pre-existed
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _scopes_for(services: list = None) -> str:
    """Build OAuth scope string for the requested services.

    Defaults to a read-only set so OAuth-without-flag grants minimal scopes.
    """
    if services is None:
        # Safer default: read-only scopes only.
        services = ["gsc_readonly", "ga4"]
    scope_urls = []
    for s in services:
        if s in SCOPES:
            scope_urls.append(SCOPES[s])
        else:
            raise ValueError(f"Unknown scope service: {s}")
    return " ".join(scope_urls)

# Human-readable service names
SERVICE_NAMES = {
    "psi": "PageSpeed Insights v5",
    "crux": "Chrome UX Report (CrUX) API",
    "crux_history": "CrUX History API",
    "youtube": "YouTube Data API v3",
    "nlp": "Cloud Natural Language API",
    "gsc": "Google Search Console API",
    "indexing": "Google Indexing API v3",
    "ga4": "GA4 Data API v1beta",
    "keywords": "Google Ads Keyword Planner",
}


def _retry_delay(headers: dict, attempt: int) -> float:
    retry_after = None
    if headers:
        retry_after = headers.get("Retry-After") or headers.get("retry-after")
    if retry_after:
        try:
            return min(float(retry_after), 60.0)
        except ValueError:
            pass
    return min(2 ** attempt, 16) + random.uniform(0, 0.5)


def request_with_retries(method: str, url: str, max_attempts: int = 5, **kwargs):
    """Run a requests call with Google-friendly Retry-After backoff."""
    try:
        import requests
    except ImportError:
        raise RuntimeError("requests library required")

    retry_statuses = {429, 500, 502, 503, 504}
    last_response = None
    for attempt in range(max_attempts):
        response = requests.request(method, url, **kwargs)
        last_response = response
        if response.status_code not in retry_statuses:
            return response
        if attempt == max_attempts - 1:
            return response
        time.sleep(_retry_delay(response.headers, attempt))
    return last_response


def execute_with_retries(request, max_attempts: int = 5):
    """Execute a googleapiclient request with Retry-After backoff."""
    retry_statuses = {429, 500, 502, 503, 504}
    for attempt in range(max_attempts):
        try:
            return request.execute()
        except Exception as exc:
            status = getattr(getattr(exc, "resp", None), "status", None)
            headers = getattr(getattr(exc, "resp", None), "headers", {}) or {}
            if status not in retry_statuses or attempt == max_attempts - 1:
                raise
            time.sleep(_retry_delay(headers, attempt))


def load_config() -> dict:
    """
    Load configuration from config file with environment variable fallbacks.

    Reads ~/.config/claude-seo/google-api.json first. Any missing fields
    are filled from environment variables.

    Returns:
        Dictionary with keys: service_account_path, api_key,
        default_property, ga4_property_id. Missing values are None.
    """
    config = {
        "service_account_path": None,
        "api_key": None,
        "oauth_client_path": None,
        "default_property": None,
        "ga4_property_id": None,
        "ads_developer_token": None,
        "ads_customer_id": None,
        "ads_login_customer_id": None,
    }

    # Load from config file
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                file_config = json.load(f)
            config.update({k: v for k, v in file_config.items() if v})
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not read config file: {e}", file=sys.stderr)

    # Environment variable fallbacks
    if not config["service_account_path"]:
        config["service_account_path"] = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    if not config["api_key"]:
        config["api_key"] = os.environ.get("GOOGLE_API_KEY")

    if not config["ga4_property_id"]:
        config["ga4_property_id"] = os.environ.get("GA4_PROPERTY_ID")

    if not config["default_property"]:
        config["default_property"] = os.environ.get("GSC_PROPERTY")

    if not config["oauth_client_path"]:
        config["oauth_client_path"] = os.environ.get("GOOGLE_OAUTH_CLIENT_PATH")

    if not config["ads_developer_token"]:
        config["ads_developer_token"] = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")

    if not config["ads_customer_id"]:
        config["ads_customer_id"] = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")

    if not config["ads_login_customer_id"]:
        config["ads_login_customer_id"] = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID")

    return config


def _save_config_value(key: str, value: str) -> None:
    """Persist one config value without weakening file permissions."""
    config = {}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError):
            config = {}
    config[key] = value
    _write_secret_atomic(CONFIG_PATH, json.dumps(config, indent=2))


def get_service_account_credentials(scopes: list):
    """
    Load Google service account credentials.

    Args:
        scopes: List of OAuth scope URLs.

    Returns:
        google.oauth2.service_account.Credentials object, or None on failure.
    """
    try:
        from google.oauth2 import service_account
    except ImportError:
        print(
            "Error: google-auth library required. "
            "Install with: pip install google-auth",
            file=sys.stderr,
        )
        return None

    config = load_config()
    sa_path = config.get("service_account_path")

    if not sa_path:
        return None

    sa_path = os.path.expanduser(sa_path)
    if not os.path.exists(sa_path):
        print(
            f"Error: Service account file not found: {sa_path}",
            file=sys.stderr,
        )
        return None

    try:
        credentials = service_account.Credentials.from_service_account_file(
            sa_path, scopes=scopes
        )
        return credentials
    except Exception as e:
        print(f"Error loading service account: {e}", file=sys.stderr)
        return None


def _load_oauth_client(creds_path: str) -> Optional[dict]:
    """Load OAuth client credentials from a client_secret JSON file."""
    try:
        with open(creds_path, "r") as f:
            data = json.load(f)
        return data.get("web", data.get("installed", {}))
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading OAuth client file: {e}", file=sys.stderr)
        return None


def _load_oauth_token() -> Optional[dict]:
    """Load saved OAuth token from TOKEN_PATH."""
    if not os.path.exists(TOKEN_PATH):
        return None
    try:
        with open(TOKEN_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def _save_oauth_token(token_data: dict):
    """Save OAuth token to TOKEN_PATH with mode 0o600 and atomic write."""
    _write_secret_atomic(TOKEN_PATH, json.dumps(token_data, indent=2))


def _refresh_oauth_token(client: dict, token_data: dict) -> Optional[dict]:
    """Refresh an expired OAuth token using the refresh_token."""
    import urllib.parse
    import urllib.request

    if not token_data.get("refresh_token"):
        return None

    params = urllib.parse.urlencode({
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
        "refresh_token": token_data["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()

    try:
        req = urllib.request.Request(client.get("token_uri", "https://oauth2.googleapis.com/token"), data=params)
        with urllib.request.urlopen(req, timeout=30) as resp:
            new_data = json.loads(resp.read())
        token_data["access_token"] = new_data["access_token"]
        token_data["expires_at"] = time.time() + new_data.get("expires_in", 3600)
        if "refresh_token" in new_data:  # Google now sometimes rotates these
            token_data["refresh_token"] = new_data["refresh_token"]
        # AUTH-001 (v1.9.1): strip client_secret on every save so older
        # token files migrate forward the first time they're refreshed.
        token_data.pop("client_secret", None)
        _save_oauth_token(token_data)
        return token_data
    except Exception as e:
        print(f"Error refreshing OAuth token: {e}", file=sys.stderr)
        return None


def get_oauth_credentials(scopes: list):
    """
    Get OAuth credentials from saved token, refreshing if needed.

    Falls back to service account if no OAuth token is available.

    Args:
        scopes: List of OAuth scope URLs (used for service account fallback).

    Returns:
        google.oauth2.credentials.Credentials or service_account.Credentials, or None.
    """
    config = load_config()

    # Try OAuth token first
    token_data = _load_oauth_token()
    if token_data and token_data.get("access_token"):
        # Check if token needs refresh
        if time.time() > token_data.get("expires_at", 0) - 60:
            oauth_creds_path = config.get("oauth_client_path")
            if oauth_creds_path:
                client = _load_oauth_client(os.path.expanduser(oauth_creds_path))
                if client:
                    token_data = _refresh_oauth_token(client, token_data)
                    if not token_data:
                        print("OAuth token refresh failed. Re-run --auth.", file=sys.stderr)
                        return get_service_account_credentials(scopes)

        if token_data and token_data.get("access_token"):
            try:
                from google.oauth2.credentials import Credentials
                # AUTH-001 (v1.9.1): client_secret is no longer stored in
                # the token file. Re-read from config["oauth_client_path"]
                # so the long-lived app credential stays in its own
                # 0o600 file (and is referenced, not duplicated).
                # Backwards-compat: legacy token files still containing
                # client_secret are honored (token_data.get fallback)
                # until v1.10.0 makes oauth_client_path mandatory.
                client_secret = None
                oauth_creds_path = config.get("oauth_client_path")
                if oauth_creds_path:
                    client = _load_oauth_client(os.path.expanduser(oauth_creds_path))
                    if client:
                        client_secret = client.get("client_secret")
                if client_secret is None:
                    client_secret = token_data.get("client_secret")  # legacy compat
                return Credentials(
                    token=token_data["access_token"],
                    refresh_token=token_data.get("refresh_token"),
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=token_data.get("client_id"),
                    client_secret=client_secret,
                )
            except ImportError:
                print("Error: google-auth required. Install with: pip install google-auth", file=sys.stderr)

    # Fall back to service account
    return get_service_account_credentials(scopes)


def run_oauth_flow(creds_path: str, services: list = None):
    """
    Run OAuth browser-based authentication flow.

    Opens a browser for consent, captures the auth code via local HTTP server,
    exchanges for tokens, and saves them.

    Args:
        creds_path: Path to the OAuth client_secret JSON file.
        services: Optional list of scope service keys (see SCOPES). Defaults to
            the read-only set built by `_scopes_for(None)`.
    """
    import http.server
    import urllib.parse
    import urllib.request
    import webbrowser

    client = _load_oauth_client(creds_path)
    if not client:
        print("Error: Could not load OAuth client credentials.", file=sys.stderr)
        sys.exit(1)

    state_token = secrets.token_urlsafe(32)
    scopes_str = _scopes_for(services)

    auth_params = {
        "client_id": client["client_id"],
        "redirect_uri": OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": scopes_str,
        "access_type": "offline",
        "prompt": "consent",
        "state": state_token,
        "include_granted_scopes": "true",
    }
    auth_url = (
        f"{client.get('auth_uri', 'https://accounts.google.com/o/oauth2/auth')}"
        f"?{urllib.parse.urlencode(auth_params)}"
    )

    auth_code = [None]

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            received_state = params.get("state", [""])[0]
            if received_state != state_token:
                self.send_response(403)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"State mismatch - possible CSRF. Aborted.")
                return
            if "code" in params:
                auth_code[0] = params["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Authorization complete.</h1>You can close this tab.</body></html>")
            else:
                self.send_response(400)
                self.end_headers()
        def log_message(self, *a):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 8085), Handler)
    server.timeout = 300

    print(f"\nOpen this URL in your browser:\n\n{auth_url}\n")
    print("Waiting up to 5 minutes for authentication...")

    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    server.handle_request()
    server.server_close()

    if not auth_code[0]:
        print("\nAuthentication failed or timed out.", file=sys.stderr)
        print("If the browser showed '127.0.0.1 refused to connect', copy the full URL")
        print("from the browser address bar and run:")
        print(f"  python3 scripts/google_auth.py --exchange --creds {creds_path} --code 'THE_CODE'")
        sys.exit(1)

    # Exchange code for tokens
    _exchange_code(client, auth_code[0], creds_path=creds_path)


def _exchange_code(client: dict, code: str, creds_path: str | None = None):
    """Exchange an authorization code for tokens."""
    import urllib.parse
    import urllib.request

    params = urllib.parse.urlencode({
        "code": code,
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
        "redirect_uri": OAUTH_REDIRECT_URI,
        "grant_type": "authorization_code",
    }).encode()

    try:
        req = urllib.request.Request(
            client.get("token_uri", "https://oauth2.googleapis.com/token"), data=params
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            token_data = json.loads(resp.read())
        token_data["expires_at"] = time.time() + token_data.get("expires_in", 3600)
        token_data["client_id"] = client["client_id"]
        # AUTH-001 (v1.9.1): client_secret is NO LONGER stored in the token
        # file. Co-locating the long-lived app credential with the
        # short-lived access token expands blast radius if the token file
        # leaks. Refresh paths re-read client_secret from
        # config["oauth_client_path"] instead. See get_oauth_credentials.
        token_data.pop("client_secret", None)
        _save_oauth_token(token_data)
        print("OAuth token saved successfully!")

        if creds_path:
            _save_config_value("oauth_client_path", os.path.abspath(os.path.expanduser(creds_path)))
        print(f"\nToken saved to: {TOKEN_PATH}")
    except Exception as e:
        print(f"Error exchanging authorization code: {e}", file=sys.stderr)
        sys.exit(1)


def get_api_key() -> Optional[str]:
    """
    Get the Google API key from config or environment.

    Returns:
        API key string, or None if not configured.
    """
    config = load_config()
    return config.get("api_key")


def build_service(api_name: str, version: str, scopes: list):
    """
    Build a Google API discovery service client.

    Args:
        api_name: API name (e.g., 'searchconsole', 'indexing', 'pagespeedonline').
        version: API version (e.g., 'v1', 'v3', 'v5').
        scopes: OAuth scopes needed.

    Returns:
        googleapiclient.discovery.Resource object, or None on failure.
    """
    try:
        from googleapiclient.discovery import build
    except ImportError:
        print(
            "Error: google-api-python-client required. "
            "Install with: pip install google-api-python-client",
            file=sys.stderr,
        )
        return None

    credentials = get_oauth_credentials(scopes)
    if not credentials:
        return None

    try:
        service = build(api_name, version, credentials=credentials)
        return service
    except Exception as e:
        print(f"Error building {api_name} service: {e}", file=sys.stderr)
        return None


def check_credentials(service: str) -> dict:
    """
    Validate credentials for a specific Google API service.

    Args:
        service: One of 'psi', 'crux', 'crux_history', 'gsc', 'indexing', 'ga4'.

    Returns:
        Dictionary with:
            - available: bool
            - method: 'api_key' or 'service_account'
            - service: service name
            - error: error message or None
    """
    result = {
        "available": False,
        "method": SERVICE_AUTH.get(service, "unknown"),
        "service": SERVICE_NAMES.get(service, service),
        "error": None,
    }

    config = load_config()

    if SERVICE_AUTH.get(service) == "api_key":
        api_key = config.get("api_key")
        if api_key:
            result["available"] = True
        else:
            result["error"] = (
                "No API key found. Set GOOGLE_API_KEY environment variable "
                f"or add 'api_key' to {CONFIG_PATH}"
            )

    elif SERVICE_AUTH.get(service) == "oauth_or_sa":
        # Check OAuth token first
        token_data = _load_oauth_token()
        if token_data and token_data.get("access_token"):
            result["available"] = True
            result["method"] = "oauth_token"
            expired = time.time() > token_data.get("expires_at", 0) - 60
            if expired and token_data.get("refresh_token"):
                result["note"] = "Token expired but refresh_token available (will auto-refresh)"
            elif expired:
                result["available"] = False
                result["error"] = "OAuth token expired and no refresh_token. Re-run --auth."
        else:
            # Fall back to service account
            sa_path = config.get("service_account_path")
            if not sa_path:
                result["error"] = (
                    "No OAuth token or service account found. Either:\n"
                    "         1. Run: python3 scripts/google_auth.py --auth --creds /path/to/client_secret.json\n"
                    f"         2. Or add 'service_account_path' to {CONFIG_PATH}"
                )
            else:
                sa_path = os.path.expanduser(sa_path)
                if not os.path.exists(sa_path):
                    result["error"] = f"Service account file not found: {sa_path}"
                else:
                    try:
                        with open(sa_path, "r") as f:
                            sa_data = json.load(f)
                        if "client_email" not in sa_data or "private_key" not in sa_data:
                            result["error"] = "Service account JSON missing required fields (client_email, private_key)"
                        else:
                            result["available"] = True
                            result["method"] = "service_account"
                            result["client_email"] = sa_data.get("client_email")
                    except (json.JSONDecodeError, IOError) as e:
                        result["error"] = f"Invalid service account file: {e}"

        # GA4 also needs property ID
        if service == "ga4" and result["available"]:
            ga4_id = config.get("ga4_property_id")
            if not ga4_id:
                result["available"] = False
                result["error"] = (
                    "Credentials found but no GA4 property ID configured. "
                    f"Set GA4_PROPERTY_ID or add 'ga4_property_id' to {CONFIG_PATH}"
                )
    elif SERVICE_AUTH.get(service) == "ads":
        missing = []
        if not config.get("ads_developer_token"):
            missing.append("ads_developer_token")
        if not config.get("ads_customer_id"):
            missing.append("ads_customer_id")
        token_data = _load_oauth_token()
        if not token_data or not token_data.get("refresh_token"):
            missing.append("OAuth refresh token from --auth")
        if not config.get("oauth_client_path"):
            missing.append("oauth_client_path")
        if missing:
            result["error"] = f"Missing Google Ads config: {', '.join(missing)}"
        else:
            result["available"] = True
            result["method"] = "google_ads_oauth"
    else:
        result["error"] = f"Unknown service: {service}"

    return result


def detect_tier() -> dict:
    """
    Detect the credential tier available.

    Returns:
        Dictionary with:
            - tier: 0, 1, or 2
            - description: human-readable tier description
            - capabilities: list of available API groups
            - missing: what's needed for the next tier
    """
    config = load_config()

    has_api_key = bool(config.get("api_key"))
    has_authenticated = False
    has_ga4 = False
    has_ads = False
    auth_method = None

    # Check OAuth token
    token_data = _load_oauth_token()
    if token_data and token_data.get("access_token"):
        has_authenticated = True
        auth_method = "oauth_token"

    # Check service account
    if not has_authenticated:
        sa_path = config.get("service_account_path")
        if sa_path:
            sa_path = os.path.expanduser(sa_path)
            if os.path.exists(sa_path):
                try:
                    with open(sa_path, "r") as f:
                        sa_data = json.load(f)
                    if "client_email" in sa_data and "private_key" in sa_data:
                        has_authenticated = True
                        auth_method = "service_account"
                except (json.JSONDecodeError, IOError):
                    pass

    if has_authenticated and config.get("ga4_property_id"):
        has_ga4 = True

    token_data = _load_oauth_token()
    has_ads = all([
        config.get("ads_developer_token"),
        config.get("ads_customer_id"),
        config.get("oauth_client_path"),
        token_data and token_data.get("refresh_token"),
    ])

    tier0_caps = [
        "PageSpeed Insights", "CrUX", "CrUX History",
        "YouTube Data", "Cloud Natural Language",
    ]
    auth_caps = [
        "Search Console", "URL Inspection", "Sitemaps",
        "Indexing API",
    ]

    if has_ads:
        capabilities = []
        if has_api_key:
            capabilities.extend(tier0_caps)
        if has_authenticated:
            capabilities.extend(auth_caps)
        if has_ga4:
            capabilities.append("GA4 Organic Traffic")
        capabilities.append("Google Ads Keyword Planner")
        missing = None
        if not has_ga4:
            missing = "Add 'ga4_property_id' if GA4 reports are also needed"
        return {
            "tier": 3,
            "description": "Ads (Google Ads OAuth + developer token)",
            "capabilities": capabilities,
            "missing": missing,
        }
    elif has_ga4:
        return {
            "tier": 2,
            "description": "Full (API key + Service Account + GA4)",
            "capabilities": tier0_caps + auth_caps + ["GA4 Organic Traffic"],
            "missing": None,
        }
    elif has_authenticated:
        return {
            "tier": 1,
            "description": "Authenticated (API key + OAuth/Service Account)",
            "capabilities": (tier0_caps if has_api_key else []) + auth_caps,
            "missing": "Add 'ga4_property_id' to unlock GA4 organic traffic reports",
        }
    elif has_api_key:
        return {
            "tier": 0,
            "description": "API Key Only",
            "capabilities": tier0_caps,
            "missing": "Add a service account to unlock Search Console, URL Inspection, and Indexing API",
        }
    else:
        return {
            "tier": -1,
            "description": "No credentials configured",
            "capabilities": [],
            "missing": (
                f"Create config at {CONFIG_PATH} with at minimum an 'api_key' field. "
                "Run with --setup for full instructions."
            ),
        }


def print_setup_instructions():
    """Print step-by-step setup instructions."""
    print("""
Google SEO API Setup Instructions
=================================

1. CREATE A GOOGLE CLOUD PROJECT
   - Go to https://console.cloud.google.com
   - Create a new project (or select existing)
   - Note the project ID

2. ENABLE APIs
   In API Library (APIs & Services > Library), enable:
   - Google Search Console API
   - PageSpeed Insights API
   - Chrome UX Report API
   - Web Search Indexing API (for Indexing API)
   - Google Analytics Data API (for GA4)
   - YouTube Data API v3
   - Cloud Natural Language API

3. CREATE AN API KEY (for PSI, CrUX, YouTube, NLP)
   - APIs & Services > Credentials > Create Credentials > API key
   - Restrict to: PageSpeed Insights API, Chrome UX Report API,
     YouTube Data API v3, Cloud Natural Language API

4. CREATE A SERVICE ACCOUNT (for GSC, Indexing API, GA4)
   - IAM & Admin > Service Accounts > Create Service Account
   - Download JSON key file, store securely

5. GRANT ACCESS
   - Search Console: Settings > Users and permissions > Add user
     Paste the service account client_email, set as Owner (for Indexing API) or Full (read-only)
   - GA4: Admin > Property Access Management > Add
     Paste email, set Viewer role

6. CREATE CONFIG FILE
   mkdir -p ~/.config/claude-seo
   Save to ~/.config/claude-seo/google-api.json:

   {
     "service_account_path": "/path/to/service_account.json",
     "api_key": "AIzaSy...",
     "oauth_client_path": "/path/to/oauth_client.json",
     "default_property": "sc-domain:example.com",
     "ga4_property_id": "properties/123456789",
     "ads_developer_token": "YOUR_DEV_TOKEN",
     "ads_customer_id": "123-456-7890",
     "ads_login_customer_id": "123-456-7890"
   }

   chmod 700 ~/.config/claude-seo
   chmod 600 ~/.config/claude-seo/google-api.json

7. VERIFY
   python3 scripts/google_auth.py --check

ENVIRONMENT VARIABLE ALTERNATIVES:
   GOOGLE_API_KEY              - API key
   GOOGLE_APPLICATION_CREDENTIALS - Path to service account JSON
   GOOGLE_OAUTH_CLIENT_PATH    - Path to OAuth client JSON
   GA4_PROPERTY_ID             - GA4 property ID (e.g., properties/123456789)
   GSC_PROPERTY                - Default Search Console property
   GOOGLE_ADS_DEVELOPER_TOKEN  - Google Ads developer token
   GOOGLE_ADS_CUSTOMER_ID      - Google Ads customer ID
   GOOGLE_ADS_LOGIN_CUSTOMER_ID - Optional manager account login customer ID
""")


def main():
    parser = argparse.ArgumentParser(
        description="Google API credential management for Claude SEO"
    )
    parser.add_argument(
        "--check",
        nargs="?",
        const="all",
        metavar="SERVICE",
        help="Check credentials. Optionally specify service: psi, crux, crux_history, youtube, nlp, gsc, indexing, ga4, keywords",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Show setup instructions",
    )
    parser.add_argument(
        "--tier",
        action="store_true",
        help="Show detected credential tier",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--auth",
        action="store_true",
        help="Run OAuth browser-based authentication flow",
    )
    parser.add_argument(
        "--exchange",
        action="store_true",
        help="Manually exchange an auth code for tokens",
    )
    parser.add_argument(
        "--creds",
        help="Path to OAuth client_secret JSON file (for --auth and --exchange)",
    )
    parser.add_argument(
        "--code",
        help="Authorization code to exchange (for --exchange)",
    )
    parser.add_argument(
        "--scopes",
        help=(
            "Comma-separated scope service keys for --auth (e.g. "
            "'gsc_readonly,ga4' or 'indexing,gsc_write'). Defaults to a "
            "read-only set: gsc_readonly,ga4."
        ),
    )

    args = parser.parse_args()

    if args.auth:
        if not args.creds:
            print("Error: --creds is required with --auth", file=sys.stderr)
            sys.exit(1)
        services = None
        if args.scopes:
            services = [s.strip() for s in args.scopes.split(",") if s.strip()]
        try:
            run_oauth_flow(args.creds, services=services)
        except ValueError as e:
            # _scopes_for raises ValueError for unknown service keys.
            # Surface a clean error instead of a stack trace.
            print(f"Error: {e}", file=sys.stderr)
            print(
                f"Valid scope keys: {', '.join(sorted(SCOPES.keys()))}",
                file=sys.stderr,
            )
            sys.exit(2)
        return

    if args.exchange:
        if not args.creds or not args.code:
            print("Error: --creds and --code are required with --exchange", file=sys.stderr)
            sys.exit(1)
        client = _load_oauth_client(args.creds)
        if client:
            _exchange_code(client, args.code, creds_path=args.creds)
        return

    if args.setup:
        print_setup_instructions()
        return

    if args.tier:
        tier_info = detect_tier()
        if args.json:
            print(json.dumps(tier_info, indent=2))
        else:
            print(f"Credential Tier: {tier_info['tier']} - {tier_info['description']}")
            if tier_info["capabilities"]:
                print(f"Available APIs: {', '.join(tier_info['capabilities'])}")
            if tier_info["missing"]:
                print(f"Next tier: {tier_info['missing']}")
        return

    if args.check:
        services = (
            list(SERVICE_AUTH.keys())
            if args.check == "all"
            else [args.check]
        )

        results = {}
        for svc in services:
            if svc not in SERVICE_AUTH:
                results[svc] = {"available": False, "error": f"Unknown service: {svc}"}
                continue
            results[svc] = check_credentials(svc)

        if args.json:
            tier_info = detect_tier()
            output = {"tier": tier_info, "services": results}
            print(json.dumps(output, indent=2))
        else:
            tier_info = detect_tier()
            print(f"Credential Tier: {tier_info['tier']} - {tier_info['description']}")
            print()
            for svc, result in results.items():
                status = "OK" if result["available"] else "MISSING"
                print(f"  [{status}] {result.get('service', svc)}")
                if result.get("error"):
                    print(f"         {result['error']}")
                if result.get("client_email"):
                    print(f"         Service account: {result['client_email']}")
            print()
            if tier_info["missing"]:
                print(f"Tip: {tier_info['missing']}")
        return

    # Default: show tier
    tier_info = detect_tier()
    if args.json:
        print(json.dumps(tier_info, indent=2))
    else:
        print(f"Credential Tier: {tier_info['tier']} - {tier_info['description']}")
        if tier_info["missing"]:
            print(f"Run --setup for configuration instructions.")


if __name__ == "__main__":
    main()
