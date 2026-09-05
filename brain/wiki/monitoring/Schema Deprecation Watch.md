---
type: spoke
title: "Schema Deprecation Watch"
domain: "Google Update Monitoring"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [monitoring, google-updates, active]
source_urls:
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://developers.google.com/search/docs/appearance/structured-data/merchant-listing"
  - "https://developers.google.com/search/updates#july-2026"
  - "https://schema.org/docs/full.html"
  - "https://www.w3.org/TR/json-ld11/"
  - "https://developers.google.com/search/blog/2025/06/simplifying-search-results"
---

# Schema Deprecation Watch

## Schema Deprecation Watch Structured Data Job

This spoke keeps deprecated or unsupported rich-result tactics out of blog briefs. It distinguishes three things that are often blurred: Schema.org vocabulary, JSON-LD syntax, and Google Search rich-result support. A type can exist in Schema.org and still be unsupported for a Google rich result.

## Schema Types And Blog Situations Covered

The watch covers Article or BlogPosting, Organization, Person, BreadcrumbList, Product or merchant-listing cases, VideoObject, FAQ or Q and A content, and any structured-data feature proposed in a brief. The canonical publishing guidance lives in [[Blog Schema Stack]]. This note only decides whether the tactic is still supported or should be blocked.

## Deprecated Or Unsupported Markup To Avoid

Avoid recommending deprecated Google rich-result features as current tactics. Avoid presenting FAQPage as a current Google FAQ rich result tactic after the 2026 retirement recorded elsewhere in the ledger. Avoid using Schema.org existence as proof of Search-gallery eligibility. Avoid making Reservation, OrderAction, or other unsupported action markup a blog deliverable unless a current Google Search source supports it.

## Schema Deprecation Watch Schema Table

| Schema situation | Required properties or check | Validation target | Warning | Source ID |
|---|---|---|---|---|
| General blog structured data | JSON-LD preferred, visible content must match markup | Rich Results Test and schema validator | Markup eligibility is not a ranking guarantee | `g-intro-sd`, `w3c-jsonld` |
| Supported rich-result selection | Confirm type appears in Google's Search gallery | Google Search gallery | Schema.org type alone is insufficient | `g-search-gallery`, `schema-full` |
| Retired or simplified result types | Check whether the feature was phased out | Search Central deprecation post | Do not sell retired visuals as active rich-result features | `g-update-2025-06-19-structured-data-deprecation`, `g-simplify-results` |
| FAQ and Q and A content | Use visible helpful content; reserve QAPage for genuine single-question pages | Current Search Central guidance | FAQPage is not a current Google FAQ rich-result tactic | `g-update-2026-05-07-faq-rich-results-retired`, `g-search-gallery` |
| Product or merchant listing mentions | Use only when the page has genuine product context | Product and merchant-listing docs | Generic blog posts should not get commerce markup | `g-merchant-listing-sd`, `g-search-docs-updates-2026-07-07-product-structured-data` |
| Product sale-duration request | Validate sale dates only when the page contains a real offer | Merchant-listing documentation | Do not add commerce facts missing from the article | `g-merchant-listing-sd`, `g-search-docs-updates-2026-07-07-product-structured-data` |
| VideoObject blog embed | Confirm the video is visible and has stable metadata | Video rich-result guidance and Schema.org vocabulary | Embedded media alone is not enough for every video field | `g-video`, `schema-full` |

## Required Properties, Validation Target, And Warning

Every schema recommendation must name the page situation, visible evidence on the page, supported Google feature when relevant, validation target, and rollback trigger. If a page has no visible entity, product, author, breadcrumb, video, or article evidence, the recommendation should be "no markup change" rather than invented JSON-LD.

## Schema Deprecation Watch Publishing Boundary

This note can block or revise a schema recommendation. It cannot deploy markup, mutate a CMS, or guarantee rich results. A publication handoff should say which structured data is eligible to test, which source IDs justify the recommendation, and which unsupported tactics were rejected.

## Schema Request Worked Example

An editor asks for FAQPage markup because a post ends with five reader questions.
This watch cites `g-update-2026-05-07-faq-rich-results-retired`.
It checks `g-search-gallery` before treating any type as Google-supported.
The result is visible Q and A content without a current FAQ rich-result promise.
If the same article mentions sale prices, `g-merchant-listing-sd` must prove product context.
The consumer is [[Schema Generation Output Contract]].
Inputs handed over are requested type, visible-page evidence, source IDs, and warning text.
The contract should output JSON-LD, validation notes, blocked requests, or no schema change.

## Schema Deprecation Failure Modes

- Schema.org existence from `schema-full` does not equal Google rich-result support.
- Product.category guidance in `g-search-docs-updates-2026-07-07-product-structured-data` belongs to product contexts, not generic thought leadership.
- FAQPage markup should not be sold as an AI citation tactic without Google source support.
- Retired feature checks need both the deprecation source and the current gallery route.

## Related

- [[Blog Schema Stack]]
- [[Google Algorithm Update Ledger]]
- [[Monthly Source Refresh]]
- [[Confirmed Update Entry Template]]
