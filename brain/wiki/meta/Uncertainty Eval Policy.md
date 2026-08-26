---
type: policy
title: "Uncertainty Eval Policy"
status: active
created: 2026-08-25
updated: 2026-08-25
tags: [meta, uncertainty, policy]
domain: "Blog Content Brain"
confidence: verified
related:
  - "[[FLOW Confidence Tags]]"
  - "[[Evidence Gap Register]]"
  - "[[Source Quality Ladder]]"
  - "[[Claim Verification Flow]]"
  - "[[Provenance Trace Policy]]"
  - "[[Memory Governance Policy]]"
  - "[[AI Citation Attribution Question]]"
  - "[[Quality Gate Failure Modes]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/third-party-seo"
---

# Uncertainty Eval Policy

## Purpose

Uncertainty must change the recommendation, not merely add a vague disclaimer after it. This policy defines how evidence gaps affect language, confidence, action, and release claims.

## Operating contract

Every nontrivial conclusion is classified as verified fact, supported inference, unresolved suspicion, user decision, or unknown. A confidence tag reflects evidence quality, freshness, scope, and contradiction. Missing evidence cannot be converted into certainty by consensus or repetition.

## Evaluation axes

| Axis | High confidence condition | Downgrade trigger |
|---|---|---|
| Authority | Primary authority for the claim | Secondary summary |
| Directness | Source states the relevant fact | Inference from adjacent text |
| Freshness | Reviewed within its interval | Living document is stale |
| Scope | Population and product match | Geography or surface differs |
| Reproducibility | Method can be repeated | Hidden sampling |
| Consistency | Independent evidence agrees | Credible contradiction |
| Completeness | Claim parts all supported | Compound citation gap |
| Measurement | Definition and denominator known | Vendor-only score |

## Confidence tags

- verified: current direct evidence supports the exact scoped claim.
- advisory: evidence supports a recommendation, but outcomes remain uncertain.
- medium: useful evidence has a clear limitation or indirect step.
- low: preliminary, conflicting, stale, or poorly scoped evidence.
- unknown: required evidence is absent.
- as-reported: the source’s result is preserved without independent confirmation.

## Decision procedure

1. Write the smallest testable claim.
2. Label fact, inference, suspicion, decision, or unknown.
3. Identify the claim’s authority and date.
4. Check whether the source scope matches.
5. Look for a credible counterexample.
6. Separate each unsupported part.
7. Select the lowest confidence implied by the chain.
8. Change the action to match the uncertainty.
9. Record a retest trigger.
10. State the remaining risk plainly.

## Action mapping

| State | Allowed response | Forbidden response |
|---|---|---|
| Verified fact | Direct scoped statement | Broader universal claim |
| Supported inference | “Evidence suggests” plus rationale | Causal certainty |
| Suspicion | Investigation question | Recommendation |
| User decision | Record scope and owner | Present as external fact |
| Unknown | Ask or block | Fill with a plausible value |
| Conflict | Present both and resolve authority | Hide the contradiction |
| Stale | Refresh or label stale | Advance verification date |
| External dependency | Report boundary | Claim completion |

## Release rule

A release-ready claim requires direct verification of its named gate. Static tests do not prove browser behavior. A local package does not prove GitHub publication. An authorization handoff does not prove execution. A clean audit does not replace human review where the contract requires it.

## Re-evaluation triggers

Re-evaluate on source changes, product launches, API version changes, new first-party data, a credible contradiction, failed tests, or a user decision that changes scope. Route unresolved evidence to [[Evidence Gap Register]].
## Calibration review

Periodically compare prior confidence tags with later outcomes. The purpose is
to improve calibration, not to reward confident language.

| Review result | Adjustment |
|---|---|
| Verified remained stable | Keep interval |
| Advisory became false | Tighten scope |
| Unknown gained evidence | Re-evaluate |
| Source drifted early | Shorten interval |
| Contradiction was missed | Expand refutation |
| Outcome was unpredictable | Preserve uncertainty |

Record both overconfidence and unnecessary caution. A well-calibrated system
sometimes returns unknown even when a stakeholder wants a recommendation.
