---
type: spoke
title: "Locale Intent Research"
domain: "Multilingual Blog Publishing"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [multilingual, localization, intent, active]
source_urls:
  - "https://developers.google.com/search/docs/specialty/international/localized-versions"
  - "https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites"
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://schema.org/docs/full.html"
---

# Locale Intent Research

## Locale Discovery Job

This note decides whether a translated brief still matches the way people search, compare, object, and decide in the target locale. It should run before drafting, not after the translation is finished. A literal translation can be accurate and still fail because the market uses different terminology, expects different examples, or needs a different proof sequence.

Primary source IDs are `g-localized`, `g-multiregional`, `g-helpful-content`, and `schema-full`. The first two keep the research tied to real language or regional targeting. The helpful-content source keeps the decision anchored in reader value. Schema.org matters only when entity labels, breadcrumbs, or article metadata must reflect the localized vocabulary visible on the page.

### Research Questions This Note Owns

- Does the topic have the same reader job in the target language or country?
- Are local objections, product names, regulations, units, or buying triggers different enough to change the outline?
- Which source-language examples become confusing or misleading when moved into this locale?

### Translation Boundary For Intent

If terminology changes but the reader job remains stable, localize headings and examples. If the reader job changes, create a locale-specific brief and send the source article back to [[Multilingual Publishing]] as a reference only. If the topic needs local evidence, open [[Localized Source Requirements]] before claims are approved.

## Locale Intent Research Table

| Locale | Search-language clue | Reader expectation | Draft change | Reviewer | Risk |
|---|---|---|---|---|---|
| en-GB | Same concept, different spelling and examples | UK pricing and legal references | Localize terms, retain structure | UK editor | Medium |
| es-MX | Local phrase differs from direct Spanish translation | More practical examples before theory | Rewrite intro and headings | Native SEO reviewer | High |
| fr-CA | Bilingual market may expect both English and French names | Clarify entity aliases | Add alias block and schema name check | Locale editor | Medium |
| ja-JP | Searcher may prefer vendor comparison before workflow | Reorder proof and examples | New outline required | Market lead | High |
| de-AT | Same language family hides country-specific examples under `g-multiregional` | Austrian proof may differ from German proof | Keep shared sections, replace local examples | DACH reviewer | Medium |
| ar-SA | Search-language and page direction both affect review under `g-helpful-content` | Screenshots and support labels need locale confirmation | Add visual review before outline approval | Locale editor | High |

## Research Procedure

1. Compare target-language SERP wording, internal site search, and first-party query data when available.
2. Mark each source heading as keep, localize, replace, or split.
3. Identify claims that need local sources before the writer starts.
4. Pass high-risk changes to [[Locale Review Workflow]] with the evidence attached.

## Output Standard

The output is a brief addendum, not a keyword dump. It should name the locale, the intent delta, the sections affected, the source IDs used, and the reviewer required before launch.

## Brief Addendum Example

A source article about choosing payroll software is approved for English readers (`g-helpful-content`).
For `en-GB`, the reader job remains comparison, but proof examples and support terminology need local review (`g-multiregional`, `g-helpful-content`).
The research addendum keeps the outline order but marks pricing examples as replace (`g-helpful-content`).
For `es-MX`, sampled SERP notes can show a stronger setup-first expectation (`g-helpful-content`).
That locale receives a rewritten introduction and a separate source requirement before drafting (`g-helpful-content`).

## Intent Errors This Note Prevents

- A direct keyword translation can miss the local noun readers actually use (`g-helpful-content`).
- One language can contain several market tasks when country, currency, or support paths differ (`g-multiregional`).
- Entity aliases may fit headings but still require schema and breadcrumb review (`schema-full`).
- SERP observations without date and locale should not become proof of stable demand (`g-helpful-content`).

## Brief Contract Wiring

Consumer: [[Content Brief Output Contract]].

Inputs provided:

- target locale, intent delta, affected headings, local terminology, and reviewer requirement.
- claim slots that need local evidence before the writer receives the assignment.

Outputs expected:

- reader job and SERP pattern fields updated for the target market.
- evidence-pack notes that separate global source IDs from local source gaps.
