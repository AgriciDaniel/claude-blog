---
name: blog-schema
description: >
  Generate complete JSON-LD schema markup for blog posts including BlogPosting,
  Person, Organization, BreadcrumbList, FAQPage, and ImageObject. Validates
  against Google requirements and warns about deprecated types. Use when user
  says "schema", "blog schema", "json-ld", "structured data", "schema markup",
  "generate schema".
allowed-tools:
  - read_file
  - write_file
  - grep_search
  - glob
---

# Blog Schema -- JSON-LD Structured Data Generation

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

Complete BlogPosting with all required and recommended properties:

```json
{
  "@type": "BlogPosting",
  "@id": "{siteUrl}/blog/{slug}#article",
  "headline": "Post title (max 110 chars)",
  "description": "Meta description (150-160 chars)",
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

Required properties: @type, headline, datePublished, author, publisher, image.
Recommended properties: description, dateModified, mainEntityOfPage, wordCount,
articleBody (excerpt).

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
- `alumniOf` — Educational institution (Organization type)
- `worksFor` — Employer (reference to Organization @id if same entity)

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

Logo requirements: must be a valid image URL. Google recommends logos be
112x112px minimum, 600px wide maximum. Rectangular logos preferred for
BlogPosting publishers.

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

### Step 6: Generate FAQPage Schema

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

Important note: Google restricted FAQ rich results to government and health
sites since August 2023. However, FAQ schema markup still provides value
because:
- AI systems (ChatGPT, Perplexity, Gemini) extract FAQ data for citations
- It structures content for future rich result eligibility changes
- It improves content organization signals

### Step 7: Generate ImageObject

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

Check for deprecated schema types and apply validation rules:

**NEVER use these deprecated types:**
- **HowTo** — Deprecated September 2023 (Google no longer shows rich results)
- **SpecialAnnouncement** — Deprecated July 2025
- **Practice Problem** — Deprecated (education markup)
- **Dataset** — Deprecated for general use
- **Sitelinks Search Box** — Deprecated
- **Q&A** — Deprecated January 2026 (distinct from FAQPage)

**Validation checks:**
1. All @id references resolve to entities within the @graph
2. dateModified is equal to or after datePublished
3. headline does not exceed 110 characters
4. description is between 50-160 characters
5. All URLs are absolute (not relative)
6. Image dimensions are positive integers
7. BreadcrumbList positions are sequential starting from 1
8. FAQPage has at least 2 questions

**AI citation optimization note:** Pages using 3 or more schema types have
approximately 13% higher AI citation likelihood. This skill generates 6 types
by default (BlogPosting, Person, Organization, BreadcrumbList, FAQPage,
ImageObject) to maximize both search engine understanding and AI extraction.

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
    { "@type": "ImageObject", ... }
  ]
}
</script>
```

**@graph pattern benefits:**
- Single script tag instead of multiple — cleaner HTML
- Entity linking via stable @id references (e.g., author references Person by @id)
- Google and AI systems parse @graph arrays correctly
- Easier to maintain and update as a single block

**Output options:**
- **Embedded HTML** — Ready to paste into `<head>` or before `</body>`
- **Standalone JSON** — For CMS schema fields or API injection
- **MDX component** — If the project uses MDX, wrap in a component

Save the generated schema to the blog post file or to a separate schema file
as the user prefers.
