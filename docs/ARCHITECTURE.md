# Architecture

System design documentation for `claude-blog`, covering component types,
data flow, scoring methodology, file conventions, and extension points.

---

## System Overview

```
                        +-----------------------------+
                        |         User Input          |
                        |   /blog <command> [args]    |
                        +-------------+---------------+
                                      |
                                      v
                        +-----------------------------+
                        |    Main Orchestrator        |
                        |      blog/SKILL.md          |
                        |                             |
                        |  - Command parsing          |
                        |  - Platform detection       |
                        |  - Sub-skill routing        |
                        |  - Quality gate enforcement |
                        +------+----------+-----------+
                               |          |
              +----------------+          +----------------+
              |                                            |
              v                                            v
+----------------------------+            +---------------------------+
|     12 Sub-Skills          |            |    On-Demand References   |
|  skills/blog-*/SKILL.md   |            |  blog/references/*.md     |
|                            |            |  blog/templates/*.md      |
|  write    rewrite          |            |                           |
|  analyze  brief            |            |  Loaded as needed         |
|  calendar strategy         |            |  (RAG-style pattern)      |
|  outline  seo-check        |            +---------------------------+
|  schema   repurpose        |
|  geo      audit            |
+------+----------+----------+
       |          |
       v          v
+------------------+  +------------------+
|  4 Subagents     |  |  Python Script   |
|  agents/*.md     |  |  analyze_blog.py |
|                  |  |                  |
|  blog-researcher |  |  Automated       |
|  blog-writer     |  |  quality metrics |
|  blog-seo        |  |  and scoring     |
|  blog-reviewer   |  +------------------+
+------------------+
```

---

## Component Types

### 1. Main Orchestrator

**File**: `blog/SKILL.md`

The entry point for all `/blog` commands. Responsibilities:

- Parse user input to identify the sub-command and arguments
- Detect the blog platform from project structure (MDX, Hugo, Jekyll, etc.)
- Route to the appropriate sub-skill
- Enforce quality gates (hard rules that never ship content violating them)
- Load reference files on demand

The orchestrator is a Claude Code skill with YAML frontmatter defining its
name, description, trigger phrases, and allowed tools.

### 2. Sub-Skills (12)

**Location**: `skills/blog-*/SKILL.md`

Each sub-skill is a standalone Claude Code skill with its own:

- YAML frontmatter (name, description, allowed-tools)
- Detailed workflow (step-by-step instructions)
- Input/output specifications
- Quality checks

| Sub-Skill | Responsibility |
|-----------|---------------|
| blog-write | New article generation with full optimization |
| blog-rewrite | Existing post optimization preserving author voice |
| blog-analyze | Quality audit with 0-100 scoring |
| blog-brief | Content brief generation with research |
| blog-calendar | Editorial calendar planning |
| blog-strategy | Blog positioning and content architecture |
| blog-outline | SERP-informed outline generation |
| blog-seo-check | Post-writing SEO validation |
| blog-schema | JSON-LD schema markup generation |
| blog-repurpose | Cross-platform content repurposing |
| blog-geo | AI citation optimization audit |
| blog-audit | Full-site blog health assessment |

### 3. Subagents (4)

**Location**: `agents/blog-*.md`

Specialized agents spawned by sub-skills via Claude Code's `Task` tool.
Each agent has a focused role with a restricted tool set.

| Agent | Tools | Role |
|-------|-------|------|
| blog-researcher | WebSearch, WebFetch, Read, Grep, Glob | Find statistics, images, competitive data |
| blog-writer | Read, Write, Edit, Grep, Glob | Write and rewrite optimized content |
| blog-seo | Read, WebFetch, Grep, Glob | Technical SEO analysis and validation |
| blog-reviewer | Read, Grep, Glob | Quality review and scoring |

Agents are defined as markdown files with YAML frontmatter specifying their
name, description, and available tools.

### 4. Reference Files (12)

**Location**: `blog/references/*.md`

Knowledge documents loaded on demand (not preloaded). Each reference covers
a specific optimization domain:

| Reference | Domain |
|-----------|--------|
| google-landscape-2026.md | December 2025 Core Update, E-E-A-T, algorithm changes |
| geo-optimization.md | GEO/AEO techniques, AI citation factors |
| content-rules.md | Structure, readability, answer-first formatting |
| visual-media.md | Image sourcing (Pixabay, Unsplash) + SVG chart integration |
| quality-scoring.md | Full scoring checklist with point values |
| eeat-signals.md | E-E-A-T demonstration techniques |
| content-templates.md | Template selection and customization guide |
| ai-crawler-guide.md | AI crawler behavior and technical requirements |
| schema-stack.md | JSON-LD schema type reference |
| platform-guides.md | Platform-specific formatting (MDX, Hugo, Ghost, etc.) |
| distribution-playbook.md | Off-site distribution tactics |
| internal-linking.md | Internal link strategy and implementation |

