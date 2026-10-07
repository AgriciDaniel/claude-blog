"""Shared source lifecycle and reviewed-evidence gates.

Availability and token overlap are retrieval diagnostics, never claim review.
Historical records remain in the ledger but cannot support current advice.
"""
from __future__ import annotations

import ipaddress
import re
from datetime import date
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import urlparse

ACTIVE_DECISIONS = {"confirmed_by_content", "confirmed_by_manual_review", "corrected", "qualified"}
LIFECYCLES = {"active", "retired", "unverified"}
SOURCE_TYPES = {"official", "primary", "vendor", "regulator", "government", "standards", "standards-body", "authority", "api-docs", "market", "practitioner", "supporting", "fixture", "local-skill-source", "repo-data"}


def day(value: Any) -> date | None:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def strings(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(v, str) and v.strip() for v in value)


def lifecycle(source: dict[str, Any]) -> str:
    # Older records omitted status. Only the absence maps to active, never an
    # unknown or blank state, and the full evidence gate still applies.
    return source.get("status", "active")


def source_errors(source: dict[str, Any], *, as_of: date | None = None) -> list[str]:
    as_of = as_of or date.today()
    errors: list[str] = []
    state = lifecycle(source)
    if not isinstance(state, str) or state not in LIFECYCLES:
        return ["unsupported lifecycle status"]
    if state == "retired":
        if not isinstance(source.get("retirement_reason"), str) or not source["retirement_reason"].strip():
            errors.append("retired source missing retirement_reason")
        if not strings(source.get("replacement_source_ids")):
            errors.append("retired source missing replacement_source_ids")
        retired_on = day(source.get("retired_on"))
        if retired_on is None or retired_on > as_of:
            errors.append("retired source missing valid nonfuture retired_on")
        return errors
    if state == "unverified":
        reason = source.get("unverified_reason") or source.get("limitations")
        if not reason:
            errors.append("unverified source missing reason or limitations")
        return errors
    verification = source.get("verification")
    if not isinstance(verification, dict):
        return ["missing verification record"]
    decision = verification.get("decision")
    if not isinstance(decision, str) or decision not in ACTIVE_DECISIONS:
        errors.append("active source missing supported review decision")
    reviewed = day(verification.get("reviewed_on"))
    retrieved = day(source.get("retrieved"))
    refresh = day(source.get("refresh_due"))
    for label, value in (("reviewed_on", reviewed), ("retrieved", retrieved)):
        if value is None or value > as_of:
            errors.append(f"missing valid nonfuture {label} date")
    if reviewed and retrieved and reviewed < retrieved:
        errors.append("reviewed_on predates retrieval")
    if refresh is None or refresh < as_of:
        errors.append("refresh_due missing or stale")
    if refresh and reviewed and refresh < reviewed:
        errors.append("refresh_due predates review")
    verified = source.get("last_verified")
    if verified is not None and day(verified) != reviewed:
        errors.append("last_verified differs from reviewed_on")
    for key in ("published", "last_updated"):
        value = source.get(key)
        if value:
            precision = source.get("date_precision", "day")
            expanded = str(value) + ("-01-01" if precision == "year" and len(str(value)) == 4 else "-01" if precision == "month" and len(str(value)) == 7 else "")
            dated = day(expanded)
            if dated is None or dated > as_of or (retrieved and dated > retrieved):
                errors.append(f"invalid or unsupported {key} date")
    digest = verification.get("normalized_content_sha256", "")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        errors.append("missing valid normalized_content_sha256")
    for key in ("review_note", "evidence_excerpt", "evidence_path"):
        if not isinstance(verification.get(key), str) or not verification[key].strip():
            errors.append(f"missing {key}")
    artifact = verification.get("evidence_path", "")
    if isinstance(artifact, str) and artifact and (PurePosixPath(artifact).is_absolute() or ".." in PurePosixPath(artifact).parts or "\\" in artifact or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", artifact)):
        errors.append("unsafe evidence_path")
    claims = source.get("claims")
    supported = source.get("supports_claims")
    if not strings(claims) or not strings(supported) or not set(claims).issubset(set(supported)):
        errors.append("active claims missing reviewed supports_claims coverage")
    if decision == "qualified" and not source.get("limitations"):
        errors.append("qualified source missing explicit limitations")
    if source.get("confidence") not in ("high", "medium", "low"):
        errors.append("invalid confidence enum")
    if source.get("source_type") not in tuple(SOURCE_TYPES):
        errors.append("unsupported source_type")
    if not isinstance(source.get("title"), str) or not source["title"].strip():
        errors.append("missing title")
    try:
        url = urlparse(str(source.get("url", "")))
    except ValueError:
        errors.append("invalid public source URL")
        return errors
    if url.scheme not in {"https", "http"} or not url.hostname or url.username or url.password:
        errors.append("invalid public source URL")
    elif url.hostname.lower() in {"example.com", "example.org", "example.net", "localhost"} or url.hostname.lower().endswith((".example.com", ".example.org", ".example.net", ".localhost", ".local", ".onion")):
        errors.append("placeholder or nonpublic source URL")
    else:
        try:
            if not ipaddress.ip_address(url.hostname).is_global:
                errors.append("nonpublic source URL")
        except ValueError:
            pass
    return errors


def can_support(source: dict[str, Any], *, as_of: date | None = None) -> bool:
    return lifecycle(source) == "active" and not source_errors(source, as_of=as_of)


def ledger_index(ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sources = ledger.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("source ledger sources must be a nonempty list")
    index: dict[str, dict[str, Any]] = {}
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get("id"), str) or not source["id"].strip():
            raise ValueError("source ledger entry missing ID or object")
        source_id = source["id"]
        if source_id in index:
            raise ValueError(f"duplicate source ID: {source_id}")
        index[source_id] = source
    return index


def ledger_errors(ledger: dict[str, Any], *, as_of: date | None = None) -> list[str]:
    try:
        index = ledger_index(ledger)
    except ValueError as exc:
        return [str(exc)]
    errors: list[str] = []
    for source_id, source in index.items():
        errors.extend(f"{source_id}: {error}" for error in source_errors(source, as_of=as_of))
        if lifecycle(source) == "retired" and strings(source.get("replacement_source_ids")):
            for replacement in source.get("replacement_source_ids", []):
                if replacement == source_id or replacement not in index or not can_support(index[replacement], as_of=as_of):
                    errors.append(f"{source_id}: replacement {replacement} lacks active reviewed evidence")
    return errors


def citation_errors(source_ids: list[str], index: dict[str, dict[str, Any]], *, as_of: date | None = None) -> list[str]:
    errors: list[str] = []
    for source_id in source_ids:
        if source_id not in index:
            errors.append(f"{source_id}: unknown source ID")
        elif lifecycle(index[source_id]) != "active":
            errors.append(f"{source_id}: {lifecycle(index[source_id])} evidence cannot support current recommendation")
        else:
            errors.extend(f"{source_id}: {error}" for error in source_errors(index[source_id], as_of=as_of))
    return errors
