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

# Load only the helper shipped beside this installed script, never from CWD.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime_paths import resolve_runtime_paths


def get_venv_python():
    """Get the virtual environment Python executable"""
    skill_dir = Path(__file__).resolve().parent.parent
    venv_dir = resolve_runtime_paths(skill_dir, "blog-google").venv

    if os.name == 'nt':  # Windows
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:  # Unix/Linux/Mac
        venv_python = venv_dir / "bin" / "python"

    return venv_python


def ensure_venv():
    """Return a ready interpreter without installing or updating anything."""
    skill_dir = Path(__file__).resolve().parent.parent
    venv_dir = resolve_runtime_paths(skill_dir, "blog-google").venv
    lock_file = skill_dir / "scripts" / "requirements.lock"
    requirements_file = skill_dir / "scripts" / "requirements.txt"
    stamp_file = venv_dir / ".requirements.stamp"

    source = lock_file if lock_file.exists() else requirements_file
    expected_stamp = hashlib.sha256(source.read_bytes()).hexdigest() if source.exists() else None
    current_stamp = stamp_file.read_text().strip() if stamp_file.exists() else None

    venv_python = get_venv_python()
    setup_script = skill_dir / "scripts" / "setup_environment.py"
    if not venv_python.is_file():
        print(f'Google skill setup required. Run: python3 "{setup_script}"')
        sys.exit(1)
    if expected_stamp and current_stamp != expected_stamp:
        print(f'Google skill dependencies are missing or stale. Run: python3 "{setup_script}"')
        sys.exit(1)
    return venv_python


USAGE = """Usage: python run.py <script_name> [args...]

Available scripts:
  google_auth.py       - Credential management and auth setup
  pagespeed_check.py   - PageSpeed Insights + CrUX field data
  crux_history.py      - CWV history, 25 weeks by default, up to 40
  youtube_search.py    - YouTube video search and details
  nlp_analyze.py       - NLP entity extraction and sentiment
  gsc_query.py         - Search Console performance data
  gsc_inspect.py       - URL Inspection API
  indexing_notify.py   - Indexing API notifications
  ga4_report.py        - GA4 organic traffic reports
  keyword_planner.py   - Google Ads Keyword Planner
  google_report.py     - PDF/HTML performance reports

Run "python run.py <script_name> --help" for a script's options."""


def main():
    """Main runner"""
    if len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help", "help"):
        print(USAGE)
        sys.exit(0)
    if len(sys.argv) < 2:
        print(USAGE)
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
    skill_dir = Path(__file__).resolve().parent.parent
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
    try:
        venv_python = ensure_venv()
    except ValueError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

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
