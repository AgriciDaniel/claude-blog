"""Verify that legacy adoption evidence stays bounded to reviewed public bytes."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
REVISIONS = {
    '7b6ca107adb40b7c59030568420c117e2ea61301',
    '2500d4c765034864cede2bf215d00ccd4d7d6fb8',
}


def inventory():
    return json.loads((ROOT / 'data/legacy-install-ownership.json').read_text())


def test_legacy_inventory_has_only_reviewed_package_paths_and_revisions():
    data = inventory()
    assert data['schema_version'] == 1
    assert {r['commit'] for r in data['revisions']} == REVISIONS
    assert len(data['files']) == 186
    for name, records in data['files'].items():
        path = PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts
        assert path.parts[0] in {'skills', 'agents', 'scripts'}
        if path.parts[0] == 'skills':
            assert path.parts[1] == 'blog' or path.parts[1].startswith('blog-')
        assert records
        for record in records:
            assert record['revision'] in REVISIONS
            source = PurePosixPath(record['source'])
            assert not source.is_absolute() and '..' not in source.parts
            assert re.fullmatch(r'[a-f0-9]{64}', record['sha256'])


def test_actual_published_legacy_fixture_is_adoptable_but_an_edit_is_not():
    content = (ROOT / 'tests/fixtures/legacy-blog-write-v2.2.0.md').read_bytes()
    allowed = {r['sha256'] for r in inventory()['files']['skills/blog-write/SKILL.md']}
    assert hashlib.sha256(content).hexdigest() in allowed
    assert hashlib.sha256(content + b'\nuser edit\n').hexdigest() not in allowed
    assert hashlib.sha256((ROOT / 'skills/blog-write/SKILL.md').read_bytes()).hexdigest() not in allowed


def test_every_legacy_hash_matches_its_pinned_public_git_blob_when_available():
    if not shutil.which('git'):
        pytest.skip('Git unavailable for historical blob provenance')
    for revision in REVISIONS:
        result = subprocess.run(['git', 'cat-file', '-e', revision + '^{commit}'], cwd=ROOT, capture_output=True)
        if result.returncode:
            pytest.skip('Shallow checkout lacks a reviewed public revision; no network fetch performed')
    for records in inventory()['files'].values():
        for record in records:
            result = subprocess.run(['git', 'show', record['revision'] + ':' + record['source']], cwd=ROOT, check=True, capture_output=True)
            assert hashlib.sha256(result.stdout).hexdigest() == record['sha256']
