---
type: deliverable
title: "Blog Image Brief And Disclosure Checklist"
domain: "Blog Media"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, images, disclosure, active]
---

# Blog Image Brief And Disclosure Checklist

## Image Brief Review Scope

This checklist governs hero images, inline images, OG assets, generated visuals, licensing, model disclosure, and accessibility before a blog post ships. It belongs with [[Images Audio and Charts]] and links schema decisions to [[Blog Schema Stack]]. The gate blocks images that decorate weak claims, hide licensing gaps, or misrepresent generated content.

### Checks Unique To This Gate

The reviewer checks asset purpose, rights or license, source URL, generated-image prompt, model or vendor disclosure, human review, alt text, caption, file naming, dimensions, OG crop, and whether structured data describes only visible assets. `g-google-images` supports image quality and alt text. `schema-full` is used when image entities need vocabulary support.

### Inputs Required Before Review

Inputs are final article section, image file or prompt, intended placement, license proof, model disclosure if generated, alt text, caption, and schema request. `g-ai-opt-guide` keeps AI-related recommendations grounded in Google Search guidance. `g-common-crawlers` can explain Google-Extended as an AI-training control, not as a ranking factor.

## Blog Image Brief And Disclosure Checklist Pass Fail Table

| Image check | Pass condition | Evidence | Severity | Fix owner | Fix status |
|---|---|---|---|---|---|
| Asset purpose | Image explains or supports a section | Placement note | major if decorative only | Editor | open, fixed, or blocked |
| Rights and provenance | License, owned asset, or generation record exists | Asset source or prompt log | blocker if unknown | Media owner | open, fixed, or blocked |
| Disclosure | Generated or edited asset is labeled where required by policy | Model and review note | major to blocker | Editor | open, fixed, or blocked |
| Accessibility | Useful alt text and caption when needed | Alt and caption fields | major if missing meaning | Media owner | open, fixed, or blocked |
| OG crop | Preview remains legible and relevant | Social preview | minor to major | Designer | open, fixed, or blocked |
| Schema fit | Markup describes visible image only | Schema review | blocker if fabricated | Technical SEO | open, fixed, or blocked |

## Handoff Rules For Media Approval

1. Block publication if rights, provenance, or generated-asset disclosure is unresolved.
2. Keep prompts and model notes with the media brief, not hidden in draft comments.
3. Send schema requests to technical review only after the visible asset is approved.

## Source IDs Used

Image review uses `g-google-images`, `g-ai-opt-guide`, `g-common-crawlers`, and `schema-full`.
