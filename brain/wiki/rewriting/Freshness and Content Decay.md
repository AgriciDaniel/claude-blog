---
type: hub
title: "Freshness and Content Decay"
domain: "Blog Rewriting"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [rewriting, freshness, content-decay, active]
---

# Freshness and Content Decay

## Operating Scope

This hub coordinates the refresh, rewrite, consolidation, pruning, and rollback notes in the rewriting folder. It is the map for deciding whether a published blog asset still helps the reader and still has source support. It is not a promise that any rewrite will recover rankings, clicks, AI visibility, or rich results.

`g-helpful-content` is the quality baseline for deciding whether the page remains useful. `g-gsc-api` supports first-party performance review when property data is available. `g-ranking-history` keeps update language tied to official Google history, and `g-canonical` routes duplicate URL concerns away from pure editorial rewriting.

### What This Hub Owns In Refresh, Rewrite, And Decay Workflows

The hub owns the decision vocabulary, handoff order, and evidence standard for the folder. A good refresh decision names the content unit, the reader job, the dated source state, the observed performance or trust issue, and the next note that owns the operational work.

### What The Hub Must Not Absorb

This hub should not become a duplicate of [[Google Data Integrations]], [[Blog Quality Score]], [[Blog Schema Stack]], or [[Google Algorithm Update Ledger]]. It can link to those notes, but it should not restate every metric, schema rule, or confirmed update entry.

## Spoke Map

| Spoke | Job boundary | Required input | Source IDs | Evidence state | Next action |
|---|---|---|---|---|---|
| [[Content Decay Detection]] | Diagnose whether decline is real | Page, query, period, source age | `g-gsc-api`; `g-helpful-content` | Confirmed data source, advisory interpretation | Label the signal before action |
| [[Historical Performance Review]] | Compare past and current performance | Matched windows and known events | `g-gsc-api`; `g-ranking-history` | First-party data plus official update context | Explain the trend window |
| [[Intent Drift Audit]] | Test whether reader intent moved | Current page promise and query set | `g-helpful-content`; `g-gsc-api` | Mixed qualitative and first-party evidence | Assign a new or unchanged intent |
| [[Content Consolidation Rules]] | Decide whether overlap needs one URL | Candidate URLs and canonical signals | `g-canonical`; `g-gsc-api` | Technical source plus property evidence | Pick retained URL or defer |
| [[Stale Claim Register]] | Track claims needing source refresh | Claim, source ID, owner, due date | `g-helpful-content` | Claim-level review | Refresh, remove, or caveat |
| [[Rewrite Rollback Notes]] | Define reversal triggers | Approved change and measurement cue | `g-ranking-history`; `g-helpful-content` | Advisory rollback logic | Set observation window |
| [[Decay Segment Prioritization]] | Rank queued decay cases | Diagnosis rows and source risk | `g-helpful-content`; `g-gsc-api` | Prioritization, not treatment | Choose queue order |
| [[Refresh Versus Rewrite Decision]] | Pick treatment class | Diagnosis, intent, claims, URL risk | `g-helpful-content`; `g-canonical` | Decision-ready packet | Select one action |
| [[Source Refresh Workflow]] | Revalidate evidence before edits | Claim list and current source IDs | `g-helpful-content` | Source-steward record | Keep, update, remove, or escalate |
| [[Rewrite QA Checklist]] | Block unsafe changed drafts | Draft, claim list, baseline cue | `g-helpful-content`; `g-ranking-history` | Pre-handoff review | Approve or return |
| [[Pruning Advisory Checklist]] | Test removal recommendation | Candidate URL and retained value | `g-helpful-content`; `g-gsc-api` | Advisory only | Recommend or reject prune |
| [[Update Timestamp Policy]] | Judge visible date changes | Work performed and checked sources | `g-helpful-content`; `g-status-dashboard` | Trust review | Keep, reviewed, or updated |

## Evidence And Refresh Rules

1. Prefer first-party page and query evidence over market averages when available.
2. Tie algorithm language to official confirmed history rather than community volatility.
3. Treat canonical, redirect, and duplicate URL questions as technical handoffs, not prose edits.
4. Date every Google or policy claim that could age, then send stale claims to [[Stale Claim Register]].
5. Keep V1 outputs advisory and read-only toward CMS, Search Console, analytics, and publishing tools.

## Folder Route Example

A comparison post loses one query family in `g-gsc-api`.
The hub first sends the signal to [[Content Decay Detection]].
If the reader job changed, [[Intent Drift Audit]] owns the reframing.
If old claims remain, [[Source Refresh Workflow]] updates evidence first.
[[Refresh Versus Rewrite Decision]] then chooses refresh, rewrite, or defer.
[[Rewrite Rollback Notes]] records the review window before handoff.

## Hub-Level Misroutes

- Do not send every stale date to rewriting; check source risk first.
- Do not fold canonical work into prose; `g-canonical` needs its owner.
- Do not turn update timelines into blame; use `g-ranking-history` for dates.
- Do not make the hub a scorecard; quality scoring stays elsewhere.

## Rewrite Plan Wiring

[[Blog Rewrite Refresh Plan]] consumes the hub's ordered handoff path.
Inputs provided: content unit, reader job, evidence state, and next-note owner.
It expects phase outputs for decay triage, source replacement, rebuild, and rollback.
The plan's measured fields use `g-gsc-api`; trust review uses `g-helpful-content`.

## Hub Source IDs

`g-gsc-api`; `g-helpful-content`; `g-ranking-history`; `g-canonical`; `g-status-dashboard`.

## Related

- [[Google Data Integrations]]
- [[Google Algorithm Update Ledger]]
- [[Blog Quality Score]]
- [[Research Pack Index]]
- [[AI Citation Mechanics]]
