---
type: spoke
title: "Generated Media Disclosure Notes"
domain: "Blog Media"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [media, images, audio, charts, active]
---

# Generated Media Disclosure Notes

## Generated Media Disclosure Notes Asset Job

Generated Media Disclosure Notes decides whether synthetic or heavily edited media needs a reader-facing disclosure, a provenance record, or replacement with a primary asset. It covers generated illustrations, edited screenshots, voice clips, synthetic video scenes, chart styling, thumbnails, and mockups. It does not approve a model, vendor, or legal policy by itself.

The assigned evidence set is search and schema oriented. `g-google-images` and `g-video` cover image and video handling. `schema-full` provides vocabulary context when media metadata is discussed. `g-ai-opt-guide` prevents the workflow from inventing Google-only AI disclosure files or hidden schema. Model-specific claims require a separate dated source in [[Research Pack Index]].

### Licensing, Accessibility, And Provenance Requirements

- Licensing: record who owns the input assets and intended output rights.
- Accessibility: write alt text, captions, labels, or transcripts according to the asset type.
- Provenance: record creation tool, edit summary, source inputs, and reviewer.
- Replacement: use a real screenshot, photo, or source chart when the visual proves a factual state.

## Generated Media Disclosure Notes Media Table

| Asset type | Disclosure trigger | Provenance record | Accessibility item | Replacement rule | QA state |
|---|---|---|---|---|---|
| Concept illustration | Could be mistaken for a real event or product | Tool, date, prompt summary | Alt explains concept, not model output | Replace if article needs documentary proof | Editorial review |
| Edited screenshot | UI state was changed, redacted, or composited | Original capture, edits, approver | Alt names edited status when material | Replace with real dated screenshot for evidence | Factcheck required |
| Synthetic voice | Voice, speaker, or narration may imply real endorsement | Script, voice source, consent note | Transcript and article link | Replace if testimonial or expert quote is implied | Approval required |
| Generated chart styling | Data is real but design was generated | Dataset, chart transform, tool | Caption gives source and date | Replace if data cannot be traced | Data review |
| Video mockup | Scene is illustrative rather than captured | Script, storyboard, generation method | Captions or transcript | Replace when page discusses actual product behavior | Video review |
| Background extension | Photo edges or setting were synthesized | Original asset, mask, edit reason | Alt avoids invented scene details | Replace if location or event proof matters | Media owner review |
| Synthetic expert portrait | Person did not sit for the image | Identity basis, consent decision, prompt note | Caption blocks implied endorsement | Replace with real author photo for E-E-A-T claims | Editor review |
| AI thumbnail text | Generated frame carries a headline or number | Prompt, final frame, transcript comparison | Text also appears in page copy | Replace if the number is unsupported | Video review |

## Generated Media Disclosure Notes Review Procedure

1. Label the asset as evidentiary, illustrative, decorative, or distribution-only.
2. If evidentiary, require a primary asset instead of generated media.
3. If illustrative, record provenance and decide whether a visible disclosure is needed.
4. Check the asset against [[Alt Text Standards]] and [[Visual Claim Review]].
5. Block publication when rights, consent, or source inputs are unclear.

## Mock Product Hero Decision

A SaaS article requests a generated dashboard hero for a feature announcement.
Before review, the image resembles a working product screen.
That can imply product behavior not visible in the article.
`g-google-images` supports image context, not product-state proof.
The approved version becomes an abstract workflow illustration.
The caption says "illustrative workflow concept" when confusion is likely.
A real dated screenshot replaces it when the article proves a UI state.
No hidden AI-disclosure file is created under `g-ai-opt-guide`.

## Disclosure Failure Paths

- A small retouch can become factual when it changes a button state.
- A synthetic voice may imply consent or endorsement absent from sources.
- Generated chart styling cannot rescue an untraceable dataset.
- A mock video cannot support a product availability claim.
- Schema fields must not invent creator, location, or event provenance.

## Image Brief Wire

[[Blog Image Brief And Disclosure Checklist]] consumes the disclosure decision.
Inputs are prompt summary, tool date, source assets, edits, and human approver.
Expected output is disclose, replace, approve, or block with owner.
`schema-full` is vocabulary context only; model-specific policy needs new sources.

## Generated Media Disclosure Notes Source IDs

This note cites `g-google-images`, `g-video`, `g-ai-opt-guide`, and `schema-full`. It intentionally does not make vendor-model availability claims. If a later release needs model shutdown dates, watermark behavior, or platform disclosure policy, add those sources to the ledger before using them.

## Generated Media Disclosure Notes Handoff

Pass the asset only when a human owner can say what was generated, what was edited, what source material was used, and why the asset is safe for the article's claim. Send unresolved rights and consent questions outside the vault workflow.
