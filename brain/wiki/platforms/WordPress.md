---
type: platform
title: "WordPress"
domain: "Blog Publishing"
status: seed
created: 2026-07-08
updated: 2026-07-09
tags: [platforms, read-only, seed]
related:
  - "[[Blog Schema Stack]]"
  - "[[Images Audio and Charts]]"
  - "[[Credential Boundary Rules]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
  - "https://developers.google.com/search/docs/appearance/google-images"
  - "https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers"
---

# WordPress

## WordPress CMS Handoff Job

WordPress is treated here as a publishing surface that may receive blog copy, media fields, schema instructions, and crawler-policy requests from the brain. The vault does not log in to WordPress, edit theme files, install plugins, change `robots.txt`, or keep account credentials. Its job is to make the handoff precise enough that a CMS owner can implement it outside the vault and report back with evidence.

For content quality, this note routes back to Google's helpful-content guidance through `g-helpful-content`; for structured data it routes to `g-intro-sd` and [[Blog Schema Stack]]; for media fields it routes to `g-google-images` and [[Images Audio and Charts]]; for Google crawler control questions it records `g-common-crawlers` with the explicit caveat that Google-Extended is not a ranking lever.

### Inputs Specific To WordPress

- The target post type, permalink pattern, editor type, theme constraints, and reusable block rules.
- The field names for title, excerpt, canonical URL, author, dates, categories, tags, featured image, captions, alt text, and custom schema fields.
- The plugin or theme owner responsible for schema, image metadata, redirects, canonical tags, and crawler controls.
- The approval ticket for any requested robots or AI-training preference change. This vault may name the request, but the implementation belongs outside the vault.

### Decisions WordPress Must Record

- Whether the page will ship with Article or BlogPosting JSON-LD, and which visible page fields support that markup.
- Whether the image inventory has usable alt text, caption context, rights notes, and stable asset URLs.
- Whether any WordPress plugin output conflicts with the brain's schema recommendation.
- Whether crawler directives are informational, compliance-driven, or a product decision. They must not be framed as ranking work unless a dated source supports that claim.

## WordPress Platform Boundary Note Table

| WordPress decision | Required inputs | Source ids | Evidence state | Owner | Next action |
|---|---|---|---|---|---|
| Prepare the article handoff | Draft body, author context, update date, reader promise, review notes | `g-helpful-content` | CONFIRMED source for quality review, not a WordPress endorsement | Content lead | Map editorial fields before CMS entry. |
| Specify schema output | Visible page facts, chosen schema types, plugin or theme schema behavior | `g-intro-sd` | CONFIRMED general structured-data rules | Schema steward | Write a JSON-LD spec and validation note, then hand it to the CMS owner. |
| Prepare media upload requirements | Featured image, inline images, alt text, captions, rights notes, dimensions | `g-google-images` | CONFIRMED image guidance | Media editor | Add missing metadata before publication approval. |
| Record crawler or AI-training preference | Requested directive, business reason, approval trail, rollback owner | `g-common-crawlers` | CONFIRMED crawler reference with non-ranking caveat | Technical SEO | Open an external implementation ticket if a change is approved. |

## WordPress Evidence And Boundary Notes

The source IDs above are intentionally narrow. `g-helpful-content` supports people-first review questions, but it does not choose WordPress over another CMS. `g-intro-sd` supports the structured-data handoff, but it does not make a plugin safe by default. `g-google-images` supports image metadata and quality checks, not decorative image stuffing. `g-common-crawlers` can justify a crawler-control discussion, while [[AI Citation Mechanics]] should handle any broader AI visibility claim.

## WordPress Operating Procedure

1. Collect the WordPress-specific field map and identify the human CMS owner before drafting implementation advice.
2. Route copy quality, schema, media, and crawler decisions to the table above, attaching the relevant source ID to each recommendation.
3. Mark plugin-dependent behavior as unverified until the CMS owner supplies a screenshot, exported HTML, rendered JSON-LD, or validation result.
4. Keep credentials, API keys, session cookies, and admin URLs out of the vault. Use [[Credential Boundary Rules]] when access is required.
5. After publication, record only the external evidence needed for review, such as final URL, rendered source excerpt, schema validation result, or media metadata check.
