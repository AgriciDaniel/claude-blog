---
type: spoke
title: "Citation Readiness Decision Tree"
domain: "Blog Content Optimization"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [dual-optimization, geo, decision-tree]
confidence: advisory
related:
  - "[[Dual Optimization]]"
  - "[[AI Citation Mechanics]]"
  - "[[Reader Value Versus Extraction Value]]"
  - "[[Classic SEO And GEO Tradeoffs]]"
source_urls:
  - "https://sparktoro.com/blog/in-2026-less-than-one-third-of-google-searches-still-send-a-click/"
  - "https://www.seerinteractive.com/insights/aio-impact-on-google-ctr-2026-update"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://developers.google.com/search/docs/appearance/ai-features"
---
# Citation Readiness Decision Tree

## Citation Readiness Decision Tree Distinct Job

This note decides whether a section deserves citation-readiness work before an editor rewrites it. The goal is selection, not blanket formatting. A passage should earn GEO attention when it answers a durable question, carries evidence that can survive extraction, and still serves the reader inside the article.

The source posture is intentionally narrow. `g-ai-opt-guide` and `g-ai-features` define the Google-facing eligibility baseline. `seer-aio-impact-ctr-2026` supports interest in cited passages, but only as reported practitioner evidence. `sparktoro-zero-click-2026` keeps the planning frame honest: some value may happen without a click, which belongs in [[AI Citation Mechanics]] and [[Search Visibility Versus Citation Exposure]] rather than in a ranking promise.

### Candidate Passage Inputs

- The exact passage or section being considered.
- Query intent, entity names, source claims, and visible supporting evidence.
- Reader task served by the passage.
- Existing crawl, index, and preview restrictions.

### Decisions Returned

- `ready`: improve the passage for citation without changing the article's job.
- `revise first`: fix reader clarity, evidence, or entity context before GEO work.
- `defer`: leave the passage alone because the query, evidence, or benefit is too weak.

## Readiness Routing Table

| Branch signal | Required check | Source IDs | Decision outcome | Owner action |
|---|---|---|---|---|
| Answer is self-contained | Can the passage stand alone without losing qualifiers? | `g-ai-opt-guide`, `g-ai-features` | Ready or revise first | Editor tightens context and visible sourcing |
| Citation value is plausible | Does the section address a likely answer-surface question? | `seer-aio-impact-ctr-2026` | Ready only with caveat | Strategist marks evidence as as-reported |
| Click value may be limited | Does the page still need non-click success metrics? | `sparktoro-zero-click-2026` | Add measurement note | Analyst links to [[Zero Click Planning Baseline]] |
| Reader value is fragile | Would extraction formatting harm flow or trust? | `g-ai-opt-guide` | Revise first or defer | Content lead protects the article experience |
| Preview controls limit reuse | Are no-snippet or max-snippet rules blocking the answer? | `g-ai-features` | Revise first | Technical SEO checks controls before editing copy |
| Source proximity is weak | Is the claim separated from its visible source context? | `g-ai-opt-guide`, `ziptie-aio-source-selection` | Revise first | Researcher moves the source closer or defers the passage |

## Passage Triage Case

A paragraph defines "zero-click planning" but buries the source at the article end. The tree returns `revise first`: keep the reader answer, move the cited market context near the claim using `sparktoro-zero-click-2026`, then recheck eligibility against `g-ai-features`.

[[GEO Citation Readiness Register]] consumes the tree result. It needs passage text, reader question, source IDs, preview-control state, and the ready or defer label; it outputs owner, status, next review date, and rollback trigger.

## Branch-Specific Breakpoints

- A source-backed sentence still fails if the reader question is unclear under `g-ai-opt-guide`.
- A concise answer should be deferred when required caveats would disappear during extraction (`ziptie-aio-source-selection`).
- A no-snippet page cannot be marked ready until preview controls are reviewed under `g-ai-features`.
- A market-study passage needs a measurement caveat from `sparktoro-zero-click-2026`, not a traffic promise.

## Branch Procedure

1. Identify one candidate passage, not the whole article.
2. Write the reader question that the passage answers.
3. Check whether the evidence is visible, dated, and specific enough for reuse.
4. Choose ready, revise first, or defer.
5. Send ready passages to [[Reader Value Versus Extraction Value]] for final editing.

## Evidence Refresh Rules

Refresh this decision tree when Google changes AI feature documentation, when a new AIO cited-page study enters the source ledger, or when first-party reporting proves that a passage class performs differently from market expectations.
