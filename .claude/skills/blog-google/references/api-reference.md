# Blog Google - API Reference

Consolidated reference for all Google APIs used by the blog-google skill.

---

## PageSpeed Insights v5

**Endpoint:** `GET https://pagespeedonline.googleapis.com/pagespeedonline/v5/runPagespeed` (canonical)
Legacy hostname also works: `https://www.googleapis.com/pagespeedonline/v5/runPagespeed`

| Param | Type | Description |
|-------|------|-------------|
| `url` | string | Required. URL to analyze |
| `category` | string | `ACCESSIBILITY`, `BEST_PRACTICES`, `PERFORMANCE`, `SEO` (can specify multiple) |
| `strategy` | string | `DESKTOP` or `MOBILE` (default) |
| `key` | string | API key (optional but recommended) |

Response contains `loadingExperience` (URL-level CrUX), `originLoadingExperience` (origin CrUX), and `lighthouseResult` with category scores and audit details.

**Note:** Google has signaled intent to remove CrUX from PSI, but as of April 2026 CrUX field
data (`loadingExperience`, `originLoadingExperience`) is still returned in PSI responses. The
standalone CrUX API is the recommended long-term solution for field data; use PSI primarily
for Lighthouse lab scores.

---

## CrUX API (Daily)

**Endpoint:** `POST https://chromeuxreport.googleapis.com/v1/records:queryRecord?key={API_KEY}`

```json
{
  "origin": "https://example.com",
  "formFactor": "PHONE",
  "metrics": ["largest_contentful_paint", "interaction_to_next_paint", "cumulative_layout_shift"]
}
```

- `origin` and `url` are mutually exclusive. Use `origin` for site-wide, `url` for a specific page.
- `formFactor`: `DESKTOP`, `PHONE`, `TABLET` (omit for all).
- Each metric returns `histogram` (density buckets), `percentiles.p75`, and `category`.
- **CLS p75 is a string** (e.g., `"0.05"` not `0.05`). Always parse as float.
- 404 = insufficient Chrome traffic (not an auth error).
- Updated daily on a best-effort basis with ~2-day lag. No guaranteed update time; timezone is PST.

---

## CrUX History API (Weekly)

**Endpoint:** `POST https://chromeuxreport.googleapis.com/v1/records:queryHistoryRecord?key={API_KEY}`

Same request format as CrUX API. Returns up to **40 weekly collection periods** (~10 months)
as timeseries arrays (`p75s[]`, `densities[]`). Default is 25; configurable via
`collectionPeriodCount` parameter (range: 1-40). Use `crux_history.py --periods N`.

- Updated **Mondays** ~04:00 UTC.
- Each period = 28-day rolling average ending on a Sunday.
- Watch for `"NaN"` strings in densities and `null` in percentiles for ineligible periods.

---

## Core Web Vitals Thresholds

Current as of March 2026. INP replaced FID on March 12, 2024.

**Core Web Vitals (the 3 official CWV):**

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** | ≤ 2,500ms | 2,500-4,000ms | > 4,000ms |
| **INP** | ≤ 200ms | 200-500ms | > 500ms |
| **CLS** | ≤ 0.1 | 0.1-0.25 | > 0.25 |

**Diagnostic metrics (not CWV - informational only):**

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **FCP** | ≤ 1,800ms | 1,800-3,000ms | > 3,000ms |
| **TTFB** | ≤ 800ms | 800-1,800ms | > 1,800ms |

---

## GSC Search Analytics

**Endpoint:** `POST https://www.googleapis.com/webmasters/v3/sites/{siteUrl}/searchAnalytics/query`

### Request Body

| Field | Type | Description |
|-------|------|-------------|
| `startDate` | string | Required. YYYY-MM-DD |
| `endDate` | string | Required. YYYY-MM-DD |
| `dimensions` | string[] | `query`, `page`, `country`, `device`, `date`, `searchAppearance` |
| `type` | string | `web`, `image`, `video`, `news`, `discover`, `googleNews` |
| `dimensionFilterGroups` | object[] | Filter groups with `dimension`, `operator`, `expression` |
| `rowLimit` | int | 1-25000 (default: 1000) |
| `startRow` | int | Pagination offset (default: 0) |
| `dataState` | string | `final` (default), `all`, `hourly_all` (April 2025, requires `hour` dimension) |

### Filter Operators
`contains`, `equals`, `notContains`, `notEquals`, `includingRegex`, `excludingRegex`

### Response Fields
Each row: `keys[]`, `clicks`, `impressions`, `ctr`, `position`.

