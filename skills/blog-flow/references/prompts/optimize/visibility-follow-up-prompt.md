<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Visibility Follow Up Prompt"
description: "Visibility Follow Up Prompt"
updated: 2026-04-25
tags:
  - prompts
  - optimize
---

# Visibility Follow Up Prompt

## Use This When

Measure whether completed changes altered search or sampled AI visibility.

## Task Inputs

- original diagnosis and baseline.
- release dates.
- comparable post-change evidence.
- ranking and reporting context.

## Decisions

- Compare equivalent windows.
- Limit attribution under confounding.
- Keep, iterate, roll back, or wait.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Reproduce baseline definitions.
2. Measure change.
3. Check confounders and completeness.
4. Select next window.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Before-after table.
- Attribution limits.
- Decision.
- Next measurement date.
- Criteria.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
