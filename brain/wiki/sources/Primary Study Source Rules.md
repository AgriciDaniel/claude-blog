---
type: spoke
title: "Primary Study Source Rules"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [sources, research-pack, active]
domain: "Source Evidence"
confidence: verified
related:
  - "[[Research Pack Index]]"
  - "[[Practitioner Source Caveats]]"
  - "[[Source Confidence Labels]]"
  - "[[Claim To Source Mapping]]"
  - "[[Evidence Gap Register]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history"
---

# Primary Study Source Rules

## Rule Scope

This note defines when a market study, platform benchmark, academic paper, or first-party analysis can support a behavior claim in the blog brain. It does not turn studies into Google requirements. It keeps study claims separate from official guidance sources such as `g-helpful-content`, `g-ai-opt-guide`, `g-search-gallery`, and `g-ranking-history`.

Use these rules when a draft wants to cite a study for user behavior, CTR direction, AI citation exposure, schema adoption, or update impact. The study can inform planning, but release copy must preserve the study's method and confidence.

## Allowed Actions And Disallowed Actions

- Allowed: cite a study as observed evidence with its sample, period, platform, and source ID.
- Allowed: pair a study with official guidance when the recommendation mixes behavior and requirements.
- Disallowed: convert a study result into a ranking guarantee, traffic forecast, or universal click-through rule.
- Disallowed: use a study to claim Google supports a feature when `g-search-gallery` or another official page does not.

## Exceptions That Require Approval

Claims touching YMYL topics, legal obligations, medical outcomes, financial decisions, or named client performance require owner approval and first-party evidence when available. Claims about current Google rollouts require `g-ranking-history` or a Google Search Central source, not a third-party volatility chart.

## Primary Study Source Rules Rule Table

| Rule | Evidence source basis | Applies to | Exception | Approval path |
|---|---|---|---|---|
| Preserve the study window and sample before using a number. | Claim-ledger verdict discipline plus official-source cross-check. | CTR, zero-click, AI citation, and market-share studies. | First-party property data supersedes market averages for local decisions. | Editor plus source steward. |
| Separate observed behavior from Google requirements. | `g-helpful-content`; `g-ai-opt-guide` | Content quality, AI Search, and audience behavior recommendations. | A Google page directly states the requirement. | Source steward records source ID in [[Claim To Source Mapping]]. |
| Check feature support before recommending schema tactics. | `g-search-gallery` | BlogPosting, Article, FAQ, HowTo, Product, and other markup advice. | A standards-only claim needs a separate source outside this note. | Schema reviewer plus source steward. |
| Do not use third-party update chatter as official rollout evidence. | `g-ranking-history` | Core, spam, ranking incident, and volatility notes. | A Google Search Central post names the event. | Monitoring owner. |
| Downgrade any single-source study used for client-facing decisions. | `references/claim-ledger.md` verdict rules. | Benchmarks, agency tests, tool reports, and surveys. | The client supplies first-party data that directly supports the local claim. | Reviewer signs the advisory label. |
| Keep AI Overview and AI Mode studies separated. | `ahrefs-aio-vs-aimode`; `g-ai-opt-guide` | Citation-surface comparison and Google AI Search boundaries. | Official Google guidance overrides practitioner interpretation. | GEO reviewer plus source steward. |
| Quote market-share datasets with their filter context. | `statcounter` | Search-engine share, geography, platform, and month. | First-party referral data answers the property question. | Analyst plus source reviewer. |

## Review And Rollback

1. Confirm the study has a real source ID or send it to [[Evidence Gap Register]].
2. Compare the claim against the official source family that governs the topic.
3. Assign `AS-REPORTED`, `SINGLE-SOURCE`, `CONTESTED`, or `FOLKLORE` when the study is not direct official evidence.
4. Add a rollback note that names the source date, study window, and condition that would retire the claim.

## Study Use Case: Zero-Click Context

A strategy deck wants a zero-click statistic beside a blog roadmap.
Use `sparktoro-zero-click-2026` only as dated market context.
Do not convert it into a forecast for the client's article inventory.
If GSC exports exist, `g-gsc-api` becomes the local evidence route.
Failure modes include missing geography, panel window, and query class.
Another failure is mixing market studies with Google requirements.
[[Blog Strategy Architecture Blueprint]] consumes the study decision.
Inputs provided: study ID, period, caveat, and local-data override rule.
Expected output: strategy context or a blocked forecast claim.

## Related

- [[Research Pack Index]]
- [[Practitioner Source Caveats]]
- [[Source Confidence Labels]]
- [[Claim To Source Mapping]]
- [[Evidence Gap Register]]
