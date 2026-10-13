import type { EngineInterface, Register, Timer } from 'claude-code'
import type { HistoryEntry, HistoryState, RunState, StudioState, Status } from '../types'
import { absoluteRoot, absoluteScripts, clean, EMPTY, jsonResponse, parseStatus, relativeDraft, summary } from './logic'
import { classify, demoRun, emptyRun, fail, pause, reduce, skillSignal, type Signal } from './pipeline'
import { formatWhen, KEY_PREFIX, makeEntry, MAX_SHOWN, MAX_STORED, mergeEntries, parseFound, sortEntries, splitDraft, statusGlyph, title, validEntry } from './history'
import { bandDetail, bandRow, effective, el, pane, pipelineLine, type PaneActions } from './view'

const PANE = 'blog-studio-review'
const REF = { plugin: 'blog-studio', key: 'studio' } as const
const RUN = { plugin: 'blog-studio', key: 'run' } as const
const HIST = { plugin: 'blog-studio', key: 'history' } as const
const CONFIG = 'config'
const HELPER = 'blog_studio_status.py'
const CHECKER = 'blog_preflight.py'

async function held($: EngineInterface) {
  const result = await $.state.get(REF)
  return { value: result.value ?? { ...EMPTY }, version: result.version }
}

async function heldRun($: EngineInterface) {
  const result = await $.state.get(RUN)
  return { value: result.value ?? emptyRun(), version: result.version }
}

// Display-only bookkeeping: a lost race only drops one counter tick, so retry twice and give up quietly.
async function updateRun($: EngineInterface, change: (run: RunState) => RunState) {
  for (let attempt = 0; attempt < 3; attempt++) {
    const current = await heldRun($)
    let base = current.value
    if (!base.workspace) base = { ...base, workspace: (await $.session.root()).replace(/\/$/, '') || '/', sessionId: await $.session.id() }
    if ((await $.state.set(RUN, change(base), { ifVersion: current.version })).isSet) return
  }
}

let ticker: Timer | null = null

function startTicker($: EngineInterface) {
  if (ticker) return
  ticker = $.clock.every(1000, () => { $.ui.invalidate('ui.render') })
}

function stopTicker() {
  ticker?.cancel()
  ticker = null
}

const rootOf = (s: StudioState) => s.projectRoot ?? s.workspace

async function heldHistory($: EngineInterface) {
  const result = await $.state.get(HIST)
  return { value: result.value ?? { entries: [], loaded: false } as HistoryState, version: result.version }
}

async function publishHistory($: EngineInterface, change: (entries: HistoryEntry[]) => HistoryEntry[]) {
  for (let attempt = 0; attempt < 3; attempt++) {
    const current = await heldHistory($)
    const entries = change(current.value.entries).slice(0, MAX_SHOWN)
    if ((await $.state.set(HIST, { entries, loaded: true }, { ifVersion: current.version })).isSet) return
  }
}

// Durable history lives in $.store, one key per draft folder. $.state mirrors the newest few so drawing never does I/O.
async function loadHistory($: EngineInterface) {
  const keys = (await $.store.keys()).filter(k => k.startsWith(KEY_PREFIX))
  const entries: HistoryEntry[] = []
  for (const key of keys) { const v = await $.store.get(key); if (validEntry(v)) entries.push(v) }
  const sorted = sortEntries(entries)
  await publishHistory($, () => sorted)
}

async function recordEntries($: EngineInterface, incoming: HistoryEntry[]) {
  const merged: HistoryEntry[] = []
  for (const entry of incoming) {
    const old = await $.store.get(KEY_PREFIX + entry.id)
    const next = mergeEntries(validEntry(old) ? [old] : [], entry)[0]
    if (!next) continue
    await $.store.set(KEY_PREFIX + next.id, next)
    merged.push(next)
  }
  const keys = (await $.store.keys()).filter(k => k.startsWith(KEY_PREFIX))
  if (keys.length > MAX_STORED) {
    const all: HistoryEntry[] = []
    for (const key of keys) { const v = await $.store.get(key); if (validEntry(v)) all.push(v); else await $.store.delete(key) }
    for (const stale of sortEntries(all).slice(MAX_STORED)) await $.store.delete(KEY_PREFIX + stale.id)
  }
  await publishHistory($, entries => merged.reduce(mergeEntries, entries))
}

