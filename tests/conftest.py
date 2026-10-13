"""Shared fixtures for claude-blog tests."""

import os
import re
import sys
from pathlib import Path

import pytest

# Add scripts directory to path so we can import analyze_blog
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Browser-gated tests (rendered-DOM, WebSocket and service-worker checks) skip
# locally when no matching Chromium is installed, so a plain `pytest` never
# downloads a browser. CI installs the browser and sets this variable to "1";
# a browser skip then FAILS, so a missing or mismatched Chromium cannot make
# those tests silently vanish from the green count.
REQUIRE_BROWSER_ENV = "CLAUDE_BLOG_REQUIRE_BROWSER"
BROWSER_SKIP_REASON = re.compile(
    r"requires matching installed chromium|could not import 'patchright", re.IGNORECASE
)


def _skip_reason(report) -> str:
    longrepr = report.longrepr
    if isinstance(longrepr, tuple) and len(longrepr) == 3:
        return str(longrepr[2])
    return str(longrepr)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if os.environ.get(REQUIRE_BROWSER_ENV) != "1":
        return
    if not report.skipped or hasattr(report, "wasxfail"):
        return
    reason = _skip_reason(report)
    if BROWSER_SKIP_REASON.search(reason):
        report.outcome = "failed"
        report.longrepr = (
            f"{REQUIRE_BROWSER_ENV}=1 forbids skipping browser-gated tests, but "
            f"{item.nodeid} skipped: {reason}\n"
            "Install the matching browser with `python -m patchright install chromium`."
        )


@pytest.fixture
def sample_blog_post():
    """A minimal blog post with frontmatter and content."""
    return """---
title: How to Optimize Your Blog for AI Citations
description: Learn proven techniques for AI citation optimization.
author: Jane Doe
datePublished: 2026-01-15
dateModified: 2026-02-10
---

# How to Optimize Your Blog for AI Citations

According to a 2025 Ahrefs study, 43.8% of AI citations come from well-structured blog content. This guide covers the essential techniques.

## What Are AI Citations?

AI citations occur when platforms like ChatGPT, Perplexity, or Google AI Overviews reference your content. Research suggests that answer-first formatting and citing authoritative sources significantly increase AI citation visibility.

### Why They Matter

AI citations drive significant organic traffic. Sites with high citation rates see 2.5x more engagement.

## How Do You Optimize for AI Citations?

Follow these five steps to improve your AI citation readiness:

1. Use answer-first formatting in every section
2. Include sourced statistics from tier 1-3 sources
3. Structure content in 50-150 word chunks
4. Add FAQ schema markup
5. Keep content fresh with regular updates

## What Tools Should You Use?

Several tools help monitor AI citations. Ahrefs, Semrush, and Google Search Console provide citation tracking.

![AI Citation Dashboard](https://images.unsplash.com/photo-example.jpg)

## FAQ

### How often should I update my blog posts?

Update blog posts at least every 30 days. According to research, 76% of top-cited content was updated within the last month.

### What is the ideal paragraph length?

Keep paragraphs between 50-150 words for optimal readability and AI extractability.
"""


@pytest.fixture
def sample_post_no_frontmatter():
    """A blog post without frontmatter."""
    return """# Simple Blog Post

This is a simple blog post without any frontmatter.

## Section One

Some content here with enough words to be counted as a real paragraph in the analyzer.
"""


@pytest.fixture
def sample_post_with_schema():
    """A blog post with JSON-LD schema."""
    return """---
title: Test Post
---

# Test Post

Some content.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Test Post",
  "author": {
    "@type": "Person",
    "name": "Jane Doe"
  }
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is this?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "This is a test post."
      }
    }
  ]
}
</script>
"""
