#!/usr/bin/env python3
"""Generate or fetch a 1200x630 hero image for a blog post.

Implements the v1.9.0 Blog Delivery Contract hero-image ladder. Banana MCP
is step 1 of the contract, but it runs in the orchestrator before this script
is called and this script never calls it. The script itself starts at step 2
(direct Gemini API) and produces the final `hero.<ext>` + `hero-credit.txt`
in the requested output directory.

Ladder:
  1. (Orchestrator only, not run by this script) Banana MCP via nanobanana-mcp
  2. Direct Gemini API via google-genai SDK. Paid: runs only with
     `--allow-paid` AND GOOGLE_AI_API_KEY or GEMINI_API_KEY. Without the flag a
     set key is ignored, stderr says so once, and the JSON result carries
     `"paid_gemini_skipped": true`. Pass the flag only after the user approves
     the cost.
  3. Premium stock APIs: Unsplash, Pexels, Pixabay (any one key suffices)
  4. Openverse public API (CC-licensed; no key required)
  5. Exit nonzero with setup instructions

A hero already in the output directory (`hero.png`, `.jpg`, `.jpeg` or
`.webp`, for example one the user placed by hand) is kept and reported with
source `existing`; no provider runs. It counts only when it is a regular,
non-empty file whose header matches its extension's format and is at least
1200x630, the minimum delivery Gates 1 and 2 enforce. The first valid one in
renderer order is kept and invalid siblings are removed; with no valid one, a
new hero replaces the invalid files. Either way the JSON result lists the
invalid files under `replaced_invalid`. `--replace` generates a new one
instead. A symlinked `hero.*` stops the run with nothing written or deleted,
and every write target (each `hero.*` and `hero-credit.txt`) is checked
before any provider runs.

A downloaded or generated image that cannot be decoded (corrupt, truncated,
oversized) is skipped and the next step runs. The new image and
`hero-credit.txt` are staged as temp files and renamed into place together;
only then is any stale `hero.*` file of another extension removed, so the
renderer cannot pick it. A refused credit write leaves the old files alone.

Usage:
    python3 scripts/generate_hero.py --topic "<title>" --tags "a,b,c" \\
        --out <draft-folder> [--width 1200] [--height 630] [--replace] \\
        [--allow-paid] [--json]

Returns 0 on success (hero.<ext> + hero-credit.txt written). Returns 1
when every ladder step is exhausted with no successful generation.
"""

from __future__ import annotations

import argparse
import base64
import io
import ipaddress
import json
import os
import re
import socket
import stat
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable, Optional


def _project_version() -> str:
    """Read the package version from pyproject.toml."""
    try:
        text = (Path(__file__).resolve().parent.parent / "pyproject.toml").read_text(encoding="utf-8")
    except OSError:
        return "0.0.0"
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return match.group(1) if match else "0.0.0"


OUTPUT_FILE_PREFIX = "hero"
CREDIT_FILE_NAME = "hero-credit.txt"
PAID_SKIPPED_MESSAGE = "Paid Gemini generation skipped: pass --allow-paid after the user approves the cost."
DEFAULT_WIDTH = 1200
DEFAULT_HEIGHT = 630
DEFAULT_GEMINI_MODEL = os.environ.get("NANOBANANA_MODEL") or "gemini-nano-banana-2.1"
OPENVERSE_API = "https://api.openverse.org/v1/images/"
UNSPLASH_API = "https://api.unsplash.com/search/photos"
PEXELS_API = "https://api.pexels.com/v1/search"
PIXABAY_API = "https://pixabay.com/api/"
USER_AGENT = f"claude-blog/{_project_version()} (+https://github.com/AgriciDaniel/claude-blog)"
HTTP_TIMEOUT = 20

# VULN-801 SSRF guard (v1.9.1):
# Hero downloads come from third-party JSON responses. Without these guards
# a poisoned upstream can redirect us to file://, ftp://, or internal IPs
# (AWS IMDS, RFC1918, loopback) and have us publish the bytes as og:image.
ALLOWED_SCHEMES = frozenset({"http", "https"})
MAX_IMAGE_BYTES = 25 * 1024 * 1024  # 25 MB; legit heroes are well under this.
GEMINI_IMAGE_MODELS = (
    "gemini-nano-banana-2.1",
    "gemini-3.1-flash-image",
    "gemini-3.1-flash-lite-image",
    "gemini-3-pro-image",
)
# Errors that no other model can fix: stop instead of trying the next model.
_GEMINI_STOP_MARKERS = (
    "api key",
    "api_key",
    "permission",
    "unauthenticated",
    "unauthorized",
    "billing",
    "quota",
    "resource_exhausted",
    "429",
    "401",
    "403",
)


