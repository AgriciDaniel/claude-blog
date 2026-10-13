<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "PAA Question Rewording Prompt"
description: "PAA Question Rewording Prompt"
updated: 2026-04-25
tags:
  - prompts
  - optimize
---

# PAA Question Rewording Prompt

## Use This When

Rewrite supplied PAA and audience questions into clear, non-duplicative questions and supported answer briefs.

## Task Inputs

- PAA questions with date and market.
- first-party questions.
- target page and sources.
- exclusions.

## Decisions

- Merge same-intent questions.
- Keep distinct decision stages.
- Do not treat PAA as stable demand.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Classify intent.
2. Rewrite without changing need.
3. Draft sourced answers.
4. Map to page sections.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Original-to-rewritten map.
- Intent clusters.
- Duplicate decisions.
- Answer briefs.
- Placements.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
