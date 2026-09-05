---
type: spoke
title: "Evidence Block Requirements"
domain: "Blog Briefs"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [briefs-outlines, serp-briefs, active]
---

# Evidence Block Requirements

## Evidence Block Requirements Claim Gate

Evidence blocks decide what a draft may assert and what proof must sit beside the assertion. The unit is the claim, not the whole article. A claim can be accepted, caveated, narrowed, escalated, or removed. This note prevents the common failure where a brief has a source list but no mapping from source to claim.

Use `g-helpful-content` for people-first quality recommendations, `g-qrg-full` when a claim has trust or YMYL sensitivity, and `g-ai-opt-guide` for Google AI-feature constraints. Use `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` when a source or tool claim drifts toward a ranking, AEO, or GEO guarantee.

### Claim Classes Owned Here

This note owns source requirements for definitions, statistics, workflow recommendations, Google-policy statements, AI-feature statements, YMYL claims, and competitor observations that are about to become prose.

### Escalations Out Of This Note

Send legal, medical, financial, or reputation advice to a qualified reviewer. Send unresolved market forecasts to [[Google Data Integrations]] if first-party data exists. Send SERP-only observations to [[SERP Observation Ledger]] until a source supports the claim.

## Evidence Requirement Table

| Claim type | Minimum evidence | Required caveat | Owner | Verdict discipline | Draft action |
| --- | --- | --- | --- | --- | --- |
| Google Search or AI feature rule | Official Google source such as `g-ai-opt-guide` | State what the source does not promise | SEO lead | CONFIRMED only when the source directly says it | Allow with source ID |
| People-first quality recommendation | `g-helpful-content` plus topic expertise when needed | Do not imply E-E-A-T is a single direct ranking factor | editor | CONFIRMED for guidance, not for guaranteed outcome | Allow with scoped wording |
| Market behavior statistic | Primary study source from [[Brief Source Pack]] | Geography, sample, date, and "not property data" | analyst | AS-REPORTED | Allow as context |
| llms.txt Google tactic | `g-ai-opt-guide` | May be relevant outside Google, but not a Google visibility lever | source steward | CONFIRMED for Google Search stance | Remove unsupported tactic |
| Live SERP pattern | Dated observation plus corroborating source if it becomes a claim | A visible pattern is not a ranking factor | brief owner | SINGLE-SOURCE or lower until supported | Hold or rewrite |
| Third-party SEO tool assertion | `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` plus vendor method note | External tools do not access Google's internal ranking data | analyst | AS-REPORTED | Caveat or remove |
| QRG trust interpretation | `g-qrg-full` plus topic context | Rater guidance informs evaluation, not direct ranking mechanics | editor | CONFIRMED for guideline wording only | Allow with limited scope |
| First-party performance claim | `g-gsc-api` export or approved data note | API fields describe property data, not causal diagnosis | analyst | CONFIRMED for reported fields | Allow as measured context |
| Structured-data eligibility claim | `g-search-gallery` or feature-specific Search Central page | Eligibility is not guaranteed appearance | technical SEO | CONFIRMED for documented support | Allow with no promise |

## Approval And Caveat Procedure

1. Rewrite the claim in one plain sentence before choosing evidence.
2. Ask what the source proves and what it leaves unproven.
3. Assign CONFIRMED, AS-REPORTED, CONTESTED, SINGLE-SOURCE, or FOLKLORE from [[Claim To Source Mapping]] practice.
4. Add the caveat beside the claim in the brief, not in a hidden reviewer note.
5. Remove any claim that cannot be sourced or safely narrowed.

## Claim Verdict Example

Draft claim: "Adding llms.txt helps Google AI Mode cite our article." Verdict: remove for Google visibility because Google's own guidance says Search does not use llms.txt for Search, AI Overviews, or AI Mode visibility. Source ID: `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`.

Narrowed replacement: "Make the page crawlable, indexable, and useful, then keep answer passages source-adjacent and caveated." The first part uses official AI guidance; the passage-readiness part remains practitioner advice. Source IDs: `g-ai-opt-guide`, `ziptie-aio-source-selection`.

## Evidence Gate Failure Modes

- The source proves a related topic, not the sentence being drafted. Source ID: `g-helpful-content`.
- A competitor claim passes through because it appears in multiple SERPs. Source ID: `dfs-api`.
- A QRG concept is presented as a mechanical ranking input. Source ID: `g-qrg-full`.
- A structured-data row promises a rich result rather than eligibility. Source ID: `g-search-gallery`.

## Claim Block Wiring

[[Content Brief Output Contract]] consumes accepted and rejected claim blocks in the evidence-pack field. Inputs provided: claim sentence, source ID, verdict label, caveat, and draft action. Expected output: the brief contains only approved or explicitly caveated claims.

[[Blog Write Article Contract]] consumes the final claim map during drafting. Expected output: every current policy, statistic, or tool claim carries a nearby source ID or is removed before review.

## Sources

- `g-helpful-content`
- `g-qrg-full`
- `g-ai-opt-guide`
- `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` for tool-claim verdicts
- `g-gsc-api`
- `g-search-gallery`
- `dfs-api`
- `ziptie-aio-source-selection`
- `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` for llms.txt claim removal

## Handoff

Accepted blocks go to [[Brief To Draft Handoff]]. Rejected blocks return to [[Brief Source Pack]] for replacement sources or to [[Brief Risk Notes]] when the issue is approval risk rather than missing evidence.
