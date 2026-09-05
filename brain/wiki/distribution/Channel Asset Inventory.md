---
type: spoke
title: "Channel Asset Inventory"
domain: "Blog Distribution"
status: active
created: 2026-07-06
updated: 2026-07-09
tags:
  - distribution
  - assets
  - inventory
  - active
confidence: advisory
related:
  - "[[Distribution and Repurposing]]"
  - "[[Canonical Attribution Rules]]"
  - "[[Repurposing Source Fidelity]]"
  - "[[Distribution Measurement Plan]]"
  - "[[Images Audio and Charts]]"
  - "[[Google Data Integrations]]"
  - "[[Voice and Style]]"
  - "[[Zero Click Planning Baseline]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://sparktoro.com/blog/in-2026-less-than-one-third-of-google-searches-still-send-a-click/"
  - "https://developers.google.com/analytics/devguides/reporting/data/v1"
  - "https://developers.google.com/search/docs/appearance/google-images"
  - "https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links"
---

# Channel Asset Inventory

## Channel Asset Inventory Channel Job

Channel Asset Inventory is the distribution control sheet for derivative assets created from one canonical blog post. It answers four questions before publication: what asset exists, which channel owns it, whether the asset still matches the source post, and how performance will be measured. The inventory should be opened before a team creates a thread, email, video, community post, podcast brief, or image card.

### Canonical Post Signals To Preserve

Every row should preserve the canonical URL, the article's main claim, publication or refresh date, source IDs used in the derivative asset, and any caveat that changes interpretation. Use `g-helpful-content` when the asset changes reader value, `g-ai-opt-guide` for Google AI setup statements, and `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` when someone asks whether an AI file is mandatory.

### Channel-Specific Adaptations Allowed

Allowed adaptations include changing the hook, shortening evidence, replacing a chart with alt text or a thumbnail, and shifting the call to action to fit the channel. The asset owner must not turn market context from `sparktoro-zero-click-2026` into a property forecast; point the context to [[Zero Click Planning Baseline]]. Image or thumbnail handling can cite `g-google-images` when visual search eligibility or descriptive alt text matters.

## Channel Asset Inventory Asset Table

| Inventory field | Required decision | Source ids | Evidence state | Owner | Next action |
|---|---|---|---|---|---|
| Canonical source | URL, title, publish date, refresh date | `g-helpful-content` | Confirmed from post | Content owner | Add canonical link to row |
| Asset format | Thread, newsletter, video, community post, podcast, image | [[Distribution and Repurposing]] | Draft until channel selected | Distribution lead | Assign one format per row |
| Source fidelity | Exact claims reused and caveats retained | `g-helpful-content`, [[Repurposing Source Fidelity]] | Needs reviewer signoff | Factcheck owner | Compare against source block |
| AI claim hygiene | No Google AI-only file requirement inserted | `g-ai-opt-guide`, `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` | Confirmed after copy review | SEO reviewer | Remove unsupported setup tasks |
| Visual provenance | Thumbnail, chart, or screenshot origin and alt text | `g-google-images`, [[Images Audio and Charts]] | Pending until asset file exists | Media owner | Record license or source path |
| Measurement route | Metric, tool, and date window | `g-ga4-data`, [[Distribution Measurement Plan]] | Blocked without access | Analytics owner | Attach report link or gap note |
| Disclosure state | Relationship, sponsorship, generated asset, or source cue | `g-qualify-links`, [[Canonical Attribution Rules]] | Open until channel copy shows it | Distribution lead | Add visible disclosure text |
| Retirement reason | Asset removed, replaced, merged, or superseded | [[Distribution Measurement Plan]] | Confirmed after owner note | Channel owner | Keep row for reporting history |

## Asset, Channel, Source Link, Owner, Status, And Measurement

An inventory row should be boring enough to audit. The status values are planned, drafted, reviewed, shipped, measured, and retired. Measurement belongs in the row only after the metric definition is known; otherwise the row records an evidence gap rather than a speculative target. If a derivative asset is deleted, keep the row and mark the reason so later reporting does not treat missing data as a performance change.

### Example: One Article, Three Assets

A canonical post becomes a newsletter, a social thread, and a short video. The inventory creates three rows, repeats the same canonical URL, assigns separate owners, and records different measurement routes with `g-ga4-data` only where property evidence exists. The video row cannot move to shipped until thumbnail provenance and source-card approval are present under `g-google-images` and [[Repurposing Source Fidelity]].

### Inventory-Specific Failure Patterns

This sheet breaks when two owners create the same asset row, when a deleted post is removed from the inventory, or when the metric field still says unknown after launch. It also breaks when a screenshot is logged as a visual asset without a source path, license note, or alt-text plan tied to `g-google-images`.

### Repurposing Matrix Feed

[[Repurposing Asset Matrix]] consumes the inventory row after channel selection. It needs asset format, canonical source, owner, source-fidelity status, disclosure state, measurement route, and retirement reason; it expects one auditable channel row that can be approved, blocked, measured, or retired.

## Channel Asset Inventory Fidelity Checks

1. Open the canonical post and highlight claims reused in the derivative asset.
2. Add the source ID beside each claim that leaves the original page.
3. Verify the channel adaptation changes framing without broadening the claim.
4. Confirm owner, status, and measurement field before the asset is marked shipped.
5. Send unresolved visual, voice, or attribution issues to [[Images Audio and Charts]], [[Voice and Style]], or [[Canonical Attribution Rules]].

## Source IDs Wired

This note cites `g-helpful-content`, `g-ai-opt-guide`, `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`, `sparktoro-zero-click-2026`, `g-ga4-data`, `g-google-images`, and `g-qualify-links`.
