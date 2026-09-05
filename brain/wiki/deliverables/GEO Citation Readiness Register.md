---
type: deliverable
title: "GEO Citation Readiness Register"
domain: "GEO and AEO"
status: active
created: 2026-07-09
updated: 2026-07-10
tags: [deliverables, geo, citation-readiness, active]
---

# GEO Citation Readiness Register

## GEO Citation Readiness Register Scope

This register records page passages and technical access checks that may be easier for AI answer systems to interpret, cite, or exclude. It tracks source proximity, entity clarity, answer blocks, preview-control caveats, AI crawler accessibility, status, owner, and rollback triggers. It must not claim that any page can force citation in AI Overviews, AI Mode, or assistant products. Official Google claims route through `g-ai-opt-guide` and `g-ai-features`; market studies route through [[AI Citation Mechanics]].

### Items Captured In This Register

Capture answer passages, cited statistics, entity definitions, no-snippet or max-snippet controls, source freshness, visible attribution, AI crawler access evidence, and unresolved caveats. `seer-aio-impact-ctr-2026` can be used only as an AS-REPORTED practitioner benchmark for AI Overview citation association, not as causal proof.

### Items Routed Elsewhere

Technical schema work goes to [[Blog Schema Stack]], full site scoring goes to [[Blog Quality Score]], and distribution variants go to [[Distribution and Repurposing]]. `sparktoro-zero-click-2026` belongs in market-context notes unless a specific page recommendation needs the caveat.

## GEO Citation Readiness Register Table

| Register item | Source ID | Confidence | Owner | Status | Next review date | Rollback trigger |
|---|---|---|---|---|---|---|
| Primary answer block | `g-ai-opt-guide` | verified for Google guidance | GEO owner | draft, ready, or blocked | 2026-08-09 | Google AI guidance changes |
| AI feature preview controls | `g-ai-features` | verified for Search docs | Technical SEO | draft, ready, or blocked | 2026-08-09 | Preview rule changes |
| AIO performance context | `seer-aio-impact-ctr-2026` | advisory practitioner | Analyst | draft, ready, or blocked | 2026-08-09 | Client data contradicts benchmark |
| Zero-click journey caveat | `sparktoro-zero-click-2026` | AS-REPORTED market context | Strategist | draft, ready, or blocked | 2026-08-09 | New market study replaces context |
| Source proximity check | approved article source IDs | claim-specific | Researcher | draft, ready, or blocked | 2026-08-09 | Claim source becomes stale |
| AI crawler accessibility | `g-robots-intro`, `rfc9309`, `g-js-seo`, `g-intro-sd`, `g-inside-googlebot`, `g-common-crawlers` | verified for Google and robots standards; owner-supplied evidence required for OpenAI, Anthropic, and Perplexity crawler docs | Technical SEO | draft, ready, or blocked | 2026-08-09 | Robots, rendering, schema, page-size, or CDN/bot-control evidence changes |

## AI Crawler Accessibility Evidence

`/blog geo` scores AI Crawler Accessibility as part of the AI Citation Readiness subscore. This register can mark a page ready only when the evidence packet separates ledger-backed Google or robots claims from owner-supplied vendor and CDN evidence.

| Check | Must record | Source state | Ready evidence |
|---|---|---|---|
| Bot policy inventory | robots.txt treatment for GPTBot, ChatGPT-User, ClaudeBot, PerplexityBot, plus any related site goals | Source-ledger gap for OpenAI, Anthropic, and Perplexity crawler docs | Dated robots.txt capture plus owner-supplied vendor-doc citation or explicit "not claimed" note |
| Google and robots controls | Googlebot, Google-Extended, robots.txt parsing, preview controls | `g-robots-intro`, `rfc9309`, `g-googlebot`, `g-common-crawlers`, `g-ai-features` | Rendered robots.txt, meta robots, and preview-control evidence |
| Static or SSR HTML | Important article text is present without client-side JavaScript execution | `g-js-seo` for Google rendering; non-Google crawler docs are a source-ledger gap | View-source or fetched HTML contains body copy, headings, citations, and internal links |
| Schema in HTML | Article or BlogPosting schema is present in delivered HTML and matches visible page facts | `g-intro-sd`, `schema-full` | HTML source or build artifact with JSON-LD and visible content parity check |
| Page-size and fetch limits | Page payload is reasonable and not hiding primary content after large scripts | `g-inside-googlebot` for Googlebot behavior; non-Google crawler limits are a source-ledger gap | Fetch log, HTML byte-size note, and no client-only content dependency |
| CDN and bot controls | Cloudflare or other CDN settings for selected AI crawlers | Owner-supplied evidence required unless a CDN source is added to the ledger | Dated CDN screenshot or export showing allow, block, or intentional policy |

## Review Loop And Rollback Trigger

1. Review each passage for entity, date, and source clarity before marking ready.
2. Separate Google-documented controls from third-party observations in the confidence column.
3. Reopen the register after a Google AI documentation update, a major page rewrite, or contradictory first-party data.

## Source IDs Used

This register uses `g-ai-opt-guide`, `g-ai-features`, `g-robots-intro`, `rfc9309`, `g-js-seo`, `g-googlebot`, `g-common-crawlers`, `g-intro-sd`, `schema-full`, `g-inside-googlebot`, `seer-aio-impact-ctr-2026`, and `sparktoro-zero-click-2026`. OpenAI, Anthropic, Perplexity, and CDN-specific crawler docs are source-ledger gaps until owner-supplied evidence is recorded.
