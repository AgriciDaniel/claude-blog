---
type: spoke
title: "AI Citation Readiness Subscore"
domain: "Blog Quality"
status: active
created: 2026-07-06
updated: 2026-07-23
tags: [quality, scorecard, active]
confidence: advisory
related:
  - "[[Blog Quality Score]]"
  - "[[Quality Score Rubric]]"
  - "[[AI Citation Mechanics]]"
  - "[[2026 Google Update Timeline]]"
---

# AI Citation Readiness Subscore

## AI Citation Readiness Scoring Job

This spoke applies an internal AI citation readiness heuristic to whether a blog
draft has passages that a reviewer can extract, verify, and safely reuse in
AI-adjacent answer contexts. It is a 15 point editorial subscore inside [[Blog
Quality Score]], not a calibrated probability or prediction engine for AI
Overview, AI Mode, or chatbot inclusion. Cite `g-ai-features` for Google AI
feature surface boundaries, `g-ai-opt-guide` for the no-special-file rule,
`ziptie-aio-source-selection` for practitioner passage-shape heuristics, and
`seer-aio-impact-ctr-2026` only as AS-REPORTED citation-click context.

## Answer Passage Criteria This Score Owns

- A short answer passage can stand alone without losing the entity, date, or claim scope.
- Nearby citations support the exact sentence they are attached to.
- Preview controls, snippets, and indexing choices do not accidentally hide the answer.
- AI-specific claims are framed as advisory unless Google documentation says otherwise.

## Criteria Delegated To Sibling Scores

Content depth belongs to [[Content Quality Subscore]]. Search intent fit belongs to [[SEO Intent Subscore]]. Author trust belongs to [[E-E-A-T Trust Subscore]]. Schema validation belongs to [[Technical Schema Subscore]]. This score only asks whether the best passages are quotable, source-near, caveated, and not built on unsupported AI-search folklore.

## Citation Readiness Evidence Matrix

| Criterion | Points | Required evidence | Blocking failure |
|---|---:|---|---|
| Answer block fit | 4 | A direct answer paragraph names the topic, condition, date, and outcome. | The passage is vague or depends on surrounding paragraphs. |
| Entity and claim clarity | 3 | Named entities, product names, and dates are explicit. | A reader cannot tell who or what the claim describes. |
| Source proximity | 3 | Source IDs sit near the claims they support. | Citations are dumped at the end or mismatched to claims. |
| Google AI guidance compliance | 3 | The note rejects required `llms.txt`, AI-only schema, or Markdown conversion claims using `g-ai-opt-guide` and `g-ai-features`. | A tactic is sold as a Google requirement without official support. |
| Market caveat discipline | 2 | `seer-aio-impact-ctr-2026` is used only as directional AIO citation context, with [[AI Citation Mechanics]] linked. | The study is turned into a property traffic forecast. |

## Point Weights And Blockers

Award partial credit only when the evidence is visible in the draft or review file. A draft with strong writing can still fail this subscore if the citation path is weak, if AI inclusion is promised, or if an optimization claim treats a third-party benchmark as first-party data. Any special AI-file requirement for Google Search is a blocker because the assigned Google sources contradict that premise.

## AI Citation Readiness Review Procedure

1. Select the three passages most likely to be quoted or summarized.
2. Check each passage for entity, date, claim, and source proximity.
3. Mark every AI-search assertion as confirmed, advisory, or blocked.
4. Route zero-click or AI-surface assumptions to [[AI Citation Mechanics]].
5. Record the final 15 point score in [[Quality Review Evidence Log]] with owner and next review date.

## Passage Rewrite Case

Input passage: "AI files help Google pick this guide."
Review result: blocked under `g-ai-opt-guide`.
Replacement passage: "Google treats AI feature optimization as normal SEO."
Attach `g-ai-opt-guide` beside that replacement sentence.
Then cite `g-ai-features` near preview-control wording.
If the paragraph uses practitioner passage-shape advice,
label it advisory with `ziptie-aio-source-selection`.
Do not attach the Seer AIO study to this sentence.
That study belongs only in market context.
Route that context to [[AI Citation Mechanics]].

## Citation-Specific Pitfalls

- A clean answer block can still fail without entity names.
- A source list after the article is not proximity evidence.
- Snippet controls can weaken the passage despite strong wording.
- Practitioner extraction advice cannot become Google policy.
- Citation-click context is not a traffic forecast.

## Deliverable Wiring

[[GEO Citation Readiness Register]] consumes this score.
Inputs supplied: passage text, entity, date, claim, source ID.
Also supply preview-control caveat and confidence label.
Expected output: register status, owner, review date, rollback trigger.
[[Blog Analyzer Score Report]] uses the 15 point result.
It expects blocker, advisory, or pass language.
