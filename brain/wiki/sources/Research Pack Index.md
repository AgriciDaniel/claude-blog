---
type: hub
title: "Research Pack Index"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [sources, research-pack, active]
domain: "Source Evidence"
confidence: verified
related:
  - "[[index|Index]]"
  - "[[hot|Hot]]"
  - "[[CONVENTIONS]]"
  - "[[Claim To Source Mapping]]"
  - "[[Current Requirements Digest]]"
  - "[[Evidence Gap Register]]"
  - "[[research-pack-2026-07-06|Research Pack 2026-07-06]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history"
---

# Research Pack Index

## Research Pack Index Routing Job

Research Pack Index is the wiki route into `references/source-ledger.json`, the current requirements digest, canon notes, claim maps, and evidence gaps. It tells operators where to go next; it does not replace the ledger.

The source ledger has 117 entries as of 2026-07-09. This hub keeps the source-governance folder navigable while leaving machine-readable evidence in `references/source-ledger.json`.

## Notes That Belong In Research Pack Index

- Source-reading and source-priority notes.
- Claim verification and claim-to-source mapping notes.
- Current requirements summaries grounded in source IDs.
- Gap, release, refresh, and URL hygiene notes.
- The human-readable [[research-pack-2026-07-06|Research Pack 2026-07-06]] companion.

## Notes That Should Be Routed Elsewhere

- Algorithm interpretation belongs in [[Google Algorithm Update Ledger]].
- Blog schema execution belongs in [[Blog Schema Stack]].
- AI citation mechanics belong in [[AI Citation Mechanics]].
- Data integration evidence belongs in [[Google Data Integrations]].

## Research Pack Index Folder Table

| Folder note | Primary job | Owner | Source coverage | Refresh trigger |
|---|---|---|---|---|
| [[Source Ledger Reading Guide]] | Explain ledger fields, dates, confidence, and source sections. | source steward | `g-helpful-content`; `g-ai-opt-guide`; `g-search-gallery`; `g-ranking-history` | Ledger schema or date model changes. |
| [[Canon Notes Map]] | Route canon notes to their primary source families. | editorial steward | Canon-specific source IDs and current requirement routes. | Canon route changes. |
| [[Google Source Priority Ladder]] | Rank Google source families by claim fit. | source steward | Google content, AI, schema, and ranking sources. | Google docs or dashboard changes. |
| [[Claim To Source Mapping]] | Tie release-facing claims to source IDs and limitations. | release reviewer | Current source IDs plus claim limitations. | Any current claim changes. |
| [[Evidence Gap Register]] | Track missing, stale, broad, or unsupported evidence. | source steward | Gap records tied to affected source IDs. | New gap or closure. |
| [[Source Refresh Cadence]] | Schedule monthly, release-time, and on-change checks. | source steward | Source IDs with cadence and owner. | Source date or update cadence changes. |
| [[Research Release Gate Notes]] | Convert source completeness into release pass or fail posture. | release owner | Evidence completeness, severity, and fix ownership. | Release review. |

## Active Notes, Owners, And Source Coverage

Use the table above as the first stop for folder-level navigation. Use [[Claim Verification Flow]] when a draft claim needs step-by-step review before it enters the map.

## Research Pack Index Graph Hygiene Checks

1. Every source-governance spoke should link back here or to a sibling source note.
2. Every source-backed body table should include source ID, URL, date, coverage, and limitation when relevant.
3. Every unsupported claim should link to [[Evidence Gap Register]] rather than hiding in prose.
4. Every Google AI Search claim should be able to route to [[AI Citation Mechanics]].
5. Every schema support claim should be able to route to [[Blog Schema Stack]].

## Routing Example For A Brief Source Pack

A strategist starts a brief for "best CRM onboarding checklist."
Open this hub, then move to [[Claim Verification Flow]] for claim slots.
Use `g-helpful-content` for usefulness and `g-ai-opt-guide` for AI caveats.
The failure mode is treating this hub as the evidence itself.
[[Content Brief Output Contract]] consumes the selected source route.
Inputs provided: source-governance note, source ID, and caveat target.
Expected output: source pack section with unresolved blockers marked.

## Related

- [[index|Index]]
- [[hot|Hot]]
- [[CONVENTIONS]]
- [[Claim To Source Mapping]]
- [[Current Requirements Digest]]
- [[Evidence Gap Register]]
- [[research-pack-2026-07-06|Research Pack 2026-07-06]]
