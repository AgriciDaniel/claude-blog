---
type: spoke
title: "Brief Source Pack"
domain: "Blog Briefs"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [briefs-outlines, serp-briefs, active]
---

# Brief Source Pack

## Brief Source Pack Evidence Job

The source pack is the evidence tray for a brief. It gathers the URLs, retrieval dates, source IDs, claim coverage, and limitations that the writer may use. It should not decide the final angle, write the outline, or approve risky claims. Those moves belong to [[Reader Job Statement]], [[Heading Hierarchy Rules]], and [[Brief Risk Notes]].

The pack favors official and primary material for rule-like guidance. `g-helpful-content` supplies the people-first baseline. `g-ai-opt-guide` keeps AI-feature advice tied to normal Search fundamentals, while `g-genai-reports` documents the Search Console reporting surface for AI Overviews and AI Mode. `sparktoro-zero-click-2026` can frame low-click planning only as practitioner market context.

### Source Type Roles

Official sources set constraints. Primary research can describe measured behavior. Practitioner sources can inspire checks, but they need caveats before they become brief requirements. Search snippets, AI answers, and competitor copy are observation inputs, not evidence records.

### Claims This Note Must Not Validate Alone

The source pack cannot by itself approve legal, medical, financial, or reputation claims. It also cannot prove a ranking factor from a visible SERP pattern. When a claim needs a verdict, send it to [[Evidence Block Requirements]] and use the claim-ledger labels.

## Brief Source Pack Source Table

| Source ID | URL | Date basis | Claim coverage | Limitation | Refresh cadence |
| --- | --- | --- | --- | --- | --- |
| `g-helpful-content` | Google Search Central helpful content page | last updated 2025-12-10, retrieved 2026-07-09 | People-first content checks, E-E-A-T framing, self-assessment prompts | Does not supply a content template or ranking guarantee | Monthly or when Search Central changes |
| `g-ai-opt-guide` | Google AI features optimization guide | last updated 2026-06-15, retrieved 2026-07-08 | Google AI feature foundations, crawlability, preview controls, no AI-only shortcut requirement | Does not guarantee AI Overview or AI Mode inclusion | Monthly while AI docs move quickly |
| `g-genai-reports` | Search Console generative AI performance reports | published 2026-06-03, retrieved 2026-07-08 | AI Overviews and AI Mode reporting in Search Console | Not a visibility guarantee or complete rollout promise | Monthly while reporting changes |
| `sparktoro-zero-click-2026` | SparkToro zero-click study | published 2026-06-08, retrieved 2026-07-08 | Market context for low-click planning and AI Mode query-share caveats | Third-party panel, not first-party site analytics | Recheck before quarterly planning |
| `g-qrg-full` | Search Quality Rater General Guidelines PDF | dated 2025-09-11, retrieved 2026-07-09 | Trust, reputation, and YMYL sensitivity checks | Rater guidance is not a direct ranking checklist | Recheck when QRG changes |
| `g-gsc-api` | Search Console Search Analytics API | living API documentation, retrieved 2026-07-06 | First-party query, page, click, impression, CTR, and position fields | Requires property access and cannot explain all visibility changes | Recheck before data integration work |
| `dfs-api` | DataForSEO API documentation | living vendor documentation, retrieved 2026-07-06 | External SERP capture and keyword evidence when first-party data is unavailable | Vendor data is not Google's internal ranking system | Recheck before provider-backed exports |
| `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` | Google guidance on SEO tools and advice | published 2026-06-05, retrieved 2026-07-09 | Boundaries for third-party ranking, AEO, and GEO claims | Does not audit a specific vendor's private method | Monthly while advice pages change |

## Brief Source Pack Refresh Procedure

1. Start with the claim list from [[SERP Brief Input Contract]], not with a generic URL bundle.
2. Match each claim to the strongest available source ID and record the claim wording it actually supports.
3. Mark every source as official, primary, practitioner, or unsupported.
4. Replace any source that lacks a date, retrieval record, or clear claim coverage.
5. Hand the approved pack to [[Brief To Draft Handoff]] with caveats the writer must preserve.

## Writer Handoff Packet

A completed pack contains the source ID, canonical URL, date, supported claim, source limit, and refresh cue. The writer may quote or paraphrase only claims that appear in this packet. Any new factual claim discovered during drafting returns here before publication-facing copy is created.

## Source Packet Example

Before review, the pack lists a Google help page, a vendor study, and two competitor URLs with no claim mapping. The source steward rewrites it into claim rows: helpful-content criteria map to the article quality promise, AI feature wording maps to normal Search guidance, and zero-click context is labeled market-only. Source IDs: `g-helpful-content`, `g-ai-opt-guide`, `sparktoro-zero-click-2026`.

The competitor pages move to [[SERP Observation Ledger]] because they can show visible patterns but cannot validate facts. A tool score enters the brief only as a vendor estimate after the limitation row cites Google's third-party tool guidance. Source IDs: `dfs-api`, `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice`.

## Pack-Specific Failure Cases

- A URL has authority, but the exact claim sits outside the cited page. Source ID: `g-helpful-content`.
- A market study replaces available property data. Source ID: `g-gsc-api`.
- A SERP snapshot is filed as a source instead of an observation. Source ID: `dfs-api`.
- A QRG passage is used to promise ranking movement. Source ID: `g-qrg-full`.

## Output Contract Fit

[[Content Brief Output Contract]] consumes the approved evidence pack. Inputs provided: source ID, URL, date basis, supported wording, limitation, and refresh cue. Expected output: each brief claim names a nearby source ID and keeps the limitation visible.

[[SERP Outline Output Contract]] consumes only the source IDs needed for section evidence slots. Expected output: no outline section requests statistics, policy claims, or AI-feature language outside this pack.

## Sources

- `g-helpful-content`
- `g-ai-opt-guide`
- `g-genai-reports`
- `g-qrg-full`
- `g-gsc-api`
- `dfs-api`
- `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` for source-pack tool limitations
- `sparktoro-zero-click-2026`
