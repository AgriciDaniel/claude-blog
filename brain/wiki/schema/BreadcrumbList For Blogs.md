---
type: spoke
title: "BreadcrumbList For Blogs"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [schema, blog-schema, evergreen]
domain: "Blog Structured Data"
confidence: verified
related:
  - "[[Blog Schema Stack]]"
  - "[[Article Schema Baseline]]"
  - "[[Internal Link Matrix]]"
source_urls:
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
  - "https://developers.google.com/search/docs/appearance/structured-data/search-gallery"
  - "https://schema.org/docs/full.html"
  - "https://www.w3.org/TR/json-ld11/"
---
# BreadcrumbList For Blogs

## Breadcrumb Review Job

Breadcrumb schema should mirror the path readers see or the canonical hierarchy the site uses for blog navigation. It is not an internal-linking strategy by itself. [[Blog Schema Stack]] owns the schema relationship, while [[Internal Link Matrix]] owns broader link placement.

The evidence split matters. Google's general guidance, source ID `g-intro-sd`, requires the markup to reflect the page. Search Gallery, source ID `g-search-gallery`, is the supported-feature checkpoint for breadcrumb appearances. Schema.org, source ID `schema-full`, defines `BreadcrumbList` and `ListItem`; JSON-LD serialization follows source ID `w3c-jsonld`.

## BreadcrumbList For Blogs Schema Table

| Breadcrumb element | Required property | Validation target | Warning to log | Source id |
|---|---|---|---|---|
| `BreadcrumbList` | `itemListElement` containing ordered list items | One list represents one visible path | Multiple competing paths can confuse ownership of the article | `schema-full` |
| `ListItem.position` | Integer sequence starting at the first path item | Positions match rendered order | Missing or duplicate positions make the trail unreliable | `schema-full` |
| `ListItem.name` | Visible label or canonical category label | Labels match navigation or taxonomy | Do not use keyword-stuffed labels hidden from readers | `g-intro-sd` |
| `ListItem.item` | Absolute canonical URL for each linked step when applicable | URLs resolve and match canonical hierarchy | Staging URLs and redirect chains should block handoff | `w3c-jsonld` |
| Search support check | Feature appears in current Google gallery | Current Search Gallery review date is recorded | Gallery support is not a guarantee of display | `g-search-gallery` |
| No visible breadcrumb trail | Prefer no BreadcrumbList unless canonical hierarchy is documented | Page template and taxonomy source agree | Invisible hierarchy needs stronger operator approval | `g-intro-sd` |
| Topic hub as parent | Hub URL, not tag archive, when hub is the editorial parent | Hub appears in navigation or internal-link plan | Tags can look like parents without owning the path | `schema-full` |

## Taxonomy Cases That Need Judgment

A blog often has category pages, topic hubs, and tag archives that could all look like breadcrumb parents. Choose the path that matches the visible template and the editorial hierarchy. If a post belongs to several tags, do not generate several breadcrumb trails unless the page visibly offers several paths and the implementation can support them cleanly.

## Breadcrumb Choice Example

Post reviewed: "CRM Migration Checklist" appeared under `/blog/crm-migration-checklist`, displayed a breadcrumb of Home > Resources > CRM, and carried tags for RevOps, SaaS, and Data Cleanup.

Accepted trail: Home, Resources, CRM. The reviewer rejected tag-based trails because the visible page exposed one navigational path and structured data should reflect the page readers see, source ID `g-intro-sd`.

The CRM parent URL was the canonical hub rather than a filtered tag archive. That choice kept the hierarchy aligned with the editorial topic structure, source ID `schema-full`.

The final JSON-LD used ordered `ListItem.position` values and production URLs, not staging links from the preview environment, source ID `w3c-jsonld`.

## Change Triggers

Review this note when categories are renamed, a hub becomes canonical, the CMS changes URL paths, or old posts are migrated. A breadcrumb can stay syntactically valid while pointing to an outdated taxonomy, so validation must include a navigation check and not only a JSON parser.

## Breadcrumb-Specific Breakpoints

- Multiple category assignments need one accepted trail, source ID `g-intro-sd`.
- Redirecting parent URLs should block handoff until the final URL is known, source ID `w3c-jsonld`.
- Keyword-edited breadcrumb labels should match navigation before schema ships, source ID `g-intro-sd`.
- Date archives should not become parents unless the template uses them visibly, source ID `schema-full`.
- Locale folders need local breadcrumb names and local URLs, source ID `w3c-jsonld`.

## Contract Output For Trails

[[Schema Generation Output Contract]] consumes the accepted breadcrumb trail.

Trail package in: ordered labels, canonical URLs, rejected alternate paths, and taxonomy proof.

Contract result expected: BreadcrumbList JSON-LD plus warnings for redirects, hidden paths, or unresolved parents.

## Breadcrumb Publishing Boundary

The handoff should list the accepted trail, rejected alternate trails, and any redirect or canonical issue. It does not approve taxonomy restructuring. Escalate large hierarchy changes to cluster planning before updating schema templates.
