---
type: spoke
title: "Stale Claim Register"
domain: "Blog Rewriting"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [rewriting, freshness, content-decay, active]
---

# Stale Claim Register

## Register Record Scope

The stale claim register tracks claims that cannot safely remain in a rewritten article without refresh, removal, or a limitation. It is not a place to park every citation. It captures only claims with a real aging, confidence, or proof problem.

Use `g-helpful-content` for the reliability test, `g-gsc-api` when a claim affects a page with search exposure, `g-ranking-history` for dated Google update statements, and `g-canonical` when a claim depends on which URL owns the content. Apply the verdict discipline from `references/claim-ledger.md`: confirmed claims can be used directly, as-reported claims keep their scope, contested claims need caveats, and folklore should not drive a recommendation.

### Events Or Items This Register Captures

Capture dated statistics, Google update references, claims about a page's search behavior, unsupported best-practice statements, statements whose source no longer matches the wording, and claims that changed during a rewrite.

### Events Or Items Routed Elsewhere

Performance diagnosis belongs to [[Historical Performance Review]], source replacement steps belong to [[Source Refresh Workflow]], and canonical or redirect questions belong to [[Content Consolidation Rules]].

## Stale Claim Register Table

| Claim item | Source ID | Confidence | Owner | Status | Next review date | Rollback trigger |
|---|---|---|---|---|---|---|
| Helpfulness claim in rewrite rationale | `g-helpful-content` | High for guidance, advisory for page judgment | Editor | Review wording | 2026-08-01 | Claim implies a ranking guarantee |
| Page decline claim from Search Console | `g-gsc-api` | High for exported fields | Analyst | Needs dated export | 2026-08-01 | Export filter cannot be reproduced |
| Google update timing claim | `g-ranking-history` | High for official event dates | Monitoring owner | Keep with date | 2026-08-01 | Source history changes or event is removed |
| Duplicate URL ownership claim | `g-canonical` | High for canonical guidance, advisory for site case | SEO technical owner | Route to consolidation | 2026-08-01 | Better canonical owner is identified |
| Claim retained after rewrite | Source varies by claim | Match weakest source | Source steward | Keep, update, remove, or caveat | Set per source refresh due date | New source contradicts retained wording |
| FAQ rich-result availability claim | `g-faqpage-sd` | High for Google rich-result status | Schema reviewer | Remove or caveat | 2026-08-09 | Google Search gallery changes |
| llms.txt visibility claim | `g-ai-opt-guide` | High for Google AI guidance | GEO owner | Remove unsupported wording | 2026-08-09 | Google AI guidance changes |

## Review Loop

1. Add a row only when a claim can affect reader trust, action choice, or rollback.
2. Copy the exact claim sentence into the working ticket or source-refresh artifact.
3. Assign the verdict before drafting replacement language.
4. Close the row only after [[Rewrite QA Checklist]] confirms the source ID appears beside the updated claim.

## Register Entry Example

Draft claim: FAQPage markup will earn FAQ rich results.
`g-faqpage-sd` marks that wording stale for current Google Search use.
Verdict: confirmed source contradicts the draft claim.
Action: remove the promise and route visible Q and A elsewhere.
QA closes the row only when the edited sentence cites the replacement source.

## Claim Aging Traps

- A source can be current while the copied claim is outdated.
- A broad Google guide does not prove every operational sentence.
- Deleting a citation without deleting the claim leaves hidden risk.
- GSC evidence from `g-gsc-api` proves fields, not editorial meaning.

## Factcheck Register Wiring

[[Factcheck Claim Register]] consumes rows that affect deliverable claims.
Inputs provided: exact claim, source ID, verdict, owner, and review date.
It expects claim status: verified, stale, pending, blocked, or removed.
AI guidance rows use `g-ai-opt-guide`; rich-result rows use `g-faqpage-sd`.

## Register Source IDs

`g-helpful-content`; `g-gsc-api`; `g-ranking-history`; `g-canonical`; `g-faqpage-sd`; `g-ai-opt-guide`.

## Related

- [[Source Refresh Workflow]]
- [[Rewrite QA Checklist]]
- [[Historical Performance Review]]
- [[Content Consolidation Rules]]
- [[Research Pack Index]]
