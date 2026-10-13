import { expect, mock, test } from 'claude-code/testing'
import type { On } from 'claude-code'
import { absoluteScripts, clean, jsonResponse, parseStatus, relativeDraft } from '../hooks/logic'
import { classify, doneCount, emptyRun, fail, reduce, skillSignal } from '../hooks/pipeline'
import { entryId, formatWhen, title, makeEntry, mergeEntries, parseFound, sortEntries, splitDraft, validEntry } from '../hooks/history'
import { bandRow, bar, duration, effective, groupViolations, spark } from '../hooks/view'

const THEME_KEYS = new Set(['text', 'inverseText', 'inactive', 'subtle', 'suggestion', 'remember', 'success', 'error', 'warning', 'merged', 'claude', 'permission', 'planMode', 'autoAccept', 'promptBorder', 'bashBorder', 'ide'])
const RUN = { origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 80 } } as const
// Mirrors the host's ProcessRunResult: truncation flags are always present.
const done = (r: { exitCode: number; stdout: string; stderr: string; isStdoutTruncated?: boolean }) =>
  ({ isStdoutTruncated: false, isStderrTruncated: false, ...r })
const PANE = { plugin: 'blog-studio', component: 'Pane', requestId: 'blog-studio-review',
  viewport: { columns: 80, rows: 30, isFullscreen: false },
  props: { title: 'Blog Studio', isFocused: true, bodyColumns: 70, placement: 'inline',
    scroll: { offset: 0, bodyRows: 20 }, view: {} } } as const
const BAND = { plugin: 'blog-studio', component: 'AbovePrompt',
  viewport: { columns: 80, rows: 30, isFullscreen: false },
  props: { hasSurvey: false, isWorking: false, maxRows: 3, bodyColumns: 80,
    scroll: { offset: 0, bodyRows: 3 }, view: {} } } as const
const PASS = {
  schema_version: 1, status: 'passed', label: 'Preflight passed', checked_at: '2026-10-08T10:00:00+00:00',
  passed_count: 5, run_id: 'a'.repeat(32), diagnostics: [], artifacts: ['article.md', 'hero.webp', 'preview/desktop.png'],
  gates: [1, 2, 3, 4, 5].map(n => ({ gate: n, name: 'Fixture gate', passed: true, violations: [], warnings: [], score: n === 4 ? 90 : null })),
}

function host(on: On, options: { surface?: 'terminal' | 'desktop' | null; link?: string; collision?: boolean; missing?: string; absent?: string; env?: string | null; store?: Record<string, unknown>; workspace?: () => string; sessionId?: () => string } = {}) {
  const opened: string[] = []
  const messages: string[] = []
  on('session.start', ($, e) => ({ cwd: e.cwd }))
  on('session.end', ($, e) => ({ sessionId: e.sessionId }))
  on('session.root', () => ({ value: options.workspace?.() ?? '/work' }))
  on('session.id', () => ({ value: options.sessionId?.() ?? 'fixture-session' }))
  on('session.surfaces', () => ({ value: options.surface === null ? [] : [options.surface ?? 'terminal'] }))
  mock.store(on, options.store)
  on('env.get', () => ({ value: options.env === undefined ? '/trusted/scripts' : options.env ?? undefined }))
  on('command.register', ($, e) => options.collision ? { deny: 'taken' } : { value: { command: e.name } })
  on('fs.stat', ($, e) => {
    if (e.path === options.absent) throw new Error('ENOENT: no such file or directory')
    return { value: { kind: e.path === options.missing ? 'other' : e.path.endsWith('.py') ? 'file' : 'dir',
    size: 10, mtimeMs: 0, isLink: e.path === options.link } }
  })
  on('ui.open', ($, e) => { opened.push(e.id); return { value: { isPlaced: true } } })
  on('ui.close', () => ({ value: undefined }))
  on('ui.toast', ($, e) => { messages.push(e.text); return { value: undefined } })
  on('tool.list', () => ({ value: [] }))
  on('ui.render', () => ({ type: 'Text', props: {}, children: ['Other mod'] }))
  return { opened, messages }
}

