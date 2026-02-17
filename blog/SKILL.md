---
name: blog
description: >
  Blog strategy, content briefs, editorial calendars, and article generation
  optimized for Google rankings (December 2025 Core Update, E-E-A-T) and AI citations
  (GEO/AEO). Writes, rewrites, analyzes, and updates blog posts with answer-first
  formatting, sourced statistics, Pixabay/Unsplash images, SVG charts via /svg skill,
  FAQ schema injection, and freshness signals. Supports any platform (WordPress,
  Next.js MDX, Hugo, Ghost, HTML). Use when user says "blog", "write blog",
  "blog post", "blog strategy", "content brief", "editorial calendar", "analyze blog",
  "rewrite blog", "update blog", "blog SEO", "blog optimization", "content plan".
user-invocable: true
argument-hint: "[write|rewrite|analyze|brief|calendar|strategy] [topic-or-file]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - WebFetch
  - WebSearch
  - Task
---

# Blog -- Content Engine for Rankings & AI Citations

Full-lifecycle blog management: strategy, briefs, writing, analysis, optimization,
and editorial planning. Dual-optimized for Google's December 2025 Core Update
and AI citation platforms (ChatGPT, Perplexity, Google AI Overviews).

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/blog write <topic>` | Write a new blog post from scratch |
| `/blog rewrite <file>` | Rewrite/optimize an existing blog post |
| `/blog analyze <file-or-url>` | Audit blog quality with 0-100 score |
| `/blog brief <topic>` | Generate a detailed content brief |
| `/blog calendar [monthly\|quarterly]` | Generate an editorial calendar |
| `/blog strategy <niche>` | Blog strategy and topic ideation |
| `/blog update <file>` | Update existing post with fresh stats and sources |

## Orchestration Logic

### Command Routing

1. Parse the user's command to determine the sub-skill
2. If no sub-command given, ask which action they need
3. Route to the appropriate sub-skill:
   - `write` → `blog-write` (new articles from scratch)
   - `rewrite` → `blog-rewrite` (optimize existing posts)
   - `analyze` / `audit` → `blog-analyze` (quality scoring)
   - `brief` → `blog-brief` (content briefs)
   - `calendar` / `plan` → `blog-calendar` (editorial calendars)
   - `strategy` / `ideation` → `blog-strategy` (positioning and topics)
   - `update` → `blog-rewrite` (with freshness-update mode)

### Platform Detection

Detect blog platform from file extension and project structure:

| Signal | Platform | Format |
|--------|----------|--------|
| `.mdx` files, `next.config` | Next.js/MDX | JSX-compatible markdown |
| `.md` files, `hugo.toml` | Hugo | Standard markdown |
| `.md` files, `_config.yml` | Jekyll | Standard markdown with YAML front matter |
| `.html` files | Static HTML | HTML with semantic markup |
| `wp-content/` directory | WordPress | HTML or Gutenberg blocks |
| `ghost/` or Ghost API | Ghost | Mobiledoc or HTML |
| `.astro` files | Astro | MDX or markdown |

Adapt output format to detected platform. Default to standard markdown if unknown.

## Core Methodology -- The 6 Pillars

Every blog post targets these 6 optimization pillars:

| Pillar | Impact | Implementation |
|--------|--------|---------------|
| Answer-First Formatting | +340% AI citations | Every H2 opens with 40-60 word stat-rich paragraph |
| Real Sourced Data | E-E-A-T trust | Tier 1-3 sources only, inline attribution |
| Visual Media | Engagement + citations | Pixabay/Unsplash images + SVG charts via `/svg` |
| FAQ Schema | +28% AI citations | Structured FAQ with 40-60 word answers |
| Content Structure | AI extractability | 50-150 word chunks, question headings, proper H hierarchy |
| Freshness Signals | 76% of top citations | Updated within 30 days, dateModified schema |

## Quality Gates

These are hard rules. Never ship content that violates them:

| Rule | Threshold | Action |
|------|-----------|--------|
| Fabricated statistics | Zero tolerance | Every number must have a named source |
| Paragraph length | Never > 100 words | Split or trim |
| Heading hierarchy | Never skip levels | H1 → H2 → H3 only |
| Source tier | Tier 1-3 only | Never cite content mills or affiliate sites |
| Image alt text | Required on all images | Descriptive, includes topic keywords naturally |
| Self-promotion | Max 1 brand mention | Author bio context only |
| Chart diversity | No duplicate types | Each chart must be a different type |

## Scoring Methodology

Blog quality is scored across 6 categories (100 points total):

| Category | Weight | What it measures |
|----------|--------|-----------------|
| Content Quality | 25 pts | Readability, paragraph length, sentence length, information gain |
| Answer-First Formatting | 20 pts | Stat-first H2 openers, direct answers, question headings |
| Statistics & Citations | 20 pts | Source count, tier quality, attribution format |
| Visual Elements | 15 pts | Image count, chart count/diversity, distribution |
| Schema & Structure | 10 pts | FAQ schema, BlogPosting schema, heading hierarchy |
| Freshness & Trust | 10 pts | Update date, author E-E-A-T, brand mentions |

### Scoring Bands

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | Excellent | Publish as-is |
| 75-89 | Good | Minor tweaks needed |
| 60-74 | Needs Work | Significant improvements required |
| < 60 | Poor | Full rewrite recommended |

## Reference Files

Load on-demand as needed:
- `references/google-landscape-2026.md` — December 2025 Core Update, E-E-A-T, algorithm changes
- `references/geo-optimization.md` — GEO/AEO techniques, AI citation factors
- `references/content-rules.md` — Structure, readability, answer-first formatting
- `references/visual-media.md` — Image sourcing (Pixabay, Unsplash) + SVG chart integration
- `references/quality-scoring.md` — Full scoring checklist with point values

## Sub-Skills

| Sub-Skill | Purpose |
|-----------|---------|
| `blog-write` | Write new blog articles from scratch with full optimization |
| `blog-rewrite` | Rewrite/optimize existing posts for rankings and AI citations |
| `blog-analyze` | Audit blog quality with 0-100 scoring and prioritized recommendations |
| `blog-brief` | Generate detailed content briefs with outlines and research |
| `blog-calendar` | Editorial calendars with topic clusters and freshness schedules |
| `blog-strategy` | Blog positioning, content pillars, audience mapping, distribution |

## Subagents

| Agent | Role |
|-------|------|
| `blog-researcher` | Research specialist — finds current statistics, sources, competitive data |
| `blog-writer` | Content generation specialist — writes optimized blog content |

## Integration with Other Skills

- **`/svg` or `/svg-chart`**: Generate dark-mode SVG charts for data visualization
- **`/seo`**: Deep SEO analysis of published blog pages
- **`/seo-schema`**: Schema markup validation and generation
- **`/seo-geo`**: AI citation optimization audit

## Anti-Patterns (Never Do These)

| Anti-Pattern | Why |
|-------------|-----|
| Fabricate statistics | December 2025 Core Update penalizes unsourced claims |
| Use the same chart type twice | Visual monotony, reduces engagement |
| Keyword-stuff headings or meta | Google ignores/penalizes this |
| Bury answers in paragraphs | AI systems extract from section openers |
| Skip source verification | Broken links and wrong data destroy trust |
| Use tier 4-5 sources | Low authority hurts E-E-A-T |
| Generate without research | AI-generated consensus content is penalized |
| Skip visual elements entirely | Blogs with images get 94% more views |
