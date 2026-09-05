---
type: spoke
title: "FLOW Report Stage"
domain: "Blog Workflow"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [flow, active]
confidence: advisory
related:
  - "[[FLOW Framework]]"
  - "[[FLOW Approval Queue]]"
  - "[[FLOW Confidence Tags]]"
  - "[[Blog Quality Score]]"
  - "[[AI Citation Mechanics]]"
---

# FLOW Report Stage

## Report Purpose

FLOW Report Stage summarizes decisions, evidence, scores, risks, and next actions for handoff. It is the final reader-facing operating note, not a place to introduce new claims. It should make the owner able to see what is ready, what is blocked, what is advisory, and which live changes need approval.

## Audience And Scope Filter

Write for the person who must decide or act next: editor, SEO lead, content strategist, technical owner, or executive stakeholder. Keep the report inside [[FLOW Framework]] boundaries. It can cite `g-helpful-content` for usefulness review, `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` when a recommendation risks tool certainty, and market studies such as `sparktoro-zero-click-2026` or `seer-aio-impact-ctr-2026` only as planning context. It should not imply guaranteed rankings, clicks, AI Overviews, or chatbot citations.

## Findings This Report Must Not Overclaim

Do not call a page "future proof." Do not present the SparkToro panel as a forecast for one property. Do not say Google requires a special AI file. Do not treat a quality score as a ranking score. If a finding is based on official guidance, say what the guidance supports. If it is based on a practitioner or panel source, keep the limitation next to the recommendation.

## FLOW Report Stage Findings Table

| Report section | Inputs | Evidence sources | Severity | Recommendation | Delivery status |
|---|---|---|---|---|---|
| Executive decision | Approved queue rows and blockers | [[FLOW Approval Queue]] | High when live content changes | Accept, revise, reject, or monitor | Ready after owner review |
| Quality finding | Review memo and score notes | `g-helpful-content`, [[Blog Quality Score]] | Medium to high | Improve reader usefulness and evidence fit | Ready if sourced |
| AI Search caveat | Draft AI claims and factcheck register | `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` | High if overclaim appears | Remove tool-certainty or guarantee language | Ready after correction |
| Market context | Distribution or visibility assumption | `sparktoro-zero-click-2026`, `seer-aio-impact-ctr-2026` | Medium | Treat as planning pressure, not traffic math | Advisory |
| Open evidence gap | Missing source IDs or dates | [[FLOW Source Intake]] | High if claim is current | Block claim until sourced | Blocked |
| Schema retirement finding | Factcheck correction and schema note | `g-faqpage-sd` | High if recommendation is current | Remove FAQ rich-result promise | Ready after schema owner accepts |
| Rollback-sensitive rewrite | Accepted queue row and baseline note | [[FLOW Rollback Notes]] | High when live content changes | Attach trigger and review date | Ready for owner decision |
| First-party evidence caveat | GSC or GA4 export summary | `g-gsc-api`, `g-ga4-data` | Medium | State scope and missing-data limits | Advisory or ready |

## Severity, Evidence, Recommendation, Owner, And Due Date

Each finding has one severity label, one evidence lane, one owner, and one due date or review date. A report with many findings and no owner is just a memo. A report with recommendations and no source IDs is not FLOW-compliant.

## FLOW Report Stage Delivery Procedure

1. Pull decided rows from the approval queue and unresolved rows from the factcheck register.
2. Convert each item into a finding with evidence, confidence, owner, and next action.
3. Put advisory market context in a separate section so it cannot be confused with property data.
4. Send rollback-sensitive items to [[FLOW Rollback Notes]] before anyone implements them.

## Example: Turning Checks Into Findings

Inputs: a review memo flags thin answer depth, factcheck blocks FAQ rich-result
language, and the approval queue accepts an AI-file correction.

The report creates three findings: usefulness improvement citing
`g-helpful-content`, schema correction citing `g-faqpage-sd`, and AI guidance
correction citing `g-ai-opt-guide`.

The market appendix links to [[AI Citation Mechanics]] instead of repeating a
click-stat block.

The owner receives one decision table with status, confidence, due date, and
rollback trigger for live-content changes.

## Report-Specific Overclaims

- A quality score is presented as a ranking score.
- A market study is written as a traffic forecast for the client.
- Missing technical data is treated as a pass because no issue was observed.
- A blocked claim remains in the summary because it sounds persuasive.

## Consumed By Score Reports

[[Blog Analyzer Score Report]] consumes report-ready findings, severity,
evidence source, owner, due date, and delivery status.

[[Full Site Blog Audit Report]] consumes the same fields at inventory scale and
expects page-level evidence where a page-level recommendation appears.

The output expected from both deliverables is a decision-ready summary with
advisory items separated from confirmed corrections.
