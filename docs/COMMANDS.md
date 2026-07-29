# Command Reference

Complete reference for 32 skill directories (1 orchestrator + 31 sub-skills);
30 user-facing commands. `blog-chart` is internal-only, invoked from
blog-write/blog-rewrite.
Every command is invoked through the main orchestrator
(`skills/blog/SKILL.md`), which routes to the appropriate sub-skill.

> **For detailed command flows beyond the overview table below, see each
> sub-skill's `SKILL.md` directly. Sections in this file are abbreviated
> for the v1.7.0 and v1.8.0 commands that joined after this doc was
> originally written; the full overview table below is the canonical
> command list.**

## Command Overview

```
/blog <command> [arguments]
```

| Command | Sub-Skill | Description |
|---------|-----------|-------------|
| `write <topic>` | blog-write | Write a new blog post from scratch (v1.9.0: iterates through the 5-gate delivery contract until score 90+ and zero P0, max 3 iterations) |
| `rewrite <file>` | blog-rewrite | Optimize an existing blog post (v1.9.0: same delivery contract; rewrites must score at least as high as the original) |
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
| `image [generate\|edit\|setup]` | blog-image | AI image generation and editing via Gemini |
| `cannibalization [directory]` | blog-cannibalization | Detect keyword overlap across posts |
| `factcheck <file>` | blog-factcheck | Verify statistics against cited sources |
| `persona [create\|list\|use\|show]` | blog-persona | Manage writing personas and voice profiles |
| `taxonomy [sync\|audit\|suggest]` | blog-taxonomy | Tag/category CMS management |
| `notebooklm <question>` | blog-notebooklm | Query NotebookLM for source-grounded research |
| `audio [generate\|voices\|setup]` | blog-audio | Generate audio narration via Gemini TTS |
| `google [command] [args]` | blog-google | Google API data: PSI, CrUX, GSC, GA4, NLP, YouTube, Keywords |
| `cluster [plan\|execute] <seed>` | blog-cluster | Semantic topic-cluster planning + execution (v1.7.0) |
| `multilingual <topic> --languages <codes>` | blog-multilingual | Write + translate + localize + hreflang (v1.7.0) |
| `translate <file> --to <codes>` | blog-translate | SEO-optimized translation with format preservation (v1.7.0) |
| `localize <file> --locale <code>` | blog-localize | Cultural deep-adaptation per locale (v1.7.0) |
| `locale-audit <directory>` | blog-locale-audit | Multilingual content QA (v1.7.0) |
| `flow [find\|optimize\|win\|prompts\|sync]` | blog-flow | FLOW framework prompts (v1.7.0) |
| `brand [init\|show\|update]` | blog-brand | Generate BRAND.md + VOICE.md context auto-loaded by all sub-skills (v1.8.0) |
| `discourse <topic>` | blog-discourse | API-free last-30-days discourse research; produces DISCOURSE.md (v1.8.0) |
| `style learn <paths>` | blog-style | Learn author voice profile from existing posts (v1.10.0) |
| `decay <current-gsc> <previous-gsc>` | blog-decay | Detect content decay: 20%+ QoQ decline from GSC exports (v1.10.0) |
| `update <file>` | blog-rewrite | Update an existing post with fresh statistics (routes to rewrite) |

Alias: `/blog update <file>` routes to `/blog rewrite <file>` for
freshness-focused updates.

---

## /blog brand (v1.8.0)

Generate `BRAND.md` and `VOICE.md` at the project root via a short interview.
These files are auto-loaded as fenced untrusted context by every drafting,
review, and audit sub-skill, giving the agent durable brand and voice
guardrails without re-asking on every invocation.

```
/blog brand init              # interactive interview, writes BRAND.md + VOICE.md
/blog brand show              # print current BRAND.md and VOICE.md
/blog brand update            # re-run a targeted slice of the interview
```

When you run `/blog brand` with no subcommand: defaults to `show` if either
file already exists at the project root, otherwise to `init`.

