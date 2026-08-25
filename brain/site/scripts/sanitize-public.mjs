#!/usr/bin/env node
/** Build a fail-closed public Markdown projection from the reviewed wiki. */

import { createHash } from "node:crypto"
import { cp, mkdir, readFile, rm, writeFile } from "node:fs/promises"
import path from "node:path"
import process from "node:process"

const PRIVATE_NAMES = new Set([".raw", "source-ledger.json", "claim-ledger.md"])
const PRIVATE_PREFIXES = ["source-review-"]
const LOCAL_PATH = /(?:\/home|\/var\/home|\/Users)\/[A-Za-z0-9_.-]+|[A-Za-z]:\\Users\\[A-Za-z0-9_.-]+/i
const SECRET = /-----BEGIN [A-Z ]*PRIVATE KEY-----|\b(?:sk-ant-|sk-|ghp_|github_pat_|AIza|AKIA)[A-Za-z0-9_-]{16,}/

function rejectPrivateName(relativePath) {
  const parts = relativePath.split(path.sep)
  if (parts.some((part) => PRIVATE_NAMES.has(part))) {
    throw new Error(`private surface selected: ${relativePath}`)
  }
  if (parts.some((part) => PRIVATE_PREFIXES.some((prefix) => part.startsWith(prefix)))) {
    throw new Error(`private review record selected: ${relativePath}`)
  }
}

export function scanPublicText(text, relativePath) {
  rejectPrivateName(relativePath)
  if (LOCAL_PATH.test(text)) throw new Error(`local path found in ${relativePath}`)
  if (SECRET.test(text)) throw new Error(`credential-shaped value found in ${relativePath}`)
}

export async function sanitize({ brainRoot, outputRoot }) {
  const source = path.resolve(brainRoot, "wiki")
  const destination = path.resolve(outputRoot, "wiki")
  if (path.resolve(outputRoot) === path.resolve(brainRoot)) {
    throw new Error("output must be separate from the Brain root")
  }
  await rm(outputRoot, { recursive: true, force: true })
  await mkdir(destination, { recursive: true })
  await cp(source, destination, {
    recursive: true,
    filter: (candidate) => {
      const relative = path.relative(brainRoot, candidate)
      rejectPrivateName(relative)
      return true
    },
  })

  const files = []
  async function walk(directory) {
    const { readdir } = await import("node:fs/promises")
    for (const entry of await readdir(directory, { withFileTypes: true })) {
      const candidate = path.join(directory, entry.name)
      if (entry.isDirectory()) await walk(candidate)
      else if (entry.isFile()) files.push(candidate)
      else throw new Error(`unsupported public entry: ${candidate}`)
    }
  }
  await walk(destination)
  const manifest = []
  for (const file of files.sort()) {
    const relative = path.relative(outputRoot, file)
    const bytes = await readFile(file)
    const text = bytes.toString("utf8")
    scanPublicText(text, relative)
    manifest.push({
      path: relative.split(path.sep).join("/"),
      sha256: createHash("sha256").update(bytes).digest("hex"),
    })
  }
  await writeFile(
    path.join(outputRoot, "PUBLIC_MANIFEST.json"),
    `${JSON.stringify({ files: manifest }, null, 2)}\n`,
    "utf8",
  )
  return manifest
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const brainRoot = path.resolve(process.argv[2] ?? path.join(import.meta.dirname, "../.."))
  const outputRoot = path.resolve(process.argv[3] ?? path.join(import.meta.dirname, "../public-content"))
  const manifest = await sanitize({ brainRoot, outputRoot })
  process.stdout.write(`Sanitized ${manifest.length} public files.\n`)
}