for (const surface of ['terminal', 'desktop'] as const) {
  for (const width of [32, 80, 160]) {
    test('panel controls and five gates on ' + surface + ' at ' + width + ' columns', async ($, on) => {
      const h = host(on, { surface })
      on('process.run', () => ({ value: done({ exitCode: 0, stdout: JSON.stringify(PASS), stderr: '' }) }))
      await $.session.start({ cwd: '/work', surface, isInteractive: true })
      await $.command.run({ command: 'blog-studio', args: '', ...RUN })
      expect(h.opened).toEqual(['blog-studio-review'])
      const ui = await $.ui.mount({ ...PANE, surface, props: { ...PANE.props, bodyColumns: width } })
      expect(await ui.find({ key: 'draft' })).toBeDefined()
      await ui.input({ key: 'draft', text: 'outputs/article' })
      await ui.press({ key: 'refresh' })
      expect(await ui.find({ type: 'Text', text: /Preflight passed/ })).toBeDefined()
      expect(await ui.findAll({ type: 'Text', text: 'Fixture gate' })).toHaveLength(5)
      expect(await ui.find({ type: 'Text', text: /90\/100/ })).toBeDefined()
      expect(await ui.find({ type: 'Text', text: /hero\.webp/ })).toBeDefined()
      // Colors must be host theme keys so light and dark both work: never hex values or ANSI names.
      const drawn = JSON.stringify(await ui.drawn())
      const colors = [...drawn.matchAll(/"(?:color|backgroundColor|borderColor)":"([^"]*)"/g)].map(m => m[1] ?? '')
      expect(colors.length).toBeGreaterThan(0)
      expect(colors.filter(c => !THEME_KEYS.has(c))).toEqual([])
      await ui.press({ key: 'close' })
      await ui.unmount()
    })
  }
}

test('band preserves another mod and yields to surveys and tiny slots', async ($, on) => {
  host(on)
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
  let band = await $.ui.mount({ ...BAND, surface: 'terminal' })
  expect(await band.find({ type: 'Text', text: 'Other mod' })).toBeDefined()
  expect(await band.find({ key: 'open-studio' })).toBeUndefined()
  await band.unmount()
  await $.command.run({ command: 'blog-studio', args: 'select outputs/article', ...RUN })
  band = await $.ui.mount({ ...BAND, surface: 'terminal' })
  expect(await band.find({ type: 'Text', text: 'Other mod' })).toBeDefined()
  expect(await band.find({ key: 'open-studio' })).toBeDefined()
  await band.press({ key: 'open-studio' })
  await band.unmount()
  for (const props of [{ ...BAND.props, hasSurvey: true }, { ...BAND.props, maxRows: 1 }]) {
    const survey = await $.ui.mount({ ...BAND, surface: 'terminal', props })
    expect(await survey.find({ key: 'open-studio' })).toBeUndefined()
    await survey.unmount()
  }
})

test('Run checks button executes the checker and inspector, then redraws', async ($, on) => {
  host(on)
  const calls: string[] = []
  on('process.run', ($, e) => {
    calls.push(e.argv[1] ?? '')
    return { value: done({ exitCode: 0, stderr: '', stdout: JSON.stringify(e.argv[1]?.endsWith('blog_preflight.py') ?
      { strict: true, blocked: false, draft: '/work/outputs/article', evidence: { run_id: PASS.run_id } } : PASS) }) }
  })
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  await ui.input({ key: 'draft', text: 'outputs/article' })
  await ui.press({ key: 'check' })
  expect(calls).toEqual(['/trusted/scripts/blog_preflight.py', '/trusted/scripts/blog_studio_status.py'])
  expect(await ui.find({ type: 'Text', text: /Preflight passed/ })).toBeDefined()
  await ui.unmount()
})

for (const missing of ['/trusted/scripts/blog_studio_status.py', '/trusted/scripts/blog_preflight.py']) {
  test('missing trusted helper cannot execute: ' + missing, async ($, on) => {
    host(on, { missing })
    let calls = 0
    on('process.run', () => { calls++; throw new Error('must not run') })
    await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
    await $.command.run({ command: 'blog-studio', args: 'select outputs/article', ...RUN })
    const result = await $.command.run({ command: 'blog-studio', args: 'check', ...RUN })
    expect(result).toMatchObject({ text: expect.stringContaining('Execution error') })
    expect(calls).toBe(0)
  })
}

for (const status of ['blocked', 'partial', 'stale', 'unverified', 'error']) {
  test('refresh preserves nonpassing inspector status: ' + status, async ($, on) => {
    host(on)
    on('process.run', () => ({ value: done({ exitCode: status === 'error' ? 1 : 0, stderr: '',
      stdout: JSON.stringify({ ...PASS, status, passed_count: 0,
        gates: [{ gate: 1, name: 'Capability', passed: false, score: null, violations: ['Missing browser'], warnings: [] }] }) }) }))
    await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
    await $.command.run({ command: 'blog-studio', args: 'select outputs/article', ...RUN })
    const result = await $.command.run({ command: 'blog-studio', args: 'refresh', ...RUN })
    expect(result).not.toMatchObject({ text: expect.stringContaining('Preflight passed') })
    const band = await $.ui.mount({ ...BAND, surface: 'terminal' })
    expect(await band.find({ type: 'Text', text: /Missing browser/ })).toBeDefined()
    await band.unmount()
  })
}

