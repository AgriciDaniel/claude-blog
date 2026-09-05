---
type: spoke
title: "Content Consolidation Rules"
domain: "Blog Rewriting"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [rewriting, freshness, content-decay, active]
---

# Content Consolidation Rules

## Consolidation Rule Scope

This note decides when two or more blog URLs should become one editorial asset. It does not approve a redirect, CMS edit, or publication change. It gives the content lead a source-cited recommendation that can be reviewed beside [[Freshness and Content Decay]], [[Content Decay Detection]], and [[Intent Drift Audit]].

Use consolidation only when overlap is harming reader clarity or measurement. `g-helpful-content` supports the people-first test: if separate pages force readers to stitch together the answer, the split is suspect. `g-gsc-api` gives the query, page, click, impression, CTR, and position dimensions needed to compare pages before recommending a retained URL. `g-canonical` is the technical source for canonical and redirect signal handling, while `g-ranking-history` keeps broad update narratives tied to confirmed Google history rather than rumor.

### Merge Actions And Blocks

Allowed advisory outputs: keep one URL as the owner, merge unique evidence into it, recommend internal-link updates, recommend a canonical or redirect review, or defer because the pages serve different jobs.

Disallowed outputs: deleting content because it is old, overwriting experience evidence without a source trail, treating canonicalization as a substitute for editorial fit, or promising ranking recovery after a merge.

### Consolidation Exceptions Requiring Approval

Escalate before recommending consolidation when a URL has external backlinks, revenue attribution, legal review history, paid campaign dependencies, or a distinct audience segment. These cases need a rollback owner and a live-system approver outside this V1 brain.

## Consolidation Rule Table

| Rule | Evidence source | Applies to | Exception | Approval path |
|---|---|---|---|---|
| Merge only when pages answer the same reader task | `g-helpful-content` | Duplicate explainers, overlapping comparisons, old update posts | Different intent or funnel stage | Content lead plus editor |
| Pick the retained URL from first-party performance and fit | `g-gsc-api` | URLs with query and page history | No clean winner in data | Analyst documents tie and defers |
| Preserve unique sourced sections before draft merge | `g-helpful-content` | Experience, examples, dated claims | Unsupported or stale evidence | Source steward refreshes first |
| Route canonical or redirect notes to technical review | `g-canonical` | Duplicate URLs, syndicated variants, protocol or path variants | Editorial overlap without URL duplication | SEO technical owner |
| Do not blame an unconfirmed update for overlap | `g-ranking-history` | Consolidation triggered after volatility | Confirmed rollout window matches decline | Monitoring owner checks [[Google Algorithm Update Ledger]] |
| Keep history separate when it answers a dated event | `g-ranking-history` | Old update recap beside evergreen guide | Recap has no distinct reader job | Monitoring owner plus editor |
| Retain different proof paths when both help readers | `g-helpful-content` | Case study beside how-to article | One page repeats the same evidence | Source steward plus content lead |

## Consolidation Review And Reversal

1. Confirm the current reader job for every candidate URL.
2. Pull page-level GSC comparisons for the same date range and locale.
3. List claims and examples that would be lost if the weaker URL disappeared.
4. Name the retained URL, the absorbed sections, and the links that need review.
5. Define rollback as restoring the separated editorial plan if the merge damages the reader path or measurable query coverage.

## Example Merge Decision

Sample pair: `/blog-refresh-checklist/` and `/content-decay-audit/`.
Both pages answer the same old-post repair task under `g-helpful-content`.
GSC page rows show the checklist owns most matching queries via `g-gsc-api`.
The audit post keeps two sourced examples that the checklist lacks.
Decision: retain the checklist URL and absorb only those examples.
Canonical notes go to technical review under `g-canonical`.
Rollback means separating the examples if query coverage narrows.

## Consolidation-Specific Failure Points

- Merging after one noisy week hides intent differences; compare periods with `g-gsc-api`.
- A canonical note cannot replace reader-fit review; cite `g-canonical` narrowly.
- Removing a weaker URL can drop unique evidence; test sections with `g-helpful-content`.
- Update timing is context only; confirm dates through `g-ranking-history`.

## Cannibalization Matrix Wiring

[[Cannibalization Resolution Matrix]] consumes this note's merge recommendation.
Inputs provided: URL group, retained owner, absorbed sections, and approval path.
It expects a row outcome: merge, differentiate, canonicalize, redirect-review, or leave separate.
Measurement cells use `g-gsc-api`; URL-signal cells use `g-canonical`.

## Source IDs Used

`g-helpful-content`; `g-gsc-api`; `g-ranking-history`; `g-canonical`.

## Related

- [[Freshness and Content Decay]]
- [[Content Decay Detection]]
- [[Intent Drift Audit]]
- [[Google Data Integrations]]
- [[Google Algorithm Update Ledger]]
