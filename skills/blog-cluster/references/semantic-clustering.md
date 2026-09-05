# Semantic Clustering: Keyword Grouping & Intent Classification

> Reference document for `blog-cluster`. Loaded on demand during Plan Phase.

## What is semantic clustering?

Semantic clustering groups keywords by **meaning and search intent**, not by
word similarity. Two keywords that look different can share the same intent
and should be targeted by one post, not two competing posts. Conversely, two
keywords that share most of their letters can have completely different
intents and require separate posts.

Example:

- "best CRM software" and "top CRM tools 2026" share commercial-comparison
  intent. They belong in the same post.
- "CRM definition" is informational and educational. It belongs in a separate
  post (or a separate FAQ entry inside the pillar).

## The four-step clustering process

### Step 1. Build the keyword universe from the seed

Use WebSearch to expand the seed keyword into 30 to 50 candidate phrases:

1. Direct search of the seed; capture related searches and "People also ask".
2. Long-tail expansion: append `guide`, `tips`, `tools`, `examples`, `vs`, `best`, `how to`.
3. Question mining: prepend `what is`, `how does`, `why`, append `for beginners`.
4. Intent variants: add commercial (best, top, review, comparison, pricing), informational (guide, tutorial, explained, examples), and transactional (buy, download, tool, software, service) modifiers.
5. Year freshness: append `2026`.

Drop near-duplicates (variants that differ by only a stop word or plural).

### Step 2. SERP overlap analysis (the strongest signal)

Two keywords belong in the same post when Google returns substantially the
same top-10 results for both. This is the single most reliable signal for
intent matching, and no paid SEO tool is required.

Method:

1. WebSearch keyword A. Note the top 10 organic result URLs (domain plus path).
2. WebSearch keyword B. Note the top 10 organic result URLs.
3. Count the overlap: how many URLs appear in both result sets?

Thresholds:

| Shared top-10 URLs | Interpretation | Action |
|--------------------|----------------|--------|
| 7 to 10 | Same intent, same SERP | Must be the same post |
| 4 to 6 | Very similar intent | Should be the same post |
| 2 to 3 | Related but distinct | Separate posts; interlink heavily |
| 0 to 1 | Different intent | Must be separate posts |

Optimization: do not test every pair. First group by initial intent guess
(Step 3), then verify SERP overlap within each candidate cluster.

### Step 3. Intent classification

Classify each keyword into one of four intents. Intent drives template
selection and cluster grouping.

| Intent | Linguistic signals | Typical template | User goal |
|--------|--------------------|------------------|-----------|
| Informational | what is, how to, guide, explained, tutorial, why | how-to-guide, faq-knowledge, tutorial, pillar-page | Learn |
| Commercial | best, top, review, comparison, vs, alternative | listicle, comparison, product-review | Evaluate |
| Transactional | buy, pricing, download, tool, software, service, free | listicle (with CTAs), product-review | Take action |
| Navigational | brand names, specific products, "<brand> login" | (excluded) | Find a known page |

Rules:

- Group informational keywords into educational clusters.
- Group commercial keywords into evaluation clusters.
- Treat transactional keywords as standalone or attach to a commercial cluster.
- Exclude navigational keywords from topic clusters; they belong to brand pages.

### Step 4. Entity mapping

Use WebSearch to identify the key entities Google associates with the topic:

- People (industry leaders, authors, researchers)
- Products and tools (software, services, platforms)
- Concepts (frameworks, methodologies, theories)
- Organizations (companies, institutions, standards bodies)

Entities help confirm cluster boundaries. Keywords that reference the same
set of entities likely belong in the same cluster.

### Step 5. Hub vs. spoke decision

For each candidate cluster:

- The **hub** (pillar) targets the broadest, highest-volume keyword across
  the entire seed set. There is exactly one pillar per seed.
- The **spokes** target specific long-tail keywords within each cluster.

Promote a keyword to pillar candidate when it scores highest on:

