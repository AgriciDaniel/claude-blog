---
type: spoke
title: "Source Confidence Labels"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [sources, research-pack, active]
domain: "Source Evidence"
confidence: verified
related:
  - "[[Research Pack Index]]"
  - "[[Claim To Source Mapping]]"
  - "[[Evidence Gap Register]]"
  - "[[Claim Verification Flow]]"
  - "[[Source Ledger Reading Guide]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history"
---

# Source Confidence Labels

## Source Confidence Labels Evidence Job

This spoke defines claim-level labels for wiki notes. A source can be high quality while a recommendation remains advisory, contested, or a gap. The label belongs to the claim as used, not to the prestige of the URL.

The claim ledger uses `CONFIRMED`, `CONTESTED`, `AS-REPORTED`, `SINGLE-SOURCE`, and `FOLKLORE`. This note translates that discipline into operating labels that writers can apply inside source-governance notes.

## Source Types This Note Owns

- Official Google Search sources that can support `verified` labels for exact Google claims.
- Claim-ledger verdict terms used to prevent overstated study or practitioner claims.
- Downgrade rules when a source supports a narrower claim than the draft.

## Claims This Note Must Not Validate Alone

- Any claim with no source ID.
- Any broad market or CTR claim that lacks method, geography, and time window.
- Any schema, AI Search, or ranking claim whose source belongs to another platform.

## Source Confidence Labels Source Table

| Operating label | Claim-ledger verdict alignment | Source pattern | Example source IDs | Use when | Downgrade when |
|---|---|---|---|---|---|
| verified | CONFIRMED | Official or primary source directly covers the claim. | `g-helpful-content`; `g-ai-opt-guide`; `g-search-gallery`; `g-ranking-history` | The wording, surface, and date all match the source. | The claim predicts outcomes or crosses platforms. |
| evidence-based | CONFIRMED or AS-REPORTED | Strong source supports an observation, but it is not a universal rule. | Same source set plus property evidence outside this note. | The note states what was observed and preserves limits. | It becomes a guarantee or local forecast. |
| practitioner | AS-REPORTED or SINGLE-SOURCE | Workflow study, tool report, or experiment. | Not established by the four Google sources alone. | The claim is framed as a heuristic. | It is presented as Google policy. |
| advisory | AS-REPORTED, SINGLE-SOURCE, or mixed evidence | Verified facts plus editorial judgment. | `g-helpful-content`; `g-ai-opt-guide` | Recommendation needs human review or local fit. | Any required source row is missing. |
| contested | CONTESTED | Credible sources or methods disagree. | Source conflict recorded in [[Evidence Gap Register]]. | The right action depends on scope or first-party data. | One source is later shown irrelevant. |
| gap | FOLKLORE or source-ledger gap | Evidence is missing, stale, date-mismatched, or too broad. | Missing, stale, or misapplied source ID. | The claim should not be release-facing. | A valid source row closes the issue. |

## Source ID, URL, Date, Claim Coverage, And Limitation

A confidence label requires all four evidence fields. If a note has a source ID and URL but no claim limitation, the reviewer cannot tell where the claim must stop.

## Source Confidence Labels Refresh Procedure

1. Read the exact claim, not just the surrounding note.
2. Match it to the source row in [[Claim To Source Mapping]].
3. Apply the weakest label needed by the full recommendation.
4. Use claim-ledger verdict language for market studies and disputed claims.
5. Move folklore, missing, or stretched claims to [[Evidence Gap Register]].

## Label Assignment Example

Claim: "Helpful content guidance guarantees ranking recovery after a rewrite."
Use `g-helpful-content`, then downgrade the claim to gap.
The source supports review framing, not a recovery guarantee.
A safe rewrite becomes advisory when paired with page evidence.
Failure cases include labeling the URL instead of the claim.
Another failure is letting a high-confidence source bless mixed evidence.
[[Blog Analyzer Score Report]] consumes the final label.
Inputs provided: claim text, source ID, downgrade reason, and limitation.
Expected output: scored finding with confidence and rollback note.

## Related

- [[Research Pack Index]]
- [[Claim To Source Mapping]]
- [[Evidence Gap Register]]
- [[Claim Verification Flow]]
- [[Source Ledger Reading Guide]]
