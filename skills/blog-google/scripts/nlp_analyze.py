#!/usr/bin/env python3
"""
Google Cloud Natural Language API - Entity, sentiment, and content analysis.

Enhances E-E-A-T scoring with NLP entity coverage, sentiment analysis,
and Google's own content classification taxonomy.

Usage:
    python nlp_analyze.py --text "Your content here" --json
    python nlp_analyze.py --url https://example.com --json
    python nlp_analyze.py --text "Your content" --features entities,sentiment,classify
"""

import argparse
import http.client
import ipaddress
import json
import socket
import ssl
import sys
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

try:
    from google_auth import describe_google_api_error, get_api_key, request_with_retries
except ImportError:
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from google_auth import describe_google_api_error, get_api_key, request_with_retries

NLP_ENDPOINT = "https://language.googleapis.com/v2/documents:annotateText"
MAX_TEXT_CHARS = 100000
MAX_FETCH_BYTES = 1_000_000

# Free tier: 5,000 units/month per feature
# Paid: $0.001 per 1,000-character unit for entity/sentiment
FEATURES = {
    "entities": "extractEntities",
    "sentiment": "extractDocumentSentiment",
    "classify": "classifyText",
    "categories": "classifyText",
    "moderate": "moderateText",
}


def analyze_text(
    text: str,
    features: Optional[list] = None,
    api_key: Optional[str] = None,
    language: str = "en",
) -> dict:
    """
    Analyze text using Google Cloud Natural Language API.

    Args:
        text: Text content to analyze (max 100,000 characters).
        features: List of features: entities, sentiment, classify, moderate.
        api_key: Google API key.
        language: Language code (default: en).

    Returns:
        Dictionary with entities, sentiment, categories, and moderation results.
    """
    result = {
        "text_length": len(text),
        "language": language,
        "entities": [],
        "sentiment": None,
        "categories": [],
        "moderation": [],
        "error": None,
    }

    key = api_key or get_api_key()
    if not key:
        result["error"] = "No API key. Set GOOGLE_API_KEY or add 'api_key' to config."
        return result

    if features is None:
        features = ["entities", "sentiment", "classify"]

    # Build request
    feature_map = {}
    for f in features:
        api_feature = FEATURES.get(f)
        if api_feature:
            feature_map[api_feature] = True

    body = {
        "document": {
            "type": "PLAIN_TEXT",
            "content": text[:MAX_TEXT_CHARS],
            "languageCode": language,
        },
        "features": feature_map,
        "encodingType": "UTF8",
    }

    try:
        resp = request_with_retries(
            "POST",
            f"{NLP_ENDPOINT}?key={key}",
            json=body,
            timeout=30,
        )

        if resp.status_code == 403:
            try:
                error_payload = resp.json()
            except ValueError:
                error_payload = {"error": {"code": 403, "message": "Request denied; invalid JSON response"}}
            result["error"] = describe_google_api_error(
                error_payload, "Cloud Natural Language", "Check the API key and service access."
            )
            return result

        if resp.status_code == 429:
            result["error"] = "NLP API quota exceeded. Check the project quota in Google Cloud Console."
            return result

        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        result["error"] = describe_google_api_error(e, "Cloud Natural Language")
        return result

    # Entities
    for entity in data.get("entities", []):
        mentions = entity.get("mentions", [])
        result["entities"].append({
            "name": entity.get("name", ""),
            "type": entity.get("type", "UNKNOWN"),
            "salience": round(entity.get("salience", 0), 4),
            "sentiment_score": entity.get("sentiment", {}).get("score"),
            "sentiment_magnitude": entity.get("sentiment", {}).get("magnitude"),
            "mention_count": len(mentions),
            "metadata": entity.get("metadata", {}),
        })

    # Sort by salience (most important first)
    result["entities"].sort(key=lambda e: e["salience"], reverse=True)

    # Document sentiment
    doc_sentiment = data.get("documentSentiment", {})
    if doc_sentiment:
        score = doc_sentiment.get("score", 0)
        magnitude = doc_sentiment.get("magnitude", 0)
        if score > 0.25:
            tone = "positive"
        elif score < -0.25:
            tone = "negative"
        else:
            tone = "neutral"

        result["sentiment"] = {
            "score": round(score, 3),
            "magnitude": round(magnitude, 3),
            "tone": tone,
            "interpretation": (
                f"{'Positive' if score > 0 else 'Negative' if score < 0 else 'Neutral'} "
                f"(score: {score:.2f}) with "
                f"{'high' if magnitude > 2 else 'moderate' if magnitude > 0.5 else 'low'} "
                f"emotional content (magnitude: {magnitude:.2f})"
            ),
        }

        # Sentence-level sentiment
        sentences = data.get("sentences", [])
        if sentences:
            result["sentiment"]["sentence_count"] = len(sentences)
            sent_scores = [s.get("sentiment", {}).get("score", 0) for s in sentences]
            result["sentiment"]["most_positive"] = max(sent_scores) if sent_scores else 0
            result["sentiment"]["most_negative"] = min(sent_scores) if sent_scores else 0

    # Categories (content classification)
    for cat in data.get("categories", []):
        result["categories"].append({
            "name": cat.get("name", ""),
            "confidence": round(cat.get("confidence", 0), 4),
        })

    # Moderation categories
    for mod in data.get("moderationCategories", []):
        if mod.get("confidence", 0) > 0.5:
            result["moderation"].append({
                "name": mod.get("name", ""),
                "confidence": round(mod.get("confidence", 0), 4),
            })

    return result


