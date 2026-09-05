---
type: spoke
title: "Current Requirements Digest"
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
  - "[[Source Confidence Labels]]"
  - "[[Google Algorithm Update Ledger]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history"
---

# Current Requirements Digest

## Current Requirements Digest Evidence Job

This digest names the current source-backed requirements that affect blog briefs, audits, schema reviews, AI-citation work, and update memory as of 2026-07-09. It intentionally avoids data-export and generated-media requirements unless those claims have a source ID in this slice.

Use this note as a quick routing surface. It does not replace `references/source-ledger.json`, [[Claim To Source Mapping]], or the canonical hub that owns the detailed workflow.

## Source Types This Note Owns

- Google content guidance for people-first review.
- Google AI Search guidance for AI feature recommendations.
- Google Search Gallery checks for rich-result support.
- Google ranking history for confirmed update status.

## Claims This Note Must Not Validate Alone

- Search Console API export behavior, because those source IDs are not in this note's assigned source set.
- Generated media provenance or model-retirement guidance, because those source IDs are outside this note.
- Client-specific effect claims, because market or property evidence must be handled separately.

## Current Requirements Digest Source Table

| Requirement route | Source ID | URL | Date in ledger | Claim coverage | Limitation | Refresh cadence |
|---|---|---|---:|---|---|---|
| Blog quality and E-E-A-T review | `g-helpful-content` | https://developers.google.com/search/docs/fundamentals/creating-helpful-content | last updated 2025-12-10, retrieved 2026-07-09 | Content should be useful, reliable, people-first, and reviewed for E-E-A-T context. | Not a deterministic ranking checklist. | Monthly and before release. |
| Google AI Search guidance | `g-ai-opt-guide` | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide | last updated 2026-06-15, retrieved 2026-07-08 | Google Search AI features use standard Search foundations rather than special AI-only requirements. | Does not cover non-Google assistants. | On guide update. |
| Schema support review | `g-search-gallery` | https://developers.google.com/search/docs/appearance/structured-data/search-gallery | last updated 2026-07-01, retrieved 2026-07-08 | Current Google rich-result support should be checked before recommending a visual result tactic. | Does not replace feature-specific docs. | Before schema release. |
| Update memory | `g-ranking-history` | https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history | last updated 2026-06-24, retrieved 2026-07-09 | Confirmed Google ranking update history and rollout state. | Does not prove site-level impact. | Weekly during rollout, monthly otherwise. |
| FAQ rich-result posture | `g-faqpage-sd` | https://developers.google.com/search/updates#deprecating-the-faq-rich-result-feature | retrieved 2026-07-09 | FAQ rich results are retired in Google Search. | Does not ban useful visible Q and A content. | Before schema deliverables. |
| llms.txt posture | `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide | retrieved 2026-07-06 | Google Search does not use llms.txt for visibility. | Does not cover other consumers. | On AI guide update. |

## Source ID, URL, Date, Claim Coverage, And Limitation

Each digest row points to a route where the operational details live. If a claim cannot be tied to one of these source IDs or another real source in the ledger, it should become a gap rather than a new "current requirement" bullet.

## Current Requirements Digest Refresh Procedure

1. Check whether the source ID still exists in `references/source-ledger.json`.
2. Compare the ledger date with the current source date recorded in the relevant hub.
3. Update the digest only when the requirement or source route changes.
4. Send unsupported data, media, API, or platform claims to [[Evidence Gap Register]].
5. Keep claim wording short enough that [[Claim To Source Mapping]] can audit it row by row.

## Digest Application In A Schema Ticket

A reviewer sees a request to add FAQPage for rich-result visibility.
The digest routes the claim to `g-faqpage-sd`, not broad schema guidance.
The same ticket can still keep reader-facing Q and A sections.
That content choice should cite `g-helpful-content` when usefulness is claimed.
The main failure is treating a retired feature as current.
Another failure is using the digest without the date column.
[[SEO Check Validation Checklist]] consumes this digest during final review.
Inputs provided: current requirement, source ID, date, and limitation.
Expected output: pass, fix, or blocked validation state.

## Related

- [[Research Pack Index]]
- [[Claim To Source Mapping]]
- [[Evidence Gap Register]]
- [[Source Confidence Labels]]
- [[Google Algorithm Update Ledger]]
