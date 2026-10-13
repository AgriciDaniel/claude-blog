"""Ownership and preservation regressions for Brain install surfaces."""
from __future__ import annotations

import json
import os
import stat
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MARKER = ".claude-blog-brain-install.json"
LOADER_START = b"<!-- claude-blog-brain-install:start -->"
LOADER_END = b"<!-- claude-blog-brain-install:end -->"
LOADER_BLOCK = LOADER_START + b"\n@./claude-blog-brain/GEMINI.md\n" + LOADER_END


def run(script: str, home: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", script, *args],
        cwd=ROOT,
        env={**os.environ, "CLAUDE_BLOG_BRAIN_INSTALL_HOME": str(home)},
        text=True,
        capture_output=True,
        check=False,
    )


def codex_target(home: Path) -> Path:
    return home / ".codex" / "skills" / "claude-blog-brain"


def gemini_target(home: Path) -> Path:
    return home / ".gemini" / "claude-blog-brain"


def gemini_loader(home: Path) -> Path:
    return home / ".gemini" / "GEMINI.md"


def assert_ok(proc: subprocess.CompletedProcess[str]) -> None:
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_clean_install_repeat_and_clean_uninstall(tmp_path: Path) -> None:
    target = codex_target(tmp_path)
    first = run("install.sh", tmp_path, "--target", "codex")
    assert_ok(first)
    manifest = json.loads((target / MARKER).read_text(encoding="utf-8"))
    assert manifest["owner"] == "claude-blog-brain-installer"
    assert "SKILL.md" in manifest["managed_files"]
    installed_mode = (target / "scripts" / "audit_brain.py").stat().st_mode
    source_mode = (ROOT / "scripts" / "audit_brain.py").stat().st_mode
    assert bool(installed_mode & stat.S_IXUSR) == bool(source_mode & stat.S_IXUSR)

    second = run("install.sh", tmp_path, "--target", "codex")
    assert_ok(second)
    removed = run("uninstall.sh", tmp_path, "--target", "codex")
    assert_ok(removed)
    assert not target.exists()


def test_foreign_directory_is_never_overwritten_or_removed(tmp_path: Path) -> None:
    target = codex_target(tmp_path)
    target.mkdir(parents=True)
    foreign = target / "foreign.txt"
    foreign.write_text("keep\n", encoding="utf-8")

    install = run("install.sh", tmp_path, "--target", "codex")
    assert install.returncode != 0
    assert "unmarked" in install.stderr
    assert foreign.read_text(encoding="utf-8") == "keep\n"

    uninstall = run("uninstall.sh", tmp_path, "--target", "codex")
    assert uninstall.returncode != 0
    assert "unmarked" in uninstall.stderr
    assert foreign.read_text(encoding="utf-8") == "keep\n"


def test_modified_managed_file_blocks_update_and_uninstall(tmp_path: Path) -> None:
    target = codex_target(tmp_path)
    assert_ok(run("install.sh", tmp_path, "--target", "codex"))
    skill = target / "SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") + "\nuser edit\n", encoding="utf-8")

    install = run("install.sh", tmp_path, "--target", "codex")
    assert install.returncode != 0
    assert "was modified" in install.stderr
    assert skill.read_text(encoding="utf-8").endswith("user edit\n")

    uninstall = run("uninstall.sh", tmp_path, "--target", "codex")
    assert uninstall.returncode != 0
    assert "was modified" in uninstall.stderr
    assert skill.exists()


def test_untracked_user_files_survive_repeat_and_uninstall(tmp_path: Path) -> None:
    target = codex_target(tmp_path)
    assert_ok(run("install.sh", tmp_path, "--target", "codex"))
    user_file = target / "notes" / "mine.md"
    user_file.parent.mkdir()
    user_file.write_text("preserve me\n", encoding="utf-8")

    assert_ok(run("install.sh", tmp_path, "--target", "codex"))
    assert user_file.read_text(encoding="utf-8") == "preserve me\n"
    removed = run("uninstall.sh", tmp_path, "--target", "codex")
    assert_ok(removed)
    assert "preserved user files" in removed.stdout
    assert user_file.read_text(encoding="utf-8") == "preserve me\n"
    assert not (target / MARKER).exists()
    assert not (target / "SKILL.md").exists()


def test_all_preflight_prevents_partial_install(tmp_path: Path) -> None:
    foreign_target = tmp_path / ".gemini" / "claude-blog-brain"
    foreign_target.mkdir(parents=True)
    foreign = foreign_target / "foreign.txt"
    foreign.write_text("keep\n", encoding="utf-8")

    install = run("install.sh", tmp_path, "--target", "all")
    assert install.returncode != 0
    assert "unmarked" in install.stderr
    assert not codex_target(tmp_path).exists()
    assert foreign.read_text(encoding="utf-8") == "keep\n"


