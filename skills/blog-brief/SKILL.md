---
name: blog-brief
description: >
  Generate detailed content briefs for blog posts with target keywords,
  content outlines, competitive analysis, recommended statistics, image and
  chart suggestions, word count targets, internal linking architecture,
  template recommendations (12 types), TL;DR drafts, citation capsule
  planning, information gain prompts, and multi-channel distribution plans.
  Briefs are optimized for Google rankings and AI citations (GEO/AEO). Use
  when user says "content brief", "blog brief", "write brief", "outline blog",
  "plan blog post", "blog outline", "content outline".
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
  - WebFetch
  - WebSearch
  - Task
---

# Blog Brief Generator -- Content Planning

Generates comprehensive content briefs that guide blog writing for maximum
impact on both Google rankings and AI citation platforms.

Reference documents:
- `references/content-templates.md` -- template selection criteria
- `references/distribution-playbook.md` -- channel-specific distribution tactics
- `references/internal-linking.md` -- link architecture patterns

## Workflow

### Step 1: Topic Intake

Gather from the user:
1. **Topic or keyword** (required)
2. **Target audience** (who reads this?)
3. **Search intent** -- Informational, commercial, transactional, navigational
4. **Business context** -- What does the company do? What's the CTA?

If only a topic is given, infer the rest from context.

### Step 2: Keyword Research

Using WebSearch:
1. Search for the target keyword -- analyze what currently ranks
2. Identify **primary keyword** (exact match target)
3. Identify **3-5 secondary keywords** (related terms, long-tail)
4. Identify **3-5 question queries** (People Also Ask style)
5. Note the **search intent** -- what do searchers actually want?

### Step 2.5: Template Recommendation

Analyze the topic, search intent, and competitive landscape to recommend one
of 12 content templates. Load `references/content-templates.md` for selection
criteria.

**Available templates:**
| Template | Best For |
|----------|----------|
| `how-to-guide` | Step-by-step instructional content |
| `listicle` | Curated lists, ranked items, resource roundups |
| `case-study` | In-depth analysis of a specific example or result |
| `comparison` | Side-by-side evaluation of 2+ options |
| `pillar-page` | Comprehensive topic hub linking to cluster content |
| `product-review` | Detailed evaluation with pros/cons/verdict |
| `thought-leadership` | Expert opinion, industry trends, predictions |
| `roundup` | Expert quotes, tool collections, best-of lists |
| `tutorial` | Technical walkthrough with code/config examples |
| `news-analysis` | Timely coverage with expert commentary |
| `data-research` | Original data, survey results, benchmark findings |
| `faq-knowledge` | Question-driven reference content |

**Selection process:**
1. Match search intent to template strength
2. Check what format top-ranking competitors use
3. Consider the user's available assets (data, expertise, tools)
4. Load the matching template file from `blog/templates/[type].md`
5. Include the template name in the brief output

### Step 3: Competitive Analysis

Analyze the top 3-5 ranking pages for the target keyword:
1. **Content length** -- What's the average word count?
2. **Heading structure** -- How many H2s? What topics do they cover?
3. **Visual elements** -- Do competitors use charts, images, videos?
4. **Content gaps** -- What do all competitors miss?
5. **Freshness** -- How recently were they updated?
6. **Schema** -- Do they use FAQ or other rich results? (Note: HowTo deprecated Sept 2023)
7. **Template pattern** -- What content format do top results use?

### Step 4: Statistics Research

Find 8-12 statistics the article should include:
1. Search: `[topic] study 2025 2026 data statistics research`
2. Prioritize tier 1-3 sources
3. For each stat, record: value, source, URL, date, methodology
4. Identify 2-4 stats suitable for chart visualization
5. Identify 1-2 stats suitable for TL;DR and social sharing

### Step 5: Generate the Brief

Output format:

