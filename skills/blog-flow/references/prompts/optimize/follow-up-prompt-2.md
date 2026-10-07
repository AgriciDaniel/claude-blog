<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Follow-up Prompt 2"
description: "Follow-up Prompt 2"
updated: 2026-04-25
tags:
  - prompts
  - optimize
---

# Follow-up Prompt 2

## Use This When

Investigate unresolved high-impact gaps after the first follow-up.

## Task Inputs

- unresolved findings.
- test results and logs.
- failed criteria.
- implementation notes.

## Decisions

- Attribute failure to evidence, implementation, measurement, or hypothesis.
- Choose retry, alternative, accept, or stop.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Trace evidence chain.
2. Compare expected and observed.
3. Design discriminating checks.
4. Set stop conditions.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Root-cause hypotheses.
- Checks.
- Retry or alternative decision.
- Stop conditions.
- Residual risk.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
