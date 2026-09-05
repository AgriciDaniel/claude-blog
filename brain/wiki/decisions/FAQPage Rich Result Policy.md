---
type: decision
title: "FAQPage Rich Result Policy"
domain: "Blog Structured Data"
status: active
created: 2026-07-08
updated: 2026-07-09
tags: [decisions, schema, active]
related:
  - "[[Structured Data Deprecation Register]]"
  - "[[Visible Q And A Without FAQ Rich Results]]"
  - "[[Claim To Source Mapping]]"
  - "[[Blog Schema Stack]]"
source_urls:
  - "https://developers.google.com/search/updates#deprecating-the-faq-rich-result-feature"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
---

# FAQPage Rich Result Policy

## FAQPage Rich Result Policy Rule Scope

This decision governs how the brain talks about FAQPage markup after Google removed FAQ rich-result visibility from Search. The current rule is: do not recommend FAQPage markup as a live Google rich-result tactic for blog posts. The rule is based on `g-faqpage-sd` and the confirmed claim `claim-faq-rich-results-retired` in the claim ledger.

Visible question-and-answer copy can remain useful when it answers reader objections, clarifies entities, or supports a page's content job. That is a content decision, not a rich-result promise. Any claim that FAQPage markup improves Google AI Overview, AI Mode, or machine-citation inclusion is rejected unless a future dated Google source says otherwise; the current claim-ledger verdict for that idea is CONTESTED.

### Allowed Actions And Disallowed Actions

- Allowed: keep visible Q and A sections when they improve the article for readers and match the page.
- Allowed: document historical FAQPage markup only as deprecated or retired Search behavior.
- Allowed: use [[Visible Q And A Without FAQ Rich Results]] for editorial Q and A guidance.
- Disallowed: present FAQPage markup as a current Google rich-result opportunity for blog posts.
- Disallowed: imply that FAQPage markup is a documented Google AI citation signal.
- Disallowed: add FAQPage JSON-LD when the visible page lacks matching Q and A content.

### Exceptions That Require Approval

- A regulated, contractual, or accessibility reason requires structured FAQ markup outside the Google rich-result goal.
- A client has existing FAQPage markup and needs a remove, keep, or no-op decision based on engineering cost and risk.
- Google publishes a new Search Central source that reinstates FAQ rich results or documents a replacement feature.

## FAQPage Rich Result Policy Rule Table

| Rule | Source basis | Applies to | Exception path | Approval owner |
|---|---|---|---|---|
| Do not sell FAQPage as a current Google rich-result tactic. | `g-faqpage-sd`, claim-ledger CONFIRMED | Blog schema audits, content briefs, delivery reports | Reopen only after a dated Google update reverses the retirement. | Schema steward |
| Check the Search Gallery before promising any rich-result eligibility. | `g-search-gallery` | New schema recommendations and schema cleanup plans | If a type is absent, classify it as unsupported for Google rich results. | Schema steward |
| Do not invent AI-citation value for FAQPage markup. | `g-ai-opt-guide`, claim-ledger CONTESTED for FAQPage AI citation | GEO notes, AI citation readiness reviews, schema output contracts | Escalate only with a Google source documenting the signal. | GEO owner |
| Keep markup tied to visible page content when any structured data is used. | `g-intro-sd` | JSON-LD specs and CMS handoffs | Block if the visible Q and A content is missing or mismatched. | Technical SEO |

## Rule Evidence Source Applies To And Enforcement

The policy is narrow by design. `g-faqpage-sd` supports the retirement rule; it does not say every visible FAQ section is bad content. `g-search-gallery` is the eligibility check for rich-result types. `g-ai-opt-guide` blocks the common overreach that a special schema file or FAQPage block is required for Google AI features. `g-intro-sd` keeps any remaining structured-data discussion anchored to visible, accurate page facts.

## FAQPage Rich Result Policy Review And Rollback

1. Before `/blog schema` or `/blog geo` uses FAQ language, check whether the recommendation promises rich-result display, reader help, or AI citation value.
2. If it promises rich-result display, reject the recommendation and cite `g-faqpage-sd`.
3. If it claims AI citation value, mark it CONTESTED and route the issue to [[AI Citation Mechanics]] and [[Claim To Source Mapping]].
4. If it is a reader-facing Q and A section with no rich-result promise, route the content decision to [[Visible Q And A Without FAQ Rich Results]].
5. Reopen this decision only when a dated Google Search Central source changes FAQ rich-result availability or publishes replacement guidance.

## Decision Record

| Field | Value |
|---|---|
| Owner | schema steward |
| Approval status | approved for advisory vault use |
| Risk level | high if violated |
| Current verdict | `claim-faq-rich-results-retired` is CONFIRMED; `claim-faqpage-ai-citation-unsupported` is CONTESTED. |
| Rollback note | Reopen if Google restores FAQ rich results or documents a replacement Search feature. |
| Affected workflows | [[Blog Schema Stack]], [[Structured Data Deprecation Register]], [[Visible Q And A Without FAQ Rich Results]], [[AI Citation Mechanics]] |
