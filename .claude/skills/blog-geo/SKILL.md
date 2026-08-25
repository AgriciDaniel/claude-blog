---
name: blog-geo
description: >
  AI citation readiness audit as part of SEO, covering classic Google search
  and AI search surfaces together. Use whenever the user wants their content
  to rank or be cited in ChatGPT, Perplexity, Claude, Gemini, Copilot,
  You.com, Google AI Overviews, or Google AI Mode. AI citation optimization
  audit scoring blog posts for major answer surfaces. Evaluates
  evidence-backed citability, purpose clarity, entity clarity, structured
  data, and AI crawler accessibility. Suggests evidence-backed explanations and a
  0-100 AI Citation Readiness score. Use when user says "geo", "ai
  citation", "ai optimization", "citation audit", "aeo", "perplexity
  optimization", "chatgpt citation".
user-invokable: true
argument-hint: "<file-path>"
license: MIT
---

# Blog GEO: AI Citation Optimization Audit

Scores blog posts for AI citation readiness across ChatGPT, Perplexity, Claude,
Gemini, Copilot, You.com, Google AI Overviews, and Google AI Mode as one SEO
workflow, not a separate discipline. Generates a 0-100 internal AI Citation
Readiness heuristic with platform-specific recommendations. The score is not a
calibrated probability of citation.

Google's 2026-05-15 guidance frames generative-AI optimization as SEO: no
special markup, llms.txt requirement, or separate GEO/AEO playbook is required
for Google visibility. Use GEO/AEO as shorthand labels only.

## Cross-reference

This skill covers FLOW surface 3 (AI assistant citations: ChatGPT, Perplexity, Claude, Gemini, Copilot, You.com) and contributes to surface 2 (SERP plus AI Overviews). Surface mapping: `skills/blog/references/flow-alignment.md`.

For directly relevant AI-citation prompts (AI-supporting-pages rewrite,
evidence-based quality follow-up, ChatGPT discovery, visibility prompts), see
`/blog flow optimize`.

## Evidence Discipline

Use numeric AI-citation benchmarks only when the report includes a source block
with URL, publisher, methodology, sample size, engine or version, query class,
retrieval date, and expiry date. If any field is missing, label the benchmark as
directional or remove the number. Default heuristics:

- Self-contained, evidence-backed explanations can aid reuse, but Google
  prescribes no passage-length or "chunking" requirement.
- Comparison tables with semantic headers may improve extractability, but do not
  cite an uplift without a dated source block.
- AI Overviews coverage is methodology-dependent: cite a dated range, not a
  fixed point.

## Audit Process

### Step 1: Read Content

Extract from the blog post:
- Full content text and word count
- Heading structure (H1, H2, H3 hierarchy)
- Individual paragraphs and their word counts
- FAQ sections (if present)
- Schema markup (JSON-LD, microdata, RDFa)
- robots.txt mentions or meta robots directives
- Any TL;DR or summary boxes
- Comparison tables and their HTML structure
- Numbered/ordered lists
- Definition-style formatting

### Step 2: Evidence-Backed Citability (4 pts)

Check each section between headings for AI-extractable passages:

| Check | Criteria |
|-------|----------|
| Context independence | Each passage makes sense extracted from surrounding context |
| Claim structure | Passages contain: specific claim + supporting evidence + source attribution |
| Completeness | Passage answers a question without requiring reader to read adjacent sections |

**Scoring:** Count important sections meeting the evidence and completeness
criteria. Do not score section length.
- 4 pts: 80%+ sections have citable passages
- 3 pts: 60-79%
- 2 pts: 40-59%
- 1 pt: 20-39%
- 0 pts: <20%

### Step 3: Purpose Fit and Reader Utility (3 pts)

Check heading format and answer structure:

| Check | Criteria |
|-------|----------|
| Clear purpose | The introduction identifies the page's topic, audience, and reader task |
| Useful section openings | Important sections state the point without throat-clearing |
| Intent-matched format | Declarative headings, questions, FAQs, tables, and lists are used only when they fit the material |

