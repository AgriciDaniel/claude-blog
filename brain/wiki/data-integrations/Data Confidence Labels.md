---
type: spoke
title: "Data Confidence Labels"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [data-integrations, gsc, ga4, read-only, active]
domain: "Blog Data"
confidence: verified
related:
  - "[[Google Data Integrations]]"
  - "[[Missing Data Disclosure]]"
  - "[[Read Only Data Access Pattern]]"
  - "[[Metric Export Schema]]"
  - "[[GSC Search Analytics Query Plan]]"
  - "[[URL Inspection Evidence Plan]]"
  - "[[Credential Boundary Rules]]"
  - "[[Page URL Canonical Data Checks]]"
source_urls:
  - "https://developers.google.com/webmaster-tools/v1/searchanalytics/query"
  - "https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect"
  - "https://developers.google.com/speed/docs/insights/v5/get-started"
  - "https://developers.google.com/analytics/devguides/reporting/data/v1"
---

# Data Confidence Labels

## Label Job

Data Confidence Labels translate metric evidence into five working labels: `verified`, `advisory`, `missing`, `stale`, and `sample`. The label is attached to the evidence packet, not to the whole article. Search Console, URL Inspection, PageSpeed Insights, and GA4 each expose different evidence shapes, so the same page can have verified query metrics, stale inspection evidence, sampled performance data, and advisory engagement interpretation at the same time. Use `g-gsc-api`, `g-urlinspect`, `g-psi`, and `g-ga4-data` as the source IDs for those distinctions.

## Inputs This Note Requires

- The export or report owner.
- The source surface and source ID.
- Retrieval date and covered date range.
- Applied filters, including country, device, search type, page, query group, or GA4 dimension.
- Canonical URL handling from [[Page URL Canonical Data Checks]].
- A short reason for the selected confidence label.

## Data Evidence Packet Table

| Label | Use when | Required input | Source IDs | Owner | Next action |
|---|---|---|---|---|---|
| `verified` | First-party export is current, scoped, and redacted | Source surface, date range, owner, export timestamp | `g-gsc-api`, `g-urlinspect`, `g-ga4-data` | Data owner | Use in report with exact caveats |
| `advisory` | Evidence supports context but not a direct recommendation | Aggregated GA4 engagement, PSI lab result, or cross-source interpretation | `g-psi`, `g-ga4-data` | SEO reviewer | Pair with a stronger source before prioritizing |
| `missing` | Access, report, or required field is absent | Missing source and reason | All listed IDs | Requester | Send wording to [[Missing Data Disclosure]] |
| `stale` | Retrieval or covered date range is outside the audit window | Last retrieved date and refresh trigger | All listed IDs | Operator | Re-export or downgrade recommendation |
| `sample` | Data is partial, filtered, redacted, or not complete enough for totals | Filter list and excluded rows | `g-gsc-api`, `g-psi`, `g-ga4-data` | Analyst | Avoid totals and phrase as directional |

## Decisions The Label Must Record

The label must say whether the evidence proves performance, only supports diagnosis, or merely records that a data source exists. For example, URL Inspection can confirm the indexed state for an owned URL, but it does not prove that the content deserves to rank. GA4 can show engagement after a visit, but it cannot supply Search query demand. PageSpeed data can support experience diagnosis, but it should not replace content, query, or index evidence.

## Label Assignment Mini Case

A page has current GSC rows, no URL Inspection timestamp, and a GA4 export with channel split. Assign `verified` to the Search Analytics packet (`g-gsc-api`), `missing` to index-state evidence (`g-urlinspect`), and `verified` or `advisory` to GA4 depending on canonical landing-page alignment (`g-ga4-data`).

The report can discuss query movement and engagement, but it cannot call the page indexed until an inspection packet exists. If a PageSpeed lab result is the only technical evidence, keep the performance finding separate from content scoring and cite `g-psi`.

[[Blog Analyzer Score Report]] consumes one label per evidence row. This note provides source ID, covered dates, filters, label reason, and next action; the score report expects those fields beside each major deduction.

## Operating Procedure

1. Name the claim the data is supposed to support.
2. Select the source ID and source surface before reading the metric.
3. Check date range, filters, canonical URL handling, and owner approval.
4. Assign one label per evidence packet, not one label per note.
5. Add the next action: use, refresh, disclose gap, or seek stronger evidence.
6. Reopen the label when any metric is re-exported or the source ledger refresh date passes.

## Wording Guardrails

Do not say "proves ranking cause" for any label. Do not upgrade a GA4 engagement trend into Search demand. Do not treat URL Inspection as a live crawl test. If the available evidence is partial, write the limitation in the same sentence as the recommendation.

## Source IDs

- `g-gsc-api`, `g-urlinspect`, `g-psi`, `g-ga4-data`

## Related

- [[Google Data Integrations]]
- [[Missing Data Disclosure]]
- [[Read Only Data Access Pattern]]
- [[Metric Export Schema]]
- [[GSC Search Analytics Query Plan]]
- [[URL Inspection Evidence Plan]]
- [[Credential Boundary Rules]]
- [[Page URL Canonical Data Checks]]
