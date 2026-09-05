"""Tests for scripts/blog_hygiene.py (optional deterministic hygiene helper)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import blog_hygiene as bh  # noqa: E402


def test_lazy_loading_added_once_and_idempotent() -> None:
    html = '<p><img src="a.png" alt="A"><img src="b.png" alt="B" loading="eager"></p>'
    out, n = bh.fix_html_lazy_loading(html)
    assert n == 1
    assert 'src="a.png" alt="A"' in out and 'loading="lazy"' in out
    # already-eager image is left untouched
    assert out.count('loading="eager"') == 1
    # idempotent: second pass changes nothing
    out2, n2 = bh.fix_html_lazy_loading(out)
    assert n2 == 0 and out2 == out


def test_missing_alt_reported_not_invented() -> None:
    html = '<img src="x.png"><img src="y.png" alt="ok">'
    missing = bh.find_missing_alt(html)
    assert missing == ["x.png"]


def test_toc_inserted_only_for_long_multi_h2_posts() -> None:
    body = "## First\n\n" + ("word " * 2100) + "\n\n## Second\n\nmore\n"
    md = "---\ntitle: t\n---\n" + body
    out, inserted = bh.insert_toc(md, min_words=2000)
    assert inserted
    assert bh.TOC_BEGIN in out and "- [First](#first)" in out and "- [Second](#second)" in out
    # TOC sits before the first H2
    assert out.index(bh.TOC_BEGIN) < out.index("## First")
    # idempotent
    out2, inserted2 = bh.insert_toc(out, min_words=2000)
    assert not inserted2 and out2 == out


def test_toc_skipped_when_short_or_single_heading() -> None:
    short = "---\nt: 1\n---\n## Only\n\nshort body\n"
    _, inserted = bh.insert_toc(short, min_words=2000)
    assert not inserted
    long_one_h2 = "---\nt: 1\n---\n## Only\n\n" + ("word " * 2100)
    _, inserted2 = bh.insert_toc(long_one_h2, min_words=2000)
    assert not inserted2


def test_h2_extraction_skips_code_fences() -> None:
    body = "## Real\n\n```\n## NotAHeading\n```\n\n## AlsoReal\n"
    h2s = bh.extract_h2s(body)
    assert [t for t, _ in h2s] == ["Real", "AlsoReal"]


def test_cli_dry_run_does_not_write(tmp_path: Path) -> None:
    p = tmp_path / "post.html"
    p.write_text('<img src="a.png">', encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "blog_hygiene.py"), "--html", str(p)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["lazy_fixed"] == 1 and data["applied"] is False
    assert p.read_text(encoding="utf-8") == '<img src="a.png">'  # unchanged in dry-run


def test_cli_apply_writes(tmp_path: Path) -> None:
    p = tmp_path / "post.html"
    p.write_text('<img src="a.png">', encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "blog_hygiene.py"), "--html", str(p), "--apply"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert 'loading="lazy"' in p.read_text(encoding="utf-8")


def test_cli_refuses_symlink(tmp_path: Path) -> None:
    real = tmp_path / "real.html"
    real.write_text("<img src='a.png'>", encoding="utf-8")
    link = tmp_path / "link.html"
    try:
        link.symlink_to(real)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unsupported on this platform")
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "blog_hygiene.py"), "--html", str(link), "--apply"],
        capture_output=True, text=True,
    )
    assert r.returncode == 2
    assert "symlink" in (r.stdout + r.stderr).lower()
