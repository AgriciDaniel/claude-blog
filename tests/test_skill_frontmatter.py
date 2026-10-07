"""Real YAML metadata regressions and installed-relative Markdown contracts."""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from validate_skills import FrontmatterError, parse_frontmatter, validate_bundle, validate_frontmatter


def skill(**updates):
    fields = dict(name="blog-fixture", description="Fixture", license="MIT", **{"user-invocable": True, "argument-hint": "<file>"})
    fields.update(updates)
    return fields


def test_maintained_bundle_uses_one_yaml_and_policy_validator():
    assert validate_bundle(ROOT) == []
    values = {path.parent.name: parse_frontmatter(path.read_text())["user-invocable"] for path in (ROOT / "skills").glob("*/SKILL.md")}
    assert len(values) == 32
    assert values.pop("blog-chart") is False
    assert list(values.values()) == [True] * 31
    assert len(list((ROOT / "agents").glob("*.md"))) == 5


@pytest.mark.parametrize("yaml_body", ["name: one\nname: two", "metadata:\n  version: a\n  version: b", "description: [unterminated", "- one\n- two", "null", "1: value"])
def test_real_yaml_rejects_duplicate_malformed_and_nonmapping_frontmatter(yaml_body):
    with pytest.raises(FrontmatterError):
        parse_frontmatter(f"---\n{yaml_body}\n---\nBody")


@pytest.mark.parametrize("text", ["Body", "\n---\nname: one\n---", "---\nname: one"])
def test_missing_or_unterminated_yaml_fails(text):
    with pytest.raises(FrontmatterError):
        parse_frontmatter(text)


def test_folded_description_map_metadata_and_yaml_booleans():
    fields = parse_frontmatter('---\nname: blog-fixture\ndescription: >\n  First line\n  second line\nlicense: MIT\nuser-invocable: false\nmetadata:\n  version: "1.0"\n  nested: {reviewed: true}\n---\nBody')
    assert "First line second line" in fields["description"]
    assert fields["metadata"]["nested"]["reviewed"] is True
    assert validate_frontmatter(fields) == []


def test_native_missing_invocation_defaults_true_but_project_requires_explicit():
    fields = skill()
    del fields["user-invocable"]
    assert validate_frontmatter(fields, project_policy=False) == []
    assert any("host defaults to true" in error for error in validate_frontmatter(fields))
    fields["user-invokable"] = False
    assert any("misspelled" in error for error in validate_frontmatter(fields))


@pytest.mark.parametrize("updates", [{"user-invocable": "false"}, {"user-invocable": 0}, {"metadata": "version: 1"}, {"description": ["words"]}, {"allowed-tools": {"Bash": True}}, {"disable-model-invocation": []}])
def test_project_typed_metadata_rejects_wrong_shapes(updates):
    assert any("invalid type" in error for error in validate_frontmatter(skill(**updates)))


@pytest.mark.parametrize("tools", ["Read Grep", "Read, Grep", ["Read", "Grep", "Bash(git status *)"]])
def test_allowed_tools_host_support_is_separate_from_no_preapproval_policy(tools):
    fields = skill(**{"allowed-tools": tools})
    assert validate_frontmatter(fields, project_policy=False) == []
    assert validate_frontmatter(fields) == ["allowed-tools is valid host preapproval metadata, but project policy forbids skill preapprovals"]


@pytest.mark.parametrize("tools", ["Read, Grep, Bash", ["Read", "Bash"], ["Bash(git status *)"]])
def test_agent_actual_allowlist_rejects_bash_grants(tools):
    fields = dict(name="fixture", description="Fixture", tools=tools)
    assert any("Bash" in error for error in validate_frontmatter(fields, agent=True))
    assert validate_frontmatter(fields, agent=True, project_policy=False) == []


def test_agent_explicit_tools_policy_does_not_silently_inherit():
    assert validate_frontmatter(dict(name="fixture", description="Fixture"), agent=True) == ["missing required field tools"]


def test_cli_nonzero_diagnostics_for_real_invalid_file(tmp_path):
    path = tmp_path / "skills" / "blog-fixture" / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\nname: first\nname: duplicate\n---\n")
    result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_skills.py"), "--root", str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "skills/blog-fixture/SKILL.md: duplicate field 'name'" in result.stderr


