import type { Status, StudioState } from '../types'

export const EMPTY: StudioState = {
  workspace: '', sessionId: '', scripts: null, draft: null,
  generation: 0, projectRoot: null, busy: false, status: null, message: null,
}
export const LABELS = {
  passed: 'Preflight passed', blocked: 'Blocked', partial: 'Partial', stale: 'Stale',
  unverified: 'Unverified', error: 'Execution error',
} as const

export function clean(value: string, limit = 500): string {
  return value.slice(0, 8192)
    .replace(/\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|$))/g, '')
    .replace(/[\x00-\x1f\x7f-\x9f]/g, ' ')
    .replace(/\b[0-9a-fA-F]{32}\b/g, '[redacted identifier]')
    .replace(/\/(?:var\/)?home\/[^/\s]+/g, '[home]')
    .slice(0, limit)
}

export function relativeDraft(value: string): string {
  const path = value.trim()
  if (!path || path.length > 1000 || path.startsWith('/') || path.includes('\\') || /[\x00-\x1f\x7f]/.test(path)) {
    throw new Error('Select a project-relative draft directory.')
  }
  const parts = path.split('/')
  if (parts.some(p => !p || p === '.' || p === '..')) throw new Error('Draft traversal and empty path components are refused.')
  return parts.join('/')
}

export function absoluteScripts(value: string): string {
  const path = value.trim().replace(/\/$/, '')
  if (!path.startsWith('/') || path.length > 2000 || /[\x00-\x1f\x7f\\]/.test(path) || path.split('/').slice(1).some(p => !p || p === '.' || p === '..')) {
    throw new Error('Configure an absolute trusted scripts directory.')
  }
  return path
}

export function absoluteRoot(value: string): string {
  const path = value.trim().replace(/\/$/, '') || '/'
  if (!path.startsWith('/') || path.length > 2000 || /[\x00-\x1f\x7f\\]/.test(path) || path.split('/').slice(1).some((p, i, a) => path !== '/' && (p === '.' || p === '..' || (!p && i < a.length)))) {
    throw new Error('Project root must be an absolute path.')
  }
  return path
}

export function parseStatus(raw: string, stderr = ''): Status {
  if (raw.length > 1024 * 1024) throw new Error('Status response exceeds size limit.')
  const value = jsonResponse(raw, stderr)
  if (!value || typeof value !== 'object') throw new Error('Invalid status response.')
  const x = value as Record<string, unknown>
  if (x.schema_version !== 1 || typeof x.status !== 'string' || !Object.hasOwn(LABELS, x.status) ||
      !Number.isInteger(x.passed_count) || Number(x.passed_count) < 0 || Number(x.passed_count) > 5 ||
      !Array.isArray(x.gates) || x.gates.length > 5 || !Array.isArray(x.artifacts) || x.artifacts.length > 8192 ||
      !Array.isArray(x.diagnostics) || x.diagnostics.length > 200 ||
      !(x.checked_at === null || typeof x.checked_at === 'string')) throw new Error('Invalid status fields.')
  const seen = new Set<number>()
  const gates = x.gates.map((g: unknown) => {
    if (!g || typeof g !== 'object') throw new Error('Invalid gate result.')
    const row = g as Record<string, unknown>
    const n = row.gate
    if (typeof n !== 'number' || !Number.isInteger(n) || n < 1 || n > 5 || seen.has(n) ||
        typeof row.name !== 'string' || typeof row.passed !== 'boolean' ||
        !Array.isArray(row.violations) || !Array.isArray(row.warnings) ||
        !(row.score === null || (typeof row.score === 'number' && Number.isFinite(row.score) && row.score >= 0 && row.score <= 100))) throw new Error('Invalid gate fields.')
    seen.add(n)
    return { gate: n, name: clean(row.name), passed: row.passed, score: row.score as number | null,
      violations: strings(row.violations), warnings: strings(row.warnings) }
  })
  if (Number(x.passed_count) !== gates.filter(g => g.passed).length) throw new Error('Gate count contradicts results.')
  if (x.status === 'passed' && (gates.length !== 5 || gates.some(g => !g.passed || g.violations.length) ||
      !gates.some(g => g.gate === 4 && g.score !== null && g.score >= 90) || typeof x.run_id !== 'string' ||
      !/^[0-9a-f]{32}$/.test(x.run_id) || typeof x.checked_at !== 'string')) throw new Error('Incomplete passing status.')
  return { schema_version: 1, status: x.status as Status['status'], label: LABELS[x.status as keyof typeof LABELS],
    passed_count: Number(x.passed_count), checked_at: x.checked_at === null ? null : clean(x.checked_at as string), gates,
    artifacts: strings(x.artifacts, 8192), diagnostics: strings(x.diagnostics),
    ...(typeof x.run_id === 'string' ? { run_id: x.run_id } : {}) }
}

export function jsonResponse(raw: string, stderr = ''): unknown {
  try { return JSON.parse(raw) } catch {
    throw new Error('Helper returned malformed or incomplete JSON. No passing result was accepted.' +
      (stderr ? ' Diagnostic: ' + clean(stderr, 500) : ''))
  }
}

function strings(value: unknown[], max = 200): string[] {
  if (value.length > max || value.some(v => typeof v !== 'string')) throw new Error('Invalid diagnostic list.')
  return (value as string[]).map(v => clean(v, 1000))
}

export function summary(s: StudioState): string {
  if (!s.draft) return 'Blog Studio: select a draft with /blog-studio select <directory>.'
  if (s.busy) return 'Blog Studio: ' + clean(s.draft, 90) + ' | ' + (s.message ?? 'Working...')
  const status = s.status
  return 'Blog Studio: ' + clean(s.draft, 90) + ' | ' + (status?.label ?? 'Unverified') +
    ' | ' + (status?.passed_count ?? 0) + '/5 gates | Last checked: ' + (status?.checked_at ?? 'unknown') +
    (s.message ? ' | ' + clean(s.message) : '')
}
