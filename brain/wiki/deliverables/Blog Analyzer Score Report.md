---
type: deliverable
title: "Blog Analyzer Score Report"
domain: "Blog Quality"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, analyzer, score-report, active]
---

# Blog Analyzer Score Report

## Report Purpose For The 100 Point Review

The analyzer report converts an inspected blog post into a 100-point advisory score across content quality, SEO and intent, E-E-A-T, technical health, and AI citation readiness. It must show the evidence behind the score instead of presenting a grade as authority. The scoring model links to [[Blog Quality Score]] and uses `g-helpful-content` for people-first content, `g-qrg-full` for quality-evaluator concepts, `wd-vitals` for Core Web Vitals terminology, and `g-ai-opt-guide` for AI feature boundaries.

### Audience, Scope, And Source Inputs

The audience is the content owner deciding whether to publish, revise, or block. Inputs are the article URL or draft, target keyword, source pack, author evidence, technical crawl notes, schema output, and any GSC or analytics files provided by the operator.

### Findings This Report Must Not Overclaim

The report must not promise ranking recovery, AI Overview citation, or traffic lift. Technical issues can be marked as observed, inferred, or missing-data. QRG evidence is a quality lens through [[E-E-A-T for Blog Content]], not a numeric Google ranking formula.

## Blog Analyzer Score Report Findings Table

| Report section | Input checked | Evidence source | Severity scale | Delivery status |
|---|---|---|---|---|
| Content usefulness | Draft, intro, answer blocks, originality notes | `g-helpful-content` and source pack | blocker, major, minor, pass | Included in content subscore |
| E-E-A-T and trust | Author, reviewer, source quality, YMYL flags | `g-qrg-full` plus [[E-E-A-T for Blog Content]] | blocker, major, minor, pass | Included in trust subscore |
| Technical experience | Field data, lab notes, crawl findings | `wd-vitals` where performance evidence exists | major, minor, pass, unavailable | Mark unavailable if data is missing |
| AI citation readiness | Passage clarity, caveats, AI guidance claims | `g-ai-opt-guide` and [[AI Citation Mechanics]] | blocker, advisory, pass | Never scored as guaranteed inclusion |
| Recommendation queue | Issue, fix, owner, due date | Source IDs and observed page evidence | blocker, queued, accepted, deferred | Delivered as action list |

## Blog Analyzer Score Report Delivery Procedure

1. Start with the score and release decision, then show the weakest category and blocker list.
2. Attach evidence rows for every major deduction so the owner can reproduce the judgment.
3. Label missing measurements as missing instead of estimating performance.
4. Close with owner, due date, and retest trigger for each recommended fix.

## Source IDs Used

Analyzer scoring uses `g-helpful-content`, `g-qrg-full`, `wd-vitals`, and `g-ai-opt-guide`; the report cites the ID nearest to each scored claim.
