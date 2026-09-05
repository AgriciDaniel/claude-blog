---
type: spoke
title: "AI Feature Preview Controls"
domain: "GEO and AEO"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [geo-aeo, ai-citation, evergreen]
---

# AI Feature Preview Controls

## AI Feature Preview Controls Citation Job

This note decides whether preview-control settings support or restrict a page's possible appearance in Google AI features. It is not a ranking lever note. The working unit is a page or section where `nosnippet`, `max-snippet`, paywall handling, or other preview constraints may reduce what Search can display or summarize.

Google's AI feature documentation and AI optimization guide are the controlling evidence for this review (`g-ai-features`, `g-ai-opt-guide`). Market studies from `sparktoro-zero-click-2026` and `seer-aio-impact-ctr-2026` explain why teams care about citations and click scarcity, but those studies do not justify loosening preview controls without a business decision. When available, Search Console generative AI reporting from `g-genai-reports` should be checked after any approved preview change.

### Passage, Entity, Or Surface This Note Owns

Own preview policy for the exact page under review. Do not use this note for copywriting changes, schema design, or broad AI Mode prioritization.

### No-Guarantee Boundary For AI Inclusion

Allowing snippets can preserve eligibility for display, but it does not create a promise of AI Overview, AI Mode, or organic feature inclusion.

## AI Feature Preview Controls Citation Table

| Control decision | Required input | Source IDs | Evidence state | Owner | Next action |
|---|---|---|---|---|---|
| Snippet restriction retained | Legal, licensing, or privacy reason for the restriction | `g-ai-features`, `g-ai-opt-guide` | CONFIRMED guidance, site-specific business call | Legal or content owner | Keep restriction and document citation tradeoff |
| Snippet restriction relaxed | Page section, affected template, approval note | `g-ai-features` | Official behavior context | SEO lead | Queue read-only recommendation for publisher approval |
| AIO performance checked | Query, URL, date range, citation state | `seer-aio-impact-ctr-2026`, `g-genai-reports` | Practitioner benchmark plus first-party report when present | Analyst | Compare before and after, then label result inconclusive if sample is thin |
| Market priority challenged | Search journey assumption and stakeholder request | `sparktoro-zero-click-2026` | AS-REPORTED market context | Strategist | Route the planning caveat to [[Dual Optimization]] |
| Max-snippet tightened | Exact character policy, affected template, business reason | `g-ai-features`, `g-ai-opt-guide` | Official preview-control context | Technical SEO | Record what Search may be allowed to display |
| Paywalled excerpt reviewed | Public teaser, subscription boundary, source license | `g-ai-features` | Search preview context plus business approval | Legal reviewer | Keep restricted copy separate from public summary |
| Google-Extended request separated | Robots rule proposal and intended crawler target | `g-common-crawlers`, `g-ai-opt-guide` | Official crawler and AI guidance context | Research owner | Do not call training opt-out a Search preview control |

## AI Feature Preview Controls Remediation Procedure

1. Record the exact directive or template rule that limits the preview.
2. Identify whether the restriction is required by policy, contract, privacy, or editorial preference.
3. State the surface affected: organic snippet, AI Overview, AI Mode, or all Google Search previews.
4. Add the source IDs above to the recommendation and mark the action as advisory.
5. Send any approved implementation to the publishing owner outside this V1 brain.

## Applied Preview Decision

A public product guide carries a sitewide `nosnippet` rule because one pricing page contains licensed partner copy. The reviewer separates the guide from the licensed template, because `g-ai-features` and `g-ai-opt-guide` support preview-control review at the Search display layer, not a blanket recommendation to expose every page.

The decision is to keep the restriction on the licensed pricing page and request approval to relax the guide template only if the page owner accepts the citation tradeoff. After publication, [[Citation Exposure Metrics]] checks available Search Console generative AI reporting with `g-genai-reports` and labels any thin sample as inconclusive.

The note rejects a second request to add `Google-Extended: disallow` as the fix. `g-common-crawlers` covers that crawler control, while `g-ai-opt-guide` keeps Google Search AI feature advice tied to normal Search foundations.

## Preview Control Failure Cases

- A legal restriction is relaxed at the template level and exposes partner text; `g-ai-features` cannot override that business risk.
- A `max-snippet:0` rule is treated as an AI-only setting, although `g-ai-features` frames previews across Search displays.
- A CMS plugin writes a hidden `nosnippet` directive after editorial approval, so the rendered HTML must be checked.
- A stakeholder treats Google-Extended as an AI Overview control, which `g-common-crawlers` and `g-ai-opt-guide` do not support.

## Register Wiring

[[GEO Citation Readiness Register]] consumes this note for preview-related rows. It needs the URL, rendered directive, template owner, approval state, source IDs, and rollback trigger.

The expected register output is a ready, blocked, or deferred preview-control status. If the change requires CMS work, the brain records the advisory recommendation and leaves implementation outside V1.

## Approval Record Detail

For a relaxed directive, attach the page pattern and the exact control reviewed under `g-ai-features`.

For a retained directive, name the business reason before citing AI feature tradeoffs from `g-ai-opt-guide`.

For mixed templates, record which URL class keeps the restriction and which class enters observation.

For post-change measurement, log whether `g-genai-reports` data is available before asking for trend language.

## AI Feature Preview Controls Handoff

If the issue is source wording, move it to [[Source Proximity Pattern]]. If the problem is an unclear answer passage, move it to [[Passage Citability Checklist]]. If stakeholders ask whether llms.txt can replace preview controls, use [[llms.txt Caveat Note]].
