<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Claude Prompt 2"
description: "Claude Prompt 2"
updated: 2026-04-25
tags:
  - prompts
  - optimize
---

# Claude Prompt 2

## Use This When

Refine a revised draft against the first diagnosis.

## Task Inputs

- initial diagnosis.
- revised draft.
- resolved and open evidence gaps.
- editor feedback.

## Decisions

- Mark each blocker resolved, partial, or open.
- Reject length without proof.
- Approve only sourced claims.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Compare draft with findings.
2. Test self-contained answers.
3. Inspect proof and transitions.
4. Define acceptance checks.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Resolution matrix.
- Remaining issues.
- Targeted edits.
- Acceptance checklist.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
