---
type: hub
title: "Voice and Style"
domain: "Blog Voice"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [personas, voice-style, active]
---

# Voice and Style

## Voice and Style Operating Scope

Voice and Style keeps blog content recognizable, useful, source-bound, and appropriate for reader risk. The hub owns the operating system for personas, brand voice, tone, terminology, examples, readability, distribution adaptation, localization voice, and drift review. It is a control hub for content decisions, not a publishing workflow.

### What This Hub Owns In Persona, Brand Voice, And Style Controls

This hub owns the route from [[Audience Persona Template]] to [[Brand Voice Inventory]], [[Tone By Funnel Stage]], [[Terminology Control List]], [[Readability Review]], and [[Voice Drift Audit]]. It also routes sensitive language through [[YMYL Tone Guardrails]] and localized voice through [[Locale Voice Adaptation]]. Evidence posture comes from `g-helpful-content`, `g-qrg-full`, `nng-editorial-heuristics`, and `g-ai-opt-guide`.

### What The Hub Must Not Absorb

It must not duplicate [[Blog Quality Score]], [[Blog Schema Stack]], [[AI Citation Mechanics]], [[Distribution and Repurposing]], [[Multilingual Publishing]], or [[Research Pack Index]]. It does not promise rankings, traffic, AI visibility, rich results, compliance, or publication. If a recommendation needs source discovery, external data, or CMS action, the hub records the handoff and stops.

## Voice and Style Spoke Map

| Spoke | Job | Deliverable boundary | Primary source IDs | Refresh trigger |
|---|---|---|---|---|
| [[Audience Persona Template]] | Convert reader evidence into writing constraints | Persona card, not market forecast | `g-helpful-content`, `g-qrg-full` | Persona or product changes |
| [[Banned Claims And Phrases]] | Block unsupported certainty | Stoplist, not legal advice | `g-ai-opt-guide`, `nng-editorial-heuristics` | New banned pattern appears |
| [[Example Selection Rules]] | Pick examples that fit reader and proof | Example approval, not source creation | `g-helpful-content`, `g-qrg-full` | Locale or risk changes |
| [[Distribution Voice Adaptation]] | Adapt channel voice without claim drift | Asset voice note, not posting action | `g-update-2025-01-23-qrg-update-jan-2025` | New channel template |
| [[Persona Evidence Packet]] | Prove a persona is usable | Evidence packet, not demand forecast | `g-helpful-content`, `g-gsc-api` | Audience evidence changes |
| [[Brand Voice Inventory]] | Store approved voice patterns | Sample inventory, not proof library | `nng-editorial-heuristics`, `g-qrg-full` | Positioning changes |
| [[Tone By Funnel Stage]] | Match tone to reader pressure | Tone row, not conversion promise | `g-helpful-content`, `g-qrg-full` | Stage changes |
| [[Terminology Control List]] | Keep terms and names stable | Glossary row, not taxonomy action | `g-ai-opt-guide`, `g-nlp` | Term drift appears |
| [[Readability Review]] | Preserve clarity and source proximity | Inspection result, not grammar pass | `g-helpful-content`, `nng-editorial-heuristics` | Draft structure changes |
| [[Locale Voice Adaptation]] | Localize voice without claim drift | Locale wording review, not hreflang fix | `g-localized`, `g-multiregional` | New locale or URL set |
| [[Voice Drift Audit]] | Detect systemic voice drift | Sample finding, not rewrite pass | `g-spam-policies`, `g-helpful-content` | Repeated drift appears |
| [[YMYL Tone Guardrails]] | Reduce risky certainty | Tone guardrail, not factual verdict | `g-qrg-full`, `g-helpful-content` | Sensitive topic enters |

### Spoke Jobs And Deliverable Boundaries

Each spoke should name the artifact it produces and the artifact it refuses to own. That boundary keeps a style discussion from swallowing evidence review, schema implementation, or analytics interpretation.

## Hub Routing Example

Incoming task: draft a decision-stage article about AI citation readiness for finance software buyers.

Route first to [[Persona Evidence Packet]] because the buyer role and objections must be dated before tone choices matter.

Then use [[Tone By Funnel Stage]] to set cautious decision language and CTA pressure.

Run [[Banned Claims And Phrases]] before the outline because AI inclusion guarantees are blocked by `g-ai-opt-guide`.

Send finance examples through [[YMYL Tone Guardrails]] with `g-qrg-full` controlling the trust posture.

Finally, [[Readability Review]] checks whether caveats and source IDs sit close enough for a skimming reader.

The hub records the path but leaves article acceptance to [[Blog Write Article Contract]].

## Hub-Level Failure Patterns

- The hub becomes a catch-all review queue and hides who owns the actual fix.
- Voice discussion starts before the persona evidence packet has a verdict.
- A schema or AI Search issue is debated here instead of moving to the correct technical note.
- A style preference overrides a source caveat and changes the claim.
- Localized drafts skip [[Locale Voice Adaptation]] because the English version sounded clear.
- A repeated drift signal stays in comments instead of reaching [[Voice Drift Audit]].

## Deliverable Wiring

Primary consumer: [[Brand Context Contract]].

Inputs supplied: approved persona route, voice inventory state, banned patterns, glossary rules, and escalation owners.

Output expected back: usable brand context, missing voice inputs, and contract blockers.

Article consumer: [[Blog Write Article Contract]] receives the final voice route before drafting or review.

## Voice and Style Evidence And Refresh Rules

Refresh this hub when Google helpful-content guidance, the full QRG, the AI optimization guide, or the editorial heuristics source changes in `references/source-ledger.json`. Review the spoke map after three repeated drift findings or after a major brand positioning change.