const STUDIO = { workspace: '/work', sessionId: 'fixture', scripts: '/trusted', draft: 'article', generation: 1, projectRoot: null, busy: false,
  message: null, status: PASS as never } as const

test('idle band keeps draft, status and gate count', () => {
  const run = emptyRun('/work', 'fixture')
  const text = bandRow(STUDIO, run, effective(run, PASS as never, false, 0), 80, 0).map(x => x.t).join('')
  expect(text).toContain('article')
  expect(text).toContain('Preflight passed')
  expect(text).toContain('5/5')
})

for (const columns of [24, 40, 62, 100, 140]) {
  test('running band fits and keeps the stage rail at ' + columns + ' columns', () => {
    let run = reduce(emptyRun('/work', 'fixture'), { kind: 'start', skill: 'blog-write' }, 0)
    run = reduce(run, { kind: 'stage', stage: 'research', note: 'r' }, 1000)
    run = reduce(run, { kind: 'stage', stage: 'draft', note: 'd' }, 61_000)
    const idle = { ...STUDIO, status: null }
    const text = bandRow(idle, run, effective(run, null, false, 62_000), columns, 62_000).map(x => x.t).join('')
    expect(text.length).toBeLessThanOrEqual(Math.max(columns, 30))
    expect(text).toContain('✓')
    expect(text).toContain('▸')
    expect(text).toContain('Draft')
  })
}

test('verified gate evidence completes stages the agent was only inferred to run', () => {
  const run = reduce(emptyRun('/work', 'fixture'), { kind: 'stage', stage: 'draft', note: 'd' }, 0)
  const stages = effective(run, PASS as never, false, 5)
  expect(stages.every(x => x.state === 'done' && x.word === 'verified')).toBe(true)
})

test('malformed JSON errors do not echo article or helper output', () => {
  expect(() => jsonResponse('private article body')).toThrow()
  try { jsonResponse('private article body') } catch (error) {
    expect(String(error)).not.toContain('private article body')
  }
})

for (const stage of ['checker', 'inspector']) {
  test('malformed ' + stage + ' JSON retains sanitized stderr diagnostics', async ($, on) => {
    host(on)
    on('process.run', ($, e) => {
      const isChecker = e.argv[1]?.endsWith('blog_preflight.py')
      const broken = stage === 'checker' ? isChecker : !isChecker
      return { value: done({ exitCode: broken ? 1 : 0, stderr: broken ? '\x1b[31mMissing browser at /var/home/owner/private; ' + 'c'.repeat(32) : '',
        stdout: broken ? 'private article body' : JSON.stringify({ strict: true, blocked: false,
          draft: '/work/outputs/article', evidence: { run_id: PASS.run_id } }) }) }
    })
    await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
    await $.command.run({ command: 'blog-studio', args: 'select outputs/article', ...RUN })
    const result = await $.command.run({ command: 'blog-studio', args: 'check', ...RUN })
    expect(result).toMatchObject({ text: expect.stringContaining('Missing browser') })
    expect(result).not.toMatchObject({ text: expect.stringContaining('private article body') })
    expect(result).not.toMatchObject({ text: expect.stringContaining('/var/home/owner') })
    expect(result).not.toMatchObject({ text: expect.stringContaining('c'.repeat(32)) })
  })
}

test('same-session reload preserves selection but invalidates proof', async ($, on) => {
  host(on)
  on('process.run', () => ({ value: done({ exitCode: 0, stdout: JSON.stringify(PASS), stderr: '' }) }))
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
  await $.command.run({ command: 'blog-studio', args: 'select outputs/article', ...RUN })
  await $.command.run({ command: 'blog-studio', args: 'refresh', ...RUN })
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
  const out = await $.command.run({ command: 'blog-studio', args: 'status', ...RUN })
  expect(out).toMatchObject({ text: expect.stringContaining('outputs/article | Unverified') })
})

test('branch into another session clears selection', async ($, on) => {
  let sessionId = 'fixture-session'
  host(on, { sessionId: () => sessionId })
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
  await $.command.run({ command: 'blog-studio', args: 'select outputs/article', ...RUN })
  sessionId = 'branched-session'
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
  const out = await $.command.run({ command: 'blog-studio', args: 'status', ...RUN })
  expect(out).toMatchObject({ text: expect.stringContaining('select a draft') })
})

