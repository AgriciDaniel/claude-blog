---
type: spoke
title: "Research Release Gate Notes"
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
  - "[[Source Ledger Reading Guide]]"
  - "[[Current Requirements Digest]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
---

# Research Release Gate Notes

## Review Scope

This spoke translates source completeness into release readiness. It does not change maturity labels, release status, scripts, or reference files. It tells the reviewer which evidence problems must be fixed before a source-backed recommendation can leave the wiki.

Use this note when a deliverable cites current Google guidance, schema guidance, or Google AI Search guidance. The gate passes only when source IDs, exact URLs, dates, confidence labels, and rollback conditions are visible in the wiki and, for release use, represented in the machine ledger.

## Checks Unique To This Gate

- Each current claim has a source ID from the assigned source set.
- Each frontmatter `source_urls` list is topic-specific.
- Each claim table separates source coverage from limitation.
- Any source not editable in this slice is named as a gap instead of silently repaired.
- Google AI Search claims keep `g-ai-opt-guide` separate from the llms.txt clarification ID.

## Inputs Required Before Review

- The note or deliverable being reviewed.
- The relevant source IDs from `references/source-ledger.json`.
- Current claim label from [[Source Confidence Labels]].
- Any open blocker from [[Evidence Gap Register]].
- The owner who can edit machine-ledger or raw-provenance files if needed.

## Research Release Gate Notes Pass Fail Table

| Gate check | Pass condition | Source evidence | Severity if missing | Fix owner |
|---|---|---|---|---|
| Content guidance source is present. | People-first content claims cite `g-helpful-content` with date and limitation. | https://developers.google.com/search/docs/fundamentals/creating-helpful-content | High for content-quality claims. | Content steward |
| Structured data source is scoped. | General schema advice cites `g-intro-sd`; feature eligibility uses a more specific source elsewhere. | https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data | High for schema recommendations. | Schema reviewer |
| Google AI Search claim is bounded. | AI Search advice cites `g-ai-opt-guide` and does not promise citations. | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide | High for GEO and AEO guidance. | GEO steward |
| llms.txt claim is specific. | Google Search llms.txt guidance cites `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`. | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide | Medium unless used as a release claim. | Source steward |
| Rich-result claim is supported. | Google visual-result recommendations cite `g-search-gallery` or a feature page. | https://developers.google.com/search/docs/appearance/structured-data/search-gallery | High for schema deliverables. | Schema reviewer |
| Ranking timing claim is official. | Update timing cites `g-ranking-history` without implying local causation. | https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history | High for audit reports. | Monitoring owner |
| Missing evidence is visible. | Gaps appear in [[Evidence Gap Register]] before release review. | Source-governance wiki notes. | Blocker when claim is release-critical. | Release owner |

## Evidence, Severity, Owner, And Fix Status

The gate should fail loudly when a source is absent, stale, too broad, or outside the platform named in the claim. The fix is not to pad the note. The fix is to either narrow the claim, add the correct source in the appropriate ledger path, or remove the claim from the release.

## Handoff Rules

1. Send source-date conflicts to [[Source Ledger Reading Guide]] and [[Evidence Gap Register]].
2. Send claim phrasing problems to [[Claim To Source Mapping]].
3. Send schema support questions to [[Blog Schema Stack]].
4. Send Google AI Search caveats to [[AI Citation Mechanics]].
5. Stop release-facing use when a gap is marked blocker.

## Gate Example For An Audit Release

A site audit draft blames a traffic drop on a confirmed core update.
`g-ranking-history` can confirm timing, not the site's cause.
The gate passes only after the claim is narrowed or property evidence appears.
If the report keeps causation language, the blocker remains open.
Another failure is hiding a missing source behind a confident severity label.
[[Full Site Blog Audit Report]] consumes the pass or fail decision.
Inputs provided: gate check, severity, fix owner, and source ID.
Expected output: release-ready finding or blocked audit note.

## Related

- [[Research Pack Index]]
- [[Claim To Source Mapping]]
- [[Evidence Gap Register]]
- [[Source Ledger Reading Guide]]
- [[Current Requirements Digest]]
