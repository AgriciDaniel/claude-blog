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
URL_ALLOWLIST = ("example.com", "example.org")
URL_ALLOWLIST_FILE = "preflight-allowlist.json"
ALLOWED_HTTP_SCHEMES = frozenset({"http", "https"})
GOOGLEBOT_HTML_BYTE_LIMIT = 2 * 1024 * 1024
INLINE_BLOAT_WARNING_BYTES = 256 * 1024
PREFLIGHT_TARGETS_FILE = "preflight-targets.json"

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


def _init_review_nonce(draft: Path) -> str:
    """Generate a CSPRNG nonce and store verifier state outside the draft."""
    import secrets
    nonce = secrets.token_hex(16)
    _atomic_write_json(
        _review_state_path(draft),
        {
            "draft": str(draft.resolve()),
            "nonce": nonce,
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
                violations.append("no slug-matched .md/.html/.pdf artifact set found")
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
    parsed = urllib.parse.urlparse(ref)
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


def _load_unreachable_allowlist(draft_dir: Path) -> set[str]:
    """Load exact host allowlist for links that should not be probed."""
    hosts = set(URL_ALLOWLIST)
    cfg_path = draft_dir / URL_ALLOWLIST_FILE
    if not cfg_path.is_file() or cfg_path.is_symlink():
        return hosts
    try:
        data = json.loads(_read_text_no_follow(cfg_path))
    except (OSError, ValueError, json.JSONDecodeError):
        return hosts
    raw_hosts = data.get("unreachable_hosts") or data.get("hosts") or []
    if isinstance(raw_hosts, list):
        for host in raw_hosts:
            parsed = urllib.parse.urlparse(str(host))
            name = (parsed.hostname or str(host)).strip().lower().rstrip(".")
            if re.fullmatch(r"[a-z0-9.-]+", name):
                hosts.add(name)
    return hosts


def _is_allowed_unreachable(url: str, allowed_hosts: set[str]) -> bool:
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    return host in allowed_hosts


def _resolve_public_http_url(url: str) -> tuple[bool, str | None, str | None, int | None, list[Any]]:
    """Validate URL scheme and resolved addresses before a fetch."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ALLOWED_HTTP_SCHEMES:
        return False, "URL scheme must be http or https", None, None, []
    host = parsed.hostname
    if not host:
        return False, "URL host missing", None, None, []
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
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
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ALLOWED_HTTP_SCHEMES:
        return False, "URL scheme must be http or https"
    if not parsed.hostname:
        return False, "URL host missing"
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
        warnings.append("neither patchright nor playwright installed; Gate 3 will warn-and-pass")
    if not py_deps["weasyprint"] and not py_deps["patchright"] and not py_deps["playwright"]:
        warnings.append("no PDF backend installed (patchright/playwright/weasyprint); PDF generation will fail")

    return _gate_result(1, "Capability Discovery", not violations, violations, warnings, capabilities=capabilities)


def gate_2_format_completeness(draft_dir: Path, slug: str | None = None) -> dict:
    """Verify .md, .html, .pdf, hero.<ext> all exist."""
    stem, selected, artifact_violations = _select_artifact_stem(draft_dir, slug)
    mds = selected["md"]
    htmls = selected["html"]
    pdfs = selected["pdf"]
    heroes = list(draft_dir.glob("hero.*"))
    review = draft_dir / "review.md"

    violations = list(artifact_violations)
    if not mds:
        violations.append("no slug-matched .md source found")
    if not htmls:
        violations.append("no slug-matched .html artifact found (run scripts/blog_render.py)")
    if not pdfs:
        violations.append("no slug-matched .pdf artifact found (run scripts/blog_render.py)")
    hero_files = [h for h in heroes if h.name != "hero-credit.txt" and h.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
    if not hero_files:
        violations.append("no hero.<png|jpg|jpeg|webp> found (run scripts/generate_hero.py)")

    return _gate_result(
        2, "Format Completeness", not violations, violations, [],
        artifacts={
            "slug": stem,
            "md": [str(p.name) for p in mds],
            "html": [str(p.name) for p in htmls],
            "pdf": [str(p.name) for p in pdfs],
            "hero": [str(p.name) for p in hero_files],
            "review_present": review.is_file(),
        },
    )


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
            3, "Visual Verification", True, [],
            ["neither patchright nor playwright installed; skipping visual checks. Run pip install -e .[presentation] to enable."],
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

    bbox_check_js = """
() => {
  const overflows = [];
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
          childBox:{l:r.left,r:r.right,t:r.top,b:r.bottom},
          svgBox:{l:svgBox.left,r:svgBox.right,t:svgBox.top,b:svgBox.bottom}});
      }
    });
  });
  const bg = getComputedStyle(document.body).backgroundColor;
  const jsonLd = document.querySelector('script[type="application/ld+json"]');
  let jsonLdValid = false, jsonLdType = null, jsonLdMissingFields = [];
  let jsonLdVisibleConsistent = false, jsonLdConsistencyMismatches = [];
  let jsonLdWordCount = null;
  if (jsonLd) {
    try {
      const raw = JSON.parse(jsonLd.textContent);
      const nodes = Array.isArray(raw) ? raw : (raw['@graph'] || [raw]);
      const obj = nodes.find((node) => {
        const type = node && node['@type'];
        return type === 'BlogPosting' || (Array.isArray(type) && type.includes('BlogPosting'));
      }) || {};
      jsonLdValid = true;
      jsonLdType = obj['@type'];
      const required = ['headline','image','datePublished','author'];
      jsonLdMissingFields = required.filter(k => !obj[k]);
      jsonLdWordCount = Number.isInteger(obj.wordCount) ? obj.wordCount : null;
      const normalize = (value) => String(value || '').replace(/\\s+/g, ' ').trim().toLowerCase();
      const visibleHeadline = normalize(document.querySelector('h1')?.textContent);
      const schemaHeadline = normalize(obj.headline);
      if (!visibleHeadline || visibleHeadline !== schemaHeadline) {
        jsonLdConsistencyMismatches.push('headline');
      }
      const visibleDate = document.querySelector('time[datetime]')?.getAttribute('datetime');
      if (visibleDate && !String(obj.datePublished || '').startsWith(visibleDate.slice(0, 10))) {
        jsonLdConsistencyMismatches.push('datePublished');
      }
      jsonLdVisibleConsistent = jsonLdConsistencyMismatches.length === 0;
    } catch (e) { jsonLdValid = false; }
  }
  return {
    overflows, bg, jsonLdValid, jsonLdType, jsonLdMissingFields,
    jsonLdVisibleConsistent, jsonLdConsistencyMismatches, jsonLdWordCount
  };
}
""".strip()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for vp in VIEWPORTS:
                context = browser.new_context(viewport={"width": vp["width"], "height": vp["height"]})
                root_resolved = draft_dir.resolve()
                def route_guard(route):
                    req_url = route.request.url
                    parsed = urllib.parse.urlparse(req_url)
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
                page = context.new_page()
                page.route("**/*", route_guard)
                console_errors: list[str] = []
                page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
                page.goto(html_path.resolve().as_uri(), wait_until="networkidle", timeout=30_000)
                screenshot = page.screenshot(full_page=True)
                _atomic_write_bytes(preview_dir / f"{vp['name']}-{vp['width']}.png", screenshot)
                result = page.evaluate(bbox_check_js)
                per_viewport[vp["name"]] = {"result": result, "console_errors": console_errors}
                if result["overflows"]:
                    violations.append(f"{vp['name']}: {len(result['overflows'])} SVG overflow(s)")
                if console_errors:
                    violations.append(f"{vp['name']}: {len(console_errors)} console error(s)")
                if not result["jsonLdValid"]:
                    violations.append(f"{vp['name']}: JSON-LD invalid or missing")
                elif result["jsonLdType"] != "BlogPosting":
                    violations.append(f"{vp['name']}: JSON-LD @type != BlogPosting")
                elif result["jsonLdMissingFields"]:
                    violations.append(f"{vp['name']}: JSON-LD missing fields: {result['jsonLdMissingFields']}")
                elif not result["jsonLdVisibleConsistent"]:
                    violations.append(
                        f"{vp['name']}: JSON-LD does not match visible content: "
                        f"{result['jsonLdConsistencyMismatches']}"
                    )
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
            context = browser.new_context(viewport={"width": 1280, "height": 800}, color_scheme="dark")
            page = context.new_page()
            root_resolved = draft_dir.resolve()
            def dark_route_guard(route):
                req_url = route.request.url
                parsed = urllib.parse.urlparse(req_url)
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
            page.route("**/*", dark_route_guard)
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
        self._in_article = False
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
        elif tag == "article":
            self._in_article = True
        elif tag == "header":
            self._in_header = True
        elif tag == "footer":
            self._in_footer = True
        elif tag == "code":
            self._in_code = True

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_jsonld = False
        elif tag == "article":
            self._in_article = False
        elif tag == "header":
            self._in_header = False
        elif tag == "footer":
            self._in_footer = False
        elif tag == "code":
            self._in_code = False

    def handle_data(self, data):
        if self._in_jsonld:
            self.json_ld_blocks.append(data)
        if self._in_code and self._in_article:
            self.codes.append(data.strip())
        # Count body-only words: exclude <header> (title, byline), <footer>
        # (site/date), and <code> blocks. Aligned with blog_render.py's
        # wordCount semantics so Gate 5 catches real drift, not template
        # boilerplate (v1.9.0 audit fix).
        if (self._in_article and not self._in_code
                and not self._in_header and not self._in_footer):
            self.article_text_chars += len(re.findall(r"\b\w+\b", data))


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


_PREFLIGHT_NO_REDIRECT_OPENER = urllib.request.build_opener(_PreflightNoRedirectHandler())


def _http_head(url: str) -> int:
    """HEAD request with SSRF guards and no redirect following."""
    ok, _reason, host, port, infos = _resolve_public_http_url(url)
    if not ok or host is None or port is None:
        return 0
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
        with _PinnedDNS(host, port, infos):
            with _PREFLIGHT_NO_REDIRECT_OPENER.open(req, timeout=HEAD_TIMEOUT) as resp:
                return resp.status
    except Exception:
        return 0


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


def _googlebot_html_prefix_check(raw_bytes: bytes) -> dict[str, Any]:
    """Check whether critical HTML exists only after Googlebot's 2MB cutoff.

    The byte limit is a fetch/indexing constraint, not a ranking factor. A
    critical component found only after the limit is a crawl warning, not a
    publication blocker. Missing components everywhere remain the
    responsibility of Gate 5's existing semantic checks.
    """
    prefix = raw_bytes[:GOOGLEBOT_HTML_BYTE_LIMIT].lower()
    full = raw_bytes.lower()
    patterns = {
        "title": re.compile(br"<title\b"),
        "meta": re.compile(
            br"<meta\b[^>]*(?:name|property)\s*=\s*[\"']"
            br"(?:description|robots|googlebot|og:[^\"']+)[\"']"
        ),
        "canonical": re.compile(
            br"<link\b[^>]*rel\s*=\s*[\"'][^\"']*\bcanonical\b[^\"']*[\"']"
        ),
        "json_ld": re.compile(
            br"<script\b[^>]*type\s*=\s*[\"']application/ld\+json[\"']"
        ),
        "main_content": re.compile(br"<(?:main|article)\b"),
    }
    after_cutoff: list[str] = []
    positions: dict[str, int | None] = {}
    for name, pattern in patterns.items():
        full_match = pattern.search(full)
        prefix_match = pattern.search(prefix)
        positions[name] = full_match.start() if full_match else None
        if full_match is not None and prefix_match is None:
            after_cutoff.append(name)

    prefix_text = prefix.decode("utf-8", errors="ignore")
    base64_bytes = sum(
        len(match.group(0).encode("utf-8"))
        for match in re.finditer(r"data:[^\"'\s>]+;base64,[a-z0-9+/=]+", prefix_text, re.IGNORECASE)
    )
    inline_bytes = base64_bytes
    for match in re.finditer(
        r"<(?:style|script)\b(?![^>]*\bsrc\s*=)[^>]*>.*?</(?:style|script)\s*>",
        prefix_text,
        re.IGNORECASE | re.DOTALL,
    ):
        inline_bytes += len(match.group(0).encode("utf-8"))

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


def gate_5_asset_link_integrity(
    draft_dir: Path,
    slug: str | None = None,
    rendered_schema_validation: dict[str, Any] | None = None,
) -> dict:
    """Verify all <img> resolve, all <a> return 200, schema validates,
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
    except (OSError, ValueError) as e:
        return _gate_result(5, "Asset + Link Integrity", False, [f"html artifact unreadable: {e}"])
    except UnicodeDecodeError as e:
        return _gate_result(5, "Asset + Link Integrity", False, [f"html artifact is not valid UTF-8: {e}"])
    parser = _MetaParser()
    parser.feed(raw)

    violations = []
    warnings = []
    allowed_hosts = _load_unreachable_allowlist(draft_dir)
    byte_check = _googlebot_html_prefix_check(raw_bytes)
    violations.extend(byte_check["violations"])
    warnings.extend(byte_check["warnings"])
    discover_enabled, discover_config_warning = _discover_target_signal(draft_dir)
    if discover_config_warning:
        warnings.append(discover_config_warning)
    discover_check = _discover_preflight_check(parser, discover_enabled)
    warnings.extend(discover_check["warnings"])

    # img src resolution
    for src in parser.imgs:
        if src.startswith("http://") or src.startswith("https://"):
            ok, reason = _safe_http_url(src)
            if not ok:
                violations.append(f"img src refused by URL safety policy: {src} ({reason})")
                continue
            if _is_allowed_unreachable(src, allowed_hosts):
                continue
            if _http_head(src) != 200:
                violations.append(f"img src returned non-200: {src}")
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

    # canonical present
    if not parser.canonical:
        violations.append("no <link rel=canonical> in document")
    else:
        ok, reason = _well_formed_http_url(parser.canonical)
        if not ok:
            violations.append(f"canonical URL invalid or unsafe: {parser.canonical} ({reason})")

    # External links: explicit http/https allowlist. Other schemes (file://,
    # gopher://, ftp://, javascript:) are flagged as violations rather than
    # silently skipped (S3 from v1.9.0 hostile review). Relative/anchor links
    # without a scheme are left to Gate 5's img-src check above.
    for href in parser.links:
        if href.startswith(("http://", "https://")):
            ok, reason = _safe_http_url(href)
            if not ok:
                violations.append(f"link refused by URL safety policy: {href} ({reason})")
                continue
            if _is_allowed_unreachable(href, allowed_hosts):
                continue
            status = _http_head(href)
            if status != 200:
                violations.append(f"link returned {status}: {href}")
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

    # JSON-LD validation. Prefer source markup when valid, but accept an
    # in-process Gate 3 proof of valid, visible-content-consistent rendered-DOM
    # markup. Never trust a persisted draft-side claim for this handoff.
    json_ld_ok = False
    declared_word_count: Optional[int] = None
    schema_validation_source = "source_html"
    schema_violations: list[str] = []
    if parser.json_ld_blocks:
        try:
            raw_jsonld = json.loads("".join(parser.json_ld_blocks))
            nodes = _jsonld_nodes(raw_jsonld)
            obj = next((node for node in nodes if _is_blogposting_node(node)), None)
            if obj is None:
                schema_violations.append("JSON-LD missing BlogPosting node")
                obj = {}
            json_ld_ok = True
            required = ("headline", "image", "datePublished", "author")
            missing = [k for k in required if not obj.get(k)]
            if missing:
                schema_violations.append(f"JSON-LD missing required fields: {missing}")
            declared_word_count = obj.get("wordCount")
            if not isinstance(declared_word_count, int):
                schema_violations.append("JSON-LD wordCount must be an integer")
        except json.JSONDecodeError as e:
            schema_violations.append(f"JSON-LD invalid: {e}")
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

    # word count match
    if isinstance(declared_word_count, int):
        actual = parser.article_text_chars
        if actual > 0:
            diff_pct = abs(declared_word_count - actual) / actual * 100
            if diff_pct > 5:
                violations.append(f"JSON-LD wordCount {declared_word_count} differs from actual {actual} by {diff_pct:.1f}%")

    return _gate_result(
        5, "Asset + Link Integrity", not violations, violations, warnings,
        imgs=parser.imgs, links_checked=len(parser.links),
        json_ld_valid=json_ld_ok, declared_word_count=declared_word_count,
        schema_validation_source=schema_validation_source,
        actual_word_count=parser.article_text_chars,
        googlebot_byte_check={
            key: value for key, value in byte_check.items()
            if key not in {"violations", "warnings"}
        },
        discover_check={
            key: value for key, value in discover_check.items()
            if key != "warnings"
        },
    )


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
    nonce_match = NONCE_PATTERN.search(text)
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

    blocking = final_match.group(1).lower() == "true"
    reason = (final_match.group(2) or "").strip()
    if blocking:
        return _gate_result(
            4, "Content Review", False,
            [f"reviewer blocked: {reason or 'see review.md'}"],
            blocking=True, reason=reason,
        )
    metric_violations: list[str] = []
    score_match = re.search(r"Overall Score:\s*(\d{1,3})\s*/\s*100", text, re.IGNORECASE)
    if not score_match:
        metric_violations.append("review.md missing machine-readable Overall Score: N/100")
        score = None
    else:
        score = int(score_match.group(1))
        if score < 0 or score > 100:
            metric_violations.append(f"review overall score {score}/100 is outside 0..100")
        elif score < 90:
            metric_violations.append(f"review overall score {score}/100 is below 90")

    if re.search(r"\bP0\b", text, re.IGNORECASE) and not re.search(r"\b(no|zero)\s+P0\b", text, re.IGNORECASE):
        metric_violations.append("review mentions P0 without a no/zero P0 clearance")

    if metric_violations:
        return _gate_result(4, "Content Review", False, metric_violations, blocking=False, reason=reason, score=score)

    return _gate_result(
        4, "Content Review", True, [],
        blocking=False, reason=reason, score=score,
    )


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
        help="Reset the per-draft iteration counter to 1 (this run counts as the first).",
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

    # Count only orchestrator repair attempts, not every preflight or single-gate run.
    iteration_exit = _iteration_check(
        draft,
        reset=args.reset_iterations,
        increment=args.repair_attempt,
    )
    if iteration_exit != 0:
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
        r = fn(draft)
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
