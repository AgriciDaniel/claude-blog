---
type: spoke
title: "Machine Translation Risk Notes"
domain: "Multilingual Blog Publishing"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [multilingual, machine-translation, localization, active]
source_urls:
  - "https://developers.google.com/search/docs/specialty/international/localized-versions"
  - "https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites"
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://schema.org/docs/full.html"
---

# Machine Translation Risk Notes

## MT Risk Job

This note flags when machine-translated blog content is a starting draft rather than a publishable localized page. It does not ban translation tools. It prevents raw or lightly edited output from being mistaken for local expertise, local source coverage, or a reviewed user experience.

The evidence set is `g-localized`, `g-multiregional`, `g-helpful-content`, and `schema-full`. The first two sources define the international page context, the helpful-content source sets the quality bar, and Schema.org is relevant when generated schema text copies mistranslated or unsupported visible content.

### Review Moments Covered

Use this note before language review, before locale launch, and whenever a CMS draft shows machine-generated phrases, untranslated segments, copied metadata, or source-language schema labels. Pair it with [[Translation Versus Localization]] when stakeholders argue that exact translation is enough.

### Translation Versus Quality Boundary

Machine translation can help produce a first pass. Quality approval requires human review for meaning, terminology, local examples, citations, and sensitive claims. A fluent paragraph still fails if it imports the wrong regulation, currency, or product promise.

## Machine Translation Risk Table

| Risk signal | What to inspect | Why it matters | Required action | Escalation state |
|---|---|---|---|---|
| Source-language metadata remains | Title, description, schema name fields | Search snippets and structured data misrepresent the page | Rewrite and rerun schema review | Major |
| Literal anchor translations | Internal links and CTA text | Links may stop matching local reader intent | Send to [[Cross Locale Internal Linking]] | Medium |
| Unsupported local examples | Examples, statistics, product claims | The draft may imply local availability or legality | Open [[Localized Source Requirements]] | High |
| Awkward but accurate prose | Paragraph flow and idioms | Reader trust drops even when facts survive | Native-language edit | Medium |
| Sensitive advice translated | Legal, financial, health, or safety sections | Local rules may differ materially | Route to [[Regional Legal And YMYL Escalation]] | Blocker |
| Entity name hallucination | Author bios, product names, institutions | Local authority can be invented by fluent text under `g-helpful-content` | Factcheck named entities before review | Blocker |
| Measurement conversion drift | Dates, decimals, currency, units | Advice can change meaning after formatting conversion under `g-helpful-content` | Send to [[Translation QA Matrix]] | Major |
| Schema language mismatch | JSON-LD strings and visible page copy | Structured data can repeat a mistranslation under `schema-full` | Block until [[Multilingual Schema Rules]] passes | Blocker |

## Escalation Procedure

1. Label the draft as MT-assisted in the internal review record.
2. Separate language defects from evidence defects.
3. Block launch for any sensitive, unsupported, or schema-visible mistranslation.
4. Release only after [[Locale Review Workflow]] records the owner and resolution for each high-risk item.

## Source Constraint

Do not cite the source IDs as proof that a specific MT tool is safe or unsafe. They support the quality and internationalization rules this note applies.

## MT Triage Example

A machine-translated finance-adjacent explainer renders a common account term as a local regulated product (`g-multiregional`, `g-helpful-content`).
The sentence is fluent, but the meaning now implies a market-specific product claim (`g-helpful-content`, `g-multiregional`).
The triage marks the segment as source fidelity risk, not style cleanup (`g-helpful-content`).
The editor removes the claim until [[Localized Source Requirements]] can name acceptable evidence (`g-helpful-content`).
Only after that decision should the draft move into normal translation QA (`g-helpful-content`).

## MT Failure Modes To Separate

- Post-editing can polish grammar while leaving source-market CTAs unchanged (`g-helpful-content`).
- A glossary may cover body text but miss title tags, alt text, and schema labels (`schema-full`).
- Date and unit conversions can alter instructions even when the sentence reads naturally (`g-helpful-content`).
- A locale reviewer should not inherit legal review merely because the draft is machine-assisted (`g-helpful-content`).

## QA Matrix Wiring

Consumer: [[Translation QA Matrix]].

Inputs provided:

- MT disclosure, flagged segment, risk signal, required reviewer, and blocked field.
- distinction between language defect, evidence defect, schema defect, and sensitivity defect.

Outputs expected:

- pass or fail rows for machine artifacts, numbers and units, schema strings, and source fidelity.
- release handoff note that sends unresolved local-quality gaps to the right owner.
