---
name: blog-cannibalization
description: >
  Detect keyword cannibalization across blog posts by extracting primary keywords
  from titles and headings, clustering semantically similar targets, and flagging
  posts competing for the same search intent. Supports local-only mode (grep-based)
  and DataForSEO API mode (Page Intersection endpoint at ~$0.01/call). Outputs
  severity-scored report with merge or differentiate recommendations. Use when
  user says "cannibalization", "keyword overlap", "competing pages", "duplicate
  keywords", "cannibalize".
user-invokable: true
argument-hint: "[directory] [--api]"
license: MIT
---

# Blog Cannibalization - Keyword Overlap Detection

Detect when multiple blog posts compete for the same search keywords. Two modes:
local-only analysis (default) and DataForSEO API mode for SERP-level data.

## Two Modes

| Mode | Flag | Cost | Data Source |
|------|------|------|-------------|
| Local | (default) | Free | File content analysis via Grep/Read |
| API | `--api` | ~$0.01/call | DataForSEO Page Intersection + Ranked Keywords |

Local mode works without any API keys. API mode requires DataForSEO credentials
set as environment variables: `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD`.

## Local Mode Workflow

### Step 1: Scan Blog Files

Use Glob to find all content files in the target directory:
- Patterns: `**/*.md`, `**/*.mdx`, `**/*.html`
- Skip files in `node_modules/`, `.git/`, `drafts/`

### Step 2: Extract Primary Keywords

For each file, read and extract keyword signals from:
- **Title tag** or H1 heading (highest weight)
- **H2 headings** (medium weight)
- **First paragraph** (supporting signal)
- **Meta description** if present in frontmatter

Primary keyword extraction method:
1. Tokenize title, H1, H2s, meta description, and first paragraph into 1-gram,
   2-gram, and 3-gram phrases.
2. Normalize deterministically: lowercase, remove locale-aware stop words,
   lemmatize or stem consistently, preserve product names, and keep intent
   modifiers such as "best", "pricing", "vs", "review", "template", and year.
3. Score sections separately: title/H1 highest, meta description and H2s medium,
   first paragraph supporting.
4. Select the top-scoring 2-3 word phrase as the primary keyword and record
   secondary keywords from H2 headings.

### Step 3: Cluster by Similarity

Group posts into clusters using these matching rules (in priority order):

1. **Exact match** - identical primary keyword across 2+ posts
2. **Stem match** - same root word (e.g., "optimize" vs "optimization")
3. **Semantic overlap** - Assign explicit intent labels such as informational,
   commercial, transactional, comparison, or troubleshooting. Include confidence
   and a one-sentence rationale, or use an embeddings workflow with a documented
   threshold.
4. **Subset match** - one keyword contains another (e.g., "email marketing"
   vs "email marketing for startups")

### Step 4: Score and Flag

For each cluster with 2+ posts, assess severity and generate a recommendation.

### Step 5: Output Report

Display the results table and per-cluster recommendations.

## API Mode Workflow (DataForSEO)

Requires the `--api` flag and a dedicated local CLI wrapper that reads
`DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD` from the environment and emits
JSON. Do not use WebFetch for DataForSEO POST calls and never expose Basic auth
headers, login, password, or encoded credentials in prompts or reports. If no
wrapper exists in the project, report `SKIPPED: DataForSEO wrapper unavailable`
and run local mode.

### Endpoints Used

**Page Intersection** - find keywords where multiple URLs rank:
```
POST https://api.dataforseo.com/v3/dataforseo_labs/google/page_intersection/live

{
  "pages": {
    "1": "https://example.com/post-a",
    "2": "https://example.com/post-b"
  },
  "language_code": "en",
  "location_code": 2840
}
```
Cost: ~$0.01 per call. Returns overlapping keywords with position, volume, CPC.

**Ranked Keywords** - get all keywords a single URL ranks for:
```
POST https://api.dataforseo.com/v3/dataforseo_labs/google/ranked_keywords/live

{
  "target": "https://example.com/post-a",
  "language_code": "en",
  "location_code": 2840
}
```

