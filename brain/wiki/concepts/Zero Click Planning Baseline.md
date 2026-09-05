---
type: spoke
title: "Zero Click Planning Baseline"
domain: "Blog Content Optimization"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [dual-optimization, zero-click, planning]
confidence: advisory
related:
  - "[[Dual Optimization]]"
  - "[[AI Citation Mechanics]]"
  - "[[Citation And Click Forecasting]]"
  - "[[Visibility Metrics For Blog Programs]]"
source_urls:
  - "https://sparktoro.com/blog/in-2026-less-than-one-third-of-google-searches-still-send-a-click/"
  - "https://www.pewresearch.org/short-reads/2025/07/22/google-users-are-less-likely-to-click-on-links-when-an-ai-summary-appears-in-the-results/"
  - "https://www.seerinteractive.com/insights/aio-impact-on-google-ctr-2026-update"
  - "https://developers.google.com/search/docs/appearance/ai-features"
---
# Zero Click Planning Baseline

## Zero Click Planning Baseline Planning Scope

This note establishes the planning baseline for searches that may not produce a visit. It is the first stop before a forecast, not the final forecast. The key source is `sparktoro-zero-click-2026`, which the claim ledger treats as `AS-REPORTED` market panel evidence for early 2026 US Google behavior. Use [[AI Citation Mechanics]] for the canonical statistic summary and [[Citation And Click Forecasting]] before turning this baseline into numbers.

Pew's AI-summary click research (`pew-ai`) and Seer's AIO CTR study (`seer-aio-impact-ctr-2026`) support the broader planning point that answer surfaces can change click behavior, but they do not prove a single universal rate. Google AI feature documentation (`g-ai-features`) supplies the official participation boundary, not a traffic estimate.

### Inputs, Assumptions, And Constraints

- Geography, device mix, page type, and query intent for the planned content.
- Whether the program has first-party click and impression data.
- Whether the value model includes non-click outcomes such as brand recall, assisted conversion, or citation presence.
- The source-ledger refresh date for every market claim used in the baseline.

### Decisions That Must Be Deferred

- Exact traffic lift without first-party evidence.
- Guaranteed AIO or AI Mode inclusion.
- Any claim that AI visibility can be forced by an unsupported technical file.

## Zero Click Planning Baseline Execution Table

| Phase | Inputs | Output | Owner | Evidence requirement | Follow-up action |
|---|---|---|---|---|---|
| Baseline frame | Query group and current click data | Zero-click caveat for the brief | Strategist | `sparktoro-zero-click-2026` | Decide whether market context is enough |
| AI summary check | AIO presence or likely trigger class | Click-risk note | Analyst | `pew-ai`, `seer-aio-impact-ctr-2026` | Route contested CTR claims to [[AI Overview CTR Interpretation]] |
| Eligibility review | Crawl, index, and preview controls | Technical blocker list | Technical reviewer | `g-ai-features` | Fix blockers before forecasting citation value |
| Value model | Non-click goals and observed conversions | Measurement lane split | Program owner | First-party data when available | Send dashboard terms to [[Visibility Metrics For Blog Programs]] |
| Property override | GSC and analytics show the site's own click pattern | Observed baseline update | Analyst | `g-gsc-api`, `g-ga4-data` | Downgrade market context to a caveat |
| AI Mode proportionality | Product news, query share, and page intent | Priority note for the brief | Strategy lead | `blog-io2026`, `sparktoro-zero-click-2026` | Route AI Mode weighting to [[AI Mode Query Share Context]] |

## Baseline Example For A Stakeholder Brief

A stakeholder expects top rankings to return historical traffic. The baseline says market click scarcity is context from `sparktoro-zero-click-2026`, not a property forecast, then asks for GSC and GA4 evidence under `g-gsc-api` and `g-ga4-data` before any traffic range is approved.

[[Content Brief Output Contract]] consumes this note before outline work. It needs query group, locale, click evidence, non-click goals, and source IDs; it expects a zero-click caveat plus a measurement lane split.

## Baseline-Specific Failure Modes

- A US market panel from `sparktoro-zero-click-2026` should not be used as a global rate without locale review.
- A branded query can behave differently from generic research demand, so pull query-level evidence through `g-gsc-api`.
- An AI summary risk note should not become an AIO traffic forecast without `seer-aio-impact-ctr-2026` caveats.
- A non-click goal needs an owner, or the baseline hides uncertainty instead of making it measurable.

## Phase, Owner, Evidence, Output, And Review Date

Each baseline must name the owner, evidence IDs, output artifact, and next review date. If the source is a market panel, the confidence stays advisory. If the source is property data, the owner may upgrade the decision language but still cannot promise rankings, clicks, or AI citation.

## Zero Click Planning Baseline Operating Loop

1. Start with the content unit and query group.
2. Add the market zero-click caveat in plain language.
3. Check whether first-party data changes the baseline.
4. Split click and non-click value before forecast work begins.
5. Refresh the baseline when the source ledger or property reporting changes.
