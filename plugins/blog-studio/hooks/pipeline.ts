import type { RunState, Stage, StageId } from '../types'
import { clean, relativeDraft } from './logic'

export const STAGES: readonly { id: StageId; label: string }[] = [
  { id: 'research', label: 'Research' }, { id: 'outline', label: 'Outline' }, { id: 'draft', label: 'Draft' },
  { id: 'visuals', label: 'Visuals' }, { id: 'render', label: 'Render' }, { id: 'review', label: 'Review' },
  { id: 'gates', label: 'Gates' },
]

export type Signal =
  | { kind: 'start'; skill: string }
  | { kind: 'stage'; stage: StageId; note: string; draft?: string }

const START_SKILLS = new Set(['blog', 'blog-write', 'blog-rewrite', 'pro-blog', 'youtube-to-blog', 'blog-multilingual'])
const SKILL_STAGE: Record<string, StageId> = {
  'blog-outline': 'outline', 'blog-brief': 'outline', 'blog-notebooklm': 'research', 'blog-discourse': 'research',
  'blog-chart': 'visuals', 'blog-image': 'visuals', banana: 'visuals',
  'blog-seo-check': 'review', 'blog-factcheck': 'review', 'blog-analyze': 'review', 'blog-geo': 'review',
}
const AGENT_STAGE: Record<string, StageId> = {
  'blog-researcher': 'research', 'blog-writer': 'draft', 'blog-translator': 'draft',
  'blog-reviewer': 'review', 'blog-seo': 'review',
}
const NOT_DRAFT = /^(brand|voice|discourse|readme|claude|agents|memory|skill|changelog)$/i

function tail(name: string): string {
  return name.split(':').pop() ?? name
}

function text(value: unknown, limit = 200): string {
  return typeof value === 'string' ? value.slice(0, limit) : ''
}

export function draftDirectory(filePath: string, workspace: string): string | null {
  const root = workspace === '/' ? '' : workspace.replace(/\/$/, '')
  if (!filePath.startsWith(root + '/')) return null
  const parts = filePath.slice(root.length + 1).split('/')
  parts.pop()
  if (!parts.length) return null
  try { return relativeDraft(parts.join('/')) } catch { return null }
}

export function skillSignal(skill: string): Signal | null {
  const name = tail(skill)
  if (START_SKILLS.has(name)) return { kind: 'start', skill: clean(name, 40) }
  const stage = SKILL_STAGE[name]
  return stage ? { kind: 'stage', stage, note: clean('/' + name, 60) } : null
}

/** Inference only: classifies one tool call by name and arguments, never by running anything. */
export function classify(tool: string, input: Record<string, unknown>, workspace: string): Signal | null {
  if (tool === 'Skill') return skillSignal(text(input.skill, 120))
  if (tool === 'WebSearch') return { kind: 'stage', stage: 'research', note: 'web search' }
  if (tool === 'WebFetch') {
    let host = ''
    try { host = new URL(text(input.url, 500)).hostname } catch { /* not a URL */ }
    return { kind: 'stage', stage: 'research', note: host ? clean('read ' + host, 60) : 'web fetch' }
  }
  if (tool === 'Agent' || tool === 'Task') {
    const stage = AGENT_STAGE[tail(text(input.subagent_type, 80))]
    return stage ? { kind: 'stage', stage, note: clean(tail(text(input.subagent_type, 80)), 40) } : null
  }
  if (tool === 'Write' || tool === 'Edit' || tool === 'MultiEdit') {
    const file = text(input.file_path, 1000)
    const base = file.split('/').pop() ?? ''
    const stem = base.replace(/\.[^.]*$/, '')
    if (/^review\.md$/i.test(base)) return { kind: 'stage', stage: 'review', note: 'review.md' }
    if (/\.(svg|png|jpe?g|webp)$/i.test(base)) return { kind: 'stage', stage: 'visuals', note: clean(base, 40) }
    if (/\.mdx?$/i.test(base) && /outline|brief/i.test(base)) return { kind: 'stage', stage: 'outline', note: clean(base, 40) }
    if (/\.mdx?$/i.test(base) && !NOT_DRAFT.test(stem)) {
      const draft = draftDirectory(file, workspace)
      return { kind: 'stage', stage: 'draft', note: clean('write ' + base, 60), ...(draft ? { draft } : {}) }
    }
    return null
  }
  if (tool === 'Bash') {
    const cmd = text(input.command, 2000)
    if (/blog_preflight/.test(cmd)) return { kind: 'stage', stage: 'gates', note: 'preflight' }
    if (/blog_render/.test(cmd)) return { kind: 'stage', stage: 'render', note: 'render html and pdf' }
    if (/generate_hero|blog_chart|chart_generator|banana/.test(cmd)) return { kind: 'stage', stage: 'visuals', note: 'images and charts' }
    if (/analyze_blog|lint_prose|ai_citation|quality_gate|cognitive_load/.test(cmd)) return { kind: 'stage', stage: 'review', note: 'quality scripts' }
    if (/discourse_research|notebooklm|last30days/.test(cmd)) return { kind: 'stage', stage: 'research', note: 'research scripts' }
    return null
  }
  if (tool.startsWith('mcp__')) {
    if (/dataforseo|notebooklm|exa|firecrawl|perplexity|search/i.test(tool)) return { kind: 'stage', stage: 'research', note: 'research tool' }
    if (/banana|nano|imagen|gemini/i.test(tool)) return { kind: 'stage', stage: 'visuals', note: 'image tool' }
  }
  return null
}

