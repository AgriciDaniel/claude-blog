"""Opt-in primary-source domains (official docs of the entity under review)."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import analyze_blog

SCRIPT = Path(__file__).parent.parent / "scripts" / "analyze_blog.py"

POST = """---
title: Bybit P2P fees explained
description: How Bybit P2P fees work for advertisers, with official sources.
author: Jane Doe
---
# Bybit P2P fees explained

## Fees

Bybit charges no P2P fee for most currencies, per the
[fee page](https://www.bybit.com/en/help-center/article/P2P-Fees),
the [API docs](https://bybit-exchange.github.io/docs/p2p/guide),
[OKX rules](https://www.okx.com/help/p2p-rules),
[Binance terms](https://www.binance.com/en/terms) and
[a forum thread](https://forum.example.org/t/fees).
"""


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("bybit.com", "bybit.com"),
        ("https://www.Bybit.com/en/help-center", "bybit.com"),
        ("*.okx.com", "okx.com"),
        ("bybit-exchange.github.io", "bybit-exchange.github.io"),
        ("binance.com:443", "binance.com"),
    ],
)
def test_domain_normalization(value, expected):
    assert analyze_blog.normalize_primary_source_domain(value) == expected


@pytest.mark.parametrize("value", ["", "com", "not a domain", "https://", "-bad-.com"])
def test_invalid_domains_are_rejected(value):
    with pytest.raises(ValueError):
        analyze_blog.normalize_primary_source_domain(value)


def test_cli_values_and_environment_are_merged_without_duplicates():
    env = {analyze_blog.PRIMARY_SOURCE_ENV: "bybit.com, okx.com binance.com"}
    assert analyze_blog.resolve_primary_source_domains(["binance.com", "bybit.com"], env) == (
        "binance.com", "bybit.com", "okx.com",
    )
    assert analyze_blog.resolve_primary_source_domains(None, {}) == ()


def test_primary_domains_promote_only_matching_hosts():
    primary = ("bybit.com",)
    assert analyze_blog._classify_source_tier("https://www.bybit.com/en/x", primary) == 1
    assert analyze_blog._classify_source_tier("https://bybit.com/x", primary) == 1
    assert analyze_blog._classify_source_tier("https://www.bybit.com/en/x") == 3
    assert analyze_blog._classify_source_tier("https://notbybit.com/x", primary) == 3
    assert analyze_blog._classify_source_tier("https://bybit.com.evil.example/x", primary) == 3
    assert analyze_blog._classify_source_tier("https://x.example/?u=bybit.com", primary) == 3


def test_default_analysis_is_unchanged_and_option_is_opt_in(tmp_path, monkeypatch):
    monkeypatch.delenv(analyze_blog.PRIMARY_SOURCE_ENV, raising=False)
    path = tmp_path / "post.md"
    path.write_text(POST, encoding="utf-8")

    default = analyze_blog.analyze_file(str(path))
    promoted = analyze_blog.analyze_file(
        str(path),
        primary_source_domains=("bybit.com", "bybit-exchange.github.io", "okx.com", "binance.com"),
    )

    assert default["citations"]["tier_counts"] == {1: 0, 2: 0, 3: 5}
    assert default["citations"]["primary_source_citations"] == 0
    assert default["source_policy"]["primary_source_domains"] == []
    assert promoted["citations"]["tier_counts"] == {1: 4, 2: 0, 3: 1}
    assert promoted["citations"]["primary_source_citations"] == 4
    assert promoted["links"]["primary_source_links"] == 4
    assert promoted["source_policy"]["primary_sources_count_as_tier"] == 1

    d_eeat = default["score"]["category_details"]["eeat_signals"]["breakdown"]
    p_eeat = promoted["score"]["category_details"]["eeat_signals"]["breakdown"]
    assert p_eeat["citations"] == d_eeat["citations"] + 2
    d_seo = default["score"]["category_details"]["seo_optimization"]["breakdown"]
    p_seo = promoted["score"]["category_details"]["seo_optimization"]["breakdown"]
    assert p_seo["external_linking"] == d_seo["external_linking"] + 1
    assert promoted["score"]["total"] == default["score"]["total"] + 3


def _run(args, env_extra=None):
    import os

    env = {k: v for k, v in os.environ.items() if k != analyze_blog.PRIMARY_SOURCE_ENV}
    env.update(env_extra or {})
    return subprocess.run(
        [sys.executable, "-I", str(SCRIPT), *args],
        capture_output=True, text=True, encoding="utf-8", env=env, timeout=60,
    )


def test_cli_flag_and_environment_variable(tmp_path):
    path = tmp_path / "post.md"
    path.write_text(POST, encoding="utf-8")

    plain = json.loads(_run([str(path)]).stdout)
    flagged = json.loads(_run([str(path), "--primary-source-domain", "bybit.com",
                               "--primary-source-domain", "bybit-exchange.github.io"]).stdout)
    from_env = json.loads(_run([str(path)], {analyze_blog.PRIMARY_SOURCE_ENV: "bybit.com"}).stdout)

    assert plain["citations"]["tier_counts"]["1"] == 0
    assert flagged["citations"]["tier_counts"]["1"] == 2
    assert from_env["citations"]["tier_counts"]["1"] == 1


def test_cli_rejects_invalid_domain(tmp_path):
    path = tmp_path / "post.md"
    path.write_text(POST, encoding="utf-8")
    result = _run([str(path), "--primary-source-domain", "com"])
    assert result.returncode == 2
    assert "invalid primary source domain" in result.stderr


def test_cli_lang_override(tmp_path):
    path = tmp_path / "post.md"
    path.write_text(POST, encoding="utf-8")
    result = json.loads(_run([str(path), "--lang", "es"]).stdout)
    assert result["language"] == "es"
    assert result["language_detection"]["method"] == "cli-override"
