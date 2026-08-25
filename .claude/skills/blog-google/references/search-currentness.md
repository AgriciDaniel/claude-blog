# Google Search Currentness Playbook

Verified against Google-owned sources on 2026-07-23. Treat product
announcements as product context, not evidence of a ranking factor. Use
`data/google-updates.json` for the machine-readable source ledger.

Resolve the ledger in this order:

1. In a repository checkout, use the repository-root
   `data/google-updates.json`.
2. In a standalone install, use `data/google-updates.json` beside the main
   blog orchestrator skill, normally
   `~/.claude/skills/blog/data/google-updates.json`.

Do not substitute a same-named file from the current working directory. If
neither trusted location exists, report the ledger as unavailable and continue
with the cited primary sources below.

## Core and Spam Update Analysis

1. Confirm the named update's start and end on the Search Status Dashboard.
2. Wait at least one full week after completion.
3. Compare a post-update week with a week before rollout.
4. Analyze Web Search, Images, Video mode, and News tab separately.
5. Distinguish small movement from a large, sustained drop.
6. Avoid quick fixes and mass deletion. Improve reader value and navigation in
   durable ways; deletion is a last resort.
7. Do not infer what an update rewarded from dates alone. Smaller core changes
   may be unannounced.

## Canonical Reevaluation

After a material canonicalization fix, Google may keep the URL in the duplicate
cluster for up to two weeks. Report the state as `PENDING_REEVALUATION` during
that window when the implementation is now correct. Search Console's Request
Indexing feature is quota-limited; reserve it for important URLs.

Request Indexing in URL Inspection is separate from the Indexing API. The
Indexing API remains restricted to eligible JobPosting and
BroadcastEvent/VideoObject pages.

## Generative AI Performance Reports

The dedicated Search Console generative-AI views are a gradual, subset rollout:

- Separate Search and Discover reports.
- Search includes AI Overviews and AI Mode.
- Documented dimensions are impressions, pages, countries, devices for Search,
  and dates.
- Do not promise clicks or queries in these dedicated reports.
- No supported Search Console API endpoint is documented for this dedicated
  view. The blog-google command must report `SKIPPED` or unavailable and direct
  the user to the Search Console UI rather than synthesize data.

Standard Search Analytics totals continue to include AI-feature activity under
Google's documented aggregation rules; do not claim those totals isolate AI
Overviews or AI Mode.

## Platform Properties

Search Console platform properties are gradually becoming available for
Instagram, TikTok, X, and YouTube. Eligible creators can use the UI for Search
and Discover performance, including clicks, impressions, posts, and queries.
Do not promise that the current Search Console API or `/blog google gsc`
supports these reports.

## Discover

Run this checklist only when Discover is a declared target or the property has
Discover data:

- Useful, original, in-depth, and timely material.
- Country and topic relevance where applicable.
- Non-sensational titles and non-clickbait presentation.
- Topic-level expertise; older useful content remains eligible.
- No special structured data requirement.

Preferred images are at least 1200px wide, contain more than 300,000 total
pixels, use a useful 16:9 crop where possible, and are enabled by
`max-image-preview:large` or AMP. Use a relevant, representative image through
schema.org markup or `og:image`.

## Preferred Sources

Preferred Sources is optional audience development, not a ranking signal. It
works at domain or subdomain level, not subdirectory level. For a user who
selects the publication, its content is more likely to appear in Top Stories
and can receive a preferred badge in AI Mode or AI Overviews. Offer Google's
publisher assets only when this fits the site's audience strategy.

## Crawl and Interaction Checks

- Googlebot processes the first 2MB of a supported file and the first 64MB of a
  PDF, measured uncompressed. Place critical title, metadata, canonical,
  essential schema, and primary content before the HTML cutoff.
- Warn on inline base64, CSS, JavaScript, or navigation bloat that can push
  critical content beyond the first 2MB. This is not a ranking factor.
- Back-button hijacking requires observed deceptive behavior. Do not flag
  normal History API use by syntax alone.
- A section intended for a "Read more" deep link should be immediately visible
  and retain its hash on load. Do not force a scroll reset. This is not a ban
  on every accordion elsewhere.

## AMP

AMP is supported, not required, and has no special ranking benefit. Since
2026-07-01 Google Search sends users directly to publisher-hosted AMP pages.
Keep AMP only when it provides operational value; remove it with correct
canonicals and redirects.

## Generative AI Product Context

Google I/O 2026 announced Gemini 3.5 Flash as AI Mode's global default,
follow-ups from AI Overviews into AI Mode, multimodal inputs, and information
agents. The May Explore-the-web update highlighted original analyses, public
discussions, inline links, and link previews.

These announcements do not create new content-scoring factors. Do not recommend
agent-specific schema, fixed-size content chunks, or fan-out page factories.
Use foundational SEO, accurate non-commodity material, authentic discussion,
clear page identity, and useful media.

## Primary Sources

- https://developers.google.com/search/updates
- https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history
- https://developers.google.com/search/docs/appearance/core-updates
- https://developers.google.com/search/docs/crawling-indexing/canonicalization-troubleshooting
- https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports
- https://developers.google.com/search/blog/2026/07/search-console-social-video-platforms
- https://developers.google.com/search/docs/appearance/google-discover
- https://developers.google.com/search/docs/appearance/preferred-sources
- https://developers.google.com/search/docs/crawling-indexing/googlebot
- https://developers.google.com/search/blog/2026/04/back-button-hijacking
- https://developers.google.com/search/docs/appearance/snippet
- https://blog.google/products-and-platforms/products/search/search-io-2026/
- https://blog.google/products-and-platforms/products/search/explore-web-generative-ai-search/
