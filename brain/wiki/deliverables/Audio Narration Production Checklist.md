---
type: deliverable
title: "Audio Narration Production Checklist"
domain: "Blog Content Brain"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, audio, production]
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://schema.org/docs/full.html"
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
---

# Audio Narration Production Checklist

## Narration Review Scope

This checklist governs audio versions of blog material: summary narration, full article narration, dialogue scripts, embedded players, transcript fidelity, and graceful failure when an audio API is unavailable. It routes media choices through [[Images Audio and Charts]] and structured data questions through [[Blog Schema Stack]]. The source IDs are `g-helpful-content`, `g-ai-opt-guide`, `schema-full`, and `g-intro-sd`.

## Audio Inputs Before Production

The producer must receive the final article, the approved script mode, pronunciation notes, voice constraints, transcript target, and publish location. The script cannot introduce claims that are absent from the article source packet. If the narration is generated, the page still needs reader-first value and visible accountability rather than a hidden automation claim.

## Pass Fail Checklist

| Check | Pass evidence | Fail state | Severity | Fix owner |
|---|---|---|---|---|
| Script mode | Summary, full, or dialogue mode named | Mixed mode with no editorial purpose | Major | Producer |
| Claim fidelity | Narration matches sourced article claims | Audio adds unsourced facts | Blocker | Factchecker |
| Voice choice | Voice fits [[Voice and Style]] and audience | Voice undermines trust or accessibility | Major | Editor |
| Accessibility | Transcript or equivalent text is planned | Audio-only asset ships alone | Blocker | Producer |
| Embed output | Player location, file name, and fallback link recorded | Broken embed or no fallback | Major | CMS owner |
| Structured data | Schema strings align with visible content | Markup describes content not present | Blocker | Schema reviewer |

## Handoff Rules For Failed Checks

Do not publish a narration file just because generation succeeded. If the audio API fails, ship the readable article and record the missing media state. If schema is used, `g-intro-sd` supports the general structured-data guardrail and `schema-full` is the vocabulary route, but the note does not claim a special audio ranking boost. For AI feature visibility, `g-ai-opt-guide` keeps the recommendation grounded in ordinary Search fundamentals, not a separate audio-only optimization path.
