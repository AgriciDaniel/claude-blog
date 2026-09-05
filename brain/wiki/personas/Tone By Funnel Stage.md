---
type: spoke
title: "Tone By Funnel Stage"
domain: "Blog Voice"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [personas, voice-style, active]
---

# Tone By Funnel Stage

## Tone By Funnel Stage Stage Purpose

Tone By Funnel Stage maps voice to awareness, evaluation, decision, retention, and advocacy contexts. The goal is to match the reader's decision pressure without manufacturing urgency. This note is useful when [[Audience Persona Template]] names the reader stage but the writer still needs tone, CTA, proof, and caveat guidance.

### Trigger And Entry Criteria

Enter this workflow when a brief has a reader job, target stage, primary claim, and source packet. Use `g-helpful-content` for usefulness, `g-qrg-full` for trust and YMYL sensitivity, `nng-editorial-heuristics` for predictable interaction cues, and `g-ai-opt-guide` if the stage includes AI answer review. `g-ai-features` can support Google AI feature context, but it cannot justify a stronger CTA.

### Output Artifact And Exit Criteria

The output is a tone row for the brief: stage, reader question, acceptable confidence, CTA type, proof type, and banned pressure. Exit only when [[Banned Claims And Phrases]] and [[YMYL Tone Guardrails]] do not block the stage framing.

## Tone By Funnel Stage Step Table

| Stage | Input | Evidence | Action | Owner | Handoff |
|---|---|---|---|---|---|
| Awareness | Problem language and low prior knowledge | `g-helpful-content` | Explain terms before advice | Strategist | [[Readability Review]] |
| Evaluation | Alternatives, criteria, objections | `nng-editorial-heuristics` | Compare tradeoffs without hype | Editor | [[Example Selection Rules]] |
| Decision | Proof, implementation risk, reviewer limits | `g-qrg-full` | State conditions and caveats early | Reviewer | [[YMYL Tone Guardrails]] |
| Retention | Existing-user task and support signal | first-party evidence | Use precise, helpful next steps | Customer owner | [[Persona Evidence Packet]] |
| Advocacy | Successful user story and permission boundary | `g-helpful-content` | Invite sharing without inflating results | Brand owner | [[Distribution Voice Adaptation]] |
| Reconsideration | Objection, failed attempt, or stale belief | `nng-editorial-heuristics` | Acknowledge friction before advice | Editor | [[Readability Review]] |
| High-risk action | Sensitive claim plus reviewer note | `g-qrg-full` | Reduce pressure and require expert path | Reviewer | [[YMYL Tone Guardrails]] |

### Input, Evidence, Action, Owner, And Handoff

The stage row should say what tone is allowed and what tone is banned. "Confident about the process" is different from "certain about the outcome"; the latter needs evidence the blog usually does not have.

## Funnel Tone Decision Example

Scenario: a reader compares CMS migration checklists after a failed site move.

Awareness tone would explain terms such as redirects and canonicals before asking for action.

Evaluation tone can compare risk categories if the article names evidence limits and reviewer scope.

Decision tone may recommend a prelaunch checklist, but it cannot promise recovery or ranking improvement.

The distinction follows `g-helpful-content` because the draft changes tone based on the reader's task.

If the article includes finance, legal, health, civic, or safety impact, `g-qrg-full` pushes the row into high-risk action.

The CTA becomes "review the checklist with your owner," not "fix this today before rankings collapse."

## Stage Misfires

- Awareness copy starts with urgency and scares readers before defining the problem.
- Evaluation copy hides tradeoffs because the brand wants a cleaner comparison.
- Decision copy borrows proof from a case study that does not match the reader's risk.
- Retention copy assumes the reader caused the issue and creates support friction.
- Advocacy copy turns a satisfied quote into a generalized performance claim.
- Reconsideration copy mocks prior choices and damages trust.

## Deliverable Wiring

Primary consumer: [[Content Brief Output Contract]].

Inputs supplied: funnel stage, reader question, acceptable confidence, CTA type, proof type, and banned pressure.

Output expected back: brief tone row, draft risks, and any handoff to evidence or legal review.

Draft consumer: [[Blog Write Article Contract]] applies the approved CTA and caveat pressure during writing.

## Tone By Funnel Stage Control Points

Reject stage changes that add scarcity, authority, or fear without a source. Recheck the tone when a draft moves from blog post to distribution asset.
