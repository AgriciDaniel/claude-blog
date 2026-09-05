---
type: spoke
title: "FLOW Source Intake"
domain: "Blog Workflow"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [flow, active]
confidence: advisory
related:
  - "[[FLOW Framework]]"
  - "[[FLOW Brief Stage]]"
  - "[[FLOW Confidence Tags]]"
  - "[[Research Pack Index]]"
  - "[[2026 Google Update Timeline]]"
---

# FLOW Source Intake

## Source Intake Purpose

FLOW Source Intake captures sources, claims, dates, confidence, limitations, and usage boundaries before writing starts. It is the first defense against memory-based SEO advice. A source can enter the workflow only when the operator knows what claim it supports and what it does not prove.

## Source Packet Entry Rules

Every intake packet records source ID, title, URL, source type, publication or update date, retrieval date, confidence, evidence tier, and limitation. `gh-flow-framework` gives this workflow its stage discipline. `g-helpful-content` enters as official support for people-first usefulness. `g-ai-features` enters when the source is about AI Overviews or AI Mode surfaces. `sparktoro-zero-click-2026` enters as practitioner market research and points interpretation to [[AI Citation Mechanics]].

## Intake Capture Table

| Intake field | Required input | Evidence required | Action | Owner | Handoff |
|---|---|---|---|---|---|
| Claim text | Exact sentence or recommendation | Source ID tied to claim | Split broad claims into checkable units | Intake owner | [[FLOW Confidence Tags]] |
| Source date | Published, updated, retrieved, or verified date | Ledger metadata | Mark stale or current | Research owner | [[Research Pack Index]] |
| Google Search guidance | Official source URL and section | `g-helpful-content` or `g-ai-features` | Record allowed operational use | SEO lead | [[FLOW Brief Stage]] |
| Update-specific caveat | Current update or changelog item | Dated ledger source ID | Attach timeline context | Factchecker | [[2026 Google Update Timeline]] |
| Market study context | Study method and geography | `sparktoro-zero-click-2026` | Label AS-REPORTED and advisory | Strategy owner | [[AI Citation Mechanics]] |
| AI file or special markup claim | Exact requested tactic | `g-ai-opt-guide` or blocked source gap | Keep or reject the tactic boundary | GEO owner | [[FLOW Confidence Tags]] |
| FAQPage rich-result claim | Requested schema wording | `g-faqpage-sd` | Record retired-rich-result caveat | Schema owner | [[FLOW Factcheck Stage]] |
| First-party export summary | Redacted GSC or GA4 file | `g-gsc-api` or `g-ga4-data` | Capture fields, date range, and limits | Data owner | [[Google API Evidence Matrix]] |

## Claim Boundary Checks

Ask what the source proves, what it does not prove, and whether the recommendation needs first-party data. A Google source may support a rule but not a performance guarantee. A market study may support planning pressure but not one site's future clicks. If a claim lacks dates or limitations, it stays out of the brief.

## Handoff To Brief Stage

The packet exits to [[FLOW Brief Stage]] with accepted source IDs, blocked claims, open refresh needs, and confidence labels. The brief owner should be able to draft without reopening the ledger for every sentence.

## Example: Intake For An AI Search Claim

Incoming claim: "Google needs an AI-specific file before it can cite the page."

The intake owner splits the claim into a Google requirement claim and a
non-Google assistant behavior claim.

The Google side cites `g-ai-opt-guide` and
`g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`.

The non-Google side stays blocked unless the operator supplies a dated source
that belongs in the ledger.

The packet sent to [[FLOW Brief Stage]] contains one verified correction, one
blocked claim, and one instruction to avoid guarantee language.

## Intake Errors That Poison Later Stages

- A source is captured by URL, but the supported claim is never written.
- A living document is treated as static without a refresh date.
- Market geography is missing, so the brief misuses the study later.
- First-party exports are summarized without date range or dimensions.

## Consumed By Research Deliverables

[[Factcheck Claim Register]] consumes source ID, exact claim text, source date,
evidence tier, confidence, limitation, and refresh need.

[[Content Brief Output Contract]] consumes the accepted source pack, blocked
claims, and caveats before outline or draft work begins.

The deliverables expect source packets that are narrow enough to verify without
reinterpreting the source from scratch.
