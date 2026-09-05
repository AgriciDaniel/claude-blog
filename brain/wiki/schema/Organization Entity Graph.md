---
type: spoke
title: "Organization Entity Graph"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [schema, blog-schema, evergreen]
domain: "Blog Structured Data"
confidence: verified
related:
  - "[[Blog Schema Stack]]"
  - "[[Author Person Markup]]"
  - "[[Schema And E-E-A-T Alignment]]"
source_urls:
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://schema.org/docs/full.html"
  - "https://www.w3.org/TR/json-ld11/"
---
# Organization Entity Graph

## Publisher Graph Job

The Organization node identifies the publisher or site owner that stands behind blog content. It should be stable across articles and connected to authors, articles, logos, and canonical site identity. This note keeps brand identity separate from author identity, product identity, sponsorship, and campaign messaging.

Google's general structured-data source `g-intro-sd` supports the visible-content and accuracy guardrail. Schema.org source `schema-full` defines Organization vocabulary. JSON-LD graph construction uses `w3c-jsonld`. Search appearance language must be checked against `g-search-gallery` before it reaches a client-facing note.

## Organization Entity Graph Schema Table

| Graph component | Required property or relation | Validation target | Warning to record | Source id |
|---|---|---|---|---|
| Publisher `Organization` | `name`, `url`, stable `@id` | Same node reused in article publisher field | Do not rotate IDs by locale, theme, or campaign | `schema-full` |
| Logo reference | Crawlable logo URL when used by the template | Image URL resolves and matches brand asset | A logo from a sponsor or product line may be the wrong publisher | `g-intro-sd` |
| `sameAs` links | Official profiles only | Links are visible in footer, about page, or approved brand profile | Unowned directory entries should not disambiguate the entity | `schema-full` |
| Author connection | Article author remains a Person or named organization as displayed | Publisher and author fields do not collapse accidentally | A staff blog can still need named author rules | `g-intro-sd` |
| JSON-LD graph link | Organization `@id` referenced from Article publisher | Graph inspection shows one publisher node | Duplicate Organization nodes split the graph | `w3c-jsonld` |
| Parent company relation | Parent only when visibly part of site identity | About page or footer names the relationship | Parent ownership should not replace the publisher | `schema-full` |
| Locale or regional publisher | Local brand entity if the page visibly presents one | Locale footer, legal page, and graph agree | Region-specific sites can fork identity accidentally | `g-intro-sd` |

## Brand, Product, And Publisher Separation

A software product, parent company, media brand, and blog publisher can be different entities. Pick the one the page visibly presents as publisher. If a post is sponsored, reviewed by a partner, or syndicated, keep those roles out of the publisher node unless the visible page states that the organization is the publisher.

## Publisher Identity Example

An article on `learn.acmecrm.com` displayed the footer "Acme CRM Learning Center" and linked to an About page for that editorial brand. A corporate parent, "Acme Holdings," appeared only in the legal notice.

Decision: the Article `publisher` stayed "Acme CRM Learning Center" because the visible page presented that entity as publisher, source ID `g-intro-sd`.

The parent company was not used as publisher, but it could be represented separately only if the visible site identity supported that relationship, source ID `schema-full`.

The logo URL pointed to the learning-center mark, not the product icon used in feature screenshots. That avoided swapping product identity into publisher identity, source ID `g-intro-sd`.

The accepted Organization `@id` was reused across article pages so the graph did not create a new publisher for every template variant, source ID `w3c-jsonld`.

## Refresh Triggers

Recheck this note after a rebrand, merger, domain migration, logo change, author platform migration, or locale split. Organization markup often breaks through old templates, not through new prose. Validation should inspect several post types so a legacy template does not keep a stale publisher node.

## Publisher Graph Failure Cases

- Sponsor logos in a post should not overwrite publisher identity, source ID `g-intro-sd`.
- Product-line blogs need a brand decision before `Organization` is emitted, source ID `schema-full`.
- Social profiles in `sameAs` need official control, not just name similarity, source ID `schema-full`.
- Domain migrations can leave old `@id` fragments connected to new pages, source ID `w3c-jsonld`.
- Locale footers can name legal entities that differ from the editorial publisher, source ID `g-intro-sd`.

## Organization Feed To Deliverables

[[Schema Generation Output Contract]] consumes the approved publisher node.

Provided input: Organization name, URL, logo decision, `sameAs` list, rejected profiles, and `@id`.

Expected output: publisher JSON-LD linked from Article plus warnings for parent, sponsor, or locale conflicts.

## Organization Graph Publishing Boundary

The handoff should identify the approved Organization `@id`, the visible proof, and any profiles rejected from `sameAs`. Trust presentation issues go to [[Schema And E-E-A-T Alignment]]; author-specific conflicts go to [[Author Person Markup]].
