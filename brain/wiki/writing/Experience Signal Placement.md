---
type: spoke
title: "Experience Signal Placement"
domain: "Blog Writing"
status: evergreen
created: 2026-07-06
updated: 2026-07-23
tags: [writing, six-pillar, evergreen]
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
  - "https://ziptie.dev/blog/google-ai-overviews-source-selection/"
---

# Experience Signal Placement

## Experience Signal Placement Drafting Job

This note decides where lived use, tested examples, author judgment, screenshots, and operational constraints should appear in a blog draft. Experience is useful when it helps the reader verify the recommendation, not when it decorates a generic article.

### Placement Zones This Note Owns

Put experience in the introduction only when it explains why the author is qualified to guide the reader. Put it under a process step when it changes how the reader executes. Put it inside a comparison when it explains a tradeoff. `g-helpful-content` and `g-qrg-full` both make experience and trust relevant quality concepts, while `ziptie-aio-source-selection` supports the extraction value of clear, self-contained examples.

### Experience Claims That Need Restraint

Do not turn an anecdote into a universal rule. Do not imply that a case example proves a ranking effect. Do not write hidden AI-only experience claims; `g-ai-opt-guide` keeps AI-facing work tied to visible, crawlable content. If an example depends on client data, anonymize it or keep it out of the public draft.

## Experience Placement Table

| Experience asset | Best location in draft | Required input | Source IDs | Evidence state | Next action |
|---|---|---|---|---|---|
| Author method | Intro or byline-adjacent note | Who did the work and how | `g-helpful-content`, `g-qrg-full` | Official quality framing | Add only if verifiable |
| Tested example | Step section or comparison row | Screenshot, sample, or result context | `g-helpful-content` | Local evidence required | Link to proof or remove |
| Expert caveat | Claim-bearing section | Reviewer note or field constraint | `g-qrg-full` | Trust-sensitive review | Escalate if YMYL-adjacent |
| Extractable example | Under the relevant intent-matched heading | Entity, answer, source, caveat | `g-ai-opt-guide`, `ziptie-aio-source-selection` | Official boundary plus practitioner guidance | Shape as a self-contained paragraph |
| Failed attempt | Troubleshooting or limitations section | What was tried and why it failed | `g-helpful-content` | Reader usefulness depends on clarity | Keep if it changes action |
| Reviewer proof | Near the claim requiring expertise | Reviewer name, role, and reviewed scope | `g-qrg-full` | Trust lens for sensitive advice | Add only when review happened |
| Tool output caveat | Beside screenshots or generated drafts | Tool, prompt purpose, and human check | `g-helpful-content`, `g-ai-opt-guide` | Visible content accountability | Remove hidden AI-only framing |

## Experience Signal Editing Procedure

1. Circle every claim that sounds first-hand.
2. Confirm whether the draft shows the method, artifact, or reviewer behind the claim.
3. Move experience closer to the decision it supports.
4. Remove anecdotes that do not alter understanding, trust, or action.
5. Add caveats when the example is narrow, dated, or sample-specific.
6. Send trust gaps to [[E-E-A-T for Blog Content]] before final scoring.

### Placement Example

Weak placement: a case screenshot appears in the intro before the reader knows
which decision it proves. Strong placement: the screenshot sits under the
step where the reader chooses between rewriting and leaving a section intact.
The stronger version gives first-hand evidence a useful job (`g-helpful-content`)
and prevents a narrow example from becoming a universal claim (`g-qrg-full`).
If the example is shaped for AI extraction, keep it visible in the article
instead of storing it as hidden metadata (`g-ai-opt-guide`).

### Experience Placement Risks

- A testimonial replaces the method that would let readers verify the advice (`g-helpful-content`).
- A case example is placed after the recommendation it should constrain (`g-qrg-full`).
- An anonymized client detail still exposes enough context to identify the account (`g-qrg-full`).
- A generated screenshot is presented as observed production evidence (`g-ai-opt-guide`).

### Deliverable Wiring

[[Blog Write Article Contract]] consumes this note for author or reviewer notes,
tested examples, failed attempts, screenshots, and caveats tied to decisions.
It expects visible proof that improves the draft rather than decorative authority.
[[Blog Analyzer Score Report]] consumes missing or misplaced experience
as E-E-A-T and content-usefulness deductions (`g-helpful-content`, `g-qrg-full`).

## Source Handling

This pass uses `g-helpful-content`, `g-ai-opt-guide`, `g-qrg-full`, and `ziptie-aio-source-selection`. Practitioner extraction advice never substitutes for proof that the experience actually happened.

## Related

- [[Information Gain Checklist]]
- [[E-E-A-T for Blog Content]]
- [[Citation Ready Paragraphs]]
- [[Reader Satisfaction Test]]
