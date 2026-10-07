<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Visibility Prompt"
description: "Visibility Prompt"
updated: 2026-04-25
tags:
  - prompts
  - optimize
---

# Visibility Prompt

## Use This When

Diagnose discoverability across search and sampled AI answer surfaces.

## Task Inputs

- dated GSC and analytics.
- AI samples and method.
- target entities and pages.
- crawl, index, and source evidence.

## Decisions

- Keep search, AI exposure, referrals, and conversion separate.
- Classify gap cause.
- Avoid universal claims.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Map questions to indexed pages.
2. Compare citations and page evidence.
3. Inspect entities and answer structure.
4. Prioritize durable fixes.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Surface-specific baseline.
- Gap matrix.
- Prioritized fixes.
- Measurement plan.
- Sampling limits.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
