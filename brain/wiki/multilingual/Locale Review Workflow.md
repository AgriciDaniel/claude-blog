---
type: spoke
title: "Locale Review Workflow"
domain: "Multilingual Blog Publishing"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [multilingual, localization, review, active]
source_urls:
  - "https://developers.google.com/search/docs/specialty/international/localized-versions"
  - "https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites"
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://schema.org/docs/full.html"
---

# Locale Review Workflow

## Review Chain Purpose

This workflow defines who must inspect a localized blog post before it can pass [[Locale Launch QA]]. It separates language quality, source fidelity, legal sensitivity, structured data, and publication readiness so one reviewer is not silently asked to cover every risk. The source IDs in scope are `g-localized`, `g-multiregional`, `g-helpful-content`, and `schema-full`.

### Entry Criteria

A draft enters this workflow only after the locale brief names the target language or country, the source article is available, and the draft identifies claims that vary by market. If the draft is raw machine translation, send it through [[Machine Translation Risk Notes]] before assigning final reviewers.

### Exit Artifact

The exit artifact is a dated review record naming each reviewer, what evidence they checked, what they approved, and what still blocks launch. Store only the decision and source IDs in the note. Do not store private reviewer credentials, CMS access details, or client-only exports.

## Locale Review Workflow Step Table

| Stage | Input | Evidence required | Action | Owner | Handoff |
|---|---|---|---|---|---|
| Language fidelity | Source and localized draft | Meaning preserved, idioms corrected, no untranslated fragments | Approve or return to translator | Locale reviewer | Content editor |
| Intent fit | Locale brief and SERP notes | Target reader job remains accurate | Confirm outline or request local brief | Locale SEO | Writer |
| Source fidelity | Claim list | Local facts have local or translated evidence | Mark pass, gap, or remove | Factchecker | Launch QA |
| Legal or YMYL screen | Sensitive claims | Local advice does not exceed evidence | Escalate when expertise is required | Policy owner | [[Regional Legal And YMYL Escalation]] |
| Schema consistency | Rendered page and JSON-LD | Visible names, URLs, authors, and breadcrumbs agree | Approve or revise structured data | Schema reviewer | [[Multilingual Schema Rules]] |
| Metadata review | CMS preview and SERP fields | Locale title, description, and social text match page purpose under `g-helpful-content` | Approve or send back to editor | Metadata owner | [[Locale Launch QA]] |
| Refresh ownership | Volatile local claim list | Owner and next review trigger are named under `g-helpful-content` | Add cadence note or block handoff | Managing editor | [[Multilingual Refresh Cadence]] |

## Control Points

1. A reviewer can approve only the lane they inspected.
2. Any unsupported local claim moves to [[Localized Source Requirements]].
3. Any page-level alternate issue goes to [[Hreflang Checklist]].
4. Final readiness belongs to [[Locale Launch QA]], not to an individual translator.

## Evidence Discipline

Use `g-helpful-content` for the quality threshold, not as proof of local law or market behavior. Use `schema-full` only for vocabulary alignment, then verify Google-specific eligibility elsewhere when rich results are part of the decision.

## Review Handoff Example

A Spanish draft about health-adjacent software onboarding arrives with fluent language (`g-helpful-content`).
The locale reviewer approves idiom and terminology, but the factchecker cannot verify an eligibility claim for the target market (`g-helpful-content`, `g-multiregional`).
The workflow does not send the page to launch QA yet (`g-helpful-content`).
It routes the claim to [[Regional Legal And YMYL Escalation]] and records source fidelity as blocked (`g-helpful-content`).
Only the approved language lane moves forward; the claim lane waits for an owner decision (`g-helpful-content`).

## Workflow-Specific Failure Modes

- Native-language approval can be mistaken for evidence approval when lanes are not separated (`g-helpful-content`).
- A schema reviewer may approve syntax while visible localized labels still differ (`schema-full`).
- Reviewer names without inspected lanes create false confidence at launch QA (`g-helpful-content`).
- Legal concerns raised during review should not be buried as copyediting comments (`g-helpful-content`).

## Adaptation Checklist Wiring

Consumer: [[Localization Adaptation Checklist]].

Inputs provided:

- reviewer lane, inspected evidence, approval state, unresolved claim, and escalation owner.
- language, source, legal, schema, metadata, and refresh decisions as separate records.

Outputs expected:

- checklist pass or blocker states for examples, CTAs, legal references, source suitability, and escalation.
- owner list that lets the adaptation deliverable avoid treating one reviewer as universal approval.
