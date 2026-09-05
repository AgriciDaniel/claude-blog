# Technical AI Visibility: Crawler Access & Rendering

## Contents

- [robots.txt Template for AI Crawlers](#robotstxt-template-for-ai-crawlers)
- [Cloudflare AI Crawl Control: Verify Current Settings](#cloudflare-ai-crawl-control-verify-current-settings)
- [Google Gen-AI Guidance](#google-gen-ai-guidance)
- [llms.txt Implementation](#llmstxt-implementation)
- [Rendering And Target-Crawler Verification](#rendering-and-target-crawler-verification)
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

## Cloudflare AI Crawl Control: Verify Current Settings

Cloudflare bot controls can affect some third-party crawlers, but defaults vary
by account, plan, configuration, crawler, and policy date. Do not treat a
Cloudflare setting, robots.txt, or client-side rendering as the universal cause
of missing visibility. Diagnose the intended crawler or Google surface using
current provider policy, the deployed configuration, response tests, and
available request logs.

### How to Fix

1. Log in to Cloudflare dashboard
2. Navigate to **Security > Bots > AI Crawlers**
3. Review the list of AI crawlers
4. Set the policy for each crawler according to the intended product surface
   and current provider documentation
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

Google Search Central says optimization for AI Overviews and AI Mode is normal
SEO:
https://developers.google.com/search/docs/fundamentals/ai-optimization-guide.
Google does not require special AI schema, llms.txt, tiny content chunks, or
AI-only rewrites. Use crawlable content, accurate metadata, clear source
attribution, helpful non-commodity material, and relevant images or video.
Creating a page for every possible fan-out query can violate scaled-content
abuse policy when done to manipulate Search.

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

## Rendering And Target-Crawler Verification

Do not assume a universal JavaScript capability across non-Google crawlers.
Check current crawler-specific documentation and test the deployed response.
For Google, JavaScript-generated primary content and schema are acceptable when
they reach the rendered DOM, match visible content, and pass validation.
Initial HTML, SSG, or SSR remain useful resilience and portability measures for
crawlers that do not execute JavaScript, not unconditional Google pass criteria.

### Rendering Strategy Ranking

| Strategy | AI Visibility | Performance | Recommendation |
|----------|--------------|-------------|----------------|
| **SSG** (Static Site Generation) | Best | Best | Preferred for blogs |
| **SSR** (Server-Side Rendering) | Excellent | Good | Good for dynamic content |
| **ISR** (Incremental Static Regeneration) | Excellent | Good | Good for large sites |
| **CSR** (Client-Side Rendering) | Crawler-dependent | Risky for non-JS crawlers | Avoid for primary content unless target-crawler rendering is verified |

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

Vercel reported no evidence of JavaScript execution in its analyzed GPTBot
fetches. Treat client-rendered-only content as unavailable to GPTBot unless
current, crawler-specific testing proves otherwise. This does not make
JavaScript-generated JSON-LD invalid for Google: Google can use it when it is in
the rendered DOM, matches visible content, and passes validation.

### Exception: Agentic Tools

Standard AI crawlers generally do not execute JavaScript. However, **agentic tools** are different:
- **OpenAI agentic browsing surfaces**: Full JS rendering may be available depending on product mode.
- **Google-Agent / Project Mariner** (Google, 2026): Operates through Chrome with full rendering.

These are user-directed agents, not automated crawlers. They can see JS-rendered content,
but that does not show how a product selects sources or remove the need to test
the documented crawlers relevant to the site's goals.

---

## Passage-Level Extractability

Crawler access gets a page into the candidate set. Organize material with
descriptive headings and coherent paragraphs for readers, but do not force
120-180-word passages, fixed-size answer capsules, question headings, or any
other "chunking" quota. Google explicitly says there is no ideal page length and
no requirement to break content into tiny pieces for generative AI Search.

When direct evidence, dates, examples, or first-hand findings are relevant, make
them clear and source them. Never add first-person experience markers unless the
article has a real method and evidence behind the claim.

---

## Performance Requirements

AI retrieval systems have practical latency budgets. Slow sites may reduce crawl,
fetch, and extraction reliability before content quality is evaluated.

**Note:** The thresholds below are industry best practices and observations from SEO tooling
(Discovered Labs, Prerender.io, Kevin Indig). They are NOT officially published specifications
from OpenAI, Anthropic, or Perplexity. Treat as directional targets, not guaranteed cutoffs.

### Directional Diagnostics

| Metric | Diagnostic use | Action |
|--------|----------------|--------|
| TTFB (Time to First Byte) | Compare by region and user agent | Investigate sustained regressions against the site's tested budget |
| Full page load (HTML) | Measure fetch reliability and variance | Investigate repeated timeouts or incomplete responses |
| Response size (HTML) | Check whether important material is fetched | Reduce bloat when testing shows truncation or extraction loss |

### Optimization Priorities

1. **Evaluate a CDN**: Use edge delivery when measurements show it improves reliability
2. **Enable compression**: gzip or Brotli for all text responses
3. **Minimize HTML bloat**: Remove unused CSS/JS from HTML response
4. **Cache intentionally**: Set cache headers that fit update frequency and correctness
5. **Prefer pre-rendering**: Use SSG or SSR for primary content when broad
   crawler portability matters

---

## Testing AI Crawler Visibility

### Quick Test: Inspect the Initial Response

```bash
# Basic: view initial response HTML; subsequent rendering varies by crawler
curl -s https://yourdomain.com/blog/your-post | head -200

# Check if main content is in HTML source
curl -s https://yourdomain.com/blog/your-post | grep -c "<article"

# Check for JS-only rendering indicators
curl -s https://yourdomain.com/blog/your-post | grep -c "id=\"__next\""
curl -s https://yourdomain.com/blog/your-post | grep -c "id=\"root\""
curl -s https://yourdomain.com/blog/your-post | grep -c "id=\"app\""

# Empty shells indicate client rendering; verify whether each target crawler
# can render and access the primary content before classifying a failure.
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

### Googlebot Byte-Limit Check

For Google Search, inspect the uncompressed response as well as the rendered
page. Googlebot processes the first 2MB of a supported file and the first 64MB
of a PDF; content after the cutoff is ignored. Keep the title, meta directives,
canonical, essential structured data, and primary article content before the
cutoff. Warn when inline base64 images, CSS, JavaScript, or navigation bloat
could push critical content beyond it. Treat this as crawl eligibility, not a
ranking factor.

### Navigation Behavior Check

Flag back-button hijacking only after demonstrating that a user cannot return
to the previous page normally, is sent to a deceptive page, or receives
unsolicited recommendations or ads through manipulated history. Legitimate
History API use is not a violation by itself.

For a section intended as a Google "Read more" deep link, keep its content
immediately visible and its heading or anchor stable. Do not remove the hash or
force the scroll position on page load. Other disclosure widgets can still be
used when they are not the intended deep-link target.

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

## AI Crawler and Referral Measurement Context

Infrastructure and analytics vendors report changing crawler volumes and
referral mixes, often from small baselines and different site samples. Use
first-party logs and analytics to measure the site's own traffic by documented
user agent, referrer, date, and response status.

Crawler volume, referral growth, and source-share observations do not establish
a ranking factor, readiness score, citation probability, or causal visibility
benefit. Blocking a crawler can be an intentional policy choice; document the
tradeoff against the site's stated goals.

---

## AI Crawler Checklist

| Check | Pass | Fail |
|-------|------|------|
| robots.txt matches declared crawler policy | Documented crawlers are allowed or blocked as intended | Policy and file behavior disagree |
| Cloudflare AI settings reviewed | Dashboard setting matches the declared policy | Setting was not reviewed or contradicts policy |
| llms.txt treated as optional | Not required for Google AI visibility | Treating a missing file as a blocker |
| Primary content accessible to the target crawler | Verified access; useful initial HTML improves portability | Testing shows the declared crawler cannot retrieve or render the primary content |
| Server response reliability | Measured from relevant regions and user agents | Timeouts or repeated failures block retrieval |
| Schema available to the target crawler | Source/server-rendered for non-JS crawlers; source or rendered DOM for Google | Special AI-only schema or absent from the rendered DOM |
| Googlebot byte cutoff checked | Critical metadata and content occur within first 2MB | Content after first 2MB produces a crawl warning, not an automatic publication failure |
| Browser history behaves normally | Back returns to the previous page | Deceptive entries, forced redirects, or unsolicited pages obstruct Back |
| Sitemap.xml accessible | Valid XML, all blog URLs included | Missing or returns 404 |
| No Cloudflare challenge on bot UA | 200 status code | 403 or challenge page |
