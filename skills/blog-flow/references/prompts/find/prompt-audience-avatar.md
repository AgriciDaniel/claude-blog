<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Prompt: Audience Avatar"
description: "Prompt: Audience Avatar"
updated: 2026-04-25
tags:
  - prompts
  - find
---

# Prompt: Audience Avatar

## Use This When

Create an evidence-backed reader profile rather than a fictional demographic persona.

## Task Inputs

- interviews, surveys, CRM, support, sales, or community evidence.
- product context.
- known segments and constraints.
- unknowns.

## Decisions

- Separate observation from assumption.
- Segment by job and decision stage.
- Reject decorative demographics.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Extract jobs, triggers, objections, proof needs, and language.
2. Trace evidence.
3. Select target segment.
4. Define missing research.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Reader profile.
- Bounded segments.
- Jobs and objections table.
- Evidence register.
- Content implications.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
