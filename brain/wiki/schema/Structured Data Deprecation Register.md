---
type: spoke
title: "Structured Data Deprecation Register"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [schema, blog-schema, evergreen]
domain: "Blog Structured Data"
confidence: verified
related:
  - "[[Blog Schema Stack]]"
  - "[[2026 Google Update Timeline]]"
  - "[[Schema Validation Workflow]]"
source_urls:
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://schema.org/docs/full.html"
  - "https://www.w3.org/TR/json-ld11/"
---
# Structured Data Deprecation Register

## Register Scope

This register records schema advice that must be removed, quarantined, or rechecked because it depends on current Google support, visible page content, or JSON-LD validity. It is not the canonical Google changelog. Dated update history belongs in [[2026 Google Update Timeline]], while this note tells schema reviewers what to do with outdated or unsupported advice inside blog workflows.

The assigned evidence set is `g-intro-sd`, `g-search-gallery`, `schema-full`, and `w3c-jsonld`. These sources support CONFIRMED rules about visible-content alignment, supported-feature checking, vocabulary breadth, and JSON-LD serialization. If a future deprecation requires a changelog-specific source, add that source to the ledger before making a dated claim.

## Structured Data Deprecation Register Table

| Item to track | Source id | Owner | Confidence | Status | Next review date | Rollback trigger |
|---|---|---|---|---|---|---|
| Rich-result promise for a type absent from current Search Gallery | `g-search-gallery` | SEO lead | CONFIRMED for gallery scope | Remove promise, keep vocabulary only if useful | 2026-08-01 | Gallery adds or restores a matching feature page |
| Markup for facts hidden from readers | `g-intro-sd` | Editor | CONFIRMED | Block until the fact is visible or removed from schema | 2026-08-01 | Page is revised so the marked-up fact is inspectable |
| Schema.org-only type sold as Google feature | `schema-full`, `g-search-gallery` | Schema reviewer | CONFIRMED for source split | Reword as vocabulary support, not Search display | 2026-08-01 | Google documentation adds explicit support |
| Invalid JSON-LD pattern copied from legacy templates | `w3c-jsonld` | Template engineer | CONFIRMED | Replace pattern before publishing | 2026-08-01 | Template parser and rendered HTML both validate |
| Product, VideoObject, or Q and A add-on used by default | `g-intro-sd` | Delivery owner | CONFIRMED | Require page-specific evidence before use | 2026-08-01 | The article visibly contains qualifying content |
| FAQPage rich-result language retained in blog templates | `g-faqpage-sd` | SEO lead | CONFIRMED | Remove feature promise and keep only useful visible Q and A | 2026-08-01 | Google restores documented FAQ rich-result support |
| Product sale fields without visible sale duration | `g-merchant-listing-sd` | Ecommerce reviewer | CONFIRMED | Block offer markup until sale timing is visible and maintained | 2026-08-09 | Price and sale dates become inspectable on the page |
| VideoObject emitted for hidden or missing media | `g-video` | Media owner | CONFIRMED | Remove VideoObject until playable video and thumbnail evidence exist | 2026-08-01 | Final page renders the qualifying media reliably |
| Search feature claim lacks a checked gallery date | `g-search-gallery` | SEO lead | CONFIRMED | Recheck support before client-facing language ships | 2026-08-01 | Source-ledger refresh confirms the wording remains current |

## Events Routed Elsewhere

Algorithm updates, Search Console reporting changes, and SERP volatility do not belong here unless they change schema advice. Put those in [[2026 Google Update Timeline]] or monitoring notes. Editorial quality guidance belongs in [[E-E-A-T for Blog Content]], and implementation defects belong in [[Schema Validation Workflow]].

## Register Use Example

A legacy theme still advertised "FAQ rich-result schema included" on every blog post. The register action removed that promise and preserved visible Q and A content only where it helped readers, source ID `g-faqpage-sd`.

The same theme emitted Product offer fields for a seasonal sale snippet. The sale price was visible, but the sale duration was not shown or maintained in the article, so the register sent the item to ecommerce review, source ID `g-merchant-listing-sd`.

A video node appeared on pages where the embedded player was lazy-loaded below a consent wall. The register blocked VideoObject until the final page showed a playable video and thumbnail evidence, source ID `g-video`.

The resulting output was not a sitewide ban on FAQ text, product mentions, or videos. It was a dated set of removal and retest decisions tied to specific source IDs.

## Register-Specific Failure Cases

- Deprecated feature copy can survive after JSON-LD is removed, source ID `g-faqpage-sd`.
- Vocabulary support can be mistaken for Google display support, source IDs `schema-full` and `g-search-gallery`.
- Sale fields can stale faster than article copy, source ID `g-merchant-listing-sd`.
- Media embeds can disappear behind consent or mobile breakpoints, source ID `g-video`.
- Monthly review dates should follow the ledger refresh cadence, source ID `g-search-gallery`.
- Feature-support caveats should name the checked source date, source ID `g-search-gallery`.

## Register Consumer Contract

[[Full Site Blog Audit Report]] consumes this register when schema problems repeat across many URLs.

Audit input supplied: affected pattern, source ID, owner, confidence, status, next review date, and rollback trigger.

Expected audit output: sitewide recommendation, severity, affected URL sample, owner, and dated recheck action.

## Review Loop

Run this register monthly with the source-ledger refresh cycle. For every schema template, ask whether the advice still has a current source, whether the page visibly supports it, and whether the note describes vocabulary support separately from Search feature support. Any unresolved item becomes a blocker or a dated advisory caveat.