async function remember($: EngineInterface, entry: HistoryEntry) {
  try { await recordEntries($, [entry]) } catch { /* history is a convenience, never a failure */ }
}

async function savedScripts($: EngineInterface): Promise<string | null> {
  try {
    const value = await $.store.get(CONFIG)
    const scripts = value && typeof value === 'object' ? (value as { scripts?: unknown }).scripts : null
    return typeof scripts === 'string' ? absoluteScripts(scripts) : null
  } catch { return null }
}

async function context($: EngineInterface) {
  const current = await held($)
  const workspace = (await $.session.root()).replace(/\/$/, '') || '/'
  const sessionId = await $.session.id()
  if (current.value.workspace === workspace && current.value.sessionId === sessionId) return current
  const pinned = await $.env.get('CLAUDE_BLOG_SCRIPTS_DIR')
  const value = { ...EMPTY, workspace, sessionId, generation: current.value.generation + 1,
    scripts: pinned ? absoluteScripts(pinned) : await savedScripts($) }
  const written = await $.state.set(REF, value, { ifVersion: current.version })
  if (!written.isSet) throw new Error('Session changed. Try again.')
  return { value, version: written.version }
}

async function noLinks($: EngineInterface, absolute: string, kind: 'file' | 'dir') {
  let path = ''
  const parts = absolute.split('/').filter(Boolean)
  for (let i = 0; i < parts.length; i++) {
    path += '/' + parts[i]
    const info = await $.fs.stat(path).catch(() => undefined)
    if (!info || info.isLink || info.kind !== (i === parts.length - 1 ? kind : 'dir')) {
      throw new Error('Missing or unsafe path. Symlinks are refused.')
    }
  }
}

async function prepare($: EngineInterface, s: StudioState) {
  if (!s.scripts) throw new Error('Configure the trusted claude-blog scripts directory first.')
  if (!s.draft) throw new Error('Select a draft first.')
  const root = rootOf(s)
  const draft = (root === '/' ? '' : root) + '/' + relativeDraft(s.draft)
  const scripts = absoluteScripts(s.scripts)
  if (scripts === draft || scripts.startsWith(draft + '/')) throw new Error('Executable helpers cannot come from the selected draft.')
  await noLinks($, draft, 'dir')
  await noLinks($, scripts + '/' + HELPER, 'file')
  await noLinks($, scripts + '/' + CHECKER, 'file')
  return { draft, scripts }
}

function response(raw: { stdout: string; stderr: string; exitCode: number }): string {
  const flags = raw as typeof raw & { isStdoutTruncated?: boolean; isStderrTruncated?: boolean }
  if (flags.isStdoutTruncated || flags.isStderrTruncated || raw.stdout.length >= 4 * 1024 * 1024) {
    throw new Error('Checker output was truncated. No passing result was accepted. ' + clean(raw.stderr))
  }
  return raw.stdout
}

async function inspect($: EngineInterface, s: StudioState, runId?: string): Promise<Status> {
  const paths = await prepare($, s)
  const args = ['python3', paths.scripts + '/' + HELPER, '--draft', paths.draft, '--project-root', rootOf(s)]
  if (runId) args.push('--expected-run', runId)
  const out = await $.process.run(args, { cwd: rootOf(s), timeoutMs: 30_000 })
  const status = parseStatus(response(out), out.stderr)
  if (out.exitCode !== 0 && status.status !== 'error') throw new Error('Status inspector failed.')
  return status
}