test('check invokes strict canonical script with no shell then verifies run identity', async ($, on) => {
  host(on)
  const calls: string[][] = []
  const limits: number[] = []
  on('process.run', ($, e) => {
    calls.push([...e.argv]); limits.push(e.init?.timeoutMs ?? 0)
    return { value: done({ exitCode: 0, stderr: '', stdout: JSON.stringify(e.argv[1]?.endsWith('blog_preflight.py') ?
      { strict: true, blocked: false, draft: '/work/outputs/article', evidence: { run_id: PASS.run_id } } : PASS) }) }
  })
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
  await $.command.run({ command: 'blog-studio', args: 'select outputs/article', ...RUN })
  const out = await $.command.run({ command: 'blog-studio', args: 'check', ...RUN })
  expect(out).toMatchObject({ text: expect.stringContaining('Preflight passed') })
  expect(calls[0]?.slice(0, 6)).toEqual(['python3', '/trusted/scripts/blog_preflight.py', '--draft', '/work/outputs/article', '--strict', '--json'])
  expect(limits).toEqual([600_000, 30_000])
  expect(calls[1]).toContain('--expected-run')
  expect(calls[0]).not.toContain('--repair-attempt')
  expect(calls[0]).not.toContain('--init-review-nonce')
  expect(calls[0]?.slice(-2)).toEqual(['--project-root', '/work'])
})

for (const failure of ['timeout', 'malformed', 'truncated', 'wrong-exit', 'missing-report']) {
  test('check failure stays visible: ' + failure, async ($, on) => {
    host(on)
    on('process.run', () => {
      if (failure === 'timeout') throw new Error('python3 unavailable or process timed out')
      return { value: done({ exitCode: failure === 'wrong-exit' ? 2 : 0, stderr: 'fixture stderr',
        stdout: failure === 'malformed' ? '{broken' : failure === 'missing-report' ? '' : JSON.stringify({ strict: true,
          blocked: false, draft: '/work/outputs/article', evidence: { run_id: PASS.run_id } }),
        isStdoutTruncated: failure === 'truncated' }) }
    })
    await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
    await $.command.run({ command: 'blog-studio', args: 'select outputs/article', ...RUN })
    const out = await $.command.run({ command: 'blog-studio', args: 'check', ...RUN })
    expect(out).toMatchObject({ text: expect.stringContaining('Execution error') })
    expect(out).not.toMatchObject({ text: expect.stringContaining('Preflight passed') })
  })
}

for (const link of ['/work/outputs', '/trusted/scripts/blog_preflight.py']) {
  test('symlink path refused before any process: ' + link, async ($, on) => {
    host(on, { link })
    let calls = 0
    on('process.run', () => { calls++; throw new Error('must not run') })
    await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
    await $.command.run({ command: 'blog-studio', args: 'select outputs/article', ...RUN })
    await $.command.run({ command: 'blog-studio', args: 'check', ...RUN })
    expect(calls).toBe(0)
  })
}

test('selecting a nonexistent draft gives the plain path message, not a raw filesystem error', async ($, on) => {
  host(on, { absent: '/work/outputs/nonexistent' })
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
  const result = await $.command.run({ command: 'blog-studio', args: 'select outputs/nonexistent', ...RUN })
  expect(result).toMatchObject({ text: expect.stringContaining('Missing or unsafe path') })
  expect(JSON.stringify(result)).not.toContain('ENOENT')
})

test('headless commands return text without opening a pane', async ($, on) => {
  const h = host(on, { surface: null })
  await $.session.start({ cwd: '/work', surface: null, isInteractive: false })
  const out = await $.command.run({ command: 'blog-studio', args: '', ...RUN })
  expect(out).toMatchObject({ text: expect.stringContaining('text subcommands') })
  expect(h.opened).toEqual([])
})

test('registration collision still returns session.start and reports the problem', async ($, on) => {
  const h = host(on, { collision: true })
  const out = await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
  expect(out).toMatchObject({ cwd: '/work' })
  expect(h.messages).toHaveLength(1)
})

