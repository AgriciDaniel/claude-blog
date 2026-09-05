---
type: deliverable
title: "Google API Evidence Matrix"
domain: "Blog Content Brain"
status: active
created: 2026-07-09
updated: 2026-07-10
tags: [deliverables, data-integrations, evidence]
source_urls:
  - "https://developers.google.com/webmaster-tools/v1/searchanalytics/query"
  - "https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect"
  - "https://developers.google.com/speed/docs/insights/v5/get-started"
  - "https://developers.google.com/analytics/devguides/reporting/data/v1"
  - "https://docs.cloud.google.com/natural-language/docs"
  - "https://developers.google.com/google-ads/api/docs/keyword-planning/overview"
---

# Google API Evidence Matrix

## Evidence Comparison Job

This matrix tells [[Google Data Integrations]] which exported fields can support a blog recommendation, which credentials would be needed outside the vault, and which surfaces are blocked because this ledger has no source ID for them. It is advisory and read-only. It never stores tokens, request headers, account IDs, or raw private exports. The source IDs wired here are `g-gsc-api`, `g-urlinspect`, `g-psi`, `g-ga4-data`, `g-nlp`, and `g-ads-kw`; YouTube Data API remains the explicit source-ledger gap.

## Credential Tiers And Evidence Rows

Credential tiers mirror the claude-blog `/blog google` skill: Tier 0 is API key access for PageSpeed, CrUX, YouTube, and NLP; Tier 1 adds OAuth or service-account access for GSC and URL Inspection; Tier 2 adds a configured GA4 property; Tier 3 adds Google Ads developer token and customer IDs for Keyword Planner. A redacted operator export can satisfy evidence review without live access, but it does not change the skill tier.

## API Evidence Matrix

| Data surface | Credential tier | Accepted evidence | Decision it can support | Source state |
|---|---|---|---|---|
| PageSpeed Insights and CrUX | Tier 0 | Lighthouse lab data and available field data | Technical risk notes for page quality | `g-psi` |
| YouTube Data API | Tier 0 | Video search metadata from `/blog google youtube` or redacted operator export | Video embedding and repurposing evidence, not blog ranking proof | Source-ledger gap: add official YouTube Data API source before release-satisfying claims |
| Natural Language API | Tier 0 | Entity, sentiment, and classification export | Entity audit and E-E-A-T entity gap review | `g-nlp` |
| GSC Search Analytics | Tier 1 | Clicks, impressions, CTR, position by query or page | Decay triage, query fit, cluster demand | `g-gsc-api` |
| URL Inspection | Tier 1 | Index state, canonical, rich result status | Indexing diagnosis and canonical review | `g-urlinspect` |
| GA4 Data API | Tier 2 | Organic engagement and post-click behavior | Content usefulness review after the click | `g-ga4-data` |
| Keyword Planner | Tier 3 | Keyword ideas or volume export with Ads account caveats | Demand planning, never exact traffic promise | `g-ads-kw` |
| Joined evidence view | Uses source-specific tiers | Page URL, canonical, query, engagement, entity, and demand joins | Recommendation confidence label | Uses wired IDs plus explicit YouTube gap |

## Interpretation Rules For Mixed API Evidence

First-party property exports outrank market averages for the property under review, but missing exports must be disclosed. GSC and GA4 answer different parts of the journey, so clicks and engagement should not be merged without a canonical URL key. URL Inspection evidence can explain index state for a specific URL, not the overall quality of the page. PSI can identify performance risk, but it should not replace editorial review through [[Blog Quality Score]].
