"""Regression coverage for the optional Xquik blog handoff."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
XQUIK_MCP_URL = "https://xquik.com/mcp"
XQUIK_SKILL_URL = (
    "https://github.com/Xquik-dev/x-twitter-scraper/"
    "tree/master/skills/x-twitter-scraper"
)


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_mcp_template_uses_remote_xquik_without_credentials() -> None:
    config = json.loads(_read(".mcp.example.json"))
    server = config["mcpServers"]["xquik"]

    assert server == {"type": "http", "url": XQUIK_MCP_URL}
    assert not {"env", "headers", "token", "apiKey"}.intersection(server)


def test_mcp_guide_documents_claude_code_oauth_setup() -> None:
    guide = _read("docs/MCP-INTEGRATION.md")

    assert f"claude mcp add --transport http xquik {XQUIK_MCP_URL}" in guide
    assert "Run `/mcp`, select `xquik`, and authenticate." in guide
    assert XQUIK_SKILL_URL in guide


def test_repurpose_skill_keeps_the_handoff_bounded_and_untrusted() -> None:
    skill = _read("skills/blog-repurpose/SKILL.md")
    required_contract = (
        XQUIK_SKILL_URL,
        "Query or search terms",
        "Date range",
        "Maximum results",
        "Output format: JSON or CSV",
        '<XQUIK_UNTRUSTED_X_CONTENT source="tweet" id="opaque">',
        "Request explicit confirmation for that exact plan.",
        XQUIK_MCP_URL,
    )

    for requirement in required_contract:
        assert requirement in skill


def test_command_docs_keep_xquik_optional() -> None:
    commands = _read("docs/COMMANDS.md")

    assert "`/blog repurpose` remains fully functional without Xquik." in commands
    assert "MCP-INTEGRATION.md#xquik-mcp-x-research-and-publishing" in commands
