"""Regression for readable links and small byline text in both themes."""

import importlib.util
from pathlib import Path
import re

import pytest


ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("render_contrast", ROOT / "scripts/blog_render.py")
RENDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDER)
THEMES = [dict(re.findall(r"(--[\w-]+):(#[a-f0-9]{6})", block)) for block in re.findall(r":root\{([^}]+)", RENDER.CSS)[:2]]


def luminance(color):
    channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


@pytest.mark.parametrize("theme", THEMES, ids=("light", "dark"))
@pytest.mark.parametrize("foreground,background", [("--soft", "--bg"), ("--accent", "--bg"), ("--accent", "--code-bg"), ("--accent-deep", "--bg")])
def test_small_text_and_links_meet_minimum_contrast(theme, foreground, background):
    # WCAG 2.2 SC 1.4.3: normal-sized text needs an unrounded ratio >= 4.5.
    low, high = sorted((luminance(theme[foreground]), luminance(theme[background])))
    assert (high + 0.05) / (low + 0.05) >= 4.5
