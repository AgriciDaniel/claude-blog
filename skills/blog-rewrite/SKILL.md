---
name: blog-rewrite
description: >
  Rewrite and optimize existing blog posts for Google rankings (December 2025
  Core Update, E-E-A-T) and AI citations (GEO/AEO). Replaces fabricated statistics
  with sourced data, applies answer-first formatting, adds Pixabay/Unsplash
  images, generates built-in SVG charts, injects FAQ schema, performs
  AI content detection, adds citation capsules and information gain markers,
  and updates freshness signals. Works with any blog format (MDX, markdown, HTML).
  Use when user says "rewrite blog", "optimize blog", "update blog",
  "improve blog", "fix blog", "refresh blog post", "blog optimization".
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

# Blog Rewriter -- Optimize Existing Posts

Rewrites and optimizes existing blog posts for dual ranking: Google search
and AI citation platforms. Preserves the author's voice while applying the
6 pillars of optimization.

**Key references:**
- `references/quality-scoring.md` — 5-category scoring (Content 30, SEO 25, E-E-A-T 15, Technical 15, AI Citation 15)
- `references/eeat-signals.md` — Experience, expertise, authority, trust markers
- `references/internal-linking.md` — Linking strategy and anchor text rules
- `references/visual-media.md` — Image sourcing and chart styling

## Workflow

### Phase 1: Audit (Read-Only)

1. **Read the blog post** — Detect format (MDX, markdown, HTML)
2. **Run the quality checklist** against `references/quality-scoring.md`:
   - Count fabricated vs sourced statistics
   - Check answer-first formatting (H2 -> stat in first sentence?)
   - Count images and charts (type diversity?)
   - Measure paragraph lengths (any > 150 words?)
   - Check heading hierarchy (H1 -> H2 -> H3, no skips?)
   - Look for FAQ schema
   - Check freshness signals (lastUpdated, dateModified)
   - Assess self-promotion level
   - Evaluate citation tier quality
3. **AI content detection scan**:
   - **Burstiness score** — Measure sentence length variance across the post. Low
     variance (most sentences within 3-5 words of each other) is a strong AI signal.
     Calculate: standard deviation of sentence word counts. Target SD > 6.
   - **Known AI phrase scan** — Check for these high-frequency AI phrases:
     - "in today's digital landscape", "it's important to note", "dive into"
     - "game-changer", "navigate the landscape", "revolutionize", "seamlessly"
     - "cutting-edge", "harness the power of", "leverage" (as verb)
     - "delve", "crucial", "elevate", "foster", "landscape" (overused)
     - "multifaceted", "robust", "tapestry", "embark"
     - Full list in `agents/blog-writer.md`
   - **Vocabulary diversity** — Calculate Type-Token Ratio (TTR): unique words /
     total words. Low TTR (< 0.40) suggests AI-generated repetitive phrasing.
     Target TTR > 0.50 for natural prose.
   - **AI content percentage estimate** — Based on burstiness, phrase density, and
     TTR, estimate what percentage of the content reads as AI-generated (0-100%).
     Report as: "AI content estimate: ~X%"
4. **Cannibalization check**:
   - Identify the post's primary keyword from title, H1, and first paragraph
   - Search the blog directory for other posts targeting the same keyword:
     - Grep headings and meta descriptions across all blog posts
     - Flag any posts with significant keyword overlap
   - If cannibalization found, report:
     - Which posts compete for the same keyword
     - Recommend: **merge** (combine into one stronger post) or **differentiate**
       (shift one post to a related but distinct keyword)
5. **Calculate current score** across 5 categories:
   - Score across 5 categories (Content Quality 30, SEO Optimization 25, E-E-A-T Signals 15, Technical Elements 15, AI Citation Readiness 15)
   - Total: 0-100
6. **Present audit summary** with specific findings, AI detection results, cannibalization status, and score
7. **Enter plan mode** — Present section-by-section optimization plan

Wait for user approval before proceeding.

### Phase 2: Research

1. **Identify the blog's core topic** from existing content
2. **Find replacement statistics** for any fabricated/unsourced data:
   - Search: `[topic] study 2025 2026 data statistics`
   - Target tier 1-3 sources only
3. **Find images** if post has fewer than 3:
   - Pixabay: `site:pixabay.com [topic keywords]`
   - Unsplash: `site:unsplash.com [topic keywords]`
   - Verify each URL returns HTTP 200
