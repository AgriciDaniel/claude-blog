import type { EngineInterface, ThemeKey } from 'claude-code'
import type { HistoryEntry, RunState, StageId, StageState, Status, StudioState } from '../types'
import { clean } from './logic'
import { formatWhen, statusGlyph, title } from './history'
import { STAGES } from './pipeline'

type Full = Extract<ReturnType<EngineInterface['ui']['resolve']>, { Input: unknown }>
type Ui = Pick<Full, 'Box' | 'Text' | 'Button'>
type TextProps = Parameters<Ui['Text']>[0]

export type Seg = { t: string; c?: ThemeKey; dim?: boolean; bold?: boolean }
export type EffStage = {
  id: StageId; label: string; state: StageState; word: string; n: number; ms: number | null
  note: string | null; evidence: boolean
}

const rootOf = (s: StudioState) => s.projectRoot ?? s.workspace

export const GLYPH: Record<StageState, string> = { done: '✓', active: '▸', failed: '✗', pending: '·' }
const COLOR: Record<StageState, ThemeKey> = { done: 'success', active: 'claude', failed: 'error', pending: 'inactive' }
const GATE_NAMES = ['Capability Discovery', 'Format Completeness', 'Visual Verification', 'Content Review', 'Asset + Link Integrity']
const SPARK = '▁▂▃▄▅▆▇█'

/** Collapses the same finding reported once per viewport into one line: "mobile + tablet: message". */
export function groupViolations(list: string[]): string[] {
  const order: string[] = []
  const seen = new Map<string, string[]>()
  for (const v of list) {
    const m = /^(mobile|tablet|desktop(?:-dark)?):\s*([\s\S]*)$/.exec(v)
    const key = m?.[2] ?? v
    if (!seen.has(key)) { seen.set(key, []); order.push(key) }
    if (m?.[1]) seen.get(key)?.push(m[1])
  }
  return order.map(key => { const where = seen.get(key) ?? []; return where.length ? where.join(' + ') + ': ' + key : key })
}

export function bar(fraction: number, width: number): string {
  const w = Math.max(0, width)
  const filled = Math.max(0, Math.min(w, Math.round(fraction * w)))
  return '━'.repeat(filled) + '─'.repeat(w - filled)
}

export function spark(values: number[]): string {
  return values.slice(-8).map(v => SPARK[Math.max(0, Math.min(7, Math.floor(v / 12.5)))]).join('')
}

export function duration(ms: number | null): string {
  if (ms === null || ms < 0) return ''
  const total = Math.floor(ms / 1000)
  return Math.floor(total / 60) + ':' + String(total % 60).padStart(2, '0')
}

/** Combines what the agent was seen doing (inference) with what the preflight proved (evidence). */
export function effective(run: RunState, status: Status | null, busy: boolean, now: number): EffStage[] {
  const gate = (n: number) => status?.gates.find(g => g.gate === n)
  const rows = STAGES.map(({ id, label }) => {
    const cur = run.stages[id]
    let state = cur.state
    let word = state === 'done' ? 'done' : state === 'active' ? (run.working ? 'working' : 'paused')
      : state === 'failed' ? 'failed' : 'waiting'
    let evidence = false
    if (status?.status === 'passed') { state = 'done'; word = 'verified'; evidence = true }
    else {
      const proved = (id === 'visuals' || id === 'render') ? gate(2)?.passed && gate(3)?.passed !== false
        : id === 'review' ? gate(4)?.passed : false
      if (proved && state !== 'done') { state = 'done'; word = 'verified'; evidence = true }
      if (id === 'gates') {
        if (busy) { state = 'active'; word = 'checking' }
        else if (status?.status === 'blocked' || status?.status === 'error') { state = 'failed'; word = status.status === 'error' ? 'error' : 'blocked' }
        else if (status?.status === 'stale') { state = 'pending'; word = 'stale' }
        else if (status?.status === 'partial') { state = 'active'; word = 'partial' }
      }
    }
    const ms = cur.startedAt === null ? null : (cur.endedAt ?? now) - cur.startedAt
    return { id, label, state, word, n: cur.n, ms: state === 'pending' ? null : ms, note: cur.note, evidence }
  })
  return rows
}

export function ratio(stages: EffStage[]): { done: number; fraction: number } {
  const done = stages.filter(s => s.state === 'done').length
  const active = stages.some(s => s.state === 'active') ? 0.5 : 0
  return { done, fraction: (done + active) / stages.length }
}

