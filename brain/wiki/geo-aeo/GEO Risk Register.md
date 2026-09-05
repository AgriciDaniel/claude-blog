---
type: spoke
title: "GEO Risk Register"
domain: "GEO and AEO"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [geo-aeo, ai-citation, evergreen]
---

# GEO Risk Register

## GEO Risk Register Record Scope

This register captures risks created by generative search recommendations. It is not a backlog of every SEO task. A risk belongs here only when an AI citation, AI Overview, AI Mode, assistant answer, or extractable-passage recommendation could mislead a client, overstate evidence, or push work outside the read-only V1 boundary.

Official Google sources set the guardrails (`g-ai-opt-guide`, `g-ai-features`). Market evidence from `sparktoro-zero-click-2026` and `seer-aio-impact-ctr-2026` must stay in the AS-REPORTED lane. The June 2026 `llms.txt` update source, `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`, is a recurring risk control because stakeholders may ask for file-based shortcuts. `ziptie-aio-source-selection` can support advisory extraction checks, not guaranteed visibility.

### Events Or Items This Register Captures

Capture citation guarantees, market-stat overreach, AI-only content changes, snippet-control tradeoffs, source-less answer blocks, llms.txt requests framed as Google Search tactics, and measurement claims without a data source.

### Events Or Items Routed Elsewhere

Traditional ranking volatility goes to [[Google Algorithm Update Ledger]], full quality scoring goes to [[Blog Quality Score]], and data export issues go to [[Google Data Integrations]].

## GEO Risk Register Table

| Risk item | Source ID | Owner | Confidence | Status | Next review date | Rollback trigger |
|---|---|---|---|---|---|---|
| AI citation guarantee appears in a recommendation | `g-ai-opt-guide` | GEO lead | high, official guidance | open | 2026-08-09 | Any wording promises inclusion |
| AIO CTR benchmark is treated as causal | `seer-aio-impact-ctr-2026` | Analyst | medium, AS-REPORTED | monitor | 2026-08-09 | Client data contradicts benchmark |
| Zero-click study becomes a site forecast | `sparktoro-zero-click-2026` | Strategist | medium, market panel | open | 2026-08-09 | Stakeholder asks for traffic estimate |
| llms.txt is sold as Google visibility work | `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` | Research owner | high, official update | open | 2026-08-09 | New proposal uses file as requirement |
| Extraction heuristic is presented as a ranking factor | `ziptie-aio-source-selection` | Editor | medium, practitioner | monitor | 2026-08-09 | Draft claims Google requires the pattern |
| Generative AI report is absent but trend is claimed | `g-genai-reports` | Analyst | high, official reporting context | open | 2026-08-09 | Recommendation cites missing property data |
| Assistant citation becomes Google proof | `seoclarity-chatgpt` | GEO reviewer | medium, practitioner | monitor | 2026-08-09 | Non-Google citation supports Search claim |
| Preview relaxation ignores contractual text | `g-ai-features` | Legal reviewer | high, official preview context | open | 2026-08-09 | Recommendation exposes restricted copy |

## GEO Risk Register Review Loop

1. Add a row when a recommendation can be misunderstood as a guarantee.
2. Tie the risk to the weakest source used in the decision.
3. Assign an owner who can remove, caveat, or defer the recommendation.
4. Recheck this register before sending a GEO audit, brief, or readiness report.

## Risk Intake Scenario

A draft audit says a page "should gain AI Overview clicks" after adding a clearer answer block. The register opens a guarantee risk tied to `g-ai-opt-guide`, because the official Google source supports foundations and caveats, not inclusion promises.

The same audit uses Seer context to rank the recommendation first. The owner changes the wording to "review citation exposure after publication" and labels the benchmark advisory, because `seer-aio-impact-ctr-2026` is not causal property evidence.

If the client asks for `llms.txt` as a fast fix, the register keeps a separate risk row tied to `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`. That row closes only when the final deliverable stops presenting the file as Google visibility work.

## Register-Specific Failure Modes

- A risk is closed because the phrase sounds cautious, but the output still implies guaranteed citation.
- The row cites the strongest source rather than the weakest claim dependency, hiding the actual evidence gap.
- The next review date passes without checking [[2026 Google Update Timeline]] for AI feature changes.
- A preview-control risk is assigned to SEO alone even though `g-ai-features` cannot override legal restrictions.

## Audit Report Wiring

[[Full Site Blog Audit Report]] consumes open and monitor rows from this register. It needs the risk item, source ID, confidence label, owner, rollback trigger, and the exact recommendation text that caused the risk.

The audit expects a decision-ready queue: remove wording, add caveat, measure first, or defer. It should not receive generic "be careful" notes without a source-tied trigger.

## Risk Row Output Detail

For `g-ai-opt-guide` risks, quote the promise that overstates Google AI guidance.

For `seer-aio-impact-ctr-2026` risks, name the causal language that must be removed.

For `g-genai-reports` risks, state whether property access exists or is missing.

For llms.txt risks, keep the Google caveat source beside the proposed wording.

## GEO Risk Register Closure Rule

Close a risk only after the claim is removed, narrowed, or backed by stronger evidence. A risk is not closed merely because the recommendation sounds plausible.
