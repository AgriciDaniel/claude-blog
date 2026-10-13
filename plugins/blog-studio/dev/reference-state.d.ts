// Provisional state-method typing for the pinned public 2.1.277 reference,
// which predates $.state. Based on the current official Mods reference.
// The native type check excludes this file and requires host-generated types.
import type { HistoryState, RunState, StudioState } from '../types'
type Values = { studio: StudioState; run: RunState; history: HistoryState }
declare module 'claude-code' {
  interface EngineInterface {
    state: {
      get<K extends keyof Values>(ref: { plugin: 'blog-studio'; key: K }): Promise<{ value: Values[K] | undefined; version: number }>
      set<K extends keyof Values>(ref: { plugin: 'blog-studio'; key: K }, value: Values[K],
        options?: { ifVersion: number }): Promise<{ isSet: boolean; version: number }>
    }
  }
}
