---
type: spoke
title: "Query Dimension Hygiene"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [data-integrations, gsc, ga4, read-only, active]
domain: "Blog Data"
confidence: verified
related:
  - "[[Google Data Integrations]]"
  - "[[Page URL Canonical Data Checks]]"
  - "[[Credential Boundary Rules]]"
  - "[[Data Confidence Labels]]"
  - "[[Missing Data Disclosure]]"
  - "[[Read Only Data Access Pattern]]"
  - "[[First Party Versus Market Data]]"
  - "[[Generative AI Performance Reporting]]"
source_urls:
  - "https://developers.google.com/webmaster-tools/v1/searchanalytics/query"
  - "https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect"
  - "https://developers.google.com/analytics/devguides/reporting/data/v1"
  - "https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports"
---

# Query Dimension Hygiene

## Dimension Scope

Query Dimension Hygiene standardizes how GSC query exports are grouped, filtered, and compared. It focuses on Search Analytics dimensions and their downstream joins with URL Inspection, GA4, and generative AI report availability. Use source IDs `g-gsc-api`, `g-urlinspect`, `g-ga4-data`, and `g-genai-reports`. The note does not define keyword strategy by itself; it defines the measurement frame that makes a strategy defensible.

## Filters This Note Freezes

Freeze date range, search type, country, device, page filter, query grouping rule, brand/non-brand rule, and redaction policy before pulling data. If any one changes, call the next export a new packet instead of appending rows to the old one.

## Query Dimension Control Table

| Decision | Required input | Evidence state | Owner | Next action | Source IDs |
|---|---|---|---|---|---|
| Date range | Start date, end date, comparison window | Verified if both windows are explicit | SEO lead | Lock before export | `g-gsc-api` |
| Search type | Web, image, video, news, or other available surface | Sample if mixed or unknown | Analyst | Split before charting | `g-gsc-api` |
| Country | Country filter or all-country note | Advisory if locale strategy is country-specific and filter is absent | Strategist | Align with locale brief | `g-gsc-api` |
| Device | Desktop, mobile, tablet, or all | Sample if device mix changes between periods | Analyst | Keep separate when UX issue suspected | `g-gsc-api`, `g-ga4-data` |
| Page filter | Canonical page, folder, or URL contains rule | Verified after canonical mapping | Technical SEO | Route variants to [[Page URL Canonical Data Checks]] | `g-gsc-api`, `g-urlinspect` |
| Query grouping | Regex, manual list, brand list, topic list | Advisory until reviewed | SEO lead | Store grouping rule with export | `g-gsc-api` |
| AI report availability | Owner confirms export exists or not | Missing if no property report is supplied | Reviewer | Route to [[Generative AI Performance Reporting]] | `g-genai-reports` |
| Brand split | Approved brand terms and exclusion rule | Sample until owner reviews ambiguous terms | Strategist | Freeze list before comparison | `g-gsc-api` |
| Query privacy handling | Redaction rule and retained aggregate fields | Sample when examples are removed | Data owner | Use group summaries only | `g-gsc-api` |

## Grouping Rules

Brand groups should be explicit, not guessed from a single term. Topic groups should use the same inclusion and exclusion rules across comparison windows. Redacted queries stay redacted. If privacy rules remove examples, write a group-level summary and do not invent query strings.

## Operating Procedure

1. Write the dimension recipe before export.
2. Pull a small sample and check that rows match the intended pages.
3. Apply canonical URL mapping before page rollups.
4. Freeze query groups and device or country filters before trend interpretation.
5. Attach the recipe to the metric packet so a reviewer can reproduce the table.

## Grouping Decision Example

A cluster plan needs demand for "pricing guide" queries without branded support terms. The recipe freezes web search, target country, mobile plus desktop split, canonical page filter, and a reviewed brand exclusion list before pulling `g-gsc-api` rows.

If privacy review removes sample query strings, the cluster still receives aggregate groups but no quoted examples. [[Semantic Cluster Execution Plan]] consumes the query recipe, grouped demand packet, excluded-term rule, confidence label, and AI report availability note from `g-genai-reports`.

## Source IDs

- `g-gsc-api`, `g-urlinspect`, `g-ga4-data`, `g-genai-reports`

## Related

- [[Google Data Integrations]]
- [[GSC Search Analytics Query Plan]]
- [[Page URL Canonical Data Checks]]
- [[First Party Versus Market Data]]
- [[Generative AI Performance Reporting]]
- [[Missing Data Disclosure]]
