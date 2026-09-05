---
type: spoke
title: "Persona Evidence Packet"
domain: "Blog Voice"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [personas, voice-style, active]
---

# Persona Evidence Packet

## Persona Evidence Packet Evidence Job

Persona Evidence Packet stores the proof that a persona is real enough to guide content. It captures interviews, support questions, sales notes, query language, survey excerpts, analytics observations, and exclusions. Without this packet, [[Audience Persona Template]] should mark the persona as a hypothesis.

### Persona Facts This Packet Can Own

The packet can own reader jobs, vocabulary, objections, comparison criteria, risk sensitivity, and evidence preferences. It cannot prove market demand or ranking opportunity by itself. Use `g-helpful-content` for audience-usefulness framing, `g-qrg-full` for trust and YMYL caution, `nng-editorial-heuristics` for recognizable wording, and `g-ai-opt-guide` when persona assumptions are used for AI answer readiness. `g-gsc-api` and `g-ga4-data` may support first-party behavioral evidence when exports exist.

### Human Review For Thin Evidence

Escalate when evidence comes from one stakeholder, one anecdote, generated personas, or a sample that excludes the intended reader. Sensitive roles and locales need review through [[YMYL Tone Guardrails]] or [[Locale Voice Adaptation]].

## Persona Evidence Packet Evidence Table

| Evidence type | Required input | Source ID or data route | Verdict discipline | Owner | Next action |
|---|---|---|---|---|---|
| Interview pattern | Date, role, excerpt, consent-safe summary | local evidence plus `g-helpful-content` | advisory until repeated | Research lead | Extract job and objection |
| Search language | Query set, intent note, date range | `g-gsc-api` or keyword source | observed, not persona proof | SEO analyst | Separate wording from need |
| Support or sales theme | Ticket or call theme, count, date | local evidence | stronger if repeated | Customer owner | Add exact pain language |
| Risk flag | Topic sensitivity and reviewer note | `g-qrg-full` | block if unresolved | Editor | Route to tone guardrail |
| Analytics behavior | Landing page, segment, and date range | `g-ga4-data` | behavior, not motivation | Analyst | Pair with qualitative evidence |
| Survey excerpt | Question text, respondent role, date | local evidence plus `g-helpful-content` | stronger when sample is named | Research lead | Extract wording cautiously |
| Exclusion note | Who the page is not for | `g-helpful-content` | valid when tied to task mismatch | Strategist | Prevent wrong-reader examples |

### Claim, Required Input, Source ID, Verdict, Owner, And Next Action

Each row should say what the evidence proves and what it does not prove. Do not promote a pattern to CONFIRMED unless the evidence is dated, repeated, and appropriate for the content decision.

## Evidence Packet Worked Case

Packet topic: "AI citation readiness for an enterprise blog team."

Evidence included: three support summaries ask about passage review, and GSC exports show queries containing "AI Overview" language through `g-gsc-api`.

Evidence excluded: a stakeholder claim that every buyer wants ChatGPT citations.

Verdict: the reader vocabulary can mention AI answer review, but the persona cannot promise or assume citation demand.

The packet cites `g-ai-opt-guide` when explaining that Google does not require special AI files for AI features.

The researcher adds an exclusion: developers building schema pipelines are outside this article's primary persona.

The persona card receives the job statement only after the evidence owner marks dates and source IDs.

## Packet Failure Modes

- Search queries prove wording familiarity, then get misused as proof of audience motivation.
- One support ticket is promoted into a segment because it sounds vivid.
- Analytics data is imported without page, date range, or segment filters.
- Survey answers lose the original question wording and change interpretation.
- A sensitive persona is approved without reviewer ownership under `g-qrg-full`.
- Negative evidence is omitted, so the draft keeps serving the wrong reader.

## Deliverable Handoff

Primary consumer: [[Persona Profile Contract]].

Inputs supplied: dated evidence rows, exclusions, verdict discipline, source IDs, owner, and next action.

Output expected back: persona fields accepted, hypothesis labels, and blockers that prevent style use.

Brief consumer: [[Content Brief Output Contract]] uses only accepted reader jobs and vocabulary findings.

## Persona Evidence Packet Expiry Check

Refresh evidence when the buyer changes, the product changes, the locale changes, or the draft uses a new risk category. Archive stale persona claims rather than leaving them as quiet assumptions.
