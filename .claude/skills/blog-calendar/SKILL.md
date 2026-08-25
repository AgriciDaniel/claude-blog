---
name: blog-calendar
description: >
  Generate editorial calendars for blogs with topic clusters, publishing
  schedules, material-change reviews, update plans, seasonal
  opportunities, content mix formula, template integration, and distribution
  scheduling. Plans monthly or quarterly calendars around reader needs,
  evidence changes, and sustainable publishing capacity.
  Use when user says "editorial calendar", "content calendar", "blog calendar",
  "publishing schedule", "blog plan", "content plan", "what should I write".
user-invokable: true
argument-hint: "[<niche>]"
license: MIT
---

# Blog Calendar: Editorial Planning

Generates editorial calendars with topic clusters, publishing cadence,
material-change reviews, content-decay investigation, template recommendations,
distribution planning, and seasonal hooks. It does not treat publication or
update frequency as a ranking or citation signal.

## Cross-reference

This skill operates at the FLOW Find stage. Before selecting topics, run
`/blog flow find` for keyword discovery, content prioritization, and audience
avatar prompts that should inform cluster selection and topic sequencing.

## Workflow

### Step 1: Understand the Blog

Gather context:
1. **Niche/industry**: What is the blog about?
2. **Existing content**: Scan for existing blog posts (Glob for *.md, *.mdx, *.html)
3. **Publishing cadence**: How often can they publish? (default: 2x/week)
4. **Timeframe**: Monthly or quarterly calendar?
5. **Business goals**: What should the blog drive? (traffic, leads, authority)

### Step 2: Topic Cluster Design

Design 3-5 topic clusters (pillar + supporting content):

```
Cluster: [Pillar Topic]
├── Pillar Page: [Comprehensive guide - 3,000+ words]
├── Supporting: [Subtopic 1 - 2,000 words]
├── Supporting: [Subtopic 2 - 2,000 words]
├── Supporting: [Subtopic 3 - 1,500 words]
├── Comparison: [X vs Y - 1,500 words]
└── FAQ: [Common questions - 1,500 words]
```

Each cluster should:
- Target a primary keyword theme
- Cover the topic comprehensively for topical authority
- Include varied content types (guides, comparisons, how-tos, listicles)
- Support internal linking between cluster pages

### Step 2.5: Content Decay Detection

Scan existing posts for material change signals. Dates are inventory metadata,
not proof that content is stale or fresh.

| Signal | Review Question | Priority Effect |
|--------|-----------------|-----------------|
| Query or fact volatility | Have prices, laws, products, events, or guidance changed? | Raise when the changed fact is material |
| Performance trend | Is there a sustained decline after controlling for seasonality and Search surface? | Investigate before rewriting |
| Source availability | Are important sources outdated, contradicted, or unavailable? | Raise when claims lose support |
| Reader intent | Does the page still solve the current task? | Raise when intent materially shifted |

Do not prioritize an update solely because a frontmatter date is old or a
vendor sample observed recently updated citations.

Output a decay report:

```
## Content Decay Report
| Post | Material Change Evidence | Performance Context | Priority | Action |
|------|--------------------------|---------------------|----------|--------|
| [slug] | [changed fact/source/intent] | [surface and comparison] | Critical | Correct material error |
| [slug] | [documented change] | [sustained trend] | High | Schedule substantive review |
| [slug] | [no confirmed change] | [stable/unclear] | Low | Monitor |
```

Priority levels:
- **Critical**: Materially wrong or harmful information needs correction
- **High**: Confirmed fact, source, product, or intent change affects usefulness
- **Medium**: Sustained performance change warrants investigation
- **Low**: No material change; monitor without editing the date

### Step 3: Freshness Update Schedule

Plan review triggers around the topic:
- **Fast-changing topics**: Review when the governing facts or official sources change
- **Seasonal topics**: Review before the relevant season using current evidence
- **Product or pricing content**: Review after documented product changes
- **Evergreen topics**: Review when evidence, intent, or performance indicates a need

