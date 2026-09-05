---
type: spoke
title: "Audience Persona Template"
domain: "Blog Voice"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [personas, voice-style, active]
---

# Audience Persona Template

## Audience Persona Template Voice Job

Audience Persona Template turns scattered audience notes into a usable writing constraint before [[SERP-Informed Briefs and Outlines]] or [[FLOW Framework]] asks for a draft. The output is a one-page persona card with the reader's job, trigger, decision stage, topic knowledge, objections, risk sensitivity, and preferred proof type. It should stop writers from assuming that every reader wants the same depth, examples, or CTA.

### Persona Or Brand Constraint Owned Here

This spoke owns reader context, not brand slogans. Use `g-helpful-content` for the people-first test, `g-qrg-full` for purpose and trust sensitivity, `nng-editorial-heuristics` for recognition and error-prevention cues, and `g-ai-opt-guide` when the persona work mentions AI Search visibility. Query language from `g-ads-kw` can inform vocabulary, but it is not proof of a persona by itself.

### Situations That Require Human Editorial Review

Escalate when the persona includes legal, medical, financial, civic, or safety pressure; when the only evidence is a stakeholder guess; or when the draft changes advice for a vulnerable reader. Route YMYL sensitivity to [[YMYL Tone Guardrails]], brand limits to [[Brand Voice Inventory]], and phrase restrictions to [[Banned Claims And Phrases]].

## Audience Persona Template Decision Table

|Persona choice|Input needed|Sources|Evidence|Owner|Action|
|---|---|---|---|---|---|
| Reader job | Interview note, support ticket, SERP intent, or sales call summary | `g-helpful-content`, `g-ads-kw` | advisory until first-party evidence exists | Strategist | Write one task the article must help complete |
| Knowledge level | Draft topic, glossary, known questions | `nng-editorial-heuristics` | editorial heuristic | Editor | Set vocabulary and explanation depth |
| Risk sensitivity | Topic category, claim list, reviewer note | `g-qrg-full` | high for trust-sensitive subjects | Reviewer | Mark cautious tone or expert review need |
| AI-facing context | Request mentions AI answers, snippets, or llms.txt | `g-ai-opt-guide` | official Google guidance | SEO lead | Link to [[AI Citation Mechanics]] without promising citation |
| Objection pattern | Repeated support, sales, or comment theme | `g-helpful-content` | stronger when dated and repeated | Researcher | Name the objection the draft must answer |
| Proof appetite | Source packet plus reader skepticism note | `g-qrg-full` | high when harm or trust risk exists | Reviewer | Set proof depth before drafting begins |
| Locale marker | Target language, region, and URL pattern | `g-localized`, `g-multiregional` | locale-bound until reviewed | Locale editor | Send wording to [[Locale Voice Adaptation]] |

### Constraint, Example, Allowed Variant, Banned Variant, And Scope

The persona card should include an approved example sentence and a forbidden version. "Compare two payroll options without assuming legal expertise" is useful. "Write for busy founders" is too vague unless it names the decision, evidence, and risk. A persona may adjust example order, vocabulary, and proof density; it may not expand a claim past its source.

## Payroll Buyer Card In Use

Topic brief: "payroll software for small clinics" targets an operations lead, not a lawyer.

Evidence packet: sales notes mention multi-state confusion twice; keyword data only informs wording through `g-ads-kw`.

Before persona: "Busy founders need fast payroll tips."

After persona: "Clinic operations leads comparing payroll tools need vendor questions, state-limit caveats, and implementation checks."

The rewrite narrows reader role, decision pressure, and proof type without making a legal recommendation.

The risk row routes payroll compliance language to [[YMYL Tone Guardrails]] because QRG trust framing applies through `g-qrg-full`.

The proof row asks for dated source IDs beside policy claims, while `g-helpful-content` keeps the card grounded in a useful reader task.

## Persona-Specific Breakpoints

- Keyword volume becomes a fake persona when no dated audience evidence exists; keep `g-ads-kw` as vocabulary support only.
- A founder persona and a practitioner persona cannot share one CTA when they own different decisions.
- "Beginner" fails if the draft still assumes CFO, SEO, or developer shorthand.
- Risk sensitivity is not a tone adjective; it changes caveat placement and reviewer ownership.
- AI Search requests can erase the human reader unless `g-ai-opt-guide` bounds the note.
- Locale assumptions fail when the same job uses different institutions or legal language.

## Contract Wiring

Primary consumer: [[Persona Profile Contract]].

Inputs supplied: reader job, trigger, stage, known terms, objections, risk level, preferred proof, banned variant, and source IDs.

Output expected back: accepted persona fields, reviewer owner, escalation state, and unresolved evidence gaps.

Secondary consumer: [[Content Brief Output Contract]] uses the reader job and proof appetite before outline planning.

## Audience Persona Template Drift Check

Refresh the card when the product, target locale, buyer role, regulatory risk, or source packet changes. If a persona has no evidence after review, mark it as a hypothesis and block it from driving tone or examples.
