/** Public projection policy for a future Quartz renderer.
 *
 * Content must first be copied by sanitize-public.mjs. Quartz must never read
 * the Brain root because `.raw`, `references/source-ledger.json`,
 * `references/claim-ledger.md`, source-review files, and local path evidence are
 * private operating surfaces.
 */
export const publicContentRoot = "./public-content"
export const excludedBrainSurfaces = [
  ".raw",
  "references/source-ledger.json",
  "references/claim-ledger.md",
  "references/source-review-*.json",
  "absolute build path",
  "local path",
]
