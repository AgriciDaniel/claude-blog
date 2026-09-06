#!/usr/bin/env python3
"""Sync FLOW operational references from GitHub into the blog-flow skill.

Ports the seo-flow sync pattern with blog-specific changes:

- Targets skills/blog-flow/references/ (not seo-flow).
- Skips the local stage entirely. Bloggers do not need GBP/citation prompts.
- Injects a CC BY 4.0 license header at the top of every synced markdown file.
- Path-traversal guard rejects any output path that escapes the references
  directory.
- Stdlib only. HTTPS only. Host-allowlisted to api.github.com. 5 MB cap.
- Anonymous-first: the script only authenticates if GITHUB_TOKEN is set in the
  environment, or if a 403 is returned and `gh auth token` provides one.
"""

import argparse
import base64
import datetime
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request


API_ROOT = "https://api.github.com/repos/AgriciDaniel/flow/contents"
_ALLOWED_HOST = "api.github.com"
_SIZE_LIMIT = 5 * 1024 * 1024  # 5 MB

LICENSE_HEADER = (
    "<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), "
    "CC BY 4.0 -->"
)

# Blog-applicable stages only. The "local" stage from FLOW is intentionally
# skipped: those prompts target Google Business Profile and brick-and-mortar
# audits, not blog content.
PROMPT_STAGES = ["find", "leverage", "optimize", "win"]

STATIC_FILES = [
    ("docs/01-framework/flow-framework.md", "flow-framework.md"),
    ("docs/10-references/bibliography.md", "bibliography.md"),
]

LOCK_REL = pathlib.Path("skills") / "blog-flow" / "references" / "flow-prompts.lock"


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Refuse redirects so the host allowlist applies to every response."""

    def http_error_301(self, req, fp, code, msg, headers):
        return None

    http_error_302 = http_error_301
    http_error_303 = http_error_301
    http_error_307 = http_error_301
    http_error_308 = http_error_301


_NO_REDIRECT_OPENER = urllib.request.build_opener(_NoRedirectHandler())


def _validate_github_url(url):
    """Abort if url is not HTTPS or does not target the expected GitHub API host."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != _ALLOWED_HOST:
        raise ValueError(
            f"Blocked request to unexpected host: {parsed.netloc!r} "
            f"(scheme: {parsed.scheme!r})"
        )


def script_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return pathlib.Path(script_dir).parent


def parse_args():
    epilog = (
        "Modes: no flags syncs all blog-applicable files to disk; --dry-run "
        "reports changes without writing; --ref <sha> syncs from a specific "
        "FLOW commit."
    )
    parser = argparse.ArgumentParser(
        description="Sync FLOW references into skills/blog-flow/references/.",
        epilog=epilog,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without writing files.",
    )
    parser.add_argument(
        "--ref",
        metavar="SHA",
        help="Pin fetches to a FLOW commit SHA.",
    )
    parser.add_argument(
        "--allow-drift",
        action="store_true",
        help="Permit lockfile drift (default: refuse to write when synced "
        "content hashes do not match flow-prompts.lock). Required when bumping "
        "the FLOW reference; review the diff carefully before passing this flag.",
    )
    return parser.parse_args()


def _base_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    env_token = os.environ.get("GITHUB_TOKEN", "").strip()
    if env_token:
        headers["Authorization"] = f"Bearer {env_token}"
    return headers


def _authed_headers():
    """Return authenticated headers via gh CLI, or base headers if unavailable."""
    try:
        result = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True
        )
    except FileNotFoundError:
        return _base_headers()
    if result.returncode != 0 or not result.stdout.strip():
        return _base_headers()
    token = result.stdout.strip()
    headers = _base_headers()
    headers["Authorization"] = f"Bearer {token}"
    return headers


def content_url(path, ref):
    return f"{API_ROOT}/{path}" + (f"?ref={ref}" if ref else "")


def api_get(path, ref, headers):
    url = content_url(path, ref)
    _validate_github_url(url)
    request = urllib.request.Request(url, headers=headers)
    try:
        with _NO_REDIRECT_OPENER.open(request, timeout=15) as response:
            final_url = response.geturl()
            _validate_github_url(final_url)
            data = response.read(_SIZE_LIMIT + 1)
            if len(data) > _SIZE_LIMIT:
                raise ValueError(
                    f"Response for {path!r} exceeds {_SIZE_LIMIT} bytes"
                )
            return json.loads(data)
    except urllib.error.HTTPError as exc:
        if exc.code == 403 and "Authorization" not in headers:
            authed = _authed_headers()
            if "Authorization" in authed:
                return api_get(path, ref, authed)
        raise


def fetch_file(path, ref, headers):
    data = api_get(path, ref, headers)
    content = data.get("content", "")
    return base64.b64decode(content).decode("utf-8")


