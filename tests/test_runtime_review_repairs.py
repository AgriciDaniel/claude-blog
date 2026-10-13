"""Independent-review regressions: identity consistency and direct safe transport."""
from __future__ import annotations

import base64
import importlib.util
import io
import json
from pathlib import Path
import socket
import ssl
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope='module')
def preflight():
    return _load('review_repair_preflight', 'blog_preflight.py')


@pytest.fixture(autouse=True)
def isolate_identity_fixture_links(preflight, monkeypatch):
    # The renderer emits a publisher footer link; identity tests never probe it.
    monkeypatch.setattr(preflight, '_safe_http_url', lambda _url: (True, None))
    monkeypatch.setattr(preflight, '_http_head', lambda _url: 200)


@pytest.fixture(scope='module')
def renderer():
    return _load('review_repair_renderer', 'blog_render.py')


@pytest.fixture(scope='module')
def hero():
    return _load('review_repair_hero', 'generate_hero.py')


def _render_fixture(directory, renderer):
    source = directory / 'post.md'
    source.write_text('---\ntitle: Fixture title\nslug: post\ndescription: Fixture description\ndate: 2026-10-07\nauthor: Fixture Editor\ncanonical: https://publisher.example/articles/post\n---\n\nA useful article.\n')
    (directory / 'hero.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGNoaGj4DwAFhAKAjM1mJgAAAABJRU5ErkJggg=='))
    renderer._render_html(source, directory, 'hero.png')
    (directory / 'post.pdf').write_bytes(b'%PDF-1.4\n')
    return directory / 'post.html'


def _schema_edit(path, edit):
    import re
    raw = path.read_text()
    match = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', raw, re.S)
    schema = json.loads(match.group(2))
    edit(schema)
    path.write_text(raw[:match.start(2)] + json.dumps(schema) + raw[match.end(2):])


@pytest.mark.parametrize('field,value', [
    ('headline', 'A different headline'),
    ('author', {'@type': 'Person', 'name': 'A different author'}),
    ('datePublished', '1999-01-01'),
    ('image', 'https://other.example/not-the-hero.png'),
])
def test_source_gate_rejects_each_visible_schema_mismatch(preflight, renderer, tmp_path, field, value):
    path = _render_fixture(tmp_path, renderer)
    _schema_edit(path, lambda schema: schema.update({field: value}))
    result = preflight.gate_5_asset_link_integrity(tmp_path, 'post')
    assert not result['passed']
    assert any('does not match visible content' in item and field in item for item in result['violations'])


@pytest.mark.parametrize('field,value', [
    ('headline', 'A different headline'),
    ('author', {'@type': 'Person', 'name': 'A different author'}),
    ('datePublished', '1999-01-01'),
    ('image', 'https://other.example/not-the-hero.png'),
    (None, None),
])
def test_rendered_gate_checks_real_dom_identity(preflight, renderer, tmp_path, field, value):
    browser_api = pytest.importorskip('patchright.sync_api')
    with browser_api.sync_playwright() as runtime:
        if not Path(runtime.chromium.executable_path).is_file():
            pytest.skip('requires matching installed Chromium; no browser download in unit tests')
    path = _render_fixture(tmp_path, renderer)
    if field:
        _schema_edit(path, lambda schema: schema.update({field: value}))
    result = preflight.gate_3_visual_verification(tmp_path, 'post')
    assert result['passed'] is (field is None), result['violations']
    assert set(result['per_viewport']) == {'mobile', 'tablet', 'desktop', 'desktop-dark'}
    assert len(list((tmp_path / 'preview').glob('*.png'))) == 4
    for viewport in ('mobile', 'tablet', 'desktop'):
        observation = result['per_viewport'][viewport]['result']
        assert observation['jsonLdVisibleConsistent'] is (field is None)
        assert observation['jsonLdConsistencyMismatches'] == ([field] if field else [])
    if field:
        assert not preflight._rendered_jsonld_handoff(result)['available']
        assert not preflight.gate_5_asset_link_integrity(tmp_path, 'post')['passed']


