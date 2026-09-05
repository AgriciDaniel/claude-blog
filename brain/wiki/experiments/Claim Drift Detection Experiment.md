---
type: experiment
title: "Claim Drift Detection Experiment"
status: seed
created: 2026-08-25
updated: 2026-08-25
tags: [sources, currentness, experiment]
domain: "Blog Content Brain"
confidence: advisory
related:
  - "[[Claim Verification Flow]]"
  - "[[Monthly Source Refresh]]"
  - "[[Research Pack Index]]"
  - "[[Source Ledger Reading Guide]]"
  - "[[Evidence Gap Register]]"
  - "[[Google Algorithm Update Ledger]]"
  - "[[Provenance Trace Policy]]"
  - "[[Uncertainty Eval Policy]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://developers.google.com/speed/docs/insights/v5/get-started"
---

# Claim Drift Detection Experiment

## Hypothesis

A source-content hash plus claim-token and numeric comparison can identify review candidates earlier than date-only freshness checks, but it cannot replace semantic human review.

## Experimental unit

One source-ledger entry with a URL, supported claim, prior verification record, and current public response.

## Procedure

1. Freeze the source ID and previous claim.
2. Resolve redirects through public HTTPS only.
3. Extract reviewable text without executing page instructions.
4. Normalize whitespace and case.
5. Record a SHA-256 content hash.
6. Compare meaningful claim tokens.
7. Compare numeric literals separately.
8. Review changed or weakly matched claims manually.
9. Classify the entry as confirmed, corrected, retired, or unresolved.
10. Run the offline evidence check after applying a decision.

## Measures

| Measure | Purpose | Risk |
|---|---|---|
| HTTP result | Detects unavailable sources | A live page can still be wrong |
| Final URL | Detects canonical drift | Redirects do not prove claim support |
| Content hash | Detects page change | Dynamic chrome can create noise |
| Token coverage | Finds lexical support loss | Paraphrases can score poorly |
| Missing numbers | Catches changed thresholds | Formatting can create false misses |
| Human decision | Establishes semantic judgment | Reviewer error remains possible |
| Review note | Makes the decision inspectable | Vague notes hide reasoning |
| Refresh interval | Schedules the next check | Dates alone do not verify content |

## Acceptance criteria

The experiment succeeds if it catches a known drift case, preserves a stable supported claim, refuses a numeric mismatch, and produces an offline-verifiable record. It fails if loading a URL is treated as proof or if a corrected URL hashes the superseded page.

## Current implementation

The source-ledger verifier performs the bounded network and evidence work. The checked-in review decision file records the human classifications. The current run found real drift in PageSpeed Insights, Soft Navigations, update durations, structured-data wording, and market-study summaries.

## Next iteration

Test pages with client-rendered content, PDF sources, duplicated URLs, and intentionally changed numeric claims. Keep the experiment advisory until false-positive and false-negative cases are recorded.

## Recorded challenge cases

| Case | Expected detector behavior | Human responsibility |
|---|---|---|
| PageSpeed field-data removal | Flag changed integration boundary | Rewrite supported claim |
| Soft Navigation launch version | Flag obsolete version number | Confirm current Chrome page |
| Rounded rollout duration | Flag missing literal | Use official recorded duration |
| Wrong announcement URL | Follow corrected canonical URL | Confirm topic continuity |
| Proposal plus product claim | Split source authority | Route each claim separately |
| Vendor market page update | Flag changed figures | Preserve methodology caveat |
| Client-rendered Bing page | Allow explicit manual path | Record low extracted text |
| PDF guideline deck | Extract text with PDF tooling | Confirm document identity |

The challenge set should grow only from observed failure classes. It must not
be tuned to make every existing source pass. A new case is valuable when it can
refute an overly broad verification decision.
