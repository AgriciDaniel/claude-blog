---
name: blog-write
description: >
  Write new blog articles from scratch optimized for Google rankings and AI
  citations. Generates full articles with template selection, answer-first
  formatting, TL;DR box, information gain markers, citation capsules, sourced
  statistics, Pixabay/Unsplash images, built-in SVG chart generation, FAQ schema,
  internal linking zones, and proper heading hierarchy. Supports MDX, markdown,
  and HTML output.
  Use when user says "write blog", "new blog post", "create article",
  "write about", "draft blog", "generate blog post".
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

# Blog Writer -- New Article Generation

Writes complete blog articles from a topic, brief, or outline. Every article
follows the 6 pillars of dual optimization (Google rankings + AI citations).

**Key references:**
- `references/content-templates.md` — Template selection guide and usage
- `references/quality-scoring.md` — 5-category scoring (Content 30, SEO 25, E-E-A-T 15, Technical 15, AI Citation 15)
- `references/eeat-signals.md` — Experience, expertise, authority, trust markers
- `references/internal-linking.md` — Linking strategy and anchor text rules
- `references/visual-media.md` — Image sourcing and chart styling

## Workflow

### Phase 1: Topic Understanding

1. **Clarify the topic** — If the user provides just a topic, ask:
   - Target audience (who is this for?)
   - Primary keyword / search intent
   - Desired word count (default: 2,000-2,500 words)
   - Platform/format (MDX, markdown, HTML — auto-detect if in a project)
2. **If a brief exists** — Load it and skip to Phase 1.5

### Phase 1.5: Template Selection

Select the appropriate content template from the 12 templates in `blog/templates/`.

1. **Auto-detect content type** from the topic and search intent:
   | Signal | Template |
   |--------|----------|
   | "How to...", process, steps | `how-to-guide` |
   | "Best X", "Top N", list format | `listicle` |
   | Client result, before/after, metrics | `case-study` |
   | "X vs Y", comparison, alternatives | `comparison` |
   | Broad topic, comprehensive guide | `pillar-page` |
   | "Is X worth it", product evaluation | `product-review` |
   | Opinion, prediction, industry take | `thought-leadership` |
   | Expert quotes, multi-source collection | `roundup` |
   | Code walkthrough, tool demo, technical | `tutorial` |
   | Breaking news, algorithm update, event | `news-analysis` |
   | Survey results, experiment, original data | `data-research` |
   | Q&A, knowledge base, "What is X" | `faq-knowledge` |

2. **Load the matching template** — Read from `blog/templates/<type>.md`
3. **Adapt the outline** — Use the template's section structure, heading patterns,
   and word count guidance to shape Phase 3's outline
4. **Fallback** — If no template clearly fits, use the generic outline structure
   in Phase 3 below. Inform the user which template was selected (or that none matched).

See `references/content-templates.md` for detailed selection criteria and intent mapping.

### Phase 2: Research

Spawn a `blog-researcher` agent (or do inline research with WebSearch):

1. **Find 8-12 current statistics** (2025-2026 data preferred)
   - Search: `[topic] study 2025 2026 data statistics`
   - Prioritize tier 1-3 sources (see `references/quality-scoring.md`)
   - Record: statistic, source name, URL, date, methodology
2. **Find a cover image** (wide, high-quality, topic-relevant):
   - Search: `site:pixabay.com [topic] wide banner` (preferred)
   - Alternative: `site:unsplash.com [topic] wide`
   - Fallback: `site:pexels.com [topic] wide banner`
   - Target dimensions: 1200x630 (OG-compatible) or 1920x1080
   - Or generate a custom SVG cover via `blog-chart` (text-on-gradient with key stat)
   - See `references/visual-media.md` for cover image sizing details
3. **Find 3-5 inline images** from open-source platforms:
   - **Pixabay** (preferred): Search `site:pixabay.com [topic keywords]`
     - Extract image URL from page
     - Direct URLs: `https://cdn.pixabay.com/photo/YYYY/MM/DD/HH/MM/filename.jpg`
     - Verify with `curl -sI "<url>" | head -1` returns HTTP 200
   - **Unsplash** (alternative): Search `site:unsplash.com [topic keywords]`
     - Build URL: `https://images.unsplash.com/photo-<id>?w=1200&h=630&fit=crop&q=80`
   - **Pexels** (fallback): Search `site:pexels.com [topic keywords]`
