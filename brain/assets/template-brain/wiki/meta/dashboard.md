---
type: "dashboard"
title: "Dashboard"
created: "{{date}}"
updated: "{{date}}"
status: "active"
domain: "Blog Content Brain"
tags: [meta, dashboard, active]
---

# Dashboard

## Visual Map

![[brain-relationship-map.svg]]

## Operating Links

- [[Source Intake Workflow]]
- [[Research Refresh Workflow]]
- [[Synthesis Workflow]]
- [[Reporting Workflow]]
- [[Approval Queue]]
- [[Health Scorecard]]
- [[Action Roadmap]]
## Dashboard status model

| Surface | State question | Evidence link |
|---|---|---|
| Sources | Are claims traceable and current? | [[Source Manifest Guide]] |
| Intake | Are new materials admitted safely? | [[Source Intake Workflow]] |
| Refresh | Are volatile sources within review date? | [[Research Refresh Workflow]] |
| Synthesis | Are facts distinct from recommendations? | [[Synthesis Workflow]] |
| Decisions | Are consequential actions authorized? | [[Approval Queue]] |
| Roadmap | Is work ordered by evidence and risk? | [[Action Roadmap]] |
| Health | Do statuses match direct gates? | [[Health Scorecard]] |
| Reporting | Can another operator verify the state? | [[Weekly Report]] |

## Attention lanes

### Now

One current action with an owner, evidence, and completion gate.

### Next

Actions whose prerequisites are satisfied but which are not started.

### Waiting

Items that require an owner decision or external dependency.

### Watching

Living sources, APIs, and release channels with refresh triggers.

### Closed

Actions whose named gate passed and whose evidence remains linked.

## Dashboard maintenance

1. Read the previous dashboard state.
2. Sample every “verified” evidence link.
3. Move stale claims to watching or at risk.
4. Remove completed actions from now.
5. Pull the next dependency-ready action forward.
6. Keep external decisions in waiting.
7. Update owners and dates.
8. Record the change in the log.
9. Regenerate visual navigation when links change.
10. Run vault lint.

## Warning indicators

| Indicator | Meaning | Response |
|---|---|---|
| Missing source date | Currentness unknown | Run refresh |
| Broken wikilink | Navigation or provenance gap | Repair link |
| Low confidence | Material limitation | Narrow claim |
| Dirty generated output | Determinism uncertain | Rebuild safely |
| Pending approval | Consequential action not authorized | Wait |
| Failed test | Implementation gate blocked | Diagnose |
| Skipped live check | External state unknown | Report boundary |
| Rights unknown | Public distribution blocked | Obtain review |

## Review questions

- Does the current action match the user’s outcome?
- Is the source authority correct for the claim?
- Is any confidence tag too strong?
- Is a local artifact being mistaken for external completion?
- Are private raw materials excluded from public surfaces?
- Is rollback still practical?
- Does the report expose all failures?
- Is the next action executable?

## Dashboard handoff

A new operator should be able to open this note, follow the operating links, and
understand what is current without reading a long chronology.

## Dashboard anti-patterns

Do not turn the dashboard into a backlog dump, a vanity score, a copied CI log,
or a collection of undated claims. Link evidence rather than duplicating it.
