<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Content Prioritization Prompt"
description: "Content Prioritization Prompt"
updated: 2026-04-25
tags:
  - prompts
  - find
---

# Content Prioritization Prompt

## Use This When

Rank competing content work against explicit evidence and capacity.

## Task Inputs

- candidate topics or URLs.
- business and reader value.
- performance and demand evidence.
- effort and dependencies.

## Decisions

- Place each item in now, next, later, maintain, or reject.
- Show ties and missing evidence.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Normalize outcomes.
2. Score value, evidence, urgency, and effort separately.
3. Test weak assumptions.
4. Select an executable tranche.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Ranked backlog with scores.
- Decision for every item.
- Dependencies.
- First tranche.
- Review triggers.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