function blankStage(): Stage {
  return { state: 'pending', n: 0, startedAt: null, endedAt: null, note: null }
}

export function emptyRun(workspace = '', sessionId = ''): RunState {
  return { workspace, sessionId, skill: null, startedAt: null, endedAt: null, working: false,
    stages: Object.fromEntries(STAGES.map(s => [s.id, blankStage()])) as RunState['stages'],
    detected: null, scores: [], setup: false, historyOpen: false }
}

export function reduce(run: RunState, signal: Signal, now: number): RunState {
  if (signal.kind === 'start') {
    return { ...emptyRun(run.workspace, run.sessionId), skill: signal.skill, startedAt: now, working: true,
      scores: run.scores, setup: run.setup, historyOpen: run.historyOpen }
  }
  const index = STAGES.findIndex(s => s.id === signal.stage)
  const stages = { ...run.stages }
  STAGES.forEach((s, i) => {
    const cur = stages[s.id]
    if (i < index && cur.state === 'active') stages[s.id] = { ...cur, state: 'done', endedAt: now }
  })
  const cur = stages[signal.stage]
  stages[signal.stage] = { state: 'active', n: cur.n + 1, startedAt: cur.state === 'active' ? cur.startedAt : now,
    endedAt: null, note: signal.note }
  return { ...run, startedAt: run.startedAt ?? now, endedAt: null, working: true, stages,
    detected: signal.draft ?? run.detected }
}

export function fail(run: RunState, stage: StageId, now: number): RunState {
  const cur = run.stages[stage]
  return { ...run, stages: { ...run.stages, [stage]: { ...cur, state: 'failed', endedAt: now } } }
}

export function pause(run: RunState, now: number): RunState {
  return { ...run, working: false, endedAt: run.startedAt ? now : null }
}

export function doneCount(run: RunState): number {
  return STAGES.filter(s => run.stages[s.id].state === 'done').length
}

export function currentStage(run: RunState): { id: StageId; label: string } | null {
  let found: { id: StageId; label: string } | null = null
  for (const s of STAGES) if (run.stages[s.id].state === 'active' || run.stages[s.id].state === 'failed') found = s
  return found
}

export function hasRun(run: RunState): boolean {
  return run.startedAt !== null
}

/** Sample data for /blog-studio demo: a run caught mid-draft, so the design can be judged without an agent. */
export function demoRun(base: RunState, now: number): RunState {
  const at = (ago: number, taken: number): Pick<Stage, 'startedAt' | 'endedAt'> => ({ startedAt: now - ago, endedAt: now - ago + taken })
  const stages = emptyRun().stages
  stages.research = { state: 'done', n: 14, ...at(134_000, 52_000), note: 'read example.com' }
  stages.outline = { state: 'done', n: 2, ...at(82_000, 9_000), note: 'outline.md' }
  stages.draft = { state: 'active', n: 3, startedAt: now - 73_000, endedAt: null, note: 'write preview-post.md' }
  return { ...base, skill: 'preview', startedAt: now - 134_000, endedAt: null, working: true, stages,
    detected: null, scores: [62, 71, 84] }
}
