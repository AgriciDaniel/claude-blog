# AI Search SEO: Citation Strategies

Use GEO and AEO as legacy labels for AI citation readiness. For Google, the
Google Search Central AI features guidance is explicit: optimization for AI
Overviews and AI Mode is SEO, not a separate discipline.

## Core AI Search SEO Research

### Princeton GEO Paper (KDD 2024)
The Princeton GEO paper reports that content changes can boost AI visibility
by up to 40% in test conditions. Treat the result as research on AI search
surfaces, not as a separate Google ranking discipline.

| Technique | Improvement |
|-----------|-------------|
| Citing authoritative sources | +115.1% visibility (5th-ranked sites, main experiment) |
| Quotation addition | +28% (main experiment); +37% (Perplexity.ai validation, Table 7) |
| Statistics addition | +41% (main experiment); +22% (Perplexity.ai validation, Table 7) |
| FAQPage entity markup | May aid AI citation as an entity signal for visible Q&A; no Google rich result; impact unverified |

Traditional keyword stuffing performs **worse than baseline** in generative engines.

### Cross-Platform Citation Divergence

- Only 11% of domains are cited by both ChatGPT and Perplexity (Digital Bloom, 2025;
  domain-level, not URL-level; AI Overviews not included in that study)
- 80% of LLM citations don't rank in Google's top 100 (Ahrefs, Aug 2025) - classic
  organic rankings alone are a poor predictor of AI citation
- Brands are 6.5x more likely to be cited through third-party sources than their own
  domains (AirOps, Oct 2025) - earned media dominates AI visibility

### Kevin Indig's AI Search Pipeline (Jan 5, 2026)
Three critical stages:

1. **Retrieval**: Which pages enter the candidate set
   - Server response time under 200ms TTFB
   - Metadata relevance
   - Content must be in HTML (not behind JS)
2. **Citation**: Which sources get mentioned
   - Content freshness dominates (70%+ cited pages updated within 12 months)
   - Content within 3 months performs best
3. **Trust**: Which citations users click
   - Brand recognition
   - Source authority

## Content Format Impact on Citations

| Format | Impact | Source |
|--------|--------|--------|
| Listicles | Often over-index in vendor datasets; exact shares vary and are directional |
| Tables/structured data | May improve extractability; specific 2.5x vendor claim is unverified |
| Long-form (2,000+ words) | Often over-indexes in vendor studies; treat multipliers as directional |
| FAQPage entity markup | May aid AI citation as an entity signal for visible Q&A; no Google rich result; impact unverified |
| Content with statistics | Original, sourced statistics improve citeability; exact lifts vary by study |
| Sections of 120-180 words between headings | Self-contained passages likely help extraction; exact lift is unverified |
| Comparison tables with `<thead>` | May improve extraction; attributed SEL figure is unverified |

### Passage-Level Extractability (2026)

Google's AI systems fragment pages and evaluate self-contained answer passages,
not just whole documents. Start each H2 with an approximately 50-word
direct-answer sentence, then build a 120-180 word passage that can stand alone
if quoted or summarized. Support it with named entities, dates, source
attribution, and a specific example.

Entity density and demonstrated first-hand Experience break ties. A single
clean passage with original testing, named tools, and verifiable evidence can
earn an AI Overview citation even when the full page is not the strongest
organic result.

## Platform-Specific Citation Patterns

Each AI platform has distinct content preferences:

| Platform | Favored Content Type | Key Bias |
|----------|---------------------|----------|
| ChatGPT | "Best X" listicles | 43.8% of citations are list-format content |
| Perplexity | Reddit discussions | 6.6% of all citations come from Reddit |
| AI Overviews | Google properties | 23% of citations favor Google-owned sources |

2026 wrinkle: AI Overviews now highlight links from a user's subscribed
publications, so publisher subscriptions can influence which sources users see
inside the AI answer (Nieman Lab, 2026-05).

**Perplexity content decay**: Citation relevance begins declining 2-3 days
post-publication - Perplexity heavily weights recency, making it the most
freshness-dependent platform. Content older than 1 week sees sharp citation drops.

## Content Freshness Requirements

