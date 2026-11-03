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


def _make_claude_blog_root(root: Path) -> None:
    manifest = root / ".claude-plugin" / "plugin.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({"name": "claude-blog"}), encoding="utf-8")


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _git_repo(root: Path) -> None:
    _git(root, "init", "-q", ".")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")


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
    _make_claude_blog_root(tmp_path)
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
    _make_claude_blog_root(tmp_path)
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


def test_docs_post_is_gated_outside_a_claude_blog_checkout(tmp_path):
    post = tmp_path / "docs" / "post.md"
    post.parent.mkdir()
    post.write_text((FIXTURES / "blog_fail.md").read_text(encoding="utf-8"), encoding="utf-8")

    assert not quality_gate.is_excluded_path(post, root=tmp_path)
    assert not quality_gate.is_excluded_path(post)
    assert quality_gate.is_blog_post(post, root=tmp_path)


def test_exclusion_needs_the_claude_blog_manifest_name(tmp_path):
    manifest = tmp_path / ".claude-plugin" / "plugin.json"
    manifest.parent.mkdir()
    manifest.write_text(json.dumps({"name": "someone-elses-plugin"}), encoding="utf-8")
    post = tmp_path / "docs" / "post.md"
    post.parent.mkdir()
    post.write_text("---\ntitle: T\ndescription: D\n---\n", encoding="utf-8")

    assert not quality_gate.is_excluded_path(post, root=tmp_path)
    manifest.write_text("not json", encoding="utf-8")
    assert not quality_gate.is_excluded_path(post, root=tmp_path)


def test_exclusion_applies_inside_a_claude_blog_checkout_without_a_root_argument(tmp_path):
    _make_claude_blog_root(tmp_path)
    inside = tmp_path / "skills" / "x" / "SKILL.md"
    outside = tmp_path / "posts" / "post.md"

    assert quality_gate.is_excluded_path(inside)
    assert not quality_gate.is_excluded_path(outside)


def test_failing_post_staged_under_docs_is_gated(tmp_path):
    """Regression: a failing post under docs/ in a normal repo used to pass silently."""
    _git_repo(tmp_path)
    post = tmp_path / "docs" / "post.md"
    post.parent.mkdir()
    post.write_text((FIXTURES / "blog_fail.md").read_text(encoding="utf-8"), encoding="utf-8")
    _git(tmp_path, "add", "-A")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--select", "--staged"],
        cwd=tmp_path, capture_output=True, text=True, check=False,
    )

    assert result.returncode == 1, result.stdout + result.stderr
    assert "docs/post.md" in result.stdout


def test_staged_files_use_nul_separation_and_the_repo_top_level(tmp_path, monkeypatch):
    """Regression: names with spaces or accents were quoted, and subdirectory runs lost the prefix."""
    _git_repo(tmp_path)
    sub = tmp_path / "sub"
    sub.mkdir()
    fail = (FIXTURES / "blog_fail.md").read_text(encoding="utf-8")
    (tmp_path / "caf\u00e9 post.md").write_text(fail, encoding="utf-8")
    (sub / "in sub.md").write_text(fail, encoding="utf-8")
    (tmp_path / "gone.md").write_text(fail, encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "-c", "core.quotepath=true", "commit", "-q", "-m", "seed")
    (tmp_path / "gone.md").unlink()
    _git(tmp_path, "rm", "-q", "--cached", "gone.md")
    (tmp_path / "new post.md").write_text(fail, encoding="utf-8")
    (tmp_path / "caf\u00e9 post.md").write_text(fail + "\nchange\n", encoding="utf-8")
    _git(tmp_path, "add", "-A")

    monkeypatch.chdir(sub)
    staged = {Path(item).resolve() for item in quality_gate._staged_files()}

    assert staged == {
        (tmp_path / "new post.md").resolve(),
        (tmp_path / "caf\u00e9 post.md").resolve(),
    }


def test_skipped_files_are_counted_in_text_and_json(tmp_path, capsys):
    _make_claude_blog_root(tmp_path)
    skipped_doc = tmp_path / "docs" / "guide.md"
    skipped_doc.parent.mkdir()
    skipped_doc.write_text("---\ntitle: T\ndescription: D\n---\n", encoding="utf-8")
    notes = tmp_path / "notes.md"
    notes.write_text("# no frontmatter\n", encoding="utf-8")
    post = _copy_fixture("blog_pass.md", tmp_path)

    assert quality_gate.main(["--select", str(skipped_doc), str(notes), str(post)]) == 0
    text = capsys.readouterr().out
    assert "1 post(s) checked" in text
    assert "2 file(s) skipped" in text

    assert quality_gate.main(["--select", "--format", "json", str(skipped_doc), str(notes), str(post)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert {Path(item["file"]).name for item in payload["skipped"]} == {"guide.md", "notes.md"}
    assert all(item["reason"] for item in payload["skipped"])


def test_nothing_skipped_prints_no_skip_line(tmp_path, capsys):
    post = _copy_fixture("blog_pass.md", tmp_path)

    assert quality_gate.main([str(post)]) == 0
    assert "skipped" not in capsys.readouterr().out
