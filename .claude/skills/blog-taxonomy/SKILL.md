---
name: blog-taxonomy
description: >
  Extract, suggest, and sync tags and categories for blog posts across all major
  CMS platforms. Supports WordPress REST API, Shopify GraphQL, Ghost Content API,
  Strapi REST/GraphQL, and Sanity GROQ. Generates tag suggestions from content
  analysis (keyword frequency, heading extraction, semantic grouping), enforces
  minimum post-count thresholds to prevent thin tag archives, and syncs taxonomy
  via authenticated API calls. Use when user says "tags", "categories", "taxonomy",
  "tag suggestions", "sync tags", "WordPress tags", "Shopify tags".
user-invokable: true
argument-hint: "[suggest|sync|audit] [file-or-cms]"
license: MIT
---

# Blog Taxonomy

Manage tags, categories, and topic clusters across CMS platforms.

## Commands

| Command | Purpose |
|---------|---------|
| `/blog taxonomy suggest <file>` | Extract candidate tags and categories from content |
| `/blog taxonomy sync <cms>` | Push taxonomy to CMS via authenticated API |
| `/blog taxonomy audit [directory]` | Check for thin tags, orphan tags, taxonomy bloat |

## Tag Suggestion Workflow

### Step 1: Parse Content Structure

Read the target file and extract:
- All H2 and H3 headings (primary topic signals)
- Bold and italic phrases (emphasis signals)
- Existing frontmatter tags/categories if present

### Step 2: Frequency Analysis

Scan the body text for high-frequency phrases:
- 1-word terms: minimum 4 occurrences (excluding stop words)
- 2-word phrases: minimum 3 occurrences
- 3-word phrases: minimum 2 occurrences

Exclude common non-tag words: articles, prepositions, conjunctions, pronouns.

### Step 3: Semantic Grouping

Group related candidates into clusters:
- Merge singular/plural variants (keep the more common form)
- Merge hyphenated and non-hyphenated forms
- Group synonyms under the highest-frequency term

### Step 4: Deduplicate and Rank

- Fuzzy match on slugified names (Levenshtein distance <= 2)
- Do not auto-merge short slugs under 5 characters using Levenshtein alone; require token overlap or manual review
- Score each candidate: `(frequency * 2) + (heading_presence * 5) + (emphasis * 1)`
- Return top 5-10 ranked suggestions

### Output Format

```
## Tag Suggestions: [Post Title]

| Rank | Tag | Score | Source |
|------|-----|-------|--------|
| 1 | content-marketing | 18 | H2 + 6 mentions |
| 2 | seo-strategy | 14 | H3 + 4 mentions |
| 3 | keyword-research | 11 | 5 mentions + bold |

### Suggested Categories
- Primary: [best-fit category]
- Secondary: [optional second category]
```

## CMS Adapters

### Adapter Overview

| CMS | API Type | Auth Method | Tags Model |
|-----|----------|-------------|------------|
| WordPress | REST | Application Passwords (base64) | First-class entities with IDs |
| Shopify | GraphQL (Admin API) | Admin API access token | String array on Article |
| Ghost | REST (Admin API) | API key with JWT signing | First-class entities |
| Strapi | REST or GraphQL | API token (Bearer) | User-defined content type |
| Sanity | GROQ / Mutations | Project token (Bearer) | Document type |

### WordPress Adapter

**List tags**:
```
GET {CMS_URL}/wp-json/wp/v2/tags?per_page=100&search={keyword}
Authorization: Basic {base64(username:app_password)}
```

**Create tag**:
```
POST {CMS_URL}/wp-json/wp/v2/tags
Body: {"name": "Tag Name", "slug": "tag-name", "description": "Optional"}
```

**List categories** (hierarchical, supports parent field):
```
GET {CMS_URL}/wp-json/wp/v2/categories?per_page=100
```

**Create category**:
```
POST {CMS_URL}/wp-json/wp/v2/categories
Body: {"name": "Category", "slug": "category", "parent": 0}
```

**Assign tags to post**:
```
POST {CMS_URL}/wp-json/wp/v2/posts/{id}
Body: {"tags": [1, 2, 3], "categories": [4]}
```

Pagination: follow `X-WP-TotalPages` header for full listing.

### Shopify Adapter

Tags on Shopify are string arrays on the Article object, not first-class entities.

**Update article tags** (GraphQL Admin API):
```graphql
mutation {
  articleUpdate(id: "gid://shopify/Article/123", article: {
    tags: ["tag-one", "tag-two", "tag-three"]
  }) {
    article { id tags }
    userErrors { field message }
  }
}
```

**List all tags in use** (GraphQL):
```graphql
{
  articles(first: 250, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    edges {
      node { id title tags }
    }
  }
}
```

Auth header: `X-Shopify-Access-Token: {token}`

Pagination: loop while `pageInfo.hasNextPage` is true, passing `endCursor` as
the next `$cursor`.

Note: REST API marked legacy Oct 2024. GraphQL required for new apps since Apr 2025.

### Ghost Adapter

**List tags**:
```
GET {CMS_URL}/ghost/api/admin/tags/?limit=all
Authorization: Ghost {jwt_token}
```

**Create tag**:
```
POST {CMS_URL}/ghost/api/admin/tags/
Body: {"tags": [{"name": "Tag Name", "slug": "tag-name"}]}
```