4. **Plan 2-4 data visualizations** from researched statistics
   - Select diverse chart types (see `references/visual-media.md`)
   - Map data points to chart formats

### Phase 3: Outline Generation

Create a structured outline before writing. If a template was loaded in Phase 1.5,
adapt this skeleton to match the template's section structure:

```
# [Title as Question — Include Primary Keyword]

## Introduction (100-150 words)
- Hook with surprising statistic
- Problem/opportunity statement
- What the reader will learn

> **TL;DR:** [40-60 word standalone summary — placeholder]

## H2: [Question Format] (300-400 words)
- Answer-first paragraph (40-60 words with stat + source)
- Supporting evidence
- [Image placement]
- Practical advice
- [CITATION CAPSULE placeholder]
- [INTERNAL-LINK: anchor text → target description]

## H2: [Question Format] (300-400 words)
- Answer-first paragraph
- [Chart: type + data description]
- Analysis and implications
- [CITATION CAPSULE placeholder]
- [INTERNAL-LINK: anchor text → target description]

## H2: [Statement for Variety] (300-400 words)
- Answer-first paragraph
- Real-world example or case study
- [Image placement]
- [CITATION CAPSULE placeholder]

## H2: [Question Format] (300-400 words)
- Answer-first paragraph
- [Chart: type + data description]
- Step-by-step guidance
- [CITATION CAPSULE placeholder]
- [INTERNAL-LINK: anchor text → target description]

## H2: [Question Format] (200-300 words)
- Answer-first paragraph
- Forward-looking analysis

## FAQ Section (3-5 questions, 40-60 words each answer)
- [INTERNAL-LINK: anchor text → detailed content]

## Conclusion (100-150 words)
- Key takeaways (bulleted)
- Call to action
- [INTERNAL-LINK: anchor text → next logical content]
```

Present the outline to the user for approval before writing.

### Phase 4: Chart Generation (Built-In)

When the researcher identifies chart-worthy data (3+ comparable metrics, trend data,
before/after comparisons):

1. Select chart type using the diversity rule (no repeated types per post)
2. Invoke `blog-chart` sub-skill with: chart type, title, data values, source, platform format
3. Embed the returned SVG directly in the post within a `<figure>` wrapper
4. Target 2-4 charts per 2,000-word post
5. Distribute charts evenly — never cluster them

See `references/visual-media.md` for chart type selection and styling rules.

### Phase 5: Content Writing

Write the full article following these rules:

#### 5a. Frontmatter
```yaml
---
title: "[Question-format title with primary keyword]"
description: "[Fact-dense, 150-160 chars, includes 1 statistic]"
coverImage: "[URL from Pixabay/Unsplash/Pexels or generated SVG path]"
coverImageAlt: "[Descriptive sentence about the cover image]"
ogImage: "[Same as coverImage, or custom OG image URL]"
date: "YYYY-MM-DD"
lastUpdated: "YYYY-MM-DD"
author: "[Author name]"
tags: ["keyword1", "keyword2", "keyword3"]
---
```

If the platform uses a different field name (e.g., `image`, `hero`, `thumbnail`),
adapt to match the project's existing frontmatter convention.

#### 5b. TL;DR Box

Immediately after the introduction (before the first H2 body section), add a TL;DR box:

```markdown
> **TL;DR:** [40-60 word standalone summary that makes sense without reading the
> full article. Contains the key finding or recommendation plus 1 statistic with
> source attribution. Reader should get the core value from this alone.]
```

Requirements:
- 40-60 words, no more
- Must be self-contained — understandable without reading the article
- Include 1 specific statistic with source name
- State the key finding, recommendation, or answer
- Place as a blockquote directly after the introduction paragraph

#### 5c. Answer-First Formatting (Critical)
Every H2 section MUST open with a 40-60 word paragraph containing:
- At least one specific statistic with source attribution
- A direct answer to the heading's implicit question

