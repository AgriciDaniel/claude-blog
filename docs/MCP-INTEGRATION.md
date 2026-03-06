# MCP Integration Guide

Optional Model Context Protocol (MCP) server integrations that extend
`claude-blog` with live data from SEO platforms, analytics services, and
performance monitoring tools.

**Important**: `claude-blog` works fully without any MCP servers. These
integrations are optional enhancements for teams that already use these
platforms.

---

## Overview

```
                    +---------------------------+
                    |      claude-blog          |
                    |    /blog commands          |
                    +------+----+----+----------+
                           |    |    |
              +------------+    |    +------------+
              |                 |                  |
              v                 v                  v
  +-----------------+  +----------------+  +------------------+
  | DataForSEO MCP  |  | Individual     |  | Custom MCP       |
  | (Recommended)   |  | MCP Servers    |  | Servers          |
  |                 |  |                |  |                  |
  | - SERP data     |  | - GSC          |  | - Analytics      |
  | - Keywords      |  | - Ahrefs       |  | - CMS APIs       |
  | - Backlinks     |  | - Semrush      |  | - Custom data    |
  | - On-page       |  | - PageSpeed    |  |                  |
  | - Domain data   |  |                |  |                  |
  | - Content       |  |                |  |                  |
  | - AI Optim.     |  |                |  |                  |
  +-----------------+  +----------------+  +------------------+
```

---

## DataForSEO MCP (Recommended)

**DataForSEO is the recommended MCP integration for `claude-blog`.** It provides
a single unified API covering SERP data, keyword research, backlink analysis,
on-page auditing, domain analytics, content analysis, and AI optimization —
replacing the need for separate Ahrefs, Semrush, GSC, and PageSpeed integrations.

### What It Enables

| Feature | Without DataForSEO MCP | With DataForSEO MCP |
|---------|----------------------|---------------------|
| SERP analysis | WebSearch only | Live Google/Bing/Yahoo SERP with all features (AI Overviews, PAA, etc.) |
| Keyword research | Not available | Search volume, CPC, competition, keyword difficulty, search intent |
| Backlink analysis | Not available | Referring domains, anchor text, spam score, new/lost links |
| On-page auditing | Manual review | Automated crawl, meta tags, Core Web Vitals, Lighthouse scores |
| Domain analytics | Not available | Technology detection, WHOIS data, competitor domain analysis |
| Content analysis | Quality scoring only | Sentiment analysis, keyword density, content quality scoring |
| AI optimization | GEO content audit | LLM mention tracking, ChatGPT scraping, AI visibility metrics |
| Competitor research | WebSearch only | Ranked keywords, traffic estimation, content gap analysis |

### Enhanced Workflows

**`/blog brief` with DataForSEO data**:

Content briefs include real keyword metrics from DataForSEO Labs:

```
Target Keywords (DataForSEO Labs)
- Primary: "kubernetes monitoring" — 2,400/mo, KD 45, Intent: informational
- Secondary: "k8s observability" — 890/mo, KD 32, Intent: informational
- Question: "how to monitor kubernetes" — 720/mo, KD 28

Competitor SERP Analysis
| Position | Domain              | Backlinks | Word Count |
|----------|---------------------|-----------|------------|
| #1       | competitor-a.com    | 142       | 3,200      |
| #2       | competitor-b.com    | 89        | 2,800      |
| #3       | competitor-c.com    | 67        | 4,100      |
```

**`/blog strategy` with DataForSEO data**:

Strategy documents gain competitive intelligence:

```
Domain Comparison (DataForSEO Labs)
| Domain           | Organic Traffic | Keywords | Backlinks | Rank |
|------------------|----------------|----------|-----------|------|
| competitor-a.com | 45,000/mo      | 2,340    | 12,400    | 52   |
| competitor-b.com | 28,000/mo      | 1,200    | 8,900     | 47   |
| your-site.com    | 3,200/mo       | 380      | 1,100     | 31   |

Content Gap: 234 keywords where competitors rank but you don't
```

**`/blog geo` with DataForSEO AI Optimization data**:

AI citation audits include LLM visibility metrics:

```
AI Visibility Report (DataForSEO AI Optimization)
| Metric              | Value | Notes                    |
|---------------------|-------|--------------------------|
| LLM mentions        | 12    | Across ChatGPT, Gemini  |
| AI Overview present | Yes   | For 3/5 target keywords  |
| Brand sentiment     | 0.72  | Positive                 |
| Citation URLs       | 4     | Directly cited pages     |
```