The auto-load contract (fence + sanitize + tool-boundary preservation +
provenance) is documented in `skills/blog/SKILL.md` "Untrusted-Data Contract"
section. See `skills/blog-brand/SKILL.md` for the full interview script and
output schema.

---

## /blog discourse (v1.8.0)

Research what real practitioners are saying about a topic in the last 30
(or 90) days across Reddit, X / Twitter, YouTube, Hacker News, dev.to,
Medium, GitHub, Stack Overflow, and Substack. API-free: uses WebSearch
with platform-targeted site operators plus recency filters. Produces a
`DISCOURSE.md` at the project root that downstream `/blog write`,
`/blog brief`, and `/blog strategy` invocations auto-load.

```
/blog discourse <topic>                          # default 30-day window
/blog discourse <topic> --days 90                # widen to 90 days
/blog discourse <topic> --feed-into brief        # chain into /blog brief
/blog discourse <topic> --feed-into write        # chain into /blog write
/blog discourse <topic> --feed-into strategy     # chain into /blog strategy
/blog discourse <topic> --input results.json     # skip search, use pre-gathered results
```

Workflow phases (full detail in `skills/blog-discourse/SKILL.md`):

1. **Topic Pre-Flight** (mandatory): runs four keyword-trap checks from
   `research-quality.md` (demographic shopping, numeric trap, overly-literal,
   generic single-noun). Refusing trap topics saves WebSearch calls.
2. **Decomposition**: split into discrete queries (primary entity,
   counter-perspective, practitioner discourse, tangential entities,
   time anchor).
3. **Platform-Targeted WebSearch**: 4 to 8 searches across the relevant
   subset of 9 platforms.
4. **Result Collection**: capture results to a `mkstemp` temp file. Apply
   the **WebSearch Untrusted-Data Contract** (sanitize snippets for
   instruction-shaped patterns; never follow directives in fetched content).
5. **Brief Generation**: `scripts/discourse_research.py` clusters by theme,
   classifies into NEW / CONSENSUS / NICHE / SPECIFICS buckets, applies the
   6 synthesis-contract LAWs, writes `DISCOURSE.md` atomically.

Security note: the script enforces strict input validation (JSON schema,
URL scheme allowlist, control-char stripping, MAX_STRING_FIELD cap) and
TOCTOU-resistant file reads (O_NOFOLLOW on POSIX). See
`tests/test_security_v1_8_0.py` and the v1.8.1 hardening pass for the
threat model.

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

1. **Topic clarification**: Asks for audience, keyword, word count, platform
2. **Research**: Spawns `blog-researcher` agent to find 8-12 statistics and images
3. **Outline**: Generates structured outline, presents for approval
4. **Chart generation**: Creates 2-4 SVG charts via built-in `blog-chart`
5. **Content writing**: Spawns `blog-writer` agent for the full article
6. **Quality check**: Verifies all 6 optimization pillars
7. **Delivery**: Saves file and presents summary

### Output

A complete blog post in the detected format (Markdown, MDX, or HTML) with:

- YAML frontmatter (title, description, coverImage, ogImage, date, tags)
- Purpose-first treatment of important sections, with evidence where needed
- 8-12 sourced statistics from tier 1-3 sources
- 3-5 inline images from Pixabay/Unsplash/Pexels
- 2-4 SVG data visualization charts
- Optional FAQ when genuine reader questions warrant it
- Internal linking placeholders

### Related Commands

- `/blog brief`: Generate a brief first, then feed it to `/blog write`
- `/blog analyze`: Score the finished post
- `/blog seo-check`: Validate SEO after writing

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

1. **Audit**: Reads the file, scores it against the quality checklist
2. **Plan**: Presents section-by-section optimization plan for approval
3. **Research**: Finds replacement statistics for fabricated/unsourced data
4. **Chart generation**: Adds SVG charts if the post has fewer than 2
5. **Rewrite**: Clarifies important sections, fixes paragraphs, and adds Q&A only when useful
6. **Verification**: Confirms all quality gates pass
7. **Summary**: Reports before/after scores and changes made