The wrapper sends DataForSEO auth headers from environment variables and never
prints them.

### API Analysis Steps

1. Collect all published URLs from the user (or sitemap)
2. Run Ranked Keywords for each URL to build keyword profiles
3. Run Page Intersection for URL pairs that share keyword clusters
4. Calculate severity using the formula below
5. Output enriched report with search volume and position data

## Severity Scoring

Four severity levels based on overlap signals:

| Level | Criteria | Action Urgency |
|-------|----------|----------------|
| Critical | Same exact keyword, both pages in top 20 | Immediate |
| High | Same keyword cluster, one page outranks the other | This week |
| Medium | Related keywords with partial SERP overlap | This month |
| Low | Semantic similarity but different confirmed intents | Monitor |

### Severity Formula (API Mode)

```
severity_score = overlap_count x avg_search_volume x (1 / position_gap)
```

Where:
- `overlap_count` = number of shared ranking keywords
- `avg_search_volume` = mean monthly volume of shared keywords
- `position_gap` = absolute difference in average ranking position (min 1)

Higher score = more urgent cannibalization problem.

### Severity Heuristic (Local Mode)

Without SERP data, use a simplified scoring:
- **Critical**: Exact primary keyword match between posts
- **High**: Stem match on primary keyword, or 3+ shared H2 keywords
- **Medium**: Semantic overlap on primary keyword
- **Low**: Subset match only, or shared secondary keywords

## Output Format

### Summary Table

```
| Post A | Post B | Shared Keywords | Severity | Recommendation |
|--------|--------|-----------------|----------|----------------|
| /best-crm-tools | /top-crm-software | best crm, crm tools, crm software | Critical | MERGE |
| /email-tips | /email-marketing-guide | email marketing | High | DIFFERENTIATE |
| /seo-basics | /seo-for-beginners | seo basics, beginner seo | Critical | CANONICAL |
| /react-hooks | /react-state-mgmt | react, state | Low | NO ACTION |
```

### Per-Cluster Detail

For each flagged cluster, provide:
- Both post titles and URLs
- Full list of overlapping keywords (with volume if API mode)
- Which post is stronger (more comprehensive, better structured)
- Specific recommendation with rationale

## Recommendations

Four possible actions for each cannibalization cluster:

### MERGE
When both pages are thin or cover the same intent with similar depth.
- Combine the best content from both into one comprehensive post
- 301 redirect the weaker URL to the merged post
- Preserve all internal links pointing to either URL

### DIFFERENTIATE
When pages serve different intents but keyword targeting overlaps.
- Shift the primary keyword of the weaker post to a related long-tail
- Update the title, H1, and meta description to reflect the new focus
- Add internal links between the two posts to signal distinct topics

### CANONICAL
When one post is clearly the authority and the other is a lesser duplicate.
- Add `rel="canonical"` on the weaker page pointing to the authority
- Do not combine canonical and noindex casually. Use noindex only when removal
  from search is intended
- Link from the weaker page to the authority page

### NOINDEX
When a page should be removed from search results but still exist for users.
- Confirm the page has no meaningful unique search demand or business value
- Keep it crawlable until the noindex directive is observed
- Do not use as the default duplicate-content fix

### NO ACTION
When intent is genuinely different despite surface-level keyword similarity.
- Document the reasoning for future audits
- Monitor rankings quarterly for any position changes
- Re-evaluate if either post drops in rankings

## Error Handling

- **No blog files found**: If the directory contains no .md, .mdx, or .html files, report "No blog files found in [directory]" and suggest checking the path
- **DataForSEO credentials missing**: In API mode, if credentials are not configured, fall back to local mode automatically and notify the user
- **API rate limits**: DataForSEO has per-minute rate limits. If a 429 response is received, wait and retry once. If it persists, switch to local mode for remaining URLs
- **API request failures**: If DataForSEO returns an error, retry once within
  rate limits. If it still fails, switch to local mode for remaining URLs and
  report the failed endpoint without credentials
- **Single-post directory**: If only one blog post exists, report "Cannibalization analysis requires at least 2 posts" and exit gracefully
