---
type: spoke
title: "Read Only Data Access Pattern"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [data-integrations, gsc, ga4, read-only, active]
domain: "Blog Data"
confidence: verified
related:
  - "[[Google Data Integrations]]"
  - "[[Metric Export Schema]]"
  - "[[GSC Search Analytics Query Plan]]"
  - "[[URL Inspection Evidence Plan]]"
  - "[[GA4 Blog Engagement Metrics]]"
  - "[[Generative AI Performance Reporting]]"
  - "[[Missing Data Disclosure]]"
  - "[[Data Confidence Labels]]"
source_urls:
  - "https://developers.google.com/webmaster-tools/v1/searchanalytics/query"
  - "https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect"
  - "https://developers.google.com/speed/docs/insights/v5/get-started"
  - "https://developers.google.com/analytics/devguides/reporting/data/v1"
---

# Read Only Data Access Pattern

## Access Pattern Job

Read Only Data Access Pattern defines the safe sequence for requesting, exporting, redacting, and citing property data. It applies to GSC Search Analytics, URL Inspection, PageSpeed Insights, and GA4 reporting. Source IDs are `g-gsc-api`, `g-urlinspect`, `g-psi`, and `g-ga4-data`. The pattern never asks this vault to authenticate, crawl, submit, publish, reconfigure, or mutate a client system.

## Request Packet

A request packet needs the business question, required source, date range, dimensions, property label, export owner, redaction needs, storage destination, and blocked actions. If the requester cannot name the decision the export supports, do not request the data yet.

## Safe Access Sequence

1. Define the audit decision and route it to the narrowest spoke under [[Google Data Integrations]].
2. Ask the data owner for a read-only UI export or approved API-derived export.
3. Require the owner to keep credentials, tokens, service accounts, cookies, and account screenshots outside the vault.
4. Confirm the export fields against [[Metric Export Schema]] before citation.
5. Redact private query, event, customer, path, or conversion details under [[Credential Boundary Rules]].
6. Assign a confidence label through [[Data Confidence Labels]].
7. Store only the sanitized summary, table, or excerpt needed for the report.
8. If a source cannot be supplied, write a gap through [[Missing Data Disclosure]].

## Access Decision Table

| Request | Allowed path | Blocked path | Evidence output | Source IDs |
|---|---|---|---|---|
| Search query trend | Owner exports GSC rows with filters | Agent stores OAuth token or unredacted account UI | Search Analytics packet | `g-gsc-api` |
| Index-state check | Owner inspects owned canonical URLs or supplies sanitized API result | Agent requests indexing or changes property settings | URL inspection packet | `g-urlinspect` |
| Page experience context | Public URL PSI result or owner-supplied export | Private staging test without approval | Performance caveat | `g-psi` |
| Engagement review | GA4 aggregate landing-page report | Raw user-level or event-payload export | Engagement packet | `g-ga4-data` |
| Cross-source comparison | Canonical URL and date windows documented | Mixed windows and unrecorded filters | Advisory joined table | All listed IDs |
| Export refresh | Owner supplies a new dated file with same filters | Agent reuses stale rows silently | Superseded packet plus review note | `g-gsc-api`, `g-ga4-data` |
| Staging performance check | Owner provides redacted host alias and approval | Private URL copied into vault | Approved alias caveat | `g-psi` |

## Decisions This Note Must Record

Record who supplied the export, which fields were removed, which fields remain, and which recommendation depends on the evidence. If the request would require write-capable access, convert it into a recommendation with owner approval and rollback outside V1.

## Access Packet Example

For a site audit, the request asks the owner for GSC query rows, a URL Inspection summary, PSI evidence for public URLs, and aggregate GA4 landing-page data. Each request names the business decision and source ID before export: `g-gsc-api`, `g-urlinspect`, `g-psi`, or `g-ga4-data`.

If the owner offers direct account login instead, the answer is a blocked-path note and a request for sanitized export. [[Full Site Blog Audit Report]] consumes the sanitized packet, removed-field list, source ID, confidence label, and missing-data wording.

## Source IDs

- `g-gsc-api`, `g-urlinspect`, `g-psi`, `g-ga4-data`

## Related

- [[Google Data Integrations]]
- [[Credential Boundary Rules]]
- [[Metric Export Schema]]
- [[Data Confidence Labels]]
- [[Missing Data Disclosure]]
