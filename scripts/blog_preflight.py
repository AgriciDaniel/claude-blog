#!/usr/bin/env python3
"""Run the Blog Delivery Contract preflight gates against a draft folder.

Implements Gates 1 through 5 of the Blog Delivery Contract, including
machine verification of the Gate 4 reviewer scorecard.

Output:
  <draft>/preflight-report.json: machine-readable gate results
  <draft>/capabilities.json: emitted by Gate 1, consumed by 2-5
  <draft>/preview/*.png: emitted by Gate 3 (if patchright installed)

Usage:
    python3 scripts/blog_preflight.py --draft <dir> [--gate N] [--strict] [--json]

  --gate N    Run only the named gate (1-5). Default: all 5 sequentially.
  --strict    Exit 1 if any gate blocks. Default: on. Use --no-strict to
              proceed regardless (logs the bypass loudly).
  --json      Emit the report JSON to stdout in addition to the file.

Exit codes: 0 = all gates passed; 1 = at least one gate blocked
(when --strict); 2 = repair iteration cap exceeded. Warnings never block.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import ipaddress
import importlib.util
import json
import os
import re
import shutil
import socket
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Optional


def _project_version() -> str:
    """Read the package version from pyproject.toml."""
    try:
        text = (Path(__file__).resolve().parent.parent / "pyproject.toml").read_text(encoding="utf-8")
    except OSError:
        return "0.0.0"
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return match.group(1) if match else "0.0.0"


CONTRACT_REF = "skills/blog/references/blog-delivery-contract.md"
REQUIRED_AGENTS = ("blog-reviewer",)
OPTIONAL_AGENTS = ("blog-researcher", "blog-writer", "blog-seo", "blog-translator")
REQUIRED_SCRIPTS = ("scripts/lint_prose.py", "scripts/load_untrusted_root.py", "scripts/analyze_blog.py")
VIEWPORTS = [
    {"name": "mobile", "width": 375, "height": 812},
    {"name": "tablet", "width": 768, "height": 1024},
    {"name": "desktop", "width": 1280, "height": 800},
]
CONTRACT_VERSION = _project_version()
HEAD_TIMEOUT = 10
USER_AGENT = f"claude-blog/{CONTRACT_VERSION} preflight (+https://github.com/AgriciDaniel/claude-blog)"
EXTERNAL_LINKS_ALLOWED_FILE = "external-links.allowed"
ALLOWED_HTTP_SCHEMES = frozenset({"http", "https"})
GOOGLEBOT_HTML_BYTE_LIMIT = 2 * 1024 * 1024
INLINE_BLOAT_WARNING_BYTES = 256 * 1024
PREFLIGHT_TARGETS_FILE = "preflight-targets.json"
LEGACY_ALLOWLIST_FILE = "preflight-allowlist.json"

# VULN-802 code-enforced iteration counter (v1.9.1).
# The contract documents "up to 3 retries before escalating." v1.9.0
# enforced this only as orchestrator prose; any draft-controlled text
# could convince the orchestrator the counter was at 0. v1.9.1 backs the
# claim with a file on disk that survives across preflight invocations.
ITERATION_COUNTER_FILE = ".iteration-count"
MAX_ITERATIONS = 3
EXIT_ITERATION_CAP = 2

# VULN-803 nonce-bound review.md provenance.
# Gate 4 used to trust any writer of <draft>/review.md. The verifier state is
# now outside the draft folder, keyed by the resolved draft path, so an agent
# with draft read/write cannot copy the nonce from the draft into a forged
# review. The orchestrator prints the nonce into the reviewer prompt.
REVIEW_STATE_ENV = "CLAUDE_BLOG_REVIEW_STATE_DIR"
REVIEW_STATE_DIR = Path.home() / ".cache" / "claude-blog" / "review-nonces"
NONCE_PATTERN = re.compile(r"^Nonce:\s*([0-9a-f]{32})\s*$", re.MULTILINE | re.IGNORECASE)
BLOCKING_PATTERN = re.compile(r"^BLOCKING:\s*(true|false)\s*(?:\((.*?)\))?\s*$", re.IGNORECASE)


def _review_state_path(draft: Path) -> Path:
    """Return the external verifier-state path for a draft."""
    state_root = Path(os.environ.get(REVIEW_STATE_ENV, str(REVIEW_STATE_DIR))).expanduser()
    digest = hashlib.sha256(str(draft.resolve()).encode("utf-8")).hexdigest()
    return state_root / f"{digest}.json"


def _reject_symlink_output(path: Path) -> None:
    if path.is_symlink():
        raise ValueError(f"refusing to overwrite symlink: {path}")


def _read_text_no_follow(path: Path) -> str:
    """Read text without following a symlink at the final path."""
    if path.is_symlink():
        raise ValueError(f"refusing to read symlink: {path}")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags)
    try:
        with os.fdopen(fd, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        raise


def _read_bytes_no_follow(path: Path) -> bytes:
    """Read bytes without following a symlink at the final path."""
    if path.is_symlink():
        raise ValueError(f"refusing to read symlink: {path}")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags)
    try:
        with os.fdopen(fd, "rb") as f:
            return f.read()
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        raise


def _atomic_write_json(
    path: Path,
    data: dict[str, Any],
    *,
    indent: int | None = None,
    sort_keys: bool = False,
    private: bool = False,
) -> None:
    """Atomic JSON write that refuses symlink output paths."""
    _reject_symlink_output(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if private:
        try:
            os.chmod(path.parent, 0o700)
        except OSError:
            pass
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, sort_keys=sort_keys)
            f.write("\n")
        os.replace(tmp, path)
        if private:
            try:
                os.chmod(path, 0o600)
            except OSError:
                pass
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    """Atomic bytes write that refuses symlink output paths."""
    _reject_symlink_output(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _read_expected_review_nonce(draft: Path) -> tuple[str | None, str | None]:
    """Read the nonce from external verifier state."""
    path = _review_state_path(draft)
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except FileNotFoundError:
        return None, f"review verifier state missing at {path}; run --init-review-nonce before dispatching blog-reviewer"
    except (OSError, json.JSONDecodeError) as e:
        return None, f"review verifier state unreadable at {path}: {e}"
    nonce = str(data.get("nonce", "")).strip().lower()
    if not re.fullmatch(r"[0-9a-f]{32}", nonce):
        return None, f"review verifier state at {path} does not contain a valid 32-hex nonce"
    return nonce, None


DIGEST_SUFFIXES = frozenset({".md", ".html", ".pdf", ".png", ".jpg", ".jpeg", ".webp"})


def _draft_digest(draft: Path) -> str:
    """Hash the deliverable artifacts a review judges (not review.md or reports)."""
    digest = hashlib.sha256()
    for path in sorted(draft.iterdir()):
        if (path.name == "review.md" or path.name.startswith(".")
                or path.suffix.lower() not in DIGEST_SUFFIXES
                or path.is_symlink() or not path.is_file()):
            continue
        try:
            content = hashlib.sha256(path.read_bytes()).digest()
        except OSError:
            continue
        digest.update(path.name.encode("utf-8") + b"\0" + content)
    return digest.hexdigest()


def _artifact_digests(draft: Path) -> dict[str, str]:
    """Return {file name: sha256 hex} for each deliverable a review judges.

    Same file selection as ``_draft_digest`` (top-level md, html, pdf and hero
    images; never review.md, dotfiles or symlinks), kept per file so Gate 4 can
    name which artifact changed.
    """
    digests: dict[str, str] = {}
    for path in sorted(draft.iterdir()):
        if (path.name == "review.md" or path.name.startswith(".")
                or path.suffix.lower() not in DIGEST_SUFFIXES
                or path.is_symlink() or not path.is_file()):
            continue
        try:
            digests[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            continue
    return digests


STALE_REVIEW_FIX = "re-render, re-init the nonce and re-review"


def _review_staleness(draft: Path) -> tuple[list[str], list[str], list[str]]:
    """Compare the draft with the digests stored by --init-review-nonce.

    Returns (violations, warnings, stale file names). State written with
    per-file ``artifact_digests`` makes any changed or removed artifact a
    violation: the review judged a different draft. Older state that carries
    only the aggregate ``draft_digest`` is not checked per file and keeps the
    advisory warning, and state with neither field is not checked at all.
    """
    try:
        data = json.loads(_review_state_path(draft).read_text(encoding="utf-8"))
        recorded = data.get("artifact_digests")
        aggregate = data.get("draft_digest")
        if isinstance(recorded, dict):
            current = _artifact_digests(draft)
            violations: list[str] = []
            stale: list[str] = []
            for name in sorted(recorded):
                if name not in current:
                    violations.append(
                        f"draft changed after the review nonce was issued: {name} (file removed); {STALE_REVIEW_FIX}"
                    )
                    stale.append(name)
                elif current[name] != recorded[name]:
                    violations.append(
                        f"draft changed after the review nonce was issued: {name}; {STALE_REVIEW_FIX}"
                    )
                    stale.append(name)
            added = sorted(set(current) - set(recorded))
            warnings = [
                f"artifact file added after the review nonce was issued: {name}; it was not part of the review"
                for name in added
            ]
            return violations, warnings, stale
        if isinstance(aggregate, str) and aggregate != _draft_digest(draft):
            return [], [
                "draft artifacts changed after --init-review-nonce; this review may be stale. "
                "Re-run --init-review-nonce and dispatch a fresh blog-reviewer"
            ], []
    except (OSError, ValueError, AttributeError):
        pass
    return [], [], []


def _review_staleness_warning(draft: Path) -> list[str]:
    """Advisory staleness warnings only (kept for callers of the old helper)."""
    return _review_staleness(draft)[1]


def _init_review_nonce(draft: Path) -> str:
    """Generate a CSPRNG nonce and store verifier state outside the draft.

    The state keeps the aggregate ``draft_digest`` older readers know and adds
    ``artifact_digests`` (sha256 per md, html, pdf and hero file) so Gate 4 can
    refuse a review that no longer matches the artifacts it judged.
    """
    import secrets
    nonce = secrets.token_hex(16)
    _atomic_write_json(
        _review_state_path(draft),
        {
            "draft": str(draft.resolve()),
            "nonce": nonce,
            "draft_digest": _draft_digest(draft),
            "artifact_digests": _artifact_digests(draft),
            "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "version": CONTRACT_VERSION,
        },
        private=True,
        sort_keys=True,
    )
    return nonce


def _iteration_check(draft: Path, reset: bool = False, increment: bool = False) -> int:
    """Read or increment the per-draft repair counter; refuse past cap.

    Behavior:
      * reset=True: counter is set to 0.
      * increment=False: no counter mutation after any reset.
      * increment=True, counter absent or corrupt: counter is set to 1.
      * increment=True, counter at MAX_ITERATIONS: emit stderr message and
        return EXIT_ITERATION_CAP. Caller should sys.exit(2).
      * Otherwise with increment=True: counter += 1; return 0.

    Fail-soft on corrupt counter file: a non-integer value resets to 1
    rather than refusing to run (an attacker who can write to the draft
    folder has bigger problems; refusing on garbage would be a self-DoS).
    """
    counter_path = draft / ITERATION_COUNTER_FILE
    if reset:
        _atomic_write_counter(counter_path, 0)
    if not increment:
        return 0
    try:
        raw = counter_path.read_text(encoding="utf-8").strip()
        current = int(raw)
    except (FileNotFoundError, ValueError, OSError):
        current = 0
    if current >= MAX_ITERATIONS:
        sys.stderr.write(
            f"ITERATION CAP EXCEEDED: this draft has used all {MAX_ITERATIONS} "
            f"preflight iterations. Escalate to the user, or run with "
            f"--reset-iterations after a code change.\n"
        )
        return EXIT_ITERATION_CAP
    _atomic_write_counter(counter_path, current + 1)
    return 0


def _atomic_write_counter(path: Path, value: int) -> None:
    """Atomic write of the integer counter (mkstemp + os.replace)."""
    import tempfile
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(f"{int(value)}\n")
        os.replace(tmp, str(path))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _gate_result(gate: int, name: str, passed: bool, violations: Optional[list] = None, warnings: Optional[list] = None, **kwargs: Any) -> dict:
    return {
        "gate": gate,
        "name": name,
        "passed": passed,
        "violations": violations or [],
        "warnings": warnings or [],
        **kwargs,
    }


def _has_module(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        # ``find_spec("parent.child")`` raises ImportError when the parent is
        # unavailable and can raise ValueError when an already-imported module
        # has ``__spec__ = None``. Optional capability discovery must degrade
        # to ``False`` for both cases rather than aborting the preflight.
        return False


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _parse_tool_names(raw: str | None) -> list[str]:
    """Parse live tool names passed by the orchestrator."""
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, list):
        return [str(item) for item in parsed]
    if isinstance(parsed, dict):
        tools = parsed.get("tools") or parsed.get("available_tools") or parsed.get("mcp")
        if isinstance(tools, list):
            return [str(item) for item in tools]
    return []


def _select_artifact_stem(draft_dir: Path, slug: str | None = None) -> tuple[str | None, dict[str, list[Path]], list[str]]:
    """Select one slug-matched .md/.html/.pdf artifact set."""
    mds = [p for p in draft_dir.glob("*.md") if p.name != "review.md"]
    htmls = list(draft_dir.glob("*.html"))
    pdfs = list(draft_dir.glob("*.pdf"))
    groups = {"md": mds, "html": htmls, "pdf": pdfs}
    violations: list[str] = []

    if slug:
        stem = slug
        selected = {kind: [p for p in paths if p.stem == stem] for kind, paths in groups.items()}
    else:
        common = set(p.stem for p in mds) & set(p.stem for p in htmls) & set(p.stem for p in pdfs)
        if len(common) != 1:
            if not common:
                found = "; ".join(
                    f"{kind}: {sorted(p.stem for p in paths) or 'none'}" for kind, paths in groups.items()
                )
                violations.append(
                    "no slug-matched .md/.html/.pdf artifact set found "
                    f"(stems found, {found}). The .md, .html and .pdf must share one stem: rename the files, "
                    "or set `slug:` in the .md frontmatter and re-run scripts/blog_render.py "
                    "(without a `slug` it names the outputs after the .md file stem)"
                )
            else:
                violations.append(f"multiple slug-matched artifact sets found: {sorted(common)}; pass --slug")
            stem = None
            selected = groups
        else:
            stem = next(iter(common))
            selected = {kind: [p for p in paths if p.stem == stem] for kind, paths in groups.items()}

    if stem is not None:
        for kind, paths in selected.items():
            if len(paths) != 1:
                violations.append(f"expected exactly one {stem}.{kind}, found {len(paths)}")
            for path in paths:
                if path.is_symlink():
                    violations.append(f"{path.name} is a symlink artifact")
    return stem, selected, violations


def _safe_local_path(root: Path, ref: str) -> tuple[Path | None, str | None]:
    """Resolve a local URL/path under root, refusing absolute paths and symlinks."""
    try:
        parsed = urllib.parse.urlparse(ref)
    except ValueError as e:
        return None, f"unparseable local path: {ref} ({e})"
    if parsed.scheme or parsed.netloc:
        return None, f"not a local path: {ref}"
    raw_path = urllib.parse.unquote(parsed.path)
    if not raw_path or raw_path.startswith("/"):
        return None, f"local path must be relative to draft: {ref}"
    candidate = root / raw_path
    if candidate.is_symlink():
        return None, f"local path is a symlink: {ref}"
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root.resolve())
    except ValueError:
        return None, f"local path escapes draft folder: {ref}"
    return resolved, None


def _normalize_external_url(url: str) -> str:
    """Normalize an external URL for exact exception matching."""
    parsed = urllib.parse.urlsplit(url.strip())
    return urllib.parse.urlunsplit(
        (parsed.scheme.lower(), parsed.netloc.lower(), parsed.path or "/", parsed.query, "")
    )


def _load_external_link_exceptions(draft_dir: Path) -> tuple[set[str], list[str]]:
    """Load exact URLs allowed to return 403/405 from a project config.

    ``external-links.allowed`` is line-oriented. Blank lines and lines that
    start with ``#`` are ignored. Entries are exact http(s) URLs, with URL
    fragments ignored for matching. The file never bypasses URL/DNS safety or
    redirect validation; it only permits a 403/405 status after those checks.
    """
    config_path = draft_dir / EXTERNAL_LINKS_ALLOWED_FILE
    if not config_path.exists():
        return set(), []
    if config_path.is_symlink():
        return set(), [f"{EXTERNAL_LINKS_ALLOWED_FILE} must not be a symlink"]
    try:
        raw = _read_text_no_follow(config_path)
    except (OSError, ValueError) as exc:
        return set(), [f"{EXTERNAL_LINKS_ALLOWED_FILE} unreadable: {exc}"]

    allowed: set[str] = set()
    violations: list[str] = []
    for line_number, raw_line in enumerate(raw.splitlines(), start=1):
        entry = raw_line.strip()
        if not entry or entry.startswith("#"):
            continue
        ok, reason = _well_formed_http_url(entry)
        if not ok:
            violations.append(
                f"{EXTERNAL_LINKS_ALLOWED_FILE} line {line_number} invalid: {reason}"
            )
            continue
        allowed.add(_normalize_external_url(entry))
    return allowed, violations


def _resolve_public_http_url(url: str) -> tuple[bool, str | None, str | None, int | None, list[Any]]:
    """Validate URL scheme and resolved addresses before a fetch."""
    try:
        parsed = urllib.parse.urlparse(url)
    except ValueError as e:
        return False, f"URL unparseable: {e}", None, None, []
    if parsed.scheme not in ALLOWED_HTTP_SCHEMES:
        return False, "URL scheme must be http or https", None, None, []
    host = parsed.hostname
    if not host:
        return False, "URL host missing", None, None, []
    try:
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
    except ValueError as e:
        # urlparse defers port validation: "http://x:abc/" raises only here.
        return False, f"URL port invalid: {e}", None, None, []
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as e:
        return False, f"DNS resolution failed: {e}", None, None, []
    except OSError as e:
        return False, f"DNS resolution failed: {e}", None, None, []
    if not infos:
        return False, "DNS resolution returned no addresses", None, None, []
    for info in infos:
        addr_text = info[4][0]
        try:
            addr = ipaddress.ip_address(addr_text)
        except ValueError:
            return False, f"invalid resolved address: {addr_text}", None, None, []
        if not addr.is_global or addr.is_loopback or addr.is_link_local or addr.is_multicast or addr.is_unspecified:
            return False, f"resolved address is not public: {addr}", None, None, []
    return True, None, host.lower().rstrip("."), port, list(infos)


def _safe_http_url(url: str) -> tuple[bool, str | None]:
    """Validate URL scheme and every resolved address before fetch."""
    ok, reason, _host, _port, _infos = _resolve_public_http_url(url)
    return ok, reason


class _PinnedDNS:
    """Temporarily pin a host to the addresses already validated."""

    def __init__(self, host: str, port: int, infos: list[Any]):
        self.host = host.lower().rstrip(".")
        self.port = port
        self.infos = list(infos)
        self.original_getaddrinfo = socket.getaddrinfo

    def __enter__(self):
        def pinned_getaddrinfo(host, port, *args, **kwargs):
            normalized = str(host).lower().rstrip(".")
            try:
                requested_port = int(port)
            except (TypeError, ValueError):
                requested_port = port
            if normalized == self.host and requested_port == self.port:
                return list(self.infos)
            return self.original_getaddrinfo(host, port, *args, **kwargs)

        socket.getaddrinfo = pinned_getaddrinfo
        return self

    def __exit__(self, exc_type, exc, tb):
        socket.getaddrinfo = self.original_getaddrinfo
        return False


def _well_formed_http_url(url: str) -> tuple[bool, str | None]:
    try:
        parsed = urllib.parse.urlparse(url)
    except ValueError as e:
        return False, f"URL unparseable: {e}"
    if parsed.scheme not in ALLOWED_HTTP_SCHEMES:
        return False, "URL scheme must be http or https"
    if not parsed.hostname:
        return False, "URL host missing"
    try:
        parsed.port
    except ValueError as e:
        return False, f"URL port invalid: {e}"
    return True, None


def gate_1_capability_discovery(draft_dir: Path, live_tools: list[str] | None = None) -> dict:
    """Enumerate available capabilities; write capabilities.json."""
    root = _project_root()
    live_tools = live_tools or []
    env_keys = {
        "GOOGLE_AI_API_KEY": bool(os.environ.get("GOOGLE_AI_API_KEY")),
        "UNSPLASH_ACCESS_KEY": bool(os.environ.get("UNSPLASH_ACCESS_KEY")),
        "PEXELS_API_KEY": bool(os.environ.get("PEXELS_API_KEY")),
        "PIXABAY_API_KEY": bool(os.environ.get("PIXABAY_API_KEY")),
    }
    py_deps = {
        "patchright": _has_module("patchright"),
        "playwright": _has_module("playwright"),
        "weasyprint": _has_module("weasyprint"),
        "google.genai": _has_module("google.genai") or _has_module("google_genai"),
        "requests": _has_module("requests"),
        "markdown": _has_module("markdown"),
    }
    project_files = {
        "BRAND.md": (root / "BRAND.md").is_file(),
        "VOICE.md": (root / "VOICE.md").is_file(),
        "DISCOURSE.md": (root / "DISCOURSE.md").is_file(),
    }
    agents = {a: (root / "agents" / f"{a}.md").is_file() for a in REQUIRED_AGENTS + OPTIONAL_AGENTS}
    scripts = {s: (root / s).is_file() for s in REQUIRED_SCRIPTS}

    configured_image_paths = (
        any("nanobanana" in tool.lower() or "banana" in tool.lower() for tool in live_tools)
        or env_keys["GOOGLE_AI_API_KEY"]
        or env_keys["UNSPLASH_ACCESS_KEY"]
        or env_keys["PEXELS_API_KEY"]
        or env_keys["PIXABAY_API_KEY"]
    )
    # Openverse is the no-key fallback at the bottom of the ladder. We do NOT
    # probe its reachability here (network HEAD at gate-1 time is too slow
    # and flaky); we report it as best-effort and let generate_hero.py
    # surface a runtime failure if Openverse is unreachable when invoked.
    openverse_assumed_available = True            # best-effort fallback
    image_gen_available = configured_image_paths or openverse_assumed_available

    capabilities = {
        "live_tools": live_tools,
        "live_tools_source": "orchestrator" if live_tools else "not-provided",
        "env_keys_present": env_keys,
        "python_deps": py_deps,
        "project_root_files": project_files,
        "agents": agents,
        "scripts": scripts,
        "image_gen_path_available": image_gen_available,
        "openverse_assumed_available": openverse_assumed_available,
    }
    try:
        _atomic_write_json(draft_dir / "capabilities.json", capabilities, indent=2)
    except (OSError, ValueError) as e:
        return _gate_result(1, "Capability Discovery", False, [f"capabilities.json write refused: {e}"])

    violations = []
    warnings = []
    if not agents.get("blog-reviewer", False):
        violations.append("blog-reviewer agent missing; cannot enforce Gate 4")
    if not live_tools:
        warnings.append("live tool availability not provided; MCP image tools cannot be verified from declarations")
    if not image_gen_available:
        violations.append("no image-gen path available: no live Banana MCP, API key, stock key, or Openverse fallback")
    if not py_deps["patchright"] and not py_deps["playwright"]:
        warnings.append("neither patchright nor playwright installed; strict Gate 3 will block delivery")
    if not py_deps["weasyprint"] and not py_deps["patchright"] and not py_deps["playwright"]:
        warnings.append("no PDF backend installed (patchright/playwright/weasyprint); PDF generation will fail")

    return _gate_result(1, "Capability Discovery", not violations, violations, warnings, capabilities=capabilities)


# --- Static artifact checks (Gate 2 and Gate 5) -----------------------------
# Every scan below is a single linear pass (html.parser, str.find, or a
# pattern with no nested quantifiers) so a hostile draft cannot stall it.

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLACEHOLDER_PATTERN = re.compile(r"\[(?:INTERNAL-LINK|IMAGE|CHART)\b", re.IGNORECASE)
HERO_SUFFIXES = frozenset({".png", ".jpg", ".jpeg", ".webp"})
# The delivery contract states a 1200x630 hero and names no tolerance, so those
# are the minimum dimensions.
HERO_MIN_WIDTH = 1200
HERO_MIN_HEIGHT = 630
SOURCE_HASH_META = "blog-source-sha256"
BODY_HASH_META = "blog-body-sha256"
BODY_START_MARKER = b"<!--bs-body:start-->"
BODY_END_MARKER = b"<!--bs-body:end-->"
GENERATED_LINK_ATTR = "data-bs-generated"
RENDERER_FRONTMATTER_HINT = (
    "The renderer reads these frontmatter keys: title, description, date, author (required); "
    "slug, canonical, site_name, lang, og_image_alt, kicker, tags (optional)"
)
CANONICAL_FIX = (
    "add `canonical: https://your-site.example/blog/<slug>/` to the .md frontmatter and re-run "
    "scripts/blog_render.py (that key also supplies og:url, the og:image and schema image URLs, the default "
    "site_name and the footer link). " + RENDERER_FRONTMATTER_HINT
)
REPORT_LIMIT = 5
DESCRIPTION_RANGE = (70, 165)
ACTIVE_TAGS = frozenset({"iframe", "object", "embed", "frame", "frameset", "applet"})
URL_ATTRIBUTES = frozenset({"href", "src", "action", "formaction", "xlink:href", "data", "poster", "background"})
SVG_ANIMATION_VALUE_ATTRIBUTES = frozenset({"to", "from", "values"})
EVENT_HANDLER_ATTRIBUTE = re.compile(r"on[a-z]+")


def _limited(items: list[str], noun: str) -> list[str]:
    """Keep the first REPORT_LIMIT messages and summarize the rest."""
    if len(items) <= REPORT_LIMIT:
        return items
    return items[:REPORT_LIMIT] + [f"... and {len(items) - REPORT_LIMIT} more {noun}"]


def _snippet(value: Any, limit: int = 60) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _element_label(tag: str, attrs: dict[str, Any]) -> str:
    """Name an element as tag plus a short selector, for violation messages."""
    label = tag
    if attrs.get("id"):
        label += "#" + _snippet(attrs["id"], 30)
    elif attrs.get("class"):
        label += "." + ".".join(_snippet(attrs["class"], 40).split()[:2])
    return f"<{label}>"


def _safe_read_bytes(path: Path) -> bytes | None:
    try:
        return _read_bytes_no_follow(path)
    except (OSError, ValueError):
        return None


def _slugify(name: str) -> str:
    stem, dot, suffix = name.rpartition(".")
    if not dot:
        stem, suffix = name, ""
    slug = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-") or "post"
    return slug + (("." + suffix.lower()) if suffix else "")


def _placeholder_hits(text: str, limit: int = 50) -> list[tuple[int, str]]:
    """Return (line number, marker text) for draft-only markers, in order."""
    hits: list[tuple[int, str]] = []
    for match in PLACEHOLDER_PATTERN.finditer(text):
        close = text.find("]", match.start(), match.start() + 80)
        end = close + 1 if close >= 0 else match.start() + 60
        hits.append((text.count("\n", 0, match.start()) + 1, _snippet(text[match.start():end])))
        if len(hits) >= limit:
            break
    return hits


class _DocumentAudit(HTMLParser):
    """One pass over an HTML artifact: document structure plus active content."""

    def __init__(self) -> None:
        super().__init__()
        self.has_html = False
        self.lang = ""
        self.title: list[str] = []
        self.title_seen = False
        self._in_title = False
        self.descriptions: list[str] = []
        self.named_meta: dict[str, str] = {}
        self.og: dict[str, str] = {}
        self.noindex: list[str] = []
        self.headings: list[tuple[int, str]] = []
        self._heading_level = 0
        self._heading_text: list[str] = []
        self.imgs: list[dict[str, str | None]] = []
        self.active: list[str] = []
        self._svg_stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs_map = {name: value for name, value in attrs}
        in_svg = bool(self._svg_stack)
        if tag == "svg":
            self._svg_stack.append(_element_label(tag, attrs_map))
        self._collect_structure(tag, attrs_map)
        self._collect_active(tag, attrs_map, in_svg or tag == "svg")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == "svg" and self._svg_stack:
            self._svg_stack.pop()
        elif tag == "title":
            self._in_title = False
        elif self._heading_level and tag == f"h{self._heading_level}":
            self.headings.append((self._heading_level, _snippet("".join(self._heading_text), 50)))
            self._heading_level = 0

    def handle_data(self, data):
        if self._in_title:
            self.title.append(data)
        if self._heading_level:
            self._heading_text.append(data)

    def _collect_structure(self, tag, attrs):
        if tag == "html":
            self.has_html = True
            self.lang = (attrs.get("lang") or "").strip()
        elif tag == "title" and not self.title_seen:
            self.title_seen = True
            self._in_title = True
        elif tag == "meta":
            name = (attrs.get("name") or "").strip().lower()
            prop = (attrs.get("property") or "").strip().lower()
            content = attrs.get("content") or ""
            if name and name not in self.named_meta:
                self.named_meta[name] = content
            if name == "description":
                self.descriptions.append(content)
            elif prop.startswith("og:") and prop not in self.og:
                self.og[prop] = content
            elif name in {"robots", "googlebot"}:
                tokens = {t.strip() for t in re.split(r"[,\s]+", content.lower()) if t.strip()}
                if tokens & {"noindex", "none"}:
                    self.noindex.append(f'<meta name="{name}" content="{_snippet(content, 50)}">')
        elif re.fullmatch(r"h[1-6]", tag):
            self._heading_level = int(tag[1])
            self._heading_text = []
        elif tag == "img":
            self.imgs.append({
                "src": attrs.get("src"), "alt": attrs.get("alt"),
                "role": attrs.get("role"), "aria-hidden": attrs.get("aria-hidden"),
                "label": _element_label("img", attrs),
            })

    def _collect_active(self, tag, attrs, in_svg):
        where = f" inside inline SVG {self._svg_stack[-1]}" if in_svg and self._svg_stack else ""
        label = _element_label(tag, attrs)
        if tag == "script":
            kind = (attrs.get("type") or "").strip().lower()
            if kind != "application/ld+json":
                source = f' src="{_snippet(attrs.get("src"), 40)}"' if attrs.get("src") else ""
                self.active.append(
                    f"<script{source}> element{where}; remove it (the only script allowed is "
                    f'type="application/ld+json")'
                )
        elif tag in ACTIVE_TAGS:
            source = attrs.get("src") or attrs.get("data") or ""
            shown = f' src="{_snippet(source, 40)}"' if source else ""
            self.active.append(
                f"<{tag}{shown}> element{where}; remove it (iframe, object, embed and frame are not allowed)"
            )
        for name, value in attrs.items():
            lowered = name.lower()
            if EVENT_HANDLER_ATTRIBUTE.fullmatch(lowered):
                self.active.append(
                    f'inline event handler {lowered}="{_snippet(value, 40)}" on {label}{where}; '
                    "remove the attribute"
                )
            elif lowered in URL_ATTRIBUTES or (in_svg and lowered in SVG_ANIMATION_VALUE_ATTRIBUTES):
                compact = re.sub(r"[\x00-\x20]+", "", value or "").lower()
                if compact.startswith(("javascript:", "vbscript:")):
                    self.active.append(
                        f'{compact.split(":", 1)[0]}: URL in {lowered}="{_snippet(value, 40)}" on {label}{where}; '
                        "replace it with a normal http(s) link or remove it"
                    )


def _audit_document(text: str) -> _DocumentAudit:
    audit = _DocumentAudit()
    audit.feed(text)
    audit.close()
    return audit


def _placeholder_violations(text: str, file_name: str, fix: str) -> list[str]:
    """One message per draft marker (first REPORT_LIMIT), naming file, line and marker."""
    messages = [
        f"draft placeholder {marker} still in {file_name} line {line}; {fix}"
        for line, marker in _placeholder_hits(text)
    ]
    return _limited(messages, "placeholder(s)")


def _local_image_name_violations(audit: _DocumentAudit) -> list[str]:
    """Local <img> files must have lowercase slug-style names."""
    problems: list[str] = []
    seen: set[str] = set()
    for img in audit.imgs:
        src = img["src"] or ""
        if not src or src.startswith(("http://", "https://", "data:", "//", "#")) or "://" in src:
            continue
        name = urllib.parse.unquote(urllib.parse.urlsplit(src).path).rsplit("/", 1)[-1]
        if not name or name in seen:
            continue
        seen.add(name)
        stem, _dot, suffix = name.rpartition(".")
        if not (SLUG_PATTERN.fullmatch(stem) and re.fullmatch(r"[a-z0-9]+", suffix)):
            problems.append(
                f"image filename is not lowercase slug style: {img['label']} src=\"{_snippet(src, 50)}\"; "
                f"rename the file to {_slugify(name)} (a-z, 0-9 and hyphens) and update the reference"
            )
    return problems


# Raster inspection. Pillow is only an optional dependency of this project
# (the `presentation` and `dev` extras), so the header parse below always runs
# and Pillow, when importable, adds a full pixel decode on top of it.

def _png_info(data: bytes) -> dict[str, Any]:
    if len(data) < 33 or data[12:16] != b"IHDR":
        return {"error": "PNG header is damaged (no IHDR chunk)"}
    width, height = int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if not data.rstrip(b"\x00").endswith(b"IEND\xaeB`\x82"):
        return {"width": width, "height": height, "error": "PNG is truncated (no IEND chunk at the end)"}
    return {"width": width, "height": height}


def _jpeg_info(data: bytes) -> dict[str, Any]:
    position = 2
    size = len(data)
    while position + 4 <= size:
        if data[position] != 0xFF:
            position += 1
            continue
        marker = data[position + 1]
        if marker == 0xFF:
            position += 1
            continue
        if marker in (0x01, 0xD8) or 0xD0 <= marker <= 0xD7:
            position += 2
            continue
        length = int.from_bytes(data[position + 2:position + 4], "big")
        if marker in range(0xC0, 0xD0) and marker not in (0xC4, 0xC8, 0xCC):
            if position + 9 > size:
                break
            height = int.from_bytes(data[position + 5:position + 7], "big")
            width = int.from_bytes(data[position + 7:position + 9], "big")
            # Entropy-coded data stores 0xFF as FF00, so FFD9 after the frame
            # header can only be the end-of-image marker. Trailing bytes after
            # it (XMP, MPF, phone trailers) are legitimate.
            if data.find(b"\xff\xd9", position + 9) < 0:
                return {"width": width, "height": height, "error": "JPEG is truncated (no end-of-image marker)"}
            return {"width": width, "height": height}
        if marker == 0xDA:
            break
        position += 2 + max(length, 2)
    return {"error": "JPEG header is damaged (no frame header found)"}


def _webp_info(data: bytes) -> dict[str, Any]:
    if int.from_bytes(data[4:8], "little") + 8 > len(data):
        return {"error": "WebP is truncated (RIFF size is larger than the file)"}
    chunk = data[12:16]
    if chunk == b"VP8X" and len(data) >= 30:
        return {"width": int.from_bytes(data[24:27], "little") + 1,
                "height": int.from_bytes(data[27:30], "little") + 1}
    if chunk == b"VP8 " and len(data) >= 30 and data[23:26] == b"\x9d\x01\x2a":
        return {"width": int.from_bytes(data[26:28], "little") & 0x3FFF,
                "height": int.from_bytes(data[28:30], "little") & 0x3FFF}
    if chunk == b"VP8L" and len(data) >= 25 and data[20] == 0x2F:
        bits = int.from_bytes(data[21:25], "little")
        return {"width": (bits & 0x3FFF) + 1, "height": ((bits >> 14) & 0x3FFF) + 1}
    return {"error": "WebP header is damaged (unrecognized or short chunk)"}


def _raster_info(data: bytes) -> dict[str, Any]:
    """Identify PNG, JPEG or WebP from its bytes: format, width, height, error."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return {"format": "PNG", **_png_info(data)}
    if data[:3] == b"\xff\xd8\xff":
        return {"format": "JPEG", **_jpeg_info(data)}
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return {"format": "WEBP", **_webp_info(data)}
    return {"format": None, "error": "not a PNG, JPEG or WebP image"}


