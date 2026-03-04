# Blog GEO -- AI Citation Optimization Audit

Scores blog posts for AI citation readiness across ChatGPT, Perplexity, and
Google AI Overviews. Generates citation capsules and a 0-100 AI Citation
Readiness score with platform-specific recommendations.

## Key Research Data

Reference these benchmarks throughout the audit:

- Only 12% of sources cited match across ChatGPT, Perplexity, and AI Overviews
- 80% of LLM citations don't rank in Google's top 100
- Brands 6.5x more likely cited through third-party sources
- 120-180 word sections get 70% more ChatGPT citations
- Comparison tables with `<thead>` achieve 47% higher AI citation rates
- Content freshness: 76.4% of top citations updated within 30 days

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

### Step 2: Passage-Level Citability (4 pts)

Check each section between headings for AI-extractable passages:

| Check | Criteria |
|-------|----------|
| Word count | Each section contains 120-180 word self-contained passages |
| Context independence | Each passage makes sense extracted from surrounding context |
| Claim structure | Passages contain: specific claim + supporting evidence + source attribution |
| Completeness | Passage answers a question without requiring reader to read adjacent sections |

**Scoring:** Count passages meeting all criteria vs total sections.
- 4 pts: 80%+ sections have citable passages
- 3 pts: 60-79%
- 2 pts: 40-59%
- 1 pt: 20-39%
- 0 pts: <20%

### Step 3: Q&A Formatting (3 pts)

Check heading format and answer structure:

| Check | Criteria |
|-------|----------|
| Question headings | 60-70% of H2s are phrased as questions |
| Answer-first format | Opening paragraph under each H2 provides a direct answer |
| FAQ section | Dedicated FAQ section with structured question-answer pairs |

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
| TL;DR box | 40-60 word standalone summary present at top |
| Comparison tables | Tables with proper HTML `<thead>` (47% higher citation rate) |
| Ordered lists | Numbered lists for processes and step-by-step instructions |
| Definition formatting | Key terms formatted with clear definition patterns |
| Citation capsules | 40-60 word definitive statements in each major section |

**Scoring:**
- 3 pts: 4-5 elements present
- 2 pts: 3 elements present
- 1 pt: 1-2 elements present
- 0 pts: None present

### Step 6: AI Crawler Accessibility (2 pts)

Check technical requirements for AI crawler indexing:

| Check | Criteria |
|-------|----------|
| Static HTML | Content rendered in static HTML, not behind JavaScript |
| robots.txt | Allows AI crawlers: GPTBot, ChatGPT-User, GeminiBot, PerplexityBot |
| Schema in HTML | Schema markup in static HTML, not JS-injected |
| Page size | Reasonable page size within AI crawler limits |

**Scoring:**
- 2 pts: All criteria met
- 1 pt: Most criteria met but one issue
- 0 pts: Multiple issues blocking AI crawlers

### Step 7: Platform-Specific Analysis

Evaluate the post for each AI platform's citation preferences:

#### ChatGPT
- Favors "Best X" listicles (43.8% of citations)
- Prefers well-cited, authoritative content
- Recency matters -- recent updates get priority
- Domain authority influences citation likelihood

#### Perplexity
- Favors Reddit sources (6.6% of all citations)
- Rapid content decay: 2-3 day citation window
- Freshness is the most critical factor
- Community-validated content preferred

#### Google AI Overviews
- Favors Google properties (23% of citations)
- High Domain Rating strongly correlated with citation
- Present in 49% of SERPs
- Prefers content that already ranks well organically

For each platform, provide:
- Current citability rating (High / Medium / Low)
- Specific improvements to increase citation likelihood
- Content format recommendations

### Step 8: Generate Citation Capsules

For each H2 section in the post, write a citation capsule:

- **Length**: 40-60 words, self-contained
- **Structure**: Specific claim + data point + source attribution
- **Purpose**: A passage AI could directly quote as a citation
- **Format**: Present as a suggested addition the author can embed

Example:
```
According to [Source], [specific claim with number]. This represents
[context/comparison], making it [significance]. [Supporting detail
that reinforces the claim].
```

Generate one capsule per H2 section. Label each with the section heading
it belongs under.

### Step 9: Calculate AI Citation Readiness Score (0-100)

Map the 15-point subcategory scores to a 0-100 display score:

| Category | Raw Points | Display Weight | Max Display Score |
|----------|-----------|----------------|-------------------|
| Passage-Level Citability | /4 | x6.75 | 27 |
| Q&A Formatting | /3 | x6.67 | 20 |
| Entity Clarity | /3 | x6.67 | 20 |
| Content Structure | /3 | x6.67 | 20 |
| AI Crawler Accessibility | /2 | x6.5 | 13 |
| **Total** | **/15** | | **100** |

Rating thresholds:
- 90-100: Excellent -- highly citable by AI systems
- 70-89: Good -- citable with minor improvements
- 50-69: Needs Work -- significant gaps in citability
- Below 50: Poor -- major restructuring needed

### Step 10: Generate Report

Output the following report:

```
## AI Citation Readiness Report: [Title]

**AI Citation Readiness Score: [X]/100** -- [Rating]

### Score Breakdown
| Category | Raw | Display | Max |
|----------|-----|---------|-----|
| Passage-Level Citability | X/4 | X | 27 |
| Q&A Formatting | X/3 | X | 20 |
| Entity Clarity | X/3 | X | 20 |
| Content Structure | X/3 | X | 20 |
| AI Crawler Accessibility | X/2 | X | 13 |
| **Total** | **X/15** | **X** | **100** |

### Per-Section Citability Analysis
| Section (H2) | Word Count | Self-Contained | Claim+Evidence | Citable |
|---------------|-----------|----------------|----------------|---------|
| [heading] | [N] | Yes/No | Yes/No | Yes/No |

### Platform-Specific Optimization
#### ChatGPT
- [specific recommendations]

#### Perplexity
- [specific recommendations]

#### Google AI Overviews
- [specific recommendations]

### Generated Citation Capsules

#### [H2 Section 1]
> [40-60 word citation capsule]

#### [H2 Section 2]
> [40-60 word citation capsule]

### Technical Recommendations
- [ ] [Technical fix with specifics]

### Priority Action Items
1. [Most impactful improvement]
2. [Second most impactful]
3. [Third most impactful]

Run `/blog:analyze <file>` for full content quality scoring.
```


