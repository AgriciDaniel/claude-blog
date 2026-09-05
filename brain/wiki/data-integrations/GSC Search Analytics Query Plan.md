---
type: spoke
title: "GSC Search Analytics Query Plan"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [data-integrations, gsc, ga4, read-only, active]
domain: "Blog Data"
confidence: verified
related:
  - "[[Google Data Integrations]]"
  - "[[URL Inspection Evidence Plan]]"
  - "[[GA4 Blog Engagement Metrics]]"
  - "[[Generative AI Performance Reporting]]"
  - "[[First Party Versus Market Data]]"
  - "[[Query Dimension Hygiene]]"
  - "[[Metric Export Schema]]"
  - "[[Read Only Data Access Pattern]]"
source_urls:
  - "https://developers.google.com/webmaster-tools/v1/searchanalytics/query"
  - "https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports"
  - "https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect"
  - "https://developers.google.com/analytics/devguides/reporting/data/v1"
---

# GSC Search Analytics Query Plan

## Planning Scope For Search Analytics Pulls

GSC Search Analytics Query Plan defines how to request read-only Search Console evidence for blog pages and topic groups. The Search Analytics API source supports clicks, impressions, CTR, and position by queryable dimensions, but this note treats the output as a filtered property report rather than a complete record of all Search behavior. Use `g-gsc-api` for the query packet, `g-urlinspect` for index-state follow-up, `g-ga4-data` for engagement comparison, and `g-genai-reports` only when the question touches Search generative AI reporting context.

## Inputs, Assumptions, And Constraints

Required inputs are property label, date window, search type, dimension list, filters, row limit or export limit, owner, and canonical page group. Assumptions must state whether the analysis is page-first, query-first, topic-first, or brand/non-brand. Constraints include redacted queries, limited rows, API or UI differences, country/device filters, and date ranges that do not match GA4 exports.

## Decisions That Must Be Deferred

- Whether a page is indexed belongs in [[URL Inspection Evidence Plan]].
- Whether a visitor engaged after clicking belongs in [[GA4 Blog Engagement Metrics]].
- Whether a page should be rewritten belongs in the content brief after evidence labels are assigned.
- Whether AI feature reporting is available belongs in [[Generative AI Performance Reporting]].
- Whether market data should influence priority belongs in [[First Party Versus Market Data]].

## Execution Table

| Phase | Owner | Evidence | Output | Review date |
|---|---|---|---|---|
| Frame question | SEO lead | Page list, topic cluster, target country, search type | Query plan note with filters | Before export |
| Pull Search Analytics | Data owner | GSC rows for selected dimensions | Sanitized metric packet | Export day |
| Normalize dimensions | Analyst | Query groups, page canonical map, device and country splits | Clean table for [[Metric Export Schema]] | Same day |
| Cross-check gaps | Reviewer | URL Inspection need, GA4 need, AI report availability | Handoff list to sibling notes | Before recommendations |
| Label confidence | Reviewer | Filters, date range, row completeness | `verified`, `sample`, `stale`, or `missing` | Report draft |
| Compare windows | SEO analyst | Current and previous `g-gsc-api` rows with identical filters | Decay signal or no-change note | Before rewrite queue |
| Package caveats | Reviewer | Redactions, row caps, omitted `g-gsc-api` or `g-genai-reports` dimensions | Disclosure text for report | Final evidence pass |

## Operating Loop

1. Write the content decision before pulling data.
2. Select the fewest dimensions that answer the question.
3. Keep query text only when approved under [[Credential Boundary Rules]].
4. Preserve filters and date windows in the metric packet.
5. Compare against GA4 only after canonical URL and date alignment.
6. Re-run the query when a new export window, source-ledger refresh, or content update changes the evidence base.

## Query Pull Scenario

A refresh review asks whether a tutorial lost non-brand demand or only shifted devices. The plan requests page plus query rows, country, device, search type, and two matched date windows from `g-gsc-api`, then sends URL variants to canonical checks before charting.

If queries are redacted, the packet can still carry grouped demand but cannot quote examples. [[Content Decay Triage Register]] consumes the matched-window output, including filters, grouping rule, confidence label, and disclosure text.

## Source IDs

- `g-gsc-api`, `g-genai-reports`, `g-urlinspect`, `g-ga4-data`

## Related

- [[Google Data Integrations]]
- [[URL Inspection Evidence Plan]]
- [[GA4 Blog Engagement Metrics]]
- [[Generative AI Performance Reporting]]
- [[First Party Versus Market Data]]
- [[Query Dimension Hygiene]]
- [[Metric Export Schema]]
- [[Read Only Data Access Pattern]]
