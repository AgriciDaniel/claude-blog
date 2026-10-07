"""Canonical frontmatter and isolation regressions."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from lint_vault import validate_frontmatter


@pytest.mark.parametrize("tags", ["tags: [blog, evidence]", "tags:\n  - blog\n  - evidence", "tags:\n- blog\n- evidence"])
def test_valid_tag_sequences_and_evergreen_status(tmp_path, tags):
    path = tmp_path / "note.md"
    text = f"---\ntype: spoke\ntitle: Example\ndomain: Blog\nstatus: evergreen\ncreated: 2026-10-07\nupdated: 2026-10-07\n{tags}\n---\n"
    errors, warnings = [], []
    validate_frontmatter(tmp_path, path, text, errors, warnings, template=False)
    assert errors == []


@pytest.mark.parametrize("field", ["tags: [broken", "tags: plain-string", "tags:\n  nested: object", "tags: [one,,two]", "tags:\n - [nested]", "tags:\n - {name: nested}", "tags:\n - true", "status: unknown\ntags: [one]"])
def test_malformed_tags_and_status_remain_rejected(tmp_path, field):
    text = f"---\ntype: spoke\ntitle: Example\ndomain: Blog\nstatus: active\ncreated: 2026-10-07\nupdated: 2026-10-07\n{field}\n---\n"
    errors, warnings = [], []
    validate_frontmatter(tmp_path, tmp_path / "note.md", text, errors, warnings, template=False)
    assert errors


def test_pipeline_audit_cannot_write_or_restore_original_sources(tmp_path, monkeypatch):
    import test_pipeline
    repo = tmp_path / "original"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".raw" / "sources").mkdir(parents=True)
    raw = repo / ".raw" / "sources" / "immutable.txt"
    raw.write_text("immutable evidence")
    # A deliberately mutating audit proves that only the disposable export is
    # touched, even if a future audit acquires a write path.
    (repo / "scripts" / "audit_brain.py").write_text("from pathlib import Path\np=Path('.raw/sources/immutable.txt')\np.unlink()\np.write_text('changed audit output')\n")
    before = (raw.read_bytes(), raw.stat().st_ino, raw.stat().st_mtime_ns)
    monkeypatch.setattr(test_pipeline, "REPO", repo)
    test_pipeline.run_audit_report_only_hermetic()
    assert (raw.read_bytes(), raw.stat().st_ino, raw.stat().st_mtime_ns) == before


def test_pipeline_rejects_source_symlink_to_original(tmp_path, monkeypatch):
    import test_pipeline
    repo = tmp_path / "original"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".raw" / "sources").mkdir(parents=True)
    evidence = tmp_path / "outside.txt"
    evidence.write_text("immutable external evidence")
    (repo / ".raw" / "sources" / "link.txt").symlink_to(evidence)
    (repo / "scripts" / "audit_brain.py").write_text("raise AssertionError('must not execute')")
    monkeypatch.setattr(test_pipeline, "REPO", repo)
    with pytest.raises(AssertionError, match="symlink"):
        test_pipeline.run_audit_report_only_hermetic()
    assert evidence.read_text() == "immutable external evidence"