@pytest.fixture(params=["plugin", "standalone"])
def installed_layout(tmp_path, request):
    package = tmp_path / ("cached plugin version" if request.param == "plugin" else "standalone profile")
    anchor = package / "skills" / "blog-style"
    anchor.mkdir(parents=True)
    helpers = package / "scripts"
    helpers.mkdir()
    (helpers / "style_learn.py").write_text("from pathlib import Path\nprint(Path(__file__).resolve())\n")
    reference = package / "skills/blog/references/quality-scoring.md"
    reference.parent.mkdir(parents=True)
    reference.write_text("TRUSTED BUNDLED REFERENCE")
    cwd = tmp_path / "unrelated consumer"
    (cwd / "scripts").mkdir(parents=True)
    (cwd / "scripts/style_learn.py").write_text("raise AssertionError('POISON CWD')")
    (cwd / "skills/blog/references").mkdir(parents=True)
    (cwd / "skills/blog/references/quality-scoring.md").write_text("POISON CWD")
    return anchor, helpers, reference, cwd


def run_style_snippet(anchor, cwd, **overrides):
    # The host renders this placeholder in Markdown. No shell env variable is
    # supplied, so accidental dependence on an exported host variable fails.
    text = (ROOT / "skills/blog-style/SKILL.md").read_text()
    block = re.search(r"```bash\n(.*?)\n```", text, re.S).group(1)
    block = block.replace("${CLAUDE_SKILL_DIR}", str(anchor)).replace("<paths>", "fixture.md")
    return run_rendered_block(block, cwd, **overrides)


def run_rendered_block(block, cwd, **overrides):
    env = {key: value for key, value in os.environ.items() if not key.startswith("CLAUDE_BLOG_") and key != "CLAUDE_SKILL_DIR"}
    env.update(overrides)
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    return subprocess.run(["bash", "-c", block], cwd=cwd, env=env, capture_output=True, text=True)


def test_rendered_installed_paths_choose_package_helper_and_reference(installed_layout):
    anchor, helpers, reference, cwd = installed_layout
    result = run_style_snippet(anchor, cwd)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == str(helpers / "style_learn.py")
    text = (ROOT / "skills/blog-write/SKILL.md").read_text()
    ref = re.search(r"`(\$\{CLAUDE_SKILL_DIR\}/../blog/references/quality-scoring.md)`", text).group(1)
    assert Path(ref.replace("${CLAUDE_SKILL_DIR}", str(anchor))).resolve() == reference
    assert Path(ref.replace("${CLAUDE_SKILL_DIR}", str(anchor))).read_text() == "TRUSTED BUNDLED REFERENCE"


def test_missing_installed_helper_fails_without_cwd_fallback(installed_layout):
    anchor, helpers, _, cwd = installed_layout
    (helpers / "style_learn.py").unlink()
    result = run_style_snippet(anchor, cwd)
    assert result.returncode != 0
    assert "POISON CWD" not in result.stderr


def test_operator_absolute_override_precedence_and_quoted_metacharacters(installed_layout, tmp_path):
    anchor, _, _, cwd = installed_layout
    override = tmp_path / "trusted override $(touch INJECTED)"
    override.mkdir()
    (override / "style_learn.py").write_text("print('OPERATOR OVERRIDE')")
    result = run_style_snippet(anchor, cwd, CLAUDE_BLOG_SCRIPTS_DIR=str(override))
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "OPERATOR OVERRIDE"
    assert not (cwd / "INJECTED").exists()


@pytest.mark.parametrize("override", ["scripts", "../scripts", "$(touch INJECTED)", "style_learn.py; touch INJECTED"])
def test_relative_and_malicious_helper_overrides_fail(installed_layout, override):
    anchor, _, _, cwd = installed_layout
    result = run_style_snippet(anchor, cwd, CLAUDE_BLOG_SCRIPTS_DIR=override)
    assert result.returncode == 1
    assert "script dir must be absolute" in result.stderr
    assert not (cwd / "INJECTED").exists()