- Data lag by `dataState`: `final` = ~2-3 days; `all` = shorter lag; `hourly_all` = few hours (April 2025). Retention: ~16 months. Use `gsc_query.py --data-state hourly_all --dimensions date,hour,...`.
- Country codes are **ISO 3166-1 alpha-3** (e.g., `USA`, `GBR`).
- The dedicated generative-AI Search and Discover reports are a gradual
  Search Console UI rollout. They are not an extra `type` or
  `searchAppearance` value documented for this endpoint. Do not synthesize
  clicks or queries for those reports or claim this API isolates AI Overviews
  and AI Mode.
- Instagram, TikTok, X, and YouTube platform properties also have a gradual UI
  rollout. Do not promise that this endpoint supports their dedicated reports
  until Google publishes API documentation.

---

## GSC URL Inspection

**Endpoint:** `POST https://searchconsole.googleapis.com/v1/urlInspection/index:inspect`

```json
{
  "inspectionUrl": "https://example.com/blog/post",
  "siteUrl": "sc-domain:example.com",
  "languageCode": "en"
}
```

### Key Response Fields (`indexStatusResult`)

| Field | Values |
|-------|--------|
| `verdict` | `PASS`, `FAIL`, `NEUTRAL`, `PARTIAL` |
| `coverageState` | Human-readable coverage description |
| `robotsTxtState` | `ALLOWED`, `DISALLOWED` |
| `indexingState` | `INDEXING_ALLOWED`, `BLOCKED_BY_META_TAG`, `BLOCKED_BY_HTTP_HEADER` |
| `pageFetchState` | `SUCCESSFUL`, `SOFT_404`, `BLOCKED_ROBOTS_TXT`, `NOT_FOUND`, `SERVER_ERROR` |
| `lastCrawlTime` | ISO 8601 timestamp |
| `googleCanonical` | URL Google selected as canonical |
| `crawledAs` | `DESKTOP`, `MOBILE` |

---

## GA4 Data API v1beta

**Base URL:** `https://analyticsdata.googleapis.com/v1beta`

### runReport Overview

Key fields: `property`, `dimensions[]`, `metrics[]`, `dateRanges[]`, `dimensionFilter`, `orderBys[]`, `limit`.

### Blog-Relevant Dimensions
`date`, `landingPage`, `pagePath`, `pageTitle`, `sessionDefaultChannelGroup`, `sessionSource`, `sessionMedium`, `country`, `deviceCategory`

### Blog-Relevant Metrics
`sessions`, `totalUsers`, `screenPageViews`, `bounceRate`, `averageSessionDuration`, `engagementRate`, `keyEvents`

### Organic Traffic Filter
```json
{
  "filter": {
    "fieldName": "sessionDefaultChannelGroup",
    "stringFilter": { "matchType": "EXACT", "value": "Organic Search" }
  }
}
```

Uses token-based quotas (200,000 Core Tokens/day per standard property; 2M for 360).
Set `returnPropertyQuota: true` to monitor consumption.

---

## Cloud Natural Language API

**Endpoint:** `POST https://language.googleapis.com/v2/documents:annotateText?key={API_KEY}`

| Feature | What It Does | Blog Use |
|---------|-------------|----------|
| `extractEntities` | People, orgs, places with salience scores | Topic coverage depth, entity optimization |
| `extractDocumentSentiment` | Document + sentence-level sentiment | Content tone assessment |
| `classifyText` | Map content to 700+ Google categories | Topic relevance verification |
| `moderateText` | Detect harmful/sensitive content categories | Content safety screening |

Each entity includes `name`, `type`, `salience` (0-1), `sentiment`, and `metadata` (Wikipedia URL, Knowledge Graph MID).

**Pricing:** 5,000 free units/month for entities and sentiment. Requires billing enabled.

---

## YouTube Data API v3

YouTube results can support relevant media research and cross-platform
distribution. Third-party visibility correlations are observational and do not
establish a Google ranking or citation requirement.

| Method | Quota Cost | Description |
|--------|-----------|-------------|
| `search.list` | 100 units | Search videos matching a query |
| `videos.list` | 1 unit | Video details, statistics, tags |
| `channels.list` | 1 unit | Channel info, subscriber count |

Default quota: **10,000 units/day** (free). API key only, no OAuth needed.

---

## Keyword Planner (Google Ads API)

Gold-standard source for keyword search volume. Methods: **GenerateKeywordIdeas** (suggestions
from seeds), **GenerateKeywordHistoricalMetrics** (volume for specific keywords), and
**GenerateKeywordForecastMetrics** (future projections). Returns volume, competition, CPC bids.

**Current API version guidance:** Google Ads API release notes list v24.2 dated 2026-06-24. Check the official release notes before changing versioned client or REST paths:
https://developers.google.com/google-ads/api/docs/release-notes

- Without active ad spend, volumes are **bucketed ranges** ("1K-10K") not exact numbers
- `competition` measures **advertiser competition**, not organic difficulty
- Requires: Google Ads Manager Account + Developer Token + OAuth credentials
