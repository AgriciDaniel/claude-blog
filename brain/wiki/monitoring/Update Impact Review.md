---
type: spoke
title: "Update Impact Review"
domain: "Google Update Monitoring"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [monitoring, google-updates, active]
source_urls:
  - "https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history"
  - "https://developers.google.com/webmaster-tools/v1/searchanalytics/query"
---

# Update Impact Review

## Update Impact Review Distinct Job

This spoke joins confirmed update dates to first-party page performance and source refresh needs. It is the first place where a monitoring event can become a site-specific recommendation. It still stays read-only: it compares evidence, writes findings, and routes next actions without changing analytics, Search Console, CMS content, or schema.

## Inputs Specific To Update Impact Review

- Confirmed update ID, type, start date, and completion date.
- Page group, query group, country, device, and Search type when first-party data exists.
- Pre/post comparison windows that do not overlap the active rollout unless the purpose is watch-only.
- Source refresh notes when a claim or source has changed.

## Decisions Update Impact Review Must Record

The review decides whether first-party evidence justifies content, spam, schema, AI-search, or no-action follow-up. `g-update-2024-06-20-june-2024-spam-update` routes to policy checks only if the affected pages have policy risk. `g-update-2024-11-11-november-2024-core-update` routes to quality review only if the page-group pattern supports it. `g-gsc-api` can support query and page comparison, but missing data should be disclosed rather than filled with market averages.

## Update Impact Review Update Entry Table

| Review decision | Required input | Source IDs | Evidence state | Owner | Next action |
|---|---|---|---|---|---|
| Define event window | Confirm update start and completion dates | `g-ranking-history`, `g-status-dashboard` | CONFIRMED chronology | Monitoring owner | Create pre/post windows and note exclusions. |
| Spam-adjacent movement | Pages move near a confirmed spam update and show policy risk | `g-update-2024-06-20-june-2024-spam-update`, `g-spam-policies` | MIXED until local proof | Spam reviewer | Open [[Spam Update Response Playbook]] only with evidence. |
| Core-adjacent movement | Page group changes after a confirmed core rollout | `g-update-2024-11-11-november-2024-core-update`, `g-ranking-history` | MIXED until local proof | SEO lead | Run quality and intent review before rewriting. |
| Query and page comparison | GSC export or API result exists for affected dimensions | `g-gsc-api` | FIRST-PARTY when property export exists | Data owner | Compare pages, queries, countries, devices, and Search type. |
| No action | Movement is absent, noisy, or outside source scope | Event source plus data note | LOW or no local evidence | Reviewer | Record no-action with next review date. |
| Control group comparison | Stable pages share topic, template, and reporting dimensions | `g-gsc-api` | FIRST-PARTY when export exists | Data owner | Separate site pattern from isolated page noise. |
| Generative-AI report check | Search Console AI reports are available for the property | `g-genai-reports` | CONFIRMED source, property access needed | Analyst | Route AI visibility questions to the AI watch lane. |

## Evidence Window Rules

Use complete rollout windows when possible. For long rollouts, do not call the first day a full post-update period. For small page sets, treat direction as a clue, not proof. If Search Console generative-AI reporting is available, route AI Overview or AI Mode visibility questions to [[AI Search Update Watch]] and [[Google Data Integrations]].

## Update Impact Review Operating Procedure

1. Confirm the update and choose a pre/post window that respects rollout timing.
2. Pull read-only first-party evidence when available and record dimensions used.
3. Compare affected page groups against unaffected controls or historical baselines.
4. Route findings to core, spam, schema, AI-search, content refresh, or no action.
5. Attach source IDs, data limits, owner, and rollback condition to every recommendation.

## Impact Review Walkthrough

A product blog section drops impressions after the May 2026 core update.
The review cites `g-update-2026-05-21-may-2026-core-update` for the event.
It cites `g-update-2026-06-02-may-2026-core-update-complete` for the closed window.
The analyst pulls pages, queries, country, device, and Search type with `g-gsc-api`.
Two comparison pages outside the product section stay flat.
The affected posts also have expired source claims, so rewrite planning is plausible.
The consumer is [[Blog Rewrite Refresh Plan]].
It receives URLs, query sets, date windows, source IDs, comparison notes, and caveats.
It should output scoped refresh tasks, monitor decisions, or no-action rows.

## Impact Review Failure Modes

- A pre/post window that overlaps rollout dates weakens the causal story.
- Mixing countries or devices can create false decline patterns in `g-gsc-api` exports.
- Treating `g-ranking-history` as proof of impact skips the first-party evidence step.
- AI visibility questions need `g-genai-reports` availability before report language changes.

## Related

- [[Google Algorithm Update Ledger]]
- [[Google Data Integrations]]
- [[Core Update Response Playbook]]
- [[Spam Update Response Playbook]]
- [[AI Search Update Watch]]
