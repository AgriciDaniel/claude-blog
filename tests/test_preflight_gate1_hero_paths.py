"""Gate 1 hero paths, project-root context files and the --no-strict warning.

Free hero paths: a valid local hero, a stock key, a reachable Openverse.
Paid paths (live Banana MCP, Gemini key) need the user's consent, so Openverse
is probed whenever no other free path exists. Gate 1 passes with any free
path, passes with only paid paths (``paid_only`` plus a cost warning), and
blocks only when there is no path at all. The Openverse probe is
monkeypatched everywhere here; no test touches the network.
"""
from __future__ import annotations

import json
import socket
import struct
import sys
import time
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import blog_preflight as preflight  # noqa: E402

KEYS = ("GOOGLE_AI_API_KEY", "GEMINI_API_KEY", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "PIXABAY_API_KEY")


def _png(width: int, height: int) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + b"\x80" * (width * 3) for _ in range(height))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


@pytest.fixture
def offline(monkeypatch, tmp_path):
    """No keys, an unreachable Openverse, and a record of probe calls."""
    for key in KEYS:
        monkeypatch.delenv(key, raising=False)
    calls: list[int] = []

    def unreachable(*_args, **_kwargs):
        calls.append(1)
        return False

    monkeypatch.setattr(preflight, "_openverse_reachable", unreachable)
    monkeypatch.setenv(preflight.REVIEW_STATE_ENV, str(tmp_path / "state"))
    draft = tmp_path / "draft"
    draft.mkdir()
    return draft, calls


def _gate1(draft, **kwargs):
    kwargs.setdefault("project_dir", draft.parent)
    return preflight.gate_1_capability_discovery(draft, **kwargs)


def test_no_hero_path_blocks_with_the_contract_message(offline):
    draft, calls = offline
    result = _gate1(draft)
    assert not result["passed"]
    assert preflight.NO_HERO_PATH_MESSAGE in result["violations"]
    assert result["violations"][0].startswith("Hero image required but no generation path available.")
    assert calls == [1]
    paths = result["capabilities"]["hero_paths"]
    assert paths["openverse_reachable"] is False and result["capabilities"]["image_gen_path_available"] is False
    assert "openverse_assumed_available" not in result["capabilities"]


def test_reachable_openverse_is_a_hero_path(offline, monkeypatch):
    draft, _calls = offline
    monkeypatch.setattr(preflight, "_openverse_reachable", lambda *a, **k: True)
    result = _gate1(draft)
    assert result["passed"], result["violations"]
    assert result["capabilities"]["hero_paths"]["openverse_reachable"] is True


def test_valid_local_hero_is_a_path_and_skips_the_probe(offline):
    draft, calls = offline
    (draft / "hero.png").write_bytes(_png(1200, 630))
    result = _gate1(draft)
    assert result["passed"], result["violations"]
    assert result["capabilities"]["hero_paths"]["local_hero"] == "hero.png"
    assert result["capabilities"]["hero_paths"]["openverse_reachable"] is None
    assert calls == []


@pytest.mark.parametrize("content", [None, b"not an image", "1199"])
def test_too_small_or_broken_local_hero_does_not_count(offline, content):
    draft, _calls = offline
    data = {None: _png(40, 20), "1199": _png(1199, 630)}.get(content, content)
    (draft / "hero.png").write_bytes(data)
    result = _gate1(draft)
    assert not result["passed"]
    assert result["capabilities"]["hero_paths"]["local_hero"] is None


def test_uppercase_hero_name_does_not_count(offline):
    draft, _calls = offline
    (draft / "hero.PNG").write_bytes(_png(1200, 630))
    if (draft / "hero.png").exists():
        pytest.skip("case-insensitive filesystem")
    assert _gate1(draft)["capabilities"]["hero_paths"]["local_hero"] is None


def test_the_hero_the_renderer_would_use_decides(offline):
    """Renderer order is png, jpg, jpeg, webp; the first present file alone counts."""
    draft, _calls = offline
    (draft / "hero.webp").write_bytes(b"junk")
    (draft / "hero.png").write_bytes(_png(1200, 630))
    assert _gate1(draft)["capabilities"]["hero_paths"]["local_hero"] == "hero.png"
    (draft / "hero.png").write_bytes(_png(600, 315))
    (draft / "hero.jpg").write_bytes(b"also junk")
    assert _gate1(draft)["capabilities"]["hero_paths"]["local_hero"] is None


def test_gate_1_and_gate_2_agree_on_a_hero_below_the_minimum(offline):
    draft, _calls = offline
    (draft / "hero.png").write_bytes(_png(1000, 600))
    assert _gate1(draft)["capabilities"]["hero_paths"]["local_hero"] is None
    problems, _evidence = preflight._hero_check(draft / "hero.png", (draft / "hero.png").read_bytes())
    assert problems


