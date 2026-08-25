---
name: blog-google
description: >
  Google API integration for blog performance: PageSpeed Insights, CrUX Core Web
  Vitals with 25-week history, Search Console performance, URL Inspection, Indexing
  API, GA4 organic traffic, NLP entity analysis for E-E-A-T, YouTube video search
  for embedding, and Google Ads Keyword Planner. Progressive feature availability
  based on credential tier (API key, OAuth/service account, GA4, Ads). Shares
  config with claude-seo at ~/.config/claude-seo/google-api.json. Use when user
  says "google data", "page speed", "core web vitals", "search console",
  "indexation", "GA4", "keyword research", "nlp entities", "blog performance",
  "youtube search", "google api setup".
user-invokable: true
argument-hint: "[setup|pagespeed|crux|crux-history|gsc|inspect|index|ga4|nlp|youtube|keywords|report|quotas] [url|property|query]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "2.1.1"
  category: blog
---

# Blog Google: Google API Data for Blog Performance

Direct access to Google's SEO APIs for blog performance analysis. Provides real
Chrome user metrics, indexation status, search performance, entity analysis, YouTube
video discovery, keyword volumes, and PDF/HTML performance reports.

All APIs are free at normal usage levels. Setup requires a Google Cloud project
with an API key and/or service account.

## Prerequisites

**Always check credentials before running any command:**
```bash
python3 skills/blog-google/scripts/run.py google_auth --check --json
```

**Config file:** `~/.config/claude-seo/google-api.json` (shared with claude-seo)
```json
{
  "api_key": "AIzaSy...",
  "oauth_client_path": "/path/to/client_secret.json",
  "default_property": "sc-domain:example.com",
  "ga4_property_id": "properties/123456789",
  "ads_developer_token": "...",
  "ads_customer_id": "123-456-7890",
  "ads_login_customer_id": "123-456-7890"
}
```

If missing, read `references/auth-setup.md` and walk the user through setup.

### Credential Tiers

| Tier | Detection | Available Commands |
|------|-----------|-------------------|
| **0** (API Key) | `api_key` present | `pagespeed`, `crux`, `crux-history`, `youtube`, `nlp` |
| **1** (OAuth/SA) | + OAuth token or service account | Tier 0 + `gsc`, `inspect`, `index` |
| **2** (Full) | + `ga4_property_id` configured | Tier 1 + `ga4` |
| **3** (Ads) | + `ads_developer_token` + `ads_customer_id` | Tier 2 + `keywords` |

Always communicate the detected tier before running commands.

## Quick Reference

| Command | What it does | Tier |
|---------|-------------|------|
| `/blog google setup` | Check/configure API credentials |: |
| `/blog google pagespeed <url>` | PSI Lighthouse + CrUX field data | 0 |
| `/blog google crux <url>` | CrUX field data only (p75 metrics) | 0 |
| `/blog google crux-history <url>` | 25-week CWV trend analysis | 0 |
| `/blog google youtube <query>` | YouTube video search (views, likes, duration) | 0 |
| `/blog google nlp <url-or-text>` | NLP entity extraction + sentiment | 0 |
| `/blog google gsc <property>` | Search Console: clicks, impressions, CTR, position | 1 |
| `/blog google inspect <url>` | URL Inspection: index status, canonical | 1 |
| `/blog google index <url>` | Submit URL to Indexing API | 1 |
| `/blog google ga4 [property-id]` | GA4 organic traffic report | 2 |
| `/blog google keywords <seed>` | Keyword ideas from Google Ads Keyword Planner | 3 |
| `/blog google report <type>` | PDF/HTML performance report |: |
| `/blog google quotas` | Show rate limits for all APIs |: |

---

## PageSpeed + CrUX

### `/blog google pagespeed <url>`

Combined Lighthouse lab data + CrUX field data for a published blog post.

**Script:** `python3 skills/blog-google/scripts/run.py pagespeed_check <url> --json`
**Reference:** `references/api-reference.md`

Output merges lab scores (point-in-time Lighthouse) with field data (28-day
Chrome user metrics). CrUX tries URL-level first, falls back to origin-level.

### `/blog google crux <url>`

