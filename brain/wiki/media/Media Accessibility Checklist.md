---
type: spoke
title: "Media Accessibility Checklist"
domain: "Blog Media"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [media, images, audio, charts, active]
---

# Media Accessibility Checklist

## Media Accessibility Checklist Review Scope

Media Accessibility Checklist verifies that a reader can understand the media without relying on a single sensory path. It covers alt text, decorative-image handling, chart labels, text alternatives, captions, transcripts, thumbnail clarity, and schema-visible descriptions. It is an editorial gate, not a legal compliance certification.

`g-google-images` provides the image-search and alt-text basis. `g-video` supports video-page and thumbnail alignment. `g-ai-opt-guide` keeps accessibility text visible and useful instead of hidden for AI extraction. `schema-full` supplies vocabulary context when media descriptions appear in structured data, with [[Blog Schema Stack]] deciding Search-supported usage.

### Checks Unique To This Gate

- Decorative images have empty alt and no lost meaning.
- Informational images have alt text that states the useful information.
- Charts expose labels, units, source date, and a text takeaway.
- Audio summaries have transcript or article-equivalent text nearby.
- Videos have caption, transcript, or summary handling appropriate to the asset.
- Structured data descriptions match visible page content.

## Media Accessibility Checklist Pass Fail Table

| Evidence | Severity | Owner | Pass condition | Fix status |
|---|---|---|---|---|
| Image alt packet | Blocker for informational images | Media editor | Alt text communicates the asset job | Rewrite before QA. |
| Decorative asset note | Advisory unless noisy alt harms comprehension | Designer | Empty alt or equivalent decorative handling | Confirm during layout review. |
| Chart text summary | Blocker for charts | Data reviewer | Units, date range, source, and takeaway are readable | Route to [[Chart Source Requirements]]. |
| Video support text | Blocker when video carries the main answer | Video owner | Captions, transcript, or summary align with player | Check [[VideoObject Checklist]]. |
| Schema description | Blocker when markup is present | Technical SEO | Description matches visible content | Review in [[Blog Schema Stack]]. |
| Audio transcript note | Blocker for standalone narration | Producer | Transcript or article-equivalent text is linked | Repair through [[Audio Summary Rules]]. |
| Interactive chart fallback | Blocker when controls hide values | Developer | Static table or summary preserves the decision | Add fallback before publish. |
| Thumbnail text review | Advisory unless thumbnail carries a claim | Video owner | Text is readable and repeated in page copy | Update thumbnail or caption. |

## Media Accessibility Checklist Handoff Rules

1. Inventory every media asset before final article QA.
2. Assign each asset one accessibility path: alt, empty alt, caption, transcript, table, or visible summary.
3. Verify that chart and video claims remain understandable when the media cannot load.
4. Send schema mismatches to [[Blog Schema Stack]] before the post is marked ready.
5. Keep unresolved accessibility gaps in [[Media QA For Blog Posts]] with owner and severity.

## Media Accessibility Checklist Limits

This note does not certify WCAG conformance, jurisdiction-specific legal status, or assistive-technology coverage. It is the blog brain's internal pass/fail gate for usable media. Bring legal or platform accessibility sources into [[Research Pack Index]] before making stronger claims.

## Chart Fallback Example

An article uses a color-coded funnel chart to explain lead loss.
Before review, red and green segments carry the entire conclusion.
`g-google-images` supports useful image context but not hidden-only meaning.
The fix adds segment labels, source date, and a short text takeaway.
The data reviewer adds a fallback table below the chart.
If schema describes the graphic, `schema-full` stays aligned with visible text.

## Accessibility Edge Cases

- Empty alt fails when the image is the only process explanation.
- Captions fail when they summarize a different video cut.
- A transcript must follow the final audio, not the draft script.
- Schema descriptions cannot compensate for missing visible explanations.
- Tiny thumbnail text needs page-copy repetition when it carries a claim.

## SEO Checklist Wire

[[SEO Check Validation Checklist]] consumes the media accessibility result.
Inputs are asset inventory, alt status, transcript status, and chart fallback.
Expected output is pass, fix, or blocked for images and OG checks.
`g-video` supports video alignment; `g-ai-opt-guide` keeps text visible.

## Media Accessibility Checklist Source IDs

Use `g-google-images`, `g-video`, `g-ai-opt-guide`, and `schema-full` when applying this checklist. The source IDs support search and vocabulary boundaries, while the operating checklist supplies the editorial accessibility workflow.
