#!/usr/bin/env python3
"""NotebookLM package helpers, without import-time setup or migration."""

import sys
from pathlib import Path


def ensure_venv_and_run():
    """Check the selected environment; setup_environment.py owns installation.

    This compatibility entrypoint does not create a venv or download packages
    or browsers. Missing/stale runtimes return the runner's setup-required exit.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from run import ensure_venv
    ensure_venv()


# No import-time call: imports must never create environments or download Chrome.
