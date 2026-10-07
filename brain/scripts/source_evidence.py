"""Shared source lifecycle and reviewed-evidence gates.

Availability and token overlap are retrieval diagnostics, never claim review.
Historical records remain in the ledger but cannot support current advice.
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import re
import stat
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse

ACTIVE_DECISIONS = {"confirmed_by_content", "confirmed_by_manual_review", "corrected", "qualified"}
LIFECYCLES = {"active", "retired", "unverified"}
SOURCE_TYPES = {"official", "primary", "vendor", "regulator", "government", "standards", "standards-body", "authority", "api-docs", "market", "practitioner", "supporting", "fixture", "local-skill-source", "repo-data"}


BRAIN_ROOT = Path(__file__).resolve().parents[1]
EXCERPT_SCHEMA = "claude-blog-brain.reviewed-excerpt.v1"
MAX_EXCERPT_ARTIFACT_BYTES = 64 * 1024


def normalize_excerpt(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def valid_digest(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{64}", value)) and value != "0" * 64


def read_excerpt_artifact(relative: Any) -> bytes:
    """Read only the packaged evidence lane, without following symlink components.

    Directory descriptors bind each lookup to the opened parent, including when
    a concurrent rename changes its pathname. There is no CWD or env override.
    """
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError("missing captured_excerpt_path")
    parts = PurePosixPath(relative).parts
    if (PurePosixPath(relative).is_absolute() or ".." in parts or "\\" in relative
            or ":" in relative or parts[:2] != ("references", "evidence") or len(parts) < 4
            or relative != PurePosixPath(relative).as_posix()):
        raise ValueError("unsafe captured_excerpt_path")
    if os.open not in os.supports_dir_fd or not all(hasattr(os, name) for name in ("O_DIRECTORY", "O_NOFOLLOW", "O_NONBLOCK")):
        raise ValueError("secure descriptor-relative nonsymlink excerpt reads are unavailable on this platform")
    descriptor = os.open(BRAIN_ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        leaf = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=descriptor)
        with os.fdopen(leaf, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError("captured excerpt must be a regular file")
            data = stream.read(MAX_EXCERPT_ARTIFACT_BYTES + 1)
        if len(data) > MAX_EXCERPT_ARTIFACT_BYTES:
            raise ValueError("captured excerpt artifact exceeds size limit")
        return data
    finally:
        os.close(descriptor)


def captured_excerpt_errors(source: dict[str, Any], verification: dict[str, Any]) -> list[str]:
    try:
        data = read_excerpt_artifact(verification.get("captured_excerpt_path"))
        digest = verification.get("captured_excerpt_sha256")
        if not valid_digest(digest) or hashlib.sha256(data).hexdigest() != digest:
            return ["captured excerpt artifact hash mismatch"]
        artifact = json.loads(data.decode("utf-8"))
        if not isinstance(artifact, dict) or artifact.get("schema") != EXCERPT_SCHEMA:
            return ["invalid captured excerpt artifact schema"]
        errors: list[str] = []
        if artifact.get("normalized_full_document_sha256") != verification.get("normalized_content_sha256"):
            errors.append("captured excerpt full-document provenance hash mismatch")
        if artifact.get("document_url") != str(verification.get("final_url", source.get("url", ""))).split("#", 1)[0]:
            errors.append("captured excerpt document URL mismatch")
        excerpts = artifact.get("excerpts")
        if not strings(excerpts) or len(set(excerpts)) != len(excerpts):
            return errors + ["invalid captured excerpt text list"]
        normalized = [normalize_excerpt(text) for text in excerpts]
        if any(not text for text in normalized) or len(set(normalized)) != len(normalized):
            errors.append("empty or duplicate normalized captured excerpt")
        if sum(len(text.split()) for text in normalized) > 25:
            errors.append("captured excerpts exceed aggregate 25-word document limit")
        records = artifact.get("records")
        if not isinstance(records, list) or not all(isinstance(record, dict) for record in records):
            return errors + ["invalid captured excerpt provenance records"]
        record_ids = [record.get("source_id") for record in records]
        if not all(isinstance(source_id, str) and source_id.strip() for source_id in record_ids):
            return errors + ["captured excerpt provenance source IDs must be nonempty strings"]
        if len(set(record_ids)) != len(record_ids):
            return errors + ["captured excerpt provenance source IDs must be unique"]
        indices = [record.get("excerpt_index") for record in records]
        if any(type(index) is not int or not 0 <= index < len(normalized) for index in indices):
            return errors + ["invalid captured excerpt provenance index"]
        if set(indices) != set(range(len(normalized))):
            errors.append("captured excerpt text lacks provenance index coverage")
        matching = [record for record in records if record.get("source_id") == source.get("id")]
        if len(matching) != 1:
            return errors + ["captured excerpt source provenance missing or duplicated"]
        record = matching[0]
        for key, expected in (("source_url", source.get("url")), ("retrieved_on", source.get("retrieved")), ("reviewed_on", verification.get("reviewed_on")), ("review_decision", verification.get("decision"))):
            if record.get(key) != expected:
                errors.append(f"captured excerpt {key} provenance mismatch")
        index = record.get("excerpt_index")
        if type(index) is not int or not 0 <= index < len(normalized):
            errors.append("invalid captured excerpt provenance index")
        elif normalize_excerpt(str(verification.get("evidence_excerpt", ""))) != normalized[index]:
            errors.append("captured excerpt differs from reviewed evidence_excerpt")
        return errors
    except (OSError, ValueError, TypeError, UnicodeError) as exc:
        return [f"captured excerpt artifact unavailable or invalid: {exc}"]


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
    if not valid_digest(digest):
        errors.append("missing valid normalized_content_sha256")
    for key in ("review_note", "evidence_excerpt", "evidence_path"):
        if not isinstance(verification.get(key), str) or not verification[key].strip():
            errors.append(f"missing {key}")
    artifact = verification.get("evidence_path", "")
    if isinstance(artifact, str) and artifact and (PurePosixPath(artifact).is_absolute() or ".." in PurePosixPath(artifact).parts or "\\" in artifact or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", artifact)):
        errors.append("unsafe evidence_path")
    errors.extend(captured_excerpt_errors(source, verification))
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


def captured_ledger_errors(index: dict[str, dict[str, Any]]) -> list[str]:
    """Bind artifacts referenced by active ledger sources and count their text.

    Coverage is the unique paths named by active records, not a directory scan.
    Unreferenced files and historical/retired paths are outside this gate. Every
    record and excerpt within a covered file must bind to the active ledger.
    Inline ledger excerpts cannot conceal additional text in those files.
    """
    paths = {
        source["verification"]["captured_excerpt_path"]
        for source in index.values()
        if lifecycle(source) == "active" and isinstance(source.get("verification"), dict)
        and isinstance(source["verification"].get("captured_excerpt_path"), str)
    }
    errors: list[str] = []
    document_excerpts: dict[str, set[str]] = {}
    for path in sorted(paths):
        try:
            data = read_excerpt_artifact(path)
            artifact_digest = hashlib.sha256(data).hexdigest()
            artifact = json.loads(data.decode("utf-8"))
            if not isinstance(artifact, dict) or artifact.get("schema") != EXCERPT_SCHEMA:
                raise ValueError("invalid captured excerpt artifact schema")
            excerpts, records = artifact.get("excerpts"), artifact.get("records")
            document = artifact.get("document_url")
            if (not strings(excerpts) or not isinstance(document, str) or not document.strip()
                    or not isinstance(records, list) or not all(isinstance(record, dict) for record in records)):
                raise ValueError("invalid captured excerpt text or provenance records")
            normalized = [normalize_excerpt(text) for text in excerpts]
            document_excerpts.setdefault(document.split("#", 1)[0], set()).update(normalized)
            bound_indices: set[int] = set()
            for record in records:
                source_id = record.get("source_id")
                source = index.get(source_id) if isinstance(source_id, str) else None
                if source is None or lifecycle(source) != "active":
                    errors.append(f"{path}: provenance source {source_id!r} is not a known active ledger source")
                    continue
                verification = source.get("verification")
                if not isinstance(verification, dict) or verification.get("captured_excerpt_path") != path:
                    errors.append(f"{path}: provenance source {source_id} is not bound to this artifact path")
                    continue
                if verification.get("captured_excerpt_sha256") != artifact_digest:
                    errors.append(f"{path}: {source_id}: captured excerpt artifact hash mismatch")
                    continue
                binding_errors = captured_excerpt_errors(source, verification)
                if binding_errors:
                    errors.extend(f"{path}: {source_id}: {error}" for error in binding_errors)
                    continue
                bound_indices.add(record["excerpt_index"])
            if bound_indices != set(range(len(normalized))):
                errors.append(f"{path}: captured excerpt text lacks matching active ledger provenance coverage")
        except (OSError, ValueError, TypeError, UnicodeError) as exc:
            errors.append(f"{path}: captured excerpt artifact unavailable or invalid: {exc}")
    for document, excerpts in document_excerpts.items():
        if sum(len(excerpt.split()) for excerpt in excerpts) > 25:
            errors.append(f"{document}: captured artifact text exceeds aggregate 25-word document limit")
    return errors


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
    errors.extend(captured_ledger_errors(index))
    return errors


def citation_errors(source_ids: list[str], index: dict[str, dict[str, Any]], *, as_of: date | None = None) -> list[str]:
    errors = captured_ledger_errors(index)
    for source_id in source_ids:
        if source_id not in index:
            errors.append(f"{source_id}: unknown source ID")
        elif lifecycle(index[source_id]) != "active":
            errors.append(f"{source_id}: {lifecycle(index[source_id])} evidence cannot support current recommendation")
        else:
            errors.extend(f"{source_id}: {error}" for error in source_errors(index[source_id], as_of=as_of))
    return errors
