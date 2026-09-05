---
type: spoke
title: "Google Source Priority Ladder"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [sources, research-pack, active]
domain: "Source Evidence"
confidence: verified
related:
  - "[[Research Pack Index]]"
  - "[[Canon Notes Map]]"
  - "[[Source Confidence Labels]]"
  - "[[Claim To Source Mapping]]"
  - "[[Google Algorithm Update Ledger]]"
  - "[[Blog Schema Stack]]"
  - "[[AI Citation Mechanics]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history"
---

# Google Source Priority Ladder

## Authority Job For Google Claims

This spoke orders Google-owned sources by how close they are to the claim being made. It protects [[Claim To Source Mapping]] from using a convenient Google URL when a more specific Google page is required.

The ladder is about source fit. A high-quality source can still be the wrong source if the claim is about another surface, feature, date, or workflow. For example, `g-helpful-content` can support people-first content review, while `g-search-gallery` is the better starting point when the claim names a supported rich-result type.

## Decisions This Ladder Makes

- Which Google source family should be checked first.
- Whether a Search Central page is enough or the Search Status Dashboard is required.
- Whether a schema claim belongs in [[Blog Schema Stack]] or a gap entry.
- Whether a Google AI Search claim should stay inside [[AI Citation Mechanics]].

## Claims This Ladder Rejects

- Any ranking-impact claim based only on documentation that does not report a ranking event.
- Any rich-result claim based only on the general structured data introduction.
- Any Google AI Search claim generalized to non-Google assistants.
- Any "current requirement" claim without source ID, date, retrieval state, and refresh trigger.

## Google Source Priority Ladder Source Table

| Priority | Use this source ID first | URL | Best for | Do not use it for | Refresh trigger |
|---:|---|---|---|---|---|
| 1 | `g-ranking-history` | https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history | Confirmed ranking update names, rollout timing, and official incident history. | Diagnosing client traffic loss or proving update impact. | New dashboard incident or monthly monitoring review. |
| 2 | `g-search-gallery` | https://developers.google.com/search/docs/appearance/structured-data/search-gallery | Current Google-supported rich result types. | General schema validity or Schema.org vocabulary claims. | Search Gallery last-updated date changes. |
| 2.5 | `g-faqpage-sd` | https://developers.google.com/search/updates#deprecating-the-faq-rich-result-feature | FAQ rich-result retirement for Google Search. | Reviving FAQPage as a current rich-result tactic. | Search updates change. |
| 3 | `g-ai-opt-guide` | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide | Google Search AI feature optimization guidance. | Assistant-wide GEO claims or platform-agnostic citation forecasts. | AI optimization guide changes. |
| 4 | `g-helpful-content` | https://developers.google.com/search/docs/fundamentals/creating-helpful-content | Helpful, reliable, people-first content review and E-E-A-T framing. | A mechanical ranking checklist or page-level score guarantee. | Helpful content page changes or release review. |

## Source ID, URL, Date, Claim Coverage, And Limitation

The source ID is the citation handle. The URL is the location to inspect. The date tells reviewers whether the source was current during the claim review. Claim coverage states what the source can prove. Limitation states what must be downgraded, routed elsewhere, or rejected.

Use a separate structured-data implementation source only after `g-search-gallery` confirms that the target rich result type is actually supported by Google Search.

## Google Source Priority Ladder Refresh Procedure

1. For a ranking claim, check `g-ranking-history` before reading commentary or tool volatility reports.
2. For schema work, check `g-search-gallery`, then add an implementation source only when the claim needs syntax or property detail.
3. For AI Search work, check `g-ai-opt-guide`, then route non-Google claims to [[Evidence Gap Register]] unless another source exists.
4. For content-quality work, check `g-helpful-content` and keep the recommendation probabilistic.
5. If the highest-priority source does not cover the claim, lower the confidence label in [[Source Confidence Labels]].

## Ladder Choice Scenario

An audit says old FAQ schema should be restored for visibility.
Start with `g-search-gallery` to test current rich-result support.
Then use `g-faqpage-sd` for the retired FAQ feature state.
Do not downgrade to `g-intro-sd` because the page is easier to quote.
The common failure is source convenience beating claim fit.
[[Schema Generation Output Contract]] consumes this ladder decision.
Inputs provided: selected source family and rejected fallback source.
Expected output: schema rationale, warning, or blocked request.

## Related

- [[Research Pack Index]]
- [[Canon Notes Map]]
- [[Source Confidence Labels]]
- [[Claim To Source Mapping]]
- [[Google Algorithm Update Ledger]]
- [[Blog Schema Stack]]
- [[AI Citation Mechanics]]
