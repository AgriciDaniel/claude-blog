---
type: deliverable
title: "FLOW Stage Prompt Map"
domain: "Blog Content Brain"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, flow, prompts]
source_urls:
  - "https://github.com/AgriciDaniel/flow"
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
---

# FLOW Stage Prompt Map

## Stage Purpose Map

This map connects FLOW stages to concrete blog artifacts so [[FLOW Framework]] can move from prompt intent to auditable output. It covers Find, Optimize, and Win across brief, draft, review, factcheck, rewrite, and report work. The source IDs are `gh-flow-framework`, `g-helpful-content`, `g-ai-opt-guide`, and `g-qrg-full`.

## Entry Triggers By FLOW Stage

Find starts when a topic, source packet, or reader job is not yet stable. Optimize starts when a brief or draft exists and needs quality, trust, schema, or citation review. Win starts when the work needs reporting, refresh, distribution, or rollback framing. Each transition must preserve source IDs and confidence.

## Prompt Handoff Table

| FLOW stage | Prompt step | Required input | Produced artifact | Downstream handoff |
|---|---|---|---|---|
| Find | Brief | Reader job, source packet, query context | Source-backed brief | [[SERP-Informed Briefs and Outlines]] |
| Find | Outline | Brief, intent map, competing patterns | Heading plan | Draft owner |
| Optimize | Draft | Outline, facts, voice constraints | Draft section set | [[Voice and Style]] |
| Optimize | Review | Draft, quality rubric, trust flags | Revision memo | [[Blog Quality Score]] |
| Optimize | Factcheck | Claims, source IDs, dates | Claim ledger packet | [[Research Pack Index]] |
| Win | Rewrite | Performance or freshness trigger | Rewrite plan | [[Freshness and Content Decay]] |
| Win | Report | Final status, blockers, confidence | Delivery summary | Project owner |

## Control Points That Stop Prompt Drift

No prompt may ask the model to invent source support, guarantee Google visibility, or create a separate AI feature requirement. `g-ai-opt-guide` keeps AI visibility work attached to normal Search fundamentals, while `g-qrg-full` supports trust review language. If the FLOW step cannot name the next artifact, owner, and evidence state, it loops back to Find rather than moving forward.