- 76.4% of ChatGPT's most-cited pages updated within 30 days (Ahrefs, ~17M citations)
- URLs cited in AI results are 25.7% fresher than traditional search
- Content < 3 months old is 3x more likely to get cited
- **Action**: Update critical content when facts, screenshots, pricing, methods,
  source availability, or SERP intent have materially changed

## Off-Site Signals (Dominate AI Visibility)

### Ahrefs Study (Dec 2025, 75,000 brands)

| Factor | Correlation with AI Visibility |
|--------|-------------------------------|
| YouTube mentions | 0.737 (strongest) |
| Branded web mentions | 0.656-0.709 |
| Domain Rating | 0.266-0.326 |
| Backlinks | 0.218 (dramatically weaker than expected) |

### Platform-Specific Citation Rates

**YouTube**:
- Citations in AI Overviews up 414% (Q1 2025, NP Digital, 10K+ AIO analysis)
- How-to videos up 651%
- Visual demos up 592%
- 200x more cited than any other video platform
- Optimization: keywords in titles/transcripts, Q&A-style, 10+ min, public transcripts

**Reddit**:
- Citations surged 1.30% → 7.15% (450% growth)
- Google's $60M annual API deal
- 2.2-21% of AI Overview citations by query type
- Strategy: Authentic participation in 3-5 subreddits BEFORE any promotional content

**Review Platforms (B2B)**:
- G2 accounts for 22-23% of review-platform citations (Radix via G2's own blog;
  self-reported - Hall.com's independent analysis found G2 at only 8.25% of B2B
  software citations in ChatGPT)
