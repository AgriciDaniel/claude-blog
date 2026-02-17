---
name: blog-strategy
description: >
  Blog strategy development including content pillar definition, audience
  mapping, competitive landscape analysis, distribution channel planning
  (YouTube, Reddit, review platforms for GEO), measurement framework, and
  content differentiation through original research and first-hand experience.
  Use when user says "blog strategy", "content strategy", "blog positioning",
  "what should I blog about", "blog topics", "content pillars", "blog ideation".
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
  - WebFetch
  - WebSearch
  - Task
---

# Blog Strategy -- Positioning & Content Architecture

Develops comprehensive blog strategies that build topical authority for
Google rankings while establishing brand presence for AI citation platforms.

## Workflow

### Step 1: Discovery

Gather context through questions or project analysis:

1. **Business**: What do you sell/do? Who are your customers?
2. **Blog goals**: Traffic? Leads? Authority? AI citations?
3. **Current state**: Existing blog content? (scan if project available)
4. **Competitors**: Who are your 3-5 main competitors?
5. **Differentiator**: What unique expertise or data do you have?
6. **Resources**: Writing capacity (posts/week), budget for visuals?

### Step 2: Competitive Landscape

Research competitors' blogs:
1. WebSearch for competitor blog URLs
2. For each competitor, assess:
   - Publishing frequency
   - Content types (guides, case studies, comparisons, news)
   - Visual quality (images, charts, videos)
   - Schema usage
   - Social distribution (YouTube, Reddit, LinkedIn)
   - AI citation presence (search ChatGPT/Perplexity for industry terms)
3. Identify gaps no competitor covers well

### Step 3: Audience Mapping

Define 2-3 audience segments:

```
### Audience Segment: [Name]
- **Role**: [Job title / description]
- **Pain points**: [What problems do they have?]
- **Search behavior**: [What do they Google?]
- **AI behavior**: [What do they ask ChatGPT/Perplexity?]
- **Content preferences**: [Long guides? Quick answers? Video?]
- **Buying stage**: [Awareness / Consideration / Decision]
```

### Step 4: Content Pillar Design

Design 3-5 content pillars based on audience needs and competitive gaps:

```
### Pillar: [Topic Area]
- **Purpose**: Build authority in [topic]
- **Primary keywords**: [3-5 keywords]
- **Content types**: Pillar guide, supporting posts, comparisons, FAQ
- **Unique angle**: [What first-hand experience/data can you provide?]
- **Estimated posts**: [N] to achieve topic coverage
- **AI citation potential**: [High/Medium/Low] — [why]
```

### Step 5: Differentiation Strategy

The December 2025 Core Update rewards first-hand experience. Plan
how to demonstrate genuine expertise:

| Signal Type | Implementation |
|-------------|---------------|
| Original data | Conduct surveys, analyze proprietary data, run experiments |
| Case studies | Document real client/project results with metrics |
| Build in public | Share process, learnings, and failures transparently |
| Expert interviews | Feature practitioners with first-hand knowledge |
| Tool reviews | Test products personally, share screenshots and results |
| Industry analysis | Provide unique perspective on public data |

### Step 6: Distribution Channel Strategy

AI visibility requires off-site presence (88-92% of AI citations come
from off-site signals). Plan brand presence:

| Channel | AI Impact | Strategy |
|---------|-----------|----------|
| YouTube | 0.737 correlation (strongest) | Companion videos for pillar posts, how-tos, demos |
| Reddit | 450% citation surge | Authentic participation in 3-5 subreddits, share insights not links |
| Review platforms | 2.6-3.5x citation multiplier | Maintain profiles on G2, Capterra, TrustRadius (B2B) |
| Wikipedia/Wikidata | Credibility tiebreaker | Build notability through earned media, create Wikidata entry |
| Industry publications | Tier 2-3 citation source | Guest posts, expert commentary, study contributions |
| Social media | Brand mentions | LinkedIn thought leadership, Twitter/X insights |

Budget allocation recommendation: **40% owned content / 60% earned media and distribution**.

### Step 7: Measurement Framework

```
### Metrics to Track

#### Traditional SEO
- Organic traffic (monthly)
- Keyword rankings (top 10, top 3)
- Domain authority / Domain Rating
- Internal link coverage
- Core Web Vitals

#### AI Citation Metrics (New)
- Share of Voice in ChatGPT responses (manual tracking)
- AI Overview citation rate (Google Search Console)
- Perplexity mentions (manual tracking)
- AI referral traffic (GA4: source contains chatgpt, perplexity, claude)
- Brand mention volume (branded search + web mentions)

#### Content Quality
- Blog quality score via `/blog analyze` (target: 80+)
- Content freshness (% of posts updated within 30 days)
- Visual element coverage (charts + images per post)
- Citation tier quality (% tier 1-3 sources)

#### Business Impact
- Blog-attributed leads/conversions
- Email subscribers from blog
- Content-assisted revenue
```

### Step 8: Generate Strategy Document

Output format:

```
# Blog Strategy: [Business Name]

## Executive Summary
[2-3 sentences on the strategic direction]

## Audience
[Segment summaries]

## Content Pillars
[3-5 pillars with descriptions]

## Competitive Positioning
[How we differentiate — what unique value we bring]

## Distribution Channels
[Priority channels with specific tactics]

## Content Velocity
- New posts: [N]/week
- Freshness updates: [N]/month
- Visual elements: [N] charts + [N] images per post

## 90-Day Roadmap
### Month 1: Foundation
- [ ] Publish [Pillar 1] guide + [N] supporting posts
- [ ] Set up YouTube channel / Reddit profiles
- [ ] Establish measurement dashboard

### Month 2: Expansion
- [ ] Publish [Pillar 2] guide + [N] supporting posts
- [ ] First freshness update cycle
- [ ] Begin Reddit/YouTube distribution

### Month 3: Optimization
- [ ] Audit all posts with `/blog analyze`
- [ ] Optimize lowest-scoring posts
- [ ] Publish [Pillar 3] guide
- [ ] Review metrics, adjust strategy

## Measurement
[KPIs and tracking approach]

## Next Steps
1. Run `/blog calendar` to create the first month's editorial calendar
2. Run `/blog brief` for the first pillar page
3. Run `/blog write` to generate the first article
```
