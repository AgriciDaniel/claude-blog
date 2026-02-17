# Command Reference

Complete reference for all 12 `/blog` slash commands. Every command is invoked
through the main orchestrator (`blog/SKILL.md`), which routes to the appropriate
sub-skill.

## Command Overview

```
/blog <command> [arguments]
```

| Command | Sub-Skill | Description |
|---------|-----------|-------------|
| `write <topic>` | blog-write | Write a new blog post from scratch |
| `rewrite <file>` | blog-rewrite | Optimize an existing blog post |
| `analyze <file-or-url>` | blog-analyze | Audit blog quality with 0-100 score |
| `brief <topic>` | blog-brief | Generate a detailed content brief |
| `calendar [monthly\|quarterly]` | blog-calendar | Generate an editorial calendar |
| `strategy <niche>` | blog-strategy | Blog strategy and topic ideation |
| `outline <topic>` | blog-outline | SERP-informed outline generation |
| `seo-check <file>` | blog-seo-check | Post-writing SEO validation |
| `schema <file>` | blog-schema | Generate JSON-LD schema markup |
| `repurpose <file>` | blog-repurpose | Repurpose content for other platforms |
| `geo <file>` | blog-geo | AI citation optimization audit |
| `audit [directory]` | blog-audit | Full-site blog health assessment |
| `update <file>` | blog-rewrite | Freshness update (alias for rewrite) |

---

## /blog write

Write a new blog post from scratch, fully optimized for Google rankings and
AI citation platforms.

### Usage

```
/blog write <topic>
/blog write "How to Optimize for AI Search in 2026"
/blog write kubernetes monitoring --format mdx --words 3000
```

### Workflow

1. **Topic clarification** -- Asks for audience, keyword, word count, platform
2. **Research** -- Spawns `blog-researcher` agent to find 8-12 statistics and images
3. **Outline** -- Generates structured outline, presents for approval
4. **Chart generation** -- Creates 2-4 SVG charts via `/svg-chart`
5. **Content writing** -- Spawns `blog-writer` agent for the full article
6. **Quality check** -- Verifies all 6 optimization pillars
7. **Delivery** -- Saves file and presents summary

### Output

A complete blog post in the detected format (Markdown, MDX, or HTML) with:

- YAML frontmatter (title, description, coverImage, ogImage, date, tags)
- Answer-first formatting on every H2 section
- 8-12 sourced statistics from tier 1-3 sources
- 3-5 inline images from Pixabay/Unsplash/Pexels
- 2-4 SVG data visualization charts
- FAQ section with 3-5 items
- Internal linking placeholders

### Related Commands

- `/blog brief` -- Generate a brief first, then feed it to `/blog write`
- `/blog analyze` -- Score the finished post
- `/blog seo-check` -- Validate SEO after writing

---

## /blog rewrite

Optimize an existing blog post for rankings and AI citations while preserving
the author's voice and unique perspective.

### Usage

```
/blog rewrite <file>
/blog rewrite content/blog/my-post.mdx
/blog rewrite posts/old-article.md
```

### Workflow

1. **Audit** -- Reads the file, scores it against the quality checklist
2. **Plan** -- Presents section-by-section optimization plan for approval
3. **Research** -- Finds replacement statistics for fabricated/unsourced data
4. **Chart generation** -- Adds SVG charts if the post has fewer than 2
5. **Rewrite** -- Applies answer-first formatting, fixes paragraphs, adds FAQ
6. **Verification** -- Confirms all quality gates pass
7. **Summary** -- Reports before/after scores and changes made

### Output

The rewritten file in its original format with:

- Updated `lastUpdated` date in frontmatter
- Answer-first paragraphs on all H2 sections
- Fabricated statistics replaced with sourced data
- Images and charts added where needed
- FAQ section added or improved
- Self-promotion reduced to max 1 brand mention

### Related Commands

- `/blog analyze` -- Audit before rewriting to see the starting score
- `/blog update` -- Alias for freshness-focused rewrite

