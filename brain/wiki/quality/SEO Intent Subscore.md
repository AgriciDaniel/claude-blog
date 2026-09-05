---
type: spoke
title: "SEO Intent Subscore"
domain: "Blog Quality"
status: active
created: 2026-07-06
updated: 2026-07-10
tags: [quality, scorecard, active]
confidence: advisory
related:
  - "[[Blog Quality Score]]"
  - "[[Quality Score Rubric]]"
  - "[[Content Quality Subscore]]"
  - "[[Google Data Integrations]]"
---

# SEO Intent Subscore

## SEO Intent Scoring Assignment

This 25 point spoke checks whether the page matches the searcher job it is trying to serve. It scores intent fit, title promise, metadata, internal links, and measurement discipline. `g-helpful-content` anchors usefulness, `g-ads-kw` can support keyword research inputs, `dfs-labs` can support SERP-overlap or competitor datasets as vendor evidence, and `g-gsc-api` is the first-party route for query performance claims.

## Query Fit Signals This Note Scores

- Primary and secondary intent are named in reviewer language.
- Title, H1, intro, and major H2s match the promise made to the searcher.
- Internal links help the reader complete the job or continue the cluster path.
- Metadata is specific without stuffing entities or implying unsupported outcomes.

## Intent Signals Routed Elsewhere

Originality belongs to [[Content Quality Subscore]]. Trust proof belongs to [[E-E-A-T Trust Subscore]]. Technical validation belongs to [[Technical Schema Subscore]]. AI passage work belongs to [[AI Citation Readiness Subscore]]. This note can block an over-optimized article, but it should not rewrite the article alone.

## SEO Intent Evidence Grid

| SEO intent criterion | Points | Required proof | Blocking failure |
|---|---:|---|---|
| Query-to-reader fit | 6 | Target query maps to a clear reader problem and article outcome. | Query targets one job while the page answers another. |
| Title and H1 promise | 5 | Title and H1 describe the real deliverable without inflated claims. | Headline promises a comparison, guide, or data point not present. |
| Section alignment | 5 | H2s cover the necessary subquestions in a useful order. | Sections chase keywords while skipping the reader decision. |
| Internal link logic | 5 | Links route to relevant hub, spoke, evidence, or next-step pages. | Links are absent, promotional, or unrelated to intent. |
| Metadata and measurement | 4 | Description, canonical target, and data availability are recorded. | Performance claims rely on market averages alone. |

## Point Rules And Stop Conditions

Do not award points for keyword repetition without reader fit. A page can be technically optimized and still fail this subscore if its title misstates the deliverable. If first-party performance data is unavailable, mark the measurement row as advisory and route the gap to [[Google Data Integrations]].

## Intent Review Steps

1. Write the target query and the reader job separately.
2. Compare the title, intro, and H2s against that job.
3. Score the five grid rows.
4. Mark unsupported outcome language as blocked.
5. Send the score and gaps to [[Quality Score Rubric]].

## Intent Mismatch Example

Target query: "blog schema examples."
Draft title: "Complete guide to SEO content strategy."
Reader job and page promise diverge.
Keyword data from `g-ads-kw` can inform demand.
SERP overlap from `dfs-labs` can inform grouping.
Neither source proves this draft satisfies intent.
Fix: retitle around schema examples.
Then move strategy material to a support section.
If GSC export exists, use `g-gsc-api`.
Without it, mark measurement advisory.

## Intent-Specific Failure Cases

- Secondary keywords drive the H2 order.
- A comparison query receives a one-product answer.
- Internal links point to sales pages before task completion.
- Metadata promises data the article never provides.
- Vendor SERP data is treated as first-party performance.

## Brief And Outline Wiring

[[Content Brief Output Contract]] consumes intent diagnostics early.
Inputs provided: reader job, query set, SERP pattern, exclusions.
Expected output: approved promise and source-backed section jobs.
[[SERP Outline Output Contract]] consumes the scored alignment.
It expects H1 job, H2 sequence, evidence slots, link zones.
[[SEO Check Validation Checklist]] consumes final metadata gaps.
