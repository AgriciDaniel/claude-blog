---
type: spoke
title: "Credential Boundary Rules"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [data-integrations, gsc, ga4, read-only, active]
domain: "Blog Data"
confidence: verified
related:
  - "[[Google Data Integrations]]"
  - "[[Metric Export Schema]]"
  - "[[Read Only Data Access Pattern]]"
  - "[[Missing Data Disclosure]]"
  - "[[Data Confidence Labels]]"
source_urls:
  - "https://developers.google.com/webmaster-tools/v1/searchanalytics/query"
  - "https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect"
  - "https://developers.google.com/speed/docs/insights/v5/get-started"
  - "https://developers.google.com/analytics/devguides/reporting/data/v1"
---

# Credential Boundary Rules

## Rule Scope For Audit Data

Credential Boundary Rules decide what can enter the vault when blog audits use Search Console, URL Inspection, PageSpeed Insights, GA4, or exported reports. The boundary is about evidence custody, not account setup. API docs confirm that the relevant systems can expose Search metrics, URL inspection status, field or lab performance data, and GA4 reporting data, but the vault stores only sanitized evidence summaries tied to source IDs: `g-gsc-api`, `g-urlinspect`, `g-psi`, and `g-ga4-data`.

The operating posture is read-only. A reviewer may cite a metric, a date range, an owner-provided export, or a redaction note. A reviewer may not store OAuth artifacts, service-account files, cookies, browser sessions, account emails, raw private event payloads, or local absolute paths.

## Allowed Actions And Disallowed Actions

- Allowed: summarize a sanitized Search Analytics export with page, query, country, device, clicks, impressions, CTR, and position when the owner approves query storage.
- Allowed: record URL Inspection results for owned URLs, including index status, selected canonical, crawl state, and rich result state.
- Allowed: keep PageSpeed or CrUX-derived URL evidence when it is tied to a public page and no credential material is present.
- Allowed: use GA4 aggregate landing-page engagement when user identifiers and private event parameters are absent.
- Disallowed: request indexing, change Search Console settings, edit GA4, submit a sitemap, publish schema, or run a CMS mutation from this brain.

## Credential Boundary Rules Table

| Rule | Evidence source basis | Applies to | Exception | Approval path |
|---|---|---|---|---|
| Prefer read-only exports or read-only scopes | `g-gsc-api`, `g-urlinspect` | GSC Search Analytics and URL Inspection | Owner can provide a UI export when API access is unavailable | Data owner confirms source, date range, and redaction |
| Never store auth artifacts | `g-gsc-api`, `g-urlinspect`, `g-ga4-data` | Tokens, cookies, service accounts, session files | No exception inside the vault | Reject artifact, purge working copy, log only the missing evidence |
| Keep PageSpeed evidence public-page only | `g-psi` | URL-level lab and field performance checks | Staging URLs require owner-written approval and redacted host labels | SEO lead approves a non-secret alias before citation |
| Separate GA4 engagement from Search demand | `g-ga4-data`, `g-gsc-api` | Landing-page sessions, events, conversions, query metrics | Join only by canonical page and date range | Reviewer documents join key in [[Metric Export Schema]] |
| Block account or platform mutations | All listed IDs | GSC, GA4, PSI, CMS, sitemap, schema deployment | Future release with approval and rollback design only | Convert requested mutation to an advisory recommendation |
| Remove request metadata before citation | `g-gsc-api`, `g-urlinspect`, `g-psi`, `g-ga4-data` | Request URLs, headers, property IDs, worksheet names | Keep an opaque export ID when traceability is needed | Reviewer confirms the identifier cannot reopen account access |
| Treat screenshots as last-resort evidence | `g-urlinspect`, `g-ga4-data` | UI evidence where table export is unavailable | Summarize only after account chrome is cropped | SEO lead signs the redaction note |

## Exceptions That Require Approval

An exception is needed when the export contains sensitive query text, staging URLs, campaign parameters, customer segments, or conversion labels that reveal private operations. Approval must name the owner, approved fields, retention period, redaction method, and rollback action. If any of those fields are missing, route the gap to [[Missing Data Disclosure]] and mark confidence through [[Data Confidence Labels]].

## Redaction Pass Example

A data owner sends a GSC CSV and a GA4 landing-page CSV for one article. Before citation, the reviewer removes property names, hidden sheet tabs, account URLs, and user comments, then keeps page, approved query group, date range, clicks, impressions, and aggregate engagement fields tied to `g-gsc-api` and `g-ga4-data`.

If the same handoff includes a service-account key, the working copy is rejected and only the missing-evidence gap remains. That preserves the read-only evidence lane for `g-gsc-api` and `g-ga4-data` without storing credential material.

[[Google API Evidence Matrix]] consumes the boundary verdict. This note provides approved source surface, credential tier, redacted field list, rejected artifact type, owner, and retention note. The deliverable expects either a sanitized evidence row or a blocked-path row.

## Review And Rollback

1. Inspect the file name, first rows, headers, and metadata before adding any excerpt to the vault.
2. Remove auth fields, local paths, private identifiers, and unapproved query strings.
3. Replace account names with stable labels such as `property_a` or `ga4_property_b`.
4. Cite the evidence with source IDs and export dates, not screenshots of credentials or account screens.
5. If a secret entered a note, remove the text, rotate the exposed credential outside the vault, and leave only a gap note without the secret value.

## Source IDs

- `g-gsc-api`: Search Analytics metrics by dimension, last updated 2026-05-20.
- `g-urlinspect`: URL-level index and rich-result inspection evidence, last updated 2024-07-23.
- `g-psi`: URL performance evidence from PageSpeed Insights API v5, last updated 2025-08-28.
- `g-ga4-data`: GA4 reporting data, last updated 2026-06-29.

## Related

- [[Google Data Integrations]]
- [[Metric Export Schema]]
- [[Read Only Data Access Pattern]]
- [[Missing Data Disclosure]]
- [[Data Confidence Labels]]
