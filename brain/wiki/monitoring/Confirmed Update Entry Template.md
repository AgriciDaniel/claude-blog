---
type: spoke
title: "Confirmed Update Entry Template"
domain: "Google Update Monitoring"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [monitoring, google-updates, active]
source_urls:
  - "https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history"
---

# Confirmed Update Entry Template

## Confirmed Update Entry Template Distinct Job

This template defines the minimum fields required before a Google update becomes operating guidance in this brain. It prevents a loose update mention from becoming advice. Use it inside [[Google Algorithm Update Ledger]], year timelines, and response playbooks whenever a new ranking, spam, QRG, schema, or AI-search event is added.

## Inputs Specific To Confirmed Update Entry Template

- Exact update name as recorded by Google or the local ledger.
- Start date, completion date when available, and surface.
- Source ID from `references/source-ledger.json`.
- Evidence verdict using the claim-ledger language: CONFIRMED, AS-REPORTED, SINGLE-SOURCE, CONTESTED, or FOLKLORE.
- Follow-up route and rollback trigger.

## Decisions Confirmed Update Entry Template Must Record

The template decides whether an event is eligible for durable guidance. `g-ranking-history` and `g-status-dashboard` are sufficient for chronology, but they are not enough for site-level diagnosis. `g-update-2024-06-20-june-2024-spam-update` and `g-update-2024-11-11-november-2024-core-update` show the difference between an event record and an action plan: one names a spam rollout, the other marks a core rollout duration.

## Confirmed Update Entry Template Field Table

| Required field | Accepted evidence | Source IDs | Reject when | Owner | Next action |
|---|---|---|---|---|---|
| Event name | Google dashboard title or local ledger title | `g-ranking-history`, `g-status-dashboard` | Name comes only from a third-party volatility tool | Monitoring owner | Add the event to the right timeline. |
| Event dates | Published, start, complete, or last-updated date | `g-update-2024-06-20-june-2024-spam-update`, `g-update-2024-11-11-november-2024-core-update` | Date is inferred from ranking movement | SEO lead | Record exact windows for later impact analysis. |
| Surface and lane | Core, spam, schema, QRG, AI search, Discover, or reporting | Event-specific `g-update-*` ID | Surface is collapsed into "algorithm update" | Topic owner | Route to the matching spoke note. |
| Evidence verdict | Claim-ledger verdict or official-source confidence | Any cited source ID | The note upgrades a weak source to confirmed | Reviewer | Downgrade or quarantine the claim. |
| Action boundary | Read-only recommendation and rollback condition | Relevant playbook note | The entry mutates CMS, GSC, GA4, or schema directly | Operator | Write an advisory next step only. |
| Completion state | Complete date, active rollout note, or unavailable status | `g-ranking-history`, `g-status-dashboard` | Completion is inferred from traffic movement | Monitoring owner | Mark watch-only until the source resolves. |
| Source limitation | What the cited source does not prove | Event-specific `g-update-*` ID | Limitation is omitted from a deliverable handoff | Reviewer | Add caveat before routing the entry. |

## Confirmation Failure Cases

An entry stays out of the confirmed ledger when the only evidence is a rank-tracker screenshot, a forum thread, or a vendor summary with no Google-owned source. It can still live in [[Unverified Volatility Quarantine]] if it is useful to watch. A confirmed event also needs a limitation statement: event existence can be confirmed while affected queries, affected pages, and recovery tactics remain unproven.

## Confirmed Update Entry Template Operating Procedure

1. Fill the five required fields before linking the event from a timeline.
2. Attach the exact source IDs in the entry table, not a generic URL bundle.
3. Assign one route note and one owner for the next review.
4. If the source changes, update the entry and record the stale claim as a refresh task.

## Filled Entry Example

Event name: May 2026 Core Update.
Dates: start 2026-05-21, complete 2026-06-02.
Source IDs: `g-update-2026-05-21-may-2026-core-update`, `g-update-2026-06-02-may-2026-core-update-complete`.
Verdict: CONFIRMED for chronology, not for page-level impact.
Route: [[Core Update Response Playbook]] before any rewrite recommendation.
Rollback trigger: dashboard date changes or first-party evidence contradicts the planned action.
The deliverable consumer is [[Factcheck Claim Register]].
It receives claim wording, source IDs, verdict, confidence, owner, and refresh date.
It should output verified, stale, blocked, or pending status before the claim leaves monitoring.

## Template-Specific Failure Checks

- A dashboard title without completion state cannot support a post-update window.
- A vendor volatility name cannot become the event name after `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice`.
- A source ID that proves chronology does not prove affected pages.
- A missing rollback trigger makes the entry unusable for delivery contracts.

## Related

- [[Google Algorithm Update Ledger]]
- [[Unverified Volatility Quarantine]]
- [[Update Impact Review]]
- [[Core Update Response Playbook]]
- [[Spam Update Response Playbook]]