@pytest.mark.parametrize('author', [
    'Fixture Editor',
    {'@type': 'Person', 'name': 'Fixture Editor'},
    [{'@type': 'Person', 'name': 'Fixture Editor'}],
])
def test_renderer_supported_author_forms_and_published_absolute_hero(preflight, renderer, tmp_path, author):
    path = _render_fixture(tmp_path, renderer)
    _schema_edit(path, lambda schema: schema.update(author=author))
    result = preflight.gate_5_asset_link_integrity(tmp_path, 'post')
    assert result['passed'], result['violations']


def _identity_html(author_markup, date_markup, image='hero.png'):
    return ('<link rel="canonical" href="https://publisher.example/post">'
            '<article><header><h1>Fixture title</h1>' + author_markup + date_markup +
            '</header><figure class="hero"><img src="' + image + '"></figure></article>')


@pytest.mark.parametrize('author_markup,authors', [
    ('<p class="byline">By Alice Smith and Bob Ray · 2026-10-07</p>', ['Alice Smith', 'Bob Ray']),
    ('<a rel="author">Alice Smith</a><a rel="author">Bob Ray</a>', [{'@type': 'Person', 'name': 'Alice Smith'}, {'@type': 'Person', 'name': 'Bob Ray'}]),
    ('<span itemprop="author"><span itemprop="name">Alice Smith</span></span>', {'@id': '#alice'}),
    ('<span class="author-name">Example &amp; Partners</span>', {'@type': 'Organization', 'name': 'Example & Partners'}),
])
def test_multiple_semantic_authors_and_graph_references(preflight, author_markup, authors):
    node = {'headline': 'Fixture title', 'author': authors, 'datePublished': '2026-10-07', 'image': {'@type': 'ImageObject', 'contentUrl': 'https://publisher.example/post/hero.png'}}
    nodes = [node, {'@id': '#alice', '@type': 'Person', 'name': 'Alice Smith'}]
    html = _identity_html(author_markup, '<time datetime="2026-10-07">October 7, 2026</time>')
    assert preflight._jsonld_identity_mismatches(html, node, nodes) == []


@pytest.mark.parametrize('visible,schema', [
    ('2026-10-07T22:30:00Z', '2026-10-08T00:30:00+02:00'),
    ('2026-10-07', '2026-10-07T12:30:00-07:00'),
    ('2026-10-07', '2026-10-08T00:30:00+02:00'),
])
def test_equivalent_publication_dates_with_timezones(preflight, visible, schema):
    html = _identity_html('<a rel="author">Editor</a>', f'<time datetime="{visible}">Published</time>')
    node = {'headline': 'Fixture title', 'author': 'Editor', 'datePublished': schema, 'image': 'hero.png'}
    assert preflight._jsonld_identity_mismatches(html, node, [node]) == []


def test_different_publication_instant_and_hidden_decoys_do_not_match(preflight):
    html = _identity_html('<a rel="author">Real Editor</a><span hidden class="author">Fake Editor</span>', '<time datetime="2026-10-07T12:00:00Z">Published</time>')
    node = {'headline': 'Fixture title', 'author': 'Fake Editor', 'datePublished': '2026-10-07T13:00:00Z', 'image': 'hero.png'}
    assert preflight._jsonld_identity_mismatches(html, node, [node]) == ['author', 'datePublished']


def test_semantic_publish_date_does_not_compare_modified_time(preflight):
    html = _identity_html('<a rel="author">Editor</a>', '<time itemprop="datePublished" datetime="2026-10-07">Published</time><time itemprop="dateModified" datetime="2026-10-08">Updated</time>')
    node = {'headline': 'Fixture title', 'author': 'Editor', 'datePublished': '2026-10-07', 'image': 'hero.png'}
    assert preflight._jsonld_identity_mismatches(html, node, [node]) == []


