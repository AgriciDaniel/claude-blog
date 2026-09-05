#!/usr/bin/env python3
"""
Authentication Manager for NotebookLM
Handles Google login and browser state persistence
Based on the MCP server implementation

Implements hybrid auth approach:
- Persistent browser profile (user_data_dir) for fingerprint consistency
- Manual cookie injection from state.json for session cookies (Playwright bug workaround)
See: https://github.com/microsoft/playwright/issues/36139
"""

import json
import time
import argparse
import shutil
import re
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from patchright.sync_api import sync_playwright, BrowserContext

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import BROWSER_STATE_DIR, STATE_FILE, AUTH_INFO_FILE, DATA_DIR
from browser_utils import BrowserFactory


def _harden_perms(path) -> None:
    """Set restrictive permissions on a credential file or directory.

    Files: 0o600 (owner read/write only).
    Dirs: 0o700 (owner traverse only).
    Recursively applies to all children of dirs.
    Best-effort: failures are swallowed silently (Windows fs may lack POSIX mode bits).
    """
    import os
    from pathlib import Path
    p = Path(path)
    try:
        if p.is_dir():
            p.chmod(0o700)
            for child in p.rglob("*"):
                try:
                    child.chmod(0o600 if child.is_file() else 0o700)
                except OSError:
                    pass
        elif p.is_file():
            p.chmod(0o600)
    except OSError:
        pass  # Windows / readonly fs / etc.