Change `lastUpdated` only after substantive content changes.

### Step 4: Seasonal & Trending Hooks

Research seasonal opportunities:
1. **Industry events**: Conferences, product launches, algorithm updates
2. **Seasonal trends**: Use Google Trends UI, API, or exported data when available; if relying on WebSearch only, mark trend timing as unverified
3. **Annual reports**: When do major studies release new data?
4. **Algorithm updates**: Validate the current Google update timeline against the Google Search Status Dashboard before scheduling update content. Do not rely on a static list.

#### Seasonal Trends Integration

- Map seasonal peaks to content production schedule
- Plan content 4-6 weeks before seasonal peaks for indexing lead time
- Create "evergreen with seasonal hook" content (e.g., "X Guide [Year]" updated annually)
- Track industry report release cycles:
  - Ahrefs Annual State of SEO (typically Q1)
  - Google Year in Search (December)
  - HubSpot State of Marketing (Q1)
  - Gartner Hype Cycle (August)
  - Major conference dates in the niche
- Use WebSearch to validate timing of trends before scheduling

### Step 5: Generate the Calendar

#### Content Mix Formula

Start from this planning heuristic, then adjust for decay risk, authority gaps,
team capacity, and available source material:
**60% new content / 30% freshness updates / 10% repurposed content**

| Cadence | Monthly Posts | New | Refreshes | Repurposed |
|---------|-------------|-----|-----------|------------|
| 2 posts/week | 8 | 5 | 2 | 1 |
| 3 posts/week | 12 | 7 | 4 | 1 |
| 4 posts/week | 16 | 10 | 5 | 1 |
| 1 post/week | 4 | 2-3 | 1 | 0-1 |

Within new posts, aim for content type diversity:
- **Guides/How-tos**: 30-40% of new content
- **Comparisons/Alternatives**: 15-20%
- **Listicles/Roundups**: 15-20%
- **Case studies/Data research**: 10-15%
- **Thought leadership/News analysis**: 10-15%

#### Template Integration

For each new post entry, recommend a content template from these 12 available:
`how-to-guide`, `listicle`, `case-study`, `comparison`, `pillar-page`,
`product-review`, `thought-leadership`, `roundup`, `tutorial`,
`news-analysis`, `data-research`, `faq-knowledge`

Reference: `skills/blog/references/content-templates.md` for full template details.

#### Monthly Calendar Format

```
# Editorial Calendar: [Month Year]

## Publishing Cadence: [N] posts/week
## Content Mix: [N] new / [N] refreshes / [N] repurposed

### Week 1: [Date Range]
| Day | Type | Title | Template | Cluster | Target Keyword | Status |
|-----|------|-------|----------|---------|---------------|--------|
| Mon | New | [Title] | how-to-guide | [Cluster] | [keyword] | Draft |
| Thu | Update | [Existing post] | - | [Cluster] | [keyword] | Refresh |

### Week 2: [Date Range]
| Day | Type | Title | Template | Cluster | Target Keyword | Status |
|-----|------|-------|----------|---------|---------------|--------|
| Mon | New | [Title] | comparison | [Cluster] | [keyword] | Brief |
| Thu | New | [Title] | listicle | [Cluster] | [keyword] | Brief |

### Week 3: [Date Range]
[...]

### Week 4: [Date Range]
[...]

## Content Mix This Month
- New posts: [N]
- Freshness updates: [N]
- Repurposed content: [N]
- Content types: [guides, comparisons, how-tos, listicles, ...]

## Freshness Update Queue
| Post | Last Updated | Priority | Scheduled |
|------|-------------|----------|-----------|
| [slug] | [date] | High | Week 2 |
| [slug] | [date] | Medium | Week 4 |

## Seasonal Hooks
- [Event/trend and how to leverage it]
```

#### Quarterly Calendar Format

