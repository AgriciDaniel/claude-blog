<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Blog Post Outline Prompt"
description: "Blog Post Outline Prompt"
updated: 2026-04-25
tags:
  - prompts
  - optimize
---

# Blog Post Outline Prompt

## Use This When

Create an answer-first outline from an approved brief.

## Task Inputs

- approved brief and primary question.
- required claims and sources.
- length, voice, and exclusions.
- related pages.

## Decisions

- Give each section one reader question.
- Place evidence beside claims.
- Remove word-count filler.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Write the direct answer.
2. Sequence decision-critical sections.
3. Mark evidence and media slots.
4. Check the next action.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Title and promise.
- H1-H3 outline with purpose.
- Evidence slots.
- Links and CTA.
- Research gaps.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
