<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Technical Audit Prompt"
description: "Technical Audit Prompt"
updated: 2026-04-25
tags:
  - prompts
  - optimize
---

# Technical Audit Prompt

## Use This When

Find technical conditions blocking crawl, render, index, performance, or measurement.

## Task Inputs

- target URLs.
- HTTP, crawl, rendered HTML, robots, sitemap, canonical, and index evidence.
- dated field and lab data.
- recent releases.

## Decisions

- Separate observed defects from causes.
- Scope URL, template, or infrastructure.
- Prioritize reproducibility and rollback.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Check access, directives, canonicalization, rendering, and discovery.
2. Keep lab and field data distinct.
3. Reproduce.
4. Define validation.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Findings with severity and scope.
- Reproduction.
- Fix, owner, and rollback table.
- Post-fix checks.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
