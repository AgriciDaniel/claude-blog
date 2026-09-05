---
type: hub
title: "Google Data Integrations"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [data-integrations, gsc, ga4, active]
domain: "Blog Data"
confidence: verified
related:
  - "[[index|Index]]"
  - "[[hot|Hot]]"
  - "[[Dual Optimization]]"
  - "[[Freshness and Content Decay]]"
  - "[[AI Citation Mechanics]]"
  - "[[Semantic Topic Clusters]]"
  - "[[Blog Quality Score]]"
  - "[[Research Pack Index]]"
source_urls:
  - "https://developers.google.com/webmaster-tools/v1/searchanalytics/query"
  - "https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect"
  - "https://developers.google.com/speed/docs/insights/v5/get-started"
  - "https://developers.google.com/analytics/devguides/reporting/data/v1"
---

# Google Data Integrations

## Operating Scope For Read Only Integrations

Google Data Integrations is the hub for evidence imported from Google-owned data surfaces during blog planning and audit work. It covers Search Analytics metrics, URL Inspection evidence, PageSpeed or CrUX-style performance checks, and GA4 engagement reporting. The hub does not grant access, fetch live data, store credentials, or mutate any external system. Source IDs wired here are `g-gsc-api`, `g-urlinspect`, `g-psi`, and `g-ga4-data`.

## What This Hub Owns

This hub owns the interpretation boundary for property-level evidence. It tells reviewers when a metric can support a content decision, which sibling spoke owns the field-level procedure, and when missing evidence must be disclosed. It also keeps first-party property data separate from market research so [[Blog Quality Score]], [[Freshness and Content Decay]], and [[Semantic Topic Clusters]] do not overfit external averages.

## What The Hub Must Not Absorb

- Claim-ledger verdicts about broad AI or click behavior. Route those to [[AI Citation Mechanics]] or [[2026 Google Update Timeline]].
- Public structured data publishing rules. Route those to [[Blog Schema Stack]].
- CMS edits, Search Console setting changes, GA4 configuration changes, sitemap submission, or indexing requests.
- Credential storage, raw private exports, account screenshots, and local paths.

## Spoke Map And Deliverable Boundaries

| Spoke | Job | Deliverable boundary | Primary source IDs | Handoff |
|---|---|---|---|---|
| [[Credential Boundary Rules]] | Decide what evidence can enter the vault | Redaction rules and approval path | `g-gsc-api`, `g-urlinspect`, `g-psi`, `g-ga4-data` | Block unsafe imports |
| [[GSC Search Analytics Query Plan]] | Define safe Search Analytics pulls | Query table or trend packet | `g-gsc-api` | Brief, audit, freshness review |
| [[URL Inspection Evidence Plan]] | Separate index state from content quality | URL evidence packet | `g-urlinspect` | Technical SEO review |
| [[GA4 Blog Engagement Metrics]] | Interpret post-click behavior | Engagement section with caveats | `g-ga4-data` | Content review |
| [[Page URL Canonical Data Checks]] | Normalize page joins | Canonical mapping register | `g-urlinspect`, `g-gsc-api` | All metric joins |
| [[Data Confidence Labels]] | Assign evidence strength | Label per evidence packet | All listed IDs | Report caveats |
| [[Missing Data Disclosure]] | Write approved gap language | Missing-data note | All listed IDs | Client-facing report |
| [[Query Dimension Hygiene]] | Freeze filters and grouping rules | Reproducible query recipe | `g-gsc-api`, `g-genai-reports` | Cluster and decay analysis |
| [[Metric Export Schema]] | Shape sanitized packets | Internal evidence contract | `g-intro-sd`, `w3c-jsonld` | Reports and schema warnings |
| [[Read Only Data Access Pattern]] | Sequence owner handoffs | Approved access request packet | `g-gsc-api`, `g-urlinspect`, `g-psi`, `g-ga4-data` | Audit intake |

## Evidence And Refresh Rules

Use source-ledger dates, not memory. As of the 2026-07-09 ledger, Search Analytics was last updated 2026-05-20, URL Inspection 2024-07-23, PageSpeed Insights 2025-08-28, and GA4 Data API 2026-06-29. Refresh this hub when any source reaches its refresh due date, when Google changes API dimensions, or when a property export introduces a field not covered by [[Metric Export Schema]].

## Operating Loop

1. Identify the decision: planning, refresh, audit, canonical cleanup, or report caveat.
2. Route the evidence to the narrowest spoke before drafting recommendations.
3. Apply [[Credential Boundary Rules]] before any source data enters a note.
4. Label every evidence packet through [[Data Confidence Labels]].
5. State missing, stale, or sampled evidence through [[Missing Data Disclosure]].

## Hub Routing Scenario

A full-site audit asks for decay, engagement, and index evidence. The hub routes query movement to `g-gsc-api`, index state to `g-urlinspect`, page experience to `g-psi`, and post-click behavior to `g-ga4-data` before the report combines recommendations.

[[Google API Evidence Matrix]] consumes that routing. This hub provides surface name, allowed evidence type, blocked access path, source ID, and sibling spoke; the matrix expects one row per evidence surface, not a blended metric.

## Source IDs

- `g-gsc-api`, `g-urlinspect`, `g-psi`, `g-ga4-data`

## Related Themes

- [[Dual Optimization]]
- [[Freshness and Content Decay]]
- [[AI Citation Mechanics]]
- [[Semantic Topic Clusters]]
- [[Blog Quality Score]]
- [[Research Pack Index]]
