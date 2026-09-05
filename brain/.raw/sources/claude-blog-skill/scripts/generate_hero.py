#!/usr/bin/env python3
"""Generate or fetch a 1200x630 hero image for a blog post.

Implements the v1.9.0 Blog Delivery Contract hero-image ladder. The
orchestrator handles step 1 (Banana MCP) when available; this script
handles steps 2-4 and produces the final `hero.<ext>` + `hero-credit.txt`
in the requested output directory.

Ladder:
  1. (Orchestrator only) Banana MCP via nanobanana-mcp
  2. Direct Gemini API via google-genai SDK (requires GOOGLE_AI_API_KEY)
  3. Premium stock APIs: Unsplash, Pexels, Pixabay (any one key suffices)
  4. Openverse public API (CC-licensed; no key required)
  5. Exit nonzero with setup instructions

Usage:
    python3 scripts/generate_hero.py --topic "<title>" --tags "a,b,c" \\
        --out <draft-folder> [--width 1200] [--height 630] [--json]

Returns 0 on success (hero.<ext> + hero-credit.txt written). Returns 1
when every ladder step is exhausted with no successful generation.
"""

from __future__ import annotations

import argparse
import base64
import ipaddress
import json
import os
import socket
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable, Optional

OUTPUT_FILE_PREFIX = "hero"
DEFAULT_WIDTH = 1200
DEFAULT_HEIGHT = 630
DEFAULT_GEMINI_MODEL = os.environ.get("NANOBANANA_MODEL") or "gemini-3.1-flash-image"
OPENVERSE_API = "https://api.openverse.engineering/v1/images/"
UNSPLASH_API = "https://api.unsplash.com/search/photos"
PEXELS_API = "https://api.pexels.com/v1/search"
PIXABAY_API = "https://pixabay.com/api/"
USER_AGENT = "claude-blog/1.9.2 (+https://github.com/AgriciDaniel/claude-blog)"
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


def _validate_url(url: str) -> bool:
    """Return True if url is safe to fetch (http/https + public host).

    Mirrors the policy of `_is_private_address`. The tests rely on
    `socket.gethostbyname` being monkeypatchable; we call it here for
    backwards-compatible test stubbing, then defer to `_is_private_address`
    for the actual public-IP check via getaddrinfo.
    """
    if not isinstance(url, str) or not url:
        return False
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False
    host = parsed.hostname
    if not host:
        return False
    try:
        addr_str = socket.gethostbyname(host)
    except socket.gaierror:
        return False
    except Exception:
        return False
    try:
        addr = ipaddress.ip_address(addr_str)
    except ValueError:
        return False
    if (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
        or addr.is_unspecified
    ):
        return False
    return not _is_private_address(host)


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


def _build_prompt(topic: str, tags: list[str]) -> str:
    parts = [
        f"Editorial illustration for a blog post titled '{topic}'.",
    ]
    if tags:
        parts.append(f"Themes: {', '.join(tags[:5])}.")
    parts.extend([
        "16:9 aspect ratio, suitable as a 1200x630 social cover.",
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
    if not _validate_url(url):
        print(f"[http] refused (scheme/host policy): {url[:80]}", file=sys.stderr)
        return None
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    try:
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

    prompt = _build_prompt(topic, tags)
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

    hero_path = out_dir / f"{OUTPUT_FILE_PREFIX}.png"
    _atomic_write_bytes(hero_path, img_bytes)
    (out_dir / "hero-credit.txt").write_text(
        f"AI-generated via {used_model}. No attribution required.\nPrompt: {prompt}\n",
        encoding="utf-8",
    )
    return {"source": "gemini", "model": used_model, "path": str(hero_path)}


def _try_unsplash(query: str, out_dir: Path) -> Optional[dict]:
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
    hero_path = out_dir / f"{OUTPUT_FILE_PREFIX}{_image_ext(img_bytes)}"
    _atomic_write_bytes(hero_path, img_bytes)
    user = item.get("user", {})
    credit = (
        f'Photo by {user.get("name", "Unsplash contributor")} on Unsplash\n'
        f'License: Unsplash License (free for commercial use, no attribution required but appreciated)\n'
        f'Source: {item.get("links", {}).get("html", img_url)}\n'
    )
    (out_dir / "hero-credit.txt").write_text(credit, encoding="utf-8")
    return {"source": "unsplash", "path": str(hero_path)}


def _try_pexels(query: str, out_dir: Path) -> Optional[dict]:
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
    hero_path = out_dir / f"{OUTPUT_FILE_PREFIX}{_image_ext(img_bytes)}"
    _atomic_write_bytes(hero_path, img_bytes)
    credit = (
        f'Photo by {item.get("photographer", "Pexels contributor")} on Pexels\n'
        f'License: Pexels License (free for commercial use)\n'
        f'Source: {item.get("url", img_url)}\n'
    )
    (out_dir / "hero-credit.txt").write_text(credit, encoding="utf-8")
    return {"source": "pexels", "path": str(hero_path)}


def _try_pixabay(query: str, out_dir: Path) -> Optional[dict]:
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
    hero_path = out_dir / f"{OUTPUT_FILE_PREFIX}{_image_ext(img_bytes)}"
    _atomic_write_bytes(hero_path, img_bytes)
    credit = (
        f'Image by {item.get("user", "Pixabay contributor")} on Pixabay\n'
        f'License: Pixabay Content License (free for commercial use)\n'
        f'Source: {item.get("pageURL", img_url)}\n'
    )
    (out_dir / "hero-credit.txt").write_text(credit, encoding="utf-8")
    return {"source": "pixabay", "path": str(hero_path)}


def _try_premium_stock(topic: str, tags: list[str], out_dir: Path) -> Optional[dict]:
    """Ladder step 3: Unsplash > Pexels > Pixabay (first whose key is set)."""
    query = " ".join([topic] + tags[:3])
    for fn in (_try_unsplash, _try_pexels, _try_pixabay):
        result = fn(query, out_dir)
        if result:
            return result
    return None


def _try_openverse(topic: str, tags: list[str], out_dir: Path) -> Optional[dict]:
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

    ext = _image_ext(img_bytes)
    hero_path = out_dir / f"{OUTPUT_FILE_PREFIX}{ext}"
    _atomic_write_bytes(hero_path, img_bytes)

    title = item.get("title") or "untitled"
    creator = item.get("creator") or "Unknown"
    license_name = (item.get("license") or "CC").upper()
    source = item.get("source") or "openverse"
    src_url = item.get("foreign_landing_url") or img_url
    (out_dir / "hero-credit.txt").write_text(
        f'"{title}" by {creator}\nLicense: {license_name}\nSource: {source}\nURL: {src_url}\n',
        encoding="utf-8",
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
    parser.add_argument("--json", action="store_true", help="Emit JSON result to stdout")
    args = parser.parse_args()

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
        ("premium-stock", lambda: _try_premium_stock(args.topic, tags, out_dir)),
        ("openverse", lambda: _try_openverse(args.topic, tags, out_dir)),
    ]

    for name, fn in ladder:
        result = fn()
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
            "set GOOGLE_AI_API_KEY, set UNSPLASH_ACCESS_KEY / PEXELS_API_KEY / PIXABAY_API_KEY, "
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