export function glyphRail(stages: EffStage[]): string {
  return stages.map(s => GLYPH[s.state]).join('')
}

export function pipelineLine(stages: EffStage[]): string {
  return 'Pipeline: ' + stages.map(s => GLYPH[s.state] + s.label).join(' ')
}

function chip(status: Status | null, busy: boolean): Seg {
  if (busy) return { t: 'Checking', c: 'claude' }
  const label = status?.label ?? 'Unverified'
  const c: ThemeKey = status?.status === 'passed' ? 'success' : status?.status === 'blocked' || status?.status === 'error' ? 'error'
    : status?.status === 'stale' || status?.status === 'partial' ? 'warning' : 'inactive'
  return { t: label, c }
}

export function el(ui: Ui, seg: Seg, wrap: 'truncate-end' | 'wrap' = 'truncate-end') {
  const props: TextProps = { wrap, children: [seg.t] }
  if (seg.c) props.color = seg.c
  if (seg.dim) props.dimColor = true
  if (seg.bold) props.bold = true
  return ui.Text(props)
}

function row(ui: Ui, segs: Seg[], gap = 0) {
  return ui.Box({ flexDirection: 'row', gap, children: segs.map(s => el(ui, s)) })
}

function railSegs(stages: EffStage[], labels: boolean): Seg[] {
  const out: Seg[] = []
  stages.forEach((s, i) => {
    out.push({ t: GLYPH[s.state] + (labels ? ' ' + s.label : ''), c: COLOR[s.state], bold: s.state === 'active' })
    if (labels && i < stages.length - 1) out.push({ t: ' ' })
  })
  return out
}

/** One band row. Wide: bar, labelled rail, clock. Medium: bar, glyph rail. Narrow: glyph rail and stage. */
export function bandRow(s: StudioState, run: RunState, stages: EffStage[], columns: number, now: number): Seg[] {
  const tracked = run.startedAt !== null
  const status = s.status
  const clock = tracked ? duration((run.endedAt ?? now) - (run.startedAt ?? now)) : ''
  const title: Seg[] = [{ t: 'Blog ', c: 'claude', bold: true }]
  if (!tracked) {
    const c = chip(status, s.busy)
    return [...title, { t: '▎ ', c: 'inactive' }, { t: clean(s.draft ?? '', Math.max(8, columns - 40)), dim: true },
      { t: '  ' }, c, { t: ' ' + (status?.passed_count ?? 0) + '/5', dim: true }]
  }
  const { done, fraction } = ratio(stages)
  const active = stages.find(x => x.state === 'active') ?? [...stages].reverse().find(x => x.state === 'failed')
  const where: Seg = active
    ? { t: ' ' + active.label + (active.state === 'failed' ? ' failed' : run.working ? '' : ' (paused)'), c: COLOR[active.state], bold: true }
    : { t: done === stages.length ? ' complete' : '', c: 'success', bold: true }
  const count: Seg = { t: ' ' + done + '/' + stages.length, dim: true }
  const time: Seg = { t: clock ? '  ' + clock : '', dim: true }
  if (columns >= 100) {
    return [...title, { t: bar(fraction, 10), c: 'claude' }, count, { t: '  ' }, ...railSegs(stages, true), time]
  }
  if (columns >= 62) {
    return [...title, { t: bar(fraction, 8), c: 'claude' }, count, { t: '  ' }, ...railSegs(stages, false), where, time]
  }
  return [...title, ...railSegs(stages, false), where]
}

/** Dim second line: the newest thing seen, or the first thing blocking delivery. */
export function bandDetail(s: StudioState, run: RunState, stages: EffStage[], columns: number): string | null {
  const blocker = s.status?.gates.find(g => !g.passed)?.violations[0]
  if (blocker && !s.busy) return clean('✗ ' + blocker, Math.max(8, columns))
  const current = stages.find(x => x.state === 'active')
  if (current?.note) return clean('▸ ' + current.label + ' · ' + current.note, Math.max(8, columns))
  return null
}

export type PaneActions = {
  refresh: () => Promise<void>; check: () => Promise<void>; useDetected: () => Promise<void>
  toggleSetup: () => Promise<void>; toggleHistory: () => Promise<void>; openEntry: (id: string) => Promise<void>; selectDraft: (value: string) => Promise<void>
  configureScripts: (value: string) => Promise<void>; close: () => Promise<void>
}

