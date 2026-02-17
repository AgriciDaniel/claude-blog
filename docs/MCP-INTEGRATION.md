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
  | Google Search   |  | Ahrefs MCP     |  | PageSpeed        |
  | Console MCP     |  | Server         |  | Insights MCP     |
  |                 |  |                |  |                  |
  | - Content decay |  | - Backlinks    |  | - Core Web       |
  | - Keywords      |  | - Keywords     |  |   Vitals         |
  | - Click data    |  | - Competitors  |  | - TTFB           |
  +-----------------+  +----------------+  +------------------+

              +------------+    +------------+
              |                              |
              v                              v
  +-----------------+              +-----------------+
  | Semrush MCP     |              | Custom MCP      |
  | Server          |              | Servers         |
  |                 |              |                 |
  | - Keyword gaps  |              | - Analytics     |
  | - Positions     |              | - CMS APIs      |
  | - Competitors   |              | - Custom data   |
  +-----------------+              +-----------------+
```

---

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

MCP integrations are planned for Phase 3 of the `claude-blog` roadmap.
Current priorities:

| Integration | Status | Priority |
|------------|--------|----------|
| Google Search Console | Planned | High |
| Ahrefs | Planned | High |
| Semrush | Planned | Medium |
| PageSpeed Insights | Planned | Medium |
| Google Analytics (GA4) | Future | Low |
| WordPress REST API | Future | Low |
| Contentful / Sanity CMS | Future | Low |

Community contributions for MCP server implementations are welcome.
See the [repository](https://github.com/AgriciDaniel/claude-blog) for
contribution guidelines.
