---
type: question
title: "AI Citation Attribution Question"
status: seed
created: 2026-08-25
updated: 2026-08-25
tags: [geo, measurement, question]
domain: "Blog Content Brain"
confidence: advisory
related:
  - "[[AI Citation Mechanics]]"
  - "[[AI Overview Citation Review]]"
  - "[[AI Mode Citation Review]]"
  - "[[Generative AI Performance Reporting]]"
  - "[[Search Visibility Versus Citation Exposure]]"
  - "[[Source Quality Ladder]]"
  - "[[Claim Verification Flow]]"
  - "[[Uncertainty Eval Policy]]"
source_urls:
  - "https://developers.google.com/search/docs/appearance/ai-features"
  - "https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports"
---

# AI Citation Attribution Question

## Question

When a page appears near an AI response, what evidence is sufficient to say the page was cited, influenced the response, or received measurable exposure?

## Why this stays open

Visible citation, Search Console impression, referral visit, and semantic similarity are different observations. Current official guidance does not make them interchangeable, and no workflow should collapse them into one success metric.

## Observation classes

| Observation | What it supports | What it does not support |
|---|---|---|
| Visible linked citation | The URL appeared in that captured response | Stable selection or causal influence |
| GSC AI feature impression | Google recorded eligible exposure under its reporting definition | A click or a visible citation in every case |
| Tagged referral session | A visit arrived with a detectable referrer | Full AI visibility or response influence |
| Repeated manual sample | Frequency in a bounded prompt set | Population-wide citation share |
| Textual similarity | Possible topical overlap | Training use or source attribution |
| Third-party visibility score | Vendor-defined comparative signal | First-party Google measurement |
| Organic ranking | Classic Search position under a method | AI Mode or AI Overview citation |
| Server log crawler visit | A crawler requested a URL | Indexing, ranking, or citation |

## Minimum record

1. Product and surface.
2. Query or task.
3. Locale, device, account state, and date.
4. Visible URL and screenshot or export.
5. Sampling method.
6. Known personalization.
7. Confidence tag.
8. Explicit non-claims.

## Current answer boundary

Use “observed citation” only for a visible linked source in a dated capture. Use “reported impression” only for a first-party export that defines the surface. Use “referral visit” only for measured traffic. Do not use “influenced” without a causal method.

## Research path

Pair [[Generative AI Performance Reporting]] with bounded manual captures. Compare AI Overview and AI Mode separately through [[AI Overview Citation Review]] and [[AI Mode Citation Review]]. Revisit this question when Google changes reporting definitions or exposes more granular fields.

## Stop conditions

Stop and label unknown when the URL is hidden, the sample cannot be reproduced, the product is unclear, personalization cannot be bounded, or the claim would imply causal attribution from correlation.
