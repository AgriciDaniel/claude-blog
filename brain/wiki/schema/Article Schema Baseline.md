---
type: spoke
title: "Article Schema Baseline"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [schema, blog-schema, evergreen]
domain: "Blog Structured Data"
confidence: verified
related:
  - "[[Blog Schema Stack]]"
  - "[[BlogPosting Versus Article]]"
  - "[[Author Person Markup]]"
  - "[[Organization Entity Graph]]"
  - "[[BreadcrumbList For Blogs]]"
  - "[[Schema Validation Workflow]]"
source_urls:
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://schema.org/docs/full.html"
  - "https://www.w3.org/TR/json-ld11/"
---
# Article Schema Baseline

## Baseline Job For Blog Articles

This note defines the smallest useful article node for a normal blog post. The job is not to make every possible Schema.org assertion. It is to make the article, author, publisher, dates, image, and breadcrumb trail legible to machines while matching what a reader can inspect on the page. [[Blog Schema Stack]] owns the overall stack; this note owns the article-level minimum.

Use JSON-LD as the default serialization unless a platform has a documented reason to use another supported format. That preference is grounded in Google's structured-data guidance, source ID `g-intro-sd`, and the JSON-LD syntax baseline is the W3C recommendation, source ID `w3c-jsonld`. Treat Schema.org as the vocabulary reference, source ID `schema-full`, and Google Search Gallery as the Search feature support check, source ID `g-search-gallery`.

## Article Schema Baseline Schema Table

| Schema item | Required or baseline property | Validation target | Warning to record | Source id |
|---|---|---|---|---|
| `Article` or `BlogPosting` | `headline`, `datePublished`, `dateModified` when visible, author, publisher, image when available | Google Rich Results Test plus rendered page comparison | Do not mark dates or titles that differ from the visible article | `g-intro-sd` |
| `Person` author reference | Stable author name and author URL when the site has one | Same `@id` used by the article and author profile | Pseudonyms, ghostwriting, and reviewed-by claims need editorial evidence | `schema-full` |
| `Organization` publisher reference | Brand name, URL, and logo when part of the site identity | Consistent publisher node across templates | Do not swap publisher with sponsor, advertiser, or product brand | `schema-full` |
| `BreadcrumbList` link | Ordered article location in the site hierarchy | Breadcrumb markup matches visible navigation | Category changes can stale the schema before the body changes | `g-search-gallery` |
| JSON-LD graph container | Valid `@context`, `@type`, and stable `@id` values | JSON parser and Rich Results Test syntax pass | A syntactic pass does not prove Search feature eligibility | `w3c-jsonld` |
| `mainEntityOfPage` or canonical page link | Canonical article URL already approved for indexing | Article node identifies the public page, not a preview route | Preview URLs should not become permanent graph IDs | `w3c-jsonld` |
| Primary image reference | Visible hero or article image with stable asset URL | Image belongs to the article and can be fetched | Decorative social thumbnails are weak baseline evidence | `g-intro-sd` |

## Fields That Must Match Visible Content

Check the rendered page before approving the node. The headline should match the article title, not a campaign headline from metadata. The author must be the displayed author or credited organization. Dates should reflect the public published and modified dates, not build time. Image references should point to stable crawlable assets that represent the article. If a field is true internally but absent to readers, leave it out or route it to editorial review.

## Baseline Repair Example

Draft page: `/blog/crm-migration-checklist` rendered one H1, "CRM Migration Checklist for RevOps Teams," but the JSON-LD headline still said "The Ultimate CRM Move." The approved fix keeps the rendered H1 in `headline` because page-visible alignment is the controlling check, source ID `g-intro-sd`.

Before review, `dateModified` used the static-site build time. After review, the field was removed until the page displayed an editorial "Updated" date, because hidden dates create markup that readers cannot verify, source ID `g-intro-sd`.

The byline displayed "Maya Rao" and linked to `/authors/maya-rao`. The Article node reused that author reference and left reviewer data out because no reviewer appeared on the page, source IDs `schema-full` and `g-intro-sd`.

The final baseline output was Article type, visible headline, published date, author, publisher, canonical URL, breadcrumb link, and one stable hero image. Product and VideoObject were rejected as separate add-ons because the article only mentioned tools in prose, source ID `g-intro-sd`.

## Exclusions From The Baseline

Do not add Product, VideoObject, FAQPage, HowTo, Review, Course, or dataset markup just because the article mentions those concepts. Extra types belong in their own review notes and need visible qualifying content. A Schema.org type can be valid vocabulary while still lacking a current Google Search appearance, so Search feature promises must go through `g-search-gallery` and not through vocabulary breadth alone.

## Baseline Edge Cases

- Organization-authored articles are acceptable only when the visible byline supports that identity, source ID `g-intro-sd`.
- A CSS background hero should not become the baseline image unless it is a real article asset, source ID `g-intro-sd`.
- Syndicated posts need author, publisher, and canonical notes kept distinct, source IDs `schema-full` and `g-intro-sd`.
- Optional rich-result warnings should not expand the baseline without page evidence, source ID `g-search-gallery`.
- Locale variants should keep stable local URLs while preserving one publisher graph, source ID `w3c-jsonld`.

## Contract Feed: Article Node

[[Schema Generation Output Contract]] consumes this note for the Article or BlogPosting object.

Inputs provided: accepted page type, visible headline, author, publisher, dates, canonical URL, breadcrumb, image decision, and rejected add-ons.

Expected output: JSON-LD rationale, Article node fields, validation notes, and warnings for absent or hidden facts.

## Article Baseline Publishing Boundary

The output is an advisory checklist or JSON-LD review comment. It may identify missing fields, stale IDs, or invalid references, but it does not publish to a CMS. Escalate author identity to [[Author Person Markup]], publisher graph conflicts to [[Organization Entity Graph]], type choice to [[BlogPosting Versus Article]], and validation evidence to [[Schema Validation Workflow]].
