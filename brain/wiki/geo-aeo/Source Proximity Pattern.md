---
type: spoke
title: "Source Proximity Pattern"
domain: "GEO and AEO"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [geo-aeo, ai-citation, evergreen]
---

# Source Proximity Pattern

## Source Proximity Pattern Evidence Job

This note defines how close a source must be to the claim it supports inside an extractable passage. The pattern is editorial and evidentiary, not a documented Google ranking factor. Use `g-ai-features` and `g-ai-opt-guide` for official Google AI feature boundaries, `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` for the file shortcut caveat, and `ziptie-aio-source-selection` for practitioner guidance on visible attribution near answer blocks. `blog-io2026` provides AI Mode product context when the passage is being reviewed for conversational search.

### Source Types This Note Owns

Own primary research, official documentation, first-party data exports, standards documents, market studies, and practitioner observations when they appear beside a claim in a blog passage.

### Claims This Note Must Not Validate Alone

Do not validate ranking effect, traffic lift, AI citation probability, or assistant inclusion. Source proximity improves auditability; it does not prove distribution.

## Source Proximity Pattern Source Table

| Source ID | URL owner or type | Date basis | Claim coverage | Limitation | Refresh cadence |
|---|---|---|---|---|---|
| `g-ai-features` | Google Search documentation | last verified 2026-07-09 | AI feature and preview-control context | Does not guarantee citation | Monthly or docs change |
| `g-ai-opt-guide` | Google Search documentation | updated 2026-06-15 | AI optimization foundations and no special AI files | Not a passage template spec | Monthly or docs change |
| `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` | Google update record | 2026-06-15 event | llms.txt has no Google Search visibility effect | Does not govern non-Google consumers | Review through [[2026 Google Update Timeline]] |
| `ziptie-aio-source-selection` | Practitioner source | published 2026-03-25 | Visible attribution and extractable blocks | Advisory, not official | Replace if stronger evidence appears |
| `blog-io2026` | Google product blog | published 2026-05-19 | AI Mode product-scale context | Not a page-level traffic metric | Refresh before AI Mode planning |
| `seer-aio-impact-ctr-2026` | Practitioner analysis | published 2026-04-24 | AI Overview citation association context | Non-causal and not property-specific | Refresh before client-facing benchmark use |
| `sparktoro-zero-click-2026` | Market panel analysis | published 2026-06-08 | Search journey and click-scarcity context | Not a page forecast | Route broad claims to [[Dual Optimization]] |
| `g-genai-reports` | Google Search Central blog | published 2026-06-03 | Search Console generative AI reporting context | Property access may vary | Check when measurement claims appear |

## Source Proximity Pattern Refresh Procedure

1. Put the source ID in the same paragraph or table row as the claim it supports.
2. Add the date, geography, sample, or official-document status when the claim depends on it.
3. Move broad market context to [[AI Citation Mechanics]] or [[Dual Optimization]] instead of overloading one passage.
4. Refresh the source when the ledger due date passes or the claim becomes client-facing.

## Proximity Rewrite Example

Weak sentence: "AI citations can recover clicks, according to recent studies." The claim is too far from the source identity and too broad for `seer-aio-impact-ctr-2026`.

Stronger sentence: "The Seer analysis is advisory context for AI Overview citation association, not a causal forecast for this page." The source ID `seer-aio-impact-ctr-2026` can sit in the same paragraph or row as that caveat.

For Google feature wording, the paragraph should cite `g-ai-features` or `g-ai-opt-guide` beside the Search-specific claim. For measurement wording, `g-genai-reports` belongs beside the reporting claim rather than in a general bibliography.

## Proximity Failure Cases

- A source ID appears once in the introduction, then later paragraphs reuse numbers without nearby support.
- A figure caption names the study, but the body text makes a broader claim without limitation.
- A page footer contains the URL list, leaving the extractable answer block unsourced.
- A broad market source is placed next to a named-site recommendation, which `sparktoro-zero-click-2026` does not support.

## Claim Register Wiring

[[Factcheck Claim Register]] consumes this note as claim-source pair hygiene. It needs the exact claim sentence, nearest source ID, verdict label, limitation, owner, and refresh date.

The register expects a source-adjacent row, not a bibliography note. If the nearest source cannot support the wording, the output is "narrow claim", "replace source", or "block until sourced".

## Claim Row Shape

Write the claim sentence first, then add the nearest source ID in the same row.

Add the limitation immediately after market sources such as `seer-aio-impact-ctr-2026`.

Use `g-ai-features` for Google feature scope and `g-genai-reports` for reporting scope.

If the row needs a missing source, route it before the claim reaches a deliverable.

## Source Proximity Pattern Handoff

If the source is close but the subject is unclear, use [[Entity Clarity For AI Answers]]. If the source is missing from the ledger, route the gap to [[Research Pack Index]] before using the claim.
