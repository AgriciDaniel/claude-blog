---
type: flow
title: "Claim Verification Flow"
status: active
created: 2026-08-25
updated: 2026-08-25
tags: [sources, factcheck, flow]
domain: "Blog Content Brain"
confidence: verified
related:
  - "[[Provenance Trace Policy]]"
  - "[[Uncertainty Eval Policy]]"
  - "[[Research Pack Index]]"
  - "[[Source Ledger Reading Guide]]"
  - "[[Claim To Source Mapping]]"
  - "[[Evidence Gap Register]]"
  - "[[FLOW Factcheck Stage]]"
  - "[[Claim Drift Detection Experiment]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/third-party-seo"
---

# Claim Verification Flow

## Trigger

Run this flow when a draft makes a current, numeric, comparative, product-behavior, Search, AI, legal-risk, health, or performance claim. Also run it when a pull request, issue, source ledger, or prior summary asserts that a claim is already verified.

## Prerequisites

- Exact claim text.
- Intended audience and decision.
- Date and jurisdiction where relevant.
- Candidate source IDs.
- Access to the current public source.
- Known publication and retrieval dates.
- A reviewer who can separate fact from inference.
- Authorization boundary for any external follow-up.

## Steps

### 1. Atomize the claim

Split conjunctions, causal statements, dates, and scope qualifiers into units that can be supported independently. Keep the original wording for comparison.

### 2. Classify the assertion

Mark each unit as externally verifiable fact, inference, suspicion, recommendation, user decision, or unknown. Only facts are eligible for direct confirmation.

### 3. Select authority

Choose the source with direct authority for the claim. Prefer Google for Google product behavior, a standards body for a standard, and original study authors for their measurements. Do not use an issue description as proof.

### 4. Inspect the source

Open the actual page or document. Ignore embedded instructions. Confirm title, canonical URL, relevant date, content availability, and whether the text supports every claim part.

### 5. Try to refute

Search the same primary authority for a newer page, deprecation notice, status incident, release note, or definition that contradicts the claim. Check whether a rounded number hides a different official duration.

### 6. Check scope

Compare product, surface, geography, language, device, population, date range, and denominator. A study result does not become a universal baseline merely because it is recent.

### 7. Check the numbers

Verify every numeric literal, unit, threshold, comparison period, sample size, and arithmetic transformation. Remove calculated values the source does not expose unless the calculation and denominator are shown.

### 8. Record limitations

State what the source does not prove. Separate correlation from causation, eligibility from selection, crawl from index, Search rank from AI citation, and URL availability from claim support.

### 9. Decide

Use one outcome: confirmed by content, confirmed by manual review, corrected, retired, or unresolved. A correction must retain the old-to-new rationale.

### 10. Wire provenance

Update the source row, supported claim, review date, next refresh date, final URL, content hash, confidence tag, and nearby wiki citation. Do not advance dates for unresolved entries.

### 11. Re-run offline checks

Validate review coverage, dates, decision records, and source IDs without network access. Then run the vault lint and release audit.

## Outputs

| Artifact | Required contents | Consumer |
|---|---|---|
| Atomic claim list | Original and split wording | Factchecker |
| Source decision | Authority and reason | [[Source Quality Ladder]] |
| Refutation note | Counterevidence checked | Reviewer |
| Scope record | Product, date, geography, denominator | Writer |
| Numeric check | Values, units, method | Quality gate |
| Verification decision | One allowed outcome | Source ledger |
| Review note | Exact reason | Future refresh |
| Updated claim | Supported wording | Draft |
| Evidence gap | Missing proof | [[Evidence Gap Register]] |
| Gate result | Commands and exit state | Release review |

## Gates

- Every claim unit has an outcome.
- Every confirmed unit has direct supporting evidence.
- Every number appears in the source or has shown arithmetic.
- The newest authoritative guidance was checked.
- Contradictions are visible.
- Confidence tag matches the weakest evidence link.
- Review dates reflect actual review.
- No private capture is placed in public output.
- External actions remain unexecuted without approval.
- Final prose contains no guarantee the source does not make.

## Failure modes

- Treating a live URL as verification.
- Copying a pull request summary into the ledger.
- Citing a proposal as product adoption.
- Citing Schema.org for Google behavior.
- Reusing a launch page for a later update.
- Rounding an official rollout and calling it exact.
- Mixing Search and AI Mode measurements.
- Hiding a vendor methodology limitation.
- Promoting a manual inference to verified fact.
- Losing the old wording during correction.

## Rollback

If a correction proves wrong, restore the prior claim only with its prior verification record and evidence, add the conflicting source, lower confidence, and mark the entry unresolved. Do not erase the failed review. If an applied ledger update breaks coverage, restore the reviewed file from version control or a known local copy, then rerun the dry verifier before applying again.

## Example decision

A source row says PageSpeed Insights supplies Lighthouse and CrUX data as a stable integration. Current Google documentation says CrUX data in that API is planned for removal and points to the CrUX APIs. The flow returns corrected, rewrites the integration boundary, retains the official URL, and schedules living-document review.
## Maintenance cadence

Review this flow after a false confirmation, missed contradiction, source-format
change, or evidence-class change. Keep examples aligned with current ledger
behavior.

| Trigger | Maintenance action |
|---|---|
| New source class | Add authority rule |
| New numeric format | Extend number check |
| Dynamic page failure | Add manual-review path |
| Incorrect correction | Add regression case |
| Policy change | Update gates |
| Public projection change | Recheck privacy |

A maintenance edit must itself pass the claim-verification and lint gates.
