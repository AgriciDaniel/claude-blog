---
type: deliverable
title: "Content Template Selection Matrix"
domain: "Blog Content Brain"
status: active
created: 2026-07-09
updated: 2026-07-23
tags: [deliverables, templates, content-strategy]
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
---

# Content Template Selection Matrix

## Template Selection Job

This matrix tells `/blog write`, `/blog brief`, and `/blog outline` which
claude-blog article shape fits the reader job before drafting starts. It belongs
between [[SERP-Informed Briefs and Outlines]] and [[Blog Quality Score]].
Template IDs, filenames, and optional planning estimates come from the local
claude-blog v2.1.0 skill under `skills/blog/templates/`; Search quality caveats
use source IDs `g-helpful-content`, `g-ai-opt-guide`, and `g-qrg-full`.

## Evidence Required Before A Template Is Picked

The selector needs intent, reader maturity, claim sensitivity, source availability, media need, locale, and whether first-party data exists. It should choose the simplest format that answers the job. Do not choose a template because it sounds optimized for AI; `g-ai-opt-guide` keeps the work tied to normal Search fundamentals.

## Twelve Template Matrix

| Template ID | File path | Intent trigger | Optional planning estimate | Required inputs |
|---|---|---|---|---|
| `how-to-guide` | `skills/blog/templates/how-to-guide.md` | "How to" queries, setup tasks, ordered processes | 2,000-2,500 | Reader task, audience, preconditions, 3+ meaningful steps, source packet, screenshots or images, success test |
| `listicle` | `skills/blog/templates/listicle.md` | "Best", "top", ranked option, tool, resource, or tip queries | 1,500-2,000 | Item set, ranking criteria, inclusion and exclusion rules, source dates, differentiators, media per item |
| `case-study` | `skills/blog/templates/case-study.md` | Client result, before and after, strategy validation, real metric story | 1,500-2,000 | Permission, challenge, strategy, implementation notes, baseline, measured results, caveats |
| `comparison` | `skills/blog/templates/comparison.md` | "X vs Y", alternatives, platform choice, method choice | 1,500-2,000 | Comparable options, decision criteria, feature and pricing facts, equal evidence depth, verdict basis |
| `pillar-page` | `skills/blog/templates/pillar-page.md` | Broad topic hub, complete guide, cluster anchor | 3,000-4,000 | Primary topic, spoke inventory, subtopic map, internal-link plan, source pack, optional reader-driven Q&A |
| `product-review` | `skills/blog/templates/product-review.md` | Product review, "is it worth it", buyer evaluation | 1,500-2,000 | Product facts, pricing, pros and cons, alternatives, disclosure state, and documented testing only when it occurred |
| `thought-leadership` | `skills/blog/templates/thought-leadership.md` | Opinion, prediction, contrarian industry take | 1,500-2,500 | Thesis, conventional view, supporting data, supported author experience or differentiated sourced analysis, caveats, better approach |
| `roundup` | `skills/blog/templates/roundup.md` | Expert quotes, multi-source perspective collection | 1,500-2,000 | Expert list, permission or quote source, inclusion criteria, bios, synthesis themes, methodology |
| `tutorial` | `skills/blog/templates/tutorial.md` | Code, tool, build, install, or configuration walkthrough | 2,000-3,000 | Prerequisites, environment, ordered steps, code or commands, verification test, troubleshooting notes |
| `news-analysis` | `skills/blog/templates/news-analysis.md` | Timely event, release, policy, or algorithm update analysis | 800-1,200 | Event source, event date, what happened, affected audience, immediate actions, retrieval notes |
| `data-research` | `skills/blog/templates/data-research.md` | Original data, survey, experiment, benchmark, statistics query | 2,000-3,000 | Dataset, method, sample, analysis approach, findings, limitations, chart plan |
| `faq-knowledge` | `skills/blog/templates/faq-knowledge.md` | "What is", recurring Q&A, support, knowledge-base topic | 1,500-2,000 | Question inventory, categories, complete intent-matched answers, source pack, related resources, optional visible-content schema plan |

## Interpretation Rules For Write Brief Outline

Sensitive topics need stronger reviewer involvement through [[E-E-A-T for Blog
Content]]. A template can improve clarity, but it cannot compensate for weak
evidence. Planning estimates are optional, intent-dependent, and never score or
block a complete article. When two templates fit, pick the one with the clearest
completion test. If the selected format requires claims the source packet
cannot support, change the format before drafting.
