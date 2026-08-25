---
type: "report"
title: "Weekly Report"
created: "{{date}}"
updated: "{{date}}"
status: "active"
domain: "Blog Content Brain"
tags: [reports, active]
---

# Weekly Report

## Summary

This report is a scaffold until source intake and research refresh are complete.

## Evidence

- [[Source Manifest Guide]]
- [[Health Scorecard]]
- [[Action Roadmap]]

Related: [[Reporting Workflow]] | [[Approval Queue]]
## Reporting period

Record start date, end date, timezone, owner, reviewer, and the decision this
report should inform.

## Outcome summary

Use two to four sentences:

1. What changed for the operator.
2. Which direct evidence supports it.
3. What remains incomplete.
4. Which owner decision is next.

## Verification table

| Gate | Command or review | Result | Evidence date | Scope |
|---|---|---|---|---|
| Focused behavior | Replace with exact check | not run | {{date}} | Local |
| Vault structure | Replace with lint command | not run | {{date}} | Local |
| Source currentness | Replace with refresh result | not run | {{date}} | Public sources |
| Secret safety | Replace with scanner | not run | {{date}} | Repository |
| Package | Replace with isolated build | not run | {{date}} | Artifact |
| Human acceptance | Name reviewer and surface | not run | {{date}} | User experience |
| Live status | Name URL or account | not run | {{date}} | External |

## Source changes

For every refreshed claim, record source ID, prior wording, current wording,
decision, and limitation. Do not list a URL load as verification.

## Work completed

Use outcome language. Link each item to [[Action Roadmap]] and its direct gate.

## Work implemented but not fully verified

Keep local code, content, and generated artifacts here until broader gates pass.

## Failures and contradictions

Record the first useful failure, whether it predates the current work, and the
next evidence-led approach. Preserve contradictory sources.

## Decisions required

Pull exact actions from [[Approval Queue]]. Include recommendation, tradeoff,
blast radius, rollback, and approval expiry.

## Risk register

| Risk | Likelihood | Impact | Evidence | Mitigation | Owner |
|---|---|---|---|---|---|
| Stale source | unknown | incorrect guidance | refresh record | review due sources | research owner |
| Private data leak | low after scan | high | scan result | sanitize output | release owner |
| Unsupported claim | unknown | high | claim review | narrow or remove | editor |
| External state drift | medium | medium | live check date | recheck before action | owner |
| Rights gap | unknown | high | rights review | withhold publication | owner |

## Next period

1. Complete the highest evidence-backed action.
2. Re-run its direct gate.
3. Refresh sources due before the next report.
4. Present consequential decisions separately.
5. Keep publication and deployment outside local completion.

## Accuracy checklist

- Test counts are exact.
- Failed checks remain visible.
- Current facts have dates.
- Numbers have denominators.
- Confidence tags match limitations.
- No secret or private path appears.
- Local work is not called live.
- Authorization is not called execution.
- Rollback is stated.
- Open items are genuine.

## Sign-off

The report owner signs for evidence accuracy. The product owner signs only for
acceptance or external action. Missing sign-off remains visible.
