---
name: blog-schema
description: >
  Generate complete JSON-LD schema markup for blog posts with Article/BlogPosting,
  Person, Organization, BreadcrumbList, ImageObject, and optional FAQPage. Validates
  against Google requirements and warns about deprecated types. Use when user
  says "schema", "blog schema", "json-ld", "structured data", "schema markup",
  "generate schema".
user-invokable: true
argument-hint: "<file-path>"
license: MIT
---

# Blog Schema: JSON-LD Structured Data Generation

Generates complete, validated JSON-LD schema markup for blog posts using the
@graph pattern. Combines multiple schema types into a single script tag with
stable @id references for entity linking.

## Workflow

### Step 1: Read Content

Read the blog post and extract all schema-relevant data:
- **Title** (headline)
- **Author** (name, job title, social links, credentials)
- **Dates** (datePublished, dateModified / lastUpdated)
- **Description** (meta description)
- **FAQ section** (question and answer pairs)
- **Images** (cover image URL, dimensions, alt text; inline images)
- **Organization info** (site name, URL, logo)
- **Word count** (approximate from content length)
- **Tags/categories** (for BreadcrumbList category)
- **Slug** (from filename or frontmatter)

### Step 2: Generate BlogPosting Schema

Complete BlogPosting with recommended properties when applicable:

```json
{
  "@type": "BlogPosting",
  "@id": "{siteUrl}/blog/{slug}#article",
  "headline": "Concise post title",
  "description": "Concise page-specific meta description",
  "datePublished": "YYYY-MM-DD",
  "dateModified": "YYYY-MM-DD",
  "author": { "@id": "{siteUrl}/author/{author-slug}#person" },
  "publisher": { "@id": "{siteUrl}#organization" },
  "image": { "@id": "{siteUrl}/blog/{slug}#primaryimage" },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "{siteUrl}/blog/{slug}"
  },
  "wordCount": 2400,
  "articleBody": "First 200 characters of content as excerpt..."
}
```

Google's Article structured data docs do not define required Article
properties. Include `headline`, `datePublished`, `author`, `publisher`, and
`image` when applicable, validate with the Rich Results Test, and treat missing
fields as warnings unless the target surface requires them. Recommended
properties: description, dateModified, mainEntityOfPage, wordCount, articleBody
(excerpt).

### Step 3: Generate Person Schema

Author schema with stable @id for cross-referencing:

```json
{
  "@type": "Person",
  "@id": "{siteUrl}/author/{author-slug}#person",
  "name": "Author Name",
  "jobTitle": "Role or Title",
  "url": "{siteUrl}/author/{author-slug}",
  "sameAs": [
    "https://twitter.com/handle",
    "https://linkedin.com/in/handle",
    "https://github.com/handle"
  ]
}
```

Optional properties (include when available):
- `alumniOf` - Educational institution (Organization type)
- `worksFor` - Employer (reference to Organization @id if same entity)

### Step 4: Generate Organization Schema

Blog's parent organization entity:

```json
{
  "@type": "Organization",
  "@id": "{siteUrl}#organization",
  "name": "Organization Name",
  "url": "{siteUrl}",
  "logo": {
    "@type": "ImageObject",
    "url": "{siteUrl}/logo.png",
    "width": 600,
    "height": 60
  },
  "sameAs": [
    "https://twitter.com/org",
    "https://linkedin.com/company/org",
    "https://github.com/org"
  ]
}
```

Logo requirements: use a valid crawlable image URL and follow the active
Organization and Article documentation for the target surface. Do not invent
hard logo dimensions unless the project or current docs require them.

### Step 5: Generate BreadcrumbList

Navigation breadcrumb schema showing content hierarchy:

```json
{
  "@type": "BreadcrumbList",
  "@id": "{siteUrl}/blog/{slug}#breadcrumb",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "{siteUrl}"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Category Name",
      "item": "{siteUrl}/blog/category/{category-slug}"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Post Title",
      "item": "{siteUrl}/blog/{slug}"
    }
  ]
}
```

If no category is available, use "Blog" as the second breadcrumb item with
`{siteUrl}/blog` as the URL.

### Step 6: Generate FAQPage Entity Schema

Extract Q&A pairs from the blog post's FAQ section:

```json
{
  "@type": "FAQPage",
  "@id": "{siteUrl}/blog/{slug}#faq",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is the question?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The complete answer text (40-60 words with statistic)."
      }
    }
  ]
}
```

