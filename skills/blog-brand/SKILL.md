---
name: blog-brand
description: >
  Establish durable brand and voice context for cross-skill consumption.
  Generates BRAND.md (audience, positioning, do/don't editorial rules, taboo
  phrases, competitor differentiation) and VOICE.md (existing persona JSON
  re-expressed as readable prose), both written to the project root. When
  present, the blog orchestrator auto-loads these files for write, rewrite,
  brief, outline, calendar, and strategy workflows. Pairs with blog-persona, which manages the structured persona
  JSON. Use when user says "blog brand", "create brand context", "brand
  voice doc", "BRAND.md", "VOICE.md", "establish editorial brand",
  "brand guidelines for blog".
user-invokable: true
argument-hint: "[init|show|update]"
license: MIT
---

# Blog Brand: Durable Editorial Context

Generates two project-root files that the blog orchestrator auto-loads for supported writing and planning commands when present:

- `BRAND.md`: who the audience is, what the brand stands for, what to never say
- `VOICE.md`: how the brand sounds, structurally and lexically

These are the editorial equivalent of impeccable's PRODUCT.md / DESIGN.md pattern: persistent context that survives across sessions and propagates to every command.

## Why this exists

Today, persona JSON (from `blog-persona`) is loaded by some skills and not others. Topic-cluster context lives inside cluster vaults. Competitor positioning lives nowhere. Each blog command re-derives "what is the brand" from whatever context it has.

`BRAND.md` and `VOICE.md` fix this: one canonical source, loaded by the `blog` orchestrator at the start of every command.

When neither file exists, behavior is unchanged from v1.7.1. Backward compatible.

## Commands

| Command | Purpose |
|---|---|
| `/blog brand init` | Interactive interview, writes BRAND.md and VOICE.md to project root |
| `/blog brand show` | Display current contents (or report missing) |
| `/blog brand update` | Re-run the interview with current values as defaults |

## Init Workflow

Run the 5-step interactive interview. Ask each step, wait for response, then proceed. If `blog-persona` JSON already exists, pre-fill voice answers from it.

### Step 1: Audience

Ask:
- **Primary audience role** (e.g. "head of marketing at a 50-500 person B2B SaaS")
- **Secondary audience** (optional)
- **Reader expertise level**: beginner / intermediate / advanced / mixed
- **Problems the reader is actively trying to solve** (3 to 5 bullets)
- **Common misconceptions the audience holds** (used to anchor information gain)

### Step 2: Positioning and Canonical Entity

Ask:
- **Official entity name** (legal or public brand name)
- **Homepage URL** (canonical brand front door)
- **Logo URL or file path** (preferred square or SVG asset)
- **sameAs profiles** (LinkedIn, X, YouTube, Crunchbase, GitHub, or other official profiles)
- **Wikidata Q-ID** if one exists; leave blank if not notable
- **One-sentence brand mission** (what the brand helps people do)
- **Distinctive point of view** (the contrarian or non-obvious belief that shapes content)
- **What this brand is NOT** (anti-positioning, what to never be confused with)
- **Top 3 direct competitors** with the one-line differentiator vs each

### Step 3: Editorial rules

