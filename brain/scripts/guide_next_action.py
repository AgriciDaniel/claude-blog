#!/usr/bin/env python3
"""Read hot.md and return the next operator action."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print the next operator action from hot.md.")
    parser.add_argument("--vault", required=True)
    parser.add_argument("--json", action="store_true", help="Print a JSON result envelope.")
    args = parser.parse_args(argv)
    hot = Path(args.vault).expanduser().resolve() / "wiki" / "hot.md"
    text = hot.read_text(encoding="utf-8") if hot.exists() else ""
    match = re.search(r"## Next Action\s+(.+?)(?:\n## |\Z)", text, re.S)
    action = match.group(1).strip() if match else "Read CODEX.md, wiki/hot.md, and wiki/index.md."
    if args.json:
        print(json.dumps({"ok": True, "next_action": action}, indent=2, sort_keys=True))
    else:
        print(action)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