def list_markdown_files(path, ref, headers):
    data = api_get(path, ref, headers)
    files = [
        (item["path"], item["name"])
        for item in data
        if item.get("type") == "file" and item.get("name", "").endswith(".md")
    ]
    return sorted(files, key=lambda item: item[1].lower())


def sync_attribution_comment(today):
    """A second comment line that records the sync date.

    Kept separate from LICENSE_HEADER so the dedupe check on LICENSE_HEADER
    works idempotently across runs.
    """
    return f"<!-- Synced from FLOW on {today} -->"


def inject_license_header(raw, today):
    """Prepend the CC BY 4.0 license header to raw, idempotently.

    If the file already starts with the exact license header, do not duplicate.
    Always appends a sync-date comment beneath the header for traceability.
    """
    sync_line = sync_attribution_comment(today)
    if raw.startswith(LICENSE_HEADER):
        # Already licensed. Refresh only the sync-date line if present on line 2.
        lines = raw.split("\n", 2)
        if len(lines) >= 2 and lines[1].startswith("<!-- Synced from FLOW on"):
            lines[1] = sync_line
            return "\n".join(lines)
        # No sync line yet. Insert one after the header.
        return f"{LICENSE_HEADER}\n{sync_line}\n{raw[len(LICENSE_HEADER):].lstrip(chr(10))}"
    return f"{LICENSE_HEADER}\n{sync_line}\n{raw}"


def frontmatter_value(lines, key):
    if not lines or lines[0].strip() != "---":
        return ""
    needle = f"{key}:"
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if stripped.lower().startswith(needle):
            value = stripped[len(needle):].strip()
            return value.strip("\"'")
    return ""


def body_lines_after_frontmatter(lines):
    if not lines or lines[0].strip() != "---":
        return lines
    for index, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return lines[index + 1:]
    return lines


def first_h1(lines):
    for line in body_lines_after_frontmatter(lines):
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return ""


