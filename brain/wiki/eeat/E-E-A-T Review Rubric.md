---
type: spoke
title: "E-E-A-T Review Rubric"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [eeat, evergreen]
domain: "Blog Trust"
confidence: verified
related:
  - "[[E-E-A-T for Blog Content]]"
  - "[[Author Bio Requirements]]"
  - "[[Experience Evidence Checklist]]"
  - "[[Source Quality Ladder]]"
  - "[[Editorial Transparency Checklist]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
  - "https://developers.google.com/search/docs/essentials/spam-policies"
  - "https://www.nngroup.com/articles/ten-usability-heuristics/"
---
# E-E-A-T Review Rubric

## E-E-A-T Review Rubric Scoring Job

This rubric turns E-E-A-T review into a scored editorial decision. It is used after a draft, refresh candidate, or content audit has a defined reader task. The score is not a Google ranking prediction. It is a practical way to decide whether the page can move forward, needs expert review, or should be rewritten. Source IDs `g-helpful-content` and `g-qrg-full` set the quality frame, `g-spam-policies` identifies abuse boundaries, and `nng-editorial-heuristics` supports clear review feedback.

### Criteria This Score Owns

The rubric owns page purpose, first-hand evidence, expertise fit, authority support, trust transparency, and AI or scaled-content risk. It also records blockers that override a numeric score.

### Criteria Routed To Sibling Scores

Do not score schema implementation, Core Web Vitals, AI citation likelihood, or traffic impact here. Send those to [[Blog Schema Stack]], [[Google Data Integrations]], [[AI Citation Mechanics]], or [[Blog Quality Score]] as appropriate.

## Rubric Evidence And Blocker Table

| Criterion | Points or severity | Required proof | Blocking failure | Source ids |
|---|---:|---|---|---|
| Clear useful purpose | 20 points | Reader task, article promise, and answer path are aligned | Page cannot say who it helps or why | g-helpful-content |
| Experience signal | 20 points | Examples, tests, observations, or operational notes are visible | Experience is claimed but not shown | g-qrg-full, nng-editorial-heuristics |
| Expertise and review fit | 20 points | Author or reviewer evidence matches the claim risk | Sensitive claim lacks qualified review | g-qrg-full |
| Source and authority support | 20 points | Claims map to strong, dated sources or reputation evidence | High-stakes claim rests on weak citation | g-helpful-content, g-qrg-full |
| Trust and transparency | 10 points | Byline, update context, limitations, and ownership are clear | Material limitation is hidden | g-qrg-full, nng-editorial-heuristics |
| Freshness and correction path | 10 points | Current source dates, update reason, and correction route are visible | Stale advice cannot be corrected by the reader | g-helpful-content, nng-editorial-heuristics |
| Scaled or low-value risk | Blocker | Draft shows original contribution and avoids mass-produced sameness | Mostly copied, paraphrased, or generic AI output | g-spam-policies, g-qrg-full |

## Point Weights, Required Proof, And Blockers

Treat any blocker as more important than the total. A page with a high score but missing expert review on a risky claim is not ready. A page below 70 should enter a rewrite queue. A page from 70 to 84 can proceed only with named fixes. A page at 85 or above can move forward if no blocker exists and all source IDs are current.

## E-E-A-T Rubric Review Procedure

1. Write the reader task in one sentence and confirm that the draft actually serves it.
2. Fill each row with page evidence, not intent from the content brief.
3. Link weak rows to the owning spoke: [[Author Bio Requirements]], [[Source Quality Ladder]], [[Experience Evidence Checklist]], or [[Editorial Transparency Checklist]].
4. Mark blocker rows before calculating the score.
5. Add a confidence label based on the weakest source required for the recommendation.
6. Attach the rubric result to the audit or rewrite plan without promising search outcomes.

## Scoring Walkthrough For A Trust Gap

A B2B security checklist answers the reader task and cites vendor docs, but the author bio is generic and the article gives configuration advice without reviewer scope. Score purpose at 18, experience at 14, expertise at 8, source support at 16, transparency at 7, and freshness at 8. The total is 71, yet the expert-review blocker controls the handoff because sensitive technical instructions need a qualified review record under `g-qrg-full`. After the reviewer narrows two risky steps and adds limitations, the rubric can move from "fix" to "pass with named caveats" without implying ranking improvement (source_ids: g-qrg-full, g-helpful-content).

## Rubric-Specific Failure Modes

- A page reaches 85 numerically while one paragraph still contains consequential unreviewed advice; blocker status overrides the score (source_id: g-qrg-full).
- The source is official but answers a different question than the draft claim; lower source-support points and reopen [[Source Quality Ladder]] (source_id: g-helpful-content).
- Experience evidence appears only in an internal audit note, not near the claim readers evaluate; reduce the experience row (source_ids: g-qrg-full, nng-editorial-heuristics).
- A score is reused across a major rewrite without rechecking source dates; rerun the freshness row before attaching the report (source_id: g-helpful-content).
- A trust score is averaged across several URLs; score each page because purpose and author evidence can differ (source_id: g-qrg-full).

## Analyzer Trust Subscore Wiring

[[Blog Analyzer Score Report]] consumes the rubric as the trust subscore source. Inputs provided are row scores, blocker flags, weakest source IDs, owner, and confidence. The report expects severity labels, a trust-subscore explanation, and fix cards that cite `g-helpful-content`, `g-qrg-full`, or `g-spam-policies` according to the failing row.