# NAT64 well-known prefix (RFC 6052): the low 32 bits are the IPv4 destination.
_NAT64_PREFIX = ipaddress.ip_network("64:ff9b::/96")


def _is_private_address(host: str) -> bool:
    """Resolve host to IP and test against RFC1918/loopback/link-local/ULA.

    Returns True if the host resolves to any non-public address (so the
    caller should refuse the request). Returns True on resolution failure
    (fail-closed).
    """
    if not host:
        return True
    try:
        # Resolve via getaddrinfo to handle both IPv4 and IPv6.
        infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return True
    except Exception:
        return True
    for info in infos:
        sockaddr = info[4]
        addr_str = sockaddr[0]
        if _is_blocked_address(addr_str):
            return True
    return False


def _is_blocked_address(addr_text: str) -> bool:
    """Fail-closed address check using ipaddress is_global semantics.

    Only globally routable unicast addresses pass. That also blocks ranges the
    older private/reserved flags missed: CGNAT 100.64.0.0/10 (Tailscale),
    deprecated site-local fec0::/10 and other special-purpose blocks. An
    IPv6 address that wraps an IPv4 one (IPv4-mapped, 6to4, NAT64) is judged
    by the IPv4 address it wraps. blog_preflight.py applies is_global too.
    """
    try:
        addr = ipaddress.ip_address(addr_text.split("%", 1)[0])
    except ValueError:
        return True
    embedded = getattr(addr, "ipv4_mapped", None) or getattr(addr, "sixtofour", None)
    if embedded is None and addr in _NAT64_PREFIX:
        embedded = ipaddress.IPv4Address(int(addr) & 0xFFFFFFFF)
    if embedded is not None:
        addr = embedded
    return (
        not addr.is_global
        or getattr(addr, "is_site_local", False)
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_multicast
        or addr.is_unspecified
    )


def _resolve_public_url(url: str) -> tuple[bool, str | None, str | None, int | None, list]:
    """Validate a URL and return the public addresses to pin."""
    if not isinstance(url, str) or not url:
        return False, "URL missing", None, None, []
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False, "URL scheme must be http or https", None, None, []
    host = parsed.hostname
    if not host:
        return False, "URL host missing", None, None, []
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        addr_str = socket.gethostbyname(host)
    except socket.gaierror as e:
        return False, f"DNS resolution failed: {e}", None, None, []
    except Exception as e:
        return False, f"DNS resolution failed: {e}", None, None, []
    if _is_blocked_address(addr_str):
        return False, f"resolved address is not public: {addr_str}", None, None, []
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as e:
        return False, f"DNS resolution failed: {e}", None, None, []
    except Exception as e:
        return False, f"DNS resolution failed: {e}", None, None, []
    if not infos:
        return False, "DNS resolution returned no addresses", None, None, []
    for info in infos:
        addr_text = info[4][0]
        if _is_blocked_address(addr_text):
            return False, f"resolved address is not public: {addr_text}", None, None, []
    return True, None, host.lower().rstrip("."), port, list(infos)


def _validate_url(url: str) -> bool:
    """Return True if url is safe to fetch (http/https + public host).

    Uses gethostbyname for backwards-compatible test stubbing, then
    validates and pins the getaddrinfo addresses used by real fetches.
    """
    ok, _reason, _host, _port, _infos = _resolve_public_url(url)
    return ok


