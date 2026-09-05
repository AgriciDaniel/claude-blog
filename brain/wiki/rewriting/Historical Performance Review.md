---
type: spoke
title: "Historical Performance Review"
domain: "Blog Rewriting"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [rewriting, freshness, content-decay, active]
---

# Historical Performance Review

## Performance Review Job

Historical performance review explains what changed before a rewrite decision is made. It compares the page to its own prior behavior, not to a generic industry benchmark. The review should leave behind a dated interpretation that another analyst can challenge.

Use `g-gsc-api` for page and query dimensions with clicks, impressions, CTR, and position. Use `g-ranking-history` only to confirm whether an official ranking update overlaps the review window. `g-helpful-content` supplies the editorial quality lens when the numbers point to a content problem, and `g-canonical` is the handoff source when multiple URLs blur the page history.

### Owned Signal

This note owns historical context: baseline period, comparison period, seasonality caveat, query mix, affected pages, and known Google events. It does not decide whether to refresh, merge, or prune. Those choices belong to [[Refresh Versus Rewrite Decision]], [[Content Consolidation Rules]], and [[Pruning Advisory Checklist]].

### Non-Comparable Periods

Do not compare a launch week with a mature month, a sale period with a normal period, or a post-migration URL with its old path unless the limitation is written into the finding. If GSC data is missing, the review can still record a gap, but it should not invent a trend.

## Historical Review Table

| URL or group | Comparison signal | Source freshness | Action | Owner | Rollback or revision cue |
|---|---|---|---|---|---|
| Single evergreen article | Query-level clicks and impressions by matched window | `g-gsc-api` retrieved for review date | Identify whether decline is demand, visibility, or CTR | Analyst | Reclassify if query mix explains the change |
| Cluster of related posts | Page dimension split across URLs | `g-gsc-api` plus `g-canonical` | Send to consolidation if history is fragmented | SEO strategist | Keep separate if paths serve separate tasks |
| Page reviewed near an update | Date overlap with official rollout | `g-ranking-history` | Add update context without claiming causation | Monitoring owner | Remove update language if dates do not overlap |
| Article with old proof points | Source age and usefulness risk | `g-helpful-content` | Send claims to source refresh before rewriting | Editor | Mark no action if sources remain current |
| Newly published post | Insufficient mature baseline | `g-gsc-api` unavailable or sparse | Hold until a comparable window exists | Program owner | Start review once the period is long enough |
| Seasonal guide | Same seasonal window across years | `g-gsc-api` page and query rows | Compare matched season before declaring decay | Analyst | Seasonality explains the difference |
| Migrated or renamed URL | Old path and new path split history | `g-canonical` plus GSC page views | Rebuild history before action choice | SEO technical owner | Path mapping proves continuity |

## Review Procedure

1. Define the baseline and comparison periods before opening any narrative explanation.
2. Pull page and query views separately so a query-mix change is not mistaken for page decay.
3. Check official Google update dates only after the trend is visible in first-party data.
4. State the weakest assumption in the finding, such as seasonality, migration, or missing country filters.
5. Hand off to the next rewriting note with a recommended action class and a confidence label.

## Matched-Window Example

Before: an analyst compares launch week against a mature month.
That finding is unusable because `g-gsc-api` windows are not comparable.
After: the analyst compares two equivalent seasonal windows.
Query rows show the same job but fewer impressions.
The note labels demand softness, not rewrite failure.
If update dates overlap, `g-ranking-history` adds context only.

## Trend Reading Hazards

- Mixing countries or devices changes the baseline; cite `g-gsc-api` filters.
- A migration can split history; check URL signals with `g-canonical`.
- Official rollout overlap is not causality; constrain `g-ranking-history` wording.
- Old proof points need source review before performance explains anything.

## Decay Register Wiring

[[Content Decay Triage Register]] consumes this note's trend interpretation.
Inputs provided: baseline period, comparison period, strongest signal, caveat, and owner.
It expects a status row for refresh, investigate, monitor, or consolidate.
The register should copy only reproducible fields from `g-gsc-api`.

## Historical Review Source IDs

`g-helpful-content`; `g-gsc-api`; `g-ranking-history`; `g-canonical`.

## Related

- [[Content Decay Detection]]
- [[Refresh Versus Rewrite Decision]]
- [[Content Consolidation Rules]]
- [[Google Algorithm Update Ledger]]
- [[Google Data Integrations]]
