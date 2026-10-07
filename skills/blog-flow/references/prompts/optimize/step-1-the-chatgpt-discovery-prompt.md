<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Step 1: The ChatGPT Discovery Prompt"
description: "Step 1: The ChatGPT Discovery Prompt"
updated: 2026-04-25
tags:
  - prompts
  - optimize
---

# Step 1: The ChatGPT Discovery Prompt

## Use This When

Discover answer and citation opportunities from supplied AI-search samples.

## Task Inputs

- prompts, outputs, citations, dates, locale, and account context.
- target entities and pages.
- source coverage.

## Decisions

- Treat samples as observations, not rankings.
- Classify access, evidence, entity, or format gaps.
- Discard irrelevant opportunities.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Map prompts to reader jobs.
2. Compare answers with pages.
3. Identify evidence gaps.
4. Create qualification candidates.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Prompt and citation map.
- Coverage gaps.
- Candidate opportunities.
- Sampling limits.
- Qualification queue.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
