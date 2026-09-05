---
type: policy
title: "Provenance Trace Policy"
status: active
created: 2026-08-25
updated: 2026-08-25
tags: [meta, provenance, policy]
domain: "Blog Content Brain"
confidence: verified
related:
  - "[[Source Ledger Reading Guide]]"
  - "[[Claim To Source Mapping]]"
  - "[[Source Quality Ladder]]"
  - "[[Research Pack Index]]"
  - "[[Claim Verification Flow]]"
  - "[[Corpus Scope Policy]]"
  - "[[Memory Governance Policy]]"
  - "[[Uncertainty Eval Policy]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
---

# Provenance Trace Policy

## Purpose

A reader must be able to move from a recommendation to its claim, source, verification decision, and limitation without trusting the author’s memory.

## Operating contract

Every volatile or externally verifiable statement must carry a traceable source ID near the claim. The ledger row identifies the URL and review dates. The verification record identifies the decision and evidence hash. The wiki note states the practical boundary and a confidence tag.

## Trace chain

Recommendation -> wiki claim -> source ID -> source-ledger row -> review decision -> public source content.

A broken link at any stage lowers confidence. A live URL alone does not repair the chain.

## Required fields

| Layer | Required elements | Failure state |
|---|---|---|
| Recommendation | Exact action and boundary | Too broad to test |
| Wiki note | Claim, caveat, related links | Orphan interpretation |
| Source reference | Stable source ID | URL-only citation |
| Ledger | Title, URL, dates, tier | Incomplete provenance |
| Verification | Decision, method, hash, note | Unreviewed freshness |
| Source | Publicly retrievable evidence | Unavailable |
| Output | Nearby citation and date | Detached bibliography |
| Update | Superseding evidence | Silent drift |

## Trace procedure

1. Split recommendations into atomic claims.
2. Mark which claims are current, numeric, or high stakes.
3. Resolve a ledger ID for each claim.
4. Inspect the source, not only the title or snippet.
5. Record what the source supports and does not support.
6. Classify evidence as official, standards, primary, practitioner, or market.
7. Apply a confidence tag that reflects the weakest link.
8. Keep inference language distinct from sourced fact.
9. Add a refresh date appropriate to the source.
10. Re-run the trace after editing the recommendation.

## Multi-source claims

A compound claim needs either one source that supports every part or separate source IDs adjacent to their parts. Do not cite a launch post for a later changelog event. Do not cite Schema.org for Google Search behavior. Do not cite a proposal for product adoption.

## Conflicts

When sources disagree, preserve both positions, their dates, and their scopes. Prefer the source with direct authority for the claim. Explain the selection. Do not average incompatible definitions.

## Public output

Public prose may cite the public source URL. Private ledgers, review records, raw captures, and local paths remain excluded by the publishing boundary. [[Claim To Source Mapping]] may guide the writer but is not itself proof.

## Audit evidence

A compliant trace can be sampled mechanically by source ID and inspected semantically by a reviewer. Missing numeric literals, low token coverage, changed canonical URLs, and updated living documents are review triggers, not automatic refutations.
## Trace sampling

Audit a representative set of claims from each authority class and every
release-critical claim. Sampling never replaces complete review of blockers.

| Sample class | Minimum focus |
|---|---|
| Official living doc | Current content and date |
| Standards source | Exact section and version |
| Primary study | Method and denominator |
| Practitioner source | Advisory limitation |
| Numeric claim | Literal and unit |
| Product behavior | Correct authority |

Record the sampled source IDs, reviewer, failures, and repairs. Expand the sample
when one failure suggests a systematic mapping problem.
