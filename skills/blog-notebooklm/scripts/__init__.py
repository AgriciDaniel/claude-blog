#!/usr/bin/env python3
"""
NotebookLM Skill Scripts Package

Provides venv management helpers. NOTE: closes audit VULN-031: this module
no longer triggers `ensure_venv_and_run()` at import time. Callers must
invoke it explicitly (typically via `setup_environment.py --bootstrap` or
the `run.py` wrapper).

Reason: import-time side effects ran venv.create + pip install + 150 MB
Chrome download whenever any script in this package was imported (incl.
test discovery, IDE auto-import). Triggering install on import violates
the principle of least surprise and slows every cold start.
"""

import os
import sys
import subprocess
from pathlib import Path


def ensure_venv_and_run():
    """
    Ensure virtual environment exists.

    Call explicitly from a wrapper (e.g. `python -m setup_environment` or
    `run.py`). Do NOT rely on this firing at import time.
    """
    # Only do this if we're not already in the skill's venv
    skill_dir = Path(__file__).parent.parent
    venv_dir = skill_dir / ".venv"

    # Check if we're in a venv
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

    # Check if it's OUR venv
    if in_venv:
        venv_path = Path(sys.prefix)
        if venv_path == venv_dir:
            # We're already in the correct venv
            return

    # We need to set up or switch to our venv
    if not venv_dir.exists():
        print("🔧 First-time setup detected...")
        print("   Creating isolated environment for NotebookLM skill...")
        print("   This ensures clean dependency management...")

        # Create venv
        import venv
        venv.create(venv_dir, with_pip=True)

        # Install requirements
        requirements_file = skill_dir / "scripts" / "requirements.txt"
        if requirements_file.exists():
            if os.name == 'nt':  # Windows
                pip_exe = venv_dir / "Scripts" / "pip.exe"
            else:
                pip_exe = venv_dir / "bin" / "pip"

            print("   Installing dependencies in isolated environment...")
            subprocess.run(
                [str(pip_exe), "install", "-q", "-r", str(requirements_file)],
                check=True
            )

            # Also install Patchright's Chrome channel
            print("   Setting up browser automation...")
            if os.name == 'nt':
                python_exe = venv_dir / "Scripts" / "python.exe"
            else:
                python_exe = venv_dir / "bin" / "python"

            subprocess.run(
                [str(python_exe), "-m", "patchright", "install", "chrome"],
                check=True,
                capture_output=True
            )

        print("✅ Environment ready! All dependencies isolated in .venv/")

    # If we're here and not in the venv, we should recommend using the venv
    if not in_venv:
        print("\n⚠️  Running outside virtual environment")
        print("   Recommended: Use scripts/run.py to ensure clean execution")
        print("   Or activate: source .venv/bin/activate")


# Audit VULN-031: removed import-time `ensure_venv_and_run()` call. Callers
# must invoke `ensure_venv_and_run()` explicitly. The `setup_environment.py`
# script and `run.py` wrapper both do this at top-level, so the user-facing
# behavior of running `python run.py ...` is unchanged.
