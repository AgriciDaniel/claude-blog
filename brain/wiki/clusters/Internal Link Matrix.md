---
type: spoke
title: "Internal Link Matrix"
domain: "Blog Topic Architecture"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [clusters, semantic-clusters, active]
confidence: advisory
---

# Internal Link Matrix

## Link Assignment Job

This note assigns intentional links among the hub, spokes, and sibling pages in a cluster. The output is an internal link matrix with anchor purpose, destination, evidence, owner, and review date.

### Link Types This Matrix Owns

The matrix owns hub-to-spoke navigation links, spoke-to-hub return links, sibling links for adjacent tasks, and corrective links when canonical ownership is unclear. It does not implement redirects or rel canonical tags, though those signals may be part of a separate technical review. Source ID: `g-canonical`.

### Bad Link Patterns

Avoid repeating the same keyword anchor across every spoke, linking to thin pages, or using market visibility pressure as a reason to add irrelevant links. Helpful content still decides whether a link helps the reader move to the next useful page. Source ID: `g-helpful-content`.

## Link Matrix Table

| Link role | From page | To page | Anchor rule | Evidence | Source IDs |
|---|---|---|---|---|---|
| Hub to spoke | Hub overview | Narrow task page | Descriptive task phrase, not exact-match stuffing | Spoke solves a distinct task | `g-helpful-content` |
| Spoke to hub | Support article | Cluster hub | Broad topic phrase or "topic guide" equivalent | Hub explains context and siblings | `g-helpful-content` |
| Sibling to sibling | Task page | Adjacent task or comparison | Natural next-step language | Reader sequence or funnel path | `g-gsc-api` when data exists |
| Canonical cleanup | Duplicate or near duplicate | Declared owner | Clarify preferred reader path | Content owner and URL signals reviewed | `g-canonical` |
| Evidence support | Claim-heavy page | Source or methodology explainer | Verification language, not sales anchor | Reader needs to inspect evidence path | `g-helpful-content`; `g-qrg-full` |
| Refresh correction | Stale spoke | Current owner page | Updated task phrase with date cue | Source refresh changed the preferred destination | `g-helpful-content`; `g-ranking-history` |
| AI surface context | Any answer-rich page | Source-backed explainer | Link only when it helps verification | Standard crawling and preview posture | `g-ai-features`; `sparktoro-zero-click-2026` |

## Audit Procedure

1. Start from the chosen hub and list every spoke that should be reachable within one click.
2. Record the exact anchor text proposed for each direction.
3. Compare GSC page-query evidence where available before changing high-value links.
4. Send duplicate-owner conflicts to [[Cannibalization Review]].
5. Recheck the matrix after hub selection, page pruning, or major refresh work.

## Link Assignment Example

A no-code automation hub links to setup, comparison, pricing, and troubleshooting spokes. Source ID: `g-helpful-content`.

The setup spoke returns to the hub with "automation workflow guide" because the reader may need broad context. Source ID: `g-helpful-content`.

The pricing spoke links to the comparison spoke only when the next decision is method selection. Source ID: `g-helpful-content`.

The troubleshooting article avoids exact-match anchors when GSC shows mixed query intent. Source ID: `g-gsc-api`.

The matrix blocks a link to a thin glossary until the glossary gains source-backed usefulness. Source ID: `g-helpful-content`.

If the declared owner changes, the old anchor list is archived before the new plan ships. Source ID: `g-canonical`.

## Link Plan Failure Modes

- Repeating one keyword anchor across every spoke can make navigation less useful. Source ID: `g-helpful-content`.
- Adding links to a weak page does not make that page a valid cluster owner. Source ID: `g-helpful-content`.
- Sibling loops can trap readers between near-duplicate pages instead of resolving intent. Source ID: `g-canonical`.
- A link added for AI visibility alone should be rejected as unsupported Google advice. Source ID: `g-ai-opt-guide`.
- Old canonical decisions can make a good anchor point to the wrong preferred URL. Source ID: `g-canonical`.

## Validation Feed

[[Semantic Cluster Execution Plan]] consumes the proposed hub, spoke, sibling, and corrective links as the link brief. Source IDs: `g-helpful-content`, `g-canonical`.

[[SEO Check Validation Checklist]] expects final anchors, destinations, evidence state, and pass or fix status before publication. Source IDs: `g-canonical`, `g-helpful-content`.

## Measurement Note

Search Console data can show query, page, CTR, and position patterns, but it does not prove why a link changed performance. Use `g-gsc-api` for measurement fields and keep the causal claim conservative.
