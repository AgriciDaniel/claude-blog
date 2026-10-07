#!/usr/bin/env python3
"""Verify source-ledger URLs and apply an explicit claim-review decision file."""

from __future__ import annotations

import argparse
import concurrent.futures
import copy
import hashlib
import http.client
import ipaddress
import json
import re
import socket
import ssl
import subprocess
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse, urlunsplit

from source_evidence import can_support, ledger_errors, ledger_index, lifecycle, source_errors

REPO = Path(__file__).resolve().parent.parent
LEDGER_PATH = REPO / "references" / "source-ledger.json"
STOPWORDS = {
    "about", "after", "also", "and", "are", "because", "been", "being",
    "between", "both", "but", "can", "could", "does", "each", "for",
    "from", "had", "has", "have", "how", "into", "its", "may", "more",
    "must", "not", "only", "other", "our", "out", "over", "per", "same",
    "should", "than", "that", "the", "their", "them", "then", "there",
    "these", "they", "this", "those", "through", "under", "use", "used",
    "uses", "using", "very", "was", "were", "what", "when", "where",
    "which", "while", "who", "will", "with", "without", "would", "your",
}
DECISION_GROUPS = {
    "confirmed_by_content",
    "confirmed_by_manual_review",
    "corrected",
    "retired",
    "qualified",
    "unverified",
}
MAX_BYTES = 20 * 1024 * 1024
MIN_CONTENT_COVERAGE = 0.60


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--review-file",
        default="references/source-review-2026-08-25.json",
        help="Brain-relative explicit review decisions.",
    )
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--offline-check",
        action="store_true",
        help="Validate current ledger verification records without network access.",
    )
    return parser.parse_args(argv)


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"ERROR: cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"ERROR: {path} must contain a JSON object")
    return value


def parse_day(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"ERROR: {label} must be YYYY-MM-DD") from exc


def public_address(value: str) -> bool:
    address = ipaddress.ip_address(value)
    return (address.is_global and not address.is_reserved and not address.is_multicast
            and not address.is_loopback and not address.is_link_local and not address.is_unspecified)


