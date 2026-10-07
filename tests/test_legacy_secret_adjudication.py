"""Bound public ownership-commit adjudication without ignoring other findings."""
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("legacy_secret_policy", ROOT / "scripts/check_secrets.py")
POLICY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLICY)
PUBLIC_COMMIT = sorted(POLICY.REVIEWED_LEGACY_COMMITS)[0]


def declaration(path, commit):
    if path.startswith("data/"):
        return f'  "commit": "{commit}",'
    if path.endswith(".ps1"):
        return f'$Baseline = "{commit}"'
    if path.endswith("test_windows_installer_ownership.py"):
        return f'    assert "{commit}" in source'
    return f'    "{commit}",'


@pytest.mark.parametrize("path", sorted(POLICY.LEGACY_COMMIT_PATHS))
def test_reviewed_public_commit_is_adjudicated_only_in_evidence_paths(path):
    line = declaration(path, PUBLIC_COMMIT)
    assert POLICY.is_adjudicated(path, {"type": "Hex High Entropy String"}, line)
    assert not POLICY.is_adjudicated("scripts/unrelated.py", {"type": "Hex High Entropy String"}, line)


def test_unknown_or_mixed_high_entropy_values_remain_unadjudicated():
    path = "data/legacy-install-ownership.json"
    unknown = "abcdef0123456789" * 2 + "abcdef01"
    assert not POLICY.is_adjudicated(path, {"type": "Hex High Entropy String"}, declaration(path, unknown))
    line = declaration(path, PUBLIC_COMMIT)
    assert not POLICY.is_adjudicated(path, {"type": "Hex High Entropy String"}, line + " " + unknown)
    assert not POLICY.is_adjudicated(path, {"type": "Hex High Entropy String"}, line + " " + "a" * 64)
    assert not POLICY.is_adjudicated(path, {"type": "Secret Keyword"}, line)


def test_public_commit_on_line_does_not_disable_credential_detection(tmp_path, monkeypatch):
    monkeypatch.setattr(POLICY, "ROOT", tmp_path)
    path = tmp_path / "data/legacy-install-ownership.json"
    path.parent.mkdir()
    # Construct the hostile fixture at runtime so no real credential is stored.
    path.write_text(PUBLIC_COMMIT + " " + "ghp_" + "A" * 36 + "\n")
    assert POLICY.scan_forbidden_values() == [{"file": "data/legacy-install-ownership.json", "line": 1, "type": "GitHub token"}]
