<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Follow-up Prompt"
description: "Follow-up Prompt"
updated: 2026-04-25
tags:
  - prompts
  - optimize
---

# Follow-up Prompt

## Use This When

Continue prior work with one evidence-linked decision and action plan.

## Task Inputs

- prior output.
- user feedback.
- new evidence.
- current state and decision needed.

## Decisions

- Preserve settled decisions unless evidence changes them.
- Answer the requested decision first.
- Separate now from later.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Summarize relevant state.
2. Evaluate new evidence.
3. Choose action and check.
4. Record superseded advice.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Decision and rationale.
- Immediate actions.
- Acceptance check.
- Superseded items.
- Unknowns.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