def test_context_loader_uses_resolved_core_root_and_helper_override(installed_layout, tmp_path):
    anchor, helpers, _, cwd = installed_layout
    text = (ROOT / "skills/blog/SKILL.md").read_text()
    block = next(block for block in re.findall(r"```bash\n(.*?)\n\s*```", text, re.S) if 'if [ -n "${CLAUDE_BLOG_LOAD_UNTRUSTED_HELPER:-}" ]' in block)
    block = block.replace("${CLAUDE_SKILL_DIR}", str(anchor.parent / "blog"))
    loader = helpers / "load_untrusted_root.py"
    loader.write_text("from pathlib import Path\nprint(Path(__file__).resolve())")
    result = run_rendered_block(block, cwd)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == str(loader)
    override = tmp_path / "trusted loader.py"
    override.write_text("print('EXPLICIT TRUSTED LOADER')")
    result = run_rendered_block(block, cwd, CLAUDE_BLOG_LOAD_UNTRUSTED_HELPER=str(override))
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "EXPLICIT TRUSTED LOADER"
    result = run_rendered_block(block, cwd, CLAUDE_BLOG_LOAD_UNTRUSTED_HELPER="scripts/load_untrusted_root.py")
    assert result.returncode == 1
    assert "helper path must be absolute" in result.stderr
    loader.unlink()
    (cwd / "scripts/load_untrusted_root.py").write_text("raise AssertionError('POISON CWD')")
    result = run_rendered_block(block, cwd)
    assert result.returncode == 1
    assert "trusted load_untrusted_root.py not found" in result.stderr


@pytest.mark.parametrize("plugin", [True, False])
def test_update_ledger_selection_uses_installed_ancestry_not_cwd(tmp_path, plugin):
    package = tmp_path / "trusted package with spaces"
    anchor = package / "skills/blog"
    anchor.mkdir(parents=True)
    if plugin:
        manifest = package / ".claude-plugin/plugin.json"
        manifest.parent.mkdir()
        manifest.write_text('{"name":"fixture"}')
        ledger = package / "data/google-updates.json"
    else:
        ledger = anchor / "data/google-updates.json"
    ledger.parent.mkdir()
    ledger.write_text("TRUSTED LEDGER")
    cwd = tmp_path / "unrelated consumer"
    (cwd / "data").mkdir(parents=True)
    (cwd / "data/google-updates.json").write_text("POISON LEDGER")
    text = (ROOT / "skills/blog/SKILL.md").read_text()
    block = next(block for block in re.findall(r"```bash\n(.*?)\n```", text, re.S) if 'BLOG_UPDATE_LEDGER=' in block)
    block = block.replace("${CLAUDE_SKILL_DIR}", str(anchor)) + '\ncat "$BLOG_UPDATE_LEDGER"'
    result = run_rendered_block(block, cwd)
    assert result.returncode == 0, result.stderr
    assert result.stdout == "TRUSTED LEDGER"
    ledger.unlink()
    result = run_rendered_block(block, cwd)
    assert result.returncode == 1
    assert "installed update ledger missing" in result.stderr


def test_own_script_paths_and_sibling_overrides_are_host_rendered(installed_layout, tmp_path):
    anchor, _, _, cwd = installed_layout
    google = anchor.parent / "blog-google"
    (google / "scripts").mkdir(parents=True)
    runner = google / "scripts/run.py"
    runner.write_text("from pathlib import Path\nprint(Path(__file__).resolve())")
    text = (ROOT / "skills/blog-google/SKILL.md").read_text()
    block = next(block for block in re.findall(r"```bash\n(.*?)\n```", text, re.S) if "BLOG_SKILLS_DIR=" in block)
    block = block.replace("${CLAUDE_SKILL_DIR}", str(google))
    result = run_rendered_block(block, cwd)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == str(runner)
    result = run_rendered_block(block, cwd, CLAUDE_BLOG_SKILLS_DIR="skills")
    assert result.returncode == 1
    assert "skills dir must be absolute" in result.stderr
    override = tmp_path / "trusted skills override"
    (override / "blog-google/scripts").mkdir(parents=True)
    (override / "blog-google/scripts/run.py").write_text("print('TRUSTED SIBLING OVERRIDE')")
    result = run_rendered_block(block, cwd, CLAUDE_BLOG_SKILLS_DIR=str(override))
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "TRUSTED SIBLING OVERRIDE"
