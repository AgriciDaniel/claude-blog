---
type: spoke
title: "Evidence Density For Blog Posts"
domain: "Blog Writing"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [writing, six-pillar, evergreen]
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
---

# Evidence Density For Blog Posts

## Evidence Density For Blog Posts Drafting Job

This note decides how much proof a section needs. Evidence density is the relationship between claim risk, reader decision cost, and source proximity. A section can be overstuffed with citations and still fail the reader if the evidence does not answer the task.

### Density Signals Owned Here

Low-risk definitions need enough evidence to avoid invented claims. Comparative, current, YMYL-adjacent, or Search-feature claims need a stronger source trail. `g-helpful-content` supports useful, reliable content; `g-qrg-full` supplies a quality lens for trust-sensitive material. `g-ai-opt-guide` and `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` keep AI-facing recommendations from becoming unsupported special-file advice.

### Anti-Patterns This Pass Removes

Remove source stacks that cite several URLs for a simple sentence without adding clarity. Remove unsourced metrics, stale tactics, and decorative references. Also remove claims that use a Google source to support a broader market conclusion. For example, an llms.txt Google Search clarification cannot prove how every assistant, crawler, or retrieval system behaves.

## Evidence Density Review Table

| Draft element | Evidence needed before approval | Source IDs | Evidence state | Owner | Next action |
|---|---|---|---|---|---|
| Definition paragraph | One authoritative source or internal glossary | `g-helpful-content` | Official when content-quality related | Editor | Keep concise |
| Process recommendation | Source plus example or client context | `g-helpful-content`, `g-qrg-full` | Official lens plus local proof | Writer | Add operational example |
| AI Search claim | Google AI guide or update event | `g-ai-opt-guide`, `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` | Official for Google only | GEO reviewer | Add caveat and date |
| Trust-sensitive assertion | Author, reviewer, source, or method evidence | `g-qrg-full` | Official quality lens | Lead editor | Escalate if proof missing |
| Practitioner tactic | Practitioner source plus official boundary | `g-ai-opt-guide` | Advisory unless corroborated | Researcher | Label confidence |
| Dated policy statement | Current Search guidance and ledger date | `g-ai-opt-guide`, `g-qrg-full` | Official but time-sensitive | Researcher | Add refresh trigger |
| Original field example | Method note, screenshot, or owned data context | `g-helpful-content` | Local proof plus usefulness lens | Writer | Keep scope narrow |

## Evidence Density Editing Procedure

1. Mark every claim that could become false after a policy, product, or market change.
2. Assign each marked claim to official, primary, practitioner, first-party, or unsupported evidence.
3. Remove citations that do not cover the claim beside them.
4. Add a date when the claim depends on a changing Google or AI feature.
5. Lower confidence when the strongest source is practitioner evidence.
6. Send remaining gaps to [[Evidence Gap Register]] before the draft reaches [[Blog Quality Score]].

### Density Calibration Case

A section says "Google ignores llms.txt" in one sentence, then cites three
market studies and a practitioner thread. That is noisy evidence density.
Keep the claim paired to the Google Search clarification
(`g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`),
then move any non-Google assistant discussion to [[AI Citation Mechanics]].
For a reader-facing recommendation, one official boundary plus a clear caveat
beats a source pile that does not cover the exact claim (`g-helpful-content`).

### Density-Specific Failure Cases

- A low-risk definition has more citations than explanation (`g-helpful-content`).
- A current policy claim lacks a date because the paragraph feels obvious (`g-ai-opt-guide`).
- Local experience is cited like a universal benchmark (`g-qrg-full`).
- An official Google page is used to validate a broader market conclusion (`g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`).

### Deliverable Wiring

[[Blog Analyzer Score Report]] consumes this note inside content usefulness
and recommendation queue fields: claim risk, source proximity, evidence tier,
missing-data label, owner, and fix priority.
It expects dense evidence only where the reader decision or claim volatility
requires it, and it marks decorative sourcing as a review problem (`g-helpful-content`).

## Source Handling

The evidence IDs for this pass are `g-helpful-content`, `g-ai-opt-guide`, `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`, and `g-qrg-full`.

## Related

- [[Claim Source Pairing Pattern]]
- [[Citation Ready Paragraphs]]
- [[Blog Quality Score]]
- [[Research Pack Index]]
