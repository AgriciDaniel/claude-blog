<!-- (c) Daniel Agrici, FLOW (https://github.com/AgriciDaniel/flow), CC BY 4.0 -->
<!-- Synced from FLOW on 2026-04-27 -->
---
title: "Evidence-based quality follow-up prompt"
description: "Evidence-based quality follow-up for clarity, support, and reader value"
updated: 2026-07-23
tags:
  - prompts
  - optimize
---

# Evidence-Based Quality Follow-Up Prompt

## Use This When

Use this prompt after a quality review to separate observations, assumptions,
recommended actions, and claims that need verification. Do not infer human or
model authorship from prose patterns.

## AI Compatibility

Works with long-context reasoning models. For smaller models, provide narrower inputs and ask for one output section at a time.

## Inputs

- Blog, publication, product, or website name.
- Target article, hub page, query set, or campaign.
- Audience and geography where relevant.
- Existing evidence: analytics, search results, reader research, source notes, sales objections, or content inventory.
- Constraints, exclusions, and required sources.

## Prompt

```text
Act as a senior SEO strategist using the FLOW model.

Task: create an evidence-based Optimize-stage quality follow-up for:
[ARTICLE, HUB, OR SITE].

Use only the supplied inputs and clearly label any assumption. Do not invent statistics. Do not reuse private examples. Build the answer around:
1. Searcher or buyer intent.
2. Evidence available now.
3. Gaps that block trust, extraction, or conversion.
4. Recommended changes in priority order.
5. Measurement events and review cadence.
6. Claims that require source verification before publication.

Evaluate clarity, source fidelity, factual support, purpose fit, originality,
and reader usefulness. Do not classify authorship, produce an AI-origin
percentage, or recommend "humanization" tricks. Treat phrase preferences,
punctuation, sentence variation, and vocabulary diversity as optional editorial
style observations only.

Return a concise working document the team can execute.
```

## Output

- Executive summary.
- Priority table.
- Recommended copy, structure, or audit findings.
- Evidence needed.
- Measurement plan.
- Verification checklist.

## Example

Input: a blog post or hub page with weak proof, thin source support, and an unclear conversion path.

Expected output: a prioritized content brief, claims to verify, internal links to add, and the conversion event to measure.

## See Also

- [Prompt Library](../README.md)
- [FLOW Framework](../../flow-framework.md)
- [Bibliography](../../bibliography.md)

## Source Note

Adapted from the FLOW repository structure and rewritten for blog use with the repository evidence standard.