def _pillow_decode(data: bytes) -> dict[str, Any] | None:
    """Fully decode with Pillow when it is installed; None when it is not."""
    if not _has_module("PIL"):
        return None
    try:
        import io
        from PIL import Image  # type: ignore
        with Image.open(io.BytesIO(data)) as image:
            image.load()
            return {"format": (image.format or "").upper(), "width": image.size[0], "height": image.size[1]}
    except Exception as exc:  # any decode failure means the file is not a usable image
        return {"error": f"image data does not decode ({type(exc).__name__}: {_snippet(exc, 80)})"}


_HERO_FORMATS = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".webp": "WEBP"}


def _hero_check(path: Path, data: bytes) -> tuple[list[str], dict[str, Any]]:
    """Return (violations, evidence) for one hero image."""
    info = _raster_info(data)
    decoder = "header"
    pillow = _pillow_decode(data)
    if pillow is not None:
        decoder = "pillow"
        if "error" in pillow and "error" not in info:
            info = {**info, "error": pillow["error"]}
        elif "error" not in pillow:
            # A full Pillow decode outranks the header heuristics, including
            # their truncation guesses.
            info = {**{k: v for k, v in info.items() if k != "error"}, **pillow}
    evidence = {"file": path.name, "format": info.get("format"), "width": info.get("width"),
                "height": info.get("height"), "decoder": decoder}
    violations: list[str] = []
    expected = _HERO_FORMATS.get(path.suffix.lower())
    if info.get("error"):
        violations.append(
            f"{path.name} is not a valid image: {info['error']}; regenerate it with scripts/generate_hero.py "
            "or replace it with a real 1200x630 image"
        )
        return violations, evidence
    if info.get("format") != expected:
        violations.append(
            f"{path.name} holds {info.get('format')} data but its extension says {expected}; rename it to "
            f"hero.{ {'PNG': 'png', 'JPEG': 'jpg', 'WEBP': 'webp'}[info['format']] } or re-export it"
        )
    width, height = info.get("width") or 0, info.get("height") or 0
    if width < HERO_MIN_WIDTH or height < HERO_MIN_HEIGHT:
        violations.append(
            f"{path.name} is {width}x{height}; the delivery contract requires at least "
            f"{HERO_MIN_WIDTH}x{HERO_MIN_HEIGHT}. Regenerate it at 1200x630 or larger"
        )
    return violations, evidence