@dataclass(frozen=True)
class _FetchTarget:
    url: str
    scheme: str
    hostname: str
    port: int
    request_target: str
    addresses: tuple[str, ...]


def _resolve_fetch_target(url: str) -> _FetchTarget:
    if any(ord(char) < 32 or ord(char) == 127 for char in url):
        raise ValueError("URL must not contain control characters")
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("URL must use http or https")
    if parsed.username or parsed.password:
        raise ValueError("URL must not contain credentials")
    if not parsed.hostname:
        raise ValueError("URL must include a host")
    hostname = parsed.hostname.encode("idna").decode("ascii")
    try:
        infos = socket.getaddrinfo(hostname, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"Could not resolve host: {exc}") from exc
    addresses = []
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global or ip.is_multicast or ip.is_unspecified:
            raise ValueError("URL resolves to a blocked network address")
        value = str(ip)
        if value not in addresses:
            addresses.append(value)
    if not addresses:
        raise ValueError("Host did not resolve to a usable public address")
    request_target = parsed.path or "/"
    if parsed.query:
        request_target += f"?{parsed.query}"
    return _FetchTarget(
        url=url,
        scheme=parsed.scheme,
        hostname=hostname,
        port=parsed.port or (443 if parsed.scheme == "https" else 80),
        request_target=request_target,
        addresses=tuple(addresses),
    )


def _validate_fetch_url(url: str) -> str:
    """Validate a fetch URL for callers that only need a guard result."""
    return _resolve_fetch_target(url).url


