---
type: spoke
title: "Image Sitemap Notes"
domain: "Blog Media"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [media, images, audio, charts, active]
---

# Image Sitemap Notes

## Image Sitemap Notes Asset Job

Image Sitemap Notes records when media discovery needs sitemap support and how the image, video, or product-media asset connects back to its canonical blog URL. It is not a prompt to submit every decorative file. The note is useful when an article depends on original screenshots, proprietary charts, product photos, or media that is loaded through a template path that may not be obvious from static HTML.

`g-google-images` supports image sitemap and image discovery context. `g-video` covers video sitemap logic and visible video requirements. `g-intro-sd` keeps structured data attached to visible page content. `g-update-2026-06-30-merchant-center-product-videos-serving-eligible` applies only when product-video material is part of merchant-oriented content.

### Sitemap Candidates This Note Covers

- Original images central to the article's answer.
- Charts or diagrams with stable file URLs.
- Screenshots that prove a dated interface state.
- Video assets that need a video sitemap or VideoObject review.
- Product videos where merchant eligibility context is relevant.

## Image Sitemap Notes Media Table

| Asset | Sitemap reason | Canonical relationship | Accessibility check | Schema check | QA state |
|---|---|---|---|---|---|
| Original diagram | Helps discovery of a unique explanatory image | Image belongs to one canonical article | Alt and caption complete | Optional ImageObject review | Add if URL is stable. |
| Dated screenshot | Supports a process or evidence claim | Canonical page owns the interpretation | Alt includes visible state | Markup only if visible | Add after source review. |
| Chart image | Carries a sourced comparison | Canonical page hosts data explanation | Caption gives source date | Schema does not replace dataset citation | Add only after chart approval. |
| Embedded video | Discovery may need video metadata | Page contains visible playable video | Captions or transcript reviewed | [[VideoObject Checklist]] required | Consider video sitemap. |
| Product video | Product media may affect merchant context | Product page or product section is canonical | Thumbnail and description match | Product-video update applies only in scope | Route to product owner. |
| CDN transformed image | Original has resized derivatives | Canonical page owns the original file | Alt attached to canonical asset | Markup uses stable original URL | Include original, not every derivative. |
| Lazy-loaded screenshot | Important asset may be hidden from static scan | Article explains the screenshot | Alt and caption complete | Structured data only if visible | Test rendered HTML before adding. |
| OG-only preview | Social preview does not teach the article | Preview points back to canonical URL | Alt not relevant to page reading | No ImageObject unless visible | Exclude from image sitemap. |

## Image Sitemap Notes Review Procedure

1. Confirm the asset is useful enough to index or discover on its own.
2. Verify the canonical page where the asset is explained.
3. Check that the file URL is stable and not a private draft path.
4. Align alt text, caption, surrounding copy, and any structured data.
5. Defer sitemap submission when the asset is decorative, temporary, or rights-blocked.

## Image Sitemap Notes Boundary Rules

Do not use sitemap inclusion to fix weak content, missing captions, or inaccessible visuals. Do not use product-video source material for an ordinary blog image unless the page is actually product or merchant oriented. When the asset is a repurposed variant, [[Media Repurposing Matrix]] must preserve the canonical link target.

## Original Diagram Sitemap Call

A pillar article includes one proprietary workflow diagram and six UI icons.
Before review, the request adds every media URL to the sitemap.
The icons are decorative and do not merit discovery support under `g-google-images`.
The diagram stays because the article explains it and uses a stable URL.
The canonical page receives the caption, alt text, and source note.
Derivative CDN sizes are excluded to avoid duplicate asset rows.
If a related video appears, `g-video` moves it to the video review path.

## Sitemap-Specific Misfires

- Staging image URLs must not enter a production discovery list.
- A canonical mismatch can send image context to the wrong article.
- A product feed video cannot justify generic blog sitemap inclusion.
- Cropped thumbnails should not replace the original explanatory image.
- Rights-blocked files stay out even when technically reachable.

## SEO Validation Wire

[[SEO Check Validation Checklist]] consumes sitemap-ready media notes.
Inputs are canonical page, stable file URL, asset job, and accessibility state.
Expected output is pass, fix, or blocked for image handling.
`g-intro-sd` applies when structured data describes the same visible asset.

## Image Sitemap Notes Source IDs

This note cites `g-google-images`, `g-video`, `g-intro-sd`, and `g-update-2026-06-30-merchant-center-product-videos-serving-eligible`. Add no sitemap recommendation unless those IDs or a more specific source support the asset class.
