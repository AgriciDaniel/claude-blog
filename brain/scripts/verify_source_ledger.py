#!/usr/bin/env python3
"""Verify source-ledger URLs and apply an explicit claim-review decision file."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import ipaddress
import json
import re
import socket
import subprocess
import tempfile
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

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


def validate_public_https(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("URL must be public HTTPS without credentials")
    try:
        addresses = socket.getaddrinfo(
            parsed.hostname,
            parsed.port or 443,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise ValueError(f"DNS resolution failed: {exc}") from exc
    for address in addresses:
        resolved = ipaddress.ip_address(address[4][0])
        if not resolved.is_global:
            raise ValueError(f"URL resolved to a non-public address: {resolved}")


def fetch_source(url: str) -> dict[str, Any]:
    import requests

    session = requests.Session()
    current = url
    for _ in range(7):
        validate_public_https(current)
        response = session.get(
            current,
            headers={
                "User-Agent": "Mozilla/5.0 ClaudeBlogSourceAudit/1.0",
                "Accept": "text/html,application/pdf,application/json,text/plain,*/*;q=0.5",
            },
            timeout=30,
            allow_redirects=False,
            stream=True,
        )
        if response.is_redirect or response.is_permanent_redirect:
            location = response.headers.get("location")
            if not location:
                raise ValueError("redirect response is missing Location")
            current = urljoin(current, location)
            continue
        response.raise_for_status()
        final_url = response.url
        validate_public_https(final_url)
        body = bytearray()
        for chunk in response.iter_content(64 * 1024):
            body.extend(chunk)
            if len(body) > MAX_BYTES:
                raise ValueError(f"source exceeds {MAX_BYTES} bytes")
        content_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
        text = extract_text(bytes(body), content_type, final_url)
        normalized = normalize_text(text)
        return {
            "http_status": response.status_code,
            "final_url": final_url,
            "content_type": content_type,
            "bytes": len(body),
            "normalized_content_sha256": hashlib.sha256(
                normalized.encode("utf-8")
            ).hexdigest(),
            "text": normalized,
            "reviewable_text_bytes": len(normalized.encode("utf-8")),
        }
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
        value = review.get(group, [] if group != "corrected" else {})
        if group == "corrected":
            if not isinstance(value, dict):
                raise SystemExit("ERROR: corrected review decisions must be an object")
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
    failures: list[str] = []
    verified = 0
    for source in ledger.get("sources", []):
        if not isinstance(source, dict):
            failures.append("non-object source entry")
            continue
        verification = source.get("verification")
        if not isinstance(verification, dict):
            failures.append(f"{source.get('id', '<missing>')} missing verification record")
            continue
        reviewed_on = verification.get("reviewed_on")
        try:
            reviewed_day = date.fromisoformat(str(reviewed_on))
        except ValueError:
            failures.append(f"{source.get('id', '<missing>')} has invalid verification date")
            continue
        if reviewed_day > as_of:
            failures.append(f"{source.get('id', '<missing>')} has future verification date")
            continue
        verified += 1
    return {"status": "pass" if not failures else "fail", "verified": verified, "failures": failures}


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

    sources = ledger.get("sources")
    if not isinstance(sources, list):
        raise SystemExit("ERROR: source-ledger sources must be a list")
    review_candidates = [
        source
        for source in sources
        if isinstance(source, dict)
        and (
            str(source.get("refresh_due", "")) < as_of.isoformat()
            or not isinstance(source.get("verification"), dict)
        )
    ]
    candidate_ids = {str(source.get("id", "")) for source in review_candidates}
    source_by_id = {
        str(source.get("id", "")): source
        for source in sources
        if isinstance(source, dict)
    }
    permitted_prior = {
        source_id
        for source_id, source in source_by_id.items()
        if isinstance(source.get("verification"), dict)
        and source["verification"].get("reviewed_on") == as_of.isoformat()
    }
    missing = sorted(candidate_ids - set(decisions))
    extra = sorted(set(decisions) - candidate_ids - permitted_prior)
    if missing or extra:
        raise SystemExit(
            f"ERROR: review coverage mismatch; missing={missing[:8]} extra={extra[:8]}"
        )

    # Apply reviewed metadata corrections before fetching. This makes a corrected
    # canonical URL the actual source that is retrieved and hashed, rather than
    # recording evidence from the superseded URL.
    for source in review_candidates:
        source_id = str(source["id"])
        if decisions[source_id] == "corrected":
            apply_correction(source, corrections[source_id])

    urls = sorted({str(source["url"]) for source in review_candidates})
    fetched: dict[str, dict[str, Any]] = {}
    failures: list[dict[str, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_map = {executor.submit(fetch_source, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_map):
            url = future_map[future]
            try:
                fetched[url] = future.result()
            except Exception as exc:
                failures.append({"url": url, "error": f"{type(exc).__name__}: {exc}"})
    if failures:
        print(json.dumps({"status": "fail", "network_failures": failures}, indent=2))
        return 1

    results: list[dict[str, Any]] = []
    for source in review_candidates:
        source_id = str(source["id"])
        decision = decisions[source_id]
        correction = corrections.get(source_id, {})
        evidence = fetched[str(source["url"])]
        claim_check = claim_evidence(source, evidence["text"])
        if decision == "confirmed_by_content" and (
            claim_check["claim_token_coverage"] < MIN_CONTENT_COVERAGE
            or claim_check["missing_numeric_literals"]
        ):
            failures.append(
                {
                    "url": str(source["url"]),
                    "error": f"{source_id} no longer meets content-confirmation thresholds",
                }
            )
            continue
        if decision == "retired":
            source["status"] = "retired"
        source["retrieved"] = as_of.isoformat()
        source["last_verified"] = as_of.isoformat()
        source["refresh_due"] = next_refresh(source, as_of).isoformat()
        source["verification"] = {
            "reviewed_on": as_of.isoformat(),
            "decision": decision,
            "method": "public-source content check plus explicit claim review",
            "http_status": evidence["http_status"],
            "final_url": evidence["final_url"],
            "content_type": evidence["content_type"],
            "reviewable_text_bytes": evidence["reviewable_text_bytes"],
            "normalized_content_sha256": evidence["normalized_content_sha256"],
            **claim_check,
            "review_note": correction.get(
                "review_note",
                "Claim retained after source-content review.",
            ),
        }
        results.append(
            {
                "id": source_id,
                "decision": decision,
                **claim_check,
            }
        )

    if failures:
        print(json.dumps({"status": "fail", "review_failures": failures}, indent=2))
        return 1
    ledger["last_verified"] = as_of.isoformat()
    ledger["status"] = "market-ready-research" if len(results) == len(review_candidates) else ledger.get("status")
    if args.apply:
        LEDGER_PATH.write_text(
            json.dumps(ledger, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(
        json.dumps(
            {
                "status": "pass",
                "applied": args.apply,
                "reviewed": len(results),
                "unique_urls": len(urls),
                "decisions": {
                    group: sum(item["decision"] == group for item in results)
                    for group in sorted(DECISION_GROUPS)
                },
                "results": results,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
