---
type: spoke
title: "Quality Score Rubric"
domain: "Blog Quality"
status: active
created: 2026-07-06
updated: 2026-07-23
tags: [quality, scorecard, active]
confidence: advisory
related:
  - "[[Blog Quality Score]]"
  - "[[Content Quality Subscore]]"
  - "[[SEO Intent Subscore]]"
  - "[[E-E-A-T Trust Subscore]]"
  - "[[Technical Schema Subscore]]"
  - "[[AI Citation Readiness Subscore]]"
---

# Quality Score Rubric

## Quality Score Rubric Scoring Job

This note defines the 100 point model used by [[Blog Quality Score]]. It owns category weights, scoring thresholds, and automatic override rules. It does not own the detailed evidence collection for each category. The rubric uses `g-helpful-content` for usefulness, `g-qrg-full` for trust-risk vocabulary, `g-intro-sd` for schema-row boundaries, and `g-ai-features` for AI surface caveats.

## Criteria This Score Owns

The rubric owns the five category weights, the pass thresholds, and the rule that unresolved blockers beat the total score. The canonical split is Content 30, SEO 25, E-E-A-T 15, Technical 15, and AI Citation 15. It also owns the rule that a score must name the weakest confidence label used by any recommendation.

## Criteria Delegated To Other Scores

The subscore notes decide row-level proof. [[Content Quality Subscore]] owns usefulness detail, [[SEO Intent Subscore]] owns query fit, [[E-E-A-T Trust Subscore]] owns trust, [[Technical Schema Subscore]] owns validation evidence, and [[AI Citation Readiness Subscore]] owns passage-level citability.

## Quality Score Rubric Evidence Table

| Category | Points | Required evidence | Blocking failure |
|---|---:|---|---|
| Content quality | 30 | Reader job, useful answer, originality, completeness, and source-backed clarity. | Thin or generic content that does not satisfy the reader. |
| SEO intent | 25 | Query fit, title promise, metadata discipline, and internal link logic. | The page optimizes for an intent it does not answer. |
| E-E-A-T trust | 15 | Experience evidence, qualified review, source quality, and risk escalation. | Sensitive advice lacks credible authorship or review. |
| Technical schema | 15 | Indexability, validation, visible-content schema, media, and performance evidence trail. | Deprecated or fabricated structured-data promise. |
| AI citation readiness | 15 | Extractable passages, source proximity, entity clarity, and AI guidance caveats. | Guaranteed AI inclusion or required special AI-file claim. |

## Point Weights, Required Proof, And Blockers

The pre-commit `quality_gate.py` threshold is 70: scores from 70 to 100 pass
that repository check, while scores below 70 fail it. The rendered five-gate
delivery contract is stricter: only scores from 90 to 100 are delivery
candidates, and only when no blocker exists. Scores from 80 to 89 are strong
and scores from 70 to 79 are acceptable as editorial bands, but both require
revision before Gate 4 delivery. A single blocker from [[Quality Gate Failure
Modes]] overrides either threshold because the rubric is a decision aid, not a
way to average away risk.

## Quality Score Rubric Review Procedure

1. Score each category from its own spoke note.
2. Record the source ID behind every current claim.
3. Apply blocker overrides before assigning the final label.
4. Attach the lowest confidence label from the packet.
5. Send the final score to [[Delivery Contract Gate]].

## Threshold Application Case

Raw score: content 24, SEO 20, trust 13, technical 9, AI 12.
Total: 78.
The score passes the 70 pre-commit threshold but requires revision before the
90-point delivery gate.
However, schema promises a retired rich result.
Check the schema claim with `g-intro-sd`.
Check AI surface wording with `g-ai-features`.
Decision: blocked until the promise is removed.
The score remains useful for prioritizing fixes.
It cannot override the blocker.

## Rubric-Specific Failure Modes

- A low technical row is hidden inside a high total.
- The weakest confidence label is omitted from the summary.
- QRG framing becomes a numeric ranking guarantee.
- Field and lab performance evidence are blended.
- AI citation readiness is mistaken for a calibrated inclusion probability
  instead of being labeled an internal editorial heuristic.

## Score Report Wiring

[[Blog Analyzer Score Report]] consumes this rubric.
Inputs supplied: category scores, total, threshold, blocker override.
It expects a release decision and weakest-category explanation.
[[Full Site Blog Audit Report]] consumes the same model.
It expects sampled page scores plus inventory-level action priority.
Use `g-helpful-content` for content deductions.
Use `wd-vitals` for performance language only.
