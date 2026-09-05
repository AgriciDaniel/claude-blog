---
type: spoke
title: "Source Ledger Reading Guide"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [sources, research-pack, active]
domain: "Source Evidence"
confidence: verified
related:
  - "[[Research Pack Index]]"
  - "[[Current Requirements Digest]]"
  - "[[Source Confidence Labels]]"
  - "[[Evidence Gap Register]]"
  - "[[Claim To Source Mapping]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history"
---

# Source Ledger Reading Guide

## Record Scope

This guide explains how to read a row in `references/source-ledger.json` without overclaiming what that row proves. The ledger has 117 source entries as of the 2026-07-09 check. Each entry can support only the claim coverage named by its URL, date fields, source type, confidence, and section.

Use this note when a writer asks why a source ID is not enough by itself. A source ID is a handle, not a verdict. The verdict comes from matching the exact claim to the source's scope and the claim-ledger discipline.

## Events Or Items This Register Captures

- Source IDs used repeatedly across source-governance notes.
- The dates reviewers must inspect before treating a claim as current.
- Confidence states that need a downgrade or a gap record.
- Rollback triggers when a source changes or no longer covers the claim.

## Events Or Items Routed Elsewhere

- New research evidence belongs in `references/source-ledger.json`, outside this folder.
- Release blocker decisions belong in [[Research Release Gate Notes]].
- Live claim rows belong in [[Claim To Source Mapping]].
- Missing source IDs, raw snapshots, or date conflicts belong in [[Evidence Gap Register]].

## Source Ledger Reading Guide Register Table

| Ledger field to inspect | Example source ID | What it tells the reviewer | Common misuse | Next action |
|---|---|---|---|---|
| `id` | `g-ai-opt-guide` | The citation handle to use in body tables and claim maps. | Treating the handle as proof without checking the claim text. | Match the claim to `supports_claims`. |
| `url` | `g-search-gallery` | The exact page that should be inspected during refresh. | Replacing it with a nearby Google page because it is easier to cite. | Keep the canonical ledger URL in `source_urls`. |
| `last_updated` or `published` | `g-helpful-content` | Whether the source date is current enough for release work. | Copying a date from another page in the same source family. | Record a date gap if fields conflict. |
| `section` | `g-ranking-history` | Which wiki route should own interpretation. | Using a monitoring source for content-quality or schema advice. | Route to the matching canon note. |
| `confidence` plus `evidence_tier` | `g-ai-opt-guide` | Source quality, not the full recommendation confidence. | Marking a mixed claim verified because one row is high confidence. | Apply [[Source Confidence Labels]]. |
| `supports_claims` | `g-faqpage-sd` | The exact wording range the ledger row can support. | Using the title to infer broader policy. | Compare the draft sentence before citing. |

## Source, Confidence, Owner, Status, And Due Date

| Source ID | Owner | Confidence use | Status on 2026-07-09 | Next review | Rollback trigger |
|---|---|---|---|---:|---|
| `g-helpful-content` | content steward | Strong for people-first content framing. | Active ledger source. | 2026-08-01 | Page date or guidance changes. |
| `g-ai-opt-guide` | GEO steward | Strong for Google Search AI guidance. | Active ledger source. | 2026-08-01 | Google changes AI Search optimization guidance. |
| `g-search-gallery` | schema steward | Strong for supported rich-result inventory. | Active ledger source. | 2026-08-01 | Supported type list changes. |
| `g-ranking-history` | monitoring owner | Strong for confirmed ranking event history. | Active ledger source. | 2026-08-01 | New incident appears or redirect target changes. |
| `g-faqpage-sd` | schema steward | Strong for FAQ rich-result retirement. | Active ledger source. | 2026-08-01 | Search updates restore or revise feature handling. |

## Source Ledger Reading Guide Review Loop

1. Read the source entry before opening wiki prose that summarizes it.
2. Confirm URL, date fields, confidence, evidence tier, section, and supported claims.
3. Compare the draft claim to the narrowest supported claim in the entry.
4. If the draft is broader, lower the label or split the claim.
5. If the ledger cannot represent the source cleanly, log the gap instead of smoothing it over.

## Ledger Read: Shared Page, Different Claim

The AI optimization guide appears under more than one source ID.
Use `g-ai-opt-guide` for Google AI Search guidance.
Use the llms.txt update ID for that specific clarification.
The failure is merging both IDs because the URL matches.
[[Factcheck Claim Register]] consumes the selected ledger row.
Inputs provided: source ID, supported claim, date, and refresh trigger.
Expected output: claim row that cites the right ledger handle.

## Related

- [[Research Pack Index]]
- [[Current Requirements Digest]]
- [[Source Confidence Labels]]
- [[Evidence Gap Register]]
- [[Claim To Source Mapping]]
