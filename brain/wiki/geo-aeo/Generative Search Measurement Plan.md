---
type: spoke
title: "Generative Search Measurement Plan"
domain: "GEO and AEO"
status: evergreen
created: 2026-07-06
updated: 2026-07-10
tags: [geo-aeo, ai-citation, evergreen]
---

# Generative Search Measurement Plan

## Generative Search Measurement Plan Planning Scope

This plan defines the measurement sequence for AI Overview, AI Mode, and assistant citation work. It does not estimate future traffic from market studies. The first choice is always whether the property has first-party reporting. Google sources `g-ai-features`, `g-ai-opt-guide`, and `g-genai-reports` provide the official measurement and feature context for Google Search. Market sources `sparktoro-zero-click-2026`, `seer-aio-impact-ctr-2026`, and `similarweb-gen-ai-stats-2026` are useful for planning assumptions only after their limitations are stated.

### Inputs, Assumptions, And Constraints

Inputs are the target URLs, query set, locale, date range, Search Console availability, observed citations, and source-ledger IDs. Assumptions must say whether data is first-party, manual observation, official documentation, market panel, or practitioner analysis.

### Decisions That Must Be Deferred

Defer lift estimates, ROI promises, and channel-budget moves until the site has enough first-party evidence. Do not replace missing AI feature data with a broad zero-click statistic from [[Dual Optimization]].

## Generative Search Measurement Plan Execution Table

| Phase | Inputs | Output | Owner | Evidence requirement | Follow-up |
|---|---|---|---|---|---|
| Surface inventory | Query list, locale, device, target URL | AIO, AI Mode, assistant, or none | Analyst | `g-ai-features` plus observation date | Pick the review note |
| First-party export | GSC generative AI report if available | Impressions, page or URL, country, device, and date | Data owner | `g-genai-reports` and export metadata | Send to [[Google Data Integrations]] |
| Citation sampling | SERP captures or assistant answers | Cited URL log and screenshot references | GEO reviewer | `g-ai-opt-guide` for caveat language | Use [[Citation Exposure Metrics]] |
| Market context | Stakeholder planning question | Caveated benchmark paragraph | Strategist | `sparktoro-zero-click-2026`, `seer-aio-impact-ctr-2026`, `similarweb-gen-ai-stats-2026` | Label as AS-REPORTED |
| Missing-report disclosure | Property lacks eligible AI reporting | Missing-data note and review date | Analyst | `g-genai-reports` | Do not replace with market averages |
| Organic baseline join | GSC classic export and URL list | Query, page, clicks, impressions | Data owner | `g-gsc-api` | Keep baseline separate from AI feature rows |
| Engagement follow-up | GA4 export supplied by operator | Organic engagement by canonical URL | Analyst | `g-ga4-data` | Use only after URL reconciliation |

## Generative Search Measurement Plan Operating Loop

1. Start with first-party availability, not with market studies.
2. Record the surface separately so AI Overview and AI Mode rows do not collapse into one metric.
3. Add source IDs beside every assumption and downgrade unsupported claims.
4. Review monthly or whenever [[2026 Google Update Timeline]] changes a relevant Google AI feature source.

## Measurement Packet Scenario

A content lead wants to know whether five refreshed articles are visible in generative search. The plan starts with property access: if Search Console generative AI reporting is available, `g-genai-reports` supports impressions by page or URL, country, device, and date for the covered Google surfaces.

If the export does not include query-level AI fields or AI click fields, the analyst writes "query-level AI data unavailable in the supplied export" and keeps query or click interpretation in the `g-gsc-api` lane or in an owner-supplied export with its own provenance.

If the report is unavailable, the analyst records a missing-report disclosure and then runs manual citation sampling. The sample uses `g-ai-features` for Search feature context and cannot be graphed as a trend without repeatable evidence.

Classic GSC query rows may still establish the organic baseline through `g-gsc-api`. GA4 engagement can help explain post-click behavior through `g-ga4-data`, but it does not identify an AI Overview citation by itself.

Market context from `sparktoro-zero-click-2026`, `seer-aio-impact-ctr-2026`, or `similarweb-gen-ai-stats-2026` appears only in an assumptions paragraph. It never replaces the property export.

## Measurement Plan Failure Points

- AI Overview and AI Mode rows are merged, even though `g-ai-features` treats them as Google AI feature contexts needing separate observation.
- A market panel is used as the site's KPI baseline, despite the AS-REPORTED limitations in the ledger.
- Screenshots are collected only when the brand appears, producing a biased citation sample.
- GA4 sessions are treated as assistant citations without a captured answer or source URL.

## Evidence Matrix Wiring

[[Google API Evidence Matrix]] consumes this plan when a client report needs data-source requirements. It needs the surface inventory, credential tier, export fields, missing-data notes, and source IDs per data lane.

The matrix expects an output that separates first-party exports, manual captures, and market context. It should not receive blended "AI visibility" metrics without a source-specific field list.

## Sampling Cadence Detail

Manual captures should keep query, locale, device, date, and reviewer constant under `g-ai-features`.

First-party AI exports should use stable date ranges before interpreting `g-genai-reports` changes, but query and click rows stay outside that source unless an owner-supplied export proves they exist.

Market assumptions should be refreshed before client-facing use when their ledger due date passes.

Baseline organic rows should stay tied to `g-gsc-api` rather than AI feature report fields.

## Generative Search Measurement Plan Output

The plan should produce a measurement packet, not a performance promise. A complete packet includes date range, query set, URL set, source IDs, missing-data notes, and the next review date.
