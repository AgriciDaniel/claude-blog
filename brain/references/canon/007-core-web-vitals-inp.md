# Core Web Vitals And INP

## Source

Interaction to Next Paint, Web Vitals, Largest Contentful Paint, and Cumulative Layout Shift, web.dev.
URLs: https://web.dev/articles/inp, https://web.dev/articles/vitals, https://web.dev/articles/lcp, https://web.dev/articles/cls
INP replacement event: 2024-03-12 (`wd-inp-mar12` announcement).
INP source updated: 2025-09-02.
Retrieved and reviewed: 2026-10-07.
Confidence: EVIDENCE-BASED.

Ledger source: `wd-inp`.

## Core Thesis

Core Web Vitals measure user experience with LCP, INP, and CLS. INP replaced FID as a Core Web Vital in 2024. Blog audits should use INP, not FID, and should evaluate field data at the 75th percentile, segmented by mobile and desktop, when available.

## Blog Application

- Use LCP at or below 2.5 seconds as the target.
- Use INP at or below 200 milliseconds as the target.
- Use CLS at or below 0.1 as the target.
- Never present FID as a current Core Web Vital.
- Treat performance as a reader and crawl accessibility constraint, not a guaranteed ranking win.

## Measurement Boundaries

`chrome-crux-history` documents a default 25 weekly periods and a maximum 40
through `collectionPeriodCount`, each a rolling 28-day window. The detailed
weekly section conflicts with an older six-month introduction; retain that
qualification. Source: <https://developer.chrome.com/docs/crux/history-api>.

The final soft-navigation origin trial covered Chrome 147-149
(`chrome-softnav-final`); current `chrome-soft-nav` documentation says enabled
by default in Chrome 151. Verify browser and tool support for the actual
measurement. Sources: <https://developer.chrome.com/blog/final-soft-navigations-origin-trial>
and <https://developer.chrome.com/docs/web-platform/soft-navigations>.

## Quote Handling

No verbatim quote included. This note paraphrases the sources and routes exact claims through `references/source-ledger.json`.

## Reinforces

Page speed, image handling, JavaScript restraint, field data, PSI, CrUX, and technical quality scoring.

## Folded into the wiki

- [[Technical Schema Subscore]]
- [[GSC Search Analytics Query Plan]]
- [[Quality Score Rubric]]
