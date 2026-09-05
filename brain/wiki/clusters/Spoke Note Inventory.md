---
type: spoke
title: "Spoke Note Inventory"
domain: "Blog Topic Architecture"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [clusters, semantic-clusters, active]
confidence: advisory
---

# Spoke Note Inventory

## Inventory Job

Use this note to list every support page attached to one cluster and mark each page as existing, missing, stale, duplicate, consolidated, or retired. The inventory is the source of truth before gap analysis, link mapping, or performance scoring begins.

### Required Fields

Each row needs page title, URL or note name, intended spoke job, canonical owner, source readiness, freshness state, internal link state, and next action. A page that lacks source-backed usefulness should not stay in the inventory just to increase coverage count. Source ID: `g-helpful-content`.

### Inventory Boundaries

Do not create AI-only spokes, llms.txt support pages, or thin pages for every query variant. The Google AI guidance and June 2026 clarification belong in [[2026 Google Update Timeline]] when a stakeholder asks for AI-file work. Source IDs: `g-ai-opt-guide`, `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`.

## Spoke Inventory Table

| Inventory state | Required inputs | Evidence state | Owner | Next action |
|---|---|---|---|---|
| Existing and healthy | Page title, role, sources, links | Useful content and current source IDs | Cluster editor | Keep and monitor |
| Existing but stale | Page role, expired source, affected claim | Needs source refresh before reuse | Source steward | Refresh or mark caveat |
| Existing but uncited | Page role and visible claims | Fails source-readiness until claim owners exist, `g-helpful-content` | Researcher | Add source IDs or remove unsupported claims |
| Missing but justified | Reader job, hub relationship, source availability | Advisory until evidence is attached | Content lead | Send to [[Cluster Gap Analysis]] |
| SERP-only candidate | Query pattern and competitor page | Weak until first-party, source, or reader evidence appears, `dfs-labs` | Strategist | Park as research-needed |
| Duplicate or overloaded | Two pages share task or owner | Needs query-page and canonical review | SEO lead | Send to [[Cannibalization Review]] |
| Wrong-locale spoke | Translated page with different local promise | Needs locale evidence and hreflang review, `g-localized` | Localization owner | Route to locale audit before cluster use |
| Retired or consolidated | Old URL, replacement owner, link route | Requires rollback and redirect discussion outside this note | Human owner | Update inventory after approval |

## Inventory Procedure

1. Start with the hub and list all pages currently linked from it.
2. Add known pages that rank or receive impressions for cluster queries.
3. Mark each page's reader job before assigning a status.
4. Attach source IDs and note whether GSC evidence exists. Source ID: `g-gsc-api`.
5. Route market visibility context to [[AI Citation Mechanics]] instead of using `sparktoro-zero-click-2026` as a page-level forecast.

## Inventory Example

A payroll cluster lists a hub, tax calendar spoke, software comparison, compliance glossary, and old announcement. Source ID: `g-helpful-content`.

The tax calendar is existing but stale because date-sensitive claims need current source verification. Source ID: `g-helpful-content`.

The software comparison remains healthy only if it keeps distinct buyer intent and current evidence. Source ID: `g-helpful-content`.

The compliance glossary is existing but uncited because definitions lack source IDs. Source ID: `g-qrg-full`.

The old announcement becomes retired or consolidated after a human owner confirms the replacement path. Source ID: `g-canonical`.

The inventory does not schedule a new "AI payroll visibility" spoke because official guidance does not require that page. Source ID: `g-ai-opt-guide`.

## Inventory Failure Cases

- Keeping a page only to raise spoke count turns the inventory into vanity coverage. Source ID: `g-helpful-content`.
- A source-ready article still fails inventory if it has no cluster role. Source ID: `g-helpful-content`.
- A consolidated URL can remain accidentally linked from sibling pages. Source ID: `g-canonical`.
- SERP-only candidates should not become briefs without local evidence or source support. Source ID: `dfs-labs`.
- Locale variants can look duplicate until language and regional intent are checked. Source ID: `g-localized`.

## Planning Feed

[[Semantic Cluster Execution Plan]] consumes the inventory statuses, page roles, evidence gaps, and owner flags. Source IDs: `g-helpful-content`, `g-gsc-api`.

[[Editorial Calendar Planning Matrix]] expects each inventory item to resolve into new, refresh, consolidate, or monitor. Source IDs: `g-ranking-history`, `g-helpful-content`.

## Handoff Rules

The inventory is not a content calendar. It feeds [[Intent Coverage Matrix]], [[Internal Link Matrix]], and [[Cluster Performance Score]] after duplicates, missing evidence, and stale sources are visible.
