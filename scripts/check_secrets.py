#!/usr/bin/env python3
"""Fail on unadjudicated detect-secrets findings without exposing values."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SHA_FIELD_RE = re.compile(
    r'"(?:sha256|raw_snapshot_sha256|content_sha256|normalized_content_sha256)"\s*:\s*"[0-9a-f]{64}"',
    re.IGNORECASE,
)
ACTION_PIN_RE = re.compile(r"uses:\s*[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}\b")
ACTION_EXPECTATION_RE = re.compile(
    r'"actions/(?:checkout|setup-node|setup-python)"\s*:\s*"[0-9a-f]{40}"'
)
PLACEHOLDER_MARKERS = (
    "YOUR_",
    "your-",
    "/path/to/",
    '"..."',
    "AIzaSy...",
)
FORBIDDEN_VALUE_PATTERNS = {
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "OpenAI key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "Anthropic key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
    "GitHub token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit a JSON result envelope.")
    return parser.parse_args(argv)


def run_detect_secrets() -> dict[str, object]:
    command = [
        "detect-secrets",
        "scan",
        "--all-files",
        "--exclude-files",
        r"^outputs/",
        "--exclude-files",
        r"^\.git/",
        "--exclude-files",
        r"^\.pytest_cache/",
    ]
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise SystemExit("ERROR: detect-secrets is not installed") from exc
    if result.returncode:
        raise SystemExit("ERROR: detect-secrets scan failed without a usable report")
    try:
        payload = json.loads(result.stdout)
    except ValueError as exc:
        raise SystemExit("ERROR: detect-secrets returned invalid JSON") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), dict):
        raise SystemExit("ERROR: detect-secrets report has an unexpected shape")
    return payload


def line_for(path: Path, number: int) -> str:
    if number < 1:
        return ""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    return lines[number - 1] if number <= len(lines) else ""


def is_adjudicated(path: str, finding: dict[str, object], line: str) -> bool:
    finding_type = str(finding.get("type", ""))
    if finding_type == "Hex High Entropy String":
        return bool(
            SHA_FIELD_RE.search(line)
            or ACTION_PIN_RE.search(line)
            or ACTION_EXPECTATION_RE.search(line)
        )
    if finding_type == "Secret Keyword":
        return any(marker in line for marker in PLACEHOLDER_MARKERS)
    return False


def scan_forbidden_values() -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if any(part in {".git", ".pytest_cache", "outputs"} for part in path.relative_to(ROOT).parts):
            continue
        if path.stat().st_size > 25 * 1024 * 1024:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for label, pattern in FORBIDDEN_VALUE_PATTERNS.items():
            match = pattern.search(text)
            if match:
                findings.append(
                    {
                        "file": rel,
                        "line": text.count("\n", 0, match.start()) + 1,
                        "type": label,
                    }
                )
    return findings


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = run_detect_secrets()
    approved = Counter()
    unexpected: list[dict[str, object]] = []
    for rel, findings in sorted(report["results"].items()):
        if not isinstance(rel, str) or not isinstance(findings, list):
            unexpected.append({"file": str(rel), "line": None, "type": "invalid report row"})
            continue
        for finding in findings:
            if not isinstance(finding, dict):
                unexpected.append({"file": rel, "line": None, "type": "invalid finding"})
                continue
            number = finding.get("line_number")
            line_number = number if isinstance(number, int) else 0
            line = line_for(ROOT / rel, line_number)
            if is_adjudicated(rel, finding, line):
                approved[str(finding.get("type", "unknown"))] += 1
            else:
                unexpected.append(
                    {
                        "file": rel,
                        "line": line_number or None,
                        "type": str(finding.get("type", "unknown")),
                    }
                )

    unexpected.extend(scan_forbidden_values())
    payload = {
        "status": "pass" if not unexpected else "fail",
        "approved_findings": dict(sorted(approved.items())),
        "approved_total": sum(approved.values()),
        "unexpected": unexpected,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif unexpected:
        print("Secret scan failed. Findings list file, line, and detector only.", file=sys.stderr)
        for finding in unexpected:
            print(
                f"{finding['file']}:{finding.get('line') or '?'}: {finding['type']}",
                file=sys.stderr,
            )
    else:
        print(f"Secret scan passed with {payload['approved_total']} adjudicated false positives.")
    return 1 if unexpected else 0


if __name__ == "__main__":
    raise SystemExit(main())