test('path parsers refuse traversal and diagnostics do not reveal nonces or controls', () => {
  for (const path of ['../escape', '/outside', 'a/../escape', 'a//b', './a', 'a\\b', '']) {
    expect(() => relativeDraft(path)).toThrow()
  }
  expect(relativeDraft('outputs/article with spaces')).toBe('outputs/article with spaces')
  expect(() => absoluteScripts('/trusted/../draft')).toThrow()
  const secret = 'b'.repeat(32)
  expect(clean('\x1b[31mNonce: ' + secret)).not.toContain(secret)
  expect(clean('\x1b[31mtext')).not.toContain('\x1b')
  expect(clean('private /var/home/owner/file')).not.toContain('/var/home/owner')
})

test('malformed and contradictory status cannot pass', () => {
  for (const raw of ['null', '{}', '{broken', JSON.stringify({ ...PASS, status: 'toString' }),
    JSON.stringify({ ...PASS, passed_count: 4 }), JSON.stringify({ ...PASS, gates: PASS.gates.slice(0, 4) })]) {
    expect(() => parseStatus(raw)).toThrow()
  }
})

for (const reason of ['clear', 'resume'] as const) {
  test('selection cleared on session ' + reason, async ($, on) => {
    host(on)
    await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
    await $.command.run({ command: 'blog-studio', args: 'select outputs/article', ...RUN })
    await $.session.end({ reason, sessionId: 'fixture-session', resume: { id: 'fixture-session' } })
    const status = await $.command.run({ command: 'blog-studio', args: 'status', ...RUN })
    expect(status).toMatchObject({ text: expect.stringContaining('select a draft') })
  })
}

test('workspace switch clears selection', async ($, on) => {
  let workspace = '/work'
  host(on, { workspace: () => workspace })
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
  await $.command.run({ command: 'blog-studio', args: 'select outputs/article', ...RUN })
  workspace = '/another-project'
  const status = await $.command.run({ command: 'blog-studio', args: 'status', ...RUN })
  expect(status).toMatchObject({ text: expect.stringContaining('select a draft') })
})

for (const change of ['clear', 'workspace'] as const) {
  test('late completion discarded after ' + change + ', duplicate check refused', async ($, on) => {
    let workspace = '/work'
    host(on, { workspace: () => workspace })
    let release: (() => void) | undefined
    let began: (() => void) | undefined
    const started = new Promise<void>(resolve => { began = resolve })
    const waiting = new Promise<void>(resolve => { release = resolve })
    let calls = 0
    on('process.run', async () => {
      calls++
      if (calls === 1) { began?.(); await waiting }
      return { value: done({ exitCode: 0, stderr: '', stdout: JSON.stringify(calls === 1 ?
        { strict: true, blocked: false, draft: '/work/outputs/article', evidence: { run_id: PASS.run_id } } : PASS) }) }
    })
    await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
    await $.command.run({ command: 'blog-studio', args: 'select outputs/article', ...RUN })
    const check = $.command.run({ command: 'blog-studio', args: 'check', ...RUN })
    await started
    const duplicate = await $.command.run({ command: 'blog-studio', args: 'check', ...RUN })
    expect(duplicate).toMatchObject({ text: 'Checks are already running.' })
    if (change === 'clear') await $.session.end({ reason: 'clear', sessionId: 'fixture-session', resume: { id: 'fixture-session' } })
    else workspace = '/another-project'
    release?.()
    const result = await check
    expect(result).toMatchObject({ text: expect.stringContaining('discarded') })
    const status = await $.command.run({ command: 'blog-studio', args: 'status', ...RUN })
    expect(status).not.toMatchObject({ text: expect.stringContaining('Preflight passed') })
  })
}

test('trusted configuration is explicit and selected draft helpers cannot execute', async ($, on) => {
  host(on)
  let calls = 0
  on('process.run', () => { calls++; throw new Error('must not run') })
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
  await $.command.run({ command: 'blog-studio', args: 'select outputs/article', ...RUN })
  await $.command.run({ command: 'blog-studio', args: 'configure /work/outputs/article/scripts', ...RUN })
  const out = await $.command.run({ command: 'blog-studio', args: 'check', ...RUN })
  expect(out).toMatchObject({ text: expect.stringContaining('Execution error') })
  expect(calls).toBe(0)
})

