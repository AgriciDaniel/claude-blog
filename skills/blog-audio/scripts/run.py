#!/usr/bin/env python3
"""
Universal runner for Blog Audio skill scripts.

Ensures all scripts run with the correct virtual environment.
"""

import json
import os
import subprocess
import sys
import argparse
from pathlib import Path

# Load only the helper shipped beside this installed script, never from CWD.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime_paths import resolve_runtime_paths


def get_venv_python():
    """Get the virtual environment Python executable"""
    skill_dir = Path(__file__).resolve().parent.parent
    venv_dir = resolve_runtime_paths(skill_dir, "blog-audio").venv

    if os.name == 'nt':  # Windows
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:  # Unix/Linux/Mac
        venv_python = venv_dir / "bin" / "python"

    return venv_python


def ensure_venv():
    """Return the configured interpreter without mutating the environment."""
    venv_python = get_venv_python()
    return venv_python if venv_python.is_file() else None


def wants_json(args):
    """Return True when wrapper-level errors should be JSON."""
    return "--json" in args


def emit_error(message, code, as_json):
    """Emit a wrapper-level error and exit."""
    if as_json:
        print(json.dumps({"status": "error", "error": message, "exit_code": code}))
    else:
        print(message)
    sys.exit(code)


def main():
    """Main runner"""
    parser = argparse.ArgumentParser(
        description="Run Blog Audio skill scripts with the managed virtual environment"
    )
    parser.add_argument("--json", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("script_name", nargs="?", help="Script file name to run")
    parser.add_argument("script_args", nargs=argparse.REMAINDER, help="Arguments for the script")

    args = parser.parse_args()

    if not args.script_name:
        emit_error(
            "Usage: python3 run.py <script_name> [args...]",
            1,
            args.json or wants_json(sys.argv[1:]),
        )

    script_name = args.script_name
    script_args = args.script_args
    as_json = args.json or wants_json(script_args)

    if "/" in script_name or "\\" in script_name or Path(script_name).name != script_name:
        emit_error("Script name must be a file name, not a path", 2, as_json)

    # Ensure .py extension
    if not script_name.endswith('.py'):
        script_name += '.py'

    # Get script path
    skill_dir = Path(__file__).resolve().parent.parent
    scripts_dir = (skill_dir / "scripts").resolve()
    script_path = (scripts_dir / script_name).resolve()

    if script_path.parent != scripts_dir:
        emit_error("Script path escapes the skill scripts directory", 2, as_json)

    if not script_path.exists():
        emit_error(f"Script not found: {script_name}", 1, as_json)

    # Ordinary runs are read-only with respect to the managed environment.
    # Installation is reserved for the explicit setup_environment.py command.
    try:
        venv_python = ensure_venv()
    except ValueError as exc:
        emit_error(str(exc), 1, as_json)
    if venv_python is None:
        emit_error(
            "Blog Audio setup required. Run: python3 skills/blog-audio/scripts/setup_environment.py",
            1,
            as_json,
        )

    # Build command
    cmd = [str(venv_python), str(script_path)] + script_args

    # Run the script
    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        emit_error("Interrupted by user", 130, as_json)
    except Exception as e:
        emit_error(f"Error: {e}", 1, as_json)


if __name__ == "__main__":
    main()