**Scoring:**
- 3 pts: All three criteria met
- 2 pts: Two criteria met
- 1 pt: One criterion met
- 0 pts: None met

### Step 4: Entity Clarity (3 pts)

Check topic consistency and disambiguation:

| Check | Criteria |
|-------|----------|
| Canonical topic | One unambiguous primary topic per page |
| Consistent naming | Same entity name used throughout (no confusing synonyms) |
| Intro statement | Clear topic statement in the introduction paragraph |
| Title-content match | Title accurately reflects the content focus |

**Scoring:**
- 3 pts: All four criteria met
- 2 pts: Three criteria met
- 1 pt: One or two criteria met
- 0 pts: None met

### Step 5: Content Structure for Extraction (3 pts)

Check for AI-extractable content patterns:

| Check | Criteria |
|-------|----------|
| Summary | Optional standalone summary when it helps the intended reader |
| Comparison tables | Tables with semantic headers such as `<thead>` or clear column labels |
| Ordered lists | Numbered lists for processes and step-by-step instructions |
| Definition formatting | Key terms formatted with clear definition patterns |
| Evidence-backed explanations | Important reusable claims carry enough context and source support |

**Scoring:**
- 3 pts: 4-5 elements present
- 2 pts: 3 elements present
- 1 pt: 1-2 elements present
- 0 pts: None present

### Step 6: AI Crawler Accessibility (2 pts)

Check technical requirements for AI crawler indexing:

| Check | Criteria |
|-------|----------|
| Rendered content | Important content is present in the rendered DOM and accessible to the target crawler |
| Google visibility | Normal crawlability and indexability for Googlebot. No special GEO/AEO file or markup is required for Google AI features |
| Non-Google AI crawlers | If the site wants visibility in non-Google answer engines, check robots.txt treatment for GPTBot, ChatGPT-User, ClaudeBot, PerplexityBot, and related documented crawlers |
| Schema consistency | Structured data reaches the rendered DOM and matches visible content |
| Page size | Reasonable page size within AI crawler limits |

**Scoring:**
- 2 pts: Google crawlability/indexability is clean, and selected non-Google
  crawler policies match the site's stated goals
- 1 pt: Google is indexable but one selected non-Google crawler or rendering
  check needs review
- 0 pts: Google crawling/indexing is blocked or multiple selected crawlers are
  unintentionally blocked

### Step 7: Platform-Specific Analysis

Evaluate observable readiness for each declared surface. Product behavior
changes by mode, query set, geography, and date, so do not infer causal
preferences from a vendor sample.

#### ChatGPT
- Check that material claims are source-backed and useful without depending on
  a specific content format.
- Treat current citation samples as non-causal context, not a listicle,
  freshness, or domain-authority rule.

#### Perplexity
- Check crawlability, source fidelity, and material freshness when the query is
  time-sensitive. Verify observations with current logs or reproducible tooling
  before describing product behavior.

#### Google AI Overviews
- Follow Google's normal SEO guidance: make content helpful, crawlable,
  indexable, and eligible for snippets. No special GEO/AEO markup or llms.txt is
  required for Google visibility.
- Measure Search and AI-feature visibility separately. Organic overlap observed
  in a sample does not establish a preference or guarantee inclusion.

#### Google AI Mode
- Treat separately from AI Overviews in reports. Emphasize normal Search
  eligibility, clear page purpose, accessible text, and consistency between
  visible content and structured data.

#### Claude, Gemini, Copilot, and You.com
- Evaluate content clarity, source accessibility, freshness, and whether robots
  policy intentionally allows or blocks each crawler where documented.
- Use engine-specific recommendations only when current docs, logs, or test
  results are available.

For each platform, provide:
- Current citability rating (High / Medium / Low)
- Specific improvements to clarity, source fidelity, usefulness, and crawlability
- Content format recommendations

