---
type: spoke
title: "Technical Schema Subscore"
domain: "Blog Quality"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [quality, scorecard, active]
confidence: advisory
related:
  - "[[Blog Quality Score]]"
  - "[[Blog Schema Stack]]"
  - "[[Google Data Integrations]]"
  - "[[Images Audio and Charts]]"
---

# Technical Schema Subscore

## Technical Schema Scoring Assignment

This 15 point spoke scores technical evidence that affects a blog quality review: indexability basics, structured data fit, mobile parity, media hygiene, and whether performance evidence is present. It does not define every schema property or Core Web Vitals threshold. When those details are needed, route to [[Blog Schema Stack]] or [[Google Data Integrations]]. The assigned sources keep this note bounded: `g-intro-sd` supports structured-data eligibility, `g-canonical` supports canonical evidence, `g-mobile-first` supports mobile parity, and `wd-vitals` supports performance evidence.

## Technical Signals Owned Here

- The page can be inspected for indexability, canonical target, and crawl blockers.
- Structured data describes visible content rather than hidden assertions.
- Mobile and desktop content do not diverge in ways that change the reader answer.
- Media, captions, and chart sources support rather than obscure claims.
- Performance evidence is present, absent, or explicitly out of scope.

## Handed-Off Checks

Detailed schema patterns belong in [[Blog Schema Stack]]. Image, audio, and chart standards belong in [[Images Audio and Charts]]. Property exports and inspection results belong in [[Google Data Integrations]]. This note records whether those proofs exist and whether missing proof should reduce the score.

## Technical Evidence Grid

| Technical criterion | Points | Required proof | Blocking failure |
|---|---:|---|---|
| Indexability trail | 3 | Canonical URL, robots status, and crawl caveat are recorded or marked unavailable. | Reviewer cannot tell whether the page can be indexed. |
| Structured data fit | 4 | Markup matches visible blog content and avoids deprecated rich-result promises. | Schema invents facts or promises unsupported Google features. |
| Mobile parity | 2 | Mobile view keeps the same core answer, links, and source context. | Mobile hides critical answer or source material. |
| Media hygiene | 3 | Images, charts, video, and captions have accessible context and source notes. | Media carries unsupported claims. |
| Performance evidence trail | 3 | Field, lab, or unavailable status is logged with owner. | Performance quality is guessed without evidence. |

## Weights, Proof, And Blockers

Technical points require reproducible evidence. A screenshot, validation result, crawl note, or first-party report can support a row; memory cannot. The score should not reward hidden markup, mismatched canonical hints, or unsupported structured-data promises because the assigned technical sources require visible, verifiable evidence.

## Technical Review Sequence

1. Collect indexability, schema, mobile, media, and performance evidence.
2. Mark unavailable evidence as a gap rather than a pass.
3. Score each row and identify blockers.
4. Route schema details to [[Blog Schema Stack]].
5. Send final technical score to [[Quality Score Rubric]].

## Technical Proof Example

A draft requests BlogPosting and FAQPage markup.
Visible Q and A content exists, but rich-result support is absent.
Use `g-intro-sd` for visible-content alignment.
Use `g-search-gallery` for supported Google features.
Decision: keep Article or BlogPosting.
Remove the rich-result promise.
Canonical proof is missing.
Mark indexability as a gap with `g-canonical`.
Mobile copy hides source notes.
Use `g-mobile-first` before awarding parity points.

## Technical Failure Cases

- Schema describes a hidden offer inside an article.
- Canonical target is assumed from the CMS slug.
- Mobile accordions drop source context.
- Lab performance is reported as field performance.
- Image captions make claims the article never sources.

## Validation Wiring

[[SEO Check Validation Checklist]] consumes this technical review.
Inputs supplied: canonical evidence, schema note, mobile parity, media list.
Expected output: pass, fix, or blocked validation row.
[[Schema Generation Output Contract]] consumes schema-specific gaps.
It expects visible fields, warnings, unsupported requests, handoff owner.
[[Google API Evidence Matrix]] consumes performance evidence state.
