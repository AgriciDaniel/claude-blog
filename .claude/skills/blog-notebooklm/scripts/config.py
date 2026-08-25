"""
Configuration for NotebookLM Skill
Centralizes constants, selectors, and paths
"""

import os
from pathlib import Path
from urllib.parse import urlparse

# Paths
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
BROWSER_STATE_DIR = DATA_DIR / "browser_state"
BROWSER_PROFILE_DIR = BROWSER_STATE_DIR / "browser_profile"
STATE_FILE = BROWSER_STATE_DIR / "state.json"
AUTH_INFO_FILE = DATA_DIR / "auth_info.json"
LIBRARY_FILE = DATA_DIR / "library.json"

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


def validate_notebook_url(url: str) -> str:
    """Allow only first-party NotebookLM notebook URLs."""
    parsed = urlparse(url.strip())
    if parsed.scheme != "https":
        raise ValueError("Notebook URL must use https")
    if parsed.netloc != "notebooklm.google.com":
        raise ValueError("Notebook URL must be on notebooklm.google.com")
    if not parsed.path.startswith("/notebook/") or parsed.path == "/notebook/":
        raise ValueError("Notebook URL must start with https://notebooklm.google.com/notebook/")
    if parsed.username or parsed.password:
        raise ValueError("Notebook URL must not contain credentials")
    return url.strip()
