---
type: spoke
title: "SERP Brief Input Contract"
domain: "Blog Briefs"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [briefs-outlines, serp-briefs, active]
---

# SERP Brief Input Contract

## SERP Brief Input Contract Deliverable Boundary

This contract defines the minimum inputs required before a SERP-informed brief can be drafted. It is a gate, not a brief template. If required fields are missing, the work pauses or moves to a research task. The contract prevents briefs from starting with only a keyword, a generic source bundle, or a copied competitor outline.

The contract uses `g-helpful-content` to require a people-first objective and `g-qrg-full` when the topic needs trust, reputation, or YMYL review. Use `g-gsc-api` for first-party query, click, and impression fields when available. Use `g-ai-features` to scope AI-feature language without promising inclusion.

### Required Inputs

Every brief needs a target topic, primary query set, reader job, intent label, source pack, competitive observations, evidence blocks, risk notes, internal-link candidates, and draft owner. A client or property-data field should say available, unavailable, or not requested.

### Exclusions Before Drafting

Exclude unverified competitor claims, AI-generated source summaries, screenshot-only evidence, and channel actions that would mutate external systems. V1 remains advisory and read-only.

## Input Acceptance Table

| Required section | Mandatory fields | Validator | Evidence | Owner | Blocker state |
| --- | --- | --- | --- | --- | --- |
| Reader and query context | reader job, primary query, locale, decision stage | [[Reader Job Statement]] | query set and stakeholder context | brief owner | Block if job is only a keyword |
| Intent and SERP notes | primary intent, secondary intent, observation date, device | [[Search Intent Classification]] | [[SERP Observation Ledger]] | SEO strategist | Block if observation is undated |
| Source inventory | source IDs, URLs, dates, claim coverage, limits | [[Brief Source Pack]] | `g-helpful-content`; other source IDs | source steward | Block if generic bundle remains |
| Trust and risk flags | YMYL status, approval owner, caveat text | [[Brief Risk Notes]] | `g-qrg-full` when trust sensitivity matters | editor | Block if high-risk claim lacks owner |
| AI and click posture | AI surface affected, click metric, visibility metric | [[AI Citation Mechanics]]; [[Dual Optimization]] | `g-ai-features`; `g-gsc-api` when property data exists | analyst | Revise if guarantees appear |
| Draft constraints | heading rules, evidence blocks, internal links, voice notes | [[Heading Hierarchy Rules]] | approved outline inputs | outline owner | Block if handoff lacks constraints |
| Property data state | GSC available, unavailable, or not requested | [[Google Data Integrations]] | `g-gsc-api` for first-party fields | analyst | Revise if market data substitutes silently |
| Brand and compliance limits | forbidden terms, reviewer, approval lane | [[Brief Risk Notes]] | `g-qrg-full` when trust sensitivity applies | editor | Block if owner is unnamed |
| Excluded claims | claims rejected by evidence review | [[Evidence Block Requirements]] | source ID behind each rejection | source steward | Block if removed claims can reappear |

## SERP Brief Input Contract Handoff Procedure

1. Fill each required section with either a value or an explicit "not available" note.
2. Attach source IDs beside claims, not only as a frontmatter list.
3. Mark blockers before the brief owner asks for writing.
4. Send missing evidence to [[Brief Source Pack]] and missing risk review to [[Brief Risk Notes]].
5. Move the contract to [[Outline QA Checklist]] only after all blocker fields have an owner or resolution.

## Input Gate Example

Initial request: "Make a brief for AI citation strategy with these three competitor URLs." The contract blocks drafting because there is no reader job, locale, observation date, source pack, property-data state, or rejected-claims list. Source IDs: `g-helpful-content`, `g-ai-features`.

Completed input: target topic, US English locale, query set, reader job, dated SERP observation, approved source IDs, risk owner, and "do not claim guaranteed AI citation" rule. The brief may proceed to outline QA because blockers now have owners. Source IDs: `g-ai-opt-guide`, `g-qrg-full`.

## Contract-Specific Failure Modes

- "Not available" is used to skip research without naming impact. Source ID: `g-helpful-content`.
- Screenshots replace dated observation summaries. Source ID: `dfs-api`.
- Source IDs appear only in a bibliography field. Source ID: `g-helpful-content`.
- The contract omits who can approve trust-sensitive claims. Source ID: `g-qrg-full`.

## Deliverable Intake Wiring

[[Content Brief Output Contract]] consumes this contract as its intake gate. Inputs provided: topic, locale, query set, reader job, intent label, source pack, risk state, data availability, and exclusions. Expected output: a complete brief packet rather than a keyword prompt.

[[SERP Outline Output Contract]] consumes the contract after blockers close. Expected output: an outline that respects excluded claims, approved evidence, and known data gaps.

## Sources

- `g-helpful-content`
- `g-qrg-full`
- `g-gsc-api`
- `g-ai-features`
- `g-ai-opt-guide`
- `dfs-api`

## Contract Outcome

The final state is ready, revise, blocked, or canceled. Ready means the drafter receives a complete brief packet, not permission to invent sources or overstate AI visibility.
