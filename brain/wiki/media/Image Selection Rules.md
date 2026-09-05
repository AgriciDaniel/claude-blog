---
type: spoke
title: "Image Selection Rules"
domain: "Blog Media"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [media, images, audio, charts, active]
---

# Image Selection Rules

## Image Selection Rules Rule Scope

Image Selection Rules chooses whether an image earns space in the article. A good image answers, demonstrates, compares, proves, or orients. A weak image decorates a thin section, repeats the headline visually, or creates trust without evidence. Use this note before writing alt text, requesting generated assets, or adding image markup.

`g-google-images` is the core evidence source for image quality and image discovery context. `schema-full` helps name image-related vocabulary, but [[Blog Schema Stack]] decides whether markup belongs on the page. `g-ai-opt-guide` keeps image selection tied to normal helpful content instead of AI-only artifacts. `g-common-crawlers` is included because Google-Extended questions may appear during media rights review; it should not be framed as a ranking lever.

### Allowed Actions And Disallowed Actions

- Allowed: choose a screenshot that proves a workflow step.
- Allowed: choose a chart when the article has dated data.
- Allowed: use a diagram when the reader needs relationships.
- Disallowed: add a stock image to mask missing substance.
- Disallowed: pick an AI-generated image as evidence of a real product state.
- Disallowed: treat crawler controls as a substitute for media licensing.

## Image Selection Rules Rule Table

| Rule | Source basis | Applies to | Enforcement | Exception path |
|---|---|---|---|---|
| Image must have a reader job | `g-google-images` | Hero and inline images | Editor records answer, demo, compare, prove, or orient | Decorative only if marked decorative in [[Alt Text Standards]]. |
| Schema follows visible media | `schema-full` | ImageObject or related vocabulary | Schema reviewer confirms visible content | No markup when the asset adds no useful detail. |
| AI-only media files are not a Google requirement | `g-ai-opt-guide` | AI citation and GEO claims | GEO reviewer removes hidden-file rationale | Non-Google systems need separate sources. |
| Google-Extended is not image-selection proof | `g-common-crawlers` | Robots and training opt-out discussions | Technical reviewer keeps crawler policy separate | Legal or policy review can add a new source. |
| Screenshot must prove a specific state | `g-google-images`, `g-ai-opt-guide` | Product or workflow articles | Capture date and version are recorded | Use diagram when real state is unavailable. |
| Diagram must clarify relationships | `g-google-images`, `schema-full` | Concept explainers and process posts | Section owner names the relationship | Remove if prose already explains it clearly. |
| Photo must not imply unverified endorsement | `g-google-images`, `g-common-crawlers` | People, products, venues, and events | Rights and claim boundary are recorded | Route consent questions outside this vault. |

## Image Selection Rules Selection Procedure

1. Write the sentence the image must help the reader understand.
2. Pick the minimum asset type that performs that job: screenshot, chart, diagram, photo, or thumbnail.
3. Verify rights, provenance, and claim source before requesting final art.
4. Send accessibility instructions to [[Alt Text Standards]].
5. Reject the asset if the section remains weak without it.

## Image Selection Rules QA Notes

For product visuals, require the pictured version, date, and claim boundary. For screenshots, capture the interface state instead of recreating it from memory. For charts, open [[Chart Source Requirements]] before approving composition. For generated assets, open [[Generated Media Disclosure Notes]] before distribution.

## Migration Diagram Choice

A technical blog section explains moving from spreadsheet tracking to a CMS queue.
Before selection, the requester proposes a stock laptop photo.
The asset is rejected because it does not answer, compare, or prove anything.
Under `g-google-images`, the chosen image must support image context and usefulness.
The replacement is a simple flow diagram with three named states.
Alt text goes to [[Alt Text Standards]] after the relationship is approved.
Schema review waits because `schema-full` never proves image usefulness alone.

## Selection Errors Seen In Review

- A stock handshaking image can imply endorsement or partnership.
- A demo screenshot cannot prove production behavior without context.
- An AI-generated product shot cannot replace a real product-state source.
- A crawler-control note cannot settle copyright or licensing questions.
- A hero image is removed when the section works better without it.

## Image Brief Wire

[[Blog Image Brief And Disclosure Checklist]] consumes the image selection result.
Inputs are article section, asset job, source basis, rights status, and owner.
Expected output is approve, revise, reject, or send for disclosure review.
`g-common-crawlers` only explains Google-Extended, not media rights.

## Image Selection Rules Source IDs

Use `g-google-images`, `g-ai-opt-guide`, `schema-full`, and `g-common-crawlers`. The source set does not decide copyright, consent, model policy, or brand suitability.
