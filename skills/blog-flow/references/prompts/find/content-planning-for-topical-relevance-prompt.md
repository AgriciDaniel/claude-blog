<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Content planning for Topical Relevance Prompt"
description: "Content planning for Topical Relevance Prompt"
updated: 2026-04-25
tags:
  - prompts
  - find
---

# Content planning for Topical Relevance Prompt

## Use This When

Plan non-overlapping pillar and cluster coverage.

## Task Inputs

- goal.
- URL inventory.
- audience and market.
- entities and sources.

## Decisions

- Assign pillar, cluster, merge, refresh, or retire.
- Separate gaps from cannibalization.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Map each page to a reader job.
2. Group unanswered needs.
3. Design internal-link routes.
4. Rank gaps by value, evidence, and effort.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Coverage map.
- Page-role decisions.
- Topic plan.
- Source and link gaps.
- Publishing queue.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
