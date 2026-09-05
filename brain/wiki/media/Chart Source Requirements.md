---
type: spoke
title: "Chart Source Requirements"
domain: "Blog Media"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [media, images, audio, charts, active]
---

# Chart Source Requirements

## Chart Source Requirements Evidence Job

Chart Source Requirements decides whether a chart has enough provenance to appear in a blog post. It does not bless the design of the chart, which belongs to [[Data Visualization Review]]. It also does not validate broad SEO market claims by itself. The chart must expose the data source, date range, retrieval date, method note, transformation, and claim sentence before a designer starts styling it.

This note uses `g-helpful-content` for people-first evidence discipline, `nng-editorial-heuristics` for review ergonomics, `g-ai-opt-guide` for avoiding special AI-only presentation claims, and `schema-full` for vocabulary context where a chart is described as an image or dataset-like creative work. If the chart claim is market research, use claim-ledger verdicts such as CONFIRMED, AS-REPORTED, SINGLE-SOURCE, or CONTESTED before drafting.

### Source Types This Note Owns

- Primary export: first-party GSC, GA4, CRM, sales, survey, or product data.
- Official source: platform documentation, changelog, regulator, standards body.
- Practitioner study: vendor or industry research with stated method limits.
- Manual observation: screenshot or logged example with date, query, locale, and device.

## Chart Source Requirements Source Table

| Source ID | URL | Date in ledger | Claim coverage | Limitation | Refresh cadence |
|---|---|---|---|---|---|
| `g-helpful-content` | https://developers.google.com/search/docs/fundamentals/creating-helpful-content | last updated 2025-12-10, verified 2026-07-09 | People-first content and self-assessment discipline | Does not validate chart data | Monthly or source change |
| `nng-editorial-heuristics` | https://www.nngroup.com/articles/ten-usability-heuristics/ | last updated 2020, verified 2026-07-06 | Review usability adapted as editorial ergonomics | Heuristic source, not SEO evidence | Quarterly or methodology change |
| `g-ai-opt-guide` | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide | last updated 2026-06-15, verified 2026-07-08 | Google AI features do not need special AI files or markup | Not chart methodology guidance | Monthly while AI docs move |
| `schema-full` | https://schema.org/docs/full.html | retrieved 2026-07-09, no page date exposed | Vocabulary route for asset description | Standards vocabulary is not Google eligibility | Monthly ledger check |
| `g-google-images` | https://developers.google.com/search/docs/appearance/google-images | last updated 2026-03-02, verified 2026-07-09 | Image context for chart files, alt text, and sitemaps | Does not prove the underlying values | Monthly or image-doc change |
| `g-intro-sd` | https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data | last updated 2025-12-10, verified 2026-07-09 | Visible-content guardrail for structured data | Does not create chart eligibility | Monthly ledger check |

## Claims This Note Must Not Validate Alone

Do not use this note as proof that a market average applies to a client site. Do not treat an SEO tool chart as a Google ranking fact. Do not infer causality from a before-after chart unless the method supports it. Do not cite a screenshot without query, locale, date, and device. Route broad AI visibility or zero-click context to [[AI Citation Mechanics]] instead of repeating a statistic in every chart note.

## Traffic Drop Chart Packet

A draft chart compares organic sessions before and after a content refresh.
Before approval, it shows two bars but no export date or filters.
The packet is blocked because `g-helpful-content` requires reliable sourcing discipline.
The repaired packet names GA4 property, date range, channel filter, and owner.
It marks the claim as AS-REPORTED when only one export supports it.
The caption says "sessions in this property," not "Google traffic recovered."
If the chart becomes an image, `g-google-images` governs alt and context.
If schema is requested, `g-intro-sd` requires visible page agreement.

## Chart Source Edge Cases

- A GSC export with thresholded rows cannot prove missing-query volume.
- A vendor index cannot stand in for a client's first-party trend.
- A screenshot without query, device, locale, and date stays unusable.
- A percent-change chart needs the denominator, not only the delta.
- A refreshed article must recheck old chart retrieval dates.

## Chart Source Requirements Refresh Procedure

1. Open the original data source and record the retrieval date.
2. Capture the exact date range, filters, sample, geography, device, and transformation.
3. Write the chart claim in one sentence, then mark its verdict using the claim-ledger discipline.
4. Add the source ID or create a source gap in [[Research Pack Index]] before publication.
5. Recheck the source when the article refreshes, the source document changes, or the chart becomes a distribution asset.

## Chart Source Requirements Handoff

Pass the chart to design only when the table above is complete for the actual data source, not merely for these operating references. Block charts with orphaned percentages, missing axes, untraceable screenshots, or decorative visuals that make the article look evidenced without carrying evidence.

## Specification Wire

[[Blog Chart Specification]] consumes the approved chart packet.
It needs source ID, retrieval date, owner, filters, caveat, and claim verdict.
It returns chart type, accessibility approach, placement, and pass-revise-block status.
`nng-editorial-heuristics` supports review ergonomics, not SEO proof.
