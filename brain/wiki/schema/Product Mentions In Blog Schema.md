---
type: spoke
title: "Product Mentions In Blog Schema"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [schema, blog-schema, evergreen]
domain: "Blog Structured Data"
confidence: verified
related:
  - "[[Blog Schema Stack]]"
  - "[[Article Schema Baseline]]"
  - "[[Structured Data Deprecation Register]]"
source_urls:
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://schema.org/docs/full.html"
  - "https://www.w3.org/TR/json-ld11/"
---
# Product Mentions In Blog Schema

## Product Mention Decision

This note prevents casual product references from turning into Product structured data. A blog post may mention a tool, compare options, review a product, or embed an offer. Those situations carry different schema risk. [[Blog Schema Stack]] treats Product as an add-on only when the visible article provides product facts that justify it.

The note uses `schema-full` for Product vocabulary, `g-intro-sd` for the rule that markup must match page content, `g-search-gallery` for supported Search feature checks, and `w3c-jsonld` for graph serialization. It does not replace a dedicated ecommerce or merchant-listing review.

## Product Mentions In Blog Schema Schema Table

| Blog situation | Schema decision | Required properties or proof | Validation target | Warning | Source id |
|---|---|---|---|---|---|
| Passing mention of a product | Keep inside article prose, no Product node | Product name is only contextual | Article schema remains sufficient | Mentions are not offers, reviews, or product pages | `g-intro-sd` |
| Tool roundup with factual comparison | Consider Product or ItemList only after visible fields are complete | Names, URLs, prices or ratings only if shown and sourced | Vocabulary fit plus Search Gallery check | Thin affiliate tables should not invent product data | `schema-full` |
| First-party product announcement | Product node may be valid if the article visibly describes the product | Brand, name, description, image, offer only when present | Rendered page and graph connection | Publisher, product brand, and seller can be different entities | `schema-full` |
| Review-style blog post | Product markup needs review evidence and visible review context | Product identity, author, date, review content | Search feature language reviewed separately | Do not imply a rich result from vocabulary alone | `g-search-gallery` |
| Embedded buy box or offer | Route to ecommerce schema review before publishing | Offer details visible and current | JSON-LD graph plus page comparison | Stale prices or hidden offers create high risk | `w3c-jsonld` |
| Merchant-style sale mention | Require sale dates and price evidence before offer fields | Sale duration and visible price reviewed | Missing sale timing can misstate the offer | `g-merchant-listing-sd` |
| Category attribute requested | Use category only when the page shows a real product category | Product category text or approved category code | Category stuffing is not article context | `g-merchant-listing-sd` |
| Affiliate comparison without current data | Usually keep Article-only and cite products in prose | Visible comparison lacks maintained offer fields | Affiliate links do not equal Product eligibility | `g-product-sd` |

## Minimum Evidence Before Adding Product

1. Confirm the reader can see the product facts being marked up.
2. Separate article author, publisher, product brand, seller, and sponsor.
3. Check whether the current Google gallery supports the feature language being used.
4. Record why Article-only markup is insufficient for this page.

## Product Decision Example

Article reviewed: "Best CRM Migration Tools" listed five tools with short editorial notes and affiliate links. It did not show current prices, offer dates, stock status, or maintained product categories.

Decision: Article-only schema. The product names stayed in prose because the page did not provide enough visible product fields to support Product or offer markup, source IDs `g-intro-sd` and `g-product-sd`.

One first-party tool section did include a visible product name, image, and feature description. The reviewer marked it as a Product candidate but deferred offer fields until ecommerce review confirmed visible price and sale timing, source ID `g-merchant-listing-sd`.

The final warning said "Do not convert affiliate mentions into Product JSON-LD without visible, maintained product facts." That warning came from the split between article context and product structured-data requirements, source IDs `g-product-sd` and `g-intro-sd`.

## Product Boundaries For Blog Teams

Do not add Product markup because a post has an affiliate link. Do not mark a comparison table as Product data when the table lacks current attributes. Do not copy ecommerce fields into an informational article without visible backing. When a blog post is also a sales page, document the mixed purpose and require a stricter review.

## Product-Specific Failure Cases

- Prices copied from screenshots are not reliable offer fields, source ID `g-merchant-listing-sd`.
- A publisher can review a product without being the seller, source ID `schema-full`.
- Product category requests need actual category evidence, source ID `g-merchant-listing-sd`.
- Stale affiliate tables should fail Product review before JSON-LD syntax is checked, source ID `g-intro-sd`.
- A product feature image should not replace the publisher logo, source ID `g-intro-sd`.

## Product Output Route

[[Schema Generation Output Contract]] consumes this note only when a page asks for product-related graph objects.

Inputs passed forward: product decision, visible fields, offer evidence, seller or brand separation, and rejected fields.

Expected return: Article-only warning, Product candidate for ecommerce review, or Product JSON-LD blocked with the missing evidence named.

## Product Schema Handoff

The output is one of three decisions: Article-only, Product candidate needing ecommerce review, or Product rejected. Any rejected Product field should name the missing visible evidence so the editor can fix the content or drop the markup.
