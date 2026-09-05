---
type: spoke
title: "Terminology Control List"
domain: "Blog Voice"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [personas, voice-style, active]
---

# Terminology Control List

## Terminology Control List Naming Job

Terminology Control List keeps preferred terms, forbidden terms, acronyms, synonyms, product names, and definitions consistent across the blog. It prevents a cluster from calling the same concept by five names or using a keyword variant that changes the meaning. It supports [[Semantic Topic Clusters]], [[Voice and Style]], and [[SERP-Informed Briefs and Outlines]].

### Terms Owned By This Control

Use `g-helpful-content` for reader clarity, `g-qrg-full` for trust-sensitive wording, `nng-editorial-heuristics` for consistency, and `g-ai-opt-guide` when terminology touches AI Search features. `g-nlp` can support entity extraction workflows, but an API label is not a brand definition.

### Human Review For Risky Names

Escalate regulated terms, competitor names, legal entity names, medical claims, financial terms, and product names that conflict with source evidence. Send prohibited phrasing to [[Banned Claims And Phrases]] and localized naming to [[Locale Voice Adaptation]].

## Terminology Control List Governance Table

| Term | Preferred use | Forbidden use | Source or basis | Owner | Action |
|---|---|---|---|---|---|
| AI citation readiness | Editorial review state | Guaranteed inclusion in AI answers | `g-ai-opt-guide`, [[AI Citation Mechanics]] | GEO reviewer | Keep caveat in templates |
| Helpful content | Reader-usefulness standard | A magic ranking label | `g-helpful-content` | Editor | Tie to concrete reader outcome |
| YMYL | Higher-risk topic class | Generic seriousness label | `g-qrg-full` | Reviewer | Require source and expert check |
| Brand product name | Exact approved capitalization | Keyword-stuffed variant | Brand source plus glossary | Brand owner | Update cluster references |
| AI Mode | Google Search AI surface | Synonym for all assistants | `blog-aimode`, `g-ai-features` | GEO owner | Keep platform scope explicit |
| llms.txt | Unsupported for Google Search AI guidance | Required Google optimization file | `g-ai-opt-guide` | SEO lead | Block special-file claims |
| FAQPage | Deprecated rich-result tactic for Google Search | Current universal rich-result lever | `g-faqpage-sd` | Schema reviewer | Use visible Q and A wording carefully |

### Term, Preferred Use, Forbidden Use, Source, Owner, And Action

Each row should include an example sentence and the contexts where the term applies. A synonym is allowed only when it helps the reader and does not break entity clarity.

## Term Cleanup Example

Cluster issue: three briefs use "GEO score," "AI visibility score," and "citation readiness" for the same review state.

Decision: standardize on "AI citation readiness" for editorial review, not guaranteed assistant inclusion.

Source basis: `g-ai-opt-guide` bounds Google AI guidance, while [[AI Citation Mechanics]] handles passage-level caveats.

Before title: "Improve Your AI Visibility Score."

After title: "Review AI Citation Readiness Before Publishing."

The after title keeps the entity and outcome narrower, so the taxonomy owner can align categories without inventing a metric.

If a stakeholder wants "GEO score," the glossary row must define whether it is a local internal label or public-facing term.

## Naming Failure Modes

- A synonym changes scope from Google Search to every AI assistant.
- A keyword variant becomes the public product name without brand approval.
- A deprecated schema label remains in templates after a source refresh.
- A term is translated literally and collides with a local legal phrase.
- Entity extraction output is treated as a definition, although `g-nlp` only supports analysis.
- A glossary row lacks an example sentence, so writers apply it inconsistently.

## Governance Wiring

Primary consumer: [[Taxonomy Governance Matrix]].

Inputs supplied: preferred term, forbidden use, source basis, example sentence, locale note, and cleanup action.

Output expected back: approve, rename, merge, or reject decision for tags, categories, and public labels.

Voice consumer: [[Style Learning Voice Profile]] receives stable terms and banned variants for sample scoring.

## Terminology Control List Drift Scan

Scan new briefs, rewritten intros, title tags, schema names, and localized variants. If multiple names are already indexed, record the cleanup plan before changing published copy.
