---
type: spoke
title: "Answer Block Extraction Test"
domain: "GEO and AEO"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [geo-aeo, ai-citation, evergreen]
---

# Answer Block Extraction Test

## Answer Block Extraction Test Purpose

This note tests whether one passage can stand on its own when copied out of the page. It is a practical editorial gate for direct-answer sections used in GEO and AEO work. The test is not a shortcut around helpful content, nor does it override Google's statement that normal SEO foundations still apply to AI features (`g-ai-opt-guide`, `g-ai-features`).

Use the market studies only to explain why extractable answers matter. `sparktoro-zero-click-2026` provides AS-REPORTED click-scarcity context owned by [[Dual Optimization]], while `seer-aio-impact-ctr-2026` should be treated as a non-causal AIO citation benchmark. `ziptie-aio-source-selection` is practitioner guidance for passage construction, so mark it advisory in any deliverable.

### Passage Unit Under Test

The unit is one heading plus the answer paragraph, supporting sentence, source reference, and internal link that immediately follows. Do not score an entire article as extractable if the target answer block fails.

### Non-Extractable Cases

Fail passages that need previous paragraphs to identify the entity, hide the date elsewhere, bury the source at the bottom, or make a claim broader than the cited evidence.

## Answer Block Extraction Test Table

| Test item | Pass condition | Source IDs | Evidence state | Owner | Fix when failed |
|---|---|---|---|---|---|
| Direct answer | First sentence answers the reader task without vague pronouns | `ziptie-aio-source-selection` | Practitioner heuristic | Editor | Rewrite the opening sentence |
| Entity name | Brand, product, person, or concept is named inside the block | `g-ai-opt-guide`, `g-ai-features` | Official guidance supports clear content foundations | GEO reviewer | Add explicit noun phrase |
| Claim boundary | Date, geography, sample, or limitation appears near the claim | `sparktoro-zero-click-2026`, `seer-aio-impact-ctr-2026` | AS-REPORTED market context | Analyst | Add caveat or remove claim |
| Source proximity | Source ID or source link sits next to the claim it supports | `ziptie-aio-source-selection` | Advisory extraction pattern | Researcher | Move source reference into the block |
| Freshness marker | Time-sensitive claim names the source date or review date | `g-ai-features`, `g-genai-reports` | Official context and reporting source when present | Analyst | Add date context or block the claim |
| Reader usefulness | Extracted block still answers a human task, not only a bot prompt | `g-helpful-content`, `g-ai-opt-guide` | Official people-first and AI guidance | Editor | Rewrite for reader value first |
| Internal support | Nearby internal link explains the next decision without replacing proof | `ziptie-aio-source-selection` | Advisory passage pattern | Content lead | Add relevant link or remove filler link |

## Answer Block Extraction Procedure

1. Copy the target answer block into a scratch note without the rest of the article.
2. Highlight every noun, date, number, and claim that depends on hidden context.
3. Add the nearest source ID beside each claim and downgrade unsupported wording.
4. Reinsert the block only after it reads accurately outside the page.

## Short Before And After

Before: "AI search is changing clicks, so brands should optimize every post for citations." The claim is too broad because `sparktoro-zero-click-2026` and `seer-aio-impact-ctr-2026` are market context sources, not property-specific guarantees.

After: "For Google AI features, keep the answer passage crawlable, source-adjacent, and useful to readers before reviewing citation exposure." That wording stays inside `g-ai-features`, `g-ai-opt-guide`, and `g-helpful-content`.

The after block names the surface, states the action, and avoids a traffic promise. It can move to [[Passage Citability Checklist]] for pass/fail review, while any metric claim waits for [[Citation Exposure Metrics]] and `g-genai-reports`.

## Extraction Test Pitfalls

- The answer depends on the H1 for the entity name, so a copied block loses its subject.
- A table carries the evidence, but the extracted paragraph omits the table source.
- A market statistic is summarized without date or method, weakening the claim boundary from `sparktoro-zero-click-2026`.
- A block sounds citation-friendly but no longer helps the reader, which conflicts with `g-helpful-content`.

## Article Contract Wiring

[[Blog Write Article Contract]] consumes this test for the "AI citation passage" acceptance row. It needs the candidate block, target query, source IDs, entity name, and pass/fail notes.

The expected output is a reviewer instruction for the draft package: keep the block, rewrite the opening sentence, add source context, or remove the unsupported claim.

## Extraction Score Notes

Mark "pass" only when the block still helps a reader under `g-helpful-content`.

Mark "revise" when the block needs `ziptie-aio-source-selection` style self-containment but the claim is otherwise supported.

Mark "blocked" when the source ID cannot support the claim boundary.

Mark "measure later" when `g-genai-reports` evidence is needed before any exposure language.

## Answer Block Extraction Handoff

If the block fails because the entity is ambiguous, use [[Entity Clarity For AI Answers]]. If the source is present but too far away, use [[Source Proximity Pattern]]. If the issue is observed AIO behavior, continue with [[AI Overview Citation Review]].
