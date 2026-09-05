# Claude Blog Brain Adapter Plan

Status: market-ready. Domain code adapters are implemented, CLI-wired,
test-covered, and release-verified with current research evidence.

## Current Adapter Honesty

`references/adapter-manifest.json` sets `generic_only` to false because domain
importers, synthesis modules, and report renderers are implemented, CLI-wired,
and covered by tests. Adapter completion did not override the source-freshness
gate. The due ledger entries were revalidated on 2026-08-25 before maturity was
promoted.
The adapter evidence now covers importers, synthesis modules, renderers,
fixtures, package CLI, malformed-input envelopes, deterministic output,
output-file assertions, and citation coverage for blog post, topic cluster, and
GEO citation audit JSON input types.

## Raw Input Types

- Blog post audit input using `schemas/blog-post-input.schema.json`.
- Markdown blog post with YAML frontmatter.
- HTML blog post with canonical URL and extracted metadata.
- Topic cluster plan input using `schemas/topic-cluster-input.schema.json`.
- GEO citation audit input using `schemas/geo-citation-audit-input.schema.json`.
- claude-blog quality report JSON from `scripts/analyze_blog.py`.
- Blog delivery contract output from `scripts/blog_preflight.py`.
- Google algorithm update ledger from `data/google-updates.json`.
- Optional future exports from GSC, PSI, CrUX, GA4, DataForSEO, Ahrefs, and Firecrawl.

## Implemented Input Schema

- Name: `blog-post-input`.
- Path: `schemas/blog-post-input.schema.json`.
- Scope: title, URL, Markdown or HTML body, frontmatter, target keyword, locale, author, dates, source block, and optional audit findings.
- Enforced facts: HTTP(S) URL patterns, ISO date or date-time strings, required
  title, URL, target keyword, locale, and at least one body field.
- Name: `topic-cluster-input`.
- Path: `schemas/topic-cluster-input.schema.json`.
- Scope: hub page, spoke pages, existing links, locale, audience, objective,
  entity terms, and source-ledger IDs for a topic cluster plan.
- Enforced facts: required cluster name, primary topic, locale, hub, at least two
  spokes, HTTP(S) URLs, unique spoke IDs, and locale pattern.
- Name: `geo-citation-audit-input`.
- Path: `schemas/geo-citation-audit-input.schema.json`.
- Scope: page URL, target queries, passage-level citation evidence, entity
  fields, page signals, and llms.txt strategy for GEO citation readiness review.
- Enforced facts: required audit name, URL, title, locale, target queries,
  passages, page signals, HTTP(S) citation URLs, ISO citation dates, and boolean
  page signal values.

## Implemented Importer

- `ingest_blog_input`, path `scripts/ingest_blog_input.py`.
- CLI path: `claude-blog-brain blog-ingest`.
- Output schema: `claude-blog-brain.ingested-blog-post.v1`.
- Output facts: normalized headings, sections, links, source counts,
  provenance hashes, date metadata, author signals, and schema hints.
- `ingest_topic_cluster_input`, path `scripts/ingest_topic_cluster_input.py`.
- CLI path: `claude-blog-brain cluster-ingest`.
- Output schema: `claude-blog-brain.ingested-topic-cluster.v1`.
- Output facts: normalized hub and spoke pages, existing link graph, duplicate
  keyword groups, orphan spoke IDs, entity terms, source IDs, and provenance hash.
- `ingest_geo_citation_audit`, path `scripts/ingest_geo_citation_audit.py`.
- CLI path: `claude-blog-brain geo-ingest`.
- Output schema: `claude-blog-brain.ingested-geo-citation-audit.v1`.
- Output facts: normalized target queries, passages, passage word counts,
  extractability flags, citation counts, entities, page signals, and provenance hash.

## Implemented Synthesis Module

- `synthesize_blog_plan`, path `scripts/synthesize_blog_plan.py`.
- CLI path: `claude-blog-brain blog-synthesize`.
- Output schema: `claude-blog-brain.blog-optimization-plan.v1`.
- Output facts: five-category blog scorecard, intent and entity coverage,
  GEO and AI citation readiness checks, schema recommendations, prioritized
  recommendations, delivery contract, and source citations.
- `synthesize_topic_cluster`, path `scripts/synthesize_topic_cluster.py`.
- CLI path: `claude-blog-brain cluster-synthesize`.
- Output schema: `claude-blog-brain.topic-cluster-plan.v1`.
- Output facts: cluster scorecard, hub and spoke internal-link matrix, spoke
  support links, prioritized recommendations, rollback notes, and source citations.