### 5. Content Templates (12)

**Location**: `blog/templates/*.md`

Structural templates for different content types. Each template defines
section structure, word count targets, and format-specific guidance.
See [TEMPLATES.md](TEMPLATES.md) for the full reference.

### 6. Python Analysis Script

**File**: `scripts/analyze_blog.py`

Standalone Python script for automated quality metrics. Runs outside Claude
Code's context as a CLI tool. Provides:

- Frontmatter extraction
- Heading structure analysis
- Paragraph length measurement
- Image and chart counting
- Citation detection and source counting
- FAQ section detection
- Self-promotion pattern matching
- 0-100 quality scoring across 6 categories
- Batch mode for directory scanning
- JSON, markdown, and table output formats

---

## Data Flow

### Write Flow

```
/blog write "topic"
      |
      v
  Orchestrator (blog/SKILL.md)
      |
      +-- Loads: references/content-rules.md
      |         references/visual-media.md
      |         templates/[auto-selected].md
      |
      +-- Spawns: blog-researcher agent
      |   |
      |   +-- WebSearch: finds 8-12 statistics
      |   +-- WebSearch: finds 3-5 Pixabay/Unsplash images
      |   +-- WebFetch: verifies sources and URLs
      |   +-- Returns: structured research data
      |
      +-- Presents outline for user approval
      |
      +-- Invokes: /svg-chart (2-4 charts)
      |
      +-- Spawns: blog-writer agent
      |   |
      |   +-- Writes full article with:
      |   |   - Answer-first formatting
      |   |   - Sourced statistics
      |   |   - Image embeds
      |   |   - Chart embeds
      |   |   - FAQ section
      |   +-- Returns: complete article
      |
      +-- Quality verification (all 6 pillars)
      |
      +-- Writes file to user's project
      |
      v
  Delivery summary
```

### Analyze Flow

```
/blog analyze "file.md"
      |
      v
  Orchestrator --> blog-analyze sub-skill
      |
      +-- Reads target file
      |
      +-- Loads: references/quality-scoring.md
      |
      +-- Runs: analyze_blog.py (if Python available)
      |   |
      |   +-- Returns: JSON metrics
      |
      +-- Manual scoring (6 categories, 100 points)
      |
      +-- Generates prioritized recommendations
      |
      v
  Quality report with score and action items
```

---

## On-Demand Reference Loading (RAG Pattern)

Reference files are NOT preloaded into context. The orchestrator and sub-skills
load them selectively based on the current task:

```
Task                    References Loaded
----                    -----------------
/blog write             content-rules, visual-media, quality-scoring
/blog rewrite           content-rules, quality-scoring
/blog analyze           quality-scoring
/blog brief             content-rules, geo-optimization
/blog strategy          geo-optimization, google-landscape-2026
/blog geo               geo-optimization, ai-crawler-guide
/blog schema            schema-stack
/blog seo-check         google-landscape-2026, schema-stack
```

This pattern keeps context usage efficient. Only the knowledge relevant to
the current operation is loaded.

---

## Scoring Methodology

Blog quality is measured across 5 categories totaling 100 points. The
`analyze_blog.py` script and the `blog-analyze` sub-skill both use this
framework.

### Category Weights

```
Content Quality (30 pts)  ############################--
SEO Signals (25 pts)      #########################-----
E-E-A-T (15 pts)          ###############---------------
Technical (15 pts)        ###############---------------
AI Citation (15 pts)      ###############---------------
                          |    |    |    |    |    |
                          0   20   40   60   80  100
```

### Scoring Bands

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | Excellent | Publish as-is |
| 75-89 | Good | Minor tweaks needed |
| 60-74 | Needs Work | Significant improvements required |
| < 60 | Poor | Full rewrite recommended |

### Quality Gates (Hard Rules)

These are non-negotiable. Content violating any of these must not be published:

| Gate | Threshold |
|------|-----------|
| Fabricated statistics | Zero tolerance |
| Paragraph length | Never > 100 words |
| Heading hierarchy | Never skip levels (H1 > H2 > H3) |
| Source tier | Tier 1-3 only |
| Image alt text | Required on all images |
| Self-promotion | Max 1 brand mention |
| Chart diversity | No duplicate chart types per post |