---

## /blog analyze

Audit a blog post's quality with a 0-100 score across 6 categories, with
prioritized improvement recommendations.

### Usage

```
/blog analyze <file>
/blog analyze <url>
/blog analyze content/blog/ --batch
```

### Input Types

| Input | Behavior |
|-------|----------|
| Local file (`.md`, `.mdx`, `.html`) | Reads and analyzes directly |
| URL | Fetches via WebFetch, extracts content |
| Directory (with `--batch`) | Scans all blog files, produces summary table |

### Output

```
Blog Quality Report: [Title]

Score: 78/100 -- Good

Score Breakdown
| Category               | Score | Max |
|------------------------|-------|-----|
| Content Quality        | 21    | 25  |
| Answer-First Format    | 15    | 20  |
| Statistics & Citations | 18    | 20  |
| Visual Elements        | 10    | 15  |
| Schema & Structure     | 7     | 10  |
| Freshness & Trust      | 7     | 10  |

Issues Found (prioritized: Critical > High > Medium > Low)
Recommended Actions (top 3 highest-impact fixes)
```

### Batch Mode Output

When given a directory, produces a ranked summary table of all posts with
scores, ratings, and top issues. Posts are sorted lowest-score-first as a
priority queue for optimization.

### Python Script

The `analyze_blog.py` script provides automated metrics:

```bash
python3 ~/.claude/skills/blog/scripts/analyze_blog.py post.md
python3 ~/.claude/skills/blog/scripts/analyze_blog.py posts/ --batch
python3 ~/.claude/skills/blog/scripts/analyze_blog.py post.md -o report.json
```

### Related Commands

- `/blog rewrite` -- Apply the recommended fixes automatically
- `/blog audit` -- Full-site assessment (broader than single-file analyze)

---

## /blog brief

Generate a comprehensive content brief with keywords, competitive analysis,
statistics research, visual element planning, and a structured outline.

### Usage

```
/blog brief <topic>
/blog brief "cloud cost optimization for startups"
/blog brief ai-search-optimization --audience "marketing managers"
```

### Workflow

1. **Topic intake** -- Gathers topic, audience, intent, business context
2. **Keyword research** -- Primary keyword, 3-5 secondary, 3-5 questions
3. **Competitive analysis** -- Analyzes top 3-5 ranking pages
4. **Statistics research** -- Finds 8-12 stats with sources
5. **Brief generation** -- Complete brief with outline and recommendations

### Output

A detailed brief document saved to `briefs/[slug]-brief.md` containing:

- Target keywords (primary, secondary, questions)
- Search intent analysis
- Content parameters (word count, format, chart/image counts)
- Recommended title options and meta description
- Full content outline with section-level guidance
- Statistics table with sources pre-researched
- Visual element plan (chart types, image search terms)
- Competitive gaps to exploit
- Internal linking opportunities
- E-E-A-T signals to include
- Distribution notes (Reddit, YouTube, social)

### Related Commands

- `/blog write` -- Write the article using the generated brief
- `/blog strategy` -- Higher-level planning before individual briefs
- `/blog outline` -- Lighter-weight outline without full research

---

## /blog calendar

Generate an editorial calendar with topic clusters, publishing schedules,
freshness update plans, and seasonal opportunities.

### Usage

```
/blog calendar
/blog calendar monthly
/blog calendar quarterly
/blog calendar --niche "devops tooling" --cadence 3
```

### Output Formats

**Monthly calendar**: Week-by-week table with post type (New/Update), title,
topic cluster, target keyword, and status. Includes freshness update queue
and seasonal hooks.

**Quarterly calendar**: Three-month plan with cluster focus per month,
content velocity targets, quarterly goals, and distribution plan.

### Key Features

- **Topic cluster design** -- 3-5 pillar + supporting content clusters
- **Freshness scheduling** -- 30-day update cycles for high-priority posts
- **Content mix** -- Balances new posts with freshness updates
- **Seasonal hooks** -- Industry events, trending topics, report releases

