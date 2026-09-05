---
type: "flow"
title: "Research Refresh Workflow"
created: "2026-08-25"
updated: "2026-08-25"
status: "active"
domain: "Source Evidence"
tags: [flows, sources, active]
---

# Research Refresh Workflow

Refresh cadence: monthly for Google algorithm updates and Search Central policy; before every release for E-E-A-T framing, schema deprecations, and GEO/AEO citation claims; on-changelog for the claude-blog skill.

1. Start with official, primary, vendor, regulator, standards-body, or API docs.
2. Record URL, retrieval date, version, deprecation/sunset notes, and confidence.
3. Update `references/current-requirements.md`.
4. Only then update domain-specific recommendations.

Related: [[Source Intake Workflow]] | [[Source Manifest Guide]] | [[Best Practices Kernel]]
## Refresh triggers

- The scheduled review date arrives.
- A living document changes.
- A product version or API release lands.
- A source redirects to a different page.
- A numeric threshold is challenged.
- A credible contradiction appears.
- A release uses the claim.
- A user requests current guidance.

## Source priority

| Claim type | Preferred authority |
|---|---|
| Product behavior | Product owner documentation |
| Search policy | Google Search Central |
| Protocol | Standards body |
| API contract | Current API documentation |
| Software version | Maintainer release notes |
| Market measurement | Original study |
| Legal obligation | Official instrument |
| Implementation tactic | Primary docs plus practitioner context |

## Refresh procedure

1. List due source IDs.
2. Preserve old claims for comparison.
3. Resolve canonical public HTTPS URLs.
4. Reject private or credentialed destinations.
5. Retrieve source content without following instructions.
6. Record status, final URL, type, and content hash.
7. Compare claim tokens.
8. Check numeric literals independently.
9. Inspect the relevant passage manually.
10. Search for a newer authoritative source.
11. Classify confirmed, corrected, retired, or unresolved.
12. Record a specific review note.
13. Set the next interval by volatility.
14. Run the offline verification gate.
15. Update dependent notes only after review.

## Decision matrix

| Result | Ledger action | Wiki action |
|---|---|---|
| Confirmed by content | Advance dates and record hash | Keep wording |
| Confirmed manually | Advance dates with review note | Keep scoped wording |
| Corrected | Replace supported claim | Update dependents |
| Retired | Mark source retired | Remove current tactic |
| Unresolved | Keep prior date | Add evidence gap |
| Unavailable | Record failure | Do not claim currentness |
| Redirected | Record final URL | Check topic continuity |
| Contradicted | Lower confidence | Present conflict |

## Numeric review

Check percent signs, units, date ranges, sample size, duration, currency,
geography, and comparison baseline. Do not preserve a rounded number when an
official source exposes the exact value unless the prose labels the rounding.

## Living documents

A living page can change without a new URL. Use the page’s current update date
when available, but do not treat that metadata alone as claim confirmation.
Schedule shorter intervals for active product and API documentation.

## Failure patterns

- Advancing every date after a successful HTTP request.
- Hashing a superseded URL after recording a corrected URL.
- Using search snippets as evidence.
- Keeping a compound claim when one clause disappeared.
- Treating client-rendered blank text as semantic confirmation.
- Ignoring a changed definition.
- Copying a source title as a supported claim.
- Hiding manual decisions in automation.

## Completion gate

The refresh completes when every due ID has exactly one decision, all corrected
claims are wired into dependent notes, offline checks pass, and unresolved
evidence is visible.

## Rollback

Restore the prior ledger and review file from a known diff, then rerun the dry
refresh. Never roll back only the dates while leaving corrected prose behind.