class AuthManager:
    """
    Manages authentication and browser state for NotebookLM

    Features:
    - Interactive Google login
    - Browser state persistence
    - Session restoration
    - Account switching
    """

    def __init__(self):
        """Initialize the authentication manager"""
        # Ensure directories exist
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        BROWSER_STATE_DIR.mkdir(parents=True, exist_ok=True)

        self.state_file = STATE_FILE
        self.auth_info_file = AUTH_INFO_FILE
        self.browser_state_dir = BROWSER_STATE_DIR

    def is_authenticated(self) -> bool:
        """Check whether a local browser state file exists."""
        if not self.state_file.exists():
            return False

        # Check if state file is not too old (7 days)
        age_days = (time.time() - self.state_file.stat().st_mtime) / 86400
        if age_days > 7:
            print(f"⚠️ Browser state is {age_days:.1f} days old, may need re-authentication")

        return True

    def get_auth_info(self) -> Dict[str, Any]:
        """Get authentication information"""
        info = {
            'authenticated': self.is_authenticated(),
            'state_file_present': self.state_file.exists(),
            'state_file': str(self.state_file),
            'state_exists': self.state_file.exists()
        }

        if self.auth_info_file.exists():
            try:
                with open(self.auth_info_file, 'r') as f:
                    saved_info = json.load(f)
                    info.update(saved_info)
            except Exception:
                pass

        if info['state_exists']:
            age_hours = (time.time() - self.state_file.stat().st_mtime) / 3600
            info['state_age_hours'] = age_hours

        return info

    def setup_auth(self, headless: bool = False, timeout_minutes: int = 10) -> bool:
        """
        Perform interactive authentication setup

        Args:
            headless: Run browser in headless mode (False for login)
            timeout_minutes: Maximum time to wait for login

        Returns:
            True if authentication successful
        """
        print("🔐 Starting authentication setup...")
        print(f"  Timeout: {timeout_minutes} minutes")

        playwright = None
        context = None

        try:
            playwright = sync_playwright().start()

            # Launch using factory
            context = BrowserFactory.launch_persistent_context(
                playwright,
                headless=headless
            )

            # Navigate to NotebookLM
            page = context.new_page()
            page.goto("https://notebooklm.google.com", wait_until="domcontentloaded")

            # Check if already authenticated
            if "notebooklm.google.com" in page.url and "accounts.google.com" not in page.url:
                print("  ✅ Already authenticated!")
                self._save_browser_state(context)
                return True

            # Wait for manual login
            print("\n  ⏳ Please log in to your Google account...")
            print(f"  ⏱️  Waiting up to {timeout_minutes} minutes for login...")

            try:
                # Wait for URL to change to NotebookLM (regex ensures it's the actual domain, not a parameter)
                timeout_ms = int(timeout_minutes * 60 * 1000)
                page.wait_for_url(re.compile(r"^https://notebooklm\.google\.com/"), timeout=timeout_ms)

                print(f"  ✅ Login successful!")

                # Save authentication state
                self._save_browser_state(context)
                self._save_auth_info()
                return True

            except Exception as e:
                print(f"  ❌ Authentication timeout: {e}")
                return False

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

        finally:
            # Clean up browser resources
            if context:
                try:
                    context.close()
                except Exception:
                    pass

            if playwright:
                try:
                    playwright.stop()
                except Exception:
                    pass

    def _save_browser_state(self, context: BrowserContext):
        """Save browser state to disk"""
        try:
            # Save storage state (cookies, localStorage)
            context.storage_state(path=str(self.state_file))
            # Harden permissions on credential file and parent dir (VULN-004 mitigation)
            _harden_perms(self.state_file)
            _harden_perms(self.browser_state_dir)
            print(f"  💾 Saved browser state to: {self.state_file}")
        except Exception as e:
            print(f"  ❌ Failed to save browser state: {e}")
            raise

    def _save_auth_info(self):
        """Save authentication metadata"""
        try:
            info = {
                'authenticated_at': time.time(),
                'authenticated_at_iso': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(self.auth_info_file, 'w') as f:
                json.dump(info, f, indent=2)
            # Harden permissions on auth info file (VULN-004 mitigation)
            _harden_perms(self.auth_info_file)
        except Exception:
            pass  # Non-critical

    def clear_auth(self) -> bool:
        """
        Clear all authentication data

        Returns:
            True if cleared successfully
        """
        print("🗑️ Clearing authentication data...")

        try:
            # Remove browser state
            if self.state_file.exists():
                self.state_file.unlink()
                print("  ✅ Removed browser state")

            # Remove auth info
            if self.auth_info_file.exists():
                self.auth_info_file.unlink()
                print("  ✅ Removed auth info")

            # Clear entire browser state directory
            if self.browser_state_dir.exists():
                shutil.rmtree(self.browser_state_dir)
                self.browser_state_dir.mkdir(parents=True, exist_ok=True)
                print("  ✅ Cleared browser data")

            return True

        except Exception as e:
            print(f"  ❌ Error clearing auth: {e}")
            return False

    def re_auth(self, headless: bool = False, timeout_minutes: int = 10) -> bool:
        """
        Perform re-authentication (clear and setup)

        Args:
            headless: Run browser in headless mode
            timeout_minutes: Login timeout in minutes

        Returns:
            True if successful
        """
        print("🔄 Starting re-authentication...")

        # Clear existing auth
        self.clear_auth()

        # Setup new auth
        return self.setup_auth(headless, timeout_minutes)

    def validate_auth(self) -> bool:
        """
        Validate that stored authentication works
        Uses persistent context to match actual usage pattern

        Returns:
            True if authentication is valid
        """
        if not self.is_authenticated():
            return False

        print("🔍 Validating authentication...")

        playwright = None
        context = None

        try:
            playwright = sync_playwright().start()

            # Launch using factory
            context = BrowserFactory.launch_persistent_context(
                playwright,
                headless=True
            )

            # Try to access NotebookLM
            page = context.new_page()
            page.goto("https://notebooklm.google.com", wait_until="domcontentloaded", timeout=30000)

            # Check if we can access NotebookLM
            if "notebooklm.google.com" in page.url and "accounts.google.com" not in page.url:
                print("  ✅ Authentication is valid")
                return True
            else:
                print("  ❌ Authentication is invalid (redirected to login)")
                return False

        except Exception as e:
            print(f"  ❌ Validation failed: {e}")
            return False

        finally:
            if context:
                try:
                    context.close()
                except Exception:
                    pass
            if playwright:
                try:
                    playwright.stop()
                except Exception:
                    pass


def main():
    """Command-line interface for authentication management"""
    parser = argparse.ArgumentParser(description='Manage NotebookLM authentication')
    parser.add_argument('--json', action='store_true', help='Output structured JSON')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup authentication')
    setup_parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    setup_parser.add_argument('--timeout', type=float, default=10, help='Login timeout in minutes (default: 10)')

    # Status command
    subparsers.add_parser('status', help='Check authentication status')

    # Validate command
    subparsers.add_parser('validate', help='Validate authentication')

    # Clear command
    subparsers.add_parser('clear', help='Clear authentication')

    # Re-auth command
    reauth_parser = subparsers.add_parser('reauth', help='Re-authenticate (clear + setup)')
    reauth_parser.add_argument('--timeout', type=float, default=10, help='Login timeout in minutes (default: 10)')

    args = parser.parse_args()

    # Initialize manager
    auth = AuthManager()

    # Execute command
    if args.command == 'setup':
        ok = auth.setup_auth(headless=args.headless, timeout_minutes=args.timeout)
        if args.json:
            print(json.dumps({"status": "success" if ok else "error", "command": "setup"}, indent=2))
        if ok:
            print("\n✅ Authentication setup complete!")
            print("You can now use ask_question.py to query NotebookLM")
        else:
            print("\n❌ Authentication setup failed")
            exit(1)

    elif args.command == 'status':
        info = auth.get_auth_info()
        if args.json:
            print(json.dumps({"status": "success", "auth": info}, indent=2))
            return
        print("\n🔐 Authentication Status:")
        print(f"  State file present: {'Yes' if info['state_file_present'] else 'No'}")
        print("  Run validate to confirm the Google login still works.")
        if info.get('state_age_hours'):
            print(f"  State age: {info['state_age_hours']:.1f} hours")
        if info.get('authenticated_at_iso'):
            print(f"  Last auth: {info['authenticated_at_iso']}")
        print(f"  State file: {info['state_file']}")

    elif args.command == 'validate':
        ok = auth.validate_auth()
        if args.json:
            print(json.dumps({"status": "success" if ok else "error", "valid": ok}, indent=2))
            return
        if ok:
            print("Authentication is valid and working")
        else:
            print("Authentication is invalid or expired")
            print("Run: auth_manager.py setup")

    elif args.command == 'clear':
        ok = auth.clear_auth()
        if args.json:
            print(json.dumps({"status": "success" if ok else "error", "command": "clear"}, indent=2))
            return
        if ok:
            print("Authentication cleared")

    elif args.command == 'reauth':
        ok = auth.re_auth(timeout_minutes=args.timeout)
        if args.json:
            print(json.dumps({"status": "success" if ok else "error", "command": "reauth"}, indent=2))
        if ok:
            print("\n✅ Re-authentication complete!")
        else:
            print("\n❌ Re-authentication failed")
            exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