def _pdf_page_count(data: bytes) -> int:
    """Count page objects, looking inside Flate object streams when needed."""
    page = re.compile(rb"/Type\s*/Page(?![A-Za-z])")
    count = len(page.findall(data))
    if count:
        return count
    import zlib
    budget = 64 * 1024 * 1024
    position = 0
    while budget > 0:
        begin = data.find(b"stream", position)
        if begin < 0:
            break
        start = begin + len(b"stream")
        if data[start:start + 2] == b"\r\n":
            start += 2
        elif data[start:start + 1] in (b"\n", b"\r"):
            start += 1
        end = data.find(b"endstream", start)
        if end < 0:
            break
        position = end + len(b"endstream")
        try:
            inflater = zlib.decompressobj()
            chunk = inflater.decompress(data[start:end], min(budget, 16 * 1024 * 1024))
        except zlib.error:
            continue
        budget -= len(chunk)
        count += len(page.findall(chunk))
        if count:
            return count
    return count


def _pdf_check(path: Path, data: bytes) -> tuple[list[str], dict[str, Any]]:
    violations: list[str] = []
    evidence: dict[str, Any] = {"file": path.name, "bytes": len(data)}
    if not data.startswith(b"%PDF-"):
        violations.append(
            f"{path.name} does not start with %PDF; it is not a PDF. Re-run blog_render.py to regenerate it"
        )
        return violations, evidence
    if b"%%EOF" not in data[-2048:]:
        violations.append(
            f"{path.name} is truncated (no %%EOF marker at the end); re-run blog_render.py to regenerate it"
        )
    pages = _pdf_page_count(data)
    evidence["pages"] = pages
    if pages < 1:
        violations.append(f"{path.name} has no pages; re-run blog_render.py to regenerate it")
    return violations, evidence


def _source_hash_violation(html_name: str, md_name: str, audit: _DocumentAudit, md_bytes: bytes) -> str | None:
    """The renderer stamps sha256(raw md bytes); a missing or different stamp means a stale render."""
    expected = hashlib.sha256(md_bytes).hexdigest()
    found = audit.named_meta.get(SOURCE_HASH_META)
    fix = f"re-run scripts/blog_render.py --md {md_name} so {html_name} and the PDF match the current source"
    if found is None:
        return f'{html_name} has no <meta name="{SOURCE_HASH_META}"> tag, so it cannot be tied to {md_name}; {fix}'
    found = found.strip().lower()
    if found != expected:
        return (
            f'{html_name} was rendered from different source bytes: <meta name="{SOURCE_HASH_META}"> is '
            f"{found[:12] or '(empty)'}... but sha256 of {md_name} is {expected[:12]}...; {fix}"
        )
    return None


def _body_integrity_violation(html_name: str, md_name: str, audit: _DocumentAudit, html_bytes: bytes) -> str | None:
    """Recompute the rendered-body hash; any hand edit of the body fails it.

    The renderer wraps the sanitized body in start/end comments and stamps the
    sha256 of the bytes strictly between them. The first start marker and the
    last end marker bound the body, and a body that holds either marker more
    than once is ambiguous and rejected. Line endings are normalized so a
    platform newline translation is not mistaken for an edit.
    """
    fix = f"edit {md_name} and re-run scripts/blog_render.py --md {md_name}"
    stamp = audit.named_meta.get(BODY_HASH_META)
    if stamp is None:
        return (
            f'{html_name} has no <meta name="{BODY_HASH_META}"> tag, so its body cannot be verified; '
            f"rendered HTML body was edited after render or was not made by the renderer: {fix}"
        )
    start = html_bytes.find(BODY_START_MARKER)
    end = html_bytes.rfind(BODY_END_MARKER)
    if start < 0 or end < 0 or end < start + len(BODY_START_MARKER):
        return f"{html_name} is missing its bs-body start/end markers; rendered HTML body was edited after render: {fix}"
    body = html_bytes[start + len(BODY_START_MARKER):end]
    if html_bytes.count(BODY_START_MARKER) != 1 or html_bytes.count(BODY_END_MARKER) != 1:
        return f"{html_name} has repeated bs-body markers, so the body is ambiguous; rendered HTML body was edited after render: {fix}"
    actual = hashlib.sha256(body.replace(b"\r\n", b"\n")).hexdigest()
    if actual != stamp.strip().lower():
        return (
            f"{html_name}: rendered HTML body was edited after render ({BODY_HASH_META} is "
            f"{stamp.strip().lower()[:12]}... but the body now hashes to {actual[:12]}...); {fix}"
        )
    return None


def gate_2_format_completeness(draft_dir: Path, slug: str | None = None) -> dict:
    """Verify .md, .html, .pdf, hero.<ext> all exist and are well formed.

    Static checks: no draft placeholders, lowercase slug filenames, a hero that
    decodes at the contract size, a PDF with pages, an HTML artifact stamped
    with the sha256 of its source, no active content in the HTML, and the
    document-structure basics (lang, title, description, one h1, heading
    order, og tags, noindex, img alt). All of it lives here so the author gets
    every static finding before the browser gate and the review.
    """
    stem, selected, artifact_violations = _select_artifact_stem(draft_dir, slug)
    mds = selected["md"]
    htmls = selected["html"]
    pdfs = selected["pdf"]
    heroes = list(draft_dir.glob("hero.*"))
    review = draft_dir / "review.md"

    violations = list(artifact_violations)
    warnings: list[str] = []
    if not mds:
        violations.append("no slug-matched .md source found")
    if not htmls:
        violations.append("no slug-matched .html artifact found (run scripts/blog_render.py)")
    if not pdfs:
        violations.append("no slug-matched .pdf artifact found (run scripts/blog_render.py)")
    hero_files = [h for h in heroes if h.name != "hero-credit.txt" and h.suffix.lower() in HERO_SUFFIXES]
    if not hero_files:
        violations.append("no hero.<png|jpg|jpeg|webp> found (run scripts/generate_hero.py)")

    evidence: dict[str, Any] = {}
    if stem is not None and not SLUG_PATTERN.fullmatch(stem):
        violations.append(
            f"artifact filename stem '{stem}' is not lowercase slug style; rename {stem}.md/.html/.pdf to "
            f"{_slugify(stem)}.* (a-z, 0-9 and hyphens only) and re-render"
        )
    for hero in hero_files:
        if hero.name != hero.name.lower():
            violations.append(f"hero filename '{hero.name}' must be lowercase; rename it to {hero.name.lower()}")
    if len(hero_files) > 1:
        warnings.append(f"more than one hero image found ({', '.join(sorted(h.name for h in hero_files))}); keep one")

    md_bytes = _safe_read_bytes(mds[0]) if len(mds) == 1 and not mds[0].is_symlink() else None
    if md_bytes is not None:
        violations.extend(_placeholder_violations(
            md_bytes.decode("utf-8", errors="replace"), mds[0].name,
            "resolve every marker (replace with a real link, local image or inline SVG chart, or remove it) and re-render",
        ))
    html_bytes = _safe_read_bytes(htmls[0]) if len(htmls) == 1 and not htmls[0].is_symlink() else None
    if html_bytes is not None:
        html_text = html_bytes.decode("utf-8", errors="replace")
        violations.extend(_placeholder_violations(
            html_text, htmls[0].name,
            f"resolve the marker in {mds[0].name if mds else 'the source'} and re-render",
        ))
        audit = _audit_document(html_text)
        violations.extend(_limited(_local_image_name_violations(audit), "image filename problem(s)"))
        violations.extend(
            _limited([f"active content in {htmls[0].name}: {item}" for item in audit.active], "active-content element(s)")
        )
        structure_violations, structure_warnings = _structure_findings(audit)
        violations.extend(structure_violations)
        warnings.extend(structure_warnings)
        if md_bytes is not None:
            hash_problem = _source_hash_violation(htmls[0].name, mds[0].name, audit, md_bytes)
            if hash_problem:
                violations.append(hash_problem)
        body_problem = _body_integrity_violation(htmls[0].name, mds[0].name if mds else "the .md", audit, html_bytes)
        if body_problem:
            violations.append(body_problem)
    for hero in hero_files:
        data = _safe_read_bytes(hero) if not hero.is_symlink() else None
        if data is None:
            violations.append(f"{hero.name} is unreadable or a symlink; replace it with a real image file")
            continue
        problems, hero_evidence = _hero_check(hero, data)
        violations.extend(problems)
        evidence.setdefault("hero_checks", []).append(hero_evidence)
    if evidence.get("hero_checks") and evidence["hero_checks"][0]["decoder"] == "header":
        warnings.append(
            "Pillow is not installed; the hero was verified from its header (format, dimensions, end marker) "
            "but its pixel data was not decoded"
        )
    if len(pdfs) == 1 and not pdfs[0].is_symlink():
        pdf_bytes = _safe_read_bytes(pdfs[0])
        if pdf_bytes is None:
            violations.append(f"{pdfs[0].name} is unreadable; re-run blog_render.py")
        else:
            problems, pdf_evidence = _pdf_check(pdfs[0], pdf_bytes)
            violations.extend(problems)
            evidence["pdf_check"] = pdf_evidence

    return _gate_result(
        2, "Format Completeness", not violations, violations, warnings,
        artifacts={
            "slug": stem,
            "md": [str(p.name) for p in mds],
            "html": [str(p.name) for p in htmls],
            "pdf": [str(p.name) for p in pdfs],
            "hero": [str(p.name) for p in hero_files],
            "review_present": review.is_file(),
        },
        **evidence,
    )


