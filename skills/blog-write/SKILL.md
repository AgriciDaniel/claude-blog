---
name: blog-write
description: >
  Write new blog articles from scratch optimized for Google rankings and AI
  citations. Generates full articles with template selection, answer-first
  formatting, Key Takeaways summary box, information gain markers, evidence-backed explanations, sourced
  statistics, Pixabay/Unsplash images, built-in SVG chart generation, optional FAQ sections,
  internal linking zones, and proper heading hierarchy. Supports MDX, markdown,
  and HTML output.
  Use when user says "write blog", "new blog post", "create article",
  "write about", "draft blog", "generate blog post".
user-invocable: true
argument-hint: "<topic>"
license: MIT
---

# Blog Writer: New Article Generation

Bundled paths below use host Markdown substitution of `${CLAUDE_SKILL_DIR}`;
it is not an exported shell variable. Resolve them before execution, quote
paths, and refuse nonabsolute overrides. Pass `blog_reference_root` resolved
from `${CLAUDE_SKILL_DIR}/../blog/references`, `blog_template_root` from
`${CLAUDE_SKILL_DIR}/../blog/templates`, and needed sibling roots to agents.
Read the main reference `orchestration-details.md` before loading project
context; pass only its helper-fenced output to downstream agents.

Writes complete blog articles from a topic, brief, or outline. Every article
follows the 6 pillars of dual optimization (Google rankings + AI citations).

