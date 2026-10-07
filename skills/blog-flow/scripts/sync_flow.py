#!/usr/bin/env python3
"""Sync blog-applicable FLOW prompt files from the upstream GitHub repository.

The script uses only the GitHub contents API over HTTPS. It allowlists
``api.github.com``, rejects redirects, checks resolved IP addresses, caps each
response at 5 MB, writes files atomically, and refuses paths that escape the
``skills/blog-flow/references`` directory.

CLI examples:
  python3 scripts/sync_flow.py
  python3 scripts/sync_flow.py --dry-run
  python3 scripts/sync_flow.py --ref 0123456789abcdef0123456789abcdef01234567
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import ipaddress
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

REPO = "AgriciDaniel/flow"
API_HOST = "api.github.com"
MAX_RESPONSE_BYTES = 5 * 1024 * 1024
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REFERENCES_DIR = SKILL_DIR / "references"
LOCK_FILE = REFERENCES_DIR / "flow-prompts.lock"
LOCK_PREFIX = "skills/blog-flow/references"

SYNC_PATHS = [
    "references/flow-framework.md",
    "references/bibliography.md",
    "references/prompts/README.md",
    "references/prompts/find/content-planning-for-topical-relevance-prompt.md",
    "references/prompts/find/content-prioritization-prompt.md",
    "references/prompts/find/keyword-research-prompt.md",
    "references/prompts/find/keyword-variations-for-topical-relevance-prompt.md",
    "references/prompts/find/prompt-audience-avatar.md",
    "references/prompts/leverage/backlink-competition-prompt.md",
    "references/prompts/optimize/ai-detector-test-follow-up-prompt.md",
    "references/prompts/optimize/ai-supporting-pages-rewrite-prompt.md",
    "references/prompts/optimize/basic-prompt.md",
    "references/prompts/optimize/blog-post-outline-prompt.md",
    "references/prompts/optimize/blog-post-writing-prompt.md",
    "references/prompts/optimize/claude-prompt-1.md",
    "references/prompts/optimize/claude-prompt-2.md",
    "references/prompts/optimize/ctr-audit-prompt.md",
    "references/prompts/optimize/follow-up-prompt-1.md",
    "references/prompts/optimize/follow-up-prompt-2.md",
    "references/prompts/optimize/follow-up-prompt.md",
    "references/prompts/optimize/paa-question-rewording-prompt.md",
    "references/prompts/optimize/prompt-core-30-content-audit.md",
    "references/prompts/optimize/property-content-with-authority-audit-prompt.md",
    "references/prompts/optimize/reddit-claude-prompt.md",
    "references/prompts/optimize/schema-prompt-1.md",
    "references/prompts/optimize/step-1-the-chatgpt-discovery-prompt.md",
    "references/prompts/optimize/step-2-the-follow-up-qualifying-prompt.md",
    "references/prompts/optimize/technical-audit-prompt.md",
    "references/prompts/optimize/visibility-follow-up-prompt.md",
    "references/prompts/optimize/visibility-prompt.md",
    "references/prompts/win/bofu-page-brief-generator.md",
    "references/prompts/win/conversion-audit-prompt.md",
    "references/prompts/win/dual-surface-content-scorecard.md",
]


def resolve_references_dir(references_dir=None, *, require_existing=False):
    """Select a trusted absolute reference root without consulting the CWD.

    Explicit roots must be outside the package. Reference contents remain
    untrusted data and cannot authorize execution, credentials or publication.
    """
    bundled = REFERENCES_DIR
    selected = references_dir if references_dir is not None else os.environ.get("CLAUDE_BLOG_FLOW_REFERENCES_DIR")
    package = SKILL_DIR.parent.parent.resolve()
    if selected is None:
        refs = bundled.resolve()
        if refs != bundled.parent.resolve() / bundled.name:
            raise ValueError("Bundled FLOW references must not traverse a symlink")
    else:
        raw = os.fspath(selected)
        refs = Path(raw)
        if not refs.is_absolute() or ".." in refs.parts or any(token in raw for token in ("$", "{", "}", "%")):
            raise ValueError("FLOW references override must be a caller-resolved absolute path")
        for component in (refs, *refs.parents):
            if component.is_symlink():
                raise ValueError("FLOW references override must not traverse a symlink")
            if component.exists() and not component.is_dir():
                raise ValueError("FLOW references override must name a directory")
        refs = refs.resolve()
        if refs == package or package in refs.parents or refs in package.parents:
            raise ValueError("Persistent FLOW references must be outside the installed package")
    if refs.exists() and not refs.is_dir():
        raise ValueError("FLOW reference root must be a directory")
    if require_existing and not refs.is_dir():
        raise ValueError("Selected FLOW references are missing; sync the configured persistent root first")
    if refs.exists():
        for entry in refs.rglob("*"):
            if entry.is_symlink() and not entry.resolve().is_relative_to(refs):
                raise ValueError("FLOW reference symlink escapes the selected root")
    return refs


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        """Reject redirects so the final host cannot change silently."""
        raise urllib.error.HTTPError(req.full_url, code, "redirect blocked", headers, fp)


def _is_public_ip(host: str) -> bool:
    infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast or ip.is_unspecified:
            return False
    return True


def _validate_api_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("GitHub API URL must use https")
    if parsed.hostname != API_HOST:
        raise ValueError(f"GitHub API host must be {API_HOST}")
    if not _is_public_ip(API_HOST):
        raise ValueError(f"{API_HOST} resolved to a non-public IP")


def _github_token() -> str | None:
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    try:
        result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=5)
    except Exception:
        return None
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return None


def _request_json(url: str, token: str | None = None) -> dict[str, Any]:
    _validate_api_url(url)
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "claude-blog-flow-sync",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    opener = urllib.request.build_opener(NoRedirect)
    with opener.open(request, timeout=20) as response:
        chunks = []
        total = 0
        while True:
            chunk = response.read(65536)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_RESPONSE_BYTES:
                raise ValueError("GitHub API response exceeded 5 MB")
            chunks.append(chunk)
    return json.loads(b"".join(chunks).decode("utf-8"))


def _fetch_content(path: str, ref: str, token: str | None) -> bytes:
    encoded = urllib.parse.quote(path, safe="/")
    query = urllib.parse.urlencode({"ref": ref})
    url = f"https://{API_HOST}/repos/{REPO}/contents/{encoded}?{query}"
    payload = _request_json(url, token=token)
    if payload.get("type") != "file" or payload.get("encoding") != "base64":
        raise ValueError(f"Unexpected GitHub contents response for {path}")
    content = base64.b64decode(payload.get("content", ""), validate=True)
    if len(content) > MAX_RESPONSE_BYTES:
        raise ValueError(f"{path} exceeds 5 MB")
    return content


def _target_for(path: str, references_dir: Path | None = None) -> Path:
    if not path.startswith("references/"):
        raise ValueError(f"Refusing non-reference path: {path}")
    rel = Path(path).relative_to("references")
    if any(part in {"..", ""} for part in rel.parts):
        raise ValueError(f"Unsafe relative path: {path}")
    root = (references_dir if references_dir is not None else REFERENCES_DIR).resolve()
    target = (root / rel).resolve()
    if target != root and root not in target.parents:
        raise ValueError(f"Refusing to write outside references: {target}")
    if target.exists() and target.is_symlink():
        raise ValueError(f"Refusing to overwrite symlink: {target}")
    return target


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _load_lock(lock_path: Path | None = None) -> dict[str, str]:
    lock_path = lock_path if lock_path is not None else LOCK_FILE
    if not lock_path.exists():
        return {}
    entries = {}
    for line in lock_path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, _, rel = line.partition("  ")
        if digest and rel:
            entries[rel] = digest
    return entries


def sync(ref: str, dry_run: bool = False, allow_drift: bool = False, references_dir: str | Path | None = None) -> dict[str, Any]:
    refs = resolve_references_dir(references_dir)
    lock_path = refs / "flow-prompts.lock"
    baseline_lock = lock_path if lock_path.exists() else LOCK_FILE
    token = _github_token()
    summary: dict[str, Any] = {
        "status": "success",
        "repo": REPO,
        "ref": ref,
        "dry_run": dry_run,
        "added": [],
        "updated": [],
        "unchanged": [],
        "lock_drift": [],
        "errors": [],
    }
    lock_exists = baseline_lock.exists()
    lock = _load_lock(baseline_lock)
    new_lock: dict[str, str] = {}
    pending: list[tuple[Path, bytes]] = []

    for path in SYNC_PATHS:
        try:
            content = _fetch_content(path, ref, token)
            rel = str(Path(path).relative_to("references"))
            lock_rel = f"{LOCK_PREFIX}/{rel}"
            target = _target_for(path, refs)
            digest = hashlib.sha256(content).hexdigest()
            new_lock[lock_rel] = digest
            if target.exists() and target.read_bytes() == content:
                summary["unchanged"].append(rel)
                continue
            if target.exists():
                summary["updated"].append(rel)
            else:
                summary["added"].append(rel)
            pending.append((target, content))
        except urllib.error.HTTPError as exc:
            if exc.code == 403 and not token:
                token = _github_token()
                time.sleep(1)
                try:
                    content = _fetch_content(path, ref, token)
                    target = _target_for(path, refs)
                    rel = str(Path(path).relative_to("references"))
                    lock_rel = f"{LOCK_PREFIX}/{rel}"
                    digest = hashlib.sha256(content).hexdigest()
                    new_lock[lock_rel] = digest
                    if target.exists() and target.read_bytes() == content:
                        summary["unchanged"].append(rel)
                    elif target.exists():
                        summary["updated"].append(rel)
                        pending.append((target, content))
                    else:
                        summary["added"].append(rel)
                        pending.append((target, content))
                    continue
                except Exception as retry_exc:
                    summary["errors"].append({"path": path, "error": str(retry_exc)})
            else:
                summary["errors"].append({"path": path, "error": str(exc)})
        except Exception as exc:
            summary["errors"].append({"path": path, "error": str(exc)})

    if lock_exists:
        for lock_rel, digest in sorted(new_lock.items()):
            if lock.get(lock_rel) != digest:
                summary["lock_drift"].append(lock_rel.removeprefix(f"{LOCK_PREFIX}/"))
        for lock_rel in sorted(set(lock) - set(new_lock)):
            summary["lock_drift"].append(lock_rel.removeprefix(f"{LOCK_PREFIX}/"))

    if summary["errors"]:
        summary["status"] = "error"
    elif summary["lock_drift"] and not dry_run and not allow_drift:
        summary["status"] = "error"
        summary["errors"].append({
            "path": str(lock_path),
            "error": (
                "Lockfile drift detected; reviewed references were not changed. "
                "Review the upstream diff, then rerun with --allow-drift to accept it."
            ),
        })
    elif not dry_run:
        # Validate every staged destination before the first write.
        for target, _content in pending:
            if not target.resolve().is_relative_to(refs):
                raise ValueError("FLOW target escaped selected references before writing")
        if not lock_path.resolve().is_relative_to(refs):
            raise ValueError("FLOW lock escaped selected references before writing")
        for target, content in pending:
            _atomic_write(target, content)
        lines = [f"{digest}  {rel}\n" for rel, digest in sorted(new_lock.items())]
        _atomic_write(lock_path, "".join(lines).encode("utf-8"))

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync blog-applicable FLOW prompt files")
    parser.add_argument("--dry-run", action="store_true", help="Report planned changes without writing")
    parser.add_argument("--ref", default="main", help="Branch, tag, or commit SHA to fetch")
    parser.add_argument(
        "--allow-drift",
        action="store_true",
        help="Accept reviewed upstream changes and update flow-prompts.lock",
    )
    parser.add_argument("--references-dir", help="Caller-resolved absolute persistent reference root outside the package")
    parser.add_argument("--resolve-references", action="store_true", help="Print the selected existing reference root without network access or writes")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.resolve_references:
        print(resolve_references_dir(args.references_dir, require_existing=True))
        return 0
    result = sync(args.ref, dry_run=args.dry_run, allow_drift=args.allow_drift, references_dir=args.references_dir)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