test('classifier maps blog tool calls to ordered stages and ignores everything else', () => {
  const at = (tool: string, input: Record<string, unknown>) => classify(tool, input, '/work')
  expect(at('WebSearch', { query: 'x' })).toMatchObject({ kind: 'stage', stage: 'research' })
  expect(at('WebFetch', { url: 'https://example.com/a' })).toMatchObject({ stage: 'research', note: 'read example.com' })
  expect(at('Agent', { subagent_type: 'claude-blog:blog-reviewer' })).toMatchObject({ stage: 'review' })
  expect(at('Agent', { subagent_type: 'general-purpose' })).toBeNull()
  expect(at('Write', { file_path: '/work/out/post/outline.md' })).toMatchObject({ stage: 'outline' })
  expect(at('Write', { file_path: '/work/out/post/post.md' })).toMatchObject({ stage: 'draft', draft: 'out/post' })
  expect(at('Write', { file_path: '/work/BRAND.md' })).toBeNull()
  expect(at('Write', { file_path: '/elsewhere/post.md' })).toMatchObject({ stage: 'draft' })
  expect((at('Write', { file_path: '/elsewhere/post.md' }) as { draft?: string }).draft).toBeUndefined()
  expect(at('Write', { file_path: '/work/out/post/chart.svg' })).toMatchObject({ stage: 'visuals' })
  expect(at('Write', { file_path: '/work/out/post/review.md' })).toMatchObject({ stage: 'review' })
  expect(at('Bash', { command: 'python3 s/generate_hero.py --x' })).toMatchObject({ stage: 'visuals' })
  expect(at('Bash', { command: 'python3 s/blog_render.py --md a.md' })).toMatchObject({ stage: 'render' })
  expect(at('Bash', { command: 'python3 s/blog_preflight.py --draft d' })).toMatchObject({ stage: 'gates' })
  expect(at('Bash', { command: 'ls -la' })).toBeNull()
  expect(at('Read', { file_path: '/work/a.md' })).toBeNull()
  expect(skillSignal('claude-blog:blog-write')).toMatchObject({ kind: 'start' })
  expect(skillSignal('claude-blog:blog-outline')).toMatchObject({ stage: 'outline' })
  expect(skillSignal('commit')).toBeNull()
})

test('stages advance in order, finish earlier work, allow revisits, and restart on a new run', () => {
  let run = reduce(emptyRun('/work', 's'), { kind: 'start', skill: 'blog-write' }, 1000)
  run = reduce(run, { kind: 'stage', stage: 'research', note: 'a' }, 2000)
  run = reduce(run, { kind: 'stage', stage: 'draft', note: 'b' }, 5000)
  expect(run.stages.research).toMatchObject({ state: 'done', endedAt: 5000, n: 1 })
  expect(run.stages.draft).toMatchObject({ state: 'active', startedAt: 5000 })
  expect(run.stages.outline.state).toBe('pending')
  run = reduce(run, { kind: 'stage', stage: 'research', note: 'again' }, 6000)
  expect(run.stages.research).toMatchObject({ state: 'active', n: 2 })
  expect(doneCount(run)).toBe(0)
  run = fail(run, 'research', 7000)
  expect(run.stages.research.state).toBe('failed')
  run = reduce(run, { kind: 'start', skill: 'blog-rewrite' }, 9000)
  expect(run.stages.research.state).toBe('pending')
  expect(run.startedAt).toBe(9000)
})

test('view helpers stay inside their bounds', () => {
  expect(bar(0.5, 10)).toBe('━━━━━─────')
  expect(bar(2, 4)).toBe('━━━━')
  expect(bar(-1, 4)).toBe('────')
  expect(spark([0, 50, 100])).toBe('▁▅█')
  expect(duration(75_000)).toBe('1:15')
  expect(duration(null)).toBe('')
})

test('observers follow the agent through real hooks and never block a tool call', async ($, on) => {
  host(on)
  on('tool.call', () => ({ result: 'ok' }))
  on('process.run', () => ({ value: done({ exitCode: 0, stdout: JSON.stringify(PASS), stderr: '' }) }))
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
  await $.tool.call({ tool: 'WebSearch', query: 'topic', mode: 'standard' })
  const written = await $.tool.call({ tool: 'Write', file_path: '/work/outputs/post/post.md', content: 'x' })
  expect(written).toMatchObject({ result: 'ok' })
  const band = await $.ui.mount({ ...BAND, surface: 'terminal' })
  expect(await band.find({ type: 'Text', text: /Draft/ })).toBeDefined()
  expect(await band.find({ type: 'Text', text: /2\/7|1\/7/ })).toBeDefined()
  await band.unmount()
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  expect(await ui.find({ key: 'use-detected' })).toBeDefined()
  await ui.press({ key: 'use-detected' })
  expect(await ui.find({ key: 'check' })).toBeDefined()
  await ui.unmount()
})

