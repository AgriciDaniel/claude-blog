#!/usr/bin/env python3
"""Audit Claude Blog Brain maturity, source integrity, and release gates."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


REPO = Path(__file__).resolve().parent.parent
RESEARCH_FILES = [
    "references/current-requirements.md",
    "references/market-research.md",
    "references/source-map.md",
    "references/safety-gates.md",
]
SOURCE_PACK_FILES = [
    "references/product-spec.md",
    "references/source-map.md",
    "references/current-requirements.md",
    "references/market-research.md",
    "references/safety-gates.md",
    "references/source-manifest-template.md",
    "references/research-plan.md",
    "references/adapter-plan.md",
    "references/source-ledger.json",
    "references/adapter-manifest.json",
]
PLACEHOLDER_PATTERNS = [
    re.compile(r"\bTBD\b", re.I),
    re.compile(r"research required", re.I),
    re.compile(r"release blocked", re.I),
    re.compile(r"add .* before release", re.I),
    re.compile(r"replace this example", re.I),
]
HIGH_STAKES_TERMS = {
    "accounting",
    "tax",
    "legal",
    "medical",
    "health",
    "finance",
    "financial",
    "compliance",
    "payroll",
    "security",
    "insurance",
    "investment",
}
FAST_MOVING_TERMS = {
    "ads",
    "advertising",
    "api",
    "platform",
    "social",
    "youtube",
    "tiktok",
    "meta",
    "google",
    "linkedin",
    "ai",
}
PRIMARY_SOURCE_TYPES = {
    "official",
    "primary",
    "vendor",
    "regulator",
    "government",
    "standards",
    "standards-body",
    "authority",
    "api-docs",
}
DISALLOWED_SOURCE_HOSTS = {
    "example.com",
    "www.example.com",
    "example.org",
    "www.example.org",
    "example.net",
    "www.example.net",
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
}
MATURITY_SCORE_CAP = {
    "scaffolded": 59,
    "researched": 74,
    "domain-adapted": 84,
    "demo-verified": 89,
    "market-ready": 100,
}
MATURITY_ORDER = ["scaffolded", "researched", "domain-adapted", "demo-verified", "market-ready"]
CONFIDENCE_VALUES = {"high", "medium", "low"}
EXEC_TIMEOUT_SECONDS = 180
SHINGLE_SIZE = 8
NEAR_DUPLICATE_THRESHOLD = 0.82
SKELETON_REUSE_THRESHOLD = 3
ANCHOR_REUSE_THRESHOLD = 2
TABLE_OR_PROCEDURE_THRESHOLD = 0.90
SPECIFIC_CITATION_THRESHOLD = 0.95
GENERIC_BUNDLE_REUSE_THRESHOLD = 3
GENERIC_BUNDLE_SOURCE_MIN = 6
DENSITY_WORD_THRESHOLD = 120
URL_RE = re.compile(r"https?://[^\s<>\]\"')]+")
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.S)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Claude Blog Brain maturity gates.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require", choices=MATURITY_ORDER)
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument("--verify", action="store_true", help="Run executable verification commands.")
    parser.add_argument("--no-exec", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    run_verification = (args.verify or args.require == "market-ready") and not args.no_exec
    result = audit_repo(run_verification=run_verification)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Status: {result['status']}")
        print(f"Score: {result['score']}")
        for failure in result["critical_failures"]:
            print(f"CRITICAL: {failure}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")

    if args.require and MATURITY_ORDER.index(result["status"]) < MATURITY_ORDER.index(args.require):
        print(f"ERROR: required maturity {args.require}, got {result['status']}", file=__import__("sys").stderr)
        return 1
    if args.require and result["critical_failures"]:
        print("ERROR: critical failures block required maturity", file=sys.stderr)
        return 1
    if args.report_only or not args.require:
        return 0
    return 0


def audit_repo(*, run_verification: bool = False) -> dict[str, Any]:
    categories: dict[str, dict[str, Any]] = {}
    critical: list[str] = []
    warnings: list[str] = []

    add_category(categories, "product_clarity", *check_product_clarity())
    maturity_ok, maturity_score, maturity_notes, maturity_critical = check_maturity_declarations()
    add_category(categories, "maturity_consistency", maturity_ok, maturity_score, maturity_notes)
    critical.extend(maturity_critical)
    add_category(categories, "source_pack", *check_source_pack())
    research_ok, research_score, research_notes, research_critical = check_research()
    add_category(categories, "current_research", research_ok, research_score, research_notes)
    critical.extend(research_critical)
    adapter_ok, adapter_score, adapter_notes, adapter_critical = check_adapters()
    add_category(categories, "domain_adapters", adapter_ok, adapter_score, adapter_notes)
    critical.extend(adapter_critical)
    citation_ok, citation_score, citation_notes, citation_critical = check_citations()
    add_category(categories, "source_citation", citation_ok, citation_score, citation_notes)
    critical.extend(citation_critical)
    wiki_ok, wiki_score, wiki_notes, wiki_critical, wiki_details = check_wiki_substance(REPO)
    add_category(categories, "wiki_substance", wiki_ok, wiki_score, wiki_notes, wiki_details)
    critical.extend(wiki_critical)
    add_category(categories, "demo_determinism", *check_demo_contract())
    add_category(categories, "tests", *check_tests_contract())
    verification_ok, verification_score, verification_notes, verification_critical = check_release_verification(run_verification=run_verification)
    add_category(categories, "release_verification", verification_ok, verification_score, verification_notes)
    critical.extend(verification_critical)
    add_category(categories, "packaging", *check_packaging())
    add_category(categories, "installability", *check_paths(["install.sh", "uninstall.sh", "pyproject.toml"]))
    add_category(categories, "docs", *check_paths(["README.md", "docs/OPERATOR_KIT.md", "docs/PRODUCT_BOUNDARIES.md", "RELEASE_CHECKLIST.md"]))
    add_category(categories, "obsidian_vault_quality", *check_paths(["assets/template-brain/CODEX.md", "assets/template-brain/.raw/.manifest.json", "assets/template-brain/wiki/hot.md", "assets/template-brain/wiki/index.md", "assets/template-brain/wiki/overview.md", "assets/template-brain/wiki/log.md", "assets/template-brain/wiki/meta/dashboard.md", "assets/template-brain/wiki/canvases/Onboarding Canvas.canvas"]))

    for name, category in categories.items():
        if not category["ok"]:
            warnings.append(f"{name}: " + "; ".join(category["notes"][:3]))

    raw_score = round(sum(category["score"] for category in categories.values()) / len(categories))
    status = determine_status(categories, raw_score, critical)
    score = min(raw_score, MATURITY_SCORE_CAP[status])
    return {
        "status": status,
        "score": score,
        "market_ready": status == "market-ready",
        "verification_executed": run_verification,
        "critical_failures": critical,
        "warnings": warnings,
        "categories": categories,
    }


def add_category(
    categories: dict[str, dict[str, Any]],
    name: str,
    ok: bool,
    score: int,
    notes: list[str],
    details: dict[str, Any] | None = None,
) -> None:
    category = {"ok": ok, "score": max(0, min(100, score)), "notes": notes}
    if details is not None:
        category["details"] = details
    categories[name] = category


def check_product_clarity() -> tuple[bool, int, list[str]]:
    text = (read(REPO / "README.md") + "\n" + read(REPO / "SKILL.md")).lower()
    required = ["buyer", "outputs", "boundaries", "quick start", "maturity"]
    notes = [f"missing {term} language" for term in required if term not in text]
    return not notes, 100 - 15 * len(notes), notes


def check_maturity_declarations() -> tuple[bool, int, list[str], list[str]]:
    docs = {
        "README.md": read(REPO / "README.md"),
        "docs/PRODUCT_BOUNDARIES.md": read(REPO / "docs" / "PRODUCT_BOUNDARIES.md"),
        "references/product-spec.md": read(REPO / "references" / "product-spec.md"),
        "references/adapter-plan.md": read(REPO / "references" / "adapter-plan.md"),
    }
    manifest, errors = load_json_object(REPO / "references" / "adapter-manifest.json")
    notes: list[str] = []
    critical: list[str] = []
    declared = {
        name: declared_maturity(text)
        for name, text in docs.items()
        if declared_maturity(text)
    }
    if manifest:
        status = clean_string(manifest.get("status"))
        if status:
            declared["references/adapter-manifest.json"] = status
    if errors:
        critical.extend(f"invalid adapter-manifest.json: {error}" for error in errors)
    if len(set(declared.values())) > 1:
        detail = ", ".join(f"{name}={value}" for name, value in sorted(declared.items()))
        critical.append("maturity declarations disagree: " + detail)
    if "not market-ready" in "\n".join(docs.values()).lower():
        notes.append("repository docs explicitly say the brain is not market-ready")
    product_spec = docs["references/product-spec.md"].lower()
    adapter_plan = docs["references/adapter-plan.md"].lower()
    if "code adapters are not built" in product_spec and manifest.get("generic_only") is False:
        critical.append("product-spec says code adapters are not built while adapter-manifest claims implemented domain adapters")
    if "generic_only` set to true" in adapter_plan and manifest.get("generic_only") is False:
        critical.append("adapter-plan says manifest should stay generic_only=true while adapter-manifest sets false")
    if "not market-ready" in "\n".join(docs.values()).lower() and manifest.get("status") == "market-ready":
        critical.append("manifest claims market-ready while docs say not market-ready")
    return not critical, max(0, 100 - 22 * len(critical) - 5 * len(notes)), notes, critical


def declared_maturity(text: str) -> str:
    lower = text.lower()
    patterns = [
        r"current maturity:\s*([a-z-]+)",
        r"status:\s*([a-z-]+)",
        r"starts as `([a-z-]+)`",
    ]
    for pattern in patterns:
        match = re.search(pattern, lower)
        if match and match.group(1) in MATURITY_ORDER:
            return match.group(1)
    return ""


def check_source_pack() -> tuple[bool, int, list[str]]:
    missing = [rel for rel in SOURCE_PACK_FILES if not (REPO / rel).exists()]
    return not missing, 100 - 12 * len(missing), [f"missing {rel}" for rel in missing]


def check_research() -> tuple[bool, int, list[str], list[str]]:
    notes: list[str] = []
    critical: list[str] = []
    score = 100
    context = read(REPO / "references" / "product-spec.md") + "\n" + read(REPO / "README.md")
    requires_fresh = contains_any(context, HIGH_STAKES_TERMS) or contains_any(context, FAST_MOVING_TERMS)

    for rel in RESEARCH_FILES:
        path = REPO / rel
        if not path.exists():
            notes.append(f"missing {rel}")
            critical.append(f"missing research file: {rel}")
            score -= 25
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(pattern.search(text) for pattern in PLACEHOLDER_PATTERNS):
            notes.append(f"placeholder research remains in {rel}")
            critical.append(f"placeholder research remains: {rel}")
            score -= 20
        if rel.endswith("current-requirements.md") and not re.search(r"\b20\d\d-\d\d-\d\d\b", text):
            notes.append(f"missing retrieval dates in {rel}")
            score -= 10

    ledger_ok, ledger_score, ledger_notes, ledger_critical = check_source_ledger(requires_fresh=requires_fresh)
    notes.extend(ledger_notes)
    critical.extend(ledger_critical)
    return not critical and ledger_ok, max(0, min(score, ledger_score)), notes, critical


def check_source_ledger(*, requires_fresh: bool) -> tuple[bool, int, list[str], list[str]]:
    path = REPO / "references" / "source-ledger.json"
    notes: list[str] = []
    critical: list[str] = []
    data, errors = load_json_object(path)
    if errors:
        critical.extend(f"invalid source-ledger.json: {error}" for error in errors)
        return False, 0, notes, critical
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        notes.append("source-ledger.json has no captured sources")
        critical.append("source-ledger has no captured official/primary sources")
        return False, 35, notes, critical

    official_count = 0
    invalid_confidence: dict[str, int] = {}
    legacy_date_count = 0
    month_only_dates: list[str] = []
    faq_ai_claims: list[str] = []
    redirected_faq_urls: list[str] = []
    llms_without_caveat: list[str] = []
    for index, source in enumerate(sources, start=1):
        label = f"source-ledger source #{index}"
        if not isinstance(source, dict):
            critical.append(f"{label} must be an object")
            continue
        source_id = clean_string(source.get("id")) or label
        source_type = clean_string(source.get("source_type")).lower()
        retrieved = parse_iso_date(clean_string(source.get("retrieved")))
        refresh_due = parse_iso_date(clean_string(source.get("refresh_due")))
        published = clean_string(source.get("published"))
        confidence = clean_string(source.get("confidence"))
        url = clean_string(source.get("url"))
        claims = source.get("claims")
        if not clean_string(source.get("title")):
            critical.append(f"{source_id} missing title")
        if not is_valid_source_url(url):
            critical.append(f"{source_id} has invalid or placeholder URL")
        if source_type in PRIMARY_SOURCE_TYPES:
            official_count += 1
        elif source_type not in {"market", "practitioner", "supporting", "fixture"}:
            critical.append(f"{source_id} has unsupported source_type")
        if retrieved is None:
            critical.append(f"{source_id} missing valid retrieved date")
        elif retrieved > date.today():
            critical.append(f"{source_id} has future retrieved date")
        claim_items = claims if isinstance(claims, list) else []
        if not claim_items or not any(clean_string(claim) for claim in claim_items):
            critical.append(f"{source_id} must list sourced claims")
        if confidence not in CONFIDENCE_VALUES:
            invalid_confidence[confidence or "<missing>"] = invalid_confidence.get(confidence or "<missing>", 0) + 1
        if "date" in source:
            legacy_date_count += 1
        if re.fullmatch(r"\d{4}-\d{2}", published) and clean_string(source.get("date_precision")) != "month":
            month_only_dates.append(source_id)
        claim_text = " ".join(clean_string(claim) for claim in claim_items)
        if "faq" in url.lower() and "developers.google.com/search/docs/appearance/structured-data/faqpage" in url:
            redirected_faq_urls.append(source_id)
        if re.search(r"faqpage.*ai|ai.*/?llm.*citation|ai-citation", claim_text, re.I):
            faq_ai_claims.append(source_id)
        if source_id.lower().startswith("llms") and "google" not in claim_text.lower():
            llms_without_caveat.append(source_id)
        if requires_fresh:
            if refresh_due is None:
                critical.append(f"{source_id} missing valid refresh_due date")
            elif refresh_due < date.today():
                critical.append(f"{source_id} refresh_due is stale")

    minimum_official = 2 if requires_fresh else 1
    if official_count < minimum_official:
        critical.append(f"source-ledger needs at least {minimum_official} official/primary sources")
    if invalid_confidence:
        detail = ", ".join(f"{value}={count}" for value, count in sorted(invalid_confidence.items()))
        critical.append("source-ledger confidence values must use one enum high|medium|low; found " + detail)
    if legacy_date_count:
        notes.append(f"source-ledger has {legacy_date_count} legacy date fields; split published, last_updated, retrieved, and date_precision")
    if month_only_dates:
        critical.append("source-ledger month-only published dates need date_precision=month: " + ", ".join(month_only_dates[:5]))
    if redirected_faq_urls:
        critical.append("FAQPage documentation URLs now redirect to Search updates: " + ", ".join(redirected_faq_urls[:5]))
    if faq_ai_claims:
        critical.append("FAQPage AI citation claims conflict with Google AI guidance: " + ", ".join(sorted(set(faq_ai_claims))[:5]))
    if llms_without_caveat:
        notes.append("llms.txt source entries need a Google Search caveat: " + ", ".join(llms_without_caveat[:5]))
    return not critical, max(0, 100 - 18 * len(critical) - 8 * len(notes)), notes, critical


def check_adapters() -> tuple[bool, int, list[str], list[str]]:
    notes: list[str] = []
    critical: list[str] = []
    data, errors = load_json_object(REPO / "references" / "adapter-manifest.json")
    if errors:
        critical.extend(f"invalid adapter-manifest.json: {error}" for error in errors)
        return False, 0, notes, critical
    if data.get("generic_only") is not False:
        notes.append("adapter-manifest declares generic_only=true")
        return False, 55, notes, critical

    required_sections = {
        "input_schemas": "input schema",
        "importers": "importer",
        "synthesis_modules": "synthesis module",
        "report_renderers": "report renderer",
        "fixtures": "fixture",
        "tests": "test",
    }
    for section, label in required_sections.items():
        entries = data.get(section)
        if not isinstance(entries, list) or not entries:
            critical.append(f"adapter-manifest missing {label} entries")
            continue
        for index, entry in enumerate(entries, start=1):
            entry_path = manifest_entry_path(entry)
            if not entry_path:
                critical.append(f"adapter-manifest {section} #{index} missing path")
            elif not (REPO / entry_path).exists():
                critical.append(f"adapter-manifest {section} path does not exist: {entry_path}")
    return not critical, max(0, 100 - 18 * len(critical) - 8 * len(notes)), notes, critical


def check_citations() -> tuple[bool, int, list[str], list[str]]:
    notes: list[str] = []
    critical: list[str] = []
    for folder in ["assets/template-brain/wiki/deliverables", "assets/template-brain/wiki/reports", "examples/sample-vault/wiki/deliverables", "examples/sample-vault/wiki/reports"]:
        root = REPO / folder
        if not root.exists():
            continue
        for path in root.rglob("*.md"):
            text = path.read_text(encoding="utf-8", errors="replace")
            if "[[" not in text and ".raw/" not in text and "sha256" not in text.lower():
                rel = path.relative_to(REPO).as_posix()
                notes.append(f"missing source citation in {rel}")
                critical.append(f"unsourced deliverable/report: {rel}")
    return not critical, max(0, 100 - 15 * len(critical)), notes, critical


def check_wiki_substance(repo_root: Path = REPO) -> tuple[bool, int, list[str], list[str], dict[str, Any]]:
    """Audit whether spoke notes have real, note-specific wiki substance.

    A note citation set is the sorted set of ledger source_ids cited anywhere in
    the note, including frontmatter and body text. Topical reuse of a compact
    authoritative source set is allowed: a 2 to 5 source set can be correct
    scholarship for a folder, such as several schema notes citing the same
    canonical structured-data specs. The boilerplate defect is an oversized
    pasted bundle. generic_bundle_reuse therefore measures the largest group of
    notes sharing an identical citation set whose size is at least 6. The
    specific citation coverage numerator counts spoke notes whose citation set
    has at least two sources and whose exact set is not an oversized bundle
    reused by more than the generic bundle threshold. If a canonical URL maps
    to multiple ledger IDs, a URL citation contributes one representative unless
    the note already cites one of those IDs explicitly.
    """
    wiki_root = repo_root / "wiki"
    notes: list[str] = []
    critical: list[str] = []
    if not wiki_root.exists():
        details = empty_wiki_substance_details()
        notes.append("missing wiki directory")
        return False, 0, notes, critical, details

    source_ids, url_to_source_ids = load_source_index(repo_root)
    source_id_pattern = compile_source_id_pattern(source_ids)
    spoke_notes = load_spoke_notes(repo_root, wiki_root, source_id_pattern, url_to_source_ids)
    if not spoke_notes:
        details = empty_wiki_substance_details()
        notes.append("no type: spoke notes found in wiki")
        return False, 0, notes, critical, details

    near_pairs = find_near_duplicate_pairs(spoke_notes)
    skeleton = largest_reuse_group(spoke_notes, "skeleton")
    anchor = largest_anchor_reuse(spoke_notes)
    table_or_procedure_failures = [
        note["rel_path"] for note in spoke_notes if not note["has_table_or_procedure"]
    ]

    citation_set_counts: Counter[frozenset[str]] = Counter(
        note["citation_set"] for note in spoke_notes
    )
    bundle_counts: Counter[frozenset[str]] = Counter(
        note["citation_set"]
        for note in spoke_notes
        if len(note["citation_set"]) >= GENERIC_BUNDLE_SOURCE_MIN
    )
    generic_bundle, generic_bundle_count = largest_bundle(bundle_counts)
    identically_reused_sets = {
        citation_set
        for citation_set, count in citation_set_counts.items()
        if (
            len(citation_set) >= GENERIC_BUNDLE_SOURCE_MIN
            and count > GENERIC_BUNDLE_REUSE_THRESHOLD
        )
    }
    citation_failures = [
        note["rel_path"]
        for note in spoke_notes
        if len(note["citation_set"]) < 2 or note["citation_set"] in identically_reused_sets
    ]

    shared_lines = shared_body_lines(spoke_notes)
    density_failures = []
    density_values: dict[str, int] = {}
    for note in spoke_notes:
        count = note_specific_word_count(note["body_lines"], shared_lines)
        density_values[note["rel_path"]] = count
        if count < DENSITY_WORD_THRESHOLD:
            density_failures.append({"path": note["rel_path"], "note_specific_words": count})

    table_or_procedure_coverage = 1.0 - (len(table_or_procedure_failures) / len(spoke_notes))
    specific_citation_coverage = 1.0 - (len(citation_failures) / len(spoke_notes))
    density_floor = min(density_values.values()) if density_values else 0
    max_skeleton_reuse = skeleton["count"] if skeleton else 0
    max_anchor_reuse = anchor["count"] if anchor else 0

    metrics = {
        "spoke_count": len(spoke_notes),
        "near_duplicate_pairs": len(near_pairs),
        "max_skeleton_reuse": max_skeleton_reuse,
        "max_anchor_reuse": max_anchor_reuse,
        "table_or_procedure_coverage": round(table_or_procedure_coverage, 4),
        "specific_citation_coverage": round(specific_citation_coverage, 4),
        "generic_bundle_reuse": generic_bundle_count,
        "density_floor": density_floor,
        "density_floor_below_count": len(density_failures),
    }
    offenders = {
        "near_duplicate_pairs": near_pairs,
        "max_skeleton_reuse": skeleton if max_skeleton_reuse > SKELETON_REUSE_THRESHOLD else {},
        "max_anchor_reuse": anchor if max_anchor_reuse > ANCHOR_REUSE_THRESHOLD else {},
        "table_or_procedure_coverage": table_or_procedure_failures,
        "specific_citation_coverage": citation_failures,
        "generic_bundle_reuse": {
            "count": generic_bundle_count,
            "source_ids": sorted(generic_bundle),
            "paths": [
                note["rel_path"] for note in spoke_notes if note["citation_set"] == generic_bundle
            ] if generic_bundle_count > GENERIC_BUNDLE_REUSE_THRESHOLD else [],
        },
        "density_floor": density_failures,
    }
    details = {"metrics": metrics, "offenders": offenders}

    if near_pairs:
        first = near_pairs[0]["paths"]
        critical.append(f"wiki_substance near_duplicate_pairs={len(near_pairs)}: {first[0]} <-> {first[1]}")
        notes.append(f"near duplicate spoke pairs: {len(near_pairs)}")
    if max_skeleton_reuse > SKELETON_REUSE_THRESHOLD:
        notes.append(f"H2/H3 skeleton reused by {max_skeleton_reuse} spoke notes")
    if max_anchor_reuse > ANCHOR_REUSE_THRESHOLD:
        notes.append(f"anchor line reused by {max_anchor_reuse} spoke notes")
    if table_or_procedure_coverage < TABLE_OR_PROCEDURE_THRESHOLD:
        notes.append(f"table/procedure coverage {table_or_procedure_coverage:.2f} below 0.90")
    if specific_citation_coverage < SPECIFIC_CITATION_THRESHOLD:
        notes.append(f"specific citation coverage {specific_citation_coverage:.2f} below {SPECIFIC_CITATION_THRESHOLD:.2f}")
    if generic_bundle_count > GENERIC_BUNDLE_REUSE_THRESHOLD:
        notes.append(f"generic source bundle reused by {generic_bundle_count} spoke notes")
    if density_failures:
        notes.append(f"{len(density_failures)} spoke notes below {DENSITY_WORD_THRESHOLD} note-specific words")

    ok = (
        len(near_pairs) == 0
        and max_skeleton_reuse <= SKELETON_REUSE_THRESHOLD
        and max_anchor_reuse <= ANCHOR_REUSE_THRESHOLD
        and table_or_procedure_coverage >= TABLE_OR_PROCEDURE_THRESHOLD
        and specific_citation_coverage >= SPECIFIC_CITATION_THRESHOLD
        and generic_bundle_count <= GENERIC_BUNDLE_REUSE_THRESHOLD
        and not density_failures
    )
    return ok, score_wiki_substance(metrics, len(spoke_notes)), notes, critical, details


def empty_wiki_substance_details() -> dict[str, Any]:
    return {
        "metrics": {
            "spoke_count": 0,
            "near_duplicate_pairs": 0,
            "max_skeleton_reuse": 0,
            "max_anchor_reuse": 0,
            "table_or_procedure_coverage": 0.0,
            "specific_citation_coverage": 0.0,
            "generic_bundle_reuse": 0,
            "density_floor": 0,
            "density_floor_below_count": 0,
        },
        "offenders": {
            "near_duplicate_pairs": [],
            "max_skeleton_reuse": {},
            "max_anchor_reuse": {},
            "table_or_procedure_coverage": [],
            "specific_citation_coverage": [],
            "generic_bundle_reuse": {"count": 0, "source_ids": [], "paths": []},
            "density_floor": [],
        },
    }


def load_source_index(repo_root: Path) -> tuple[set[str], dict[str, tuple[str, ...]]]:
    data, _errors = load_json_object(repo_root / "references" / "source-ledger.json")
    source_ids: set[str] = set()
    url_to_source_ids: dict[str, list[str]] = defaultdict(list)
    sources = data.get("sources") if isinstance(data, dict) else None
    if not isinstance(sources, list):
        return source_ids, {}
    for source in sources:
        if not isinstance(source, dict):
            continue
        source_id = clean_string(source.get("id")) or clean_string(source.get("source_id"))
        if not source_id:
            continue
        source_ids.add(source_id)
        url = canonical_source_url(clean_string(source.get("url")))
        if url and source_id not in url_to_source_ids[url]:
            url_to_source_ids[url].append(source_id)
    return source_ids, {url: tuple(ids) for url, ids in url_to_source_ids.items()}


def compile_source_id_pattern(source_ids: set[str]) -> re.Pattern[str] | None:
    if not source_ids:
        return None
    alternatives = "|".join(re.escape(source_id) for source_id in sorted(source_ids, key=len, reverse=True))
    return re.compile(r"(?<![A-Za-z0-9_-])(" + alternatives + r")(?![A-Za-z0-9_-])")


def load_spoke_notes(
    repo_root: Path,
    wiki_root: Path,
    source_id_pattern: re.Pattern[str] | None,
    url_to_source_ids: dict[str, tuple[str, ...]],
) -> list[dict[str, Any]]:
    spoke_notes: list[dict[str, Any]] = []
    for path in sorted(wiki_root.rglob("*.md")):
        if path.name == "_index.md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        frontmatter, body = split_frontmatter(text)
        if frontmatter_type(frontmatter) != "spoke":
            continue
        body_lines = [collapse_whitespace(line) for line in body.splitlines()]
        normalized = normalize_body(body)
        tokens = normalized.split()
        citation_set = frozenset(extract_source_ids(text, source_id_pattern, url_to_source_ids))
        spoke_notes.append(
            {
                "path": path,
                "rel_path": display_path(path, repo_root),
                "body": body,
                "body_lines": body_lines,
                "normalized_body": normalized,
                "tokens": tokens,
                "shingles": make_shingles(tokens),
                "skeleton": heading_skeleton(body),
                "has_table_or_procedure": has_table_or_procedure(body),
                "citation_set": citation_set,
            }
        )
    return spoke_notes


def split_frontmatter(text: str) -> tuple[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return "", text
    return match.group(1), text[match.end():]


def frontmatter_type(frontmatter: str) -> str:
    match = re.search(r"(?m)^type:\s*[\"']?([^\"'\n#]+)[\"']?", frontmatter)
    return match.group(1).strip().lower() if match else ""


def normalize_body(body: str) -> str:
    return collapse_whitespace(body.lower())


def collapse_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def make_shingles(tokens: list[str], size: int = SHINGLE_SIZE) -> frozenset[int]:
    if not tokens:
        return frozenset()
    if len(tokens) < size:
        return frozenset({stable_shingle_hash(tokens)})
    return frozenset(stable_shingle_hash(tokens[index:index + size]) for index in range(len(tokens) - size + 1))


def stable_shingle_hash(tokens: list[str]) -> int:
    digest = hashlib.blake2b(" ".join(tokens).encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big")


def heading_skeleton(body: str) -> tuple[str, ...]:
    headings = []
    for line in body.splitlines():
        match = re.match(r"^\s{0,3}(#{2,3})\s+(.+?)\s*$", line)
        if match:
            headings.append(match.group(1) + " " + collapse_whitespace(match.group(2)).lower())
    return tuple(headings)


def has_table_or_procedure(body: str) -> bool:
    lines = body.splitlines()
    for index, line in enumerate(lines[:-1]):
        if "|" in line and re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", lines[index + 1]):
            return True
    step_count = 0
    for line in lines:
        if re.match(r"^\s*(?:\d+[\.)]|step\s+\d+\b)\s+", line, re.I):
            step_count += 1
            if step_count >= 3:
                return True
    return False


def extract_source_ids(
    text: str,
    source_id_pattern: re.Pattern[str] | None,
    url_to_source_ids: dict[str, tuple[str, ...]],
) -> set[str]:
    found: set[str] = set()
    if source_id_pattern:
        found.update(source_id_pattern.findall(text))
    for match in URL_RE.finditer(text):
        source_ids = url_to_source_ids.get(canonical_source_url(match.group(0)))
        if not source_ids:
            continue
        if any(source_id in found for source_id in source_ids):
            continue
        found.add(source_ids[0])
    return found


def canonical_source_url(value: str) -> str:
    if not value:
        return ""
    cleaned = value.strip().strip("<>\"'").rstrip(".,;:")
    parsed = urlparse(cleaned)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    parsed = parsed._replace(netloc=parsed.netloc.lower(), fragment="")
    return parsed.geturl().rstrip("/")


def find_near_duplicate_pairs(spoke_notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    inverted: dict[int, list[int]] = defaultdict(list)
    for index, note in enumerate(spoke_notes):
        for shingle in note["shingles"]:
            inverted[shingle].append(index)

    intersections: Counter[tuple[int, int]] = Counter()
    for indexes in inverted.values():
        if len(indexes) < 2:
            continue
        for left_pos, left in enumerate(indexes):
            for right in indexes[left_pos + 1:]:
                intersections[(left, right)] += 1

    pairs = []
    for (left, right), intersection in intersections.items():
        left_shingles = spoke_notes[left]["shingles"]
        right_shingles = spoke_notes[right]["shingles"]
        union = len(left_shingles) + len(right_shingles) - intersection
        similarity = 1.0 if union == 0 else intersection / union
        if similarity >= NEAR_DUPLICATE_THRESHOLD:
            pairs.append(
                {
                    "paths": [spoke_notes[left]["rel_path"], spoke_notes[right]["rel_path"]],
                    "similarity": round(similarity, 4),
                }
            )
    return sorted(pairs, key=lambda item: (-item["similarity"], item["paths"]))


def largest_reuse_group(spoke_notes: list[dict[str, Any]], key: str) -> dict[str, Any]:
    groups: dict[Any, list[str]] = defaultdict(list)
    for note in spoke_notes:
        groups[note[key]].append(note["rel_path"])
    candidates = list(groups.items())
    if not candidates:
        return {}
    value, paths = max(candidates, key=lambda item: (len(item[1]), sorted(item[1])[0]))
    return {"count": len(paths), "value": list(value), "paths": sorted(paths)}


def largest_anchor_reuse(spoke_notes: list[dict[str, Any]]) -> dict[str, Any]:
    anchors: dict[str, list[str]] = defaultdict(list)
    for note in spoke_notes:
        seen_in_note = set()
        for line in note["body_lines"]:
            if line and len(WORD_RE.findall(line)) >= 12:
                seen_in_note.add(line)
        for line in seen_in_note:
            anchors[line].append(note["rel_path"])
    candidates = list(anchors.items())
    if not candidates:
        return {}
    line, paths = max(candidates, key=lambda item: (len(item[1]), item[0]))
    return {"count": len(paths), "line": line, "paths": sorted(paths)}


def largest_bundle(bundle_counts: Counter[frozenset[str]]) -> tuple[frozenset[str], int]:
    if not bundle_counts:
        return frozenset(), 0
    bundle, count = max(bundle_counts.items(), key=lambda item: (item[1], len(item[0]), sorted(item[0])))
    return bundle, count


def shared_body_lines(spoke_notes: list[dict[str, Any]]) -> set[str]:
    counts: Counter[str] = Counter()
    for note in spoke_notes:
        counts.update({line for line in note["body_lines"] if line})
    return {line for line, count in counts.items() if count > 1}


def note_specific_word_count(body_lines: list[str], shared_lines: set[str]) -> int:
    specific_lines = [line for line in body_lines if line and line not in shared_lines]
    return len(WORD_RE.findall("\n".join(specific_lines)))


def score_wiki_substance(metrics: dict[str, Any], spoke_count: int) -> int:
    if spoke_count <= 0:
        return 0
    score = 100.0
    if metrics["max_skeleton_reuse"] > SKELETON_REUSE_THRESHOLD:
        overage = metrics["max_skeleton_reuse"] - SKELETON_REUSE_THRESHOLD
        score -= 10.0 * min(1.0, overage / max(1, spoke_count - SKELETON_REUSE_THRESHOLD))
    if metrics["max_anchor_reuse"] > ANCHOR_REUSE_THRESHOLD:
        overage = metrics["max_anchor_reuse"] - ANCHOR_REUSE_THRESHOLD
        score -= 10.0 * min(1.0, overage / max(1, spoke_count - ANCHOR_REUSE_THRESHOLD))
    if metrics["generic_bundle_reuse"] > GENERIC_BUNDLE_REUSE_THRESHOLD:
        overage = metrics["generic_bundle_reuse"] - GENERIC_BUNDLE_REUSE_THRESHOLD
        score -= 10.0 * min(1.0, overage / max(1, spoke_count - GENERIC_BUNDLE_REUSE_THRESHOLD))
    if metrics["table_or_procedure_coverage"] < TABLE_OR_PROCEDURE_THRESHOLD:
        shortfall = TABLE_OR_PROCEDURE_THRESHOLD - metrics["table_or_procedure_coverage"]
        score -= 15.0 * min(1.0, shortfall / TABLE_OR_PROCEDURE_THRESHOLD)
    if metrics["specific_citation_coverage"] < SPECIFIC_CITATION_THRESHOLD:
        shortfall = SPECIFIC_CITATION_THRESHOLD - metrics["specific_citation_coverage"]
        score -= 20.0 * min(1.0, shortfall / SPECIFIC_CITATION_THRESHOLD)
    if metrics["density_floor_below_count"]:
        score -= 15.0 * min(1.0, metrics["density_floor_below_count"] / spoke_count)
    if metrics["near_duplicate_pairs"] > 0:
        score = min(score, 40.0)
    return round(max(0.0, min(100.0, score)))


def check_demo_contract() -> tuple[bool, int, list[str]]:
    required = ["examples/sample-vault/CODEX.md", "examples/sample-vault/.raw/.manifest.json", "examples/sample-vault/wiki/hot.md", "examples/sample-vault/wiki/reports/Weekly Report.md"]
    ok, score, notes = check_paths(required)
    script = read(REPO / "scripts" / "build_demo_vault.py")
    for term in ["--force", "TemporaryDirectory", "clean target", "--json"]:
        if term not in script:
            notes.append(f"build_demo_vault.py missing {term} safeguard")
            score -= 15
    return ok and not notes, max(0, score), notes


def check_tests_contract() -> tuple[bool, int, list[str]]:
    required = ["tests/test_pipeline.py", "tests/test_blog_adapters.py", ".github/workflows/ci.yml"]
    ok, score, notes = check_paths(required)
    adapter_tests = read(REPO / "tests" / "test_blog_adapters.py")
    pipeline_tests = read(REPO / "tests" / "test_pipeline.py")
    for term in ["subprocess", "ingest_blog_input.py", "synthesize_blog_plan.py", "render_blog_report.py"]:
        if term not in adapter_tests:
            notes.append(f"adapter tests do not exercise {term}")
            score -= 12
    for term in ["TemporaryDirectory", "--skip-release"]:
        if term not in pipeline_tests:
            notes.append(f"pipeline test missing isolated {term} support")
            score -= 12
    return ok and not notes, max(0, score), notes


def check_release_verification(*, run_verification: bool) -> tuple[bool, int, list[str], list[str]]:
    if not run_verification:
        return False, 55, ["executable release verification not run; use --verify or --require market-ready"], []
    notes: list[str] = []
    critical: list[str] = []
    commands: list[tuple[str, list[str]]] = [
        ("compileall", [sys.executable, "-m", "compileall", "scripts", "claude_blog_brain", "tests"]),
        ("adapter tests", [sys.executable, "-m", "pytest", "tests/test_blog_adapters.py"]),
        ("pipeline", [sys.executable, "tests/test_pipeline.py", "--skip-release"]),
        ("audit self-check", [sys.executable, "scripts/audit_brain.py", "--json", "--report-only", "--no-exec"]),
    ]
    with tempfile.TemporaryDirectory(prefix="claude-blog-brain-release-") as tmp:
        commands.append(
            (
                "package release",
                [
                    sys.executable,
                    "scripts/package_release.py",
                    "--version",
                    "0.2.0",
                    "--dist-dir",
                    tmp,
                    "--allow-outside-dist",
                ],
            )
        )
        for label, command in commands:
            proc = run_command(command)
            if proc.returncode:
                detail = first_nonempty_line(proc.stderr) or first_nonempty_line(proc.stdout) or f"exit {proc.returncode}"
                critical.append(f"verification command failed ({label}): {detail}")
            else:
                notes.append(f"verification command passed: {label}")
    return not critical, max(0, 100 - 22 * len(critical)), notes, critical


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=REPO,
            text=True,
            capture_output=True,
            timeout=EXEC_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(command, 124, exc.stdout or "", exc.stderr or "command timed out")


def first_nonempty_line(value: str | None) -> str:
    for line in (value or "").splitlines():
        if line.strip():
            return line.strip()
    return ""


def check_packaging() -> tuple[bool, int, list[str]]:
    path = REPO / "scripts" / "package_release.py"
    if not path.exists():
        return False, 0, ["missing scripts/package_release.py"]
    text = path.read_text(encoding="utf-8", errors="replace")
    notes = [f"package script missing {term}" for term in ["SHA256SUMS", "RELEASE_MANIFEST", "release-type", "market-ready", "audit_brain.py"] if term not in text]
    return not notes, 100 - 20 * len(notes), notes


def check_paths(paths: list[str]) -> tuple[bool, int, list[str]]:
    missing = [rel for rel in paths if not (REPO / rel).exists()]
    return not missing, 100 - 12 * len(missing), [f"missing {rel}" for rel in missing]


def determine_status(categories: dict[str, dict[str, Any]], score: int, critical: list[str]) -> str:
    if not categories["maturity_consistency"]["ok"]:
        return "scaffolded"
    if not categories["current_research"]["ok"]:
        return "scaffolded"
    if not categories["domain_adapters"]["ok"]:
        return "researched"
    if not categories["demo_determinism"]["ok"] or not categories["tests"]["ok"]:
        return "domain-adapted"
    if critical or score < 90 or any(not categories[name]["ok"] for name in ["packaging", "installability", "docs", "source_citation", "wiki_substance", "obsidian_vault_quality", "release_verification"]):
        return "demo-verified"
    return "market-ready"


def load_json_object(path: Path) -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        return {}, [f"missing {display_path(path, REPO)}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return {}, [str(exc)]
    if not isinstance(data, dict):
        return {}, ["top-level value must be an object"]
    return data, []


def display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def contains_any(text: str, terms: set[str]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def clean_string(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def parse_iso_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def is_valid_source_url(value: str) -> bool:
    parsed = urlparse(value)
    host = parsed.netloc.lower()
    return parsed.scheme in {"http", "https"} and bool(host) and host not in DISALLOWED_SOURCE_HOSTS and "TBD" not in value.upper()


def manifest_entry_path(entry: object) -> str:
    if isinstance(entry, str):
        return entry
    if not isinstance(entry, dict):
        return ""
    for key in ["path", "schema_path", "module", "fixture", "test"]:
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


if __name__ == "__main__":
    raise SystemExit(main())
