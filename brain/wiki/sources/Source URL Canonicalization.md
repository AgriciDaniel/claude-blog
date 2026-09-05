---
type: spoke
title: "Source URL Canonicalization"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [sources, research-pack, active]
domain: "Source Evidence"
confidence: verified
related:
  - "[[Research Pack Index]]"
  - "[[Source Ledger Reading Guide]]"
  - "[[Claim To Source Mapping]]"
  - "[[Evidence Gap Register]]"
  - "[[AI Citation Mechanics]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
---

# Source URL Canonicalization

## Canonical URL Job

This spoke keeps source URLs stable across frontmatter, source tables, and body citations. A canonical URL is the ledger URL for the specific claim source, not a nearby page, redirect target guessed by memory, or generic Google documentation bundle.

URL discipline matters because Google documentation often separates a concept page from a changelog event. The AI optimization guide can be both the current guidance page for `g-ai-opt-guide` and the location of the llms.txt clarification source ID. Those IDs can share a URL while still carrying different claim roles.

## URL Forms This Note Owns

- Ledger URLs copied into `source_urls` frontmatter.
- Body-table URLs attached to source IDs.
- Anchor URLs when a changelog section is the claim source.
- Duplicate URLs that represent different source IDs on the same page.

## URL Forms Routed Elsewhere

- Raw snapshot storage and hashes belong outside this folder.
- Redirect investigation belongs in [[Evidence Gap Register]] when the ledger URL no longer resolves cleanly.
- Claim confidence belongs in [[Source Confidence Labels]].

## Source URL Canonicalization Source Table

| Source ID | Canonical URL | Date in ledger | Claim coverage | URL handling rule | Limitation |
|---|---|---:|---|---|---|
| `g-helpful-content` | https://developers.google.com/search/docs/fundamentals/creating-helpful-content | last updated 2025-12-10 | Helpful content and E-E-A-T framing. | Use the page URL without adding a campaign query or copied SERP URL. | Does not support schema or AI-specific claims. |
| `g-intro-sd` | https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data | last updated 2025-12-10 | General structured data guidance. | Keep this separate from Search Gallery and feature-specific pages. | Does not confirm a particular rich result type. |
| `g-search-gallery` | https://developers.google.com/search/docs/appearance/structured-data/search-gallery | last updated 2026-07-01 | Current Google-supported rich-result inventory. | Use the gallery URL for support checks, not a generic schema page. | Does not provide implementation syntax for every type. |
| `g-faqpage-sd` | https://developers.google.com/search/updates#deprecating-the-faq-rich-result-feature | retrieved 2026-07-09 | FAQ rich-result retirement. | Keep the changelog anchor when citing retirement state. | Does not replace visible-content guidance. |
| `g-ai-opt-guide` | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide | last updated 2026-06-15 | Google Search AI feature guidance. | Use the canonical guide URL for Google AI Search guidance. | Does not cover non-Google assistants. |
| `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide | last updated 2026-06-15 | llms.txt clarification for Google Search. | It may share the guide URL, but keep the distinct source ID in tables. | Does not decide whether other crawlers use llms.txt. |

## Source ID, URL, Date, Claim Coverage, And Limitation

When two source IDs share a URL, do not merge them in prose. The ID explains the claim role. The URL explains where reviewers inspect it. The date explains whether the page was current. The limitation explains what cannot be copied into another note.

## Source URL Canonicalization Procedure

1. Copy URLs from `references/source-ledger.json`, not from a browser search result.
2. Keep only source URLs that appear in the body table or directly support the note.
3. Remove tracking parameters, fragments without review value, and duplicate generic bundles.
4. Preserve distinct source IDs even when the canonical URL is shared.
5. Open [[Evidence Gap Register]] if a redirect, date mismatch, or missing raw snapshot changes source confidence.

## URL Collision Example

A schema reviewer pastes the structured-data introduction for FAQ retirement.
The canonical URL should be `g-faqpage-sd` with its changelog anchor.
Use `g-intro-sd` only for general JSON-LD and visible-content guidance.
Failure appears when two Google URLs are treated as interchangeable.
Another failure is stripping the only useful anchor from an update URL.
[[Schema Generation Output Contract]] consumes the canonical URL choice.
Inputs provided: source ID, canonical URL, anchor rule, and limitation.
Expected output: schema warning that cites the right source.

## Related

- [[Research Pack Index]]
- [[Source Ledger Reading Guide]]
- [[Claim To Source Mapping]]
- [[Evidence Gap Register]]
- [[AI Citation Mechanics]]
