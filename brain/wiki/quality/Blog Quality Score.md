---
type: hub
title: "Blog Quality Score"
domain: "Blog Quality"
status: active
created: 2026-07-06
updated: 2026-07-10
tags: [quality, scorecard, active]
confidence: verified
related:
  - "[[index|Index]]"
  - "[[hot|Hot]]"
  - "[[Dual Optimization]]"
  - "[[E-E-A-T for Blog Content]]"
  - "[[AI Citation Mechanics]]"
  - "[[Blog Schema Stack]]"
---

# Blog Quality Score

## Blog Quality Score Operating Scope

[[Blog Quality Score]] is the hub that turns strategy, writing, trust, technical checks, and AI citation readiness into one auditable review. It owns the final gate, score total, and evidence posture. It does not replace the spoke notes that define how each score is earned. Use `g-helpful-content` for people-first content expectations, `g-qrg-full` for quality evaluation vocabulary, `wd-vitals` for current performance measurement language, and `g-ai-opt-guide` for the boundary around AI feature optimization.

## What This Hub Owns In Blog Quality Scoring

- The five-category 100 point score model.
- Category weights: Content 30, SEO 25, E-E-A-T 15, Technical 15, AI Citation 15.
- Final status labels: ready, revise, blocked, or monitor.
- Evidence freshness checks before a recommendation is shipped.
- The rule that a blocker overrides the point total.
- Cross-links to the spoke that must fix each weak score.

## What The Hub Must Not Absorb

This hub must not become the page-level evidence log, schema validator, content rewrite checklist, or AI citation tactics library. It also must not state ranking, traffic, Discover, AI Overview, AI Mode, or assistant-citation guarantees. If a score depends on property data, the hub records whether that data exists and links to [[Google Data Integrations]] rather than inventing a benchmark.

## Blog Quality Score Spoke Map

| Spoke | Points or gate role | Deliverable boundary | Blocking checks |
|---|---:|---|---|
| [[Content Quality Subscore]] | 30 | Reader usefulness, originality, completeness, and source-backed clarity. | Thin content, filler, or unsourced current claims. |
| [[SEO Intent Subscore]] | 25 | Query fit, title promise, metadata, and internal-link logic. | Intent mismatch or misleading SERP promise. |
| [[E-E-A-T Trust Subscore]] | 15 | Experience, expertise, transparency, source quality, and YMYL risk. | Anonymous sensitive advice or weak sources. |
| [[Technical Schema Subscore]] | 15 | Indexability evidence, structured data fit, performance source trail, and media hygiene. | Deprecated schema promises or validation gaps. |
| [[AI Citation Readiness Subscore]] | 15 | Answer-first passages, entity clarity, source proximity, and AI guidance caveats. | Unsupported AI inclusion or special-file requirements. |
| [[Delivery Contract Gate]] | Gate | Five delivery gates, retry loop, and strict-mode handoff. | Any failed delivery gate under strict mode. |

## Spoke Jobs And Deliverable Boundaries

The hub records scores after each spoke has produced evidence. It should not repeat every row from the subscore tables. The review packet should include a one-line reason for each score, the lowest confidence label from [[Recommendation Confidence Labels]], and any rollback note from [[Rollback Note Patterns]]. When the QRG is used, describe it as an evaluation framework, not as proof of a direct ranking factor.

## Evidence And Refresh Rules

1. Attach source IDs before scoring any current Search, trust, AI, or performance claim.
2. Treat old or missing evidence as a score reducer until [[Quality Review Evidence Log]] is updated.
3. Refresh living Google and web.dev sources by their ledger due dates.
4. Mark a score blocked when a recommendation lacks owner, source, confidence, or rollback path.

## Score Assembly Example

A draft about AI-friendly blog structure scores strongly on usefulness.
The content row cites `g-helpful-content`.
The trust row cites `g-qrg-full`.
Technical evidence is unavailable, so the technical score is reduced.
The AI section claims "llms.txt is required."
That claim is blocked by `g-ai-opt-guide`.
Final decision: blocked despite an 82 raw total.
The blocker travels to [[Delivery Contract Gate]].
The owner fixes the claim before layout work.

## Hub-Level Misreads

- Averaging away an AI blocker hides source conflict.
- QRG language cannot become a ranking-factor formula.
- Missing field data is not the same as passing CWV.
- A strong score does not approve CMS mutation.
- Market context cannot replace property evidence.

## Report Wiring

[[Blog Analyzer Score Report]] consumes the assembled score.
It receives five subscores, total score, blocker override, and lowest confidence.
It returns release decision, weakest category, evidence rows, and action list.
[[Full Site Blog Audit Report]] consumes sampled page scores.
It expects category totals plus page-level recommendation status.
When property data is absent, cite [[Google Data Integrations]].
Use `wd-vitals` only for performance terminology.
Use `g-helpful-content` for reader-value deductions.
