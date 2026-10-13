<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Keyword research prompt"
description: "Keyword research prompt"
updated: 2026-04-25
tags:
  - prompts
  - find
---

# Keyword research prompt

## Use This When

Build an evidence-ready query and intent map before briefing.

## Task Inputs

- seed topic.
- audience, geography, and language.
- first-party queries or supplied exports.
- SERP observations and exclusions.

## Decisions

- Group by shared intent, not wording alone.
- Choose one primary family per page.
- Mark unsourced metrics unverified.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Extract entities, modifiers, questions, and comparisons.
2. Classify intent.
3. Map clusters to pages.
4. Flag validation needs.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Cluster table.
- Primary and supporting families.
- Question and entity map.
- Cannibalization risks.
- Validation queue.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
