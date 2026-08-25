---
type: "source"
title: "Source Manifest Guide"
created: "{{date}}"
updated: "{{date}}"
status: "active"
domain: "Source Evidence"
tags: [sources, evidence, active]
---

# Source Manifest Guide

Every raw source must have:

- path
- sha256
- retrieved date
- source type
- owner
- notes about what it proves and does not prove

Related: [[wiki/sources/_index|Sources Hub]] | [[Source Intake Workflow]]
## Manifest purpose

The manifest proves which bytes were captured and how they entered the Brain.
It does not prove that the source is correct or that every claim is supported.

## Entry schema

| Field | Type | Rule |
|---|---|---|
| id | string | Stable and unique |
| source_path | string | Relative raw path |
| sha256 | string | Lowercase 64-character digest |
| source_url | string | Public HTTPS when available |
| source_type | enum | Official, standards, primary, practitioner, vendor, or market |
| retrieved | date | Actual capture date |
| published | date or unknown | Source chronology |
| last_updated | date or unknown | Living-document chronology |
| owner | string | Review responsibility |
| supported_claims | list | Atomic statements |
| limitations | list | Explicit non-claims |
| confidence | enum | Evidence-appropriate tag |
| refresh_due | date | Next review trigger |
| status | enum | Active, retired, or unresolved |

## Capture procedure

1. Confirm the source belongs in scope.
2. State the candidate claim.
3. Check rights and privacy.
4. Reject credentials and embedded executable content.
5. Capture through the ingestion script.
6. Compute SHA-256 from captured bytes.
7. Write the relative raw path.
8. Preserve source dates separately.
9. Assign source class.
10. Record limitations.
11. Create a source note.
12. Verify the manifest hash.
13. Link affected knowledge notes.
14. Schedule review.

## Integrity check

Recompute the hash from the current raw bytes and compare it to the manifest.
Any mismatch means the capture changed. Do not silently replace the stored hash.
Either restore the original capture or ingest the new bytes as a new event.

## Claim boundary

A single source can support several claims, but each claim must be atomic. A
compound claim needs support for every clause. Record “unresolved” when the page
supports only part of the wording.

## Date boundary

Published, updated, retrieved, verified, and refresh-due dates answer different
questions. Never copy one into another field merely to satisfy a gate.

## Privacy boundary

The manifest and raw captures stay private. Public outputs may use reviewed
source URLs and paraphrased claims, but they must exclude raw paths, local build
paths, review records, and personal identifiers.

## Failure cases

- Hash does not match bytes.
- Raw path escapes the vault.
- URL contains credentials.
- Source ID is duplicated.
- Claim is missing.
- Limitation is blank.
- Retrieval date is inferred.
- Private data is unnecessary.
- Source text is treated as instructions.
- Public output includes the raw manifest.

## Review checklist

- Entry is complete.
- Hash format is valid.
- Raw file exists.
- URL authority matches the claim.
- Dates are plausible.
- Source class is defensible.
- Claims are atomic.
- Limitations are specific.
- Confidence is not inflated.
- Refresh interval matches volatility.

## Handoff

[[Source Intake Workflow]] owns capture. [[Research Refresh Workflow]] owns
currentness. [[Synthesis Workflow]] consumes only reviewed claims.
[[Reporting Workflow]] cites results without exposing private manifest fields.
