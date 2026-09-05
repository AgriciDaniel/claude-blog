---
type: spoke
title: "AI Overview Citation Review"
domain: "GEO and AEO"
status: evergreen
created: 2026-07-06
updated: 2026-07-10
tags: [geo-aeo, ai-citation, evergreen]
---

# AI Overview Citation Review

## AI Overview Citation Review Surface Scope

This note reviews a page against the observed or expected AI Overview surface for a query class. The purpose is to decide whether the answer passage, nearby source, and entity naming are strong enough to include in an editorial or GEO audit. It does not claim that a passage can cause an AI Overview citation.

The evidence base is intentionally mixed. `g-ai-features` documents how Google frames AI features and preview controls. `seer-aio-impact-ctr-2026`, `pew-ai`, and `ahrefs-aio` are market or practitioner studies that report different click effects when AI summaries appear. The claim ledger treats the overall CTR effect as CONTESTED, so this note should compare sources and then prefer first-party evidence whenever the site has it. `semrush-aio` may be used only as extra practitioner context about AI Overview prevalence and composition.

### Queries This Review Accepts

Use this note for search results where an AI Overview is visible, likely, or strategically important. If the task is a follow-up conversation, use [[AI Mode Citation Review]] instead.

### Claims This Review Rejects

Reject universal CTR-loss percentages, guaranteed citation value, or recommendations that treat any third-party study as Google's own ranking guidance.

## AI Overview Citation Review Evidence Table

| Review question | Accepted evidence | Source IDs | Confidence posture | Owner | Decision use |
|---|---|---|---|---|---|
| Does the surface exist for this query? | Screenshot, date, locale, device, query | `g-ai-features` | Official feature context only | Analyst | Establish the review lane |
| Is the page cited or adjacent? | Cited URL, cited domain, visible answer text | `seer-aio-impact-ctr-2026` | AS-REPORTED citation association | GEO reviewer | Prioritize passage inspection |
| How should clicks be interpreted? | GSC data, AIO presence, control query | `pew-ai`, `ahrefs-aio` | CONTESTED market evidence | Analyst | Avoid single-number forecasts |
| Is the topic AIO-prone? | Query class and SERP sample | `semrush-aio` | Practitioner context | Strategist | Decide whether to broaden sampling |
| Is the cited claim fresh? | Source date, page update date, claim date, and article source IDs | `g-ai-features` plus article source IDs | Official feature context plus cited-source provenance | Analyst | Mark stale or current before rewrite |
| Are previews limiting display? | Rendered meta robots and snippet rule | `g-ai-features`, `g-ai-opt-guide` | Official preview-control guidance | Technical SEO | Route to [[AI Feature Preview Controls]] |

## AI Overview Citation Review Procedure

1. Save the query, date, locale, device, and whether an AI Overview appears.
2. Capture the cited URLs without assuming the top organic result is the cited source.
3. Compare the answer passage against entity clarity, source proximity, and freshness.
4. Label CTR claims as property data, AS-REPORTED study data, or unknown.
5. Route passage fixes to [[Answer Block Extraction Test]] before adding work to a brief.

## Observed AIO Scenario

A product comparison query shows an AI Overview on desktop for the US locale. The observed answer cites a competitor page, while the reviewed page ranks organically but is not cited. `g-ai-features` supports recording the Search feature context, but it does not support saying the competitor was selected because of one visible passage trait.

The reviewed page has a statistics paragraph where the source name appears only in a footnote. The analyst sends that paragraph to [[Source Proximity Pattern]] and labels any click discussion as CONTESTED, because `pew-ai`, `ahrefs-aio`, and `seer-aio-impact-ctr-2026` report different market views.

If the property has Search Console generative AI reporting, [[Citation Exposure Metrics]] records impressions by page or URL, country, device, and date with `g-genai-reports`. Click and query interpretation uses `g-gsc-api` or an owner-supplied export; when those fields are absent, the report keeps the screenshot separate from performance claims.

## AIO-Specific Failure Modes

- The top organic URL is logged as cited without checking the visible AIO citation.
- A desktop observation is copied into mobile or another locale without a new capture.
- One third-party CTR study becomes a forecast, even though [[AI Citation Mechanics]] treats the impact evidence as contested.
- A passage rewrite is prioritized before preview controls are checked with `g-ai-opt-guide`.

## Readiness Register Wiring

[[GEO Citation Readiness Register]] consumes the final AIO review row. It needs query, locale, device, observed citation URL, passage status, evidence label, and next review date.

The register expects one of three outputs from this note: ready for passage review, revise the extractable block, or measure first. It must not receive a promised AIO inclusion statement.

## Capture Fields That Change Decisions

Record the exact visible cited URL, because `g-ai-features` does not let reviewers infer it from organic rank.

Record the page passage reviewed, not just the query, before applying `ziptie-aio-source-selection`.

Record whether click interpretation uses property data, `pew-ai`, `ahrefs-aio`, or `seer-aio-impact-ctr-2026`.

Record preview-control conflicts before assigning a passage rewrite to the editor.

## AI Overview Citation Review Exit Rule

Exit with "ready", "revise", or "measure first". A recommendation is not ready if it lacks the observed surface, the passage being evaluated, or the evidence label for any click claim.
