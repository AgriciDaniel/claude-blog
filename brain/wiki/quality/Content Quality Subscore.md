---
type: spoke
title: "Content Quality Subscore"
domain: "Blog Quality"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [quality, scorecard, active]
confidence: advisory
related:
  - "[[Blog Quality Score]]"
  - "[[Quality Score Rubric]]"
  - "[[SEO Intent Subscore]]"
  - "[[E-E-A-T Trust Subscore]]"
---

# Content Quality Subscore

## Content Quality Scoring Job

This 30 point spoke asks whether the article helps a real reader before it asks whether the page is optimized. Use `g-helpful-content` for people-first self-assessment, `g-qrg-full` for quality-review vocabulary, `g-spam-policies` when thin or scaled pages look like abuse risk, and `nng-editorial-heuristics` for editorial clarity checks.

## Reader Value Signals This Score Owns

- A reader job is named before the outline drifts into tactics.
- The article gives a direct answer, then explains limits and edge cases.
- Examples, data, screenshots, expert review, or original synthesis add information gain.
- Claims that depend on current Search or AI guidance carry source IDs.

## Signals Routed Out Of Scope

Ranking opportunity, title metadata, and internal link maps go to [[SEO Intent Subscore]]. Author proof and sensitive-topic escalation go to [[E-E-A-T Trust Subscore]]. Passage extractability goes to [[AI Citation Readiness Subscore]]. This score can penalize those gaps when they damage usefulness, but it does not own their remediation details.

## Content Quality Evidence Table

| Criterion | Points | Required proof | Blocking failure |
|---|---:|---|---|
| Reader job and answer | 8 | Intro states the practical question and gives a useful answer quickly. | No clear reader task or answer is delayed by filler. |
| Original information gain | 7 | Draft adds first-hand evidence, examples, comparison, or synthesis. | Mostly repeats common SERP definitions. |
| Completeness without padding | 6 | Necessary subquestions, caveats, and decision paths are covered. | Extra sections exist only to increase word count. |
| Source-backed clarity | 5 | Current claims have nearby source IDs and dates. | A current policy, AI, or market claim has no cited source. |
| Editorial structure | 4 | Headings, lists, and paragraphs make the review scannable. | The structure hides the recommendation or mixes facts with advice. |

## Point Logic And Blocking Cases

The content score cannot pass when the page is useful only to an optimizer and not to the reader. A high word count earns no credit by itself. A market study can justify context, but it cannot substitute for client data or source-backed claims. If the article repeats scaled, copied, or low-value patterns, mark the relevant row as zero even when the prose is polished.

## Content Review Steps

1. Write the reader job in one sentence.
2. Highlight unsupported current claims before assigning points.
3. Compare the draft against the five evidence rows.
4. Send source and trust gaps to their sibling spokes.
5. Log the score rationale in [[Quality Review Evidence Log]].

## Intro Repair Scenario

Before: "This post explains everything about GEO."
Reader job is missing.
No usable answer appears before the background.
After: "Use GEO checks to make claims inspectable."
The revision names the task and gives direction.
Attach `g-helpful-content` to the usefulness judgment.
If the draft repeats AI-output at scale,
check abuse risk with `g-spam-policies`.
If the paragraph still feels hard to scan,
use `nng-editorial-heuristics` for review language.
Do not add a filler FAQ to gain length.

## Content-Only Failure Patterns

- Definitions crowd out the reader's decision.
- Examples repeat SERP summaries without new synthesis.
- Caveats appear after recommendations, too late to help.
- Current AI guidance appears without ledger IDs.
- Polished prose masks copied or scaled structure.

## Writer Handoff

[[Blog Write Article Contract]] consumes this subscore first.
Inputs passed forward: reader job, answer gap, source gaps.
Also pass originality notes and padding warnings.
Expected output: answer-first intro and claim-backed body.
The contract should block unsupported current claims.
[[Blog Analyzer Score Report]] consumes the 30 point result.
It expects blocker, major, minor, or pass wording.
