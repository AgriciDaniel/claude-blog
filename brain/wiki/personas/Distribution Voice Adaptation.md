---
type: spoke
title: "Distribution Voice Adaptation"
domain: "Blog Voice"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [personas, voice-style, active]
---

# Distribution Voice Adaptation

## Distribution Voice Adaptation Channel Job

Distribution Voice Adaptation converts a finished blog claim into email, social, community, video, podcast, and AI-answer-review contexts without changing what the source supports. It belongs between [[Voice and Style]] and [[Distribution and Repurposing]]: voice can become shorter or more conversational, but claim scope, dates, and caveats travel with the asset.

### Channel-Specific Voice Boundaries

Use `g-helpful-content` to preserve reader value, `g-qrg-full` to keep trust-sensitive caveats visible, `g-update-2025-01-23-qrg-update-jan-2025` for scaled or low-value content warnings, and `g-update-2025-09-11-qrg-update-sept-2025` when AI Overview examples or expanded YMYL scope affect review. `g-ai-opt-guide` applies when a channel draft implies special Google AI setup.

### Human Review For Derived Assets

Escalate when a derivative asset drops a material qualifier, strips the source date, changes the audience from expert to consumer, or reframes an advisory note as an implementation order. Use [[Banned Claims And Phrases]] before publishing short hooks.

## Distribution Voice Adaptation Matrix

| Channel | Allowed voice shift | Claim lock | Evidence required | Review cue | Handoff |
|---|---|---|---|---|---|
| Email | Warmer and more personal | Source date and canonical URL remain | `g-helpful-content` | Forwarded copy must stand alone | [[Distribution and Repurposing]] |
| Social | Sharper opening, one idea per post | No ranking or citation promise | `g-qrg-full` | Hook cannot outrun evidence | [[Banned Claims And Phrases]] |
| Community | More conversational and question-led | Caveats stay attached to advice | `g-update-2025-01-23-qrg-update-jan-2025` | Avoid thin copied summaries | [[Persona Evidence Packet]] |
| AI answer review | More self-contained phrasing | No AI inclusion guarantee | `g-ai-opt-guide` | Route to canonical hub | [[AI Citation Mechanics]] |
| Short video | Spoken and visual hook | Claim matches article wording | `g-helpful-content` | On-screen text carries the qualifier | [[Repurposing Asset Matrix]] |
| Podcast prompt | Conversational setup | Host cannot add unsourced anecdotes | `g-qrg-full` | Producer marks speculation clearly | [[Audio Narration Production Checklist]] |
| Newsletter subject | Concise and timely | No fear or scarcity without evidence | `nng-editorial-heuristics` | Subject line matches body claim | [[Repurposing Asset Matrix]] |

### Channel, Allowed Shift, Claim Lock, And Review Cue

The adapter should record the source post, channel, changed wording, retained claim, omitted context, and reviewer. If a format cannot carry the caveat, the asset should narrow the claim or stay unpublished.

## Short Hook Conversion Example

Source article claim: "Google documents ordinary Search fundamentals for AI features and does not require a special AI file."

LinkedIn draft: "You do not need a secret AI SEO file."

Review decision: publish only if the post links the official boundary and avoids making a universal platform claim, citing `g-ai-opt-guide`.

Email rewrite: "For Google Search AI features, keep standard crawlable content and skip llms.txt promises."

Video caption: "Google AI guidance follows SEO basics; no special AI markup is required for that surface."

The short-video version keeps the platform scope visible because `g-ai-features` and `g-ai-opt-guide` do not cover every assistant.

## Channel Breakpoints

- A social hook quotes the punchline but drops the source date.
- A community prompt turns a caveat into a controversy bait question.
- A podcast host adds personal advice to a YMYL example without review.
- An email subject says "new rule" when the source is a living guide.
- A video lower-third shortens a claim until the platform qualifier disappears.
- A thread splits one caveated claim across posts and leaves the caveat last.

## Matrix Wiring

Primary consumer: [[Repurposing Asset Matrix]].

Inputs supplied: source article URL, channel, original claim, changed wording, carried caveat, omitted context, and reviewer.

Output expected back: approval state, link target, measurement signal, and blocked channel variants.

Audio consumer: [[Audio Narration Production Checklist]] receives podcast prompts and voice constraints before production.

## Distribution Voice Adaptation Drift Controls

Sample assets after each campaign. If the same channel repeatedly drops source context, rework the channel template before creating more variants.