### Configuration

**One-command install (recommended):**

```bash
claude mcp add dataforseo \
  --env DATAFORSEO_USERNAME=your_username \
  --env DATAFORSEO_PASSWORD=your_password \
  -- npx -y dataforseo-mcp-server
```

**Or remote server (no local install needed):**

```bash
claude mcp add --transport http dataforseo https://mcp.dataforseo.com/http \
  --header "Authorization: Basic $(echo -n 'username:password' | base64)"
```

**Or add to `~/.claude/settings.json` manually:**

```json
{
  "mcpServers": {
    "dataforseo": {
      "command": "npx",
      "args": ["-y", "dataforseo-mcp-server"],
      "env": {
        "DATAFORSEO_USERNAME": "your-username",
        "DATAFORSEO_PASSWORD": "your-password",
        "ENABLED_MODULES": "SERP,KEYWORDS_DATA,ONPAGE,DATAFORSEO_LABS,BACKLINKS,DOMAIN_ANALYTICS,BUSINESS_DATA,CONTENT_ANALYSIS,AI_OPTIMIZATION"
      }
    }
  }
}
```

### Best Practices

1. **Store credentials in environment variables** (not in settings.json):
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   export DATAFORSEO_USERNAME="your-username"
   export DATAFORSEO_PASSWORD="your-password"
   ```

2. **Use field filtering** to reduce token usage (~75%):
   Create a field config JSON file and set `FIELD_CONFIG_PATH`:
   ```json
   {
     "env": {
       "FIELD_CONFIG_PATH": "/path/to/dataforseo-field-config.json"
     }
   }
   ```
   A comprehensive field config is available in the repository at
   `skills/seo/dataforseo-field-config.json` (if using the companion `/seo` skill).

3. **Enable only the modules you need** via `ENABLED_MODULES` to reduce
   available tools and improve response relevance.

### Available Modules

| Module | What It Provides |
|--------|-----------------|
| `SERP` | Live Google/Bing/Yahoo search results with all SERP features |
| `KEYWORDS_DATA` | Search volume, CPC, competition from Google Ads |
| `DATAFORSEO_LABS` | Keyword research, domain analysis, competitor data |
| `BACKLINKS` | Backlink profiles, referring domains, anchor text |
| `ONPAGE` | Website crawling, meta analysis, Core Web Vitals, Lighthouse |
| `DOMAIN_ANALYTICS` | Technology detection, WHOIS records |
| `BUSINESS_DATA` | Google Maps listings, reviews, business info |
| `CONTENT_ANALYSIS` | Brand citations, sentiment analysis, phrase trends |
| `AI_OPTIMIZATION` | LLM mention tracking, ChatGPT scraping, AI keyword discovery |

### Setup Requirements

1. [DataForSEO account](https://dataforseo.com/) with API credentials
2. Node.js 18+ (for `npx dataforseo-mcp-server`)
3. API username and password from the DataForSEO dashboard

---

## Alternative Individual MCP Integrations

The following individual MCP servers can be used instead of (or alongside)
DataForSEO for teams that already have accounts with these platforms.

## Google Search Console MCP

### What It Enables

| Feature | Without GSC MCP | With GSC MCP |
|---------|----------------|--------------|
| Content decay detection | Manual check | Automated: flags posts with 20%+ QoQ traffic decline |
| Keyword tracking | Not available | Live keyword rankings and CTR data |
| Query analysis | Not available | Actual search queries driving traffic |
| AI Overview impact | Not available | CTR changes when AI Overviews appear |
| Freshness scheduling | Time-based (30 days) | Data-driven (based on actual performance drops) |

### Enhanced Workflows

**`/blog audit` with GSC data**:

Instead of scoring posts only on content quality, the audit can incorporate
actual performance data:

```
Blog Audit: 47 Posts Analyzed

| Post              | Quality | Traffic (QoQ) | CTR    | Action          |
|-------------------|---------|---------------|--------|-----------------|
| ai-search-guide   | 85/100  | -35%          | 1.2%   | Content decay!  |
| kubernetes-setup   | 72/100  | +12%          | 3.1%   | Quality fixes   |
| react-patterns     | 91/100  | -5%           | 4.2%   | Monitor         |
```

**`/blog calendar` with GSC data**:

Editorial calendars can prioritize updates based on actual traffic decay
rather than arbitrary 30-day cycles:

```
Freshness Update Queue (Data-Driven)
| Post              | Last Updated | Traffic Change | Priority |
|-------------------|-------------|----------------|----------|
| ai-search-guide   | 45 days ago | -35% QoQ       | Critical |
| seo-strategy      | 60 days ago | -22% QoQ       | High     |
| blog-writing-tips  | 30 days ago | +5% QoQ        | Low      |
```

### Configuration

Add the GSC MCP server to your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "google-search-console": {
      "command": "npx",
      "args": ["-y", "@anthropic/gsc-mcp-server"],
      "env": {
        "GSC_CREDENTIALS_PATH": "/path/to/credentials.json"
      }
    }
  }
}
```

