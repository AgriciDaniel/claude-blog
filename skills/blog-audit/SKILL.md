---
name: blog-audit
description: >
  Full-site blog health assessment scanning all blog files for quality scores,
  orphan pages, topic cannibalization, stale content, and AI citation readiness.
  Spawns parallel subagents for comprehensive analysis. Produces per-post scores
  and a prioritized action queue. Use when user says "audit blog", "blog audit",
  "site audit", "blog health", "audit all posts", "check all blogs".
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
  - Task
---

# Blog Audit -- Full-Site Health Assessment

Performs a comprehensive blog health assessment across all posts in the project.
Scans for quality scores, orphan pages, topic cannibalization, stale content,
and AI citation readiness. Uses parallel subagents for efficient analysis and
produces a prioritized action queue.

## Audit Process

### Step 1: Discover Blog Files

Scan the project for all blog content files:

- Glob for `*.md`, `*.mdx`, `*.html` in common blog directories
- Common paths to check:
  - `content/`
  - `posts/`
  - `blog/`
  - `src/content/`
  - `_posts/`
  - `pages/blog/`
  - `articles/`
  - `src/pages/blog/`
- Filter out non-blog files: README, CHANGELOG, LICENSE, config files,
  SKILL.md, package.json, node_modules
- Report: "Found N blog files in [directories]"

If no blog files are found in standard locations, search the entire project
root for markdown files with blog-like frontmatter (title, date, description).

### Step 2: Parallel Analysis

Spawn subagents via the Task tool for parallel processing across all
discovered blog files:

#### Content Quality Agent
- Score each post on the 30-point content quality scale
- Check paragraph length (target 40-80 words, hard limit 150)
- Check sentence length (target 15-20 words)
- Evaluate heading structure and question-format headings
- Assess readability (Flesch Reading Ease 60-70 target)

#### SEO Optimization Agent
- Check on-page SEO elements per post:
  - Title tag length (50-60 chars)
  - Meta description (150-160 chars, includes statistic)
  - H1 presence and uniqueness
  - Image alt text coverage
  - Internal and external link counts
  - URL slug quality

#### Schema Validation Agent
- Detect structured data across all posts
- Validate BlogPosting schema completeness
- Check FAQ schema presence and format
- Verify dateModified matches lastUpdated frontmatter
- Flag missing or malformed schema

#### Link Health Agent
- Map internal links across all posts
- Build a directed link graph
- Detect orphan pages (zero inbound internal links)
- Detect dead-end pages (zero outbound internal links)
- Check for broken internal link targets
- Recommend bidirectional link opportunities

#### Freshness Check Agent
- Read lastUpdated or dateModified from each post's frontmatter
- Calculate days since last update
- Flag posts not updated in 90+ days
- Categorize by refresh priority

#### AI Readiness Agent
- Score each post for AI citation readiness
- Check passage-level citability (120-180 word sections)
- Evaluate Q&A formatting and entity clarity
- Check for TL;DR boxes and citation capsules
- Assess AI crawler accessibility

### Step 3: Topic Cannibalization Detection

Analyze across all posts for keyword competition:

1. Extract primary keyword/topic from each post:
   - Title text
   - H1 heading
   - Meta description
   - First paragraph
2. Normalize keywords (lowercase, remove stop words)
3. Detect multiple posts targeting the same primary keyword
4. Flag competing posts with one of these recommendations:
   - **Merge**: Combine two weak posts into one strong post
   - **Redirect**: 301 redirect the weaker post to the stronger one
   - **Differentiate**: Adjust focus so posts target distinct intents

### Step 4: Orphan Page Detection

Build and analyze the internal link graph:

1. For each blog post, extract all internal links (relative and absolute)
2. Build an adjacency map: `{ page -> [pages it links to] }`
3. Build a reverse map: `{ page -> [pages linking to it] }`
4. Identify orphan pages: posts with zero inbound internal links
5. Identify dead-end pages: posts with zero outbound internal links
6. For each orphan, recommend 2-3 existing posts that should link to it
   based on topic relevance

### Step 5: Stale Content Detection

Audit content freshness across all posts:

1. Read frontmatter fields: `lastUpdated`, `dateModified`, `date`, `updated`
2. Calculate days since last update for each post
3. Categorize by refresh priority:
   - **High** (>180 days): Likely outdated, statistics may be stale
   - **Medium** (90-180 days): Review for accuracy, update statistics
   - **Low** (<90 days): Recently updated, no immediate action
4. Estimate refresh effort per post:
   - Light refresh: Update statistics, check links (1-2 hours)
   - Moderate refresh: Rewrite sections, add new data (3-4 hours)
   - Heavy refresh: Full rewrite recommended (5+ hours)

### Step 6: Generate Site-Wide Report

Aggregate all results into a comprehensive report:

#### Summary Dashboard
```
## Blog Audit Report

**Audit Date:** [date]
**Total Posts:** N
**Average Score:** XX/100

### Health Overview
| Metric | Count |
|--------|-------|
| Posts Scoring 90+ (Excellent) | N |
| Posts Scoring 70-89 (Good) | N |
| Posts Scoring 50-69 (Needs Work) | N |
| Posts Scoring <50 (Poor) | N |
| Orphan Pages | N |
| Dead-End Pages | N |
| Cannibalization Issues | N |
| Stale Content (90+ days) | N |
```

#### Per-Post Table
```
### Per-Post Scores
| Post | Score | Content | SEO | E-E-A-T | Technical | AI Citation | Issues |
|------|-------|---------|-----|---------|-----------|-------------|--------|
| [filename] | XX/100 | X/25 | X/20 | X/20 | X/15 | X/20 | [count] |
```

#### Prioritized Action Queue
```
### Prioritized Action Queue (Lowest Score First)
| Priority | Post | Score | Top Issue | Recommended Action |
|----------|------|-------|-----------|--------------------|
| 1 | [file] | XX | [issue] | [action] |
| 2 | [file] | XX | [issue] | [action] |
```

#### Cannibalization Report
```
### Topic Cannibalization
| Keyword | Competing Posts | Recommendation |
|---------|----------------|----------------|
| [keyword] | post-a.md, post-b.md | Merge / Redirect / Differentiate |
```

#### Orphan Pages
```
### Orphan Pages (No Inbound Links)
| Page | Inbound Links | Recommended Link Sources |
|------|---------------|--------------------------|
| [file] | 0 | post-a.md, post-b.md, post-c.md |
```

#### Stale Content
```
### Stale Content
| Post | Last Updated | Days Stale | Priority | Refresh Effort |
|------|-------------|------------|----------|----------------|
| [file] | [date] | [N] | High/Med/Low | Light/Moderate/Heavy |
```

### Step 7: Save Report

Save the complete report to `blog-audit-report.md` in the project root.

After saving, inform the user:
- Report location: `[project-root]/blog-audit-report.md`
- Summary of findings (total posts, average score, critical issues count)
- Suggest running `/blog analyze <file>` on the lowest-scoring post first
- Suggest running `/blog geo <file>` for AI citation optimization on key posts
