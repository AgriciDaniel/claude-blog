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
