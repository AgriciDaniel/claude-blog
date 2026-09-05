# Content Templates

Reference guide for the 12 content type templates included with `claude-blog`.
Templates provide structural blueprints for different article types, ensuring
consistent quality and optimization across all content.

---

## Template Overview

| Template | Content Type | Word Count Target | Best For |
|----------|-------------|-------------------|----------|
| how-to-guide.md | How-To Guide | 2,000-2,500 | Step-by-step tutorials, process guides |
| listicle.md | Listicle | 1,500-2,000 | Ranked lists, curated collections |
| case-study.md | Case Study | 2,000-3,000 | Client results, project retrospectives |
| comparison.md | Comparison | 1,500-2,000 | X vs Y, tool evaluations |
| pillar-page.md | Pillar Page | 3,000-4,000 | Comprehensive topic guides |
| product-review.md | Product Review | 1,500-2,500 | Tool reviews, software evaluations |
| thought-leadership.md | Thought Leadership | 2,000-3,000 | Industry analysis, opinion pieces |
| roundup.md | Expert Roundup | 2,000-2,500 | Multi-source collections, trend reports |
| tutorial.md | Tutorial | 2,500-3,500 | Code walkthroughs, technical demos |
| news-analysis.md | News Analysis | 800-1,500 | Industry updates, algorithm changes |
| data-research.md | Data/Research | 2,500-3,500 | Original research, survey results |
| faq-knowledge.md | FAQ / Knowledge Base | 1,500-2,000 | Reference content, Q&A collections |

---

## How Templates Work

Templates are structural blueprints, not fill-in-the-blank forms. Each template
defines:

1. **Section structure**: The H2/H3 skeleton for the content type
2. **Answer-first prompts**: Guidance for opening each section with data
3. **Coverage prompts**: Intent-dependent completeness without padding
4. **Info gain markers**: Where original data or unique perspective is needed
5. **Visual element placement**: Where charts and images should appear
6. **Optional Q&A zone**: Where genuine unanswered reader questions fit
7. **Linking zones**: Where internal and external links are most natural

---

## Template Structure Anatomy

Every template follows a consistent internal structure:

```
# [Template Name]

## Metadata
- Content type: [type]
- Word count: [range]
- H2 sections: [count]
- Charts: [count]
- Images: [count]
- Optional Q&A items: [count by reader need]

## Section Structure

### Frontmatter
[Required fields for this content type]

### Introduction (100-150 words)
- Hook: [Type of hook that works best]
- Problem/opportunity: [Framing guidance]
- Promise: [What reader learns]

### H2: [Section Pattern] (word count)
ANSWER-FIRST: [Guidance for the opening stat paragraph]
CONTENT: [What to cover in the body]
INFO-GAIN: [Where unique perspective is needed]
VISUAL: [Chart type or image suggestion]

[... additional H2 sections ...]

### Optional Q&A Zone (count by reader need)
[Visible Q&A guidance specific to this content type; omit when it would repeat
the article. Q&A presence earns no score.]

### Conclusion (100-150 words)
[Closing pattern for this content type]

## Optimization Notes
[Content-type-specific SEO and GEO tips]
```

### Section Markers

| Marker | Purpose |
|--------|---------|
| `ANSWER-FIRST:` | Guidance to state the section point early and support material claims; no fixed length or statistic quota |
| `CONTENT:` | What topics and subtopics to cover in the section body |
| `INFO-GAIN:` | Where original data, first-hand experience, or unique perspective is needed |
| `VISUAL:` | Recommended chart type or image placement |
| `FAQ-ZONE:` | Where an optional visible Q&A section may appear when reader need warrants it |
| `LINK-ZONE:` | Natural places for internal or external links |

---

## How /blog write Selects Templates

When `/blog write` is invoked, the orchestrator selects a template based on:

### 1. Explicit User Request

If the user specifies a content type, that template is used directly:

```
/blog write "10 Best CI/CD Tools for 2026"      --> listicle.md
/blog write "How to Set Up Kubernetes Monitoring" --> how-to-guide.md
/blog write case study: Acme Corp migration       --> case-study.md
```

### 2. Topic Analysis

If no type is specified, the orchestrator analyzes the topic:

| Topic Signal | Template Selected |
|-------------|-------------------|
| "How to...", "Guide to..." | how-to-guide.md |
| Numbers in title ("10 Best...", "7 Ways...") | listicle.md |
| "X vs Y", "compared", "alternative" | comparison.md |
| "Review", "tested", "hands-on" | product-review.md |
| Company/project name + "results" | case-study.md |
| Broad topic, "complete guide", "everything" | pillar-page.md |
| "Tutorial", "walkthrough", "step by step" | tutorial.md |
| News event, update, announcement | news-analysis.md |
| Survey, study, data, research | data-research.md |
| "FAQ", "questions about" | faq-knowledge.md |
| Industry trend, prediction, opinion | thought-leadership.md |
| Expert quotes, collection, roundup | roundup.md |