def test_symlinked_local_hero_does_not_count(offline, tmp_path):
    draft, _calls = offline
    real = tmp_path / "elsewhere.png"
    real.write_bytes(_png(1200, 630))
    (draft / "hero.png").symlink_to(real)
    assert not _gate1(draft)["passed"]


@pytest.mark.parametrize("key", ["UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "PIXABAY_API_KEY"])
def test_stock_key_is_a_path_and_skips_the_probe(offline, monkeypatch, key):
    draft, calls = offline
    monkeypatch.setenv(key, "your-test-key")
    result = _gate1(draft)
    assert result["passed"], result["violations"]
    assert result["capabilities"]["hero_paths"]["stock_api"] is True
    assert calls == []
    assert not any("paid" in w for w in result["warnings"])


@pytest.mark.parametrize("key", ["GOOGLE_AI_API_KEY", "GEMINI_API_KEY"])
def test_gemini_key_alone_is_paid_only_and_still_probes_openverse(offline, monkeypatch, key):
    draft, calls = offline
    monkeypatch.setenv(key, "your-test-key")
    result = _gate1(draft)
    assert result["passed"], result["violations"]
    assert result["capabilities"]["env_keys_present"][key] is True
    paths = result["capabilities"]["hero_paths"]
    assert paths["gemini_api"] == {"available": True, "paid": True, "requires_consent": True}
    assert paths["paid_only"] is True and paths["free_path"] is False
    assert any(w.startswith("paid_only:") and "approve the cost" in w and "--allow-paid" in w
               for w in result["warnings"])
    assert calls == [1], "a paid key must not skip the free Openverse probe"


def test_live_banana_tool_alone_is_paid_only(offline):
    draft, calls = offline
    result = _gate1(draft, live_tools=["mcp__nanobanana__gemini_generate_image"])
    assert result["passed"], result["violations"]
    assert result["capabilities"]["hero_paths"]["paid_only"] is True
    assert any("Banana MCP" in w and "approve the cost" in w for w in result["warnings"])
    assert calls == [1]


def test_paid_key_with_reachable_openverse_is_not_paid_only(offline, monkeypatch):
    draft, _calls = offline
    monkeypatch.setenv("GEMINI_API_KEY", "your-test-key")
    monkeypatch.setattr(preflight, "_openverse_reachable", lambda *a, **k: True)
    result = _gate1(draft)
    assert result["passed"]
    assert result["capabilities"]["hero_paths"]["paid_only"] is False
    assert not any(w.startswith("paid_only:") for w in result["warnings"])


def test_capability_file_never_holds_key_values(offline, monkeypatch):
    draft, _calls = offline
    monkeypatch.setenv("GEMINI_API_KEY", "secret-value-must-not-appear")
    _gate1(draft)
    assert "secret-value-must-not-appear" not in (draft / "capabilities.json").read_text()


# --- The Openverse probe itself ---------------------------------------------


def test_probe_constants_are_https_and_at_most_three_seconds():
    assert preflight.OPENVERSE_PROBE_URL.startswith("https://api.openverse.org/")
    assert preflight.OPENVERSE_PROBE_TIMEOUT <= 3


def test_probe_total_time_is_bounded(monkeypatch):
    monkeypatch.setattr(preflight, "_openverse_probe_once", lambda *_a: time.sleep(5) or True)
    started = time.monotonic()
    assert preflight._openverse_reachable(timeout=0.2) is False
    assert time.monotonic() - started < 1.5


def test_probe_errors_count_as_unreachable(monkeypatch):
    def boom(*_a):
        raise OSError("down")
    monkeypatch.setattr(preflight, "_openverse_probe_once", boom)
    assert preflight._openverse_reachable(timeout=0.5) is False


def test_probe_refuses_plain_http_before_any_lookup(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: pytest.fail("no DNS lookup for http"))
    assert preflight._openverse_probe_once("http://api.openverse.org/v1/images/", 1) is False


def test_probe_refuses_non_public_addresses(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))])
    monkeypatch.setattr(preflight, "_PinnedHTTPSConnection", lambda *a, **k: pytest.fail("must not connect"))
    assert preflight._openverse_probe_once(preflight.OPENVERSE_PROBE_URL, 1) is False


@pytest.mark.parametrize("status,reachable", [(200, True), (301, False), (302, False), (403, False), (503, False)])
def test_probe_counts_only_a_direct_2xx(monkeypatch, status, reachable):
    public = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: public)
    seen = {}

    class FakeConnection:
        def __init__(self, host, address, port, timeout):
            seen.update(host=host, address=address, port=port, timeout=timeout)

        def request(self, method, target, headers):
            seen.update(method=method, target=target)

        def getresponse(self):
            return type("R", (), {"status": status})()

        def close(self):
            seen["closed"] = True

    monkeypatch.setattr(preflight, "_PinnedHTTPSConnection", FakeConnection)
    assert preflight._openverse_probe_once(preflight.OPENVERSE_PROBE_URL, 2) is reachable
    assert seen["host"] == "api.openverse.org" and seen["address"] == "93.184.216.34" and seen["port"] == 443
    assert seen["method"] == "HEAD" and seen["target"].startswith("/v1/images/") and seen["closed"]


