#!/usr/bin/env python3
"""
Environment Setup for NotebookLM Skill
Manages virtual environment and dependencies automatically
"""

import os
import sys
import subprocess
import venv
import hashlib
import json
from pathlib import Path


class SkillEnvironment:
    """Manages skill-specific virtual environment"""

    def __init__(self):
        # Skill directory paths
        self.skill_dir = Path(__file__).parent.parent
        self.venv_dir = self.skill_dir / ".venv"
        # Bug fix: requirements.txt actually lives in scripts/, not the skill
        # root. Prior path looked at skill_dir/requirements.txt which never
        # existed. Now also prefer the lock file when present (closes audit
        # VULN-006 supply-chain detection gap).
        self.lock_file = self.skill_dir / "scripts" / "requirements.lock"
        self.requirements_file = self.skill_dir / "scripts" / "requirements.txt"
        self.stamp_file = self.venv_dir / ".requirements.stamp"

        # Python executable in venv
        if os.name == 'nt':  # Windows
            self.venv_python = self.venv_dir / "Scripts" / "python.exe"
            self.venv_pip = self.venv_dir / "Scripts" / "pip.exe"
        else:  # Unix/Linux/Mac
            self.venv_python = self.venv_dir / "bin" / "python"
            self.venv_pip = self.venv_dir / "bin" / "pip"

    def ensure_venv(self) -> bool:
        """Ensure virtual environment exists and is set up"""

        # Check if we're already in the correct venv
        if self.is_in_skill_venv():
            print("✅ Already running in skill virtual environment")
            return True

        # Create venv if it doesn't exist
        if not self.venv_dir.exists():
            print(f"🔧 Creating virtual environment in {self.venv_dir.name}/")
            try:
                venv.create(self.venv_dir, with_pip=True)
                print("✅ Virtual environment created")
            except Exception as e:
                print(f"❌ Failed to create venv: {e}")
                return False

        # Install/update dependencies. Prefer lock file when present.
        if self.lock_file.exists():
            install_args = ["install", "--require-hashes", "-r", str(self.lock_file)]
            install_label = "lock file (hash-verified)"
        elif self.requirements_file.exists():
            install_args = ["install", "-r", str(self.requirements_file)]
            install_label = "requirements.txt (no hash verification)"
        else:
            install_args = None

        if install_args:
            print(f"📦 Installing dependencies from {install_label}...")
            try:
                # Install requirements (lock or .txt)
                result = subprocess.run(
                    [str(self.venv_pip)] + install_args,
                    check=True,
                    capture_output=True,
                    text=True
                )
                self.write_dependency_stamp()
                print("✅ Dependencies installed")

                # Install Chrome for Patchright (not Chromium!)
                # Using real Chrome ensures cross-platform reliability and consistent browser fingerprinting
                # See: https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python#anti-detection
                print("🌐 Installing Google Chrome for Patchright...")
                try:
                    subprocess.run(
                        [str(self.venv_python), "-m", "patchright", "install", "chrome"],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    print("✅ Chrome installed")
                except subprocess.CalledProcessError as e:
                    print(f"⚠️ Warning: Failed to install Chrome: {e}")
                    print("   You may need to run manually: python3 -m patchright install chrome")
                    print("   Chrome is required (not Chromium) for reliability!")

                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install dependencies: {e}")
                print(f"   Output: {e.output if hasattr(e, 'output') else 'No output'}")
                return False
        else:
            print("⚠️ No requirements.txt found, skipping dependency installation")
            return True

    def is_in_skill_venv(self) -> bool:
        """Check if we're already running in the skill's venv"""
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            # We're in a venv, check if it's ours
            venv_path = Path(sys.prefix)
            return venv_path == self.venv_dir
        return False

    def get_python_executable(self) -> str:
        """Get the correct Python executable to use"""
        if self.venv_python.exists():
            return str(self.venv_python)
        return sys.executable

    def dependency_source(self) -> Path | None:
        if self.lock_file.exists():
            return self.lock_file
        if self.requirements_file.exists():
            return self.requirements_file
        return None

    def dependency_stamp(self) -> str | None:
        source = self.dependency_source()
        if not source:
            return None
        return hashlib.sha256(source.read_bytes()).hexdigest()

    def dependencies_current(self) -> bool:
        expected = self.dependency_stamp()
        if not expected or not self.stamp_file.exists():
            return False
        try:
            return self.stamp_file.read_text().strip() == expected
        except OSError:
            return False

    def write_dependency_stamp(self) -> None:
        stamp = self.dependency_stamp()
        if stamp:
            self.stamp_file.write_text(stamp)

    def resolve_script_path(self, script_name: str) -> Path:
        """Resolve a script path and require it to stay in scripts/."""
        if script_name.startswith("scripts/") or script_name.startswith("scripts\\"):
            script_name = script_name[8:]
        scripts_dir = (self.skill_dir / "scripts").resolve()
        script_path = (scripts_dir / script_name).resolve()
        try:
            script_path.relative_to(scripts_dir)
        except ValueError as exc:
            raise ValueError(f"Script path escapes scripts directory: {script_name}") from exc
        return script_path

    def run_script(self, script_name: str, args: list = None) -> int:
        """Run a script with the virtual environment"""
        try:
            script_path = self.resolve_script_path(script_name)
        except ValueError as e:
            print(f"❌ {e}")
            return 1

        if not script_path.is_file():
            print(f"❌ Script not found: {script_path}")
            return 1

        # Ensure venv is set up
        if not self.ensure_venv():
            print("❌ Failed to set up environment")
            return 1

        # Build command
        cmd = [str(self.venv_python), str(script_path)]
        if args:
            cmd.extend(args)

        print(f"🚀 Running: {script_name} with venv Python")

        try:
            # Run the script with venv Python
            result = subprocess.run(cmd)
            return result.returncode
        except Exception as e:
            print(f"❌ Failed to run script: {e}")
            return 1

    def activate_instructions(self) -> str:
        """Get instructions for manual activation"""
        if os.name == 'nt':
            activate = self.venv_dir / "Scripts" / "activate.bat"
            return f"Run: {activate}"
        else:
            activate = self.venv_dir / "bin" / "activate"
            return f"Run: source {activate}"


def main():
    """Main entry point for environment setup"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Setup NotebookLM skill environment'
    )

    parser.add_argument(
        '--check',
        action='store_true',
        help='Check if environment is set up'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output structured JSON'
    )

    parser.add_argument(
        '--run',
        help='Run a script with the venv (e.g., --run ask_question.py)'
    )

    parser.add_argument(
        'args',
        nargs='*',
        help='Arguments to pass to the script'
    )

    args = parser.parse_args()

    env = SkillEnvironment()

    if args.check:
        status = {
            "venv_exists": env.venv_dir.exists(),
            "python": env.get_python_executable(),
            "dependencies_current": env.dependencies_current(),
            "dependency_source": str(env.dependency_source()) if env.dependency_source() else None,
        }
        if args.json:
            print(json.dumps(status, indent=2))
            return 0 if status["venv_exists"] and status["dependencies_current"] else 1
        if env.venv_dir.exists():
            print(f"✅ Virtual environment exists: {env.venv_dir}")
            print(f"   Python: {env.get_python_executable()}")
            print(f"   Dependencies current: {'yes' if env.dependencies_current() else 'no'}")
            print(f"   To activate manually: {env.activate_instructions()}")
        else:
            print(f"❌ No virtual environment found")
            print(f"   Run setup_environment.py to create it")
        return

    if args.run:
        # Run a script with venv
        return env.run_script(args.run, args.args)

    # Default: ensure environment is set up
    if env.ensure_venv():
        if args.json:
            print(json.dumps({
                "status": "success",
                "venv": str(env.venv_dir),
                "python": env.get_python_executable(),
                "dependencies_current": env.dependencies_current(),
            }, indent=2))
            return 0
        print("\n✅ Environment ready!")
        print(f"   Virtual env: {env.venv_dir}")
        print(f"   Python: {env.get_python_executable()}")
        print(f"\nTo activate manually: {env.activate_instructions()}")
        print(f"Or run scripts directly: python3 setup_environment.py --run script_name.py")
    else:
        if args.json:
            print(json.dumps({"status": "error", "venv": str(env.venv_dir)}, indent=2))
            return 1
        print("\n❌ Environment setup failed")
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
