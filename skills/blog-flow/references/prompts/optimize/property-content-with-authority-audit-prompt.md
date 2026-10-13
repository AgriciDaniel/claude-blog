<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Property content with authority audit prompt"
description: "Property content with authority audit prompt"
updated: 2026-04-25
tags:
  - prompts
  - optimize
---

# Property content with authority audit prompt

## Use This When

Assess visible authority and trust evidence for the page's claims.

## Task Inputs

- page and identity pages.
- author and review-process evidence.
- citations and first-hand proof.
- topic risk.

## Decisions

- Match proof to claim risk.
- Distinguish missing from disconnected evidence.
- Do not treat schema or biography alone as proof.

## Prompt

```text
Act as a senior blog strategist using the FLOW model.

Use only supplied evidence. Label assumptions and unverified claims. Complete these checks:
1. Trace claims.
2. Inspect author and publisher identity.
3. Check disclosures and corrections.
4. Rank trust gaps.

Return only the required output. Do not invent statistics, support, or private examples.
```

## Required Output

- Claim-proof matrix.
- Identity findings.
- Disclosure gaps.
- Authority fixes.
- Verification steps.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
