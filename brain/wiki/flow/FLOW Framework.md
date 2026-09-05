---
type: hub
title: "FLOW Framework"
domain: "Blog Workflow"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [flow, active]
confidence: verified
related:
  - "[[FLOW Source Intake]]"
  - "[[FLOW Brief Stage]]"
  - "[[FLOW Draft Stage]]"
  - "[[FLOW Review Stage]]"
  - "[[FLOW Factcheck Stage]]"
  - "[[FLOW Report Stage]]"
---

# FLOW Framework

## FLOW Framework Operating Scope

FLOW Framework is the evidence discipline layer for blog planning, drafting, checking, rewriting, and reporting. It keeps the workflow from becoming a generic prompt chain by requiring source IDs, confidence, owners, and handoffs at each stage. The FLOW bibliography is the local framework source (source_id: `gh-flow-framework`). Google helpful-content guidance and the QRG inform usefulness and trust review (source_ids: `g-helpful-content`, `g-qrg-full`). Google AI optimization guidance keeps AI feature work grounded in Search fundamentals rather than separate folklore requirements (source_id: `g-ai-opt-guide`).

### What This Hub Owns In FLOW Evidence Workflow

The hub owns stage boundaries, source discipline, confidence tags, approval routing, and reporting shape. It connects writing work to [[FLOW Source Intake]], [[FLOW Brief Stage]], [[FLOW Draft Stage]], [[FLOW Review Stage]], [[FLOW Factcheck Stage]], [[FLOW Rewrite Stage]], [[FLOW Approval Queue]], [[FLOW Rollback Notes]], and [[FLOW Report Stage]].

### What The Hub Must Not Absorb

The hub must not absorb every SEO concept, rewrite tactic, schema rule, or Google update. Those belong in their canonical notes such as [[AI Citation Mechanics]], [[Blog Schema Stack]], [[E-E-A-T for Blog Content]], and [[2026 Google Update Timeline]]. FLOW points to those notes when evidence is needed.

## FLOW Framework Spoke Map

| Spoke | Input | Evidence required | Produced artifact | Downstream handoff |
|---|---|---|---|---|
| [[FLOW Source Intake]] | Raw source, claim, update, or study | Source ID, date, limitation | Intake packet | [[FLOW Brief Stage]] |
| [[FLOW Brief Stage]] | Reader problem and intake packet | Helpful-content baseline, claim map | Draftable brief | [[FLOW Draft Stage]] |
| [[FLOW Draft Stage]] | Approved brief and voice constraints | Bound source IDs | Source-preserving draft | [[FLOW Review Stage]] |
| [[FLOW Review Stage]] | Draft and rubric | Usefulness, trust, link, schema signals | Revision memo | [[FLOW Factcheck Stage]] |
| [[FLOW Factcheck Stage]] | Claims and citations | Ledger verdicts and source dates | Checked claim register | [[FLOW Confidence Tags]] |
| [[FLOW Rewrite Stage]] | Refresh, consolidation, or pruning trigger | Current evidence and rollback risk | Rewrite plan | [[FLOW Approval Queue]] |
| [[FLOW Report Stage]] | Decisions, blockers, risks | Verified or advisory findings | Delivery summary | Human owner |
| [[FLOW Confidence Tags]] | Checked claim or recommendation | Verdict, source type, limitation | Confidence label | [[Factcheck Claim Register]] |
| [[FLOW Read Only Boundary]] | Account, CMS, or data-access request | Product boundary and API source IDs | Advisory-only packet | Human operator |
| [[FLOW Rollback Notes]] | Accepted live-change recommendation | Trigger, owner, review window | Reversal note | [[Blog Rewrite Refresh Plan]] |

## Spoke Jobs And Deliverable Boundaries

Each spoke produces one artifact and names the next owner. If a stage cannot name an artifact, it has drifted into general advice. If it cannot cite a source ID for a current claim, it loops back to intake. If it affects live content, it waits in the approval queue.

## FLOW Framework Evidence And Refresh Rules

Use official sources for rule-like claims, the QRG for quality-evaluation framing, and practitioner studies only with their limits. Refresh FLOW notes when source-ledger records change, Google Search guidance changes, or a report reveals a repeated handoff failure.

## Example: Routing A Full Article Job

A `/blog write` request arrives with a topic, target reader, and AI citation ask.

The hub sends source discovery to [[FLOW Source Intake]], the reader job to
[[FLOW Brief Stage]], and wording work to [[FLOW Draft Stage]] only after the
source packet exists.

AI visibility language stays tied to Google guidance from `g-ai-opt-guide`; any
passage-level extraction tactic keeps practitioner scope from `ziptie-aio-source-selection`.

If the draft asks for a live CMS edit, [[FLOW Read Only Boundary]] converts that
request into an approval packet instead of an action.

## Hub-Level Routing Errors

- The framework becomes a dumping ground for schema, E-E-A-T, and update detail.
- A prompt skips intake and reaches drafting with no dated source packet.
- A factcheck result reaches the report without a confidence tag.
- A live-content decision bypasses approval because the draft "looks ready."

## Consumed By Stage Maps

[[FLOW Stage Prompt Map]] consumes the stage order, artifact names, required
inputs, and downstream owner expectations from this hub.

It expects the hub to output a lane decision: Find for brief and outline work,
Optimize for draft, review, and factcheck, or Win for report and rewrite work.

When the map cannot name source IDs, owners, and output artifacts, it should
loop the task back to [[FLOW Source Intake]].
