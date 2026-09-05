---
type: deliverable
title: "Brand Context Contract"
domain: "Blog Content Brain"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, brand, voice]
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
  - "https://www.nngroup.com/articles/ten-usability-heuristics/"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
---

# Brand Context Contract

## Contract Boundary For Brand Context

This contract defines the minimum acceptable `BRAND.md` and `VOICE.md` context before [[Voice and Style]], [[Blog Quality Score]], or [[FLOW Framework]] can use brand direction in a draft. It separates durable audience and positioning facts from campaign-only preferences. The source IDs are `g-helpful-content`, `g-qrg-full`, `nng-editorial-heuristics`, and `g-ai-opt-guide`.

## Required Inputs Excluded From Guesswork

The contract requires audience, buyer problem, positioning, approved claims, proof points, vocabulary, taboo phrases, tone range, example passages, and reviewer owner. It excludes invented differentiation, unverifiable superiority claims, and style rules that conflict with reader comprehension or trust.

## Brand Context Acceptance Table

| Contract field | Mandatory content | Validator | Blocker state | Handoff owner |
|---|---|---|---|---|
| Audience | Role, maturity, pain, decision context | Strategist | Audience could fit any brand | Brand owner |
| Positioning | Category, promise, proof, limits | Editor | Unverified superiority claim | Brand owner |
| Do rules | Preferred vocabulary and examples | Voice reviewer | Rule lacks example passage | Editor |
| Do not rules | Taboo phrases, banned claims, tone limits | Legal or brand owner | Ban conflicts with required disclosure | Reviewer |
| Proof library | Approved sources and case references | Factchecker | Claim has no evidence route | Researcher |
| Auto-load map | Which skills or workflows load context | Operator | Wrong context loads for workflow | Workflow owner |
| Revision log | Date, reason, approver | Managing editor | Change lacks owner | Managing editor |

## Handoff Procedure For Brand Updates

1. Confirm whether the update changes reader value, trust, or only surface wording.
2. Check claims against [[Research Pack Index]] before adding them to the proof library.
3. Test voice rules on one paragraph and reject rules that reduce clarity.
4. Route approved context to [[Style Learning Voice Profile]] for measurable style fields.
