import { readFile } from 'node:fs/promises'
const source = await readFile(new URL('../.claude-plugin/types/claude-code/index.d.ts', import.meta.url), 'utf8')
if (!source.startsWith('// Written by Claude Code 2.1.294.')) throw new Error('Native gate requires fresh Claude Code 2.1.294 generated typings')
