"""Dependency manifests, hash locks and uv.lock must agree with each other.

The assertions are relational: they read every declared range and every locked
pin from the files and compare them, so a Dependabot bump of a range or an
exact pin never needs a matching edit here. A bump that leaves a stale lock
fails with the exact command that regenerates it.
"""
from __future__ import annotations

import re
import tomllib
from collections import defaultdict
from pathlib import Path

import pytest
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("blog-audio", "blog-google", "blog-notebooklm")
REQUIREMENT_FILES = [ROOT / "requirements.txt"] + [
    ROOT / "skills" / skill / "scripts" / "requirements.txt" for skill in SKILLS
]
LOCK_FILES = [path.with_suffix(".lock") for path in REQUIREMENT_FILES]

STANZA = re.compile(
    r"^(?P<name>[A-Za-z0-9_.-]+)==(?P<version>[^\s;\\]+)"
    r"(?: ; (?P<marker>[^\\]+?))? \\\n(?P<body>(?:[ \t]+.*\n?)*)",
    re.MULTILINE,
)
HASH = re.compile(r"--hash=sha256:[0-9a-f]{64}\b")


def _relock_hint(lock: Path) -> str:
    requirements = lock.with_suffix(".txt").relative_to(ROOT).as_posix()
    return (
        f"regenerate with: uv pip compile {requirements} --universal "
        f"--generate-hashes --python-version 3.11 --output-file "
        f"{lock.relative_to(ROOT).as_posix()}"
    )


def _locked(lock: Path) -> list[dict]:
    text = lock.read_text(encoding="utf-8")
    return [match.groupdict() for match in STANZA.finditer(text)]


def _declared(path: Path) -> list[Requirement]:
    lines = (line.split("#", 1)[0].strip() for line in path.read_text(encoding="utf-8").splitlines())
    return [Requirement(line) for line in lines if line]


def _pyproject_requirements() -> list[Requirement]:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return [
        Requirement(raw)
        for group in project["project"]["optional-dependencies"].values()
        for raw in group
    ]


def _versions_by_name(lock: Path) -> dict[str, set[str]]:
    versions: dict[str, set[str]] = defaultdict(set)
    for stanza in _locked(lock):
        versions[canonicalize_name(stanza["name"])].add(stanza["version"])
    return versions


@pytest.mark.parametrize("lock", LOCK_FILES, ids=lambda path: path.relative_to(ROOT).as_posix())
def test_lock_is_complete_and_hash_backed(lock):
    stanzas = _locked(lock)
    assert stanzas, f"{lock} contains no pinned packages"
    names = [canonicalize_name(stanza["name"]) for stanza in stanzas]
    # Universal locks may repeat a package with disjoint markers, never without.
    for name in set(names):
        repeated = [stanza for stanza in stanzas if canonicalize_name(stanza["name"]) == name]
        if len(repeated) > 1:
            assert all(stanza["marker"] for stanza in repeated), f"{lock}: {name} repeated without markers"
    for stanza in stanzas:
        assert HASH.search(stanza["body"]), f"{lock}: {stanza['name']}=={stanza['version']} has no sha256 hash"
        # The marker must be real PEP 508 syntax that pip can evaluate.
        marker = f" ; {stanza['marker']}" if stanza["marker"] else ""
        Requirement(f"{stanza['name']}=={stanza['version']}{marker}")


@pytest.mark.parametrize("requirements", REQUIREMENT_FILES, ids=lambda path: path.relative_to(ROOT).as_posix())
def test_declared_ranges_are_satisfied_by_their_lock(requirements):
    lock = requirements.with_suffix(".lock")
    versions = _versions_by_name(lock)
    for requirement in _declared(requirements):
        name = canonicalize_name(requirement.name)
        assert name in versions, f"{lock.name}: {name} is missing; {_relock_hint(lock)}"
        for version in versions[name]:
            assert requirement.specifier.contains(Version(version), prereleases=True), (
                f"{lock}: {name}=={version} violates {requirement}; {_relock_hint(lock)}"
            )


def test_pyproject_ranges_accept_every_locked_version():
    by_name: dict[str, list[Requirement]] = defaultdict(list)
    for requirement in _pyproject_requirements():
        by_name[canonicalize_name(requirement.name)].append(requirement)
    checked = 0
    for lock in LOCK_FILES:
        for name, versions in _versions_by_name(lock).items():
            for requirement in by_name.get(name, ()):
                for version in versions:
                    checked += 1
                    assert requirement.specifier.contains(Version(version), prereleases=True), (
                        f"pyproject.toml requires {requirement} but {lock.relative_to(ROOT)} "
                        f"pins {name}=={version}; {_relock_hint(lock)}"
                    )
    assert checked, "no pyproject dependency appears in any lock; the comparison proved nothing"


def test_exact_pins_agree_across_manifests_and_locks():
    """A package pinned with == anywhere must be pinned to one version everywhere."""
    exact: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    sources = [(ROOT / "pyproject.toml", _pyproject_requirements())] + [
        (path, _declared(path)) for path in REQUIREMENT_FILES
    ]
    for path, requirements in sources:
        for requirement in requirements:
            for spec in requirement.specifier:
                if spec.operator == "==":
                    exact[canonicalize_name(requirement.name)][spec.version].add(path.relative_to(ROOT).as_posix())
    assert exact, "no exact pins found; the agreement check proved nothing"
    for name, pins in exact.items():
        assert len(pins) == 1, f"{name} is pinned to different versions: {dict(pins)}"
        (version,) = pins
        for lock in LOCK_FILES:
            locked = _versions_by_name(lock).get(name)
            if locked is not None:
                assert locked == {version}, f"{lock.relative_to(ROOT)}: {name} lock {locked} != pin {version}"


def test_uv_lock_agrees_with_pip_locks_for_declared_packages():
    uv_lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    uv_versions: dict[str, set[str]] = defaultdict(set)
    for package in uv_lock["package"]:
        uv_versions[canonicalize_name(package["name"])].add(package["version"])
    declared = {canonicalize_name(r.name) for r in _pyproject_requirements()}
    for path in REQUIREMENT_FILES:
        declared |= {canonicalize_name(r.name) for r in _declared(path)}
    compared = 0
    for lock in LOCK_FILES:
        for name, versions in _versions_by_name(lock).items():
            if name in declared and name in uv_versions:
                compared += 1
                assert versions <= uv_versions[name], (
                    f"{lock.relative_to(ROOT)} pins {name} {sorted(versions)} but uv.lock has "
                    f"{sorted(uv_versions[name])}; run `uv lock` and {_relock_hint(lock)}"
                )
    assert compared, "no declared package appears in uv.lock; the comparison proved nothing"


@pytest.mark.parametrize("lock", LOCK_FILES, ids=lambda path: path.relative_to(ROOT).as_posix())
def test_locks_are_universal_not_linux_only(lock):
    header = "\n".join(lock.read_text(encoding="utf-8").splitlines()[:3])
    assert "--universal" in header, f"{lock.name} was not compiled with --universal; {_relock_hint(lock)}"


def test_platform_conditional_dependencies_are_locked_with_markers():
    """tqdm needs colorama on Windows only; a Linux-resolved lock drops it."""
    lock = ROOT / "requirements.lock"
    versions = _versions_by_name(lock)
    assert "tqdm" in versions or "textstat" in versions
    if "tqdm" in versions:
        stanzas = [s for s in _locked(lock) if canonicalize_name(s["name"]) == "colorama"]
        assert stanzas, f"colorama is missing for Windows installs; {_relock_hint(lock)}"
        assert all("win32" in (s["marker"] or "") for s in stanzas)
