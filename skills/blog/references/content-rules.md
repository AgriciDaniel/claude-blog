# Content Structure Rules: Dual Optimization

## Contents

- [Purpose-First Formatting](#purpose-first-formatting)
- [Title Optimization](#title-optimization)
- [Summary Box Requirement](#summary-box-requirement)
- [Heading Hierarchy](#heading-hierarchy)
- [Sentence Rules](#sentence-rules)
- [Paragraph Rules](#paragraph-rules)
- [Readability Targets](#readability-targets)
- [Visual Content Rules](#visual-content-rules)
- [Anti-Pattern Detection](#anti-pattern-detection)
- [Content Length Guidelines](#content-length-guidelines)
- [Citation Statistics Rules (AI Search SEO)](#citation-statistics-rules-ai-search-seo)
- [Information Gain: The Key Differentiator](#information-gain-the-key-differentiator)
- [Meta Description Formula](#meta-description-formula)
- [Citation Format](#citation-format)
- [Citation Tiers](#citation-tiers)
- [Self-Promotion Rules](#self-promotion-rules)
- [Internal Linking](#internal-linking)

## Purpose-First Formatting

Important sections should state their point early, using the length and heading
form that best fits the material. A section opener can:

1. Directly answers the heading's implicit question
2. Names the core entity, year, and practical implication
3. Lead into a self-contained explanation with verified support when the claim needs it

### Pattern
```markdown
## Impact of X on Y

[Clear conclusion naming the entity and practical implication.]
[Continue with enough source-backed context, dates, implications, and examples
to satisfy the reader. Do not pad to a target length.]
```

### Why It Works
Readers can identify the point faster when important answers appear early.
Some vendor samples observe more cited material near the start of pages, but
that pattern is non-causal and query-dependent. Use direct declarative
structures when they improve clarity, then provide the context and source
attribution the claim needs.

## Title Optimization

| Check | Editorial Guidance |
|-------|--------------------|
| Accuracy | Describe the visible page without exaggeration |
| Purpose fit | Make the reader task or subject clear |
| Distinctiveness | Avoid generic titles that could label unrelated pages |
| Truncation resilience | Keep critical meaning understandable in likely previews |
| Topic consistency | Use natural terminology consistent with the page |

### Title Formula
Pattern: `[Clear Topic]: [Specific Reader-Relevant Scope]`
Example: `[TOPIC]: [SUPPORTED SCOPE OR OUTCOME]`

Avoid: clickbait, ALL CAPS words, excessive punctuation, vague promises.

## Optional Summary Box

A summary box may follow the title or introduction when it helps the content
type and reader:

- **Length**: As short as the material allows while remaining useful
- **Purpose**: Reader orientation and a concise decision aid
- **Content**: 3-5 bullet points covering core findings; include a sourced key statistic only when central
- **Format**: Visually distinct block (callout, bordered box, or blockquote)
- **Rule**: If included, it must be comprehensible without reading the rest of the article

### Pattern
The default label is **Key Takeaways** (professional, universally understood).
Alternative labels configurable per persona: "The Bottom Line" (business/finance),
"What You'll Learn" (educational/tutorial), "At a Glance" (scan-optimized),
"In Brief" (journalistic).

Format: 3-5 bullet points (not a prose paragraph):
```markdown
> **Key Takeaways**
> - [Core finding with statistic] ([Source], year)
> - [Second key insight or recommendation]
> - [Third actionable takeaway]
```

For backward compatibility, blog-analyze accepts "TL;DR", "Key Takeaways",
"Summary", and "Quick Answer".

## Heading Hierarchy

### Rules
- ONE H1 per page (the title only)
- H2s for main sections (target 6-8 per post)
- Add headings where they clarify topic boundaries; no fixed spacing quota
- H3 every 100-200 words under each H2 for deeper structure
- H3s for subsections - never skip levels (no H2 → H4)
- Include primary keyword naturally in 2-3 headings

### Heading Form
Use questions only when they match how readers frame the task:
- "The Future of X" → "What Does X Look Like in 2026?"
- "Strategies for Y" → "How Do You Achieve Y in 2026?"
- Mix declarative, noun-phrase, and question headings naturally

### Why Questions Work
Heading form is not a ranking or citation quota. Clear hierarchy and accurate
labels matter more than punctuation.

## Sentence Rules

| Parameter | Optional Observation | Interpretation |
|-----------|----------------------|----------------|
| Average sentence length | Descriptive sample | Judge against audience and subject |
| Long sentences | Review in context | Split only when comprehension improves |
| Sentence-length distribution | Descriptive sample | No universal percentage |
| Sentence-length variance | Review for monotony | Internal style diagnostic only |

### Sentence Rhythm
Vary sentence structure when it improves rhythm, emphasis, or comprehension.
Sentence-length variance cannot determine authorship and never affects
readiness scoring. Do not enforce a fixed distribution.

## Paragraph Rules

| Parameter | Optional Observation | Interpretation |
|-----------|----------------------|----------------|
| Paragraph length | Descriptive sample | Judge against intent and comprehension |
| Sentences per paragraph | Descriptive sample | One or many can be appropriate |
| Mobile presentation | Visual density and line wrapping | Test the rendered page |

### Key Principle
Start each paragraph with the most important sentence. This enables both
readers and AI to grasp concepts by scanning. 79% of users scan rather than
read (NNGroup). Concise, scannable formatting improves usability 124-159%
(NNGroup).

### Paragraph Review
Single-sentence and multi-sentence paragraphs can both be appropriate. Split a
paragraph when it contains competing ideas or becomes difficult to follow, not
because it crossed a fixed count.

One topic per paragraph - no topic drift within a paragraph.

## Readability Targets

| Metric | Target | Acceptable | Source |
|--------|--------|-----------|--------|
| Flesch Reading Ease | 60-70 | 55-75 | Optional internal clarity heuristic |
| Flesch-Kincaid Grade | 7-8 | 6-9 (B2B/technical: 8-10) | Siteimprove, First Page Sage |
| Gunning Fog | 7-8 | Max 12 | Springer 2023: highest correlation with engagement |
| SMOG | ≤8 | - | Healthcare gold standard |

Flesch 60-70 is an optional default clarity band. Adjust it for the audience,
subject, and publication voice. It is not a Google signal, authorship test,
ranking factor, readiness score, or citation predictor.

Fluent, specific, well-structured content helps readers. Do not claim that a
readability band causes AI citation; useful content also needs accurate
evidence, clear entities, and distinctive value.

### Readability Bands by Audience
| Audience | Flesch Grade | Flesch Ease | Max Sentence | Use When |
|----------|-------------|-------------|--------------|----------|
| Consumer | 6-8 | 60-80 | 20 words | General audience, lifestyle, health |
| Professional (B2B) | 8-10 | 50-60 | 25 words | Business, marketing, finance |
| Technical/Developer | 10-12 | 30-50 | 30 words | Engineering, API docs, data science |

Default target (no persona active): Grade 7-8, Flesch Ease 60-70.
When a persona is active, use the persona's readability band instead.
Readability is an internal editorial heuristic, not a calibrated citation
probability. Match the audience rather than forcing a universal grade level.

## Visual Content Rules

| Parameter | Target | Minimum | Source |
|-----------|--------|---------|--------|
| Image/visual frequency | Every 200-350 words | 1 per 500 words | BuzzSumo, NNGroup |
| Bold/emphasis | 3-5 per 300 words | - | Competitive analysis |
| Bold % of total text | <10% | - | Diminishing impact above 10% |

### Lists
Use bulleted or numbered lists when 3+ parallel items exist. Don't force lists
where prose works better - lists are for scannable parallel items, not for
every piece of information.

### Visual Impact
Older visual-content studies reported large engagement lifts, but those figures
are historical context rather than active 2026 targets. Use visuals when they
clarify, prove, or summarize information. NNGroup scanning research supports
using visuals to anchor key information for readers.

### Visual Rhythm (Mandatory Pacing)
Insert a visual element (image, chart, or callout) every 300-500 words.
- Minimum: 1 visual per 500 words; optimal: 1 per 300-350 words
- Alternate visual types: image -> chart -> callout -> image (no consecutive same-type)
- Hero image: above the fold, 1920x1080 (16:9) or 1200x630 (OG-compatible)
- All images: explicit width/height attributes for CLS prevention (score <= 0.1)
- Below-fold images: loading="lazy"; hero image: fetchpriority="high"
- Posts with 10+ visuals are 2x more likely to report strong results (Orbit Media)
- 79% of people scan content rather than reading it (NNGroup)

## Project Style Diagnostics

### Configured Style-List Terms
The following terms may be flagged for manual voice review. Their presence does
not identify AI authorship, violate Google policy, or change the score:

delve, tapestry, multifaceted, testament, pivotal, robust, cutting-edge,
furthermore, indeed, moreover, utilize, leverage, comprehensive, landscape,
crucial, foster, illuminate, underscore, embark, endeavor, facilitate,
paramount, nuanced, intricate, meticulous, realm

### Em Dashes (Project Style)
NEVER use the em dash character, U+2014, in blog content. Replace it with
commas, hyphens, colons, or periods. Split sentences when a long dash was used
to join two independent clauses.

### Passive Voice (Optional Project Diagnostic)
Review passive-voice clusters when active voice would make a sentence clearer.
Passive voice can be correct, so there is no universal threshold. This
diagnostic is a project readability and voice preference, not an AI-authorship
test or Google signal.

### Transition Words
Review unusually repetitive connective phrasing for clarity. Do not infer
authorship or enforce a universal percentage.

### Topic Terminology
Use stable, natural terminology so the title, headings, and body describe the
same topic. Do not enforce exact-match placement or keyword-density bands.

### Filler Content Detection
QRG 2025 targets "artificially inflated content." Flag: entity drift,
topical dilution, needless repetition, intent mismatch.

## Content Length Planning Ranges

| Content Type | Optional Planning Range | Final-Length Rule |
|-------------|-------------------------|-------------------|
| Pillar guide | Often 3,000-4,000 words | Complete the reader task without padding |
| Standard blog post | Often 2,000-2,500 words | Complete the reader task without padding |
| Comparison post | Often 1,500-2,000 words | Cover the decision criteria that matter |
| FAQ/listicle | Often 1,500-2,000 words | Include only useful questions or items |
| News/update | Often 800-1,200 words | Match the significance and available facts |

These are planning ranges for template sizing, not Google preferences or score
thresholds. A shorter page can pass when it completely serves the intent; a
longer page must justify every section.

Reading time can be estimated from word count for reader convenience. Do not
optimize toward a universal duration; the appropriate depth depends on intent.

## Citation Statistics Rules (AI Search SEO)

| Parameter | Target | AI Search SEO Optimized | Source |
|-----------|--------|--------------|--------|
| Statistic use | As evidence needs warrant | No density quota | Reader and source fidelity |
| External citations | As verification needs warrant | No density quota | Source traceability |
| Internal links | Where they help navigation | No density quota | Reader navigation |

Experimental and vendor studies have tested statistics, citations, and fluency
on defined query sets. Treat them as research context, not expected uplift.
Use statistics and citations only when they support reader understanding.

### Attribution Format
Attribute material statistics close enough to the claim that readers can trace
the support. Use a citation format appropriate to the publication.
Unattributed statistics damage E-E-A-T trust signals and are flagged as
fabrication risks in quality scoring.

**Useful source-record fields:**

- Date or study period when it changes the meaning of the claim.
- Publisher and document title when needed to identify the source.
- A stable URL, plus a retrieval date for changeable or undated material.
- Methodology and limitations when they affect interpretation.

Drop unverifiable stats. Replace contradicted stats with verified alternatives. See `flow-alignment.md`.

## Information Gain: The Key Differentiator

Google's Information Gain patent (US11354342B2, 2022) suggests a retrieval
concept for valuing novel information, but patents do not prove current ranking
use. Treat information gain as an editorial differentiation principle:

1. **Original research**: Surveys, proprietary data, experiments (+25.1% top-10, Stratabeat)
2. **Personal perspective**: Opinions AI cannot replicate
3. **Expert interviews**: Practitioners with first-hand knowledge
4. **Case studies**: Real metrics and results
5. **Industry-segmented analysis**: Break down by vertical (+43.4% top-10, Animalz)

## Meta Description Formula

Pattern: "[Specific value proposition]. Here's how [strategy] delivers [outcome] in 2026."

Rules:
- Accurately and specifically summarize the visible page
- Put the most useful information early so truncation does not obscure the point
- Include a specific statistic only when it is central and sourced
- No keyword stuffing
- Make the value clear without forcing a call to action

## Citation Format

Inline: `[Number]% [claim] ([Source](url), [Year])`. Always name the source.
Study: Name the paper, institution, and year. Quote: Use quotation marks with speaker name and date.

## Citation Tiers

| Tier | Examples | Trust |
|------|----------|-------|
| 1 - Primary Authority | Google Search Central, .gov, .edu, W3C | Highest |
| 2 - Primary Data | Ahrefs, SparkToro, Seer, BrightEdge, Princeton GEO Paper | High |
| 3 - Trusted Journalism | Search Engine Land, SEJ, The Verge, Wired, TechCrunch | Good |
| 4-5 - AVOID | SEO tool blogs (non-research), affiliate sites, content mills | Hurts E-E-A-T |

## Self-Promotion Rules

- Keep brand mentions intent-specific: strict for informational posts, more flexible for product reviews, case studies, and branded BOFU pages
- Remove "At [Company], we..." patterns and promotional links
- Author section should demonstrate E-E-A-T credentials, not sell

## Internal Linking

- 5-10 internal links per 2,000-word post, descriptive anchor text
- Ensure bidirectional linking (pillar ↔ supporting pages)
