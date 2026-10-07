<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Prompt: Core 30 Content Audit"
description: "Prompt: Core 30 Content Audit"
updated: 2026-04-25
tags:
  - prompts
  - optimize
---

# Prompt: Core 30 Content Audit

## Use This When

Audit up to 30 pages as a portfolio and choose page-level actions.

## Task Inputs

- up to 30 pages with purpose.
- comparable performance.
- query map and priorities.
- capacity constraints.

## Decisions

- Keep, refresh, consolidate, redirect, retire, or investigate each page.
- Protect distinct roles.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Assess intent, evidence, freshness, overlap, links, and conversion.
2. Compare cohorts.
3. Identify patterns.
4. Sequence work.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Page scorecard.
- Disposition for every page.
- Portfolio blockers.
- Prioritized roadmap.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
