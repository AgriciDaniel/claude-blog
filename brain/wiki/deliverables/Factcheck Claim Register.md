---
type: deliverable
title: "Factcheck Claim Register"
domain: "Research Quality"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, factcheck, claim-register, active]
---

# Factcheck Claim Register

## Factcheck Claim Register Scope

This register tracks claims that need verification before they appear in briefs, drafts, reports, or repurposed assets. It records the claim, source ID, evidence tier, claim-ledger verdict, confidence, owner, status, refresh date, and rollback trigger. It is the operating layer for the verdict discipline described in `references/claim-ledger.md`.

### Claims Captured Here

Capture statistics, Google policy statements, AI citation claims, schema eligibility statements, E-E-A-T or QRG interpretations, and market-study summaries. `g-helpful-content` supports content-quality claims. `g-qrg-full` supports quality-evaluator language with careful scope, and `g-ai-opt-guide` supports Google AI Search guidance.

### Claims Routed Elsewhere

Routine grammar edits, brand voice choices, and unsupported brainstorm ideas do not belong in the register. Technical implementation checks go to [[SEO Check Validation Checklist]] once that note exists. AI citation caveats route to [[AI Citation Mechanics]], and source discovery routes to [[Research Pack Index]].

## Factcheck Claim Register Verification Table

| Claim item | Source ID | Verdict label | Confidence | Owner | Status | Next review date | Rollback trigger |
|---|---|---|---|---|---|---|---|
| Helpful-content requirement | `g-helpful-content` | CONFIRMED | high | Researcher | verified or stale | 2026-08-09 | Google guidance updates |
| QRG trust framing | `g-qrg-full` | CONFIRMED for document text | high | E-E-A-T reviewer | verified or stale | 2026-08-09 | New QRG version appears |
| Google AI guidance | `g-ai-opt-guide` | CONFIRMED for Search guidance | high | GEO owner | verified or stale | 2026-08-09 | AI guidance changes |
| Market or practitioner statistic | note-specific source ID | AS-REPORTED or CONTESTED | medium or low | Researcher | pending or verified | source-specific | New source or client data conflicts |
| Unsupported draft claim | none yet | FOLKLORE until sourced | low | Writer | blocked | before handoff | No trustworthy source found |

## Review Loop For Claims

1. Rewrite the claim in plain language before checking sources.
2. Assign CONFIRMED, CONTESTED, AS-REPORTED, SINGLE-SOURCE, or FOLKLORE.
3. Keep unsupported claims out of deliverables until a source ID and limitation are recorded.
4. Reopen verified claims when a source refresh date arrives or a contradictory source appears.

## Source IDs Used

Factcheck operations use `g-helpful-content`, `g-qrg-full`, and `g-ai-opt-guide`.
