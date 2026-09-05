---
type: spoke
title: "Cluster Performance Score"
domain: "Blog Topic Architecture"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [clusters, semantic-clusters, active]
confidence: advisory
---

# Cluster Performance Score

## Scoring Purpose

Use this note to judge whether a topic cluster is healthy enough to brief, refresh, or report on. The score is an editorial operating score, not a Google ranking model and not a traffic forecast.

### Criteria This Score Owns

The score owns coverage completeness, helpfulness, evidence freshness, link clarity, and visible outcome tracking. A cluster can score well only when the hub and spokes help readers complete distinct jobs. Source ID: `g-helpful-content`.

### Criteria Delegated Elsewhere

Query-page overlap belongs to [[Cannibalization Review]], owner selection belongs to [[Cluster Hub Selection]], and AI feature measurement belongs to [[Google Data Integrations]] when Search Console generative AI reports are available. Source ID: `g-genai-reports`.

## Score Evidence Table

| Criterion | Points | Required proof | Blocking failure | Source IDs |
|---|---:|---|---|---|
| Reader-job coverage | 25 | Hub and spokes map to distinct tasks | Multiple pages solve the same job | `g-helpful-content` |
| Evidence currency | 20 | Current source IDs and refresh dates on volatile claims | Undated Search or AI claim | `g-ai-opt-guide`; `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` |
| Link architecture | 20 | Hub-to-spoke, spoke-to-hub, and sibling anchors are intentional | Orphaned support page | `g-helpful-content` |
| Measurement readiness | 20 | GSC or generative AI reporting path named when available | Market stat treated as property data | `g-genai-reports`; `sparktoro-zero-click-2026` |
| Caveat discipline | 15 | No ranking, traffic, or AI inclusion promise | Unqualified forecast or guarantee | `sparktoro-zero-click-2026` |

## Non-Scoring Diagnostics

| Diagnostic signal | Why it matters | Evidence route | Score handling | Source IDs |
|---|---|---|---|---|
| AI reporting unavailable | Missing report access changes observability, not page usefulness | Search Console generative AI reporting note | Mark measurement caveat instead of inventing exposure data | `g-genai-reports` |
| One orphaned spoke | Reader path breaks even when coverage exists | Link crawl and hub map | Penalize link architecture before adding new pages | `g-helpful-content` |
| Source freshness mixed | Stable evergreen claims and volatile AI claims age differently | Source IDs plus update timeline | Penalize only the claim family that went stale | `g-helpful-content`; `g-ranking-history` |
| External benchmark only | Market context cannot stand in for client property performance | [[AI Citation Mechanics]] caveat record | Keep the score advisory and request first-party data | `sparktoro-zero-click-2026`; `g-gsc-api` |

## Worked Score Read

A cybersecurity cluster has clear hub and spoke roles, but two support pages lack current sources. Source ID: `g-helpful-content`.

The hub links to four spokes, while one incident-response article has no return path. Source ID: `g-helpful-content`.

GSC page-query exports exist, but generative AI reporting is unavailable for the property. Source IDs: `g-gsc-api`, `g-genai-reports`.

The score lands in the structural-repair band rather than ready because links and evidence block scale. Source IDs: `g-helpful-content`, `g-genai-reports`.

The next action is refresh sources, repair the return link, and rescore before calendar expansion. Source ID: `g-helpful-content`.

The rollback trigger is a later export showing the repaired spoke still receives unrelated query traffic. Source ID: `g-gsc-api`.

## Scoring Distortions

- A high total should not override one blocker tied to unsupported Search or AI claims. Source ID: `g-ai-opt-guide`.
- Treating a practitioner benchmark as client data inflates measurement readiness. Source ID: `sparktoro-zero-click-2026`.
- Blending two clusters in one score hides cannibalization and owner conflicts. Source ID: `g-helpful-content`.
- Polished anchors cannot compensate for a page that fails its reader job. Source ID: `g-helpful-content`.
- Missing generative AI report access should be labeled missing, not scored as failure. Source ID: `g-genai-reports`.

## Audit Wiring

[[Full Site Blog Audit Report]] consumes the total score, lowest criterion, blocker note, evidence type, and recommended action. Source IDs: `g-helpful-content`, `g-gsc-api`.

The expected output is an audit finding with severity, recommendation format, delivery status, and rollback trigger. Source IDs: `g-qrg-full`, `g-gsc-api`.

## Review Procedure

1. Score only a named cluster, never a folder in the abstract.
2. Subtract points for missing evidence before adding points for polish.
3. Mark any criterion blocked when the evidence source is stale or outside the ledger.
4. Convert the total into one action: refresh, expand, consolidate, monitor, or escalate.
5. Record the weakest source type because that sets confidence for the whole score.

## Interpretation Bands

Use 85 to 100 for ready, 70 to 84 for refresh before scale, 50 to 69 for structural repair, and below 50 for consolidation or research. The zero-click source remains an `AS-REPORTED` market signal owned by [[AI Citation Mechanics]], so it should influence caveats more than scoring math.
