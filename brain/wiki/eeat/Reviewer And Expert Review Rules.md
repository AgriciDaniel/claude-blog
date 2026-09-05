---
type: spoke
title: "Reviewer And Expert Review Rules"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [eeat, evergreen]
domain: "Blog Trust"
confidence: verified
related:
  - "[[E-E-A-T for Blog Content]]"
  - "[[Author Bio Requirements]]"
  - "[[YMYL Escalation Matrix]]"
  - "[[Editorial Transparency Checklist]]"
  - "[[AI Assisted Content Accountability]]"
source_urls:
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
---
# Reviewer And Expert Review Rules

## Reviewer And Expert Review Rules Rule Scope

This note decides when an ordinary editorial pass is not enough. It covers expert review for YMYL-adjacent guidance, technical claims, regulated contexts, AI-assisted drafts, and pages where the author lacks direct authority. The source posture is QRG-led: use `g-qrg-full` plus the 2025 QRG update records for review sensitivity, and use `g-helpful-content` to keep the final standard grounded in reader value.

### Allowed Actions Under This Rule Set

An editor may request expert review, narrow the claim, add limitations, remove unsupported advice, or defer publication advice. The rule set does not authorize direct CMS edits, medical or legal signoff, or claims that a review guarantees Search performance.

### Approval Exceptions

Exceptions require a named owner when a deadline forces publication with a known trust gap, when a reviewer has a conflict, or when review evidence cannot be shown publicly but can be retained in the internal audit record.

## Expert Review Rule Table

| Rule | Source basis | Applies to | Exception | Approval path |
|---|---|---|---|---|
| Expert review is required for consequential advice | g-qrg-full, g-update-2025-09-11-qrg-update-sept-2025 | Money, health, safety, legal, civic, and political/social topics | Low-risk informational summary with no recommendation | Managing editor plus topic reviewer |
| Reviewer scope must be written down | g-qrg-full, g-helpful-content | Any page showing a reviewer name | None for sensitive claims | Reviewer note attached to audit |
| AI-assisted drafts need human claim review | g-update-2025-01-23-qrg-update-jan-2025, g-helpful-content | Pages with generated or heavily transformed main content | Draft used only for internal outline | [[AI Assisted Content Accountability]] owner |
| Author expertise and reviewer expertise are separate | g-qrg-full | Pages where the author is not the specialist | Reviewer can cover only claims they checked | Editor records split responsibility |
| Unreviewed risky claims must be removed or softened | g-helpful-content, g-qrg-full | Claims that affect reader decisions | Defer only with visible limitation | Escalate to [[YMYL Escalation Matrix]] |
| Reviewer conflict must be visible | g-qrg-full, nng-editorial-heuristics | Sponsored, affiliate, employer, or product-review contexts | Conflict is immaterial and labeled | Managing editor approval |
| Locale or jurisdiction mismatch blocks signoff | g-qrg-full, g-helpful-content | Legal, financial, safety, or eligibility claims | Claim is rewritten as general context | Topic reviewer plus editor |

## Enforcement Notes For Reviewer Rules

Use the highest-risk claim on the page to choose enforcement. If one paragraph requires expert review, the page cannot be marked ready simply because the rest is low risk. Record the source ID and review owner beside the claim so the next editor can see why the rule fired.

## Expert Review Rollback Path

1. Identify claim categories that exceed ordinary copyediting.
2. Match each category to a reviewer with relevant expertise or direct experience.
3. Record review date, scope, exclusions, and the exact sections reviewed.
4. If the reviewer rejects a claim, remove it, narrow it, or add a limitation before handoff.
5. If later evidence changes the recommendation, roll back the trust claim and reopen [[E-E-A-T Review Rubric]].

## Expert Review Routing Example

A DIY electrical-safety article includes step-by-step fixture replacement advice. A copyeditor can improve clarity, but the safety instruction itself needs qualified review or removal because reader harm risk controls the gate (source_id: g-qrg-full). If no reviewer is available, the article angle changes to "questions to ask a licensed electrician" and the instructions become non-operational context. Helpful-content guidance supports narrowing the page to useful advice the team can stand behind (source_id: g-helpful-content).

## Reviewer Rule Failure Cases

- The reviewer approves a summary but not the numbered procedure; do not mark the whole page reviewed (source_id: g-qrg-full).
- A credential is real in one country, while the article makes local eligibility claims elsewhere; apply the locale mismatch row (source_id: g-qrg-full).
- A sponsor supplies the reviewer for a product comparison; record the relationship before trust language is used (source_ids: g-qrg-full, nng-editorial-heuristics).
- The reviewer changes a claim after the editor's source check; reopen source mapping so the final wording has evidence (source_id: g-helpful-content).
- A reviewer approves examples but not the final CTA; remove the CTA from reviewed scope (source_id: g-qrg-full).
- A technical reviewer validates accuracy but not reader suitability; keep usefulness review with the editor (source_id: g-helpful-content).
- A late reviewer substitution changes expertise coverage; restart approval for affected sections (source_id: g-qrg-full).
- A private review note cannot be shown publicly; retain scope internally and add safe visible limits (source_id: nng-editorial-heuristics).

## Write Package Review Output

[[Blog Write Article Contract]] consumes these rules when the draft requires author or reviewer notes. Inputs are claim categories, reviewer identity, relevant expertise, conflict status, review date, sections checked, and exclusions. The contract expects publish-ready review notes, removed-claim list, limitation language, and blocker status for unreviewed consequential advice.
