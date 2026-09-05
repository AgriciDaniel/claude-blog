---
type: spoke
title: "URL Inspection Evidence Plan"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [data-integrations, gsc, ga4, read-only, active]
domain: "Blog Data"
confidence: verified
related:
  - "[[Google Data Integrations]]"
  - "[[GA4 Blog Engagement Metrics]]"
  - "[[Generative AI Performance Reporting]]"
  - "[[First Party Versus Market Data]]"
  - "[[Query Dimension Hygiene]]"
  - "[[Page URL Canonical Data Checks]]"
  - "[[GSC Search Analytics Query Plan]]"
  - "[[Metric Export Schema]]"
source_urls:
  - "https://developers.google.com/webmaster-tools/v1/searchanalytics/query"
  - "https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect"
  - "https://developers.google.com/speed/docs/insights/v5/get-started"
  - "https://developers.google.com/analytics/devguides/reporting/data/v1"
---

# URL Inspection Evidence Plan

## Planning Scope For URL Inspection

URL Inspection Evidence Plan uses property-owned URL evidence to separate indexing status from content quality diagnosis. The URL Inspection API source supports URL-level index and rich-result status, while GSC Search Analytics, PageSpeed Insights, and GA4 answer different questions. Use source IDs `g-urlinspect`, `g-gsc-api`, `g-psi`, and `g-ga4-data` to keep those evidence lanes distinct.

## Inputs, Assumptions, And Limits

Required inputs are inspected URL, property label, canonical candidate, inspection timestamp, owner, and the exact question being answered. The plan assumes the inspected URL belongs to the property and that credentials or auth headers stay outside the vault. URL Inspection evidence is not a live rendering test, not a ranking diagnosis, and not a replacement for content review.

## Decisions Deferred To Other Notes

- Search demand and query movement belong in [[GSC Search Analytics Query Plan]].
- Page experience belongs in PageSpeed evidence under [[Google Data Integrations]] and may inform [[Blog Quality Score]].
- Engagement after arrival belongs in [[GA4 Blog Engagement Metrics]].
- Canonical row merging belongs in [[Page URL Canonical Data Checks]].
- Missing inspection access belongs in [[Missing Data Disclosure]].

## Execution Table

| Phase | Owner | Evidence | Output | Follow-up action |
|---|---|---|---|---|
| Select URLs | SEO lead | Canonical page list, changed URLs, high-value pages | Inspection queue | Exclude private or unapproved URLs |
| Inspect owned URL | Data owner | URL Inspection result and timestamp | Index evidence packet | Store only sanitized fields |
| Compare canonical state | Technical SEO | Inspected URL, user-declared canonical, Google-selected canonical | Canonical discrepancy note | Route joins to [[Page URL Canonical Data Checks]] |
| Cross-check demand | Analyst | GSC rows for the same canonical page | Search performance context | Avoid ranking-cause language | 
| Add experience or engagement context | Reviewer | PSI and GA4 packets when available | Advisory caveat | Keep labels separate |
| Decide report wording | Reviewer | Confidence label and missing fields | Indexing section | Do not prescribe mutation from V1 |
| Check rich-result state | Technical SEO | URL Inspection rich-result fields under `g-urlinspect` | Structured-data evidence note | Route markup decisions to [[Blog Schema Stack]] |
| Reinspect after crawl event | Data owner | New timestamped URL Inspection result under `g-urlinspect` | Superseded inspection packet | Preserve old packet as stale context |

## Operating Loop

1. Inspect only URLs owned by the verified property.
2. Record the timestamp and source ID beside each inspected URL.
3. Separate "not indexed" from "low quality", "low demand", and "low engagement".
4. When canonical evidence conflicts with performance rows, pause metric rollups until the canonical map is updated.
5. Re-inspect after a crawl-relevant event only when the owner supplies a new read-only result.

## Inspection Decision Example

A finished post is ready for publication review, but the inspected URL shows a selected canonical different from the draft target. The report can cite URL-level index and canonical state through `g-urlinspect`; it cannot infer reader usefulness or query demand from that result.

The next step is not an indexing request from this brain. [[SEO Check Validation Checklist]] consumes inspected URL, selected canonical, rich-result state, timestamp, confidence label, and blocked mutation note before marking the canonical gate pass or blocked.

## Source IDs

- `g-gsc-api`, `g-urlinspect`, `g-psi`, `g-ga4-data`

## Related

- [[Google Data Integrations]]
- [[GSC Search Analytics Query Plan]]
- [[Page URL Canonical Data Checks]]
- [[GA4 Blog Engagement Metrics]]
- [[Missing Data Disclosure]]
- [[Blog Quality Score]]
