"""install.sh refuses unsafe git inputs before it runs git.

The wrapper clones the repository when it is piped to bash. CLAUDE_BLOG_REPO,
CLAUDE_BLOG_REF and CLAUDE_BLOG_URL reach git, so they must be plain names:
the same rules install.ps1 applies. These cases all fail before any network
or git call, so they run offline.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
INSTALL = ROOT / "install.sh"


def _run_piped(tmp_path: Path, **env_overrides: str) -> subprocess.CompletedProcess[str]:
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    # A PATH git that fails loudly proves the validation runs first.
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir(exist_ok=True)
    marker = tmp_path / "git-was-called"
    git = fake_bin / "git"
    git.write_text(f"#!/bin/sh\necho called > '{marker}'\nexit 1\n", encoding="utf-8")
    git.chmod(0o755)
    env = dict(os.environ, HOME=str(home), CLAUDE_BLOG_SKIP_PIP="1")
    env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"
    for key in ("CLAUDE_BLOG_REPO", "CLAUDE_BLOG_REF", "CLAUDE_BLOG_URL"):
        env.pop(key, None)
    env.update(env_overrides)
    result = subprocess.run(
        ["bash"],
        input=INSTALL.read_text(encoding="utf-8"),
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )
    result.git_called = marker.exists()  # type: ignore[attr-defined]
    return result


@pytest.mark.parametrize(
    ("variable", "value", "message"),
    [
        ("CLAUDE_BLOG_REF", "--upload-pack=touch /tmp/x", "CLAUDE_BLOG_REF"),
        ("CLAUDE_BLOG_REF", "-main", "CLAUDE_BLOG_REF"),
        ("CLAUDE_BLOG_REF", "a..b", "CLAUDE_BLOG_REF"),
        ("CLAUDE_BLOG_REF", "topic/", "CLAUDE_BLOG_REF"),
        ("CLAUDE_BLOG_REF", "release.lock", "CLAUDE_BLOG_REF"),
        ("CLAUDE_BLOG_REPO", "not-a-repo", "CLAUDE_BLOG_REPO"),
        ("CLAUDE_BLOG_REPO", "-x/evil", "CLAUDE_BLOG_REPO"),
        ("CLAUDE_BLOG_URL", "--upload-pack=sh", "CLAUDE_BLOG_URL"),
        ("CLAUDE_BLOG_URL", "ext::sh -c id", "CLAUDE_BLOG_URL"),
        ("CLAUDE_BLOG_URL", "fd::3", "CLAUDE_BLOG_URL"),
    ],
)
def test_unsafe_git_inputs_are_refused_before_git_runs(tmp_path, variable, value, message):
    result = _run_piped(tmp_path, **{variable: value})
    assert result.returncode != 0
    assert message in result.stderr
    assert not result.git_called
