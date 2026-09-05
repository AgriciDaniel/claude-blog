---
type: spoke
title: "QRG Revision Watch"
domain: "Google Update Monitoring"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [monitoring, google-updates, active]
source_urls:
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
  - "https://services.google.com/fh/files/misc/hsw-sqrg.pdf"
---

# QRG Revision Watch

## QRG Revision Watch Distinct Job

This spoke watches Search Quality Rater Guideline revisions and maps them to blog quality checks. It is a quality-review input, not a ranking-factor claim. The full guideline PDF is the authority for rater-guideline claims; the short overview deck is useful only as an orientation source and must not replace the full PDF.

## Inputs Specific To QRG Revision Watch

- Full QRG source record and dated local update-ledger entries.
- Revision date, changed section, and affected review lane.
- Quality-check destination in [[E-E-A-T for Blog Content]] or a related review note.
- Caveat that raters evaluate examples and guidance, not direct ranking-system inputs.

## Decisions QRG Revision Watch Must Record

The watch decides whether a QRG revision changes internal review questions. `g-update-2025-01-23-qrg-update-jan-2025` affects how the brain reviews generated, copied, and filler main content. `g-update-2025-09-11-qrg-update-sept-2025` affects AI Overview examples and YMYL-adjacent framing. `g-qrg-full` owns the full guideline source. `g-qrg` is only the overview deck and should never carry detailed section claims by itself.

## QRG Revision Watch Update Entry Table

| Revision decision | Required input | Source IDs | Evidence state | Owner | Next action |
|---|---|---|---|---|---|
| Use full PDF for detailed claims | Verify the full guideline source, not only the overview deck | `g-qrg-full`, `g-qrg` | CONFIRMED source hierarchy | Quality reviewer | Route full-section claims to the full PDF. |
| January 2025 AI and spam examples | Record changed quality questions for generated or copied content | `g-update-2025-01-23-qrg-update-jan-2025` | CONFIRMED | Editorial lead | Refresh checks for copied, paraphrased, or low-value generated main content. |
| September 2025 AI Overview examples | Map examples to answer quality and YMYL sensitivity | `g-update-2025-09-11-qrg-update-sept-2025` | CONFIRMED | Quality reviewer | Update AI-answer review prompts without promising ranking effect. |
| Non-QRG event boundary | Dashboard core or spam updates appear with no QRG file change | `g-ranking-history`, `g-status-dashboard`, `g-update-2026-05-21-may-2026-core-update`, `g-update-2026-06-24-june-2026-spam-update` | CONFIRMED different lane | Monitoring owner | Leave QRG checks unchanged and route event work elsewhere. |
| No newer QRG as of this check | Confirm source-ledger status on 2026-07-09 | `g-qrg-full` | CONFIRMED current local state | Monitoring owner | Recheck next month and before release packaging. |
| YMYL-adjacent brief flag | Check whether the topic needs heightened trust review | `g-qrg-full`, `g-update-2025-09-11-qrg-update-sept-2025` | CONFIRMED for guideline text | E-E-A-T reviewer | Route sensitive topics to trust scoring. |
| Generated-content guard | Page uses AI, paraphrasing, or copied main content patterns | `g-update-2025-01-23-qrg-update-jan-2025` | CONFIRMED quality context | Reviewer | Require originality and source evidence before pass. |

## QRG Quality Mapping

Use QRG revisions to adjust review questions, not to force a content formula. A blog audit may add checks for experience evidence, author identity, source quality, YMYL sensitivity, or generated-content disclosure. It should not claim that adding a section heading or a biography creates a ranking gain. When a revision touches AI examples, link the interpretation to [[AI Citation Mechanics]] only if the claim concerns answer extraction or citation surfaces.

## QRG Revision Watch Operating Procedure

1. Confirm the latest full QRG date and compare it with the local source-ledger row.
2. Identify the changed sections and translate them into reviewer questions.
3. Update only the affected quality checks, leaving ranking-impact analysis to [[Update Impact Review]].
4. If the source is unchanged, write a dated no-change note for the refresh log.

## QRG Review Example

A draft about medical insurance cites AI-generated summaries without author review.
The watch uses `g-qrg-full` for the quality-evaluator source.
It uses `g-update-2025-09-11-qrg-update-sept-2025` for YMYL-adjacent framing.
It uses `g-update-2025-01-23-qrg-update-jan-2025` when copied or filler main content appears.
The recommendation is a trust review, not a ranking-causation claim.
The consumer is [[Blog Analyzer Score Report]].
Inputs passed are affected topic, QRG source IDs, trust concern, caveat, and owner.
The report should output score impact, evidence row, blocker status, and retest trigger.

## QRG Watch Failure Modes

- The 36-page overview `g-qrg` cannot carry detailed section claims without `g-qrg-full`.
- A QRG revision does not prove a core-update impact in [[Update Impact Review]].
- AI Overview examples do not guarantee AI citation inclusion.
- Treating author bio additions as automatic trust repair overstates `g-qrg-full`.

## Related

- [[Google Algorithm Update Ledger]]
- [[E-E-A-T for Blog Content]]
- [[AI Citation Mechanics]]
- [[Monthly Source Refresh]]
