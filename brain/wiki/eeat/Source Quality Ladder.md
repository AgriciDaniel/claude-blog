---
type: spoke
title: "Source Quality Ladder"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [eeat, evergreen]
domain: "Blog Trust"
confidence: verified
related:
  - "[[E-E-A-T for Blog Content]]"
  - "[[Research Pack Index]]"
  - "[[Reputation Research Workflow]]"
  - "[[AI Citation Mechanics]]"
  - "[[Google Algorithm Update Ledger]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
  - "https://developers.google.com/search/docs/essentials/spam-policies"
  - "https://www.nngroup.com/articles/ten-usability-heuristics/"
---
# Source Quality Ladder

## Source Quality Ladder Evidence Job

This note decides whether a source is strong enough for the claim it supports. It is not a generic citation list. The ladder ranks evidence by proximity to the claim, date, publisher authority, methodology visibility, and limitation handling. For blog-trust work, `g-helpful-content` and `g-qrg-full` are the main quality-policy anchors, `g-spam-policies` is the abuse boundary, and `nng-editorial-heuristics` is the review-usability support source.

### Source Types This Note Owns

The ladder owns official guidance, primary documents, first-party data, independent expert material, vendor or practitioner studies, and internal operating notes. It also says when a claim needs two sources or should be removed.

### Claims This Ladder Must Not Validate Alone

Do not use this note alone to validate traffic forecasts, AI citation probabilities, algorithm impact, or rich-result eligibility. Those claims need their canonical hubs, especially [[AI Citation Mechanics]], [[Google Algorithm Update Ledger]], and [[Blog Schema Stack]].

## Source Quality Ladder Source Table

| Source id | URL | Date basis | Claim coverage | Limitation | Refresh cadence |
|---|---|---|---|---|---|
| g-helpful-content | https://developers.google.com/search/docs/fundamentals/creating-helpful-content | Last updated 2025-12-10, retrieved 2026-07-09 | People-first self-assessment and E-E-A-T framing | Not a page-specific ranking diagnosis | Monthly or on Search Central change |
| g-qrg-full | https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf | Published 2025-09-11, retrieved 2026-07-08 | Quality-rater framework for trust, purpose, and YMYL review | Rater guidelines are not the ranking algorithm | On QRG revision or before release |
| g-spam-policies | https://developers.google.com/search/docs/essentials/spam-policies | Updated 2026-05-15, retrieved 2026-07-06 | Scaled content, deceptive practices, and spam boundaries | Does not prove a specific site was penalized | Monthly or on policy update |
| nng-editorial-heuristics | https://www.nngroup.com/articles/ten-usability-heuristics/ | Last updated 2020, retrieved 2026-07-06 | Editorial ergonomics for visible status and error prevention | UX heuristic source, not Google policy | Quarterly unless local workflow changes |
| g-gsc-api | https://developers.google.com/webmaster-tools/v1/searchanalytics/query | Updated 2026-05-20, retrieved 2026-07-06 | First-party query clicks, impressions, CTR, and position | Requires property access and cannot explain cause alone | Per reporting window |
| g-ranking-history | https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history | Verified 2026-06-24, retrieved 2026-07-06 | Confirmed Google ranking-update timing | Does not diagnose a site's loss | On status-dashboard change |
| seer-aio-impact-ctr-2026 | https://www.seerinteractive.com/insights/aio-impact-on-google-ctr-2026-update | Published 2026-04-24, retrieved 2026-07-06 | Practitioner AI Overview CTR context | Not causal proof for a client page | Before AI visibility claims |
| sparktoro-zero-click-2026 | https://sparktoro.com/blog/in-2026-less-than-one-third-of-google-searches-still-send-a-click/ | Published 2026-06-08, retrieved 2026-07-06 | Market-level zero-click context | Not property-specific traffic evidence | Before strategy reports |

## Source ID, URL, Date, Claim Coverage, And Limitation Rules

Every source row used in a note should answer five questions: what claim it supports, how fresh it is, what it cannot prove, who owns refresh, and which canonical hub should handle disputes. A source with a strong publisher can still be weak if it is stale or aimed at a different claim.

## Source Quality Ladder Refresh Procedure

1. Start with official or primary sources for policy, eligibility, and high-stakes claims.
2. Add practitioner or vendor studies only when the claim is explicitly about observed market behavior.
3. Record the weakest source that matters to the recommendation.
4. If a source does not cover the claim, replace the claim or send the gap to [[Research Pack Index]].
5. Refresh source dates before relying on this ladder in a release-facing report.

## Source Triage Example

A draft says AI Overviews reduced "our" clicks and that a May 2026 core update caused the decline. The ladder splits the claim into two pieces. Market AI-search context can cite practitioner studies only as reported context and should link to [[AI Citation Mechanics]] rather than repeat the statistic here (source_ids: seer-aio-impact-ctr-2026, sparktoro-zero-click-2026). Property impact needs GSC export and cannot be assigned to a confirmed update without page-level evidence plus official timing context (source_ids: g-gsc-api, g-ranking-history).

## Ladder-Specific Failure Modes

- An official URL is cited for a claim it does not make; source strength drops to mismatch until the wording changes (source_id: g-helpful-content).
- A practitioner benchmark is used as a forecast for one client page; classify it as context, not proof (source_ids: seer-aio-impact-ctr-2026, sparktoro-zero-click-2026).
- A source ID appears in the approved pack but not near the claim it supports; the factcheck row remains incomplete (source_id: nng-editorial-heuristics).
- A policy source has a newer ledger date than the draft's citation note; refresh before release-facing advice (source_id: g-helpful-content).
- A ranking-history citation gives timing only; it cannot supply remediation advice by itself (source_id: g-ranking-history).

## Claim Register Feed

[[Factcheck Claim Register]] consumes the ladder after claim wording is stable. Inputs are claim text, chosen source ID, evidence tier, date basis, limitation, confidence, and refresh trigger. The register expects a verdict label, owner, next review date, and rollback trigger for every claim that survives this ladder.
