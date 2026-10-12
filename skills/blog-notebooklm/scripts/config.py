"""
Configuration for NotebookLM Skill
Centralizes constants, selectors, and paths
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime_paths import confined_directory, resolve_runtime_paths

# Paths
SKILL_DIR = Path(__file__).resolve().parent.parent
RUNTIME_PATHS = resolve_runtime_paths(SKILL_DIR, "blog-notebooklm")
DATA_DIR = RUNTIME_PATHS.data
BROWSER_STATE_DIR = confined_directory(DATA_DIR, "browser_state")
BROWSER_PROFILE_DIR = confined_directory(DATA_DIR, "browser_state", "browser_profile")
STATE_FILE = BROWSER_STATE_DIR / "state.json"
AUTH_INFO_FILE = DATA_DIR / "auth_info.json"
LIBRARY_FILE = DATA_DIR / "library.json"


def ensure_private_dir(path) -> Path:
    """Create a credential-bearing directory with mode 0700 (best effort off POSIX)."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        path.chmod(0o700)
    except OSError:
        pass  # Windows or a filesystem without POSIX mode bits
    return path


def write_private_file(path, text: str) -> None:
    """Write a file that is created 0600, never briefly world-readable."""
    path = Path(path)
    if path.is_symlink():
        raise ValueError(f"Refusing to write through a symlink: {path}")
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
    finally:
        try:
            path.chmod(0o600)
        except OSError:
            pass


def fail_missing_dependency(package: str, error: BaseException) -> None:
    """Exit with an actionable message instead of a raw ModuleNotFoundError traceback."""
    setup = Path(__file__).resolve().parent / "setup_environment.py"
    print(
        f"Error: the Python package '{package}' is not installed for this interpreter. "
        "Run the NotebookLM skill setup, which creates the skill virtual environment and "
        f'installs it: python3 "{setup}"  (then run scripts through run.py).',
        file=sys.stderr,
    )
    sys.exit(1)


# NotebookLM Selectors
QUERY_INPUT_SELECTORS = [
    "textarea.query-box-input",  # Primary
    'textarea[aria-label="Feld für Anfragen"]',  # Fallback German
    'textarea[aria-label="Input for queries"]',  # Fallback English
]

RESPONSE_SELECTORS = [
    ".to-user-container .message-text-content",  # Primary
    "[data-message-author='bot']",
    "[data-message-author='assistant']",
]

# Browser Configuration
# Note: "--no-sandbox" intentionally removed (VULN-009 mitigation). Enabling
# sandbox-disabled mode without container isolation gives the renderer
# process full host access. If running inside a container that requires it
# (e.g. Docker without a non-root user), set env PATCHRIGHT_NO_SANDBOX=1
# and the launcher will append it conditionally.
BROWSER_ARGS = [
    '--disable-blink-features=AutomationControlled',  # Patches navigator.webdriver
    '--disable-dev-shm-usage',
    '--no-first-run',
    '--no-default-browser-check'
]

if os.environ.get('PATCHRIGHT_NO_SANDBOX') == '1':
    BROWSER_ARGS.append('--no-sandbox')

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Timeouts
LOGIN_TIMEOUT_MINUTES = 10
QUERY_TIMEOUT_SECONDS = 120
PAGE_LOAD_TIMEOUT = 30000


# Gemini Notebook (renamed from NotebookLM on 2026-07-16). notebooklm.google.com
# answered a 301 to notebook.google.com on 2026-10-12 (HEAD request, path and query
# preserved), so both hosts are accepted. Exact hostnames only, https only: no
# suffix or substring matching, so look-alikes such as
# notebooklm.google.com.evil.example or evilnotebook.google.com are rejected.
CANONICAL_NOTEBOOK_HOST = "notebook.google.com"
LEGACY_NOTEBOOK_HOST = "notebooklm.google.com"
ALLOWED_NOTEBOOK_HOSTS = frozenset({CANONICAL_NOTEBOOK_HOST, LEGACY_NOTEBOOK_HOST})
LOGIN_HOST = "accounts.google.com"
NOTEBOOK_HOME_URL = f"https://{CANONICAL_NOTEBOOK_HOST}/"
_NOTEBOOK_ID_RE = re.compile(r"[A-Za-z0-9_-]{1,128}")


def _https_hostname(url: str):
    """Return the lowercase hostname of a clean https URL with no userinfo or port, else None."""
    if not isinstance(url, str) or any(ord(ch) <= 32 or ord(ch) == 127 for ch in url.strip()):
        return None
    try:
        parsed = urlparse(url.strip())
        port = parsed.port
    except ValueError:
        return None
    if parsed.scheme != "https" or parsed.username or parsed.password:
        return None
    if port not in (None, 443) or parsed.hostname is None:
        return None
    if parsed.netloc.lower() not in (parsed.hostname, f"{parsed.hostname}:443"):
        return None
    return parsed.hostname


def is_notebook_host_url(url: str) -> bool:
    """True when url is https on exactly one of the allowed notebook hosts."""
    return _https_hostname(url) in ALLOWED_NOTEBOOK_HOSTS


def is_google_login_url(url: str) -> bool:
    """True when url is on the Google sign-in host (exact match, not a substring)."""
    return _https_hostname(url) == LOGIN_HOST


def validate_notebook_url(url: str) -> str:
    """Allow only first-party notebook URLs on the canonical or legacy host."""
    clean = url.strip() if isinstance(url, str) else ""
    parsed = urlparse(clean)
    if parsed.scheme != "https":
        raise ValueError("Notebook URL must use https")
    if parsed.username or parsed.password:
        raise ValueError("Notebook URL must not contain credentials")
    if not is_notebook_host_url(clean):
        raise ValueError(
            "Notebook URL must be on notebook.google.com or the legacy notebooklm.google.com"
        )
    if not parsed.path.startswith("/notebook/") or parsed.path == "/notebook/":
        raise ValueError(
            "Notebook URL must start with https://notebook.google.com/notebook/ "
            "(or https://notebooklm.google.com/notebook/)"
        )
    return clean


def extract_notebook_id(url: str) -> str:
    """Return the notebook id from a validated URL on either host."""
    path = urlparse(validate_notebook_url(url)).path
    candidate = path[len("/notebook/"):].split("/", 1)[0]
    if not _NOTEBOOK_ID_RE.fullmatch(candidate):
        raise ValueError("Notebook URL has an unexpected notebook id")
    return candidate


def canonical_notebook_url(url: str) -> str:
    """Rewrite a legacy-host URL to the canonical host, keeping path and query."""
    clean = validate_notebook_url(url)
    parsed = urlparse(clean)
    return parsed._replace(netloc=CANONICAL_NOTEBOOK_HOST).geturl()
