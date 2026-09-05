---
type: spoke
title: "Data Visualization Review"
domain: "Blog Media"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [media, images, audio, charts, active]
---

# Data Visualization Review

## Data Visualization Review Asset Job

Data Visualization Review asks whether a chart lets the reader inspect the intended comparison without being nudged by scale tricks, missing labels, cropped windows, or overloaded design. [[Chart Source Requirements]] answers "can we prove the data?" This note answers "does the visual encode the data fairly?"

The media source set is intentionally narrow. `g-google-images` supports high-quality image handling and image context. `g-video` matters when the visualization appears inside a video or thumbnail. `g-intro-sd` keeps structured data tied to visible page content. `g-update-2026-06-30-merchant-center-product-videos-serving-eligible` is relevant only for product pages that use product video assets, not generic editorial charts.

### Review Cases This Note Covers

- A line chart where the chosen date window changes the conclusion.
- A bar chart where the baseline or ordering exaggerates differences.
- A comparison table converted into a visual summary.
- A video frame or thumbnail that contains a data claim.
- A product chart used in merchant-oriented content.

## Data Visualization Review Media Table

| Visual asset | Provenance requirement | Accessibility check | Placement rule | Review result |
|---|---|---|---|---|
| Trend line | Source table and full date window from [[Chart Source Requirements]] | Axis labels and text summary | Near the paragraph interpreting the trend | Pass only when window choice is explained. |
| Ranked bars | Sorting rule and sample size | Values readable without color alone | Before recommendations based on rank | Block if the order hides ties or uncertainty. |
| Comparison chart | Unit definition and denominator | Caption names units and source date | Next to the decision it supports | Revise when measures mix incompatible bases. |
| Video thumbnail with numbers | Video frame source and transcript alignment | Thumbnail text also appears in page copy | Only beside visible video | Use `g-video` before VideoObject review. |
| Product media chart | Product data source and product-page context | Labels readable on mobile | Product or merchant content only | Apply merchant video update source only when in scope. |
| Stacked share chart | Category definitions and total denominator | Pattern or label beyond color | Beside segmentation caveat | Block when the total changes silently. |
| Before-after annotation | Event source and unaffected comparison window | Annotation readable without hover | Near the causal language | Revise unless causality is stated cautiously. |
| Interactive chart export | Static fallback table and source packet | Keyboard-independent summary | After plain-language takeaway | Block if fallback loses key values. |

## Data Visualization Review Scale Audit

1. Identify the claim the chart is supposed to make.
2. Check whether another reasonable date range would weaken or reverse the story.
3. Test whether removing color, animation, or annotation still leaves the comparison understandable.
4. Confirm the caption states source, date range, unit, and caveat.
5. Send schema questions to [[Blog Schema Stack]] only after the visual is final and visible.

## Data Visualization Review Failure Triggers

Fail the asset when it uses cropped axes without disclosure, compares raw counts to percentages, hides sample size, repeats a chart from another article without checking freshness, or relies on a product-video rule outside product content. If the visual will become a channel variant, [[Media Repurposing Matrix]] must preserve the same caveat.

## Scale Repair Example

A bar chart shows conversion rate by landing-page template.
Before review, the y-axis starts at 93 percent and exaggerates small gaps.
The claim cites a source packet from [[Chart Source Requirements]].
The reviewer changes the view to a table plus a modest bar chart.
The caption states denominator, window, and metric name.
If the chart is exported as an image, `g-google-images` governs context.
If the chart appears in a video thumbnail, `g-video` governs alignment.

## Visualization-Specific Traps

- Color-only legends fail when exported to grayscale slide decks.
- Hover-only labels disappear in static newsletter screenshots.
- Product-video eligibility cannot justify a generic editorial chart.
- Axis breaks need a visible note beside the chart.
- Animated charts need a still frame that preserves the same caveat.

## Chart Deliverable Wire

[[Blog Chart Specification]] consumes this visual verdict after source approval.
Inputs are chart draft, source packet, caption, fallback plan, and placement.
Outputs are pass, revise, or block plus the exact repair instruction.
`g-intro-sd` applies only when structured data describes the visible chart.

## Data Visualization Review Source IDs

Use `g-google-images`, `g-video`, `g-intro-sd`, and `g-update-2026-06-30-merchant-center-product-videos-serving-eligible` for this note. These sources do not supply chart data; they govern image, video, structured-data, and product-video boundaries.
