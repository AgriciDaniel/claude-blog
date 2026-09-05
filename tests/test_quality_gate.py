"""Tests for the blog post quality gate."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import analyze_blog
import quality_gate

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).parent / "fixtures"
SCRIPT = ROOT / "scripts" / "quality_gate.py"


def _copy_fixture(name: str, tmp_path: Path) -> Path:
    target = tmp_path / name
    target.write_text((FIXTURES / name).read_text(encoding="utf-8"), encoding="utf-8")
    return target


def test_passing_post_exits_zero(tmp_path, capsys):
    post = _copy_fixture("blog_pass.md", tmp_path)
    score = analyze_blog.analyze_file(str(post))["score"]["total"]

    assert score >= quality_gate.DEFAULT_THRESHOLD
    assert quality_gate.main([str(post)]) == 0
    assert "1 post(s) checked" in capsys.readouterr().out


def test_failing_post_exits_one(tmp_path, capsys):
    post = _copy_fixture("blog_fail.md", tmp_path)

    assert quality_gate.main([str(post)]) == 1
    output = capsys.readouterr().out
    assert "Blog quality gate failed" in output
    assert "blog_fail.md" in output
    assert "[high]" in output


def test_selection_skips_non_blog_paths(tmp_path):
    skill_file = tmp_path / "skills" / "blog" / "SKILL.md"
    skill_file.parent.mkdir(parents=True)
    skill_file.write_text(
        "---\n"
        "title: Looks Like a Post\n"
        "description: This should still be skipped because it is a skill file.\n"
        "---\n\n"
        "# Looks Like a Post\n",
        encoding="utf-8",
    )

    reference_file = tmp_path / "references" / "source.md"
    reference_file.parent.mkdir(parents=True)
    reference_file.write_text(
        "---\n"
        "title: Reference Entry\n"
        "description: This should be skipped because it is reference material.\n"
        "---\n\n"
        "# Reference Entry\n",
        encoding="utf-8",
    )

    notes_file = tmp_path / "notes.md"
    notes_file.write_text(
        "---\n"
        "source: Editorial memo\n"
        "---\n\n"
        "# Notes\n",
        encoding="utf-8",
    )

    post_file = tmp_path / "posts" / "post.md"
    post_file.parent.mkdir()
    post_file.write_text(
        "---\n"
        "title: A Real Blog Post\n"
        "description: This one has the required blog post frontmatter fields.\n"
        "---\n\n"
        "# A Real Blog Post\n",
        encoding="utf-8",
    )

    assert not quality_gate.is_blog_post(skill_file, root=tmp_path)
    assert not quality_gate.is_blog_post(reference_file, root=tmp_path)
    assert not quality_gate.is_blog_post(notes_file, root=tmp_path)
    assert quality_gate.is_blog_post(post_file, root=tmp_path)


def test_selection_uses_lexical_path_for_symlinks(tmp_path):
    docs_dir = tmp_path / "docs"
    posts_dir = tmp_path / "posts"
    docs_dir.mkdir()
    posts_dir.mkdir()

    docs_post = docs_dir / "doc-post.md"
    docs_post.write_text(
        "---\n"
        "title: Docs Post\n"
        "description: This target lives in an excluded directory.\n"
        "---\n\n"
        "# Docs Post\n",
        encoding="utf-8",
    )

    real_post = posts_dir / "real-post.md"
    real_post.write_text(
        "---\n"
        "title: Real Post\n"
        "description: This target lives outside excluded directories.\n"
        "---\n\n"
        "# Real Post\n",
        encoding="utf-8",
    )

    docs_link = docs_dir / "linked-real.md"
    root_link = tmp_path / "linked-docs.md"
    try:
        docs_link.symlink_to(real_post)
        root_link.symlink_to(docs_post)
    except OSError:
        pytest.skip("symlinks not supported on this filesystem")

    assert not quality_gate.is_blog_post(docs_link, root=tmp_path)
    assert quality_gate.is_blog_post(root_link, root=tmp_path)


def test_json_format_shape(tmp_path, capsys):
    post = _copy_fixture("blog_fail.md", tmp_path)

    assert quality_gate.main([str(post), "--format", "json"]) == 1
    payload = json.loads(capsys.readouterr().out)

    assert payload["threshold"] == quality_gate.DEFAULT_THRESHOLD
    assert len(payload["checked"]) == 1
    assert len(payload["failures"]) == 1
    assert payload["failures"][0]["file"].endswith("blog_fail.md")
    assert payload["failures"][0]["score"] < quality_gate.DEFAULT_THRESHOLD
    assert payload["failures"][0]["issues"]
    assert payload["failures"][0]["issues"][0]["severity"] == "high"


def test_invalid_utf8_returns_structured_json_error(tmp_path):
    bad_post = tmp_path / "bad.md"
    bad_post.write_bytes(
        b"---\ntitle: Bad\ndescription: Invalid bytes\n---\n\n# Bad\n\xff\n"
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(bad_post),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert "error" in payload
    assert "Could not analyze" in payload["error"]
    assert "Traceback" not in result.stderr
