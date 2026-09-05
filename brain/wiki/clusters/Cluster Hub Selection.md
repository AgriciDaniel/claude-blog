---
type: spoke
title: "Cluster Hub Selection"
domain: "Blog Topic Architecture"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [clusters, semantic-clusters, active]
confidence: advisory
---

# Cluster Hub Selection

## Hub Selection Mandate

This note picks the page that should act as the center of a topic cluster. The selected hub owns the broad reader promise, names the important entities, routes users to spokes, and becomes the internal link target for the cluster.

### Hub Eligibility

A hub candidate must be broad enough to orient a reader, specific enough to avoid becoming a glossary, and strong enough to stand alone as helpful content. The best hub can explain why each spoke exists without trying to absorb every answer. Source ID: `g-helpful-content`.

### Hub Disqualifiers

Reject a candidate when it is only a list of links, a thin intro page, a stale announcement, or a page optimized around an AI-only tactic. The Google Search llms.txt clarification, tracked through [[2026 Google Update Timeline]], is a reminder that special files are not a hub-selection criterion. Source IDs: `g-ai-opt-guide`, `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`.

## Candidate Hub Scorecard

| Candidate page | Reader promise | Evidence source | Hub fit | Decision |
|---|---|---|---|---|
| Existing broad guide | Explains the whole topic and links to task pages | Helpful-content review and SERP-overlap export | Strong if source dates are current | Nominate as hub |
| High-traffic narrow article | Solves one task very well | `dfs-labs` or property query data, plus editorial review | Weak as hub, strong as spoke | Keep as spoke unless broadened |
| Expert-authored overview | Frames decisions, caveats, and examples across the topic | Author proof, source inventory, `g-qrg-full` | Strong when it can route every major task | Nominate after source review |
| New overview page | Needed when no page can orient readers | Source inventory and gap analysis | Possible, but only with original examples | Draft after [[Cluster Gap Analysis]] |
| Legacy category page | Mostly navigation with little substance | Internal link crawl and content review | Usually weak | Refresh or retire from hub role |
| Product feature page | Explains one solution and conversion path | Product facts, audience fit, `g-helpful-content` | Risky as hub when education is broader | Keep as spoke or sales page |

## Selection Procedure

1. Write the cluster promise before looking at traffic.
2. List all candidate pages and their existing query, entity, and conversion roles.
3. Compare candidates for reader usefulness, not just impressions.
4. Use `dfs-labs` or first-party exports to identify overlap, then keep the evidence caveats visible.
5. Assign one hub, name its first five required spokes, and send conflicts to [[Cluster Canonical Page Rules]].

## Selection Example

A "marketing attribution" cluster contains a broad guide, a tool-comparison post, and a product feature page. Source ID: `g-helpful-content`.

The comparison post has stronger query demand, but it answers a choice task rather than orienting the whole field. Source IDs: `g-gsc-api`, `g-helpful-content`.

The product feature page is useful for buyers, yet it narrows the promise to one vendor path. Source ID: `g-helpful-content`.

The broad guide becomes hub because it defines the problem, names entities, and routes readers to specific tasks. Source ID: `g-helpful-content`.

The first spoke list includes comparison, implementation, reporting, troubleshooting, and glossary support. Source ID: `g-helpful-content`.

If SERP-overlap data later shows the guide and comparison page serving one task, ownership returns to review. Source IDs: `dfs-labs`, `g-gsc-api`.

## Hub Selection Errors

- Selecting by traffic alone can put a narrow article in charge of unrelated spokes. Source IDs: `g-gsc-api`, `g-helpful-content`.
- Treating a tag archive as a hub can hide a missing explanatory page. Source ID: `g-helpful-content`.
- Using "AI-ready hub" as a criterion invents a requirement Google does not state. Source ID: `g-ai-opt-guide`.
- Ignoring stale source dates lets an old hub keep ownership without current evidence. Source ID: `g-helpful-content`.
- Forcing a product page to educate all audiences can blur commercial and informational intent. Source ID: `g-helpful-content`.

## Plan Wiring

[[Semantic Cluster Execution Plan]] consumes the chosen hub, rejected candidates, first spokes, and unresolved conflicts. Source IDs: `g-helpful-content`, `g-canonical`.

Its expected output is a cluster execution row with chosen canonical hub, evidence note, owner, and review trigger. Source IDs: `g-canonical`, `g-gsc-api`.

## Forecast Caveat

The SparkToro zero-click record is useful context for why hubs should answer clearly and route users efficiently, but the benchmark in [[AI Citation Mechanics]] does not predict cluster traffic. Source ID: `sparktoro-zero-click-2026`.
