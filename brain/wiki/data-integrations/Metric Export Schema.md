---
type: spoke
title: "Metric Export Schema"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [data-integrations, gsc, ga4, read-only, active]
domain: "Blog Data"
confidence: verified
related:
  - "[[Google Data Integrations]]"
  - "[[Credential Boundary Rules]]"
  - "[[Generative AI Performance Reporting]]"
  - "[[Missing Data Disclosure]]"
source_urls:
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://schema.org/docs/full.html"
  - "https://www.w3.org/TR/json-ld11/"
---

# Metric Export Schema

## Structured Export Job

Metric Export Schema defines the internal data contract for sanitized blog performance packets. The source IDs assigned to this note are structured-data and JSON-LD sources: `g-intro-sd`, `g-search-gallery`, `schema-full`, and `w3c-jsonld`. That makes the key boundary explicit: internal metric exports may be structured, but they are not public Search structured data and must not be published as invented rich-result markup.

## Schema Meaning In This Note

Use "schema" here as a table contract for evidence, not as a promise of Google rich results. Google's structured data guidance covers eligible markup and recommends JSON-LD for Search structured data. The Search gallery limits which public rich-result types Google documents. Schema.org provides a wider vocabulary than Google Search supports, and W3C JSON-LD defines a linked-data serialization. Those sources guide the boundary between internal metric packets and publishable page markup.

## Sanitized Export Schema Table

| Field | Required | Validation target | Warning | Source ID |
|---|---|---|---|---|
| `export_id` | Yes | Stable opaque identifier | Do not include account names or local paths | `w3c-jsonld` |
| `source_id` | Yes | Ledger ID such as `g-gsc-api` or `g-ga4-data` | This is evidence provenance, not public schema markup | `g-intro-sd` |
| `page_url` | Yes | Canonical public URL or approved alias | Remove private draft tokens and campaign secrets | `schema-full` |
| `entity_type` | Yes | Internal value such as `BlogPosting`, `Article`, or `LandingPage` | Use Schema.org names only when they match visible page facts | `schema-full` |
| `metric_name` | Yes | Controlled list from the data-integration spoke | Never invent a Search rich-result property for metrics | `g-search-gallery` |
| `metric_value` | Yes | Number, rate, label, or null with reason | Keep sampled or missing values labeled | `g-intro-sd` |
| `date_start` and `date_end` | Yes | ISO dates | Do not mix GA4 and GSC windows without noting it | `w3c-jsonld` |
| `public_schema_candidate` | No | `none`, `Article`, `BlogPosting`, `BreadcrumbList`, or another supported type | Candidate status does not mean publish approval | `g-search-gallery` |
| `confidence_label` | Yes | `verified`, `advisory`, `missing`, `stale`, or `sample` | Internal evidence state is not a Schema.org property | `schema-full` |
| `redaction_note` | Conditional | Removed field categories, not private values | Do not serialize secrets into JSON-LD | `g-intro-sd` |
| `consumer_deliverable` | Yes | Wikilinked report or matrix name | Routing metadata should not become page markup | `w3c-jsonld` |

## Unsupported Markup To Avoid

Do not place clicks, impressions, CTR, average position, engagement rate, or private conversion metrics inside public BlogPosting or Article JSON-LD. Do not use the full Schema.org hierarchy as proof that Google Search supports a rich result. Do not turn a metric packet into an `@graph` block on a live page unless [[Blog Schema Stack]] confirms that every property is visible, useful, and supported for the page context.

## Packet Boundary Example

A GSC export row becomes an internal packet with `source_id` set to `g-gsc-api`, `metric_name` set to impressions, and `public_schema_candidate` set to `none`. The Search gallery does not make private performance metrics eligible rich-result fields, so the public schema path stays blocked under `g-search-gallery`.

If the same packet contains a visible article headline, only that visible page fact may travel toward Article or BlogPosting review. [[Schema Generation Output Contract]] consumes the candidate field, visible fact list, unsupported-warning note, and JSON-LD serialization cue from `w3c-jsonld`.

Edge cases that break this note are usually vocabulary leaks: using `schema-full` breadth as Google eligibility, placing metric values in public JSON-LD, or omitting a redaction note because the packet is "internal." Keep those failures blocked through `g-search-gallery` and `g-intro-sd`.

## Publishing Boundary

1. Build metric exports as internal evidence tables.
2. Validate provenance, dates, redaction, and confidence labels before citation.
3. If a field might inform public structured data, route it to [[Blog Schema Stack]].
4. Keep public JSON-LD limited to visible page facts and supported Search use cases.
5. Store unpublished metrics only in notes or reports that follow [[Credential Boundary Rules]].

## Source IDs

- `g-intro-sd`, `g-search-gallery`, `schema-full`, `w3c-jsonld`

## Related

- [[Google Data Integrations]]
- [[Credential Boundary Rules]]
- [[Generative AI Performance Reporting]]
- [[Missing Data Disclosure]]
- [[Blog Schema Stack]]