### Step 8: Strengthen Reusable Evidence

For important sections that lack support, propose a self-contained improvement
with a specific claim, the context needed to understand it, and a verified
source or transparent original methodology. Do not pad every section, impose a
word band, or manufacture statistics.

### Step 9: Calculate AI Citation Readiness Score (0-100)

Map the 15-point subcategory scores to a 0-100 display score:

| Category | Raw Points | Display Weight | Max Display Score |
|----------|-----------|----------------|-------------------|
| Evidence-Backed Citability | /4 | x6.75 | 27 |
| Purpose Fit and Reader Utility | /3 | x6.67 | 20 |
| Entity Clarity | /3 | x6.67 | 20 |
| Content Structure | /3 | x6.67 | 20 |
| AI Crawler Accessibility | /2 | x6.5 | 13 |
| **Total** | **/15** | | **100** |

Rating thresholds:
- 90-100: Excellent: highly citable by AI systems
- 70-89: Good: citable with minor improvements
- 50-69: Needs Work: significant gaps in citability
- Below 50: Poor: major restructuring needed

### Step 10: Generate Report

Output the following report:

```
## AI Citation Readiness Report: [Title]

**AI Citation Readiness Heuristic: [X]/100**: [Rating]

This is an internal editorial heuristic, not a calibrated probability.

### Score Breakdown
| Category | Raw | Display | Max |
|----------|-----|---------|-----|
| Evidence-Backed Citability | X/4 | X | 27 |
| Purpose Fit and Reader Utility | X/3 | X | 20 |
| Entity Clarity | X/3 | X | 20 |
| Content Structure | X/3 | X | 20 |
| AI Crawler Accessibility | X/2 | X | 13 |
| **Total** | **X/15** | **X** | **100** |

### Per-Section Citability Analysis
| Section (H2) | Purpose Clear | Self-Contained | Claim+Evidence | Ready |
|---------------|---------------|----------------|----------------|-------|
| [heading] | Yes/No | Yes/No | Yes/No | Yes/No |

### Platform-Specific Optimization
#### ChatGPT
- [specific recommendations]

#### Perplexity
- [specific recommendations]

#### Google AI Overviews
- [specific recommendations]

#### Google AI Mode
- [specific recommendations]

#### Claude / Gemini / Copilot / You.com
- [specific recommendations]

### Evidence Improvements

#### [H2 Section 1]
> [Self-contained, source-backed improvement sized to the material]

#### [H2 Section 2]
> [Self-contained, source-backed improvement sized to the material]

### Technical Recommendations
- [ ] [Technical fix with specifics]

### Priority Action Items
1. [Most impactful improvement]
2. [Second most impactful]
3. [Third most impactful]

Run `/blog analyze <file>` for full content quality scoring.
```

### Optional: Search Performance Context (blog-google)

If blog-google credentials include Tier 1 (GSC) and the post has a published URL:

1. Query GSC by page and query dimensions, then filter rows to the URL:
   `python3 skills/blog-google/scripts/run.py gsc_query --property <property> --dimensions query,page --json`
2. Add to platform-specific analysis:
   - Current impressions, clicks, CTR, average position
   - Search queries driving traffic to this URL
3. Check indexation: `python3 skills/blog-google/scripts/run.py gsc_inspect <url> --json`
4. Report indexation status, canonical selection, mobile usability.
5. If skipped, report `SKIPPED: credentials unavailable` or
   `SKIPPED: unpublished URL`.

### Optional: AI Citation Readiness Heuristic

For a per-engine readiness view (distinct
from the 15-point AI Citation Readiness category scored by `/blog analyze`), run:

```bash
python3 scripts/ai_citation_score.py <file> --format markdown
```

It returns a non-calibrated 0-100 overall heuristic plus per-engine subscores
for Google AI Overview, Perplexity, and ChatGPT, a factor breakdown, and up to
three highest-impact fixes. Legacy `overall_probability` output is retained
only as a compatibility alias.