Pattern:
```markdown
## How Does X Impact Y in 2026?

[Stat from source] ([Source Name](url), year). [Direct answer to the heading
question in 1-2 more sentences, explaining the implication and what this means
for the reader.]
```

#### 5d. Information Gain Markers

Distribute at least 2-3 information gain markers throughout the article. These
signal to search engines and AI systems that the content contains original value
not available elsewhere.

Tag each with a comment or visible marker:

- `[ORIGINAL DATA]` — Proprietary surveys, experiments, A/B test results, case
  study metrics the author collected first-hand
- `[PERSONAL EXPERIENCE]` — First-hand observations, lessons learned from direct
  involvement, "when we tried X, Y happened" narratives
- `[UNIQUE INSIGHT]` — Analysis others haven't made, contrarian perspectives
  backed by data, novel connections between existing research

Placement:
- Weave into the body text naturally
- Use as inline comments: `<!-- [ORIGINAL DATA] -->` before the relevant paragraph
- Or as visible callouts if the format supports it:
  ```markdown
  > **Our finding:** [original observation backed by specific data]
  ```
- Minimum 2 per post, target 3 for comprehensive articles

These markers map directly to the "Originality/unique value markers" criterion
in the Content Quality scoring category (see `references/quality-scoring.md`).

#### 5e. Citation Capsules

For each major H2 section, generate a citation capsule — a 40-60 word self-contained
passage designed so AI systems can extract and quote it directly.

Requirements per capsule:
- 40-60 words, self-contained (makes sense in isolation)
- Contains: one specific claim + one data point + source attribution
- Written in a declarative, quotable style
- Placed within the H2 section body (not as a separate block)

Example:
```markdown
According to a 2026 Gartner study, 58% of enterprise buyers now consult AI
assistants before contacting a vendor ([Gartner](https://www.gartner.com), 2026).
This shift means B2B content must answer specific questions concisely enough
for AI systems to extract and cite in their responses.
```

Capsules map to the "AI Citation Readiness" scoring category (15 points) in
`references/quality-scoring.md`.

#### 5f. Internal Linking Zones

Mark internal linking opportunities throughout the article using placeholder
notation. The user (or a follow-up pass) will resolve these to actual URLs.

Zone placement:
- **Introduction** — Link to related pillar content or topic hub
- **Each H2 section** — Link to supporting articles, deeper dives, related tools
- **FAQ section** — Link answers to detailed content that expands on the answer
- **Conclusion** — Link to the next logical piece of content the reader should consume

Format:
```markdown
[INTERNAL-LINK: anchor text → target description]
```

Example:
```markdown
For a deeper dive into keyword clustering, see our
[INTERNAL-LINK: complete guide to keyword clustering → pillar page on keyword research methodology].
```

Target 5-10 internal link zones per 2,000-word post. Use descriptive anchor text
(never "click here" or "read more"). See `references/internal-linking.md` for
anchor text rules and linking strategy.

#### 5g. Paragraph Rules
- Every paragraph: 40-80 words (never exceed 150)
- Every sentence: max 15-20 words
- Start each paragraph with the most important information
- Target Flesch Reading Ease: 60-70

#### 5h. Heading Rules
- One H1 (title only)
- H2s for main sections (60-70% as questions)
- H3s for subsections only — never skip levels
- Include primary keyword naturally in 2-3 headings

#### 5i. Image Embedding

Standard markdown:
```markdown
![Descriptive alt text — topic keywords naturally](https://cdn.pixabay.com/photo/...)
```

MDX with Next.js Image (if detected):
```mdx
![Descriptive alt text — topic keywords naturally](https://cdn.pixabay.com/photo/...)
```

- Place images after H2 headings, before body text
- Space evenly throughout the post (not clustered)
- Alt text should be a full descriptive sentence

#### 5j. Chart Embedding

Standard markdown/HTML:
```html
<figure>
  <svg viewBox="0 0 560 380" ...>...</svg>
  <figcaption>Source: [Source Name], [Year]</figcaption>
</figure>
```