class _PinnedDNS:
    """Temporarily pin a host to the addresses already validated."""

    def __init__(self, host: str, port: int, infos: list):
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


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Refuse automatic redirect-following.

    Without this, urllib silently follows 30x responses to wherever the
    server points, including back to private IPs (defeats _validate_url).
    """
    def http_error_301(self, req, fp, code, msg, headers):  # noqa: D401
        return None
    http_error_302 = http_error_301
    http_error_303 = http_error_301
    http_error_307 = http_error_301
    http_error_308 = http_error_301


_NO_REDIRECT_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirectHandler())


def _url_for_log(url: str) -> str:
    """Redact query and fragment data before logging URLs."""
    parsed = urllib.parse.urlparse(url)
    redacted = parsed._replace(query="[redacted]" if parsed.query else "", fragment="")
    return urllib.parse.urlunparse(redacted)[:120]


def _is_supported_image(data: bytes) -> bool:
    """Accept only JPEG, PNG, or WebP byte signatures."""
    return (
        data.startswith(b"\xff\xd8\xff")
        or data.startswith(b"\x89PNG\r\n\x1a\n")
        or (len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP")
    )


def _image_ext(data: bytes, fallback: str = ".jpg") -> str:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    return fallback


def _is_trusted_system_symlink(path: Path) -> bool:
    """True for an OS-level alias such as /home -> var/home or macOS /tmp.

    Only a root-owned link sitting directly under the filesystem root
    qualifies. An attacker who can plant links inside a working tree cannot
    create one there, so honouring these keeps the guard focused on
    redirection inside the output tree and at the leaf.
    """
    if os.name != "posix":
        return False
    try:
        return path.lstat().st_uid == 0 and path.parent == Path(path.anchor)
    except OSError:
        return False


def _symlink_component(path: Path) -> Path | None:
    """Inspect unresolved components before mkdir/resolve can follow an alias.

    Trusted system-level aliases directly under the filesystem root are
    skipped; every other symlinked component is returned.
    """
    candidate = path if path.is_absolute() else Path.cwd() / path
    for component in (candidate, *candidate.parents):
        if component.is_symlink() and not _is_trusted_system_symlink(component):
            return component
    return None


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    """Atomic write via mkstemp + os.replace. Mirrors load_untrusted_root.py."""
    unsafe = _symlink_component(path)
    if unsafe is not None:
        raise ValueError(f"refusing symlink output path component: {unsafe}")
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, str(path))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _atomic_write_text(path: Path, text: str) -> None:
    """Atomic text write that refuses symlink output paths."""
    unsafe = _symlink_component(path)
    if unsafe is not None:
        raise ValueError(f"refusing symlink output path component: {unsafe}")
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, str(path))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _validate_dimensions(width: int, height: int) -> tuple[bool, str | None]:
    if width < 1 or height < 1:
        return False, "width and height must be positive integers"
    if width > 10000 or height > 10000:
        return False, "width and height must be 10000 or less"
    return True, None


class _ImageUnusable(RuntimeError):
    """The image bytes could not be decoded or resized; the caller moves to the next source."""


def _fit_image_bytes(data: bytes, width: int, height: int) -> bytes:
    """Resize and center-crop image bytes to exact output dimensions.

    Raises RuntimeError when Pillow is missing and its subclass _ImageUnusable
    when the bytes cannot be decoded (corrupt, truncated, decompression bomb).
    Both make the ladder skip this source; neither is a write error.
    """
    try:
        from PIL import Image, ImageOps  # type: ignore
    except ImportError as e:
        raise RuntimeError("Pillow is required to enforce --width/--height") from e

    try:
        with Image.open(io.BytesIO(data)) as img:
            fmt = (img.format or "PNG").upper()
            fitted = ImageOps.fit(img, (width, height), method=Image.Resampling.LANCZOS)
            if fmt in {"JPEG", "JPG"} and fitted.mode in {"RGBA", "LA", "P"}:
                fitted = fitted.convert("RGB")
            out = io.BytesIO()
            save_format = "JPEG" if fmt == "JPG" else fmt
            if save_format not in {"JPEG", "PNG", "WEBP"}:
                save_format = "PNG"
            fitted.save(out, format=save_format)
            return out.getvalue()
    except Exception as e:  # PIL raises OSError, ValueError, SyntaxError, DecompressionBombError, ...
        raise _ImageUnusable(f"image could not be decoded ({type(e).__name__}: {e})") from e


HERO_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
# Format each hero extension must carry; blog_preflight.py checks the same map.
_HERO_FORMATS = {".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg", ".webp": "webp"}
# Minimum hero size Gates 1 and 2 of blog_preflight.py enforce. Kept as local
# numbers (not imported) and pinned equal by tests/test_hero_safety_gates.py.
HERO_MIN_WIDTH = 1200
HERO_MIN_HEIGHT = 630
# SOFn markers that carry frame dimensions (C4 DHT, C8 JPG and CC DAC do not).
_JPEG_SOF_MARKERS = frozenset(range(0xC0, 0xD0)) - {0xC4, 0xC8, 0xCC}
_JPEG_MAX_SEGMENTS = 4096


def _png_dimensions(f) -> Optional[tuple[int, int]]:
    head = f.read(24)
    if len(head) < 24 or not head.startswith(b"\x89PNG\r\n\x1a\n") or head[12:16] != b"IHDR":
        return None
    return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")


def _webp_dimensions(f) -> Optional[tuple[int, int]]:
    head = f.read(30)
    if len(head) < 16 or head[:4] != b"RIFF" or head[8:12] != b"WEBP":
        return None
    chunk = head[12:16]
    if chunk == b"VP8 " and len(head) >= 30 and head[23:26] == b"\x9d\x01\x2a":
        return int.from_bytes(head[26:28], "little") & 0x3FFF, int.from_bytes(head[28:30], "little") & 0x3FFF
    if chunk == b"VP8L" and len(head) >= 25 and head[20] == 0x2F:
        bits = int.from_bytes(head[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if chunk == b"VP8X" and len(head) >= 30:
        return int.from_bytes(head[24:27], "little") + 1, int.from_bytes(head[27:30], "little") + 1
    return None


def _jpeg_dimensions(f) -> Optional[tuple[int, int]]:
    """Walk JPEG segments (seeking past their bodies) to the first SOFn frame header."""
    if f.read(2) != b"\xff\xd8":
        return None
    for _ in range(_JPEG_MAX_SEGMENTS):
        if f.read(1) != b"\xff":
            return None
        marker = f.read(1)
        for _fill in range(64):  # optional 0xFF fill bytes before the marker code
            if marker != b"\xff":
                break
            marker = f.read(1)
        if not marker or marker == b"\xff":
            return None
        code = marker[0]
        if code == 0x01 or 0xD0 <= code <= 0xD7:
            continue  # standalone markers have no length field
        if code in (0xD9, 0xDA):
            return None  # end of image or scan data before any frame header
        length_bytes = f.read(2)
        if len(length_bytes) < 2:
            return None
        length = int.from_bytes(length_bytes, "big")
        if length < 2:
            return None
        if code in _JPEG_SOF_MARKERS:
            body = f.read(5)  # precision, height, width
            if len(body) < 5:
                return None
            return int.from_bytes(body[3:5], "big"), int.from_bytes(body[1:3], "big")
        f.seek(length - 2, os.SEEK_CUR)
    return None


_DIMENSION_READERS = {"png": _png_dimensions, "jpeg": _jpeg_dimensions, "webp": _webp_dimensions}


def _hero_problem(path: Path) -> Optional[str]:
    """Return why path is not a usable hero, or None when it is.

    Cheap checks without Pillow: a regular non-symlink file, non-empty, the
    signature of its extension's format, and a header whose size meets the
    HERO_MIN_WIDTH x HERO_MIN_HEIGHT minimum that delivery Gates 1 and 2
    enforce. A smaller hero would be kept here and then block delivery, so it
    counts as invalid. Full decoding is left to blog_preflight.py.
    """
    fmt = _HERO_FORMATS.get(path.suffix)
    if fmt is None:
        return "unsupported extension"
    try:
        info = path.lstat()
    except OSError as e:
        return f"cannot be inspected ({e})"
    if not stat.S_ISREG(info.st_mode):
        return "not a regular file"
    if info.st_size == 0:
        return "empty file"
    try:
        fd = os.open(str(path), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "rb") as f:
            dims = _DIMENSION_READERS[fmt](f)
    except OSError as e:
        return f"unreadable ({e})"
    if dims is None:
        return f"no valid {fmt.upper()} header"
    width, height = dims
    if width < 1 or height < 1:
        return "header reports zero width or height"
    if width < HERO_MIN_WIDTH or height < HERO_MIN_HEIGHT:
        return f"{width}x{height} is below the {HERO_MIN_WIDTH}x{HERO_MIN_HEIGHT} delivery minimum"
    return None


def _hero_candidates(out_dir: Path) -> list[Path]:
    """Lowercase hero.<ext> paths in scripts/blog_render.py preference order."""
    return [out_dir / f"{OUTPUT_FILE_PREFIX}{extension}" for extension in HERO_EXTENSIONS]


def _symlinked_heroes(out_dir: Path) -> list[Path]:
    return [candidate for candidate in _hero_candidates(out_dir) if candidate.is_symlink()]


def _survey_heroes(out_dir: Path) -> tuple[Optional[Path], list[tuple[Path, str]]]:
    """Return (first valid hero, invalid regular hero files with reasons).

    The valid hero is the first in renderer preference order. Symlinks and
    other non-regular entries are in neither list; main refuses them.
    """
    valid: Optional[Path] = None
    invalid: list[tuple[Path, str]] = []
    for candidate in _hero_candidates(out_dir):
        if candidate.is_symlink() or not candidate.is_file():
            continue
        problem = _hero_problem(candidate)
        if problem is not None:
            invalid.append((candidate, problem))
        elif valid is None:
            valid = candidate
    return valid, invalid


def _existing_hero(out_dir: Path) -> Optional[Path]:
    """Return the first valid hero already in out_dir, if any (symlinks do not count)."""
    return _survey_heroes(out_dir)[0]


def _refuse_unwritable_target(path: Path) -> None:
    """_refuse_unsafe_target plus a writability check on an existing file."""
    _refuse_unsafe_target(path)
    if os.path.lexists(path) and not os.access(path, os.W_OK):
        raise ValueError(f"refusing unwritable output path: {path}")


def _refuse_unsafe_target(path: Path) -> None:
    """Raise ValueError when path is reached through a symlink or is not a regular file."""
    unsafe = _symlink_component(path)
    if unsafe is not None:
        raise ValueError(f"refusing symlink output path component: {unsafe}")
    if os.path.lexists(path) and not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError(f"refusing non-regular output path: {path}")


def _stage_temp(path: Path, data: bytes) -> str:
    """Write data to a temp file beside path and return the temp path."""
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return tmp


def _write_hero(out_dir: Path, img_bytes: bytes, credit_text: str) -> Path:
    """Write hero.<ext> and hero-credit.txt together, then remove stale hero.* siblings.

    Both are staged as temp files in out_dir and renamed into place only after
    both writes succeeded, so a refused credit (symlink, directory, disk full)
    leaves the old hero, old credit and siblings untouched. scripts/blog_render.py
    prefers hero.png, so an older hero.png left beside a fresh hero.jpg would
    silently win. Cleanup runs only after both renames, and never touches the
    file just written.
    """
    hero_path = out_dir / f"{OUTPUT_FILE_PREFIX}{_image_ext(img_bytes)}"
    credit_path = out_dir / CREDIT_FILE_NAME
    _refuse_unsafe_target(hero_path)
    _refuse_unsafe_target(credit_path)
    staged: list[tuple[str, Path]] = []
    try:
        staged.append((_stage_temp(hero_path, img_bytes), hero_path))
        staged.append((_stage_temp(credit_path, credit_text.encode("utf-8")), credit_path))
        for tmp, target in staged:
            os.replace(tmp, str(target))
    except Exception:
        for tmp, _target in staged:
            try:
                os.unlink(tmp)
            except OSError:
                pass  # already renamed into place
        raise
    for stale in _hero_candidates(out_dir):
        if stale != hero_path and (stale.is_symlink() or stale.is_file()):
            stale.unlink()
    return hero_path


def _build_prompt(topic: str, tags: list[str], width: int, height: int) -> str:
    parts = [
        f"Editorial illustration for a blog post titled '{topic}'.",
    ]
    if tags:
        parts.append(f"Themes: {', '.join(tags[:5])}.")
    parts.extend([
        f"Suitable as a {width}x{height} social cover.",
        "Clean, minimalist, professional. No text, no human faces, no logos.",
    ])
    return " ".join(parts)


def _http_get(url: str, headers: Optional[dict] = None, timeout: int = HTTP_TIMEOUT) -> Optional[bytes]:
    """Fetch URL with SSRF guards (VULN-801, v1.9.1).

    Refuses:
      * non-http(s) schemes (file://, ftp://, gopher://, data:, javascript:)
      * hosts resolving to RFC1918 / loopback / link-local / ULA / reserved
      * responses larger than MAX_IMAGE_BYTES
      * automatic redirect-following (no-redirect opener; redirects return None)
    """
    ok, reason, host, port, infos = _resolve_public_url(url)
    if not ok or host is None or port is None:
        print(f"[http] refused (scheme/host policy): {_url_for_log(url)} ({reason})", file=sys.stderr)
        return None
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    try:
        with _PinnedDNS(host, port, infos):
            with _NO_REDIRECT_OPENER.open(req, timeout=timeout) as resp:
                status = getattr(resp, "status", 200)
                if 300 <= int(status) < 400:
                    print(f"[http] redirect refused: {_url_for_log(url)}", file=sys.stderr)
                    return None
                # Read at most MAX_IMAGE_BYTES + 1 to detect oversize.
                data = resp.read(MAX_IMAGE_BYTES + 1)
                if len(data) > MAX_IMAGE_BYTES:
                    print(
                        f"[http] response exceeds {MAX_IMAGE_BYTES} bytes; refusing",
                        file=sys.stderr,
                    )
                    return None
                return data
    except Exception as e:
        print(f"[http] {_url_for_log(url)}: {e}", file=sys.stderr)
        return None


def _download_image(url: str) -> Optional[bytes]:
    data = _http_get(url)
    if data is None:
        return None
    if not _is_supported_image(data):
        print(f"[http] response is not a supported image: {_url_for_log(url)}", file=sys.stderr)
        return None
    return data


def _http_get_json(url: str, headers: Optional[dict] = None) -> Optional[dict]:
    raw = _http_get(url, headers=headers)
    if raw is None:
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"[http] json decode failed: {e}", file=sys.stderr)
        return None


def _paid_key_set() -> bool:
    return bool(os.environ.get("GOOGLE_AI_API_KEY") or os.environ.get("GEMINI_API_KEY"))


def _try_gemini(
    topic: str, tags: list[str], out_dir: Path, width: int, height: int, model: str, allow_paid: bool = False
) -> Optional[dict]:
    """Ladder step 2: direct Gemini API. Paid, so it runs only with allow_paid and a key."""
    if not allow_paid:
        return None
    api_key = os.environ.get("GOOGLE_AI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        from google import genai  # type: ignore
    except ImportError:
        print("[gemini] google-genai not installed; skipping", file=sys.stderr)
        return None

    prompt = _build_prompt(topic, tags, width, height)
    client = genai.Client(api_key=api_key)
    img_bytes: Optional[bytes] = None
    used_model = model

    # Try Gemini image-capable GA models via the Interactions API.
    for try_model in dict.fromkeys((model, *GEMINI_IMAGE_MODELS)):
        if not try_model:
            continue
        try:
            interaction = client.interactions.create(
                model=try_model,
                input=prompt,
                response_format={
                    "type": "image",
                    "mime_type": "image/jpeg",
                    "aspect_ratio": "16:9",
                },
            )
            output_image = getattr(interaction, "output_image", None)
            if output_image and getattr(output_image, "data", None):
                raw_data = output_image.data
                img_bytes = base64.b64decode(raw_data) if isinstance(raw_data, str) else raw_data
                used_model = try_model
            if img_bytes:
                break
        except Exception as e:
            message = str(e).replace(api_key, "[redacted]")
            print(f"[gemini] {try_model} interactions.create failed: {message}", file=sys.stderr)
            if any(marker in message.lower() for marker in _GEMINI_STOP_MARKERS):
                break

    if not img_bytes or not _is_supported_image(img_bytes):
        return None

    try:
        img_bytes = _fit_image_bytes(img_bytes, width, height)
    except RuntimeError as e:
        print(f"[image] {e}", file=sys.stderr)
        return None
    hero_path = _write_hero(
        out_dir, img_bytes, f"AI-generated via {used_model}. No attribution required.\nPrompt: {prompt}\n",
    )
    return {"source": "gemini", "model": used_model, "path": str(hero_path)}


def _try_unsplash(query: str, out_dir: Path, width: int, height: int) -> Optional[dict]:
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        return None
    params = urllib.parse.urlencode({
        "query": query, "orientation": "landscape", "content_filter": "high", "per_page": 10,
    })
    data = _http_get_json(f"{UNSPLASH_API}?{params}", headers={"Authorization": f"Client-ID {key}"})
    if not data or not data.get("results"):
        return None
    item = data["results"][0]
    img_url = item.get("urls", {}).get("regular")
    if not img_url:
        return None
    img_bytes = _download_image(img_url)
    if not img_bytes:
        return None
    try:
        img_bytes = _fit_image_bytes(img_bytes, width, height)
    except RuntimeError as e:
        print(f"[image] {e}", file=sys.stderr)
        return None
    user = item.get("user", {})
    credit = (
        f'Photo by {user.get("name", "Unsplash contributor")} on Unsplash\n'
        f'License: Unsplash License (free for commercial use, no attribution required but appreciated)\n'
        f'Source: {item.get("links", {}).get("html", img_url)}\n'
    )
    hero_path = _write_hero(out_dir, img_bytes, credit)
    return {"source": "unsplash", "path": str(hero_path)}


def _try_pexels(query: str, out_dir: Path, width: int, height: int) -> Optional[dict]:
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        return None
    params = urllib.parse.urlencode({"query": query, "orientation": "landscape", "per_page": 10})
    data = _http_get_json(f"{PEXELS_API}?{params}", headers={"Authorization": key})
    if not data or not data.get("photos"):
        return None
    item = data["photos"][0]
    img_url = item.get("src", {}).get("large2x") or item.get("src", {}).get("large")
    if not img_url:
        return None
    img_bytes = _download_image(img_url)
    if not img_bytes:
        return None
    try:
        img_bytes = _fit_image_bytes(img_bytes, width, height)
    except RuntimeError as e:
        print(f"[image] {e}", file=sys.stderr)
        return None
    credit = (
        f'Photo by {item.get("photographer", "Pexels contributor")} on Pexels\n'
        f'License: Pexels License (free for commercial use)\n'
        f'Source: {item.get("url", img_url)}\n'
    )
    hero_path = _write_hero(out_dir, img_bytes, credit)
    return {"source": "pexels", "path": str(hero_path)}


def _try_pixabay(query: str, out_dir: Path, width: int, height: int) -> Optional[dict]:
    key = os.environ.get("PIXABAY_API_KEY")
    if not key:
        return None
    params = urllib.parse.urlencode({
        "key": key, "q": query, "orientation": "horizontal",
        "image_type": "photo", "safesearch": "true", "per_page": 10,
    })
    data = _http_get_json(f"{PIXABAY_API}?{params}")
    if not data or not data.get("hits"):
        return None
    item = data["hits"][0]
    img_url = item.get("largeImageURL") or item.get("webformatURL")
    if not img_url:
        return None
    img_bytes = _download_image(img_url)
    if not img_bytes:
        return None
    try:
        img_bytes = _fit_image_bytes(img_bytes, width, height)
    except RuntimeError as e:
        print(f"[image] {e}", file=sys.stderr)
        return None
    credit = (
        f'Image by {item.get("user", "Pixabay contributor")} on Pixabay\n'
        f'License: Pixabay Content License (free for commercial use)\n'
        f'Source: {item.get("pageURL", img_url)}\n'
    )
    hero_path = _write_hero(out_dir, img_bytes, credit)
    return {"source": "pixabay", "path": str(hero_path)}


def _try_premium_stock(topic: str, tags: list[str], out_dir: Path, width: int, height: int) -> Optional[dict]:
    """Ladder step 3: Unsplash > Pexels > Pixabay (first whose key is set)."""
    query = " ".join([topic] + tags[:3])
    for fn in (_try_unsplash, _try_pexels, _try_pixabay):
        result = fn(query, out_dir, width, height)
        if result:
            return result
    return None


def _try_openverse(topic: str, tags: list[str], out_dir: Path, width: int, height: int) -> Optional[dict]:
    """Ladder step 4: public API, no key required, CC-licensed.

    Openverse search terms are restrictive when combined, so try a bounded
    sequence from specific to broad rather than making one overlong query.
    """
    queries: list[str] = []
    for candidate in (
        " ".join([topic] + tags[:3]),
        " ".join(tags[:3]) if tags else "",
        " ".join(topic.split()[:3]),
        tags[0] if tags else "",
    ):
        query = candidate.strip()
        if query and query not in queries:
            queries.append(query)

    data = None
    for query in queries:
        params = urllib.parse.urlencode({
            "q": query, "aspect_ratio": "wide", "license": "cc0,by,by-sa",
            "size": "large", "page_size": 10,
        })
        candidate_data = _http_get_json(f"{OPENVERSE_API}?{params}")
        if candidate_data and candidate_data.get("results"):
            data = candidate_data
            break
        print(f"[openverse] no results for {query!r}", file=sys.stderr)

    if not data or not data.get("results"):
        print("[openverse] no results", file=sys.stderr)
        return None

    item = data["results"][0]
    img_url = item.get("url") or item.get("thumbnail")
    if not img_url:
        return None
    img_bytes = _download_image(img_url)
    if not img_bytes:
        return None
    try:
        img_bytes = _fit_image_bytes(img_bytes, width, height)
    except RuntimeError as e:
        print(f"[image] {e}", file=sys.stderr)
        return None

    title = item.get("title") or "untitled"
    creator = item.get("creator") or "Unknown"
    license_name = (item.get("license") or "CC").upper()
    source = item.get("source") or "openverse"
    src_url = item.get("foreign_landing_url") or img_url
    hero_path = _write_hero(
        out_dir, img_bytes, f'"{title}" by {creator}\nLicense: {license_name}\nSource: {source}\nURL: {src_url}\n',
    )
    return {"source": "openverse", "creator": creator, "license": license_name, "path": str(hero_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--topic", required=True, help="Post title or topic for image search/generation")
    parser.add_argument("--tags", default="", help="Comma-separated tag list")
    parser.add_argument("--out", required=True, help="Output directory (will receive hero.<ext> and hero-credit.txt)")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--model", default=DEFAULT_GEMINI_MODEL, help="Gemini image model name")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Generate a new hero even when the output directory already has one (default: keep it)",
    )
    parser.add_argument(
        "--allow-paid",
        action="store_true",
        help=(
            "Allow the paid Gemini route (needs GOOGLE_AI_API_KEY or GEMINI_API_KEY). Pass it only after "
            "the user approves the cost; without it a set key is ignored and the free steps run."
        ),
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON result to stdout")
    args = parser.parse_args()

    def fail(code: str, msg: str, **extra) -> int:
        if args.json:
            print(json.dumps({"error": code, "message": msg, **extra}))
        else:
            print(msg, file=sys.stderr)
        return 1

    dims_ok, dims_error = _validate_dimensions(args.width, args.height)
    if not dims_ok:
        return fail("invalid-dimensions", f"ERROR: {dims_error}")

    raw_out_dir = Path(args.out)
    unsafe = _symlink_component(raw_out_dir)
    if unsafe is not None:
        return fail("out-dir-symlink", f"ERROR: refusing symlink output directory component {unsafe}")
    out_dir = raw_out_dir.resolve()
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        return fail("out-dir-create-failed", f"ERROR: cannot create output directory {out_dir}: {e}")
    if not os.access(out_dir, os.W_OK):
        return fail("out-dir-not-writable", f"ERROR: output directory {out_dir} is not writable")
    symlinked = _symlinked_heroes(out_dir)
    if symlinked:
        # A link may point anywhere: never keep it, write through it, or delete it.
        names = ", ".join(path.name for path in symlinked)
        return fail(
            "hero-symlink",
            f"ERROR: refusing to run: {names} in {out_dir} is a symlink. "
            "Replace it with a regular image file or remove it, then rerun. Nothing was written or deleted.",
        )
    existing, invalid = _survey_heroes(out_dir)
    invalid_names = [path.name for path, _problem in invalid]
    if existing is not None and not args.replace:
        # Never overwrite or delete a valid hero that is already there (the
        # contract lets the user place one by hand), and never spend on a
        # second one. Invalid siblings are removed so the renderer cannot
        # embed them ahead of the kept hero.
        for path, problem in invalid:
            print(f"[existing] removing {path.name}: not a usable hero ({problem})", file=sys.stderr)
            try:
                path.unlink()
            except OSError as e:
                return fail("output-write-refused", f"ERROR: cannot remove invalid {path.name}: {e}")
        result = {"source": "existing", "path": str(existing)}
        if invalid_names:
            result["replaced_invalid"] = invalid_names
        if args.json:
            print(json.dumps(result))
        else:
            print(f"OK: kept existing hero {existing} (pass --replace to generate a new one)")
        return 0
    try:
        # Refuse before any provider runs, so a bad target never costs a generation.
        for target in (*_hero_candidates(out_dir), out_dir / CREDIT_FILE_NAME):
            _refuse_unwritable_target(target)
    except (OSError, ValueError) as e:
        return fail("output-write-refused", f"ERROR: output write refused: {e}. Nothing was written or deleted.")
    for path, problem in invalid:
        print(f"[existing] {path.name} is not a usable hero ({problem}); generating a replacement", file=sys.stderr)

    notes: dict = {}
    if _paid_key_set() and not args.allow_paid:
        print(PAID_SKIPPED_MESSAGE, file=sys.stderr)
        notes["paid_gemini_skipped"] = True
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    ladder: list[tuple[str, Callable[[], Optional[dict]]]] = [
        (
            "gemini",
            lambda: _try_gemini(
                args.topic, tags, out_dir, args.width, args.height, args.model, allow_paid=args.allow_paid
            ),
        ),
        ("premium-stock", lambda: _try_premium_stock(args.topic, tags, out_dir, args.width, args.height)),
        ("openverse", lambda: _try_openverse(args.topic, tags, out_dir, args.width, args.height)),
    ]

    for name, fn in ladder:
        try:
            result = fn()
        except (OSError, ValueError) as e:
            return fail("output-write-refused", f"ERROR: {name} output write refused: {e}", **notes)
        if result:
            result.update(notes)
            if invalid_names:
                result["replaced_invalid"] = invalid_names
            if args.json:
                print(json.dumps(result))
            else:
                print(f"OK: hero from {result['source']} -> {result['path']}")
            return 0

    return fail(
        "no-image-gen-path",
        (
            "Hero image required but no generation path available. Configure Banana MCP, "
            "set GOOGLE_AI_API_KEY or GEMINI_API_KEY and pass --allow-paid once the user approves the cost, "
            "set UNSPLASH_ACCESS_KEY / PEXELS_API_KEY / PIXABAY_API_KEY, "
            "or place a 1200x630 hero.png in the draft folder manually."
        ),
        **notes,
    )


if __name__ == "__main__":
    sys.exit(main())
