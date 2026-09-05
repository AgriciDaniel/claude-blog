---
type: spoke
title: "Evidence Gap Register"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [sources, research-pack, active]
domain: "Source Evidence"
confidence: verified
related:
  - "[[Research Pack Index]]"
  - "[[Claim To Source Mapping]]"
  - "[[Current Requirements Digest]]"
  - "[[Source Confidence Labels]]"
  - "[[Research Release Gate Notes]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history"
---

# Evidence Gap Register

## Evidence Gap Register Record Scope

This register holds source problems that would otherwise leak into recommendations as confident claims. A gap is not a backlog wish. It is a claim-risk record with an owner, review date, confidence state, and rollback trigger.

Use this note when a source is missing, stale, too broad, unsupported by the assigned source IDs, or unable to prove the exact claim. The fix can be to find better evidence, narrow the claim, downgrade the label, or remove the claim.

## Events Or Items This Register Captures

- A Google source supports a narrower claim than the draft uses.
- A claim cites a real URL but no source ID exists in the ledger.
- A source date conflicts with a note's date.
- A recommendation crosses from Google Search into non-Google assistant behavior.
- A schema claim names a feature not present in `g-search-gallery`.

## Events Or Items Routed Elsewhere

- Confirmed update history belongs in [[Google Algorithm Update Ledger]] once `g-ranking-history` supports it.
- Clean claim rows belong in [[Claim To Source Mapping]].
- Label definitions belong in [[Source Confidence Labels]].
- Release gate consequences belong in [[Research Release Gate Notes]].

## Evidence Gap Register Register Table

| Gap ID | Evidence problem | Source ID involved | Owner | Confidence state | Status | Next review | Rollback trigger |
|---|---|---|---|---|---|---:|---|
| GAP-SRC-001 | A content claim turns `g-helpful-content` into a ranking guarantee. | `g-helpful-content` | content steward | gap | open | 2026-07-16 | Remove guarantee or add property evidence with a narrower claim. |
| GAP-SRC-002 | A Google AI Search claim is applied to non-Google assistants. | `g-ai-opt-guide` | GEO steward | contested | open | 2026-07-16 | Split Google Search guidance from assistant-specific evidence. |
| GAP-SRC-003 | A schema recommendation names a rich result not shown in Search Gallery. | `g-search-gallery` | schema reviewer | gap | open | 2026-07-16 | Remove rich-result claim or add current feature documentation. |
| GAP-SRC-004 | An update impact claim uses official history for timing but not causation. | `g-ranking-history` | monitoring owner | advisory | open | 2026-07-16 | Rephrase as confirmed rollout only, or add first-party impact analysis. |
| GAP-SRC-005 | A note needs API or generated-media evidence outside this source slice. | none in assigned set | source steward | gap | open | 2026-07-23 | Add proper ledger entries outside this folder or remove the claim. |
| GAP-SRC-006 | A FAQPage recommendation treats a retired Google feature as current. | `g-faqpage-sd` | schema reviewer | gap | open | 2026-07-16 | Replace the rich-result promise with visible-content guidance. |
| GAP-SRC-007 | An llms.txt recommendation promises Google AI visibility improvement. | `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` | GEO steward | contested | open | 2026-07-16 | Split Google Search from other crawler assumptions. |

## Source, Confidence, Owner, Status, And Due Date

The table's confidence state is a claim state, not a source-quality score. A high-quality Google source can still produce a gap when a note asks it to prove too much.

## Evidence Gap Register Review Loop

1. Identify the exact sentence that would become unsafe if published.
2. Name the source ID that was used or mark the source as missing.
3. Assign an owner who can narrow, source, or remove the claim.
4. Set the next review date close enough to block release drift.
5. Move the issue to [[Claim To Source Mapping]] only after the claim has source ID, date, coverage, and limitation.

## Gap Closure Example

A draft says FAQPage markup will recover Google FAQ rich results.
The gap cites `g-faqpage-sd` and blocks that release wording.
Closure means replacing the promise with a visible-content recommendation.
If the reviewer cannot narrow it, the claim stays blocked.
The failure mode is marking a gap closed because the URL is official.
Official sources still fail when they do not cover the exact sentence.
[[Factcheck Claim Register]] consumes open and closed gap outcomes.
Inputs provided: gap ID, source ID, owner, and rollback trigger.
Expected output: claim status, blocked release note, or approved rewrite.

## Related

- [[Research Pack Index]]
- [[Claim To Source Mapping]]
- [[Current Requirements Digest]]
- [[Source Confidence Labels]]
- [[Research Release Gate Notes]]
