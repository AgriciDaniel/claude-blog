---
type: spoke
title: "FLOW Read Only Boundary"
domain: "Blog Workflow"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [flow, active]
confidence: advisory
related:
  - "[[FLOW Framework]]"
  - "[[FLOW Approval Queue]]"
  - "[[FLOW Rollback Notes]]"
  - "[[Google Data Integrations]]"
  - "[[Blog Schema Stack]]"
---

# FLOW Read Only Boundary

## Read Only Boundary Purpose

FLOW Read Only Boundary defines what this brain may advise and what it must not mutate in V1. The vault can inspect source packets, drafts, reports, and exported metrics. It can recommend edits, confidence labels, rollbacks, and review windows. It must not change a CMS, Search Console, analytics account, ad platform, repository deployment, or publishing queue.

## External Systems Outside V1

External systems include WordPress, headless CMSs, GSC, GA4, crawlers that write settings, social schedulers, newsletter tools, and schema deployment paths. [[Google Data Integrations]] may describe how evidence should be read, but access and mutation decisions stay with a human operator. Google guidance on third-party SEO advice keeps recommendations from claiming tool certainty (source_id: `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice`). GSC, URL Inspection, and GA4 APIs are evidence sources, not permissions to mutate accounts (source_ids: `g-gsc-api`, `g-urlinspect`, `g-ga4-data`).

## Boundary Decision Table

| Situation | Allowed advisory action | Forbidden mutation | Source basis | Owner | Handoff |
|---|---|---|---|---|---|
| Draft needs a usefulness rewrite | Recommend rewrite scope and quality reason | Publish or overwrite the CMS page | Source packet plus owner approval | Editor | [[FLOW Rewrite Stage]] |
| AI visibility request asks for tool-driven certainty | Explain advisory limits | Create or upload site files | `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` | SEO lead | [[2026 Google Update Timeline]] |
| Report uses property Search metrics | Add scoped evidence caveat | Change forecasts or budgets automatically | `g-gsc-api`, `g-ga4-data` | Strategy owner | [[Google Data Integrations]] |
| Schema issue appears in draft | Recommend validation and visible-content check | Deploy structured data | `g-urlinspect` plus [[Blog Schema Stack]] | Technical owner | [[FLOW Approval Queue]] |
| Live content change is accepted | Record owner and rollback condition | Execute the change | Approval record | Human implementer | [[FLOW Rollback Notes]] |
| URL Inspection result is supplied | Interpret index state for that URL | Trigger indexing action in an account | `g-urlinspect` | Technical owner | [[Google API Evidence Matrix]] |
| Robots or noindex question appears | Explain crawl versus indexing effect | Edit robots.txt or page headers | `g-robots-intro`, `g-block-indexing` | Technical SEO | [[SEO Check Validation Checklist]] |
| GA4 engagement export is attached | Summarize scoped organic engagement | Change campaign budgets or audiences | `g-ga4-data` | Strategy owner | [[Full Site Blog Audit Report]] |

## Escalation And Approval Notes

Any action that touches live content or account configuration needs a human owner, a reversible change description, and an observation window. If the request asks the brain to make the change directly, the correct response is a recommendation packet, not execution.

## Evidence Use For Safe Advice

GSC and GA4 evidence can justify a recommendation only inside the exported scope the owner provided. URL Inspection evidence can support a validation note, not a deployment. The read-only boundary keeps recommendations useful while preserving auditability.

## Example: API Evidence Without Mutation

An operator uploads a redacted GSC export showing query, page, click, impression,
CTR, and position fields.

Allowed output: a scoped evidence note for decay triage under `g-gsc-api`.

Forbidden output: changing Search Console settings, submitting removals, or
claiming that the export proves an algorithmic cause.

If a canonical concern appears, the note sends a validation request to
[[Google API Evidence Matrix]] and an approval row to [[FLOW Approval Queue]].

## Boundary Breaches To Catch

- A report recommendation silently becomes a CMS instruction.
- A URL Inspection observation is treated as permission to deploy schema.
- A tool vendor claim is repeated as certainty despite official caution.
- A private export is copied into prose instead of summarized with scope.

## Consumed By Audit Evidence

[[Google API Evidence Matrix]] consumes the allowed evidence surfaces,
credential tier, forbidden mutation, source basis, and human owner.

[[Full Site Blog Audit Report]] consumes the boundary result as a disclosure
that separates advisory findings from implementation actions.

The expected deliverable output is a recommendation packet, never a live-system
change or account-side command.
