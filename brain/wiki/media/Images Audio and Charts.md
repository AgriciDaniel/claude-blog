---
type: hub
title: "Images Audio and Charts"
domain: "Blog Media"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [media, images, audio, charts, active]
---

# Images Audio and Charts

## Images Audio and Charts Operating Scope

Images Audio and Charts is the media hub for blog assets that improve comprehension, trust, distribution, and schema hygiene. It owns the decision layer before production: what asset is needed, what source or rights evidence is required, what accessibility work must exist, and which spoke note reviews the asset before publication.

This hub does not publish files, edit a CMS, submit sitemaps, create schema, or approve legal rights. It records the operating decision and sends implementation to the correct owner. Image and video discovery are sourced through `g-google-images`; AI-specific overreach is bounded by `g-ai-opt-guide`; media vocabulary uses `schema-full`; crawler-policy caveats use `g-common-crawlers`.

### What This Hub Owns In Media Handling

- Image usefulness, provenance, alt text, captions, and sitemap readiness.
- Audio summary fidelity and transcript handoff.
- Chart source packets, visualization review, and chart-accessibility review.
- VideoObject readiness when visible videos appear on a post.
- Repurposing boundaries for social, email, slide, chart, audio, and video variants.

### What The Hub Must Not Absorb

Claims about broad AI behavior belong in [[AI Citation Mechanics]]. Schema generation belongs in [[Blog Schema Stack]]. Distribution scheduling belongs in [[Distribution and Repurposing]]. Overall scoring belongs in [[Blog Quality Score]]. Source discovery and source gaps belong in [[Research Pack Index]].

## Images Audio and Charts Spoke Map

| Spoke | Deliverable boundary | Primary input | Output | Source IDs |
|---|---|---|---|---|
| [[Image Selection Rules]] | Decide whether an image earns placement | Article section and asset idea | Accept, revise, or reject image request | `g-google-images`, `g-ai-opt-guide`, `schema-full`, `g-common-crawlers` |
| [[Alt Text Standards]] | Write useful alt text and caption needs | Approved asset and reader job | Alt/caption instruction | `g-google-images`, `g-video`, `g-ai-opt-guide`, `schema-full` |
| [[Chart Source Requirements]] | Prove the chart's data basis | Dataset, method, date range | Source packet or blocked chart | `g-helpful-content`, `nng-editorial-heuristics`, `g-ai-opt-guide`, `schema-full` |
| [[Data Visualization Review]] | Check scale, labels, and comparison fairness | Chart draft | Pass, revise, or block | `g-google-images`, `g-video`, `g-intro-sd`, `g-update-2026-06-30-merchant-center-product-videos-serving-eligible` |
| [[VideoObject Checklist]] | Validate visible video markup readiness | Video page, thumbnail, transcript | Schema handoff or rejection | `g-video`, `schema-full`, `g-search-gallery`, `g-ai-opt-guide` |
| [[Media QA For Blog Posts]] | Final gate before ready status | Full media inventory | Pass/fail handoff | `g-google-images`, `g-video`, `g-ai-opt-guide`, `schema-full`, `g-intro-sd` |

## Images Audio and Charts Evidence And Refresh Rules

1. Start every media recommendation with an asset job, not an asset format.
2. Cite source IDs in the note that makes the decision.
3. Treat Schema.org vocabulary as vocabulary until Google Search documentation supports a feature claim.
4. Refresh media notes when Google image, video, AI guidance, crawler, or structured-data documents change in the ledger.
5. Record source gaps instead of filling them with generic media advice.

## Images Audio and Charts Asset Review Table

| Asset family | Required evidence | Accessibility minimum | Placement check | Review owner |
|---|---|---|---|---|
| Image | Source, rights, asset job | Alt or empty-alt decision | Near the copy it clarifies | Media editor |
| Audio | Script map to article claims | Transcript or summary text | Canonical article link nearby | Editor |
| Chart | Dataset, method, date range | Text summary and labeled units | Beside interpretation | Data reviewer |
| Video | Visible player, thumbnail, transcript note | Captions or transcript route | Page content matches markup | Video reviewer |
| Generated media | Tool, inputs, edit summary, approval | Disclosure and alt/caption as needed | Not used as factual proof | Editorial owner |

## Images Audio and Charts Source IDs

Hub-level source IDs are `g-google-images`, `g-ai-opt-guide`, `schema-full`, and `g-common-crawlers`. Spoke notes carry narrower source packets when a decision needs video, chart, or product-media evidence.