4. **Plan charts** if post has fewer than 2:
   - Identify data suitable for visualization
   - Select diverse chart types

### Phase 3: Chart Generation (Built-In)

When the post needs more visual elements, invoke the `blog-chart` sub-skill:

1. Select chart type using the diversity rule (no repeated types per post)
2. Pass: chart type, title, data values, source, platform format
3. Embed the returned SVG directly within a `<figure>` wrapper
4. Target 2-4 charts per 2,000-word post

See `references/visual-media.md` for chart type selection and styling rules.

### Phase 4: Content Rewrite

Apply changes in this order:

#### 4a. Preserve What Works
- Keep the author's voice and unique perspective
- Preserve original insights and first-hand experience
- Keep existing quality images and charts
- Maintain internal links

#### 4b. Fix Frontmatter
- Add `lastUpdated: "YYYY-MM-DD"` (today's date)
- Keep original `date` unchanged
- Fix meta description: fact-dense, 150-160 chars, includes 1 statistic
- Add `coverImage` + `coverImageAlt` + `ogImage` if missing
  - Search Pixabay/Unsplash/Pexels for wide hero image (1200x630)
  - Or generate custom SVG cover via `blog-chart` (text-on-gradient with key stat)
- Verify tags/categories are appropriate

#### 4c. Apply Answer-First Formatting
Every H2 section MUST open with a 40-60 word paragraph containing:
- At least one specific statistic with source attribution
- A direct answer to the heading's implicit question

#### 4d. Replace Fabricated Statistics
- Search for patterns: "X% of...", "X out of Y...", unsourced claims
- Replace with real data from tier 1-3 sources
- Always include inline attribution: `([Source Name](url), year)`

#### 4e. Improve Headings
- Convert statement headings to questions where natural (60-70% target)
- Keep 2-3 statement headings for variety
- Ensure keyword appears in 2-3 headings naturally

#### 4f. Fix Paragraph Length
- Split any paragraph > 150 words
- Target 40-80 words per paragraph
- Ensure each paragraph starts with its most important sentence

#### 4g. Add Visual Elements
- Embed new images after H2 headings, spaced evenly
- Embed charts within relevant sections
- Adapt embed format to detected platform (MDX vs markdown vs HTML)

#### 4h. Add/Improve FAQ
- If no FAQ exists, add one (3-5 questions)
- If FAQ exists, ensure answers are 40-60 words with statistics
- Add FAQ schema markup appropriate to platform

#### 4i. Reduce Self-Promotion
- Max 1 brand mention (author bio context only)
- Remove "At [Company], we..." patterns
- Convert promotional sections to educational content

#### 4j. Citation Capsule Injection
For each H2 section, generate (or improve existing) a citation capsule:
- 40-60 word self-contained passage per H2
- Contains: one specific claim + one data point + source attribution
- Written in a declarative style so an AI system could extract and quote it directly
- Placed naturally within the section body, not as a separate callout

Example:
```markdown
According to a 2026 Gartner study, 58% of enterprise buyers now consult AI
assistants before contacting a vendor ([Gartner](https://www.gartner.com), 2026).
This shift means B2B content must answer specific questions concisely enough
for AI systems to extract and cite in their responses.
```

Capsules map to the "AI Citation Readiness" category (15 points) in
`references/quality-scoring.md`.

#### 4k. Anti-AI-Detection Patterns
Apply these transformations to reduce AI-detectable writing patterns:
- **Replace flagged phrases** — Swap every detected AI phrase (from the scan in
  Phase 1 step 3) with a natural alternative. Examples:
  - "it's important to note" -> "worth noting" or "keep in mind"
  - "in today's digital landscape" -> "right now" or "in [specific year]"
  - "leverage" -> "use", "apply", "take advantage of"
  - "delve" -> "look at", "explore", "dig into"
  - "robust" -> "strong", "solid", "reliable"
  - "crucial" -> "key", "essential", "critical" (or restructure the sentence)
- **Vary sentence length deliberately** — After rewriting, scan each paragraph.
  Inject short punchy sentences (5-10 words) between longer ones (18-25 words).
  Target: no more than 3 consecutive sentences within 5 words of each other's length.
- **Inject rhetorical questions** — Add at least one rhetorical question every
  200-300 words to break up declarative monotony.
- **Use contractions naturally** — Replace formal constructions with contractions
  where they sound natural: "it is" -> "it's", "we have" -> "we've",
  "do not" -> "don't", "is not" -> "isn't".
- **Include hedging language** — Sprinkle first-person hedges that signal real
  experience: "in our experience", "we've found that", "from what we've seen",
  "this tends to", "it depends on".

#### 4l. TL;DR Box
If the post lacks a TL;DR box, add one immediately after the introduction:
```markdown
> **TL;DR:** [40-60 word standalone summary. Contains the key finding or
> recommendation plus 1 statistic with source. Self-contained — reader gets
> the core value without reading the full article.]
```
If a TL;DR already exists, verify it meets the 40-60 word requirement and
contains a statistic with source attribution.

#### 4m. Information Gain Marker Injection
Review the post for original value and tag it:
- `[ORIGINAL DATA]` — Any proprietary data, survey results, experiments, or
  case study metrics the author collected first-hand
- `[PERSONAL EXPERIENCE]` — First-hand observations, lessons learned
- `[UNIQUE INSIGHT]` — Novel analysis, contrarian perspectives backed by data

If the post lacks original value markers:
- Ask the author for first-hand data or experience to include
- At minimum, add analytical insights that connect existing research in new ways
- Target: at least 2-3 markers per post

Use HTML comments (`<!-- [ORIGINAL DATA] -->`) or visible callouts depending
on the post's style.

### Phase 5: Verification

After rewriting, verify all quality gates pass:

#### Core Quality Gates
1. Every H2 opens with a statistic + source
2. No paragraph exceeds 150 words
3. Zero fabricated statistics
4. Heading hierarchy is clean
5. FAQ section present with schema
6. Images have descriptive alt text
7. Cover image present in frontmatter (coverImage + ogImage)
8. If MDX: build the project to verify no compilation errors

#### New Element Verification
9. TL;DR box present after introduction (40-60 words, contains statistic)
10. At least 2-3 information gain markers present
11. Citation capsules in major H2 sections (40-60 words, self-contained)
12. Internal linking zones marked or actual links present (5-10 per 2,000 words)
13. No AI-detectable phrases remain from banned list

#### Burstiness and Naturalness Check
14. Sentence length variance: SD > 6 (mix of short and long sentences)
15. Contractions used naturally throughout
16. Rhetorical questions present (1 per 200-300 words)
17. AI content estimate reduced from audit baseline
18. Score improved across all 5 categories vs Phase 1 audit

### Phase 6: Summary

```
## Blog Optimization Complete: [Title]

### Score Change
- Before: [X]/100 ([Rating])
  - Content Quality: [X]/30
  - SEO Optimization: [X]/25
  - E-E-A-T Signals: [X]/15
  - Technical Elements: [X]/15
  - AI Citation Readiness: [X]/15
- After: [Y]/100 ([Rating])
  - Content Quality: [Y]/30
  - SEO Optimization: [Y]/25
  - E-E-A-T Signals: [Y]/15
  - Technical Elements: [Y]/15
  - AI Citation Readiness: [Y]/15

### AI Detection
- Before: ~[X]% AI-detected content
- After: ~[Y]% AI-detected content
- Phrases replaced: [N]
- Burstiness improved: [before SD] -> [after SD]

### Cannibalization
- [Status: none found / flagged N posts / resolved]

### Changes Made
- [X] statistics replaced with sourced data
- [X] SVG charts added (types: ...)
- [X] images added from Pixabay/Unsplash
- Answer-first formatting applied to [N] H2 sections
- FAQ schema injected with [N] questions
- TL;DR box: [added/updated]
- Information gain markers: [N] ([types])
- Citation capsules: [N] across H2 sections
- AI phrases replaced: [N]
- lastUpdated set to [date]
- Self-promotion reduced to [N] mentions

### Visual Elements
- Charts: [count] ([types])
- Images: [count]

### Ready for
- `/blog analyze <file>` to verify final score
- Publishing / deploying
```

## Update Mode

When invoked as `/blog update <file>`, focus on freshness:
1. Update statistics to latest available data (2025-2026)
2. Add new developments since last update
3. Refresh images if older than 1 year
4. Update `lastUpdated` in frontmatter
5. Preserve the existing structure — minimize rewrites
6. Target: at least 30% content change to register as "fresh" for AI crawlers
