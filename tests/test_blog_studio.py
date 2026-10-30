"""Saved evidence is complete, scoped and fresh before Studio displays success.

Unit tests here patch the gates. The real CLI contract the Blog Studio plugin
relies on is covered end to end in test_blog_studio_integration.py.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest
import blog_preflight as preflight
import blog_studio_status as studio


@pytest.fixture
def draft(tmp_path, monkeypatch):
    root = tmp_path / 'project'
    root.mkdir()
    folder = root / 'article'
    folder.mkdir()
    for name in ('article.md', 'article.html', 'article.pdf', 'hero.webp', 'review.md', 'style.css'):
        (folder / name).write_text('fixture ' + name)
    monkeypatch.setenv(preflight.REVIEW_STATE_ENV, str(tmp_path / 'verifier'))
    preflight._init_review_nonce(folder)
    return folder


def run(draft, monkeypatch, *, gate=None, blocked=None, preview=False, mutate=False, mutate_name='article.md', project_root=None):
    def result(n):
        def check(_draft, **_kwargs):
            if mutate and n == 3:
                (_draft / mutate_name).write_text('changed during checks')
            if n == 1:
                (_draft / 'capabilities.json').write_text('{}')
            if n == 3:
                (_draft / 'preview').mkdir(exist_ok=True)
                (_draft / 'preview/desktop-1280.png').write_bytes(b'fixture screenshot')
            kwargs = {'score': 90} if n == 4 else {}
            return preflight._gate_result(n, 'Fixture gate', blocked != n,
                                          ['fixture blocker'] if blocked == n else [], **kwargs)
        return check
    for n, name in enumerate(('gate_1_capability_discovery', 'gate_2_format_completeness',
                              'gate_3_visual_verification', 'gate_4_content_review', 'gate_5_asset_link_integrity'), 1):
        monkeypatch.setattr(preflight, name, result(n))
    args = ['blog_preflight.py', '--draft', str(draft), '--json']
    if gate: args.extend(['--gate', str(gate)])
    if preview: args.append('--no-strict')
    if project_root: args.extend(['--project-root', str(project_root)])
    monkeypatch.setattr(sys, 'argv', args)
    code = preflight.main()
    return code, json.loads((draft / 'preflight-report.json').read_text())


def test_full_strict_run_has_complete_evidence(draft, monkeypatch):
    code, report = run(draft, monkeypatch)
    assert code == 0
    assert report['strict'] is True and report['blocked'] is False
    assert report['evidence']['requested_gates'] == [1, 2, 3, 4, 5]
    assert report['evidence']['completed_gates'] == [1, 2, 3, 4, 5]
    assert report['evidence']['inputs_unchanged'] is True
    assert set(report['evidence']['inputs']['files']) == {'article.md', 'article.html', 'article.pdf', 'hero.webp', 'review.md', 'style.css'}
    assert set(report['evidence']['outputs']['files']) == {'capabilities.json', 'preview/desktop-1280.png'}
    status = studio.inspect_status(draft, draft.parent, report['evidence']['run_id'])
    assert status['status'] == 'passed'
    assert status['passed_count'] == 5
    assert 'nonce' not in json.dumps(status).lower()


@pytest.mark.parametrize('gate', [1, 2, 3, 4, 5])
def test_single_gate_never_displays_full_success(draft, monkeypatch, gate):
    run(draft, monkeypatch, gate=gate)
    assert studio.inspect_status(draft)['status'] == 'partial'


@pytest.mark.parametrize('blocked', [1, 2, 3, 4, 5])
def test_fail_fast_preserves_exit_and_blocker(draft, monkeypatch, blocked):
    code, report = run(draft, monkeypatch, blocked=blocked)
    assert code == 1
    assert len(report['gates']) == blocked
    status = studio.inspect_status(draft)
    assert status['status'] == 'blocked'
    assert status['gates'][-1]['violations'] == ['fixture blocker']


def test_preview_run_remains_unverified(draft, monkeypatch):
    code, _ = run(draft, monkeypatch, blocked=3, preview=True)
    assert code == 0
    assert studio.inspect_status(draft)['status'] == 'unverified'


def test_inputs_changed_during_checks_invalidate_evidence(draft, monkeypatch):
    _, report = run(draft, monkeypatch, mutate=True)
    assert report['evidence']['inputs_unchanged'] is False
    assert studio.inspect_status(draft)['status'] == 'stale'


@pytest.mark.parametrize('name', ['article.md', 'article.html', 'article.pdf', 'hero.webp', 'review.md', 'style.css', 'preflight-targets.json', 'external-links.allowed', 'preview/desktop-1280.png', 'capabilities.json'])
def test_any_changed_consumed_input_or_output_is_stale(draft, monkeypatch, name):
    run(draft, monkeypatch)
    (draft / name).write_text('changed')
    assert studio.inspect_status(draft)['status'] == 'stale'


def test_deleted_input_is_stale(draft, monkeypatch):
    run(draft, monkeypatch)
    (draft / 'article.pdf').unlink()
    assert studio.inspect_status(draft)['status'] == 'stale'


def test_verifier_rotation_is_stale_without_exposing_nonce(draft, monkeypatch):
    run(draft, monkeypatch)
    nonce = preflight._init_review_nonce(draft)
    status = studio.inspect_status(draft)
    assert status['status'] == 'stale'
    assert nonce not in json.dumps(status)


def test_run_identity_mismatch_cannot_accept_an_old_report(draft, monkeypatch):
    run(draft, monkeypatch)
    assert studio.inspect_status(draft, expected_run='b' * 32)['status'] == 'error'


def test_legacy_report_has_unknown_freshness(draft, monkeypatch):
    _, report = run(draft, monkeypatch)
    del report['evidence']
    (draft / 'preflight-report.json').write_text(json.dumps(report))
    assert studio.inspect_status(draft)['status'] == 'unverified'


@pytest.mark.parametrize('change', [
    lambda r: r.update(draft='/somewhere/else'),
    lambda r: r.update(blocked=True),
    lambda r: r['gates'].append(r['gates'][0]),
    lambda r: r['gates'][0].update(passed='true'),
    lambda r: r['gates'][0].update(violations=['contradiction']),
    lambda r: r['gates'][3].update(score=89),
    lambda r: r['gates'][3].update(score=float('nan')),
    lambda r: r['evidence'].update(completed_gates=[1]),
    lambda r: r['evidence'].update(requested_gates=[True, 2, 3, 4, 5]),
    lambda r: r['evidence'].update(started_at='tomorrow'),
    lambda r: r['evidence'].update(run_id='invalid'),
])
def test_malformed_or_contradictory_report_is_rejected(draft, monkeypatch, change):
    _, report = run(draft, monkeypatch)
    change(report)
    (draft / 'preflight-report.json').write_text(json.dumps(report))
    assert studio.inspect_status(draft)['status'] == 'error'


@pytest.mark.parametrize('raw', ['{"strict":true,"strict":false}', '[]', '{broken'])
def test_bad_json_is_rejected(draft, raw):
    (draft / 'preflight-report.json').write_text(raw)
    assert studio.inspect_status(draft)['status'] == 'error'


def test_missing_report_is_unverified(draft):
    assert studio.inspect_status(draft)['status'] == 'unverified'


def test_symlink_input_is_unverified(draft, monkeypatch, tmp_path):
    run(draft, monkeypatch)
    (draft / 'escape').symlink_to(tmp_path)
    assert studio.inspect_status(draft)['status'] == 'unverified'


def test_symlink_report_is_rejected(draft, tmp_path):
    target = tmp_path / 'report.json'
    target.write_text('{}')
    (draft / 'preflight-report.json').symlink_to(target)
    assert studio.inspect_status(draft)['status'] == 'error'


@pytest.mark.skipif(not hasattr(os, 'mkfifo'), reason='FIFO requires Unix')
def test_fifo_report_is_refused_without_blocking(draft):
    os.mkfifo(draft / 'preflight-report.json')
    assert studio.inspect_status(draft)['status'] == 'error'


def test_streaming_hash_supports_files_larger_than_mod_fs_limit(draft, monkeypatch):
    (draft / 'hero.webp').write_bytes(b'fixture' * 800_000)
    run(draft, monkeypatch)
    assert studio.inspect_status(draft)['status'] == 'passed'


def test_fingerprint_limit_is_not_a_pass(draft, monkeypatch):
    monkeypatch.setattr(studio, 'MAX_FILES', 1)
    run(draft, monkeypatch)
    assert studio.inspect_status(draft)['status'] == 'unverified'


def test_project_boundary_is_enforced(draft, monkeypatch, tmp_path):
    run(draft, monkeypatch)
    other = tmp_path / 'other'
    other.mkdir()
    assert studio.inspect_status(draft, other)['status'] == 'error'
    link = draft.parent / 'alias'
    link.symlink_to(draft, target_is_directory=True)
    assert studio.inspect_status(link, draft.parent)['status'] == 'error'


def test_lexical_traversal_is_rejected_even_when_target_returns_inside(draft, monkeypatch):
    run(draft, monkeypatch)
    (draft.parent / 'other').mkdir()
    traversing = draft.parent / 'other/../article'
    assert studio.inspect_status(traversing, draft.parent)['status'] == 'error'


def test_changed_engine_is_stale(draft, monkeypatch):
    run(draft, monkeypatch)
    identity = studio.engine_identity()
    identity['python'] = [0, 0, 0]
    monkeypatch.setattr(studio, 'engine_identity', lambda: identity)
    assert studio.inspect_status(draft)['status'] == 'stale'


@pytest.mark.parametrize('missing', ['blog_preflight.py', 'blog_studio_status.py', 'blog-delivery-contract.md', 'blog-reviewer.md'])
def test_missing_identity_file_cannot_establish_freshness(draft, monkeypatch, missing):
    original = studio._file_hash
    def missing_hash(path, *args):
        if path.name == missing:
            raise FileNotFoundError('fixture identity file absent')
        return original(path, *args)
    monkeypatch.setattr(studio, '_file_hash', missing_hash)
    _, report = run(draft, monkeypatch)
    assert report['evidence']['engine']['errors']
    assert studio.inspect_status(draft)['status'] == 'unverified'


def test_non_generated_preview_resources_are_inputs(draft, monkeypatch):
    resource = draft / 'preview/fonts/local.woff'
    resource.parent.mkdir(parents=True)
    resource.write_bytes(b'fixture font')
    _, report = run(draft, monkeypatch, mutate=True, mutate_name='preview/fonts/local.woff')
    assert 'preview/fonts/local.woff' in report['evidence']['inputs']['files']
    assert report['evidence']['inputs_unchanged'] is False
    assert studio.inspect_status(draft)['status'] == 'stale'


def test_generated_screenshot_names_match_canonical_viewports():
    expected = {f"preview/{vp['name']}-{vp['width']}.png" for vp in preflight.VIEWPORTS}
    assert studio.SCREENSHOTS == expected | {'preview/desktop-1280-dark.png'}


def test_project_contained_run_preserves_draft_identity_and_restores_cwd(draft, monkeypatch):
    before = Path.cwd()
    code, report = run(draft, monkeypatch, project_root=draft.parent)
    assert Path.cwd() == before
    assert code == 0 and report['draft'] == str(draft)
    assert studio.inspect_status(draft, draft.parent)['status'] == 'passed'


def test_launch_refuses_replaced_draft_symlink(draft, monkeypatch, tmp_path):
    outside = tmp_path / 'outside'
    outside.mkdir()
    draft.rename(draft.with_name('original'))
    draft.symlink_to(outside, target_is_directory=True)
    monkeypatch.setattr(sys, 'argv', ['blog_preflight.py', '--draft', str(draft), '--project-root', str(draft.parent), '--json'])
    assert preflight.main() == 1
    assert not (outside / 'preflight-report.json').exists()
    assert not (outside / 'capabilities.json').exists()


def test_anchored_writes_cannot_follow_replaced_path(draft, tmp_path):
    outside = tmp_path / 'outside'
    outside.mkdir()
    original = draft.with_name('original')
    before = Path.cwd()
    with preflight._anchored_draft(str(draft), str(draft.parent)) as (anchored, identity):
        assert identity == str(draft)
        draft.rename(original)
        draft.symlink_to(outside, target_is_directory=True)
        (anchored / 'sentinel').write_text('authorized selected directory only')
    assert Path.cwd() == before
    assert (original / 'sentinel').is_file()
    assert not (outside / 'sentinel').exists()


def test_inspection_stays_anchored_when_selected_path_is_replaced(draft, monkeypatch, tmp_path):
    run(draft, monkeypatch)
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'preflight-report.json').write_text('{"outside":true}')
    original = draft.with_name('original')
    original_load = studio.load_report
    opened = []
    def swapping_load(path):
        draft.rename(original)
        draft.symlink_to(outside, target_is_directory=True)
        opened.append(path.resolve())
        return original_load(path)
    monkeypatch.setattr(studio, 'load_report', swapping_load)
    before = Path.cwd()
    status = studio.inspect_status(draft, draft.parent)
    assert Path.cwd() == before
    assert opened == [original / 'preflight-report.json']
    assert status['status'] == 'stale'


def test_fingerprinting_cannot_follow_a_replaced_child_directory(draft, monkeypatch, tmp_path):
    folder = draft / 'resources'
    folder.mkdir()
    (folder / 'local.css').write_text('selected style')
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'local.css').write_text('outside private data')
    original_hash = studio._file_hash
    def swapping_hash(path, *args):
        if path.name == 'local.css':
            folder.rename(draft / 'original-resources')
            folder.symlink_to(outside, target_is_directory=True)
        return original_hash(path, *args)
    monkeypatch.setattr(studio, '_file_hash', swapping_hash)
    inputs = studio.capture_inputs(draft, preflight._review_state_path(draft))
    assert inputs['errors']
    assert 'resources/local.css' not in inputs['files']


def test_report_open_refuses_symlinked_parent(tmp_path):
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'report.json').write_text('{}')
    link = tmp_path / 'alias'
    link.symlink_to(outside, target_is_directory=True)
    with pytest.raises(OSError):
        studio.load_report(link / 'report.json')


def test_status_inspection_does_not_write_files(draft, monkeypatch):
    run(draft, monkeypatch)
    before = {p: (p.stat().st_mtime_ns, p.read_bytes()) for p in draft.rglob('*') if p.is_file()}
    studio.inspect_status(draft)
    assert {p: (p.stat().st_mtime_ns, p.read_bytes()) for p in before} == before


def test_diagnostics_strip_terminal_controls_and_identifiers():
    text = studio.safe_text('\x1b[31mBLOCKING: false Nonce: ' + 'a' * 32)
    assert '\x1b' not in text and 'a' * 32 not in text


def test_unfinished_run_marker_is_blocked_not_passed(draft, monkeypatch):
    run(draft, monkeypatch)
    marker = preflight._incomplete_report(str(draft), True, 'run started and has not finished')
    (draft / 'preflight-report.json').write_text(json.dumps(marker))
    status = studio.inspect_status(draft, draft.parent)
    assert status['status'] == 'blocked' and status['gates'] == [] and status['passed_count'] == 0
    assert 'did not finish' in status['diagnostics'][0]


def test_iteration_cap_keeps_lexical_draft_and_never_looks_passed(draft, monkeypatch):
    run(draft, monkeypatch)
    preflight._write_iteration_count(draft, preflight._iteration_state_path(draft), preflight.MAX_ITERATIONS)
    monkeypatch.setattr(sys, 'argv', ['blog_preflight.py', '--draft', str(draft), '--json',
                                      '--project-root', str(draft.parent)])
    assert preflight.main() == preflight.EXIT_ITERATION_CAP
    report = json.loads((draft / 'preflight-report.json').read_text())
    assert report['draft'] == str(draft) and report['incomplete'] is True and report['blocked'] is True
    assert 'evidence' not in report and report['previous_gates']
    assert studio.inspect_status(draft, draft.parent)['status'] == 'blocked'


def test_evidence_is_additive_and_optional_without_the_studio_module(draft, monkeypatch):
    for name in ('_anchored_draft', 'capture_inputs', 'capture_outputs', 'engine_identity'):
        monkeypatch.setattr(preflight, name, None)
    code, report = run(draft, monkeypatch)
    assert code == 0 and 'evidence' not in report
    assert set(report) == {'draft', 'strict', 'blocked', 'gates'}
    assert studio.inspect_status(draft)['status'] == 'unverified'


def test_project_root_without_the_studio_module_is_refused(draft, monkeypatch, capsys):
    monkeypatch.setattr(preflight, '_anchored_draft', None)
    monkeypatch.setattr(sys, 'argv', ['blog_preflight.py', '--draft', str(draft), '--project-root', str(draft.parent)])
    assert preflight.main() == 1
    assert 'blog_studio_status.py' in capsys.readouterr().err
    assert not (draft / 'preflight-report.json').exists()


def test_run_ids_are_unique_32_hex(draft, monkeypatch):
    first = run(draft, monkeypatch)[1]['evidence']['run_id']
    second = run(draft, monkeypatch)[1]['evidence']['run_id']
    assert first != second
    assert all(len(i) == 32 and set(i) <= set('0123456789abcdef') for i in (first, second))