---

## Platform Detection

The orchestrator auto-detects the blog platform from project signals:

| Signal | Platform | Output Format |
|--------|----------|---------------|
| `.mdx` files + `next.config` | Next.js/MDX | JSX-compatible markdown |
| `.md` files + `hugo.toml` | Hugo | Standard markdown |
| `.md` files + `_config.yml` | Jekyll | Markdown with YAML front matter |
| `.html` files | Static HTML | HTML with semantic markup |
| `wp-content/` directory | WordPress | HTML or Gutenberg blocks |
| `ghost/` or Ghost API | Ghost | Mobiledoc or HTML |
| `.astro` files | Astro | MDX or markdown |
| No signals detected | Default | Standard markdown |

Platform detection affects:

- Frontmatter format and field names
- Image embedding syntax (markdown vs `<Image>` component)
- Chart embedding format (HTML SVG vs JSX SVG with camelCase)
- Schema injection method

---

## File Naming Conventions

| Component | Location | Naming |
|-----------|----------|--------|
| Main skill | `blog/SKILL.md` | Fixed name |
| Sub-skills | `skills/blog-<command>/SKILL.md` | Prefix `blog-` + command name |
| Agents | `agents/blog-<role>.md` | Prefix `blog-` + role name |
| References | `blog/references/<topic>.md` | Kebab-case topic name |
| Templates | `blog/templates/<type>.md` | Kebab-case content type |
| Scripts | `scripts/<name>.py` | Snake-case script name |

---

## Extension Points

### Adding a New Command

1. Create `skills/blog-<name>/SKILL.md` with YAML frontmatter
2. Add routing logic to `blog/SKILL.md` orchestrator
3. Update `install.sh` and `install.ps1` to copy the new sub-skill
4. Update `uninstall.sh` to remove it

### Adding a New Agent

1. Create `agents/blog-<role>.md` with YAML frontmatter
2. Define the tool set (keep it minimal for the role)
3. Reference the agent from sub-skills that need it

### Adding a New Reference

1. Create `blog/references/<topic>.md`
2. Document when to load it in the orchestrator
3. Update `install.sh` to copy the new reference file

### Adding a New Template

1. Create `blog/templates/<type>.md`
2. Define section structure, markers, and word count targets
3. Add template selection logic to `blog-write`

---

## Installed Directory Tree

After installation, `claude-blog` occupies this structure inside `~/.claude/`:

```
~/.claude/
├── skills/
│   ├── blog/
│   │   ├── SKILL.md                    # Main orchestrator
│   │   ├── references/
│   │   │   ├── ai-crawler-guide.md
│   │   │   ├── content-rules.md
│   │   │   ├── content-templates.md
│   │   │   ├── distribution-playbook.md
│   │   │   ├── eeat-signals.md
│   │   │   ├── geo-optimization.md
│   │   │   ├── google-landscape-2026.md
│   │   │   ├── internal-linking.md
│   │   │   ├── platform-guides.md
│   │   │   ├── quality-scoring.md
│   │   │   ├── schema-stack.md
│   │   │   └── visual-media.md
│   │   ├── templates/
│   │   │   ├── how-to.md
│   │   │   ├── listicle.md
│   │   │   ├── case-study.md
│   │   │   ├── comparison.md
│   │   │   ├── pillar-page.md
│   │   │   ├── product-review.md
│   │   │   ├── thought-leadership.md
│   │   │   ├── roundup.md
│   │   │   ├── tutorial.md
│   │   │   ├── news-analysis.md
│   │   │   ├── data-research.md
│   │   │   └── faq-knowledge-base.md
│   │   └── scripts/
│   │       └── analyze_blog.py
│   ├── blog-write/SKILL.md
│   ├── blog-rewrite/SKILL.md
│   ├── blog-analyze/SKILL.md
│   ├── blog-brief/SKILL.md
│   ├── blog-calendar/SKILL.md
│   ├── blog-strategy/SKILL.md
│   ├── blog-outline/SKILL.md
│   ├── blog-seo-check/SKILL.md
│   ├── blog-schema/SKILL.md
│   ├── blog-repurpose/SKILL.md
│   ├── blog-geo/SKILL.md
│   └── blog-audit/SKILL.md
└── agents/
    ├── blog-researcher.md
    ├── blog-writer.md
    ├── blog-seo.md
    └── blog-reviewer.md
```

**Component counts**: 1 orchestrator, 12 sub-skills, 4 agents, 12 references,
12 templates, 1 Python script = **42 files total**.
