<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "CTR AUDIT PROMPT"
description: "CTR AUDIT PROMPT"
updated: 2026-04-25
tags:
  - prompts
  - optimize
---

# CTR AUDIT PROMPT

## Use This When

Diagnose low organic CTR without confusing rank, demand, or logging changes with snippet performance.

## Task Inputs

- dated GSC query-page data by device and country.
- current title and description.
- supplied SERP examples.
- recent changes.

## Decisions

- Compare equivalent segments.
- Separate snippet hypotheses from rank, seasonality, and anomalies.
- Test one reversible variable.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Find CTR gaps at comparable positions.
2. Compare snippet promise with page.
3. Draft truthful variants.
4. Set guardrails.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Segmented diagnosis.
- Confounder register.
- Title and description test matrix.
- Success metric.
- Rollback rule.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
