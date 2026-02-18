---
name: blog-strategy
description: >
  Blog strategy development including topic cluster architecture with
  hub-and-spoke design, audience mapping, competitive landscape analysis,
  AI citation surface strategy across ChatGPT/Perplexity/AI Overviews,
  distribution channel planning (YouTube, Reddit, review platforms for GEO),
  content scoring targets, measurement framework, and content differentiation
  through original research and first-hand experience.
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
Includes topic cluster architecture, AI citation surface strategy, content
scoring targets, and GEO-specific optimization plans.

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

#### Competitive AI Citation Analysis

Map competitor visibility across AI platforms. Use WebSearch to find how
competitors appear in AI-generated responses for target keywords.

```
## Competitive AI Citation Map
| Query | ChatGPT Cites | Perplexity Cites | AI Overview Cites | Gap? |
|-------|--------------|-----------------|-------------------|------|
| [keyword] | [competitor/none] | [competitor/none] | [competitor/none] | [Yes/No] |
| [keyword] | [competitor/none] | [competitor/none] | [competitor/none] | [Yes/No] |
| [keyword] | [competitor/none] | [competitor/none] | [competitor/none] | [Yes/No] |
```

Score each competitor's AI visibility:
- **High**: Cited in 3/3 platforms for multiple queries
- **Medium**: Cited in 1-2 platforms or for limited queries
- **Low**: Rarely cited, only in niche queries
- **None**: No AI citation presence detected

Identify AI citation gaps -- queries where no competitor is cited. These
represent the highest-opportunity targets for new content.

Note: Only 12% overlap between platforms -- a competitor strong on ChatGPT
may be absent from Perplexity. Analyze each platform independently.

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

### Step 4: Content Pillar Design with Topic Cluster Architecture

Design 3-5 content pillars based on audience needs and competitive gaps.
For each pillar, build the full hub-and-spoke cluster model.

```
### Pillar: [Topic Area]
- **Purpose**: Build authority in [topic]
- **Primary keywords**: [3-5 keywords]
- **Content types**: Pillar guide, supporting posts, comparisons, FAQ
- **Unique angle**: [What first-hand experience/data can you provide?]
- **Estimated posts**: [N] to achieve topic coverage
- **AI citation potential**: [High/Medium/Low] — [why]
```

#### Cluster Architecture Design

For each pillar, design the complete hub-and-spoke structure:

```
### Cluster Architecture: [Pillar Topic]

                    ┌──────────────────┐
                    │   Pillar Page    │
                    │   3,000-4,000w   │
                    └────────┬─────────┘
                             │
           ┌─────────────────┼──────────────────┐
           │                 │                   │
    ┌──────▼──────┐   ┌─────▼──────┐   ┌───────▼──────┐
    │  Spoke #1   │   │  Spoke #2  │   │   Spoke #3   │
    │  1,500-2,500│   │  1,500-2,500│  │  1,500-2,500 │
    └──────┬──────┘   └─────┬──────┘   └───────┬──────┘
           │                │                   │
           └────────────────┼───────────────────┘
                    (cross-links between spokes)
```

For each cluster, specify:
- **8-12 spoke topics** per pillar, each targeting a specific long-tail keyword
- **Internal linking plan** between all cluster pages (every spoke links to pillar, pillar links to all spokes, spokes cross-link to related spokes)
- **Content template assignment** for each piece from the 12 available templates:
  `how-to-guide`, `listicle`, `case-study`, `comparison`, `pillar-page`,
  `product-review`, `thought-leadership`, `roundup`, `tutorial`,
  `news-analysis`, `data-research`, `faq-knowledge`

```
### Cluster Build Plan: [Pillar Topic]
| # | Spoke Topic | Template | Target Keyword | Word Count | Internal Links |
|---|------------|----------|---------------|-----------|----------------|
| P | [Pillar title] | pillar-page | [keyword] | 3,000-4,000 | Links to all spokes |
| 1 | [Spoke title] | how-to-guide | [keyword] | 1,500-2,500 | Pillar + Spokes 2,3 |
| 2 | [Spoke title] | comparison | [keyword] | 1,500-2,500 | Pillar + Spokes 1,3 |
| 3 | [Spoke title] | listicle | [keyword] | 1,500-2,500 | Pillar + Spokes 1,2 |
| ... | ... | ... | ... | ... | ... |
```

Reference: `references/internal-linking.md` for hub-and-spoke model and anchor text rules.

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

### Step 5.5: AI Citation Surface Strategy

Plan how to maximize AI citation across platforms. 80% of LLM citations
come from outside the top 100 organic results -- traditional SEO alone
is insufficient.

#### On-Site Optimization

Structure every piece of content for AI citability:
- Every H2 opens with an answer-first paragraph (40-60 words with stat + source)
- **Citation capsules**: 40-60 word self-contained passages per H2 section
- **Q&A format**: 60-70% of H2 headings phrased as questions
- **FAQ sections** with schema markup on every post
- **Entity clarity**: consistent terminology throughout (no synonym variation for key concepts)
- **Structured data**: JSON-LD for Article, FAQ, HowTo, and Review schemas