- 33% of review citations come from G2 (Profound via G2's blog; treat as directional)
- Multi-platform presence: 4.6-6.3 citations vs 1.8 without (2.6-3.5x multiplier)

**Wikipedia/Wikidata**:
- 7.8% of all ChatGPT citations (Profound)
- Used as "credibility tiebreaker" when sources conflict

### Budget Allocation
Recommended: **40% owned content / 60% earned media**
(Most companies allocate 90/10 - this is wrong for AI search SEO)

88-92% of AI citations come from off-site signals in vendor-reported datasets.
Treat this as directional, not a universal law.

## AI Crawler Technical Requirements

| Crawler | JavaScript Rendering |
|---------|---------------------|
| GPTBot (OpenAI) | No |
| ChatGPT-User | No |
| ClaudeBot | No |
| PerplexityBot | No |
| Googlebot | Yes |

**Critical**: Content behind JavaScript is invisible to ChatGPT, Claude, Perplexity.
Use SSR, SSG, or ISR. Test by disabling JS and reloading.

### Google's Official Gen-AI Guidance

Google's stance holds: optimization for AI Overviews and AI Mode is SEO. There
is no special schema for gen-AI features, and Google does not need llms.txt.
Use standard crawlable HTML, Article schema with author and Organization
entities, helpful content, clear source attribution, and fast server responses.

### AI Crawler Traffic Growth

- Cloudflare AI crawling rose 32% YoY across all monitored sites
- GPTBot traffic grew 305% YoY
- PerplexityBot traffic grew 157,490% YoY (from near-zero baseline)
- 65% of AI bot hits target content published within the past year (Seer Interactive)
  - freshness is a retrieval signal, not just a citation signal

### Performance Requirements for AI Retrieval
- Server response time under 200ms TTFB (Kevin Indig pipeline)
- TTFB above 600ms may reduce crawl or extraction reliability
- Some crawlers and retrieval systems use short practical timeouts; verify per crawler
- Core Web Vitals are a constraint, not a growth lever - good CWV doesn't reliably
  outperform, but severe LCP failure creates disadvantage (Search Engine Land, 107,352 pages)
- Top 10 domains capture 46% of all ChatGPT citations per topic (Growth Memo, Mar 2026)
- Slow pages may miss crawl, fetch, or extraction opportunities
- Vercel analysis of 500+ million GPTBot fetches found zero evidence of JS execution

### robots.txt for AI Visibility
```
User-agent: GPTBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: PerplexityBot
Allow: /
```

### llms.txt Standard
Google does not need llms.txt for AI Overviews or AI Mode. Treat the file as an
optional site inventory for non-Google tools, not a ranking or citation lever.
Do not spend AI search SEO budget on llms.txt before crawlability, passage extraction,
Article schema, source quality, and entity consistency.

## Attribution Gaps

Perplexity visits ~10 pages per query but cites only 3-4. Not all AI responses
include citations - optimizing for retrieval is critical. Content must enter the
candidate set before citation is possible.

## AI Search Case Study Results

These examples are illustrative, vendor-reported, and not independently
verified. Do not reuse the numbers as factual benchmarks without primary
confirmation.

| Company | Results | Timeframe |
|---------|---------|-----------|
| Go Fish Digital | +43% AI traffic, +83% conversions, 25x conversion rate | 3 months |
| Netpeak USA | +120% revenue, +693% AI visits | Ongoing |
| Nine Peaks Media | 36% visibility improvement, first ChatGPT citations | Ongoing |
| ABM Agency/Chemours | 82% ChatGPT mention rate, $90M+ pipeline | Ongoing |
| Smart Rent | 32% SQL increase, 40% faster pipeline | Ongoing |

## Entity-First SEO

Every page should unambiguously represent ONE canonical entity.
Google Knowledge Graph: 800B facts about 8B entities.

Entity building timeline (3-6 months):
1. Create entity map with Wikidata Q-IDs
2. Establish Wikipedia/Wikidata presence only when the entity meets independent
   notability requirements; disclose conflicts of interest and follow platform policy
3. Build entity consistency across all platforms (exact same name)
4. Practice "controlled co-occurrence" via third-party mentions
5. Earn external citations from recognized publications

## Readability and AI Search Connection

Readability can support AI citation rates, but the lift is not independently
verified. Use Flesch 60-75 as a clarity heuristic, not as a citation guarantee.

### Flesch Score & AI Citation Rates
- Commercial platform reports associate Flesch 60-75 with more AI citations;
  this is vendor-reported internal data with no independent verification.
- Teams improving Flesch from 52→68 saw parallel citation lifts within two
  crawl windows
- Content that is too complex (Flesch <50) or too simple (Flesch >80) gets
  fewer citations - AI systems prefer fluent, authoritative writing

### Citation Position Bias
- **44.2% of all LLM citations come from the first 30% of text** is a
  single-source Growth Memo finding (Feb 2026, Kevin Indig). Treat it as
  directional support for answer-first formatting, not a settled benchmark.
- Direct answers in the first 1-2 sentences of each section maximize
  extractability for AI systems

### AI Search Tactic Combinations
Princeton GEO paper (KDD 2024) findings on readability-related tactics:
- **Fluency optimization** = 15-30% visibility boost
- **Statistics addition** = up to 41% visibility boost
- **Fluency + Statistics combined** outperforms any single tactic by 5.5%
- Keyword stuffing performs -10% WORSE than baseline

**FLOW evidence triple is mandatory for AI-citation readiness.** AI assistants extract claims that have year anchor in prose, inline publisher + title, and URL with retrieval date. Stats without the triple are less likely to surface in citations. See `flow-alignment.md`.

### Schema & Structure for AI Citation
- Comparison tables with proper HTML (`<thead>`, `<tbody>`) = **47% higher**
  AI citation rates (attributed to SEL; primary source unlocatable - treat as directional)
- Structured data helps machine understanding, but do not claim all major AI
  platforms use schema during citation selection without current primary evidence

### Platform-Specific Citation Behaviors
| Platform | Key Behavior | Readability Preference |
|----------|-------------|----------------------|
| ChatGPT | Wikipedia = 7.8% of citations; SearchGPT: 87% match Bing top 10 | Prefers well-structured, fluent content |
| Perplexity | Reddit = 46.7% of top-10 sources; strongest depth correlation (0.191) | 2-3 day content decay; heavily weights recency |
| AI Overviews | 93.67% from top-10 organic; avg 10.2 links per response | Prefers established authority + clear answers |

Only 11% of domains are cited by both ChatGPT and Perplexity (Digital Bloom). Only 12%
of URLs cited by ChatGPT, Perplexity, and Copilot rank in Google's top 10 (Ahrefs).

### Content Freshness for AI Citation
- **65%** of AI bot hits target content published within the past year (Seer Interactive)
- **85%** of AI Overview citations come from content <2 years old
- **44%** of AI Overview citations come from 2025 content specifically
- **50%** of Perplexity citations come from 2025 alone
- Content older than 3 months sees 3x fewer citations
