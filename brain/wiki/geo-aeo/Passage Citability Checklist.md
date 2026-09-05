---
type: spoke
title: "Passage Citability Checklist"
domain: "GEO and AEO"
status: evergreen
created: 2026-07-06
updated: 2026-07-10
tags: [geo-aeo, ai-citation, evergreen]
---

# Passage Citability Checklist

## Passage Citability Checklist Review Scope

This checklist is the pre-flight gate for a single passage before it enters an AI Overview, AI Mode, or assistant-answer review. It checks whether the passage is useful to a reader, clear outside its surrounding article, and tied to source evidence. Google sources `g-ai-opt-guide` and `g-ai-features` support the general AI feature and content-foundation posture. `ziptie-aio-source-selection` is advisory passage-craft evidence, while `sparktoro-zero-click-2026` and `seer-aio-impact-ctr-2026` provide market context that must not be turned into a claim of citation or click lift.

### Checks Unique To This Gate

The gate focuses on answer structure, entity naming, nearby evidence, scope limits, and whether a reader would still understand the claim if the passage appeared outside the article.

### Inputs Required Before Review

Bring the passage text, page URL, target query, source IDs for claims, date-sensitive numbers, and any preview-control constraints.

## Passage Citability Checklist Pass Fail Table

| Check | Pass state | Source evidence | Severity | Fix owner | Status |
|---|---|---|---|---|---|
| Answer sentence | The first sentence directly answers the reader job | `ziptie-aio-source-selection` | blocker | Editor | pass, fix, or defer |
| Entity clarity | The target entity is named inside the passage | `g-ai-opt-guide`, `g-ai-features` | blocker | GEO reviewer | pass, fix, or defer |
| Source proximity | The supporting source sits next to the claim | `ziptie-aio-source-selection`, article source IDs | high | Researcher | pass, fix, or defer |
| Market caveat | Broad click behavior is clearly labeled as market context | `sparktoro-zero-click-2026` | medium | Strategist | pass, fix, or defer |
| Measurement path | A later citation check has a metric or explicit missing-data note | `g-genai-reports` | medium | Analyst | pass, fix, or defer |
| Freshness context | Time-sensitive advice includes source date or review date | `g-ai-features`, `g-genai-reports` | high | Analyst | pass, fix, or defer |
| Preview eligibility | Passage is not blocked by snippet policy | `g-ai-opt-guide`, `g-ai-features` | blocker | Technical SEO | pass, fix, or defer |
| Reader value | Passage answers a real task before extraction polish | `g-helpful-content`, `g-ai-opt-guide` | blocker | Editor | pass, fix, or defer |

## Passage Citability Checklist Procedure

1. Read only the candidate passage and mark any missing entity, date, source, or limitation.
2. Compare each claim with its source ID and remove unsupported generalizations.
3. Decide whether the passage is ready for surface-specific review or needs a rewrite.
4. Send failed answer structure to [[Answer Block Extraction Test]] and failed source placement to [[Source Proximity Pattern]].

## Applied Passage Check

A draft section says, "AI Overviews reduce clicks, so every SaaS guide needs a citation-ready paragraph." The checklist fails the market caveat row because `seer-aio-impact-ctr-2026` and `sparktoro-zero-click-2026` do not support a universal page-level prescription.

The revision says, "For this SaaS guide, the next review checks whether the answer paragraph names the product, keeps the source beside the claim, and remains crawlable for Google Search features." That version fits `g-ai-features`, `g-ai-opt-guide`, and the advisory passage pattern from `ziptie-aio-source-selection`.

If the page uses `nosnippet`, the passage cannot pass until [[AI Feature Preview Controls]] resolves the preview row. If Search Console reporting is absent, the measurement row records missing data through `g-genai-reports` rather than a substitute benchmark.

## Checklist Failure Cases

- A passage is concise but omits the entity, so extraction loses the subject.
- A chart contains the source, but the surrounding paragraph makes the claim without visible attribution.
- FAQ-style phrasing is mistaken for current rich-result strategy, which belongs in [[2026 Google Update Timeline]] and schema notes.
- A translated passage drops date and geography from a market claim, weakening the `sparktoro-zero-click-2026` caveat.

## Write Contract Wiring

[[Blog Write Article Contract]] consumes this checklist for the draft's AI citation passage row. It needs the candidate text, target query, source IDs, preview-control status, and pass/fix/defer verdict.

The article contract expects a concrete editing instruction: rewrite the first sentence, name the entity, move the source, add caveat language, or block the passage until evidence exists.

## Passage Verdict Detail

Use "pass" only when `g-helpful-content` reader value and source proximity both hold.

Use "fix" when `ziptie-aio-source-selection` supports a craft improvement without changing the claim.

Use "defer" when `g-genai-reports` data is needed before exposure language.

Use "blocked" when preview controls or source IDs make the passage unsuitable for review.

## Passage Citability Checklist Handoff Rules

A passage passes this checklist only when it is accurate, self-contained, source-adjacent, and clear to a human reader. Passing the checklist means "ready to review", not "likely to be cited".
