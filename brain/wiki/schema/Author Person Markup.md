---
type: spoke
title: "Author Person Markup"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [schema, blog-schema, evergreen]
domain: "Blog Structured Data"
confidence: verified
related:
  - "[[Blog Schema Stack]]"
  - "[[Article Schema Baseline]]"
  - "[[Schema And E-E-A-T Alignment]]"
  - "[[E-E-A-T for Blog Content]]"
source_urls:
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://schema.org/docs/full.html"
  - "https://www.w3.org/TR/json-ld11/"
---
# Author Person Markup

## Author Identity Job

Author markup answers one narrow question: which visible person is responsible for this blog post, and how does that person connect to the site's article graph? It supports entity clarity inside [[Blog Schema Stack]], but it is not an E-E-A-T badge and it cannot compensate for a weak byline, absent bio, or unsupported reviewer claim.

Google's general structured-data guidance, source ID `g-intro-sd`, keeps the markup tied to page content. Schema.org, source ID `schema-full`, supplies the Person vocabulary. JSON-LD graph syntax comes from `w3c-jsonld`. Search feature claims still need a current Google feature route through `g-search-gallery`; most author work is about clarity rather than a special visual result.

## Person Property Evidence Map

| Person field | Visible evidence needed | Schema use | Reviewer warning | Source id |
|---|---|---|---|---|
| `name` | Byline or author card uses the same name | Primary Person label linked from Article author | Do not invent full names from initials or staff aliases | `g-intro-sd` |
| `url` | Crawlable author page, team page, or profile URL | Stable author `@id` target when available | A broken or thin author page weakens the graph | `schema-full` |
| `sameAs` | Public profile controlled by the author or brand | Disambiguation only when confidence is high | Avoid random social handles, syndication pages, or scraper bios | `schema-full` |
| `jobTitle` or `affiliation` | Visible bio or site policy states the role | Optional context for expertise and organization relation | Role claims need editorial proof, especially in YMYL-adjacent topics | `g-intro-sd` |
| JSON-LD `@id` | Stable canonical URL or fragment strategy | Connects author across article nodes | Template-generated IDs must not vary per build | `w3c-jsonld` |
| `image` | Author headshot appears on an approved profile or card | Optional visual disambiguation | Do not use stock avatars as identity evidence | `schema-full` |
| expertise terms | Bio names the subject area in reader-facing copy | Optional context such as `knowsAbout` only when visible | Keyword lists should not replace credentials or experience | `g-intro-sd` |

## Profile And Byline Consistency Review

1. Compare the rendered byline, author card, and author profile before looking at JSON-LD.
2. Confirm the article node uses the same Person `@id` that the author profile uses.
3. Record any mismatch between displayed role, editorial review claim, and schema field.
4. Send unresolved trust evidence to [[E-E-A-T for Blog Content]] rather than hiding it in markup.

## Identity Repair Scenario

A draft article displayed the byline "M. Chen" while the author page and JSON-LD used "Maya Chen, CPA." The accepted change updated the visible byline to "Maya Chen" before keeping the Person `name`, because markup should reflect what readers can inspect, source ID `g-intro-sd`.

The CPA credential stayed out of Person markup until the author profile showed the credential and editorial owner confirmed it. Schema.org provides vocabulary for Person attributes, but it does not prove the credential by itself, source ID `schema-full`.

The original `sameAs` list included a scraped conference profile. The reviewer kept only the author's controlled LinkedIn profile because unverified profile URLs are weak disambiguation evidence, source ID `schema-full`.

The final handoff used `/authors/maya-chen#person` as the stable `@id`, and the article node referenced that ID instead of generating a per-post author fragment, source ID `w3c-jsonld`.

## Unsupported Author Shortcuts

Do not use Person markup to claim medical, legal, financial, or professional authority that the page does not show. Do not attach `sameAs` links because an SEO template has a field to fill. Do not treat an author schema warning as proof of ranking loss or recovery. The Search Gallery is the guardrail for supported Search appearances, while this note remains focused on accurate identity.

## Byline-Specific Failure Cases

- Staff aliases need an editorial policy before becoming Person nodes, source ID `g-intro-sd`.
- Ghostwritten pieces should not expose a hidden author through JSON-LD, source ID `g-intro-sd`.
- Two authors with the same name need different profile URLs or fragments, source ID `w3c-jsonld`.
- Locale author pages should not mint separate people for the same contributor, source ID `w3c-jsonld`.
- Reviewer fields belong only when review participation is visible, source ID `g-intro-sd`.

## Contract Path For Author Fields

[[Schema Generation Output Contract]] uses this note when building the Person block.

Author input supplied: accepted `name`, approved URL, optional `sameAs`, visible role evidence, and rejected identity fields.

Returned output expected: Person JSON-LD, linked Article author reference, and warnings for weak profile evidence.

## Author Handoff

The handoff should list the accepted Person fields, rejected fields, and any needed author-page edits. If the author is a company, freelancer, syndicated partner, or committee, document that choice before changing the graph. The final recommendation stays advisory until a separate publishing workflow approves template changes.
