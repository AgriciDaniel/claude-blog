---
type: spoke
title: "Source Refresh Cadence"
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
  - "[[Google Algorithm Update Ledger]]"
  - "[[Current Requirements Digest]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history"
---

# Source Refresh Cadence

## Refresh Cadence Job

This spoke decides how often the source pack must be checked and what kind of event forces an immediate refresh. It is a schedule, not a source summary. Each row names the source ID, the claim family it protects, and the owner who must act when the source changes.

The default is monthly for Google Search documentation and ranking history, before every release for claim maps, and immediately when an official changelog or dashboard changes a source used in current guidance.

## Source Groups This Note Owns

- Google Search fundamentals used for blog content advice.
- Google AI Search guidance used in [[AI Citation Mechanics]].
- Search Gallery checks used by schema notes.
- Ranking history checks used by [[Google Algorithm Update Ledger]].

## Claims This Note Must Not Validate Alone

This cadence does not prove that a source is still correct. It only tells the reviewer when to check. The actual claim review still happens in [[Claim To Source Mapping]], [[Current Requirements Digest]], or the canonical hub that owns the claim.

## Source Refresh Cadence Source Table

| Source ID | URL | Last ledger date | Claim coverage | Limitation | Refresh cadence |
|---|---|---:|---|---|---|
| `g-helpful-content` | https://developers.google.com/search/docs/fundamentals/creating-helpful-content | 2025-12-10 | People-first content and E-E-A-T framing. | Not a ranking guarantee or page score. | Monthly, before content-policy release, and after Search Central updates. |
| `g-ai-opt-guide` | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide | 2026-06-15 | Google Search AI feature guidance. | Does not cover non-Google assistants. | Monthly and immediately after AI Search docs changes. |
| `g-search-gallery` | https://developers.google.com/search/docs/appearance/structured-data/search-gallery | 2026-07-01 | Supported Google rich-result types. | Does not validate arbitrary Schema.org markup. | Before schema recommendations and after gallery updates. |
| `g-ranking-history` | https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history | 2026-06-24 | Confirmed ranking events and rollout state. | Does not explain site-specific performance changes. | Weekly during active rollout, monthly otherwise. |
| `g-faqpage-sd` | https://developers.google.com/search/updates#deprecating-the-faq-rich-result-feature | 2026-07-09 | FAQ rich-result retirement state. | Does not judge visible Q and A usefulness. | Before schema releases and on Search updates. |
| `g-genai-reports` | https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports | 2026-07-08 | Search Console generative-AI reporting scope. | Does not guarantee access for every property. | Monthly until rollout stabilizes. |

## Source ID, URL, Date, Claim Coverage, And Limitation

Refresh work starts from the source ID because that is what body citations and claim tables reference. The URL and date protect against stale copies. Claim coverage and limitation prevent the refresh from expanding into unsupported advice.

## Source Refresh Cadence Procedure

1. Sort the active source IDs by cadence: immediate, release-time, monthly, or dormant.
2. Check the live source date against the ledger date without editing references in this slice.
3. If the source changed, update only in-scope wiki notes and record a gap for machine-ledger work.
4. If the source did not change, record no new claim and leave the existing source ID intact.
5. Escalate any changed ranking source to [[Google Algorithm Update Ledger]] and any schema source to [[Blog Schema Stack]].

## Cadence Scenario During A Rollout

Google ranking history shows an active update window under `g-ranking-history`.
Switch that source to weekly checks until completion appears.
Do not rewrite client decay notes from timing alone.
Use `g-gsc-api` only when property exports support the local pattern.
The failure mode is missing a dashboard completion date.
Another failure is treating monthly cadence as safe during rollout.
[[Content Decay Triage Register]] consumes the refresh state.
Inputs provided: source ID, cadence tier, changed date, and escalation owner.
Expected output: triage annotation or delayed recommendation.

## Related

- [[Research Pack Index]]
- [[Claim To Source Mapping]]
- [[Evidence Gap Register]]
- [[Google Algorithm Update Ledger]]
- [[Current Requirements Digest]]
