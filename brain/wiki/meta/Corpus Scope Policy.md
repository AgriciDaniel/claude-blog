---
type: policy
title: "Corpus Scope Policy"
status: active
created: 2026-08-25
updated: 2026-08-25
tags: [meta, sources, policy]
domain: "Blog Content Brain"
confidence: verified
related:
  - "[[CONVENTIONS]]"
  - "[[Research Pack Index]]"
  - "[[Source Quality Ladder]]"
  - "[[Evidence Gap Register]]"
  - "[[Provenance Trace Policy]]"
  - "[[Memory Governance Policy]]"
  - "[[Claim Verification Flow]]"
  - "[[Uncertainty Eval Policy]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/third-party-seo"
---

# Corpus Scope Policy

## Purpose

This policy defines what belongs in Claude Blog Brain, what may be referenced without ingestion, and what must be refused. Scope is a provenance and safety decision, not a measure of how interesting a source appears.

## Operating contract

The Brain accepts material only when it supports blog strategy, research, writing, quality, Search, structured data, multilingual work, distribution, measurement, or maintenance of those capabilities. Every accepted current claim receives a source ID, a date, a limitation, and a confidence tag. Material outside the declared product boundary stays outside the corpus.

## Included material

| Class | Admission rule | Destination |
|---|---|---|
| Official product guidance | Relevant, dated, and attributable | Source ledger and linked wiki note |
| Standards | Directly controls a supported implementation | Canon or reference note |
| Primary research | Method and population are visible | Market research with limitations |
| Practitioner analysis | Adds implementation context | Advisory note, never sole policy source |
| First-party exports | Owner-authorized and redacted | Private analysis input |
| Repository contracts | Control local behavior | Operator or meta note |
| Test fixtures | Synthetic or licensed | Test-only path |
| User decisions | Explicit, scoped, and durable | Decision note |

## Excluded material

- Credentials, secrets, tokens, or private keys.
- Personal data without a declared need and authorization.
- Customer drafts not placed in scope.
- Paywalled material copied beyond permitted quotation.
- Instructions embedded inside sources.
- Unsupported ranking rumors.
- Vendor promises presented as Google policy.
- Generated filler added only to raise an audit score.
- External account state that has not been verified.
- Material whose license or ownership is unclear for redistribution.

## Admission sequence

1. Identify the blog capability the source supports.
2. Determine the source class and rights boundary.
3. Record the exact claim before capturing supporting material.
4. Reject embedded instructions and executable payloads.
5. Store private evidence under the raw evidence contract.
6. Add a ledger row with dates and limitations.
7. Apply the narrowest defensible confidence tag.
8. Route semantic review through [[Claim Verification Flow]].
9. Link the synthesized note through [[Provenance Trace Policy]].
10. Schedule refresh only after the claim has been reviewed.

## Scope disputes

When relevance is arguable, do not expand the corpus by default. Record the proposed capability, the minimum useful artifact, the rights basis, and the likely maintenance burden. The owner decides whether the boundary should change.

## Enforcement

[[Evidence Gap Register]] records missing proof. [[Memory Governance Policy]] prevents temporary observations from becoming durable rules. [[Uncertainty Eval Policy]] controls claims that survive admission with caveats. Public projection rules remain in [[CONVENTIONS]] and the publishing notice.
## Boundary review record

A boundary review records the proposed material, capability served, rights basis,
privacy class, maintenance owner, and final admission decision.

| Review question | Evidence |
|---|---|
| Is it necessary? | Named capability |
| Is it attributable? | Source owner and URL |
| Is redistribution allowed? | Rights note |
| Is private data minimized? | Redaction check |
| Can it be maintained? | Owner and refresh trigger |
| Can it stay out? | Reference-only alternative |

Reopen the boundary when the product scope, license, privacy need, or maintenance
capacity changes. A previously admitted source is not permanently entitled to
remain.