# --- BRAND.md, VOICE.md, DISCOURSE.md come from the user's project ----------


def _context_files(result):
    return result["capabilities"]["project_root_files"]


def test_context_files_are_read_from_the_given_project_dir(offline, tmp_path):
    draft, _calls = offline
    project = tmp_path / "site"
    project.mkdir()
    (project / "BRAND.md").write_text("brand")
    (project / "DISCOURSE.md").write_text("discourse")
    files = _context_files(_gate1(draft, project_dir=project))
    assert files == {"BRAND.md": True, "VOICE.md": False, "DISCOURSE.md": True}


def test_main_uses_project_root_for_context_files(offline, monkeypatch, tmp_path):
    draft, _calls = offline
    (tmp_path / "VOICE.md").write_text("voice")
    elsewhere = tmp_path / "cwd"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    monkeypatch.setattr(sys, "argv", ["blog_preflight.py", "--draft", str(draft), "--gate", "1",
                                      "--no-strict", "--project-root", str(tmp_path)])
    preflight.main()
    capabilities = json.loads((draft / "capabilities.json").read_text())
    assert capabilities["project_root_files"]["VOICE.md"] is True
    assert capabilities["project_root"] == str(tmp_path.resolve())


def test_main_defaults_to_the_current_directory_not_the_install_root(offline, monkeypatch, tmp_path):
    draft, _calls = offline
    cwd = tmp_path / "user-project"
    cwd.mkdir()
    (cwd / "BRAND.md").write_text("brand")
    monkeypatch.chdir(cwd)
    monkeypatch.setattr(sys, "argv", ["blog_preflight.py", "--draft", str(draft), "--gate", "1", "--no-strict"])
    preflight.main()
    capabilities = json.loads((draft / "capabilities.json").read_text())
    assert capabilities["project_root_files"]["BRAND.md"] is True
    assert capabilities["project_root"] == str(cwd)


# --- --no-strict prints the contract's bypass warning in every mode ----------


def _contract_warning() -> str:
    text = (ROOT / "skills/blog/references/blog-delivery-contract.md").read_text(encoding="utf-8")
    block = text[text.index("## Bypass Mechanism"):]
    return block[block.index("```\n") + 4:block.index("\n```", block.index("```\n") + 4)]


def _stub_gates(monkeypatch, failing):
    names = ("gate_1_capability_discovery", "gate_2_format_completeness", "gate_3_visual_verification",
             "gate_4_content_review", "gate_5_asset_link_integrity")
    for n, name in enumerate(names, 1):
        def gate(_draft, n=n, **_kwargs):
            return preflight._gate_result(n, preflight.GATE_NAMES[n], n not in failing,
                                          ["fixture"] if n in failing else [])
        monkeypatch.setattr(preflight, name, gate)


@pytest.mark.parametrize("json_mode", [False, True])
def test_bypass_warning_matches_the_contract_text(offline, monkeypatch, capsys, json_mode):
    draft, _calls = offline
    _stub_gates(monkeypatch, {3, 5})
    argv = ["blog_preflight.py", "--draft", str(draft), "--no-strict", "--diagnostics-all"]
    if json_mode:
        argv.append("--json")
    monkeypatch.setattr(sys, "argv", argv)
    assert preflight.main() == 0
    out = capsys.readouterr()
    expected = _contract_warning()
    assert "Failed gates: [Gate 3, Gate 5]." in expected
    assert expected in out.err
    assert "WARNING" not in out.out
    if json_mode:
        json.loads(out.out)


def test_no_bypass_warning_when_nothing_failed_or_strict(offline, monkeypatch, capsys):
    draft, _calls = offline
    _stub_gates(monkeypatch, set())
    monkeypatch.setattr(sys, "argv", ["blog_preflight.py", "--draft", str(draft), "--no-strict", "--json"])
    assert preflight.main() == 0
    assert "bypassed" not in capsys.readouterr().err
    _stub_gates(monkeypatch, {2})
    monkeypatch.setattr(sys, "argv", ["blog_preflight.py", "--draft", str(draft), "--json"])
    assert preflight.main() == 1
    assert "bypassed" not in capsys.readouterr().err


def test_project_root_help_matches_the_recorded_path():
    import subprocess
    text = " ".join(subprocess.run([sys.executable, str(ROOT / "scripts/blog_preflight.py"), "--help"],
                                   capture_output=True, text=True, check=True).stdout.split())
    assert "as given" not in text
    assert "absolute path" in text and "symlinks not resolved" in text
