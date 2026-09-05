---
type: deliverable
title: "Content Decay Triage Register"
domain: "Blog Content Brain"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, freshness, triage]
source_urls:
  - "https://developers.google.com/webmaster-tools/v1/searchanalytics/query"
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history"
  - "https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls"
---

# Content Decay Triage Register

## Decay Record Scope

This register compares current and previous GSC exports, query shifts, dropped pages, canonical conflicts, and refresh actions for [[Freshness and Content Decay]]. It does not diagnose ranking updates from chatter. The source IDs are `g-gsc-api`, `g-helpful-content`, `g-ranking-history`, and `g-canonical`.

## Events This Register Captures

Capture a page when clicks, impressions, ranking position, query mix, or indexed URL changes enough to affect the content plan. Also capture updates where the page still ranks but no longer satisfies the reader job. Use [[Google Data Integrations]] for export hygiene and [[2026 Google Update Timeline]] only for Google-confirmed update timing.

## Events Routed Elsewhere

Technical outages go to engineering. Schema-only problems go to [[Blog Schema Stack]]. A migration or duplicate URL problem goes to canonical review before rewriting. Market-wide AI or zero-click context belongs in [[AI Citation Mechanics]], not this register.

## Content Decay Triage Register Table

| Item | Source evidence | Confidence | Status | Rollback trigger |
|---|---|---|---|---|
| Query loss | Current vs previous GSC query rows | High with matched date windows | Refresh brief | Recovery or further drop after review |
| Page drop | Page-level clicks and impressions | Medium until canonical checked | Investigate | URL Inspection contradicts index assumption |
| Position slide | Query position trend | Medium, because position averages blur | Rewrite or monitor | Confirmed Google update overlaps |
| Canonical confusion | Duplicate URL or selected canonical issue | High when canonical evidence exists | Consolidate plan | Preferred URL changes unexpectedly |
| Helpfulness gap | Reader job no longer answered | Advisory until editorial review | Refresh content | Reviewer rejects new angle |
| Update overlap | Date aligns with official ranking history | High for timing only | Annotate, do not blame | No property evidence supports impact |

## Review Loop And Rollback Trigger

Every register item needs an owner, next review date, and accepted action: refresh, consolidate, prune, monitor, or escalate. `g-ranking-history` supports confirmed update dates, not causal proof. `g-gsc-api` supports property evidence when exports are available. If the action changes live content, the rollback trigger must be written before implementation.
