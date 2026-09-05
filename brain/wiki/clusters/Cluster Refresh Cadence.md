---
type: spoke
title: "Cluster Refresh Cadence"
domain: "Blog Topic Architecture"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [clusters, semantic-clusters, active]
confidence: advisory
---

# Cluster Refresh Cadence

## Cadence Owner

This note sets review timing for a cluster's hub, spokes, links, evidence, and outcome metrics. It prevents a cluster from looking complete while its source posture or internal links quietly decay.

### Event Driven Refreshes

Refresh immediately when Google changes relevant Search guidance, a cluster page loses its canonical role, a source ID passes its refresh window, or first-party data contradicts a recommendation. The official ranking-history source is for confirmed Google rollout status, not third-party impact analysis. Source ID: `g-ranking-history`.

### Scheduled Refreshes

For stable clusters, use a monthly source scan, quarterly link and intent review, and annual hub rewrite review. Faster cadence is justified for YMYL, volatile AI guidance, or pages that inform revenue decisions. Source IDs: `g-helpful-content`, `g-ai-opt-guide`.

## Refresh Timing Table

| Asset or signal | Normal cadence | Triggered cadence | Evidence to check | Source IDs |
|---|---|---|---|---|
| Hub page | Quarterly | Major Search guidance change or cannibalization flag | Reader promise, source dates, spoke map | `g-helpful-content`; `g-ranking-history` |
| Spoke page | Quarterly to semiannual | Query shift, stale claim, or duplicate intent | Intent fit and cited source freshness | `g-helpful-content` |
| Source ID | Monthly | Refresh date due or source guidance changed | Last verified date and claim family | `g-helpful-content`; `g-ranking-history` |
| Confirmed update window | After completion | Google status dashboard records a rollout | Affected assumption and review delay | `g-ranking-history` |
| AI guidance caveat | Monthly | Google updates AI optimization wording | llms.txt and special-file language | `g-ai-opt-guide`; `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` |
| Market context | Monthly while volatile | New zero-click or AI visibility study | Caveats in [[AI Citation Mechanics]] | `sparktoro-zero-click-2026` |
| Query-page split | Reporting cycle | GSC shows a new competing page pattern | Query, page, CTR, and position rows | `g-gsc-api` |
| Internal links | Quarterly | Hub, URL, or owner changes | Anchor, direction, and destination | `g-helpful-content` |

## Cadence Runbook

1. Open [[Research Pack Index]] and list source IDs whose refresh date is due.
2. Check whether [[2026 Google Update Timeline]] changes the cluster's assumptions.
3. Inspect hub and spoke anchors for stale ownership language.
4. Compare recent property data with the prior review period when available.
5. Assign each page keep, refresh, consolidate, monitor, or source-needed.

## Cadence Example

A cluster about AI search tactics cites Google AI guidance and a practitioner visibility study. Source IDs: `g-ai-opt-guide`, `sparktoro-zero-click-2026`.

The official AI guidance receives a monthly check because special-file advice changes quickly. Source ID: `g-ai-opt-guide`.

The market study is checked only as context and kept in [[AI Citation Mechanics]]. Source ID: `sparktoro-zero-click-2026`.

If the ranking dashboard confirms a broad rollout, the cluster waits for completion before assigning cause. Source ID: `g-ranking-history`.

If GSC later shows a spoke taking hub queries, the cadence changes from scheduled review to cannibalization review. Source ID: `g-gsc-api`.

The calendar slot becomes refresh or monitor only after the evidence path is named. Source ID: `g-helpful-content`.

## Cadence Mistakes

- Refreshing during an active rollout can confuse volatility with page-level failure. Source ID: `g-ranking-history`.
- Rewriting every quarter without changed evidence creates churn without reader benefit. Source ID: `g-helpful-content`.
- Updating only the hub can leave stale source claims inside supporting spokes. Source ID: `g-helpful-content`.
- Treating market studies as triggers for all pages overstates their property relevance. Source ID: `sparktoro-zero-click-2026`.
- Missing GSC access should create a data task, not an invented trend note. Source ID: `g-gsc-api`.

## Calendar Feed

[[Editorial Calendar Planning Matrix]] consumes asset type, normal cadence, triggered cadence, evidence check, and owner. Source IDs: `g-helpful-content`, `g-ranking-history`.

The expected output is a calendar row marked new, refresh, consolidate, or monitor with a review trigger. Source IDs: `g-gsc-api`, `g-helpful-content`.

## Staleness Signals

A cluster is stale when it cites outdated Search guidance, uses a market study as if it were property evidence, or still points readers to a page whose intent has changed. Cadence is a risk control, not a license to rewrite pages on a calendar when no evidence changed.