Ask:
- **Do list** (3 to 7 things the blog will always do; e.g. "cite primary sources only," "name the practitioner not the product")
- **Don't list** (3 to 7 things the blog will never do; e.g. "no clickbait titles," "no listicle filler")
- **Taboo phrases** (specific words or phrases this brand never uses; separate
  from the repository's optional project style list)
- **Required disclosures** (e.g. affiliate disclosure, AI-content disclosure, conflict-of-interest patterns)

### Step 4: Topic boundaries

Ask:
- **Topics fully in scope** (core content pillars)
- **Topics partially in scope** (adjacent; covered only with original angle)
- **Topics out of scope** (will not cover; redirect to partner content)
- **Recurring formats / column names** if any (e.g. "Monthly Field Notes," "Reader Q&A")

### Step 5: Voice (auto-fill from blog-persona if present)

Ask:
- **Pronoun stance**: first-person (we / I), second-person (you), third-person (the team), or mixed
- **Acceptable contractions**: full / partial / none
- **Sentence ceiling**: max words per sentence as a hard cap
- **Paragraph ceiling**: max words per paragraph (default 150)
- **Headline patterns to favor**: numbered / question / promise / statement
- **Headline patterns to avoid**: any patterns banned for this brand
- **Summary box label**: from blog-persona, or pick one

## Output Files

### BRAND.md template

Write to project root as:

```markdown
# Brand Context

> This file is auto-loaded by all blog sub-skills. Last updated: YYYY-MM-DD.

## Audience

- **Primary**: [role + context]
- **Secondary**: [if any]
- **Expertise**: [level]
- **Active problems**:
  - [problem 1]
  - [problem 2]
  - [problem 3]
- **Common misconceptions**:
  - [misconception 1]
  - [misconception 2]

## Positioning

- **Official entity name**: [brand/entity]
- **Homepage**: [canonical URL]
- **Logo**: [URL or file path]
- **sameAs profiles**:
  - [profile URL 1]
  - [profile URL 2]
- **Wikidata Q-ID**: [QID or none]
- **Mission**: [one sentence]
- **Distinctive POV**: [contrarian or non-obvious belief]
- **What we are NOT**: [anti-positioning]
- **Competitors**:
  - [Competitor A]: [our one-line differentiator]
  - [Competitor B]: [our one-line differentiator]
  - [Competitor C]: [our one-line differentiator]

## Editorial Rules

### Always do
- [rule 1]
- [rule 2]
- [rule 3]

### Never do
- [rule 1]
- [rule 2]
- [rule 3]

### Taboo phrases
- [phrase 1]
- [phrase 2]

### Required disclosures
- [disclosure rule]

## Topic Scope

- **In scope**: [pillars]
- **Partial scope**: [adjacent topics]
- **Out of scope**: [topics to refuse]
- **Recurring formats**: [if any]
```

### VOICE.md template

Write to project root as:

```markdown
# Voice Context

> This file is auto-loaded by all blog sub-skills. Last updated: YYYY-MM-DD.

## Pronoun stance
[first-person / second-person / third-person / mixed]

## Lexical rules
- **Contractions**: [full / partial / none]
- **Sentence ceiling**: [N words max]
- **Paragraph ceiling**: [N words max, default 150]
- **Summary label**: [Key Takeaways / TL;DR / etc.]

## Headline patterns
- **Favor**: [list]
- **Avoid**: [list]

## Voice fingerprint (from blog-persona)
- Funny vs serious: [0.0 to 1.0]
- Formal vs casual: [0.0 to 1.0]
- Respectful vs irreverent: [0.0 to 1.0]
- Enthusiastic vs matter-of-fact: [0.0 to 1.0]

## Readability target
- Audience tier: [consumer / professional / technical]
- Flesch Grade: [range]
- Flesch Ease: [range]

## Reference samples
- [URL 1] (extracted patterns: [summary])
- [URL 2] (extracted patterns: [summary])
```

## Show Workflow

1. Check for `BRAND.md` and `VOICE.md` at project root.
2. If both exist, print a summary table (key sections only) and the file paths.
3. If one or both are missing, print which are missing and suggest `/blog brand init`.

## Update Workflow

Same as Init, but pre-fills every answer with the current value. The user can press enter to accept or type a new value. After collecting all answers, overwrite both files with the new contents and update the `Last updated:` line.

## Integration with the blog orchestrator

When `/blog write`, `/blog rewrite`, `/blog brief`, `/blog outline`, `/blog calendar`, or `/blog strategy` runs, the orchestrator (`skills/blog/SKILL.md`) checks for `BRAND.md` and `VOICE.md` at the project root. If present, the contents are injected into the system prompt for downstream agents (`blog-researcher`, `blog-writer`, `blog-seo`, `blog-reviewer`).

If absent, behavior is unchanged. The orchestrator does not prompt the user to create them; they are opt-in context.

## Relationship to blog-persona

| Concern | blog-persona | blog-brand |
|---|---|---|
| Structured persona JSON for programmatic use | Yes | No |
| Readable brand context for cross-skill prompts | No | Yes |
| Audience and positioning | No | Yes |
| Taboo phrases and editorial don'ts | Partial (don't list) | Full (taboo + disclosures + scope) |
| Competitor differentiation | No | Yes |
| Topic boundaries | No | Yes |
| Voice fingerprint (tone sliders) | Yes (canonical) | Mirror (read-only) |

`blog-brand` does not replace `blog-persona`; it consumes it. The persona JSON remains the source of truth for tone dimensions, sentence-length distribution, and contraction frequency. `VOICE.md` mirrors the readable parts so prompts are self-contained.

If no persona exists when `/blog brand init` runs, the voice questions still produce a `VOICE.md`. Users who want programmatic enforcement can run `/blog persona create` after.

## Error Handling

- **Project root unclear**: ask the user where to write the files. Default is the current working directory.
- **Files already exist on init**: ask whether to overwrite or run update instead.
- **Persona referenced but missing**: ask whether to leave the persona reference blank or create one.
- **Reader provides minimal answers**: prompt for at least 2 audience bullets and 3 editorial rules; refuse to write skeletons.
