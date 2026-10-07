# Source Map

## Raw Sources

- `.raw/sources/claude-blog-skill/`: immutable local claude-blog v1.11.0
  snapshot captured 2026-07-09, covering 32 skill directories
  (1 orchestrator + 31 sub-skills), 30 user-facing commands, 5 agents,
  14 scripts, 22 references, 12 templates, plugin metadata, README, license,
  changelog, and top docs.
- `.raw/sources/claude-blog-brain-data/google-updates.json`: immutable
  historical snapshot of the repo's Google update ledger captured 2026-07-09.
  It is provenance, not the current ledger.
- Google Search Central docs; web.dev CWV; FLOW framework bibliography;
  GEO/AEO studies; content-marketing and copywriting research.

## Enrichment Sources

- Official Google Search Central, web.dev, and Schema.org documentation
- Primary-source-verified Google algorithm-update ledger (data/google-updates.json)
- Quality Rater Guidelines (E-E-A-T, YMYL, scaled-content abuse) and the Search Essentials / spam policies
- FLOW framework (github.com/AgriciDaniel/flow) and its cited studies
- GEO/AEO and AI-search studies (AI Overviews coverage and CTR, AI Mode behavior, passage-level citability)

## Import Strategy

- Copy raw source files into `.raw/sources/`.
- Record path, hash, retrieval date, owner, and source type.
- Use `sha256` only and keep all raw paths vault-relative.
- Record external research sources in `references/source-ledger.json`.
- Give each record an explicit lifecycle: `active`, `retired` or `unverified`.
  Only active, reviewed, unexpired evidence can support current recommendations.
  Retired records retain their historical dates and name active replacement IDs
  and a retirement reason; do not fetch or refresh them as current evidence.
- For active records, review the claim scope against content, record the actual
  retrieval and review dates separately from publication/update dates, and keep
  limitations visible. Record the excerpt, rationale, normalized SHA-256 and
  safe repository-relative full-capture path in `verification`. Also record
  `captured_excerpt_path` and `captured_excerpt_sha256` for the packaged reviewed
  excerpt artifact under `references/evidence/`. Availability and token overlap
  are diagnostics, not claim verification.
- `verify_source_ledger.py --offline-check` requires actual regular,
  nonsymlinked excerpt artifacts inside that fixed evidence root. It checks
  file hashes, normalized excerpt agreement, source identity, URL, review and
  retrieval dates, disposition and the recorded full-document hash binding.
  The aggregate redistributed excerpts for each document are capped at 25
  words. The offline gate does not recompute the full-document digest, prove
  full-page availability or determine semantic entailment. Preserve the
  separate full-capture pack and independently check its hashes and excerpts.
  Secure descriptor-relative reads are verified on Linux and fail closed on
  unsupported platforms. Coverage is the unique paths referenced by active
  sources, with every artifact record and excerpt bound to the active ledger.
  Unreferenced and historical files are outside this gate. A new retrieval
  attempt must not overwrite a
  successful review until its claims are reviewed.
- When a ledger entry relies on a captured raw file, record
  `raw_snapshot_path` and `raw_snapshot_sha256`.
- Record implemented schemas and adapters in `references/adapter-manifest.json`.
- Treat repository-root `data/google-updates.json` as canonical. Generate
  `brain/data/google-updates.json` with `scripts/sync_google_updates.py`; never
  edit the Brain projection independently.
- Create a source note under `wiki/sources/`.
- Link affected entities, workflows, and deliverables.

## Source Note Convention

- Source-note IDs must match `references/source-ledger.json` source IDs.
- Source notes use `wiki/sources/<source-id>.md` with a backlink to the ledger ID.
- Each source note must link at least one affected workflow, claim, canon note, or deliverable.
- Do not add source-only prose without a matching ledger entry.
- Raw-source paths must be vault-relative normalized paths under `.raw/sources/`,
  never absolute paths and never symlink exits.