async function perform($: EngineInterface, check: boolean): Promise<string> {
  const snapshot = await context($)
  const s = snapshot.value
  if (s.busy) return 'Checks are already running.'
  // Reserve this state version before any process starts. A later selection,
  // reset or reload changes the version, so this operation cannot publish late.
  const reservation = await $.state.set(REF, { ...s, busy: true, message: check ? 'Running checks...' : 'Refreshing evidence...' }, { ifVersion: snapshot.version })
  if (!reservation.isSet) return 'State changed. Try again.'
  let status: Status | null = null
  let message: string | null = null
  try {
    let runId: string | undefined
    if (check) {
      const paths = await prepare($, s)
      const tools = (await $.tool.list()).map(t => t.name)
      const out = await $.process.run(['python3', paths.scripts + '/' + CHECKER, '--draft', paths.draft,
        '--strict', '--json', '--tools-json', JSON.stringify(tools), '--project-root', rootOf(s)], { cwd: rootOf(s), timeoutMs: 600_000 })
      const report = jsonResponse(response(out), out.stderr)
      if (!report || typeof report !== 'object') throw new Error('Checker returned no valid report.')
      const r = report as { evidence?: { run_id?: unknown }; strict?: unknown; blocked?: unknown; draft?: unknown }
      if (r.strict !== true || r.draft !== paths.draft || typeof r.blocked !== 'boolean' ||
          (out.exitCode !== 0 && out.exitCode !== 1) || (out.exitCode === 0) === r.blocked ||
          typeof r.evidence?.run_id !== 'string' || !/^[0-9a-f]{32}$/.test(r.evidence.run_id)) {
        throw new Error('Checker exit status or report was inconsistent. ' + clean(out.stderr))
      }
      runId = r.evidence.run_id
    }
    status = await inspect($, s, runId)
  } catch (error) {
    message = clean(error instanceof Error ? error.message : String(error))
    status = { schema_version: 1, status: 'error', label: 'Execution error', checked_at: null,
      passed_count: 0, gates: [], artifacts: [], diagnostics: [message] }
  }
  if (((await $.session.root()).replace(/\/$/, '') || '/') !== s.workspace || await $.session.id() !== s.sessionId) return 'Previous check finished after the session changed; its result was discarded.'
  const final = { ...s, busy: false, status, message }
  const written = await $.state.set(REF, final, { ifVersion: reservation.version })
  if (written.isSet && s.draft) {
    const result = status.status === 'error' ? null : status
    await remember($, makeEntry(rootOf(s), s.draft, Date.now(), check ? 'checked' : 'selected', result))
    const score = status.gates.find(g => g.gate === 4)?.score
    if (check && typeof score === 'number') {
      try { await updateRun($, run => (run.scores.at(-1) === score ? run : { ...run, scores: [...run.scores, score].slice(-8) })) } catch { /* display only */ }
    }
  }
  return written.isSet ? summary(final) : 'Previous check result was discarded after a state change.'
}

async function select($: EngineInterface, raw: string): Promise<string> {
  const current = await context($)
  const s = current.value
  if (s.busy) throw new Error('Wait for the current check before changing the selection.')
  const draft = relativeDraft(raw)
  await noLinks($, (s.workspace === '/' ? '' : s.workspace) + '/' + draft, 'dir')
  const next = { ...s, draft, projectRoot: null, status: null, message: null, generation: s.generation + 1 }
  if (!(await $.state.set(REF, next, { ifVersion: current.version })).isSet) throw new Error('Selection changed. Try again.')
  await remember($, makeEntry(s.workspace, draft, Date.now(), 'selected'))
  return summary(next)
}

// A past blog may live in another project. Its recorded root is re-validated like a fresh selection,
// and the checks run anchored to that root, which the panel shows.
async function open($: EngineInterface, entry: HistoryEntry): Promise<string> {
  const current = await context($)
  const s = current.value
  if (s.busy) throw new Error('Wait for the current check before changing the selection.')
  const root = absoluteRoot(entry.root)
  const draft = relativeDraft(entry.draft)
  await noLinks($, root, 'dir')
  await noLinks($, (root === '/' ? '' : root) + '/' + draft, 'dir')
  const next = { ...s, draft, projectRoot: root === s.workspace ? null : root, status: null, message: null, generation: s.generation + 1 }
  if (!(await $.state.set(REF, next, { ifVersion: current.version })).isSet) throw new Error('Selection changed. Try again.')
  await remember($, { ...entry, lastSeen: Date.now(), source: 'selected', status: null })
  return summary(next) + (next.projectRoot ? '\nProject root: ' + clean(next.projectRoot, 200) : '')
}

