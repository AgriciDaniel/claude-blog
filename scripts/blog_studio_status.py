#!/usr/bin/env python3
"""Inspect saved preflight evidence without rendering, network calls or writes.

Fingerprints describe the files checked, not authenticated approval. The
preflight remains the delivery authority. Legacy reports have unknown freshness.

Usage:
    python3 scripts/blog_studio_status.py --draft <dir> [--project-root <root>]
        [--expected-run <32-hex run id>]

Reads <draft>/preflight-report.json (written by blog_preflight.py) and prints
one JSON object on stdout: schema_version, status (passed, blocked, partial,
stale, unverified or error), passed_count, gates, artifacts, diagnostics,
checked_at and, once the report carries evidence, run_id. Exit status is 1 only
for status "error", otherwise 0. With --project-root the inspection is anchored
inside that project and refuses symlinked or traversing draft paths. With
--expected-run a report from any other run is an error. The same module also
supplies the fingerprint helpers blog_preflight.py uses to write the report's
additive "evidence" object (see skills/blog/references/blog-delivery-contract.md).
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import datetime as dt
import hashlib
import json
import math
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any

# blog_preflight is imported lazily from this directory, also under `python3 -I`.
sys.path.insert(0, str(Path(__file__).resolve().parent))

EVIDENCE_VERSION = 1
MAX_REPORT_BYTES = 1024 * 1024
MAX_FILES = 4096
MAX_INPUT_BYTES = 512 * 1024 * 1024
EXCLUDED_FILES = {"preflight-report.json", "capabilities.json", ".iteration-count"}
SCREENSHOTS = {"preview/mobile-375.png", "preview/tablet-768.png",
               "preview/desktop-1280.png", "preview/desktop-1280-dark.png"}
LABELS = {
    "passed": "Preflight passed", "blocked": "Blocked", "partial": "Partial",
    "stale": "Stale", "unverified": "Unverified", "error": "Execution error",
}


@contextmanager
def anchored_draft(draft_name: str, project_name: str):
    """Anchor a Linux companion subprocess to a verified directory object.

    Walking with directory descriptors and O_NOFOLLOW refuses ancestor links.
    Relative gate I/O then uses the anchored cwd, so replacing the lexical
    draft path after launch cannot redirect report writes to another directory.
    This is path containment, not a sandbox against a hostile local user.
    """
    if not all(hasattr(os, name) for name in ("O_NOFOLLOW", "O_DIRECTORY", "fchdir")):
        raise ValueError("project-contained execution requires Unix directory descriptors")
    # "." is harmless (pathlib drops it, so `--project-root .` works); ".." is not.
    if any(part == ".." for value in (draft_name, project_name) for part in value.split("/")):
        raise ValueError("draft/project traversal is refused")
    project = Path(project_name).absolute()
    selected = Path(draft_name).absolute()
    selected.relative_to(project)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    previous = os.open(".", flags)
    current = -1
    try:
        current = os.open("/", flags)
        for component in selected.parts[1:]:
            child = os.open(component, flags, dir_fd=current)
            os.close(current)
            current = child
        expected, actual = os.stat(selected, follow_symlinks=False), os.fstat(current)
        if (expected.st_dev, expected.st_ino) != (actual.st_dev, actual.st_ino):
            raise ValueError("selected draft changed during launch")
        os.fchdir(current)
        yield Path("."), str(selected)
    finally:
        os.fchdir(previous)
        os.close(previous)
        if current >= 0:
            os.close(current)



def safe_text(value: str, limit: int = 500) -> str:
    """Bound diagnostic text and suppress terminal control codes and nonces."""
    value = re.sub(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|$))", "", value)
    value = re.sub(r"\b[0-9a-fA-F]{32}\b", "[redacted identifier]", value)
    return "".join(c for c in value if c.isprintable() or c == "\n")[:limit]


def _open_no_follow(path: Path, flags: int) -> int:
    """Open through anchored parent descriptors on the Linux target."""
    if os.open not in os.supports_dir_fd or not hasattr(os, "O_NOFOLLOW"):
        return os.open(path, flags)
    parts = path.parts[1:] if path.is_absolute() else path.parts
    if ".." in parts:
        raise ValueError("fingerprint traversal is refused")
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    parent = os.open("/" if path.is_absolute() else ".", directory_flags)
    try:
        for component in parts[:-1]:
            child = os.open(component, directory_flags, dir_fd=parent)
            os.close(parent)
            parent = child
        return os.open(parts[-1] if parts else ".", flags, dir_fd=parent)
    finally:
        os.close(parent)


def _entries(directory: Path) -> list[tuple[Path, int]]:
    if os.stat not in os.supports_dir_fd or not hasattr(os, "O_DIRECTORY"):
        return [(path, path.lstat().st_mode) for path in sorted(directory.iterdir())]
    fd = _open_no_follow(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        names = sorted(os.listdir(fd))
        if len(names) > MAX_FILES:
            raise ValueError("fingerprint directory entry limit exceeded")
        return [(directory / name, os.stat(name, dir_fd=fd, follow_symlinks=False).st_mode) for name in names]
    finally:
        os.close(fd)


def _file_hash(path: Path, budget: int = MAX_INPUT_BYTES) -> dict[str, Any]:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    fd = _open_no_follow(path, flags)
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > budget:
            raise ValueError("not a regular file or fingerprint byte limit exceeded")
        digest = hashlib.sha256()
        total = 0
        while chunk := stream.read(min(1024 * 1024, budget - total + 1)):
            total += len(chunk)
            if total > budget:
                raise ValueError("fingerprint byte limit exceeded")
            digest.update(chunk)
        after = os.fstat(stream.fileno())
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
            after.st_size, after.st_mtime_ns, after.st_ctime_ns
        ):
            raise ValueError("file changed during fingerprinting")
    return {"sha256": digest.hexdigest(), "size": total}


def _optional_hash(path: Path) -> dict[str, Any] | None:
    try:
        return _file_hash(path)
    except FileNotFoundError:
        return None


def capture_inputs(draft: Path, review_state_path: Path) -> dict[str, Any]:
    """Conservatively fingerprint the bounded draft tree and verifier state.

    All regular files are inputs except known preflight outputs. This includes
    local styles, fonts, images and scripts whose browser use is dynamic.
    Symlinks and unsupported file types make freshness unverified.
    """
    files: dict[str, Any] = {}
    errors: list[str] = []
    total = 0
    try:
        pending = [draft]
        while pending:
            directory = pending.pop()
            if directory.is_symlink():
                raise ValueError("symlink directory in draft")
            for path, mode in _entries(directory):
                relative = path.relative_to(draft).as_posix()
                if relative in SCREENSHOTS or relative in EXCLUDED_FILES:
                    continue
                # Atomic preflight temporary files are outputs, not inputs.
                if path.parent == draft and path.name.startswith((".preflight-report.json.", ".capabilities.json.", ".iteration-count.")):
                    continue
                if any(path.parent == draft / "preview" and path.name.startswith("." + Path(name).name + ".")
                       for name in SCREENSHOTS):
                    continue
                if stat.S_ISLNK(mode):
                    raise ValueError("symlink in draft: " + relative)
                if stat.S_ISDIR(mode):
                    pending.append(path)
                elif stat.S_ISREG(mode):
                    if len(files) >= MAX_FILES:
                        raise ValueError("fingerprint file limit exceeded")
                    value = _file_hash(path, MAX_INPUT_BYTES - total)
                    files[relative] = value
                    total += value["size"]
                else:
                    raise ValueError("unsupported file type: " + relative)
        verifier = _optional_hash(review_state_path)
    except (OSError, ValueError) as exc:
        errors.append(safe_text(str(exc)))
        verifier = None
    return {"files": files, "review_state": verifier, "errors": errors}


def capture_outputs(draft: Path) -> dict[str, Any]:
    files: dict[str, Any] = {}
    errors: list[str] = []
    try:
        if (draft / "preview").is_symlink():
            raise ValueError("preview is a symlink")
        paths = [draft / "capabilities.json", *(draft / name for name in sorted(SCREENSHOTS))]
        total = 0
        for path in paths:
            if not path.exists() and not path.is_symlink():
                continue
            if len(files) >= MAX_FILES or path.is_symlink():
                raise ValueError("unsafe or excessive generated outputs")
            value = _file_hash(path, MAX_INPUT_BYTES - total)
            files[path.relative_to(draft).as_posix()] = value
            total += value["size"]
    except (OSError, ValueError) as exc:
        errors.append(safe_text(str(exc)))
    return {"files": files, "errors": errors}


def engine_identity() -> dict[str, Any]:
    scripts = Path(__file__).resolve().parent
    files = {}
    errors = []
    for name in ("blog_preflight.py", "blog_studio_status.py"):
        try:
            files[name] = _file_hash(scripts / name)
        except (OSError, ValueError):
            errors.append("Engine fingerprint unavailable: " + name)
    for name in ("skills/blog/references/blog-delivery-contract.md", "agents/blog-reviewer.md"):
        try:
            files[name] = _file_hash(scripts.parent / name)
        except (OSError, ValueError):
            errors.append("Contract fingerprint unavailable: " + name)
    return {"files": files, "python": list(sys.version_info[:3]), "errors": errors}


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def load_report(path: Path) -> dict[str, Any]:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    fd = _open_no_follow(path, flags)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_REPORT_BYTES:
            raise ValueError("report must be a regular file within the size limit")
        data = stream.read(MAX_REPORT_BYTES + 1)
        if len(data) > MAX_REPORT_BYTES:
            raise ValueError("report exceeds size limit")
        result = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object)
    if not isinstance(result, dict):
        raise ValueError("report must be an object")
    return result


def _validate_report(report: dict[str, Any]) -> list[dict[str, Any]]:
    if type(report.get("strict")) is not bool or type(report.get("blocked")) is not bool:
        raise ValueError("report strict/blocked must be booleans")
    gates = report.get("gates")
    if not isinstance(gates, list) or not 1 <= len(gates) <= 5:
        raise ValueError("report requires one to five gates")
    seen = set()
    for gate in gates:
        if not isinstance(gate, dict) or type(gate.get("gate")) is not int:
            raise ValueError("invalid gate")
        number = gate["gate"]
        if number not in range(1, 6) or number in seen or type(gate.get("passed")) is not bool:
            raise ValueError("invalid, duplicate or nonboolean gate")
        seen.add(number)
        for key in ("violations", "warnings"):
            value = gate.get(key, [])
            if not isinstance(value, list) or len(value) > 200 or not all(isinstance(v, str) for v in value):
                raise ValueError("invalid gate diagnostics")
        if not isinstance(gate.get("name"), str):
            raise ValueError("invalid gate name")
        if gate["passed"] and gate.get("violations"):
            raise ValueError("passing gate contains violations")
        score = gate.get("score")
        if score is not None and (type(score) not in (int, float) or not math.isfinite(score) or not 0 <= score <= 100):
            raise ValueError("invalid reviewer score")
        if number == 4 and gate["passed"] and (score is None or score < 90):
            raise ValueError("passing content review contradicts the delivery threshold")
    if report["blocked"] != any(not g["passed"] for g in gates):
        raise ValueError("report blocked flag contradicts gate results")
    return gates


def inspect_status(draft: Path, project_root: Path | None = None, expected_run: str | None = None) -> dict[str, Any]:
    if project_root is None:
        return _inspect_status(draft, expected_run)
    try:
        with anchored_draft(str(draft), str(project_root)) as (anchored, identity):
            return _inspect_status(anchored, expected_run, identity)
    except (OSError, ValueError) as exc:
        status = "unverified" if isinstance(exc, FileNotFoundError) else "error"
        return {"schema_version": 1, "status": status, "label": LABELS[status],
                "checked_at": None, "passed_count": 0, "gates": [], "artifacts": [],
                "diagnostics": [safe_text("Project-contained inspection refused: " + str(exc))]}


def _inspect_status(draft: Path, expected_run: str | None = None, draft_identity: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"schema_version": 1, "status": "unverified", "label": LABELS["unverified"],
                              "checked_at": None, "passed_count": 0, "gates": [], "artifacts": [], "diagnostics": []}
    def finish(status: str, message: str | None = None) -> dict[str, Any]:
        result.update(status=status, label=LABELS[status])
        if message:
            result["diagnostics"].append(safe_text(message))
        return result
    try:
        if draft.is_symlink() or not draft.is_dir():
            raise ValueError("draft must be a regular directory")
        if draft_identity is None:
            draft = draft.resolve()
            draft_identity = str(draft)
        report = load_report(draft / "preflight-report.json")
        if report.get("draft") != draft_identity:
            raise ValueError("report belongs to a different draft")
        if report.get("incomplete") is True:
            # Start marker or iteration-cap record: no current gate results.
            return finish("blocked", "Preflight did not finish: " + str(report.get("reason", "run incomplete")))
        gates = _validate_report(report)
        result["passed_count"] = sum(g["passed"] for g in gates)
        result["gates"] = [{"gate": g["gate"], "name": safe_text(g["name"]), "passed": g["passed"],
                            "violations": [safe_text(v) for v in g.get("violations", [])],
                            "warnings": [safe_text(v) for v in g.get("warnings", [])],
                            "score": g.get("score") if type(g.get("score")) in (int, float) else None} for g in gates]
        evidence = report.get("evidence")
        if not isinstance(evidence, dict) or evidence.get("schema_version") != EVIDENCE_VERSION:
            return finish("unverified", "Saved report has no supported freshness evidence. Run checks.")
        run_id = evidence.get("run_id")
        if not isinstance(run_id, str) or not re.fullmatch(r"[0-9a-f]{32}", run_id):
            raise ValueError("invalid run identity")
        if expected_run is not None and run_id != expected_run:
            return finish("error", "Saved report does not match this check run.")
        result["run_id"] = run_id
        for key in ("started_at", "finished_at"):
            stamp = dt.datetime.fromisoformat(evidence[key])
            if stamp.tzinfo is None or stamp.utcoffset() != dt.timedelta(0):
                raise ValueError("evidence timestamps must use UTC")
        if dt.datetime.fromisoformat(evidence["started_at"]) > dt.datetime.fromisoformat(evidence["finished_at"]):
            raise ValueError("invalid check timestamps")
        if evidence.get("contract_version") != blog_contract_version():
            return finish("stale", "Delivery contract version changed since the check.")
        result["checked_at"] = evidence["finished_at"]
        completed = [g["gate"] for g in gates]
        requested = evidence.get("requested_gates")
        if (evidence.get("completed_gates") != completed or not isinstance(requested, list)
                or not requested or any(type(n) is not int or n not in range(1, 6) for n in requested)
                or len(set(requested)) != len(requested) or completed != requested[:len(completed)]):
            raise ValueError("evidence gate scope contradicts results")
        # Import the canonical nonce-state locator without running any gates.
        import blog_preflight
        current = capture_inputs(draft, blog_preflight._review_state_path(draft))
        current_engine = engine_identity()
        if current_engine["errors"]:
            return finish("unverified", "Engine identity could not be established.")
        if evidence.get("engine") != current_engine:
            return finish("stale", "Engine or Python runtime changed since the check.")
        if current["errors"] or evidence.get("inputs", {}).get("errors") or evidence.get("outputs", {}).get("errors"):
            return finish("unverified", "Freshness could not be established for all files.")
        if evidence.get("inputs_unchanged") is not True or current != evidence.get("inputs"):
            return finish("stale", "Article inputs or review verifier state changed. Run checks again.")
        if capture_outputs(draft) != evidence.get("outputs"):
            return finish("stale", "Generated verification artifacts changed or are missing.")
        result["artifacts"] = [safe_text(p, 1000) for p in sorted(current["files"])] + [safe_text(p, 1000) for p in sorted(evidence["outputs"]["files"])]
        if not report["strict"]:
            return finish("unverified", "Preview mode cannot establish strict preflight success.")
        if report["blocked"]:
            return finish("blocked")
        if evidence["requested_gates"] != [1, 2, 3, 4, 5] or completed != [1, 2, 3, 4, 5]:
            return finish("partial", "Only part of the delivery contract was checked.")
        return finish("passed")
    except FileNotFoundError:
        return finish("unverified", "No saved report or selected draft is available. Run checks.")
    except ImportError as exc:
        return finish("error", "Engine module unavailable: " + str(exc))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RecursionError) as exc:
        return finish("error", "Invalid evidence: " + str(exc))


def blog_contract_version() -> str:
    import blog_preflight
    return blog_preflight.CONTRACT_VERSION


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--draft", type=Path, required=True)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--expected-run")
    args = parser.parse_args()
    result = inspect_status(args.draft, args.project_root, args.expected_run)
    print(json.dumps(result, allow_nan=False))
    return 1 if result["status"] == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
