---
type: spoke
title: "Content Decay Detection"
domain: "Blog Rewriting"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [rewriting, freshness, content-decay, active]
---

# Content Decay Detection

## Detection Refresh Job

Content decay detection separates a real deterioration pattern from normal search noise. The output is a diagnosis, not a rewrite order. It should say whether the page has lost demand, lost relevance, lost source trust, been split across competing URLs, or needs no action.

`g-gsc-api` is the main measurement source because the Search Analytics API exposes query and page dimensions with clicks, impressions, CTR, and position. `g-helpful-content` frames the qualitative review: stale pages are not just pages with worse numbers, they are pages that no longer help the reader complete the task. `g-ranking-history` checks whether a confirmed Google rollout overlaps the review window, and `g-canonical` helps identify duplicate or competing URL signals before anyone rewrites copy.

### Decay Signal Owned Here

This note owns the first-pass classification of decline signals: demand shift, ranking loss, CTR change, query mix change, source age, intent mismatch, and URL duplication. It does not own the final action. Route action selection to [[Refresh Versus Rewrite Decision]], merge questions to [[Content Consolidation Rules]], and stale evidence to [[Stale Claim Register]].

### Rewrite Versus Consolidate Versus Prune Boundary

Rewrite when the page still owns the reader job but the answer is incomplete. Consolidate when another URL already serves the same job better. Prune only after helpful content review, GSC evidence, and canonical checks show that neither readers nor the site architecture need the page.

## Decay Diagnosis Table

| Reviewed URL | Primary signal | Source freshness | Action | Owner | Rollback cue |
|---|---|---|---|---|---|
| Post losing clicks while impressions hold | CTR or SERP presentation changed | `g-gsc-api` pulled for matched periods | Send to snippet and title review before rewrite | Analyst | CTR recovers without content edits |
| Post losing impressions and average position | Query coverage or ranking visibility changed | `g-gsc-api`; compare against `g-ranking-history` | Check confirmed update window, then review answer completeness | SEO strategist | Decline does not persist after rollout window |
| Post still ranks but claim dates are old | Evidence age weakens trust | `g-helpful-content` plus source ledger dates | Send claims to [[Stale Claim Register]] | Source steward | Source refresh confirms old claim remains valid |
| Two URLs split related queries | Competing page and query dimensions | `g-gsc-api`; technical check from `g-canonical` | Move to [[Content Consolidation Rules]] | Content lead | One URL clearly serves a different reader job |
| Page has no meaningful search history | Thin or unmeasured asset | `g-gsc-api` unavailable or sparse | Defer, annotate data gap, avoid false precision | Program owner | New first-party data appears |
| Impressions fall while position holds | Demand or query mix changed | `g-gsc-api` query rows by matched window | Check demand and intent before rewriting | Analyst | Next matched window stabilizes |
| Canonical target changes unexpectedly | URL ownership changed | `g-canonical` plus page export | Pause prose edits and route URL review | SEO technical owner | Preferred URL returns to expected page |

## Verification Procedure

1. Compare at least two equivalent date windows and record the property, country, device, and page filter.
2. Label the strongest signal before recommending work: demand, ranking, CTR, intent, source, duplicate URL, or data gap.
3. Check [[Google Algorithm Update Ledger]] only for confirmed rollout context, not for speculative volatility.
4. Assign the next note owner so the detection record does not become an all-purpose rewrite checklist.
5. Record what would disprove the diagnosis during the next measurement pass.

## Detection Walkthrough

Example input: a glossary page loses clicks but keeps impressions.
Query rows from `g-gsc-api` show demand moved toward checklist language.
The page still answers its definition job under `g-helpful-content`.
Diagnosis: intent drift, not full content decay.
Next step: send the case to [[Intent Drift Audit]].
Do not cite a confirmed update unless `g-ranking-history` dates overlap.

## Misread Signals

- Average position can mask query churn; inspect queries through `g-gsc-api`.
- Canonical changes can mimic decay; verify URL signals with `g-canonical`.
- Old citations are trust risk, not performance proof; use `g-helpful-content`.
- Official rollout dates explain timing only; use `g-ranking-history` carefully.

## Triage Register Wiring

[[Content Decay Triage Register]] consumes the diagnosis row from this note.
Inputs provided: URL, signal label, evidence source, owner, and rollback cue.
It expects status output: refresh brief, investigate, consolidate plan, monitor, or escalate.
Data fields come from `g-gsc-api`; update annotations come from `g-ranking-history`.

## Decay Source IDs

`g-gsc-api`; `g-helpful-content`; `g-ranking-history`; `g-canonical`.

## Related

- [[Freshness and Content Decay]]
- [[Refresh Versus Rewrite Decision]]
- [[Content Consolidation Rules]]
- [[Stale Claim Register]]
- [[Google Data Integrations]]
