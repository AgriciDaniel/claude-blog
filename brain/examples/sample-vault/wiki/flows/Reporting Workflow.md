---
type: "flow"
title: "Reporting Workflow"
created: "2026-08-25"
updated: "2026-08-25"
status: "active"
domain: "Blog Content Brain"
tags: [flows, reports, active]
---

# Reporting Workflow

1. Read [[Health Scorecard]] and [[Action Roadmap]].
2. Confirm every claim points to a source note or raw hash.
3. Render [[Weekly Report]].
4. Remove local paths and private data before sharing.

Related: [[Weekly Report]] | [[Approval Queue]]
## Reporting trigger

Run reporting on the agreed cadence, after a material gate changes, or before a
handoff. A report describes evidence and decisions, not activity volume.

## Inputs

| Input | Minimum record |
|---|---|
| Scorecard | Status, evidence, date, owner |
| Roadmap | Current action and next checkpoint |
| Approval queue | Pending consequential decisions |
| Source manifest | New and refreshed evidence |
| Verification log | Commands, exit states, counts |
| Incident notes | Failures and rollback state |
| External status | Directly verified live state only |
| Human review | Reviewer, scope, outcome |

## Preparation steps

1. Freeze the reporting period and timezone.
2. Read the previous report.
3. Sample scorecard evidence links.
4. Re-run volatile checks when due.
5. Reconcile roadmap states with verification.
6. Separate implemented, verified, accepted, and released.
7. Identify new blockers.
8. Record pre-existing failures separately.
9. Remove secrets and personal identifiers.
10. Draft the summary last.

## Claim language

| Evidence | Allowed wording |
|---|---|
| Local diff | implemented locally |
| Focused test | focused test passed |
| Full suite | repository suite passed |
| Isolated package | package built and scanned |
| Human review | accepted by named reviewer |
| Live URL | live state verified at a date |
| Missing gate | not verified |
| External dependency | awaiting owner or provider |

## Report structure

### Outcome

Lead with what changed for the operator or buyer.

### Evidence

List direct commands, artifacts, source decisions, and review dates.

### Risks

Name blast radius, remaining uncertainty, and rollback.

### Decisions

Present only choices that require the owner.

### Open items

Keep genuine gaps visible. Do not move them into vague future work.

## Quality checks

- Every number has a denominator or test count.
- Every source claim has a date.
- Every status matches its gate.
- Every blocker names a dependency.
- Every external claim has direct evidence.
- Every skipped check is stated.
- Every recommendation names a tradeoff.
- Every local path is removed from public prose.
- Every rights-sensitive artifact is excluded.
- Every secret scan reports no raw value.

## Failure patterns

- Reporting files changed instead of outcomes.
- “All good” hides skipped checks.
- Authorization is described as execution.
- A stale source date is copied forward.
- A failing gate is called pre-existing without evidence.
- A market statistic is presented as property data.
- A generated artifact is assumed deterministic.
- A long chronology hides the current decision.

## Review handoff

The report owner compares [[Weekly Report]] to [[Health Scorecard]] and
[[Action Roadmap]]. The decision owner sees [[Approval Queue]] separately.

## Rollback

If the report overstates evidence, correct it immediately, preserve the reason,
and notify only the same audience that received the incorrect report. Do not
change the underlying evidence to make the report appear right.