```
# Quarterly Editorial Plan: Q[N] [Year]

## Content Strategy
- Topic clusters: [N] active
- New posts planned: [N]
- Freshness updates planned: [N]
- Repurposed content: [N]
- Total content actions: [N]

## Month 1: [Month]
### Focus: [Primary cluster or theme]
| Week | Type | Title | Template | Cluster | Keyword |
|------|------|-------|----------|---------|---------|
| W1 | New | ... | how-to-guide | ... | ... |
| W1 | Update | ... | - | ... | ... |
| W2 | New | ... | comparison | ... | ... |
[...]

## Month 2: [Month]
### Focus: [Primary cluster or theme]
[...]

## Month 3: [Month]
### Focus: [Primary cluster or theme]
[...]

## Quarterly Goals
- [ ] Publish [N] new posts
- [ ] Update [N] existing posts for freshness
- [ ] Complete [Cluster] pillar + [N] supporting pages
- [ ] Achieve [metric target]
```

### Step 5.5: Topic Cluster Progress Tracking

Track the build-out state of each topic cluster. Prioritize completing
partially-built clusters over starting new ones.

```
## Topic Cluster Progress
| Cluster | Pillar | Spokes Published | Spokes Planned | Coverage |
|---------|--------|-----------------|----------------|----------|
| [Topic] | Published | 5/10 | 5 this quarter | 50% |
| [Topic] | Draft | 2/8 | 3 this quarter | 25% |
| [Topic] | Not started | 0/6 | 1 this quarter | 0% |
```

Rules for cluster prioritization:
- Clusters at 50%+ coverage: highest priority to complete
- Clusters with published pillar but few spokes: second priority
- New clusters: only start when existing clusters reach 75%+ coverage
- Never have more than 3 clusters in active build-out simultaneously

### Step 5.6: Distribution Scheduling

For each new post, plan distribution across channels. Include distribution
timing in the calendar output.

```
## Distribution Schedule
| Post | Publish Date | LinkedIn | Reddit | Email | YouTube |
|------|-------------|----------|--------|-------|---------|
| [Title] | [Date] | Same day | +2-3 days | Next batch | If pillar |
```

Channel timing rules:
- **LinkedIn**: Same day as publish (share key insight + link)
- **Reddit**: 2-3 days after publish (share genuine insight, not a link drop)
- **Email newsletter**: Batch weekly (include 2-3 posts per newsletter)
- **YouTube**: Plan companion video for pillar posts only (resource-intensive)
- **Twitter/X**: Same day as publish (thread key takeaways)

Reference: `skills/blog/references/distribution-playbook.md` for detailed channel tactics.

### Step 5.7: Freshness Automation

Set up a system for ongoing freshness maintenance:

```
## Material-Change Review Queue
| Post | Review Trigger | Evidence | Priority | Owner |
|------|----------------|----------|----------|-------|
| [slug] | [official source/product/fact changed] | [link or observation] | High | [name] |
| [slug] | [sustained performance or intent shift] | [surface-specific comparison] | Medium | [name] |
```

Automation recommendations:
- Monitor official sources or product changes for fast-changing topics
- Sort the queue by material risk and reader impact
- Use traffic only as context, not proof that an update is needed
- Update `lastUpdated` only after substantive content changes
- Track what changed and compare relevant Search surfaces separately
- Suggest `/blog rewrite` only when a substantive review finds work to do

### Step 6: Save & Next Steps

Save to `calendars/[yyyy-mm]-editorial-calendar.md` unless the user specifies
another path. Create `calendars/` if it does not exist.

Suggested workflow:
1. Run `/blog strategy` when positioning or pillars are unclear
2. Run `/blog cluster plan <seed-keyword>` for cluster-heavy calendars
3. Use `/blog brief <first-topic>` or `/blog outline <first-topic>` for the first scheduled item
4. Use `/blog write` to generate articles from approved briefs or outlines
5. Use `/blog rewrite` for freshness updates on existing content
6. Re-run `/blog calendar` next month/quarter for the next plan
7. Review the Content Decay Report weekly and address Critical items first
8. Track Topic Cluster Progress monthly to ensure clusters reach completion
