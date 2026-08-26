# Core Web Vitals And INP

## Source

Interaction to Next Paint, Web Vitals, Largest Contentful Paint, and Cumulative Layout Shift, web.dev.
URLs: https://web.dev/articles/inp, https://web.dev/articles/vitals, https://web.dev/articles/lcp, https://web.dev/articles/cls
INP ledger date: 2024-03-05.
INP source updated: 2025-09-02.
Retrieved: 2026-07-09.
Confidence: EVIDENCE-BASED.

## Core Thesis

Core Web Vitals measure user experience with LCP, INP, and CLS. INP replaced FID as a Core Web Vital in 2024. Blog audits should use INP, not FID, and should evaluate field data at the 75th percentile when available.

## Blog Application

- Use LCP at or below 2.5 seconds as the target.
- Use INP at or below 200 milliseconds as the target.
- Use CLS at or below 0.1 as the target.
- Never present FID as a current Core Web Vital.
- Treat performance as a reader and crawl accessibility constraint, not a guaranteed ranking win.

## Quote Handling

No verbatim quote included. This note paraphrases the sources and routes exact claims through `references/source-ledger.json`.

## Reinforces

Page speed, image handling, JavaScript restraint, field data, PSI, CrUX, and technical quality scoring.

## Folded into the wiki

- [[Technical Schema Subscore]]
- [[GSC Search Analytics Query Plan]]
- [[Quality Score Rubric]]
