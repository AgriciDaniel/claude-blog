#!/usr/bin/env python3
"""
Universal runner for Blog Google skill scripts
Ensures all scripts run with the correct virtual environment
"""

import os
import sys
import subprocess
import hashlib
from pathlib import Path


def get_venv_python():
    """Get the virtual environment Python executable"""
    skill_dir = Path(__file__).parent.parent
    venv_dir = skill_dir / ".venv"

    if os.name == 'nt':  # Windows
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:  # Unix/Linux/Mac
        venv_python = venv_dir / "bin" / "python"

    return venv_python


def ensure_venv():
    """Ensure virtual environment exists"""
    skill_dir = Path(__file__).parent.parent
    venv_dir = skill_dir / ".venv"
    setup_script = skill_dir / "scripts" / "setup_environment.py"
    lock_file = skill_dir / "scripts" / "requirements.lock"
    requirements_file = skill_dir / "scripts" / "requirements.txt"
    stamp_file = venv_dir / ".requirements.stamp"

    source = lock_file if lock_file.exists() else requirements_file
    expected_stamp = hashlib.sha256(source.read_bytes()).hexdigest() if source.exists() else None
    current_stamp = stamp_file.read_text().strip() if stamp_file.exists() else None

    # Check if venv exists
    if not venv_dir.exists() or (expected_stamp and current_stamp != expected_stamp):
        print("First-time setup: Creating virtual environment...")
        print("   This may take a minute...")

        # Run setup with system Python
        result = subprocess.run([sys.executable, str(setup_script)])
        if result.returncode != 0:
            print("Failed to set up environment")
            sys.exit(1)

        print("Environment ready!")

    return get_venv_python()


def main():
    """Main runner"""
    if len(sys.argv) < 2:
        print("Usage: python run.py <script_name> [args...]")
        print("\nAvailable scripts:")
        print("  google_auth.py       - Credential management and auth setup")
        print("  pagespeed_check.py   - PageSpeed Insights + CrUX field data")
        print("  crux_history.py      - 25-week CWV trend history")
        print("  youtube_search.py    - YouTube video search and details")
        print("  nlp_analyze.py       - NLP entity extraction and sentiment")
        print("  gsc_query.py         - Search Console performance data")
        print("  gsc_inspect.py       - URL Inspection API")
        print("  indexing_notify.py   - Indexing API notifications")
        print("  ga4_report.py        - GA4 organic traffic reports")
        print("  keyword_planner.py   - Google Ads Keyword Planner")
        print("  google_report.py     - PDF/HTML performance reports")
        sys.exit(1)

    script_name = sys.argv[1]
    script_args = sys.argv[2:]

    # Handle both "scripts/script.py" and "script.py" formats
    if script_name.startswith('scripts/'):
        script_name = script_name[8:]  # len('scripts/') = 8

    # Ensure .py extension
    if not script_name.endswith('.py'):
        script_name += '.py'

    # Get script path
    skill_dir = Path(__file__).parent.parent
    scripts_dir = (skill_dir / "scripts").resolve()
    script_path = (scripts_dir / script_name).resolve()

    try:
        script_path.relative_to(scripts_dir)
    except ValueError:
        print(f"Script path escapes scripts directory: {script_name}")
        sys.exit(1)

    if not script_path.is_file():
        print(f"Script not found: {script_name}")
        print(f"   Skill directory: {skill_dir}")
        print(f"   Looked for: {script_path}")
        sys.exit(1)

    # Ensure venv exists and get Python executable
    venv_python = ensure_venv()

    # Build command
    cmd = [str(venv_python), str(script_path)] + script_args

    # Run the script
    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
