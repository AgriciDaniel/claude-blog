---
type: spoke
title: "Claim Verification Evidence Guide"
domain: "Source Evidence"
status: active
created: 2026-07-08
updated: 2026-07-09
tags: [sources, evidence, verification, active]
confidence: advisory
related:
  - "[[Research Pack Index]]"
  - "[[Claim To Source Mapping]]"
  - "[[Source Confidence Labels]]"
  - "[[Evidence Gap Register]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history"
---

# Claim Verification Flow

## Verification Job

This note is the operating sequence for checking a claim before it enters [[Claim To Source Mapping]]. It exists because source URLs, source IDs, and verdict labels solve different problems. A claim is verified only after the sentence, source coverage, date, and limitation agree.

Use this flow for current SEO, schema, AI Search, and monitoring claims. It is especially useful when a draft combines official Google guidance with an interpretation, because the interpretation may need a weaker label than the source itself.

## Intake Boundary

Bring one claim at a time. Do not submit a paragraph, a bundle of bullets, or a vague recommendation. The claim should be a sentence that could appear in a brief, audit, scorecard, or release note.

## Claim Triage Procedure

1. Copy the exact claim into a review scratchpad.
2. Underline the platform, surface, date, audience, and promised outcome.
3. Pick the first source family: content, AI Search, schema, or ranking history.
4. Open the source ID row in `references/source-ledger.json` and compare `supports_claims` with the draft.
5. Assign a draft label through [[Source Confidence Labels]].
6. If the source is too broad, narrow the claim or create a row in [[Evidence Gap Register]].
7. Only after the limitation is clear, move the claim to [[Claim To Source Mapping]].

## Claim Verification Evidence Decision Table

| Claim class | First source ID | What the source can confirm | Required limitation | Output destination |
|---|---|---|---|---|
| People-first content quality | `g-helpful-content` | Google guidance for helpful, reliable content review. | No rankings, traffic, or score guarantees. | [[Claim To Source Mapping]] |
| Google AI Search optimization | `g-ai-opt-guide` | Google Search AI guidance and absence of special AI-only requirements. | Google Search only, not all assistants. | [[AI Citation Mechanics]] then [[Claim To Source Mapping]] |
| Supported rich result | `g-search-gallery` | Whether Google lists the rich-result type. | Feature support is not eligibility or display guarantee. | [[Blog Schema Stack]] |
| Confirmed update history | `g-ranking-history` | Official ranking-update names and rollout state. | Does not prove local site impact. | [[Google Algorithm Update Ledger]] |
| FAQ rich-result retirement | `g-faqpage-sd` | Google Search FAQ rich-result retirement state. | Reader-useful Q and A is a separate content choice. | [[Schema Generation Output Contract]] |
| Google llms.txt claim | `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` | Google Search does not use llms.txt visibility controls. | Non-Google crawlers are outside that evidence. | [[GEO Citation Readiness Register]] |

## Verdict Terms From Claim Ledger

Use `CONFIRMED` only when the exact claim is directly supported. Use `AS-REPORTED` for a dated study claim. Use `SINGLE-SOURCE` when corroboration is absent. Use `CONTESTED` when methods or sources conflict. Use `FOLKLORE` when a common tactic lacks source support.

## Escalation And Closeout

The flow closes when the claim has a source ID, URL, date, limitation, confidence label, and owner. If any of those fields are missing, the claim should remain out of release-facing notes and appear in [[Evidence Gap Register]] instead.

## Verification Walkthrough For llms.txt

Draft claim: "Publish llms.txt so Google AI Mode cites us."
The platform and promised outcome make the sentence too broad.
Use `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`.
The safe claim says Google Search does not use that file.
Failure cases include bundled claims and assistant-wide wording.
Another failure is accepting a source ID without reading `supports_claims`.
[[Factcheck Claim Register]] receives the narrowed claim row.
Inputs provided: claim text, label, source ID, and unresolved platform gaps.
Expected output: accepted register item or evidence-gap escalation.

## Related

- [[Research Pack Index]]
- [[Claim To Source Mapping]]
- [[Source Confidence Labels]]
- [[Evidence Gap Register]]
