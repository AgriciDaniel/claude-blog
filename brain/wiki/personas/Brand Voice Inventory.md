---
type: spoke
title: "Brand Voice Inventory"
domain: "Blog Voice"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [personas, voice-style, active]
---

# Brand Voice Inventory

## Brand Voice Inventory Capture Job

Brand Voice Inventory stores the voice traits writers can actually apply: approved phrases, sentence posture, evidence style, banned moves, and tolerated variation. It should make [[Voice and Style]] operational without pretending that voice is evidence. The inventory is useful only when each trait has a sample, a reason, and a boundary.

### Voice Traits Owned By This Spoke

Use `g-helpful-content` to keep voice tied to usefulness, `g-qrg-full` to avoid softening trust-sensitive claims, `nng-editorial-heuristics` to keep choices recognizable and consistent, and `g-ai-opt-guide` when brand voice is adapted for AI answer contexts. `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` is relevant when brand language risks sounding like a guaranteed SEO service.

### Sample Approval And Human Review

Human review is required when a sample changes legal meaning, adds urgency, makes the brand sound more certain than the source, or alters a named product claim. [[Terminology Control List]] owns naming consistency; [[Banned Claims And Phrases]] owns prohibited promises; [[Readability Review]] owns clarity after the voice pass.

## Brand Voice Inventory Pattern Table

| Trait | Approved example | Allowed variation | Blocked move | Evidence cue | Owner |
|---|---|---|---|---|---|
| Direct | "Start with the reader's decision." | Short lead, answer-first structure | Decorative opener before the answer | `g-helpful-content` | Editor |
| Cautious | "The source supports this condition." | Caveat after the recommendation | Hiding the limitation in a footnote | `g-qrg-full` | Reviewer |
| Practical | "Use this when the source packet is complete." | Checklist or table format | Abstract advice with no handoff | `nng-editorial-heuristics` | Strategist |
| Search-aware | "No special AI-only file is required for Google." | Link to the canonical caveat | Invented AI markup requirement | `g-ai-opt-guide` | SEO lead |
| Evidence-forward | "The claim is ready when the source ID is named." | Short proof cue before advice | Confident claim with no provenance | `g-helpful-content` | Researcher |
| Non-imitation | "Match the approved sample's clarity, not a person's identity." | Use measurable cadence notes | Mimic an unapproved individual | `nng-editorial-heuristics` | Brand owner |
| Limited-confidence | "This is a review finding, not a forecast." | Advisory label beside recommendation | Ranking or recovery certainty | `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` | SEO lead |

### Trait, Example, Allowed Variation, And Blocked Move

Every trait needs a positive and negative sample from the current content system. The inventory should prefer short examples that can be reused in briefs, QA comments, and [[FLOW Framework]] stage prompts.

## Voice Sample Calibration

Sample source: an approved audit paragraph says, "The article can be clearer when the answer appears before the tool caveat."

Captured trait: direct, evidence-forward, and limited-confidence.

Before inventory: "Our system fixes confusing blog posts."

After inventory: "Move the answer above the caveat, then cite the source that controls the recommendation."

The after version keeps the action concrete without promising performance, matching `g-helpful-content` and the tool caveat source.

The blocked move is a service guarantee, so the owner also checks [[Banned Claims And Phrases]].

The usable variation can appear in review comments, brief notes, and [[FLOW Stage Prompt Map]] prompts.

## Inventory Failure Modes

- A trait says "bold" but every approved example is actually cautious and sourced.
- A brand owner approves a phrase that makes a regulated claim stronger than its source.
- A legacy campaign tagline is stored as durable voice guidance without a date.
- Multiple samples come from one ghostwritten page and hide the normal house style.
- A search-aware trait becomes a promise about AI features, violating `g-ai-opt-guide`.
- A negative sample is missing, so writers cannot see the boundary.

## Deliverable Wiring

Primary consumer: [[Brand Context Contract]].

Inputs supplied: approved phrases, trait boundaries, sample passages, banned moves, source IDs, and reviewer owner.

Output expected back: accepted brand context fields, proof-library links, and whether the voice rule is durable or campaign-only.

Style consumer: [[Style Learning Voice Profile]] converts approved samples into measurable cadence and vocabulary fields.

## Brand Voice Inventory Refresh Test

Rebaseline after a positioning change, new legal review, product rename, or repeated drift in [[Voice Drift Audit]]. Retire traits that cannot be shown in a real draft.