CrUX field data only (no Lighthouse run). Faster.

**Script:** `python3 skills/blog-google/scripts/run.py pagespeed_check <url> --crux-only --json`

### `/blog google crux-history <url>`

25-week CrUX History trends. Shows whether CWV metrics are improving, stable, or degrading.

**Script:** `python3 skills/blog-google/scripts/run.py crux_history <url> --json`

---

## Search Console

### `/blog google gsc <property>`

Search Analytics: clicks, impressions, CTR, position for last 28 days.

**Script:** `python3 skills/blog-google/scripts/run.py gsc_query --property <property> --json`
**Default:** 28 days, dimensions=query,page, type=web, limit=1000.

Includes quick-win detection: queries at position 4-10 with high impressions.

The dedicated Search Console generative-AI reports are a gradual, subset
rollout in the Search Console UI. They have separate Search and Discover views;
the Search view covers AI Overviews and AI Mode. Do not promise clicks, queries,
or API retrieval from these dedicated views. Until Google documents an API,
report that capability as `SKIPPED` or unavailable and point the user to the UI.

Search Console platform properties for Instagram, TikTok, X, and YouTube are
also rolling out gradually. Their UI can expose Search and Discover performance,
but `/blog google gsc` must not claim to retrieve these platform reports through
the current API.

### `/blog google inspect <url>`

URL Inspection: real indexation status from Google.

**Script:** `python3 skills/blog-google/scripts/run.py gsc_inspect <url> --json`

Returns: verdict (PASS/FAIL), coverage state, robots.txt status, indexing state,
page fetch state, canonical selection, mobile usability, rich results.

After a canonicalization fix, Google may retain the URL in a duplicate cluster
for up to two weeks. If the implementation is now correct and the fix is within
that window, report `PENDING_REEVALUATION` rather than an immediate failure.
Search Console's Request Indexing feature is quota-limited; reserve it for
important URLs.

For batch inspection: `python3 skills/blog-google/scripts/run.py gsc_inspect --batch <file> --json`

---

## Indexing API

### `/blog google index <url>`

Notify Google of a URL update through the Indexing API.

**Script:** `python3 skills/blog-google/scripts/run.py indexing_notify <url> --json`
**Reference:** `references/api-reference.md`

The Indexing API is officially for JobPosting and BroadcastEvent/VideoObject pages.
Always inform the user of this restriction. Daily quota: 200 publish requests.
Do not present it as a general-purpose replacement for URL Inspection's Request
Indexing feature.

For batch: `python3 skills/blog-google/scripts/run.py indexing_notify --batch <file> --json`

---

## GA4 Traffic

### `/blog google ga4 [property-id]`

Organic traffic report: daily sessions, users, pageviews, bounce rate, engagement.

**Script:** `python3 skills/blog-google/scripts/run.py ga4_report --property <id> --json`
**Default:** 28 days, filtered to Organic Search channel group.

For top landing pages: `python3 skills/blog-google/scripts/run.py ga4_report --property <id> --report top-pages --json`

---

## YouTube (Video Discovery)

YouTube research can add useful, relevant media and distribution context. Any
third-party visibility correlation is observational, not a Google ranking or
citation requirement. Free, API key only. Used by blog-write and blog-rewrite
for video embedding.

### `/blog google youtube <query>`

Search YouTube for videos relevant to a blog topic.

**Script:** `python3 skills/blog-google/scripts/run.py youtube_search search "<query>" --json`
**Quota:** 100 units per search (10,000 units/day free).

Returns: title, channel, views, likes, duration, description, tags.

For video details + comments: `python3 skills/blog-google/scripts/run.py youtube_search video <video_id> --json`

---

## NLP Content Analysis

Google's entity and sentiment analysis can support topic and editorial review.
It does not expose ranking-system scores, and E-E-A-T is not a numeric Google
ranking factor.

### `/blog google nlp <url-or-text>`

Full NLP analysis: entities, sentiment, content classification.

**Script:** `python3 skills/blog-google/scripts/run.py nlp_analyze --url <url> --json`
**Free tier:** 5,000 units/month. Requires billing enabled on GCP project.

