---
type: policy
title: "Answer Engine Citability Policy"
status: active
created: 2026-08-25
updated: 2026-08-25
tags: [meta, geo, policy]
domain: "Blog Content Brain"
confidence: verified
related:
  - "[[AI Citation Mechanics]]"
  - "[[AI Overview Citation Review]]"
  - "[[AI Mode Citation Review]]"
  - "[[Entity Clarity For AI Answers]]"
  - "[[Citation Ready Paragraphs]]"
  - "[[Search Visibility Versus Citation Exposure]]"
  - "[[Provenance Trace Policy]]"
  - "[[Uncertainty Eval Policy]]"
source_urls:
  - "https://developers.google.com/search/docs/appearance/ai-features"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
---

# Answer Engine Citability Policy

## Purpose

Citability work should make a page easier to understand, verify, and quote without inventing a separate ranking system or promising inclusion in an AI response.

## Operating contract

Recommendations must remain consistent with visible content, standard Search accessibility, and current official guidance. Each AI-facing recommendation needs a source boundary and confidence tag. The Brain never claims that formatting, schema, llms.txt, or a crawler visit guarantees citation.

## Allowed recommendations

| Practice | Reader value | Evidence boundary |
|---|---|---|
| Direct answer under a descriptive heading | Reduces search cost | Writing recommendation |
| Explicit entity names | Prevents ambiguous references | Semantic clarity |
| Nearby source attribution | Makes facts verifiable | Provenance |
| Visible dates and authorship | Clarifies responsibility | Trust presentation |
| Tables for true comparisons | Makes relations inspectable | Editorial structure |
| Stable canonical URLs | Supports consistent discovery | Standard Search |
| Deliberate preview controls | Expresses publisher preference | Google documentation |
| Accessible HTML text | Preserves crawl and reader access | Technical baseline |

## Disallowed claims

- A page is guaranteed to appear in AI Overviews or AI Mode.
- An llms.txt file improves Google visibility.
- Unsupported schema creates an AI citation feature.
- Repeating a phrase trains an answer engine to cite the page.
- A visibility vendor measures causal influence.
- Organic rank is equivalent to AI citation.
- A crawler request proves ingestion or use.
- Citation formatting overrides poor or unsupported content.

## Review sequence

1. Confirm the reader question and page purpose.
2. Identify the claim that needs citation.
3. Pair the claim with a public source.
4. Rewrite the passage so it stands alone without losing caveats.
5. Keep entity, date, number, and scope explicit.
6. Check that links do not separate evidence from the claim.
7. Validate crawlability and preview controls.
8. Apply an evidence-appropriate confidence tag.
9. Review AI Overview and AI Mode separately.
10. State that selection remains outside publisher control.

## Measurement language

Use observed, reported, or measured with a defined method. Do not use optimized, influenced, or caused unless the evidence supports that relationship. [[AI Citation Attribution Question]] remains open for observations that cannot be classified.

## Relationship to SEO

Google’s current guidance frames AI feature optimization on the same foundation as Search. Citability review adds passage clarity and evidence proximity, but it does not replace people-first usefulness, technical eligibility, or editorial accountability.

## Gate

A passage passes when its answer is useful without the citation objective, the source proves the claim, the caveat remains visible, and no guarantee language survives.
## Citability evidence packet

A review packet keeps the visible passage, entity, claim, source, date, preview
control, observation method, and non-claim together.

| Packet element | Rejection condition |
|---|---|
| Passage | Cannot stand alone |
| Entity | Ambiguous referent |
| Claim | Broader than source |
| Citation | Detached from claim |
| Date | Missing for volatile fact |
| Observation | Surface or method unclear |

Reject the packet when its usefulness depends on guessing hidden context or when
removing the AI objective makes the passage worse for the reader.
