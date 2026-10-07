<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Claude Prompt 1"
description: "Claude Prompt 1"
updated: 2026-04-25
tags:
  - prompts
  - optimize
---

# Claude Prompt 1

## Use This When

Perform a first model-assisted page diagnosis before rewriting.

## Task Inputs

- page capture.
- reader and business goal.
- query family.
- analytics and source notes.

## Decisions

- Separate evidence from hypotheses.
- Select defects blocking comprehension, trust, or extraction.
- Name what to preserve.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Trace promise through headings, proof, examples, and CTA.
2. Find missing answers and entity ambiguity.
3. Rank by confidence.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Diagnosis.
- Preserve, fix, and investigate lists.
- Evidence gaps.
- Second-pass brief.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