async function pick($: EngineInterface, ref: string): Promise<string> {
  const entries = (await heldHistory($)).value.entries
  const number = /^[0-9]{1,3}$/.test(ref) ? Number(ref) : 0
  const entry = number ? entries[number - 1] : entries.find(e => e.id === ref)
  if (!entry) throw new Error(number ? 'No blog number ' + number + '. Run /blog-studio history.' : 'That blog is no longer in the history.')
  return open($, entry)
}

function historyText(entries: HistoryEntry[]): string {
  if (!entries.length) return 'Blog Studio: no blogs in the history yet. They are added as the agent writes or you select them. Backfill with /blog-studio history scan <folder>.'
  return 'Blog Studio history (newest first):\n' + entries.slice(0, 20).map((e, i) =>
    String(i + 1).padStart(2) + '. ' + formatWhen(e.lastSeen) + ' ' + statusGlyph(e.status) + ' ' + title(e) +
    (e.status ? ' ' + e.passed + '/5 gates' : '')).join('\n') +
    '\nOpen one with /blog-studio open <number>. Remove one with /blog-studio history forget <number>.'
}

async function forget($: EngineInterface, ref: string): Promise<string> {
  const entries = (await heldHistory($)).value.entries
  const number = /^[0-9]{1,3}$/.test(ref) ? Number(ref) : 0
  const entry = number ? entries[number - 1] : undefined
  if (!entry) throw new Error('Give the number from /blog-studio history.')
  await $.store.delete(KEY_PREFIX + entry.id)
  await publishHistory($, list => list.filter(e => e.id !== entry.id))
  return 'Blog Studio: removed ' + title(entry) + ' from the history. The files were not touched.'
}

async function scan($: EngineInterface, raw: string): Promise<string> {
  const s = (await context($)).value
  const root = raw ? absoluteRoot(raw) : s.workspace
  await noLinks($, root, 'dir')
  const out = await $.process.run(['find', root, '-maxdepth', '7', '-name', 'preflight-report.json', '-not', '-path', '*/node_modules/*',
    '-not', '-path', '*/.*', '-printf', '%T@\\t%h\\n'], { cwd: s.workspace, timeoutMs: 30_000 })
  if (out.exitCode !== 0 && !out.stdout) throw new Error('Scan failed. It needs GNU find. ' + clean(out.stderr, 200))
  const now = Date.now()
  const entries = parseFound(out.stdout, 100).flatMap(row => {
    const place = splitDraft(row.path, s.workspace)
    return place ? [makeEntry(place.root, place.draft, now, 'scan', null, row.mtimeMs)] : []
  })
  if (!entries.length) return 'Blog Studio: no delivered drafts found under ' + clean(root, 120) + '.'
  await recordEntries($, entries)
  return 'Blog Studio: added ' + entries.length + ' draft' + (entries.length === 1 ? '' : 's') + ' from ' + clean(root, 120) + '. Run /blog-studio history.'
}

async function configure($: EngineInterface, raw: string): Promise<string> {
  const current = await context($)
  const s = current.value
  if (s.busy) throw new Error('Wait for the current check before configuring helpers.')
  if (raw.trim() === 'reset') {
    await $.store.delete(CONFIG)
    const pinned = await $.env.get('CLAUDE_BLOG_SCRIPTS_DIR')
    const cleared = { ...s, scripts: pinned ? absoluteScripts(pinned) : null, status: null, message: null, generation: s.generation + 1 }
    if (!(await $.state.set(REF, cleared, { ifVersion: current.version })).isSet) throw new Error('Configuration changed. Try again.')
    return 'Blog Studio: remembered engine location cleared.'
  }
  const scripts = absoluteScripts(raw)
  await noLinks($, scripts + '/' + HELPER, 'file')
  await noLinks($, scripts + '/' + CHECKER, 'file')
  const next = { ...s, scripts, status: null, message: null, generation: s.generation + 1 }
  if (!(await $.state.set(REF, next, { ifVersion: current.version })).isSet) throw new Error('Configuration changed. Try again.')
  await $.store.set(CONFIG, { scripts })
  return 'Trusted blog-engine helpers configured and remembered for every session. /blog-studio configure reset forgets them.'
}

