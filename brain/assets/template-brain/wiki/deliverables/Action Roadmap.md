---
type: "deliverable"
title: "Action Roadmap"
created: "{{date}}"
updated: "{{date}}"
status: "active"
domain: "Blog Content Brain"
tags: [deliverables, active]
---

# Action Roadmap

## Next 30 Days

- Complete source intake and research refresh.
- Replace scaffold assumptions with sourced domain notes.
- Run release lint and package scans.

Related: [[Health Scorecard]] | [[Approval Queue]] | [[Synthesis Workflow]]
## Roadmap construction rules

A roadmap turns evidence into ordered work. It is not a wish list and does not
convert uncertain outcomes into deadlines.

1. Start from verified gaps.
2. Group work by dependency, not by department.
3. Put safety and evidence gates before optimization.
4. Name one owner per action.
5. Define a direct completion check.
6. Separate local work from external decisions.
7. Preserve rollback for generated or destructive changes.
8. Mark assumptions that could change sequencing.
9. Use date ranges only when capacity is known.
10. Replan when evidence changes.

## Priority model

| Priority | Definition | Example |
|---|---|---|
| P0 | Safety, data loss, secret, or release blocker | Exposed credential |
| P1 | Requested outcome cannot work | Broken install |
| P2 | Quality or maintainability risk | Stale source boundary |
| P3 | Useful improvement with no current failure | Optional navigation polish |

Severity and effort are separate. A small P0 fix stays ahead of a large P2
initiative. A costly action still needs owner approval.

## Action card

Each roadmap action records:

- Action ID.
- Desired outcome.
- Evidence for the gap.
- In-scope files or systems.
- Explicit exclusions.
- Prerequisites.
- Owner.
- Supporting reviewer.
- Confidence tag.
- Expected effort band.
- Verification command or review.
- Rollback.
- External decision boundary.
- Current state.
- Next checkpoint.

## Dependency lanes

| Lane | Entry gate | Exit gate |
|---|---|---|
| Evidence | Claim or defect is reproducible | Scope and source are confirmed |
| Safety | Secret, path, rights, and rollback checked | No blocking risk remains |
| Implementation | Plan and ownership are clear | Focused checks pass |
| Integration | Dependent surfaces are updated | Broader checks pass |
| Release | Artifacts are deterministic and scanned | Release review passes |
| External | Owner authorizes the action | Live state is verified |

## Thirty-day planning frame

### Days 1 to 5

Confirm sources, reproduce defects, protect existing work, and close P0 risks.

### Days 6 to 12

Implement the narrowest P1 fixes with focused tests.

### Days 13 to 20

Run integration, content, and currentness reviews. Correct contradictions.

### Days 21 to 26

Build isolated artifacts, verify determinism, and complete human review.

### Days 27 to 30

Present remaining external decisions. Do not publish or deploy by assumption.

## Progress language

Use complete only when the exit gate passed. Use implemented when code exists
but broader verification remains. Use blocked only when a named dependency
prevents meaningful progress. Use deferred when the owner intentionally leaves
work out of scope.

## Replanning triggers

- A primary source contradicts the planned tactic.
- A focused test exposes a wider contract.
- User-owned changes overlap the target.
- A dependency version changes.
- The rollback is no longer safe.
- An external approval expires.
- The requested outcome changes.
- The implementation becomes a separate product decision.

## Roadmap review

At each checkpoint, remove completed actions, update evidence dates, preserve
failed attempts that affect the next approach, and keep only one current action
per owner.

## Delivery handoff

The roadmap ships with [[Health Scorecard]], [[Approval Queue]], and the exact
verification evidence. It names skipped live or human gates and never describes
authorization as execution.
