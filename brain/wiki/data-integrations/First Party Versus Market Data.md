---
type: spoke
title: "First Party Versus Market Data"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [data-integrations, gsc, ga4, read-only, active]
domain: "Blog Data"
confidence: verified
related:
  - "[[Google Data Integrations]]"
  - "[[AI Citation Mechanics]]"
  - "[[Query Dimension Hygiene]]"
  - "[[Page URL Canonical Data Checks]]"
  - "[[Credential Boundary Rules]]"
  - "[[Data Confidence Labels]]"
  - "[[Missing Data Disclosure]]"
  - "[[Generative AI Performance Reporting]]"
  - "[[GA4 Blog Engagement Metrics]]"
source_urls:
  - "https://developers.google.com/webmaster-tools/v1/searchanalytics/query"
  - "https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect"
  - "https://developers.google.com/analytics/devguides/reporting/data/v1"
  - "https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports"
---

# First Party Versus Market Data

## Separation Job

First Party Versus Market Data prevents an audit from treating external studies as if they were the site owner's data. First-party data comes from the property or account being audited: Search Console Search Analytics, URL Inspection, GA4, and property-specific generative AI reporting when available. Market data belongs in context sections, trend caveats, or opportunity framing. It should not override a clean property export. Source IDs for this note are `g-gsc-api`, `g-urlinspect`, `g-ga4-data`, and `g-genai-reports`.

## Inputs That Prove Property Reality

The minimum first-party packet is a property label, owner, date range, export date, dimensions, filters, and canonical URL handling. If a report lacks one of those items, keep the conclusion narrower. When the property has no relevant export, use [[Missing Data Disclosure]] before adding market context from [[AI Citation Mechanics]] or [[2026 Google Update Timeline]].

## Boundary Matrix For Report Claims

| Claim type | First-party evidence | Market context role | Confidence label | Source IDs |
|---|---|---|---|---|
| Query demand changed | GSC clicks, impressions, CTR, position by page or query group | Can explain why traffic may not equal visibility | `verified` or `sample` | `g-gsc-api` |
| URL is indexed or canonicalized differently | URL Inspection result for the owned property URL | None unless discussing common diagnosis patterns | `verified` for that URL only | `g-urlinspect` |
| Readers engaged after arrival | GA4 landing page engagement and events | Can compare with internal baselines, not external averages | `verified` or `advisory` | `g-ga4-data` |
| AI feature visibility exists | Property export from Search Console generative AI reports | Market studies can explain volatility, not site performance | `verified`, `missing`, or `advisory` | `g-genai-reports` |
| Content strategy priority | Joined first-party packet across page, query, and engagement | Market data may rank background risks after property facts | Mixed label by evidence row | All listed IDs |
| Brand demand changed | GSC query groups split by approved brand rule | External visibility trends stay background only | `verified` or `sample` | `g-gsc-api` |
| AI report unavailable | Owner confirmation or missing export note | Market AI research may frame risk, not site visibility | `missing` plus caveat | `g-genai-reports` |

## Decisions This Note Must Record

- Whether the recommendation depends on first-party data, market context, or both.
- Which source ID supports the measurable property claim.
- Which dimensions were unavailable and how that changes the conclusion.
- Whether market evidence is used only as background.
- Which hub owns a broad stat or trend if the report mentions one.

## Operating Procedure

1. Start every performance section with property evidence when a current export exists.
2. Move market studies to a separate caveat paragraph and name them as market context.
3. Reject external averages when they conflict with a clean property trend.
4. Label missing property data before using market context.
5. Route AI visibility context to [[AI Citation Mechanics]] and keep this note focused on evidence class.

## Property-First Case

Before: a strategy note used an AI-search market study to justify rewriting a page. After: the audit checks site-specific GSC query movement and GA4 landing-page engagement first (`g-gsc-api`, `g-ga4-data`), then records AI report absence through `g-genai-reports`.

[[Full Site Blog Audit Report]] consumes this separation. This note supplies first-party rows, market-context labels, unavailable dimensions, and blocked claims; the audit expects property findings in tables and trend commentary in a named caveat.

## Report Wording

Use "in this property export" for first-party findings. Use "external market research suggests" only for context that is not measured on the audited site. Do not write a universal CTR, AI visibility, or ranking claim unless the source ledger and claim ledger already support that wording.

## Source IDs

- `g-gsc-api`, `g-urlinspect`, `g-ga4-data`, `g-genai-reports`

## Related

- [[Google Data Integrations]]
- [[AI Citation Mechanics]]
- [[Query Dimension Hygiene]]
- [[Page URL Canonical Data Checks]]
- [[Credential Boundary Rules]]
- [[Data Confidence Labels]]
- [[Missing Data Disclosure]]
- [[Generative AI Performance Reporting]]
- [[GA4 Blog Engagement Metrics]]