@pytest.mark.parametrize('relative,absolute', [
    ('hero.png', 'https://publisher.example/post/hero.png'),
    ('hero.png', 'https://publisher.example/hero.png'),
    ('/assets/hero%20cover.png', 'https://publisher.example/assets/hero cover.png'),
])
def test_relative_and_published_absolute_assets_match(preflight, relative, absolute):
    html = _identity_html('<a rel="author">Editor</a>', '<time datetime="2026-10-07">Published</time>', relative)
    node = {'headline': 'Fixture title', 'author': 'Editor', 'datePublished': '2026-10-07', 'image': [absolute]}
    assert preflight._jsonld_identity_mismatches(html, node, [node]) == []


@pytest.mark.parametrize('filename', ['blog_preflight.py', 'generate_hero.py'])
@pytest.mark.parametrize('scheme', ['http', 'https'])
@pytest.mark.parametrize('proxy', ['http://127.0.0.1:8765', 'http://untrusted-proxy.invalid:8765'])
def test_safe_url_transport_ignores_environment_proxies(monkeypatch, filename, scheme, proxy):
    # Load after poisoning the environment: urllib normally captures it at opener creation.
    for key in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy'):
        monkeypatch.setenv(key, proxy)
    for key in ('NO_PROXY', 'no_proxy', 'REQUEST_METHOD'):
        monkeypatch.delenv(key, raising=False)
    port = 443 if scheme == 'https' else 80
    validated = [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', ('93.184.216.34', port))]
    dns_calls, connections, requests, sni = [], [], [], []

    def dns(host, requested_port, *args, **kwargs):
        dns_calls.append((host, requested_port))
        assert host == 'public.example', 'proxy DNS must never be requested'
        assert len(dns_calls) == 1, 'transport must use validated pinned DNS, not re-resolve'
        return validated

    class FakeSocket:
        def sendall(self, data):
            requests.append(data)
        def makefile(self, *args, **kwargs):
            return io.BytesIO(b'HTTP/1.1 200 OK\r\nContent-Length: 4\r\n\r\nbody')
        def close(self):
            pass
        def settimeout(self, timeout):
            pass
        def setsockopt(self, *args):
            pass

    def connect(address, *args, **kwargs):
        connections.append(address)
        assert address == ('public.example', port), 'must connect to origin, never proxy'
        assert socket.getaddrinfo(*address, proto=socket.IPPROTO_TCP) == validated
        return FakeSocket()

    class FakeTLS:
        post_handshake_auth = False
        verify_mode = ssl.CERT_REQUIRED
        check_hostname = True
        def set_alpn_protocols(self, protocols):
            pass
        def wrap_socket(self, sock, server_hostname=None):
            sni.append(server_hostname)
            return sock

    monkeypatch.setattr(socket, 'getaddrinfo', dns)
    monkeypatch.setattr(socket, 'gethostbyname', lambda host: '93.184.216.34')
    monkeypatch.setattr(socket, 'create_connection', connect)
    monkeypatch.setattr(ssl, '_create_default_https_context', FakeTLS)
    # Python 3.12 constructs the urllib TLS context when the opener is built.
    module = _load('direct_transport_' + filename.replace('.', '_'), filename)
    url = scheme + '://public.example/proof'
    if filename == 'blog_preflight.py':
        assert module._http_request_status(url, method='HEAD') == (200, None)
        expected_method = b'HEAD'
    else:
        assert module._http_get(url) == b'body'
        expected_method = b'GET'
    assert connections == [('public.example', port)]
    assert len(dns_calls) == 1
    assert len(requests) == 1 and requests[0].startswith(expected_method + b' /proof HTTP/1.1\r\n')
    assert b'Host: public.example\r\n' in requests[0]
    assert b'CONNECT' not in requests[0] and b'127.0.0.1' not in requests[0] and b'untrusted-proxy' not in requests[0]
    assert sni == (['public.example'] if scheme == 'https' else [])


def test_hero_rejects_symlink_ancestor_before_creating_leaf(hero, tmp_path, monkeypatch, capsys):
    outside = tmp_path / 'outside'
    outside.mkdir()
    sentinel = outside / 'sentinel'
    sentinel.write_text('untouched')
    draft = tmp_path / 'draft'
    draft.mkdir()
    (draft / 'alias').symlink_to(outside, target_is_directory=True)
    target = draft / 'alias' / 'absent-leaf'
    monkeypatch.setattr(sys, 'argv', ['generate_hero.py', '--topic', 'fixture', '--out', str(target), '--json'])
    monkeypatch.setattr(hero, '_try_gemini', lambda *args: pytest.fail('no provider call allowed'))
    assert hero.main() == 1
    assert json.loads(capsys.readouterr().out)['error'] == 'out-dir-symlink'
    assert not (outside / 'absent-leaf').exists()
    assert sentinel.read_text() == 'untouched'
    assert sorted(path.name for path in outside.iterdir()) == ['sentinel']


@pytest.mark.parametrize('writer,payload', [('_atomic_write_bytes', b'replacement'), ('_atomic_write_text', 'replacement')])
def test_hero_atomic_writes_refuse_symlink_ancestors(hero, tmp_path, writer, payload):
    outside = tmp_path / 'outside'
    outside.mkdir()
    sentinel = outside / 'hero.png'
    sentinel.write_bytes(b'untouched')
    alias = tmp_path / 'alias'
    alias.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match='symlink output path component'):
        getattr(hero, writer)(alias / 'hero.png', payload)
    assert sentinel.read_bytes() == b'untouched'


