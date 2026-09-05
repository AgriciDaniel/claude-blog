---
type: spoke
title: "E-E-A-T Trust Subscore"
domain: "Blog Quality"
status: active
created: 2026-07-06
updated: 2026-07-10
tags: [quality, scorecard, active]
confidence: advisory
related:
  - "[[Blog Quality Score]]"
  - "[[E-E-A-T for Blog Content]]"
  - "[[Quality Review Evidence Log]]"
  - "[[Recommendation Confidence Labels]]"
---

# E-E-A-T Trust Subscore

## Trust Scoring Assignment

This 15 point spoke scores whether the draft makes experience, expertise, accountability, source quality, and sensitivity visible enough for a reviewer to trust the recommendation. `g-helpful-content` ties helpful content review to E-E-A-T style questions, `g-qrg-full` supplies the full rater-guideline frame, `g-update-2025-09-11-qrg-update-sept-2025` flags current AI Overview and YMYL examples, and `nng-editorial-heuristics` supports transparent review feedback.

## Trust Signals This Note Scores

- Author, reviewer, or owner transparency for the topic.
- Evidence that the writer has used, tested, researched, or responsibly synthesized the subject.
- Source quality for current Search, AI, market, legal, medical, financial, or reputation claims.
- Clear escalation when a topic is YMYL-adjacent or could materially affect a reader.

## Escalations This Score Delegates

Detailed E-E-A-T doctrine belongs in [[E-E-A-T for Blog Content]]. Final pass or block status belongs in [[Delivery Contract Gate]]. If the issue is a missing citation rather than a trust judgment, route it to [[Quality Review Evidence Log]]. If the issue is recommendation language, use [[Recommendation Confidence Labels]].

## E-E-A-T Evidence Matrix

| Trust criterion | Points | Required proof | Blocking failure |
|---|---:|---|---|
| Experience evidence | 3 | First-hand use, case context, expert interview, or original research is visible. | The piece gives advice without showing how it knows. |
| Expertise fit | 3 | Author or reviewer background matches topic risk. | Sensitive advice lacks qualified review. |
| Transparency | 3 | Dates, authorship, AI assistance, conflicts, and limitations are disclosed when relevant. | Material conflict or generated assistance is hidden. |
| Source quality | 4 | Important claims use official, primary, or clearly caveated sources. | Roundups or uncited summaries support core advice. |
| YMYL and reputation risk | 2 | Escalation path is named for high-sensitivity content. | A risky recommendation ships with no specialist review. |

## Weighting, Proof, And Blockers

Do not award trust points for a byline alone. The point value comes from evidence that a reader and reviewer can inspect. A current market statistic gets no trust credit unless its methodology and limitation are visible. A recommendation that promises AI citations, rankings, or traffic fails the trust row even when the sources are otherwise good.

## Trust Review Runbook

1. Classify the topic as ordinary, sensitive, or YMYL-adjacent.
2. Check whether the author, reviewer, and source stack fit that risk.
3. Score the five matrix rows and name the weakest row.
4. Apply a blocked label when risk exceeds available evidence.
5. Add the decision to [[Quality Review Evidence Log]].

## Trust Triage Example

Draft topic: choosing SEO software for a clinic blog.
The topic is reputation and YMYL-adjacent.
Author note: "Reviewed by content team."
That note does not prove expertise fit.
Add reviewer credentials or mark trust reduced.
Use `g-qrg-full` for quality-review vocabulary.
Use `g-update-2025-09-11-qrg-update-sept-2025` for current YMYL framing.
If the article discloses AI assistance,
score transparency against `g-helpful-content`.
If the disclosure is hidden in footer text,
treat it as weak accountability evidence.

## Trust Failures That Look Acceptable

- A named byline lacks topic-relevant reviewer support.
- A sensitive recommendation uses only vendor documentation.
- A market study appears without method limits.
- AI assistance is mentioned after the recommendation.
- A conflict disclosure omits the recommended product.

## Audit Wiring

[[Blog Analyzer Score Report]] consumes this trust subscore.
Inputs sent: topic risk, author proof, reviewer proof, source quality.
Also send conflict notes and sensitivity escalation.
Expected output: trust severity and report recommendation.
[[Factcheck Claim Register]] consumes risky claim details.
It expects source ID, verdict label, confidence, and refresh date.
