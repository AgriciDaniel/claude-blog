---
type: deliverable
title: "Discourse Research Brief Contract"
domain: "Blog Content Brain"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, discourse, research]
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://www.nngroup.com/articles/ten-usability-heuristics/"
  - "https://sparktoro.com/blog/in-2026-less-than-one-third-of-google-searches-still-send-a-click/"
---

# Discourse Research Brief Contract

## Research Brief Boundary For Public Discourse

This contract governs briefs built from forums, social platforms, communities, comment threads, and other public discourse signals. It supports [[SERP-Informed Briefs and Outlines]] and [[AI Citation Mechanics]] by capturing language patterns and objections without treating snippets as verified facts. The source IDs are `g-helpful-content`, `g-ai-opt-guide`, `nng-editorial-heuristics`, and `sparktoro-zero-click-2026`.

## Inputs And Snippet Trust Rules

Accepted inputs include platform, query operator, date range, thread URL, author context when public, snippet, and cluster label. Excluded inputs include private groups, scraped personal data, deleted content, or claims that cannot be independently sourced. SparkToro's reported search behavior can justify listening beyond click traffic, but it cannot validate a discourse claim.

## Discourse Contract Acceptance Table

| Field | Required evidence | Validator | Blocker state | Owner |
|---|---|---|---|---|
| Recency window | Date range and reason | Researcher | Window does not match topic volatility | Research lead |
| Platform operator | Exact query string and platform | Editor | Search cannot be repeated | Researcher |
| Snippet handling | URL, quote summary, context note | Factchecker | Snippet treated as truth | Factchecker |
| Cluster label | Pain, objection, vocabulary, or use case | Strategist | Cluster mixes unrelated intents | Strategist |
| Source escalation | Needed official or primary source | Researcher | No trustworthy source can support claim | Research lead |
| Synthesis rule | What the brief may infer | Editor | Summary overstates sample | Managing editor |
| Handoff note | Draft use, risk, confidence | Reviewer | No owner for high-risk insight | Project owner |

## Handoff Procedure For Weak Evidence

If discourse only reveals vocabulary, hand it to [[Voice and Style]] or outline framing. If it suggests a factual claim, route it to [[Research Pack Index]] before drafting. If it suggests a product, legal, medical, or financial risk, escalate before publication. `g-ai-opt-guide` prevents the brief from inventing special AI-only files or markup as a response to community speculation.