### 3. Default

If the topic is ambiguous, the orchestrator defaults to `how-to-guide.md` as the
most versatile template and confirms with the user.

---

## Template Details

### how-to-guide.md

Best for step-by-step guides where the reader wants to accomplish something.

```
Structure:
  Introduction (hook with difficulty/time stat)
  H2: Why This Matters (context + data)
  H2: Prerequisites / What You Need
  H2: Step 1 - [Action] (answer-first with success rate)
  H2: Step 2 - [Action]
  H2: Step 3 - [Action]
  H2: Common Mistakes to Avoid
  H2: Optional Q&A (count by reader need)
  Conclusion (key takeaways + next step)

Visuals: Process flow chart, before/after comparison chart
Images: Screenshots or relevant stock for each major step
```

### listicle.md

Best for ranked lists, tool collections, and curated recommendations.

```
Structure:
  Introduction (hook with total count stat)
  H2: [Item 1] - [Key Differentiator]
  H2: [Item 2] - [Key Differentiator]
  ... (5-15 items depending on depth)
  H2: How We Evaluated [Category]
  H2: Optional Q&A (count by reader need)
  Conclusion (top pick + comparison table)

Visuals: Comparison bar chart, market share donut chart
Images: Logo/screenshot per item, or grouped comparison image
```

### case-study.md

Best for showcasing real results with specific metrics.

```
Structure:
  Introduction (headline result stat)
  H2: The Challenge
  H2: The Approach / Solution
  H2: Implementation Details
  H2: Results (metrics + timeline)
  H2: Key Takeaways
  H2: Optional Q&A (count by reader need)
  Conclusion (CTA to learn more)

Visuals: Before/after bar chart, timeline or results line chart
Images: Screenshots, dashboards, team/process photos
Info-Gain: Real metrics from the actual project (critical)
```

### comparison.md

Best for X vs Y evaluations and tool comparisons.

```
Structure:
  Introduction (market context stat)
  H2: Quick Comparison Table
  H2: [Product A] Overview
  H2: [Product B] Overview
  H2: Feature-by-Feature Comparison
  H2: Pricing Comparison
  H2: Which Should You Choose?
  H2: Optional Q&A (count by reader need)
  Conclusion (recommendation matrix)

Visuals: Feature comparison radar chart, pricing bar chart
Images: Product screenshots, UI comparisons
```

### pillar-page.md

Best for comprehensive guides that serve as hub pages for topic clusters.

```
Structure:
  Introduction (scope + authority stat)
  H2: What Is [Topic]? (definition + context)
  H2: Why [Topic] Matters in 2026
  H2: [Core Subtopic 1] (detailed coverage)
  H2: [Core Subtopic 2]
  H2: [Core Subtopic 3]
  H2: [Core Subtopic 4]
  H2: [Advanced Topic]
  H2: Tools and Resources
  H2: Optional Q&A (count by reader need)
  Conclusion (learning path + next steps)

Visuals: 3-4 charts (diverse types), topic overview diagram
Images: 5+ images distributed throughout
Linking: Heavy internal linking to supporting cluster pages
```

### product-review.md

Best for hands-on tool reviews with real testing results.

```
Structure:
  Introduction (verdict stat, e.g., performance score)
  H2: Quick Verdict
  H2: What Is [Product]?
  H2: Setup and First Impressions
  H2: Key Features Tested
  H2: Performance Results
  H2: Pricing and Value
  H2: Pros and Cons
  H2: Who Is This For?
  H2: Optional Q&A (count by reader need)
  Conclusion (final rating + recommendation)

Visuals: Performance benchmark chart, pricing comparison
Images: Screenshots from actual testing (critical for E-E-A-T)
Info-Gain: First-hand testing data (must demonstrate Experience)
```

### thought-leadership.md

Best for industry analysis and forward-looking opinion pieces.

```
Structure:
  Introduction (trend stat that sets the stage)
  H2: The Current Landscape
  H2: What's Changing (analysis + data)
  H2: Why This Matters
  H2: Evidence and Interpretation (supported first-hand perspective when
      supplied, otherwise differentiated sourced analysis)
  H2: What to Do About It (actionable advice)
  H2: Looking Ahead (predictions)
  H2: Optional Q&A (count by reader need)
  Conclusion (key thesis + call to action)

Visuals: Trend line chart, market shift chart
Info-Gain: Supported personal perspective when available, or differentiated
sourced synthesis and clearly framed analysis
```