def test_hero_atomic_writes_accept_ordinary_directory(hero, tmp_path):
    hero._atomic_write_bytes(tmp_path / 'hero.png', b'image')
    hero._atomic_write_text(tmp_path / 'hero-credit.txt', 'credit')
    assert (tmp_path / 'hero.png').read_bytes() == b'image'
    assert (tmp_path / 'hero-credit.txt').read_text() == 'credit'


def test_body_historic_time_is_not_the_publication_date(preflight):
    html = _identity_html('<a rel="author">Editor</a>', '<time datetime="2026-10-07">Published</time>')
    html = html.replace('</article>', '<p>This event happened <time datetime="1999-01-01">long ago</time>.</p></article>')
    node = {'headline': 'Fixture title', 'author': 'Editor', 'datePublished': '2026-10-07', 'image': 'hero.png'}
    assert preflight._jsonld_identity_mismatches(html, node, [node]) == []


def test_conflicting_open_graph_image_blocks_source_gate(preflight, renderer, tmp_path):
    path = _render_fixture(tmp_path, renderer)
    raw = path.read_text()
    raw = raw.replace('<meta property="og:image" content="https://publisher.example/articles/post/hero.png">', '<meta property="og:image" content="https://other.example/wrong.png">')
    path.write_text(raw)
    result = preflight.gate_5_asset_link_integrity(tmp_path, 'post')
    assert not result['passed']
    assert any('does not match visible content' in item and 'image' in item for item in result['violations'])


@pytest.mark.parametrize('decoy', [
    '<span class="author" style="opacity:0">Fixture Editor</span>',
    '<span style="opacity:0"><span class="author" style="opacity:1">Fixture Editor</span></span>',
    '<style>.transparent-author{opacity:0}</style><span class="author transparent-author">Fixture Editor</span>',
    '<span class="author" style="color:transparent">Fixture Editor</span>',
    '<span class="author">Fixture Editor</span>',
    '<span class="author" style="display:none">Fixture Editor</span>',
])
def test_author_decoy_cannot_suppress_visible_conflicting_byline(preflight, renderer, tmp_path, decoy):
    path = _render_fixture(tmp_path, renderer)
    html = path.read_text().replace('<strong>By Fixture Editor</strong>', '<strong>By Visible Wrong Author</strong>' + decoy)
    path.write_text(html)
    result = preflight.gate_5_asset_link_integrity(tmp_path, 'post')
    assert not result['passed']
    assert any('does not match visible content' in item and 'author' in item for item in result['violations'])


