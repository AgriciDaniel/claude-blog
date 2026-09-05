---
type: deliverable
title: "SEO Check Validation Checklist"
domain: "Technical SEO"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, seo-check, validation, active]
---

# SEO Check Validation Checklist

## Post Writing Validation Scope

This checklist is the final SEO gate after writing and before publication. It checks titles, meta descriptions, headings, internal links, canonicals, Open Graph data, schema, image handling, and avoidable technical blockers. It is not a strategy document and should not reopen the article premise unless a blocker proves the draft cannot be safely shipped.

### Checks Unique To This Gate

The gate validates implementation details: title uniqueness, meta fit, H1 alignment, heading order, canonical tag, indexability note, OG title and image, structured-data presence, image alt text, and internal-link sanity. `g-canonical` supports canonical review. `g-intro-sd` supports the visible-content standard for structured data, and `g-google-images` supports image quality and alt text requirements.

### Inputs Required Before Review

The reviewer needs final copy, target URL, target canonical, source pack, image list, schema draft, internal links, and preview metadata. Helpful-content guidance from `g-helpful-content` remains the guardrail against shipping technically tidy but thin content.

## SEO Check Validation Checklist Pass Fail Table

| Check | Pass condition | Evidence captured | Severity | Fix owner | Status |
|---|---|---|---|---|---|
| Title and meta | Describes the page and matches intent | SERP preview or CMS fields | major if misleading | Editor | pass, fix, or blocked |
| Heading structure | One H1 and ordered H2/H3 jobs | Rendered page or markdown | minor to major | Writer | pass, fix, or blocked |
| Canonical | Self or approved canonical target | HTML tag and `g-canonical` review | blocker if wrong target | Technical SEO | pass, fix, or blocked |
| Internal links | Useful anchors to relevant pages | Link list and target check | minor to major | Strategist | pass, fix, or blocked |
| Structured data | Describes visible content only | Schema validator note and `g-intro-sd` | blocker if fabricated | Technical SEO | pass, fix, or blocked |
| Images and OG | Useful alt text, stable asset, preview fit | Image list and `g-google-images` | major if inaccessible | Media owner | pass, fix, or blocked |

## Handoff Rules After Fixes

1. Block publication when canonical, schema, source, or indexability evidence is unknown.
2. Route content usefulness issues back to the editor instead of hiding them as SEO tweaks.
3. Preserve the final checklist with owner and fix state for later audits.

## Source IDs Used

SEO validation uses `g-helpful-content`, `g-canonical`, `g-intro-sd`, and `g-google-images`.