For entity extraction only: `python3 skills/blog-google/scripts/run.py nlp_analyze --url <url> --features entities --json`

---

## Keyword Research (Google Ads)

Gold-standard keyword volume data. Requires Google Ads account (Tier 3).

### `/blog google keywords <seed>`

Generate keyword ideas from seed terms for blog topic research.

**Script:** `python3 skills/blog-google/scripts/run.py keyword_planner ideas "<seed>" --json`

For volume lookup: `python3 skills/blog-google/scripts/run.py keyword_planner volume "<kw1>,<kw2>" --json`

---

## Reports

### `/blog google report <type>`

Generate a PDF/HTML report with charts and tables.

**Script:** `python3 skills/blog-google/scripts/run.py google_report --type <type> --data <json> --domain <domain> --format pdf`

| Type | Input | Output |
|------|-------|--------|
| `cwv-audit` | PSI + CrUX + CrUX History data | Core Web Vitals audit with gauges, timelines |
| `gsc-performance` | GSC query data | Search Console report with query tables |
| `indexation` | Batch inspection data | Indexation status with coverage donut |
| `full` | All data combined | Comprehensive Google SEO report |

**Note:** PDF generation requires system libraries: `sudo apt install libpango1.0-dev libcairo2-dev`.
Falls back to HTML if WeasyPrint is unavailable or PDF rendering fails.

---

## Rate Limits

| API | Per-Minute | Per-Day | Auth |
|-----|-----------|---------|------|
| PSI v5 | 240 QPM | 25,000 QPD | API Key |
| CrUX + History | 150 QPM (shared) | Unlimited | API Key |
| GSC Search Analytics | 1,200 QPM/site | 30M QPD | Service Account |
| GSC URL Inspection | 600 QPM | 2,000 QPD/site | Service Account |
| Indexing API | 380 RPM | 200 publish/day | Service Account |
| GA4 Data API | 10 concurrent (50 for 360) | 200K Core Tokens/day (2M for 360) | Service Account |
| YouTube Data |: | 10,000 units/day | API Key |
| NLP API |: | 5,000 units/month | API Key (billing) |

Read `references/rate-limits-quotas.md` for detailed quota management.

## Blog Workflow Integration

This skill is both user-invocable (`/blog google pagespeed`) and callable
internally by other blog sub-skills:

- **blog-seo-check**: Runs PSI + CrUX on published post URL for live CWV data
- **blog-rewrite**: NLP entity analysis to identify E-E-A-T entity gaps
- **blog-geo**: GSC performance data for real search appearance insights
- **blog-audit**: Batch CWV + indexation checks across all published blog URLs
- **blog-write / blog-rewrite**: YouTube search for video embedding

Falls back gracefully when credentials are not configured.

## Technical Notes

- INP replaced FID on March 12, 2024. Never reference FID.
- CLS values from CrUX are string-encoded (e.g., "0.05"). Scripts handle parsing.
- CrUX 404 = insufficient Chrome traffic, not an auth error.
- Search Analytics data has 2-3 day lag.
- Indexing API is officially for JobPosting/BroadcastEvent pages only.
- All Google APIs used are FREE at normal usage levels.
- Read `references/search-currentness.md` before diagnosing a named update,
  canonical change, Discover visibility, Google generative-AI reporting,
  platform properties, Preferred Sources, AMP, or crawler byte-limit issue.
- A named update's dates do not prove what caused an individual site's change.
  Wait one full week after rollout before comparing data, and separate Web,
  Image, Video, and News performance.
- Googlebot processes only the first 2MB of supported files and first 64MB of
  PDFs. Keep critical metadata and primary content before the cutoff.

## Error Handling

| Scenario | Action |
|----------|--------|
| No credentials configured | Run `/blog google setup`. List Tier 0 commands (API key only). |
| Service account lacks GSC access | Add `client_email` to GSC > Settings > Users > Add. |
| CrUX data unavailable (404) | Insufficient Chrome traffic. Use PSI lab data as fallback. |
| GA4 property not found | Find property ID in GA4 Admin > Property Details. |
| Indexing API quota exceeded | 200/day limit. Prioritize most important URLs. |
| Rate limit (429) | Wait and retry with exponential backoff. |
