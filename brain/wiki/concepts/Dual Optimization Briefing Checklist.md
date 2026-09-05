---
type: spoke
title: "Dual Optimization Briefing Checklist"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [dual-optimization, evergreen]
domain: "Blog Content Optimization"
confidence: advisory
related:
  - "[[Dual Optimization]]"
  - "[[index|Index]]"
  - "[[hot|Hot]]"
  - "[[Search Visibility Versus Citation Exposure]]"
  - "[[Zero Click Planning Baseline]]"
  - "[[AI Overview CTR Interpretation]]"
  - "[[AI Mode Query Share Context]]"
  - "[[Citation Readiness Decision Tree]]"
  - "[[Reader Value Versus Extraction Value]]"
  - "[[Dual Optimization Risk Register]]"
  - "[[Classic SEO And GEO Tradeoffs]]"
  - "[[6-Pillar Dual Optimization]]"
source_urls:
  - "https://sparktoro.com/blog/in-2026-less-than-one-third-of-google-searches-still-send-a-click/"
  - "https://www.seerinteractive.com/insights/aio-impact-on-google-ctr-2026-update"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://developers.google.com/search/docs/appearance/ai-features"
  - "https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports"
---
# Dual Optimization Briefing Checklist

## Brief Gate Purpose

This checklist is the pre-draft gate for a dual-optimization brief. It confirms the reader job, search surface, evidence class, and measurement lane before a writer receives the assignment. Use [[AI Citation Mechanics]] for broad statistic context from `sparktoro-zero-click-2026` and `seer-aio-impact-ctr-2026` rather than repeating those figures here.

### Inputs The Gate Must See

- Reader task, target locale, page or cluster scope, and intended deliverable.
- Search surface label: classic Search, AIO, AI Mode, mixed, or unknown.
- Source posture using official, first-party, market, or practitioner labels.
- Metric path, including whether property exports exist under `g-gsc-api`.

## Briefing Gate Table

| Gate item | Evidence to inspect | Source IDs | Pass output | Blocker cue |
|---|---|---|---|---|
| Reader task | Problem, audience, and outcome | `g-helpful-content` | One sentence job statement | Topic is only keyword-led |
| Surface role | Classic Search, AIO, AI Mode, or mixed | `g-ai-features`, `blog-io2026` | Surface priority label | AI Mode chosen from news alone |
| Evidence class | Official, property, market, practitioner | `g-ai-opt-guide`, `sparktoro-zero-click-2026` | Confidence label | Market data written as site data |
| Metric lane | Visibility, clicks, citation, or assisted value | `g-gsc-api`, `g-genai-reports` | Measurement note | Metric unavailable but inferred |
| Passage need | Candidate answer block and source proximity | `g-ai-opt-guide`, `ziptie-aio-source-selection` | Draft instruction | Extractability harms flow |
| Refresh cue | Source date and next review event | `g-ranking-history`, `g-ai-features` | Review trigger | Fast-moving claim lacks date |

## Applied Brief Gate

A brief for "AI writing tools for HR policy teams" should not move to outline if it only says "optimize for AI." The gate asks for a reader task under `g-helpful-content`, official AI boundaries from `g-ai-opt-guide`, and any property query evidence from `g-gsc-api` before drafting.

[[Content Brief Output Contract]] consumes this checklist. It needs the filled gate table, approved source IDs, and blocker notes; it expects a pass, revise, or defer decision attached to the brief handoff.

## Checklist-Specific Edge Cases

- A brief can pass Search intent work but still fail the gate if AIO or AI Mode language lacks `g-ai-features`.
- A market caveat from `sparktoro-zero-click-2026` should not replace property data when `g-gsc-api` exports exist.
- A passage instruction should be blocked when the source cannot sit near the claim under `ziptie-aio-source-selection`.
- A current Google-change claim belongs in [[2026 Google Update Timeline]] when `g-ranking-history` is the evidence owner.

## Handoff Rules

1. Send reader-language problems to [[6-Pillar Dual Optimization]].
2. Send surface and metric splits to [[Search Visibility Versus Citation Exposure]].
3. Send disputed CTR framing to [[AI Overview CTR Interpretation]].
4. Send AI Mode weighting to [[AI Mode Query Share Context]].
5. Send unresolved risk entries to [[Dual Optimization Risk Register]].

## Related
- [[Dual Optimization]]
- [[6-Pillar Dual Optimization]]
- [[AI Citation Mechanics]]
- [[Search Visibility Versus Citation Exposure]]
- [[AI Mode Query Share Context]]
- [[Dual Optimization Risk Register]]