**Key references** (paths relative to repo root; references live in the
main `blog` skill's references directory, not in `blog-write/`):

- `${CLAUDE_SKILL_DIR}/../blog/references/synthesis-contract.md`: 6 LAWs for synthesis output (v1.8.0; applies whenever the article embeds research-synthesis prose)
- `${CLAUDE_SKILL_DIR}/../blog/references/content-templates.md`: Template selection guide and usage
- `${CLAUDE_SKILL_DIR}/../blog/references/quality-scoring.md`: 5-category scoring (Content 30, SEO 25, E-E-A-T 15, Technical 15, AI Citation 15)
- `${CLAUDE_SKILL_DIR}/../blog/references/eeat-signals.md`: Experience, expertise, authority, trust markers
- `${CLAUDE_SKILL_DIR}/../blog/references/internal-linking.md`: Linking strategy and anchor text rules
- `${CLAUDE_SKILL_DIR}/../blog/references/visual-media.md`: Image sourcing and chart styling
- `${CLAUDE_SKILL_DIR}/../blog-write/references/delivery.md`: delivery contract steps and summary template for this sub-skill

## Workflow

### Phase 0: Surface Targeting (do this BEFORE research)

Decide which of the FLOW 5 surfaces this post is meant to win. The choice
shapes structure, length, citation density, and call-to-action. The 5 surfaces
in 2026:

1. Owned site (organic Google ranking)
2. SERP including AI Overviews
3. AI assistant citations (ChatGPT, Perplexity, Claude, Gemini, Copilot, You.com)
4. Local pack (out of scope for blog content; use claude-seo for local)
5. Communities and video (Reddit, YouTube, LinkedIn, Quora, niche forums)

Most posts target surfaces 1, 2, and 3 by default. If the same query also
surfaces in a community (Reddit thread, YouTube comment), apply dual-surface
thinking: optimize the post for extraction AND plan a community echo (covered
in `/blog repurpose`).

The article remains subject-led. Choose its structure, evidence, examples,
media, and tone from what the reader needs to understand or do. Do not make a
post resemble an abstract blog template by adding sections, statistics, media,
questions, or stock phrases that the subject does not earn.

For a deeper surface-by-surface workflow, see
`${CLAUDE_SKILL_DIR}/../blog/references/flow-alignment.md` and `/blog flow find`.

### Phase 1: Topic Understanding

1. **Clarify the topic** - If the user provides just a topic, ask:
   - Target audience (who is this for?)
   - Primary keyword / search intent
   - Desired depth or word-count constraint, if any. Treat 2,000-2,500 words as
     a planning estimate only when the task warrants a comprehensive guide.
   - Platform/format (MDX, markdown, HTML - auto-detect if in a project)
2. **If a brief exists** - Load it and skip to Phase 1.5

### Phase 1.5: Template Selection

Select the appropriate content template from the 12 templates in
`${CLAUDE_SKILL_DIR}/../blog/templates/` (the main `blog` skill owns the templates directory).

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

2. **Check template evidence before selection**:
   - `product-review` requires documented first-hand testing.
   - `case-study` requires measurable outcomes and permission to identify the subject.
   - `roundup` requires attributable contributions from credible participants.
   - `data-research` requires original data and a transparent methodology.
   If the required evidence is unavailable, do not simulate it. Select another
   supported template that fits the evidence, or return a concise evidence-needs
   brief listing what must be supplied before drafting.
3. **Load the matching template**: Read from `${CLAUDE_SKILL_DIR}/../blog/templates/<type>.md`
4. **Adapt the outline** - Use the template's section structure, heading patterns,
   and word count guidance to shape Phase 3's outline
5. **Fallback** - If no template clearly fits, use the generic outline structure
   in Phase 3 below. Inform the user which template was selected (or that none matched).

See `${CLAUDE_SKILL_DIR}/../blog/references/content-templates.md` for detailed selection criteria and intent mapping.

### Phase 2: Research

Spawn a `blog-researcher` agent (or do inline research with WebSearch):

1. **Find the current evidence the subject requires**
   - Search: `[topic] study 2025 2026 data statistics`
   - Prioritize tier 1-3 sources (see `${CLAUDE_SKILL_DIR}/../blog/references/quality-scoring.md`)
   - Record: statistic, source name, URL, date, methodology
2. **Find a cover image** (wide, high-quality, topic-relevant):
   - Prefer original screenshots, product visuals, diagrams, or data graphics when available
   - For stock, use official APIs such as Openverse, Unsplash, Pexels, or Pixabay so license, creator, source URL, and download URL are captured
   - Download approved assets into the draft folder, store attribution, and never hotlink arbitrary CDN URLs
   - Reject `javascript:`, `data:`, and `file:` image URLs
   - Target dimensions: 1200x630 (OG-compatible) or 1920x1080
   - Or generate a custom SVG cover via `blog-chart` (text-on-gradient with key stat)
   - Or generate a custom AI image via `blog-image`; prefer `gemini-3.1-flash-image`, then `gemini-3.1-flash-lite-image` or `gemini-3-pro-image` when available, and record the model ID
   - See `${CLAUDE_SKILL_DIR}/../blog/references/visual-media.md` for cover image sizing details
3. **Find inline images only where they explain, demonstrate, or verify something prose cannot**:
   - Use official APIs or Openverse search; keep license, creator, source URL, and retrieval date with each asset
   - Download images locally and reference local paths in the draft
   - Validate final URLs with the delivery contract SSRF rules before download
4. **Plan data visualizations only for meaningful comparisons, distributions, or trends**
   - Select diverse chart types (see `${CLAUDE_SKILL_DIR}/../blog/references/visual-media.md`)
   - Map data points to chart formats
5. **AI image generation** (optional, if `blog-image` is available):
   - If stock photo results are insufficient for a justified visual need or the topic is too niche
   - Generate custom hero image and/or inline illustrations via `blog-image` sub-skill
   - Record prompt, provider, and model ID; stock photos remain available, but original and data visuals are preferred when they better serve the topic
6. **NotebookLM research** (optional, if user has relevant notebooks):
   - If the user mentions a NotebookLM notebook or the topic aligns with a configured notebook
   - Query via `blog-notebooklm` for source-grounded data from user-uploaded documents
   - Inherit the source tier from the underlying document provenance; user's own primary documents can be Tier 1, while copied secondary sources keep their original tier
   - Falls back silently if not configured or not authenticated
7. **Find relevant YouTube videos only when a demonstration or expert source materially helps the article**:
   - Use `blog-google` youtube command or WebSearch `site:youtube.com [topic] [year]`
   - Apply quality criteria from `${CLAUDE_SKILL_DIR}/../blog/references/video-embeds.md` (min score 50/100)
   - Select only videos that add evidence or explanation. Falls back silently if none qualify.

### Phase 3: Outline Generation

Create a structured outline before writing. If a template was loaded in Phase 1.5,
adapt this skeleton to match the template's section structure:

```
# [Title as Question - Include Primary Keyword]

## Introduction (100-150 words)
- Open with the reader's problem, a useful finding, a concrete example, or an
  optional verified statistic when evidence makes that the strongest hook
- Problem/opportunity statement
- What the reader will learn

> **Key Takeaways**
> - [Core finding with statistic and source]
> - [Second key insight or recommendation]
> - [Third actionable takeaway]
> (Concise bullets sized to the material when a summary helps this content type)

## H2: [Intent-Matched Heading]
- Clear section point with verified support where needed
- Supporting evidence
- [Image placement]
- Practical advice
- [EVIDENCE-BACKED EXPLANATION placeholder]
- [INTERNAL-LINK: anchor text → target description]

## H2: [Intent-Matched Heading]
- Answer-first paragraph
- [Chart: type + data description]
- Analysis and implications
- [EVIDENCE-BACKED EXPLANATION placeholder]
- [INTERNAL-LINK: anchor text → target description]

## H2: [Intent-Matched Heading]
- Answer-first paragraph
- Real-world example or case study
- [Image placement]
- [EVIDENCE-BACKED EXPLANATION placeholder]

## H2: [Intent-Matched Heading]
- Answer-first paragraph
- [Chart: type + data description]
- Step-by-step guidance
- [EVIDENCE-BACKED EXPLANATION placeholder]
- [INTERNAL-LINK: anchor text → target description]

## H2: [Intent-Matched Heading]
- Answer-first paragraph
- Forward-looking analysis

## [CTA Section or Inline Placement]
- See `${CLAUDE_SKILL_DIR}/../blog/references/cta-placement.md` for placement rules by content type
- Place CTA after value delivery, not at arbitrary positions
- Single focused CTA per post (266% more conversions)
- [CTA: contextual call-to-action matching article topic]

## Optional FAQ Section (only when real reader questions warrant it)
- [INTERNAL-LINK: anchor text → detailed content]

## Conclusion (100-150 words)
- Key takeaways (bulleted)
- Call to action
- [INTERNAL-LINK: anchor text → next logical content]
```

Present the outline to the user for approval before writing.

**Visual selection**: Insert `[IMAGE]`, `[CHART]`, `[VIDEO]`, or `[CALLOUT]`
markers only where the visual materially improves understanding, proof, or task
completion. Do not use a word-count interval or media quota. Avoid consecutive
same-type visuals when variation makes the sequence easier to understand. See
`${CLAUDE_SKILL_DIR}/../blog/references/content-rules.md` Visual Rhythm section and
`${CLAUDE_SKILL_DIR}/../blog/references/cta-placement.md` for CTA positioning.

### Phase 4: Chart Generation (Built-In)

When the researcher identifies chart-worthy data (3+ comparable metrics, trend data,
before/after comparisons):

1. Select chart type using the diversity rule (no repeated types per post)
2. Invoke `blog-chart` sub-skill with: chart type, title, data values, source, platform format
3. Embed the returned SVG directly in the post within a `<figure>` wrapper
4. Use as many charts as the chart-worthy evidence requires, including none
5. Place each chart beside the claim or comparison it supports

See `${CLAUDE_SKILL_DIR}/../blog/references/visual-media.md` for chart type selection and styling rules.

### Phase 5: Content Writing

Write the full article following these rules:

#### 5a. Frontmatter
```yaml
---
title: "[Clear title that identifies the page and matches search intent]"
description: "[Accurate, page-specific summary of the visible content]"
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

#### 5b. Summary Box (Key Takeaways)

Immediately after the introduction (before the first H2 body section), add a summary box:

```markdown
> **Key Takeaways**
> - [Core finding with verified support when needed]
> - [Second key insight or recommendation]
> - [Third actionable takeaway]
```

Requirements:
- 3-5 concise bullet points sized to the material
- Must be self-contained - understandable without reading the article
- Use statistics only when material to the summary and verified
- State the key finding, recommendation, or answer
- Default label: "Key Takeaways". If a persona is active, use the persona's summary_label
- Backward compatible: accept existing TL;DR boxes during rewrites

#### 5c. Purpose-First Formatting (Critical)
State the point of important sections early, then supply the context and
verified evidence the claim needs. Do not force statistics or fixed lengths.

Pattern:
```markdown
## How Does X Impact Y in 2026?

[Stat from source] ([Source Name](url), year). [Direct answer to the heading
question in 1-2 more sentences, explaining the implication and what this means
for the reader.]
```

**Source record for material public statistics:**

Record enough provenance for a reader or editor to verify the claim. Use the
publication's citation style rather than forcing one sentence pattern.

1. **Relevant date or study period.** Include it where recency or the measured
   period changes the claim's meaning.

2. **Identifiable source.** Name the publisher and document title when needed
   to distinguish the source and place the citation close to the claim.

3. **Retrievable support.** Keep a stable URL. Add a retrieval date for
   changeable or undated sources, and record methodology or limitations when
   they affect interpretation.

**FLOW quality bar (drop or replace):**
Public claims must use verified sources OR stay qualitative. If a statistic
cannot be verified, drop it. If it is contradicted by a more recent source,
replace it with the verified alternative. Do not soften vague language to
keep an unsourceable number.

For evidence-led optimization prompts (CTR audit, quality follow-up, schema,
PAA rewording, ChatGPT visibility), see `/blog flow optimize`.

#### 5d. Information Gain Markers

Use information-gain markers as optional drafting annotations when the article
contains genuinely original data, transparent first-hand evidence, or
distinctive sourced synthesis. The evidence itself helps readers; the marker is
not a search-engine signal and earns no points by its presence.

Tag each with a comment or visible marker:

- `[ORIGINAL DATA]` - Proprietary surveys, experiments, A/B test results, case
  study metrics the author collected first-hand
- `[PERSONAL EXPERIENCE]` - First-hand observations, lessons learned from direct
  involvement, "when we tried X, Y happened" narratives
- `[UNIQUE INSIGHT]` - Analysis others haven't made, contrarian perspectives
  backed by data, novel connections between existing research

Placement:
- Weave into the body text naturally
- Use as inline comments: `<!-- [ORIGINAL DATA] -->` before the relevant paragraph
- Or as visible callouts if the format supports it:
  ```markdown
  > **Our finding:** [original observation backed by specific data]
  ```
- Use only as many as the supported original material warrants.

#### 5e. Evidence-Backed Explanations

For important reusable claims, create a self-contained, evidence-backed
explanation sized to the material.

Guidance:
- Self-contained and understandable in isolation
- Contains a specific claim plus verified support when the claim needs it
- Written in a declarative, quotable style
- Placed within the H2 section body (not as a separate block)

Example:
```markdown
[Verified source title], a [method or sample description] published on [date],
found [specific metric] for [audience or market] ([Source name](https://example.com/full-report),
retrieved YYYY-MM-DD). In practical terms, connect the evidence to one action
the reader should take before making a claim or changing a workflow.
```

Do not pad explanations to a fixed length or add them solely to earn readiness
points.

#### 5f. Internal Linking Zones

Mark internal linking opportunities throughout the article using placeholder
notation. The user (or a follow-up pass) will resolve these to actual URLs.

Zone placement:
- **Introduction** - Link to related pillar content or topic hub
- **Each H2 section** - Link to supporting articles, deeper dives, related tools
- **FAQ section** - Link answers to detailed content that expands on the answer
- **Conclusion** - Link to the next logical piece of content the reader should consume

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
(never "click here" or "read more"). See `${CLAUDE_SKILL_DIR}/../blog/references/internal-linking.md` for
anchor text rules and linking strategy.

#### 5g. Paragraph Rules
- Use paragraph and sentence lengths that fit the audience and material
- Split passages when doing so improves comprehension, not to satisfy a quota
- Start each paragraph with the most important information
- Target Flesch Reading Ease: 60-70

#### 5h. Heading Rules
- One H1 (title only)
- H2s for main sections; use question or declarative forms according to intent
- H3s for subsections only - never skip levels
- Keep heading terminology naturally consistent with the page topic; do not
  enforce an exact-match keyword quota

#### 5i. Image and Chart Embedding

Use the platform-specific image and chart examples in
`${CLAUDE_SKILL_DIR}/../blog-write/references/delivery.md` when adding those assets. Place each
visual where it helps explain the adjacent text, with descriptive alt text or
a useful caption. Preserve MDX syntax when the platform requires it.

#### 5k. Video Embedding
Embed YouTube videos using srcdoc lazy-loading pattern from `${CLAUDE_SKILL_DIR}/../blog/references/video-embeds.md`.
Include aria-label, noscript fallback for AI crawlers. Place after relevant H2, 500+ words apart.

#### 5l. Citation Format
Inline attribution (always):
```markdown
[Publisher]'s [dated study title] reports [verified finding] for [sample]
([Publisher](https://example.com/actual-source), retrieved YYYY-MM-DD).
```

#### 5m. FAQ Section
Add FAQ items only when user questions warrant them. Answers should be complete
and concise; include verified statistics only when relevant.

FAQPage is optional entity markup only. Google FAQ rich results were fully retired for all sites on 2026-05-07, so do not make FAQ schema a core Google rich-result output or citation lever. For the internal schema heuristic, Article or BlogPosting earns 2 points, Person earns 1, and either Organization or BreadcrumbList earns 1. This is not a Google requirement. Emit FAQPage only when the platform already supports it and the questions genuinely help users.

For MDX with an optional FAQSchema component:
```mdx
<FAQSchema faqs={[
  { question: "Question?", answer: "Complete answer with support where needed." },
]} />
```

For standard markdown:
```markdown
## Frequently Asked Questions

### Question text here?

Answer completely, with source attribution where the claim needs it.
```

#### 5n. Internal Linking
- Add internal links only where an existing page helps the reader continue the task
- Link to relevant existing content naturally
- Use descriptive anchor text (not "click here")

### Phase 6: Quality Check

Before delivering, verify:

#### Structure and Content
1. Important claims state their point clearly and include verified support where needed
2. Paragraph and sentence pacing suits the audience; length alone cannot block delivery
3. All statistics have named tier 1-3 sources
4. Every chart present clarifies chart-worthy evidence and uses an appropriate type
5. Every inline image present materially helps the reader and has descriptive alt text
6. Cover image present in frontmatter (coverImage + ogImage)
7. FAQ section present with 3-5 items when warranted by user questions
8. Heading hierarchy is clean (H1 -> H2 -> H3)
9. Meta description accurately and specifically summarizes the visible content

#### New Element Verification
10. Optional summary helps the reader and contains no unsupported claims
11. Any information-gain markers point to supported original material
12. Important reusable claims are self-contained and evidence-backed
13. Internal linking zones marked in introduction, H2 sections, FAQ, and conclusion
14. Project voice preferences reviewed where they improve clarity and fit

#### Optional Editorial Voice Review
15. **Sentence rhythm** - Vary sentence structure only where it improves clarity,
    emphasis, or flow. Do not infer authorship from sentence patterns or enforce
    fixed sentence-length bands.
16. **Project voice review** - Treat configured style-list terms as review cues,
    not banned phrases. Replace wording only when a more precise, subject-appropriate
    expression fits the publication voice.
17. **Contractions** - Use contractions when they fit the selected voice. Their
    presence or absence says nothing about authorship or Google performance.
18. **Rhetorical questions** - Use them only when they help the reader reason
    through a decision. There is no quota.
19. **YouTube videos** - If a video materially helps, use a verified embed with lazy loading, an aria-label, and a noscript fallback (see `${CLAUDE_SKILL_DIR}/../blog/references/video-embeds.md`)

### Phase 6.5: Delivery Contract Enforcement (v1.9.0)
Before Phase 7, resolve
`BLOG_SCRIPT_DIR="${CLAUDE_BLOG_SCRIPTS_DIR:-${CLAUDE_SKILL_DIR}/../../scripts}"`, reject
it unless absolute, and run the 5-gate delivery contract via
`python3 "$BLOG_SCRIPT_DIR/blog_preflight.py"` plus a BLOCKING
`blog-reviewer` agent. Follow `${CLAUDE_SKILL_DIR}/../blog/references/blog-delivery-contract.md`
and the writer-specific checklist in `${CLAUDE_SKILL_DIR}/../blog-write/references/delivery.md`.
Never resolve the preflight helper from the current project. The user is never
the first reviewer; the gates are.
On any block, capture `<folder>/preflight-report.json`, re-dispatch the blog-writer agent with the diagnostic as input, and re-run the gated steps. Maximum 3 iterations. On the 3rd failure, stop and present the failure diagnostic instead of the draft.

### Phase 7: Delivery
Present the completed article only after Phase 6.5 returns all gates passing. Include `<folder>/preview/*.png` screenshots and the compact completion summary described in `${CLAUDE_SKILL_DIR}/../blog-write/references/delivery.md`.
