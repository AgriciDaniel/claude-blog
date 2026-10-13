#!/usr/bin/env python3
"""Validate native skill/agent YAML and the stricter maintained bundle contract.

Host fields: https://code.claude.com/docs/en/skills and /sub-agents,
reviewed 2026-10-07. Repository policy requires explicit invocation booleans,
names matching directories, no agent Bash access and no skill preapprovals.
The host itself defaults missing user-invocable to true. allowed-tools is valid
permission preapproval metadata, not a restriction on the available tool pool.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

import yaml


class FrontmatterError(ValueError):
    """Frontmatter cannot be interpreted unambiguously as a YAML mapping."""


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that refuses repeated keys at every mapping level."""


def _unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in result
        except TypeError as exc:
            raise FrontmatterError("mapping keys must be scalar and hashable") from exc
        if duplicate:
            raise FrontmatterError(f"duplicate field {key!r} (line {key_node.start_mark.line + 1})")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping)


def parse_frontmatter(text: str) -> dict:
    """Parse real YAML; missing, malformed, duplicate or nonmapping data fails."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise FrontmatterError("missing YAML frontmatter on first line")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i] == "---")
    except StopIteration as exc:
        raise FrontmatterError("unterminated YAML frontmatter") from exc
    try:
        value = yaml.load("\n".join(lines[1:end]), Loader=UniqueKeyLoader)
    except yaml.YAMLError as exc:
        raise FrontmatterError(f"malformed YAML: {exc}") from exc
    if not isinstance(value, dict):
        raise FrontmatterError("frontmatter must be a YAML mapping")
    if any(not isinstance(key, str) for key in value):
        raise FrontmatterError("frontmatter field names must be strings")
    return value


def _string(value):
    return isinstance(value, str) and bool(value.strip())


def _strings(value):
    return _string(value) or (isinstance(value, list) and all(_string(item) for item in value))


def _boolean(value):
    return type(value) is bool


SKILL_FIELDS = {
    **dict.fromkeys(("name", "description", "when_to_use", "argument-hint", "model", "agent", "license", "compatibility"), _string),
    **dict.fromkeys(("user-invocable", "disable-model-invocation", "background"), _boolean),
    **dict.fromkeys(("allowed-tools", "disallowed-tools", "arguments", "paths"), _strings),
    "metadata": lambda value: isinstance(value, dict),
    "hooks": lambda value: isinstance(value, dict),
    "context": lambda value: value == "fork",
    "effort": lambda value: value in ("low", "medium", "high", "xhigh", "max"),
    "shell": lambda value: value in ("bash", "powershell"),
}
AGENT_FIELDS = {
    **dict.fromkeys(("name", "description", "model", "initialPrompt", "color"), _string),
    **dict.fromkeys(("tools", "disallowedTools"), _strings),
    "skills": lambda value: isinstance(value, list) and all(_string(item) for item in value),
    "mcpServers": lambda value: isinstance(value, list) and all(_string(item) or isinstance(item, dict) for item in value),
    "hooks": lambda value: isinstance(value, dict),
    "maxTurns": lambda value: type(value) is int and value > 0,
    "permissionMode": lambda value: value in ("default", "acceptEdits", "auto", "dontAsk", "bypassPermissions", "plan", "manual"),
    "memory": lambda value: value in ("user", "project", "local"),
    "effort": SKILL_FIELDS["effort"],
    "isolation": lambda value: value == "worktree",
    **dict.fromkeys(("background", "omitClaudeMd"), _boolean),
}


def validate_frontmatter(fields: dict, *, agent: bool = False, project_policy: bool = True) -> list[str]:
    """Check field shapes separately from the bundle's no-preapproval policy."""
    errors = []
    schema = AGENT_FIELDS if agent else SKILL_FIELDS
    for key, value in fields.items():
        if key == "user-invokable":
            errors.append("user-invokable is misspelled; use user-invocable")
        elif key not in schema:
            errors.append(f"unknown frontmatter field {key}")
        elif not schema[key](value):
            errors.append(f"invalid type or value for {key}")
    required = {"name", "description"}
    if project_policy:
        required |= {"tools"} if agent else {"license", "user-invocable"}
    for key in sorted(required - fields.keys()):
        suffix = " (project requires explicit declaration; host defaults to true)" if key == "user-invocable" else ""
        errors.append(f"missing required field {key}{suffix}")
    if project_policy and not agent:
        if fields.get("user-invocable", True) is True and "argument-hint" not in fields:
            errors.append("user-invocable skills must declare argument-hint (project policy)")
        if "allowed-tools" in fields:
            errors.append("allowed-tools is valid host preapproval metadata, but project policy forbids skill preapprovals")
    if project_policy and agent:
        tools = fields.get("tools", [])
        tools = re.split(r",\s*", tools) if isinstance(tools, str) else tools
        if isinstance(tools, list) and any(isinstance(tool, str) and tool.strip().split("(", 1)[0] == "Bash" for tool in tools):
            errors.append("tools grants Bash access, forbidden by project policy")
    if "compatibility" in fields and isinstance(fields["compatibility"], str) and len(fields["compatibility"]) > 500:
        errors.append("compatibility exceeds host 500-character limit")
    return errors


def validate_bundle(root: Path) -> list[str]:
    errors = []
    for agent, paths in ((False, sorted((root / "skills").glob("*/SKILL.md"))), (True, sorted((root / "agents").glob("*.md")))):
        if not paths:
            errors.append(f"{root}: no {'agents' if agent else 'skills'} found")
        names = {}
        for path in paths:
            label = path.relative_to(root).as_posix()
            try:
                text = path.read_text(encoding="utf-8")
                fields = parse_frontmatter(text)
            except (OSError, UnicodeError, FrontmatterError) as exc:
                errors.append(f"{label}: {exc}")
                continue
            errors.extend(f"{label}: {error}" for error in validate_frontmatter(fields, agent=agent))
            name = fields.get("name")
            if isinstance(name, str):
                if name in names:
                    errors.append(f"{label}: duplicate name {name!r}, also in {names[name]}")
                names[name] = label
                if not agent and name != path.parent.name:
                    errors.append(f"{label}: name must match skill directory {path.parent.name!r} (project policy)")
            if not agent:
                if len(text.splitlines()) > 500:
                    errors.append(f"{label}: exceeds project 500-line cap")
                if len(text.split()) > 5000:
                    errors.append(f"{label}: exceeds project approximate 5000-token (whitespace word) cap")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    errors = validate_bundle(args.root.resolve())
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("All skill and agent YAML passed host-field and project-policy checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
