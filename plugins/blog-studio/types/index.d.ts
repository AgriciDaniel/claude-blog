export type Gate = { gate: number; name: string; passed: boolean; score: number | null; violations: string[]; warnings: string[] }
export type Status = {
  schema_version: 1
  status: 'passed' | 'blocked' | 'partial' | 'stale' | 'unverified' | 'error'
  label: string
  checked_at: string | null
  passed_count: number
  gates: Gate[]
  artifacts: string[]
  diagnostics: string[]
  run_id?: string
}
export type StudioState = {
  workspace: string
  sessionId: string
  scripts: string | null
  draft: string | null
  generation: number
  projectRoot: string | null
  busy: boolean
  status: Status | null
  message: string | null
}
export type StageId = 'research' | 'outline' | 'draft' | 'visuals' | 'render' | 'review' | 'gates'
export type StageState = 'pending' | 'active' | 'done' | 'failed'
export type Stage = { state: StageState; n: number; startedAt: number | null; endedAt: number | null; note: string | null }
export type RunState = {
  workspace: string
  sessionId: string
  skill: string | null
  startedAt: number | null
  endedAt: number | null
  working: boolean
  stages: Record<StageId, Stage>
  detected: string | null
  scores: number[]
  setup: boolean
  historyOpen: boolean
}
export type HistoryEntry = {
  id: string
  root: string
  draft: string
  name: string
  firstSeen: number
  lastSeen: number
  status: Status['status'] | null
  passed: number
  score: number | null
  source: 'observed' | 'selected' | 'checked' | 'scan'
}
export type HistoryState = { entries: HistoryEntry[]; loaded: boolean }
declare module 'claude-code' {
  interface PluginState { 'blog-studio': { studio: StudioState; run: RunState; history: HistoryState } }
}
