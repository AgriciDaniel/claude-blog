---
type: spoke
title: "Assistant Answer Surface Map"
domain: "GEO and AEO"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [geo-aeo, ai-citation, evergreen]
---

# Assistant Answer Surface Map

## Assistant Answer Surface Map Boundary

This note separates Google Search AI features from broader assistant-like answer systems. It exists because teams often say "AI citations" as if AI Overviews, AI Mode, ChatGPT, Gemini, Copilot, Perplexity, and other tools share one citation rule. They do not. Google-specific claims must cite `g-ai-features`, `g-ai-opt-guide`, and the June 2026 `llms.txt` clarification source `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`; product-scale AI Mode context can cite `blog-io2026`.

Non-Google assistant evidence is weaker in this ledger. `seoclarity-chatgpt` can support an AS-REPORTED observation about ChatGPT-cited pages, but it cannot validate Google Search visibility. Keep that separation visible before creating an action item.

### Surfaces This Map Accepts

Use this note when a brief, audit, or report names more than one answer surface and needs different evidence, measurement, or caveat language for each.

### Surfaces Routed To Sibling Notes

AI Overview-specific work goes to [[AI Overview Citation Review]], AI Mode work goes to [[AI Mode Citation Review]], and llms.txt claims go to [[llms.txt Caveat Note]].

## Assistant Answer Surface Map Table

| Surface | Evidence accepted | Source IDs | Measurement route | Caveat |
|---|---|---|---|---|
| Google AI Overviews | Search docs, observed SERP, cited URL | `g-ai-features`, `g-ai-opt-guide` | [[Citation Exposure Metrics]] | Google feature behavior, not assistant-wide proof |
| Google AI Mode | Google product announcement, AI feature docs, observed answer | `blog-io2026`, `g-ai-features` | AI Mode query sampling and GSC report if available | Product reach is not a site forecast |
| Google Search file requests | AI optimization guide and update record | `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` | No Google visibility metric for llms.txt | File may exist for other consumers |
| Non-Google assistants | Platform-specific observations and cited URLs | `seoclarity-chatgpt` | Referral and citation logs outside this V1 brain | Do not infer Google ranking value |
| Search Console AI reporting | Property export for eligible Google surfaces | `g-genai-reports`, `g-ai-features` | [[Google API Evidence Matrix]] when export exists | Reporting availability is property-specific |
| AI training crawler controls | Robots rule for Google-Extended or similar request | `g-common-crawlers`, `g-ai-opt-guide` | Crawler-control inventory, not citation exposure | Separate training opt-out from Search display |
| Assistant citation audit | Captured answer, cited URL, date, and platform name | `seoclarity-chatgpt` | Manual citation log outside Google Search | Treat as assistant-specific evidence only |

## Assistant Answer Surface Routing Procedure

1. Name the exact product or result type before writing the recommendation.
2. Attach only source IDs that speak to that product or surface.
3. Mark cross-surface claims as unsupported until a second surface-specific source exists.
4. Send measurement work to [[Google Data Integrations]] only when the evidence is first-party or Search Console based.

## Routing Scenario

A stakeholder says a post was cited by ChatGPT and asks why it was not also cited in Google AI Overviews. This map keeps those as different evidence lanes: `seoclarity-chatgpt` can support a non-Google assistant observation, while `g-ai-features` is required for Google Search feature language.

If the same post has Search Console generative AI data, the Google row moves to [[Citation Exposure Metrics]] with `g-genai-reports`. If it lacks that report, the assistant citation stays a manual observation and does not become a Google visibility metric.

If the stakeholder proposes `llms.txt` as the bridge between the surfaces, the request goes to [[llms.txt Caveat Note]]. The Google caveat comes from `g-ai-opt-guide` and `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`.

## Surface Confusion Traps

- Google AI Mode product scale from `blog-io2026` is mistaken for a target site's opportunity.
- A ChatGPT citation is used to justify a Google ranking recommendation, beyond `seoclarity-chatgpt`.
- Google-Extended crawler control is filed as a Search citation tactic, conflicting with `g-common-crawlers`.
- A Search Console Google report is expected to explain non-Google assistant referrals, which `g-genai-reports` does not cover.

## Formatting Matrix Wiring

[[Platform Output Formatting Matrix]] consumes this map when output packaging raises "AI-ready format" claims. It needs the surface name, supported source IDs, and a clear note on whether special files or markup are unsupported.

The matrix should receive a platform-neutral caveat: preserve headings, visible citations, and metadata, but do not add a CMS-specific AI promise unless a surface-specific source supports it.

## Routing Record Fields

For Google Search rows, cite `g-ai-features` or `g-ai-opt-guide` before any formatting recommendation.

For AI Mode rows, attach `blog-io2026` only to product context, not page demand.

For assistant rows, keep `seoclarity-chatgpt` observations outside Google proof language.

For crawler-control rows, separate `g-common-crawlers` from llms.txt and preview-control claims.

## Assistant Answer Surface Map Output

The output is a routing decision, not a full optimization plan. It should tell the reviewer which sibling note to use, which evidence tier applies, and which claim must be removed or narrowed.