def _guard_context_network(context: Any, root_resolved: Path) -> None:
    """Confine a Gate 3 browser context to the draft folder.

    HTTP(S) requests are aborted, file reads outside the draft are aborted,
    and WebSocket connections are closed before they reach the network
    (``route`` does not cover WebSockets). Service workers are blocked at
    context creation by the caller.
    """
    def route_guard(route):
        parsed = urllib.parse.urlparse(route.request.url)
        if parsed.scheme in ("http", "https"):
            route.abort()
            return
        if parsed.scheme == "file":
            try:
                req_path = Path(urllib.request.url2pathname(parsed.path)).resolve()
                req_path.relative_to(root_resolved)
            except ValueError:
                route.abort()
                return
        route.continue_()

    context.route("**/*", route_guard)
    context.route_web_socket("**/*", lambda web_socket: web_socket.close())


HIDDEN_TEXT_CHARS = 100
HIDDEN_TEXT_ELEMENTS = 3


def _hidden_text_message(viewport: str, hidden: dict[str, Any]) -> str:
    """Name the first hidden-text element and the totals (spam-policy hidden text)."""
    first = hidden.get("first") or {}
    return (
        f"{viewport}: {hidden['chars']} characters of article text in {hidden['elements']} element(s) are in the "
        f"page but not rendered; first is {first.get('selector', '?')} "
        f"(\"{_snippet(first.get('sample'), 40)}\"). Hidden text can break Google's spam policies: remove it "
        f"or show it (a violation at {HIDDEN_TEXT_CHARS}+ characters or {HIDDEN_TEXT_ELEMENTS}+ elements, a warning below)"
    )


def _describe_overflows(overflows: list[dict[str, Any]], limit: int = 3) -> str:
    """Name the overflowing elements (selector, child and how far it sticks out)."""
    parts = []
    for item in overflows[:limit]:
        container = item.get("containerSelector") or str(item.get("container", "?")).lower()
        child = item.get("childSelector") or str(item.get("tag", "?")).lower()
        text = f' "{_snippet(item.get("content"), 30)}"' if item.get("content") else ""
        extent = f" by {item['overflowPx']}px" if item.get("overflowPx") else ""
        parts.append(f"{child}{text} overflows {container}{extent}")
    more = f" (+{len(overflows) - limit} more)" if len(overflows) > limit else ""
    return "; ".join(parts) + more + ". Shrink or reflow that element, or widen the container"


def gate_3_visual_verification(draft_dir: Path, slug: str | None = None) -> dict:
    """Render the .html via patchright (or playwright); screenshot at 3
    widths; check SVG bboxes, dark mode, console errors, JSON-LD."""
    sync_playwright = None
    backend = None
    try:
        from patchright.sync_api import sync_playwright  # type: ignore
        backend = "patchright"
    except ImportError:
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
            backend = "playwright"
        except ImportError:
            pass
    if sync_playwright is None:
        return _gate_result(
            3, "Visual Verification", False,
            [
                "neither patchright nor playwright is installed; visual verification "
                "is required. Run the documented environment setup before delivery"
            ],
        )

    _stem, selected, artifact_violations = _select_artifact_stem(draft_dir, slug)
    htmls = selected["html"]
    if not htmls:
        return _gate_result(3, "Visual Verification", False, ["no .html artifact to verify"])
    if artifact_violations:
        return _gate_result(3, "Visual Verification", False, artifact_violations)

    html_path = htmls[0]
    preview_dir = draft_dir / "preview"
    if preview_dir.exists() and preview_dir.is_symlink():
        return _gate_result(3, "Visual Verification", False, [f"preview output path is a symlink: {preview_dir}"])
    preview_dir.mkdir(exist_ok=True)
    if not preview_dir.is_dir():
        return _gate_result(3, "Visual Verification", False, [f"preview output path is not a directory: {preview_dir}"])

    violations = []
    warnings = [f"backend: {backend}"]
    per_viewport: dict = {}
    identity_mismatch_seen = False
    hidden_by_viewport: dict[str, dict[str, Any]] = {}

    bbox_check_js = r"""
() => {
  const overflows = [];
  const selectorOf = (el) => el.tagName.toLowerCase()
    + (el.id ? '#' + el.id : (typeof el.className === 'string' && el.className.trim()
      ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : ''));
  const boxes = document.querySelectorAll('svg, figure');
  boxes.forEach((box, i) => {
    const svgBox = box.getBoundingClientRect();
    const desc = box.querySelectorAll('text, path, rect, image, circle, line, img, figcaption');
    desc.forEach((child) => {
      const r = child.getBoundingClientRect();
      const margin = 2;
      if (r.left < svgBox.left - margin || r.right > svgBox.right + margin ||
          r.top < svgBox.top - margin || r.bottom > svgBox.bottom + margin) {
        overflows.push({containerIndex: i, container: box.tagName, tag: child.tagName, content: (child.textContent||'').slice(0,40),
          containerSelector: selectorOf(box), childSelector: selectorOf(child),
          overflowPx: Math.round(Math.max(svgBox.left - r.left, r.right - svgBox.right, svgBox.top - r.top, r.bottom - svgBox.bottom)),
          childBox:{l:r.left,r:r.right,t:r.top,b:r.bottom},
          svgBox:{l:svgBox.left,r:svgBox.right,t:svgBox.top,b:svgBox.bottom}});
      }
    });
  });
  const bg = getComputedStyle(document.body).backgroundColor;
  const jsonLdScripts = [...document.querySelectorAll('script[type="application/ld+json"]')];
  let jsonLdValid = false, jsonLdType = null, jsonLdMissingFields = [];
  let jsonLdVisibleConsistent = false, jsonLdConsistencyMismatches = [];
  let jsonLdWordCount = null;
  if (jsonLdScripts.length) {
    try {
      // Every block must parse; the BlogPosting node may sit in any of them.
      const nodes = jsonLdScripts.flatMap((script) => {
        const raw = JSON.parse(script.textContent);
        return Array.isArray(raw) ? raw : (raw['@graph'] || [raw]);
      });
      const obj = nodes.find((node) => {
        const type = node && node['@type'];
        return type === 'BlogPosting' || (Array.isArray(type) && type.includes('BlogPosting'));
      }) || {};
      jsonLdValid = true;
      jsonLdType = obj['@type'];
      const required = ['headline','image','datePublished','author'];
      jsonLdMissingFields = required.filter(k => !obj[k]);
      jsonLdWordCount = Number.isInteger(obj.wordCount) ? obj.wordCount : null;
    } catch (e) { jsonLdValid = false; }
  }
  // Keep head/schema markup, but remove body nodes hidden by actual computed layout.
  const visibleDocument = document.documentElement.cloneNode(true);
  const originals = [...document.body.querySelectorAll('*')];
  const copies = [...visibleDocument.querySelector('body').querySelectorAll('*')];
  const identitySelector = 'h1,.byline,[rel~=author],[itemprop~=author],[itemprop~=name],[itemprop~=datePublished],time,.author,.author-name,.byline-author,.p-author';
  // Identity matching also reads the hero image, so its geometry is checked too.
  const geometrySelector = identitySelector + ',img,.hero';
  const pageRight = document.documentElement.clientWidth;
  // Rects are clipped by every ancestor that crops its contents (overflow:hidden,
  // clip, clip-path) and must keep a few visible pixels, so sr-only boxes fail.
  const lengthPx = (token, size) => token.endsWith('%') ? parseFloat(token) / 100 * size : parseFloat(token);
  const clipRect = (rect, ancestor, self) => {
    const style = getComputedStyle(ancestor);
    const box = ancestor.getBoundingClientRect();
    let {left, top, right, bottom} = rect;
    if (!self) {
      const cropX = ['hidden', 'clip'].includes(style.overflowX);
      const cropY = ['hidden', 'clip'].includes(style.overflowY);
      if (cropX) { left = Math.max(left, box.left); right = Math.min(right, box.right); }
      if (cropY) { top = Math.max(top, box.top); bottom = Math.min(bottom, box.bottom); }
    }
    const clip = style.clip.match(/^rect\(([^)]*)\)$/);
    if (clip && ['absolute', 'fixed'].includes(style.position)) {
      const [t, r, b, l] = clip[1].split(/[\s,]+/).map(parseFloat);
      if (!Number.isNaN(l)) left = Math.max(left, box.left + l);
      if (!Number.isNaN(r)) right = Math.min(right, box.left + r);
      if (!Number.isNaN(t)) top = Math.max(top, box.top + t);
      if (!Number.isNaN(b)) bottom = Math.min(bottom, box.top + b);
    }
    const path = style.clipPath;
    if (path && path !== 'none') {
      const inset = path.match(/^inset\(([^)]*)\)/);
      if (inset) {
        const sides = inset[1].split(/\s+round\s+/)[0].trim().split(/\s+/);
        const [t, r = t, b = t, l = r] = sides;
        left = Math.max(left, box.left + lengthPx(l, box.width));
        right = Math.min(right, box.right - lengthPx(r, box.width));
        top = Math.max(top, box.top + lengthPx(t, box.height));
        bottom = Math.min(bottom, box.bottom - lengthPx(b, box.height));
      } else if (/^(?:circle|ellipse)\(\s*0(?:px|%)?[\s,)]/.test(path)) {
        return null;
      } else if (path.startsWith('polygon(')) {
        const points = new Set(path.slice(8, -1).replace(/^[^,]*?(?:nonzero|evenodd)\s*,/, '').split(','));
        if (points.size <= 1) return null;
      }
    }
    const width = right - left, height = bottom - top;
    if (width <= 0 || height <= 0) return null;
    const cropped = left !== rect.left || top !== rect.top || right !== rect.right || bottom !== rect.bottom;
    return cropped && (width < 2 || height < 2) ? null : {left, top, right, bottom};
  };
  const rectIsVisible = (rect, element) => {
    if (!(rect.width > 0 && rect.height > 0)) return false;
    // Anything left of or above the page origin can never be scrolled to; anything
    // starting past the layout width is outside the page box.
    if (rect.right + window.scrollX <= 0 || rect.bottom + window.scrollY <= 0) return false;
    if (rect.left + window.scrollX >= pageRight) return false;
    let current = {left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom};
    for (let node = element; node && node !== document.documentElement; node = node.parentElement) {
      current = clipRect(current, node, node === element);
      if (!current) return false;
    }
    return true;
  };
  const textIsHidden = (node) => {
    // Hidden text can sit in an on-screen box (text-indent:-9999px, font-size:0).
    if (!node.nodeValue.trim()) return false;
    if (parseFloat(getComputedStyle(node.parentElement).fontSize) < 1) return true;
    const range = document.createRange();
    range.selectNodeContents(node);
    return ![...range.getClientRects()].some((rect) => rectIsVisible(rect, node.parentElement));
  };
  const tinyFont = (element) => parseFloat(getComputedStyle(element).fontSize) < 1
    && [...element.querySelectorAll('*')].every((child) => parseFloat(getComputedStyle(child).fontSize) < 1);
  const geometryHidden = (element) => {
    if (tinyFont(element)) return true;
    // A wrapper is visible while any of its descendants still has a visible box.
    return ![element, ...element.querySelectorAll('*')].some((node) =>
      [...node.getClientRects()].some((rect) => rectIsVisible(rect, node)));
  };
  const originalText = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const copiedText = document.createTreeWalker(visibleDocument.querySelector('body'), NodeFilter.SHOW_TEXT);
  let originalNode, copiedNode;
  while ((originalNode = originalText.nextNode()) && (copiedNode = copiedText.nextNode())) {
    if (!originalNode.parentElement.closest(identitySelector)) continue;
    const color = getComputedStyle(originalNode.parentElement).color;
    const alpha = color.match(/(?:,|\/)\s*([.\d]+%?)\s*\)$/);
    if (color === 'transparent' || ((color.startsWith('rgba(') || color.includes('/')) && alpha && parseFloat(alpha[1]) === 0)
        || textIsHidden(originalNode)) {
      copiedNode.nodeValue = '';
    }
  }
  originals.forEach((element, index) => {
    if (['SCRIPT', 'STYLE'].includes(element.tagName)) return;
    const style = getComputedStyle(element);
    // Opacity multiplies through ancestors, even when a child computes to 1.
    let opacityHidden = false;
    for (let ancestor = element; ancestor; ancestor = ancestor.parentElement) {
      if (Number(getComputedStyle(ancestor).opacity) === 0) {
        opacityHidden = true;
        break;
      }
    }
    const geometryScoped = element.closest(geometrySelector) && geometryHidden(element);
    if (opacityHidden || geometryScoped || (!element.getClientRects().length && style.display !== 'contents') || style.visibility === 'hidden' || style.display === 'none') {
      copies[index].remove();
    }
  });
  // Text in the article that is in the DOM but not rendered (keyword stuffing).
  // Skips inert containers, closed <details> content and decorative SVG, and
  // trusts only non-geometric signals inside scrollers (a wide table scrolls).
  const hiddenTextSkip = 'template,noscript,script,style,svg[aria-hidden="true"],[aria-hidden="true"] svg';
  const hiddenElements = new Map();
  const articleRoot = document.querySelector('article') || document.body;
  const hiddenWalker = document.createTreeWalker(articleRoot, NodeFilter.SHOW_TEXT);
  let hiddenNode;
  while ((hiddenNode = hiddenWalker.nextNode())) {
    const text = hiddenNode.nodeValue.replace(/\s+/g, ' ').trim();
    const owner = hiddenNode.parentElement;
    if (!text || !owner || owner.closest(hiddenTextSkip)) continue;
    const closedDetails = owner.closest('details:not([open])');
    if (closedDetails && !owner.closest('summary')) continue;
    const ownerStyle = getComputedStyle(owner);
    let faded = false, scrolls = false;
    for (let up = owner; up && up !== document.documentElement; up = up.parentElement) {
      const upStyle = getComputedStyle(up);
      if (Number(upStyle.opacity) === 0) faded = true;
      if (up !== owner && ['auto', 'scroll'].includes(upStyle.overflowX)) scrolls = true;
    }
    const hidden = ownerStyle.display === 'none' || ownerStyle.visibility === 'hidden' || faded
      || parseFloat(ownerStyle.fontSize) < 1 || !owner.getClientRects().length && ownerStyle.display !== 'contents'
      || (!scrolls && textIsHidden(hiddenNode));
    if (!hidden) continue;
    const entry = hiddenElements.get(owner) || {selector: selectorOf(owner), chars: 0, sample: text.slice(0, 40)};
    entry.chars += text.length;
    hiddenElements.set(owner, entry);
  }
  const hiddenList = [...hiddenElements.values()];
  const hiddenText = {
    chars: hiddenList.reduce((sum, item) => sum + item.chars, 0),
    elements: hiddenList.length,
    first: hiddenList[0] || null,
  };
  const visibleIdentityHtml = visibleDocument.outerHTML;
  return {
    hiddenText, visibleIdentityHtml, overflows, bg, jsonLdValid, jsonLdType, jsonLdMissingFields,
    jsonLdVisibleConsistent, jsonLdConsistencyMismatches, jsonLdWordCount
  };
}
""".strip()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for vp in VIEWPORTS:
                context = browser.new_context(
                    viewport={"width": vp["width"], "height": vp["height"]},
                    service_workers="block",
                )
                _guard_context_network(context, draft_dir.resolve())
                page = context.new_page()
                console_errors: list[str] = []
                def record_console(msg, sink=console_errors):
                    if msg.type != "error":
                        return
                    # Resource load errors carry no URL in their text; name it.
                    url = (getattr(msg, "location", None) or {}).get("url") or ""
                    sink.append(f"{msg.text} ({url})" if url and url not in msg.text else msg.text)

                page.on("console", record_console)
                page.goto(html_path.resolve().as_uri(), wait_until="networkidle", timeout=30_000)
                screenshot = page.screenshot(full_page=True)
                _atomic_write_bytes(preview_dir / f"{vp['name']}-{vp['width']}.png", screenshot)
                result = page.evaluate(bbox_check_js)
                identity_html = result.pop("visibleIdentityHtml")
                identity_parser = _MetaParser()
                identity_parser.feed(identity_html)
                try:
                    identity_nodes, block_errors = _parse_jsonld_blocks(identity_parser.json_ld_blocks)
                    identity_obj = next((node for node in identity_nodes if _is_blogposting_node(node)), None)
                    if block_errors or identity_obj is None:
                        # Name the failing block instead of reporting an empty mismatch list.
                        result["jsonLdConsistencyMismatches"] = [
                            "JSON-LD " + "; ".join(block_errors) if block_errors
                            else "JSON-LD has no BlogPosting node"
                        ]
                    else:
                        result["jsonLdConsistencyMismatches"] = _jsonld_identity_mismatches(identity_html, identity_obj, identity_nodes)
                    result["jsonLdVisibleConsistent"] = not result["jsonLdConsistencyMismatches"]
                    if identity_obj is not None and not block_errors:
                        report = _jsonld_identity_report(identity_html, identity_obj, identity_nodes)
                        result["jsonLdConsistencyDetails"] = {
                            field: {"schema": schema, "visible": visible} for field, (schema, visible) in report.items()
                        }
                except (ValueError, TypeError):
                    result["jsonLdVisibleConsistent"] = False
                per_viewport[vp["name"]] = {"result": result, "console_errors": console_errors}
                hidden = result.get("hiddenText") or {}
                if hidden.get("chars"):
                    hidden_by_viewport[vp["name"]] = hidden
                if result["overflows"]:
                    violations.append(
                        f"{vp['name']}: {len(result['overflows'])} SVG overflow(s): "
                        f"{_describe_overflows(result['overflows'])}"
                    )
                if console_errors:
                    violations.append(
                        f"{vp['name']}: {len(console_errors)} console error(s): "
                        f"{_snippet('; '.join(dict.fromkeys(console_errors)), 300)}"
                    )
                if not result["jsonLdValid"]:
                    violations.append(f"{vp['name']}: JSON-LD invalid or missing")
                elif result["jsonLdType"] != "BlogPosting":
                    violations.append(f"{vp['name']}: JSON-LD @type != BlogPosting")
                elif result["jsonLdMissingFields"]:
                    violations.append(f"{vp['name']}: JSON-LD missing fields: {result['jsonLdMissingFields']}")
                elif not result["jsonLdVisibleConsistent"]:
                    details = result.get("jsonLdConsistencyDetails") or {}
                    shown = "; ".join(
                        f'{field} (schema "{details[field]["schema"]}" vs visible "{details[field]["visible"]}")'
                        if field in details else str(field)
                        for field in result["jsonLdConsistencyMismatches"]
                    )
                    violations.append(f"{vp['name']}: JSON-LD does not match visible content: {shown}")
                    identity_mismatch_seen = True
                if vp["name"] == "desktop":
                    observation = {
                        "attempted_back": True,
                        "observation_complete": False,
                        "returned_to_previous": False,
                        "before_url": page.url,
                    }
                    try:
                        page.go_back(wait_until="domcontentloaded", timeout=5_000)
                        observation["observation_complete"] = True
                        observation["after_url"] = page.url
                        observation["returned_to_previous"] = page.url == "about:blank"
                    except Exception as exc:
                        observation["error"] = str(exc)
                        observation["after_url"] = page.url
                    back_check = _classify_back_button_behavior(observation)
                    per_viewport[vp["name"]]["back_button"] = {
                        **observation,
                        **back_check,
                    }
                    if back_check["violation"]:
                        violations.append(f"desktop: {back_check['violation']}")
                    elif back_check["checked"] and not back_check["conclusive"]:
                        warnings.append(
                            "desktop: back-button behavior check was inconclusive; "
                            "no violation was recorded"
                        )
                context.close()

            # Dark mode pass at desktop width
            context = browser.new_context(
                viewport={"width": 1280, "height": 800}, color_scheme="dark",
                service_workers="block",
            )
            _guard_context_network(context, draft_dir.resolve())
            page = context.new_page()
            page.goto(html_path.resolve().as_uri(), wait_until="networkidle", timeout=30_000)
            dark_bg = page.evaluate("() => getComputedStyle(document.body).backgroundColor")
            light_bg = per_viewport["desktop"]["result"]["bg"]
            screenshot = page.screenshot(full_page=True)
            _atomic_write_bytes(preview_dir / "desktop-1280-dark.png", screenshot)
            if dark_bg == light_bg:
                violations.append(f"dark mode did not change background color (still {dark_bg})")
            per_viewport["desktop-dark"] = {"bg": dark_bg, "light_bg": light_bg}
            context.close()
            browser.close()
    except Exception as e:
        return _gate_result(3, "Visual Verification", False, [f"patchright runtime error: {e}"])

    if hidden_by_viewport:
        worst_name, worst = max(hidden_by_viewport.items(), key=lambda item: item[1]["chars"])
        message = _hidden_text_message(worst_name, worst)
        if worst["chars"] >= HIDDEN_TEXT_CHARS or worst["elements"] >= HIDDEN_TEXT_ELEMENTS:
            violations.append(message)
        else:
            warnings.append(message)

    if identity_mismatch_seen:
        source = _safe_read_bytes(html_path)
        canonical_probe = _MetaParser()
        canonical_probe.feed(source.decode("utf-8", errors="replace") if source is not None else "")
        if not canonical_probe.canonical:
            # Relative image URLs resolve against the canonical, so report the cause first.
            violations.insert(
                0,
                "no <link rel=canonical> in document; image identity mismatches below may only be a result "
                f"of it. Fix: {CANONICAL_FIX}",
            )

    return _gate_result(3, "Visual Verification", not violations, violations, warnings, per_viewport=per_viewport)