```
# Content Brief: [Title Suggestion]

## Template
**Recommended**: [template-name] -- [1-sentence rationale]
**Template file**: `blog/templates/[type].md`

## Target Keywords
- **Primary**: [keyword] -- [estimated monthly search volume if available]
- **Secondary**: [keyword 1], [keyword 2], [keyword 3]
- **Questions**: [question 1], [question 2], [question 3]

## Search Intent
[Informational/Commercial/Transactional] -- [1-2 sentence explanation of
what the searcher wants]

## Content Parameters
- **Word count**: [2,000-2,500] words
- **Reading level**: Flesch 60-70 (expert-accessible)
- **Format**: [Markdown/MDX/HTML]
- **H2 sections**: [6-8]
- **Images**: 3-5 from Pixabay/Unsplash
- **Charts**: 2-4 via built-in blog-chart (diverse types)
- **FAQ items**: 3-5

## Recommended Title
[Question-format title including primary keyword, under 60 chars]

Alternative titles:
1. [Option 2]
2. [Option 3]

## Meta Description
[150-160 chars, fact-dense, includes 1 statistic, ends with value proposition]

## TL;DR Draft
> **TL;DR:** [40-60 word summary with key finding + 1 statistic + source.
> Should be self-contained -- a reader who only reads this box gets the
> core value of the article.]

## Information Gain Opportunities
- **[ORIGINAL DATA]**: [Suggestion for proprietary data, survey, experiment,
  or benchmark the author can produce to differentiate this post]
- **[PERSONAL EXPERIENCE]**: [Suggestion for first-hand observation, test
  result, or case study to include -- "When we tested X, we found Y"]
- **[UNIQUE INSIGHT]**: [Suggestion for contrarian take, novel analysis,
  or non-obvious connection that competitors have not covered]

## Content Outline

### Introduction (100-150 words)
- Hook: [Surprising statistic to open with]
- Problem: [What challenge does the reader face?]
- Promise: [What will they learn?]
- TL;DR box placement (after hook, before first H2)

### H2: [Question Format] (300-400 words)
- **Answer-first**: Open with [specific stat + source]
- Cover: [subtopic 1], [subtopic 2]
- **Image**: [Description of recommended image]
- **Key stat**: [Specific statistic to include]

### H2: [Question Format] (300-400 words)
- **Answer-first**: Open with [specific stat + source]
- Cover: [subtopic 1], [subtopic 2]
- **Chart**: [Type] showing [data description]
- **Key stat**: [Specific statistic to include]

[... repeat for 6-8 sections ...]

### FAQ Section (3-5 items)
1. [Question] -- Answer with [stat + source]
2. [Question] -- Answer with [stat + source]
3. [Question] -- Answer with [stat + source]

### Conclusion (100-150 words)
- Key takeaways (bulleted)
- Call to action: [What should the reader do next?]

## Statistics to Include

| # | Statistic | Source | Year | Section |
|---|-----------|--------|------|---------|
| 1 | [stat] | [source + URL] | 2025 | H2: Section 1 |
| 2 | [stat] | [source + URL] | 2026 | H2: Section 2 |
| ... | ... | ... | ... | ... |

## Citation Capsule Plan
For each H2, plan a 40-60 word self-contained passage optimized for AI
extraction. Each capsule should include a stat, its source, and a clear
claim that can stand alone when quoted.

| Section | Capsule Focus | Key Stat | Source |
|---------|--------------|----------|--------|
| H2: [Section 1] | [Core claim this section makes] | [stat] | [source] |
| H2: [Section 2] | [Core claim this section makes] | [stat] | [source] |
| H2: [Section 3] | [Core claim this section makes] | [stat] | [source] |
| ... | ... | ... | ... |

## Cover Image

| Option | Details |
|--------|---------|
| Photo cover | [Pixabay/Unsplash/Pexels search terms for wide hero image] |
| Generated SVG | [Text-on-gradient concept with key stat, if data-heavy topic] |
| Dimensions | 1200x630 (OG-compatible) |

## Visual Element Plan

| # | Type | Data | Section |
|---|------|------|---------|
| 1 | [Bar chart] | [Data description] | H2: Section 2 |
| 2 | [Donut chart] | [Data description] | H2: Section 4 |
| 3 | [Image: Pixabay] | [Search terms] | H2: Section 1 |
| 4 | [Image: Pixabay] | [Search terms] | H2: Section 3 |

## Competitive Gaps to Exploit
1. [What competitors miss that we should cover]
2. [Unique angle or original data we can provide]
3. [Format advantage -- charts/visuals competitors lack]

## Internal Link Architecture
- **Link TO** (from this new post to existing pages):
  1. [Page title/URL] -- anchor text: "[descriptive anchor]"
  2. [Page title/URL] -- anchor text: "[descriptive anchor]"
  3. [Page title/URL] -- anchor text: "[descriptive anchor]"
  4. [Page title/URL] -- anchor text: "[descriptive anchor]"
  5. [Page title/URL] -- anchor text: "[descriptive anchor]"
- **Link FROM** (update these existing pages to link to this new post):
  1. [Page title/URL] -- anchor text: "[descriptive anchor]"
  2. [Page title/URL] -- anchor text: "[descriptive anchor]"
  3. [Page title/URL] -- anchor text: "[descriptive anchor]"
  4. [Page title/URL] -- anchor text: "[descriptive anchor]"
  5. [Page title/URL] -- anchor text: "[descriptive anchor]"
- **Pillar connection**: [Which pillar page this belongs to, if applicable]
- **Cluster position**: [Hub / Spoke / Standalone]

## E-E-A-T Signals to Include
- **Experience**: [First-hand insight, case study, or test result]
- **Expertise**: [Author credentials relevant to topic]
- **Authority**: [Industry recognition, citations, partnerships]
- **Trust**: [Transparency, sourced data, no self-promotion]

## Distribution Plan
- **Reddit**: [Specific subreddits (r/sub1, r/sub2), posting approach (value-first
  comment vs. link post), authentic participation strategy, timing]
- **YouTube**: [Video companion concept, estimated length, key visuals from the
  post to reuse, thumbnail idea]
- **LinkedIn**: [Article excerpt angle, target audience segment, best posting
  time for the niche, engagement hook]
- **Email**: [Newsletter excerpt (2-3 sentences), subject line suggestion,
  CTA linking back to the full post]
- **Twitter/X**: [Thread hook (first tweet), 3-5 key tweet ideas built from
  statistics in the post, hashtag suggestions]
```

### Step 6: Save the Brief

Save to the user's project as `briefs/[slug]-brief.md` or to a location
they specify. Confirm the brief is ready for `/blog write`.
