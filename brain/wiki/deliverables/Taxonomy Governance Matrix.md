---
type: deliverable
title: "Taxonomy Governance Matrix"
domain: "Blog Content Brain"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, taxonomy, governance]
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls"
  - "https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview"
  - "https://developers.google.com/search/docs/crawling-indexing/robots/intro"
---

# Taxonomy Governance Matrix

## Governance Comparison Job

This deliverable decides whether a tag, category, archive, locale grouping, or recommendation bucket should exist, merge, remain hidden, or route to CMS work. It connects [[Tag Taxonomy]], [[Research Pack Index]], and [[Blog Quality Score]] without turning a taxonomy review into a publishing action. The source IDs wired here are `g-helpful-content`, `g-canonical`, `g-sitemaps`, and `g-robots-intro`.

## Rows The Matrix Must Force

Every row must name the taxonomy object, its user job, the page or archive it creates, and the reason a search engine or reader would need it. A tag that only mirrors an author habit is not enough. If two rows serve the same intent, the matrix should recommend merge or no-index review rather than expanding the archive.

## Decision Columns For Audit Trails

| Governance object | Decision question | Required evidence | Source IDs | Next action |
|---|---|---|---|---|
| Suggested tag | Does this label support a reader task not already covered? | Sample URLs, target intent, internal-link use | `g-helpful-content` | Approve, rename, or reject |
| Thin archive | Does the archive create a low-value page set? | URL count, indexed state, traffic, quality note | `g-helpful-content`, `g-robots-intro` | Consolidate or block crawl only with caveat |
| Duplicate category | Which URL should represent the cluster? | Canonical target, redirects, duplicate paths | `g-canonical` | Merge category and update links |
| Sitemap inclusion | Should this taxonomy URL appear in XML discovery? | Canonical status, update cadence, index intent | `g-sitemaps`, `g-canonical` | Include, exclude, or fix canonical first |
| Locale taxonomy | Does the label mean the same thing in each market? | Locale owner, translated term, local examples | `g-helpful-content` | Route to locale review |
| Recommendation bucket | Is the grouping operational or cosmetic? | Decision owner, related deliverable, review date | `g-helpful-content` | Keep only if it changes workflow |

## Interpretation Rules For Reviewers

Robots.txt can help control crawling, but it is not an indexing guarantee, so taxonomy cleanup must not rely on crawl blocking alone. Canonical signals are used when duplicate or near-duplicate taxonomy URLs compete, but the row still needs a human decision about the preferred archive. Sitemap inclusion is a discovery signal for eligible URLs, not proof that the taxonomy is useful. When evidence is missing, route the object back to [[Google Data Integrations]] or [[Freshness and Content Decay]] instead of filling the cell with assumptions.
