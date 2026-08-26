import assert from "node:assert/strict"
import { mkdir, mkdtemp, readFile, writeFile } from "node:fs/promises"
import os from "node:os"
import path from "node:path"
import test from "node:test"

import { sanitize, scanPublicText } from "./sanitize-public.mjs"

test("copies only reviewed wiki content and writes hashes", async () => {
  const root = await mkdtemp(path.join(os.tmpdir(), "claude-blog-public-"))
  const brain = path.join(root, "brain")
  const output = path.join(root, "public")
  await mkdir(path.join(brain, "wiki"), { recursive: true })
  await mkdir(path.join(brain, ".raw", "sources"), { recursive: true })
  await writeFile(path.join(brain, "wiki", "note.md"), "# Reviewed note\n", "utf8")
  await writeFile(path.join(brain, ".raw", "sources", "private.md"), "private\n", "utf8")

  const manifest = await sanitize({ brainRoot: brain, outputRoot: output })
  assert.deepEqual(manifest.map((item) => item.path), ["wiki/note.md"])
  const saved = JSON.parse(await readFile(path.join(output, "PUBLIC_MANIFEST.json"), "utf8"))
  assert.equal(saved.files.length, 1)
  await assert.rejects(readFile(path.join(output, ".raw", "sources", "private.md")))
})

test("rejects local paths, credentials, and private ledger names", () => {
  assert.throws(() => scanPublicText("/" + "var/home/alice/work", "wiki/note.md"), /local path/)
  assert.throws(() => scanPublicText("sk-" + "a".repeat(24), "wiki/note.md"), /credential/)
  assert.throws(() => scanPublicText("safe", "references/source-ledger.json"), /private surface/)
})
