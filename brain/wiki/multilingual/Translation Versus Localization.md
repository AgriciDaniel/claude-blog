---
type: spoke
title: "Translation Versus Localization"
domain: "Multilingual Blog Publishing"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [multilingual, translation, localization, active]
source_urls:
  - "https://developers.google.com/search/docs/specialty/international/localized-versions"
  - "https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites"
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://schema.org/docs/full.html"
---

# Translation Versus Localization

## Boundary Job

This note separates literal language transfer from local market adaptation. Translation preserves meaning across languages. Localization adapts the page for the target reader's terminology, expectations, evidence, examples, legal context, and internal-link path.

The source IDs are `g-localized`, `g-multiregional`, `g-helpful-content`, and `schema-full`. They support the international page context, people-first quality threshold, and structured-data vocabulary. They do not replace a local source when a claim depends on a country or region.

### Use This Note Before

Use it before assigning a translator, building a locale brief, or deciding whether a source article can be cloned into another market. It is also useful when stakeholders want a fast translation but the topic includes pricing, regulation, culture, or country-specific examples.

### What Counts As Translation

Translation keeps the same reader job, evidence base, examples, and structure while changing language. It still needs review for accuracy, grammar, metadata, schema strings, and internal links.

### What Counts As Localization

Localization changes the article so the target reader gets the right context. It may alter headings, examples, calls to action, proof order, screenshots, legal caveats, source citations, and links.

## Translation Versus Localization Decision Table

| Signal | Translation is enough when | Localization is required when | Owner | Follow-up note |
|---|---|---|---|---|
| Search intent | Query goal is the same across locales | SERP or sales data shows different objections | Locale SEO | [[Locale Intent Research]] |
| Evidence | Claims are global and source remains valid | Country law, pricing, or availability changes | Factchecker | [[Localized Source Requirements]] |
| Examples | Examples are culturally neutral | Examples depend on institutions, seasons, currency, or norms | Editor | [[Locale Review Workflow]] |
| Links | Equivalent local pages exist | Source-language links would mislead or frustrate readers | SEO lead | [[Cross Locale Internal Linking]] |
| Structured data | Entity labels match visible localized text | Schema needs local names, URLs, or breadcrumbs | Schema reviewer | [[Multilingual Schema Rules]] |
| Offer and CTA | Same action is available in the target market under `g-multiregional` | Currency, signup route, or support promise changes | Marketing owner | [[Localized Source Requirements]] |
| Metadata | Title and description can preserve the same promise under `g-helpful-content` | Search snippet would imply a source-market offer | Editor | [[Locale Launch QA]] |
| Units and formats | Conversions do not change meaning under `g-helpful-content` | Dates, measurements, or decimal style affect advice | Translator | [[Translation QA Matrix]] |

## Decision Procedure

1. Mark each source article section as translate, localize, replace, or omit.
2. Identify every claim that changes by market.
3. Choose translation only when reader job, proof, and page path survive intact.
4. Send unresolved market differences to the relevant spoke before launch.

## Practical Rule

If the team cannot explain why the localized page helps that locale's reader beyond language access, treat the job as incomplete localization rather than finished translation.

## Boundary Decision Example

A US SaaS comparison article moves to `es-MX` (`g-multiregional`).
The feature explanation can be translated because the reader job and evidence remain global (`g-helpful-content`).
The pricing example, support CTA, and customer quote need localization because they imply market availability (`g-multiregional`, `g-helpful-content`).
The decision memo labels feature sections as translate and conversion sections as localize (`g-helpful-content`).
That split keeps the schedule fast without pretending every paragraph has the same risk (`g-helpful-content`).

## Boundary Failure Modes

- Same language does not guarantee the same market, offer, or reader expectation (`g-multiregional`).
- Product UI translations can exist while local support or purchase paths are absent (`g-multiregional`).
- A legal caveat translated accurately can still name the wrong jurisdiction (`g-helpful-content`).
- Schema labels copied from the source article can make localization look complete before content review (`schema-full`).

## Adaptation Checklist Wiring

Consumer: [[Localization Adaptation Checklist]].

Inputs provided:

- per-section label of translate, localize, replace, or omit.
- affected examples, CTAs, source claims, metadata, links, and schema fields.

Outputs expected:

- pass or blocker rows for regional examples, CTA wording, legal references, source suitability, and formality.
- reviewer escalation when the boundary decision exposes local risk.
