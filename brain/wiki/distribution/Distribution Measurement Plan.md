---
type: spoke
title: "Distribution Measurement Plan"
domain: "Blog Distribution"
status: active
created: 2026-07-06
updated: 2026-07-09
tags:
  - distribution
  - measurement
  - planning
  - active
confidence: advisory
related:
  - "[[Distribution and Repurposing]]"
  - "[[AI Referral Reporting]]"
  - "[[Google Data Integrations]]"
  - "[[Channel Asset Inventory]]"
  - "[[Zero Click Planning Baseline]]"
  - "[[AI Citation Mechanics]]"
  - "[[Canonical Attribution Rules]]"
  - "[[Blog Quality Score]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://sparktoro.com/blog/in-2026-less-than-one-third-of-google-searches-still-send-a-click/"
  - "https://developers.google.com/webmaster-tools/v1/searchanalytics/query"
  - "https://developers.google.com/analytics/devguides/reporting/data/v1"
  - "https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports"
---

# Distribution Measurement Plan

## Distribution Measurement Plan Planning Scope

Distribution Measurement Plan defines how a distributed blog post is measured after channel assets go live. It separates reach, clicks, engagement, citations, and owned audience actions because each signal answers a different operating question. The plan uses first-party property evidence when access exists, then labels market sources as context. `sparktoro-zero-click-2026` informs [[Zero Click Planning Baseline]], but it does not forecast a site's traffic.

### Inputs, Assumptions, And Constraints

Inputs include canonical URL, distribution dates, asset inventory, UTM or link conventions, GA4 engagement exports, Search Console query data, Search Console generative AI reports if available, and manual citation observations. Google helpful content guidance, `g-helpful-content`, matters when a metric would reward thin derivatives. The AI optimization guide and the June 2026 llms.txt clarification, `g-ai-opt-guide` and `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`, prevent measurement plans from counting completion of a non-required Google AI setup task.

### Decisions That Must Be Deferred

Defer ranking explanations, AI citation causality, and channel ROI until the evidence exists. A measurement owner may report that an asset coincided with referrals or impressions, but causation requires a stronger design than this advisory plan usually has. If the site lacks GSC or GA4 access, route the gap to [[Google Data Integrations]] instead of using a market average as a substitute.

## Distribution Measurement Plan Execution Table

| Phase | Input | Output | Owner | Evidence requirement | Follow-up action |
|---|---|---|---|---|---|
| Baseline | Canonical URL and pre-distribution date range | Starting clicks, sessions, and engagement | Analytics owner | `g-gsc-api`, `g-ga4-data` | Save export reference |
| Asset launch | Channel asset inventory and publication dates | Shipped asset list | Distribution lead | [[Channel Asset Inventory]] | Confirm canonical links |
| Reach review | Platform impressions, email sends, community views | Reach by channel | Channel owners | Platform export or manual note | Label non-comparable metrics |
| Search review | Queries, clicks, CTR, and impressions | Search movement summary | SEO owner | `g-gsc-api` | Compare to baseline window |
| AI feature review | Generative AI impressions or citation observations | AI visibility note | SEO owner | `g-genai-reports`, [[AI Citation Mechanics]] | Keep separate from referrals |
| Owned action review | Signups, return visits, replies, saves | Audience loop result | Content lead | `g-ga4-data`, [[Owned Audience Loop]] | Select next owned follow-up |
| Attribution QA | UTM rules, referrer buckets, and canonical URL key | Cleaned metric map | Analytics owner | `g-ga4-data`, [[Canonical Attribution Rules]] | Fix labels before interpretation |
| Retirement review | Asset result, cost, and evidence quality | Keep, revise, pause, or retire decision | Distribution lead | [[Channel Asset Inventory]] | Update row status and reason |

## Phase, Owner, Evidence, Output, And Review Date

Every measurement phase gets a review date before the asset is shipped. The default cadence is seven days for fast channels, thirty days for search and owned audience, and immediate correction for any inflated claim. A result can be "not measurable" if the data is missing; that is better than inventing a confidence level.

### Example: Reading A Launch Without Causation

After an email and thread go live, GA4 shows newsletter visits, GSC query clicks stay flat, and one assistant citation screenshot appears. The plan records the newsletter under `g-ga4-data`, leaves search movement neutral under `g-gsc-api`, and places the screenshot in the citation-observation bucket tied to [[AI Citation Mechanics]]. The decision can be "repeat email angle," but not "social caused Google AI visibility."

### Measurement Traps For Distributed Posts

This plan breaks when platform impressions are compared directly with GSC impressions, when a seven-day social window is merged with a thirty-day search window, or when unavailable GSC AI reports are turned into a zero result. It also breaks when private-community replies are counted as traffic without a stated observation method.

### Evidence Matrix Handoff

[[Google API Evidence Matrix]] consumes the measurement plan when property evidence is requested. It needs canonical URL key, date range, requested surface, credential tier, redacted export reference, and missing-data label; it expects accepted evidence rows or a blocked source state.

## Distribution Measurement Plan Operating Loop

1. Build a baseline from available first-party data and name missing sources.
2. Attach each distributed asset to the canonical post and launch date.
3. Read channel metrics in their own units before comparing across channels.
4. Separate AI referrals, Google AI feature reporting, and citation observations.
5. Convert the review into keep, revise, retire, or retest decisions.

## Source IDs Wired

This plan cites `g-helpful-content`, `g-ai-opt-guide`, `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`, `sparktoro-zero-click-2026`, `g-gsc-api`, `g-ga4-data`, and `g-genai-reports`.
