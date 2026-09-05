"""Guard the plugin manifest against org-install validation failures.

The Claude plugin registry enforces a 500-character cap on the plugin
description (issue #22: a 579 -> 809 char description silently blocked
organisation installs even though `claude plugin validate` passed locally).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_plugin_description_within_registry_cap() -> None:
    d = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    desc = d.get("description", "")
    assert 0 < len(desc) <= 500, (
        f"plugin.json description is {len(desc)} chars; the plugin registry caps "
        f"it at 500 and rejects org installs above that."
    )


def test_marketplace_plugin_description_within_cap() -> None:
    m = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    for plugin in m.get("plugins", []):
        desc = plugin.get("description", "")
        assert len(desc) <= 500, (
            f"marketplace plugin '{plugin.get('name')}' description is {len(desc)} "
            f"chars; keep it at or under 500."
        )
