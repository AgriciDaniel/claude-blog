---
type: spoke
title: "Update Timestamp Policy"
domain: "Blog Rewriting"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [rewriting, freshness, content-decay, active]
---

# Update Timestamp Policy

## Timestamp Rule Scope

This policy decides when a visible "updated," "reviewed," or "published" date change is justified in an advisory rewrite plan. It does not change the CMS date. The purpose is to preserve reader trust and avoid cosmetic freshness signals.

`g-helpful-content` supports the trust standard: dates should reflect meaningful review or change, not decoration. `g-ranking-history` and `g-status-dashboard` provide official context when an article is updated because Google documentation or a confirmed rollout changed. `g-update-2024-06-20-june-2024-spam-update` is a model for citing a specific dated update record without implying site-level impact.

### Date Changes Allowed And Blocked

Allowed advisory actions include recommending a reviewed date after source verification, recommending an updated date after substantive content changes, and preserving the original published date when the article's creation date still matters.

Disallowed actions include changing a date because traffic declined, because a competitor uses newer dates, because a generic rewrite pass touched wording, or because an unconfirmed update rumor created pressure.

### Timestamp Exceptions Requiring Approval

Escalate date changes for legal, financial, medical, or other trust-sensitive content; syndicated posts; live event coverage; and articles whose visible date is part of a contractual or editorial policy.

## Timestamp Rule Table

| Rule | Evidence source | Applies to | Enforcement | Approval path |
|---|---|---|---|---|
| Keep original published date when the article origin matters | `g-helpful-content` | Historical explainers, event recaps, dated announcements | Do not replace history with freshness theater | Editor approves wording |
| Add reviewed date when claims were checked but prose barely changed | `g-helpful-content` | Evergreen guides with source validation | Record checked source IDs and reviewer | Source steward plus editor |
| Add updated date only after substantive change | `g-helpful-content` | New sections, changed recommendations, replaced evidence | Link to decision and QA note | Content lead approves |
| Cite official update context only from official sources | `g-ranking-history`; `g-status-dashboard` | Articles referencing Google rollouts | Use dated event wording, avoid causality claims | Monitoring owner reviews |
| Treat specific spam-update references as dated records | `g-update-2024-06-20-june-2024-spam-update` | Historical update notes or spam-policy context | State the event date and source limit | SEO strategist reviews |
| Do not change dates for unconfirmed volatility | `g-status-dashboard` | Traffic dips without confirmed event | Keep date unchanged and route to monitoring | Program owner can defer |
| Preserve date after typography-only work | `g-helpful-content` | Copyedits, formatting, internal housekeeping | No visible freshness signal | Editor records no-date-change |
| Update schema dates only from visible facts | `g-intro-sd` | Article or BlogPosting handoff | Date values must match page evidence | Technical SEO reviews |

## Timestamp Audit And Reversal

1. Name the visible date field under review: published, updated, reviewed, or editorial note.
2. Record the exact work performed and the source IDs checked.
3. Choose no date change when the work was only formatting, typo repair, or internal workflow cleanup.
4. Add a rollback cue: revert the visible date if QA finds the change was cosmetic or unsupported.

## Date Choice Example

Before: an editor wants a new updated date after typo fixes.
`g-helpful-content` supports trust, not cosmetic freshness.
Decision: keep the visible dates unchanged.
Later, an AI guidance claim is replaced using `g-ai-opt-guide`.
That source change can justify a reviewed date if QA confirms scope.
Schema date fields still need visible-page support under `g-intro-sd`.

## Timestamp Abuse Cases

- Traffic decline alone does not justify a visible date change.
- Competitor freshness pressure is not evidence under `g-helpful-content`.
- Update names need official dates from `g-ranking-history`.
- Schema dates must not invent facts absent from the article.

## Schema Contract Wiring

[[Schema Generation Output Contract]] consumes the approved date decision.
Inputs provided: published date, modified date, reviewed date, and no-change reason.
It expects schema date values or warnings when page facts are missing.
Visible-content checks use `g-intro-sd`; trust checks use `g-helpful-content`.

## Timestamp Source IDs

`g-helpful-content`; `g-ranking-history`; `g-status-dashboard`; `g-update-2024-06-20-june-2024-spam-update`; `g-intro-sd`; `g-ai-opt-guide`.

## Related

- [[Source Refresh Workflow]]
- [[Rewrite QA Checklist]]
- [[Stale Claim Register]]
- [[Google Algorithm Update Ledger]]
- [[2026 Google Update Timeline]]
