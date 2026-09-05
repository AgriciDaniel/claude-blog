---
type: deliverable
title: "Locale Audit Coverage Matrix"
domain: "Blog Content Brain"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, locale-audit, multilingual]
source_urls:
  - "https://developers.google.com/search/docs/specialty/international/localized-versions"
  - "https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites"
  - "https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls"
  - "https://www.sitemaps.org/protocol.html"
---

# Locale Audit Coverage Matrix

## Coverage Comparison Job For Live Locales

This matrix compares locale completeness, hreflang correctness, canonical parity, stale translations, schema text, and fix-readiness for [[Multilingual Publishing]]. It is a review artifact, not a CMS mutation script. Source IDs wired here are `g-localized`, `g-multiregional`, `g-canonical`, and `sitemaps-org`.

## Locale Rows Required For A Complete Audit

Each row must identify the source URL, target locale URL, language or region code, canonical target, hreflang return state, sitemap presence, and owner. If a locale is absent by strategy, mark it excluded with reason instead of treating it as missing content.

## Locale Audit Coverage Matrix

| Locale element | Evidence cell | Confidence rule | Dry-run fix lane | Next action |
|---|---|---|---|---|
| Page pair completeness | Source and target URLs exist | High only when both pages are reviewed | Create missing-page task | Assign locale owner |
| Hreflang return links | Each alternate links back | `g-localized` required for interpretation | Draft annotation diff | Fix map before publish |
| x-default target | Default URL is named | High when default intent is explicit | Draft default mapping | Confirm with SEO lead |
| Canonical parity | Locale URL canonicals to itself or approved target | `g-canonical` required | Draft canonical diff | Resolve duplicate conflict |
| URL structure | ccTLD, subdomain, or subdirectory path is consistent | `g-multiregional` required | Draft path correction | Route to CMS owner |
| Sitemap coverage | Canonical locale URL appears in discovery list | `sitemaps-org` required | Draft sitemap entry diff | Update after approval |
| Stale translation | Updated date lags source materially | Confidence depends on source article date | Create refresh task | Send to translator |
| Schema locale text | Schema labels match visible locale copy | Needs schema reviewer | Draft schema string diff | Block until aligned |

## Interpretation Rules For Locale Auditors

Any write action must remain outside V1 until an approved publishing adapter exists. The dry-run lane records the change a human or future system should make. Hreflang errors block international handoff because return relationships are central to the annotation model. Canonical conflicts take priority over sitemap additions because discovery of the wrong URL can amplify the wrong signal.