async function uiAction($: EngineInterface, action: () => Promise<unknown>) {
  try { await action() } catch (error) {
    $.ui.toast(clean(error instanceof Error ? error.message : String(error)))
  }
}

function paneActions($: EngineInterface): PaneActions {
  return {
    refresh: async () => { await uiAction($, () => perform($, false)) },
    check: async () => { await uiAction($, () => perform($, true)) },
    useDetected: async () => {
      await uiAction($, async () => {
        const run = (await heldRun($)).value
        if (run.detected) await select($, run.detected)
      })
    },
    toggleSetup: async () => { await updateRun($, run => ({ ...run, setup: !run.setup })) },
    toggleHistory: async () => { await updateRun($, run => ({ ...run, historyOpen: !run.historyOpen })) },
    openEntry: async (id: string) => { await uiAction($, () => pick($, id)) },
    selectDraft: async value => { await uiAction($, () => select($, value)) },
    configureScripts: async value => { await uiAction($, () => configure($, value)) },
    close: async () => { await $.ui.close({ id: PANE }) },
  }
}

async function observe($: EngineInterface, signal: Signal | null) {
  if (!signal) return
  await updateRun($, run => reduce(run, signal, Date.now()))
  startTicker($)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const current = await context($)
    const s = current.value
    // Reload preserves selection but invalidates in-flight work and cached proof.
    await $.state.set(REF, { ...s, busy: false, status: null, message: null, generation: s.generation + 1 }, { ifVersion: current.version })
    try { if (!(await heldHistory($)).value.loaded) await loadHistory($) } catch { /* history is a convenience */ }
    try {
      await $.command.register({ name: 'blog-studio', description: 'Open the blog pipeline and delivery checks',
        argumentHint: '[status|select <directory>|open <n>|history [scan <folder>|forget <n>]|configure <scripts>|refresh|check|demo|reset]', immediate: true })
    } catch { $.ui.toast('Blog Studio could not register /blog-studio because the name is already taken.') }
    return next(e)
  })
  on('session.end', async ($, e, next) => {
    stopTicker()
    const current = await held($)
    await $.state.set(REF, { ...EMPTY, generation: current.value.generation + 1 })
    await $.state.set(RUN, emptyRun())
    return next(e)
  })
  on('turn.start', async ($, e, next) => {
    const current = await held($)
    if (current.value.draft && !current.value.busy) {
      await $.state.set(REF, { ...current.value, status: null, message: 'Refresh evidence after this turn.' }, { ifVersion: current.version })
    }
    return next(e)
  })
  on('turn.complete', async ($, e, next) => {
    if (!e.agentId) {
      stopTicker()
      try { await updateRun($, run => (run.startedAt === null ? run : pause(run, Date.now()))) } catch { /* display only */ }
    }
    const current = await held($)
    if (current.value.draft && !current.value.busy) await perform($, false)
    return next(e)
  })
  // Observers: read-only, no model calls, and they always fall through to the real call.
  on('skill.prompt', async ($, e, next) => {
    try { await observe($, skillSignal(e.skill)) } catch { /* display only */ }
    return next(e)
  })
  on('tool.call', async ($, e, next) => {
    let signal: Signal | null = null
    try {
      const run = (await heldRun($)).value
      const workspace = run.workspace || (await $.session.root()).replace(/\/$/, '')
      signal = classify(e.tool, e as unknown as Record<string, unknown>, workspace)
      await observe($, signal)
      if (signal?.kind === 'stage' && signal.draft && signal.draft !== run.detected) {
        await remember($, makeEntry(workspace || '/', signal.draft, Date.now(), 'observed'))
      }
    } catch { signal = null }
    const result = await next(e)
    if (signal?.kind === 'stage' && (signal.stage === 'render' || signal.stage === 'gates') &&
        (result as { isError?: boolean }).isError) {
      const stage = signal.stage
      try { await updateRun($, run => fail(run, stage, Date.now())) } catch { /* display only */ }
    }
    return result
  })
  on('command.run', { command: 'blog-studio' }, async ($, e) => {
    try {
      const input = e.args.trim()
      const space = input.indexOf(' ')
      const action = space < 0 ? input : input.slice(0, space)
      const value = space < 0 ? '' : input.slice(space + 1).trim()
      if (action === 'select') return { text: await select($, value) }
      if (action === 'configure') return { text: await configure($, value) }
      if (action === 'history') {
        if (value.startsWith('scan')) return { text: await scan($, value.slice(4).trim()) }
        if (value.startsWith('forget')) return { text: await forget($, value.slice(6).trim()) }
        return { text: historyText((await heldHistory($)).value.entries) }
      }
      if (action === 'open') return { text: await pick($, value) }
      if (action === 'demo') {
        await updateRun($, run => demoRun(run, Date.now()))
        startTicker($)
        return { text: 'Blog Studio: showing a sample pipeline. Run /blog-studio reset to clear it.' }
      }
      if (action === 'reset') {
        stopTicker()
        await updateRun($, run => ({ ...emptyRun(run.workspace, run.sessionId), setup: run.setup, historyOpen: run.historyOpen }))
        return { text: 'Blog Studio: pipeline cleared.' }
      }
      if (action === 'check' || action === 'refresh') return { text: await perform($, action === 'check') }
      const text = async () => {
        const s = (await context($)).value
        const run = (await heldRun($)).value
        return summary(s) + (run.startedAt === null ? '' : '\n' + pipelineLine(effective(run, s.status, s.busy, Date.now())))
      }
      if (action === 'status') return { text: await text() }
      if (action) return { text: 'Usage: /blog-studio [status|select <directory>|open <n>|history [scan <folder>|forget <n>]|configure <scripts>|refresh|check|demo|reset]' }
      const surfaces = await $.session.surfaces()
      if (!surfaces.some(surface => surface === 'terminal' || surface === 'desktop')) {
        return { text: (await text()) + '\nThis surface has no Blog Studio panel. Use the text subcommands.' }
      }
      const opened: unknown = await $.ui.open({ id: PANE, title: 'Blog Studio', focus: true, closeOnEscape: true })
      return opened && typeof opened === 'object' && 'isPlaced' in opened && opened.isPlaced === true ? {} : { text: (await text()) + '\nPanel unavailable. Use the text subcommands.' }
    } catch (error) { return { text: 'Blog Studio: ' + clean(error instanceof Error ? error.message : String(error)) } }
  })
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const s = (await held($)).value
    const run = (await heldRun($)).value
    const tracked = run.startedAt !== null
    if ((!s.draft && !tracked) || e.props.hasSurvey || e.props.maxRows < 2 || (e.surface !== 'terminal' && e.surface !== 'desktop')) return next(e)
    const ui = $.ui.resolve(e)
    const theirs = await next(e)
    const now = Date.now()
    const stages = effective(run, s.status, s.busy, now)
    const detail = e.props.maxRows >= 3 ? bandDetail(s, run, stages, e.props.bodyColumns) : null
    return ui.Box({ flexDirection: 'column', children: [theirs,
      ui.Box({ flexDirection: 'row', children: [
        ui.Box({ flexDirection: 'row', flexGrow: 1, children: bandRow(s, run, stages, e.props.bodyColumns - 14, now).map(seg => el(ui, seg)) }),
        ui.Button({ key: 'open-studio', label: 'Open (o)', hotkey: 'o', onPress: async () => {
          await uiAction($, () => $.ui.open({ id: PANE, title: 'Blog Studio', focus: true, closeOnEscape: true }))
        } }),
      ] }),
      ...(detail ? [el(ui, { t: detail, dim: true })] : []),
    ] })
  })
  on('ui.render', { component: 'Pane' }, async ($, e, next) => {
    if (e.requestId !== PANE || (e.surface !== 'terminal' && e.surface !== 'desktop')) return next(e)
    const s = (await held($)).value
    const run = (await heldRun($)).value
    const ui = $.ui.resolve(e)
    const now = Date.now()
    const history = (await heldHistory($)).value.entries
    return pane(ui, s, run, effective(run, s.status, s.busy, now), history, Math.max(24, e.props.bodyColumns - 2), now, paneActions($))
  })
}