export function pane(ui: Full, s: StudioState, run: RunState, stages: EffStage[], history: HistoryEntry[], width: number, now: number, act: PaneActions) {
  const W = Math.max(24, width)
  const status = s.status
  const { done, fraction } = ratio(stages)
  const tracked = run.startedAt !== null
  const active = stages.find(x => x.state === 'active') ?? [...stages].reverse().find(x => x.state === 'failed')
  const elapsed = tracked ? duration((run.endedAt ?? now) - (run.startedAt ?? now)) : ''
  const rule = (label: string, right = ''): ReturnType<Ui['Box']> => {
    const fill = Math.max(2, W - label.length - right.length - 4)
    return row(ui, [{ t: label, c: 'claude', bold: true }, { t: ' ' + '─'.repeat(fill) + ' ', c: 'inactive' }, { t: right, dim: true }])
  }
  const children: ReturnType<Ui['Box']>[] = []

  children.push(ui.Box({ flexDirection: 'row', justifyContent: 'space-between', children: [
    el(ui, { t: '✎ Blog Studio', c: 'claude', bold: true }),
    el(ui, active ? { t: (active.state === 'failed' ? '✗ ' : run.working ? '▸ ' : '❚❚ ') + active.label + (elapsed ? ' · ' + elapsed : ''),
      c: COLOR[active.state] } : { t: tracked ? 'complete' + (elapsed ? ' · ' + elapsed : '') : 'idle', c: tracked ? 'success' : 'inactive' }),
  ] }))
  children.push(row(ui, [{ t: bar(fraction, Math.max(10, W - 16)), c: 'claude' },
    { t: '  ' + done + '/' + stages.length + ' · ' + Math.round(fraction * 100) + '%', dim: true }]))

  children.push(rule('PIPELINE', tracked ? 'what the agent is doing, inferred' : 'starts when the agent begins a blog'))
  const noteRoom = Math.max(0, W - 36)
  for (const st of stages) {
    const segs: Seg[] = [
      { t: GLYPH[st.state] + ' ', c: COLOR[st.state], bold: st.state === 'active' },
      { t: st.label.padEnd(9), c: st.state === 'pending' ? 'inactive' : 'text', bold: st.state === 'active' },
      { t: st.word.padEnd(9), c: COLOR[st.state] },
      { t: (st.n && !st.evidence ? '×' + st.n : '').padEnd(5), dim: true },
      { t: duration(st.ms).padEnd(6), dim: true },
    ]
    if (st.state === 'active' && st.note && noteRoom > 8) segs.push({ t: clean(st.note, noteRoom), dim: true })
    children.push(row(ui, segs))
  }

  const failedCount = status?.gates.filter(g => !g.passed).length ?? 0
  const passedCount = status?.passed_count ?? 0
  children.push(rule('DELIVERY GATES', status ? '✓' + passedCount + ' ✗' + failedCount + ' ·' + (5 - passedCount - failedCount) : 'not checked'))
  for (let n = 1; n <= 5; n++) {
    const g = status?.gates.find(x => x.gate === n)
    const state: StageState = g ? (g.passed ? 'done' : 'failed') : 'pending'
    children.push(row(ui, [{ t: GLYPH[state] + ' ', c: COLOR[state] }, { t: n + '  ', dim: true },
      { t: clean(g?.name ?? GATE_NAMES[n - 1] ?? '', W - 6),
        c: g ? 'text' : 'inactive' }]))
    if (g?.score != null) {
      const ok = g.score >= 90
      const barWidth = Math.max(8, Math.min(24, W - 34))
      children.push(row(ui, [{ t: '     ' }, { t: bar(g.score / 100, barWidth), c: ok ? 'success' : 'warning' },
        { t: ' ' + g.score + '/100', c: ok ? 'success' : 'warning', bold: true }, { t: ' needs 90', dim: true },
        ...(run.scores.length > 1 ? [{ t: '   ' + spark(run.scores), c: 'claude' as ThemeKey }] : [])]))
    }
    const blockers = groupViolations(g?.violations ?? [])
    for (const v of blockers.slice(0, 3)) children.push(el(ui, { t: '     ✗ ' + clean(v, 300), c: 'error' }, 'wrap'))
    if (blockers.length > 3) children.push(el(ui, { t: '     +' + (blockers.length - 3) + ' more', dim: true }))
    for (const v of groupViolations(g?.warnings ?? []).slice(0, 2)) children.push(el(ui, { t: '     ! ' + clean(v, 300), c: 'warning', dim: true }, 'wrap'))
  }
  if (status?.diagnostics.length) for (const d of status.diagnostics.slice(0, 3)) children.push(el(ui, { t: '! ' + clean(d, 400), c: 'warning' }, 'wrap'))
  if (s.message && !s.busy) children.push(el(ui, { t: clean(s.message, 400), dim: true }, 'wrap'))

  children.push(rule('DRAFT'))
  children.push(row(ui, [{ t: s.draft ? clean(s.draft, W - 4) : 'none selected', c: s.draft ? 'text' : 'warning' }]))
  if (s.projectRoot) children.push(el(ui, { t: 'project  ' + clean(s.projectRoot, Math.max(8, W - 10)), dim: true }))
  if (s.draft) {
    const when = status?.checked_at?.match(/T(\d\d:\d\d)/)?.[1]
    children.push(row(ui, [chip(status, s.busy), { t: ' · ' + passedCount + '/5 gates · last check ' + (when ? when + 'Z' : 'never'), dim: true }]))
  }
  if (status?.artifacts.length) {
    const names = status.artifacts.slice(0, 6).map(a => clean(a, 40))
    children.push(el(ui, { t: 'files  ' + names.join(', ') + (status.artifacts.length > 6 ? ' +' + (status.artifacts.length - 6) : ''), dim: true }, 'wrap'))
  }
  if (run.detected && run.detected !== s.draft) {
    children.push(ui.Box({ flexDirection: 'row', gap: 1, children: [
      el(ui, { t: 'seen: ' + clean(run.detected, Math.max(8, W - 24)), dim: true }),
      ui.Button({ key: 'use-detected', label: 'Use this draft (u)', hotkey: 'u', onPress: act.useDetected }),
    ] }))
  }

  if (s.busy) {
    children.push(el(ui, { t: '◐ ' + clean(s.message ?? 'Working...', 80) + ' (buttons are off until it finishes)', c: 'claude' }, 'wrap'))
  } else {
    children.push(ui.Box({ flexDirection: W < 48 ? 'column' : 'row', gap: 1, children: [
      ...(s.draft ? [
        ui.Button({ key: 'refresh', label: 'Refresh (r)', hotkey: 'r', onPress: act.refresh }),
        ui.Button({ key: 'check', label: 'Run checks (c)', hotkey: 'c', variant: 'primary', onPress: act.check }),
      ] : []),
      ui.Button({ key: 'setup', label: (run.setup ? 'Hide settings' : 'Settings') + ' (s)', hotkey: 's', dimColor: true, onPress: act.toggleSetup }),
      ui.Button({ key: 'close', label: 'Close', role: 'dismiss', dimColor: true, onPress: act.close }),
    ] }))
    children.push(rule('RECENT BLOGS', history.length ? history.length + ' saved' : ''))
    if (!history.length) {
      children.push(el(ui, { t: 'None yet. Blogs appear as the agent writes them. Backfill: /blog-studio history scan <folder>', dim: true }, 'wrap'))
    } else {
      const shown = history.slice(0, run.historyOpen ? 25 : 5)
      shown.forEach((e, i) => {
        const current = e.root === rootOf(s) && e.draft === s.draft
        const label = (i + 1) + ' ' + formatWhen(e.lastSeen) + ' ' + statusGlyph(e.status) + ' ' + clean(title(e), Math.max(8, W - 26)) +
          (e.status ? ' ' + e.passed + '/5' : '')
        children.push(ui.Button({ key: 'hist-' + e.id, label, ...(i < 9 ? { hotkey: String(i + 1) } : {}),
          ...(current ? { variant: 'primary' as const } : { dimColor: true }), onPress: () => act.openEntry(e.id) }))
      })
      if (history.length > 5) children.push(ui.Button({ key: 'hist-toggle', label: (run.historyOpen ? 'Fewer' : 'All ' + history.length + ' blogs') + ' (h)',
        hotkey: 'h', dimColor: true, onPress: act.toggleHistory }))
    }
    if (!s.draft || !s.scripts || run.setup) {
      children.push(rule('SETTINGS'))
      children.push(ui.Input({ key: 'draft', label: 'Draft folder', placeholder: 'outputs/article', onSubmit: act.selectDraft }))
      children.push(ui.Input({ key: 'scripts', label: 'Engine scripts', placeholder: s.scripts ? clean(s.scripts, 60) : '/path/to/claude-blog/scripts',
        onSubmit: act.configureScripts }))
    }
  }
  return ui.Box({ flexDirection: 'column', gap: 0, children })
}
