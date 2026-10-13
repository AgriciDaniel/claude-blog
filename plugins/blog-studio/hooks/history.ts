import type { HistoryEntry, Status } from '../types'
import { clean, relativeDraft } from './logic'

export const MAX_STORED = 100
export const MAX_SHOWN = 30
export const KEY_PREFIX = 'entry:'

/** FNV-1a over the absolute location, so one draft folder is one entry. */
export function entryId(root: string, draft: string): string {
  let h = 0x811c9dc5
  for (const c of root + '\n' + draft) { h ^= c.charCodeAt(0); h = Math.imul(h, 0x01000193) >>> 0 }
  return h.toString(16).padStart(8, '0')
}

export function makeEntry(root: string, draft: string, now: number, source: HistoryEntry['source'],
  status: Status | null = null, lastSeen = now): HistoryEntry {
  return { id: entryId(root, draft), root, draft, name: clean(draft.split('/').pop() ?? draft, 80),
    firstSeen: lastSeen, lastSeen, source, status: status?.status ?? null, passed: status?.passed_count ?? 0,
    score: status?.gates.find(g => g.gate === 4)?.score ?? null }
}

/** Newest activity first. Merging keeps the earliest firstSeen and never lets a bare sighting erase a known result. */
export function mergeEntries(list: HistoryEntry[], entry: HistoryEntry): HistoryEntry[] {
  const old = list.find(e => e.id === entry.id)
  const merged: HistoryEntry = old ? { ...entry, firstSeen: Math.min(old.firstSeen, entry.firstSeen),
    lastSeen: Math.max(old.lastSeen, entry.lastSeen),
    ...(entry.status === null ? { status: old.status, passed: old.passed, score: old.score } : {}) } : entry
  return sortEntries([...list.filter(e => e.id !== entry.id), merged])
}

export function sortEntries(list: HistoryEntry[]): HistoryEntry[] {
  return [...list].sort((a, b) => b.lastSeen - a.lastSeen || a.name.localeCompare(b.name))
}

export function validEntry(value: unknown): value is HistoryEntry {
  if (!value || typeof value !== 'object') return false
  const e = value as Record<string, unknown>
  if (typeof e.id !== 'string' || typeof e.root !== 'string' || typeof e.draft !== 'string' || typeof e.name !== 'string' ||
      typeof e.firstSeen !== 'number' || typeof e.lastSeen !== 'number' || typeof e.passed !== 'number') return false
  if (!e.root.startsWith('/') || e.root.length > 2000 || /[\x00-\x1f\x7f\\]/.test(e.root)) return false
  try { relativeDraft(e.draft) } catch { return false }
  return true
}

export function formatWhen(ms: number): string {
  const d = new Date(ms)
  const two = (n: number) => String(n).padStart(2, '0')
  return two(d.getMonth() + 1) + '-' + two(d.getDate()) + ' ' + two(d.getHours()) + ':' + two(d.getMinutes())
}

export function statusGlyph(status: HistoryEntry['status']): string {
  return status === 'passed' ? '✓' : status === 'blocked' || status === 'error' ? '✗' : status === 'stale' || status === 'partial' ? '!' : '·'
}

/** Splits an absolute draft folder into the project root it is anchored to and its relative path. */
export function splitDraft(absolute: string, workspace: string): { root: string; draft: string } | null {
  const ws = workspace === '/' ? '' : workspace.replace(/\/$/, '')
  if (ws && absolute.startsWith(ws + '/')) {
    try { return { root: workspace, draft: relativeDraft(absolute.slice(ws.length + 1)) } } catch { return null }
  }
  const parts = absolute.split('/').filter(Boolean)
  if (parts.length < 2) return null
  const draft = parts.pop() as string
  try { return { root: '/' + parts.join('/'), draft: relativeDraft(draft) } } catch { return null }
}

/** Parses `find -printf '%T@\t%h\n'` output into folders and modification times, newest first. */
export function parseFound(out: string, limit = 300): { path: string; mtimeMs: number }[] {
  const rows: { path: string; mtimeMs: number }[] = []
  for (const line of out.split('\n')) {
    const [t, path] = line.split('\t')
    const seconds = Number(t)
    if (!path || !path.startsWith('/') || !Number.isFinite(seconds) || /[\x00-\x1f\x7f\\]/.test(path)) continue
    rows.push({ path, mtimeMs: Math.round(seconds * 1000) })
  }
  return rows.sort((a, b) => b.mtimeMs - a.mtimeMs).slice(0, limit)
}

/** A folder called 03-article says little, so lead with the project it sits in. */
export function title(e: Pick<HistoryEntry, 'root' | 'name'>): string {
  const project = clean(e.root.split('/').filter(Boolean).pop() ?? '', 60)
  return project && project !== e.name ? project + ' / ' + e.name : e.name
}
