---
type: spoke
title: "Claim To Source Mapping"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [sources, research-pack, active]
domain: "Source Evidence"
confidence: verified
related:
  - "[[Research Pack Index]]"
  - "[[Source Confidence Labels]]"
  - "[[Evidence Gap Register]]"
  - "[[Current Requirements Digest]]"
  - "[[Claim Verification Flow]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history"
---

# Claim To Source Mapping

## Claim To Source Mapping Evidence Job

This spoke is the release-review surface for wiki claims. It maps a claim to the source ID that can actually support it, then records the limitation that prevents the claim from being overstated.

Use this note before a claim appears in a blog brief, audit, quality score, schema review, AI-citation recommendation, or update-memory note. A claim can still be useful when evidence is advisory, but it must not be marked verified unless the source directly covers the wording, date, and surface.

## Source Types This Note Owns

- Official Google Search documentation for content, AI Search, and structured data.
- Google ranking history for confirmed update events.
- Claim-level confidence and verdict routing through [[Source Confidence Labels]].
- Gap handoff when a real source is missing from the machine ledger.

## Claims This Note Must Not Validate Alone

- Client-specific traffic loss, revenue impact, or conversion movement.
- Any study result reported by a third party without sample and method caveats.
- Google rich-result eligibility when only the general structured data page is cited.
- Non-Google assistant citation behavior when the source is a Google Search page.

## Claim To Source Mapping Source Table

| Claim pattern | Canonical note | Source ID | URL | Date checked | Claim coverage | Limitation |
|---|---|---|---|---:|---|---|
| People-first blog review should evaluate usefulness, trust, and reader value before optimization tactics. | [[E-E-A-T for Blog Content]] | `g-helpful-content` | https://developers.google.com/search/docs/fundamentals/creating-helpful-content | retrieved 2026-07-09 | Supports content self-review and E-E-A-T framing. | Does not guarantee ranking improvement. |
| Google Search AI guidance does not require special AI-only files or markup. | [[AI Citation Mechanics]] | `g-ai-opt-guide` | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide | retrieved 2026-07-08 | Supports Google Search AI feature guidance. | Does not prove behavior for non-Google assistants. |
| A supported rich-result type must appear in Google's Search Gallery before it is recommended as a Google visual result tactic. | [[Blog Schema Stack]] | `g-search-gallery` | https://developers.google.com/search/docs/appearance/structured-data/search-gallery | retrieved 2026-07-08 | Supports current Google rich-result inventory checks. | Does not validate every Schema.org property. |
| Confirmed ranking update status must come from Google's ranking history. | [[Google Algorithm Update Ledger]] | `g-ranking-history` | https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history | retrieved 2026-07-09 | Supports official update names and rollout history. | Does not diagnose a site's cause of change. |
| FAQPage markup should not be sold as a current Google FAQ rich-result tactic. | [[Blog Schema Stack]] | `g-faqpage-sd` | https://developers.google.com/search/updates#deprecating-the-faq-rich-result-feature | retrieved 2026-07-09 | Supports FAQ rich-result retirement for Google Search. | Visible Q and A may still serve readers. |
| llms.txt should not be presented as a Google Search visibility control. | [[llms.txt Caveat Note]] | `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide | retrieved 2026-07-06 | Supports the Google Search llms.txt clarification. | Other crawlers need separate evidence. |

## Source ID, URL, Date, Claim Coverage, And Limitation

The source ID is required in the table because downstream notes cite IDs, not generic URLs. The limitation column is just as important as the evidence column: it marks where the claim must stop or downgrade.

## Claim To Source Mapping Refresh Procedure

1. Draft the exact claim and remove vague verbs such as "proves" unless the source truly proves it.
2. Choose the narrowest source ID that covers the claim.
3. Add URL, date checked, claim coverage, and limitation in one row.
4. Assign the label in [[Source Confidence Labels]] using the weakest required evidence.
5. Move unsupported or stale claims to [[Evidence Gap Register]] before release use.

## Claim Row Rewrite Case

Before: "Add FAQPage schema to earn Google FAQ rich results."
After: "Do not recommend FAQPage as a Google FAQ rich-result tactic."
The corrected claim cites `g-faqpage-sd` and keeps reader value separate.
The row fails if the limitation says all Q and A content is useless.
Another failure is using `g-intro-sd` for the retired feature claim.
[[Factcheck Claim Register]] consumes completed mapping rows.
Inputs provided: exact claim, source ID, verdict, and limitation.
Expected output: verified register item or blocked unsupported claim.

## Related

- [[Research Pack Index]]
- [[Source Confidence Labels]]
- [[Evidence Gap Register]]
- [[Current Requirements Digest]]
- [[Claim Verification Flow]]
