---
type: spoke
title: "YMYL Adjacent Blog Policy"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [eeat, evergreen]
domain: "Blog Trust"
confidence: verified
related:
  - "[[E-E-A-T for Blog Content]]"
  - "[[YMYL Escalation Matrix]]"
  - "[[Reviewer And Expert Review Rules]]"
  - "[[Editorial Transparency Checklist]]"
  - "[[Source Quality Ladder]]"
source_urls:
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
---
# YMYL Adjacent Blog Policy

## YMYL Adjacent Blog Policy Rule Scope

This policy covers blog posts that are not framed as professional advice but still influence money, health, safety, legal, civic, or major life decisions. It also covers political and social topics when the content could shape public understanding or action. The policy is intentionally stricter than ordinary blog review because the QRG and its 2025 update records treat sensitive decision contexts and generated main content differently (source_ids: g-qrg-full, g-update-2025-01-23-qrg-update-jan-2025, g-update-2025-09-11-qrg-update-sept-2025). Helpful-content guidance keeps the article focused on useful, reliable help rather than risk-free phrasing (source_id: g-helpful-content).

### Allowed Actions For Adjacent Topics

Editors may narrow claims, add limitation language, require expert review, replace weak sources, remove recommendations, or change the article angle from advice to informational explanation. They may not hide sensitivity by calling the article "general tips."

### Exceptions That Require Approval

Exceptions require approval when the article contains specific recommendations, local or jurisdictional claims, diagnosis-like language, financial calculations, safety instructions, civic participation guidance, or strong claims about public affairs.

## YMYL Adjacent Policy Rule Table

| Rule | Evidence source | Applies to | Exception | Approval path |
|---|---|---|---|---|
| Treat outcome-changing advice as elevated risk | g-qrg-full, g-helpful-content | Health, finance, legal, safety, and major purchases | Pure glossary or history page with no advice | [[YMYL Escalation Matrix]] owner |
| Add expert review when consequences are material | g-qrg-full | Recommendations, comparisons, calculators, and checklists | Low-risk editorial opinion clearly labeled | [[Reviewer And Expert Review Rules]] |
| Use primary or official sources for sensitive claims | g-helpful-content, g-qrg-full | Statistics, rules, eligibility, safety, and legal statements | First-person story that makes no general claim | [[Source Quality Ladder]] |
| Include limitations before the reader acts | g-helpful-content | Any adjacent topic with uncertainty | None for high-severity claims | Editor and reviewer signoff |
| Escalate generated advice on sensitive topics | g-update-2025-01-23-qrg-update-jan-2025, g-qrg-full | AI-assisted pages that provide instructions or recommendations | AI used only for internal outlining | [[AI Assisted Content Accountability]] |
| Escalate political or social decision content | g-update-2025-09-11-qrg-update-sept-2025, g-qrg-full | Civic, public policy, and social issue explainers | Narrow cultural commentary with no instruction | Managing editor approval |
| Escalate calculators or estimates | g-qrg-full, g-helpful-content | Savings, debt, dosage, eligibility, or risk estimates | Clearly labeled toy example with no decision use | Reviewer plus source owner |
| Escalate local rule references | g-qrg-full | Tax, legal, benefits, safety, or election rules by location | Historical overview without advice | Jurisdiction-aware reviewer |

## Rule, Evidence Source, Applies To, And Enforcement

Severity follows the reader's possible harm, not the keyword. A post about "budget meal planning" can be low risk; a post telling readers how to handle debt or medical diets needs stronger review. Record the risk reason in the handoff so later editors understand why the policy fired.

## YMYL Adjacent Blog Policy Review And Rollback

1. Identify the reader decision that could be affected by the article.
2. Choose the policy row that matches the highest-risk claim.
3. Require the source and reviewer level that the row names.
4. Add visible limitations and remove unsupported instructions.
5. If the risk was over-classified, document the reason and downgrade through [[YMYL Escalation Matrix]], not by deleting the note.

## Adjacent Topic Classification Case

A lifestyle post titled "budget meal planning for students" becomes YMYL-adjacent when a section gives diet advice for diabetes and recommends supplement timing. The allowed path is to remove the health instruction, narrow it to non-medical meal-planning context, or require qualified review and stronger sources. The QRG and helpful-content sources support escalating by reader consequence rather than by the soft tone of the headline (source_ids: g-qrg-full, g-helpful-content).

## Adjacent Policy Edge Cases

- "General tips" copy still gives an actionable debt, diet, safety, or legal step; classify by reader action, not disclaimer wording (source_id: g-qrg-full).
- A calculator outputs a number readers may use for eligibility or risk; require source assumptions and reviewer scope (source_ids: g-qrg-full, g-helpful-content).
- Local law or public-benefit details are correct in one jurisdiction and wrong in another; send the claim to a jurisdiction-aware reviewer (source_id: g-qrg-full).
- Political or social explainers avoid explicit advice but frame civic action with selective context; require senior editorial review (source_id: g-update-2025-09-11-qrg-update-sept-2025).
- An affiliate comparison affects major purchases; combine commercial disclosure with stricter source review (source_id: g-qrg-full).
- A first-person story gives recovery, investment, or legal takeaways; keep the story but remove generalized instruction (source_id: g-helpful-content).
- A checklist title sounds harmless while the steps guide risky action; classify by the steps, not the title (source_id: g-qrg-full).

## Brief Contract Risk Input

[[Content Brief Output Contract]] consumes this policy before drafting starts. Inputs are reader decision, highest-risk claim, required source tier, reviewer requirement, excluded claims, and limitation language. The brief expects a draft-risk field, must-avoid list, source-pack requirements, and escalation owner for any YMYL-adjacent topic.