test('a failing render marks that stage failed without changing the tool result', async ($, on) => {
  host(on)
  on('tool.call', () => ({ result: 'boom', isError: true }))
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
  const result = await $.tool.call({ tool: 'Bash', command: 'python3 blog_render.py --md a.md' })
  expect(result).toMatchObject({ result: 'boom', isError: true })
  const band = await $.ui.mount({ ...BAND, surface: 'terminal' })
  expect(await band.find({ type: 'Text', text: /Render/ })).toBeDefined()
  expect(await band.find({ type: 'Text', text: /✗/ })).toBeDefined()
  await band.unmount()
})

test('the same blocker from every viewport collapses to one line', () => {
  expect(groupViolations([
    'mobile: 1 console error', 'tablet: 1 console error', 'desktop: 1 console error', 'no hero image found',
  ])).toEqual(['mobile + tablet + desktop: 1 console error', 'no hero image found'])
  expect(groupViolations([])).toEqual([])
})

test('history entries are stable, merge without losing results, and sort newest first', () => {
  expect(entryId('/work', 'a')).toBe(entryId('/work', 'a'))
  expect(entryId('/work', 'a')).not.toBe(entryId('/work', 'b'))
  const known = { ...makeEntry('/work', 'a', 5000, 'checked', PASS as never), lastSeen: 5000 }
  const seen = makeEntry('/work', 'a', 9000, 'observed')
  const merged = mergeEntries([known], seen)
  expect(merged).toHaveLength(1)
  expect(merged[0]).toMatchObject({ lastSeen: 9000, firstSeen: 5000, status: 'passed', passed: 5, score: 90 })
  const old = makeEntry('/work', 'old', 1000, 'scan', null, 1000)
  expect(sortEntries([old, known, seen]).map(e => e.draft)).toEqual(['a', 'a', 'old'])
  expect(formatWhen(new Date(2026, 9, 8, 19, 5).getTime())).toBe('10-08 19:05')
})

test('history validation rejects unsafe or malformed records', () => {
  const good = makeEntry('/work', 'outputs/a', 1, 'observed')
  expect(validEntry(good)).toBe(true)
  expect(validEntry({ ...good, root: 'relative' })).toBe(false)
  expect(validEntry({ ...good, draft: '../escape' })).toBe(false)
  expect(validEntry({ ...good, draft: '/abs' })).toBe(false)
  expect(validEntry({ ...good, lastSeen: 'x' })).toBe(false)
  expect(validEntry(null)).toBe(false)
})

test('absolute draft folders split into a project root and a relative draft', () => {
  expect(splitDraft('/work/outputs/a', '/work')).toEqual({ root: '/work', draft: 'outputs/a' })
  expect(splitDraft('/other/proj/blog-a', '/work')).toEqual({ root: '/other/proj', draft: 'blog-a' })
  expect(splitDraft('/lonely', '/work')).toBeNull()
  expect(parseFound('1760000000.5\t/x/a\nbad line\n1770000000\t/x/b\n1770000001\trelative\n'))
    .toEqual([{ path: '/x/b', mtimeMs: 1770000000000 }, { path: '/x/a', mtimeMs: 1760000000500 }])
})

test('history follows the agent, backfills by scan, and opens a past blog in another project', async ($, on) => {
  host(on)
  on('tool.call', () => ({ result: 'ok' }))
  const argvs: string[][] = []
  on('process.run', ($$, e) => {
    argvs.push([...e.argv])
    if (e.argv[0] === 'find') return { value: done({ exitCode: 0, stderr: '', stdout: '1760000000.0\t/other/proj/blog-a\n' }) }
    const isChecker = e.argv[1]?.endsWith('blog_preflight.py')
    return { value: done({ exitCode: 0, stderr: '', stdout: JSON.stringify(isChecker ?
      { strict: true, blocked: false, draft: '/other/proj/blog-a', evidence: { run_id: PASS.run_id } } : PASS) }) }
  })
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
  await $.tool.call({ tool: 'Write', file_path: '/work/outputs/post/post.md', content: 'x' })
  let listed = await $.command.run({ command: 'blog-studio', args: 'history', ...RUN })
  expect(listed).toMatchObject({ text: expect.stringContaining('post') })
  const scanned = await $.command.run({ command: 'blog-studio', args: 'history scan /other', ...RUN })
  expect(scanned).toMatchObject({ text: expect.stringContaining('added 1 draft') })
  expect(argvs.find(a => a[0] === 'find')).toEqual(expect.arrayContaining(['/other', '-maxdepth', '7', '-name', 'preflight-report.json']))
  listed = await $.command.run({ command: 'blog-studio', args: 'history', ...RUN })
  const text = (listed as { text: string }).text
  expect(text.indexOf('post')).toBeLessThan(text.indexOf('blog-a'))
  const opened = await $.command.run({ command: 'blog-studio', args: 'open 2', ...RUN })
  expect(opened).toMatchObject({ text: expect.stringContaining('Project root: /other/proj') })
  await $.command.run({ command: 'blog-studio', args: 'check', ...RUN })
  const checker = argvs.find(a => a[1]?.endsWith('blog_preflight.py'))
  expect(checker).toEqual(expect.arrayContaining(['--draft', '/other/proj/blog-a', '--project-root', '/other/proj']))
  const missing = await $.command.run({ command: 'blog-studio', args: 'open 9', ...RUN })
  expect(missing).toMatchObject({ text: expect.stringContaining('No blog number 9') })
})

