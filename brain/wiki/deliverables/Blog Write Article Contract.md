---
type: deliverable
title: "Blog Write Article Contract"
domain: "Blog Writing"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, writing, article-contract, active]
---

# Blog Write Article Contract

## Blog Write Article Contract Deliverable Boundary

This contract defines what `/blog write` must return before an article is ready for editorial review. It covers the article draft, evidence placement, media requests, schema notes, and internal-link obligations. It does not publish, mutate a CMS, guarantee rankings, or claim AI inclusion. Google helpful-content guidance is the quality baseline through `g-helpful-content`, while AI-specific claims route through [[AI Citation Mechanics]] and remain bounded by `g-ai-opt-guide`.

### Drafting Inputs That Must Be Present

The writer needs an approved brief, target query, reader job, source IDs, brand voice note, required internal links, and any legal or YMYL constraints. If the topic needs passage-level citability, use `ziptie-aio-source-selection` as practitioner guidance only, not as an official Google rule.

### Exclusions From The Write Contract

The contract excludes keyword-volume promises, backlink plans, CMS formatting quirks, and post-publication performance interpretation. QRG concepts from `g-qrg-full` can inform trust review, but the draft must not describe QRG as a direct ranking checklist. Connect trust issues to [[E-E-A-T for Blog Content]].

## Blog Write Article Package Sections

The output must include an answer-first introduction, H2/H3 structure, claim-backed body, author or reviewer notes, suggested visuals, schema brief, internal-link list, and final delivery gate.

## Blog Write Article Contract Acceptance Table

| Article component | Mandatory field | Validator | Acceptance signal | Handoff owner | Blocker state |
|---|---|---|---|---|---|
| Answer-first intro | Direct answer, audience, date context | Editor reads first 150 words | Reader task is answered before background | Writer | Blocked if the answer is missing |
| Evidence-backed claims | Source ID beside each current claim | Factcheck register comparison | No unsupported statistics or policy claims | Researcher | Blocked if any current claim lacks a source ID |
| AI citation passage | Entity, date, source proximity, caveat | GEO reviewer checks [[AI Citation Mechanics]] | Passage is extractable without overpromising inclusion | GEO owner | Review if only practitioner support exists |
| Media request | Asset purpose, caption need, alt text direction | Media editor checks [[Images Audio and Charts]] | Visual improves comprehension and has provenance | Media owner | Blocked if chart data is absent |
| Schema note | Suggested types and visible-content basis | Schema reviewer checks [[Blog Schema Stack]] | No unsupported rich-result promise | Technical SEO | Blocked if markup invents facts |
| Internal links | Source, target, anchor reason | Content strategist checks topic map | Links support depth rather than stuffing | Strategist | Review if target page is stale |

## Blog Write Article Contract Handoff Procedure

1. Confirm all source IDs named in the draft appear in the approved source pack.
2. Run the draft through [[Blog Quality Score]] and record any blocked category before layout work starts.
3. Send unresolved source, media, schema, or internal-link issues to the named owner instead of leaving comments for a generic reviewer.
4. Release the article only after the delivery gate says pass, pass with fixes, or blocked with a specific reason.

## Source IDs Used

Blog write uses `g-helpful-content`, `g-ai-opt-guide`, `g-qrg-full`, and `ziptie-aio-source-selection`. The Google sources carry official guidance dates in the ledger; the ZipTie source is a dated practitioner reference for answer-passage construction.
