// Fetch only the hash-pinned public declaration file. No mod is loaded.
import { readFile, mkdir, writeFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
const source = JSON.parse(await readFile(new URL('./types-source.json', import.meta.url), 'utf8'))
const folder = new URL('../.reference-types/', import.meta.url)
const target = new URL('claude-code.d.ts', folder)
let data
try { data = await readFile(target) } catch { /* First reference check downloads its development input. */ }
const hash = bytes => createHash('sha256').update(bytes).digest('hex')
if (!data || hash(data) !== source.sha256) {
  const response = await fetch(source.url, { signal: AbortSignal.timeout(30_000) })
  if (!response.ok) throw new Error('Public type reference unavailable: ' + response.status)
  data = Buffer.from(await response.arrayBuffer())
  if (data.length > 2 * 1024 * 1024 || hash(data) !== source.sha256) throw new Error('Public typing reference hash mismatch')
  await mkdir(folder, { recursive: true })
  await writeFile(target, data)
}
console.log('Reference type check: public Claude Code 2.1.277 declarations plus provisional state typing. Native 2.1.294 typing remains a separate gate.')
