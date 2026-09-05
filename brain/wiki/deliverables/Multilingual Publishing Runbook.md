---
type: deliverable
title: "Multilingual Publishing Runbook"
domain: "Blog Content Brain"
status: active
created: 2026-07-09
updated: 2026-07-10
tags: [deliverables, multilingual, publishing]
source_urls:
  - "https://developers.google.com/search/docs/specialty/international/localized-versions"
  - "https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites"
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://schema.org/docs/full.html"
---

# Multilingual Publishing Runbook

## Publishing Scope For One Command

This runbook defines the artifact package that the current `/blog multilingual` command produces for [[Multilingual Publishing]]. In V1 it is an artifact-only command: it writes source and localized files plus hreflang assets, but it does not mutate CMS settings, submit sitemaps, or publish changes. The source IDs are `g-localized`, `g-multiregional`, `g-helpful-content`, and `schema-full`.

## Inputs And Decisions Held Outside Automation

Required inputs are source article, target locale, URL structure, translator or reviewer owner, localized examples, schema field map, and CMS language-map destination. Legal, medical, financial, and cultural sensitivity decisions stay with human reviewers. Machine translation alone is not treated as added value.

## Multilingual Execution Table

| Phase | Input | Output | Evidence requirement | Review date |
|---|---|---|---|---|
| Source write | Topic, source language, format | `multilingual/{source}/{slug}.{ext}` | Helpfulness and source fidelity via `g-helpful-content` | Before translation |
| Translate | Source packet, glossary, target codes | `multilingual/{lang}/{localized-slug}.{ext}` | Preserved claims and citations | Same sprint |
| Localize | Draft, regional examples, CTA rules | Market-adapted localized file | Human locale review | Before QA |
| Hreflang plan | URL map, language codes | `multilingual/hreflang-tags.html`, `multilingual/hreflang-sitemap.xml`, `multilingual/hreflang-map.json` | Return-link and x-default check via `g-localized` | Before publish |
| URL structure | ccTLD, subdomain, or subdirectory decision | CMS-ready path map | Structure rationale via `g-multiregional` | Before CMS work |
| Schema strings | Localized title, description, entity names | Localized Article or BlogPosting JSON-LD with `inLanguage` and translation relationship | Vocabulary route through `schema-full` | Before final QA |
| Sitemap-ready list | Approved localized URLs | Discovery handoff | Only canonical locale URLs | After QA |

## Operating Loop After Launch

After publication, route parity and stale translation checks to [[Locale Audit Coverage Matrix]] when that deliverable exists in the workflow. If locale performance is reviewed, use [[Google Data Integrations]] rather than global market averages. Any missing return link, unreviewed schema text, or untranslated legal reference blocks the handoff.
