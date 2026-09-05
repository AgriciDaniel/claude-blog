---
type: spoke
title: "Media Repurposing Matrix"
domain: "Blog Media"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [media, images, audio, charts, active]
---

# Media Repurposing Matrix

## Media Repurposing Matrix Comparison Job

Media Repurposing Matrix maps one approved blog asset into social, email, slide, chart, audio, and video variants without widening the original claim. It answers: what can be reused, what must be shortened, what caveat must survive, where the canonical link points, and who signs off before distribution.

This matrix uses `g-google-images` for image handling, `g-video` for video variants, `g-intro-sd` for structured-data visibility boundaries, and `g-update-2026-06-30-merchant-center-product-videos-serving-eligible` only when product-video material enters a merchant context. Distribution strategy itself belongs to [[Distribution and Repurposing]].

### Rows This Matrix Must Contain

- Source article asset.
- Destination channel.
- Carried claim.
- Required caveat.
- Format constraints.
- Canonical link.
- Owner and approval state.

## Media Repurposing Matrix Matrix Table

| Destination | Asset variant | Claim allowed | Evidence cell | Confidence | Next action |
|---|---|---|---|---|---|
| Social post | Cropped image or carousel | Only the article's visible claim | Source note plus `g-google-images` when image handling matters | Same as source article | Add canonical URL and caption caveat. |
| Email | Inline image or chart thumbnail | Summary claim with source date | Chart packet or image approval note | Same or lower | Link to article for full context. |
| Short video | Scripted clip or animated chart | No new statistic or product promise | `g-video` and transcript comparison | Same or lower | Run [[Audio Summary Rules]] if narrated. |
| Slide deck | Figure, quote card, or diagram | Educational point, not unsupported forecast | Source ID and article section | Same or lower | Keep method note on speaker notes. |
| Product media | Product image or video | Product-specific only when page supports it | Merchant product-video source if in scope | Requires product owner | Confirm product context before reuse. |
| Podcast teaser | Spoken recap from approved article | No new forecast, endorsement, or guarantee | Article claim map plus `g-helpful-content` | Same or lower | Send script through [[Audio Summary Rules]]. |
| Community thread | Screenshot, chart crop, or question prompt | Discussion question preserves uncertainty | Source note and canonical section link | Same or lower | Label open questions plainly. |
| AI answer snippet candidate | Short answer block from article | Entity and source stay visible | [[AI Citation Mechanics]] plus source IDs | Same or lower | Keep no-inclusion guarantee in review notes. |

## Media Repurposing Matrix Interpretation Rules

1. A variant may narrow a claim but must not broaden it.
2. Confidence never increases during repurposing.
3. Removed caveats must be replaced with a link and visible short caveat.
4. Product-video eligibility is not a generic video recommendation.
5. Structured data belongs on the canonical page, not on a detached social asset.

## Media Repurposing Matrix Boundary Notes

If the source article changes, all derived assets become stale until checked. If a chart is converted into a thumbnail, the visible units and source date still matter. If a video turns into a transcript or audio cut, route the script through [[Audio Summary Rules]] before distribution.

## Carousel Compression Example

A report chart becomes a three-slide social carousel.
Before review, slide one drops the AS-REPORTED label.
That widens the claim beyond the source article's confidence.
The fixed slide restores the caveat and links the canonical section.
The crop keeps the unit and source date visible.
The caption points broad AI-search context to [[AI Citation Mechanics]].
`g-google-images` supports image context; `g-helpful-content` supports claim fidelity.

## Repurposing Breakpoints

- A crop that removes the denominator blocks the chart variant.
- A short video script cannot add urgency absent from the article.
- Product-media rows need product context before merchant sources apply.
- Community prompts must not phrase contested claims as settled facts.
- Confidence drops when a caveat cannot fit the destination format.

## Distribution Matrix Wire

[[Repurposing Asset Matrix]] consumes this media-level matrix.
Inputs are source asset, carried claim, caveat, channel, and canonical link.
Expected output is approved, revised, or blocked variant rows.
`g-update-2026-06-30-merchant-center-product-videos-serving-eligible` stays product-scoped.

## Media Repurposing Matrix Source IDs

The wired source IDs are `g-google-images`, `g-video`, `g-intro-sd`, `g-helpful-content`, and `g-update-2026-06-30-merchant-center-product-videos-serving-eligible`. The matrix does not cite social-platform policy or email deliverability rules.