Important note: Google retired FAQ rich results for all sites on 2026-05-07.
FAQPage is not a Google rich result path. Only emit FAQPage when visible FAQ
content exists, with at least one valid `Question` and matching visible answer.
Treat it as entity clarity markup, not a Google rich-result promise. The
Article/BlogPosting schema remains the priority for blog search eligibility.

### Step 7: Generate VideoObject (if videos present)

For each YouTube video embedded in the post, generate a VideoObject schema:

```json
{
  "@type": "VideoObject",
  "@id": "{siteUrl}/blog/{slug}#video-{index}",
  "name": "Video title",
  "description": "Video description excerpt (first 200 chars)",
  "thumbnailUrl": "https://img.youtube.com/vi/{videoId}/hqdefault.jpg",
  "uploadDate": "{ISO 8601 date}",
  "contentUrl": "https://www.youtube.com/watch?v={videoId}",
  "embedUrl": "https://www.youtube.com/embed/{videoId}",
  "duration": "PT{M}M{S}S",
  "interactionStatistic": {
    "@type": "InteractionCounter",
    "interactionType": { "@type": "WatchAction" },
    "userInteractionCount": {viewCount}
  }
}
```

Add each VideoObject to the @graph array. Use `#video-1`, `#video-2` etc. for
the @id fragment. Extract video metadata from the embed's noscript fallback or
from YouTube Data API if available via `blog-google`.

### Step 7.5: Generate ImageObject

Cover image schema for the post's primary image:

```json
{
  "@type": "ImageObject",
  "@id": "{siteUrl}/blog/{slug}#primaryimage",
  "url": "https://cdn.pixabay.com/photo/.../image.jpg",
  "width": 1200,
  "height": 630,
  "caption": "Descriptive caption matching alt text"
}
```

Image requirements:
- URL must be crawlable and publicly accessible
- Width and height should reflect actual image dimensions
- Caption should match or closely align with the image alt text
- Preferred dimensions: 1200x630 (OG-compatible) or 1920x1080

### Step 8: Validate & Warn

Check per-surface support before recommending schema types:

| Type | Google rich-result status | Valid entity/context use |
|------|---------------------------|--------------------------|
| HowTo | Not a current Google rich-result tactic | Valid schema.org type when the page genuinely contains how-to content |
| Dataset | Not for generic blog rich results | Valid for dataset pages and Dataset Search eligibility |
| QAPage | Not the same as FAQPage | Valid when the page contains one question with user-submitted answers |
| SpecialAnnouncement, PracticeProblem, Sitelinks Search Box | Do not recommend for general blog posts | Use only when current official docs and page content match |

**Validation checks:**
1. All @id references resolve to entities within the @graph
2. dateModified is equal to or after datePublished
3. headline is concise. Warn when it may truncate or becomes unclear
4. description is concise, page-specific, and not duplicated across posts
5. All URLs are absolute (not relative)
6. Image dimensions are positive integers
7. BreadcrumbList positions are sequential starting from 1
8. If FAQPage is emitted, visible Q&A content exists and includes at least 1 valid `Question`

**AI citation optimization note:** Relevant schema helps entity clarity and
rich-result eligibility where supported, but structured data is not required for
Google generative AI search visibility. Prioritize Article/BlogPosting, Person,
Organization, and BreadcrumbList. Add ImageObject or VideoObject when assets
exist, and add FAQPage only when visible FAQ content exists.

### Step 9: Output

Combine all schemas into a single `<script>` tag using the @graph pattern:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    { "@type": "BlogPosting", ... },
    { "@type": "Person", ... },
    { "@type": "Organization", ... },
    { "@type": "BreadcrumbList", ... },
    { "@type": "FAQPage", ... },
    { "@type": "VideoObject", ... },
    { "@type": "ImageObject", ... }
  ]
}
</script>
```

**@graph pattern benefits:**
- Single script tag instead of multiple - cleaner HTML
- Entity linking via stable @id references (e.g., author references Person by @id)
- Google and AI systems parse @graph arrays correctly
- Easier to maintain and update as a single block

**Output options:**
- **Embedded HTML** - Ready to paste into `<head>` or before `</body>`
- **Standalone JSON** - For CMS schema fields or API injection
- **MDX component** - If the project uses MDX, wrap in a component

Save the generated schema to the blog post file or to a separate schema file
as the user prefers.
