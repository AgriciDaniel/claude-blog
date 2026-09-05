"""
Browser Utilities for NotebookLM Skill
Handles browser launching, stealth features, and common interactions
"""

import json
import time
import random
from pathlib import Path
from typing import Optional, List

from patchright.sync_api import Playwright, BrowserContext, Page
from config import BROWSER_PROFILE_DIR, STATE_FILE, BROWSER_ARGS, USER_AGENT


def _harden_perms(path) -> None:
    """Set restrictive permissions on a credential file or directory.

    Files: 0o600 (owner read/write only).
    Dirs: 0o700 (owner traverse only).
    Recursively applies to all children of dirs.
    Best-effort: failures are swallowed silently (Windows fs may lack POSIX mode bits).

    Duplicated here (also lives in auth_manager) to avoid an import cycle:
    auth_manager already imports browser_utils.
    """
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
        pass


class BrowserFactory:
    """Factory for creating configured browser contexts"""

    @staticmethod
    def launch_persistent_context(
        playwright: Playwright,
        headless: bool = True,
        user_data_dir: str = str(BROWSER_PROFILE_DIR)
    ) -> BrowserContext:
        """
        Launch a persistent browser context with anti-detection features
        and cookie workaround.
        """
        # Launch persistent context
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",  # Use real Chrome
            headless=headless,
            no_viewport=True,
            ignore_default_args=["--enable-automation"],
            user_agent=USER_AGENT,
            args=BROWSER_ARGS
        )

        # Harden the persistent profile dir recursively (VULN-004 mitigation).
        # Patchright writes cookies, tokens, and cache here under default 0o755.
        _harden_perms(user_data_dir)

        # Cookie Workaround for Playwright bug #36139
        # Session cookies (expires=-1) don't persist in user_data_dir automatically
        BrowserFactory._inject_cookies(context)

        return context

    @staticmethod
    def _inject_cookies(context: BrowserContext):
        """Inject cookies from state.json if available"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    state = json.load(f)
                    if 'cookies' in state and len(state['cookies']) > 0:
                        context.add_cookies(state['cookies'])
                        # print(f"  🔧 Injected {len(state['cookies'])} cookies from state.json")
            except Exception as e:
                print(f"  ⚠️  Could not load state.json: {e}")


class StealthUtils:
    """Human-like interaction utilities"""

    @staticmethod
    def random_delay(min_ms: int = 100, max_ms: int = 500):
        """Add random delay"""
        time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))

    @staticmethod
    def human_type(page: Page, selector: str, text: str, wpm_min: int = 320, wpm_max: int = 480):
        """Type with human-like speed"""
        element = page.query_selector(selector)
        if not element:
            # Try waiting if not immediately found
            try:
                element = page.wait_for_selector(selector, timeout=2000)
            except Exception:
                pass
        
        if not element:
            print(f"⚠️ Element not found for typing: {selector}")
            return

        # Click to focus
        element.click()
        
        # Type
        for char in text:
            element.type(char, delay=random.uniform(25, 75))
            if random.random() < 0.05:
                time.sleep(random.uniform(0.15, 0.4))

    @staticmethod
    def realistic_click(page: Page, selector: str):
        """Click with realistic movement"""
        element = page.query_selector(selector)
        if not element:
            return

        # Optional: Move mouse to element (simplified)
        box = element.bounding_box()
        if box:
            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2
            page.mouse.move(x, y, steps=5)

        StealthUtils.random_delay(100, 300)
        element.click()
        StealthUtils.random_delay(100, 300)

    @staticmethod
    def random_mouse_movement(page: Page, moves: int = 3):
        """Move the mouse across random visible points."""
        viewport = page.viewport_size or {"width": 1280, "height": 720}
        width = max(1, int(viewport.get("width", 1280)))
        height = max(1, int(viewport.get("height", 720)))
        for _ in range(max(1, moves)):
            x = random.randint(1, width)
            y = random.randint(1, height)
            page.mouse.move(x, y, steps=random.randint(3, 8))
            StealthUtils.random_delay(80, 220)
