---
type: deliverable
title: "Cannibalization Resolution Matrix"
domain: "SEO Strategy"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, cannibalization, resolution-matrix, active]
---

# Cannibalization Resolution Matrix

## Cannibalization Comparison Job

This matrix compares pages that overlap by query, intent, entity, or internal-link role. Its job is to decide whether to merge, differentiate, canonicalize, redirect, or leave pages separate. The artifact connects to [[Semantic Topic Clusters]] for topic architecture and to [[Google Data Integrations]] for Search Console evidence.

### Rows Required Before A Decision

Each row must represent a candidate URL pair or group with target query, landing page, intent, current canonical, GSC evidence, SERP evidence, and content role. `g-gsc-api` supports query and page data, while `dfs-api` can provide external SERP or keyword evidence when first-party data is unavailable.

### Columns That Make Intent Auditable

Columns must record searcher intent, business purpose, unique information, canonical evidence, internal-link role, helpfulness risk, and recommended action. `g-canonical` supports canonical signal review. `g-helpful-content` keeps the decision centered on whether separate pages serve distinct readers.

## Cannibalization Resolution Matrix Table

| URL group | Intent relationship | Query evidence | Canonical evidence | Recommended action | Confidence | Next action |
|---|---|---|---|---|---|---|
| Page A plus Page B | same intent, partial overlap, or distinct task | `g-gsc-api` clicks, impressions, CTR, position | Current tags, redirects, internal links, `g-canonical` | merge, differentiate, canonicalize, redirect, leave | high, medium, low | Assign owner and due date |
| Hub plus spoke | hub overview versus specific subtask | GSC query split and SERP intent | Hub-spoke link pattern | clarify roles or rewrite intros | medium | Update link anchors |
| Old post plus new post | freshness replacement or separate history | Date range comparison and source age | Preferred URL signal | refresh old, fold into new, or keep both | medium | Draft rollback note |
| Localized variants | locale or market distinction | Locale query evidence | hreflang and canonical relationship | keep separate or fix targeting | low to high | Escalate to locale review |

## Interpretation Rules For Merge Or Differentiate

1. Merge only when the pages serve the same reader task and one stronger URL can preserve useful information.
2. Differentiate when each page has a clear audience, query class, or conversion purpose.
3. Use canonicalization to consolidate duplicate URL signals, not to hide weak editorial decisions.

## Source IDs Used

Cannibalization work uses `g-helpful-content`, `g-canonical`, `g-gsc-api`, and `dfs-api`.
