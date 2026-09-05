#!/usr/bin/env python3
"""
Environment Setup for Blog Audio Skill.

Manages virtual environment and dependencies automatically.
"""

import json
import os
import subprocess
import sys
import venv
from pathlib import Path


class SkillEnvironment:
    """Manages skill-specific virtual environment"""

    def __init__(self, quiet: bool = False):
        self.skill_dir = Path(__file__).parent.parent
        self.venv_dir = self.skill_dir / ".venv"
        self.quiet = quiet
        # Prefer the lock file (hash-verified). Fall back to loose
        # requirements.txt if no lock present (closes audit VULN-006).
        self.lock_file = self.skill_dir / "scripts" / "requirements.lock"
        self.requirements_file = self.skill_dir / "scripts" / "requirements.txt"

        if os.name == 'nt':
            self.venv_python = self.venv_dir / "Scripts" / "python.exe"
            self.venv_pip = self.venv_dir / "Scripts" / "pip.exe"
        else:
            self.venv_python = self.venv_dir / "bin" / "python"
            self.venv_pip = self.venv_dir / "bin" / "pip"

    def say(self, message: str) -> None:
        """Print a message unless JSON mode requested quiet output."""
        if not self.quiet:
            print(message)

    def ensure_venv(self) -> bool:
        """Ensure virtual environment exists and is set up"""
        if self.is_in_skill_venv():
            return True

        if not self.venv_dir.exists():
            self.say(f"Creating virtual environment in {self.venv_dir.name}/")
            try:
                venv.create(self.venv_dir, with_pip=True)
            except Exception as e:
                self.say(f"Failed to create venv: {e}")
                return False

        # Use lock file when available (hash-verified, reproducible).
        if self.lock_file.exists():
            install_args = ["install", "--require-hashes", "-r", str(self.lock_file)]
            install_label = "lock file (hash-verified)"
        elif self.requirements_file.exists():
            install_args = ["install", "-r", str(self.requirements_file)]
            install_label = "requirements.txt (no hash verification)"
        else:
            self.say("No requirements.txt or requirements.lock found; skipping install")
            return True

        self.say(f"Installing dependencies from {install_label}...")
        try:
            subprocess.run(
                [str(self.venv_pip)] + install_args,
                check=True, capture_output=True, text=True,
            )
            self.say("Dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            self.say(f"Failed to install dependencies: {e}")
            return False

    def is_in_skill_venv(self) -> bool:
        """Check if running in the skill's venv"""
        if hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        ):
            return Path(sys.prefix) == self.venv_dir
        return False

    def get_python_executable(self) -> str:
        """Get the correct Python executable"""
        if self.venv_python.exists():
            return str(self.venv_python)
        return sys.executable


def main():
    """Main entry point for environment setup"""
    import argparse

    parser = argparse.ArgumentParser(description='Setup Blog Audio skill environment')
    parser.add_argument('--check', action='store_true', help='Check if environment is set up')
    parser.add_argument('--json', action='store_true', help='Output structured JSON')
    args = parser.parse_args()

    env = SkillEnvironment(quiet=args.json)

    if args.check:
        data = {
            "status": "ok" if env.venv_dir.exists() else "missing",
            "venv_dir": str(env.venv_dir),
            "python": env.get_python_executable() if env.venv_dir.exists() else None,
        }
        if args.json:
            print(json.dumps(data, indent=2))
            return 0 if env.venv_dir.exists() else 1
        if env.venv_dir.exists():
            print(f"Virtual environment exists: {env.venv_dir}")
            print(f"   Python: {env.get_python_executable()}")
        else:
            print("No virtual environment found")
        return 0 if env.venv_dir.exists() else 1

    if env.ensure_venv():
        if args.json:
            print(json.dumps({
                "status": "success",
                "venv_dir": str(env.venv_dir),
                "python": env.get_python_executable(),
            }, indent=2))
            return 0
        print(f"\nEnvironment ready!")
        print(f"   Virtual env: {env.venv_dir}")
        print(f"   Python: {env.get_python_executable()}")
    else:
        if args.json:
            print(json.dumps({
                "status": "error",
                "error": "Environment setup failed",
                "venv_dir": str(env.venv_dir),
            }, indent=2))
            return 1
        print("\nEnvironment setup failed")
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
