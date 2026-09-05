---
type: spoke
title: "Media QA For Blog Posts"
domain: "Blog Media"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [media, images, audio, charts, active]
---

# Media QA For Blog Posts

## Media QA For Blog Posts Review Scope

Media QA For Blog Posts is the final gate before a post is marked ready from the media side. It gathers the decisions from [[Image Selection Rules]], [[Alt Text Standards]], [[Chart Source Requirements]], [[Data Visualization Review]], [[Media Accessibility Checklist]], [[Generated Media Disclosure Notes]], [[Audio Summary Rules]], and [[VideoObject Checklist]] into one pass/fail record.

The source set is intentionally practical. `g-google-images` and `g-video` govern image and video search boundaries. `g-ai-opt-guide` blocks AI-only claims about hidden files or special markup. `schema-full` and `g-intro-sd` keep vocabulary and structured-data use tied to visible content. QA does not guarantee ranking, rich results, accessibility compliance, or AI citation.

### Inputs Required Before Review

- Final media inventory with filenames or URLs.
- Asset job for each media item.
- Rights, provenance, source, or generation record.
- Alt text, captions, transcripts, chart notes, or empty-alt decisions.
- Schema proposal when media markup exists.
- Blocked-claim list for charts, screenshots, videos, and generated assets.

## Media QA For Blog Posts Pass Fail Table

| QA check | Evidence | Severity | Owner | Fix status |
|---|---|---|---|---|
| Asset earns placement | Image request or media brief | Advisory unless section depends on it | Editor | Remove decorative filler or revise section. |
| Source and rights are recorded | Asset source, license, consent, generation note | Blocker | Media owner | Hold publication until source packet exists. |
| Accessibility path is complete | Alt, empty alt, transcript, caption, or table | Blocker for informational assets | Accessibility reviewer | Repair through [[Media Accessibility Checklist]]. |
| Chart claim is provable | Dataset and method note | Blocker | Data reviewer | Complete [[Chart Source Requirements]]. |
| Structured data matches visible content | JSON-LD draft and page preview | Blocker when markup is present | Technical SEO | Reconcile through [[Blog Schema Stack]]. |
| AI or crawler claim is bounded | Source ID and note link | Advisory or blocker by claim strength | GEO reviewer | Route to [[AI Citation Mechanics]] or remove. |
| Generated media is disclosed | Prompt log, edit note, replacement decision | Blocker when asset may mislead | Editor | Complete [[Generated Media Disclosure Notes]]. |
| Video package is aligned | Player, thumbnail, title, transcript | Blocker when VideoObject exists | Video owner | Complete [[VideoObject Checklist]]. |
| Discovery URL is stable | Canonical URL and media file path | Major for indexable media | Technical SEO | Check [[Image Sitemap Notes]]. |

## Media QA For Blog Posts Handoff Rules

1. Run media QA after copy freeze, not before the article structure settles.
2. Mark each asset pass, revise, remove, or blocked.
3. Keep the owner and next action in the QA table until fixed.
4. Reject ready status if any blocker remains.
5. Reopen QA after a source date, screenshot, chart, video, or schema field changes.

## Media QA For Blog Posts Source IDs

Use `g-google-images`, `g-video`, `g-ai-opt-guide`, `schema-full`, and `g-intro-sd` for the QA gate. The extra structured-data source makes this note broader than individual alt or accessibility checks and prevents one generic bundle from standing in for final QA.

## Launch Gate Walkthrough

A post reaches QA with a generated hero, one chart, and a product demo video.
The hero passes only after disclosure and alt status are recorded.
The chart blocks publication because the source packet lacks retrieval date.
The video blocks schema handoff until thumbnail and transcript match.
`g-intro-sd` applies when JSON-LD describes visible media.
`g-ai-opt-guide` removes a note claiming special AI-media treatment.
After fixes, QA records three pass states and one removed asset.

## QA Failure Patterns

- A late image swap reopens alt, rights, and OG crop checks.
- A reused schema block can describe media from an older post.
- A CDN path change can break sitemap and schema image URLs.
- A chart source correction changes both caption and audio variant.
- A decorative image with unknown rights is removed, not deferred.

## Validation Deliverable Wire

[[SEO Check Validation Checklist]] consumes the final media QA row set.
Inputs are image list, schema draft, preview metadata, and blocker status.
Expected output is final pass, fix, or blocked before publication.
`g-google-images` covers image checks; `g-video` covers video checks.

## Media QA For Blog Posts Completion Rule

The article can leave this gate only when every media item has a reader job, provenance, accessibility handling, and schema alignment where relevant. If a media asset is nice to have but unresolved, remove it instead of carrying an open risk into publication.
