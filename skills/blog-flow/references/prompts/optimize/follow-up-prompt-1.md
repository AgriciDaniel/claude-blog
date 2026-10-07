<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Follow-up Prompt 1"
description: "Follow-up Prompt 1"
updated: 2026-04-25
tags:
  - prompts
  - optimize
---

# Follow-up Prompt 1

## Use This When

Turn an initial audit into clarified implementation decisions.

## Task Inputs

- initial audit.
- owner responses.
- new evidence.
- constraints and dependencies.

## Decisions

- Mark each finding accepted, rejected, needs evidence, or deferred.
- Resolve scope conflicts.
- Set acceptance criteria.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Reconcile evidence.
2. Collapse overlap.
3. Assign owners and prerequisites.
4. Name review point.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Finding dispositions.
- Implementation queue.
- Acceptance criteria.
- Owners.
- Remaining questions.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