def _rendered_jsonld_handoff(gate_3_result: dict[str, Any] | None) -> dict[str, Any]:
    """Derive an in-process Gate 5 schema handoff from conclusive Gate 3 data."""
    unavailable = {
        "available": False,
        "valid": False,
        "source": "rendered_dom",
        "word_count": None,
    }
    if not gate_3_result or not gate_3_result.get("passed"):
        return unavailable
    per_viewport = gate_3_result.get("per_viewport")
    if not isinstance(per_viewport, dict):
        return unavailable

    results: list[dict[str, Any]] = []
    for viewport in (item["name"] for item in VIEWPORTS):
        entry = per_viewport.get(viewport)
        result = entry.get("result") if isinstance(entry, dict) else None
        if not isinstance(result, dict):
            return unavailable
        results.append(result)

    valid = all(
        result.get("jsonLdValid") is True
        and result.get("jsonLdType") == "BlogPosting"
        and result.get("jsonLdMissingFields") == []
        and result.get("jsonLdVisibleConsistent") is True
        for result in results
    )
    if not valid:
        return unavailable
    word_counts = {result.get("jsonLdWordCount") for result in results}
    word_count = word_counts.pop() if len(word_counts) == 1 else None
    if not isinstance(word_count, int):
        word_count = None
    return {
        "available": True,
        "valid": True,
        "source": "rendered_dom",
        "word_count": word_count,
        "viewports": [item["name"] for item in VIEWPORTS],
    }


class _MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.imgs: list[str] = []
        self.links: list[str] = []
        # Parallel to ``links``: True for the renderer's own footer link
        # (data-bs-generated="1" inside <footer>), which Gate 5 does not fetch.
        self.link_generated: list[bool] = []
        self.codes: list[str] = []
        self.ids: set[str] = set()
        self.og_image: Optional[str] = None
        self.og_image_width: Optional[int] = None
        self.og_image_height: Optional[int] = None
        self.robots_content: list[str] = []
        self.has_amp = False
        self.canonical: Optional[str] = None
        self.json_ld_blocks: list[str] = []
        self._in_jsonld = False
        self._jsonld_buffer: list[str] = []
        self._in_article = False
        self._in_main = False
        self.saw_article = False
        self.saw_main = False
        self.main_text_chars = 0
        self._in_code = False
        self._in_header = False
        self._in_footer = False
        self.article_text_chars = 0

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if d.get("id"):
            self.ids.add(d["id"])
        if d.get("name"):
            self.ids.add(d["name"])
        if tag == "img" and d.get("src"):
            self.imgs.append(d["src"])
        elif tag == "a" and d.get("href"):
            self.links.append(d["href"])
            self.link_generated.append(self._in_footer and d.get(GENERATED_LINK_ATTR) == "1")
        elif tag == "meta" and d.get("property") == "og:image" and d.get("content"):
            self.og_image = d["content"]
        elif tag == "meta" and d.get("property") == "og:image:width" and d.get("content"):
            try:
                self.og_image_width = int(d["content"])
            except (TypeError, ValueError):
                pass
        elif tag == "meta" and d.get("property") == "og:image:height" and d.get("content"):
            try:
                self.og_image_height = int(d["content"])
            except (TypeError, ValueError):
                pass
        elif tag == "meta" and d.get("name", "").lower() in {"robots", "googlebot"}:
            if d.get("content"):
                self.robots_content.append(d["content"])
        elif tag == "html" and "amp" in d:
            self.has_amp = True
        elif tag == "link" and d.get("rel") == "canonical" and d.get("href"):
            self.canonical = d["href"]
        elif tag == "script" and d.get("type") == "application/ld+json":
            self._in_jsonld = True
            self._jsonld_buffer = []
        elif tag == "article":
            self._in_article = True
            self.saw_article = True
        elif tag == "main":
            self._in_main = True
            self.saw_main = True
        elif tag == "header":
            self._in_header = True
        elif tag == "footer":
            self._in_footer = True
        elif tag == "code":
            self._in_code = True

    def handle_endtag(self, tag):
        if tag == "script":
            if self._in_jsonld:
                # One entry per block so several blocks never concatenate.
                self.json_ld_blocks.append("".join(self._jsonld_buffer))
            self._in_jsonld = False
        elif tag == "article":
            self._in_article = False
        elif tag == "main":
            self._in_main = False
        elif tag == "header":
            self._in_header = False
        elif tag == "footer":
            self._in_footer = False
        elif tag == "code":
            self._in_code = False

    def handle_data(self, data):
        if self._in_jsonld:
            self._jsonld_buffer.append(data)
        if self._in_code and self._in_article:
            self.codes.append(data.strip())
        # Count body-only words: exclude <header> (title, byline), <footer>
        # (site/date), and <code> blocks. Aligned with blog_render.py's
        # wordCount semantics so Gate 5 catches real drift, not template
        # boilerplate (v1.9.0 audit fix).
        if (self._in_article and not self._in_code
                and not self._in_header and not self._in_footer):
            self.article_text_chars += len(re.findall(r"\b\w+\b", data))
        if (self._in_main and not self._in_code
                and not self._in_header and not self._in_footer):
            self.main_text_chars += len(re.findall(r"\b\w+\b", data))


class _IdentityHTMLParser(HTMLParser):
    """Small element tree for visible article identity, never head metadata."""

    _VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.root = {"tag": "document", "attrs": {}, "children": []}
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = {"tag": tag, "attrs": dict(attrs), "children": []}
        self.stack[-1]["children"].append(node)
        if tag not in self._VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self._VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index]["tag"] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1]["children"].append(data)


def _identity_inline_style(style, property_name):
    values = re.findall(r"(?:^|;)" + re.escape(property_name) + r":([^;]+)", style)
    important = [value for value in values if value.endswith("!important")]
    selected = (important or values)[-1] if values else ""
    return selected.removesuffix("!important")


def _identity_zero_alpha(value):
    try:
        return float(value.rstrip("%")) <= 0
    except ValueError:
        return False


def _identity_transparent_color(color):
    if color == "transparent" or re.fullmatch(r"#[0-9a-f]{3}0|#[0-9a-f]{6}00", color):
        return True
    if "/" in color:
        return _identity_zero_alpha(color.rsplit("/", 1)[1].rstrip(")"))
    if color.startswith(("rgba(", "hsla(")) and color.count(",") == 3:
        return _identity_zero_alpha(color.rsplit(",", 1)[1].rstrip(")"))
    return False


def _identity_length(style, property_name):
    """Return an inline CSS length as (number, unit), or None."""
    match = re.fullmatch(r"(-?\d*\.?\d+)([a-z%]*)", _identity_inline_style(style, property_name))
    return (float(match.group(1)), match.group(2)) if match else None


def _identity_inline_hidden_by_geometry(style):
    """Spot inline-style tricks that keep a node out of sight without display:none.

    Only inline styles are visible here; stylesheet-driven variants are caught
    from real layout in Gate 3.
    """
    positioned = _identity_inline_style(style, "position") in {"absolute", "fixed"}
    for side in ("left", "top"):
        offset = _identity_length(style, side)
        if positioned and offset and (offset[0] <= -100 or (side == "left" and offset[0] >= 5000)):
            return True
    indent = _identity_length(style, "text-indent")
    if indent and indent[0] <= -100:
        return True
    size = _identity_length(style, "font-size")
    if size and size[0] == 0:
        return True
    if re.fullmatch(r"rect\((?:0(?:px)?,?){4}\)", _identity_inline_style(style, "clip")):
        return True
    if re.fullmatch(r"inset\((?:50|100)%\)|circle\(0(?:px|%)?\)", _identity_inline_style(style, "clip-path")):
        return True
    if re.fullmatch(r"scale\(0(?:,0)?\)", _identity_inline_style(style, "transform")):
        return True
    cropped = _identity_inline_style(style, "overflow") in {"hidden", "clip"}
    return cropped and any(
        (length := _identity_length(style, name)) and length[0] == 0 for name in ("width", "height")
    )


def _identity_elements(node):
    attrs = node["attrs"]
    style = re.sub(r"\s+", "", (attrs.get("style") or "")).lower()
    if (node["tag"] in {"head", "script", "style", "template", "noscript"}
            or "hidden" in attrs or (attrs.get("aria-hidden") or "").lower() == "true"
            or "display:none" in style or "visibility:hidden" in style
            or _identity_zero_alpha(_identity_inline_style(style, "opacity"))
            or _identity_inline_hidden_by_geometry(style)):
        return
    yield node
    for child in node["children"]:
        if isinstance(child, dict):
            yield from _identity_elements(child)


def _identity_text(node, inherited_transparent=False):
    style = re.sub(r"\s+", "", node["attrs"].get("style") or "").lower()
    color = _identity_inline_style(style, "color")
    transparent = _identity_transparent_color(color) if color else inherited_transparent
    return "".join(
        ("" if transparent else child) if isinstance(child, str)
        else _identity_text(child, transparent)
        for child in node["children"]
        if isinstance(child, str) or list(_identity_elements(child))
    )


def _identity_normalize(value):
    return re.sub(r"\s+", " ", str(value or "")).strip().casefold()


def _identity_date(value):
    text = str(value or "").strip()
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            return dt.date.fromisoformat(text)
        return dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        for pattern in ("%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y", "%d %B %Y", "%d %b %Y"):
            try:
                return dt.datetime.strptime(text, pattern).date()
            except ValueError:
                pass
    return None


def _identity_dates_equal(left, right):
    left, right = _identity_date(left), _identity_date(right)
    if left is None or right is None:
        return False
    if isinstance(left, dt.datetime) and isinstance(right, dt.datetime):
        if (left.tzinfo is None) == (right.tzinfo is None):
            return left == right
        return left.replace(tzinfo=None) == right.replace(tzinfo=None)
    def dates(value):
        if not isinstance(value, dt.datetime):
            return {value}
        result = {value.date()}
        if value.tzinfo is not None:
            result.add(value.astimezone(dt.timezone.utc).date())
        return result
    return bool(dates(left) & dates(right))


def _identity_schema_values(value, nodes, field, seen=None):
    """Accept name strings, Person/Organization/ImageObject objects and arrays."""
    seen = set() if seen is None else seen
    if isinstance(value, list):
        return [part for item in value for part in _identity_schema_values(item, nodes, field, seen)]
    if isinstance(value, str):
        target = next((node for node in nodes if node.get("@id") == value), None)
        if target is not None and value not in seen:
            return _identity_schema_values(target, nodes, field, seen | {value})
        return [value] if value.strip() else []
    if isinstance(value, dict):
        for key in (("name",) if field == "author" else ("url", "contentUrl")):
            if value.get(key):
                return _identity_schema_values(value[key], nodes, field, seen)
        reference = value.get("@id")
        if reference and reference not in seen:
            target = next((node for node in nodes if node.get("@id") == reference and node is not value), None)
            if target is not None:
                return _identity_schema_values(target, nodes, field, seen | {reference})
    return []


