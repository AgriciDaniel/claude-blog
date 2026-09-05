---
type: spoke
title: "Page URL Canonical Data Checks"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [data-integrations, gsc, ga4, read-only, active]
domain: "Blog Data"
confidence: verified
related:
  - "[[Google Data Integrations]]"
  - "[[Credential Boundary Rules]]"
  - "[[Data Confidence Labels]]"
  - "[[Missing Data Disclosure]]"
  - "[[Read Only Data Access Pattern]]"
  - "[[Metric Export Schema]]"
  - "[[Query Dimension Hygiene]]"
  - "[[First Party Versus Market Data]]"
source_urls:
  - "https://developers.google.com/webmaster-tools/v1/searchanalytics/query"
  - "https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect"
  - "https://developers.google.com/speed/docs/insights/v5/get-started"
  - "https://developers.google.com/analytics/devguides/reporting/data/v1"
---

# Page URL Canonical Data Checks

## Canonical Join Job

Page URL Canonical Data Checks map exported rows to the page identity used by the blog brain. Search Analytics can group performance by page, URL Inspection can report the inspected URL and Google's selected canonical evidence, PageSpeed checks are URL-specific, and GA4 often reports path-like landing pages. Without a canonical join, the same article can appear as multiple rows because of query parameters, trailing slashes, HTTP variants, language paths, or analytics path formatting. Cite `g-gsc-api`, `g-urlinspect`, `g-psi`, and `g-ga4-data` when this note supports a data join.

## Data Joins This Note Allows

This note allows joins from raw exported URLs to a canonical reporting URL. It does not decide whether the canonical tag is correct, whether a page should be redirected, or whether content should be consolidated. Those are recommendations that need technical SEO approval and rollback notes.

## Canonical Evidence Table

| Page group | Target intent | Canonical owner | Anchor for joins | Evidence state | Source IDs |
|---|---|---|---|---|---|
| Blog article | Compare page performance over time | Content owner plus technical SEO | Final public canonical URL | GSC page rows normalized | `g-gsc-api` |
| Indexed URL check | Detect indexed canonical mismatch | Technical SEO | URL Inspection inspected URL and selected canonical | Verified for inspected URL only | `g-urlinspect` |
| Page experience check | Compare performance for the same URL variant | Web performance owner | PSI tested URL matched to canonical | Advisory if variant differs | `g-psi` |
| Landing-page engagement | Join GA4 paths to page records | Analytics owner | Normalized landing page path or URL | Sample if query strings remain | `g-ga4-data` |
| Topic cluster spoke | Roll up metrics by canonical page | SEO lead | Canonical URL plus internal link anchor | Verified after all row variants merge | `g-gsc-api`, `g-ga4-data` |
| Query-parameter article URL | Remove tracking noise from reporting joins | Analyst | Canonical URL plus stripped parameter list | Sample until owner approves parameter rule | `g-gsc-api`, `g-ga4-data` |
| Locale path variant | Keep language or market pages distinct | Localization owner | Locale URL and approved canonical target | Blocked if locale path is merged blindly | `g-urlinspect`, `g-gsc-api` |

## URL Normalization Procedure

1. Start with the page inventory used by [[Semantic Topic Clusters]] or the audit brief.
2. Normalize scheme, host, trailing slash, fragments, known tracking parameters, and case only when the site rules allow it.
3. Preserve locale, pagination, and variant paths until the owner confirms they are not distinct pages.
4. Compare URL Inspection evidence before merging rows that Google may canonicalize differently.
5. Store the mapping in the metric packet before GSC, PSI, or GA4 comparisons are charted.

## Decisions This Note Must Record

Record the canonical URL, the raw URL variants, the rule used to merge them, and the owner who approved the rule. If a variant cannot be safely merged, keep it as a separate row and label the rollup `sample` through [[Data Confidence Labels]].

## Canonical Join Example

An audit receives `/blog/guide?utm_source=email`, `/blog/guide/`, and a GA4 path `/blog/guide`. The reviewer keeps the raw variants, asks the owner to approve the parameter rule, and joins only after GSC page rows and GA4 landing paths map to the same canonical under `g-gsc-api` and `g-ga4-data`.

If URL Inspection reports a different Google-selected canonical, the rollup stops. [[Cannibalization Resolution Matrix]] consumes the raw variant list, approved canonical, selected-canonical evidence, confidence label, and unresolved merge risk from `g-urlinspect`.

## Source IDs

- `g-gsc-api`, `g-urlinspect`, `g-psi`, `g-ga4-data`

## Related

- [[Google Data Integrations]]
- [[Query Dimension Hygiene]]
- [[Metric Export Schema]]
- [[URL Inspection Evidence Plan]]
- [[GA4 Blog Engagement Metrics]]
- [[Semantic Topic Clusters]]
