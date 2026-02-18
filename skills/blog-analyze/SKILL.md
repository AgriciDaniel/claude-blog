---
name: blog-analyze
description: >
  Audit and score blog posts on a 5-category 100-point scoring system covering
  content quality, SEO optimization, E-E-A-T signals, technical elements, and
  AI citation readiness. Includes AI content detection (burstiness, phrase
  flagging, vocabulary diversity). Supports export formats (markdown, JSON,
  table) and batch analysis with sorting. Generates prioritized recommendations
  (Critical/High/Medium/Low) with specific fixes. Works with any format (MDX,
  markdown, HTML, URL). Use when user says "analyze blog", "audit blog",
  "blog score", "check blog quality", "blog review", "rate this blog",
  "blog health check".
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
  - WebFetch
---

# Blog Analyzer -- Quality Audit & Scoring

Scores blog posts on a 0-100 scale across 5 categories and provides prioritized
improvement recommendations. Includes AI content detection analysis. Works with
local files or published URLs.

Reference documents:
- `references/quality-scoring.md` -- full scoring checklist
- `references/eeat-signals.md` -- E-E-A-T evaluation criteria

## Input Handling

- **Local file**: Read the file directly
- **URL**: Fetch with WebFetch, extract content
- **Directory**: Scan for blog files, audit all (batch mode)
- **Flags**: `--format json|table`, `--batch`, `--sort score`

## Scoring Process

### Step 1: Content Extraction

Read the blog post and extract:
- Frontmatter (title, description, date, lastUpdated, author, tags)
- Heading structure (H1, H2, H3 with hierarchy)
- Paragraph count and word counts per paragraph
- Statistics (any number claims with or without sources)
- Images (count, alt text presence, format)
- Charts/SVGs (count, type diversity)
- Links (internal, external, broken)
- FAQ section presence
- Schema markup (types present)
- Meta tags (title, description, OG tags, twitter cards)
- Sentence lengths for burstiness analysis
- Vocabulary tokens for diversity scoring

### Step 2: Score Each Category

Load `references/quality-scoring.md` for the full checklist. Score each:

#### Content Quality (30 points)
| Check | Points | Pass Criteria |
|-------|--------|---------------|
| Depth/comprehensiveness | 7 | Covers topic thoroughly, no major gaps |
| Readability (Flesch 60-70) | 7 | Flesch 60-70 ideal, 55-75 acceptable; Grade 7-8; Gunning Fog 7-8 |
| Originality/unique value markers | 5 | Original data, case studies, first-hand experience |
| Sentence & paragraph structure | 4 | Avg sentence 15-20 words, ≤25% over 20; paragraphs 40-80 words; H2 every 200-300 words |
| Engagement elements | 4 | TL;DR box, callouts, varied content blocks |
| Grammar/anti-pattern | 3 | Passive voice ≤10%, AI trigger words ≤5/1K, transition words 20-30%, clean prose |

#### SEO Optimization (25 points)
| Check | Points | Pass Criteria |
|-------|--------|---------------|
| Heading hierarchy with keywords | 5 | H1 -> H2 -> H3, no skips, keyword in 2-3 headings |
| Title tag (40-60 chars, keyword, power word) | 4 | Front-loaded keyword, positive sentiment |
| Keyword placement/density | 4 | Natural integration, no stuffing, in first 100 words |
| Internal linking (3-10 contextual) | 4 | Descriptive anchor text, bidirectional |
| URL structure | 3 | Short, keyword-rich, no stop words, lowercase |
| Meta description (150-160 chars, stat) | 3 | Fact-dense, includes one statistic |
| External linking (tier 1-3) | 2 | 3-8 outbound links to authoritative sources |

#### E-E-A-T Signals (15 points)
| Check | Points | Pass Criteria |
|-------|--------|---------------|
| Author attribution (named, with bio) | 4 | Real name, credentials, not sales pitch |
| Source citations (tier 1-3, inline) | 4 | 8+ unique stats, zero fabricated |
| Trust indicators | 4 | Contact page, about page, editorial policy |
| Experience signals | 3 | "When we tested...", original photos/data |

#### Technical Elements (15 points)
| Check | Points | Pass Criteria |
|-------|--------|---------------|
| Schema markup (3+ types = bonus) | 4 | BlogPosting + FAQ + Person minimum |
| Image optimization | 3 | AVIF/WebP, descriptive alt text, lazy except LCP |
| Structured data elements | 2 | Tables, lists, comparison blocks |
| Page speed signals | 2 | LCP < 2.5s, no render-blocking JS |
| Mobile-friendliness | 2 | Responsive, tap targets 48px+ |
| OG/social meta tags | 2 | og:title, og:description, og:image, twitter:card |

#### AI Citation Readiness (15 points)
| Check | Points | Pass Criteria |
|-------|--------|---------------|
| Passage-level citability (120-180 words) | 4 | Self-contained sections with stat + source |
| Q&A formatted sections | 3 | 60-70% of H2s as questions, FAQ present |
| Entity clarity | 3 | Unambiguous topic entity, consistent terminology |
| Content structure for extraction | 3 | Answer-first, tables with thead, comparison formats |
| AI crawler accessibility | 2 | SSR/SSG, no JS-gated content |

### Step 3: AI Content Detection

Analyze the post for AI-generated content risk:

**Burstiness Score** (sentence length variance):
- Calculate standard deviation of sentence lengths across the post
- Human writing: high variance (short punchy + long complex sentences)
- AI writing: low variance (consistently medium-length sentences)
- Score: 0-10 scale (10 = very human-like burstiness)

