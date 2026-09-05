# Claude Blog Brain Product Spec

Status: market-ready. Implemented adapters, deterministic demo verification,
source review, public-projection safety, and executable release verification
pass as of 2026-08-25.

## Buyer

Content teams, bloggers, SEO content strategists, and operators who run the claude-blog skill and need a persistent, source-cited operating system for writing, optimizing, and auditing blog content that ranks on Google and can be cited by AI assistants.

## Domain

Claude Blog Brain serves blog content creation, optimization, and management. It covers Google ranking work, E-E-A-T, 2026 core and spam updates, GEO and AEO, schema, topic clusters, multilingual publishing, FLOW evidence discipline, factchecking, persona and voice context, distribution, and the blog delivery contract.

## Skill Surface

The brain is grounded in the claude-blog v1.11.0 skill. The served user-facing workflows include `/blog write`, `/blog rewrite`, `/blog analyze`, `/blog brief`, `/blog outline`, `/blog calendar`, `/blog strategy`, `/blog seo-check`, `/blog schema`, `/blog repurpose`, `/blog geo`, `/blog image`, `/blog audit`, `/blog cannibalization`, `/blog factcheck`, `/blog persona`, `/blog brand`, `/blog discourse`, `/blog taxonomy`, `/blog notebooklm`, `/blog audio`, `/blog google`, `/blog update`, `/blog cluster`, `/blog multilingual`, `/blog translate`, `/blog localize`, `/blog locale-audit`, `/blog flow`, `/blog style`, and `/blog decay`. `blog-chart` remains internal-only.

## Core Workflows

- Source intake and provenance capture from the claude-blog skill, Google Search Central, web.dev, Schema.org, QRG, FLOW, GEO research, and vetted market studies.
- Answer-first article writing and rewriting through the six-pillar dual optimization framework.
- SERP-informed briefs, outlines, heading hierarchy, and source-backed statistics.
- Semantic topic-cluster planning with hub and spoke internal linking.
- Schema stack review for BlogPosting or Article, Person, Organization, BreadcrumbList, VideoObject, Product where relevant, and visible Q and A content.
- GEO and AEO citation readiness review at the passage level.
- Blog quality scoring across content quality, SEO, E-E-A-T, technical elements, and AI citation readiness.
- Multilingual publishing, translation, localization, hreflang, and locale audit planning.
- Distribution planning across owned site, Search, AI assistants, communities, video, email, and social surfaces.
- Google algorithm-update memory and freshness refresh.
- Approval queue for recommendations, with confidence and rollback notes.

## Deliverables

- Blog quality score synthesis playbook.
- SERP-informed content brief and outline.
- Semantic topic-cluster map with internal-link matrix.
- GEO and AI-citation readiness register.
- Schema stack and internal-linking reference library.
- Editorial calendar and content strategy plan.
- Blog delivery-contract gate report.
- Multilingual publishing and locale review checklist.
- Approval queue for recommendations.
- Google algorithm-update memory and refresh log.

## Input Contract

The first domain input contract is `schemas/blog-post-input.schema.json`. It
accepts a blog post or audit target with title, URL, Markdown body or HTML body,
frontmatter, target keyword, locale, dates, author metadata, source blocks, and
optional audit findings. The first implemented adapter path is:

- Importer: `scripts/ingest_blog_input.py`, CLI `claude-blog-brain blog-ingest`,
  output schema `claude-blog-brain.ingested-blog-post.v1`.
- Synthesis module: `scripts/synthesize_blog_plan.py`, CLI
  `claude-blog-brain blog-synthesize`, output schema
  `claude-blog-brain.blog-optimization-plan.v1`.
- Renderer: `scripts/render_blog_report.py`, CLI
  `claude-blog-brain blog-report`, output format Markdown.
- End-to-end CLI: `claude-blog-brain blog-pipeline`, which writes the ingested
  record, optimization plan, and rendered report to a caller-supplied output
  directory.
- Test coverage: `tests/test_blog_adapters.py` covers valid input, malformed
  JSON error envelopes, output-file assertions, deterministic output,
  domain-specific end-to-end report content, source-citation coverage,
  operator-supplied uncited findings, invalid URL and date rejection, and
  package CLI subcommands.

Release-counted adapters must enforce these gates before reading, fetching, or
rendering input:

- URL intake allows only `https` and `http`, blocks private, loopback, link-local,
  multicast, localhost, onion, file, data, and credential-bearing URLs, and
  resolves DNS before fetch to prevent SSRF through redirects or rebinding.
- Local input paths are vault-relative, normalized, non-absolute, cannot contain
  `..`, and cannot traverse symlinks outside the allowed raw-source lane.
- HTML input is parsed with a sanitizer that removes scripts, event handlers,
  remote executable embeds, unsafe URL schemes, and style injection before any
  report rendering.
- Rendered reports must not expose local absolute paths, credentials, tokens,
  cookies, private draft URLs, or raw private client content.
- Missing source dates, missing retrieval dates, unsupported statistics, and
  unverified audit findings remain advisory until tied to source-ledger IDs.

## Promise

Turn volatile blog SEO, content quality, and AI citation requirements into a persistent, source-cited operating brain that can support claude-blog planning, drafting, auditing, and delivery decisions.

## Explicit Non-Promises

- No ranking or traffic guarantee. Content outcomes are probabilistic and never certain.
- No guarantee of AI Overview, AI Mode, ChatGPT, Perplexity, Gemini, or Copilot citation.
- No credentials, tokens, API keys, or private client content in repo artifacts.
- No mutation of a CMS, GSC, GA4, GBP, ad platform, or publishing platform. V1 is advisory and read-only.
- No recommendation without a dated source, confidence level, and rollback note.
- No deprecated advice presented as current, including HowTo rich results, FAQ rich results, and FID.
- No fabricated statistics, unsourced market claims, or generic, unsupported, or low-quality generated filler presented as fact.
- No treatment of third-party SEO tools as access to Google's internal ranking systems.