#### Off-Site Presence (Critical -- 88-92% of AI citations from off-site)

| Channel | AI Citation Impact | Priority Action |
|---------|-------------------|-----------------|
| YouTube | 0.737 correlation (strongest) | Companion videos for pillar posts |
| Reddit | 450% citation surge | Authentic participation in 3-5 subreddits |
| Review platforms | 2.6-3.5x multiplier | Maintain profiles on G2, Capterra (B2B) |
| Wikipedia/Wikidata | Credibility tiebreaker | Build notability, create Wikidata entry |
| Industry publications | Tier 2-3 citation source | Guest posts, expert commentary |

#### Cross-Platform Monitoring

- Track brand mentions in ChatGPT, Perplexity, Google AI Overviews
- Only 12% overlap between platforms -- optimize for each separately
- 80% of LLM citations come from outside the top 100 organic results
- Monitor monthly: search 10-20 target queries on each platform, log citations

Reference: `references/geo-optimization.md` for detailed GEO tactics.

### Step 5.6: Content Scoring Targets

Set quality standards that all blog content must meet:

```
### Content Quality Standards
| Metric | Target | Measured By |
|--------|--------|-------------|
| Blog quality score | 80+ | `/blog analyze` |
| E-E-A-T compliance | Named author + 8+ tier 1-3 sources | Manual review |
| AI citation readiness | Answer-first + FAQ + citation capsules | `/blog analyze` |
| Visual minimum | 2+ charts + 3+ images per post | Asset count |
| Internal links | 5+ per post (within cluster) | Link audit |
| Schema markup | Article + FAQ + relevant type | Structured data test |
| Word count | 1,500+ for spokes, 3,000+ for pillars | Word count tool |
```

Every post should be scored before publishing. Posts below 80 quality score
should be revised before going live.

### Step 5.7: GEO-Specific Strategy

Plan passage-level citability across all content, tailored to each AI platform.

| AI Platform | Favors | Optimization Focus |
|-------------|--------|-------------------|
| ChatGPT | Recency, brand authority, conversational clarity | Update posts within 30 days, clear entity definitions |
| Perplexity | Citations, source diversity, structured answers | Tier 1-3 sources, numbered lists, data tables |
| Google AI Overviews | Structured data, schema, topical authority | FAQ schema, HowTo schema, complete topic clusters |

Strategy by platform:
- **ChatGPT**: Ensure brand name appears consistently, maintain 30-day freshness, use conversational answer-first formatting
- **Perplexity**: Maximize external citation count (8+ per post), use structured data tables, cite authoritative sources
- **AI Overviews**: Complete topic cluster coverage, implement all relevant schema types, achieve featured snippet format

Reference: `references/geo-optimization.md` for platform-specific optimization guides.

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

Reference: `references/distribution-playbook.md` for detailed channel tactics and templates.

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

## Content Pillars & Cluster Architecture
[3-5 pillars with full hub-and-spoke cluster plans]
[Internal linking map for each cluster]
[Template assignments for each piece]

## Competitive Positioning
[How we differentiate — what unique value we bring]
[Competitive AI Citation Map showing gaps to exploit]

## AI Citation Surface Strategy
[On-site optimization checklist]
[Off-site presence plan with priority channels]
[Platform-specific GEO tactics]

## Content Quality Standards
[Scoring targets for all content]
[E-E-A-T compliance requirements]

## Distribution Channels
[Priority channels with specific tactics]

## Content Velocity
- New posts: [N]/week
- Freshness updates: [N]/month
- Visual elements: [N] charts + [N] images per post

## 90-Day Roadmap
### Month 1: Foundation
- [ ] Publish [Pillar 1] guide + [N] supporting spokes
- [ ] Set up YouTube channel / Reddit profiles
- [ ] Establish measurement dashboard
- [ ] Complete competitive AI citation audit

### Month 2: Expansion
- [ ] Publish [Pillar 2] guide + [N] supporting spokes
- [ ] First freshness update cycle
- [ ] Begin Reddit/YouTube distribution
- [ ] Launch off-site presence on review platforms

### Month 3: Optimization
- [ ] Audit all posts with `/blog analyze` (target: 80+ score)
- [ ] Optimize lowest-scoring posts
- [ ] Publish [Pillar 3] guide
- [ ] Review AI citation metrics across all platforms
- [ ] Adjust strategy based on data

## Measurement
[KPIs and tracking approach — traditional SEO + AI citation metrics]

## Reference Documents
- `references/internal-linking.md` — Hub-and-spoke model, anchor text rules
- `references/distribution-playbook.md` — Channel tactics and templates
- `references/geo-optimization.md` — GEO platform-specific optimization
- `references/content-templates.md` — 12 content templates with structures

## Next Steps
1. Run `/blog calendar` to create the first month's editorial calendar
2. Run `/blog brief` for the first pillar page
3. Run `/blog write` to generate the first article
4. Set up AI citation monitoring for target queries
```