def _identity_asset_urls(value, canonical):
    """Resolve local assets both beside a document and below its publish URL."""
    value = str(value or "").strip()
    if not value:
        return set()
    candidates = {value}
    if canonical and not urllib.parse.urlsplit(value).scheme:
        candidates = {
            urllib.parse.urljoin(canonical, value),
            urllib.parse.urljoin(canonical.rstrip("/") + "/", value),
        }
    result = set()
    for candidate in candidates:
        parsed = urllib.parse.urlsplit(candidate)
        host = (parsed.hostname or "").lower()
        try:
            port = parsed.port
        except ValueError:
            continue
        if port and (parsed.scheme.lower(), port) not in {("http", 80), ("https", 443)}:
            host += ":" + str(port)
        path = urllib.parse.quote(urllib.parse.unquote(parsed.path), safe="/:@-._~!$&'()*+,;=")
        result.add(urllib.parse.urlunsplit((parsed.scheme.lower(), host, path, parsed.query, "")))
    return result


def _jsonld_identity_mismatches(html, obj, nodes):
    """Compare required schema identity against article markup, not meta tags."""
    return list(_jsonld_identity_report(html, obj, nodes))


def _identity_shown(values):
    shown = [_snippet(value, 70) for value in values if str(value or "").strip()]
    return " | ".join(shown) if shown else "(none found)"


def _describe_identity_mismatches(report):
    """Render {field: (schema, visible)} as 'field (schema "A" vs visible "B")' text."""
    return "; ".join(
        f'{field} (schema "{schema}" vs visible "{visible}")' for field, (schema, visible) in report.items()
    )


def _jsonld_identity_report(html, obj, nodes):
    """Return {field: (schema value, visible value)} for each identity mismatch."""
    parser = _IdentityHTMLParser()
    parser.feed(html)
    elements = list(_identity_elements(parser.root))
    article = next((node for node in elements if node["tag"] == "article"), parser.root)
    visible = list(_identity_elements(article))
    def tokens(node, key):
        return set((node["attrs"].get(key) or "").split())
    h1 = next((node for node in visible if node["tag"] == "h1"), None)
    mismatches = {}
    if h1 is None or _identity_normalize(_identity_text(h1)) != _identity_normalize(obj.get("headline")):
        mismatches["headline"] = (
            _identity_shown([obj.get("headline")]),
            _identity_shown([_identity_text(h1)]) if h1 is not None else "(no visible <h1>)",
        )

    bylines = [node for node in visible if "byline" in tokens(node, "class")]
    author_nodes = [node for node in visible if (
        "author" in tokens(node, "itemprop") or "author" in tokens(node, "rel")
        or tokens(node, "class") & {"author", "author-name", "byline-author", "p-author"}
    )]
    representations = []
    if author_nodes:
        visible_names = []
        for node in author_nodes:
            name_nodes = [child for child in _identity_elements(node) if "name" in tokens(child, "itemprop")]
            visible_names.extend(_identity_text(child) for child in (name_nodes or [node]))
        if any(_identity_normalize(name) for name in visible_names):
            representations.append((" and ".join(visible_names), not bylines))
    # A matching semantic author must never suppress a contradictory byline.
    for byline in bylines:
        text = re.split(r"[·•|]", _identity_text(byline))[0]
        text = re.split(r"\d{4}-\d{2}-\d{2}", text)[0]
        representations.append((text, True))
    names = {_identity_normalize(name) for name in _identity_schema_values(obj.get("author"), nodes, "author")}
    names.discard("")
    author_ok = bool(representations and names)
    for text, require_all in representations:
        author_text = _identity_normalize(text)
        matched = False
        for name in sorted(names, key=len, reverse=True):
            author_text, count = re.subn(r"(?<!\w)" + re.escape(name) + r"(?!\w)", " ", author_text)
            matched = matched or count > 0
            if require_all and count == 0:
                author_ok = False
        remainder = re.sub(r"\b(?:by|and|with)\b|[,;&/|]", " ", author_text).strip()
        author_ok = author_ok and matched and not remainder
    if not author_ok:
        mismatches["author"] = (
            _identity_shown(sorted(names)),
            _identity_shown(_identity_normalize(text) for text, _all in representations),
        )

    def publication_time(node):
        return (node["tag"] == "time"
                and "dateModified" not in tokens(node, "itemprop")
                and not tokens(node, "class") & {"updated", "modified"})

    date_nodes = [node for node in visible if "datePublished" in tokens(node, "itemprop")]
    if not date_nodes:
        date_nodes = [child for byline in bylines for child in _identity_elements(byline) if publication_time(child)]
    if not date_nodes:
        date_nodes = [child for header in visible if header["tag"] == "header"
                      for child in _identity_elements(header) if publication_time(child)]
    if not date_nodes and not bylines:
        date_nodes = [node for node in visible if publication_time(node)][:1]
    dates = [node["attrs"].get("datetime") or _identity_text(node) for node in date_nodes]
    if not dates:
        date_pattern = r"\d{4}-\d{2}-\d{2}(?:T[\d:.]+(?:Z|[+-]\d{2}:\d{2})?)?|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}"
        dates = [match.group() for byline in bylines for match in re.finditer(date_pattern, _identity_text(byline), re.I)]
    if not dates or not all(_identity_dates_equal(value, obj.get("datePublished")) for value in dates):
        mismatches["datePublished"] = (
            _identity_shown([obj.get("datePublished")]),
            _identity_shown(dates),
        )

    hero_containers = [node for node in visible if "hero" in tokens(node, "class")]
    hero_images = [child for node in hero_containers for child in _identity_elements(node) if child["tag"] == "img"]
    if not hero_images:
        hero_images = [node for node in visible if node["tag"] == "img" and "image" in tokens(node, "itemprop")]
    if not hero_images:
        hero_images = [node for node in visible if node["tag"] == "img"][:1]
    canonical_parser = _MetaParser()
    canonical_parser.feed(html)
    canonical = canonical_parser.canonical
    actual_images = set().union(*(_identity_asset_urls(node["attrs"].get("src"), canonical) for node in hero_images))
    schema_images = set().union(*(_identity_asset_urls(value, canonical) for value in _identity_schema_values(obj.get("image"), nodes, "image")))
    og_images = _identity_asset_urls(canonical_parser.og_image, canonical)
    if (not actual_images or not actual_images & schema_images
            or (og_images and not actual_images & schema_images & og_images)):
        schema_shown = _identity_shown(_identity_schema_values(obj.get("image"), nodes, "image"))
        visible_shown = _identity_shown(node["attrs"].get("src") for node in hero_images)
        if canonical is None:
            visible_shown += " (no <link rel=canonical>, so relative image URLs cannot be resolved; set it first)"
        mismatches["image"] = (schema_shown, visible_shown)
    return mismatches


class _PreflightNoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Refuse automatic redirect-following in Gate 5 link checks (VULN-804).

    Default urllib follows 30x silently; a draft containing a redirect
    chain via attacker.example -> 169.254.169.254 would let preflight
    probe internal hosts. Refuse on the first hop; treat as broken link.
    """
    def http_error_301(self, req, fp, code, msg, headers):  # noqa: D401
        return None
    http_error_302 = http_error_301
    http_error_303 = http_error_301
    http_error_307 = http_error_301
    http_error_308 = http_error_301


_PREFLIGHT_NO_REDIRECT_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}), _PreflightNoRedirectHandler())


# Why the last probe of a URL produced no HTTP response (status 0), keyed by
# URL. Gate 5 reads it to tell a network or DNS problem from a dead link while
# ``_http_head`` keeps returning a plain int.
_HTTP_FAILURE_REASONS: dict[str, str] = {}


def _describe_network_failure(exc: BaseException) -> str:
    reason = exc.reason if isinstance(exc, urllib.error.URLError) else exc
    if isinstance(reason, socket.gaierror):
        return "DNS lookup failed"
    if isinstance(reason, (socket.timeout, TimeoutError)):
        return f"timed out after {HEAD_TIMEOUT}s"
    if isinstance(reason, ConnectionRefusedError):
        return "connection refused"
    if isinstance(reason, OSError):
        return f"connection error ({type(reason).__name__})"
    return type(reason).__name__


def _http_request_status(
    url: str,
    *,
    method: str,
    headers: dict[str, str] | None = None,
) -> tuple[int, str | None]:
    """Return one HTTP status and Location without following redirects."""
    ok, _reason, host, port, infos = _resolve_public_http_url(url)
    if not ok or host is None or port is None:
        _HTTP_FAILURE_REASONS[url] = _reason or "URL refused"
        return 0, None
    request_headers = {"User-Agent": USER_AGENT, **(headers or {})}
    req = urllib.request.Request(url, method=method, headers=request_headers)
    try:
        with _PinnedDNS(host, port, infos):
            with _PREFLIGHT_NO_REDIRECT_OPENER.open(req, timeout=HEAD_TIMEOUT) as resp:
                if method == "GET":
                    resp.read(1)
                response_headers = getattr(resp, "headers", {})
                return int(getattr(resp, "status", 200)), response_headers.get("Location")
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.headers.get("Location") if exc.headers else None
    except Exception as exc:
        _HTTP_FAILURE_REASONS[url] = _describe_network_failure(exc)
        return 0, None


def _http_head(url: str) -> int:
    """Probe a URL with HEAD, then a bounded GET when HEAD is blocked.

    Redirects are never followed. A 3xx is returned only when its Location
    resolves to another public http(s) URL. This keeps redirect and DNS safety
    checks in force while allowing valid redirect responses under Gate 5.
    """
    status, location = _http_request_status(url, method="HEAD")
    if status in {403, 405}:
        status, location = _http_request_status(
            url,
            method="GET",
            headers={"Range": "bytes=0-0"},
        )
    if 300 <= status < 400:
        if not location:
            _HTTP_FAILURE_REASONS[url] = "redirect without a Location header"
            return 0
        redirect_url = urllib.parse.urljoin(url, location)
        safe, _reason = _safe_http_url(redirect_url)
        if not safe:
            _HTTP_FAILURE_REASONS[url] = f"redirect refused ({_reason})"
            return 0
    return status


def _jsonld_nodes(value: Any) -> list[dict[str, Any]]:
    """Flatten JSON-LD arrays and @graph containers."""
    nodes: list[dict[str, Any]] = []
    if isinstance(value, list):
        for item in value:
            nodes.extend(_jsonld_nodes(item))
    elif isinstance(value, dict):
        graph = value.get("@graph")
        if isinstance(graph, list):
            nodes.extend(_jsonld_nodes(graph))
        nodes.append(value)
    return nodes


def _is_blogposting_node(node: dict[str, Any]) -> bool:
    node_type = node.get("@type")
    if node_type == "BlogPosting":
        return True
    if isinstance(node_type, list) and "BlogPosting" in node_type:
        return True
    return False


def _parse_jsonld_blocks(blocks: list[str]) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse each JSON-LD block alone; return flattened nodes and per-block errors."""
    nodes: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, block in enumerate(blocks, start=1):
        try:
            nodes.extend(_jsonld_nodes(json.loads(block)))
        except ValueError as exc:
            errors.append(f"block {index} of {len(blocks)} invalid: {exc}")
    return nodes, errors


def _iter_tags(data: bytes):
    """Yield (offset, name, text) for each start tag, in one linear pass.

    ``text`` runs from the tag name to the first ``>``. A tag with no closing
    ``>`` ends the scan, because no later tag could close either.
    """
    tag_start = re.compile(br"<(\w+)")
    position = 0
    while True:
        begin = data.find(b"<", position)
        if begin < 0:
            return
        name = tag_start.match(data, begin)
        close = data.find(b">", begin)
        if close < 0:
            return
        if name:
            yield begin, name.group(1), data[begin:close + 1]
        position = close + 1


_URI_RUN = re.compile(r"[^\"'\s>]+")
_BASE64_TAIL = re.compile(r"[a-z0-9+/=]+", re.IGNORECASE)


def _base64_uri_bytes(text: str) -> int:
    """Count bytes of ``data:...;base64,<payload>`` URIs, one linear pass.

    Splits on the URI delimiters first so a run of repeated ``data:`` cannot
    make a single regex rescan the rest of the file from every start.
    """
    total = 0
    for run in _URI_RUN.finditer(text):
        value = run.group(0)
        begin = value.find("data:")
        marker = value.rfind(";base64,")
        if begin < 0 or marker < begin + 6:
            continue
        tail = _BASE64_TAIL.match(value, marker + len(";base64,"))
        if tail:
            total += len(value[begin:tail.end()].encode("utf-8"))
    return total


_INLINE_OPEN = re.compile(r"<(?:style|script)\b", re.IGNORECASE)
_INLINE_CLOSE = re.compile(r"</(?:style|script)\s*>", re.IGNORECASE)
_SRC_ATTRIBUTE = re.compile(r"\bsrc\s*=", re.IGNORECASE)


def _inline_block_bytes(text: str) -> int:
    """Count bytes in inline <style>/<script> blocks (those without src=).

    Linear: each open tag is paired with the next closer after it, and the
    scan stops at the first opener that has no closer or no ``>``.
    """
    total = 0
    position = 0
    while True:
        opener = _INLINE_OPEN.search(text, position)
        if opener is None:
            return total
        tag_end = text.find(">", opener.end())
        if tag_end < 0:
            return total
        if _SRC_ATTRIBUTE.search(text, opener.start(), tag_end):
            position = tag_end + 1
            continue
        closer = _INLINE_CLOSE.search(text, tag_end + 1)
        if closer is None:
            return total
        total += len(text[opener.start():closer.end()].encode("utf-8"))
        position = closer.end()


def _googlebot_html_prefix_check(raw_bytes: bytes) -> dict[str, Any]:
    """Check whether critical HTML exists only after Googlebot's 2MB cutoff.

    The byte limit is a fetch/indexing constraint, not a ranking factor. A
    critical component found only after the limit is a crawl warning, not a
    publication blocker. Missing components everywhere remain the
    responsibility of Gate 5's existing semantic checks.
    """
    prefix = raw_bytes[:GOOGLEBOT_HTML_BYTE_LIMIT].lower()
    full = raw_bytes.lower()
    limit = len(prefix)
    attribute_patterns = {
        "meta": re.compile(
            br"(?:name|property)\s*=\s*[\"']"
            br"(?:description|robots|googlebot|og:[^\"']+)[\"']"
        ),
        "canonical": re.compile(
            br"rel\s*=\s*[\"'][^\"']*\bcanonical\b[^\"']*[\"']"
        ),
        "json_ld": re.compile(
            br"type\s*=\s*[\"']application/ld\+json[\"']"
        ),
    }
    tag_kinds = {b"title": "title", b"meta": "meta", b"link": "canonical",
                 b"script": "json_ld", b"main": "main_content", b"article": "main_content"}
    # One linear pass over the tags. Per-pattern `[^>]*` regexes rescan to the
    # end of the file from every unterminated "<meta" or "<script", which made
    # long repeats quadratic.
    positions: dict[str, int | None] = {name: None for name in
                                         ("title", "meta", "canonical", "json_ld", "main_content")}
    in_prefix: set[str] = set()
    for start, tag_name, tag_text in _iter_tags(full):
        kind = tag_kinds.get(tag_name)
        if kind is None:
            continue
        pattern = attribute_patterns.get(kind)
        match = pattern.search(tag_text) if pattern else True
        if not match:
            continue
        end = start + (match.end() if pattern else len(tag_name) + 1)
        if positions[kind] is None:
            positions[kind] = start
        if end <= limit:
            in_prefix.add(kind)
    after_cutoff: list[str] = [
        name for name, position in positions.items()
        if position is not None and name not in in_prefix
    ]

    prefix_text = prefix.decode("utf-8", errors="ignore")
    inline_bytes = _base64_uri_bytes(prefix_text) + _inline_block_bytes(prefix_text)

    violations: list[str] = []
    warnings = [
        f"Googlebot first-2MB cutoff may hide critical {name.replace('_', ' ')} content"
        for name in after_cutoff
    ]
    if inline_bytes > INLINE_BLOAT_WARNING_BYTES:
        warnings.append(
            "excessive inline base64/CSS/JS before critical content "
            f"({inline_bytes} bytes); reduce HTML bloat. This is a crawl "
            "visibility warning, not a ranking factor"
        )
    return {
        "limit_bytes": GOOGLEBOT_HTML_BYTE_LIMIT,
        "artifact_bytes": len(raw_bytes),
        "critical_positions": positions,
        "critical_after_cutoff": after_cutoff,
        "inline_bloat_bytes": inline_bytes,
        "violations": violations,
        "warnings": warnings,
    }


