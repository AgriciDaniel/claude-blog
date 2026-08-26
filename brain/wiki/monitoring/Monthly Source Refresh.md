---
type: spoke
title: "Monthly Source Refresh"
domain: "Google Update Monitoring"
status: active
created: 2026-07-06
updated: 2026-08-25
tags: [monitoring, google-updates, active]
source_urls:
  - "https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
  - "https://developers.google.com/search/updates/search_docs_updates.rss"
  - "https://status.search.google.com/incidents.json"
---

# Monthly Source Refresh

## Monthly Source Refresh Evidence Job

This spoke defines the monthly monitoring routine for Search Central, the Search Status Dashboard, QRG, schema support, spam policy, and AI-search guidance. Its job is evidence hygiene. It should update source posture and route stale claims, not rewrite advice directly.

## Source Types This Note Owns

The refresh owns living sources and fast-moving official records: status history, Search Central documentation, structured-data support lists, spam-policy pages, AI guidance, and QRG files. It also checks whether source-ledger records have enough date precision and retrieval metadata for release use. If an item is market research rather than an official or standards source, the refresh can flag it but should not validate it alone.

Run `python3 scripts/check_google_currentness.py --root . --json` before manual
review. It compares the canonical ledger date with Google's ranking-incident
JSON and Search documentation RSS and fails closed when a newer source date or
an overdue review is found. It never writes guidance. Review the manual source
watches in `data/google-updates.json` separately, then run
`python3 scripts/sync_google_updates.py --root . --check` to detect projection
drift.

## Claims This Note Must Not Validate Alone

This note cannot validate ranking impact, traffic impact, AI citation rate, or a named site's recovery. It can only confirm whether the source still says what the brain claims it says. Impact and measurement need [[Google Data Integrations]] or a source-specific note such as [[AI Citation Mechanics]].

## Monthly Source Refresh Source Table

| Source ID | URL role | Date checked | Claim coverage | Limitation | Refresh cadence |
|---|---|---|---|---|---|
| `g-ranking-history` | Official ranking-history chronology | 2026-07-09 | Ranking and rollout history | Does not prove page impact | Monthly and after status changes |
| `g-status-dashboard` | Current dashboard route for ranking history | 2026-07-06 | Confirmed dashboard event lane | Same URL can represent multiple event IDs | Monthly |
| `g-search-gallery` | Supported rich-result types | 2026-07-08 | Schema support and unsupported feature checks | Gallery support is not a ranking promise | Monthly and before schema deliverables |
| `g-ai-opt-guide` | AI-search guidance and llms.txt stance | 2026-07-08 | Special-file and special-markup claims | Does not provide market-share metrics | Monthly and before GEO/AEO briefs |
| `g-qrg-full` | Full rater guidelines | 2026-07-09 | Quality-review context | Rater guidelines are not a direct ranking-system changelog | Monthly |
| `g-spam-policies` | Spam-policy definitions | 2026-07-06 | Scaled content, cloaking, redirects, abuse categories | Needs page-level evidence before action | Monthly and after spam updates |
| `g-update-2026-05-21-may-2026-core-update` | Current core-event smoke test | 2026-07-09 | Confirms the refresh sees the latest 2026 core route | Does not validate page impact | Monthly with dashboard check |
| `g-update-2026-06-24-june-2026-spam-update` | Current spam-event smoke test | 2026-07-06 | Confirms the refresh sees the latest spam route | Does not prove local spam risk | Monthly with dashboard check |
| `g-genai-reports` | Generative-AI reporting source | 2026-07-08 | AI Overview and AI Mode reporting availability | Property access can differ from documentation | Monthly and before GEO reports |
| `g-search-docs-updates-2026-07-07-product-structured-data` | Product-schema changelog check | 2026-07-09 | Product.category and sale-duration guidance | Product context is required before blog schema use | Before schema deliverables |
| `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` | Vendor-claim boundary | 2026-07-06 | Third-party SEO tool limitations | Does not replace first-party property evidence | Monthly and before audit claims |

## Monthly Source Refresh Refresh Procedure

1. Open the source-ledger row and verify URL, retrieval date, source type, confidence, and refresh due date.
2. Compare the current source to the note that depends on it; mark claims stale when wording, support, or date precision changed.
3. Route the finding to the owning note: timeline, schema watch, AI search watch, QRG watch, spam playbook, or impact review.
4. Record no-action results with an exact date so they can be invalidated next month.
5. Keep the brain read-only: write a recommendation or gap, never change external systems from this routine.

## Refresh Output Format

Each refresh should produce a short entry with source ID, check date, changed or unchanged status, affected notes, owner, and next due date. If the source is a living document, include a limitation line even when no visible change is found.

## Refresh Packet Example

For the 2026-08 refresh, the operator checks `g-ai-opt-guide`, `g-search-gallery`, and `g-qrg-full`.
`g-ai-opt-guide` still blocks special Google AI file claims.
`g-search-gallery` still controls supported rich-result eligibility.
`g-qrg-full` still supplies quality-review context, not direct ranking-system proof.
The packet names affected notes and marks no-change where the source text is stable.
The downstream deliverable is [[Factcheck Claim Register]].
It receives source ID, checked date, claim wording, limitation, and next review date.
It should output verified, stale, blocked, or pending for each delivery claim.

## Refresh-Specific Pitfalls

- A living document can be unchanged today and still require a due date.
- A fresh retrieval date does not make a weak claim stronger than its source.
- Market research flagged here still needs claim-ledger verdicts before use.
- Updating a source row without routing affected notes leaves stale guidance hidden.

## Related

- [[Google Algorithm Update Ledger]]
- [[Schema Deprecation Watch]]
- [[AI Search Update Watch]]
- [[QRG Revision Watch]]
- [[Research Pack Index]]
