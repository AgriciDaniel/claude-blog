---
type: spoke
title: "Brief Risk Notes"
domain: "Blog Briefs"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [briefs-outlines, serp-briefs, active]
---

# Brief Risk Notes

## Brief Risk Notes Planning Job

This note owns the risk register that travels with a SERP-informed brief. It is not the place to fix the outline or rewrite the article. Its job is to make uncertainty visible before drafting starts, especially when the brief touches YMYL-adjacent advice, stale statistics, non-Google AI tactics, or market data that could be mistaken for property performance.

Risk notes should point reviewers to the canonical hub rather than restating broad evidence. Use [[AI Citation Mechanics]] for Google AI feature constraints, [[Dual Optimization]] for zero-click and click-planning context, and [[2026 Google Update Timeline]] when the concern is tied to a dated Google Search change. Cite `sparktoro-zero-click-2026` only as market context, and use `g-qrg-full` when the brief enters trust or YMYL sensitivity.

### Risk Register Boundary

Record only risks that can change the brief, block drafting, or force a named caveat. Minor wording preferences belong in [[Brief To Draft Handoff]], and missing sources belong in [[Brief Source Pack]] unless the absence creates approval risk.

### Approval Triggers

Require owner review when a claim depends on practitioner data, when a recommendation implies Google AI feature eligibility, or when the source is older than its refresh cadence. `g-spam-policies` covers scaled-content and abuse risk, while `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` blocks unsupported AI-file requirements for Google Search.

## Reader Intent Signals And Exposure Caveats

Risk scoring starts with the reader decision the brief will influence. A high-volume query is not enough. The reviewer should know whether the reader is choosing a tool, handling a compliance concern, comparing options, or solving a time-sensitive problem. If the likely search journey may end without a site visit, the brief still needs a useful answer path and a measurement caveat tied to [[Dual Optimization]].

## Brief Risk Notes Planning Table

| Risk field | Owner | Source requirement | Acceptance check | Draft handoff state |
| --- | --- | --- | --- | --- |
| YMYL or reputation sensitivity | editor | `g-qrg-full` plus an expert or policy source for the topic | Risk note names who must approve the claim before drafting | Blocked until owner signs off |
| AI feature tactic | SEO lead | `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` when the tactic mentions special files | No claim says a file, schema, or formatting trick guarantees AI visibility | Ready with caveat |
| Market behavior statistic | analyst | `sparktoro-zero-click-2026` with method limits | The note says market panel, geography, and that first-party data wins | Advisory only |
| Outdated Search guidance | source steward | `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` or newer ledger entry | Refresh due date is named and routed to [[Research Pack Index]] | Monitor |
| Unapproved factual claim | brief owner | Source ID from [[Brief Source Pack]] | Claim has a verdict label from the claim-ledger discipline | Revise before draft |
| Third-party tool guarantee | analyst | `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` | Tool output is framed as external estimate, not Google's internal data | Caveat before approval |
| Host-authority content tactic | editor | `g-site-rep-abuse` and `g-spam-policies` | Brief avoids outsourced content framed around borrowed authority | Blocked until strategy changes |
| Scaled update request | brief owner | `g-spam-policies` | Bulk page generation has named user value and review owner | Escalate if value is thin |

## Brief Risk Notes Acceptance Procedure

1. Name the exact brief, page, cluster, or outline section affected by the risk.
2. Classify the risk as blocker, caveat, monitor, or no action.
3. Attach at least one source ID and state whether the evidence is official, primary, or practitioner.
4. Decide who can approve the risk and what wording the drafter must preserve.
5. Send unresolved source gaps to [[Brief Source Pack]] and unresolved structure gaps to [[Outline QA Checklist]].

## Risk Call In Practice

Scenario: a brief for "AI search optimization checklist" asks the writer to add an llms.txt requirement and forecast traffic from market behavior. The llms.txt claim becomes a blocker because Google says that file is not used for Search, AI Overviews, or AI Mode visibility; the market data stays advisory only. Source IDs: `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`, `sparktoro-zero-click-2026`.

After review, the risk note preserves this instruction: "Cover crawlable helpful content, snippet controls, and source clarity, but do not describe llms.txt as a Google visibility lever." The brief may mention low-click planning as market context, then sends property-specific projections to first-party data review. Source IDs: `g-ai-opt-guide`, `g-gsc-api`.

## Topic-Specific Breakpoints

- A practitioner chart becomes a property forecast without GSC support. Source ID: `g-gsc-api`.
- A YMYL-adjacent angle moves forward without an approval owner. Source ID: `g-qrg-full`.
- A tool score is treated as Google's ranking data. Source ID: `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice`.
- A site-reputation tactic is softened into "partner content" wording. Source ID: `g-site-rep-abuse`.

## Risk Packet Wiring

[[Content Brief Output Contract]] consumes this note as the draft-risk section. Inputs provided: risk class, source ID, owner, caveat text, and handoff state. Expected output: the brief either blocks drafting, carries the caveat, or names who accepted the remaining risk.

[[Blog Write Article Contract]] receives only resolved or explicitly carried risks through [[Brief To Draft Handoff]]. Expected output: no draft section removes caveat wording unless the owner changes the risk state.

## Sources

- `g-qrg-full`
- `g-spam-policies`
- `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` for unsupported file requirements
- `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` for tool-guarantee risk
- `g-site-rep-abuse`
- `g-ai-opt-guide`
- `g-gsc-api`
- `sparktoro-zero-click-2026`

## Related Routes

[[SERP-Informed Briefs and Outlines]] owns the parent workflow. [[Evidence Block Requirements]] decides source strength for individual claims. [[SERP Observation Ledger]] holds dated SERP observations without turning them into ranking facts.
