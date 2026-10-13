<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Keyword variations for topical relevance prompt"
description: "Keyword variations for topical relevance prompt"
updated: 2026-04-25
tags:
  - prompts
  - find
---

# Keyword variations for topical relevance prompt

## Use This When

Expand one validated query without manufacturing thin pages.

## Task Inputs

- primary query and page.
- audience vocabulary and entities.
- supplied related-query evidence.
- existing overlapping pages.

## Decisions

- Classify each variation as same-page, separate-page, alias, or reject.
- Preserve market scope.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Group problem, task, comparison, alternative, and constraint modifiers.
2. Map intent.
3. Check overlap.
4. Select useful headings.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Variation groups.
- Intent labels.
- Page decisions.
- Coverage gaps.
- Headings and terminology.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
