<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Dual-Surface Content Scorecard"
description: "Dual-Surface Content Scorecard"
updated: 2026-04-25
tags:
  - prompts
  - win
---

# Dual-Surface Content Scorecard

## Use This When

Use this when you need to judge whether a page can perform in traditional search and AI-assisted discovery while still supporting conversion.

## AI Compatibility

Claude, GPT, Gemini, and other long-context models. Works best with current customer language and conversion evidence.

## Inputs

- Page copy.
- Target queries or topics.
- Intended conversion goal.
- Audience segment.
- Known first-party insights.
- Performance data, if available.
- Competing page examples, optional.

## Prompt

```text
Score this content for two discovery surfaces: traditional search and AI-assisted answer environments.

Evaluate:
1. Original usefulness and specificity.
2. Alignment with audience needs and decision stage.
3. Evidence, examples, data, or firsthand insight.
4. Clear answers to buyer questions.
5. Conversion support: CTA, proof, objection handling, and next step.
6. Refresh or update need.
7. Measurement readiness: traffic, engagement, qualified leads, sales conversions, and ROI indicators.

Return traditional search score, AI-assisted discovery score, conversion-readiness score, evidence strengths, gaps, risks, recommended updates, and the highest-impact next three actions. Use business-impact language, not traffic-only language.
```

## Output

- A structured Win-stage working document.
- Prioritized recommendations.
- Evidence and measurement gaps.
- Claims or assumptions that require verification.

## Example

Input: existing service page with traffic but low form submissions. Output: scores showing whether the page lacks buyer proof, direct answers, customer language, CTA clarity, or measurable conversion paths.

## See Also

- [Prompt Library](../README.md)
- [BOFU Page Brief Generator](bofu-page-brief-generator.md)
- [Conversion Audit Prompt](conversion-audit-prompt.md)

## Source Note

Derived from SEJ State of SEO 2026, verified AI-search evidence, and SEJ B2B Lead Generation.
