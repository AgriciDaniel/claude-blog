---
type: spoke
title: "Visual Claim Review"
domain: "Blog Media"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [media, images, audio, charts, active]
---

# Visual Claim Review

## Visual Claim Review Asset Job

Visual Claim Review checks every claim made by an image, chart, screenshot, thumbnail, or video frame against the same evidence discipline used for text. A visual can imply a ranking, product state, search result, interface behavior, before-after effect, or market comparison even when the caption is cautious. This note makes those implied claims explicit before publication.

The assigned media sources are `g-google-images`, `g-video`, `g-intro-sd`, and `g-update-2026-06-30-merchant-center-product-videos-serving-eligible`. This note also cites `g-helpful-content` because visual evidence must support people-first usefulness rather than decorative authority. Claim verdicts should follow [[Research Pack Index]] and the claim-ledger labels: CONFIRMED, AS-REPORTED, SINGLE-SOURCE, CONTESTED, or FOLKLORE.

### Blog Asset Types Covered

- Screenshot claims about a current interface state.
- Chart claims about trend, rank, share, or comparison.
- Product visuals that imply feature availability or merchant eligibility.
- Video thumbnails that show numbers, product states, or outcomes.
- Generated visuals that could be mistaken for evidence.

## Visual Claim Review Media Table

| Asset | Implied claim | Required source | Caption or alt action | Schema state | QA result |
|---|---|---|---|---|---|
| SERP screenshot | Query result looked this way at capture time | Query, locale, device, date, screenshot source | State capture context | No markup unless visible page content needs it | Pass with context |
| Chart | The comparison supports a conclusion | Dataset and method packet | Give source date and unit | Image vocabulary only after chart approval | Needs data review |
| Product video frame | Product media is eligible or accurate | Product source and merchant context | Keep product scope explicit | Product-video source applies only in scope | Product owner review |
| Generated visual | Illustration represents a concept, not proof | Tool and input provenance | Disclose illustrative status when material | Do not invent provenance fields | Editorial approval |
| Thumbnail number | Video supports the stated number | Transcript and source note | Align thumbnail and page copy | [[VideoObject Checklist]] if marked up | Video review |
| Before-after screenshot | Change occurred between two dated states | Original captures, dates, and method | State dates and avoid causal overreach | Markup only after visible context | Factcheck review |
| Annotated UI screenshot | Highlight points to a real interface element | Capture date and unedited original | Note annotation if material | Schema describes page content, not overlay alone | Editor review |
| Cropped comparison image | Crop preserves denominator and unit | Source image plus crop rationale | Caption names what was omitted | No markup for hidden evidence | Data review |

## Visual Claim Review Review Procedure

1. List every claim the asset states or strongly implies.
2. Attach a source ID, data packet, screenshot context, or source gap to each claim.
3. Assign a claim-ledger verdict before writing caption or alt text.
4. Remove, relabel, or replace visuals that cannot support their implied claim.
5. Recheck the visual when the article, source, product state, or video changes.

## Visual Claim Review Boundaries

Do not let a visual turn an AS-REPORTED study into a universal fact. Do not use product-video guidance outside product content. Do not add structured data that describes a claim hidden inside an image but absent from the page. Route chart design issues to [[Data Visualization Review]] after evidence passes.

## SERP Screenshot Verdict

A draft shows a search-result screenshot beside a "Google prefers us" caption.
Before approval, the file lacks query, locale, device, and capture date.
That asset cannot support a broad ranking claim under `g-helpful-content`.
The repaired caption says the screenshot shows one observed result instance.
It records query, locale, device, date, and screenshot owner.
The article routes broad AI visibility context to [[AI Citation Mechanics]].
`g-google-images` supports image context, not ranking proof.

## Visual Claim Breakpoints

- A cropped chart can hide a denominator while looking authoritative.
- A UI annotation can point at a feature not yet available.
- A generated "customer" scene cannot prove customer usage.
- A video frame with a number needs transcript or source support.
- Merchant product-video claims stay scoped to product content only.

## Image Brief Wire

[[Blog Image Brief And Disclosure Checklist]] consumes the visual-claim verdict.
Inputs are implied claim list, evidence packet, caption action, and owner.
Expected output is approve, relabel, replace, or block.
`g-intro-sd` applies when structured data would echo the visual claim.

## Visual Claim Review Source IDs

This note wires `g-google-images`, `g-video`, `g-intro-sd`, `g-update-2026-06-30-merchant-center-product-videos-serving-eligible`, and `g-helpful-content`. The added helpful-content source keeps the review focused on reader value and separates it from the sitemap and repurposing bundle.
