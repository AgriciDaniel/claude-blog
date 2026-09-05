---
type: spoke
title: "Search Intent Classification"
domain: "Blog Briefs"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [briefs-outlines, serp-briefs, active]
---

# Search Intent Classification

## Search Intent Classification Decision Job

This note classifies the primary and secondary intent behind a query set before a brief chooses its angle. It distinguishes learn, compare, choose, troubleshoot, localize, buy, and refresh intents. The output is a classification map with confidence, evidence state, and a canonical owner for the next step.

Do not treat intent as a static keyword label. Use [[SERP Observation Ledger]] for dated SERP evidence, [[Reader Job Statement]] for the human task, and [[Competitive Pattern Notes]] for format pressure. `g-helpful-content` supports matching content to a real user need. `g-ads-kw` can support keyword-discovery inputs, while `dfs-labs` can support SERP-overlap or competitor datasets. Use `g-ai-features` when the intent may be answered on a Google AI surface.

### Primary Intent Labels

Choose one primary label and one optional secondary label. If no label wins, write a mixed-intent note and split the brief or page plan.

### Mixed Intent Handling

Mixed SERPs need a deliberate choice. A comparison article, glossary page, and implementation guide should not be collapsed into one outline unless the reader job genuinely requires all three.

## Intent Classification Map

| Hub or spoke page | Target intent | Canonical owner | Anchor evidence | Evidence state |
| --- | --- | --- | --- | --- |
| [[Reader Job Statement]] | Translate query into task | brief owner | Query set plus reader context | Required before classification |
| [[Competitive Pattern Notes]] | Observe format and source pattern | SEO strategist | Dated SERP notes | Observation, not causation |
| [[Heading Hierarchy Rules]] | Structure selected intent | outline owner | Approved reader job and intent label | Ready after intent decision |
| [[Evidence Block Requirements]] | Support claim-heavy sections | source steward | Source IDs from source pack | Required for factual sections |
| [[AI Citation Mechanics]] | Handle AI answer surfaces | SEO lead | `g-ai-features` plus dated observation | Official boundary plus advisory planning |
| [[Dual Optimization]] | Separate click, visibility, and citation goals | analyst | Property or market evidence with limits | Advisory context |
| [[Content Template Selection Matrix]] | Select article container | strategist | Approved reader job and intent mix | Template follows reader task |
| [[SERP Outline Output Contract]] | Turn intent into section jobs | outline owner | Chosen and rejected intents | Ready after split cases close |

## Classification Procedure

1. List the query set and remove brand, navigational, or irrelevant variants.
2. Assign a provisional intent label based on the reader job, not volume alone.
3. Compare the label against current SERP observations and competitor formats.
4. Mark confidence as high, medium, or low and explain the weakest evidence.
5. Send low-confidence or split-intent cases back to the brief owner before outline work starts.

## Intent Split Example

Query set: "best CRM blog examples", "CRM content strategy", and "how to write CRM comparison posts." The first query leans compare, the second leans learn, and the third leans implement. One article can cover them only if the reader job is choosing a repeatable comparison format. Source IDs: `g-helpful-content`, `dfs-labs`.

Rejected path: a broad "CRM content strategy guide" would mix learn and implement intents without a clear decision container. Approved path: a comparison-format article with an implementation checklist linked as a follow-up. Source IDs: `nng-editorial-heuristics`, `g-helpful-content`.

## Intent Classification Failure Modes

- Search volume picks the intent when the reader job says otherwise. Source ID: `g-ads-kw`.
- Navigational or brand variants contaminate an informational brief. Source ID: `g-helpful-content`.
- AI answer presence is treated as a separate intent label. Source ID: `g-ai-features`.
- Mixed intent is hidden inside a bloated outline. Source ID: `nng-editorial-heuristics`.

## Intent Deliverable Wiring

[[Content Brief Output Contract]] consumes the classification map. Inputs provided: primary intent, secondary intent, rejected intents, confidence, weakest evidence, and split recommendation. Expected output: the brief chooses one article type and states what it will not cover.

[[SERP Outline Output Contract]] consumes the approved intent decision. Expected output: H2 jobs match the selected intent, while rejected intents become internal links or future briefs.

## Sources

- `g-helpful-content`
- `g-ads-kw`
- `dfs-labs`
- `g-ai-features`
- `nng-editorial-heuristics`

## Handoff

The approved classification goes to [[SERP Brief Input Contract]] and [[Heading Hierarchy Rules]]. The handoff must include the primary intent, secondary intent if present, rejected intents, and the reason the chosen article type is the right container.
