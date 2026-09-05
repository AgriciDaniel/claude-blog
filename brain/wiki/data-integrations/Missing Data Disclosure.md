---
type: spoke
title: "Missing Data Disclosure"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [data-integrations, gsc, ga4, read-only, active]
domain: "Blog Data"
confidence: verified
related:
  - "[[Google Data Integrations]]"
  - "[[Read Only Data Access Pattern]]"
  - "[[Metric Export Schema]]"
  - "[[GSC Search Analytics Query Plan]]"
  - "[[URL Inspection Evidence Plan]]"
  - "[[GA4 Blog Engagement Metrics]]"
  - "[[Data Confidence Labels]]"
  - "[[Credential Boundary Rules]]"
source_urls:
  - "https://developers.google.com/webmaster-tools/v1/searchanalytics/query"
  - "https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect"
  - "https://developers.google.com/analytics/devguides/reporting/data/v1"
  - "https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports"
---

# Missing Data Disclosure

## Disclosure Job

Missing Data Disclosure gives writers approved language for absent, stale, inaccessible, or redacted evidence. It prevents a missing export from becoming an invented metric. The source IDs for this note are `g-gsc-api`, `g-urlinspect`, `g-ga4-data`, and `g-genai-reports`, which cover Search Analytics, URL Inspection, GA4 reporting, and Search generative AI report context.

## Absence Types Writers Must Distinguish

Missing means the evidence was not available. Stale means it exists but is outside the audit window. Redacted means the owner removed sensitive fields before handoff. Unsupported means the report does not expose the claimed dimension or metric. Those states are not interchangeable, and each should be reflected in [[Data Confidence Labels]].

## Disclosure Library Table

| Missing evidence | Required check | Approved wording | Confidence | Next action | Source IDs |
|---|---|---|---|---|---|
| GSC Search Analytics export | Property access, date range, dimensions, filters | "Search Console performance data was not available for this audit window, so query demand recommendations stay advisory." | `missing` | Request sanitized export | `g-gsc-api` |
| URL Inspection result | Owned URL, property match, inspection timestamp | "Index status was not verified through URL Inspection, so this review does not diagnose indexing state." | `missing` | Inspect owned canonical URL | `g-urlinspect` |
| GA4 engagement packet | Property, landing-page dimension, channel split | "Engagement evidence was not supplied, so post-click behavior is not used to prioritize this content change." | `missing` | Request aggregate landing-page report | `g-ga4-data` |
| Generative AI report | Property eligibility or owner-provided export | "No property-level AI feature report was supplied, so the AI visibility section uses only non-AI Search data and clearly marked context." | `missing` | Recheck availability in next reporting cycle | `g-genai-reports` |
| Redacted query or event field | Redaction reason and owner approval | "The export was redacted for privacy, so totals and examples are limited to the fields retained." | `sample` | Keep limitation beside the finding | `g-gsc-api`, `g-ga4-data` |
| Stale comparison export | Export date, covered window, refresh trigger | "The comparison window is stale, so trend direction is not used as a current priority signal." | `stale` | Re-export matched dates | `g-gsc-api` |
| Unsupported AI query column | Visible dimensions and owner confirmation | "The AI feature report did not expose query-level detail, so query-level AI visibility is not claimed." | `missing` | Keep page-level wording only | `g-genai-reports` |

## Decisions The Disclosure Must Record

Every disclosure needs a missing source, reason, owner, date checked, fallback evidence, and blocked claim. The blocked claim matters most. If GSC is absent, the report cannot claim query opportunity from property data. If URL Inspection is absent, the report cannot say whether Google selected a different canonical. If GA4 is absent, the report cannot say engagement improved or worsened. If generative AI reporting is absent, route broad AI interpretation to [[AI Citation Mechanics]] as context only.

## Operating Procedure

1. Ask which claim the missing evidence would have supported.
2. Check whether another first-party source can answer the same claim.
3. If not, write one disclosure sentence and downgrade the confidence label.
4. Keep the fallback source separate from the missing source.
5. Revisit the disclosure when the owner supplies a new export or confirms continued absence.

## Disclosure Scenario

A report draft says a post lost demand, but the only GSC export is outside the review window. The line changes to a stale-data caveat, because `g-gsc-api` supports query metrics only when the covered dates match the decision.

When GA4 engagement exists for the same page, it remains a separate post-click context under `g-ga4-data`. [[Full Site Blog Audit Report]] consumes the disclosure sentence, blocked claim, fallback source, owner, and next check date.

## Source IDs

- `g-gsc-api`, `g-urlinspect`, `g-ga4-data`, `g-genai-reports`

## Related

- [[Google Data Integrations]]
- [[Read Only Data Access Pattern]]
- [[Metric Export Schema]]
- [[GSC Search Analytics Query Plan]]
- [[URL Inspection Evidence Plan]]
- [[GA4 Blog Engagement Metrics]]
- [[Data Confidence Labels]]
- [[Credential Boundary Rules]]
