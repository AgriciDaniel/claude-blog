---
type: spoke
title: "Repurposing Source Fidelity"
domain: "Blog Distribution"
status: active
created: 2026-07-06
updated: 2026-07-09
tags:
  - distribution
  - source-fidelity
  - factcheck
  - active
confidence: advisory
related:
  - "[[Distribution and Repurposing]]"
  - "[[Canonical Attribution Rules]]"
  - "[[Channel Asset Inventory]]"
  - "[[AI Citation Mechanics]]"
  - "[[Zero Click Planning Baseline]]"
  - "[[2026 Google Update Timeline]]"
  - "[[E-E-A-T for Blog Content]]"
  - "[[Research Pack Index]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://sparktoro.com/blog/in-2026-less-than-one-third-of-google-searches-still-send-a-click/"
  - "https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links"
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
  - "https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports"
  - "https://developers.google.com/search/docs/fundamentals/third-party-seo"
---

# Repurposing Source Fidelity

## Repurposing Source Fidelity Evidence Job

Repurposing Source Fidelity is the evidence gate for taking facts, dates, source context, and caveats out of a blog post and into another channel. Its output is a claim-level source map, not a copy deck. A derivative asset can be short, but it still needs to preserve what the evidence says and what the evidence does not say.

### Source Types This Note Owns

This note owns official Google guidance, source-ledger IDs, original article source blocks, claim-ledger verdicts, and dated market studies used inside derivative assets. `g-helpful-content` anchors source-backed usefulness. `g-qrg-full` supports trust-sensitive review. AI setup caveats cite `g-ai-opt-guide` and `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`; the dated update belongs in [[2026 Google Update Timeline]].

### Claims This Note Must Not Validate Alone

Do not validate ranking effects, AI citation probability, or traffic forecasts from a distribution asset alone. SparkToro's clickstream study, `sparktoro-zero-click-2026`, is useful context for [[Zero Click Planning Baseline]], but this note only checks whether the claim is carried accurately. It does not prove a thread, email, or video caused a change in search behavior.

## Repurposing Source Fidelity Source Table

| Source ID | URL owner | Date context | Claim coverage | Limitation | Refresh cadence |
|---|---|---|---|---|---|
| `g-helpful-content` | Google Search Central | Last updated 2025-12-10, retrieved 2026-07-09 | People-first and self-assessment framing | Does not score a specific asset | Monthly source-ledger check |
| `g-ai-opt-guide` | Google Search Central | Updated 2026-06-15, retrieved 2026-07-08 | No special Google AI files or schema requirement | Applies to Google Search features, not every assistant | Refresh with AI guidance changes |
| `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` | Google update ledger | Update dated 2026-06-15 | llms.txt has no Google Search visibility effect | Does not govern non-Google crawlers | Review through [[2026 Google Update Timeline]] |
| `sparktoro-zero-click-2026` | SparkToro study | Published 2026-06-08 | Click scarcity planning context | Practitioner panel, not site forecast | Refresh when market pack updates |
| `g-qualify-links` | Google Search Central | Last updated 2025-12-10 | Link qualification for paid, UGC, and nofollow cases | Markup control may sit outside the team | Monthly source-ledger check |
| `g-qrg-full` | Google rater guidelines PDF | Published 2025-09-11 | Trust review context for sensitive claims | Rater guidelines are not direct ranking-factor proof | Refresh when QRG changes |
| `g-genai-reports` | Google Search Central | Published 2026-06-03 | Search Console AI feature reporting availability | Reporting source, not future visibility proof | Refresh with GSC report changes |
| `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` | Google Search Central | Update dated 2026-06-05 | Third-party SEO tools lack Google's internal ranking data | Does not invalidate all external metrics | Review when tool claims change |

## Source ID, URL, Date, Claim Coverage, And Limitation

The reviewer should preserve the smallest accurate claim. If a channel format cannot carry the caveat, the claim should be narrowed or removed. If a source has a practitioner verdict, keep that label visible in draft notes. If a source ID is missing from the ledger, pause the adaptation and route research to [[Research Pack Index]] instead of inventing a citation.

### Example: Compressing A Tool Screenshot Claim

A social post draft says a vendor dashboard "proves Google rewarded the article." The fidelity pass rewrites it as an observed third-party metric, points the ranking-system caveat to `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice`, and keeps any Google AI reporting line separate under `g-genai-reports`. If the caveat will not fit the thread, the claim is removed rather than squeezed.

### Fidelity Breakpoints

This note fails when a claim keeps its number but loses the date, when "as reported" turns into "confirmed by Google," or when an AI citation screenshot is copied without query wording. It also fails when `sparktoro-zero-click-2026` is reused as a client forecast instead of market context routed to [[Zero Click Planning Baseline]].

### Claim Register Output

[[Factcheck Claim Register]] consumes fidelity decisions for repurposed claims. It needs claim text, source ID, evidence tier, verdict label, limitation, refresh date, and owner; it expects a verified, pending, or blocked register row before the claim enters a channel asset.

## Repurposing Source Fidelity Refresh Procedure

1. Extract all claims that will leave the canonical post.
2. Assign each claim a source ID, date, verdict posture, and limitation.
3. Compare the derivative wording against the original claim scope.
4. Remove claims whose caveats cannot fit the channel.
5. Recheck source freshness before a repeated asset is reused in a later campaign.

## Source IDs Wired

Repurposing Source Fidelity wires `g-helpful-content`, `g-ai-opt-guide`, `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`, `sparktoro-zero-click-2026`, `g-qualify-links`, `g-qrg-full`, `g-genai-reports`, and `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice`.
