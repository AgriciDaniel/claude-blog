---
type: spoke
title: "Intent Drift Audit"
domain: "Blog Rewriting"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [rewriting, freshness, content-decay, active]
---

# Intent Drift Audit

## Intent Drift Audit Job

Intent drift audit checks whether a page still satisfies the searcher and reader task it was built for. A page can keep traffic and still drift if the current queries, SERP language, or internal cluster role no longer match the article's promise.

`g-helpful-content` supports the people-first test: the page should be written for the user task rather than for a legacy keyword. `g-gsc-api` supplies query and page evidence for how users now discover the URL. `g-ranking-history` prevents unsupported claims that a Google update changed intent, and `g-canonical` helps decide whether a different URL should own the intent.

### Intent Evidence Owned Here

This note owns observed query language, title and heading promise, target reader job, page role in a cluster, and whether the canonical owner still matches that job. It does not rewrite the page. Rewrite planning belongs to [[Refresh Versus Rewrite Decision]] and source replacement belongs to [[Source Refresh Workflow]].

### Drift Versus Normal Variation

Normal variation means the page attracts adjacent queries while still answering its core job. Drift means the strongest current demand asks for a different outcome, format, depth, persona, or product stage than the page provides.

## Intent Ownership Table

| Page or cluster role | Target intent | Canonical owner | Anchor evidence | Evidence state |
|---|---|---|---|---|
| Hub page | Broad explanation and route to spokes | Existing hub if it still clarifies the topic | `g-helpful-content`; internal links | CONFIRMED guideline basis, editorial judgment required |
| Comparison article | Decision support between options | Best matching comparison URL | `g-gsc-api` query terms and page filter | First-party data if export exists |
| Old update post | Dated context, not evergreen answer | Timeline or ledger note if the update is historical | `g-ranking-history` | Official date context only |
| Duplicate explainer | Same task as stronger article | Retained URL selected by consolidation review | `g-canonical`; [[Content Consolidation Rules]] | Technical and editorial review needed |
| Spoke page with new query family | Narrow job or new spoke candidate | Current page only if the content can own the job | `g-gsc-api`; `g-helpful-content` | Advisory until rewritten or split |
| Template post attracting pricing queries | Buyer evaluation, not template use | Comparison or pricing guide if approved | `g-gsc-api`; `g-helpful-content` | Decision-stage mismatch |
| Definition page attracting implementation queries | How-to task beyond glossary depth | New or existing how-to spoke | `g-gsc-api`; internal links | Split candidate until drafted |

## Drift Audit Procedure

1. Write the page's intended reader job in one sentence before looking at performance data.
2. Export current query language and group it by job, format, stage, and entity.
3. Compare the query groups against the title, intro, H2s, internal links, and canonical owner.
4. Choose one outcome: intent intact, refresh framing, rewrite for new intent, split a spoke, consolidate, or defer.
5. Record the phrase or query cluster that would trigger a future re-audit.

## Query Reframe Example

Before: a page promises "what is content decay" in the intro.
Current queries ask for a checklist, shown by `g-gsc-api`.
The definition still satisfies beginners under `g-helpful-content`.
Decision: keep the definition page and brief a checklist spoke.
If another URL already owns checklists, route through `g-canonical`.

## Drift Traps

- Adjacent queries are not drift when the core task still matches.
- A title tweak cannot fix a page built for the wrong stage.
- Cluster ownership matters; do not let one URL steal every subtask.
- Update timing should not explain intent change without `g-ranking-history`.

## Cannibalization Matrix Wiring

[[Cannibalization Resolution Matrix]] consumes this note's intent relationship.
Inputs provided: query group, reader job, current owner, and split-or-merge cue.
It expects an action of merge, differentiate, canonicalize, redirect-review, or leave.
Query evidence uses `g-gsc-api`; owner evidence can require `g-canonical`.

## Intent Audit Source IDs

`g-helpful-content`; `g-gsc-api`; `g-ranking-history`; `g-canonical`.

## Related

- [[Freshness and Content Decay]]
- [[Content Consolidation Rules]]
- [[Source Refresh Workflow]]
- [[Semantic Topic Clusters]]
- [[Google Data Integrations]]
