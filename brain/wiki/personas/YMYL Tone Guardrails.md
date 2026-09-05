---
type: spoke
title: "YMYL Tone Guardrails"
domain: "Blog Voice"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [personas, voice-style, active]
---

# YMYL Tone Guardrails

## YMYL Tone Guardrails Rule Scope

YMYL Tone Guardrails controls voice when blog content could affect money, health, safety, legal rights, civic decisions, or other high-impact choices. The note does not decide the factual answer. It decides whether tone, certainty, examples, and CTA pressure are appropriate for the source quality and reviewer ownership.

### Allowed Actions And Disallowed Actions

Allowed actions include cautious wording, source-date placement, expert-review notes, narrower examples, and clearer "not advice" boundaries where appropriate. Disallowed actions include promises of outcomes, casualizing risk, hiding uncertainty, replacing expert review with generated prose, or turning a checklist into professional advice. Cite `g-helpful-content`, `g-qrg-full`, `g-update-2025-01-23-qrg-update-jan-2025`, and `g-update-2025-09-11-qrg-update-sept-2025` for the review basis; add `g-update-2026-05-15-spam-policies-update-gen-ai-scaled-content` when a generated batch creates sensitive pages without added value.

### Exceptions That Require Approval

Any stronger claim, urgent CTA, personal recommendation, or region-specific regulated example needs a named human owner. Link locale-sensitive cases to [[Locale Voice Adaptation]] and evidence gaps to [[Research Pack Index]].

## YMYL Tone Guardrails Rule Table

|Guardrail|Evidence|Topic|Enforcement|Approval|
|---|---|---|---|---|
| Put risk before persuasion | `g-qrg-full` | Health, finance, legal, civic, safety | Block hype-led intros | Expert or senior editor |
| Keep source limits visible | `g-helpful-content` | Advice, comparisons, how-to content | Require date and caveat near claim | Factcheck owner |
| Reject low-value generated depth | `g-update-2025-01-23-qrg-update-jan-2025`, `g-update-2026-05-15-spam-policies-update-gen-ai-scaled-content` | AI-assisted drafts | Block filler sections | SEO lead plus editor |
| Expand YMYL awareness for civic and social topics | `g-update-2025-09-11-qrg-update-sept-2025` | Political and social topics | Require extra reviewer note | Policy-aware reviewer |
| Reduce personal directives | `g-qrg-full` | Health, legal, financial examples | Replace command with review path | Expert reviewer |
| Separate education from advice | `g-helpful-content` | Explainers and checklists | Label scope before next step | Editor plus factchecker |
| Localize regulated wording | `g-qrg-full`, `g-localized` | Region-specific legal or finance copy | Require local reviewer | Locale owner |

### Rule, Evidence Source, Applies To, And Enforcement

The guardrail should produce a pass, revise, or block decision. A cautious tone is not enough when the underlying source is too weak; in that case the claim leaves the draft.

## Finance Checklist Tone Case

Draft line: "Use this checklist to avoid payroll penalties."

Guardrail decision: revise, because the wording implies a legal or financial outcome the draft cannot guarantee.

Safer line: "Use this checklist to prepare questions for your payroll advisor or vendor."

The revised line keeps the reader task useful under `g-helpful-content` while reducing personal directive risk under `g-qrg-full`.

If the article targets a specific country, the local reviewer must approve regulated wording before [[Localization Adaptation Checklist]] passes it.

If source support is too weak, the claim moves to [[Factcheck Claim Register]] or leaves the draft.

The CTA can ask for internal review; it cannot imply guaranteed compliance.

## Guardrail Failure Modes

- "Not financial advice" is added while the paragraph still gives individual instructions.
- A checklist sounds harmless but tells readers to take a regulated action.
- A high-risk example uses a fictional person to dodge expert review.
- A local law reference is translated without a local subject reviewer.
- A generated section adds depth by paraphrasing generic advice, triggering scaled-content concerns.
- A source date is present but the caveat sits after the conversion CTA.

## Guardrail Wiring

Primary consumer: [[Factcheck Claim Register]].

Inputs supplied: risky claim, topic category, proposed safer wording, source ID, reviewer owner, and block state.

Output expected back: verdict label, confidence, rollback trigger, and whether the sentence can remain.

Locale consumer: [[Localization Adaptation Checklist]] receives local reviewer requirements for sensitive wording.

## YMYL Tone Guardrails Review And Rollback

Rollback if a reviewer identifies missing professional context, local legal risk, or overconfident wording. Reopen [[Banned Claims And Phrases]] when the same risky phrase appears in multiple drafts.