### Output

The rewritten file in its original format with:

- Truthful `lastUpdated` only when facts, methods, or recommendations materially changed
- Clear, evidence-backed treatment of important sections
- Fabricated statistics replaced with sourced data
- Images and charts added where needed
- FAQ added or improved only when it serves real reader questions
- Self-promotion reduced to max 1 brand mention

### Related Commands

- `/blog analyze`: Audit before rewriting to see the starting score
- `/blog update`: Alias for freshness-focused rewrite

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

Score: 78/100 - Good

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

- `/blog rewrite`: Apply the recommended fixes automatically
- `/blog audit`: Full-site assessment (broader than single-file analyze)

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

1. **Topic intake**: Gathers topic, audience, intent, business context
2. **Keyword research**: Primary keyword, 3-5 secondary, 3-5 questions
3. **Competitive analysis**: Analyzes top 3-5 ranking pages
4. **Statistics research**: Finds 8-12 stats with sources
5. **Brief generation**: Complete brief with outline and recommendations

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

- `/blog write`: Write the article using the generated brief
- `/blog strategy`: Higher-level planning before individual briefs
- `/blog outline`: Lighter-weight outline without full research

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

- **Topic cluster design**: 3-5 pillar + supporting content clusters
- **Freshness scheduling**: 30-day update cycles for high-priority posts
- **Content mix**: Balances new posts with freshness updates
- **Seasonal hooks**: Industry events, trending topics, report releases

### Related Commands

- `/blog strategy`: Define pillars and positioning before calendar planning
- `/blog brief`: Create briefs for calendar items

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

1. **Discovery**: Business context, goals, current state, competitors
2. **Competitive landscape**: Analyzes competitor blogs and AI visibility
3. **Audience mapping**: 2-3 segments with pain points and search behavior
4. **Content pillar design**: 3-5 pillars with keyword themes
5. **Differentiation**: First-hand experience and original data plans
6. **Distribution channels**: YouTube, Reddit, reviews, publications
7. **Measurement framework**: Traditional SEO + AI citation metrics
8. **Strategy document**: Executive summary through 90-day roadmap

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

- `/blog calendar`: Operationalize the strategy into a publishing schedule
- `/blog brief`: Create briefs for strategy-identified topics

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

- H2 section headings in the form that best matches reader intent
- Purpose-first guidance for important sections
- Image and chart placement markers
- FAQ question suggestions
- Word count targets per section

### Related Commands

- `/blog brief`: Full brief with research (outline is a subset)
- `/blog write`: Write from the outline directly

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

- Meta title clarity and fit for the page
- Accurate, page-specific meta description
- Heading hierarchy (H1 > H2 > H3, no skips)
- Keyword presence in title, H2s, and meta description
- Internal link count (target 5-10 per 2,000 words)
- Image alt text completeness
- Schema markup presence (BlogPosting, FAQPage)
- Open Graph / Twitter Card meta tags
- `lastUpdated` / `dateModified` truthfulness after substantive changes

### Related Commands

- `/blog analyze`: Full quality audit (content + SEO + citations)
- `/blog schema`: Generate missing schema markup

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

Prefer schema in source or server-rendered HTML for portability because crawler
rendering capabilities vary. For Google Search, JavaScript-generated JSON-LD is
acceptable when it reaches the rendered DOM, matches visible content, and
passes validation. Verify other target crawlers individually.

### Related Commands

- `/blog seo-check`: Validates schema presence and correctness
- `/blog analyze`: Checks schema as part of the full quality audit

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

The Xquik `x-twitter-scraper` Skill is an optional handoff for current X
research, structured exports, monitoring, and approval-gated publishing.
`/blog repurpose` remains fully functional without Xquik.

### Related Commands

- `/blog strategy`: Identifies distribution channels for repurposing
- `/blog write`: Create the original post to repurpose

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