class _PinnedHTTPConnection(http.client.HTTPConnection):
    """HTTP connection whose TCP peer is a previously validated numeric IP."""

    def __init__(self, host: str, port: int, pinned_ip: str, timeout: float):
        super().__init__(host, port=port, timeout=timeout)
        self._pinned_ip = pinned_ip

    def connect(self) -> None:
        self.sock = socket.create_connection(
            (self._pinned_ip, self.port), self.timeout, self.source_address
        )


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS connection pinned to an IP while retaining hostname TLS checks."""

    def __init__(self, host: str, port: int, pinned_ip: str, timeout: float):
        super().__init__(host, port=port, timeout=timeout, context=ssl.create_default_context())
        self._pinned_ip = pinned_ip

    def connect(self) -> None:
        raw_sock = socket.create_connection(
            (self._pinned_ip, self.port), self.timeout, self.source_address
        )
        try:
            self.sock = self._context.wrap_socket(raw_sock, server_hostname=self.host)
        except Exception:
            raw_sock.close()
            raise


def _host_header(target: _FetchTarget) -> str:
    host = f"[{target.hostname}]" if ":" in target.hostname else target.hostname
    default_port = 443 if target.scheme == "https" else 80
    return host if target.port == default_port else f"{host}:{target.port}"


def _request_pinned(target: _FetchTarget) -> tuple[int, dict[str, str], bytes, str]:
    """Fetch once using only validated IPs, with no environment proxy lookup."""
    last_error = None
    for address in target.addresses:
        connection_class = _PinnedHTTPSConnection if target.scheme == "https" else _PinnedHTTPConnection
        connection = connection_class(target.hostname, target.port, address, timeout=15)
        try:
            connection.request(
                "GET",
                target.request_target,
                headers={
                    "Accept-Encoding": "identity",
                    "Connection": "close",
                    "Host": _host_header(target),
                    "User-Agent": "Mozilla/5.0 (compatible; ClaudeSEO/1.10 NLP Analyzer)",
                },
            )
            response = connection.getresponse()
            headers = {key.lower(): value for key, value in response.getheaders()}
            content_length = headers.get("content-length")
            if content_length:
                try:
                    declared_length = int(content_length)
                except ValueError as exc:
                    raise ValueError("Fetched response had an invalid Content-Length") from exc
                if declared_length < 0:
                    raise ValueError("Fetched response had an invalid Content-Length")
                if declared_length > MAX_FETCH_BYTES:
                    raise ValueError("Fetched response exceeded 1 MB")
            if headers.get("content-encoding", "identity").lower() not in {"", "identity"}:
                raise ValueError("Fetched response used an unsupported content encoding")
            body = response.read(MAX_FETCH_BYTES + 1)
            if len(body) > MAX_FETCH_BYTES:
                raise ValueError("Fetched response exceeded 1 MB")
            encoding = response.headers.get_content_charset() or "utf-8"
            return response.status, headers, body, encoding
        except ValueError:
            raise
        except (OSError, ssl.SSLError, http.client.HTTPException) as exc:
            last_error = exc
        finally:
            connection.close()
    raise ValueError(f"Could not connect to validated public address: {last_error}")


def _fetch_url_text(url: str, max_redirects: int = 3) -> str:
    current = url
    for _ in range(max_redirects + 1):
        target = _resolve_fetch_target(current)
        status, headers, body, encoding = _request_pinned(target)
        if status in {301, 302, 303, 307, 308}:
            location = headers.get("location")
            if not location:
                raise ValueError("Redirect response missing Location header")
            current = urljoin(current, location)
            continue
        if not 200 <= status < 300:
            raise ValueError(f"Fetched URL returned HTTP {status}")
        try:
            return body.decode(encoding, errors="replace")
        except LookupError as exc:
            raise ValueError(
                f"Fetched response declared an unsupported charset: {encoding}"
            ) from exc
    raise ValueError("Too many redirects")


def analyze_url(
    url: str,
    features: Optional[list] = None,
    api_key: Optional[str] = None,
) -> dict:
    """
    Fetch a URL's text content and analyze it.

    Args:
        url: URL to fetch and analyze.
        features: NLP features to extract.
        api_key: API key override.

    Returns:
        Dictionary with NLP analysis results.
    """
    try:
        html = _fetch_url_text(url)
    except (requests.exceptions.RequestException, ValueError) as e:
        return {"error": f"Could not fetch URL: {e}"}

    # Extract text from HTML (simple approach)
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        # Remove script and style
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
    except ImportError:
        # Fallback: regex-based text extraction
        import re
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

    if not text or len(text) < 50:
        return {"error": "Extracted text too short for meaningful NLP analysis."}

    result = analyze_text(text, features=features, api_key=api_key)
    result["source_url"] = url
    result["extracted_text_length"] = len(text)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Google Cloud Natural Language API - Entity/sentiment/classification for SEO"
    )
    parser.add_argument("--text", "-t", help="Text to analyze")
    parser.add_argument("--url", "-u", help="URL to fetch and analyze")
    parser.add_argument(
        "--features", "-f",
        default="entities,sentiment,classify",
        help="Comma-separated features: entities, sentiment, classify, moderate (default: entities,sentiment,classify)",
    )
    parser.add_argument("--api-key", help="API key override")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.text and not args.url:
        print("Error: Provide --text or --url to analyze.", file=sys.stderr)
        sys.exit(1)

    features = [f.strip() for f in args.features.split(",")]

    if args.url:
        result = analyze_url(args.url, features=features, api_key=args.api_key)
    else:
        result = analyze_text(args.text, features=features, api_key=args.api_key)

    if result.get("error"):
        print(f"Error: {result['error']}", file=sys.stderr)
        if not args.json:
            sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("source_url"):
            print(f"=== NLP Analysis: {result['source_url']} ===")
            print(f"Text extracted: {result.get('extracted_text_length', 0):,} chars")
        else:
            print(f"=== NLP Analysis ({result.get('text_length', 0):,} chars) ===")

        sent = result.get("sentiment")
        if sent:
            print(f"\nSentiment: {sent['tone'].upper()} (score: {sent['score']}, magnitude: {sent['magnitude']})")
            print(f"  {sent['interpretation']}")

        entities = result.get("entities", [])
        if entities:
            print(f"\nTop Entities ({len(entities)} total):")
            for e in entities[:15]:
                print(f"  [{e['type']:12s}] {e['name']} (salience: {e['salience']:.3f})")

        categories = result.get("categories", [])
        if categories:
            print(f"\nContent Categories:")
            for c in categories:
                print(f"  {c['name']} ({c['confidence']:.1%})")

        moderation = result.get("moderation", [])
        if moderation:
            print(f"\nModeration Flags:")
            for m in moderation:
                print(f"  {m['name']} ({m['confidence']:.1%})")


if __name__ == "__main__":
    main()