### Related Commands

- `/blog strategy` -- Define pillars and positioning before calendar planning
- `/blog brief` -- Create briefs for calendar items

---

## /blog strategy

Develop a comprehensive blog strategy with content pillars, audience mapping,
competitive landscape analysis, and distribution planning.

### Usage

```
/blog strategy <niche>
/blog strategy "B2B SaaS marketing"
/blog strategy ecommerce --competitors "shopify,bigcommerce,woocommerce"
```

### Workflow

1. **Discovery** -- Business context, goals, current state, competitors
2. **Competitive landscape** -- Analyzes competitor blogs and AI visibility
3. **Audience mapping** -- 2-3 segments with pain points and search behavior
4. **Content pillar design** -- 3-5 pillars with keyword themes
5. **Differentiation** -- First-hand experience and original data plans
6. **Distribution channels** -- YouTube, Reddit, reviews, publications
7. **Measurement framework** -- Traditional SEO + AI citation metrics
8. **Strategy document** -- Executive summary through 90-day roadmap

### Output

A full strategy document with:

- Audience segments with AI behavior analysis
- Content pillars with estimated post counts
- Competitive positioning and gaps
- Distribution channel priorities with tactics
- Content velocity recommendations
- 90-day implementation roadmap
- KPIs across SEO, AI citation, quality, and business impact

### Related Commands

- `/blog calendar` -- Operationalize the strategy into a publishing schedule
- `/blog brief` -- Create briefs for strategy-identified topics

---

## /blog outline

Generate a SERP-informed content outline by analyzing what currently ranks for
the target keyword.

### Usage

```
/blog outline <topic>
/blog outline "react server components best practices"
```

### Output

A structured outline with:

- H2 section headings (60-70% question format)
- Answer-first guidance per section
- Image and chart placement markers
- FAQ question suggestions
- Word count targets per section

### Related Commands

- `/blog brief` -- Full brief with research (outline is a subset)
- `/blog write` -- Write from the outline directly

---

## /blog seo-check

Post-writing SEO validation that checks technical SEO elements beyond content
quality.

### Usage

```
/blog seo-check <file>
/blog seo-check content/blog/new-post.mdx
```

### Checks Performed

- Meta title length (under 60 characters)
- Meta description length (150-160 characters with statistic)
- Heading hierarchy (H1 > H2 > H3, no skips)
- Keyword presence in title, H2s, and meta description
- Internal link count (target 5-10 per 2,000 words)
- Image alt text completeness
- Schema markup presence (BlogPosting, FAQPage)
- Open Graph / Twitter Card meta tags
- `lastUpdated` / `dateModified` freshness signal

### Related Commands

- `/blog analyze` -- Full quality audit (content + SEO + citations)
- `/blog schema` -- Generate missing schema markup

---

## /blog schema

Generate JSON-LD structured data markup for a blog post.

### Usage

```
/blog schema <file>
/blog schema content/blog/my-post.mdx
```

### Generated Schema Types

| Schema Type | When Generated |
|-------------|---------------|
| BlogPosting | Always (primary) |
| FAQPage | When FAQ section detected |
| BreadcrumbList | When site structure available |
| Person | When author information available |
| Organization | When company context available |

### Output

JSON-LD `<script>` blocks ready for injection into the page `<head>` or
component. Includes `datePublished`, `dateModified`, `author`, `image`,
and FAQ items.

### Important

Schema must appear in HTML source (server-rendered), not injected via
client-side JavaScript. AI crawlers (GPTBot, ClaudeBot, PerplexityBot) do
not execute JavaScript.

### Related Commands

- `/blog seo-check` -- Validates schema presence and correctness
- `/blog analyze` -- Checks schema as part of the full quality audit

---

## /blog repurpose

Repurpose a blog post into content for other platforms and formats.

### Usage

