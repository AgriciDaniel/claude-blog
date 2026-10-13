"""Unit tests for the CI wrapper around `claude plugin validate`.

Samples under tests/fixtures/plugin_validate/ are real validator output
captured from Claude Code 2.1.218, 2.1.292 and 2.1.296 against this tree, and
against a copy with extra defects injected (bad manifest field types, an
unparseable skill and agent frontmatter, an invalid marketplace source). Paths
inside them are normalized to a runner-style prefix.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".github" / "scripts" / "validate_plugin_tolerate_reserved_name.py"
SAMPLES = ROOT / "tests" / "fixtures" / "plugin_validate"


def _load():
    spec = importlib.util.spec_from_file_location("validate_plugin_tolerance", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tolerance = _load()


def _sample(name: str) -> str:
    return (SAMPLES / name).read_text(encoding="utf-8")


def test_old_cli_pass_tolerates_only_the_studio_types_warning():
    ok, tolerated, blocking = tolerance.evaluate(_sample("v2.1.218-shipped-tree.txt"), 0)
    assert ok and not blocking
    assert tolerated == ["blog-studio-types-field-warning"]


def test_the_types_warning_is_tolerated_only_once_and_only_on_the_studio_entry():
    text = _sample("v2.1.218-shipped-tree.txt")
    ok, _t, blocking = tolerance.evaluate(text + text.split("\n", 2)[2], 0)
    assert not ok and any("duplicate" in item or "plugins[1]" in item for item in blocking)
    other = text.replace("plugins[1]", "plugins[0]")
    ok, _t, blocking = tolerance.evaluate(other, 0)
    assert not ok and any("plugins[0] plugin.json" in item for item in blocking)
    other_field = text.replace("types: Unknown field 'types'", "hooks: Unknown field 'hooks'")
    ok, _t, blocking = tolerance.evaluate(other_field, 0)
    assert not ok


@pytest.mark.parametrize("version", ["2.1.292", "2.1.296"])
def test_shipped_tree_on_new_cli_tolerates_only_the_known_findings(version):
    ok, tolerated, blocking = tolerance.evaluate(_sample(f"v{version}-shipped-tree.txt"), 1)
    assert ok, blocking
    assert sorted(tolerated) == [
        "marketplace-reserved-name",
        "plugin-json-reserved-name",
        "root-claude-md-warning",
    ]


@pytest.mark.parametrize("version", ["2.1.218", "2.1.292", "2.1.296"])
def test_injected_extra_errors_fail_on_every_validator_version(version):
    ok, _tolerated, blocking = tolerance.evaluate(_sample(f"v{version}-injected-errors.txt"), 1)
    assert not ok
    assert any("plugins.0.source: Invalid input" in item for item in blocking)


def test_injected_errors_are_all_named_on_new_cli():
    ok, tolerated, blocking = tolerance.evaluate(_sample("v2.1.296-injected-errors.txt"), 1)
    assert not ok
    joined = "\n".join(blocking)
    for needle in (
        "plugins.0.source",
        "version: Invalid input: expected string",
        "keywords: Invalid input: expected array",
        "skills/blog-write/SKILL.md: frontmatter",
        "agents/blog-writer.md: frontmatter",
    ):
        assert needle in joined, needle
    # The reserved-name findings sit in the same output and stay tolerated.
    assert "marketplace-reserved-name" in tolerated
    assert not any("is reserved" in item for item in blocking)


def _shipped_with(extra: str) -> str:
    return _sample("v2.1.296-shipped-tree.txt").replace("\n✘ Validation failed", extra + "\n✘ Validation failed")


def test_unknown_warning_class_fails():
    extra = (
        "\nValidating skill: /home/runner/work/claude-blog/claude-blog/skills/blog/SKILL.md\n\n"
        "⚠ Found 1 warning:\n\n  ❯ description: Description is very long\n"
    )
    ok, _tolerated, blocking = tolerance.evaluate(_shipped_with(extra), 1)
    assert not ok and any("description: Description is very long" in item for item in blocking)


def test_reserved_name_for_another_plugin_is_not_tolerated():
    text = _sample("v2.1.296-shipped-tree.txt").replace(
        'Plugin name "claude-blog" is reserved', 'Plugin name "claude-other" is reserved'
    )
    ok, _tolerated, blocking = tolerance.evaluate(text, 1)
    assert not ok and sum("claude-other" in item for item in blocking) == 2


def test_reserved_name_on_a_different_field_is_not_tolerated():
    text = _sample("v2.1.296-shipped-tree.txt").replace("  ❯ name: Plugin name", "  ❯ displayName: Plugin name")
    ok, _tolerated, blocking = tolerance.evaluate(text, 1)
    assert not ok and any("displayName" in item for item in blocking)


def test_a_third_reserved_name_occurrence_fails():
    extra = (
        "\nValidating plugin: /home/runner/work/claude-blog/claude-blog/.claude-plugin/plugin.json\n\n"
        '✘ Found 1 error:\n\n  ❯ name: Plugin name "claude-blog" is reserved: again\n'
    )
    ok, _tolerated, blocking = tolerance.evaluate(_shipped_with(extra), 1)
    assert not ok and any(item.startswith("duplicate of a tolerated finding") for item in blocking)


def test_error_count_mismatch_fails():
    text = _sample("v2.1.296-shipped-tree.txt").replace("Found 1 error:", "Found 2 errors:", 1)
    ok, _tolerated, blocking = tolerance.evaluate(text, 1)
    assert not ok and any("announced 2 error(s) but 1 were parsed" in item for item in blocking)


def test_nonzero_exit_with_unparseable_output_fails():
    ok, _tolerated, blocking = tolerance.evaluate("something went wrong\n", 1)
    assert not ok and any("no error block could be parsed" in item for item in blocking)


def test_ansi_colors_do_not_hide_findings():
    text = _sample("v2.1.296-shipped-tree.txt").replace("✘ Found", "\x1b[31m✘ Found").replace("error:", "error:\x1b[0m")
    ok, _tolerated, blocking = tolerance.evaluate(text, 1)
    assert ok, blocking


def test_cli_entrypoint_exit_codes(tmp_path):
    def run(sample: str, code: int) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-I", str(SCRIPT), "--from-file", str(SAMPLES / sample), "--exit-code", str(code)],
            capture_output=True, text=True, check=False,
        )

    assert run("v2.1.296-shipped-tree.txt", 1).returncode == 0
    assert run("v2.1.218-shipped-tree.txt", 0).returncode == 0
    failing = run("v2.1.292-injected-errors.txt", 1)
    assert failing.returncode == 1 and "plugins.0.source" in failing.stderr


def test_cli_runs_the_validator_and_propagates_a_failing_stub(tmp_path):
    stub = tmp_path / "claude"
    stub.write_text(
        "#!/bin/sh\ncat <<'EOF'\nValidating marketplace manifest: /x/marketplace.json\n\n"
        "✘ Found 1 error:\n\n  ❯ plugins.0.source: Invalid input\n\n✘ Validation failed\nEOF\nexit 1\n",
        encoding="utf-8",
    )
    stub.chmod(0o755)
    result = subprocess.run(
        [sys.executable, "-I", str(SCRIPT), "--cli", str(stub), "--root", str(tmp_path)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 1 and "plugins.0.source: Invalid input" in result.stderr


def test_workflow_uses_the_wrapper_for_every_validator_version():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert ".github/scripts/validate_plugin_tolerate_reserved_name.py" in workflow
    assert "claude plugin validate ." not in workflow
    assert '"2.1.218", "2.1.292"' in workflow