1. Volume estimate (Step 6 below).
2. Centrality: it is referenced by, or related to, the largest number of
   other keywords in the universe.
3. Intent breadth: it is informational and broad enough to anchor sub-topics
   of multiple intents.

## Search volume estimation (without paid tools)

| Signal | Volume estimate |
|--------|-----------------|
| Appears in Google autocomplete | Medium to High |
| Has a "People also ask" block | Medium to High |
| Multiple dedicated articles from major publications | High |
| Forum / Reddit discussions only | Low to Medium |
| Niche blogs only, no major publications | Low |

Label each keyword as `high`, `medium`, or `low`. This is sufficient for
relative prioritization within a cluster. For absolute numbers, the user can
run `/blog google` (Keyword Insights) or use DataForSEO via `seo-dataforseo`.

## Cluster naming convention

`Cluster <Letter>: <Theme> (<intent>)`

Example: `Cluster A: Content Creation (informational)`.

## Worked example: seed = "AI marketing for small business"

Keyword universe (selected, 12 of ~35):

1. ai marketing for small business
2. how to use ai for small business marketing
3. best ai marketing tools for small business
4. ai marketing automation small business
5. small business ai email marketing
6. ai content creation for small business
7. ai social media tools for small business
8. how much does ai marketing cost
9. ai marketing roi small business
10. small business ai marketing case study
11. chatgpt for small business marketing
12. ai marketing strategy for small business

SERP overlap pass (sampled):

- 1 vs. 12: 8 of 10 URLs match. Same post (pillar candidate).
- 2 vs. 6: 6 of 10 URLs match. Same post.
- 3 vs. 7: 5 of 10 URLs match. Same post (commercial-tools cluster).
- 8 vs. 9: 3 of 10 URLs match. Related but distinct; keep separate and interlink.

Intent classification:

- Informational: 1, 2, 6, 12, 4, 5, 11
- Commercial: 3, 7
- Transactional: (none pure)
- Mixed (informational + commercial): 8, 9, 10

Resulting cluster map:

| ID | Role | Title | Primary keyword | Intent | Template |
|----|------|-------|-----------------|--------|----------|
| P | Pillar | AI Marketing for Small Business: Complete 2026 Guide | ai marketing for small business | informational | pillar-page |
| A1 | Spoke | How to Use AI for Small Business Marketing (Step by Step) | how to use ai for small business marketing | informational | how-to-guide |
| A2 | Spoke | AI Content Creation for Small Business: Tools and Workflow | ai content creation for small business | informational | how-to-guide |
| A3 | Spoke | ChatGPT for Small Business Marketing: 12 Practical Use Cases | chatgpt for small business marketing | informational | listicle |
| B1 | Spoke | Best AI Marketing Tools for Small Business in 2026 | best ai marketing tools for small business | commercial | listicle |
| B2 | Spoke | AI Social Media Tools for Small Business Compared | ai social media tools for small business | commercial | comparison |
| C1 | Spoke | How Much Does AI Marketing Actually Cost a Small Business? | how much does ai marketing cost | informational+commercial | data-research |
| C2 | Spoke | AI Marketing ROI: A Small Business Case Study | ai marketing roi small business | informational | case-study |

Result: 1 pillar + 7 spokes across 3 clusters (Content Creation, Tools, Economics). Intent diversity: 2. Template diversity: 5. Total interlinks (planned): roughly 22.

## Anti-patterns

| Anti-pattern | Why it fails | Fix |
|--------------|--------------|-----|
| Grouping by word similarity | "email marketing" and "email etiquette" share words but not intent | Use SERP overlap plus intent |
| One keyword per post | Wastes effort and risks thin content | Group keywords with shared SERPs |
| Mixing intents in one cluster | Dilutes both ranking signals | Separate by intent first |
| More than 5 clusters per pillar | Spreads authority too thin | Cap at 5 clusters |
| Single-post clusters | No internal-linking mass | Minimum 2 spokes per cluster |
