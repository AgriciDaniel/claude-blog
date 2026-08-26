---
type: "concept"
title: "Best Practices Kernel"
created: "2026-08-25"
updated: "2026-08-25"
status: "active"
domain: "Blog Content Brain"
tags: [concepts, active]
---

# Best Practices Kernel

Read first. Write second. Verify third.

## Six Cuts

- Read before write.
- Name like the next reader is hostile.
- Ship the smallest unit that works.
- Delete more than you add.
- Evidence over intuition.
- Failure is the spec.

Related: [[Index]] | [[Source Intake Workflow]] | [[Synthesis Workflow]]
## How to apply the kernel

The six cuts are decision rules. They do not replace domain evidence or owner
judgment. Use them to reduce unsupported work before it enters a deliverable.

| Cut | Question | Required evidence | Failure signal |
|---|---|---|---|
| Read before write | Which contract controls this change? | Repository or vault instruction | Editing from memory |
| Hostile naming | Can a new reviewer predict the artifact? | Clear title and path | Clever but ambiguous label |
| Smallest unit | What is the narrowest useful outcome? | Scoped request | Unrelated refactor |
| Delete first | Which assumption can be removed? | Diff or content comparison | Added explanation hides confusion |
| Evidence first | What proves the statement? | Source, test, or decision | Plausible assertion |
| Failure as spec | What must never happen? | Reproduction or risk model | Happy-path-only design |

## Evidence order

1. Direct owner decision for product scope.
2. Current repository behavior for implementation facts.
3. Passing focused test for a local contract.
4. Current primary source for external facts.
5. Standards text for protocol behavior.
6. Original study for reported measurements.
7. Practitioner material for implementation context.
8. Inference, clearly labeled, when evidence is incomplete.

Never upgrade a lower item merely because it is convenient. A confidence label
describes the evidence chain, not the confidence of the writer.

## Working loop

1. State the requested outcome.
2. Locate the real files and current state.
3. Read the contracts that apply.
4. List assumptions that could change the result.
5. Test the most consequential assumption.
6. Try to refute the proposed diagnosis.
7. Choose the smallest coherent edit.
8. Preserve unrelated work.
9. Run the closest reliable check.
10. Inspect the final diff.
11. Report what remains unverified.
12. Ask for a decision only when it changes scope or reversibility.

## Verification classes

| Class | What it proves | What it cannot prove |
|---|---|---|
| Static inspection | Code or prose exists | Runtime behavior |
| Unit test | Focused logic contract | Full integration |
| Integration test | Components cooperate | Production account state |
| Build | Artifact compiles or renders | User acceptance |
| Lint | Declared structural rules | Factual correctness |
| Secret scan | Known credential shapes absent | Rights clearance |
| Browser review | Captured browser behavior | Every device |
| Live check | Current external state | Future stability |

## Stop rules

- Stop when the repository path is uncertain.
- Stop when a destructive target is broad or unresolved.
- Stop when a secret may be printed.
- Stop after repeated failures and return to evidence.
- Stop when a user decision would materially change the solution.
- Stop before commit, push, publish, or deploy without approval.
- Stop a claim when its source proves only part of it.
- Stop a release claim when its named gate was skipped.

## Handoff contract

A useful handoff contains the outcome, scope, changed behavior, verification
commands, failures, skipped checks, rollback, and remaining human decisions.

It does not hide uncertainty in a generic “all good” statement.

## Worked example

A request says a pull request fixed a current Google integration.

The kernel first inspects the actual diff and tests. It then opens the current
Google documentation, looks for a deprecation or changed boundary, and compares
the implementation to that source. If the code is correct but the documentation
claim is stale, the smallest coherent update changes the claim, adds a test for
the dependency boundary, and records the source date.

The final report can say the local gates passed. It cannot say the pull request
was merged or the external service works in production without direct evidence.
