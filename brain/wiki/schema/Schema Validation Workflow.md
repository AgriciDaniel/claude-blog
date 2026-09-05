---
type: spoke
title: "Schema Validation Workflow"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [schema, blog-schema, evergreen]
domain: "Blog Structured Data"
confidence: verified
related:
  - "[[Blog Schema Stack]]"
  - "[[JSON-LD Publishing Checklist]]"
  - "[[Article Schema Baseline]]"
source_urls:
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://schema.org/docs/full.html"
  - "https://www.w3.org/TR/json-ld11/"
---
# Schema Validation Workflow

## Validation Scope

This workflow validates four layers in order: syntax, vocabulary, Google support, and editorial alignment. A page can pass one layer and fail the next. The workflow exists so a schema reviewer does not mistake valid JSON-LD for a correct article graph or a supported Search feature.

The source route is fixed for this folder. `w3c-jsonld` covers serialization mechanics, `schema-full` covers vocabulary and type fit, `g-search-gallery` covers Google supported-feature checks, and `g-intro-sd` covers the relationship between markup and visible page content.

## Concrete Validation Procedure

1. Capture the final rendered HTML or the exact preview HTML that will publish.
2. Parse the JSON-LD and fix syntax or duplicate graph errors first.
3. Check each `@type` and property against Schema.org vocabulary.
4. Compare marked-up facts against the rendered page, including author, dates, image, video, product, and breadcrumb labels.
5. Check current Google Search Gallery support before any rich-result language is included.
6. Record pass, fail, owner, and rollback trigger in the publishing ticket or audit note.

## Schema Validation Workflow Pass Fail Table

| Gate | Pass or fail state | Source evidence | Blocker severity | Fix owner |
|---|---|---|---|---|
| JSON-LD parses | Pass when final HTML parses without JSON errors | `w3c-jsonld` | Blocker | Template engineer |
| Vocabulary fits type | Pass when every property belongs to the chosen type or inherited vocabulary | `schema-full` | Blocker | Schema reviewer |
| Page content matches | Pass when every material claim is visible or directly represented on the page | `g-intro-sd` | Blocker | Editor |
| Google feature support checked | Pass when feature wording matches the current gallery | `g-search-gallery` | Major | SEO lead |
| Entity graph connected | Pass when article, author, organization, and breadcrumbs use stable IDs | `w3c-jsonld` | Major | Schema owner |
| Warnings triaged | Pass when warnings are accepted, fixed, or escalated with an owner | `g-intro-sd` | Minor to major | Delivery owner |
| Post-render output captured | Pass when validation uses final HTML or exact preview output | `w3c-jsonld` | Blocker | Developer |
| Add-on types approved | Pass when Product, VideoObject, and Q and A decisions cite their spoke notes | `g-intro-sd` | Major | Schema reviewer |
| Retest trigger recorded | Pass when a later CMS or source change has an owner | `g-search-gallery` | Minor to major | Delivery owner |

## Evidence Packet

Attach the validated URL or HTML sample, testing tool output, selected source IDs, and manual page comparison notes. If the page is not public yet, label the result as preview validation and require a post-publish recheck.

## Validation Walkthrough

Scenario: a post about webinar software shipped valid JSON-LD with Article, Product, and VideoObject nodes. The parser passed, but the product price was hidden in a collapsed personalization block and the video iframe failed on mobile.

Layer one passed because the JSON-LD parsed in the rendered HTML, source ID `w3c-jsonld`.

Layer two passed for vocabulary names after the reviewer checked Product and VideoObject properties against Schema.org, source ID `schema-full`.

Layer three failed because the marked-up price and playable video were not reliably visible to readers, source ID `g-intro-sd`.

Layer four blocked Search feature language until the current gallery wording was checked separately, source ID `g-search-gallery`.

The final action was "Article schema passes, Product and VideoObject blocked, retest after template fix." That status gave the delivery owner a precise rollback and retest path.

## Validation Failure Patterns

- Valid JSON can still describe invisible page facts, source ID `g-intro-sd`.
- A single page may pass Article review while failing add-on objects, source ID `schema-full`.
- Rich-result wording needs a current gallery check after syntax passes, source ID `g-search-gallery`.
- Preview validation should be repeated after production rendering, source ID `w3c-jsonld`.
- CMS plugins can reintroduce removed nodes during later template updates, source ID `g-intro-sd`.

## Workflow Consumer

[[SEO Check Validation Checklist]] consumes this workflow for the structured-data row.

It receives: rendered HTML, selected schema objects, source IDs, validation output, and page-comparison notes.

It expects back: pass, fix, or blocked status, fix owner, blocker severity, rollback trigger, and retest date.

## Validation Handoff Rules

Block release on syntax errors, hidden marked-up facts, unsupported Search feature promises, and role conflicts. Allow handoff with documented minor warnings when they do not alter the visible claim, but set a review date.