**Known AI Phrase Detection** -- flag occurrences of these 17 phrases:
1. "It's important to note"
2. "In today's digital landscape"
3. "Delve into"
4. "Navigating the complexities"
5. "Let's explore"
6. "Furthermore"
7. "In conclusion"
8. "It is worth mentioning"
9. "Embark on"
10. "Cutting-edge"
11. "Leverage" (as a verb, non-financial context)
12. "Game-changer"
13. "Revolutionize"
14. "Streamline"
15. "Harness the power"
16. "Dive deep"
17. "Unlock the potential"

**Vocabulary Diversity** (Type-Token Ratio):
- Calculate unique words / total words
- Human writing: TTR typically 0.4-0.6 for long-form
- AI writing: TTR often below 0.35 (repetitive vocabulary)

**AI Content Risk Assessment**:
- Flag if AI probability > 50% based on combined signals
- Provide specific passages that triggered the flag
- Recommend humanization: personal anecdotes, varied sentence rhythm, domain jargon

### Step 4: Determine Rating

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | Exceptional | Publish as-is, flagship content |
| 80-89 | Strong | Minor polish, ready for publication |
| 70-79 | Acceptable | Targeted improvements needed |
| 60-69 | Below Standard | Significant rework required |
| < 60 | Rewrite | Fundamental issues, start from outline |

### Step 5: Generate Report

Default output format (Markdown):

```
## Blog Quality Report: [Title]

**Score: [X]/100** -- [Rating]

### Score Breakdown
| Category | Score | Max | Notes |
|----------|-------|-----|-------|
| Content Quality | X | 30 | [1-line summary] |
| SEO Optimization | X | 25 | [1-line summary] |
| E-E-A-T Signals | X | 15 | [1-line summary] |
| Technical Elements | X | 15 | [1-line summary] |
| AI Citation Readiness | X | 15 | [1-line summary] |
| **Total** | **X** | **100** | |

### AI Content Risk
- **Burstiness score**: [X]/10 ([human-like / moderate / flat])
- **AI phrases detected**: [N] ([list phrases found])
- **Vocabulary diversity (TTR)**: [X] ([high / acceptable / low])
- **AI probability**: [X]% -- [No concern / Review recommended / High risk]
- **Flagged passages**: [quote specific flat or formulaic sections, if any]

### Issues Found

#### Critical (Must Fix)
- [ ] [Issue with specific location and fix]

#### High Priority
- [ ] [Issue with specific location and fix]

#### Medium Priority
- [ ] [Issue with specific location and fix]

#### Low Priority
- [ ] [Issue with specific location and fix]

### Quick Stats
- Word count: [N]
- Paragraphs: [N] (X over 150 words)
- H2 sections: [N] (X as questions, X with answer-first formatting)
- Statistics: [N] sourced / [N] unsourced
- Images: [N] (X with alt text, formats: ...)
- Charts: [N] (types: ...)
- Internal links: [N]
- External links: [N] (tier breakdown: ...)
- Schema types: [list]
- OG/social tags: [present/missing]

### Recommended Actions
1. [Most impactful fix -- Critical items first]
2. [Second most impactful]
3. [Third]

Run `/blog rewrite <file>` to apply these optimizations automatically.
```

## Export Formats

### Default: Markdown Report
Standard detailed report as shown above.

### JSON Export (`--format json`)
Machine-readable output for integration with CI/CD or dashboards:
```json
{
  "file": "post.md",
  "title": "...",
  "score": 78,
  "rating": "Acceptable",
  "categories": {
    "content_quality": { "score": 22, "max": 30 },
    "seo_optimization": { "score": 18, "max": 25 },
    "eeat_signals": { "score": 12, "max": 15 },
    "technical_elements": { "score": 13, "max": 15 },
    "ai_citation_readiness": { "score": 13, "max": 15 }
  },
  "ai_detection": {
    "burstiness": 6.2,
    "ai_phrases_found": ["Furthermore", "Let's explore"],
    "ttr": 0.44,
    "ai_probability": 32
  },
  "issues": {
    "critical": [],
    "high": [],
    "medium": [],
    "low": []
  }
}
```

### Table Export (`--format table`)
Compact summary for quick review:
```
File            | Score | Rating     | Content | SEO | EEAT | Tech | AI-Ready | AI Risk
post.md         |    78 | Acceptable |   22/30 | 18/25 | 12/15 | 13/15 |    13/15 |    32%
```

## Batch Mode

When given a directory or `--batch` flag, scan for blog files and produce a
summary table. Use `--sort score` to order by score (ascending by default).

```
## Blog Audit Summary: [N] Posts Analyzed

| File | Score | Rating | Content | SEO | EEAT | Tech | AI-Ready | AI Risk | Top Issue |
|------|-------|--------|---------|-----|------|------|----------|---------|-----------|
| post-1.md | 85 | Strong | 26/30 | 20/25 | 13/15 | 14/15 | 12/15 | 18% | Missing OG tags |
| post-2.md | 42 | Rewrite | 10/30 | 8/25 | 5/15 | 9/15 | 10/15 | 71% | 12 fabricated stats |
| post-3.md | 71 | Acceptable | 20/30 | 16/25 | 10/15 | 12/15 | 13/15 | 25% | No answer-first |

### Priority Queue (Lowest Scoring First)
1. post-2.md (42) -- Full rewrite needed, high AI content risk
2. post-3.md (71) -- Answer-first formatting + stats needed
3. post-1.md (85) -- Add OG tags, minor polish

Run `/blog rewrite <file>` on each, starting from lowest score.
```
