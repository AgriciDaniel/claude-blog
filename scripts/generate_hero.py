#!/usr/bin/env python3
"""Generate or fetch a 1200x630 hero image for a blog post.

Implements the v1.9.0 Blog Delivery Contract hero-image ladder. The
orchestrator handles step 1 (Banana MCP) when available; this script
handles steps 2-5 and produces the final `hero.<ext>` + `hero-credit.txt`
in the requested output directory.

Ladder:
  1. (Orchestrator only) Banana MCP via nanobanana-mcp
  2. Direct Gemini API via google-genai SDK (requires GOOGLE_AI_API_KEY)
  3. Atlas Cloud image API (requires ATLASCLOUD_API_KEY)
  4. Premium stock APIs: Unsplash, Pexels, Pixabay (any one key suffices)
  5. Openverse public API (CC-licensed; no key required)
  6. Exit nonzero with setup instructions

Usage:
    python3 scripts/generate_hero.py --topic "<title>" --tags "a,b,c" \\
        --out <draft-folder> [--width 1200] [--height 630] [--json]

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
import sys
import tempfile
import time
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
DEFAULT_WIDTH = 1200
DEFAULT_HEIGHT = 630
DEFAULT_GEMINI_MODEL = os.environ.get("NANOBANANA_MODEL") or "gemini-3.1-flash-image"
DEFAULT_ATLAS_MODEL = (
    os.environ.get("ATLASCLOUD_IMAGE_MODEL")
    or "google/nano-banana-2-lite/text-to-image"
)
ATLAS_API_BASE = os.environ.get(
    "ATLASCLOUD_MEDIA_API_BASE", "https://api.atlascloud.ai/api/v1"
).rstrip("/")
ATLAS_POLL_DELAYS = (1, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4)
OPENVERSE_API = "https://api.openverse.engineering/v1/images/"
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
    "gemini-3.1-flash-image",
    "gemini-3.1-flash-lite-image",
    "gemini-3-pro-image",
)


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
        try:
            addr = ipaddress.ip_address(addr_str)
        except ValueError:
            return True
        if (
            addr.is_private
            or addr.is_loopback
            or addr.is_link_local
            or addr.is_reserved
            or addr.is_multicast
            or addr.is_unspecified
        ):
            return True
    return False


def _is_blocked_address(addr_text: str) -> bool:
    try:
        addr = ipaddress.ip_address(addr_text)
    except ValueError:
        return True
    return (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
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


_NO_REDIRECT_OPENER = urllib.request.build_opener(_NoRedirectHandler())


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


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    """Atomic write via mkstemp + os.replace. Mirrors load_untrusted_root.py."""
    if path.exists() and path.is_symlink():
        raise ValueError(f"refusing to overwrite symlink: {path}")
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
    if path.exists() and path.is_symlink():
        raise ValueError(f"refusing to overwrite symlink: {path}")
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


def _fit_image_bytes(data: bytes, width: int, height: int) -> bytes:
    """Resize and center-crop image bytes to exact output dimensions."""
    try:
        from PIL import Image, ImageOps  # type: ignore
    except ImportError as e:
        raise RuntimeError("Pillow is required to enforce --width/--height") from e

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


def _http_post_json(url: str, payload: dict, headers: Optional[dict] = None) -> Optional[dict]:
    """POST JSON exactly once with the same URL and response guards as GET."""
    ok, reason, host, port, infos = _resolve_public_url(url)
    if not ok or host is None or port is None:
        print(f"[http] refused (scheme/host policy): {_url_for_log(url)} ({reason})", file=sys.stderr)
        return None
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            **(headers or {}),
        },
        method="POST",
    )
    try:
        with _PinnedDNS(host, port, infos):
            with _NO_REDIRECT_OPENER.open(req, timeout=HTTP_TIMEOUT) as resp:
                status = getattr(resp, "status", 200)
                if 300 <= int(status) < 400:
                    print(f"[http] redirect refused: {_url_for_log(url)}", file=sys.stderr)
                    return None
                raw = resp.read(MAX_IMAGE_BYTES + 1)
                if len(raw) > MAX_IMAGE_BYTES:
                    print(
                        f"[http] response exceeds {MAX_IMAGE_BYTES} bytes; refusing",
                        file=sys.stderr,
                    )
                    return None
    except Exception as e:
        print(f"[http] POST {_url_for_log(url)}: {e}", file=sys.stderr)
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"[http] json decode failed: {e}", file=sys.stderr)
        return None


def _try_gemini(topic: str, tags: list[str], out_dir: Path, width: int, height: int, model: str) -> Optional[dict]:
    """Ladder step 2: direct Gemini API."""
    api_key = os.environ.get("GOOGLE_AI_API_KEY")
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
                    "mime_type": "image/png",
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
            print(f"[gemini] {try_model} interactions.create failed: {e}", file=sys.stderr)

    if not img_bytes or not _is_supported_image(img_bytes):
        return None

    try:
        img_bytes = _fit_image_bytes(img_bytes, width, height)
    except RuntimeError as e:
        print(f"[image] {e}", file=sys.stderr)
        return None
    hero_path = out_dir / f"{OUTPUT_FILE_PREFIX}.png"
    _atomic_write_bytes(hero_path, img_bytes)
    _atomic_write_text(
        out_dir / "hero-credit.txt",
        f"AI-generated via {used_model}. No attribution required.\nPrompt: {prompt}\n",
    )
    return {"source": "gemini", "model": used_model, "path": str(hero_path)}


def _try_atlas(
    topic: str,
    tags: list[str],
    out_dir: Path,
    width: int,
    height: int,
    model: str,
) -> Optional[dict]:
    """Ladder step 3: Atlas Cloud async image generation."""
    api_key = os.environ.get("ATLASCLOUD_API_KEY")
    if not api_key:
        return None

    prompt = _build_prompt(topic, tags, width, height)
    headers = {"Authorization": f"Bearer {api_key}"}
    submitted = _http_post_json(
        f"{ATLAS_API_BASE}/model/generateImage",
        {
            "model": model,
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "resolution": "1k",
        },
        headers=headers,
    )
    if not submitted or str(submitted.get("code", "200")) != "200":
        print("[atlas] image submission failed", file=sys.stderr)
        return None

    prediction = submitted.get("data") or submitted
    prediction_id = prediction.get("id") if isinstance(prediction, dict) else None
    if not prediction_id:
        print("[atlas] image submission returned no prediction id", file=sys.stderr)
        return None

    output_url: Optional[str] = None
    for delay in ATLAS_POLL_DELAYS:
        time.sleep(delay)
        polled = _http_get_json(
            f"{ATLAS_API_BASE}/model/prediction/{urllib.parse.quote(str(prediction_id), safe='')}",
            headers=headers,
        )
        if not polled or str(polled.get("code", "200")) != "200":
            continue
        result = polled.get("data") or polled
        if not isinstance(result, dict):
            continue
        status = str(result.get("status") or "").lower()
        if status in {"failed", "timeout", "canceled", "cancelled"}:
            print(f"[atlas] prediction ended with status {status}", file=sys.stderr)
            return None
        if status in {"completed", "succeeded"}:
            outputs = result.get("outputs") or []
            if outputs and isinstance(outputs[0], str):
                output_url = outputs[0]
            break

    if not output_url:
        print("[atlas] prediction did not complete within the polling window", file=sys.stderr)
        return None
    img_bytes = _download_image(output_url)
    if not img_bytes:
        return None
    try:
        img_bytes = _fit_image_bytes(img_bytes, width, height)
    except RuntimeError as e:
        print(f"[image] {e}", file=sys.stderr)
        return None
    hero_path = out_dir / f"{OUTPUT_FILE_PREFIX}{_image_ext(img_bytes, '.png')}"
    _atomic_write_bytes(hero_path, img_bytes)
    _atomic_write_text(
        out_dir / "hero-credit.txt",
        f"AI-generated via Atlas Cloud model {model}. No attribution required.\nPrompt: {prompt}\n",
    )
    return {"source": "atlas", "model": model, "path": str(hero_path)}


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
    hero_path = out_dir / f"{OUTPUT_FILE_PREFIX}{_image_ext(img_bytes)}"
    _atomic_write_bytes(hero_path, img_bytes)
    user = item.get("user", {})
    credit = (
        f'Photo by {user.get("name", "Unsplash contributor")} on Unsplash\n'
        f'License: Unsplash License (free for commercial use, no attribution required but appreciated)\n'
        f'Source: {item.get("links", {}).get("html", img_url)}\n'
    )
    _atomic_write_text(out_dir / "hero-credit.txt", credit)
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
    hero_path = out_dir / f"{OUTPUT_FILE_PREFIX}{_image_ext(img_bytes)}"
    _atomic_write_bytes(hero_path, img_bytes)
    credit = (
        f'Photo by {item.get("photographer", "Pexels contributor")} on Pexels\n'
        f'License: Pexels License (free for commercial use)\n'
        f'Source: {item.get("url", img_url)}\n'
    )
    _atomic_write_text(out_dir / "hero-credit.txt", credit)
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
    hero_path = out_dir / f"{OUTPUT_FILE_PREFIX}{_image_ext(img_bytes)}"
    _atomic_write_bytes(hero_path, img_bytes)
    credit = (
        f'Image by {item.get("user", "Pixabay contributor")} on Pixabay\n'
        f'License: Pixabay Content License (free for commercial use)\n'
        f'Source: {item.get("pageURL", img_url)}\n'
    )
    _atomic_write_text(out_dir / "hero-credit.txt", credit)
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
    """Ladder step 4: public API, no key required, CC-licensed."""
    query = " ".join([topic] + tags[:3] + ["editorial illustration"])
    params = urllib.parse.urlencode({
        "q": query, "aspect_ratio": "wide", "license": "cc0,by,by-sa",
        "size": "large", "page_size": 10,
    })
    data = _http_get_json(f"{OPENVERSE_API}?{params}")
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

    ext = _image_ext(img_bytes)
    hero_path = out_dir / f"{OUTPUT_FILE_PREFIX}{ext}"
    _atomic_write_bytes(hero_path, img_bytes)

    title = item.get("title") or "untitled"
    creator = item.get("creator") or "Unknown"
    license_name = (item.get("license") or "CC").upper()
    source = item.get("source") or "openverse"
    src_url = item.get("foreign_landing_url") or img_url
    _atomic_write_text(
        out_dir / "hero-credit.txt",
        f'"{title}" by {creator}\nLicense: {license_name}\nSource: {source}\nURL: {src_url}\n',
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
        "--atlas-model",
        default=DEFAULT_ATLAS_MODEL,
        help="Atlas Cloud image model name",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON result to stdout")
    args = parser.parse_args()

    dims_ok, dims_error = _validate_dimensions(args.width, args.height)
    if not dims_ok:
        msg = f"ERROR: {dims_error}"
        if args.json:
            print(json.dumps({"error": "invalid-dimensions", "message": msg}))
        else:
            print(msg, file=sys.stderr)
        return 1

    raw_out_dir = Path(args.out)
    if raw_out_dir.exists() and raw_out_dir.is_symlink():
        msg = f"ERROR: refusing symlink output directory {raw_out_dir}"
        if args.json:
            print(json.dumps({"error": "out-dir-symlink", "message": msg}))
        else:
            print(msg, file=sys.stderr)
        return 1
    out_dir = raw_out_dir.resolve()
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        msg = f"ERROR: cannot create output directory {out_dir}: {e}"
        if args.json:
            print(json.dumps({"error": "out-dir-create-failed", "message": msg}))
        else:
            print(msg, file=sys.stderr)
        return 1
    if not os.access(out_dir, os.W_OK):
        msg = f"ERROR: output directory {out_dir} is not writable"
        if args.json:
            print(json.dumps({"error": "out-dir-not-writable", "message": msg}))
        else:
            print(msg, file=sys.stderr)
        return 1
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    ladder: list[tuple[str, Callable[[], Optional[dict]]]] = [
        ("gemini", lambda: _try_gemini(args.topic, tags, out_dir, args.width, args.height, args.model)),
        ("atlas", lambda: _try_atlas(
            args.topic, tags, out_dir, args.width, args.height, args.atlas_model
        )),
        ("premium-stock", lambda: _try_premium_stock(args.topic, tags, out_dir, args.width, args.height)),
        ("openverse", lambda: _try_openverse(args.topic, tags, out_dir, args.width, args.height)),
    ]

    for name, fn in ladder:
        try:
            result = fn()
        except (OSError, ValueError) as e:
            msg = f"ERROR: {name} output write refused: {e}"
            if args.json:
                print(json.dumps({"error": "output-write-refused", "message": msg}))
            else:
                print(msg, file=sys.stderr)
            return 1
        if result:
            if args.json:
                print(json.dumps(result))
            else:
                print(f"OK: hero from {result['source']} -> {result['path']}")
            return 0

    err = {
        "error": "no-image-gen-path",
        "message": (
            "Hero image required but no generation path available. Configure Banana MCP, "
            "set GOOGLE_AI_API_KEY or ATLASCLOUD_API_KEY, set "
            "UNSPLASH_ACCESS_KEY / PEXELS_API_KEY / PIXABAY_API_KEY, "
            "or place a 1200x630 hero.png in the draft folder manually."
        ),
    }
    if args.json:
        print(json.dumps(err))
    else:
        print(err["message"], file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
