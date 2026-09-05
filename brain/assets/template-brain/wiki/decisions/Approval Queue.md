---
type: "decision"
title: "Approval Queue"
created: "{{date}}"
updated: "{{date}}"
status: "active"
domain: "Blog Content Brain"
tags: [decisions, active]
---

# Approval Queue

No action is approved until it has source, confidence, owner, status, and rollback.

## Queue

| Action | Source | Confidence | Owner | Status | Rollback |
|---|---|---:|---|---|---|
| Replace this example after source intake | [[Source Manifest Guide]] | low | {{owner}} | proposed | Do nothing |

Related: [[Action Roadmap]] | [[Best Practices Kernel]]
## Decision states

| State | Meaning | Who can advance it |
|---|---|---|
| proposed | An action is described but not authorized | Owner |
| needs evidence | Scope or consequence is not yet grounded | Research owner |
| needs decision | Evidence is sufficient and a choice remains | Owner |
| approved | Exact action and blast radius are authorized | Owner |
| executing | Approved local work is in progress | Assigned operator |
| verified | Named completion gate passed | Reviewer |
| rejected | Owner declined the action | Owner |
| superseded | A later decision replaced it | Owner |
| blocked | Required authority or dependency is unavailable | Owner or dependency |
| rolled back | The approved change was reversed | Operator and reviewer |

## Required queue fields

1. Decision ID.
2. Exact proposed action.
3. Target path, system, or account.
4. Expected outcome.
5. Source or evidence.
6. Confidence tag.
7. Owner.
8. Reversibility.
9. Blast radius.
10. Verification gate.
11. Expiry or review date.
12. Current state.

## Evidence packet

| Field | Reviewer question |
|---|---|
| Problem | What observed condition requires a decision? |
| Options | Which mutually exclusive choices exist? |
| Recommendation | Which option is preferred and why? |
| Tradeoff | What does the recommendation sacrifice? |
| Risk | What could fail or affect other work? |
| Rollback | How is the prior state restored? |
| Cost | Does the action spend money or quota? |
| External effect | Does it contact, publish, or change an account? |
| Test | What direct evidence closes the action? |
| Expiry | When does this approval stop being safe to reuse? |

## Approval boundaries

Local analysis, explanation, and read-only inspection do not require a queue
entry. Ordinary reversible edits within an approved build request may proceed.

Commit, push, publication, deployment, spending, account changes, permission
changes, third-party contact, destructive deletion, and production mutation
require an explicit decision for the exact target.

Access to a credential or tool is not approval.

## Reviewer checklist

- The target is unambiguous.
- The action is the smallest useful unit.
- Unrelated work is protected.
- The evidence is current.
- Alternatives are decision-relevant.
- Risks are not hidden.
- The rollback is practical.
- The completion gate is direct.
- External effects are named.
- The decision has not expired.

## Execution record

When an approved action begins, record who is acting, the start time, and the
pre-change state. Keep command output free of secrets. If scope changes, return
the item to needs decision rather than stretching the old approval.

## Closeout record

A verified item records the exact check, exit state, artifact or account state,
and reviewer. A rolled-back item records why verification failed and whether
follow-up is still required.

## Example queue item

| Field | Value |
|---|---|
| Action | Build a local sanitized public preview |
| Target | Isolated output directory |
| Evidence | Publishing notice and sanitizer tests |
| Reversibility | Delete the generated preview |
| External effect | None, local only |
| Gate | Manifest, secret scan, and path scan pass |
| State | proposed until the owner requests the build |

Publishing that preview is a separate decision. The local artifact does not
carry publication approval forward.
