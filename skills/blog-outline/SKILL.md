---
name: blog-outline
description: >
  SERP-informed outline generation with H2/H3 heading hierarchy, competitive
  content gap analysis, section-by-section word count targets, chart and image
  placement markers, FAQ question planning, and internal linking zones. Lighter
  than a full content brief — generates article skeleton and structure only,
  ready for /blog write to consume. Use when user says "outline", "blog outline",
  "content outline", "structure blog", "plan sections", "article skeleton",
  "heading structure", "SERP analysis", "competitive outline", "plan article".
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
  - WebSearch
  - WebFetch
---

# Blog Outline Generator -- SERP-Informed Structure Planning

Generates skeletal blog post outlines informed by SERP analysis. A lighter
alternative to a full content brief — produces heading hierarchy, section
targets, and content gap notes without deep statistics research or full
competitive analysis.

## Workflow

### Step 1: Topic & Intent

Gather from the user:
1. **Topic or target keyword** (required)
2. **Target keyword** — the exact phrase to rank for (if different from topic)
3. **Search intent** — Informational, commercial, or transactional

If only a topic is given, infer the keyword and intent from context.

### Step 2: SERP Analysis

Use WebSearch to analyze the top 5 results for the target keyword:

1. Search for the target keyword
2. For each of the top 5 results, note:
   - **Heading structure** — H2/H3 topics covered
   - **Content length** — Approximate word count
   - **Visual elements** — Charts, images, videos, infographics
   - **FAQs** — Any FAQ sections or People Also Ask coverage
   - **Unique angles** — What makes each result distinct
   - **Gaps** — What's missing or weak

3. Use WebFetch on the top 2-3 results to extract detailed heading structures
   if the search snippets are insufficient.

4. Compile a summary of common patterns and missed opportunities.

### Step 3: Generate Outline

Create a structured outline with the following format:

```
# Outline: [Topic]

## Title Suggestions
1. [Primary title — 40-60 chars, front-loaded keyword, power word]
2. [Alternative title — different angle]
3. [Alternative title — question format]

## Target Parameters
- **Primary keyword**: [keyword]
- **Search intent**: [Informational/Commercial/Transactional]
- **Target word count**: [X,XXX] words
- **H2 sections**: [6-8]
- **Target reading level**: Flesch 60-70

---

## Outline

### H2: [Section Title — Question Format] (~300-400 words)
- **Answer-first opener**: [What stat or fact should open this section?]
- **Key points to cover**:
  - [Point 1]
  - [Point 2]
  - [Point 3]
- **H3: [Subsection]** (if appropriate)
  - [What this subsection covers]
- **Key statistic to find**: [What data point would strengthen this section?]
- **Chart suggestion**: [Bar/Line/Donut/None] — [What data to visualize]
- **Image placement**: [Yes/No] — [Description of recommended image]

### H2: [Section Title] (~300-400 words)
[... repeat for 6-8 sections ...]

### FAQ Section (3-5 items)
1. [Question from People Also Ask] — [Brief answer direction]
2. [Question from People Also Ask] — [Brief answer direction]
3. [Question from People Also Ask] — [Brief answer direction]
4. [Question from SERP analysis] — [Brief answer direction]

### Conclusion (~100-150 words)
- Key takeaways to summarize
- Call to action direction

---

## Internal Linking Zones
- **Link TO from this post**: [Existing content that should be referenced]
- **Link FROM to this post**: [Existing content that should link here]

## Content Gaps to Exploit
1. [What competitors miss that this post should cover]
2. [Unique angle or original perspective to include]
3. [Format advantage — visuals, depth, or structure competitors lack]
```

Guidelines for heading generation:
- 60-70% of H2 headings should be in question format
- Each H2 should have a clear answer-first paragraph prompt
- Include H3 subsections only where the topic genuinely warrants subdivision
- Target word counts should sum to the overall post target
- Chart type suggestions should be diverse (no two identical types)
- Image placement markers should be distributed evenly across the post

### Step 4: Content Gaps

After generating the outline, add a dedicated content gaps analysis:
1. List 3-5 topics or angles that all top-ranking competitors miss
2. Identify opportunities for original data, case studies, or perspectives
3. Note format advantages this post can have (more visuals, better structure,
   deeper coverage on a specific subtopic)

### Step 5: Save

Save the outline to `outlines/[slug]-outline.md` or to a user-specified path.
Confirm the outline is ready for `/blog write` to consume.

If the `outlines/` directory does not exist, create it.