**Setup requirements**:
1. Google Cloud project with Search Console API enabled
2. OAuth credentials or service account key
3. Site verified in Google Search Console

---

## Ahrefs MCP

### What It Enables

| Feature | Without Ahrefs MCP | With Ahrefs MCP |
|---------|-------------------|-----------------|
| Backlink analysis | Not available | Referring domains, anchor text distribution |
| Keyword research | WebSearch only | Search volume, difficulty, SERP features |
| Competitor monitoring | Manual WebSearch | Automated gap analysis and tracking |
| Content gap analysis | Not available | Keywords competitors rank for that you don't |
| Domain Rating | Not available | Live DR tracking |

### Enhanced Workflows

**`/blog brief` with Ahrefs data**:

Content briefs can include precise keyword metrics:

```
Target Keywords
- Primary: "kubernetes monitoring" (2,400/mo, KD 45)
- Secondary: "k8s observability" (890/mo, KD 32)
- Question: "how to monitor kubernetes clusters" (720/mo, KD 28)

Competitor Content Gap
| Keyword                    | Competitor A | Competitor B | You  |
|---------------------------|-------------|-------------|------|
| kubernetes alerting setup  | #3          | #7          | --   |
| prometheus vs datadog      | #5          | #2          | --   |
| k8s monitoring best practices | #1       | #4          | #12  |
```

**`/blog strategy` with Ahrefs data**:

Strategy documents gain competitive intelligence with actual metrics:

```
Competitive Landscape
| Competitor      | DR  | Blog Posts | Avg Traffic/Post | Top Keywords |
|----------------|-----|-----------|-----------------|-------------|
| competitor-a.com | 72  | 340       | 2,100           | 890         |
| competitor-b.com | 65  | 180       | 1,400           | 520         |
| your-site.com    | 45  | 47        | 380             | 120         |

Opportunity: 234 keywords where competitors rank but you don't
```

### Configuration

```json
{
  "mcpServers": {
    "ahrefs": {
      "command": "npx",
      "args": ["-y", "@anthropic/ahrefs-mcp-server"],
      "env": {
        "AHREFS_API_KEY": "your-api-key"
      }
    }
  }
}
```

**Setup requirements**:
1. Ahrefs account with API access (Standard plan or higher)
2. API key from Ahrefs dashboard

---

## Semrush MCP

### What It Enables

| Feature | Without Semrush MCP | With Semrush MCP |
|---------|-------------------|-----------------|
| Keyword gap analysis | Not available | Side-by-side keyword overlap with competitors |
| Position tracking | Not available | Daily rank tracking for target keywords |
| Topic research | WebSearch only | Semrush Topic Research data |
| Content audit | Quality-only scoring | Quality + traffic + keyword data |

### Enhanced Workflows

**`/blog strategy` with Semrush data**:

Topic research backed by Semrush's keyword clustering:

```
Content Pillar: Kubernetes Monitoring
| Topic Cluster      | Keywords | Total Volume | Avg KD | Gap Score |
|-------------------|----------|-------------|--------|-----------|
| Setup & Config     | 34       | 12,400      | 38     | High      |
| Tools Comparison   | 22       | 8,900       | 52     | Medium    |
| Best Practices     | 18       | 6,200       | 41     | High      |
| Troubleshooting    | 45       | 15,100      | 29     | Low       |
```

### Configuration

```json
{
  "mcpServers": {
    "semrush": {
      "command": "npx",
      "args": ["-y", "@anthropic/semrush-mcp-server"],
      "env": {
        "SEMRUSH_API_KEY": "your-api-key"
      }
    }
  }
}
```

---

## PageSpeed Insights MCP

### What It Enables

| Feature | Without PSI MCP | With PSI MCP |
|---------|----------------|-------------|
| Core Web Vitals | Not available | LCP, FID, CLS, INP measurements |
| TTFB monitoring | Not available | Server response time (critical for AI crawlers) |
| Performance scoring | Not available | Lighthouse performance score |
| AI crawl readiness | Manual check | Automated TTFB < 200ms verification |

