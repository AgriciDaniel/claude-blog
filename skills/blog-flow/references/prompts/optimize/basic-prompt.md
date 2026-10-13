<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Basic Prompt"
description: "Basic Prompt"
updated: 2026-04-25
tags:
  - prompts
  - optimize
---

# Basic Prompt

## Use This When

Run a bounded first-pass page audit.

## Task Inputs

- page capture.
- audience and goal.
- performance and source evidence.
- constraints.

## Decisions

- Separate observed defects from performance hypotheses.
- Limit work to highest-impact issues.
- Route deeper checks.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Check answer clarity, structure, evidence, identity, and next action.
2. Name strengths and defects.
3. Rank fixes.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Diagnosis.
- Top fixes.
- Preserve list.
- Open questions.
- Recommended follow-up.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
