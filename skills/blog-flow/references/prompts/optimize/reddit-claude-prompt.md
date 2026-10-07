<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Reddit Claude Prompt"
description: "Reddit Claude Prompt"
updated: 2026-04-25
tags:
  - prompts
  - optimize
---

# Reddit Claude Prompt

## Use This When

Extract audience language from supplied Reddit material without treating comments as verified fact.

## Task Inputs

- public URLs or excerpts with dates.
- research question.
- sampling limits.
- primary sources for cross-checking.

## Decisions

- Separate language and experience from facts.
- Downweight promotion.
- Avoid prevalence claims.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Code jobs, frustrations, objections, and vocabulary.
2. Preserve dissent.
3. Flag claims.
4. Derive content hypotheses.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Theme table with links.
- Vocabulary.
- Contested claims.
- Content angles.
- Research gaps.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
