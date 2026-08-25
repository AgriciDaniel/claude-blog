# Product Boundaries

Claude Blog Brain is an advisory, read-only Obsidian brain for blog content creation, optimization, and management dual-optimized for Google rankings (E-E-A-T, the 2026 core updates) and AI citations (GEO/AEO), spanning writing, rewriting and freshness, SERP-informed briefs and outlines, editorial calendars and strategy, semantic topic clusters, schema and internal linking, multilingual publishing, the FLOW framework, factchecking, personas, distribution, and the blog delivery contract, grounded in the claude-blog skill.

## It Does

- Preserve raw sources under `.raw/`.
- Synthesize source-cited notes and deliverables.
- Maintain action queues, reports, and next actions.
- Keep decisions auditable through source links and rollback notes.
- Gate maturity through `references/source-ledger.json`,
  `references/adapter-manifest.json`, and `scripts/audit_brain.py`.

## It Does Not

- No ranking or traffic guarantee; content outcomes are probabilistic and never certain
- No credentials, tokens, API keys, or private client content in repo artifacts
- No mutation of a CMS, GSC, GA4, or publishing platform; the brain is advisory and read-only
- No recommendation without a dated source, confidence level, and rollback note
- No deprecated advice (HowTo schema, retired FAQ rich results, FID) presented as current
- No fabricated or unsourced statistics and no generic, unsupported, or low-quality generated filler presented as fact

## Safety Risks

- Stale Google algorithm, E-E-A-T, or schema-deprecation requirements presented as current
- Fabricated, unsourced, or low-quality generated statistics written into published content
- Private client content, draft URLs, or credentials leaking into raw inputs or reports
- Overconfident content recommendations from thin or single-source inputs
- Generated reports leaking local filesystem paths

## Maturity Boundary

Current maturity: market-ready. Domain adapters, local raw-source provenance,
deterministic demo verification, citations, graph hygiene, public-projection
safety, and executable release verification pass. All 118 source-ledger entries
that were due on 2026-08-25 received explicit review decisions. Refreshing a
future date still requires rechecking the source and its claim.
