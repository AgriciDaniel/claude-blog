---
type: spoke
title: "JSON-LD Publishing Checklist"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [schema, blog-schema, evergreen]
domain: "Blog Structured Data"
confidence: verified
related:
  - "[[Blog Schema Stack]]"
  - "[[Schema Validation Workflow]]"
  - "[[Article Schema Baseline]]"
source_urls:
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://schema.org/docs/full.html"
  - "https://www.w3.org/TR/json-ld11/"
---
# JSON-LD Publishing Checklist

## Prepublish Gate Scope

This checklist catches JSON-LD issues after the schema decision is made and before a template, MDX file, or CMS block is handed off. It is narrower than [[Schema Validation Workflow]]: the workflow decides whether the structured data is correct; this gate decides whether the serialized JSON-LD can be published without obvious breakage.

Use `w3c-jsonld` for syntax and graph serialization expectations. Use `g-intro-sd` for Google's stated preference and visible-content guardrail. Use `schema-full` for vocabulary names and property fit. Use `g-search-gallery` when the checklist mentions a Google Search appearance.

## JSON-LD Publishing Checklist Pass Fail Table

| Check | Pass or fail state | Source evidence | Blocker severity | Fix owner |
|---|---|---|---|---|
| Script parses as JSON-LD | Pass only after final rendered HTML is parsed, not just source code | `w3c-jsonld` | Blocker | Template engineer |
| `@context`, `@type`, and `@id` are stable | Pass when IDs remain stable across preview and production URLs | `w3c-jsonld` | Blocker | Schema owner |
| Marked-up facts are visible | Pass when title, author, dates, image, and special entities match the rendered page | `g-intro-sd` | Blocker | Editor |
| Vocabulary properties are valid | Pass when properties belong to the selected Schema.org type or a valid inherited type | `schema-full` | Major | Schema reviewer |
| Google feature language is current | Pass when any rich-result note matches the current Search Gallery | `g-search-gallery` | Major | SEO lead |
| CMS output is not duplicated | Pass when only one authoritative graph is present for the page | `g-intro-sd` | Major | Platform owner |
| Preview IDs replaced | Pass when preview, staging, and production IDs are not mixed | `w3c-jsonld` | Blocker | Developer |
| Escaped characters survive render | Pass when quotes, slashes, and Unicode survive the final page render | `w3c-jsonld` | Major | Template engineer |
| Optional objects gated | Pass when Product, VideoObject, and Q and A blocks have note-specific approval | `g-intro-sd` | Major | Schema owner |
| Script source ownership clear | Pass when plugin, theme, or manual source is named | `g-intro-sd` | Minor to major | Platform owner |

## Inputs Required Before Review

The reviewer needs the final URL or preview HTML, the rendered article body, the CMS template source, canonical URL policy, author data, publisher node, and any media or product block that contributes structured data. Reviewing a disconnected snippet is allowed only for early drafting and should be labeled as provisional.

## Rendered-HTML Check Example

The source MDX snippet for a blog post parsed correctly, but the final page contained two JSON-LD scripts because an SEO plugin emitted a second Article node. The checklist failed "CMS output is not duplicated" because the published graph, not the source snippet, is the review target, source ID `g-intro-sd`.

The first script used `https://preview.example.com/post#article` as `@id`, while the canonical page used `https://example.com/blog/post`. The fix replaced preview identifiers before publishing, because graph identifiers should remain stable in the final document, source ID `w3c-jsonld`.

The second script included a Product node copied from a roundup template. It was removed until [[Product Mentions In Blog Schema]] confirmed visible product evidence, source ID `g-intro-sd`.

After the duplicate script was removed, the handoff still required Search feature wording to be checked separately from JSON-LD validity, source ID `g-search-gallery`.

## Serialization Failure Cases

- Hydration can replace the server-rendered script after validation, source ID `w3c-jsonld`.
- Minifiers can break JSON strings when templates concatenate fields, source ID `w3c-jsonld`.
- Plugins can emit parallel Article nodes with different authors, source ID `g-intro-sd`.
- Preview-only image URLs can make an otherwise valid graph unusable, source ID `g-intro-sd`.
- Schema.org vocabulary passes do not approve Google appearance claims, source ID `g-search-gallery`.
- CMS rich text editors can escape JSON-LD differently than templates, source ID `w3c-jsonld`.

## Checklist Contract Wiring

[[SEO Check Validation Checklist]] consumes this note as the structured-data prepublish gate.

Incoming review packet: final HTML, schema draft, canonical URL, rendered body, and plugin output.

Expected checklist result: pass, fix, or blocked status for structured data, with owner and retest trigger.

## JSON-LD Checklist Handoff Rules

If a blocker fails, stop the schema handoff and record the owner. If only advisory warnings remain, attach them to the publishing ticket with a review date. Do not use a JSON parser pass as proof of Google eligibility; the Search Gallery check is separate from JSON-LD validity.
