---
type: "deliverable"
title: "Health Scorecard"
created: "{{date}}"
updated: "{{date}}"
status: "active"
domain: "Blog Content Brain"
tags: [deliverables, active]
---

# Health Scorecard

| Area | Status | Evidence | Confidence |
|---|---|---|---:|
| Source provenance | Needs source intake | [[Source Manifest Guide]] | low |
| Research freshness | Needs refresh | [[Research Refresh Workflow]] | low |
| Reporting readiness | Draft | [[Weekly Report]] | low |

Related: [[Action Roadmap]] | [[Weekly Report]]
## Status vocabulary

| Status | Definition |
|---|---|
| unknown | Required evidence has not been collected |
| at risk | Evidence indicates likely failure |
| blocked | A named dependency prevents progress |
| in progress | Owned work is active |
| implemented | The change exists but full verification remains |
| verified | The stated gate passed |
| accepted | The responsible human approved the result |
| released | The artifact is published and live state was checked |

Do not substitute “green” for a more precise state.

## Evidence dimensions

| Dimension | Weighting question | Required record |
|---|---|---|
| Correctness | Does behavior match the contract? | Focused test |
| Currentness | Are volatile claims freshly reviewed? | Source decision |
| Safety | Are secrets, paths, and destructive effects controlled? | Scan and rollback |
| Determinism | Does the same input produce the same bytes? | Repeated build hash |
| Usability | Can the intended operator complete the task? | Human or browser review |
| Installability | Does a clean environment work? | Isolated install |
| Portability | Are local assumptions removed? | Path and platform checks |
| Rights | Can each public artifact be distributed? | Rights review |
| Observability | Can failure be diagnosed? | Clear result envelope |
| Maintainability | Is the next update path documented? | Owner and refresh trigger |

## Scoring rule

Score only dimensions that have evidence. Missing evidence is unknown, not zero
and not passed. A blocking safety defect caps the overall status regardless of
the numeric average.

Suggested per-dimension scale:

- 0: known failure.
- 1: incomplete and high risk.
- 2: implemented with material gaps.
- 3: focused verification passed.
- 4: broad verification passed.
- 5: release or human acceptance passed.

## Scorecard row contract

Each row includes area, status, evidence, evidence date, owner, confidence tag,
next action, and retest trigger.

## Gate examples

| Claim | Direct gate | Insufficient substitute |
|---|---|---|
| Tests pass | Named suite and count | “CI looks good” |
| Build succeeds | Build command exit zero | Type check only |
| Source is current | Content review decision | HTTP 200 |
| Package is clean | Artifact scan | Source-tree scan only |
| Browser flow works | Browser capture | Unit test |
| Install works | Clean isolated install | Existing developer environment |
| Public page is live | Live URL check | Local preview |
| Issue is resolved | Verified fix and external state | Local code change |

## Review cadence

Review active P0 and P1 rows at every work session. Review source currentness on
its declared interval. Review release, rights, and installability before every
artifact handoff. Review accepted or released rows when their external
dependency changes.

## Blocking rules

- Secret or credential exposure.
- Unsafe destructive target.
- Missing rights for public distribution.
- Current claim contradicted by authority.
- Market-ready declaration without its gate.
- Non-deterministic generated artifact.
- Unresolved user-owned work overlap.
- Required human review not completed.

## Trend notes

A score may improve because evidence was added, a defect was fixed, or scope was
narrowed. Record which occurred. Narrowing scope is valid, but it must not be
presented as a product capability gain.

## Scorecard closeout

Before calling the scorecard verified:

1. Sample every evidence link.
2. Re-run volatile checks.
3. Confirm dates and owners.
4. Check that no blocker is averaged away.
5. Compare status language to direct evidence.
6. Record skipped live and human gates.
7. Link unresolved rows to [[Action Roadmap]].
8. Present external decisions in [[Approval Queue]].