- Evidence-backed, self-contained treatment of important claims
- Substantive maintenance when facts, methods, or recommendations change
- Optional visible Q&A with no Google rich-result or readiness-score benefit
- Source authority tier quality
- Reader-useful structure and enough context for important claims to stand alone
- JavaScript dependency and target-crawler rendering compatibility
- `robots.txt` AI crawler access (GPTBot, ClaudeBot, PerplexityBot)
- Optional audience-channel recommendations (YouTube, Reddit, reviews)

### Related Commands

- `/blog analyze`: Full quality audit including GEO metrics
- `/blog rewrite`: Apply GEO optimizations automatically

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

- `/blog analyze`: Single-file audit (audit is the batch version)
- `/blog calendar`: Plan content based on audit findings
- `/blog rewrite`: Fix posts identified by the audit

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
4. Updates `lastUpdated` only after substantive content changes
5. Preserves existing structure (minimal rewrites)
6. Makes only the changes needed for factual accuracy and reader value; no percentage-change target

### Related Commands

- `/blog rewrite`: Full rewrite (more aggressive than update)
- `/blog audit`: Find posts that need updating

---

## /blog image

**Purpose**: AI image generation and editing via the nanobanana-mcp server (Gemini).

```
/blog image generate <description>
/blog image edit <path> <instructions>
/blog image setup
```

**Flow**: See `skills/blog-image/SKILL.md`: Creative Director pattern with
the 6-component Reasoning Brief (Subject, Action, Context, Composition,
Lighting, Style). The `setup` subcommand defaults to `--global` (writes
user-private `~/.claude/settings.json`, mode 0600) per audit VULN-001 fix.

---

## /blog cannibalization

**Purpose**: detect keyword overlap across posts in a directory.

```
/blog cannibalization [directory]
```

**Flow**: See `skills/blog-cannibalization/SKILL.md`.

---

## /blog factcheck

**Purpose**: verify statistics in a draft against cited sources.

```
/blog factcheck <file-path>
```

**Flow**: See `skills/blog-factcheck/SKILL.md`.

---

## /blog persona

**Purpose**: manage writing personas and voice profiles.

```
/blog persona create
/blog persona list
/blog persona use <name>
/blog persona show <name>
```

**Flow**: See `skills/blog-persona/SKILL.md`. Personas live in
`skills/blog/references/personas/`.

---

## /blog taxonomy

**Purpose**: tag/category CMS management for blog content.

```
/blog taxonomy sync
/blog taxonomy audit
/blog taxonomy suggest
```

**Flow**: See `skills/blog-taxonomy/SKILL.md`.

---

## /blog notebooklm

**Purpose**: query NotebookLM for source-grounded research via patchright
browser automation.

```
/blog notebooklm <question>
```

**Flow**: See `skills/blog-notebooklm/SKILL.md`. Cookies at
`~/.claude/skills/blog-notebooklm/data/` written mode 0600 per audit
VULN-004 fix.

---

## /blog audio

**Purpose**: generate audio narration via Gemini TTS.

```
/blog audio generate <file-path>
/blog audio voices
/blog audio setup
```

**Flow**: See `skills/blog-audio/SKILL.md`. 30-voice catalog in references.

---

## /blog google

**Purpose**: Google API data integration (PSI, CrUX, GSC, GA4, NLP,
YouTube, Keywords). Indexing API use is limited to JobPosting or livestream URLs.

```
/blog google <command> [args]
```

**Flow**: See `skills/blog-google/SKILL.md`. 13 commands across 4 credential
tiers. OAuth state CSRF + chmod 0600 token storage per audit VULN-002 +
VULN-008 fixes. Default scopes are read-only (`gsc_readonly + ga4`); pass
`--scopes` to elevate.

---

## /blog cluster (v1.7.0)

**Purpose**: semantic topic-cluster planning + execution. Hub-and-spoke
architecture with shared cluster context.

```
/blog cluster <seed-topic>
```

