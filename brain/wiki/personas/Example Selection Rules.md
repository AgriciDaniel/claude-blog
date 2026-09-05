---
type: spoke
title: "Example Selection Rules"
domain: "Blog Voice"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [personas, voice-style, active]
---

# Example Selection Rules

## Example Selection Rules Scope

Example Selection Rules decides which examples can appear in a blog draft, brief, or review note. The example must match the reader, evidence, risk level, and locale. It should make an abstract recommendation easier to apply, not smuggle in a claim the source packet does not support.

### Allowed Example Moves

Use a small scenario, comparison, failure case, sample sentence, or before-and-after rewrite when it clarifies the reader task. Cite `g-helpful-content` for usefulness, `g-qrg-full` for trust-sensitive content, `g-update-2025-01-23-qrg-update-jan-2025` for avoiding copied or filler main content, and `g-update-2025-09-11-qrg-update-sept-2025` when AI Overview examples or YMYL expansion change review pressure. `g-localized` is relevant when the example depends on language or region.

### Disallowed Example Moves And Approval Exceptions

Block examples that invent metrics, imitate a real person without evidence, use a regulated topic casually, or localize a legal or medical claim without human review. Exceptions require the owner named in [[YMYL Tone Guardrails]] or [[Locale Voice Adaptation]].

## Example Selection Rules Table

|Example rule|Basis|Use case|Exception|Approval|
|---|---|---|---|---|
| Match the reader's actual task | `g-helpful-content` | How-to, comparison, and decision posts | None for thin personas | Editor signs persona fit |
| Keep sensitive examples conservative | `g-qrg-full` | Legal, medical, financial, civic, safety | Expert-approved scenario | Reviewer records scope |
| Avoid filler or copied examples | `g-update-2025-01-23-qrg-update-jan-2025` | AI-assisted drafts and rewrites | Quoted source with attribution | Factcheck owner approves |
| Check locale fit | `g-localized` | Regional examples, idioms, compliance references | Global concept with neutral wording | Locale reviewer approves |
| Prefer decision contrast | `g-helpful-content` | Comparison and alternative posts | None when evidence is missing | Editor names the tradeoff |
| Mark example provenance | `g-qrg-full` | Case studies and expert examples | Composite example labeled clearly | Reviewer approves label |
| Remove unsupported specificity | `g-update-2025-01-23-qrg-update-jan-2025` | Generated drafts | Real source added later | Factchecker blocks until sourced |

### Rule, Source Basis, Applies To, And Enforcement

Each selected example should name its job: explain a term, reveal a risk, compare choices, or show a blocked phrase. Delete examples that only make the page longer.

## Example Triage In A Rewrite

Draft recommendation: "Show a startup saving 40 percent after a blog refresh."

Decision: remove the numeric outcome because no source ID supports it.

Replacement example: "Compare a stale introduction against an answer-first rewrite, then explain which reader task improves."

The replacement demonstrates the editorial procedure without inventing performance, aligned with `g-helpful-content`.

If the article covers a regulated topic, the example must show the limitation before the CTA under `g-qrg-full`.

If the example is adapted from a client story, label it as anonymized or composite before reuse.

Generated placeholder examples stay blocked when they only pad the article, using `g-update-2025-01-23-qrg-update-jan-2025`.

## Example Selection Pitfalls

- The example matches the keyword but not the persona's actual decision.
- A failure case embarrasses a real customer pattern without consent-safe abstraction.
- A regional analogy depends on institutions the locale reviewer has not approved.
- A case study number becomes the article's main proof even though it is anecdotal.
- A "simple example" removes the condition that makes the advice safe.
- A repeated example across a cluster makes each page feel copied.

## Deliverable Consumption

Primary consumer: [[Content Brief Output Contract]].

Inputs supplied: approved example job, rejected example reason, risk level, locale dependency, and source ID.

Output expected back: section placement, owner signoff, and unresolved example gaps for the outline.

Draft consumer: [[Blog Write Article Contract]] uses the approved example and banned variant during body drafting.

## Example Selection Rules Rollback Review

Rollback an example when a source changes, a locale reviewer objects, or a claim-ledger verdict weakens. Route replacement examples through [[Persona Evidence Packet]] before reuse.