def test_all_preflight_prevents_partial_uninstall(tmp_path: Path) -> None:
    assert_ok(run("install.sh", tmp_path, "--target", "codex"))
    codex_skill = codex_target(tmp_path) / "SKILL.md"
    foreign_target = tmp_path / ".gemini" / "claude-blog-brain"
    foreign_target.mkdir(parents=True)
    foreign = foreign_target / "foreign.txt"
    foreign.write_text("keep\n", encoding="utf-8")

    uninstall = run("uninstall.sh", tmp_path, "--target", "all")
    assert uninstall.returncode != 0
    assert "unmarked" in uninstall.stderr
    assert codex_skill.exists()
    assert foreign.read_text(encoding="utf-8") == "keep\n"


def test_gemini_loader_round_trip_preserves_unrelated_bytes(tmp_path: Path) -> None:
    loader = gemini_loader(tmp_path)
    loader.parent.mkdir(parents=True)
    original = b"user bytes without newline: \xff"
    loader.write_bytes(original)

    first = run("install.sh", tmp_path, "--target", "gemini")
    assert_ok(first)
    assert loader.read_bytes() == original + LOADER_BLOCK
    repeated = run("install.sh", tmp_path, "--target", "gemini")
    assert_ok(repeated)
    assert loader.read_bytes() == original + LOADER_BLOCK

    removed = run("uninstall.sh", tmp_path, "--target", "gemini")
    assert_ok(removed)
    assert loader.read_bytes() == original
    assert not gemini_target(tmp_path).exists()


def test_gemini_uninstall_without_markers_is_loader_noop(tmp_path: Path) -> None:
    loader = gemini_loader(tmp_path)
    loader.parent.mkdir(parents=True)
    original = b"plain user loader\n\x00tail"
    loader.write_bytes(original)

    removed = run("uninstall.sh", tmp_path, "--target", "gemini")
    assert_ok(removed)
    assert loader.read_bytes() == original


@pytest.mark.parametrize("loader_kind", ["symlink", "directory"])
def test_nonregular_gemini_loader_blocks_all_before_mutation(
    tmp_path: Path, loader_kind: str
) -> None:
    loader = gemini_loader(tmp_path)
    loader.parent.mkdir(parents=True)
    if loader_kind == "symlink":
        real_loader = tmp_path / "real-GEMINI.md"
        real_loader.write_bytes(b"user loader")
        loader.symlink_to(real_loader)
    else:
        loader.mkdir()

    install = run("install.sh", tmp_path, "--target", "all")
    assert install.returncode != 0
    assert "not a regular file" in install.stderr
    assert not codex_target(tmp_path).exists()


def test_symlink_gemini_loader_blocks_all_uninstall_before_mutation(
    tmp_path: Path,
) -> None:
    assert_ok(run("install.sh", tmp_path, "--target", "codex"))
    loader = gemini_loader(tmp_path)
    loader.parent.mkdir(parents=True, exist_ok=True)
    real_loader = tmp_path / "real-GEMINI.md"
    real_loader.write_bytes(b"user loader")
    loader.symlink_to(real_loader)

    uninstall = run("uninstall.sh", tmp_path, "--target", "all")
    assert uninstall.returncode != 0
    assert "not a regular file" in uninstall.stderr
    assert codex_target(tmp_path).exists()
    assert real_loader.read_bytes() == b"user loader"


@pytest.mark.parametrize(
    "invalid_loader",
    [
        LOADER_START + b"\n@./user-edited/GEMINI.md\n" + LOADER_END,
        LOADER_BLOCK + LOADER_BLOCK,
        LOADER_START + b"\nmissing end marker",
    ],
)
def test_invalid_gemini_marker_blocks_install_before_target_mutation(
    tmp_path: Path, invalid_loader: bytes
) -> None:
    loader = gemini_loader(tmp_path)
    loader.parent.mkdir(parents=True)
    loader.write_bytes(invalid_loader)

    install = run("install.sh", tmp_path, "--target", "gemini")
    assert install.returncode != 0
    assert "malformed, duplicate, or modified" in install.stderr
    assert not gemini_target(tmp_path).exists()
    assert loader.read_bytes() == invalid_loader


def test_modified_owned_gemini_block_blocks_uninstall_before_target_mutation(
    tmp_path: Path,
) -> None:
    assert_ok(run("install.sh", tmp_path, "--target", "gemini"))
    loader = gemini_loader(tmp_path)
    modified = loader.read_bytes().replace(
        b"@./claude-blog-brain/GEMINI.md", b"@./user-edited/GEMINI.md"
    )
    loader.write_bytes(modified)

    uninstall = run("uninstall.sh", tmp_path, "--target", "gemini")
    assert uninstall.returncode != 0
    assert "malformed, duplicate, or modified" in uninstall.stderr
    assert gemini_target(tmp_path).exists()
    assert loader.read_bytes() == modified
