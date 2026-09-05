---
type: spoke
title: "Quality Review Evidence Log"
domain: "Blog Quality"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [quality, scorecard, active]
confidence: advisory
related:
  - "[[Blog Quality Score]]"
  - "[[Quality Score Rubric]]"
  - "[[Quality Gate Failure Modes]]"
  - "[[Recommendation Confidence Labels]]"
---

# Quality Review Evidence Log

## Quality Review Evidence Log Record Scope

This register captures the exact evidence used during a quality score review. It is not a bibliography and it is not a replacement for `references/source-ledger.json`. It records which ledger source, claim, owner, confidence label, and next review action supported a scoring decision. The examples here are `g-helpful-content` for usefulness, `g-ai-opt-guide` for AI-feature caveats, `g-gsc-api` for first-party query evidence, and `seer-aio-impact-ctr-2026` for practitioner AIO context.

## Events Or Items This Register Captures

- A score row that depends on a current Search, AI, market, or trust claim.
- A source-date check that changes pass, revise, or blocked status.
- A market study used as context rather than property evidence.
- A reviewer decision that downgrades a recommendation from verified to advisory.

## Events Or Items Routed Elsewhere

Raw source ingestion stays outside this folder. Final delivery status belongs in [[Delivery Contract Gate]]. The interpretation of zero-click or AI-surface behavior belongs in [[AI Citation Mechanics]]. Scoring math belongs in [[Quality Score Rubric]]. The log links to those notes without copying their full instructions.

## Quality Review Evidence Log Register Table

| Evidence item | Source ID | Owner | Confidence | Status | Next review date | Rollback trigger |
|---|---|---|---|---|---|---|
| People-first usefulness row | `g-helpful-content` | Editor | confirmed | accepted | 2026-08-01 | Reopen if guidance refresh changes content self-assessment. |
| Google AI feature caveat | `g-ai-opt-guide` | SEO reviewer | confirmed | accepted | 2026-08-01 | Reopen if Google changes AI feature guidance. |
| Search Console query evidence | `g-gsc-api` | Data owner | confirmed | accepted | 2026-08-01 | Reopen if export scope or API contract changes. |
| AIO click context caveat | `seer-aio-impact-ctr-2026` | Strategy owner | as-reported | advisory | 2026-08-06 | Reopen if first-party data contradicts planning assumption. |
| Canonical inspection note | `g-urlinspect` | Technical SEO | confirmed when export exists | accepted or gap | 2026-08-01 | Reopen if selected canonical changes. |
| Schema visible-content check | `g-intro-sd` | Schema reviewer | confirmed | accepted | 2026-08-01 | Reopen if markup stops matching page copy. |
| Performance measurement row | `wd-vitals` | Data owner | confirmed for terminology | unavailable or accepted | 2026-08-01 | Reopen when field data becomes available. |
| GenAI report availability | `g-genai-reports` | Analyst | confirmed for reporting surface | gap or accepted | 2026-08-01 | Reopen when property export is supplied. |

## Source, Confidence, Owner, Status, And Due Date

Each row needs a source ID, owner, confidence label, and due date. If evidence is missing, write `gap`, not a guessed source. If a claim uses a practitioner study, keep the methodology limit visible. If a claim depends on client property data, link the first-party export or state that it was unavailable.

## Quality Review Evidence Log Review Loop

1. Add rows while scoring, not after the decision is written.
2. Check every row against [[Recommendation Confidence Labels]].
3. Move unresolved rows into [[Quality Gate Failure Modes]].
4. Refresh due rows before reusing an old score.
5. Preserve the distinction between confirmed, as-reported, contested, and unknown.

## Evidence Row Example

Claim under review: "This page improved AI Mode visibility."
Available data: Search Console export is missing.
Ledger route: `g-genai-reports` supports the reporting surface.
Status: gap, not accepted.
Confidence: unknown for this property.
Next review date: use the source refresh date.
Rollback trigger: remove claim if no export appears.

## Register Failure Details

- A source ID without claim location is incomplete.
- A retrieval date cannot replace source relevance.
- Practitioner evidence needs its limitation copied into the row.
- Property-data gaps stay gaps until an export exists.
- Old accepted rows expire when refresh dates arrive.

## Report Consumption

[[Blog Analyzer Score Report]] consumes these evidence rows.
Inputs sent: source ID, confidence, owner, status, due date.
Expected output: reproducible deduction rationale.
[[Full Site Blog Audit Report]] consumes repeated evidence gaps.
It expects URL, finding, action priority, and rollback trigger.
