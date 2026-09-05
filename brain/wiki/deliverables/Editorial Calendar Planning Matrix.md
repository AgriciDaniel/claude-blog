---
type: deliverable
title: "Editorial Calendar Planning Matrix"
domain: "Editorial Planning"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, editorial-calendar, planning-matrix, active]
---

# Editorial Calendar Planning Matrix

## Calendar Planning Scope

This matrix schedules topics across a month or quarter by cluster role, freshness risk, distribution need, and measurement cadence. It is a planning artifact, not a promise that publishing volume creates rankings. Helpful-content quality from `g-helpful-content` is the gate for every scheduled piece, and performance checks should use [[Google Data Integrations]] when property data exists.

### Cadence Inputs And Constraints

Inputs include topic cluster, business priority, seasonality, last-modified date, source freshness, available authors, review capacity, and planned distribution surface. `g-ranking-history` can explain confirmed Google update timing, but the calendar must not assume a broad update caused a page's performance change without evidence.

### Decisions Deferred To Other Notes

Merge decisions go to [[Cannibalization Resolution Matrix]] once that artifact exists. Detailed rewrite scope goes to [[Freshness and Content Decay]]. Market context from `sparktoro-zero-click-2026` can shape distribution expectations, but it cannot replace site-level data from `g-gsc-api`.

## Editorial Calendar Planning Matrix Execution Table

| Planning phase | Input needed | Calendar output | Owner | Evidence requirement | Follow-up action |
|---|---|---|---|---|---|
| Cluster sequencing | Hub and spoke map | Publish order by cluster role | Strategist | Helpful-content fit and topic coverage | Confirm internal links |
| Freshness review | Last updated date and source age | Refresh slot or monitor slot | Editor | Dated sources and rewrite need | Assign source refresh |
| Search data check | Query, page, and date range | Priority score with caveat | SEO analyst | `g-gsc-api` export or missing-data note | Recheck after next reporting period |
| Update awareness | Confirmed ranking-history event | Volatility annotation | SEO analyst | `g-ranking-history` only | Avoid unsupported causation |
| Distribution planning | Channel and asset need | Promotion date and asset owner | Distribution lead | Market context caveated through [[Dual Optimization]] | Schedule repurposing brief |

## Operating Loop For Calendar Review

1. Rebuild the calendar from evidence, not from a fixed publishing quota.
2. Mark each item as new, refresh, consolidate, or monitor before assigning a writer.
3. Revisit the matrix monthly or when a confirmed Google update changes the review context.
4. Keep source-refresh work ahead of draft deadlines so weak evidence does not travel downstream.

## Source IDs Used

Calendar planning uses `g-helpful-content`, `g-ranking-history`, `sparktoro-zero-click-2026`, and `g-gsc-api`.
