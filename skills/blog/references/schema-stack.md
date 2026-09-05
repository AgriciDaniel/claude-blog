# Complete Blog Schema Reference

## Contents

- [Why Schema Matters](#why-schema-matters)
- [BlogPosting Schema](#blogposting-schema)
- [Person Schema](#person-schema)
- [Organization Schema](#organization-schema)
- [BreadcrumbList Schema](#breadcrumblist-schema)
- [FAQPage Schema](#faqpage-schema)
- [ImageObject Schema](#imageobject-schema)
- [VideoObject Schema](#videoobject-schema)
- [Speakable Schema](#speakable-schema)
- [Stable @id Patterns](#stable-id-patterns)
- [Schema Types: Use Only When Eligible](#schema-types-use-only-when-eligible)
- [ProfilePage Schema (Author Pages)](#profilepage-schema-author-pages)
- [JSON-LD @graph Pattern](#json-ld-graph-pattern)
- [Schema Validation Checklist](#schema-validation-checklist)

## Why Schema Matters

Article schema with author Person, publisher Organization, and BreadcrumbList
is the priority schema family for blog content in 2026. FAQ and HowTo rich
results are no longer broadly available for general blog content, so standard
article entities remain the practical baseline. Structured data does not earn
Google generative-AI visibility by itself and no special AI schema is required.
Google can process JavaScript-generated JSON-LD when it is available in the
rendered DOM. Source or server-rendered markup remains more portable for
non-Google crawlers.

Still rich-result-eligible for eligible blog content in 2026: Article,
BreadcrumbList, Video, Product, Review, and Event. FAQPage and HowTo remain
valid schema.org types, but general blogs should not expect FAQ or HowTo visual
rich results.

---

## BlogPosting Schema

The priority schema family for every blog post is Article. `BlogPosting` remains
acceptable as an Article-family implementation, but the required shape is the
same: author Person, publisher Organization, dates, headline, and canonical page
metadata in a single structured entity.

### Full Property Reference

**Note:** Google states "there are no required properties" for Article or
BlogPosting structured data. All properties below are recommended. `@context`
and `@type` are required by the JSON-LD spec itself.

| Property | Status | Type | Description |
|----------|--------|------|-------------|
| `@context` | JSON-LD required | URL | Always `"https://schema.org"` |
| `@type` | JSON-LD required | String | `"Article"` or `"BlogPosting"` |
| `@id` | Recommended | URI | Stable identifier: `{siteUrl}/blog/{slug}#article` |
| `headline` | Recommended | String | Post title, max 110 characters |
| `description` | Recommended | String | Accurate description that matches visible content |
| `datePublished` | Recommended | ISO 8601 | Original publish date |
| `dateModified` | Recommended | ISO 8601 | Last content update date |
| `author` | Recommended | Person | Author entity (use @id reference) |
| `publisher` | Recommended | Organization | Site/company entity (use @id reference) |
| `image` | Recommended | ImageObject or URL | Featured image, min 1200x630px |
| `mainEntityOfPage` | Recommended | WebPage | The page URL |
| `wordCount` | Recommended | Integer | Total word count of article body |
| `articleSection` | Recommended | String | Category/topic (e.g., "SEO") |
| `keywords` | Recommended | String or Array | Comma-separated or array of keywords |
| `inLanguage` | Recommended | String | BCP 47 language code (e.g., "en-US") |
| `url` | Recommended | URL | Canonical URL of the post |
| `thumbnailUrl` | Optional | URL | Smaller preview image |
| `articleBody` | Optional | String | Full text (usually omitted for size) |

### Complete Article/BlogPosting Example

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "@id": "https://example.com/blog/technical-seo-guide#article",
  "headline": "Complete Guide to Technical SEO in 2026",
  "description": "Technical SEO has evolved beyond Core Web Vitals. 72% of top-ranking pages now use structured data. Here's how to optimize your site for both traditional search and AI systems.",
  "datePublished": "2026-01-15T08:00:00Z",
  "dateModified": "2026-02-10T14:30:00Z",
  "author": {
    "@id": "https://example.com/author/sarah-chen#person"
  },
  "publisher": {
    "@id": "https://example.com#organization"
  },
  "image": {
    "@type": "ImageObject",
    "url": "https://example.com/images/blog/technical-seo-guide.jpg",
    "width": 1200,
    "height": 630,
    "caption": "Technical SEO optimization workflow diagram"
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://example.com/blog/technical-seo-guide"
  },
  "wordCount": 3200,
  "articleSection": "SEO",
  "keywords": ["technical SEO", "structured data", "Core Web Vitals", "schema markup"],
  "inLanguage": "en-US"
}
```

---

## Person Schema

Used for author attribution in BlogPosting and on dedicated author pages.

### Full Property Reference

| Property | Required | Type | Description |
|----------|----------|------|-------------|
| `@type` | Yes | String | Always `"Person"` |
| `@id` | Yes | URI | Stable: `{siteUrl}/author/{slug}#person` |
| `name` | Yes | String | Full name |
| `jobTitle` | Yes | String | Current professional title |
| `url` | Yes | URL | Author page URL |
| `image` | Yes | URL | Professional headshot |
| `sameAs` | Yes | Array | Social profile URLs (LinkedIn, Twitter, GitHub, personal site) |
| `worksFor` | Recommended | Organization | Current employer |
| `alumniOf` | Optional | CollegeOrUniversity | Educational background |
| `description` | Recommended | String | Brief professional bio |
| `knowsAbout` | Optional | Array | Expertise topics |

### Complete Person Example

```json
{
  "@type": "Person",
  "@id": "https://example.com/author/sarah-chen#person",
  "name": "Sarah Chen",
  "jobTitle": "Content Strategist",
  "url": "https://example.com/author/sarah-chen",
  "image": "https://example.com/images/authors/sarah-chen.jpg",
  "description": "Content strategist with 8 years of experience in B2B SaaS, specializing in data-driven blog optimization.",
  "sameAs": [
    "https://linkedin.com/in/sarahchen",
    "https://twitter.com/sarahchen",
    "https://sarahchen.com"
  ],
  "worksFor": {
    "@type": "Organization",
    "name": "Example Corp",
    "url": "https://example.com"
  },
  "alumniOf": {
    "@type": "CollegeOrUniversity",
    "name": "UC Berkeley"
  },
  "knowsAbout": ["SEO", "Content Strategy", "B2B SaaS Marketing"]
}
```

---

## Organization Schema

Represents the publishing entity. Referenced by every BlogPosting via the
`publisher` property.

### Full Property Reference

| Property | Required | Type | Description |
|----------|----------|------|-------------|
| `@type` | Yes | String | `"Organization"` or `"LocalBusiness"` |
| `@id` | Yes | URI | Stable: `{siteUrl}#organization` |
| `name` | Yes | String | Company/brand name |
| `url` | Yes | URL | Homepage URL |
| `logo` | Yes | ImageObject | Company logo (min 112x112px, max 600px wide) |
| `sameAs` | Recommended | Array | Social media profile URLs |
| `contactPoint` | Recommended | ContactPoint | Support/contact info |
| `description` | Optional | String | Brief company description |
| `founder` | Optional | Person | Company founder |
| `foundingDate` | Optional | Date | When the company was founded |

### Complete Organization Example

```json
{
  "@type": "Organization",
  "@id": "https://example.com#organization",
  "name": "Example Corp",
  "url": "https://example.com",
  "logo": {
    "@type": "ImageObject",
    "url": "https://example.com/images/logo.png",
    "width": 300,
    "height": 60
  },
  "sameAs": [
    "https://twitter.com/examplecorp",
    "https://linkedin.com/company/examplecorp",
    "https://github.com/examplecorp"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "customer support",
    "email": "support@example.com",
    "url": "https://example.com/contact"
  }
}
```

---

## BreadcrumbList Schema

Provides navigation hierarchy to search engines and AI systems. Improves
how pages appear in search results and helps crawlers understand site structure.

### ItemListElement Pattern

Each breadcrumb item requires `@type`, `position`, `name`, and `item` (URL).

### Complete BreadcrumbList Example

```json
{
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://example.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Blog",
      "item": "https://example.com/blog"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "SEO",
      "item": "https://example.com/blog/category/seo"
    },
    {
      "@type": "ListItem",
      "position": 4,
      "name": "Complete Guide to Technical SEO in 2026",
      "item": "https://example.com/blog/technical-seo-guide"
    }
  ]
}
```

### Rules

- Always start with Home (position 1)
- Include category/topic level if applicable
- Final item is the current page
- Positions must be sequential integers starting at 1
- Every item except the last must have an `item` URL

---

## FAQPage Schema

Google retired FAQ rich results for every site on 2026-05-07 and removed the
feature documentation in June. FAQPage remains a schema.org type, but it is not
a Google rich-result or generative-AI optimization path. Keep or add it only
when the visible FAQ is independently useful to readers. It earns no SEO or
AI-readiness credit.

### Structure

```
FAQPage
  └── mainEntity (array)
        └── Question
              ├── name (the question text)
              └── acceptedAnswer
                    └── Answer
                          └── text (the complete visible answer)
```

### Complete FAQPage Example

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How does technical SEO affect AI visibility?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Technical SEO helps crawlers access and understand a page. Render the primary content reliably, keep important metadata crawlable, and validate structured data against the visible page."
      }
    },
    {
      "@type": "Question",
      "name": "What is the most important schema type for blog posts?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Article or BlogPosting describes the article and can reference its author and publisher. Use properties that are accurate for the visible page and validate them for the intended search surface."
      }
    },
    {
      "@type": "Question",
      "name": "Do AI search engines use schema markup?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Google does not require structured data for generative AI search and has no special AI schema. Use structured data for supported search features and accurate entity description, not as a citation guarantee."
      }
    }
  ]
}
```

### Guidelines

- Include only the questions readers genuinely need
- Let each answer be as short or long as the subject requires
- Use questions supported by user research, support data, or the article's purpose
- Do not duplicate content already in the main article body
- Each answer should be self-contained and useful without context
- Do not use QAPage for editorial FAQs; QAPage requires one question and
  user-submitted answers

---

## ImageObject Schema

Used within BlogPosting for featured images and inline article images.

### Properties

| Property | Required | Type | Description |
|----------|----------|------|-------------|
| `@type` | Yes | String | `"ImageObject"` |
| `url` | Yes | URL | Full image URL |
| `width` | Yes | Integer | Width in pixels |
| `height` | Yes | Integer | Height in pixels |
| `caption` | Recommended | String | Descriptive caption |
| `creditText` | Recommended | String | Photographer or source credit |
| `copyrightHolder` | Optional | Person/Organization | Rights holder |
| `license` | Optional | URL | Link to license (e.g., Creative Commons) |

### Complete ImageObject Example

```json
{
  "@type": "ImageObject",
  "url": "https://example.com/images/blog/seo-workflow-diagram.jpg",
  "width": 1200,
  "height": 630,
  "caption": "Technical SEO audit workflow showing the 7-step process from crawl analysis to implementation",
  "creditText": "Example Corp Design Team",
  "copyrightHolder": {
    "@type": "Organization",
    "name": "Example Corp"
  }
}
```

---

## VideoObject Schema

Use VideoObject only for a visible, relevant, useful video when the page and
markup satisfy Google's current video structured-data eligibility and
visible-content requirements. The markup does not create a ranking, readiness,
or AI-citation bonus.

### Properties

| Property | Required | Type | Description |
|----------|----------|------|-------------|
| `@type` | Yes | String | `"VideoObject"` |
| `@id` | Yes | URI | `{siteUrl}/blog/{slug}#video-{index}` |
| `name` | Yes | String | Video title |
| `description` | Yes | String | First 200 chars of video description |
| `thumbnailUrl` | Yes | URL | `https://img.youtube.com/vi/{id}/hqdefault.jpg` |
| `uploadDate` | Yes | ISO 8601 | Video publish date |
| `contentUrl` | Yes | URL | `https://www.youtube.com/watch?v={id}` |
| `embedUrl` | Yes | URL | `https://www.youtube.com/embed/{id}` |
| `duration` | Recommended | ISO 8601 | Duration (e.g., `PT10M30S`) |
| `interactionStatistic` | Recommended | InteractionCounter | View count |
| `publisher` | Optional | Organization | Channel name and URL |

### Complete VideoObject Example

```json
{
  "@type": "VideoObject",
  "@id": "https://example.com/blog/seo-guide#video-1",
  "name": "Complete Guide to Technical SEO in 2026",
  "description": "Learn the essential technical SEO strategies for 2026 including Core Web Vitals optimization, structured data, and AI search readiness.",
  "thumbnailUrl": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
  "uploadDate": "2026-01-20T00:00:00Z",
  "contentUrl": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "embedUrl": "https://www.youtube.com/embed/dQw4w9WgXcQ",
  "duration": "PT12M45S",
  "interactionStatistic": {
    "@type": "InteractionCounter",
    "interactionType": { "@type": "WatchAction" },
    "userInteractionCount": 25000
  }
}
```

### Guidelines

- Only generate for YouTube videos actually embedded in the post
- Use `#video-1`, `#video-2` for sequential @id fragments
- Duration must be ISO 8601 format (PT prefix, M for minutes, S for seconds)
- Extract metadata from embed noscript text or YouTube Data API

---

## Speakable Schema

Speakable support is limited and should not be a default schema recommendation
for normal blog pages. Use it only when the target surface explicitly supports
Speakable markup and the selected text is visible on the page.

### Implementation Options

Use `cssSelector` (preferred) or `xPath` to identify speakable content sections.

### Speakable Example with CSS Selectors

```json
{
  "@type": "WebPage",
  "speakable": {
    "@type": "SpeakableSpecification",
    "cssSelector": [
      ".article-summary",
      ".faq-answer",
      "h1",
      ".key-takeaway"
    ]
  }
}
```

### Speakable Example with XPath

```json
{
  "@type": "WebPage",
  "speakable": {
    "@type": "SpeakableSpecification",
    "xPath": [
      "/html/head/title",
      "/html/body//article/p[1]",
      "/html/body//div[@class='key-takeaway']"
    ]
  }
}
```

### Guidelines

- Point to concise, self-contained text sections
- Ideal sections: article summaries, FAQ answers, key takeaways
- Avoid pointing to entire articles (too long for voice)
- Each speakable section should be under 2-3 sentences
- Content must make sense when read aloud without visual context

---

## Stable @id Patterns

Every schema entity needs a stable, unique `@id` that remains consistent across
page loads and site rebuilds. This allows search engines to build entity graphs
and AI systems to deduplicate references.

### Standard Patterns

| Entity | @id Pattern | Example |
|--------|-------------|---------|
| Blog Post | `{siteUrl}/blog/{slug}#article` | `https://example.com/blog/seo-guide#article` |
| Author | `{siteUrl}/author/{slug}#person` | `https://example.com/author/sarah-chen#person` |
| Organization | `{siteUrl}#organization` | `https://example.com#organization` |
| WebPage | `{siteUrl}/blog/{slug}` | `https://example.com/blog/seo-guide` |
| BreadcrumbList | `{siteUrl}/blog/{slug}#breadcrumb` | `https://example.com/blog/seo-guide#breadcrumb` |
| FAQPage | `{siteUrl}/blog/{slug}#faq` | `https://example.com/blog/seo-guide#faq` |
| VideoObject | `{siteUrl}/blog/{slug}#video-{N}` | `https://example.com/blog/seo-guide#video-1` |

### Rules

- Use the fragment identifier (`#`) to differentiate entities on the same page
- Never use random IDs, timestamps, or build hashes
- Keep patterns consistent across every page on the site
- The URL portion must match the canonical URL
- Use `@id` references to link entities instead of embedding duplicates

### Referencing by @id

Instead of embedding a full Person object in every BlogPosting, reference the
@id and define the Person once in the @graph:

```json
"author": {
  "@id": "https://example.com/author/sarah-chen#person"
}
```

---

## Schema Types: Use Only When Eligible

These entries separate Google rich-result eligibility from schema.org validity.
Using unsupported rich-result markup can waste implementation effort and cause
validation confusion. Schema.org validity and Google Search feature support are
separate questions.

| Type | Google Search status | Notes |
|------|----------------------|-------|
| HowTo | No current rich-result experience | Use visible step content plus Article for general blogs |
| ClaimReview | Former Search experience | Retired as part of Google's 2025 result simplification |
| SpecialAnnouncement | Former Search experience | Documentation removed in September 2025 |
| Course Info | Former Search experience | Distinct from the currently documented Course list feature |
| Estimated Salary | Former Search experience | Documentation removed in September 2025 |
| Learning Video | Former Search experience | Documentation removed in September 2025 |
| Vehicle Listing | Former Search experience | Documentation removed in September 2025 |
| PracticeProblem | Removed Search experience | Documentation removed in January 2026 |
| Dataset | Dataset Search only | Do not use for ordinary articles |
| Sitelinks Search Box | No dedicated visual element | Google generates sitelinks algorithmically |
| QAPage | Supported narrow use | One question with user-submitted answers, not editorial FAQs |

### What to Use Instead

| Deprecated Type | Alternative |
|----------------|-------------|
| HowTo | Use standard Article or BlogPosting with clear step headings (H2/H3) |
| QAPage | Use FAQPage only for a genuinely useful visible editorial FAQ |
| SpecialAnnouncement | Use standard Article or NewsArticle |
| ClaimReview | No direct replacement for blogs; use Author entity with credentials |

---

## ProfilePage Schema (Author Pages)

Supported in 2026. Add to author bio/team pages to strengthen E-E-A-T signals
and improve eligibility for author entity understanding.

```json
{
  "@context": "https://schema.org",
  "@type": "ProfilePage",
  "dateCreated": "2024-01-01T00:00:00Z",
  "dateModified": "2026-04-01T00:00:00Z",
  "mainEntity": {
    "@type": "Person",
    "@id": "https://example.com/author/jane-smith#person",
    "name": "Jane Smith",
    "url": "https://example.com/author/jane-smith",
    "jobTitle": "Senior Content Strategist",
    "description": "Jane writes about SEO and content marketing with 8 years of experience.",
    "image": {
      "@type": "ImageObject",
      "url": "https://example.com/images/jane-smith.jpg"
    },
    "sameAs": [
      "https://linkedin.com/in/janesmith",
      "https://twitter.com/janesmith"
    ]
  }
}
```

---

## JSON-LD @graph Pattern

Combine all schema entities in a single `<script type="application/ld+json">`
tag using the `@graph` array. This is the recommended approach for pages with
multiple schema types.

### Benefits

- Single script tag instead of multiple scattered blocks
- Entities reference each other via `@id`
- Easier to maintain and validate
- Cleaner HTML source

### Complete @graph Example (Blog Post Page)

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.com#organization",
      "name": "Example Corp",
      "url": "https://example.com",
      "logo": {
        "@type": "ImageObject",
        "url": "https://example.com/images/logo.png",
        "width": 300,
        "height": 60
      },
      "sameAs": [
        "https://twitter.com/examplecorp",
        "https://linkedin.com/company/examplecorp"
      ]
    },
    {
      "@type": "Person",
      "@id": "https://example.com/author/sarah-chen#person",
      "name": "Sarah Chen",
      "jobTitle": "Content Strategist",
      "url": "https://example.com/author/sarah-chen",
      "image": "https://example.com/images/authors/sarah-chen.jpg",
      "sameAs": [
        "https://linkedin.com/in/sarahchen",
        "https://twitter.com/sarahchen"
      ],
      "worksFor": {
        "@id": "https://example.com#organization"
      }
    },
    {
      "@type": "Article",
      "@id": "https://example.com/blog/technical-seo-guide#article",
      "headline": "Complete Guide to Technical SEO in 2026",
      "description": "Technical SEO has evolved beyond Core Web Vitals. 72% of top-ranking pages now use structured data. Here's how to optimize your site for both traditional search and AI systems.",
      "datePublished": "2026-01-15T08:00:00Z",
      "dateModified": "2026-02-10T14:30:00Z",
      "author": {
        "@id": "https://example.com/author/sarah-chen#person"
      },
      "publisher": {
        "@id": "https://example.com#organization"
      },
      "image": {
        "@type": "ImageObject",
        "url": "https://example.com/images/blog/technical-seo-guide.jpg",
        "width": 1200,
        "height": 630,
        "caption": "Technical SEO optimization workflow diagram"
      },
      "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": "https://example.com/blog/technical-seo-guide"
      },
      "wordCount": 3200,
      "articleSection": "SEO",
      "keywords": ["technical SEO", "structured data", "schema markup"],
      "inLanguage": "en-US"
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://example.com/blog/technical-seo-guide#breadcrumb",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "https://example.com"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "Blog",
          "item": "https://example.com/blog"
        },
        {
          "@type": "ListItem",
          "position": 3,
          "name": "Complete Guide to Technical SEO in 2026",
          "item": "https://example.com/blog/technical-seo-guide"
        }
      ]
    },
    {
      "@type": "FAQPage",
      "@id": "https://example.com/blog/technical-seo-guide#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "How does technical SEO affect AI visibility?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Technical SEO helps crawlers access and understand a page. Render the primary content reliably, keep important metadata crawlable, and validate structured data against the visible page."
          }
        },
        {
          "@type": "Question",
          "name": "What schema types should every blog post have?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Use Article or BlogPosting with accurate author, publisher, date, image, and canonical-page information when those properties apply. Add other types only when visible content and the intended search feature support them."
          }
        }
      ]
    }
  ]
}
```

---

## Schema Validation Checklist

| Check | Pass | Fail |
|-------|------|------|
| JSON-LD reaches rendered DOM | Present in source or reliably rendered DOM | Missing from rendered DOM or populated after a failed request |
| Valid JSON syntax | Passes JSON.parse() | Syntax errors |
| @context is `https://schema.org` | Exact match | Missing or HTTP |
| @id uses stable fragment pattern | Consistent across builds | Random or missing |
| dateModified matches actual update | Within 24 hours of last edit | Stale or fabricated |
| Author @id matches author page | Same URI used everywhere | Inconsistent references |
| Image URLs are absolute | Start with `https://` | Relative paths |
| Eligibility checked for optional types | Type is valid for the visible content and target surface | Ineligible rich-result markup used as a default |
| Complete schema graph per page | Article/BlogPosting + Person + Organization + BreadcrumbList minimum | Missing priority entity baseline |
| Validates in the right tool | Schema.org Validator for schema validity; Rich Results Test only for eligible Google rich-result types | Errors present |

### Validation Tools

- **Schema.org Validator**: https://validator.schema.org
- **Google Rich Results Test**: https://search.google.com/test/rich-results for eligible Google rich-result types
- **JSON-LD Playground**: https://json-ld.org/playground/

For JavaScript-generated JSON-LD, test the URL rather than only a copied code
fragment, inspect the rendered HTML, and confirm every marked-up fact matches
visible content. Google documents both Google Tag Manager and custom JavaScript
generation at:
https://developers.google.com/search/docs/appearance/structured-data/generate-structured-data-with-javascript
