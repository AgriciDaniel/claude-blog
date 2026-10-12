"""Wave 3 regression tests: brain script safety (demo vault, symlinks, edits, lint)."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BRAIN = ROOT / "brain"
SCRIPTS = BRAIN / "scripts"


def _run(script, *args, cwd=BRAIN):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True, text=True, cwd=cwd, check=False,
    )


@pytest.fixture
def vault(tmp_path):
    out = tmp_path / "vaults"
    result = _run(
        "scaffold_vault.py", "--client", "acme", "--client-name", "Acme",
        "--owner", "Tester", "--out-dir", str(out),
    )
    assert result.returncode == 0, result.stderr
    path = out / "acme"
    ingest = _run(
        "ingest_source.py", "--vault", str(path),
        "--file", str(BRAIN / "tests" / "fixtures" / "sample-source.md"),
        "--source-type", "fixture",
    )
    assert ingest.returncode == 0, ingest.stderr
    assert _run("synthesize_brain.py", "--vault", str(path)).returncode == 0
    return path


# ---- build_demo_vault ------------------------------------------------------

def test_force_refuses_a_scaffolded_vault_with_a_user_note(vault):
    note = vault / "wiki" / "My Own Note.md"
    note.write_text("precious user note\n", encoding="utf-8")
    result = _run("build_demo_vault.py", "--out", str(vault), "--force")
    assert result.returncode != 0
    assert ".demo-vault" in result.stderr + result.stdout
    assert note.read_text(encoding="utf-8") == "precious user note\n"
    assert (vault / "CODEX.md").exists()


def test_force_refuses_a_marked_demo_that_holds_a_user_file(tmp_path):
    demo = tmp_path / "demo"
    first = _run("build_demo_vault.py", "--out", str(demo))
    assert first.returncode == 0, first.stderr
    assert (demo / ".demo-vault").is_file()
    user = demo / "wiki" / "mine.md"
    user.write_text("keep me\n", encoding="utf-8")
    result = _run("build_demo_vault.py", "--out", str(demo), "--force")
    assert result.returncode != 0
    assert "did not create" in result.stderr + result.stdout
    assert user.read_text(encoding="utf-8") == "keep me\n"


def test_force_rebuilds_a_pristine_marked_demo(tmp_path):
    demo = tmp_path / "demo"
    assert _run("build_demo_vault.py", "--out", str(demo)).returncode == 0
    again = _run("build_demo_vault.py", "--out", str(demo), "--force", "--json")
    assert again.returncode == 0, again.stderr
    assert json.loads(again.stdout[again.stdout.rindex("{\n"):])["changed"] is False


def test_committed_sample_vault_carries_the_demo_marker():
    marker = BRAIN / "examples" / "sample-vault" / ".demo-vault"
    assert json.loads(marker.read_text(encoding="utf-8"))["demo_only"] is True


# ---- symlinked default outputs --------------------------------------------

def test_report_does_not_write_through_a_planted_symlink(vault, tmp_path):
    victim = tmp_path / "victim.txt"
    victim.write_text("do not touch\n", encoding="utf-8")
    (vault / "weekly-report.html").symlink_to(victim)
    result = _run("render_brain_report.py", "--vault", str(vault), "--html-only")
    assert result.returncode != 0
    assert "symlink" in result.stderr
    assert victim.read_text(encoding="utf-8") == "do not touch\n"


def test_report_explicit_out_symlink_is_not_followed(vault, tmp_path):
    victim = vault / "wiki" / "victim.html"
    victim.write_text("do not touch\n", encoding="utf-8")
    link = vault / "linked.html"
    link.symlink_to(victim)
    result = _run("render_brain_report.py", "--vault", str(vault), "--out", str(link))
    assert result.returncode != 0
    assert victim.read_text(encoding="utf-8") == "do not touch\n"


def test_report_normal_write_still_works(vault):
    result = _run("render_brain_report.py", "--vault", str(vault), "--html-only")
    assert result.returncode == 0, result.stderr
    assert "<h1>" in (vault / "weekly-report.html").read_text(encoding="utf-8")


def test_visuals_do_not_write_through_a_planted_symlink(vault, tmp_path):
    victim = tmp_path / "victim.svg"
    victim.write_text("do not touch\n", encoding="utf-8")
    target = vault / "_attachments" / "brain-relationship-map.svg"
    target.parent.mkdir(exist_ok=True)
    if target.exists() or target.is_symlink():
        target.unlink()
    target.symlink_to(victim)
    result = _run("generate_vault_visuals.py", "--vault", str(vault))
    assert result.returncode != 0
    assert victim.read_text(encoding="utf-8") == "do not touch\n"


def test_visuals_refuse_a_symlinked_attachments_directory(vault, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    shutil.rmtree(vault / "_attachments", ignore_errors=True)
    (vault / "_attachments").symlink_to(outside, target_is_directory=True)
    result = _run("generate_vault_visuals.py", "--vault", str(vault))
    assert result.returncode != 0
    assert list(outside.iterdir()) == []


# ---- synthesize keeps user edits ------------------------------------------

def test_resynthesis_keeps_user_edited_roadmap_sections(vault):
    roadmap = vault / "wiki" / "deliverables" / "Action Roadmap.md"
    text = roadmap.read_text(encoding="utf-8")
    edited = text.replace("1. Complete source intake.", "1. Ship the pricing page first.")
    edited += "\n## My Own Section\n\nOwner notes that must survive.\n"
    roadmap.write_text(edited, encoding="utf-8")
    result = _run("synthesize_brain.py", "--vault", str(vault), "--json")
    assert result.returncode == 0, result.stderr
    after = roadmap.read_text(encoding="utf-8")
    assert "Ship the pricing page first." in after
    assert "Owner notes that must survive." in after
    assert "Kept user-edited section(s)" in result.stderr
    assert json.loads(result.stdout)["preserved_sections"]


def test_handwritten_roadmap_stops_the_run_before_anything_is_written(vault):
    roadmap = vault / "wiki" / "deliverables" / "Action Roadmap.md"
    roadmap.write_text("---\ntitle: Mine\n---\n\n# Mine\n\n## Totally custom\n\nMy plan.\n", encoding="utf-8")
    scorecard = vault / "wiki" / "deliverables" / "Health Scorecard.md"
    before = scorecard.read_bytes()
    result = _run("synthesize_brain.py", "--vault", str(vault))
    assert result.returncode == 2
    assert "hand-written" in result.stderr
    assert "My plan." in roadmap.read_text(encoding="utf-8")
    assert scorecard.read_bytes() == before


def test_first_synthesis_still_replaces_the_scaffold_template(tmp_path):
    out = tmp_path / "vaults"
    assert _run("scaffold_vault.py", "--client", "fresh", "--client-name", "Fresh",
                "--owner", "T", "--out-dir", str(out)).returncode == 0
    vault = out / "fresh"
    assert "Roadmap construction rules" in (vault / "wiki/deliverables/Action Roadmap.md").read_text(encoding="utf-8")
    assert _run("ingest_source.py", "--vault", str(vault), "--file",
                str(BRAIN / "tests/fixtures/sample-source.md")).returncode == 0
    assert _run("synthesize_brain.py", "--vault", str(vault)).returncode == 0
    text = (vault / "wiki/deliverables/Action Roadmap.md").read_text(encoding="utf-8")
    assert "Roadmap construction rules" not in text and "## Immediate Actions" in text


def test_resynthesis_of_untouched_files_is_idempotent(vault):
    paths = [
        vault / "wiki" / "deliverables" / "Action Roadmap.md",
        vault / "wiki" / "deliverables" / "Health Scorecard.md",
        vault / "wiki" / "reports" / "Weekly Report.md",
    ]
    before = [p.read_bytes() for p in paths]
    assert _run("synthesize_brain.py", "--vault", str(vault)).returncode == 0
    assert [p.read_bytes() for p in paths] == before


# ---- sk- secret regex ------------------------------------------------------

def _load(name):
    spec = importlib.util.spec_from_file_location(f"wave3_{name}", SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SCRIPTS))
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("name", ["ingest_source", "package_release"])
def test_sk_pattern_needs_a_word_boundary(name):
    module = _load(name)
    patterns = getattr(module, "SECRET_PATTERNS", None) or module.FORBIDDEN_TEXT_PATTERNS
    openai = patterns["openai api key"]
    for benign in (b"risk-based-content-strategy-planning-guide", b"disk-backed-storage-configuration-notes"):
        assert not openai.search(benign), benign
    assert openai.search(b"key = sk-" + b"a" * 30)
    assert openai.search(b"sk-proj-" + b"B" * 30)
    assert patterns["anthropic api key"].search(b"x sk-ant-" + b"c" * 30)


def test_ingest_accepts_risk_prose_and_still_rejects_a_key(vault, tmp_path):
    good = tmp_path / "risk.md"
    good.write_text("# Notes\n\nA risk-based-content-strategy-planning approach.\n", encoding="utf-8")
    ok = _run("ingest_source.py", "--vault", str(vault), "--file", str(good), "--allow-source-root", str(tmp_path))
    assert ok.returncode == 0, ok.stderr
    bad = tmp_path / "leak.md"
    bad.write_text("token: sk-" + "d" * 30 + "\n", encoding="utf-8")
    refused = _run("ingest_source.py", "--vault", str(vault), "--file", str(bad), "--allow-source-root", str(tmp_path))
    assert refused.returncode == 2
    assert "possible secret" in refused.stderr


# ---- lint_vault exit codes --------------------------------------------------

def test_lint_clean_vault_passes(vault):
    assert _run("lint_vault.py", "--vault", str(vault)).returncode == 0


def test_lint_non_utf8_note_is_a_distinct_unreadable_error(vault):
    (vault / "wiki" / "bad.md").write_bytes(b"---\ntitle: x\n---\n\xff\xfe broken\n")
    result = _run("lint_vault.py", "--vault", str(vault))
    assert result.returncode == 2
    assert "Traceback" not in result.stderr
    assert "cannot read wiki/bad.md" in result.stderr


def test_lint_malformed_graph_json_is_a_distinct_unreadable_error(vault):
    graph = vault / ".obsidian" / "graph.json"
    graph.parent.mkdir(exist_ok=True)
    graph.write_text("{not json", encoding="utf-8")
    result = _run("lint_vault.py", "--vault", str(vault), "--json")
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert any(row["code"] == "UNREADABLE" for row in payload["diagnostics"])
    graph.write_text("[1, 2]", encoding="utf-8")
    assert _run("lint_vault.py", "--vault", str(vault)).returncode == 2


def test_lint_real_failure_still_exits_one(vault):
    (vault / "CODEX.md").unlink()
    result = _run("lint_vault.py", "--vault", str(vault))
    assert result.returncode == 1
    assert "missing CODEX.md" in result.stderr


def test_lint_real_failure_wins_over_unreadable_input(vault):
    (vault / "CODEX.md").unlink()
    (vault / "wiki" / "bad.md").write_bytes(b"\xff\xfe")
    assert _run("lint_vault.py", "--vault", str(vault)).returncode == 1
