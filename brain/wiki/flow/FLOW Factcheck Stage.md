---
type: spoke
title: "FLOW Factcheck Stage"
domain: "Blog Workflow"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [flow, active]
confidence: advisory
related:
  - "[[FLOW Framework]]"
  - "[[FLOW Draft Stage]]"
  - "[[FLOW Confidence Tags]]"
  - "[[Research Pack Index]]"
  - "[[AI Citation Mechanics]]"
---

# FLOW Factcheck Stage

## Factcheck Purpose

FLOW Factcheck Stage verifies current claims, statistics, citations, sensitive language, and source scope before a recommendation is delivered. It is not a copyedit pass. It tests whether the draft's evidence can carry the exact sentence being made and whether the verdict should be confirmed, advisory, contested, or blocked.

## Claim Classes Requiring Checks

Check Search policy, AI feature claims, schema advice, performance language, market statistics, and any recommendation that could alter live content. Use [[Research Pack Index]] for source lookup and [[FLOW Confidence Tags]] for verdict language. AI-file language is checked against Google guidance and the June 2026 ledger entry (source_ids: `g-ai-opt-guide`, `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`). Retired FAQ rich-result claims use the schema changelog (source_id: `g-faqpage-sd`). Market statistics remain AS-REPORTED and are checked against the cited study, such as SparkToro (source_id: `sparktoro-zero-click-2026`).

## Verification Register Table

| Check item | Evidence required | Action | Verdict label | Owner | Handoff |
|---|---|---|---|---|---|
| People-first content claim | Source packet with dated retrieval | Confirm the sentence matches guidance | CONFIRMED if direct | Factchecker | [[FLOW Review Stage]] |
| AI optimization instruction | `g-ai-opt-guide` | Remove special-file or special-schema overreach | CONFIRMED for correction | SEO factchecker | [[FLOW Draft Stage]] |
| `llms.txt` mention | June 2026 update source ID | Mark unsupported as a Google requirement | CONFIRMED correction | SEO factchecker | [[2026 Google Update Timeline]] |
| Zero-click statistic or conclusion | `sparktoro-zero-click-2026` with method caveat | Retain only as market context | AS-REPORTED | Strategy reviewer | [[AI Citation Mechanics]] |
| Unsourced new claim | Source packet absent | Block the claim or send to intake | BLOCKED | Editor | [[FLOW Source Intake]] |
| FAQ rich-result recommendation | `g-faqpage-sd` | Remove current-rich-result framing | CONFIRMED correction | Schema reviewer | [[Schema Generation Output Contract]] |
| QRG used as ranking formula | `g-qrg-full` | Reframe as quality-evaluator guidance | CONFIRMED for document scope | E-E-A-T reviewer | [[Blog Quality Score]] |
| Tool guarantee or vendor certainty | `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` | Replace guarantee with advisory language | CONFIRMED correction | SEO lead | [[FLOW Approval Queue]] |

## Escalation Rules

Escalate when a draft makes a legal, medical, financial, reputation, or platform policy statement without sufficient evidence. Escalate also when a source is dated but does not prove the operational recommendation. A factcheck can approve wording, request rewrite, or block publication advice, but it does not mutate external systems in V1.

## Exit Packet

The exit packet contains checked claims, rejected claims, source IDs, verdicts, unresolved gaps, and the owner of each correction. Items that affect live content move to [[FLOW Approval Queue]] with a rollback note.

## Example: Blocking A FAQ Rich Result Claim

Draft sentence: "Add FAQPage schema so Google can show FAQ rich results."

Factcheck result: blocked as a current Search recommendation because the ledger
records the FAQ rich-result retirement under `g-faqpage-sd`.

Revised sentence: "Keep visible question-and-answer content only when it helps
the reader, and do not present FAQPage as a current rich-result tactic."

The schema owner then updates the handoff note for [[Schema Generation Output Contract]].

## Factcheck Misses That Slip Through

- A date is present, but it belongs to retrieval rather than publication.
- A source supports the topic but not the exact operational recommendation.
- A practitioner statistic is quoted without geography, sample, or method caveat.
- A correction is made in prose but not copied into the deliverable register.

## Consumed By Claim Registers

[[Factcheck Claim Register]] consumes checked claim text, source ID, verdict,
confidence, owner, refresh date, and rollback trigger.

[[Blog Analyzer Score Report]] consumes blockers and major source failures as
score evidence, not as a separate copyedit list.

The expected output is a claim row with either confirmed wording, advisory
scope, or blocked status before the report stage.