JWT generation: sign with admin API key (id:secret format), iat = now, exp = 5 min,
audience = `/admin/`.

### Strapi Adapter

Endpoint auto-generated from content types. Typical setup:

```
GET {CMS_URL}/api/tags?pagination[pageSize]=100
POST {CMS_URL}/api/tags
Body: {"data": {"name": "Tag Name", "slug": "tag-name"}}
Authorization: Bearer {api_token}
```

Pagination: increment `pagination[page]` until all pages are exhausted.

Strapi v4 responses use the `data` wrapper with `attributes`; Strapi v5 uses
a flatter response shape. Detect the version or normalize both shapes before
deduplication. Check your content type schema for field names.

### Sanity Adapter

**Query tags** (GROQ):
```
*[_type == "tag"] { _id, name, slug }
```

**Create tag** (Mutations API):
```
POST https://{project_id}.api.sanity.io/{SANITY_API_VERSION}/data/mutate/{dataset}
Body: {"mutations": [{"create": {"_type": "tag", "name": "Tag", "slug": {"current": "tag"}}}]}
Authorization: Bearer {token}
```

Default `SANITY_API_VERSION` to a current tested API date supplied by the
project environment; do not hard-code it in generated requests.

## Taxonomy Audit Workflow

### Step 1: Inventory

Scan all posts in the target directory (or fetch from CMS). Build a map:
- tag_name -> [list of post files/IDs using this tag]
- category_name -> [list of post files/IDs]

### Step 2: Health Checks

| Check | Threshold | Action |
|-------|-----------|--------|
| Thin tag archives | < 5 posts per tag | Review for merge or noindex after traffic, intent, and link checks |
| Orphan tags | 0 posts | Recommend deletion |
| Tag bloat | More than `max(50, post_count * 0.25)` total tags, adjusted for taxonomy purpose | Recommend consolidation |
| Category depth | > 3 levels | Recommend flattening |
| Uncategorized posts | No category assigned | Assign to appropriate category |
| Duplicate slugs | Same slug, different name | Merge into canonical version |

### Step 3: Recommendations

Group findings by priority:
- **Critical**: orphan tags creating empty archive pages (crawl waste)
- **High**: thin tags with < 5 posts after traffic, intent, and link checks
- **Medium**: tag bloat above the scaled threshold (diluted taxonomy, harder to navigate)
- **Low**: naming inconsistencies (mixed case, hyphen vs space)

### Output Format

```
## Taxonomy Audit: [Site/Directory]

**Total tags**: [n] | **Total categories**: [n]
**Healthy**: [n] | **Thin**: [n] | **Orphan**: [n]

### Critical Issues
- [orphan tags list]

### Recommendations
1. Merge [tag-a] and [tag-b] (same topic, [n] combined posts)
2. Delete orphan tags: [list]
3. Merge or noindex tag archives with < 5 posts only after traffic, intent, and link checks
```

## Site-Wide Guidelines

- Aim for 5-10 main categories per site (broad topics)
- Tags should have at least 5 posts before creating an archive page
- Use consistent slug format: lowercase, hyphen-separated
- Every post needs exactly 1 primary category
- Tags per post: 3-8 recommended, never exceed 15

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| CMS_TYPE | Platform identifier | wordpress, shopify, ghost, strapi, sanity |
| CMS_URL | HTTPS base URL of the CMS | https://example.com |
| CMS_ALLOWED_HOSTS | Optional comma-separated allowlist for CMS hosts | example.com,admin.example.com |
| CMS_USERNAME | WordPress username when using Application Passwords | editor@example.com |
| CMS_API_KEY | Authentication credential | WordPress app password, API token, or key |
| SANITY_API_VERSION | Sanity API date for mutations | v2026-07-01 |

These must be set in the shell environment. Never store credentials in files or
commit them to version control. The skill reads them via `$CMS_TYPE`, `$CMS_URL`,
`$CMS_USERNAME`, `$CMS_API_KEY`, and optional platform-specific variables at runtime.

Security rule for CMS calls: require HTTPS, allow only `http` and `https`
parsing paths but send authenticated requests over HTTPS only, resolve DNS and
block loopback/private/link-local/reserved IPs, validate redirects with the same
checks or disable redirects, cap timeouts at 10 seconds, and enforce
`CMS_ALLOWED_HOSTS` when set.

## Error Handling

- **Missing environment variables**: If CMS_TYPE, CMS_URL, or CMS_API_KEY is unset, or if WordPress lacks CMS_USERNAME, report which variable is missing and provide the expected format
- **Invalid credentials**: If the CMS API returns 401/403, report "Authentication failed - check CMS_USERNAME/CMS_API_KEY" and do not retry
- **Connection timeouts**: If the CMS endpoint is unreachable after 10 seconds, report the timeout and suggest checking CMS_URL
- **Duplicate tag slugs**: If a tag already exists on the CMS, skip creation and note "Tag already exists: [name]"
- **Rate limits**: If the CMS API returns 429, honor `Retry-After` when present; otherwise use exponential backoff and retry once. Report if the limit persists
- **Unsupported CMS**: If CMS_TYPE is not one of the 5 supported platforms, list the valid options and exit
