---
type: spoke
title: "FLOW Approval Queue"
domain: "Blog Workflow"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [flow, active]
confidence: advisory
related:
  - "[[FLOW Framework]]"
  - "[[FLOW Source Intake]]"
  - "[[FLOW Confidence Tags]]"
  - "[[FLOW Rollback Notes]]"
  - "[[FLOW Report Stage]]"
---

# FLOW Approval Queue

## Queue Record Scope

FLOW Approval Queue is the holding register for recommendations that are too consequential, uncertain, or live-site-adjacent to implement from a draft or report alone. It belongs under [[FLOW Framework]] and receives items from [[FLOW Review Stage]], [[FLOW Factcheck Stage]], [[FLOW Rewrite Stage]], and [[FLOW Report Stage]]. The queue does not publish, edit a CMS, change tracking, or approve itself. It gives the human owner a compact record of the object, evidence state, confidence, next review date, and rollback trigger.

### Events Or Items This Register Captures

Capture changes that affect live content, visible Search claims, AI feature positioning, schema language, deletion, consolidation, or recommendations built from market-level evidence. Usefulness rewrites cite the people-first baseline (source_id: `g-helpful-content`). AI-file corrections cite the Google AI guidance (source_id: `g-ai-opt-guide`). Schema-language decisions point to structured-data guidance (source_id: `g-intro-sd`). Rows based on traffic or engagement observations need property evidence such as GA4 reporting (source_id: `g-ga4-data`) before the queue treats them as site-specific.

### Events Or Items Routed Elsewhere

Pure source capture goes to [[FLOW Source Intake]]. Draft wording without implementation risk goes to [[FLOW Draft Stage]]. Confidence labels go to [[FLOW Confidence Tags]]. A final stakeholder summary goes to [[FLOW Report Stage]] after the queue owner decides.

## FLOW Approval Queue Register Table

| Queue item | Source id | Owner | Confidence | Status | Next review date | Rollback trigger |
|---|---|---|---|---|---|---|
| Rewrite a section for usefulness rather than keyword coverage | `g-helpful-content` | Managing editor | High | Awaiting approval | 2026-07-16 | Reader task becomes less clear after edit |
| Remove a proposed Google AI-specific file requirement | `g-ai-opt-guide` | SEO lead | High | Ready to accept | 2026-07-12 | Recommendation again implies a special AI Search file |
| Validate a schema wording change before handoff | `g-intro-sd` | Technical owner | High | Needs review | 2026-07-14 | Recommendation implies unsupported structured-data eligibility |
| Use GA4 observations as site-specific planning evidence | `g-ga4-data` | Strategy owner | Medium | Monitor | 2026-08-06 | Analytics access, segment, or date range proves unsuitable |
| Remove FAQ rich-result positioning from a template note | `g-faqpage-sd` | Schema owner | High | Awaiting approval | 2026-07-18 | Copy again presents FAQPage as a current rich-result tactic |
| Queue a noindex recommendation for human review | `g-block-indexing` | Technical owner | High | Needs review | 2026-07-19 | Page must remain discoverable for the business case |
| Approve a rewrite after a confirmed Google update window | `g-ranking-history` | SEO lead | Medium | Monitor | 2026-08-02 | Later evidence shows the update date was not the cause |

## Source, Confidence, Owner, Status, And Due Date

Each row needs one accountable owner and one confidence label. Use high confidence for official Google documentation that directly governs the recommendation. Use medium confidence for practitioner or panel research and mark the row as advisory when the data is not from the client property. If the item has no rollback trigger, it is not ready for approval because the operator cannot tell when to revisit the decision.

## FLOW Approval Queue Review Loop

1. Add the item only after [[FLOW Confidence Tags]] names the verdict and evidence tier.
2. Ask the owner to accept, revise, reject, or monitor the item before a live-content handoff.
3. Send accepted live-change items to [[FLOW Rollback Notes]] and unresolved evidence items back to [[FLOW Source Intake]].
4. Include only decided or clearly blocked rows in [[FLOW Report Stage]] so the report does not hide pending approvals.

## Example: AI File Recommendation Queued

A draft report says, "Upload an `llms.txt` file to improve Google AI visibility."

Before: the recommendation is written as a required implementation task.

After: the queue item says "remove special-file requirement" and cites `g-ai-opt-guide`.

The owner accepts the correction because Google AI feature guidance does not
make `llms.txt` a Search, AI Overview, or AI Mode requirement (source_id:
`g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`).

The accepted output goes to [[FLOW Report Stage]] as a corrected caveat, not as
a new technical task.

## Queue Mistakes That Matter

- Treating "awaiting approval" as permission to publish bypasses V1 read-only rules.
- Assigning a team instead of a person leaves rollback ownership unresolved.
- Using `g-ranking-history` as client-impact proof confuses update timing with site evidence.
- Filing low-risk copyedits here clogs the register and hides live-change decisions.

## Consumed By Report Deliverables

[[Full Site Blog Audit Report]] consumes decided queue rows as the executive
decision queue.

Inputs provided: item, source ID, owner, confidence, status, review date, and
rollback trigger.

Outputs expected: accepted actions become report findings, rejected actions
become rationale notes, and monitor items keep their next evidence check.
