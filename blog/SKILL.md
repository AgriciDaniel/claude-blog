---
name: blog
description: >
  Full-lifecycle blog engine with 12 commands, 12 content templates, 5-category
  100-point scoring, and 4 specialized agents. Optimized for Google rankings
  (December 2025 Core Update, E-E-A-T) and AI citations (GEO/AEO). Writes,
  rewrites, analyzes, outlines, audits, and repurposes blog content with
  answer-first formatting, sourced statistics, Pixabay/Unsplash/Pexels images,
  built-in SVG chart generation, JSON-LD schema generation, and freshness signals.
  Supports any platform (WordPress, Next.js MDX, Hugo, Ghost, Astro, Jekyll,
  11ty, Gatsby, HTML). Use when user says "blog", "write blog", "blog post",
  "blog strategy", "content brief", "editorial calendar", "analyze blog",
  "rewrite blog", "update blog", "blog SEO", "blog optimization", "content plan",
  "blog outline", "seo check", "schema markup", "repurpose", "geo audit",
  "blog audit", "citation readiness".
user-invocable: true
argument-hint: "[write|rewrite|analyze|brief|calendar|strategy|outline|seo-check|schema|repurpose|geo|audit] [topic-or-file]"
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

Full-lifecycle blog management: strategy, briefs, outlines, writing, analysis,
optimization, schema generation, repurposing, and editorial planning. Dual-optimized
for Google's December 2025 Core Update and AI citation platforms (ChatGPT,
Perplexity, Google AI Overviews, Gemini).

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/blog write <topic>` | Write a new blog post from scratch |
| `/blog rewrite <file>` | Rewrite/optimize an existing blog post |
| `/blog analyze <file-or-url>` | Audit blog quality with 0-100 score |
| `/blog brief <topic>` | Generate a detailed content brief |
| `/blog calendar [monthly\|quarterly]` | Generate an editorial calendar |
| `/blog strategy <niche>` | Blog strategy and topic ideation |
| `/blog outline <topic>` | Generate SERP-informed content outline |
| `/blog seo-check <file>` | Post-writing SEO validation checklist |
| `/blog schema <file>` | Generate JSON-LD schema markup |
| `/blog repurpose <file>` | Repurpose content for other platforms |
| `/blog geo <file>` | AI citation readiness audit |
| `/blog audit [directory]` | Full-site blog health assessment |
| `/blog update <file>` | Update existing post with fresh stats (routes to rewrite) |

## Orchestration Logic

### Command Routing

1. Parse the user's command to determine the sub-skill
2. If no sub-command given, ask which action they need
3. Route to the appropriate sub-skill:
   - `write` → `blog-write` (new articles from scratch)
   - `rewrite` → `blog-rewrite` (optimize existing posts)
   - `analyze` → `blog-analyze` (quality scoring)
   - `brief` → `blog-brief` (content briefs)
   - `calendar` / `plan` → `blog-calendar` (editorial calendars)
   - `strategy` / `ideation` → `blog-strategy` (positioning and topics)
   - `outline` → `blog-outline` (SERP-informed outlines)
   - `seo-check` / `seo` → `blog-seo-check` (SEO validation)
   - `schema` → `blog-schema` (JSON-LD generation)
   - `repurpose` → `blog-repurpose` (cross-platform content)
   - `geo` / `aeo` / `citation` → `blog-geo` (AI citation audit)
   - `audit` / `health` → `blog-audit` (site-wide assessment)
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
| `.njk` files, `.eleventy.js` | 11ty | Nunjucks/Markdown |
| `gatsby-config.js` | Gatsby | MDX/React |

Adapt output format to detected platform. Default to standard markdown if unknown.

## Core Methodology -- The 6 Pillars

Every blog post targets these 6 optimization pillars:

| Pillar | Impact | Implementation |
|--------|--------|---------------|
| Answer-First Formatting | +340% AI citations | Every H2 opens with 40-60 word stat-rich paragraph |
| Real Sourced Data | E-E-A-T trust | Tier 1-3 sources only, inline attribution |
| Visual Media | Engagement + citations | Pixabay/Unsplash images + built-in SVG chart generation |
| FAQ Schema | +28% AI citations | Structured FAQ with 40-60 word answers |
| Content Structure | AI extractability | 50-150 word chunks, question headings, proper H hierarchy |
| Freshness Signals | 76% of top citations | Updated within 30 days, dateModified schema |

## Quality Gates

These are hard rules. Never ship content that violates them:

| Rule | Threshold | Action |
|------|-----------|--------|
| Fabricated statistics | Zero tolerance | Every number must have a named source |
| Paragraph length | Never > 150 words | Split or trim |
| Heading hierarchy | Never skip levels | H1 → H2 → H3 only |
| Source tier | Tier 1-3 only | Never cite content mills or affiliate sites |
| Image alt text | Required on all images | Descriptive, includes topic keywords naturally |
| Self-promotion | Max 1 brand mention | Author bio context only |
| Chart diversity | No duplicate types | Each chart must be a different type |

## Scoring Methodology

Blog quality is scored across 5 categories (100 points total):

| Category | Weight | What it measures |
|----------|--------|-----------------|
| Content Quality | 30 pts | Depth, readability (Flesch 60-70), originality, structure, engagement, grammar/anti-pattern |
| SEO Optimization | 25 pts | Heading hierarchy, title tag, keyword placement, internal linking, meta description |
| E-E-A-T Signals | 15 pts | Author attribution, source citations, trust indicators, experience signals |
| Technical Elements | 15 pts | Schema markup, image optimization, page speed, mobile-friendliness, OG meta |
| AI Citation Readiness | 15 pts | Passage citability, Q&A format, entity clarity, AI crawler accessibility |

### Scoring Bands

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | Exceptional | Publish as-is, flagship content |
| 80-89 | Strong | Minor polish, ready for publication |
| 70-79 | Acceptable | Targeted improvements needed |
| 60-69 | Below Standard | Significant rework required |
| < 60 | Rewrite | Fundamental issues, start from outline |

## Reference Files

Load on-demand as needed (12 references):

- `references/google-landscape-2026.md` -- December 2025 Core Update, E-E-A-T, algorithm changes
- `references/geo-optimization.md` -- GEO/AEO techniques, AI citation factors
- `references/content-rules.md` -- Structure, readability, answer-first formatting
- `references/visual-media.md` -- Image sourcing (Pixabay, Unsplash, Pexels) + SVG chart integration
- `references/quality-scoring.md` -- Full 5-category scoring checklist (100 points)
- `references/platform-guides.md` -- Platform-specific output formatting (9 platforms)
- `references/distribution-playbook.md` -- Content distribution strategy (Reddit, YouTube, LinkedIn, etc.)
- `references/content-templates.md` -- Content type template index (12 templates)
- `references/eeat-signals.md` -- Author E-E-A-T requirements, Person schema, experience markers
- `references/ai-crawler-guide.md` -- AI bot management, robots.txt, SSR requirements
- `references/schema-stack.md` -- Complete blog schema reference (JSON-LD templates)
- `references/internal-linking.md` -- Link architecture, anchor text, hub-and-spoke model

## Content Templates

12 structural templates for different content types. Auto-selected by `blog-write` and `blog-brief`:

| Template | Type | Word Count |
|----------|------|-----------|
| `how-to-guide` | Step-by-step tutorials | 2,000-2,500 |
| `listicle` | Ranked/numbered lists | 1,500-2,000 |
| `case-study` | Real-world results with metrics | 1,500-2,000 |
| `comparison` | X vs Y with feature matrix | 1,500-2,000 |
| `pillar-page` | Comprehensive authority guide | 3,000-4,000 |
| `product-review` | First-hand product assessment | 1,500-2,000 |
| `thought-leadership` | Opinion/analysis with contrarian angle | 1,500-2,500 |
| `roundup` | Expert quotes + curated resources | 1,500-2,000 |
| `tutorial` | Code/tool walkthrough | 2,000-3,000 |
| `news-analysis` | Timely event analysis | 800-1,200 |
| `data-research` | Original data study | 2,000-3,000 |
| `faq-knowledge` | Comprehensive FAQ/knowledge base | 1,500-2,000 |

Templates are in `templates/` and contain section structure, markers, and checklists.

## Sub-Skills

| Sub-Skill | Purpose |
|-----------|---------|
| `blog-write` | Write new blog articles with template selection, TL;DR, citation capsules |
| `blog-rewrite` | Optimize existing posts with AI detection, anti-AI patterns |
| `blog-analyze` | 5-category 100-point quality audit with AI content detection |
| `blog-brief` | Content briefs with template recommendation, distribution plan |
| `blog-calendar` | Editorial calendars with decay detection, 60/30/10 content mix |
| `blog-strategy` | Positioning, topic clusters, AI citation surface strategy |
| `blog-outline` | SERP-informed outlines with competitive gap analysis |
| `blog-seo-check` | Post-writing SEO validation (title, meta, headings, links, OG) |
| `blog-schema` | JSON-LD schema generation (BlogPosting, Person, FAQ, Breadcrumb) |
| `blog-repurpose` | Cross-platform repurposing (social, email, YouTube, Reddit) |
| `blog-geo` | AI citation readiness audit with 0-100 GEO score |
| `blog-audit` | Full-site blog health assessment with parallel subagents |
| `blog-chart` | Generate inline SVG data visualization charts with dark-mode styling |

## Agents

| Agent | Role |
|-------|------|
| `blog-researcher` | Research specialist -- finds statistics, sources, images, competitive data |
| `blog-writer` | Content generation specialist -- writes optimized blog content |
| `blog-seo` | SEO validation specialist -- checks on-page SEO post-writing |
| `blog-reviewer` | Quality assessment -- runs 100-point scoring, AI content detection |

### Agent Details

**blog-researcher**: Runs as a Task subagent. Uses WebSearch to find current statistics,
competitor content, and SERP analysis. Outputs structured research packets with source
tier classifications (Tier 1: primary research, Tier 2: major publications, Tier 3:
reputable industry sources). Also sources Pixabay/Unsplash/Pexels image URLs.

**blog-writer**: Receives research packets and content briefs. Writes content using the
selected template structure. Applies answer-first formatting, citation capsules, and
TL;DR blocks. Outputs platform-formatted content ready for the SEO agent.

**blog-seo**: Post-writing validation agent. Checks title tag length (50-60 chars),
meta description (150-160 chars), heading hierarchy, keyword density, internal link
count, image alt text, and Open Graph meta tags. Returns pass/fail checklist.

**blog-reviewer**: Final quality gate. Runs the full 5-category 100-point scoring
rubric. Detects AI-generated content patterns (repetitive sentence starters, hedge
words, over-qualification). Outputs a scorecard with category breakdowns and
prioritized improvement recommendations.

## Execution Flow

Standard execution order for `/blog write`:

1. **Parse** -- Identify topic, detect platform, select template
2. **Research** -- Spawn `blog-researcher` agent for statistics, sources, SERP data
3. **Outline** -- Build section structure from template + research gaps
4. **Write** -- Spawn `blog-writer` agent with research packet and outline
5. **Optimize** -- Spawn `blog-seo` agent for on-page validation
6. **Score** -- Spawn `blog-reviewer` agent for 100-point quality audit
7. **Deliver** -- Output final content with scorecard and improvement notes

For `/blog analyze`, only steps 1 and 6 run (read + score).
For `/blog audit`, step 6 runs in parallel across all posts in the directory.

### Internal Workflows (Not User-Facing Commands)

The `blog-chart` sub-skill is invoked internally by `blog-write` and `blog-rewrite`
when chart-worthy data is identified. It is not a standalone slash command.
Users do not need to call it directly.

## Integration

Chart generation is built-in — no external dependencies required for full functionality.

**Optional companion skills** (for deeper analysis of published pages):
- `/seo` — Full SEO audit of published blog pages
- `/seo-schema` — Schema markup validation and generation
- `/seo-geo` — AI citation optimization audit

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
