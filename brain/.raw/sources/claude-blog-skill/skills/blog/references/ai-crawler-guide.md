# Technical AI Visibility: Crawler Access & Rendering

## Contents

- [robots.txt Template for AI Crawlers](#robotstxt-template-for-ai-crawlers)
- [Cloudflare AI Crawl Control: CRITICAL](#cloudflare-ai-crawl-control-critical)
- [Google Gen-AI Guidance](#google-gen-ai-guidance)
- [llms.txt Implementation](#llmstxt-implementation)
- [Server-Side Rendering Requirements](#server-side-rendering-requirements)
- [Passage-Level Extractability](#passage-level-extractability)
- [Performance Requirements](#performance-requirements)
- [Testing AI Crawler Visibility](#testing-ai-crawler-visibility)
- [AI Crawler Traffic Growth](#ai-crawler-traffic-growth)
- [AI Crawler Checklist](#ai-crawler-checklist)

## robots.txt Template for AI Crawlers

Allow documented AI crawlers explicitly when you want access. For compliant
crawlers, an absent `Disallow` usually means allowed; explicit `Allow` rules are
optional documentation and help teams audit intent.

```
# ===========================================
# AI Search & LLM Crawlers: Explicitly Allow
# ===========================================

# OpenAI
User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

# Anthropic documented crawler families
User-agent: ClaudeBot
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: Claude-User
Allow: /

# Deprecated Anthropic strings (kept for legacy compatibility):
# User-agent: Claude-Web
# User-agent: anthropic-ai

# Google AI product token (Gemini/Vertex training and non-Search grounding controls)
# Google Search AI features use Googlebot plus preview controls:
# https://developers.google.com/search/docs/appearance/ai-features
User-agent: Google-Extended
Allow: /

# Perplexity
User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

# Meta
User-agent: Meta-ExternalAgent
Allow: /

# ByteDance
User-agent: Bytespider
Allow: /

# Google AI agents (Project Mariner)
User-agent: Google-Agent
Allow: /

# DuckDuckGo AI
User-agent: DuckAssistBot
Allow: /

# Apple (Siri, Apple Intelligence)
User-agent: Applebot-Extended
Allow: /

# Amazon (Alexa, product search)
User-agent: Amazonbot
Allow: /

# You.com
User-agent: YouBot
Allow: /

# Phind (developer search)
User-agent: PhindBot
Allow: /

# Exa (AI-native search engine)
User-agent: ExaBot
Allow: /

# Common Crawl (used by many AI models)
User-agent: CCBot
Allow: /

# ===========================================
# Traditional Search Engines
# ===========================================

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: *
Allow: /

# ===========================================
# Sitemap
# ===========================================
Sitemap: https://example.com/sitemap.xml
```

### Crawler Identification Reference

Providers expose different crawler classes. Some split training, search indexing,
and user-triggered retrieval; others publish only one bot or a product token.
Blocking a documented search/indexing bot can reduce visibility in that platform's
answers. User-triggered retrieval may not fully respect robots.txt.
OpenAI bot details: https://platform.openai.com/docs/bots.

| Crawler | Operator | Type | Respects robots.txt |
|---------|----------|------|---------------------|
| GPTBot | OpenAI | Training | Yes |
| OAI-SearchBot | OpenAI | Search indexing | Yes |
| ChatGPT-User | OpenAI | User-triggered retrieval | Not guaranteed |
| ClaudeBot | Anthropic | Training | Yes |
| Claude-SearchBot | Anthropic | Search indexing | Yes |
| Claude-User | Anthropic | User retrieval | Yes |
| ~~Claude-Web~~ | Anthropic | Deprecated | - |
| ~~anthropic-ai~~ | Anthropic | Deprecated | - |
| Google-Extended | Google | Gemini/Vertex training and some non-Search grounding controls; not Search AI inclusion | Yes |
| Google-Agent | Google | Project Mariner agentic (2026) | Yes |
| PerplexityBot | Perplexity | Search indexing | Yes |
| Perplexity-User | Perplexity | User retrieval | Partial |
| Applebot-Extended | Apple | Apple Intelligence training | Yes |
| Meta-ExternalAgent | Meta | High-volume data collection | Yes |
| Bytespider | ByteDance | Training/indexing | Partial (documented issues) |
| Amazonbot | Amazon | Alexa / product search | Yes |
| DuckAssistBot | DuckDuckGo | DuckAssist AI answers | Yes |
| YouBot | You.com | AI search engine | Yes |
| PhindBot | Phind | Developer-focused AI search | Yes |
| ExaBot | Exa | Neural search engine | Yes |
| CCBot | Common Crawl | Open dataset (used by many LLMs) | Yes |

### robots.txt Strategy by Bot Type

Treat each bot category differently based on your goals:
- **Training/product tokens** (GPTBot, ClaudeBot, CCBot, Google-Extended): Your
  choice. Blocking affects training or non-Search product use as documented by
  each provider, but Google-Extended does not control Google Search AI inclusion.
- **Search/indexing bots** (OAI-SearchBot, Claude-SearchBot, PerplexityBot): **Allow these.**
  Blocking means your content won't appear in ChatGPT, Claude, or Perplexity answers.
- **Retrieval bots** (ChatGPT-User, Perplexity-User): May not fully respect robots.txt. These
  are triggered by live user queries and may fetch content regardless of directives.

---

## Cloudflare AI Crawl Control: CRITICAL

**Since July 2025, Cloudflare blocks AI crawlers by default on new domains.**
This is the single most common reason blogs are invisible to AI systems despite
having correct robots.txt configuration.

### How to Fix

1. Log in to Cloudflare dashboard
2. Navigate to **Security > Bots > AI Crawlers**
3. Review the list of AI crawlers
4. **Toggle "Allow" for each AI crawler you want to permit**
5. Save changes

### What Cloudflare Blocks by Default

| Crawler or token | Default Status (New Domains) |
|------------------|------------------------------|
| GPTBot | Blocked |
| ClaudeBot | Blocked |
| PerplexityBot | Blocked |
| CCBot | Blocked |
| Google-Extended | Blocked |
| Applebot-Extended | Allowed |
| Googlebot | Allowed (not an AI crawler) |

### Verification

After updating Cloudflare settings, verify access:

```bash
# Simulate GPTBot user-agent
curl -s -A "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.0; +https://openai.com/gptbot)" https://yourdomain.com/blog/test-post | head -50

# Check for Cloudflare block page (403 or challenge page)
curl -s -o /dev/null -w "%{http_code}" -A "Mozilla/5.0 (compatible; ClaudeBot/1.0)" https://yourdomain.com/
```

If you get a 403 or an HTML page with "Cloudflare" in it, the crawler is blocked.

---

## Google Gen-AI Guidance

Google Search Central's AI features guidance says optimization for AI Overviews
and AI Mode is normal SEO: https://developers.google.com/search/docs/appearance/ai-features.
Google does not require special AI schema or llms.txt for Search AI features.
Use crawlable HTML, standard Article schema with author Person and publisher
Organization, clear source attribution, helpful trustworthy content, and fast
server responses.

---

## llms.txt Implementation

The `llms.txt` standard (proposed by llmstxt.org, Sep 2024) provides a machine-readable
summary of your site for LLMs. Place at site root: `https://example.com/llms.txt`.

**Important caveat:** Google's current stance is no llms.txt needed for AI
Overviews or AI Mode per Google Search Central's AI features guidance. No major
AI platform has confirmed relying on it. Treat it as an optional site inventory
for non-Google tools, not a ranking, indexing, or citation requirement.

### Specification

- Plain text file, UTF-8
- Under 10KB total
- Structured list of important URLs with brief descriptions
- Helps LLMs understand site structure and find authoritative content

### Template

```
# Example Blog

> A blog about modern web development, SEO, and content strategy.

## Main Pages

- [Home](https://example.com/): Main landing page with latest articles
- [About](https://example.com/about): Company information and mission
- [Blog](https://example.com/blog): All published articles

## Popular Articles

- [Complete Guide to Technical SEO in 2026](https://example.com/blog/technical-seo-guide): Comprehensive technical SEO guide covering Core Web Vitals, crawlability, and schema markup.
- [How AI Overviews Changed Search](https://example.com/blog/ai-overviews-impact): Data-driven analysis of AI Overview impact on organic traffic with case studies.
- [Content Strategy for B2B SaaS](https://example.com/blog/b2b-saas-content-strategy): Framework for building a content program that drives pipeline.

## Topic Clusters

- [SEO](https://example.com/topics/seo): All articles about search engine optimization
- [Content Strategy](https://example.com/topics/content-strategy): Content planning and execution
- [Web Development](https://example.com/topics/web-development): Frontend and backend development guides

## Authors

- [Sarah Chen](https://example.com/author/sarah-chen): Content strategist, B2B SaaS specialist
- [Marcus Rivera](https://example.com/author/marcus-rivera): Senior frontend engineer, React expert
```

### Key Rules

- Do not exceed 10KB (LLMs may truncate or ignore larger files)
- Use markdown-style links: `[Title](URL): Description`
- Include only your most important and highest-quality pages
- Update when you publish significant new content
- This is NOT a sitemap replacement: it supplements sitemap.xml
- Do not treat a missing llms.txt file as an AI visibility blocker

---

## Server-Side Rendering Requirements

Standard non-Google AI crawlers generally should be assumed not to execute
JavaScript unless their documentation says otherwise. Content rendered only via
client-side JavaScript is risky for AI visibility; render important blog content
into initial HTML and verify per crawler.

### Rendering Strategy Ranking

| Strategy | AI Visibility | Performance | Recommendation |
|----------|--------------|-------------|----------------|
| **SSG** (Static Site Generation) | Best | Best | Preferred for blogs |
| **SSR** (Server-Side Rendering) | Excellent | Good | Good for dynamic content |
| **ISR** (Incremental Static Regeneration) | Excellent | Good | Good for large sites |
| **CSR** (Client-Side Rendering) | None | Poor for crawlers | Never use for content |

### JavaScript Execution by Crawler

| Crawler | Executes JavaScript | Renders Pages |
|---------|-------------------|---------------|
| GPTBot | No | No |
| OAI-SearchBot | No | No |
| ChatGPT-User | No | No |
| ClaudeBot | No | No |
| Claude-SearchBot | No | No |
| Claude-User | No | No |
| PerplexityBot | No | No |
| Perplexity-User | No | No |
| Meta-ExternalAgent | No | No |
| Bytespider | No | No |
| Amazonbot | No | No |
| CCBot | No | No |
| **Googlebot** | **Yes** | **Yes** |
| **AppleBot** | **Yes** | **Yes** |
| **OpenAI agentic browsing surfaces** | **Yes** | **Yes** |
| **Google-Agent** (agentic) | **Yes** | **Yes** |

### Vercel Findings

Vercel analyzed 500M+ GPTBot fetches and found **zero evidence of JavaScript
execution**. GPTBot reads raw HTML only. Content loaded via React hydration,
Vue mounting, or any client-side framework is completely invisible.

### Exception: Agentic Tools

Standard AI crawlers generally do not execute JavaScript. However, **agentic tools** are different:
- **OpenAI agentic browsing surfaces**: Full JS rendering may be available depending on product mode.
- **Google-Agent / Project Mariner** (Google, 2026): Operates through Chrome with full rendering.

These are user-directed agents, not automated crawlers. They can see JS-rendered content,
but they do not replace the need for SSR - standard crawlers still dominate citation indexing.

---

## Passage-Level Extractability

Crawler access gets a page into the candidate set. Citation selection depends on
whether the page contains self-contained answer passages AI systems can extract.
Target 120-180 word passages that answer one question without relying on the
surrounding article.

Under each H2, start with an approximately 50-word direct-answer sentence that
gives the answer, the year, the named entity, and the source attribution. Follow
with specific entities, dates, original examples, and first-hand Experience
markers. A clean passage can earn an AI Overview citation even when the full
page is not cited.

AI Overviews also began highlighting links from a user's subscribed
publications in 2026, so publisher trust and subscriptions can affect which
citations users notice (Nieman Lab, 2026-05).

---

## Performance Requirements

AI retrieval systems have practical latency budgets. Slow sites may reduce crawl,
fetch, and extraction reliability before content quality is evaluated.

**Note:** The thresholds below are industry best practices and observations from SEO tooling
(Discovered Labs, Prerender.io, Kevin Indig). They are NOT officially published specifications
from OpenAI, Anthropic, or Perplexity. Treat as directional targets, not guaranteed cutoffs.

### Thresholds

| Metric | Target | Risk threshold | Consequence |
|--------|--------|----------------|-------------|
| TTFB (Time to First Byte) | < 200ms | > 600ms | May reduce crawl or extraction reliability |
| Full page load (HTML) | < 500ms | > 1,000ms | May reduce crawl frequency |
| Response size (HTML) | < 200KB | > 500KB | May cause partial content extraction |

### Optimization Priorities

1. **Use a CDN**: Content must be served from edge locations
2. **Enable compression**: gzip or Brotli for all text responses
3. **Minimize HTML bloat**: Remove unused CSS/JS from HTML response
4. **Cache aggressively**: Static pages should have long cache headers
5. **Pre-render**: Use SSG or SSR, never CSR for content pages

---

## Testing AI Crawler Visibility

### Quick Test: See What AI Crawlers See

```bash
# Basic: view raw HTML (what all AI crawlers receive)
curl -s https://yourdomain.com/blog/your-post | head -200

# Check if main content is in HTML source
curl -s https://yourdomain.com/blog/your-post | grep -c "<article"

# Check for JS-only rendering indicators
curl -s https://yourdomain.com/blog/your-post | grep -c "id=\"__next\""
curl -s https://yourdomain.com/blog/your-post | grep -c "id=\"root\""
curl -s https://yourdomain.com/blog/your-post | grep -c "id=\"app\""

# If the above returns content in a <noscript> tag or empty divs,
# your content is behind JS and invisible to AI crawlers.
```

### Full Crawler Simulation

```bash
# Simulate GPTBot
curl -s -H "User-Agent: Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.0; +https://openai.com/gptbot)" \
  https://yourdomain.com/blog/your-post > /tmp/gptbot-view.html

# Simulate ClaudeBot
curl -s -H "User-Agent: Mozilla/5.0 (compatible; ClaudeBot/1.0; +https://claudebot.ai)" \
  https://yourdomain.com/blog/your-post > /tmp/claudebot-view.html

# Check if content exists
wc -l /tmp/gptbot-view.html
grep -c "your-expected-heading-text" /tmp/gptbot-view.html
```

### Red Flags (Content Invisible to AI)

| Indicator | What It Means |
|-----------|---------------|
| Empty `<div id="root"></div>` | React CSR: content loads via JS only |
| Empty `<div id="__next"></div>` without SSR/RSC/static output | Next.js App Router or Pages Router shipping content client-side only |
| `<noscript>` contains the content | Content explicitly hidden from non-JS clients |
| `<script>` tags contain all content as JSON | Data fetched client-side, not in HTML |
| HTML under 5KB for a full blog post | Content not rendered server-side |

### Next.js App Router Guidance

- Prefer static rendering for blog routes. Use Server Components for article
  content and `generateStaticParams()` for known slugs.
- Use ISR for large blogs when content changes after build. Keep the article body
  in server-rendered HTML.
- Use dynamic rendering only when the page genuinely depends on request-time data.
  Do not move the article body behind client-only data fetching.
- `generateMetadata()` should emit canonical, Open Graph, and Article metadata
  server-side.

---

## AI Crawler Traffic Growth

Traffic from AI crawlers is growing exponentially. Sites that block or fail
to serve these crawlers are losing compounding visibility.

| Metric | Value | Source |
|--------|-------|--------|
| GPTBot traffic growth | +305% YoY | Cloudflare Radar, 2025 |
| PerplexityBot traffic growth | +157,490% YoY | Cloudflare Radar, 2025 |
| AI crawling volume overall | +32% YoY | Cloudflare, 2025 |
| Top 10 domains' citation share | 46% of all ChatGPT citations per topic | Growth Memo, Mar 2026 |
| AI referral traffic share | Small but fastest-growing; no standardized total-web share | Similarweb, 2026-05-28 |
| AI referral traffic growth | 3x+ YoY from September 2024 to September 2025 | Similarweb, 2026-05-28 |
| Gemini referral trend | About 18% share, +237% YoY | Similarweb, 2026-05-28 |
| ChatGPT referral trend | Share slid from about 87% to the high-60s | Similarweb, 2026-05-28 |

---

## AI Crawler Checklist

| Check | Pass | Fail |
|-------|------|------|
| robots.txt allows AI crawlers | All major bots listed with `Allow: /` | Missing entries or `Disallow: /` |
| Cloudflare AI settings reviewed | AI crawlers explicitly allowed in dashboard | Default block left in place |
| llms.txt treated as optional | Not required for Google AI visibility | Treating a missing file as a blocker |
| Content in HTML source | `curl` returns full content | Empty divs, JS-only rendering |
| TTFB under 200ms | Measured from CDN edge | Over 600ms increases crawl or extraction risk |
| Schema in HTML source | Standard Article, Person, Organization JSON-LD in source HTML | Special AI-only schema or JS-injected schema |
| Sitemap.xml accessible | Valid XML, all blog URLs included | Missing or returns 404 |
| No Cloudflare challenge on bot UA | 200 status code | 403 or challenge page |