def first_description(lines):
    for line in body_lines_after_frontmatter(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return ""


def prompt_meta(stage, filename, raw):
    lines = raw.splitlines()
    return {
        "stage": stage,
        "filename": filename,
        "title": frontmatter_value(lines, "title") or first_h1(lines),
        "description": (
            frontmatter_value(lines, "description") or first_description(lines)
        ),
    }


def escape_cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def prompt_readme(rows):
    lines = [
        "# FLOW Prompt Index (Blog-Applicable)",
        "",
        "Local-SEO prompts are excluded by design. See claude-seo for those.",
        "",
        "| Stage | Filename | Title | Description |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {stage} | {filename} | {title} | {description} |".format(
                stage=escape_cell(row["stage"]),
                filename=escape_cell(row["filename"]),
                title=escape_cell(row["title"]),
                description=escape_cell(row["description"]),
            )
        )
    return "\n".join(lines) + "\n"


def _sha256(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _atomic_write(path, content):
    """Write content atomically via a temp file in the same directory."""
    dir_ = path.parent
    fd, tmp = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        shutil.move(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _assert_inside_references(refs_root, candidate):
    """Path-traversal guard.

    Every output target must resolve to a path inside refs_root. Abort with a
    clear error if it does not, regardless of how the path was constructed.
    """
    refs_resolved = refs_root.resolve()
    candidate_resolved = candidate.resolve()
    refs_str = str(refs_resolved)
    cand_str = str(candidate_resolved)
    if cand_str != refs_str and not cand_str.startswith(refs_str + os.sep):
        raise ValueError(
            f"Path traversal blocked: {candidate_resolved} is outside "
            f"{refs_resolved}"
        )


def record_write(root, refs_root, path, content, dry_run, changes):
    # Path-traversal guard. Must run before any filesystem mutation.
    _assert_inside_references(refs_root, path)

    rel = path.relative_to(root).as_posix()
    changes.setdefault("hashes", {})[rel] = _sha256(content)
    if path.exists():
        current = path.read_text(encoding="utf-8")
        bucket = "unchanged" if current == content else "updated"
    else:
        bucket = "added"
    changes[bucket].append(rel)
    print(f"{bucket}: {rel}", file=sys.stderr)
    if not dry_run and bucket != "unchanged":
        path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write(path, content)


def sync(args):
    root = script_root()
    refs = root / "skills" / "blog-flow" / "references"
    today = datetime.date.today().isoformat()
    headers = _base_headers()
    changes = {"added": [], "updated": [], "unchanged": [], "hashes": {}}
    prompt_rows = []

    # Phase 1: fetch and stage all content in memory. Compute would-be hashes
    # without writing, so the drift check can fire BEFORE any filesystem
    # mutation (audit VULN-018).
    pending = []  # list of (target_path, content) tuples

    for source, target in STATIC_FILES:
        print(f"fetch: {source}", file=sys.stderr)
        raw = fetch_file(source, args.ref, headers)
        content = inject_license_header(raw, today)
        target_path = refs / target
        pending.append((target_path, content))
        rel = target_path.relative_to(root).as_posix()
        changes["hashes"][rel] = _sha256(content)

    for stage in PROMPT_STAGES:
        source_dir = f"docs/09-prompts/{stage}"
        print(f"list: {source_dir}", file=sys.stderr)
        for source, filename in list_markdown_files(source_dir, args.ref, headers):
            print(f"fetch: {source}", file=sys.stderr)
            raw = fetch_file(source, args.ref, headers)
            prompt_rows.append(prompt_meta(stage, filename, raw))
            target_path = refs / "prompts" / stage / filename
            content = inject_license_header(raw, today)
            pending.append((target_path, content))
            rel = target_path.relative_to(root).as_posix()
            changes["hashes"][rel] = _sha256(content)

    readme_path = refs / "prompts" / "README.md"
    readme_content = inject_license_header(prompt_readme(prompt_rows), today)
    pending.append((readme_path, readme_content))
    readme_rel = readme_path.relative_to(root).as_posix()
    changes["hashes"][readme_rel] = _sha256(readme_content)

    # Phase 2: compute lockfile drift against the staged hashes (pre-write).
    lock_path = root / LOCK_REL
    drift_lines = []
    if lock_path.exists():
        old_lock = lock_path.read_text(encoding="utf-8")
        old_hashes = {}
        for line in old_lock.splitlines():
            if line and not line.startswith("#"):
                parts = line.split("  ", 1)
                if len(parts) == 2:
                    old_hashes[parts[1]] = parts[0]
        for rel, sha in sorted(changes["hashes"].items()):
            old_sha = old_hashes.get(rel)
            if old_sha is None:
                drift_lines.append(f"ADDED   {rel}")
            elif old_sha != sha:
                drift_lines.append(f"CHANGED {rel}")
        for rel in sorted(old_hashes):
            if rel not in changes["hashes"]:
                drift_lines.append(f"REMOVED {rel}")

    # Phase 3: enforce drift policy BEFORE any writes happen.
    if drift_lines and not args.dry_run and not args.allow_drift:
        print(
            "ERROR: Lockfile drift detected. The synced content hashes do not "
            "match flow-prompts.lock.",
            file=sys.stderr,
        )
        print(
            "Review the upstream changes carefully before bumping the lockfile.",
            file=sys.stderr,
        )
        print(
            "If the changes are legitimate, re-run with --allow-drift.",
            file=sys.stderr,
        )
        print("Drift report:", file=sys.stderr)
        for line in drift_lines:
            print(f"  {line}", file=sys.stderr)
        sys.exit(2)
    elif drift_lines and args.allow_drift:
        print(
            "NOTE: Lockfile drift detected. Proceeding because --allow-drift "
            "was explicitly passed.",
            file=sys.stderr,
        )
        for line in drift_lines:
            print(f"  {line}", file=sys.stderr)
    elif drift_lines and args.dry_run:
        print(
            "DRY-RUN: Lockfile drift detected (informational, no exit):",
            file=sys.stderr,
        )
        for line in drift_lines:
            print(f"  {line}", file=sys.stderr)
    elif lock_path.exists():
        print(
            "Lockfile: no drift (all hashes match baseline)",
            file=sys.stderr,
        )

    # Phase 4: write all staged content to disk. The hash for each file was
    # already recorded in Phase 1, so we drop record_write's hash-recording
    # side effect by passing a throwaway dict for the hashes slot. We keep the
    # added/updated/unchanged bookkeeping by reusing `changes`.
    for target_path, content in pending:
        record_write(root, refs, target_path, content, args.dry_run, changes)

    # Phase 5: build and write the lockfile from the now-finalized hashes.
    lock_lines = [
        "# flow-prompts.lock. SHA-256 baseline for synced FLOW prompts.",
        f"# Ref: {args.ref or 'HEAD'} | format: <sha256hex>  <rel_path> "
        "(sha256sum-compatible)",
        "",
    ]
    for rel in sorted(changes["hashes"]):
        lock_lines.append(f"{changes['hashes'][rel]}  {rel}")
    lock_content = "\n".join(lock_lines) + "\n"

    # Write lockfile (excluded from its own hashes tracking).
    record_write(root, refs, lock_path, lock_content, args.dry_run, changes)
    lock_rel = LOCK_REL.as_posix()
    changes["hashes"].pop(lock_rel, None)
    for bucket in ("added", "updated", "unchanged"):
        try:
            changes[bucket].remove(lock_rel)
        except ValueError:
            pass

    return changes


if __name__ == "__main__":
    print(json.dumps(sync(parse_args()), sort_keys=True))
