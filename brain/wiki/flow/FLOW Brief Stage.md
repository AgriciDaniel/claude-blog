---
type: spoke
title: "FLOW Brief Stage"
domain: "Blog Workflow"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [flow, active]
confidence: advisory
related:
  - "[[FLOW Framework]]"
  - "[[FLOW Source Intake]]"
  - "[[FLOW Draft Stage]]"
  - "[[SERP-Informed Briefs and Outlines]]"
  - "[[AI Citation Mechanics]]"
---

# FLOW Brief Stage

## Brief Stage Job

FLOW Brief Stage turns a source packet and reader problem into a draftable brief. It sits between [[FLOW Source Intake]] and [[FLOW Draft Stage]], so its job is not to write the article. It decides what the draft must answer, which evidence is allowed, which claims need caution, and which handoffs are blocked until a human owner resolves the gap.

### Trigger And Entry Criteria

Enter this stage when the topic, target reader, source IDs, and intended artifact are known. The brief may cite Google helpful-content guidance for reader value and usefulness checks (source_id: `g-helpful-content`). AI visibility instructions use Google's AI feature documentation for surface boundaries (source_id: `g-ai-features`). Passage-level answer blocks remain practitioner guidance and need that label when used (source_id: `ziptie-aio-source-selection`). Zero-click research can shape distribution framing, but it should point to [[AI Citation Mechanics]] and not become a traffic forecast (source_id: `sparktoro-zero-click-2026`).

### Output Artifact And Exit Criteria

The exit artifact is a brief with a reader job, answer promise, claim inventory, source list, excluded claims, internal link targets, and owner notes. It exits only when a draft owner can write without guessing source authority or Search policy.

## FLOW Brief Stage Step Table

| Step | Input | Evidence required | Produced artifact | Downstream handoff |
|---|---|---|---|---|
| 1. Frame the reader job | Topic, audience, search intent | `g-helpful-content` plus local persona notes | One-sentence reader task | [[FLOW Draft Stage]] |
| 2. Bind source claims | Source intake packet | Source IDs, dates, verdicts, limitations | Claim inventory with allowed use | [[FLOW Confidence Tags]] |
| 3. Separate AI Search guidance | AI or GEO requirement in the request | `g-ai-features`, `ziptie-aio-source-selection` if passage tactics appear | AI caveat block for the brief | [[AI Citation Mechanics]] |
| 4. Decide market-context use | Zero-click or distribution assumption | `sparktoro-zero-click-2026` with AS-REPORTED scope | Advisory planning note | [[FLOW Report Stage]] |
| 5. Name draft constraints | Voice, structure, internal links, exclusions | Accepted source and link list | Draft-ready brief packet | [[FLOW Draft Stage]] |
| 6. Pin evidence to section jobs | Approved source packet and outline needs | Source IDs beside claim slots | Section evidence map | [[SERP Outline Output Contract]] |
| 7. Quarantine unsupported asks | Stakeholder request or competitor pattern | Missing source ID or blocked verdict | Brief blocker note | [[FLOW Approval Queue]] |

## Input, Evidence, Action, Owner, And Handoff

The brief owner records who supplied the source packet, who accepts the framing, and who will draft. If first-party GSC, analytics, or crawl evidence exists, the brief names it separately from market studies. If it does not exist, the brief says that property evidence is missing rather than filling the gap with a public benchmark.

## FLOW Brief Stage Control Points

Reject the brief if it asks the writer to prove a result the evidence does not support, if it treats panel research as client data, or if it describes a Google AI file as required. Send those items back to [[FLOW Source Intake]] or forward them to [[FLOW Approval Queue]] when a stakeholder must decide whether to keep an advisory assumption.

## Example: Turning Market Context Into A Brief

Request: "Write a post that will recover traffic lost to AI answers."

The brief rewrites that into a reader job: answer the comparison question clearly
and add an advisory visibility caveat.

The market-context slot may cite `sparktoro-zero-click-2026`, but it cannot
predict the client's future clicks from the panel source.

The AI note cites `g-ai-opt-guide` and keeps optimization framed as normal
Search fundamentals rather than a new AI-only checklist.

The draft owner receives a source-backed answer promise, an excluded traffic
forecast, and one link to [[AI Citation Mechanics]].

## Brief-Specific Breakpoints

- A competitor H2 copied into the brief can create similarity without evidence.
- A section job that lacks a source ID asks the writer to invent support later.
- A zero-click caveat in the outline can become a fake property forecast.
- A brief that accepts every stakeholder keyword usually loses the reader job.

## Consumed By Brief Contracts

[[Content Brief Output Contract]] consumes the reader job, source pack,
must-use claims, exclusions, and unresolved blockers.

[[SERP Outline Output Contract]] consumes the section evidence map and turns it
into H2/H3 jobs with source IDs beside claim slots.

The brief expects the deliverables to return either draft-ready acceptance or a
blocked field with the owner named.
