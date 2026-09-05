---
type: deliverable
title: "Full Site Blog Audit Report"
domain: "Blog Auditing"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, site-audit, blog-audit, active]
---

# Full Site Blog Audit Report

## Full Site Blog Audit Report Purpose

The full site audit summarizes the health of a blog inventory across quality scores, stale content, orphan pages, cannibalization, AI citation readiness, technical experience, and action priority. It is a decision report for operators, not a crawler dump. Use [[Blog Quality Score]] for scoring definitions and [[Google Data Integrations]] for property data.

### Audience Scope And Source Inputs

The audience is the content lead, SEO owner, and implementation team. Inputs include URL inventory, crawl notes, GSC export, source inventory, author data, schema observations, Core Web Vitals evidence, and current content priorities. `g-helpful-content` anchors quality recommendations, while `g-gsc-api` supports query-level evidence where access exists.

### Findings This Report Must Not Overclaim

The audit must not infer algorithmic cause from timing alone, score unsupported claims as pass, or treat lab-only performance notes as field outcomes. `wd-vitals` defines LCP, INP, CLS, and measurement distinctions. `g-qrg-full` can guide trust review but should not be presented as a direct ranking-factor formula.

## Full Site Blog Audit Report Findings Table

| Audit section | Input source | Evidence required | Severity level | Recommendation format | Delivery status |
|---|---|---|---|---|---|
| Inventory quality | URL list and score sample | `g-helpful-content` and source checks | blocker, major, minor | Keep, improve, merge, prune, monitor | draft or final |
| Staleness and decay | Modified dates, source age, GSC trend | Source dates and query data | major or minor | Refresh with evidence owner | draft or final |
| Cannibalization | Query overlap and intent map | GSC data and SERP review | blocker to minor | Merge, differentiate, canonicalize, or leave | draft or final |
| AI citation readiness | Passage review and AI caveats | [[AI Citation Mechanics]] evidence | advisory or blocker | Improve passage, caveat, or defer | draft or final |
| Technical experience | CWV, crawl, schema notes | `wd-vitals` and technical observations | blocker, major, minor | Fix, monitor, or mark unavailable | draft or final |
| Priority queue | Impact, effort, risk, owner | Evidence and rollback trigger | high, medium, low | Action card with due date | draft or final |

## Delivery Procedure For Audit Reports

1. Present the executive decision queue before detailed findings.
2. Keep every page-level recommendation tied to evidence, owner, confidence, and rollback trigger.
3. Separate missing data from passing data so the team can decide whether to collect more evidence.

## Source IDs Used

Full site audits use `g-helpful-content`, `g-qrg-full`, `g-gsc-api`, and `wd-vitals`.
