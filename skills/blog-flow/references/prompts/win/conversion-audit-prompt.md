<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Conversion Audit Prompt"
description: "Conversion Audit Prompt"
updated: 2026-04-25
tags:
  - prompts
  - win
---

# Conversion Audit Prompt

## Use This When

Use this when a page, campaign, or funnel gets traffic but produces weak leads, low conversion rate, unclear attribution, or poor sales follow-up quality.

## AI Compatibility

Claude, GPT, Gemini, and other long-context models. Works best with current customer language and conversion evidence.

## Inputs

- Page or funnel copy.
- Traffic sources.
- Conversion goal.
- Analytics or conversion data.
- Call, chat, or form transcript samples.
- Known objections.
- Ad copy or campaign promise.
- Sales feedback, if available.

## Prompt

```text
Audit this conversion path for lead quality, friction, and measurement gaps.

Use the supplied page, campaign, and first-party conversation data. Identify:
1. Where visitor expectations may not match the page or offer.
2. Common objections and hesitation points.
3. Missing decision-making information.
4. Language mismatches between customers and the page.
5. CTA friction.
6. Tracking gaps across form, phone, chat, and offline outcomes.
7. Whether reporting connects to qualified leads or sales, not only traffic.

Return an executive summary, top blockers, lead-quality risks, messaging fixes, page/content fixes, tracking fixes, first-party data to collect next, and a ranked test backlog. Do not recommend more spend until content, offer clarity, and measurement gaps are assessed.
```

## Output

- A structured Win-stage working document.
- Prioritized recommendations.
- Evidence and measurement gaps.
- Claims or assumptions that require verification.

## Example

Input: paid search landing page with many calls but few booked appointments. Output: an audit of pricing clarity, qualification, phone attribution, repeated objections, CTA mismatch, and test priorities.

## See Also

- [Prompt Library](../README.md)
- [BOFU Page Brief Generator](bofu-page-brief-generator.md)
- [Dual-Surface Content Scorecard](dual-surface-content-scorecard.md)

## Source Note

Derived from PPC Trends 2026, CallRail/SEJ Better Leads More Sales 2025, and SEJ State of SEO 2026.
