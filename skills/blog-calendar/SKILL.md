---
name: blog-calendar
description: >
  Generate editorial calendars for blogs with topic clusters, publishing
  schedules, content decay detection, freshness update plans, seasonal
  opportunities, content mix formula, template integration, and distribution
  scheduling. Plans monthly or quarterly calendars optimized for SEO topic
  authority and AI citation freshness requirements (30-day update cycles).
  Use when user says "editorial calendar", "content calendar", "blog calendar",
  "publishing schedule", "blog plan", "content plan", "what should I write".
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
  - WebFetch
  - WebSearch
---

# Blog Calendar -- Editorial Planning

Generates editorial calendars with topic clusters, publishing cadence,
freshness update schedules, content decay detection, template recommendations,
distribution planning, and seasonal hooks. Optimized for building topical
authority (Google) and maintaining citation freshness (AI platforms).

## Workflow

### Step 1: Understand the Blog

Gather context:
1. **Niche/industry** -- What is the blog about?
2. **Existing content** -- Scan for existing blog posts (Glob for *.md, *.mdx, *.html)
3. **Publishing cadence** -- How often can they publish? (default: 2x/week)
4. **Timeframe** -- Monthly or quarterly calendar?
5. **Business goals** -- What should the blog drive? (traffic, leads, authority)

### Step 2: Topic Cluster Design

Design 3-5 topic clusters (pillar + supporting content):

```
Cluster: [Pillar Topic]
├── Pillar Page: [Comprehensive guide — 3,000+ words]
├── Supporting: [Subtopic 1 — 2,000 words]
├── Supporting: [Subtopic 2 — 2,000 words]
├── Supporting: [Subtopic 3 — 1,500 words]
├── Comparison: [X vs Y — 1,500 words]
└── FAQ: [Common questions — 1,500 words]
```

Each cluster should:
- Target a primary keyword theme
- Cover the topic comprehensively for topical authority
- Include varied content types (guides, comparisons, how-tos, listicles)
- Support internal linking between cluster pages

### Step 2.5: Content Decay Detection

Scan existing blog posts for `lastUpdated` or `date` fields in frontmatter.
Classify each post by staleness using these thresholds:

| Traffic Level | Stale Threshold | At-Risk Threshold |
|---------------|----------------|-------------------|
| High-traffic posts | >30 days since update | >90 days |
| Medium-traffic posts | >90 days since update | >180 days |
| Low-traffic posts | >180 days since update | >365 days |

Reference: 76% of top AI citations are from content updated within 30 days.

Output a decay report:

```
## Content Decay Report
| Post | Last Updated | Days Stale | Priority | Action |
|------|-------------|-----------|----------|--------|
| [slug] | [date] | [N] | Critical | Refresh immediately |
| [slug] | [date] | [N] | High | Schedule this month |
| [slug] | [date] | [N] | Medium | Schedule this quarter |
```

Priority levels:
- **Critical**: High-traffic post stale >30 days -- refresh immediately
- **High**: Any post stale beyond its threshold -- schedule this month
- **Medium**: Posts approaching their threshold -- schedule this quarter
- **Low**: Posts within threshold -- no action needed

### Step 3: Freshness Update Schedule

AI platforms heavily favor fresh content (76% of top citations updated within 30 days).

Plan update cycles:
- **High-priority posts** (traffic drivers): Update every 30 days
- **Medium-priority posts**: Update every 90 days
- **Low-priority posts**: Update annually
- **Evergreen posts**: Update when data changes

### Step 4: Seasonal & Trending Hooks

Research seasonal opportunities:
1. **Industry events** -- Conferences, product launches, algorithm updates
2. **Seasonal trends** -- Use WebSearch to check Google Trends for the niche
3. **Annual reports** -- When do major studies release new data?
4. **Algorithm updates** -- Google core updates (typically 3-4 per year)

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

Apply the recommended content mix ratio:
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

Reference: `references/content-templates.md` for full template details.

#### Monthly Calendar Format

```
# Editorial Calendar: [Month Year]

## Publishing Cadence: [N] posts/week
## Content Mix: [N] new / [N] refreshes / [N] repurposed

### Week 1: [Date Range]
| Day | Type | Title | Template | Cluster | Target Keyword | Status |
|-----|------|-------|----------|---------|---------------|--------|
| Mon | New | [Title] | how-to-guide | [Cluster] | [keyword] | Draft |
| Thu | Update | [Existing post] | -- | [Cluster] | [keyword] | Refresh |

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
| W1 | Update | ... | -- | ... | ... |
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

Reference: `references/distribution-playbook.md` for detailed channel tactics.

### Step 5.7: Freshness Automation

Set up a system for ongoing freshness maintenance:

```
## Freshness Schedule: Next 30 Days
| Post | Last Updated | Next Refresh Date | Priority | Owner |
|------|-------------|-------------------|----------|-------|
| [slug] | [date] | [date + 30] | High | [name] |
| [slug] | [date] | [date + 90] | Medium | [name] |
```

Automation recommendations:
- Set calendar reminders for 30-day refresh cycles on high-traffic posts
- List posts by "next refresh date" in ascending order (most urgent first)
- Prioritize refresh order by traffic/importance
- After each refresh, update the `lastUpdated` frontmatter field
- Track refresh history to measure freshness impact on rankings/citations
- Suggest running `/blog rewrite` for each scheduled refresh

### Step 6: Save & Next Steps

Save the calendar and suggest:
1. Start with `/blog brief <first-topic>` to create the first content brief
2. Use `/blog write` to generate articles from briefs
3. Use `/blog rewrite` for freshness updates on existing content
4. Re-run `/blog calendar` next month/quarter for the next plan
5. Review the Content Decay Report weekly and address Critical items first
6. Track Topic Cluster Progress monthly to ensure clusters reach completion