### roundup.md

Best for collecting insights from multiple sources or experts.

```
Structure:
  Introduction (theme + number of sources stat)
  H2: Key Finding 1 (synthesis from multiple sources)
  H2: Key Finding 2
  H2: Key Finding 3
  H2: Expert Perspectives
  H2: What This Means for [Audience]
  H2: Optional Q&A (count by reader need)
  Conclusion (synthesis + action items)

Visuals: Multi-source comparison chart, trend aggregation
```

### tutorial.md

Best for technical walkthroughs with code examples.

```
Structure:
  Introduction (what you'll build + tech stack)
  H2: Prerequisites and Setup
  H2: Step 1 - [Foundation]
  H2: Step 2 - [Core Feature]
  H2: Step 3 - [Integration]
  H2: Step 4 - [Testing/Deployment]
  H2: Troubleshooting Common Issues
  H2: Optional Q&A (count by reader need)
  Conclusion (complete code repo link + extensions)

Visuals: Architecture diagram (SVG), performance chart
Images: Terminal screenshots, UI results
Special: Code blocks with syntax highlighting throughout
```

### news-analysis.md

Best for timely commentary on industry events and updates.

```
Structure:
  Introduction (the news + impact stat)
  H2: What Happened
  H2: Why It Matters
  H2: Who's Affected
  H2: What to Do Now (immediate actions)
  H2: Optional Q&A (count by reader need)
  Conclusion (outlook)

Visuals: 1-2 charts (impact visualization)
Note: Shorter format (800-1,500 words), speed matters
```

### data-research.md

Best for original research, surveys, and data analysis.

```
Structure:
  Introduction (headline finding)
  H2: Methodology
  H2: Key Finding 1 (data + analysis)
  H2: Key Finding 2
  H2: Key Finding 3
  H2: Implications
  H2: Limitations
  H2: Optional Q&A (count by reader need)
  Conclusion (summary of findings + data access)

Visuals: 3-4 charts (data visualizations are central)
Info-Gain: Original data is the entire value proposition
```

### faq-knowledge.md

Best for comprehensive Q&A reference content.

```
Structure:
  Introduction (topic scope + common questions stat)
  H2: [Category 1] Questions
    H3: Question 1? (concise, complete answer with support where needed)
    H3: Question 2?
  H2: [Category 2] Questions
    H3: Question 3?
    H3: Question 4?
  H2: [Category 3] Questions
  Conclusion (additional resources)

Visuals: 1-2 summary charts
Special: Use statistics only when relevant, verified, and useful
Schema: FAQPage is optional visible-content markup with no readiness-score benefit
```

---

## How to Customize Templates

### Modifying an Existing Template

1. Navigate to `~/.claude/skills/blog/templates/`
2. Open the template file you want to modify
3. Adjust section structure, word counts, or guidance
4. Changes take effect immediately (no restart needed)

### Creating a New Template

1. Copy an existing template as a starting point:
   ```bash
   cp ~/.claude/skills/blog/templates/how-to-guide.md \
      ~/.claude/skills/blog/templates/my-custom-type.md
   ```
2. Define the section structure for your content type
3. Add `ANSWER-FIRST:`, `VISUAL:`, and `INFO-GAIN:` markers
4. Set appropriate word count targets
5. Add a topic signal entry in the template selection logic

### Template Best Practices

- Keep sections focused on one topic each
- Place `VISUAL:` markers where data naturally supports a chart
- Use `INFO-GAIN:` markers liberally: these are the sections that
  differentiate your content from AI-generated consensus
- Set realistic word counts that match the content type's natural depth
- Include an FAQ zone only when genuine reader questions warrant it; keep a conclusion when the content type benefits from one

---

## Template and Scoring Integration

Templates guide content creation; the scoring system validates the result.
The mapping between template features and scoring categories:

| Template Feature | Scoring Category | Points At Stake |
|-----------------|------------------|-----------------|
| Section structure | Schema & Structure | 10 |
| Purpose-first markers | Purpose Fit and Reader Utility | 20 |
| Visual placement | Visual Elements | 15 |
| Optional FAQ zone | Reader utility only; no Google/AI score effect | 0 |
| Info-gain markers | Content Quality | 25 |
| Citation guidance | Statistics & Citations | 20 |

A well-followed template naturally produces content scoring 75+ without
additional optimization passes.
