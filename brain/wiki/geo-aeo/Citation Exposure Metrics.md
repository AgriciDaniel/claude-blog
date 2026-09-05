---
type: spoke
title: "Citation Exposure Metrics"
domain: "GEO and AEO"
status: evergreen
created: 2026-07-06
updated: 2026-07-10
tags: [geo-aeo, ai-citation, evergreen]
---

# Citation Exposure Metrics

## Citation Exposure Metrics Measurement Scope

This note defines what can be measured when a blog team asks whether content appears in AI answer surfaces. It separates directly available property data from manually observed citations and from market context. Google documentation is the basis for how AI features and preview controls are understood (`g-ai-features`, `g-ai-opt-guide`). Search Console generative AI performance reporting, when available to the property, is the preferred evidence lane (`g-genai-reports`).

The Google `llms.txt` clarification (`g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`) is included because a file request is not a metric for Google Search visibility. `blog-io2026` is useful for product-scale context, but it should not be used as a KPI target.

### Metrics This Note Counts

Count only the fields the selected data source can provide. The Search Console generative AI report lane counts impressions with page or URL, country, device, and date fields under `g-genai-reports`; query and click analysis belongs to classic Search Console via `g-gsc-api` or to an owner-supplied export with provenance.

### Metrics This Note Refuses

Do not count "AI optimized" badges, llms.txt existence, unverified screenshots, or generic AI traffic estimates as citation exposure.

## Citation Exposure Metrics Table

| Metric | Accepted source | Source IDs | Evidence state | Owner | Reporting action |
|---|---|---|---|---|---|
| AI feature impressions | Search Console generative AI report if enabled | `g-genai-reports`, `g-ai-features` | CONFIRMED feature reporting for eligible properties | Analyst | Export with date range and filters |
| Observed citation | Manual SERP or assistant capture with URL and date | `g-ai-features`, `blog-io2026` | Observation, not guaranteed repeatability | GEO reviewer | Store query, locale, device, and screenshot reference |
| Preview-control exposure risk | Snippet setting and page rule | `g-ai-opt-guide`, `g-ai-features` | Official guidance context | Technical SEO | Link to [[AI Feature Preview Controls]] |
| llms.txt request | File exists or stakeholder asks for one | `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` | CONFIRMED no Google Search visibility effect | Researcher | Report as caveat, not KPI |
| Organic query baseline | GSC query and page export | `g-gsc-api` | First-party export when supplied | Analyst | Keep classic Search and AI feature rows separate |
| Post-click engagement | GA4 organic sessions and engagement fields | `g-ga4-data` | First-party export when supplied | Data owner | Use only after URL keys are reconciled |
| Manual sample gap | Query capture exists but no repeatable export | `g-ai-features` | Observation-only evidence | GEO reviewer | Add missing-data note instead of trend language |

## Citation Exposure Metrics Procedure

1. Choose the surface before exporting or sampling.
2. Label the evidence as first-party, official documentation, observation, market study, or unsupported.
3. Keep AI Overview and AI Mode rows separate even when the same URL appears.
4. Add "not available" instead of substituting third-party market data for property reporting.
5. Escalate trend claims to [[Google Data Integrations]] when GSC or GA4 exports are needed.

## Measurement Packet Example

A reviewer samples three queries for one guide and observes an AI Overview citation on only one capture. The metric row remains "observed citation" because `g-ai-features` supports feature context, not repeatability or trend interpretation.

The property owner later provides a Search Console generative AI export. The packet adds surface, page or URL, country, device, date range, and impressions under the first-party lane using `g-genai-reports`, while queries, clicks, CTR, and position stay in the `g-gsc-api` lane unless an owner-supplied AI export documents those fields.

If GA4 export is supplied, post-click engagement is reported after canonical URL matching. `g-ga4-data` supports the GA4 reporting surface, but it does not identify which answer surface created a visit without clean source and medium evidence.

## Metric Failure Patterns

- Manual screenshots are counted as impressions, although `g-genai-reports` is the reporting source for eligible Google properties.
- Market context replaces unavailable property data, despite [[AI Citation Mechanics]] routing broad context away from KPI rows.
- AI Overview and AI Mode observations are merged into one count, weakening the surface-specific caveat from `g-ai-features`.
- GA4 referral sessions are treated as citations without the cited answer URL, which `g-ga4-data` does not provide by itself.

## API Matrix Wiring

[[Google API Evidence Matrix]] consumes this note for field-level evidence planning. It needs surface label, credential tier, export fields, missing-data notes, and the source ID that supports each API surface.

The matrix expects a concrete output list: GSC generative AI fields, GSC classic query and click fields, optional GA4 fields, and manual observation fields that cannot be joined without operator evidence.

## Metric Packet Shape

A Google AI row lists surface, page or URL, country, device, date range, impressions, and `g-genai-reports`. If query-level AI data or AI click data is absent, write "query-level AI data unavailable in the supplied export" instead of inferring it.

A classic organic row lists query, page, clicks, impressions, and `g-gsc-api`.

A GA4 row lists canonical URL, traffic source, engagement fields, and `g-ga4-data`.

A manual citation row lists screenshot reference, locale, device, date, and `g-ai-features`.

## Citation Exposure Metrics Review Loop

Refresh this note when `g-genai-reports` changes, when the property gains or loses access to the report, or when [[2026 Google Update Timeline]] records a relevant Google Search documentation update.
