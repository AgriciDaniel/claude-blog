---
name: blog-rewrite
description: >
  Rewrite and optimize existing blog posts for Google SEO (May 2026 Core
  Update, E-E-A-T) and AI citation visibility as one SEO discipline. For
  AI-citation-only audit (no Google work), use blog-geo instead. Replaces
  fabricated statistics with sourced data, applies answer-first formatting,
  adds images, generates SVG charts, and updates freshness signals. Works
  with any blog format (MDX, markdown, HTML). Use when user says "rewrite
  blog", "optimize blog", "update blog", "improve blog", "fix blog".
user-invokable: true
argument-hint: "<file-path>"
license: MIT
---

# Blog Rewriter: Optimize Existing Posts

Rewrites and optimizes existing blog posts for dual ranking: Google search
and AI citation platforms. Preserves the author's voice while applying the
6 pillars of optimization.

**Key references:**
- `skills/blog/references/quality-scoring.md` - 5-category scoring (Content 30, SEO 25, E-E-A-T 15, Technical 15, AI Citation 15)
- `skills/blog/references/eeat-signals.md` - Experience, expertise, authority, trust markers
- `skills/blog/references/internal-linking.md` - Linking strategy and anchor text rules
- `skills/blog/references/visual-media.md` - Image sourcing and chart styling
- `skills/blog/references/synthesis-contract.md` - 6 LAWs for re-citation hygiene during rewrite (v1.8.0; cross-skill ref lives in the orchestrator's references dir)
- `skills/blog/references/research-quality.md` - cross-source clustering for replacement-statistic research (v1.8.0)

## Cross-reference

For 21 evidence-led optimization prompts (quality follow-up, CTR audit, schema,
PAA rewording, technical audit, ChatGPT visibility) directly applicable to
rewrite work, see `/blog flow optimize`.

## Workflow

### Phase 1: Audit (Read-Only)

1. **Read the blog post** - Detect format (MDX, markdown, HTML)
2. **Run the quality checklist** against `skills/blog/references/quality-scoring.md`:
   - Count fabricated vs sourced statistics
   - Check answer-first formatting (H2 -> stat in first sentence?)
   - Count images and charts (type diversity?)
   - Review paragraph pacing in context; record length only as a descriptive aid
   - Check heading hierarchy (H1 -> H2 -> H3, no skips?)
   - Check schema presence and validity, prioritizing Article/BlogPosting, Person, Organization, and BreadcrumbList; FAQPage is optional entity markup only
   - Check freshness signals (lastUpdated, dateModified)
   - Assess self-promotion level
   - Evaluate citation tier quality
3. **Advisory editorial style scan**:
   - **Sentence-length variation** - Report it descriptively when rhythm needs
     review. It cannot determine authorship and has no pass/fail threshold.
   - **Known AI phrase scan** - Check for these high-frequency AI phrases:
     - "in today's digital landscape", "it's important to note", "dive into"
     - "game-changer", "navigate the landscape", "revolutionize", "seamlessly"
     - "cutting-edge", "harness the power of", "leverage" (as verb)
     - "delve", "crucial", "elevate", "foster", "landscape" (overused)
     - "multifaceted", "robust", "tapestry", "embark"
     - Full list in `agents/blog-writer.md`
   - **Vocabulary sample** - Report Type-Token Ratio (TTR) descriptively and
     interpret it against text length and specialist terminology.
   - Never estimate AI authorship from TTR, sentence-length variation, punctuation,
     or phrase density. These are advisory project-style observations only.
   - **Second-order structural reflex scan** (v1.8.0) - The first-order checks above
     are vocabulary-level. The second-order pass reviews structural repetition
     that can survive simple wording edits. Run against
     `skills/blog/references/ai-slop-detection.md`. Flag at minimum:
     - Repetitive question-cadence H2s that do not suit reader intent
     - Three or more "Here..." paragraph openers
     - Three-clause sentence rhythm above 50% in any 200-word window
     - More than 2 hedge words ("may," "often," "typically," "generally") in any 20-word span
     - Symmetric-list bloat (list-item word-count SD below 5)
     - More than 2 wrap-up rhetorical questions ("What does this mean for...?")
     - More than half of H2 openers starting with a transition word
     - "The key insight is..." or "What's important here is..." as sentence openers
     - Listicle pre-list intro above 250 words
     - Opening-word repetition: top three first-words above 25% share
     - Paragraph-shape SD below 25 (visual monotony)
     Apply editorial judgment; none of these metrics changes the score or blocks delivery.
4. **Video embed check**:
   - Count existing YouTube embeds in the post
   - If 0 embeds, flag: "No video embeds. Consider adding relevant high-quality YouTube embeds when they add useful context."
   - If present, check: lazy loading? aria-labels? noscript fallback? VideoObject schema?
5. **Cannibalization check**:
   - Identify the post's primary keyword from title, H1, and first paragraph
   - Search the blog directory for other posts targeting the same keyword:
     - Grep headings and meta descriptions across all blog posts
     - Flag any posts with significant keyword overlap
   - If cannibalization found, report:
     - Which posts compete for the same keyword
     - Recommend: **merge** (combine into one stronger post) or **differentiate**
       (shift one post to a related but distinct keyword)
6. **Calculate current score** across 5 categories:
   - Score across 5 categories (Content Quality 30, SEO Optimization 25, E-E-A-T Signals 15, Technical Elements 15, AI Citation Readiness 15)
   - Total: 0-100
7. **Present audit summary** with specific findings, advisory style diagnostics, video status, cannibalization status, and score
8. **Enter plan mode** - Present section-by-section optimization plan

Wait for user approval before proceeding.

### Phase 2: Research

1. **Identify the blog's core topic** from existing content
2. **Find replacement statistics** for any fabricated/unsourced data:
   - Search: `[topic] study 2025 2026 data statistics`
   - Target tier 1-3 sources only
3. **Find images** if post has fewer than 3:
   - Prefer original screenshots, product visuals, diagrams, or data graphics when available
   - For stock, use official provider APIs such as Openverse, Unsplash, Pexels, or Pixabay so license, creator, source URL, and download URL are captured
   - Download approved assets locally, store attribution, and reject `javascript:`, `data:`, and `file:` URLs
   - If `blog-image` is available, offer AI generation for missing or insufficient images and record the selected model ID
4. **Plan charts** if post has fewer than 2:
   - Identify data suitable for visualization
   - Select diverse chart types

### Phase 3: Chart Generation (Built-In)

When the post needs more visual elements, invoke the `blog-chart` sub-skill:

1. Select chart type using the diversity rule (no repeated types per post)
2. Pass: chart type, title, data values, source, platform format
3. Embed the returned SVG directly within a `<figure>` wrapper
4. Target 2-4 charts per 2,000-word post

See `skills/blog/references/visual-media.md` for chart type selection and styling rules.

### Phase 4: Content Rewrite

Apply changes in this order:

#### 4a. Preserve What Works
- Keep the author's voice and unique perspective
- Preserve original insights and first-hand experience
- Keep existing quality images and charts
- Maintain internal links

#### 4b. Fix Frontmatter
- Update `lastUpdated` only when the rewrite materially changes facts, methods, or recommendations
- Keep original `date` unchanged
- Fix the meta description so it accurately and specifically summarizes the
  visible content
- Add `coverImage` + `coverImageAlt` + `ogImage` if missing
  - Search Pixabay/Unsplash/Pexels for wide hero image (1200x630)
  - Or generate custom SVG cover via `blog-chart` (text-on-gradient with key stat)
  - Or generate custom AI image via `blog-image` sub-skill when available; record the model ID
- Verify tags/categories are appropriate

#### 4c. Apply Purpose-First Formatting
State the point of important sections early, then add the verified evidence and
context each claim needs. Do not force statistics or word bands.

#### 4d. Replace Fabricated Statistics
- Search for patterns: "X% of...", "X out of Y...", unsourced claims
- Replace with real data from tier 1-3 sources
- Give each material claim enough provenance to verify and interpret it. Include
  publisher or document details, relevant dates, methodology, limitations, and a
  stable URL when the claim requires them; do not force a fixed citation form.

#### 4e. Improve Headings
- Use question or declarative headings according to reader intent; no ratio target
- Ensure keyword appears in 2-3 headings naturally

#### 4f. Fix Paragraph Length
- Split paragraphs only when doing so improves comprehension
- Use paragraph length as an optional planning observation, not a fixed target
- Ensure each paragraph starts with its most important sentence

#### 4g. Add Visual Elements
- Embed new images after H2 headings, spaced evenly
- Embed charts within relevant sections
- If `blog-image` is available: generate custom images for sections lacking good stock matches, prefer the current image model registry, and record the model ID
- Adapt embed format to detected platform (MDX vs markdown vs HTML)

#### 4h. Add Video Embeds
If the post lacks YouTube video embeds:
- Search 2-3 relevant videos using quality criteria from `skills/blog/references/video-embeds.md`
- Embed using platform-appropriate format (srcdoc lazy loading)
- Place: 1 after introduction, 1-2 in mid-article sections
- Include noscript fallback for AI crawlers

#### 4i. Add/Improve FAQ
- If the query set warrants it and no FAQ exists, add one (3-5 questions)
- If FAQ exists, ensure answers are complete and contain verified support where needed
- FAQPage is optional entity markup only. Google FAQ rich results were fully retired for all sites on 2026-05-07, so do not make FAQPage a core Google rich-result gate.

#### 4j. Reduce Self-Promotion
- Max 1 brand mention (author bio context only)
- Remove "At [Company], we..." patterns
- Convert promotional sections to educational content

#### 4k. Evidence-Backed Explanation
For important claims, generate or improve a self-contained explanation with
enough context and verified support to stand on its own. Do not pad every H2.
- Placed naturally within the section body, not as a separate callout

Example:
```markdown
[Verified source title], a [method or sample description] published on [date],
found [specific metric] for [audience or market] ([Source name](https://example.com/full-report),
retrieved YYYY-MM-DD). In practical terms, connect the evidence to one action
the reader should take before making a claim or changing a workflow.
```

Do not pad explanations to a fixed length or add them solely to earn readiness
points.

#### 4l. Project Voice and Repetition Review
Apply these transformations only where they improve the configured voice:
- **Eliminate em dashes** - Replace every U+2014 character with a comma, hyphen,
  colon, or period. Split sentences if needed. This is a project style rule.
- **Replace flagged phrases** - Swap every detected AI phrase (from the scan in
  Phase 1 step 3) with a natural alternative. Examples:
  - "it's important to note" -> "worth noting" or "keep in mind"
  - "in today's digital landscape" -> "right now" or "in [specific year]"
  - "leverage" -> "use", "apply", "take advantage of"
  - "delve" -> "look at", "explore", "dig into"
  - "robust" -> "strong", "solid", "reliable"
  - "crucial" -> "key", "essential", "critical" (or restructure the sentence)
- **Vary sentence length deliberately** - After rewriting, scan each paragraph.
  Inject short punchy sentences (5-10 words) between longer ones (18-25 words).
  Target: no more than 3 consecutive sentences within 5 words of each other's length.
- **Use rhetorical questions sparingly** - Add one only when it clarifies the
  reader's next decision.
- **Use contractions naturally** - Replace formal constructions with contractions
  where they sound natural: "it is" -> "it's", "we have" -> "we've",
  "do not" -> "don't", "is not" -> "isn't".
- **Support first-hand language** - Keep "we tested" or "in our experience" only
  when methodology, observations, or evidence can substantiate the claim.

#### 4m. Summary Box (Key Takeaways)
If the post lacks a summary box, add one immediately after the introduction:
```markdown
> **Key Takeaways**
> - [Core finding with statistic and source]
> - [Second key insight or recommendation]
> - [Third actionable takeaway]
> (Use concise bullets sized to the material. Keep the summary self-contained so the reader gets
> the core value without reading the full article.)
```
Default label is "Key Takeaways", but this is configurable per persona or
brand voice (e.g., "The Bottom Line", "Quick Summary", "What You Need to Know").

If an existing TL;DR box is useful, convert it to concise Key Takeaways and
verify every factual statement is supported. Do not add a statistic merely to
fit the format.

#### 4n. Information Gain Marker Injection
Review the post for original value and tag it:
- `[ORIGINAL DATA]` - Any proprietary data, survey results, experiments, or
  case study metrics the author collected first-hand
- `[PERSONAL EXPERIENCE]` - First-hand observations, lessons learned
- `[UNIQUE INSIGHT]` - Novel analysis, contrarian perspectives backed by data

If the post lacks original value markers:
- Ask the author for first-hand data or experience to include
- At minimum, add analytical insights that connect existing research in new ways
- Target: at least 2-3 markers per post

Use HTML comments (`<!-- [ORIGINAL DATA] -->`) or visible callouts depending
on the post's style.

### Phase 5: Verification

After rewriting, verify all quality gates pass:

#### Core Quality Gates
1. Important claims state their point clearly and include verified support where needed
2. Paragraph and sentence pacing suits the audience; length alone cannot fail review
3. Zero fabricated statistics
4. Heading hierarchy is clean
5. Article-priority schema present and valid; FAQPage only if useful as optional entity markup
6. Images have descriptive alt text
7. Cover image present in frontmatter (coverImage + ogImage)
8. If MDX: build the project to verify no compilation errors

#### New Element Verification
9. Optional summary is useful and contains no unsupported claims
10. Any information-gain markers identify supported original material
11. Important reusable claims are self-contained and evidence-backed
12. Internal linking zones marked or actual links present (5-10 per 2,000 words)
13. Configured project style-list terms reviewed in context

#### Editorial Style Check
14. Sentence-length variation reviewed descriptively, with no authorship verdict
15. Contractions used naturally throughout
16. Rhetorical questions used only where useful
17. No unsupported first-hand claims
18. Score improved across all 5 categories vs Phase 1 audit
19. YouTube video embeds present with lazy loading, aria-labels, and noscript fallback

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

### Editorial Style Diagnostics
- Configured style-list terms reviewed: [N]
- Sentence-length variation: [descriptive observation]
- These observations do not infer authorship and do not affect the score.

### Cannibalization
- [Status: none found / flagged N posts / resolved]

### Changes Made
- [X] statistics replaced with sourced data
- [X] SVG charts added (types: ...)
- [X] images added from Pixabay/Unsplash
- Answer-first formatting applied to [N] H2 sections
- FAQ section updated with [N] questions; FAQPage emitted only as optional entity markup if appropriate
- TL;DR box: [added/updated]
- Information gain markers: [N] ([types])
- Evidence-backed explanations improved: [N]
- Configured project style-list terms reviewed: [N]
- lastUpdated set to [date]
- Self-promotion reduced to [N] mentions

### Visual Elements
- Charts: [count] ([types])
- Images: [count]
- YouTube videos: [count] ([titles])

### Ready for
- `/blog analyze <file>` to verify final score
- Publishing / deploying
```

## Phase 5.5: Delivery Contract Enforcement (v1.9.0)

Before presenting the rewritten draft, run the 5-gate delivery contract per `skills/blog/references/blog-delivery-contract.md`. The contract applies to rewrites the same way it applies to new posts: the user is never the first reviewer.

Steps:

1. **Hero check**: if the existing post already has a hero image referenced and still on disk, keep it. If the rewrite changed the topic substantially OR the hero is missing, regenerate via `python3 scripts/generate_hero.py --topic "<new title>" --tags "<tags>" --out <folder>`.
2. **Re-render**: run `python3 scripts/blog_render.py --md <slug>.md --out-dir <folder>` to refresh the `.html` and `.pdf` from the updated `.md`.
3. **Reviewer dispatch**: dispatch the `blog-reviewer` agent against the rendered `.html`. Threshold: score 90/100 or higher AND zero P0 issues.
4. **Preflight**: run `python3 scripts/blog_preflight.py --draft <folder> --strict`. Exit 0 = ship; exit 1 = block.
5. **Iterate on failure**: maximum 3 iterations. After the 3rd failure, STOP and present the diagnostic from `<folder>/preflight-report.json`.

Rewrites have a higher implicit threshold because the existing draft was presumably already published. Re-presenting something worse than the original is not acceptable. If the rewritten score is lower than the original score, that itself is a P0 condition.

## Update Mode

When invoked as `/blog update <file>`, focus on freshness:
1. Update statistics to latest available data (2025-2026)
2. Add new developments since last update
3. Refresh images if older than 1 year
4. Update `lastUpdated` in frontmatter
5. Preserve the existing structure - minimize rewrites
6. Target: genuine freshness only. Replace stale statistics, add real new developments, and update `lastUpdated`/`dateModified`; do not rewrite to hit a percentage-change threshold.