### Enhanced Workflows

**`/blog geo` with PageSpeed data**:

AI citation audits can include technical performance checks:

```
AI Crawler Readiness
| Metric   | Value  | Target  | Status |
|----------|--------|---------|--------|
| TTFB     | 145ms  | < 200ms | Pass   |
| LCP      | 2.1s   | < 2.5s  | Pass   |
| CLS      | 0.08   | < 0.1   | Pass   |
| JS-only? | No     | No      | Pass   |

Your pages are accessible to AI crawlers (GPTBot, ClaudeBot, PerplexityBot).
```

### Configuration

```json
{
  "mcpServers": {
    "pagespeed": {
      "command": "npx",
      "args": ["-y", "@anthropic/pagespeed-mcp-server"],
      "env": {
        "PAGESPEED_API_KEY": "your-google-api-key"
      }
    }
  }
}
```

**Setup requirements**:
1. Google Cloud project with PageSpeed Insights API enabled
2. API key from Google Cloud Console

---

## How to Configure MCP Servers

MCP servers are configured in your Claude Code settings file. The location
depends on your setup:

### Settings File Location

| Platform | Path |
|----------|------|
| Linux/macOS | `~/.claude/settings.json` |
| Windows | `%USERPROFILE%\.claude\settings.json` |

### Adding an MCP Server

Edit `settings.json` to add MCP servers under the `mcpServers` key:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": {
        "API_KEY": "your-key"
      }
    }
  }
}
```

### Verifying MCP Connection

After adding an MCP server:
1. Restart Claude Code
2. The MCP server should appear in available tools
3. Test with a simple query related to the server's function

### Environment Variables for API Keys

Never commit API keys to version control. Use environment variables:

```bash
# Add to ~/.bashrc or ~/.zshrc
export AHREFS_API_KEY="your-key"
export SEMRUSH_API_KEY="your-key"
export GSC_CREDENTIALS_PATH="/path/to/credentials.json"
export PAGESPEED_API_KEY="your-key"
```

Then reference them in settings:

```json
{
  "mcpServers": {
    "ahrefs": {
      "command": "npx",
      "args": ["-y", "@anthropic/ahrefs-mcp-server"],
      "env": {
        "AHREFS_API_KEY": "${AHREFS_API_KEY}"
      }
    }
  }
}
```

---

## Example Workflows

### Content Decay Detection (GSC + Blog Audit)

Combine Google Search Console data with `claude-blog`'s quality scoring to
identify posts that need immediate attention:

```
1. /blog audit content/blog/        # Quality scores for all posts
2. GSC MCP provides traffic data    # QoQ traffic changes
3. Combined report identifies:
   - High quality but declining traffic  --> needs freshness update
   - Low quality and declining traffic   --> needs full rewrite
   - Low quality but stable traffic      --> optimize for AI citations
4. /blog calendar                    # Auto-prioritized update schedule
```

### Competitor-Informed Content Strategy (Ahrefs + Strategy)

Use Ahrefs data to ground your content strategy in competitive intelligence:

```
1. /blog strategy "your-niche"      # Base strategy from analysis
2. Ahrefs MCP provides:
   - Competitor keyword rankings
   - Content gap keywords
   - Backlink opportunities
3. Strategy document includes:
   - Data-backed pillar topics
   - Specific keyword targets with volume/difficulty
   - Competitor weakness mapping
4. /blog calendar                    # Execution plan with keyword targets
```

### Performance-Optimized GEO Audit (PSI + GEO)

Validate both content quality and technical readiness for AI crawlers:

```
1. /blog geo content/blog/post.mdx  # Content-level GEO audit
2. PageSpeed MCP provides:
   - TTFB measurement (must be < 200ms)
   - JavaScript rendering check
   - Core Web Vitals scores
3. Combined report covers:
   - Content optimization (answer-first, freshness, FAQ)
   - Technical optimization (TTFB, SSR, robots.txt)
   - AI crawler accessibility verification
```

---

## Roadmap

| Integration | Status | Priority |
|------------|--------|----------|
| DataForSEO | **Available** | Recommended — covers SERP, keywords, backlinks, on-page, domain, content, AI optimization |
| Google Search Console | Planned | High — for first-party traffic/CTR data |
| Google Analytics (GA4) | Future | Low |
| WordPress REST API | Future | Low |
| Contentful / Sanity CMS | Future | Low |

Community contributions for MCP server implementations are welcome.
See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.
