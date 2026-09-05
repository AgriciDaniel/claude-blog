---
type: spoke
title: "VideoObject For Blog Posts"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [schema, blog-schema, evergreen]
domain: "Blog Structured Data"
confidence: verified
related:
  - "[[Blog Schema Stack]]"
  - "[[Images Audio and Charts]]"
  - "[[Article Schema Baseline]]"
source_urls:
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://schema.org/docs/full.html"
  - "https://www.w3.org/TR/json-ld11/"
---
# VideoObject For Blog Posts

## VideoObject Decision Job

VideoObject is an add-on for blog posts that visibly contain a meaningful video. It should not be added to every article template, to decorative embeds, or to a page that only links to a video elsewhere. [[Images Audio and Charts]] owns media quality and accessibility; this note owns the structured-data decision.

Use `g-intro-sd` to keep markup aligned with visible media, `schema-full` for VideoObject vocabulary, `w3c-jsonld` for graph syntax, and `g-search-gallery` before discussing a Google Search video appearance.

## VideoObject For Blog Posts Schema Table

| Video situation | Required property or proof | Validation target | Warning to record | Source id |
|---|---|---|---|---|
| Original embedded explainer | Video is visible, playable, and central to the article | Article body and player render in final HTML | Do not mark a hidden or lazy-failed player as a video | `g-intro-sd` |
| Hosted video with thumbnail | Name, description, thumbnail URL, upload date when available | VideoObject fields match visible media and asset metadata | Thumbnail and upload date should not be invented | `schema-full` |
| Third-party embed | Embed URL, visible player, and rights or platform context | JSON-LD links the article and video consistently | Platform embed changes can stale the graph | `w3c-jsonld` |
| Short decorative clip | Usually no VideoObject | Editorial value is incidental | Decorative motion should stay outside schema | `g-intro-sd` |
| Search feature claim | Current gallery confirms relevant support | Search Gallery reviewed on current source date | Eligibility language is not a guarantee of display | `g-search-gallery` |
| Transcript-only media reference | Usually no VideoObject unless the video is present | Reader can access actual video on the page | Transcript text is not a playable video | `g-video` |
| Product demo inside article | VideoObject review plus product role separation | Video facts and product facts reviewed separately | Product video can blur media and offer claims | `g-product-sd` |
| Webinar recording with gated player | Defer until final page renders player and thumbnail | Consent, login, or embed gate checked | Hidden video evidence should not ship | `g-intro-sd` |

## Qualification Procedure

1. Watch or inspect the video enough to confirm it supports the article's reader task.
2. Verify the player, thumbnail, transcript or caption availability, and publication metadata.
3. Connect the VideoObject to the article graph only after the media facts pass review.
4. Escalate rights, accessibility, and production gaps to [[Images Audio and Charts]].

## Video Review Example

An article about "CRM Data Cleanup" included a YouTube embed titled "How to deduplicate CRM contacts" and a visible transcript below the player. The video directly supported the article task, so it became a VideoObject candidate, source ID `g-video`.

The reviewer accepted name, description, thumbnail, and upload date only after matching them to the visible embed and asset metadata, source IDs `schema-full` and `g-video`.

A second autoplay background clip showed dashboard motion behind the hero. It was rejected because decorative motion is not a meaningful article video and should not be marked up as VideoObject, source ID `g-intro-sd`.

The output also warned that video Search appearance language needed a current gallery check and could not be promised from markup alone, source ID `g-search-gallery`.

## Cases To Reject

Reject VideoObject when the page has only a text link, a broken embed, a background animation, an unrelated product demo, or a video whose title and thumbnail do not match the article. Also reject it when the CMS would emit the same video node on every post.

## VideoObject Failure Points

- Lazy-loaded embeds can pass source review while failing final render, source ID `w3c-jsonld`.
- Thumbnail URLs should not be guessed from platform conventions, source ID `g-video`.
- Third-party videos can be removed or retitled after publication, source ID `w3c-jsonld`.
- Product demos need Product review before offer claims appear, source ID `g-product-sd`.
- Transcript blocks help readers but do not replace a visible player, source ID `g-video`.

## Video Handoff To Deliverables

[[Schema Generation Output Contract]] consumes this note only after media review identifies a qualifying video.

Inputs passed: video URL or embed, title, description, thumbnail, upload date if visible, transcript note, and rejection reasons.

Expected output: VideoObject JSON-LD, defer decision, or rejection warning with the missing media evidence named.

## VideoObject Publishing Boundary

The handoff should say VideoObject accepted, rejected, or deferred. Accepted handoffs list the visible video, fields used, validation result, and owner for future media changes.
