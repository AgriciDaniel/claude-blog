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
                        |      skills/blog/SKILL.md          |
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
|   32 Skill Directories     |            |    On-Demand References   |
|  1 orchestrator + 31       |            |  skills/blog/references/*.md     |
|  sub-skills                |            |  skills/blog/templates/*.md      |
|  write    rewrite          |            |                           |
|  analyze  brief            |            |  22 references loaded     |
|  calendar strategy         |            |  on demand (RAG pattern)  |
|  outline  seo-check        |            |  12 content templates     |
|  schema   repurpose        |            +---------------------------+
|  geo      audit            |
|  image    cannibalization  |
|  factcheck persona         |
|  taxonomy notebooklm       |
|  audio    google           |
|  cluster  flow             |
|  multilingual translate    |
|  localize locale-audit     |
|  brand    discourse        |
|  style    decay            |
|  chart (internal)          |
+------+----------+----------+
       |          |
       v          v
+------------------+  +------------------------+
|  5 Subagents     |  |  14 root-level Scripts  |
|  agents/*.md     |  |  scripts/*.py          |
|                  |  |                        |
|  blog-researcher |  |  analyze_blog          |
|  blog-writer     |  |  blog_preflight (1.9)  |
|  blog-seo        |  |  blog_render (1.9)     |
|  blog-reviewer   |  |  blog_hygiene (1.11)   |
|  blog-translator |  |  ai_citation_score     |
|                  |  |  content_decay         |
|                  |  |  quality_gate          |
|                  |  |  style_learn           |
|                  |  |                        |
|                  |  |  generate_hero (1.9)   |
|                  |  |  cognitive_load        |
+------------------+  |  discourse_research    |
                      |  load_untrusted_root   |
                      |  lint_prose            |
                      |  sync_flow             |
                      +------------------------+
```

---

## Component Types

### 1. Main Orchestrator

**File**: `skills/blog/SKILL.md`

The entry point for all `/blog` commands. Responsibilities:

- Parse user input to identify the sub-command and arguments
- Detect the blog platform from project structure (MDX, Hugo, Jekyll, etc.)
- Route to the appropriate sub-skill
- Enforce quality gates (hard rules that never ship content violating them)
- Load reference files on demand

The orchestrator is a Claude Code skill with YAML frontmatter defining its
name, description, trigger phrases, and allowed tools.

### 2. Skill Directories (32 total: 1 orchestrator + 31 sub-skills; 30 user-facing commands)

**Location**: `skills/blog-*/SKILL.md` (and `skills/blog/SKILL.md` for the orchestrator)

Each sub-skill is a standalone Claude Code skill with its own:

- YAML frontmatter (name, description, user-invokable, argument-hint, metadata.version)
- Detailed workflow (step-by-step instructions)
- Input/output specifications
- Quality checks

| Sub-Skill | Responsibility | Introduced |
|-----------|----------------|------------|
| blog-write | New article generation with full optimization (v1.9.0: iterates through 5-gate delivery contract until score >= 90 and zero P0, max 3 iterations) | v1.0.0 |
| blog-rewrite | Existing post optimization preserving author voice (v1.9.0: same delivery contract) | v1.0.0 |
| blog-analyze | Quality audit with 5-category 100-point scoring | v1.0.0 |
| blog-brief | Content brief generation with research | v1.0.0 |
| blog-calendar | Editorial calendar planning | v1.0.0 |
| blog-strategy | Blog positioning and content architecture | v1.0.0 |
| blog-outline | SERP-informed outline generation | v1.0.0 |
| blog-seo-check | Post-writing SEO validation | v1.0.0 |
| blog-schema | JSON-LD schema markup generation | v1.0.0 |
| blog-repurpose | Cross-platform content repurposing | v1.0.0 |
| blog-geo | AI citation optimization audit | v1.0.0 |
| blog-audit | Full-site blog health assessment | v1.0.0 |
| blog-chart | Inline SVG charts (internal-only, invoked by write/rewrite) | v1.0.0 |
| blog-image | AI image generation via Gemini (nanobanana-mcp) | v1.4.0 |
| blog-cannibalization | Keyword overlap detection across posts | v1.4.x |
| blog-factcheck | Statistics verification against cited sources | v1.4.x |
| blog-persona | Writing persona / voice profile management | v1.4.x |
| blog-taxonomy | CMS tag / category management (WordPress, Shopify, Ghost, Strapi, Sanity) | v1.4.x |
| blog-notebooklm | Source-grounded research via NotebookLM | v1.5.0 |
| blog-audio | Audio narration via Gemini TTS (30 voices, 80+ languages) | v1.6.0 |
| blog-google | Google API integration (PSI, CrUX, GSC, GA4, NLP, YouTube, Ads) | v1.6.5 |
| blog-cluster | Semantic topic-cluster planning + execution (hub-and-spoke) | v1.7.0 |
| blog-flow | FLOW framework prompts (find / optimize / win / prompts / sync) | v1.7.0 |
| blog-multilingual | One-command multilingual write + translate + localize + hreflang | v1.7.0 |
| blog-translate | SEO-optimized translation with format preservation | v1.7.0 |
| blog-localize | Cultural deep-adaptation per locale | v1.7.0 |
| blog-locale-audit | Multilingual content QA (completeness, hreflang, parity, freshness) | v1.7.0 |
| blog-brand | Generate BRAND.md + VOICE.md context auto-loaded by all sub-skills | v1.8.0 |
| blog-discourse | API-free last-30-days discourse research (Reddit, X, YouTube, etc.) | v1.8.0 |
| blog-style | Learn author voice profiles from existing posts | v1.10.0 |
| blog-decay | Detect GSC content decay and prioritize refresh candidates | v1.10.0 |

### 3. Subagents (5)

**Location**: `agents/blog-*.md`

Specialized agents spawned by sub-skills via Claude Code's `Task` tool.
Each agent has a focused role with a restricted tool set. None of the
agents have Bash access; the v1.7.0 hardening removed Bash from the
agent frontmatter to bound blast radius (see `agents/blog-reviewer.md`
and `agents/blog-translator.md`).

| Agent | Tools | Role |
|-------|-------|------|
| blog-researcher | WebSearch, WebFetch, Read, Grep, Glob | Find statistics, images, competitive data |
| blog-writer | Read, Write, Edit, Grep, Glob | Write and rewrite optimized content |
| blog-seo | Read, WebFetch, Grep, Glob | Technical SEO analysis and validation |
| blog-reviewer | Read, Grep, Glob | Quality review and scoring; **BLOCKING in v1.9.0** (emits `BLOCKING: true\|false (reason)` line parsed by `scripts/blog_preflight.py` Gate 4) |
| blog-translator | Read, Write, Edit, Grep, Glob | Multilingual translation (v1.7.0; no Bash for blast-radius safety) |

Agents are defined as markdown files with YAML frontmatter specifying their
name, description, and available tools.

### 4. Reference Files (22)

**Location**: `skills/blog/references/*.md`

Knowledge documents loaded on demand (RAG-style; not preloaded into context).
22 references in `skills/blog/references/` cover SEO landscape, GEO/AEO,
content rules, visual media, schema, E-E-A-T, platform guides, distribution,
internal linking, FLOW prompts, video embeds, AI-slop detection, editorial
heuristics, cognitive load, research quality, synthesis contract, and the
v1.9.0 blog-delivery-contract spec.

To list the current set:

```bash
ls skills/blog/references/*.md
```

The exact list is intentionally not enumerated here so this doc doesn't drift
behind file-system reality. The `test_reference_count_coherence` pytest
asserts the count claimed in `skills/blog/SKILL.md` matches the actual file
count, so every documented count auto-syncs.

### 5. Content Templates (12)

**Location**: `skills/blog/templates/*.md`

Structural templates for different content types. Each template defines
section structure, word count targets, and format-specific guidance.
See [TEMPLATES.md](TEMPLATES.md) for the full reference.

### 6. Root-Level Python Scripts (14)

**Location**: `scripts/*.py`

Standalone CLIs that the orchestrator calls via Bash. Each has argparse,
docstring, JSON output, and stdlib-only or narrowly-pinned dependencies.

| Script | Purpose | Introduced |
|---|---|---|
| `analyze_blog.py` | 5-category 100-point quality scoring; batch mode; JSON/markdown/table output | v1.0.0 |
| `ai_citation_score.py` | AI citation probability 0-100 per post | v1.10.0 |
| `blog_hygiene.py` | Optional deterministic hygiene: lazy-load images and auto-TOC | v1.11.0 |
| `blog_preflight.py` | Runs 5-gate Blog Delivery Contract (Gates 1, 2, 3, 5; reads Gate 4 output) | v1.9.0 |
| `blog_render.py` | md -> html -> pdf renderer; XSS-safe JSON-LD via `</`->`<\/`; O_NOFOLLOW symlink refusal; frontmatter validation | v1.9.0 |
| `cognitive_load.py` | Per-section concept-density analyzer (entities, numerics, jargon, forward refs, clause depth) | v1.8.0 |
| `content_decay.py` | GSC content-decay detector: 20%+ QoQ decline | v1.10.0 |
| `discourse_research.py` | Discourse-brief synthesis from SERP JSON; depth-bounded parsing; path-traversal guards | v1.8.0 |
| `generate_hero.py` | Hero image ladder: Banana MCP -> Gemini API -> Unsplash/Pexels/Pixabay -> Openverse | v1.9.0 |
| `load_untrusted_root.py` | Code-enforced BRAND/VOICE/DISCOURSE fencing with CSPRNG nonces; O_NOFOLLOW + size cap | v1.8.3 |
| `lint_prose.py` | Fence-aware prose-hygiene linter (no em-dash, en-dash, ` -- `); CI-enforced | v1.8.4 |
| `quality_gate.py` | Pre-commit gate: block posts scoring < 70 | v1.10.0 |
| `style_learn.py` | Author voice-profile learner from sample posts | v1.10.0 |
| `sync_flow.py` | Pulls FLOW reference prompts from upstream; sandboxed; stdlib-only | v1.7.0 |

---

## Data Flow

### Write Flow

```
/blog write "topic"
      |
      v
  Orchestrator (skills/blog/SKILL.md)
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
      +-- Invokes: blog-chart (2-4 charts, built-in)
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
      +-- Quality verification (5 categories, 100 points)
      |
      +-- v1.9.0: 5-gate Blog Delivery Contract (blog_preflight.py)
      |     Gate 1 Capability Discovery -> capabilities.json
      |     Gate 2 Format Completeness  -> .md + .html + .pdf + hero.<ext>
      |     Gate 3 Visual Verification  -> patchright/playwright 3 viewports
      |     Gate 4 Content Review       -> blog-reviewer agent (BLOCKING)
      |     Gate 5 Asset + Link         -> imgs, links, schema, wordCount
      |     If any gate BLOCKS: iterate up to 3x then escalate to user
      |
      +-- Writes file to user's project
      |
      v
  Delivery summary (8 artifacts: md, html, pdf, hero, 4 viewport screenshots, review.md, preflight-report.json)
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
      +-- Manual scoring (5 categories, 100 points)
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
| 90-100 | Exceptional | Publish as-is (v1.9.0 contract delivers GREEN) |
| 80-89 | Strong | Minor tweaks; orchestrator iterates if Gate 4 wants 90+ |
| 70-79 | Acceptable | Notable gaps; iterate |
| 60-69 | Below Standard | Significant improvements required |
| < 60 | Rewrite | Full rewrite recommended |

The v1.9.0 Blog Delivery Contract Gate 4 BLOCKS on score < 90 OR any P0 issue
from `editorial-heuristics.md`. The orchestrator iterates the writer up to 3
times before escalating with a diagnostic to the user.

### Quality Gates (Hard Rules)

These are non-negotiable. Content violating any of these must not be published:

| Gate | Threshold |
|------|-----------|
| Fabricated statistics | Zero tolerance |
| Paragraph length | Never > 150 words |
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
| Main skill | `skills/blog/SKILL.md` | Fixed name |
| Sub-skills | `skills/blog-<command>/SKILL.md` | Prefix `blog-` + command name |
| Agents | `agents/blog-<role>.md` | Prefix `blog-` + role name |
| References | `skills/blog/references/<topic>.md` | Kebab-case topic name |
| Templates | `skills/blog/templates/<type>.md` | Kebab-case content type |
| Scripts | `scripts/<name>.py` | Snake-case script name |

---

## Extension Points

### Adding a New Command

1. Create `skills/blog-<name>/SKILL.md` with YAML frontmatter
2. Add routing logic to `skills/blog/SKILL.md` orchestrator
3. Update `install.sh` and `install.ps1` to copy the new sub-skill
4. Update `uninstall.sh` to remove it

### Adding a New Agent

1. Create `agents/blog-<role>.md` with YAML frontmatter
2. Define the tool set (keep it minimal for the role)
3. Reference the agent from sub-skills that need it

### Adding a New Reference

1. Create `skills/blog/references/<topic>.md`
2. Document when to load it in the orchestrator
3. Update `install.sh` to copy the new reference file

### Adding a New Template

1. Create `skills/blog/templates/<type>.md`
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
│   │   │   ├── how-to-guide.md
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
│   │   │   └── faq-knowledge.md
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
│   ├── blog-audit/SKILL.md
│   ├── blog-chart/SKILL.md             # internal-only (SVG generation)
│   ├── blog-image/SKILL.md             # v1.4.0
│   ├── blog-cannibalization/SKILL.md
│   ├── blog-factcheck/SKILL.md
│   ├── blog-persona/SKILL.md
│   ├── blog-taxonomy/SKILL.md
│   ├── blog-notebooklm/SKILL.md        # v1.5.0
│   ├── blog-audio/SKILL.md             # v1.6.0
│   ├── blog-google/SKILL.md            # v1.6.5
│   ├── blog-cluster/SKILL.md           # v1.7.0
│   ├── blog-flow/SKILL.md              # v1.7.0
│   ├── blog-multilingual/SKILL.md      # v1.7.0
│   ├── blog-translate/SKILL.md         # v1.7.0
│   ├── blog-localize/SKILL.md          # v1.7.0
│   ├── blog-locale-audit/SKILL.md      # v1.7.0
│   ├── blog-brand/SKILL.md             # v1.8.0
│   ├── blog-discourse/SKILL.md         # v1.8.0
│   ├── blog-style/SKILL.md             # v1.10.0
│   └── blog-decay/SKILL.md             # v1.10.0
└── agents/
    ├── blog-researcher.md
    ├── blog-writer.md
    ├── blog-seo.md
    ├── blog-reviewer.md
    └── blog-translator.md              # v1.7.0
```

**Component counts (v1.11.0)**: 32 skill directories (1 orchestrator + 31
sub-skills); 30 user-facing commands, 5 agents (blog-researcher, blog-writer, blog-seo, blog-reviewer,
blog-translator), 22 references in `skills/blog/references/` (plus per-sub-skill
references and 30 synced FLOW prompts under `skills/blog-flow/references/`),
12 content templates, 14 root-level scripts (`scripts/analyze_blog.py`,
`ai_citation_score.py`, `blog_hygiene.py`, `blog_preflight.py`,
`blog_render.py`, `cognitive_load.py`, `content_decay.py`,
`discourse_research.py`, `generate_hero.py`, `load_untrusted_root.py`,
`lint_prose.py`, `quality_gate.py`, `style_learn.py`, `sync_flow.py`) plus per-sub-skill scripts under
`blog-google/`, `blog-notebooklm/`, `blog-audio/`, `blog-image/`.
v1.8.0+ adds three project-root context files (BRAND.md / VOICE.md /
DISCOURSE.md, auto-loaded via `scripts/load_untrusted_root.py` with
CSPRNG nonce fencing). v1.8.4+ enforces prose hygiene and version
coherence via CI (see `scripts/lint_prose.py`, `tests/test_version_coherence.py`).
v1.9.0 adds the 5-gate Blog Delivery Contract (see
`skills/blog/references/blog-delivery-contract.md`) and 242-test pytest
suite including mutation-test-verified XSS, symlink, and frontmatter
regression coverage.