def _discover_target_signal(draft_dir: Path) -> tuple[bool, str | None]:
    """Return whether Discover checks were explicitly requested."""
    path = draft_dir / PREFLIGHT_TARGETS_FILE
    if not path.is_file() or path.is_symlink():
        return False, None
    try:
        data = json.loads(_read_text_no_follow(path))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return False, f"{PREFLIGHT_TARGETS_FILE} ignored: {exc}"
    if not isinstance(data, dict):
        return False, f"{PREFLIGHT_TARGETS_FILE} ignored: top level must be a JSON object"
    targets = data.get("targets", [])
    explicit_target = isinstance(targets, list) and any(
        str(item).strip().lower() == "discover" for item in targets
    )
    has_data = data.get("has_discover_data") is True
    return explicit_target or has_data or data.get("discover") is True, None


def _discover_preflight_check(parser: _MetaParser, enabled: bool) -> dict[str, Any]:
    """Validate preferred-image hints only for an explicit Discover target."""
    if not enabled:
        return {"enabled": False, "warnings": []}
    warnings: list[str] = []
    width = parser.og_image_width
    height = parser.og_image_height
    if not parser.og_image:
        warnings.append("Discover target has no og:image preferred-image declaration")
    if width is None or height is None:
        warnings.append("Discover target is missing og:image width/height metadata")
    else:
        if width < 1200:
            warnings.append(f"Discover preferred image width is {width}px; target at least 1200px")
        if width * height <= 300_000:
            warnings.append(
                f"Discover preferred image has {width * height} pixels; target more than 300000"
            )
        ratio = width / height if height else 0
        if ratio and not 1.6 <= ratio <= 1.9:
            warnings.append("Discover preferred image is not near a useful 16:9 landscape crop")
    preview_allowed = parser.has_amp or any(
        "max-image-preview:large" in value.lower() for value in parser.robots_content
    )
    if not preview_allowed:
        warnings.append(
            "Discover target does not enable max-image-preview:large and is not AMP"
        )
    return {
        "enabled": True,
        "preferred_image": parser.og_image,
        "width": width,
        "height": height,
        "warnings": warnings,
    }


def _classify_back_button_behavior(observation: dict[str, Any]) -> dict[str, Any]:
    """Classify observed navigation behavior without scanning for API syntax."""
    attempted = observation.get("attempted_back") is True
    conclusive = observation.get("observation_complete") is True
    returned = observation.get("returned_to_previous") is True
    obstructed = attempted and conclusive and not returned
    return {
        "checked": attempted,
        "conclusive": conclusive,
        "obstructed": obstructed,
        "violation": (
            "back-button navigation was behaviorally obstructed; review page, "
            "library, and advertising history manipulation"
            if obstructed
            else None
        ),
    }


NETWORK_REASON_PREFIXES = ("DNS", "timed out", "connection")


def _is_network_reason(reason: str | None) -> bool:
    return bool(reason) and reason.startswith(NETWORK_REASON_PREFIXES)


def _network_hint(url: str) -> str:
    return (
        "This may be a network or DNS problem on this machine rather than a dead link: run "
        f"`curl -I {url}` here to tell, or re-run the gates on a working connection"
    )


def _external_failure_message(kind: str, url: str, status: int) -> tuple[str, bool]:
    """Describe a failed probe; the bool marks failures that look like network trouble."""
    if status != 0:
        return f"{kind} returned {status}: {url}", False
    reason = _HTTP_FAILURE_REASONS.get(url, "no HTTP response")
    network = _is_network_reason(reason)
    detail = _network_hint(url) if network else "The server did not give a usable response; open it in a browser to check"
    return f"{kind} could not be checked ({reason}): {url}. {detail}", network


def _structure_findings(audit: "_DocumentAudit") -> tuple[list[str], list[str]]:
    """Document-structure checks shared with search and accessibility basics."""
    violations: list[str] = []
    warnings: list[str] = []
    if not audit.lang:
        violations.append(
            '<html> has no lang attribute; add lang="en" (or the article language) to the opening <html> tag'
        )
    if not "".join(audit.title).strip():
        violations.append("<title> is missing or empty in <head>; add the article title")
    description = next((d.strip() for d in audit.descriptions if d.strip()), "")
    if not description:
        violations.append(
            '<meta name="description"> is missing or empty; add a '
            f"{DESCRIPTION_RANGE[0]} to {DESCRIPTION_RANGE[1]} character summary of the article"
        )
    elif not DESCRIPTION_RANGE[0] <= len(description) <= DESCRIPTION_RANGE[1]:
        warnings.append(
            f'<meta name="description"> is {len(description)} characters; aim for '
            f"{DESCRIPTION_RANGE[0]} to {DESCRIPTION_RANGE[1]}"
        )
    h1s = [text for level, text in audit.headings if level == 1]
    if not h1s:
        violations.append("no <h1> in the document; add exactly one <h1> holding the article headline")
    elif len(h1s) > 1:
        shown = ", ".join(f'"{text}"' for text in h1s[:3])
        violations.append(
            f"{len(h1s)} <h1> elements found ({shown}); keep exactly one and demote the rest to <h2>"
        )
    skips = []
    previous = None
    for level, text in audit.headings:
        if previous is not None and level > previous + 1:
            skips.append(
                f'heading level skips from <h{previous}> to <h{level}> at "{text}"; '
                f"use <h{previous + 1}> or restructure the sections"
            )
        previous = level
    violations.extend(_limited(skips, "heading level skip(s)"))
    for prop in ("og:title", "og:description", "og:image"):
        if not (audit.og.get(prop) or "").strip():
            violations.append(f'<meta property="{prop}"> is missing or empty; add it for social previews')
    for tag in audit.noindex:
        violations.append(f"{tag} blocks indexing; remove noindex before publishing")
    missing_alt: list[str] = []
    for img in audit.imgs:
        alt = img["alt"]
        decorative = (img["role"] or "").strip().lower() in {"presentation", "none"} or (
            (img["aria-hidden"] or "").strip().lower() == "true"
        )
        if alt is None:
            missing_alt.append(
                f"{img['label']} src=\"{_snippet(img['src'], 50)}\" has no alt attribute; add descriptive alt "
                'text (or alt="" with role="presentation" for a purely decorative image)'
            )
        elif not alt.strip() and not decorative:
            warnings.append(
                f"{img['label']} src=\"{_snippet(img['src'], 50)}\" has empty alt text; describe the image, or "
                'add role="presentation" if it is decorative'
            )
    violations.extend(_limited(missing_alt, "image(s) without alt"))
    return violations, warnings


