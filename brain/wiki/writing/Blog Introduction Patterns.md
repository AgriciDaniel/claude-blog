---
type: spoke
title: "Blog Introduction Patterns"
domain: "Blog Writing"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [writing, six-pillar, evergreen]
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
---

# Blog Introduction Patterns

## Blog Introduction Patterns Entry Job

This note owns the opening block before the first substantive H2. The introduction should confirm the reader's problem, preview the answer path, and set the evidence standard. It should not delay the answer with history, brand framing, or a generic claim about search volatility.

### Opening Moves This Note Allows

Use a problem-confirmation opening when the query is broad and the reader may still be clarifying the task. Use a direct-answer opening when the target query is specific. Use a scope boundary opening when the article involves changing Search guidance, AI features, or YMYL-adjacent decisions. `g-helpful-content` supports the people-first requirement; `g-qrg-full` raises the bar when trust, safety, or expertise are part of the topic.

### AI And Search Caveats In The First Screen

An introduction may say that the article considers AI-search visibility only when the claim stays sourced and measured. It must not tell readers to add an AI-only artifact for Google Search. `g-ai-opt-guide` and `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` together anchor that boundary. For broad click behavior or citation mechanics, link to [[AI Citation Mechanics]] instead of restating a panel statistic here.

## Introduction Pattern Matrix

| Intro pattern | Best fit | Required evidence before use | Reader promise | Source IDs | Fix if weak |
|---|---|---|---|---|---|
| Problem confirmation | Broad educational query | Audience pain and intent notes | "This explains the decision space" | `g-helpful-content` | Replace vague stakes with a specific task |
| Direct answer preview | Narrow how-to or definition | Approved primary answer | "This gives the answer then exceptions" | `g-helpful-content`, `g-ai-opt-guide` | Move answer into sentence one |
| Scope boundary | Fast-moving Search or AI topic | Date, source age, and caveat | "This covers what is currently supported" | `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` | Add dated wording |
| Trust setup | YMYL-adjacent or expert-heavy topic | Author, reviewer, or source authority | "This shows who and what the reader can verify" | `g-qrg-full` | Add byline or reviewer context |
| Evidence preview | Research-led article or audit | Source pack and verdict labels | "This tells how claims will be proven" | `g-helpful-content`, `g-qrg-full` | Name evidence type before tactic |
| Audience boundary | Mixed beginner and expert demand | Reader job and excluded use case | "This is for a specific operator" | `g-helpful-content` | Cut the audience sprawl |

## Introduction Editing Pass

1. Delete the first paragraph if it could fit any article in the niche.
2. State the reader task in the first or second sentence.
3. Preview the article's evidence type before naming tactics.
4. Move broad market context to a linked hub if it is not needed to start the answer.
5. Check whether the promise can be fulfilled by the sections that follow.
6. Send any unverified search-feature claim to [[Research Pack Index]] before drafting continues.

### Opening Rewrite Scenario

Before: "Search is changing fast, and brands need stronger blog strategy."
After: "Use this checklist when a finished blog draft has claims, links,
and AI-search caveats that must be verified before publication."
The second version names the reader task and evidence standard,
which matches people-first guidance (`g-helpful-content`).
If the intro mentions Google AI features, it must stay inside documented
Search guidance rather than promising a new visibility path (`g-ai-opt-guide`).

### First-Screen Mistakes

- The hook names volatility but not the reader's immediate job (`g-helpful-content`).
- The intro promises a comparison while the H2s deliver a tutorial (`g-helpful-content`).
- A trust-sensitive topic starts without author, reviewer, or method context (`g-qrg-full`).
- AI-search framing appears before the draft has source dates (`g-ai-opt-guide`).

### Deliverable Wiring

[[Content Brief Output Contract]] consumes this note before drafting:
reader job, opening promise, source standard, excluded claim, and audience boundary.
It expects the brief to hand writers a startable promise, not a loose theme.
[[SERP Outline Output Contract]] uses the same inputs to validate the H1,
intro job, and first H2 sequence before the article is written (`g-helpful-content`).

## Source Handling

The working source IDs are `g-helpful-content`, `g-ai-opt-guide`, `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`, and `g-qrg-full`. Use them to shape the opening promise, not to inflate the introduction with source names.

## Related

- [[6-Pillar Dual Optimization]]
- [[Intent Fit Writing Pass]]
- [[E-E-A-T for Blog Content]]
- [[AI Citation Mechanics]]
