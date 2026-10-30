"""Marketplace layout that Claude Desktop accepts.

Claude Desktop refuses a plugin folder that holds a second plugin manifest
("plugin.json must be at .claude-plugin/plugin.json at the plugin root ...
found nested"). The claude-blog entry uses ``source: "./"``, so the whole
repository is its plugin folder and only the root manifest may exist. Blog
Studio is therefore served from the blog-studio branch, pinned to a commit.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"


def test_no_nested_plugin_manifest_below_the_repository_root():
    root_manifest = (ROOT / ".claude-plugin" / "plugin.json").resolve()
    nested = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("plugin.json")
        if path.parent.name == ".claude-plugin"
        and path.resolve() != root_manifest
        and not {".git", ".venv", "node_modules"} & set(path.relative_to(ROOT).parts)
    ]
    assert not nested, f"nested plugin manifests break Claude Desktop installs: {nested}"


def test_blog_studio_installs_from_the_pinned_branch():
    marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    entries = {entry["name"]: entry for entry in marketplace["plugins"]}
    assert marketplace["name"] == "agricidaniel-blog"
    assert marketplace["plugins"][0]["name"] == "claude-blog"
    assert marketplace["plugins"][0]["source"] == "./"
    assert list(entries) == ["claude-blog", "blog-studio"]
    studio = entries["blog-studio"]
    source = studio["source"]
    assert isinstance(source, dict), "blog-studio must not be a local path inside the plugin root"
    assert source["source"] == "git-subdir"
    assert source["url"] == "AgriciDaniel/claude-blog"
    assert source["path"] == "plugins/blog-studio"
    assert source["ref"] == "blog-studio"
    assert re.fullmatch(r"[0-9a-f]{40}", source["sha"]), source.get("sha")
    assert studio["version"] == "0.3.0"
    assert studio["homepage"] == "https://github.com/AgriciDaniel/claude-blog/tree/blog-studio/plugins/blog-studio"
