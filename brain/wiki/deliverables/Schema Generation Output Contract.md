---
type: deliverable
title: "Schema Generation Output Contract"
domain: "Blog Structured Data"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, schema, json-ld, active]
---

# Schema Generation Output Contract

## JSON LD Deliverable Boundary

This contract defines the JSON-LD output expected from `/blog schema`. The generator can produce Article or BlogPosting, Person, Organization, BreadcrumbList, ImageObject, and relevant warnings. It must describe visible page content and route schema decisions through [[Blog Schema Stack]]. It does not promise rich results or create facts missing from the page.

### Required Inputs And Hard Stops

Inputs are URL, headline, description, author, publisher, dates, image assets, breadcrumb trail, visible body summary, and any entity identifiers approved by the operator. `g-intro-sd` supports the visible-content and JSON-LD preference posture. `w3c-jsonld` anchors serialization rules, while `schema-full` is the vocabulary reference.

### Warnings The Generator Must Emit

The output must warn when dates are missing, author identity is unclear, image URLs are unstable, breadcrumb labels differ from page navigation, or requested markup is not supported for Google Search. The supported-rich-result check uses `g-search-gallery` and should separate Google eligibility from Schema.org vocabulary breadth.

## Structured Data Output Sections

The deliverable contains a short schema rationale, JSON-LD block, validation notes, unsupported or risky requests, and handoff instructions for implementation review.

## Schema Generation Output Contract Acceptance Table

| Schema object | Required fields | Validator | Acceptance criterion | Handoff owner | Blocker state |
|---|---|---|---|---|---|
| BlogPosting or Article | headline, dates, author, publisher, mainEntityOfPage | Visible page and `g-intro-sd` | Describes the article accurately | Technical SEO | Blocked if page facts are absent |
| Person | name and approved identity fields | Author bio or provided profile | Author matches visible byline | Editor | Review if author evidence is weak |
| Organization | name, URL, logo where available | Site identity source | Publisher is consistent | Technical SEO | Blocked if invented |
| BreadcrumbList | ordered visible path | Page navigation | Trail matches user-facing hierarchy | Developer | Fix if labels differ |
| ImageObject | URL, caption or alt context when available | Media list and [[Images Audio and Charts]] | Image is stable and relevant | Media owner | Blocked if asset rights unknown |
| Warnings | unsupported features and missing inputs | `g-search-gallery`, `schema-full` | Limitations are explicit | Reviewer | Blocked if warning is ignored |

## Handoff Procedure For Validation

1. Compare every schema value with visible page content before validation.
2. Run Google eligibility checks separately from general Schema.org vocabulary checks.
3. Preserve warnings in the implementation ticket so unsupported requests are not silently shipped.

## Source IDs Used

Schema generation uses `g-intro-sd`, `g-search-gallery`, `schema-full`, and `w3c-jsonld`.