@pytest.mark.parametrize('decoy', [
    '<span class="author" style="opacity:0">Fixture Editor</span>',
    '<span style="opacity:0"><span class="author" style="opacity:1">Fixture Editor</span></span>',
    '<style>.transparent-author{opacity:0}</style><span class="author transparent-author">Fixture Editor</span>',
    '<span class="author" style="color:transparent">Fixture Editor</span>',
    '<style>.transparent-author{color:transparent}</style><span class="author transparent-author">Fixture Editor</span>',
    '<span class="author">Fixture Editor</span>',
    '<span class="author" style="display:none">Fixture Editor</span>',
])
def test_rendered_author_decoys_fail_actual_visibility(preflight, renderer, tmp_path, decoy):
    browser_api = pytest.importorskip('patchright.sync_api')
    with browser_api.sync_playwright() as runtime:
        if not Path(runtime.chromium.executable_path).is_file():
            pytest.skip('requires matching installed Chromium; no browser download in unit tests')
    path = _render_fixture(tmp_path, renderer)
    html = path.read_text().replace('<strong>By Fixture Editor</strong>', '<strong>By Visible Wrong Author</strong>' + decoy)
    path.write_text(html)
    result = preflight.gate_3_visual_verification(tmp_path, 'post')
    assert not result['passed']
    assert set(result['per_viewport']) == {'mobile', 'tablet', 'desktop', 'desktop-dark'}
    for viewport in ('mobile', 'tablet', 'desktop'):
        observation = result['per_viewport'][viewport]['result']
        assert observation['jsonLdVisibleConsistent'] is False
        assert 'author' in observation['jsonLdConsistencyMismatches']
    assert not preflight._rendered_jsonld_handoff(result)['available']


@pytest.mark.parametrize('extra', [
    '<span class="author">Fixture Editor</span>',
    '<span class="author" style="opacity:0">Wrong Hidden Author</span>',
    '<span class="author" style="display:none">Wrong Hidden Author</span>',
])
def test_matching_author_representations_and_hidden_decoys_remain_valid(preflight, renderer, tmp_path, extra):
    path = _render_fixture(tmp_path, renderer)
    path.write_text(path.read_text().replace('<strong>By Fixture Editor</strong>', '<strong>By Fixture Editor</strong> ' + extra))
    result = preflight.gate_5_asset_link_integrity(tmp_path, 'post')
    assert result['passed'], result['violations']


@pytest.mark.parametrize('style', ['opacity:0', 'opacity:.0!important', 'opacity:0%', 'opacity:1;opacity:0'])
def test_source_inline_opacity_zero_is_not_visible_author(preflight, style):
    html = _identity_html(f'<span style="{style}"><a rel="author">Editor</a></span>', '<time datetime="2026-10-07">Published</time>')
    node = {'headline': 'Fixture title', 'author': 'Editor', 'datePublished': '2026-10-07', 'image': 'hero.png'}
    assert preflight._jsonld_identity_mismatches(html, node, [node]) == ['author']


def test_multiple_authors_may_combine_semantic_name_and_complete_byline(preflight):
    html = _identity_html('<p class="byline">By <a rel="author">Alice Smith</a> and Bob Ray · 2026-10-07</p>', '')
    node = {'headline': 'Fixture title', 'author': ['Alice Smith', 'Bob Ray'], 'datePublished': '2026-10-07', 'image': 'hero.png'}
    assert preflight._jsonld_identity_mismatches(html, node, [node]) == []