- `synthesize_geo_citation_readiness`, path
  `scripts/synthesize_geo_citation_readiness.py`.
- CLI path: `claude-blog-brain geo-synthesize`.
- Output schema: `claude-blog-brain.geo-citation-readiness.v1`.
- Output facts: readiness score, passage extractability, visible citation
  support, entity clarity, schema and crawl eligibility, measurement readiness,
  llms.txt caveat, no-guarantee guardrail, rollback notes, and source citations.

## Implemented Renderer

- `render_blog_report`, path `scripts/render_blog_report.py`.
- CLI path: `claude-blog-brain blog-report`.
- Output format: Markdown report with scorecard, delivery verdict, prioritized
  recommendations, GEO and AI citation readiness, schema recommendations, and
  source citations.
- `render_topic_cluster_report`, path `scripts/render_topic_cluster_report.py`.
- CLI path: `claude-blog-brain cluster-report`.
- Output format: Markdown report with cluster scorecard, internal-link matrix,
  prioritized recommendations, rollback notes, and source citations.
- `render_geo_citation_report`, path `scripts/render_geo_citation_report.py`.
- CLI path: `claude-blog-brain geo-report`.
- Output format: Markdown report with readiness metrics, checks,
  recommendations, rollback notes, and source citations.

## Implemented Fixture

- `sample-blog-post`, path `tests/fixtures/sample-blog-post.json`.
- `sample-topic-cluster-plan`, path
  `tests/fixtures/sample-topic-cluster-plan.json`.
- `sample-geo-citation-audit`, path
  `tests/fixtures/sample-geo-citation-audit.json`.
- Later fixtures may cover blog audits, Google update ledgers, and claude-blog
  reference packs after these input types are release-verified.

## Implemented Tests

- `valid_input`, path `tests/test_blog_adapters.py`.
- `malformed_input_json_error_envelope`, path `tests/test_blog_adapters.py`.
- `output_file_assertions`, path `tests/test_blog_adapters.py`.
- `deterministic_output`, path `tests/test_blog_adapters.py`.
- `domain_specific_end_to_end_output`, path `tests/test_blog_adapters.py`.
- `citation_coverage`, path `tests/test_blog_adapters.py`.
- `operator_supplied_uncited_audit_finding`, path `tests/test_blog_adapters.py`.
- `invalid_date_and_url_rejection`, path `tests/test_blog_adapters.py`.
- `package_cli_blog_subcommands`, path `tests/test_blog_adapters.py`.
- `package_cli_blog_pipeline`, path `tests/test_blog_adapters.py`.
- `topic_cluster_valid_deterministic_output_and_citation_coverage`, path
  `tests/test_domain_adapters.py`.
- `topic_cluster_malformed_input_json_error_envelope`, path
  `tests/test_domain_adapters.py`.
- `geo_valid_deterministic_output_and_citation_coverage`, path
  `tests/test_domain_adapters.py`.
- `geo_malformed_input_json_error_envelope`, path
  `tests/test_domain_adapters.py`.
- `package_cli_new_adapter_subcommands`, path `tests/test_domain_adapters.py`.
- `package_cli_new_pipelines`, path `tests/test_domain_adapters.py`.

## Safety Requirements

- Reject credentials and private client data in fixtures.
- Preserve raw inputs before transformation.
- Cite every recommendation to `references/source-ledger.json`.
- Keep advice read-only unless a future release defines approval, mutation, and rollback.
- Treat missing source dates, deprecated schema advice, fabricated statistics, and unsupported GEO promises as blocking defects.
- Reject non-HTTP(S) URLs, localhost, private IP ranges, link-local IPs,
  credential-bearing URLs, and redirect chains that resolve into blocked ranges.
- Normalize local paths as vault-relative paths, reject absolute paths and `..`,
  and never follow symlinks outside the allowed raw-source lane.
- Sanitize HTML before extraction or report rendering by removing scripts, event
  handlers, unsafe URL schemes, remote executable embeds, and style injection.
- Scrub rendered outputs for local absolute paths, secrets, cookies, private draft
  URLs, and raw private client content.

## Completion Gate

Domain-adapted maturity requires one implemented importer, one implemented
synthesis module, one implemented report renderer, one fixture per supported
input type, and tests for valid input, malformed input, rendering, credentials
boundary, deterministic output, and citation coverage.