def validate_public_https(url: str) -> tuple[str, int, list[Any]]:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("URL must be public HTTPS without credentials")
    host = parsed.hostname
    if host.lower().rstrip(".") in {"localhost"} or host.lower().rstrip(".").endswith((".localhost", ".local", ".onion")):
        raise ValueError("URL host is not public")
    port = parsed.port or 443
    if not 1 <= port <= 65535:
        raise ValueError("URL port is invalid")
    try:
        addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
    except OSError as exc:
        raise ValueError(f"DNS resolution failed: {exc}") from exc
    if not addresses:
        raise ValueError("DNS resolution returned no addresses")
    for family, kind, protocol, _name, sockaddr in addresses:
        if (family not in {socket.AF_INET, socket.AF_INET6} or kind != socket.SOCK_STREAM
                or protocol != socket.IPPROTO_TCP or sockaddr[1] != port or not public_address(sockaddr[0])):
            raise ValueError(f"URL resolved to a non-public or invalid address: {sockaddr[0]}")
    return host, port, list(addresses)


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Connect only to prevalidated sockaddr tuples, preserving TLS host/SNI.

    Direct stdlib sockets do not consult environment proxies or perform another
    hostname lookup. No process-global DNS monkeypatch is used by worker threads.
    """
    def __init__(self, host: str, port: int, addresses: list[Any], *, timeout: float):
        super().__init__(host, port, timeout=timeout, context=ssl.create_default_context())
        self.addresses = addresses

    def connect(self) -> None:
        last_error = None
        deadline = time.monotonic() + self.timeout
        for family, kind, protocol, _name, sockaddr in self.addresses:
            if not public_address(sockaddr[0]) or sockaddr[1] != self.port:
                raise ValueError("pinned connection address is not public or changed port")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("source connection timed out")
            raw = socket.socket(family, kind, protocol)
            try:
                raw.settimeout(remaining)
                raw.connect(sockaddr)
                self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
                return
            except OSError as exc:
                raw.close()
                last_error = exc
        if last_error:
            raise last_error
        raise ValueError("no pinned public connection address")


def fetch_source(url: str) -> dict[str, Any]:
    # No requests Session or environment proxy trust: every redirect gets its
    # own validated address set and connects directly to those exact addresses.
    current = url
    deadline = time.monotonic() + 30
    for _ in range(7):
        host, port, addresses = validate_public_https(current)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("source fetch timed out")
        connection = PinnedHTTPSConnection(host, port, addresses, timeout=remaining)
        try:
            parsed = urlparse(current)
            target = urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
            connection.request("GET", target, headers={
                "User-Agent": "Mozilla/5.0 ClaudeBlogSourceAudit/1.0",
                "Accept": "text/html,application/pdf,application/json,text/plain,*/*;q=0.5",
            })
            response = connection.getresponse()
            if response.status in {301, 302, 303, 307, 308}:
                location = response.getheader("location")
                if not location:
                    raise ValueError("redirect response is missing Location")
                current = urljoin(current, location)
                continue
            if not 200 <= response.status < 300:
                raise ValueError(f"source returned HTTP {response.status}")
            body = bytearray()
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("source fetch timed out")
                if connection.sock is not None:
                    connection.sock.settimeout(remaining)
                chunk = response.read1(64 * 1024)
                if not chunk:
                    break
                body.extend(chunk)
                if len(body) > MAX_BYTES:
                    raise ValueError(f"source exceeds {MAX_BYTES} bytes")
            content_type = response.getheader("content-type", "").split(";", 1)[0].lower()
            text = extract_text(bytes(body), content_type, current)
            normalized = normalize_text(text)
            return {
                "http_status": response.status, "final_url": current,
                "content_type": content_type, "bytes": len(body),
                "normalized_content_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
                "text": normalized, "reviewable_text_bytes": len(normalized.encode("utf-8")),
            }
        finally:
            connection.close()
    raise ValueError("too many redirects")


def extract_text(body: bytes, content_type: str, final_url: str) -> str:
    if content_type == "application/pdf" or urlparse(final_url).path.lower().endswith(".pdf"):
        with tempfile.NamedTemporaryFile(suffix=".pdf") as pdf_file:
            with tempfile.NamedTemporaryFile(suffix=".txt") as text_file:
                pdf_file.write(body)
                pdf_file.flush()
                result = subprocess.run(
                    ["pdftotext", "-layout", pdf_file.name, text_file.name],
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=30,
                )
                if result.returncode:
                    raise ValueError("pdftotext could not extract the review source")
                return Path(text_file.name).read_text(
                    encoding="utf-8", errors="replace"
                )
    if "html" in content_type:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(body, "html.parser")
        for element in soup(["script", "style", "svg", "noscript", "template"]):
            element.decompose()
        review_root = soup.find("main") or soup.find("article") or soup
        return review_root.get_text(" ", strip=True)
    return body.decode("utf-8", errors="replace")


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def claim_text(source: dict[str, Any]) -> str:
    claims = source.get("claims")
    if not isinstance(claims, list):
        return ""
    return " ".join(str(item) for item in claims if isinstance(item, str))


def claim_evidence(source: dict[str, Any], text: str) -> dict[str, Any]:
    claim = claim_text(source).lower()
    tokens = list(
        dict.fromkeys(
            token
            for token in re.findall(r"[a-z0-9]+", claim)
            if len(token) >= 4 and token not in STOPWORDS and not token.isdigit()
        )
    )
    matched = sum(token in text for token in tokens)
    coverage = matched / len(tokens) if tokens else 1.0
    numbers = list(
        dict.fromkeys(re.findall(r"(?<![a-z])\d+(?:\.\d+)?%?", claim))
    )
    missing_numbers = [
        number
        for number in numbers
        if number not in text
        and not (number.startswith("0") and number.lstrip("0") in text)
    ]
    return {
        "claim_token_coverage": round(coverage, 3),
        "missing_numeric_literals": missing_numbers,
    }


def review_decisions(review: dict[str, Any]) -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    decisions: dict[str, str] = {}
    corrections: dict[str, dict[str, Any]] = {}
    for group in DECISION_GROUPS:
        value = review.get(group, [] if group not in {"corrected", "qualified"} else {})
        if group in {"corrected", "qualified"}:
            if not isinstance(value, dict):
                raise SystemExit("ERROR: corrected/qualified review decisions must be an object")
            for source_id, correction in value.items():
                if not isinstance(correction, dict):
                    raise SystemExit(f"ERROR: corrected decision for {source_id} must be an object")
                if source_id in decisions:
                    raise SystemExit(f"ERROR: duplicate review decision for {source_id}")
                decisions[source_id] = group
                corrections[source_id] = correction
            continue
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise SystemExit(f"ERROR: {group} review decisions must be a string list")
        for source_id in value:
            if source_id in decisions:
                raise SystemExit(f"ERROR: duplicate review decision for {source_id}")
            decisions[source_id] = group
    return decisions, corrections


def next_refresh(source: dict[str, Any], reviewed_on: date) -> date:
    if source.get("living_doc") is True:
        days = 31
    elif str(source.get("source_type", "")) in {"primary", "practitioner", "market"}:
        days = 90
    else:
        days = 180
    return reviewed_on + timedelta(days=days)


def apply_correction(source: dict[str, Any], correction: dict[str, Any]) -> None:
    allowed = {
        "title", "url", "source_type", "claims", "supports_claims",
        "confidence", "evidence_tier", "limitations", "last_updated",
        "published", "date_precision", "living_doc", "review_note",
    }
    unknown = sorted(set(correction) - allowed)
    if unknown:
        raise SystemExit(
            f"ERROR: unsupported correction fields for {source.get('id')}: {unknown}"
        )
    for key, value in correction.items():
        if key != "review_note":
            source[key] = value


def offline_check(ledger: dict[str, Any], as_of: date) -> dict[str, Any]:
    failures = ledger_errors(ledger, as_of=as_of)
    try:
        index = ledger_index(ledger)
    except ValueError:
        index = {}
    verified = sum(can_support(source, as_of=as_of) for source in index.values())
    states = {state: sum(lifecycle(source) == state for source in index.values()) for state in ("active", "retired", "unverified")}
    # Explicit quarantine is truthful history, but not successful verification.
    failures.extend(f"{source_id}: unverified evidence requires review" for source_id, source in index.items() if lifecycle(source) == "unverified")
    return {
        "status": "pass" if not failures else "fail", "verified": verified,
        "failures": failures, "lifecycle_counts": states,
        "evidence_validation": {
            "mode": "packaged_reviewed_excerpt",
            "captured_artifacts_checked": True,
            "excerpt_integrity_checked": True,
            "full_capture_checked": False,
            "full_document_artifacts_checked": False,
            "semantic_entailment_checked": False,
            "artifact_coverage": "Unique paths referenced by active ledger records; every excerpt and provenance record in those files must bind to an active source. Unreferenced and historical files are outside this gate.",
            "scope": "Packaged excerpt bytes/hash, normalized excerpt agreement, URL/retrieval/review/full-document-hash provenance, lifecycle, chronology and freshness. Full-page availability and semantic entailment remain separate review boundaries.",
        },
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    as_of = parse_day(args.as_of, "--as-of")
    ledger = load_object(LEDGER_PATH)
    if args.offline_check:
        result = offline_check(ledger, as_of)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == "pass" else 1

    review_path = (REPO / args.review_file).resolve()
    if not review_path.is_relative_to(REPO):
        raise SystemExit("ERROR: --review-file must stay inside the Brain")
    review = load_object(review_path)
    if review.get("reviewed_on") != as_of.isoformat():
        raise SystemExit("ERROR: review-file date does not match --as-of")
    decisions, corrections = review_decisions(review)

    try:
        source_by_id = ledger_index(ledger)
    except ValueError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    extra = sorted(set(decisions) - set(source_by_id))
    if extra:
        raise SystemExit(f"ERROR: review decisions reference unknown IDs: {extra}")
    # An explicit subset can be reviewed. Unreviewed or failed records retain
    # their old evidence and remain visible to the final semantic check.
    review_evidence = review.get("evidence", {})
    dispositions = review.get("dispositions", {})
    if not isinstance(review_evidence, dict) or not isinstance(dispositions, dict):
        raise SystemExit("ERROR: evidence and dispositions must be objects keyed by source ID")
    staged = {source_id: copy.deepcopy(source) for source_id, source in source_by_id.items() if source_id in decisions}
    for source_id, source in staged.items():
        if decisions[source_id] in {"corrected", "qualified"}:
            apply_correction(source, corrections.get(source_id, {}))
    urls = sorted({str(source["url"]) for source_id, source in staged.items() if decisions[source_id] not in {"retired", "unverified"}})
    fetched: dict[str, dict[str, Any]] = {}
    network_failures: list[dict[str, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_map = {executor.submit(fetch_source, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_map):
            url = future_map[future]
            try:
                fetched[url] = future.result()
            except Exception as exc:
                network_failures.append({"url": url, "error": f"{type(exc).__name__}: {exc}"})

    results: list[dict[str, Any]] = []
    review_failures: list[dict[str, str]] = []
    for source_id, source in staged.items():
        decision = decisions[source_id]
        disposition = dispositions.get(source_id, {})
        if not isinstance(disposition, dict):
            review_failures.append({"id": source_id, "error": "disposition must be an object"})
            continue
        if decision == "retired":
            source.update(status="retired", retired_on=as_of.isoformat(), retirement_reason=disposition.get("retirement_reason", ""), replacement_source_ids=disposition.get("replacement_source_ids", []))
            # Keep prior retrieval and verification exactly as history. Retirement
            # neither needs a successful fetch nor invents a new retrieval date.
        elif decision == "unverified":
            source.update(status="unverified", unverified_reason=disposition.get("unverified_reason", ""))
        else:
            evidence = fetched.get(str(source["url"]))
            if evidence is None:
                original = source_by_id[source_id]
                original.setdefault("retrieval_attempts", []).append({"attempted_on": as_of.isoformat(), "url": source["url"], "status": "failed"})
                continue
            claim_check = claim_evidence(source, evidence["text"])
            if decision == "confirmed_by_content" and (claim_check["claim_token_coverage"] < MIN_CONTENT_COVERAGE or claim_check["missing_numeric_literals"]):
                review_failures.append({"id": source_id, "error": "content-confirmation thresholds not met"})
                continue
            reviewed = review_evidence.get(source_id, {})
            if not isinstance(reviewed, dict):
                reviewed = {}
            # Evidence must be explicitly bound by the reviewer to the fetched
            # content. A review file authored against an older page fails closed.
            if reviewed.get("normalized_content_sha256") != evidence["normalized_content_sha256"]:
                review_failures.append({"id": source_id, "error": "review evidence hash does not match retrieved content"})
                continue
            excerpt = reviewed.get("evidence_excerpt", "")
            if not isinstance(excerpt, str) or normalize_text(excerpt) not in evidence["text"] or not excerpt.strip():
                review_failures.append({"id": source_id, "error": "review excerpt absent from retrieved content"})
                continue
            source.update(status="active", retrieved=as_of.isoformat(), last_verified=as_of.isoformat(), refresh_due=next_refresh(source, as_of).isoformat())
            source["verification"] = {
                "reviewed_on": as_of.isoformat(), "decision": decision,
                "method": "public-source content check plus explicit claim review",
                **{key: evidence[key] for key in ("http_status", "final_url", "content_type", "reviewable_text_bytes", "normalized_content_sha256")},
                **claim_check,
                "review_note": reviewed.get("review_note", ""),
                "evidence_excerpt": excerpt,
                "evidence_path": reviewed.get("evidence_path", ""),
                "captured_excerpt_path": reviewed.get("captured_excerpt_path", ""),
                "captured_excerpt_sha256": reviewed.get("captured_excerpt_sha256", ""),
                "normalized_content_hash_scope": "full reviewed document; excerpt artifact hash recorded separately",
            }
        errors = source_errors(source, as_of=as_of)
        if errors:
            review_failures.append({"id": source_id, "error": "; ".join(errors)})
            continue
        source_by_id[source_id].clear()
        source_by_id[source_id].update(source)
        results.append({"id": source_id, "decision": decision})

    semantic = offline_check(ledger, as_of)
    complete = not network_failures and not review_failures and semantic["status"] == "pass"
    # The aggregate date advances only when every active source was actually
    # reviewed on this day, never merely because stale candidates were fetched.
    all_reviewed_today = all(source.get("verification", {}).get("reviewed_on") == as_of.isoformat() for source in source_by_id.values() if lifecycle(source) == "active")
    if complete and all_reviewed_today:
        ledger["last_verified"] = as_of.isoformat()
    ledger["status"] = "reviewed-research" if complete else "partial-review"
    if args.apply:
        LEDGER_PATH.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "pass" if complete else "fail", "applied": args.apply,
        "reviewed": len(results), "unique_urls": len(urls),
        "decisions": {group: sum(item["decision"] == group for item in results) for group in sorted(DECISION_GROUPS)},
        "results": results, "network_failures": network_failures,
        "review_failures": review_failures, "failures": semantic["failures"],
    }, indent=2, sort_keys=True))
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
