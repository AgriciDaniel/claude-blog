---
type: spoke
title: "Alt Text Standards"
domain: "Blog Media"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [media, images, audio, charts, active]
---

# Alt Text Standards

## Alt Text Standards Asset Job

Alt Text Standards decides what the image contributes for readers before anyone writes the `alt` attribute. The note covers informational images, decorative separators, screenshots, charts, video thumbnails, and product visuals used inside blog posts. It belongs under [[Images Audio and Charts]] and hands schema questions to [[Blog Schema Stack]] when the visible asset needs ImageObject or VideoObject review.

Google Images guidance is the primary source for descriptive image treatment and image discovery context through `g-google-images`. Google Video guidance enters only when the image is a video thumbnail or preview frame through `g-video`. Schema.org vocabulary is source context for fields, not proof of Google rich-result support, through `schema-full`. Google AI guidance keeps the rule honest: alt text is not a hidden AI optimization file or keyword reservoir, and AI-specific claims route to [[AI Citation Mechanics]] with `g-ai-opt-guide`.

### Blog Asset Types Covered

- Informational diagrams: describe the relationship or process the image adds.
- Decorative dividers: leave empty alt text when no reader information is lost.
- Screenshots: name the interface, date context, and visible state.
- Charts: summarize the measured comparison and link to [[Chart Source Requirements]].
- Product visuals: describe the exact product state visible in the article.
- Video thumbnails: align thumbnail text with the visible embedded video.

## Alt Text Standards Decision Table

| Asset job | Required input | Source IDs | Evidence state | Owner | Next action |
|---|---|---|---|---|---|
| Explain a concept diagram | Section claim, diagram draft, caption | `g-google-images`, `schema-full` | CONFIRMED for descriptive image handling, vocabulary-only for schema | Media editor | Write alt as the diagram's takeaway, not the file name. |
| Mark a decorative spacer | Layout reason and surrounding text | `g-google-images` | CONFIRMED for image best-practice context | Designer | Use empty alt and keep meaning in text. |
| Document a UI screenshot | Product/version, capture date, visible state | `g-google-images`, `g-ai-opt-guide` | Evidence depends on the screenshot source | Editor | State what changed or what control is visible. |
| Summarize a chart | Dataset, date range, chart claim | `g-google-images`, `schema-full` | Needs chart-source proof before approval | Data reviewer | Link to [[Chart Source Requirements]] before final alt. |
| Label a video thumbnail | Embedded video URL, thumbnail, transcript note | `g-video`, `schema-full` | CONFIRMED for video-page alignment | Video reviewer | Match thumbnail, caption, and VideoObject fields. |
| Show product state | Version, date, owner, visible feature | `g-google-images`, `schema-full` | Needs product evidence before approval | Product owner | Describe the state shown, not the promised roadmap. |
| Fit an OG preview | Crop draft, article promise, visible text | `g-google-images`, `g-ai-opt-guide` | CONFIRMED for image context only | Designer | Keep preview text legible and non-promotional. |

## Alt Text Standards Review Procedure

1. Name the asset job in one verb: explain, identify, compare, prove, or decorate.
2. Check whether the same information already appears in nearby copy. If yes, keep alt concise.
3. For charts and screenshots, verify the source date before the visual carries a factual claim.
4. Remove search keywords that do not help a screen-reader user understand the asset.
5. Route schema-visible assets to [[Blog Schema Stack]] when markup will describe them.

## Checkout Screenshot Alt Pass

Before: the draft used "shopping cart SEO image" for a checkout article.
That phrase explains nothing about the visual job under `g-google-images`.
After: the editor chose a dated checkout screenshot with two shipping options.
The alt became "checkout screen showing express and economy shipping choices."
The caption recorded product version and capture date for the UI claim.
If privacy edits hide customer data, [[Generated Media Disclosure Notes]] owns provenance.
Schema review waits until the screenshot is visible on-page through `schema-full`.

## Alt-Specific Breakpoints

- Empty alt fails when a badge contains the only beta-status notice.
- A chart alt cannot state a trend before data provenance passes.
- Video thumbnail alt becomes stale after the underlying clip changes.
- Product screenshot alt must not mention features outside the visible frame.
- Keyword stuffing is removed even when marketing requests image-search terms.

## Alt Text Standards Source Boundaries

The source IDs for this note are `g-google-images`, `g-video`, `g-ai-opt-guide`, and `schema-full`. They do not validate the underlying chart data, screenshot truth, product claim, or legal right to use the image. Those checks belong to [[Visual Claim Review]], [[Chart Source Requirements]], and [[Generated Media Disclosure Notes]].

## Alt Text Standards Handoff

Pass the note when the asset job, alt text, caption need, source owner, and next reviewer are explicit. Block it when alt text is stuffed with promotional terms, when the asset is only decorative but has noisy alt, when a chart lacks data provenance, or when markup describes information not visible on the page.

## Deliverable Wire

[[Blog Image Brief And Disclosure Checklist]] consumes this note during image approval.
It takes asset job, alt instruction, caption need, and reviewer owner.
It expects a pass, fix, or blocked state for accessibility and schema fit.
`g-google-images` covers the image context; `schema-full` stays vocabulary-only.
