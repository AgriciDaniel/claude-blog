---
type: deliverable
title: "NotebookLM Research Brief Contract"
domain: "Blog Content Brain"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, research, brief]
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
  - "https://sparktoro.com/blog/in-2026-less-than-one-third-of-google-searches-still-send-a-click/"
---

# NotebookLM Research Brief Contract

## Brief Boundary For Source Bound Work

This contract defines what a NotebookLM-assisted research brief may hand to [[SERP-Informed Briefs and Outlines]], [[AI Citation Mechanics]], or [[Blog Quality Score]]. It does not treat a generated answer as evidence by itself. It requires source provenance, query trace, fallback handling, and reviewer ownership before any claim reaches a draft. The source IDs are `g-helpful-content`, `g-ai-opt-guide`, `g-qrg-full`, and `sparktoro-zero-click-2026`.

## Accepted Inputs And Deliberate Exclusions

Accepted inputs are uploaded source documents, dated source URLs from [[Research Pack Index]], client-approved documents, and a query brief with the reader job. Excluded inputs are private credentials, uncaptured screenshots, unsourced snippets, and broad market claims that are not tied to a ledger ID. SparkToro material can explain search behavior context through [[AI Citation Mechanics]], but the brief must not reuse its panel statistic as a decorative fact.

## Required Sections Table

| Brief section | Mandatory fields | Validator | Acceptance condition | Handoff owner |
|---|---|---|---|---|
| Query frame | Reader question, locale, decision needed | Brief lead | One answerable research job | Content strategist |
| Source packet | Source ID, URL, date, document title | Researcher | Every factual claim points to a source | Researcher |
| Synthesis | Claim, confidence, limitation | Factchecker | Unsupported claims are removed or labeled | Editor |
| Citation handling | Inline source ID, canonical hub wikilink | Reviewer | Claims route to [[Research Pack Index]] or topic hub | Factchecker |
| Fallback path | Missing source, blocked answer, next source | Owner | Gaps are explicit, not guessed | Research lead |
| Publishing caveat | AI inclusion, traffic, ranking limits | Editor | No guaranteed citation or ranking language | Managing editor |

## Handoff Procedure With Block States

1. Start with source-bound questions and reject prompts that ask for unsupported general advice.
2. Compare the answer against the uploaded source packet and remove claims that do not trace back to a listed document.
3. Apply the claim-ledger verdict style: official guidance can be confirmed, while practitioner data remains reported context.
4. Hand the brief to [[FLOW Framework]] only after the blocker column is empty or explicitly accepted by the owner.
