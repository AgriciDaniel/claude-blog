---
type: deliverable
title: "Translation QA Matrix"
domain: "Blog Content Brain"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, translation, qa]
source_urls:
  - "https://developers.google.com/search/docs/specialty/international/localized-versions"
  - "https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites"
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://schema.org/docs/full.html"
---

# Translation QA Matrix

## Translation Gate Scope

This matrix checks whether a translated blog draft preserves structure, meaning, metadata, schema text, and source fidelity before it enters [[Multilingual Publishing]]. It is narrower than localization: it asks whether the translation is faithful and publishable, not whether all regional examples are optimal. Source IDs wired here are `g-localized`, `g-multiregional`, `g-helpful-content`, and `schema-full`.

## Inputs That Must Arrive With The Draft

The QA reviewer needs the source article, translated article, target locale, glossary, localized URL pattern, meta title and description, schema strings, source citations, and machine-translation disclosure when relevant. Without those inputs, the matrix records a blocker instead of filling confidence with guesswork.

## Translation QA Pass Fail Matrix

| Check | Pass evidence | Fail pattern | Severity | Fix owner |
|---|---|---|---|---|
| Structure preservation | Headings, lists, tables, and embeds match the source intent | Missing section or reordered logic | Major | Translator |
| Keyword localization | Target term reflects local search language | Literal keyword sounds unnatural | Major | Locale SEO |
| Meta tags | Title and description fit locale and page purpose | Source-language metadata remains | Blocker | Editor |
| Numbers and units | Dates, currency, decimal style, and units are adapted | Mixed units confuse readers | Major | Translator |
| Schema strings | Visible page text and schema labels agree | Schema translates a claim differently | Blocker | Schema reviewer |
| Machine artifacts | No untranslated fragments or robotic phrasing | Raw MT output remains | Blocker | Locale reviewer |
| Hreflang readiness | Locale URL and language code are present | URL map missing return-link data | Major | SEO lead |

## Release Handoff For Translation Defects

Pass does not mean the localized article is strategically complete. It means the translation can move to [[Localization Adaptation Checklist]] or final locale review. If structured data is present, `schema-full` provides the vocabulary route, while Google international docs handle locale annotation evidence. The reviewer must record any unresolved source or local-quality gap in [[Research Pack Index]].
