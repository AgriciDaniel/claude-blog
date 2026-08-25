# AI Search SEO: Citation Strategies

Use GEO and AEO as legacy labels for AI citation readiness. For Google, the
Google Search Central AI features guidance is explicit: optimization for AI
Overviews and AI Mode is SEO, not a separate discipline.

## Core AI Search SEO Research

### Princeton GEO Paper (KDD 2024)
The Princeton GEO paper tested content transformations in a defined
experimental setting. It offers research context, not a calibrated forecast,
Google ranking factor, or universal causal effect.

| Technique | Reader-first interpretation |
|-----------|-----------------------------|
| Citing authoritative sources | Improves traceability when the source supports the claim |
| Relevant quotations | Can preserve expert context when quoted accurately |
| Supported statistics | Can make claims more specific when methodology and limits are clear |
| FAQPage entity markup | Optional visible-content markup; no Google rich result and no readiness score benefit |

Keyword stuffing is unhelpful to readers and conflicts with Google spam
guidance.

### Cross-Platform Citation Divergence

Vendor datasets show that citation sets can differ across products and query
samples. Treat those observations as non-causal and time-bound. They support
monitoring each declared surface separately, not a fixed content formula or
budget allocation.

### Kevin Indig's AI Search Pipeline (Jan 5, 2026)
Three critical stages:

1. **Retrieval**: Which pages enter the candidate set
   - Reliable server response time measured as an operational diagnostic
   - Metadata relevance
   - Primary content accessible to each declared target crawler; initial HTML
     improves portability when rendering support is unknown
2. **Citation**: Which sources get mentioned
   - Retrieval systems may value current facts for time-sensitive queries
   - Update only when facts, methods, or recommendations materially change
3. **Trust**: Which citations users click
   - Brand recognition
   - Source authority

## Content Format Impact on Citations

| Format | Impact | Source |
|--------|--------|--------|
| Listicles | Useful when the reader genuinely needs a curated set |
| Tables/structured data | Useful when they make comparisons or facts clearer |
| Long-form | Appropriate only when the task requires depth; no word minimum |
| FAQPage entity markup | Optional visible-content markup; no Google rich result and no readiness score benefit |
| Content with statistics | Use supported statistics when they improve reader understanding |
| Self-contained evidence-backed sections | Useful for readers and reuse; Google prescribes no chunk length |
| Comparison tables with `<thead>` | May improve extraction; attributed SEL figure is unverified |

### Passage-Level Extractability (2026)

Google may use query fan-out and retrieval across passages, but its guidance
does not prescribe chunking, question headings, or word bands. Make important
sections understandable on their own and support material claims with named
entities, dates when relevant, source attribution, and specific examples.

Clear entity references and transparent first-hand evidence can improve reader
trust when they are real and relevant. Do not treat either as a tie-breaker or
guarantee of inclusion in an AI answer.

## Platform-Specific Citation Patterns

Vendor observations vary by product, time, geography, and query set:

| Platform | Scoped observation |
|----------|--------------------|
| ChatGPT | Source mixes vary by retrieval mode and query sample |
| Perplexity | Community sources appear in some vendor datasets |
| AI Overviews | Eligible sources and links vary by query and Search surface |

2026 wrinkle: AI Overviews now highlight links from a user's subscribed
publications, so publisher subscriptions can influence which sources users see
inside the AI answer (Nieman Lab, 2026-05).

Vendor datasets report rapid source turnover on some Perplexity query sets.
Treat this as directional and query-dependent, not a universal content-decay
window or reason to change dates without substantive work.

## Meaningful Freshness

Update critical content when facts, screenshots, pricing, methods, source
availability, or intent have materially changed. Do not change dates or copy
solely to imitate freshness patterns observed in vendor datasets.

## Off-Site Context

### Vendor Dataset Context

Some vendor datasets report associations between branded mentions, video
mentions, links, and measured visibility. Correlation does not establish which
factor caused an outcome. Use off-site work to reach relevant audiences and
earn accurate coverage, not to satisfy an internal multiplier.

### Platform Presence

**YouTube**:
- Publish useful videos when demonstrations improve understanding.
- Use accurate titles and public transcripts for accessibility and discovery.

**Reddit**:
- Participate only where the community and topic are relevant.
- Follow community rules and avoid manufactured promotional activity.

