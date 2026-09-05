---
type: flow
title: "Explore Plan Code Commit"
status: active
created: 2026-08-25
updated: 2026-08-25
tags: [engineering, verification, flow]
domain: "Blog Content Brain"
confidence: verified
related:
  - "[[Quality Gate Failure Modes]]"
  - "[[Delivery Contract Gate]]"
  - "[[Claim Verification Flow]]"
  - "[[Context Compaction Routine]]"
  - "[[Memory Governance Policy]]"
  - "[[Provenance Trace Policy]]"
  - "[[Evidence Gap Register]]"
  - "[[Uncertainty Eval Policy]]"
source_urls:
  - "https://git-scm.com/docs/git-diff"
  - "https://git-scm.com/docs/git-status"
---

# Explore Plan Code Commit

## Trigger

Use this flow for a repository change that spans more than one file, depends on unfamiliar contracts, touches release behavior, or begins from claims in issues and pull requests that have not been verified.

## Prerequisites

- A clear requested outcome.
- The real repository and current branch.
- Read access to code, tests, configuration, and local instructions.
- A recorded dirty-worktree state.
- A reversible edit path.
- A closest reliable verification command.
- Explicit authorization before commit, push, publication, or deployment.
- A stop condition for ambiguous product decisions.

## Steps

### Explore

1. Resolve the actual checkout and current branch.
2. Read repository instructions and named contracts.
3. Inspect status without modifying files.
4. Identify user-owned or concurrent changes.
5. Read the implementation, tests, configuration, and callers.
6. Reproduce the gap with a focused check where possible.
7. Compare issue and pull request claims to repository evidence.
8. Inspect current primary sources for volatile product facts.
9. Record confirmed facts, inferences, suspicions, and unavailable checks.
10. Define the smallest coherent change surface.

### Plan

11. Write outcome-focused steps.
12. Put prerequisite or evidence work before mutation.
13. Identify files owned by the change.
14. State what remains deliberately out of scope.
15. Choose focused tests and broader gates proportional to risk.
16. Preserve a rollback for generated or destructive work.
17. Mark external actions as separate human decisions.
18. Identify release claims that require direct evidence.
19. Set a replan trigger if repeated attempts fail.
20. Keep the plan updated as facts change.

### Code

21. Edit only after reading the relevant pattern.
22. Use the repository’s existing abstractions.
23. Keep untrusted text as data.
24. Add validation at the authority boundary.
25. Fail closed for secrets, unsafe paths, or missing evidence.
26. Write tests for the reported defect and the safe path.
27. Avoid unrelated refactors.
28. Regenerate lockfiles only with the declared tool.
29. Preserve generated-file determinism.
30. Review edits while context is fresh.

### Verify

31. Run syntax or compile checks.
32. Run focused tests.
33. Run type, lint, and build gates where applicable.
34. Run security and secret scans.
35. Run repository consistency checks.
36. Run release packaging in an isolated destination.
37. Validate generated artifacts and hashes.
38. Inspect the final diff against the request.
39. Separate new failures from pre-existing failures.
40. State skipped browser, native, live, or human checks.

### Commit boundary

41. Prepare a Conventional Commit message only when requested.
42. Stage only intended files.
43. Review the staged diff and secret scan.
44. Commit only with explicit authorization.
45. Push or create a pull request only with separate authorization.
46. Never describe an unpushed local commit as published.
47. Never close issues based only on local evidence.

## Outputs

| Output | Evidence |
|---|---|
| Scope statement | Requested outcome and excluded work |
| Repository inventory | Branch, status, contracts, affected code |
| Plan | Ordered steps with one current action |
| Scoped diff | Relevant files only |
| Focused verification | Exact command and result |
| Broad verification | Test, lint, build, audit, package |
| Risk note | Blast radius and rollback |
| Boundary note | Commit, push, deploy, and external status |
| Open items | Genuine remaining work |
| Handoff | Reproducible next action |

## Gates

- Repository instructions were read.
- Dirty work was preserved.
- The defect or gap was evidenced.
- Edits match existing patterns.
- Focused tests cover the change.
- Broad gates match the risk.
- The final diff was inspected.
- No failing check is called green.
- No external action occurred without authorization.
- Rollback remains possible.

## Failure modes

- Editing the wrong checkout.
- Trusting an issue’s diagnosis.
- Overwriting user changes.
- Expanding scope during cleanup.
- Suppressing a failing test.
- Updating a lock without its source declaration.
- Treating static success as live proof.
- Committing unreviewed generated output.
- Pushing because credentials are available.
- Hiding remaining vendor or account work.

## Rollback

Revert only the files owned by the change, using the saved diff or a user-approved version-control operation. Never use a broad destructive reset. If generated outputs are wrong, rebuild from the source declaration after restoring the prior inputs. If a commit exists, recommend reverting that commit rather than rewriting shared history.

## Decision point

A clean local gauntlet authorizes a completion report. It does not authorize commit, push, publication, deployment, third-party contact, spending, or issue closure.
## Evidence ledger

Keep a task-scoped ledger of assumptions, checks, results, and changed decisions.
This prevents repeated exploration and makes replanning explicit.

| Entry | Required detail |
|---|---|
| Assumption | What could change the result |
| Check | Exact read-only or test action |
| Result | Direct observation |
| Decision | Keep, change, or stop |
| Owner | Responsible reviewer |
| Next trigger | Condition for recheck |

Discard noisy command history, but preserve failures that changed the approach.
