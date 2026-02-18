---
name: blog-seo-check
description: >
  Post-writing SEO validation with pass/fail checklist covering title tag length
  and keyword placement, meta description quality, heading hierarchy and keyword
  density, internal/external link audit with anchor text analysis, canonical URL
  verification, Open Graph meta tags (og:title, og:description, og:image), Twitter
  Card validation, URL structure optimization, and image alt text presence. Produces
  prioritized fix list with specific recommendations. Use when user says "seo check",
  "check seo", "validate seo", "blog seo", "seo validation", "on-page seo",
  "title tag check", "meta description check", "heading check", "link audit".
allowed-tools:
  - Read
  - Grep
  - Glob
  - WebFetch
---

# Blog SEO Check -- Post-Writing Validation

Runs a comprehensive on-page SEO validation against a completed blog post and
generates a pass/fail checklist with specific fixes for each failure. Designed
to run after writing — catches issues before publishing.

## Workflow

### Step 1: Read Content

Read the target file and extract:
- **Frontmatter** — title, description, date, lastUpdated, author, tags,
  canonical, og:image, slug/URL
- **Heading structure** — H1, H2, H3 hierarchy with full text
- **Links** — All internal and external links with anchor text
- **Meta tags** — OG tags, Twitter Card tags, canonical URL
- **Body content** — Full text for keyword and structural analysis

If the user provides a URL instead of a file path, use WebFetch to retrieve
the page and extract the relevant elements.

### Step 2: Title Tag Validation

| Check | Pass Criteria |
|-------|---------------|
| Character count | 40-60 characters (no truncation in SERPs) |
| Keyword placement | Primary keyword in first half of title |
| Power word | Contains at least one power word (e.g., Guide, Best, How, Why, Essential, Proven, Complete) |
| Truncation risk | No critical meaning lost if truncated at 60 chars |
| Uniqueness | Not generic — specific to the content |

### Step 3: Meta Description

| Check | Pass Criteria |
|-------|---------------|
| Character count | 150-160 characters |
| Statistic included | Contains at least one specific number or data point |
| Value proposition | Ends with clear reader benefit or value proposition |
| Keyword presence | Primary keyword appears naturally (not stuffed) |
| No keyword stuffing | Keyword appears at most once |
| Call to action | Implies action (learn, discover, find out, see) |

### Step 4: Heading Hierarchy

| Check | Pass Criteria |
|-------|---------------|
| Single H1 | Exactly one H1 tag (the title) |
| No skipped levels | H1 -> H2 -> H3, never H1 -> H3 or H2 -> H4 |
| Keyword in headings | Primary keyword in 2-3 headings (natural, not forced) |
| Question format | 60-70% of H2 headings are questions |
| H2 count | 6-8 H2 sections for a standard blog post |
| Heading length | Each heading under 70 characters |

### Step 5: Internal Links

| Check | Pass Criteria |
|-------|---------------|
| Link count | 3-10 internal links per post |
| Anchor text | Descriptive (not "click here" or "read more") |
| Bidirectional | Check if linked pages also link back (flag if not) |
| No orphan status | Post links to at least 3 other pages on the site |
| Link distribution | Links spread across the post, not clustered |
| No self-links | Post does not link to itself |

Use Grep and Glob to scan the project for existing blog content and verify
bidirectional linking where possible.

### Step 6: External Links

| Check | Pass Criteria |
|-------|---------------|
| Source tier | Links to tier 1-3 sources only (authoritative, not SEO blogs) |
| Broken links | Use WebFetch to verify top external links are reachable |
| Rel attributes | External links have appropriate rel attributes (nofollow for sponsored/UGC) |
| Link count | At least 3 external links to authoritative sources |
| No competitor links | Not linking to direct competitors unnecessarily |

### Step 7: Canonical URL

| Check | Pass Criteria |
|-------|---------------|
| Present | Canonical URL is defined in frontmatter or meta tags |
| Correct format | Full absolute URL (https://domain.com/path) |
| Trailing slash | Consistent with site convention (no mixed trailing slashes) |
| Self-referencing | Canonical points to the page itself (unless intentional cross-domain) |

### Step 8: OG Meta Tags

| Check | Pass Criteria |
|-------|---------------|
| og:title | Present, matches or complements the title tag |
| og:description | Present, 150-160 characters, compelling for social sharing |
| og:image | Present, 1200x630 minimum dimensions, absolute URL |
| og:type | Set to "article" for blog posts |
| og:url | Present, matches canonical URL |
| og:site_name | Present, matches site/brand name |

### Step 9: Twitter Card

| Check | Pass Criteria |
|-------|---------------|
| twitter:card | Set to "summary_large_image" for blog posts |
| twitter:title | Present, under 70 characters |
| twitter:description | Present, under 200 characters |
| twitter:image | Present, same as or similar to og:image |
| twitter:site | Present if the site has a Twitter/X account |

### Step 10: URL Structure

| Check | Pass Criteria |
|-------|---------------|
| Length | Short — under 75 characters for the path portion |
| Keyword presence | Primary keyword or close variant in the URL slug |
| No dates | URL does not contain /2025/ or /2026/ date segments |
| No special characters | Only lowercase letters, numbers, and hyphens |
| Lowercase | Entire URL path is lowercase |
| No stop words | Minimal use of "the", "a", "and", "of" in slug |
| No file extension | No .html or .php in the URL (clean URLs) |

### Step 11: Generate Report

Output a comprehensive SEO validation report in this format:

```
## SEO Validation Report: [Title]

**File**: [path or URL]
**Date**: [check date]
**Overall**: [X/Y checks passed] — [PASS/NEEDS WORK/FAIL]

### Results

| # | Check | Status | Details | Fix |
|---|-------|--------|---------|-----|
| 1 | Title length | PASS | 52 chars | — |
| 2 | Title keyword | PASS | "keyword" in first half | — |
| 3 | Title power word | FAIL | No power word found | Add "Guide", "Essential", or "Complete" |
| 4 | Meta description length | PASS | 155 chars | — |
| 5 | Meta description stat | FAIL | No number found | Add a key statistic from the post |
| ... | ... | ... | ... | ... |

### Summary

**Passed**: [N] checks
**Failed**: [N] checks

### Priority Fixes
1. [Most impactful fix — what to change and where]
2. [Second most impactful fix]
3. [Third most impactful fix]

### Notes
- [Any observations about overall SEO health]
- [Suggestions for improvement beyond the checklist]
```

Status values:
- **PASS** — Meets the criteria
- **FAIL** — Does not meet the criteria, fix provided
- **WARN** — Partially meets criteria or edge case, recommendation provided
- **N/A** — Not applicable (e.g., no Twitter Card tags if site has no X account)
