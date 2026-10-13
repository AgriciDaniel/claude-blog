#!/usr/bin/env python3
"""Run `claude plugin validate` and tolerate exactly one known false positive.

Claude Code 2.1.292 and later reserve every plugin name that starts with
"claude-", so the published name `claude-blog` is reported once by the
marketplace check and once by the plugin.json check. The name is the public
install slug and cannot change without breaking installed users, so CI must
accept those two findings and nothing else.

Policy, implemented below and covered by tests/test_dependency_plugin_validate_tolerance.py:

* Tolerated error 1: marketplace manifest, field `plugins[0].name`, message
  starting `Plugin name "claude-blog" is reserved`.
* Tolerated error 2: `.claude-plugin/plugin.json`, field `name`, same message.
* Tolerated warning: the plugin-root CLAUDE.md notice. The file is the
  contributor guide for this repository and is not shipped as plugin context.
* Tolerated warning (Claude Code 2.1.218 only, which predates mods): marketplace
  manifest, field `plugins[1] plugin.json → types`, message starting
  `Unknown field 'types'`. The optional blog-studio companion declares a
  `types` manifest key that mods-era Claude Code reads and the older validator
  reports as unknown ("Claude Code ignores it at load time").
* Every other error or warning, in any section, fails the run. Each tolerated
  finding counts once per section, so a duplicate is also a failure.
* A non-zero CLI exit with no parseable error block fails (an unknown output
  format must never turn into a silent pass). A "Found N errors" header whose
  item count differs from N fails for the same reason.

The script never contacts the network and never edits files.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

RESERVED_NAME_PREFIX = 'Plugin name "claude-blog" is reserved'
ROOT_CLAUDE_MD_PREFIX = "CLAUDE.md at the plugin root is not loaded as project context"
STUDIO_TYPES_FIELD = "plugins[1] plugin.json \u2192 types"
STUDIO_TYPES_PREFIX = "Unknown field 'types'"

ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
SECTION = re.compile(r"^Validating (?P<kind>[^:]+): (?P<target>.+?)\s*$")
BLOCK = re.compile(r"^\S?\s*Found (?P<count>\d+) (?P<level>error|warning)s?:\s*$")
ITEM = re.compile(r"^\s+[❯>]\s+(?P<field>[^\s:][^:]*?): (?P<message>.*)$")
CONTINUATION = re.compile(r"^\s{4,}\S")


@dataclass
class Finding:
    level: str
    section_kind: str
    section_target: str
    field: str
    message: str

    def describe(self) -> str:
        return (
            f"{self.level} in {self.section_kind} {self.section_target}: "
            f"{self.field}: {self.message}"
        )


@dataclass
class Parsed:
    findings: list[Finding] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)


def parse_output(text: str) -> Parsed:
    """Parse validator output into findings plus structural problems."""
    parsed = Parsed()
    kind = target = ""
    level = None
    expected = 0
    seen = 0
    open_finding: Finding | None = None

    def close_block() -> None:
        nonlocal level, expected, seen, open_finding
        if level is not None and seen != expected:
            parsed.problems.append(
                f"{kind} {target}: header announced {expected} {level}(s) but "
                f"{seen} were parsed"
            )
        level = None
        expected = seen = 0
        open_finding = None

    for raw in ANSI.sub("", text).splitlines():
        line = raw.rstrip("\r")
        section = SECTION.match(line)
        if section:
            close_block()
            kind, target = section.group("kind"), section.group("target")
            continue
        block = BLOCK.match(line)
        if block:
            close_block()
            level = block.group("level")
            expected = int(block.group("count"))
            continue
        if level is None:
            continue
        item = ITEM.match(line)
        if item:
            open_finding = Finding(
                level, kind, target, item.group("field"), item.group("message")
            )
            parsed.findings.append(open_finding)
            seen += 1
        elif open_finding is not None and CONTINUATION.match(line):
            open_finding.message += " " + line.strip()
    close_block()
    return parsed


def _is_marketplace(finding: Finding) -> bool:
    return finding.section_kind.startswith("marketplace")


def _is_plugin_json(finding: Finding) -> bool:
    return finding.section_kind == "plugin" and Path(
        finding.section_target
    ).as_posix().endswith(".claude-plugin/plugin.json")


def _is_root_claude_md(finding: Finding) -> bool:
    return finding.section_kind == "plugin" and Path(
        finding.section_target
    ).name == "CLAUDE.md"


def tolerated_key(finding: Finding) -> str | None:
    """Return the allowlist slot a finding fills, or None when it is not allowed."""
    if finding.level == "error" and finding.message.startswith(RESERVED_NAME_PREFIX):
        if _is_marketplace(finding) and finding.field == "plugins[0].name":
            return "marketplace-reserved-name"
        if _is_plugin_json(finding) and finding.field == "name":
            return "plugin-json-reserved-name"
    if (
        finding.level == "warning"
        and finding.field == "root"
        and finding.message.startswith(ROOT_CLAUDE_MD_PREFIX)
        and _is_root_claude_md(finding)
    ):
        return "root-claude-md-warning"
    if (
        finding.level == "warning"
        and _is_marketplace(finding)
        and finding.field == STUDIO_TYPES_FIELD
        and finding.message.startswith(STUDIO_TYPES_PREFIX)
    ):
        return "blog-studio-types-field-warning"
    return None


def evaluate(text: str, exit_code: int) -> tuple[bool, list[str], list[str]]:
    """Return (ok, tolerated descriptions, blocking descriptions)."""
    parsed = parse_output(text)
    tolerated: list[str] = []
    blocking: list[str] = list(parsed.problems)
    used: set[str] = set()
    for finding in parsed.findings:
        key = tolerated_key(finding)
        if key is None:
            blocking.append(finding.describe())
        elif key in used:
            blocking.append("duplicate of a tolerated finding: " + finding.describe())
        else:
            used.add(key)
            tolerated.append(key)
    if exit_code != 0 and not any(f.level == "error" for f in parsed.findings):
        blocking.append(
            f"validator exited {exit_code} but no error block could be parsed; "
            "refusing to treat unknown output as a pass"
        )
    return not blocking, tolerated, blocking


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="plugin root to validate")
    parser.add_argument("--cli", default="claude", help="Claude Code executable")
    parser.add_argument(
        "--from-file",
        help="parse saved validator output instead of running the CLI",
    )
    parser.add_argument(
        "--exit-code",
        type=int,
        default=None,
        help="exit status of the saved run (required with --from-file)",
    )
    args = parser.parse_args(argv)

    if args.from_file:
        if args.exit_code is None:
            parser.error("--from-file requires --exit-code")
        text = Path(args.from_file).read_text(encoding="utf-8")
        exit_code = args.exit_code
    else:
        result = subprocess.run(
            [args.cli, "plugin", "validate", args.root],
            capture_output=True,
            text=True,
            check=False,
        )
        text = result.stdout + result.stderr
        exit_code = result.returncode
        sys.stdout.write(text)

    ok, tolerated, blocking = evaluate(text, exit_code)
    if tolerated:
        print(f"Tolerated known findings: {', '.join(sorted(tolerated))}")
    if not ok:
        print("Blocking validator findings:", file=sys.stderr)
        for item in blocking:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print("claude plugin validate: no blocking findings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
