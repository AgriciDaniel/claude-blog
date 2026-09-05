---
type: deliverable
title: "Blog Rewrite Refresh Plan"
domain: "Blog Rewriting"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, rewriting, refresh-plan, active]
---

# Blog Rewrite Refresh Plan

## Rewrite Refresh Planning Scope

This plan turns an existing post into a controlled rewrite queue. It separates source refresh, answer restructuring, decay diagnosis, canonical risk, and rollback planning. A refresh is not automatically a full rewrite: the plan must prove why the page needs revision, what evidence changed, and how success will be checked through [[Google Data Integrations]].

### Inputs, Assumptions, And Constraints

Required inputs are the current URL, target query set, publication and modified dates, existing headings, source list, internal links, GSC comparison window, and known canonical target. `g-gsc-api` supports click, impression, CTR, and position evidence, while `g-ranking-history` is used only for confirmed Google ranking update timing. Do not assign a ranking loss to an update without property evidence.

### Decisions That Must Be Deferred

Defer merge, prune, noindex, and canonical changes until [[Freshness and Content Decay]], [[Google Algorithm Update Ledger]], and canonical evidence agree. `g-canonical` supports URL consolidation review, not a shortcut for deleting useful pages.

## Blog Rewrite Refresh Plan Execution Table

| Refresh phase | Required input | Output produced | Owner | Evidence requirement | Follow-up action |
|---|---|---|---|---|---|
| Decay triage | GSC window, ranking-history dates, query class | Refresh, monitor, merge, or leave alone | SEO analyst | `g-gsc-api` export plus `g-ranking-history` date check | Schedule review date |
| Source replacement | Current claims and old citations | Source swap list | Researcher | `g-helpful-content` quality standard and dated source IDs | Mark stale claims before rewriting |
| Answer rebuild | Reader job and old intro | New answer block and revised H2 order | Editor | Helpful-content self-assessment fit | Compare against original intent |
| Canonical review | URL pair, duplicate intent, internal links | Canonical or differentiation recommendation | Technical SEO | `g-canonical` plus query evidence | Escalate risky consolidations |
| Rollback note | Baseline metrics and changed sections | Reversal trigger and owner | Content lead | Pre-change snapshot and review date | Recheck after crawl and performance window |

## Operating Loop For Existing Posts

1. Capture the current page state before editing, including source IDs, headings, title, canonical tag, and internal links.
2. Replace stale or weak claims first so the rewrite is not a style pass over old evidence.
3. Restructure the answer if the reader job has changed; otherwise keep stable sections intact.
4. Publish the plan with a rollback trigger tied to measured queries, not a vague traffic target.

## Source IDs Used

This rewrite plan wires `g-helpful-content`, `g-gsc-api`, `g-ranking-history`, and `g-canonical` to the refresh decision path.
