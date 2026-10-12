# Blog Google - Authentication Setup

## Overview

Four credential tiers serve different API combinations:

| Tier | Credentials | APIs Unlocked |
|------|------------|---------------|
| **0** | API Key only | PageSpeed Insights, CrUX, CrUX History, YouTube Data, Cloud Natural Language |
| **1** | + Service Account | + Search Console (and the Indexing API for eligible job or livestream pages only) |
| **2** | + GA4 property ID | + GA4 Data API |
| **3** | + Google Ads tokens | + Keyword Planner |

## Step 1: Create a Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click **Select a project** > **New Project**
3. Name it (e.g., "Claude Blog") and note the project ID
4. Select the project after creation

## Step 2: Enable APIs

Navigate to **APIs & Services > Library** and enable:

| API | Required For |
|-----|-------------|
| PageSpeed Insights API | Lighthouse lab data, CWV scores |
| Chrome UX Report API | CrUX field data + History |
| Google Search Console API | Search Analytics, URL Inspection, Sitemaps |
| Web Search Indexing API | Indexing API v3 (job and livestream pages only; not blog posts). Leave it disabled for a blog |
| Google Analytics Data API | GA4 organic traffic analysis |
| YouTube Data API v3 | Video research for AI-search SEO visibility |
| Cloud Natural Language API | Entity salience, sentiment, classification |

## Step 3: Create an API Key (Tier 0)

1. **APIs & Services > Credentials > Create Credentials > API key**
2. Click **Restrict key** > under **API restrictions**, select the APIs above
3. Copy the key (starts with `AIzaSy...`)

## Step 4: Create a Service Account (Tier 1)

1. **IAM & Admin > Service Accounts > Create Service Account**
2. Name: `claude-blog` (or similar)
3. Skip optional permissions steps
4. Click on the created service account > **Keys > Add Key > Create new key > JSON**
5. Download and store securely (e.g., `~/.config/claude-seo/service_account.json`)

### Grant Search Console Access

1. Go to [Google Search Console](https://search.google.com/search-console)
2. Select your property > **Settings > Users and permissions > Add user**
3. Paste the service account `client_email` from the JSON file
4. Set the LOWEST permission that works. Do not grant **Owner**.
   - **Restricted** is enough to read Performance (Search Analytics) data.
   - **Full** is needed for URL Inspection beyond fetch-only, sitemap
     submission, and the other tools Google lists for Full users.
   - Try Restricted first and raise to Full only if the call returns 403.

   Why: Google's Help Center describes Owner as full control (it can add and
   remove users and change settings), Full as view rights plus some actions,
   and Restricted as simple view rights
   (https://support.google.com/webmasters/answer/7687615, read 2026-10-12).
   Google's Search Analytics and URL Inspection API pages name only OAuth
   scopes (`webmasters.readonly` is enough to read) and do not state a
   minimum property role, so the exact minimum for URL Inspection is
   unverified: confirm it by testing.

   The Owner role is required only by the Indexing API
   ("Grant owner status to your service account",
   https://developers.google.com/search/apis/indexing-api/v3/prereqs). That
   API serves only JobPosting and BroadcastEvent-in-VideoObject pages, so a
   blog never needs it. Do not grant Owner for blog work.

## Step 5: Set Up OAuth for Interactive Flows

1. **APIs & Services > Credentials > Create Credentials > OAuth client ID**
2. Application type: **Desktop app**
3. Download the `client_secret_*.json` file
4. Store at `~/.config/claude-seo/oauth_client.json`

OAuth is needed for Keyword Planner and any user-consent flows.

## Step 6: GA4 Property ID (Tier 2)

1. Go to [Google Analytics](https://analytics.google.com)
2. **Admin > Property Access Management > Add users** (+ icon)
3. Paste the service account `client_email`, set role: **Viewer**
4. Note the numeric property ID from **Admin > Property Details** (e.g., `123456789`)

## Step 7: Google Ads Credentials (Tier 3)

1. Create a Google Ads Manager Account at ads.google.com
2. Apply for a Developer Token at Google Ads API Center
3. Note: Without active ad spend, Keyword Planner returns bucketed ranges ("1K-10K")

## Config File

Config is shared with claude-seo at `~/.config/claude-seo/google-api.json`:

```json
{
  "service_account_path": "~/.config/claude-seo/service_account.json",
  "api_key": "YOUR_GOOGLE_API_KEY",
  "oauth_client_path": "~/.config/claude-seo/oauth_client.json",
  "default_property": "sc-domain:example.com",
  "ga4_property_id": "properties/123456789",
  "ads_developer_token": "YOUR_DEV_TOKEN",
  "ads_customer_id": "123-456-7890",
  "ads_login_customer_id": "123-456-7890"
}
```

Protect the config and downloaded credential files:

```bash
chmod 700 ~/.config/claude-seo
chmod 600 ~/.config/claude-seo/google-api.json
chmod 600 ~/.config/claude-seo/service_account.json ~/.config/claude-seo/oauth_client.json
```

### GSC Property URL Formats

| Format | Example | When to Use |
|--------|---------|-------------|
| Domain property | `sc-domain:example.com` | All URLs on the domain (recommended) |
| URL-prefix property | `https://example.com/` | Only that specific prefix |

## Environment Variable Fallbacks

| Variable | Purpose |
|----------|---------|
| `GOOGLE_API_KEY` | API key for PSI/CrUX/YouTube/NLP |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON |
| `GOOGLE_OAUTH_CLIENT_PATH` | Path to OAuth client JSON |
| `GA4_PROPERTY_ID` | GA4 property (e.g., `properties/123456789`) |
| `GSC_PROPERTY` | Default GSC property (e.g., `sc-domain:example.com`) |
| `GOOGLE_ADS_DEVELOPER_TOKEN` | Google Ads developer token |
| `GOOGLE_ADS_CUSTOMER_ID` | Google Ads customer ID |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | Optional manager account login customer ID |

## Verify Setup

Resolve the installed skill directory first and reject it unless absolute.
Never run a relative scripts path from the current project:

```bash
BLOG_SKILLS_DIR="${CLAUDE_BLOG_SKILLS_DIR:-${CLAUDE_SKILL_DIR}/..}"
case "$BLOG_SKILLS_DIR" in /*) ;; *) echo "ERROR: skills dir must be absolute" >&2; exit 1 ;; esac
python3 "$BLOG_SKILLS_DIR/blog-google/scripts/run.py" google_auth --check --json
```

If the managed environment is missing, the runner reports setup required.
Create it with the explicit setup script (with the user's yes), not with an
ad hoc package install:

```bash
python3 "$BLOG_SKILLS_DIR/blog-google/scripts/setup_environment.py"
```

## Quick Troubleshooting

| Error | Fix |
|-------|-----|
| `403 Forbidden` on GSC | Service account email not added to property, or its role is too low (try Full; do not jump to Owner) |
| `403 Forbidden` on GA4 | Service account not added as Viewer in GA4 property |
| `404 Not Found` on GSC | Wrong property URL format: use `sc-domain:` or include trailing slash |
| `404 Not Found` on CrUX | Site has insufficient Chrome traffic (not a credentials issue) |
| `429 Rate Limit` | Wait and retry with backoff. See rate-limits-quotas.md |
| `API not enabled` | Enable the specific API in GCP Console > APIs & Services > Library |
| `Billing required` | NLP API requires billing enabled (free tier still applies) |
