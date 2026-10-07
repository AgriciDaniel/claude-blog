<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Schema Prompt 1"
description: "Schema Prompt 1"
updated: 2026-04-25
tags:
  - prompts
  - optimize
---

# Schema Prompt 1

## Use This When

Recommend structured data that matches visible content and current Google eligibility.

## Task Inputs

- rendered content and canonical URL.
- page and entity facts.
- existing markup.
- current property documentation.

## Decisions

- Use only visible primary content.
- Separate Schema.org validity from Google eligibility.
- Reject fabricated values.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Inventory entities.
2. Map eligible types and required properties.
3. Compare markup to page.
4. Define validation.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Type and property table.
- Keep, add, correct, and remove decisions.
- JSON-LD brief.
- Validation checklist.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