def gate_5_asset_link_integrity(
    draft_dir: Path,
    slug: str | None = None,
    rendered_schema_validation: dict[str, Any] | None = None,
) -> dict:
    """Verify image resolution, safe external-link responses and schema,
    word count within +/-5%."""
    _stem, selected, artifact_violations = _select_artifact_stem(draft_dir, slug)
    htmls = selected["html"]
    if not htmls:
        return _gate_result(5, "Asset + Link Integrity", False, ["no .html artifact to verify"])
    if artifact_violations:
        return _gate_result(5, "Asset + Link Integrity", False, artifact_violations)

    html_path = htmls[0]
    try:
        raw_bytes = _read_bytes_no_follow(html_path)
        raw = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        # A ValueError subclass, so it must be caught before the ValueError branch.
        return _gate_result(5, "Asset + Link Integrity", False, [f"html artifact is not valid UTF-8: {e}"])
    except (OSError, ValueError) as e:
        return _gate_result(5, "Asset + Link Integrity", False, [f"html artifact unreadable: {e}"])
    parser = _MetaParser()
    parser.feed(raw)

    violations = []
    warnings = []
    allowed_status_urls, exception_config_violations = _load_external_link_exceptions(draft_dir)
    violations.extend(exception_config_violations)
    if (draft_dir / LEGACY_ALLOWLIST_FILE).exists():
        warnings.append(
            f"{LEGACY_ALLOWLIST_FILE} is no longer read and exempts nothing; "
            f"use {EXTERNAL_LINKS_ALLOWED_FILE} (exact URLs, 403/405 only)"
        )
    byte_check = _googlebot_html_prefix_check(raw_bytes)
    violations.extend(byte_check["violations"])
    warnings.extend(byte_check["warnings"])
    discover_enabled, discover_config_warning = _discover_target_signal(draft_dir)
    if discover_config_warning:
        warnings.append(discover_config_warning)
    discover_check = _discover_preflight_check(parser, discover_enabled)
    warnings.extend(discover_check["warnings"])

    _HTTP_FAILURE_REASONS.clear()
    network_failures: list[str] = []
    external_checked = 0

    # canonical first: relative image URLs and og:url resolve against it, so a
    # missing canonical is the cause of several later mismatches.
    if not parser.canonical:
        violations.append(
            "no <link rel=canonical> in document; relative image URLs and Open Graph URLs cannot be matched "
            f"without it. Fix: {CANONICAL_FIX}"
        )
    else:
        ok, reason = _well_formed_http_url(parser.canonical)
        if not ok:
            violations.append(f"canonical URL invalid or unsafe: {parser.canonical} ({reason})")

    # img src resolution
    for src in parser.imgs:
        if src.startswith("http://") or src.startswith("https://"):
            ok, reason = _safe_http_url(src)
            if not ok:
                if reason and reason.startswith("DNS"):
                    network_failures.append(src)
                    external_checked += 1
                    violations.append(
                        f"img src could not be resolved: {src} ({reason}). {_network_hint(src)}"
                    )
                else:
                    violations.append(f"img src refused by URL safety policy: {src} ({reason})")
                continue
            external_checked += 1
            status = _http_head(src)
            if not 200 <= status < 400:
                message, network = _external_failure_message("img src", src, status)
                violations.append(message)
                if network:
                    network_failures.append(src)
        else:
            local, local_error = _safe_local_path(draft_dir, src)
            if local_error:
                violations.append(f"img src invalid local path: {src} ({local_error})")
                continue
            if not local.exists():
                violations.append(f"img src not on disk: {src}")
            elif local.is_symlink():
                violations.append(f"img src is a symlink: {src}")

    # og:image specifically must resolve to a local hero.<ext> when canonical points to a host
    if parser.og_image:
        if parser.og_image.startswith(("http://", "https://")):
            hero_files = list(draft_dir.glob("hero.*"))
            hero_files = [h for h in hero_files if h.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
            if not hero_files:
                violations.append(f"og:image declared {parser.og_image} but no hero.<ext> exists locally")

    # External links: explicit http/https allowlist. Other schemes (file://,
    # gopher://, ftp://, javascript:) are flagged as violations rather than
    # silently skipped (S3 from v1.9.0 hostile review). Relative/anchor links
    # without a scheme are left to Gate 5's img-src check above.
    generated_skipped = 0
    for href, generated in zip(parser.links, parser.link_generated):
        if href.startswith(("http://", "https://")):
            if generated:
                # The renderer's own footer link: validate scheme, host and port
                # (and refuse a literal non-public IP) but never fetch it, so a
                # fully local article passes offline.
                ok, reason = _well_formed_http_url(href)
                if ok:
                    try:
                        literal = ipaddress.ip_address(urllib.parse.urlparse(href).hostname or "")
                        ok = literal.is_global and not (literal.is_loopback or literal.is_multicast)
                        reason = f"address is not public: {literal}"
                    except ValueError:
                        pass
                if not ok:
                    violations.append(f"link refused by URL safety policy: {href} ({reason})")
                else:
                    generated_skipped += 1
                continue
            ok, reason = _safe_http_url(href)
            if not ok:
                if reason and reason.startswith("DNS"):
                    network_failures.append(href)
                    external_checked += 1
                    violations.append(
                        f"link could not be resolved: {href} ({reason}). {_network_hint(href)}"
                    )
                else:
                    violations.append(f"link refused by URL safety policy: {href} ({reason})")
                continue
            external_checked += 1
            status = _http_head(href)
            if 200 <= status < 400:
                continue
            normalized_href = _normalize_external_url(href)
            if status in {403, 405} and normalized_href in allowed_status_urls:
                warnings.append(
                    f"link returned documented {status} and is allowed by "
                    f"{EXTERNAL_LINKS_ALLOWED_FILE}: {href}"
                )
                continue
            message, network = _external_failure_message("link", href, status)
            violations.append(message)
            if network:
                network_failures.append(href)
            continue
        if href.lower().startswith("mailto:"):
            # Matches blog_render's SAFE_LINK_SCHEMES: mail links are not network fetches.
            continue
        if "://" in href or href.startswith(("javascript:", "data:", "vbscript:")):
            violations.append(
                f"non-http(s) URL scheme is not allowed in published links: {href}"
            )
            continue
        if href.startswith("#"):
            target = urllib.parse.unquote(href[1:])
            if target and target not in parser.ids:
                violations.append(f"anchor link target missing: {href}")
            continue
        if href:
            local_href, local_error = _safe_local_path(draft_dir, href)
            if local_error:
                violations.append(f"local link invalid path: {href} ({local_error})")
                continue
            if not local_href.exists():
                violations.append(f"local link not on disk: {href}")
    if external_checked and len(network_failures) == external_checked:
        warnings.append(
            f"all {external_checked} external check(s) failed at the network level; this machine may be offline "
            "or behind a proxy, so these failures may not be dead links"
        )

    # JSON-LD validation. Prefer source markup when valid, but accept an
    # in-process Gate 3 proof of valid, visible-content-consistent rendered-DOM
    # markup. Never trust a persisted draft-side claim for this handoff.
    json_ld_ok = False
    declared_word_count: Optional[int] = None
    schema_validation_source = "source_html"
    schema_violations: list[str] = []
    if parser.json_ld_blocks:
        nodes, block_errors = _parse_jsonld_blocks(parser.json_ld_blocks)
        multiple = len(parser.json_ld_blocks) > 1
        if block_errors:
            schema_violations.append("JSON-LD invalid: " + "; ".join(block_errors))
        else:
            obj = next((node for node in nodes if _is_blogposting_node(node)), None)
            if obj is None:
                schema_violations.append("JSON-LD missing BlogPosting node")
                obj = {}
            json_ld_ok = True
            where = " (across %d JSON-LD blocks)" % len(parser.json_ld_blocks) if multiple else ""
            required = ("headline", "image", "datePublished", "author")
            missing = [k for k in required if not obj.get(k)]
            if missing:
                schema_violations.append(f"JSON-LD missing required fields: {missing}{where}")
            identity_report = _jsonld_identity_report(raw, obj, nodes)
            if identity_report:
                schema_violations.append(
                    f"JSON-LD does not match visible content: {_describe_identity_mismatches(identity_report)}{where}"
                )
            declared_word_count = obj.get("wordCount")
            if not isinstance(declared_word_count, int):
                schema_violations.append("JSON-LD wordCount must be an integer")
    else:
        schema_violations.append("no source JSON-LD <script> block present")

    rendered_valid = (
        isinstance(rendered_schema_validation, dict)
        and rendered_schema_validation.get("available") is True
        and rendered_schema_validation.get("valid") is True
        and rendered_schema_validation.get("source") == "rendered_dom"
    )
    if schema_violations and rendered_valid:
        json_ld_ok = True
        schema_validation_source = "rendered_dom"
        rendered_word_count = rendered_schema_validation.get("word_count")
        declared_word_count = (
            rendered_word_count if isinstance(rendered_word_count, int) else None
        )
        warnings.append(
            "source JSON-LD was absent or invalid; accepted JSON-LD validated "
            "in the rendered DOM by Gate 3"
        )
        schema_violations = []
    else:
        violations.extend(schema_violations)

    # word count match: against <article>, else <main>; with neither region
    # the declared count cannot be checked, so fail closed.
    if parser.saw_article:
        actual = parser.article_text_chars
        region = "<article>"
    elif parser.saw_main:
        actual = parser.main_text_chars
        region = "<main>"
    else:
        actual = 0
        region = None
    if isinstance(declared_word_count, int):
        if region is None:
            violations.append(
                f"JSON-LD wordCount {declared_word_count} cannot be verified: "
                "no <article> or <main> content region in the document"
            )
        elif actual > 0:
            diff_pct = abs(declared_word_count - actual) / actual * 100
            if diff_pct > 5:
                violations.append(f"JSON-LD wordCount {declared_word_count} differs from actual {actual} by {diff_pct:.1f}%")
        elif declared_word_count != 0:
            violations.append(f"JSON-LD wordCount {declared_word_count} differs from actual 0 in {region}")

    return _gate_result(
        5, "Asset + Link Integrity", not violations, violations, warnings,
        imgs=parser.imgs, links_checked=len(parser.links),
        generated_links_skipped=generated_skipped,
        json_ld_valid=json_ld_ok, declared_word_count=declared_word_count,
        schema_validation_source=schema_validation_source,
        actual_word_count=actual,
        googlebot_byte_check={
            key: value for key, value in byte_check.items()
            if key not in {"violations", "warnings"}
        },
        discover_check={
            key: value for key, value in discover_check.items()
            if key != "warnings"
        },
    )


# Category maxima from the reviewer rubric (agents/blog-reviewer.md and
# skills/blog/references/quality-scoring.md); they sum to the 100-point total.
REVIEW_CATEGORY_MAX = {
    "Content Quality": 30,
    "SEO Optimization": 25,
    "E-E-A-T Signals": 15,
    "Technical Elements": 15,
    "AI Citation Readiness": 15,
}


def _category_score_violations(text: str, overall: int) -> list[str]:
    """Check reviewer category scores against the rubric and the overall score.

    Reads `Category: N/MAX` and `| Category | N | MAX |` forms. Absent
    categories are allowed (older reviews carry only the overall line), but
    every present score must fit its rubric maximum and the overall must lie
    between the sum of the stated scores and that sum plus the maxima of the
    categories not stated. With all five present this means overall == sum.
    """
    violations: list[str] = []
    found: dict[str, float] = {}
    for name, maximum in REVIEW_CATEGORY_MAX.items():
        number = r"(\d{1,3}(?:\.\d+)?)(?![\d.])"
        pattern = re.compile(
            re.escape(name) + r"(?:[ \t]*\([ \t]*\d+[ \t]*(?:pts?|points?)[ \t]*\))?[ \t]*[:|][ \t]*" + number
            + r"(?:[ \t]*[/|][ \t]*" + number + ")?",
            re.IGNORECASE,
        )
        values = {(float(m.group(1)), float(m.group(2)) if m.group(2) else None) for m in pattern.finditer(text)}
        if not values:
            continue
        if len({value for value, _stated in values}) > 1:
            violations.append(f"review.md contains conflicting {name} scores")
            continue
        value, stated = next(iter(values))
        stated_maxima = {stated for _value, stated in values if stated is not None}
        if stated_maxima - {maximum}:
            violations.append(f"review {name} maximum {sorted(stated_maxima)[0]:g} does not match the rubric maximum {maximum}")
        elif value > maximum:
            violations.append(f"review {name} score {value:g}/{maximum} exceeds its maximum")
        else:
            found[name] = value
    if found and not violations:
        floor = sum(found.values())
        ceiling = floor + sum(m for n, m in REVIEW_CATEGORY_MAX.items() if n not in found)
        if not floor - 1e-9 <= overall <= ceiling + 1e-9:
            violations.append(
                f"review overall score {overall}/100 is inconsistent with its category scores "
                f"(stated categories sum to {floor:g}; overall must be between {floor:g} and {ceiling:g})"
            )
    return violations


def gate_4_content_review(draft_dir: Path) -> dict:
    """Check that the blog-reviewer agent has run and emitted review.md
    with `BLOCKING: false`, a matching Nonce, and a machine-checkable score.

    Editorial style diagnostics such as phrase counts, type-token ratio, and
    sentence-length variance are never authorship classifiers or blocking
    metrics. Gate 4 blocks on the score, P0 defects, provenance, or the
    reviewer's explicit decision.
    """
    review = draft_dir / "review.md"
    if not review.is_file():
        return _gate_result(
            4, "Content Review", False,
            ["review.md absent; orchestrator must dispatch blog-reviewer agent before preflight Gate 4"],
        )
    try:
        text = _read_text_no_follow(review)
    except (OSError, ValueError) as e:
        return _gate_result(4, "Content Review", False, [f"review.md unreadable: {e}"])

    expected_nonce, nonce_error = _read_expected_review_nonce(draft_dir)
    if nonce_error or expected_nonce is None:
        return _gate_result(4, "Content Review", False, [nonce_error or "review verifier state missing"])
    nonce_matches = list(NONCE_PATTERN.finditer(text))
    nonce_fields = re.findall(r"^\s*Nonce:", text, re.MULTILINE | re.IGNORECASE)
    if len(nonce_fields) > 1:
        return _gate_result(4, "Content Review", False, ["review.md contains duplicate or conflicting Nonce fields"])
    nonce_match = nonce_matches[0] if len(nonce_matches) == 1 else None
    if not nonce_match:
        return _gate_result(
            4, "Content Review", False,
            [
                "review.md is missing the `Nonce: <hex>` line required for provenance. "
                "The orchestrator must pass the nonce printed by --init-review-nonce "
                "to the blog-reviewer agent."
            ],
        )
    actual_nonce = nonce_match.group(1).lower()
    if actual_nonce != expected_nonce:
        return _gate_result(
            4, "Content Review", False,
            ["review.md Nonce does not match external verifier state; provenance check failed"],
        )
    stale_violations, stale_warnings, stale_files = _review_staleness(draft_dir)
    if stale_violations:
        # The review judged different artifacts, so its score and decision say
        # nothing about this draft. Report the cause alone.
        return _gate_result(
            4, "Content Review", False, stale_violations, stale_warnings,
            stale_artifacts=stale_files,
        )

    non_empty = [line.strip() for line in text.splitlines() if line.strip()]
    if not non_empty:
        return _gate_result(4, "Content Review", False, ["review.md is empty"])
    final_match = BLOCKING_PATTERN.fullmatch(non_empty[-1])
    all_decisions = [BLOCKING_PATTERN.fullmatch(line) for line in non_empty]
    all_decisions = [m for m in all_decisions if m is not None]
    if not final_match:
        return _gate_result(
            4, "Content Review", False,
            ["review.md last non-empty line must be `BLOCKING: true|false (reason)`"],
        )
    if {m.group(1).lower() for m in all_decisions} == {"true", "false"}:
        return _gate_result(
            4, "Content Review", False,
            ["review.md contains conflicting BLOCKING decisions"],
        )

    decision_fields = [line for line in non_empty if re.match(r"^BLOCKING:", line, re.IGNORECASE)]
    if len(decision_fields) != 1:
        return _gate_result(4, "Content Review", False, ["review.md must contain exactly one final BLOCKING decision"])
    blocking = final_match.group(1).lower() == "true"
    reason = (final_match.group(2) or "").strip()
    if not reason:
        return _gate_result(4, "Content Review", False, ["review.md final BLOCKING decision requires a non-empty reason"])
    if blocking:
        return _gate_result(
            4, "Content Review", False,
            [f"reviewer blocked: {reason or 'see review.md'}"],
            blocking=True, reason=reason,
        )
    metric_violations: list[str] = []
    score_matches = list(re.finditer(r"Overall Score:\s*(\d{1,3})\s*/\s*100", text, re.IGNORECASE))
    score_fields = re.findall(r"Overall Score:", text, re.IGNORECASE)
    score_match = score_matches[0] if len(score_matches) == 1 and len(score_fields) == 1 else None
    if len(score_fields) > 1:
        metric_violations.append("review.md contains duplicate or conflicting Overall Score fields")
    if not score_match:
        metric_violations.append("review.md missing machine-readable Overall Score: N/100")
        score = None
    else:
        score = int(score_match.group(1))
        if score < 0 or score > 100:
            metric_violations.append(f"review overall score {score}/100 is outside 0..100")
        elif score < 90:
            metric_violations.append(f"review overall score {score}/100 is below 90")

    if score is not None and 0 <= score <= 100:
        metric_violations.extend(_category_score_violations(text, score))

    # Accept the existing no/zero P0 forms only as affirmative fields or
    # complete decision clauses. Substring matching would accept negation
    # such as "There are not zero P0 issues" or "zero P0 issues except ...".
    clearance_field = re.compile(
        r"(?:[-*]\s+)?(?:no|zero)\s+P0s?(?:\s+issues?)?"
        r"(?:\s+(?:found|remain|remaining|outstanding))?[.!]?",
        re.IGNORECASE,
    )
    affirmative_lines = {line for line in non_empty if clearance_field.fullmatch(line)}
    decision_clauses = [clause.strip() for clause in re.split(r"[;,]", reason)]
    affirmative_clauses = [clause for clause in decision_clauses if clearance_field.fullmatch(clause)]
    if not affirmative_lines and not affirmative_clauses:
        metric_violations.append("review missing an explicit affirmative no/zero P0 clearance")
    else:
        for line in non_empty:
            if line in affirmative_lines:
                continue
            if line == non_empty[-1]:
                remainder = reason
                for clause in affirmative_clauses:
                    remainder = remainder.replace(clause, "", 1)
            else:
                remainder = line
            if re.search(r"\bP0s?\b", remainder, re.IGNORECASE):
                if not re.match(r"^(?:[-*]\s*)?(?:resolved|cleared|fixed)\s+P0\s*:", line, re.IGNORECASE):
                    metric_violations.append("review mentions P0 without a no/zero P0 clearance for that finding")
                    break

    if metric_violations:
        return _gate_result(4, "Content Review", False, metric_violations, blocking=False, reason=reason, score=score)

    return _gate_result(
        4, "Content Review", True, [], stale_warnings,
        blocking=False, reason=reason, score=score,
    )


GATE_NAMES = {
    1: "Capability Discovery",
    2: "Format Completeness",
    3: "Visual Verification",
    4: "Content Review",
    5: "Asset + Link Integrity",
}


def _incomplete_report(draft: Path, strict: bool, reason: str) -> dict[str, Any]:
    """Blocked placeholder report written before any gate runs."""
    return {
        "draft": str(draft),
        "strict": strict,
        "blocked": True,
        "incomplete": True,
        "reason": reason,
        "gates": [],
    }


def _previous_report_gates(report_path: Path) -> list[Any]:
    """Gates of the last complete run, carried across a cap or crash marker."""
    try:
        if report_path.is_symlink():
            return []
        data = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(data, dict):
        return []
    gates = data.get("gates")
    if isinstance(gates, list) and gates:
        return gates
    carried = data.get("previous_gates")
    return carried if isinstance(carried, list) else []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--draft", required=True, help="Draft folder containing the .md/.html/.pdf/hero artifacts")
    parser.add_argument("--gate", type=int, choices=[1, 2, 3, 4, 5], help="Run only this gate (default: all)")
    parser.add_argument("--slug", help="Require all source/rendered artifacts to match this stem")
    parser.add_argument("--strict", dest="strict", action="store_true", default=True)
    parser.add_argument("--no-strict", dest="strict", action="store_false")
    parser.add_argument("--json", action="store_true", help="Emit report JSON to stdout")
    parser.add_argument("--tools-json", help="JSON list/object of live tool names supplied by the orchestrator")
    parser.add_argument("--diagnostics-all", action="store_true", help="Run later gates after a failure for diagnostics")
    parser.add_argument("--repair-attempt", action="store_true", help="Increment the repair iteration counter for orchestrator repair loops")
    parser.add_argument(
        "--reset-iterations",
        action="store_true",
        help="Reset the per-draft iteration counter to 0 (the next --repair-attempt counts as the first).",
    )
    parser.add_argument(
        "--init-review-nonce",
        action="store_true",
        help=(
            "Generate a fresh CSPRNG nonce, store verifier state outside the "
            "draft folder, then exit. The "
            "orchestrator passes the printed nonce to blog-reviewer; Gate 4 "
            "verifies review.md contains the matching nonce."
        ),
    )
    args = parser.parse_args()

    draft = Path(args.draft).resolve()
    if not draft.is_dir():
        print(f"ERROR: {draft} is not a directory", file=sys.stderr)
        return 1

    if args.init_review_nonce:
        nonce = _init_review_nonce(draft)
        print(nonce)
        return 0

    # Fail closed from the first moment: a report left by an earlier passing run
    # must not outlive a run that crashes or stops early (iteration cap).
    report_path = draft / "preflight-report.json"
    previous_gates = _previous_report_gates(report_path)
    try:
        started = _incomplete_report(draft, args.strict, "run started and has not finished")
        if previous_gates:
            # Crash safety must not erase the last diagnostic.
            started["previous_gates"] = previous_gates
        _atomic_write_json(report_path, started, indent=2)
    except (OSError, ValueError) as e:
        print(f"ERROR: preflight-report.json write refused: {e}", file=sys.stderr)
        return 1

    # Count only orchestrator repair attempts, not every preflight or single-gate run.
    iteration_exit = _iteration_check(
        draft,
        reset=args.reset_iterations,
        increment=args.repair_attempt,
    )
    if iteration_exit != 0:
        # Keep the diagnostic the cap exists to hand over, but never as a
        # current result: the report stays blocked and incomplete.
        capped = _incomplete_report(
            draft, args.strict,
            "iteration cap exceeded; the last complete run's gates are in previous_gates",
        )
        capped["iteration_cap_exceeded"] = True
        capped["previous_gates"] = previous_gates
        _atomic_write_json(report_path, capped, indent=2)
        return iteration_exit

    live_tools = _parse_tool_names(args.tools_json or os.environ.get("CLAUDE_BLOG_TOOLS_JSON"))
    rendered_context: dict[str, Any] = {}

    def run_gate_3(draft_dir: Path) -> dict:
        result = gate_3_visual_verification(draft_dir, slug=args.slug)
        rendered_context["schema"] = _rendered_jsonld_handoff(result)
        return result

    def run_gate_5(draft_dir: Path) -> dict:
        return gate_5_asset_link_integrity(
            draft_dir,
            slug=args.slug,
            rendered_schema_validation=rendered_context.get("schema"),
        )

    gates = [
        (1, lambda d: gate_1_capability_discovery(d, live_tools=live_tools)),
        (2, lambda d: gate_2_format_completeness(d, slug=args.slug)),
        (3, run_gate_3),
        (4, gate_4_content_review),
        (5, run_gate_5),
    ]
    if args.gate:
        gates = [(n, fn) for (n, fn) in gates if n == args.gate]

    results: list[dict] = []
    blocked = False
    for n, fn in gates:
        try:
            r = fn(draft)
        except Exception as exc:  # a crashed gate is a failed gate, never a traceback
            r = _gate_result(n, GATE_NAMES[n], False, [f"gate {n} crashed: {type(exc).__name__}: {exc}"])
        results.append(r)
        if not r["passed"]:
            blocked = True
            if not args.gate and not args.diagnostics_all:
                break

    report = {
        "draft": str(draft),
        "strict": args.strict,
        "blocked": blocked,
        "gates": results,
    }
    try:
        _atomic_write_json(draft / "preflight-report.json", report, indent=2)
    except (OSError, ValueError) as e:
        print(f"ERROR: preflight-report.json write refused: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report))
    else:
        for r in results:
            mark = "PASS" if r["passed"] else "FAIL"
            print(f"[{mark}] Gate {r['gate']}: {r['name']}")
            for v in r.get("violations", []):
                print(f"       violation: {v}")
            for w in r.get("warnings", []):
                print(f"       warning:   {w}")
        if blocked and not args.strict:
            print("WARNING: contract bypassed via --no-strict; do not publish without manual review.", file=sys.stderr)

    if blocked and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
