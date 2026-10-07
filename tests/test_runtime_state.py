"""Offline runtime continuity, explicit setup and owned-data boundaries."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path, PureWindowsPath
import re
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
INTEGRATIONS = ("blog-audio", "blog-google", "blog-notebooklm")


@pytest.fixture(autouse=True)
def isolated_runtime_override(monkeypatch):
    monkeypatch.delenv("CLAUDE_BLOG_RUNTIME_DIR", raising=False)


def load_paths():
    spec = importlib.util.spec_from_file_location("runtime_paths_fixture", ROOT / "skills/blog-notebooklm/scripts/runtime_paths.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install_copy(tmp_path, integration, version):
    skill = tmp_path / f"plugin {version}" / "skills" / integration
    shutil.copytree(ROOT / "skills" / integration / "scripts", skill / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    (skill / "scripts/probe.py").write_text("import json,os,sys\nprint(json.dumps({'args':sys.argv[1:],'runtime':os.environ.get('CLAUDE_BLOG_RUNTIME_DIR')}))")
    return skill


def child(skill, code, runtime=None, cwd=None):
    env = dict(os.environ)
    env.pop("CLAUDE_BLOG_RUNTIME_DIR", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    if runtime is not None:
        env["CLAUDE_BLOG_RUNTIME_DIR"] = str(runtime)
    prefix = f"import sys; sys.path.insert(0,{str(skill / 'scripts')!r}); "
    return subprocess.run([sys.executable, "-c", prefix + code], cwd=cwd or skill, env=env, capture_output=True, text=True)


def configure_interpreter(venv):
    interpreter = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    interpreter.parent.mkdir(parents=True)
    try:
        interpreter.symlink_to(sys.executable)
    except OSError:
        shutil.copy2(sys.executable, interpreter)
    return interpreter


def test_shipped_runtime_resolvers_are_identical():
    contents = [(ROOT / "skills" / name / "scripts/runtime_paths.py").read_bytes() for name in INTEGRATIONS]
    assert contents[0] == contents[1] == contents[2]


@pytest.mark.parametrize("integration", INTEGRATIONS)
def test_default_is_legacy_skill_local_and_version_bound(tmp_path, integration):
    paths = load_paths()
    first = install_copy(tmp_path, integration, "v1")
    second = install_copy(tmp_path, integration, "v2")
    one = paths.resolve_runtime_paths(first, integration)
    two = paths.resolve_runtime_paths(second, integration)
    assert one.venv == first / ".venv"
    assert one.data == first / "data"
    assert one.venv != two.venv and one.data != two.data
    assert not one.venv.exists() and not one.data.exists()


@pytest.mark.parametrize("integration", INTEGRATIONS)
def test_two_plugin_versions_share_opted_in_environment_without_setup(tmp_path, integration):
    first = install_copy(tmp_path, integration, "v1")
    second = install_copy(tmp_path, integration, "v2")
    runtime = tmp_path / "persistent root with spaces"
    venv = runtime / integration / ".venv"
    configure_interpreter(venv)
    source = first / "scripts/requirements.lock"
    (venv / ".requirements.stamp").write_text(hashlib.sha256(source.read_bytes()).hexdigest())
    # Poisoning CWD cannot replace either the runner target or its path helper.
    cwd = tmp_path / "consumer"
    cwd.mkdir()
    (cwd / "runtime_paths.py").write_text("raise AssertionError('POISON CWD')")
    for skill in (first, second):
        result = child(skill, "import run; sys.argv=['run.py','probe.py','unchanged-argument']; run.main()", runtime, cwd)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout) == {"args": ["unchanged-argument"], "runtime": str(runtime)}
        assert not (skill / ".venv").exists() and not (skill / "data").exists()


@pytest.mark.parametrize("integration", INTEGRATIONS)
def test_ordinary_runner_and_check_do_not_create_missing_runtime(tmp_path, integration):
    skill = install_copy(tmp_path, integration, "v1")
    runtime = tmp_path / "absent persistent root"
    result = child(skill, "import run; sys.argv=['run.py','probe.py']; run.main()", runtime)
    assert result.returncode == 1
    assert "setup required" in (result.stdout + result.stderr).lower()
    check = child(skill, "import setup_environment as setup; sys.argv=['setup_environment.py','--check','--json']; sys.exit(setup.main() or 0)", runtime)
    assert check.returncode == 1
    assert json.loads(check.stdout)
    assert not runtime.exists()
    assert not (skill / ".venv").exists()


@pytest.mark.parametrize("integration", INTEGRATIONS)
def test_explicit_setup_uses_same_persistent_root_as_runner_offline(tmp_path, integration):
    skill = install_copy(tmp_path, integration, "v1")
    runtime = tmp_path / "persistent setup root"
    # Stub only package/browser installation. Setup and its stamp/path logic
    # execute unchanged; no network, real venv install or browser is launched.
    code = '''
import setup_environment as setup
from pathlib import Path
from types import SimpleNamespace
created=[]
calls=[]
def fake_create(path, **kwargs):
    created.append(str(path))
    Path(path).mkdir(parents=True)
def fake_run(command, **kwargs):
    calls.append(command)
    return SimpleNamespace(returncode=0)
setup.venv.create=fake_create
setup.subprocess.run=fake_run
env=setup.SkillEnvironment()
assert env.ensure_venv()
import run,json
print('RESULT:'+json.dumps({'created':created,'venv':str(env.venv_dir),'runner':str(run.get_venv_python()),'setup_python':str(env.venv_python),'calls':calls}))
'''
    result = child(skill, code, runtime)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout.split("RESULT:", 1)[1])
    assert payload["created"] == [str(runtime / integration / ".venv")]
    assert payload["runner"] == payload["setup_python"]
    assert payload["calls"]
    assert all(str(runtime / integration / ".venv") in str(command[0]) for command in payload["calls"])
    assert not (skill / ".venv").exists()


@pytest.mark.parametrize("raw", ["", "relative", "../state", "~/state", "${CLAUDE_PLUGIN_DATA}/state", "/tmp/$UNRESOLVED", "/tmp/%UNRESOLVED%", "/tmp/../state", " /absolute"])
def test_invalid_overrides_fail_without_writes(tmp_path, monkeypatch, raw):
    paths = load_paths()
    monkeypatch.setenv("CLAUDE_BLOG_RUNTIME_DIR", raw)
    with pytest.raises(ValueError):
        paths.resolve_runtime_paths(tmp_path / "blog-notebooklm", "blog-notebooklm")
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("integration", INTEGRATIONS)
def test_invalid_cli_root_refused_by_setup_and_runner(tmp_path, integration):
    skill = install_copy(tmp_path, integration, "v1")
    for code in ("import run; sys.argv=['run.py','probe.py']; run.main()", "import setup_environment as setup; sys.argv=['setup_environment.py','--check','--json']; sys.exit(setup.main() or 0)"):
        result = child(skill, code, "relative-state")
        assert result.returncode == 1
        assert "CLAUDE_BLOG_RUNTIME_DIR" in result.stdout
        assert not (skill / "relative-state").exists()
        assert not (skill / ".venv").exists()


@pytest.mark.parametrize("raw", ["C:/Users/Writer/Persistent State", r"C:\Users\Writer\Persistent State", r"\\server\share\Persistent State"])
def test_windows_native_path_anchors_accept_absolute_roots(raw):
    assert load_paths().validate_absolute_override(raw, PureWindowsPath).is_absolute()


@pytest.mark.parametrize("raw", [r"C:relative", r"\rooted-without-drive", r"..\state", r"C:\Users\..\state"])
def test_windows_drive_relative_and_parent_paths_are_rejected(raw):
    with pytest.raises(ValueError):
        load_paths().validate_absolute_override(raw, PureWindowsPath)


def test_notebook_config_library_auth_and_cleanup_share_cross_version_state(tmp_path):
    first = install_copy(tmp_path, "blog-notebooklm", "v1")
    second = install_copy(tmp_path, "blog-notebooklm", "v2")
    runtime = tmp_path / "persistent notebook state"
    data = runtime / "blog-notebooklm/data"
    data.mkdir(parents=True)
    (data / "library.json").write_text(json.dumps({"notebooks": {"fixture": {"name": "Fixture"}}, "active_notebook_id": "fixture"}))
    (data / "auth_info.json").write_text('{"fixture":true}')
    (data / "browser_state").mkdir()
    (data / "browser_state/state.json").write_text('{"cookies":[]}')
    (data / "browser_state/browser_profile").mkdir()
    (data / "browser_state/browser_profile/fixture").write_text("profile fixture")
    for skill in (first, second):
        code = '''
import config,notebook_manager,auth_manager,cleanup_manager,json
library=notebook_manager.NotebookLibrary()
auth=auth_manager.AuthManager()
cleanup=cleanup_manager.CleanupManager()
assert library.library_file==config.LIBRARY_FILE
assert auth.auth_info_file==config.AUTH_INFO_FILE
assert auth.state_file==config.STATE_FILE
assert cleanup.data_dir==config.DATA_DIR==library.data_dir
assert 'fixture' in library.notebooks
assert auth.is_authenticated()
preview=cleanup.perform_cleanup(preserve_library=True,dry_run=True)
print('RESULT:'+json.dumps({'data':str(config.DATA_DIR),'preview':preview}))
'''
        result = child(skill, code, runtime)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout.split("RESULT:", 1)[1])["data"] == str(data)
    venv = runtime / "blog-notebooklm/.venv"
    venv.mkdir()
    (venv / "keep").write_text("environment")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep").write_text("unrelated state")
    (data / "outside-link").symlink_to(outside, target_is_directory=True)
    result = child(second, "import cleanup_manager,json; result=cleanup_manager.CleanupManager().perform_cleanup(preserve_library=True); print('RESULT:'+json.dumps(result))", runtime)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout.split("RESULT:", 1)[1])["failed_count"] == 0
    assert (data / "library.json").exists()
    assert not (data / "auth_info.json").exists()
    assert not (data / "browser_state/state.json").exists()
    assert not (data / "outside-link").exists()
    assert (outside / "keep").read_text() == "unrelated state"
    assert (venv / "keep").read_text() == "environment"


@pytest.mark.parametrize("linked_part", ["blog-notebooklm", "blog-notebooklm/data", "blog-notebooklm/.venv"])
def test_managed_runtime_symlink_roots_are_refused(tmp_path, monkeypatch, linked_part):
    runtime = tmp_path / "persistent"
    outside = tmp_path / "outside"
    outside.mkdir()
    link = runtime / linked_part
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(outside, target_is_directory=True)
    monkeypatch.setenv("CLAUDE_BLOG_RUNTIME_DIR", str(runtime))
    with pytest.raises(ValueError, match="symlink"):
        load_paths().resolve_runtime_paths(tmp_path / "source/blog-notebooklm", "blog-notebooklm")
    assert list(outside.iterdir()) == []


def test_cleanup_refuses_data_root_replaced_after_resolution(tmp_path):
    skill = install_copy(tmp_path, "blog-notebooklm", "v1")
    runtime = tmp_path / "persistent"
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep").write_text("unrelated state")
    code = f'''
import cleanup_manager
from pathlib import Path
cleanup=cleanup_manager.CleanupManager()
cleanup.data_dir.parent.mkdir(parents=True)
cleanup.data_dir.symlink_to({str(outside)!r},target_is_directory=True)
try:
    cleanup.perform_cleanup()
except ValueError as exc:
    assert 'symlink' in str(exc)
else:
    raise AssertionError('cleanup followed a changed root')
'''
    result = child(skill, code, runtime)
    assert result.returncode == 0, result.stderr
    assert (outside / "keep").read_text() == "unrelated state"


def test_legacy_package_helper_is_nonmutating_and_requires_explicit_setup(tmp_path):
    skill = install_copy(tmp_path, "blog-notebooklm", "v1")
    runtime = tmp_path / "missing runtime"
    code = f"import runpy; module=runpy.run_path({str(skill / 'scripts/__init__.py')!r}); module['ensure_venv_and_run']()"
    result = child(skill, code, runtime)
    assert result.returncode == 1
    assert "setup required" in result.stdout.lower()
    assert not runtime.exists()


def test_runtime_documentation_passes_host_data_explicitly():
    for name in INTEGRATIONS:
        text = (ROOT / "skills" / name / "SKILL.md").read_text()
        assert "CLAUDE_BLOG_RUNTIME_DIR='${CLAUDE_PLUGIN_DATA}/claude-blog-runtime'" in text
        assert "not an exported shell variable" in text
        assert "No state is" in text and "copied or migrated automatically" in text
    for name in ("blog-decay", "blog-geo", "blog-seo-check"):
        text = (ROOT / "skills" / name / "SKILL.md").read_text()
        assert "Propagate the same absolute `CLAUDE_BLOG_RUNTIME_DIR`" in text
        assert "${CLAUDE_PLUGIN_DATA}/claude-blog-runtime" in text
        assert "standalone use with no override, omit the variable" in text


@pytest.mark.parametrize("integration", INTEGRATIONS)
def test_documented_plugin_runner_passes_resolved_persistent_path(tmp_path, integration):
    skill = install_copy(tmp_path, integration, "v1")
    host_data = tmp_path / "host plugin data with spaces"
    runtime = host_data / "claude-blog-runtime"
    venv = runtime / integration / ".venv"
    configure_interpreter(venv)
    source = skill / "scripts/requirements.lock"
    (venv / ".requirements.stamp").write_text(hashlib.sha256(source.read_bytes()).hexdigest())
    target = {"blog-audio": "generate_audio.py", "blog-google": "google_auth.py", "blog-notebooklm": "notebook_manager.py"}[integration]
    (skill / "scripts" / target).write_text("import os\nprint(os.environ['CLAUDE_BLOG_RUNTIME_DIR'])")
    text = (ROOT / "skills" / integration / "SKILL.md").read_text()
    block = next(block for block in re.findall(r"```bash\n(.*?)\n```", text, re.S) if "CLAUDE_BLOG_RUNTIME_DIR='${CLAUDE_PLUGIN_DATA}" in block)
    command = block.splitlines()[1]
    env = dict(os.environ)
    env.pop("CLAUDE_PLUGIN_DATA", None)
    env.pop("CLAUDE_SKILL_DIR", None)
    env.pop("CLAUDE_BLOG_RUNTIME_DIR", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    rendered = command.replace("${CLAUDE_PLUGIN_DATA}", str(host_data)).replace("${CLAUDE_SKILL_DIR}", str(skill))
    result = subprocess.run(["bash", "-c", rendered], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == str(runtime)
    unresolved = command.replace("${CLAUDE_SKILL_DIR}", str(skill))
    result = subprocess.run(["bash", "-c", unresolved], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert result.returncode == 1
    assert "CLAUDE_BLOG_RUNTIME_DIR" in result.stdout


@pytest.mark.parametrize("integration", ["blog-google", "blog-notebooklm"])
def test_new_version_stale_dependencies_require_setup_without_modifying_state(tmp_path, integration):
    skill = install_copy(tmp_path, integration, "v2")
    runtime = tmp_path / "persistent"
    venv = runtime / integration / ".venv"
    configure_interpreter(venv)
    (venv / ".requirements.stamp").write_text("previous-version-stamp")
    state = runtime / integration / "data"
    state.mkdir()
    (state / "keep").write_text("existing user state")
    result = child(skill, "import run; sys.argv=['run.py','probe.py']; run.main()", runtime)
    assert result.returncode == 1
    assert "missing or stale" in result.stdout
    assert (venv / ".requirements.stamp").read_text() == "previous-version-stamp"
    assert (state / "keep").read_text() == "existing user state"


def test_null_byte_override_is_rejected():
    with pytest.raises(ValueError):
        load_paths().validate_absolute_override("abc\x00def")
