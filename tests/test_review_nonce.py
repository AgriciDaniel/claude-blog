"""Nonce-bound review.md provenance tests (VULN-803, v1.9.1).

Gate 4 v1.9.0 trusted any writer of <draft>/review.md. The 5-gate
contract collapsed to '4 gates + 1 filesystem write the orchestrator
trusts.' v1.9.1 adds nonce-bound provenance:

  1. Before dispatching the blog-reviewer agent, the orchestrator runs
     `blog_preflight.py --init-review-nonce --draft <dir>` which stores
     verifier state outside the draft and prints a CSPRNG nonce.
  2. The agent's prompt template includes the nonce; the agent emits
     `Nonce: <NONCE>` somewhere in review.md.
  3. Gate 4 reads external verifier state, then verifies review.md contains
     `Nonce: <matching value>`. Missing or mismatched -> gate fails.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PREFLIGHT = ROOT / "scripts" / "blog_preflight.py"


@pytest.fixture
def preflight_module(monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_BLOG_REVIEW_STATE_DIR", str(tmp_path / "review-state"))
    spec = importlib.util.spec_from_file_location("blog_preflight", PREFLIGHT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["blog_preflight_test_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


def _make_draft(tmp_path: Path, review_text: str = "") -> Path:
    draft = tmp_path / "post"
    draft.mkdir()
    if review_text:
        (draft / "review.md").write_text(review_text, encoding="utf-8")
    return draft


def _write_state(preflight_module, draft: Path, nonce: str) -> None:
    preflight_module._atomic_write_json(
        preflight_module._review_state_path(draft),
        {"draft": str(draft.resolve()), "nonce": nonce, "version": "test"},
    )


def test_init_review_nonce_creates_file_with_csprng_value(tmp_path, preflight_module):
    draft = tmp_path / "post"
    draft.mkdir()
    preflight_module._init_review_nonce(draft)
    state_path = preflight_module._review_state_path(draft)
    assert state_path.exists()
    nonce_value = json.loads(state_path.read_text(encoding="utf-8"))["nonce"]
    # 32 hex chars (16 bytes via secrets.token_hex(16))
    assert re.fullmatch(r"[0-9a-f]{32}", nonce_value), (
        f"nonce must be 32 hex chars, got {nonce_value!r}"
    )


def test_init_review_nonce_overwrites_existing(tmp_path, preflight_module):
    draft = tmp_path / "post"
    draft.mkdir()
    _write_state(preflight_module, draft, "0" * 32)
    preflight_module._init_review_nonce(draft)
    data = json.loads(preflight_module._review_state_path(draft).read_text(encoding="utf-8"))
    assert data["nonce"] != "0" * 32


def test_gate_4_passes_when_nonce_matches(tmp_path, preflight_module):
    nonce = "a" * 32
    review = _passing_review(nonce)
    draft = _make_draft(tmp_path, review_text=review)
    _write_state(preflight_module, draft, nonce)
    result = preflight_module.gate_4_content_review(draft)
    assert result["passed"] is True, f"Gate should pass with matching nonce: {result}"


def test_gate_4_fails_when_nonce_file_present_but_review_lacks_nonce(tmp_path, preflight_module):
    nonce = "b" * 32
    review = _passing_review(nonce).replace(f"Nonce: {nonce}\n", "")
    draft = _make_draft(tmp_path, review_text=review)
    _write_state(preflight_module, draft, nonce)
    result = preflight_module.gate_4_content_review(draft)
    assert result["passed"] is False, "Gate should fail when nonce file exists but review lacks Nonce: line"
    assert any("nonce" in v.lower() for v in result.get("violations", []))


def test_gate_4_fails_when_review_has_wrong_nonce(tmp_path, preflight_module):
    real_nonce = "c" * 32
    fake_nonce = "d" * 32
    review = _passing_review(fake_nonce)
    draft = _make_draft(tmp_path, review_text=review)
    _write_state(preflight_module, draft, real_nonce)
    result = preflight_module.gate_4_content_review(draft)
    assert result["passed"] is False, "Gate should fail on nonce mismatch"
    assert any("nonce" in v.lower() for v in result.get("violations", []))


def test_gate_4_fails_when_external_state_absent(tmp_path, preflight_module):
    review = _passing_review("f" * 32)
    draft = _make_draft(tmp_path, review_text=review)
    result = preflight_module.gate_4_content_review(draft)
    assert result["passed"] is False
    assert any("verifier state" in v.lower() for v in result.get("violations", []))


def test_gate_4_nonce_must_be_exact_match_no_suffix_attack(tmp_path, preflight_module):
    """Nonce match must be word-bounded; substring match shouldn't fool the gate."""
    nonce = "e" * 32
    # Attacker emits a different 32-char string that contains the real nonce as
    # a prefix or suffix in raw text.
    leaked = nonce + "f" * 4  # 36 chars, starts with the real nonce
    review = _passing_review(nonce).replace(f"Nonce: {nonce}", f"Nonce: {leaked}")
    draft = _make_draft(tmp_path, review_text=review)
    _write_state(preflight_module, draft, nonce)
    result = preflight_module.gate_4_content_review(draft)
    assert result["passed"] is False, "Suffix attack on nonce match must be refused"


def test_gate_4_rejects_score_above_100(tmp_path, preflight_module):
    nonce = "1" * 32
    review = _passing_review(nonce).replace("92/100", "999/100")
    draft = _make_draft(tmp_path, review_text=review)
    _write_state(preflight_module, draft, nonce)
    result = preflight_module.gate_4_content_review(draft)
    assert result["passed"] is False
    assert any("outside 0..100" in v for v in result.get("violations", []))


def test_gate_4_style_diagnostics_do_not_block(tmp_path, preflight_module):
    nonce = "2" * 32
    review = _passing_review(nonce).replace(
        "zero P0 issues found\n",
        "- Sentence-length variation: 0.01\n"
        "- Configured style phrases: 99\n"
        "- Vocabulary diversity sample: 0.10\n"
        "zero P0 issues found\n",
    )
    draft = _make_draft(tmp_path, review_text=review)
    _write_state(preflight_module, draft, nonce)

    result = preflight_module.gate_4_content_review(draft)

    assert result["passed"] is True


def test_init_review_nonce_cli_flag(tmp_path):
    """`blog_preflight.py --init-review-nonce --draft <dir>` exits 0 and writes the file."""
    draft = tmp_path / "post"
    draft.mkdir()
    env = {**os.environ, "CLAUDE_BLOG_REVIEW_STATE_DIR": str(tmp_path / "state")}
    result = subprocess.run(
        [sys.executable, str(PREFLIGHT), "--init-review-nonce", "--draft", str(draft)],
        capture_output=True, text=True, cwd=str(ROOT), env=env,
    )
    assert result.returncode == 0, (
        f"--init-review-nonce should exit 0; stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert not (draft / ".review-nonce").exists()
    value = result.stdout.strip()
    assert re.fullmatch(r"[0-9a-f]{32}", value)


def _passing_review(nonce: str) -> str:
    return (
        "## Quality Review: Fixture\n"
        "### Overall Score: 92/100 - Exceptional\n"
        "### Editorial Style Diagnostics\n"
        "These observations are advisory and do not infer authorship.\n"
        "zero P0 issues found\n"
        f"Nonce: {nonce}\n"
        "BLOCKING: false (cleared all gates; 92/100 overall, no P0)\n"
    )
