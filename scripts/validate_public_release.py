#!/usr/bin/env python3
"""Validate a prepared public claude-blog release worktree.

This read-only check prevents private raw URLs, private marketplace slugs, and
membership-only install instructions from leaking into the public mirror.
Run it against the prepared public worktree, never as a validator for the
private source tree.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PUBLIC_REPOSITORY = "https://github.com/AgriciDaniel/claude-blog"
PUBLIC_VERSION = "2.1.1"
PUBLIC_SLUG = "claude-blog@agricidaniel-blog"
PUBLIC_OWNER = "AgriciDaniel"
PUBLIC_OWNER_URL = "https://github.com/AgriciDaniel"
PUBLIC_MARKETPLACE = "agricidaniel-blog"
PUBLIC_RAW_INSTALL_SH = (
    "https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.sh"
)
PUBLIC_RAW_INSTALL_PS1 = (
    "https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.ps1"
)
PUBLIC_PINNED_INSTALL_SH = (
    f"https://raw.githubusercontent.com/AgriciDaniel/claude-blog/"
    f"v{PUBLIC_VERSION}/install.sh"
)
PUBLIC_DISCUSSIONS = f"{PUBLIC_REPOSITORY}/discussions"
PUBLIC_SECURITY_ADVISORY = f"{PUBLIC_REPOSITORY}/security/advisories/new"
PUBLIC_DOCUMENTATION = f"{PUBLIC_REPOSITORY}/tree/main/docs"
SECURITY_CHECKOUT_RE = re.compile(
    r"\bgit checkout v([0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?)\b"
)
SURFACES = (
    "README.md",
    "CLAUDE.md",
    "CITATION.cff",
    "pyproject.toml",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/SECURITY.md",
    "install.sh",
    "install.ps1",
    "skills/blog/SKILL.md",
)
FORBIDDEN_PATTERNS = {
    "private_raw_url": re.compile(
        r"raw\.githubusercontent\.com/AI-Marketing-Hub/claude-blog",
        re.IGNORECASE,
    ),
    "private_repository_url": re.compile(
        r"github\.com/AI-Marketing-Hub/claude-blog",
        re.IGNORECASE,
    ),
    "private_marketplace_slug": re.compile(
        r"claude-blog@ai-marketing-hub-claude-blog",
        re.IGNORECASE,
    ),
    "obsolete_public_slug": re.compile(
        r"claude-blog@agricidaniel-claude-blog",
        re.IGNORECASE,
    ),
    "private_auth_instruction": re.compile(
        r"(?:authenticated\s+`?gh auth login`?|GitHub PAT).{0,100}"
        r"(?:AI-Marketing-Hub|private|org)",
        re.IGNORECASE | re.DOTALL,
    ),
    "private_membership_instruction": re.compile(
        r"(?:requires?\s+(?:an?\s+)?(?:Pro\s+)?membership|"
        r"account\s+is\s+not\s+in\s+the\s+org)",
        re.IGNORECASE,
    ),
}
RAW_INSTALLER_RE = re.compile(
    r"https://raw\.githubusercontent\.com/[^/\s]+/[^/\s]+/"
    r"[^/\s]+/install\.(?:sh|ps1)",
    re.IGNORECASE,
)


def validate(root: Path) -> dict:
    root = root.resolve()
    errors: list[dict] = []
    contents: dict[str, str] = {}
    for relative in SURFACES:
        path = root / relative
        if not path.is_file():
            errors.append({"kind": "missing_release_surface", "file": relative})
            continue
        contents[relative] = path.read_text(encoding="utf-8")

    docs_dir = root / "docs"
    if docs_dir.is_dir():
        for path in docs_dir.rglob("*.md"):
            relative = path.relative_to(root).as_posix()
            contents.setdefault(relative, path.read_text(encoding="utf-8"))
            if path.name.startswith("PUBLIC-BACKLOG-TRIAGE-"):
                errors.append({"kind": "private_triage_note", "file": relative})

    for relative, text in contents.items():
        for kind, pattern in FORBIDDEN_PATTERNS.items():
            if kind == "private_repository_url" and relative not in SURFACES:
                # Attribution and migration history may legitimately mention
                # the private repository. Canonical distribution surfaces may
                # not identify it as the public package.
                continue
            if pattern.search(text):
                errors.append({"kind": kind, "file": relative})

    readme = contents.get("README.md", "")
    if PUBLIC_SLUG not in readme:
        errors.append(
            {
                "kind": "missing_public_marketplace_slug",
                "file": "README.md",
                "expected": PUBLIC_SLUG,
            }
        )
    if PUBLIC_REPOSITORY not in readme:
        errors.append(
            {
                "kind": "missing_public_repository_url",
                "file": "README.md",
                "expected": PUBLIC_REPOSITORY,
            }
        )
    for expected in (PUBLIC_RAW_INSTALL_SH, PUBLIC_RAW_INSTALL_PS1):
        if expected not in readme:
            errors.append(
                {
                    "kind": "missing_exact_public_raw_installer",
                    "file": "README.md",
                    "expected": expected,
                }
            )

    version_fragments = {
        "README.md": (
            f"git checkout v{PUBLIC_VERSION}",
            f"CLAUDE_BLOG_REF=v{PUBLIC_VERSION}",
        ),
        "CLAUDE.md": (
            f"CLAUDE_BLOG_REF=v{PUBLIC_VERSION}",
            PUBLIC_PINNED_INSTALL_SH,
        ),
        "CITATION.cff": (f"version: {PUBLIC_VERSION}",),
        "pyproject.toml": (f'version = "{PUBLIC_VERSION}"',),
        ".claude-plugin/plugin.json": (f'"version": "{PUBLIC_VERSION}"',),
        "install.sh": (f'CLAUDE_BLOG_VERSION="{PUBLIC_VERSION}"',),
        "install.ps1": (f'$ClaudeBlogVersion = "{PUBLIC_VERSION}"',),
        "skills/blog/SKILL.md": (f'version: "{PUBLIC_VERSION}"',),
    }
    for relative, expected_fragments in version_fragments.items():
        text = contents.get(relative, "")
        for expected in expected_fragments:
            if expected not in text:
                errors.append(
                    {
                        "kind": "invalid_public_release_version",
                        "file": relative,
                        "expected": expected,
                    }
                )

    security = contents.get(".github/SECURITY.md", "")
    security_versions = sorted(set(SECURITY_CHECKOUT_RE.findall(security)))
    if security_versions != [PUBLIC_VERSION]:
        errors.append(
            {
                "kind": "invalid_public_security_version",
                "file": ".github/SECURITY.md",
                "expected": PUBLIC_VERSION,
                "actual": security_versions,
            }
        )

    citation = contents.get("CITATION.cff", "")
    expected_citation_repository = f'repository-code: "{PUBLIC_REPOSITORY}"'
    if expected_citation_repository not in citation:
        errors.append(
            {
                "kind": "invalid_public_citation_repository",
                "file": "CITATION.cff",
                "expected": expected_citation_repository,
            }
        )

    issue_config = contents.get(".github/ISSUE_TEMPLATE/config.yml", "")
    for expected in (
        PUBLIC_DISCUSSIONS,
        PUBLIC_SECURITY_ADVISORY,
        PUBLIC_DOCUMENTATION,
    ):
        if expected not in issue_config:
            errors.append(
                {
                    "kind": "invalid_public_issue_routing",
                    "file": ".github/ISSUE_TEMPLATE/config.yml",
                    "expected": expected,
                }
            )

    expected_installer_urls = {
        "install.sh": PUBLIC_RAW_INSTALL_SH,
        "install.ps1": PUBLIC_RAW_INSTALL_PS1,
    }
    for relative, expected in expected_installer_urls.items():
        text = contents.get(relative, "")
        if expected not in text:
            errors.append(
                {
                    "kind": "missing_exact_public_raw_installer",
                    "file": relative,
                    "expected": expected,
                }
            )
        if "AgriciDaniel/claude-blog" not in text:
            errors.append(
                {
                    "kind": "invalid_public_installer_owner",
                    "file": relative,
                    "expected": "AgriciDaniel/claude-blog",
                }
            )

    for relative, text in contents.items():
        for found in RAW_INSTALLER_RE.findall(text):
            if found not in {
                PUBLIC_RAW_INSTALL_SH,
                PUBLIC_RAW_INSTALL_PS1,
                PUBLIC_PINNED_INSTALL_SH,
            }:
                errors.append(
                    {
                        "kind": "wrong_public_raw_installer_url",
                        "file": relative,
                        "actual": found,
                    }
                )

    pyproject = contents.get("pyproject.toml", "")
    canonical_fields = ("homepage", "repository", "issues", "documentation", "changelog")
    for field in canonical_fields:
        pattern = re.compile(
            rf"^{field}\s*=\s*[\"']{re.escape(PUBLIC_REPOSITORY)}(?:[^\"']*)[\"']",
            re.MULTILINE,
        )
        if not pattern.search(pyproject):
            errors.append(
                {
                    "kind": "invalid_public_canonical",
                    "file": "pyproject.toml",
                    "field": field,
                }
            )

    plugin_text = contents.get(".claude-plugin/plugin.json", "")
    try:
        plugin = json.loads(plugin_text)
    except json.JSONDecodeError:
        errors.append(
            {"kind": "invalid_json", "file": ".claude-plugin/plugin.json"}
        )
    else:
        expected_plugin = {
            "homepage": PUBLIC_REPOSITORY,
            "repository": PUBLIC_REPOSITORY,
        }
        for field, expected in expected_plugin.items():
            if plugin.get(field) != expected:
                errors.append(
                    {
                        "kind": "invalid_public_plugin_ownership",
                        "file": ".claude-plugin/plugin.json",
                        "field": field,
                        "expected": expected,
                    }
                )
        author = plugin.get("author")
        if not isinstance(author, dict) or author.get("name") != PUBLIC_OWNER:
            errors.append(
                {
                    "kind": "invalid_public_plugin_ownership",
                    "file": ".claude-plugin/plugin.json",
                    "field": "author.name",
                    "expected": PUBLIC_OWNER,
                }
            )
        if not isinstance(author, dict) or author.get("url") != PUBLIC_OWNER_URL:
            errors.append(
                {
                    "kind": "invalid_public_plugin_ownership",
                    "file": ".claude-plugin/plugin.json",
                    "field": "author.url",
                    "expected": PUBLIC_OWNER_URL,
                }
            )

    marketplace_text = contents.get(".claude-plugin/marketplace.json", "")
    try:
        marketplace = json.loads(marketplace_text)
    except json.JSONDecodeError:
        errors.append(
            {"kind": "invalid_json", "file": ".claude-plugin/marketplace.json"}
        )
    else:
        owner = marketplace.get("owner")
        plugins = marketplace.get("plugins")
        if marketplace.get("name") != PUBLIC_MARKETPLACE:
            errors.append(
                {
                    "kind": "invalid_public_marketplace_ownership",
                    "file": ".claude-plugin/marketplace.json",
                    "field": "name",
                    "expected": PUBLIC_MARKETPLACE,
                }
            )
        if not isinstance(owner, dict) or owner.get("name") != PUBLIC_OWNER:
            errors.append(
                {
                    "kind": "invalid_public_marketplace_ownership",
                    "file": ".claude-plugin/marketplace.json",
                    "field": "owner.name",
                    "expected": PUBLIC_OWNER,
                }
            )
        if (
            not isinstance(plugins, list)
            or not any(
                isinstance(entry, dict)
                and entry.get("name") == "claude-blog"
                and entry.get("source") == "./"
                for entry in plugins
            )
        ):
            errors.append(
                {
                    "kind": "invalid_public_marketplace_plugin",
                    "file": ".claude-plugin/marketplace.json",
                }
            )

    return {
        "status": "pass" if not errors else "fail",
        "root": str(root),
        "errors": errors,
        "summary": {"errors": len(errors), "surfaces_checked": len(contents)},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a prepared public claude-blog release worktree."
    )
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON.")
    args = parser.parse_args(argv)
    report = validate(args.root)
    print(json.dumps(report, indent=None if args.compact else 2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