```
/blog repurpose <file>
/blog repurpose content/blog/ai-search-guide.mdx
```

### Output Formats

| Platform | Format |
|----------|--------|
| Twitter/X | Thread (5-10 tweets with key insights) |
| LinkedIn | Article or post with professional angle |
| Reddit | Discussion-starter post for relevant subreddits |
| YouTube | Video script outline with talking points |
| Newsletter | Email digest version with CTA |
| Podcast | Interview/discussion script based on post content |

### Related Commands

- `/blog strategy` -- Identifies distribution channels for repurposing
- `/blog write` -- Create the original post to repurpose

---

## /blog geo

AI citation optimization audit. Analyzes a blog post specifically for
visibility on AI platforms (ChatGPT, Perplexity, Google AI Overviews).

### Usage

```
/blog geo <file>
/blog geo content/blog/my-post.mdx
```

### Checks Performed

- Answer-first formatting (critical for +340% AI citations)
- Content freshness (76% of top citations updated within 30 days)
- FAQ schema presence (+28% AI citations)
- Source authority tier quality
- Content extractability (50-150 word chunks)
- JavaScript dependency (AI crawlers cannot execute JS)
- `robots.txt` AI crawler access (GPTBot, ClaudeBot, PerplexityBot)
- Off-site signal recommendations (YouTube, Reddit, reviews)

### Related Commands

- `/blog analyze` -- Full quality audit including GEO metrics
- `/blog rewrite` -- Apply GEO optimizations automatically

---

## /blog audit

Full-site blog health assessment. Scans an entire directory of blog posts
and produces a comprehensive report.

### Usage

```
/blog audit
/blog audit content/blog/
/blog audit posts/ --format markdown
```

### Output

- **Summary table**: Every post scored and rated
- **Priority queue**: Posts ranked lowest-score-first for optimization
- **Category breakdown**: Site-wide averages per scoring category
- **Common issues**: Most frequent problems across all posts
- **Freshness report**: Posts overdue for updates (>30 days)
- **Topic coverage**: Cluster analysis and gap identification

### Related Commands

- `/blog analyze` -- Single-file audit (audit is the batch version)
- `/blog calendar` -- Plan content based on audit findings
- `/blog rewrite` -- Fix posts identified by the audit

---

## /blog update

Alias for `/blog rewrite` with a freshness-focused mode. Minimizes structural
changes and focuses on updating data and signals.

### Usage

```
/blog update <file>
/blog update content/blog/old-post.mdx
```

### What It Does

1. Updates statistics to latest available data (2025-2026)
2. Adds new developments since last update
3. Refreshes images if older than 1 year
4. Updates `lastUpdated` in frontmatter
5. Preserves existing structure (minimal rewrites)
6. Targets at least 30% content change for AI freshness signals

### Related Commands

- `/blog rewrite` -- Full rewrite (more aggressive than update)
- `/blog audit` -- Find posts that need updating

---

## Command Routing

The main orchestrator (`blog/SKILL.md`) parses user input and routes to
the correct sub-skill:

```
User Input                        Routes To
-----------                       ---------
/blog write <topic>           --> blog-write
/blog rewrite <file>          --> blog-rewrite
/blog analyze <file-or-url>   --> blog-analyze
/blog audit <file-or-url>     --> blog-analyze
/blog brief <topic>           --> blog-brief
/blog calendar [period]       --> blog-calendar
/blog plan [period]           --> blog-calendar
/blog strategy <niche>        --> blog-strategy
/blog ideation <niche>        --> blog-strategy
/blog outline <topic>         --> blog-outline
/blog seo-check <file>        --> blog-seo-check
/blog schema <file>           --> blog-schema
/blog repurpose <file>        --> blog-repurpose
/blog geo <file>              --> blog-geo
/blog audit [directory]       --> blog-audit
/blog update <file>           --> blog-rewrite (freshness mode)
```

If no sub-command is provided, the orchestrator asks which action the user
needs.
