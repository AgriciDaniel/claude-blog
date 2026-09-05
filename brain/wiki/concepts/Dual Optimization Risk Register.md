---
type: spoke
title: "Dual Optimization Risk Register"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [dual-optimization, evergreen]
domain: "Blog Content Optimization"
confidence: advisory
related:
  - "[[Dual Optimization]]"
  - "[[index|Index]]"
  - "[[hot|Hot]]"
  - "[[Search Visibility Versus Citation Exposure]]"
  - "[[Zero Click Planning Baseline]]"
  - "[[AI Overview CTR Interpretation]]"
  - "[[AI Mode Query Share Context]]"
  - "[[Citation Readiness Decision Tree]]"
  - "[[Reader Value Versus Extraction Value]]"
  - "[[Dual Optimization Briefing Checklist]]"
  - "[[Classic SEO And GEO Tradeoffs]]"
  - "[[6-Pillar Dual Optimization]]"
source_urls:
  - "https://sparktoro.com/blog/in-2026-less-than-one-third-of-google-searches-still-send-a-click/"
  - "https://www.seerinteractive.com/insights/aio-impact-on-google-ctr-2026-update"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://developers.google.com/search/docs/appearance/ai-features"
  - "https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports"
---
# Dual Optimization Risk Register

## Register Purpose

This register captures dual-optimization recommendations that could mislead stakeholders, become stale, or move outside the advisory boundary. It records the risk before a brief, audit, or strategy blueprint turns uncertainty into action. Use [[AI Citation Mechanics]] and [[2026 Google Update Timeline]] for broad evidence context instead of storing repeated statistic blocks here.

### Risk Entry Inputs

- Content unit, recommendation text, affected surface, and business decision.
- Source IDs, evidence tier, owner, review date, and confidence label.
- Observable rollback cue, such as engagement decline or contradictory property data.
- Boundary note when a recommendation approaches publishing or platform mutation.

## Dual Optimization Risk Register Table

| Risk entry | Trigger | Source IDs | Severity | Owner | Rollback or correction |
|---|---|---|---|---|---|
| AI inclusion guarantee | Recommendation promises AIO or AI Mode placement | `g-ai-features`, `g-ai-opt-guide` | blocker | GEO owner | Replace promise with eligibility language |
| Market data overreach | External study used as site forecast | `sparktoro-zero-click-2026`, `seer-aio-impact-ctr-2026` | major | Analyst | Re-run with property evidence or caveat |
| Unsupported AI file task | `llms.txt` requested for Google visibility | `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` | blocker | Technical SEO | Remove task from Search plan |
| Tool authority claim | Vendor score treated as Google ranking access | `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` | major | SEO lead | Rephrase as external estimate |
| Stale update reference | Ranking-update claim lacks confirmed date | `g-ranking-history` | major | Researcher | Route to [[2026 Google Update Timeline]] |
| Reader harm from snippets | Passage becomes awkward or under-caveated | `g-helpful-content`, `ziptie-aio-source-selection` | major | Editor | Revert to reader-first copy |

## Register Example: Rejecting A Visibility Shortcut

An audit asks for an `llms.txt` implementation to improve Google AI visibility. The register marks the item blocker, cites `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`, and sends the recommendation back as a non-Google experiment rather than a Search deliverable.

[[Full Site Blog Audit Report]] consumes this register for its priority queue. It needs risk entry, affected URL or cluster, source IDs, severity, owner, and rollback cue; it expects an action card marked fix, monitor, defer, or remove.

## Register-Specific Edge Cases

- A risk without an owner should stay unapproved because no one can refresh `g-ranking-history` or `g-ai-features`.
- A market-study risk can be downgraded only when matching property data exists under `g-gsc-api`.
- A blocked recommendation should not be softened into a minor note when `g-ai-opt-guide` rejects the premise.
- A reader-harm risk should remain open until the article passes [[Reader Value Versus Extraction Value]] with source proximity intact.

## Review Cadence

1. Reopen high-severity entries after Google AI guidance changes.
2. Reopen market-data entries when first-party reporting becomes available.
3. Reopen passage risks after major rewrites or source substitutions.
4. Move resolved entries into the consuming deliverable with the correction noted.

## Related
- [[Dual Optimization]]
- [[AI Citation Mechanics]]
- [[Search Visibility Versus Citation Exposure]]
- [[Reader Value Versus Extraction Value]]
- [[Dual Optimization Briefing Checklist]]
- [[Market Average Versus First Party Data]]
