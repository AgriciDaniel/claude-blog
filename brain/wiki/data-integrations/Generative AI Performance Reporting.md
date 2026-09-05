---
type: spoke
title: "Generative AI Performance Reporting"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [data-integrations, gsc, ga4, read-only, active]
domain: "Blog Data"
confidence: verified
related:
  - "[[Google Data Integrations]]"
  - "[[Metric Export Schema]]"
  - "[[Credential Boundary Rules]]"
  - "[[Missing Data Disclosure]]"
  - "[[AI Citation Mechanics]]"
source_urls:
  - "https://developers.google.com/webmaster-tools/v1/searchanalytics/query"
  - "https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect"
  - "https://developers.google.com/speed/docs/insights/v5/get-started"
  - "https://developers.google.com/analytics/devguides/reporting/data/v1"
  - "https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports"
---

# Generative AI Performance Reporting

## Report Purpose When An Export Exists

Generative AI Performance Reporting turns a property owner's AI feature export into a cautious audit section. This note does not claim API parity or feature availability by itself because the assigned sources here are the general data-source IDs: `g-gsc-api`, `g-urlinspect`, `g-psi`, and `g-ga4-data`. Confirmed AI feature background belongs in [[AI Citation Mechanics]] and the hub-level [[Google Data Integrations]] source trail. Inside this note, the task is to reconcile an owner-provided export with ordinary Search metrics, indexed URL evidence, page experience checks, and GA4 engagement.

## Audience, Scope, And Source Inputs

The primary audience is the SEO reviewer writing an audit or monitoring memo. The scope is page-level interpretation, not a promise of AI Overview or AI Mode visibility. Required inputs are the exported file, property label, export date, visible dimensions, metric definitions, and a confidence label. If the export is missing, use [[Missing Data Disclosure]] rather than estimating from ordinary Search Analytics.

## Findings This Report Must Not Overclaim

- Do not infer query-level AI feature data from ordinary Search Analytics rows.
- Do not treat GA4 referral or engagement data as proof that a URL was cited by an AI feature.
- Do not use URL Inspection to diagnose AI citation quality.
- Do not treat PageSpeed output as an AI feature ranking or citation factor.
- Do not compare external market benchmarks against the property unless [[First Party Versus Market Data]] marks the benchmark as context only.

## Findings Table

| Severity | Evidence | Recommendation | Owner | Due date | Source IDs |
|---|---|---|---|---|---|
| High | AI feature export is unavailable for the property | State the gap and rely on standard GSC, GA4, and URL evidence only | SEO lead | Before report delivery | `g-gsc-api`, `g-ga4-data` |
| Medium | AI feature export contains page rows but no query detail | Report page visibility only and avoid query-level wording | Analyst | Same review cycle | `g-gsc-api` |
| Medium | AI feature page URL differs from canonical reporting URL | Normalize through [[Page URL Canonical Data Checks]] before comparing | Technical SEO | Before trend charting | `g-urlinspect`, `g-gsc-api` |
| Low | Page has engagement but no Search feature export | Treat engagement as post-click behavior, not AI visibility | Content strategist | During brief update | `g-ga4-data` |
| Low | Performance evidence is requested for the same page | Add PSI as experience context, not as citation evidence | Web performance owner | Next audit pass | `g-psi` |
| Medium | AI feature rows are mixed with standard Search rows | Keep the two evidence packets separate before trend wording | Analyst | Before report charting | `g-genai-reports`, `g-gsc-api` |
| High | Export omits the queried AI feature dimension | Block query-level AI claims and disclose the missing column | SEO lead | Before client handoff | `g-genai-reports` |

## Delivery Procedure

1. Verify whether the property owner supplied an AI feature export or confirmed absence.
2. Record the export's exact dimensions and metrics without inventing missing columns.
3. Join the export to canonical page URLs before comparing it with GSC or GA4.
4. Add a separate caveat when only standard Search Analytics is available.
5. Route broad AI citation claims to [[AI Citation Mechanics]] and cite this note only for the evidence-handling procedure.

## AI Export Reconciliation Example

An owner supplies a page-level generative AI report but no query column. The report may say that property-level AI feature rows were available for the page under `g-genai-reports`, but it must not name query winners from ordinary Search Analytics under `g-gsc-api`.

If the AI row URL uses a parameterized path, canonical mapping is required before joining with engagement. That join can use `g-urlinspect` for URL evidence and `g-ga4-data` only for post-click behavior.

[[GEO Citation Readiness Register]] consumes the reconciled evidence state. This note provides AI export availability, page URL match, missing dimensions, confidence label, and caveat text; the register expects no citation guarantee.

## Source IDs

- `g-gsc-api`, `g-urlinspect`, `g-psi`, `g-ga4-data`, `g-genai-reports`

## Related

- [[Google Data Integrations]]
- [[Metric Export Schema]]
- [[Credential Boundary Rules]]
- [[Missing Data Disclosure]]
- [[AI Citation Mechanics]]
- [[First Party Versus Market Data]]