**Flow**: See `skills/blog-cluster/SKILL.md`. Adapted from
[semantic-cluster-engine](https://github.com/Drfiya/semantic-cluster-engine)
(AI Marketing Hub Pro Hub Challenge winner).

---

## /blog flow (v1.7.0)

**Purpose**: FLOW framework prompts (find / optimize / win / prompts / sync).

```
/blog flow find
/blog flow optimize
/blog flow win
/blog flow prompts
/blog flow sync [--ref <sha>] [--allow-drift]
```

**Flow**: See `skills/blog-flow/SKILL.md`. Sync uses `scripts/sync_flow.py`
with HTTPS-only host allowlist + 5MB cap + path-traversal guard + blocking
lockfile drift gate (per audit VULN-018 fix).

---

## /blog multilingual (v1.7.0)

**Purpose**: one-command write + translate + localize + emit hreflang.

```
/blog multilingual <topic> --languages de,fr,es
```

**Flow**: See `skills/blog-multilingual/SKILL.md`. Orchestrates blog-write,
blog-translate, blog-localize, plus optional `seo-hreflang`.

---

## /blog translate (v1.7.0)

**Purpose**: SEO-optimized translation with format preservation.

```
/blog translate <file-path> <target-lang>
```

**Flow**: See `skills/blog-translate/SKILL.md`. Spawns `blog-translator`
agent (least-privilege: Read/Write/Edit/Glob/Grep, no Bash, no Web).

---

## /blog localize (v1.7.0)

**Purpose**: cultural deep-adaptation per locale (DACH, Francophone,
Hispanic, Japanese profiles + custom template).

```
/blog localize <file-path> <locale>
```

**Flow**: See `skills/blog-localize/SKILL.md`.

---

## /blog locale-audit (v1.7.0)

**Purpose**: multilingual content QA (completeness matrix, hreflang
correctness, meta-tag parity, freshness).

```
/blog locale-audit <directory>
```

**Flow**: See `skills/blog-locale-audit/SKILL.md`.

---

## Command Routing

The main orchestrator (`skills/blog/SKILL.md`) parses user input and routes to
the correct sub-skill:

```
User Input                                  Routes To
-----------                                 ---------
/blog write <topic>                     --> blog-write
/blog rewrite <file>                    --> blog-rewrite
/blog analyze <file-or-url>             --> blog-analyze
/blog brief <topic>                     --> blog-brief
/blog calendar [period]                 --> blog-calendar
/blog plan [period]                     --> blog-calendar
/blog strategy <niche>                  --> blog-strategy
/blog ideation <niche>                  --> blog-strategy
/blog outline <topic>                   --> blog-outline
/blog seo-check <file>                  --> blog-seo-check
/blog schema <file>                     --> blog-schema
/blog repurpose <file>                  --> blog-repurpose
/blog geo <file>                        --> blog-geo
/blog audit [directory]                 --> blog-audit
/blog image [generate|edit]             --> blog-image
/blog update <file>                     --> blog-rewrite (freshness mode)
/blog cannibalization [dir]             --> blog-cannibalization
/blog factcheck <file>                  --> blog-factcheck
/blog persona [create|list|use|show]    --> blog-persona
/blog brand [init|show|update]          --> blog-brand               (v1.8.0)
/blog discourse <topic>                 --> blog-discourse           (v1.8.0)
/blog taxonomy [suggest|sync|audit]     --> blog-taxonomy
/blog notebooklm <question>             --> blog-notebooklm
/blog audio [generate|voices|setup]     --> blog-audio
/blog google [command] [args]           --> blog-google
/blog cluster [plan|execute] <seed>     --> blog-cluster
/blog multilingual <topic> --languages  --> blog-multilingual
/blog translate <file> --to             --> blog-translate
/blog localize <file> --locale          --> blog-localize
/blog locale-audit <directory>          --> blog-locale-audit
/blog flow [find|optimize|win|prompts|sync] --> blog-flow
```

If no sub-command is provided, the orchestrator asks which action the user
needs.