**Review Platforms (B2B)**:
- Maintain accurate profiles where buyers actually research the category.
- Treat self-reported citation shares as product context, not causal evidence.

**Wikipedia/Wikidata**:
- Contribute only under the platform's notability, sourcing, neutrality, and
  conflict-of-interest policies.

## AI Crawler Technical Requirements

| Crawler | JavaScript rendering guidance |
|---------|-------------------------------|
| GPTBot (OpenAI) | Verify current official documentation and observed fetch behavior |
| ChatGPT-User | Capabilities can vary by product mode; verify current behavior |
| ClaudeBot | Verify current official documentation and observed fetch behavior |
| PerplexityBot | Verify current official documentation and observed fetch behavior |
| Googlebot | Can render eligible JavaScript; validate the rendered result |

Rendering capabilities and crawler policies can change. Prefer SSR, SSG, ISR,
or otherwise useful initial HTML for cross-crawler portability. Treat
JavaScript-gated content as critical only when testing shows a declared target
crawler cannot access the primary content.

### Google's Official Gen-AI Guidance

Google's stance holds: optimization for AI Overviews and AI Mode is SEO. There
is no special schema for gen-AI features, and Google does not need llms.txt.
Use standard crawlable HTML, Article schema with author and Organization
entities, helpful content, clear source attribution, and fast server responses.

### AI Crawler Traffic Context

Crawler volumes reported by infrastructure vendors can change quickly and may
start from very small baselines. Use server logs to understand the site's own
traffic. Do not convert aggregate growth figures into content or freshness
requirements.

### Performance Guidance for Retrieval
- Keep server responses reliable and reasonably fast for users and crawlers.
- Some crawlers and retrieval systems use practical timeouts; verify per crawler.
- Core Web Vitals are a constraint, not a growth lever - good CWV doesn't reliably
  outperform, but severe LCP failure creates disadvantage (Search Engine Land, 107,352 pages)
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
source quality, crawlability, and entity consistency.

## Attribution Gaps

Not all AI responses include citations, and retrieval behavior varies by
product and query. A page must be crawlable and eligible for retrieval before
it can appear as a cited source, but that does not guarantee selection.

## AI Search Case Study Context

Vendor case studies can suggest questions to test, but their attribution,
samples, query sets, product versions, and confounders differ. Do not reuse
headline uplift figures as benchmarks or evidence of a causal tactic. Require
the underlying methodology and results before making a case-study claim.

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

Readability supports readers. Any relationship with AI citation frequency is
vendor-reported and not a calibrated effect. Use audience-appropriate
readability as an editorial heuristic, not as a citation target.

### Readability Context
- Commercial platform reports associate some readability bands with citation
  outcomes, but the findings are not independently verified.
- Choose sentence structure and vocabulary for the audience and subject.
- Do not turn a Flesch range into a mandatory target or citation score.

### Citation Position Bias
- Some vendor samples observe more cited material earlier on a page, but that
  pattern is non-causal and query-dependent.
- State important answers early when that helps the reader, without requiring a
  fixed sentence position or section form.

### Reader-First Tactic Combinations
Clear writing and supported evidence can work together because readers need
both comprehension and trust. Do not apply experimental uplift figures as
expected results. Avoid keyword stuffing because it reduces usefulness and can
conflict with spam policies.

Support material claims with sources that actually substantiate them. Record
dates, titles, URLs, retrieval notes, methodology, and limitations when they
help readers identify or interpret the evidence. No fixed evidence triple,
length, or citation format is required for readiness.

### Schema & Structure for AI Citation
- Use proper table markup when a comparison helps readers and accessibility.
- Structured data can help supported parsers understand a page, but do not
  claim a citation lift or universal platform use without current primary
  evidence.

### Platform-Specific Observation Limits
| Platform | Non-causal context |
|----------|--------------------|
| ChatGPT | Source mixes depend on product mode, retrieval provider, and query set |
| Perplexity | Community-source and recency shares vary across vendor samples |
| AI Overviews | Source overlap with organic results varies by query and Search surface |

Compare declared surfaces independently with current, reproducible samples.
Do not infer a platform preference or causal ranking rule from overlap rates.

### Content Freshness for AI Citation
Freshness matters when the query or facts are time-sensitive. Update content
only after a substantive change and do not infer a universal decay window from
vendor citation samples.