test('the history list in the panel opens a blog and an unsafe stored record is refused', async ($, on) => {
  host(on, { link: '/other/proj/blog-a' })
  on('tool.call', () => ({ result: 'ok' }))
  on('process.run', ($$, e) => ({ value: done({ exitCode: 0, stderr: '', stdout: e.argv[0] === 'find'
    ? '1760000000.0\t/other/proj/blog-a\n1750000000.0\t/other/proj/blog-b\n' : JSON.stringify(PASS) }) }))
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
  await $.command.run({ command: 'blog-studio', args: 'history scan /other', ...RUN })
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  const rows = await ui.findAll({ type: 'Button', text: /blog-/ })
  expect(rows.length).toBe(2)
  const refused = await $.command.run({ command: 'blog-studio', args: 'open 1', ...RUN })
  expect(refused).toMatchObject({ text: expect.stringContaining('unsafe path') })
  const fine = await $.command.run({ command: 'blog-studio', args: 'open 2', ...RUN })
  expect(fine).toMatchObject({ text: expect.stringContaining('blog-b') })
  await ui.unmount()
})

test('the engine location is remembered across sessions and can be forgotten', async ($, on) => {
  let sessionId = 'one'
  const argvs: string[][] = []
  host(on, { env: null, sessionId: () => sessionId })
  on('process.run', ($$, e) => {
    argvs.push([...e.argv])
    const isChecker = e.argv[1]?.endsWith('blog_preflight.py')
    return { value: done({ exitCode: 0, stderr: '', stdout: JSON.stringify(isChecker ?
      { strict: true, blocked: false, draft: '/work/outputs/article', evidence: { run_id: PASS.run_id } } : PASS) }) }
  })
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
  const set = await $.command.run({ command: 'blog-studio', args: 'configure /trusted/scripts', ...RUN })
  expect(set).toMatchObject({ text: expect.stringContaining('remembered') })
  sessionId = 'two'
  await $.command.run({ command: 'blog-studio', args: 'select outputs/article', ...RUN })
  await $.command.run({ command: 'blog-studio', args: 'check', ...RUN })
  expect(argvs.some(a => a[1] === '/trusted/scripts/blog_preflight.py')).toBe(true)
  const cleared = await $.command.run({ command: 'blog-studio', args: 'configure reset', ...RUN })
  expect(cleared).toMatchObject({ text: expect.stringContaining('cleared') })
  sessionId = 'three'
  await $.command.run({ command: 'blog-studio', args: 'select outputs/article', ...RUN })
  const refused = await $.command.run({ command: 'blog-studio', args: 'check', ...RUN })
  expect(refused).toMatchObject({ text: expect.stringContaining('Configure the trusted claude-blog scripts directory first') })
})

test('generic folder names lead with their project, and forgetting removes only the history record', async ($, on) => {
  expect(title({ root: '/x/YouTube Scout', name: '03-article' })).toBe('YouTube Scout / 03-article')
  expect(title({ root: '/x/post', name: 'post' })).toBe('post')
  host(on)
  on('tool.call', () => ({ result: 'ok' }))
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
  await $.tool.call({ tool: 'Write', file_path: '/work/outputs/post/post.md', content: 'x' })
  const gone = await $.command.run({ command: 'blog-studio', args: 'history forget 1', ...RUN })
  expect(gone).toMatchObject({ text: expect.stringContaining('files were not touched') })
  const after = await $.command.run({ command: 'blog-studio', args: 'history', ...RUN })
  expect(after).toMatchObject({ text: expect.stringContaining('no blogs in the history yet') })
  const bad = await $.command.run({ command: 'blog-studio', args: 'history forget 7', ...RUN })
  expect(bad).toMatchObject({ text: expect.stringContaining('Give the number') })
})
