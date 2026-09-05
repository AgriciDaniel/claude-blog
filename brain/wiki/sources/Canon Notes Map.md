---
type: spoke
title: "Canon Notes Map"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [sources, research-pack, active]
domain: "Source Evidence"
confidence: verified
related:
  - "[[Research Pack Index]]"
  - "[[Google Source Priority Ladder]]"
  - "[[Claim To Source Mapping]]"
  - "[[Current Requirements Digest]]"
  - "[[AI Citation Mechanics]]"
  - "[[Blog Schema Stack]]"
  - "[[E-E-A-T for Blog Content]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
---

# Canon Notes Map

## Canon Notes Map Evidence Job

This note maps canonical wiki hubs to the primary source families that should be opened before a writer makes a blog SEO, schema, or Google AI Search recommendation. It is a routing layer for [[Research Pack Index]], not a place to prove every downstream claim.

Use this map when a brief, audit, or rewrite asks which hub owns the source trail. The rule is simple: start with the Google or standards source that directly governs the claim, then use sibling notes for local interpretation. A canon note can summarize evidence, but the claim still needs a source ID from `references/source-ledger.json`.

## Source Types This Note Owns

- People-first content and E-E-A-T routing through `g-helpful-content`.
- General structured data routing through `g-intro-sd`.
- Google generative AI Search routing through `g-ai-opt-guide` and the llms.txt clarification entry `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`.
- Canon handoff to [[Claim To Source Mapping]] when the claim will appear in a deliverable.

## Claims This Note Must Not Validate Alone

- Ranking volatility, rollout duration, or algorithm impact. Send those to [[Google Algorithm Update Ledger]].
- Rich result eligibility beyond the general structured data introduction. Send those to [[Blog Schema Stack]] and current feature documentation.
- Non-Google assistant behavior. Google Search documentation does not prove ChatGPT, Perplexity, Copilot, or Gemini app citation behavior.

## Canon Notes Map Source Table

| Canon route | Source ID | URL | Date in ledger | Claim coverage | Limitation | Refresh cadence |
|---|---|---|---:|---|---|---|
| [[E-E-A-T for Blog Content]] | `g-helpful-content` | https://developers.google.com/search/docs/fundamentals/creating-helpful-content | last updated 2025-12-10, retrieved 2026-07-09 | People-first content self-review and E-E-A-T framing for Search-facing blog work. | Does not score a page, promise rankings, or replace human editorial review. | Monthly and before release. |
| [[Blog Schema Stack]] | `g-intro-sd` | https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data | last updated 2025-12-10, retrieved 2026-07-09 | General structured data concepts, JSON-LD preference, and eligibility framing. | Does not say a specific rich result is available for a blog page. | Before schema changes. |
| [[Blog Schema Stack]] | `g-search-gallery` | https://developers.google.com/search/docs/appearance/structured-data/search-gallery | last updated 2026-07-01, retrieved 2026-07-08 | Current Google-supported rich-result inventory. | Does not validate every Schema.org property or page implementation. | Before rich-result claims. |
| [[AI Citation Mechanics]] | `g-ai-opt-guide` | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide | last updated 2026-06-15, retrieved 2026-07-08 | Google Search AI feature guidance and the absence of special AI-only requirements. | Google Search only. It is not evidence for non-Google assistants. | On Google Search documentation change. |
| [[llms.txt Caveat Note]] | `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide | last updated 2026-06-15, retrieved 2026-07-06 | Treat llms.txt as unused by Google Search visibility systems. | Does not forbid maintaining the file for other crawlers or tools. | On AI optimization guide update. |
| [[Google Algorithm Update Ledger]] | `g-ranking-history` | https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history | last updated 2026-06-24, retrieved 2026-07-09 | Official ranking-update names and rollout states. | Does not explain a site's traffic movement. | Weekly during rollouts. |

## Source ID, URL, Date, Claim Coverage, And Limitation

When a writer chooses a canon note, carry over the source ID and date from the table, not just the note title. If a downstream note needs a stronger source than this map provides, the stronger source must appear in [[Claim To Source Mapping]]. If the source page date conflicts with the machine ledger, open [[Evidence Gap Register]] before using the claim in release material.

## Canon Notes Map Refresh Procedure

1. Open `references/source-ledger.json` and confirm that each source ID in the table still exists.
2. Compare the ledger date with the live-source date already recorded in the relevant canon note.
3. Update this map only when the routing decision changes, not when a downstream prose example changes.
4. Send missing IDs, date conflicts, or overbroad canon claims to [[Evidence Gap Register]].
5. Keep Google AI Search claims linked to [[AI Citation Mechanics]] and schema claims linked to [[Blog Schema Stack]].

## Canon Route Worked Case

A brief asks whether a SaaS comparison post needs an AI citation section.
Route usefulness language to [[E-E-A-T for Blog Content]] through `g-helpful-content`.
Route Google AI wording to [[AI Citation Mechanics]] through `g-ai-opt-guide`.
Do not let the brief promise assistant citations from a section format.
That promise exceeds Google Search guidance and becomes a gap.
Route collisions are the main failure mode here.
The shared AI guide URL carries different claim roles for two source IDs.
[[Content Brief Output Contract]] consumes the selected canon route.
Inputs provided: canon note, source ID, date, and limitation.
Expected output: approved evidence pack or an evidence-gap ticket.

## Related

- [[Research Pack Index]]
- [[Google Source Priority Ladder]]
- [[Claim To Source Mapping]]
- [[Current Requirements Digest]]
- [[AI Citation Mechanics]]
- [[Blog Schema Stack]]
- [[E-E-A-T for Blog Content]]