MDX format:
```mdx
<figure className="chart-container" style={{margin: '2.5rem 0', textAlign: 'center', padding: '1.5rem', borderRadius: '12px'}}>
  <svg viewBox="0 0 560 380" ...>...</svg>
</figure>
```

#### 5k. Citation Format
Inline attribution (always):
```markdown
Organic CTR declined 61% with AI Overviews ([Seer Interactive](https://www.seerinteractive.com/), 2025).
```

#### 5l. FAQ Section
Add 3-5 FAQ items with 40-60 word answers. Each answer must contain a statistic.

For MDX with FAQSchema component:
```mdx
<FAQSchema faqs={[
  { question: "Question?", answer: "40-60 word answer with statistic and source." },
]} />
```

For standard markdown:
```markdown
## Frequently Asked Questions

### Question text here?

Answer with statistic and source attribution (40-60 words).
```

#### 5m. Internal Linking
- 5-10 internal links per 2,000-word post
- Link to relevant existing content naturally
- Use descriptive anchor text (not "click here")

### Phase 6: Quality Check

Before delivering, verify:

#### Structure and Content
1. Every H2 opens with a statistic + source
2. No paragraph exceeds 150 words
3. All statistics have named tier 1-3 sources
4. 2-4 charts with type diversity
5. 3-5 inline images with descriptive alt text
6. Cover image present in frontmatter (coverImage + ogImage)
7. FAQ section present with 3-5 items
8. Heading hierarchy is clean (H1 -> H2 -> H3)
9. Meta description is 150-160 chars with a stat

#### New Element Verification
10. TL;DR box present after introduction (40-60 words, contains statistic + source)
11. At least 2-3 information gain markers (`[ORIGINAL DATA]`, `[PERSONAL EXPERIENCE]`, or `[UNIQUE INSIGHT]`)
12. Citation capsules present in major H2 sections (40-60 words, self-contained, quotable)
13. Internal linking zones marked in introduction, H2 sections, FAQ, and conclusion
14. No AI-detectable phrases from banned list (see `agents/blog-writer.md`)

#### Burstiness and Naturalness Check
15. **Sentence length variance** — Verify a mix of short (8-word) and long (25-word) sentences. Uniform sentence length signals AI authorship.
16. **Banned AI phrase scan** — Check for and remove:
    - "in today's digital landscape", "it's important to note", "dive into"
    - "game-changer", "navigate the landscape", "revolutionize", "seamlessly"
    - "cutting-edge", "harness the power of", "leverage" (as verb)
    - "delve", "crucial", "elevate", "foster", "landscape" (overused)
    - "multifaceted", "robust", "tapestry", "embark"
    - Full list in `agents/blog-writer.md`
17. **Contractions** — Verify natural use of contractions ("it's", "we've", "don't", "isn't"). Formal AI prose avoids contractions; natural writing uses them.
18. **Rhetorical questions** — Verify at least one rhetorical question every 200-300 words to break up declarative patterns.

### Phase 7: Delivery

Present the completed article with a summary:

```
## Blog Post Complete: [Title]

### Template Used
- [Template name] (or "generic outline — no template matched")

### Statistics
- [N] sourced statistics from tier 1-3 sources
- [N] unique sources cited

### Visual Elements
- Cover image: [source — Pixabay/Unsplash/Pexels or generated SVG]
- [N] inline images (Pixabay/Unsplash/Pexels)
- [N] SVG charts (types: bar, lollipop, donut, line)

### Dual-Optimization Elements
- TL;DR box: present (N words)
- Information gain markers: [N] ([types used])
- Citation capsules: [N] across H2 sections
- Internal linking zones: [N] marked

### Structure
- [N] H2 sections with answer-first formatting
- [N] FAQ items with schema
- Word count: ~[N] words
- Estimated reading time: [N] min

### Naturalness
- Sentence length variance: [pass/fail]
- AI phrase scan: [pass/fail]
- Contractions used: [yes/no]
- Rhetorical questions: [N] (target: 1 per 200-300 words)

### Next Steps
- Review and customize for your brand voice
- Resolve [INTERNAL-LINK] placeholders with actual URLs
- Add internal links to your existing content
- Run `/blog analyze <file>` to verify quality score
```
