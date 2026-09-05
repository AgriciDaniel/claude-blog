---
type: deliverable
title: "Platform Output Formatting Matrix"
domain: "Blog Content Brain"
status: active
created: 2026-07-09
updated: 2026-07-10
tags: [deliverables, platforms, formatting]
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data"
  - "https://developers.google.com/search/docs/appearance/google-images"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
---

# Platform Output Formatting Matrix

## Formatting Comparison Job

This matrix helps [[Blog Quality Score]] and [[Images Audio and Charts]] hand a finished article to WordPress, MDX, Hugo, Ghost, Astro, Jekyll, 11ty, Gatsby, or static HTML without losing metadata, image context, internal links, or structured-data intent. The source IDs are `g-helpful-content`, `g-intro-sd`, `g-google-images`, and `g-ai-opt-guide`.

## Platform Rows To Include

The matrix records platform-specific output packaging only. It does not claim that any CMS has a ranking advantage. It also avoids special AI-only formatting claims because `g-ai-opt-guide` does not support a separate file or markup requirement for Google AI features.

## Platform Output Formatting Matrix

| Platform | Artifact names | Required fields | Schema placement | Media alt and caption handling | Concrete validation evidence |
|---|---|---|---|---|---|
| WordPress | `post-body.html`, CMS field map | title, slug, excerpt, category, tags, author, date, canonical, featured image | Theme head, SEO plugin field, or approved custom field that renders JSON-LD in HTML | Media Library alt text, caption, featured-image alt, local attribution note | Editor preview, rendered source containing article text and JSON-LD, media-alt audit |
| Next.js / MDX | `slug.mdx`, local images, optional component imports | title, description, date, lastUpdated, author, tags, coverImage, coverImageAlt, ogImage | Page component or layout renders JSON-LD in initial static or SSR HTML | Markdown image alt or `Image` `alt`, width, height, optional figure caption | `next build` or preview, view-source/static HTML check, screenshot of rendered article |
| Hugo | `content/posts/slug.md`, page bundle assets | title, description, date, lastmod, author, tags, categories, series, images, draft | Layout partial or shortcode emits JSON-LD into built `public/` HTML | Page bundle or static asset path, image alt in markdown or shortcode, figcaption when needed | `hugo` render, built HTML, canonical and sitemap spot check |
| Ghost | `ghost-post.html` or Admin API payload | title, slug, excerpt, tags, authors, feature image, feature image alt when available | Theme, code injection, or approved integration renders JSON-LD for visible content | Image card alt/caption, feature image attribution, no hotlinked unvetted assets | Ghost preview, exported HTML, head/schema check |
| Astro | `src/content/blog/slug.md` or `slug.mdx`, local assets | title, description, pubDate, updatedDate, author, tags, heroImage, heroImageAlt | Layout or page component emits JSON-LD during static build | `astro:assets` or local markdown image with alt, figure captions for charts | `astro build`, `dist/` HTML check, content collection schema pass |
| Jekyll | `_posts/YYYY-MM-DD-slug.md`, asset folder | title, description, date, last_modified_at, author, tags, categories, image, canonical_url | Layout include in `<head>` using page frontmatter and visible body facts | Markdown image alt, local asset paths, caption include when required | `jekyll build`, `_site/` HTML check, YAML frontmatter parse |
| 11ty | `src/posts/slug.md`, optional data file | title, description, date, updated, tags, layout, permalink, image data | Nunjucks or layout template renders JSON-LD into final `_site/` HTML | Markdown image alt or figure include, caption data preserved through data cascade | `npx @11ty/eleventy`, `_site/` HTML check, data cascade check |
| Gatsby | `slug.mdx` or CMS source node | title, description, date, updated, tags, slug, featuredImage, author | Gatsby Head API, React Helmet SSR, or template renders JSON-LD in built HTML | `gatsby-plugin-image` alt, local image node, figure caption for charts | `gatsby build`, `public/` HTML and page-data check, GraphQL field check |
| Static HTML | `slug.html`, `/assets/` folder | `<title>`, meta description, canonical, OG/Twitter fields, visible author/date or schema dates | `<script type="application/ld+json">` in `<head>` or before body close | `<img alt>`, `<figure><figcaption>`, stable local or approved CDN URLs | Browser preview, view-source check for article text and schema, image-alt checklist |

## Interpretation Rules For Platform Exports

Helpful content and source fidelity survive the export only if the platform wrapper preserves headings, citations, media context, and visible text. `g-intro-sd` supports structured-data caution, while `g-google-images` supports image-context checks. If a platform cannot render a required element, the deliverable records a blocker rather than replacing it with decorative formatting.
