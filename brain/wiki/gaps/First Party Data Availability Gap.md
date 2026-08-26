---
type: gap
title: "First Party Data Availability Gap"
status: seed
created: 2026-08-25
updated: 2026-08-25
tags: [data-integrations, evidence, gap]
domain: "Blog Content Brain"
confidence: advisory
related:
  - "[[Google Data Integrations]]"
  - "[[GSC Search Analytics Query Plan]]"
  - "[[Generative AI Performance Reporting]]"
  - "[[Historical Performance Review]]"
  - "[[Metric Export Schema]]"
  - "[[Research Pack Index]]"
  - "[[Evidence Gap Register]]"
  - "[[Uncertainty Eval Policy]]"
source_urls:
  - "https://developers.google.com/webmaster-tools/v1/searchanalytics/query"
  - "https://developers.google.com/analytics/devguides/reporting/data/v1"
---

# First Party Data Availability Gap

## Summary

The Brain can define safe Search Console and GA4 analysis, but it cannot assume a property, date range, or export exists. This seed records what remains unknown before performance claims become property-specific.

## Open evidence

| Needed evidence | Why it matters | Acceptable input | Blocked conclusion |
|---|---|---|---|
| Verified GSC property | Establishes the site boundary | Redacted property identifier | Sitewide Search performance |
| Search Analytics range | Controls seasonality | Start date, end date, timezone | Trend direction |
| Query and page dimensions | Separates topics and URLs | Export schema from [[GSC Search Analytics Query Plan]] | Cannibalization |
| Search appearance fields | Distinguishes supported surfaces | Available dimension values | AI feature segmentation |
| GA4 channel mapping | Defines organic sessions | Redacted channel export | Engagement comparison |
| Publication history | Explains page age and changes | URL, first publish, update dates | Decay diagnosis |
| Known migrations | Explains discontinuities | Dated migration ledger | Before and after claims |
| Consent effects | Limits analytics completeness | Measurement note | Absolute user counts |

## Intake gate

1. Confirm the operator is authorized to use the export.
2. Remove credentials, email addresses, and account identifiers.
3. Record date range, timezone, filters, dimensions, and row limits.
4. Validate the file against [[Metric Export Schema]].
5. Preserve the original outside the public projection.
6. Write only aggregated findings into the wiki.
7. Apply a confidence tag to every property-specific conclusion.
8. Keep missing values visible instead of estimating them.

## Resolution criteria

This gap closes only for a named analysis when the required export, scope, and method are present. It does not close globally because future properties may still lack access.

## Failure signals

- A market study is substituted for site data.
- An average position is treated as a rank.
- A partial export is described as complete.
- AI feature reporting is assumed to exist for every property.
- GA4 sessions are equated with GSC clicks.
- Timezones or filters are omitted.

## Handoff

Route accepted data to [[Historical Performance Review]]. Route format failures to [[Metric Export Schema]]. Route unsupported Search conclusions to [[Evidence Gap Register]]. Keep the overall answer advisory until the owner confirms the analysis scope.
