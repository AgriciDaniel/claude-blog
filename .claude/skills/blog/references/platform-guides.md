# Platform-Specific Output Formatting

Adapt blog output to each platform's requirements. Detect the platform
from project structure (see `SKILL.md` Platform Detection table) and apply
the corresponding format rules below.

## Contents

- [Next.js / MDX](#nextjs--mdx)
- [Astro](#astro)
- [Hugo](#hugo)
- [Jekyll](#jekyll)
- [WordPress](#wordpress)
- [Ghost](#ghost)
- [11ty (Eleventy)](#11ty-eleventy)
- [Gatsby](#gatsby)
- [HTML / Static](#html--static)
- [Platform Selection Quick Reference](#platform-selection-quick-reference)

---

## Next.js / MDX

### Frontmatter Format
```yaml
---
title: "How Does AI Search Impact Organic Traffic in 2026?"
description: "A practical guide to measuring how AI search features affect organic traffic and reader journeys."
date: "2026-02-18"
lastUpdated: "2026-02-18"
author: "Author Name"
tags: ["ai-search", "seo", "traffic"]
coverImage: "/images/blog/ai-search.jpg"
coverImageAlt: "Marketing dashboard showing AI search traffic trends"
ogImage: "/images/blog/ai-search.jpg"
---
```

**Supported frontmatter fields**: title, description, date, lastUpdated, author,
tags, coverImage, coverImageAlt, ogImage. Adapt field names to match the
project's existing convention (some use `image` instead of `coverImage`).

### Image Embedding
```mdx
![Marketing team analyzing search traffic on a dashboard](/images/blog/ai-search.jpg)
```

For projects using `next/image` component:
```tsx
import Image from 'next/image'

<Image
  src="/images/blog/ai-search.jpg"
  alt="Marketing team analyzing search traffic on a dashboard"
  width={1200}
  height={630}
  priority={false}
/>
```

### Local Image Policy

Store generated or downloaded images in `public/images/blog/` or import them
from the local asset tree. Do not depend on remote CDN allowlists for
claude-blog generated assets.

### Chart / SVG Embedding (JSX-Compatible)

All SVG attributes must use camelCase in MDX files. HTML-style attributes
cause compilation errors.

```mdx
<figure className="chart-container" style={{margin: '2.5rem 0', textAlign: 'center', padding: '1.5rem', borderRadius: '12px'}}>
  <svg
    viewBox="0 0 560 380"
    style={{maxWidth: '100%', height: 'auto', fontFamily: "'Inter', system-ui, sans-serif"}}
    role="img"
    aria-label="Chart showing AIO organic CTR rebound from 1.3% to about 2.4%"
  >
    <title>AIO Organic CTR Rebound</title>
    <desc>Bar chart comparing the December 2025 AIO CTR floor to the February 2026 rebound</desc>
    <text x="280" y="30" textAnchor="middle" fontSize="16" fontWeight="700" fill="currentColor">
      AIO Organic CTR Rebound
    </text>
    <rect x="100" y="152" width="160" height="108" rx="6" fill="#f97316" />
    <text x="180" y="212" textAnchor="middle" fontSize="14" fontWeight="800" fill="white">
      1.3%
    </text>
    <rect x="300" y="60" width="160" height="200" rx="6" fill="#38bdf8" />
    <text x="380" y="165" textAnchor="middle" fontSize="14" fontWeight="800" fill="white">
      ~2.4%
    </text>
    <text x="280" y="372" textAnchor="middle" fontSize="10" fill="currentColor" opacity="0.35">
      Source: Seer Interactive (Apr 2026)
    </text>
  </svg>
</figure>
```

**JSX attribute conversion reference:**

| HTML Attribute | JSX Attribute |
|----------------|---------------|
| `stroke-width` | `strokeWidth` |
| `stroke-dasharray` | `strokeDasharray` |
| `stroke-linecap` | `strokeLinecap` |
| `text-anchor` | `textAnchor` |
| `font-size` | `fontSize` |
| `font-weight` | `fontWeight` |
| `font-family` | `fontFamily` |
| `class` | `className` |
| `style="..."` | `style={{...}}` |
| `fill-opacity` | `fillOpacity` |
| `stop-color` | `stopColor` |
| `clip-path` | `clipPath` |

### MDX Component Imports for Custom Charts
```mdx
import { BarChart } from '@/components/charts/BarChart'
import { FAQSchema } from '@/components/FAQSchema'

<BarChart data={chartData} title="AIO Organic CTR Rebound" />
<FAQSchema faqs={[{ question: "...", answer: "..." }]} />
```

Check the project's `components/` directory for available chart components
before inlining SVG. Use project components when they exist.

### generateStaticParams for Broad Crawler Portability

Crawler rendering capabilities vary. Prefer statically generated or
server-rendered primary content for broad portability, and verify each target
crawler. Google Search can process JavaScript-generated JSON-LD when it reaches
the rendered DOM, matches visible content, and passes validation.

```typescript
// app/blog/[slug]/page.tsx
export async function generateStaticParams() {
  const posts = getAllPosts()
  return posts.map((post) => ({
    slug: post.slug,
  }))
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const post = getPostBySlug(slug)
  return {
    title: post.title,
    description: post.description,
    openGraph: {
      title: post.title,
      description: post.description,
      images: [post.ogImage],
      type: 'article',
      publishedTime: post.date,
      modifiedTime: post.lastUpdated,
    },
  }
}
```

### Key Configuration Notes
- MDX files require `@next/mdx` or `next-mdx-remote` package
- Verify `mdx-components.tsx` exists at project root for custom element mapping
- Use `export const metadata` or `generateMetadata` for per-page SEO
- Prefer server-rendered JSON-LD for crawler portability. Google can process
  JavaScript-generated JSON-LD when it reaches the rendered DOM, matches visible
  content, and passes validation.
- Sitemap: use `app/sitemap.ts` with `MetadataRoute.Sitemap` type

---

## Astro

### Frontmatter Format
```yaml
---
title: "How Does AI Search Impact Organic Traffic in 2026?"
description: "A practical guide to measuring how AI search features affect organic traffic and reader journeys."
pubDate: 2026-02-18
updatedDate: 2026-02-18
author: "Author Name"
tags: ["ai-search", "seo", "traffic"]
heroImage: "/images/ai-search-cover.jpg"
heroImageAlt: "Marketing dashboard showing AI search metrics"
---
```

Astro uses `pubDate` and `updatedDate` (Date objects) instead of `date`
and `lastUpdated` (strings). Adapt to match the project's content schema.

### Content Collections (src/content/blog/)

Astro 4+ uses type-safe content collections with Zod schema validation:

```typescript
// src/content/config.ts
import { defineCollection, z } from 'astro:content'

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    author: z.string().optional(),
    tags: z.array(z.string()).optional(),
    heroImage: z.string().optional(),
    heroImageAlt: z.string().optional(),
  }),
})

export const collections = { blog }
```

Place blog posts in `src/content/blog/` as `.md` or `.mdx` files.

### Image Embedding
```markdown
![Marketing team analyzing search data](./images/search-dashboard.jpg)
```

Using `astro:assets` for optimization:
```astro
---
import { Image } from 'astro:assets'
import searchDashboard from '../assets/search-dashboard.jpg'
---
<Image src={searchDashboard} alt="Marketing team analyzing search data" />
```

Generated or downloaded images should be local Astro assets. Do not depend on
remote image-domain configuration for claude-blog generated assets.

### Chart / SVG Embedding

Standard SVG works directly in `.md` files. For `.astro` component wrappers:

```astro
---
// src/components/Chart.astro
const { title, ariaLabel } = Astro.props
---
<figure class="chart-container">
  <slot />
  <figcaption>{title}</figcaption>
</figure>
```

Use standard HTML attributes (not camelCase) in `.astro` and `.md` files:
```html
<svg viewBox="0 0 560 380" role="img" aria-label="AIO CTR rebound chart">
  <text x="280" y="30" text-anchor="middle" font-size="16" fill="currentColor">
    Chart Title
  </text>
</svg>
```

### Key Configuration Notes
- Static output by default (SSG): ideal for AI crawlers without JS execution
- Markdown files support raw HTML/SVG natively (no unsafe config needed)
- For MDX support: add `@astrojs/mdx` integration
- Sitemap: add `@astrojs/sitemap` integration with `site` config
- RSS: add `@astrojs/rss` for feed generation
- View Transitions: built-in via `<ViewTransitions />` component

---

## Hugo

### Frontmatter Format (YAML)
```yaml
---
title: "How Does AI Search Impact Organic Traffic in 2026?"
description: "A practical guide to measuring how AI search features affect organic traffic and reader journeys."
date: 2026-02-18
lastmod: 2026-02-18
author: "Author Name"
tags: ["ai-search", "seo", "traffic"]
categories: ["SEO Strategy"]
series: ["AI Search Optimization"]
images:
  - "/images/ai-search-cover.jpg"
draft: false
---
```

### Frontmatter Format (TOML)
```toml
+++
title = "How Does AI Search Impact Organic Traffic in 2026?"
description = "A practical guide to measuring how AI search features affect organic traffic and reader journeys."
date = 2026-02-18
lastmod = 2026-02-18
author = "Author Name"
tags = ["ai-search", "seo", "traffic"]
categories = ["SEO Strategy"]
series = ["AI Search Optimization"]
images = ["/images/ai-search-cover.jpg"]
draft = false
+++
```

Hugo uses `lastmod` instead of `lastUpdated`. Supports both YAML (`---`)
and TOML (`+++`) frontmatter delimiters.

### Taxonomy Structure
Hugo supports three built-in taxonomies:
- **categories**: Broad topic groupings (content pillars)
- **tags**: Specific topic labels (keywords)
- **series**: Multi-part content sequences

Configure in `hugo.toml`:
```toml
[taxonomies]
  category = "categories"
  tag = "tags"
  series = "series"
```

### Image Embedding
```markdown
![Marketing team analyzing search data](/images/search-dashboard.jpg)
```

Hugo processes images from `static/images/` or page bundles (`content/blog/post-name/images/`).

### Chart / SVG Embedding via Shortcodes

Create a custom shortcode for trusted, sanitized inline SVG only. Do not pass
user-derived or generated text through `safeHTML` unless it has been sanitized
with a strict SVG allowlist.

```html
<!-- layouts/shortcodes/chart.html -->
<figure class="chart-container" style="margin: 2.5rem 0; text-align: center;">
  {{ .Inner | safeHTML }}
  {{ with .Get "caption" }}<figcaption>{{ . }}</figcaption>{{ end }}
</figure>
```

Usage in markdown:
```markdown
{{< chart caption="Source: Seer Interactive (Apr 2026)" >}}
<svg viewBox="0 0 560 380" role="img" aria-label="AIO CTR rebound chart">
  <!-- SVG content -->
</svg>
{{< /chart >}}
```

### Goldmark Renderer Config (Required for SVG)

Hugo's default Goldmark renderer escapes raw HTML. Enable unsafe rendering only
for trusted authored SVG/HTML after sanitization:

```toml
# hugo.toml
[markup.goldmark.renderer]
  unsafe = true
```

Without this setting, all `<svg>`, `<figure>`, and other HTML tags in markdown
files will be stripped from the output. If authors or external systems can
provide markup, prefer a shortcode that sanitizes SVG and rejects scripts,
event-handler attributes, foreignObject, external resources, and unsafe URLs.

### Custom Archetypes
```markdown
<!-- archetypes/blog.md -->
---
title: "{{ replace .Name "-" " " | title }}"
description: ""
date: {{ .Date }}
lastmod: {{ .Date }}
author: ""
tags: []
categories: []
images: []
draft: true
---

## Introduction

[Hook with statistic]
```

Create new posts with: `hugo new blog/my-post-title.md`

### Key Configuration Notes
- Posts go in `content/blog/` or `content/posts/` (check project convention)
- Page bundles (`content/blog/post-name/index.md`) co-locate images with content
- Use `{{ .Params.lastmod }}` in templates for freshness display
- JSON-LD schema: add in `layouts/partials/schema.html` partial
- Sitemap auto-generated at `/sitemap.xml`
- RSS auto-generated at `/index.xml`

---

## Jekyll

### Frontmatter Format (YAML Required)
```yaml
---
layout: post
title: "How Does AI Search Impact Organic Traffic in 2026?"
description: "A practical guide to measuring how AI search features affect organic traffic and reader journeys."
date: 2026-02-18
last_modified_at: 2026-02-18
author: "Author Name"
categories: [seo-strategy]
tags: [ai-search, seo, traffic]
image: /assets/images/ai-search-cover.jpg
---
```

### Naming Convention (Required)
Posts must follow: `_posts/YYYY-MM-DD-title-slug.md`
Example: `_posts/2026-02-18-ai-search-organic-traffic.md`

Jekyll will not process files that do not follow this naming pattern.

### Image Embedding
```markdown
![Marketing team analyzing search data](/assets/images/search-dashboard.jpg)
```

Images live in `assets/images/` or `images/` depending on project convention.

### Chart / SVG Embedding

Jekyll uses the kramdown renderer, which passes through raw HTML:

```markdown
<figure>
  <svg viewBox="0 0 560 380" role="img" aria-label="AIO CTR rebound chart">
    <!-- SVG content with standard HTML attributes -->
  </svg>
  <figcaption>Source: Seer Interactive (Apr 2026)</figcaption>
</figure>
```

No special configuration needed: kramdown does not strip HTML by default.

### Liquid Templates

Access page variables in layouts:
```liquid
<h1>{{ page.title }}</h1>
<time datetime="{{ page.date | date_to_xmlschema }}">
  {{ page.date | date: "%B %d, %Y" }}
</time>

{% if page.last_modified_at %}
  <meta property="article:modified_time"
        content="{{ page.last_modified_at | date_to_xmlschema }}">
{% endif %}
```

Loop through posts:
```liquid
{% for post in site.posts limit:10 %}
  <article>
    <h2><a href="{{ post.url }}">{{ post.title }}</a></h2>
    <p>{{ post.description }}</p>
  </article>
{% endfor %}
```

### Layout Hierarchy
```
_layouts/
  default.html    <-- Base layout (HTML shell, head, nav, footer)
  post.html       <-- Blog post layout (extends default)
  page.html       <-- Static page layout (extends default)
```

### Math Support via MathJax
```yaml
# _config.yml
markdown: kramdown
kramdown:
  math_engine: mathjax
```

Usage in posts:
```markdown
The formula is $$ E = mc^2 $$
```

### Key Configuration Notes
- `_config.yml` is the central configuration file
- Collections: define custom collections beyond posts in `_config.yml`
- Plugins: `jekyll-seo-tag` for automatic OG/Twitter meta tags
- `jekyll-sitemap` for sitemap generation
- `jekyll-last-modified-at` for automatic `last_modified_at` from git
- Build with `bundle exec jekyll build` (produces `_site/` directory)
- JSON-LD: use `jekyll-seo-tag` or manually include in `_includes/head.html`

---

## WordPress

### Gutenberg Blocks (Modern)

Gutenberg uses block-based editing. Key blocks for blog content:

| Block | Purpose | Notes |
|-------|---------|-------|
| Paragraph | Body text | Each paragraph auto-wraps in `<p>` |
| Heading | H2-H6 | Set level in block toolbar |
| Image | Photos | Set alt text, caption, link in sidebar |
| Custom HTML | SVG charts | Paste only sanitized inline SVG in HTML block |
| List | Bullets/numbers | For FAQ answers, step lists |
| Quote | Blockquotes | For expert quotes with attribution |
| Table | Comparison tables | For feature/pricing comparisons |
| Group | Wrappers | Group blocks for styling |

### Classic Editor (HTML)
```html
<h2>How Does AI Search Impact Organic Traffic?</h2>

<p>AIO organic CTR rebounded from 1.3% in December 2025 to about 2.4%
in February 2026 (<a href="https://seerinteractive.com">Seer Interactive</a>,
April 2026). Treat this vendor observation as methodology-specific,
non-causal research context rather than a citation optimization target.</p>

<figure>
  <img src="/images/blog/topic-hero.jpg"
       alt="Marketing dashboard showing AI search traffic metrics"
       width="1200" height="630" loading="lazy">
  <figcaption>Photo via Pixabay</figcaption>
</figure>
```

### Image Embedding
Upload via Media Library, then insert. Set these fields:
- **Alt text**: Descriptive sentence with topic keywords
- **Title**: Short descriptive title
- **Caption**: Optional, shows below image
- **Featured Image**: Set in post sidebar (used as OG image and blog listing)

### Chart / SVG Embedding
Use the Custom HTML block only after sanitizing the SVG. Apply a strict element
and attribute allowlist, escape text content, and reject `script`,
event-handler attributes such as `onclick`, `foreignObject`, external
references, `javascript:` URLs, `data:` URLs, and remote `<image href>`.
```html
<figure class="wp-block-html chart-container">
  <svg viewBox="0 0 560 380" role="img" aria-label="Chart description">
    <!-- Sanitized SVG with HTML attributes -->
  </svg>
</figure>
```

### Yoast SEO / RankMath Integration

| Field | Where | Purpose |
|-------|-------|---------|
| Focus keyword | SEO panel below editor | Primary target keyword |
| SEO title | SEO panel | Title tag (if different from H1) |
| Meta description | SEO panel | Accurate, page-specific visible-content summary |
| Canonical URL | SEO panel → Advanced | Prevents duplicate content |
| OG image | Social tab in SEO panel | Social sharing preview |
| OG title | Social tab | Title for social shares |
| OG description | Social tab | Description for social shares |

### Custom Fields for Structured Data
Use ACF (Advanced Custom Fields) or native custom fields:
- `last_updated`: for dateModified in schema
- `author_bio`: for E-E-A-T author section
- `faq_items`: for FAQPage entity markup when visible Q&A exists

### Featured Image
Set via the "Featured Image" panel in the post editor sidebar. This image
serves as both the blog listing thumbnail and the OG image for social sharing.
Recommended size: 1200x630px.

### Excerpt Field
The Excerpt field (in post sidebar) generates the meta description if Yoast/
RankMath meta description is empty. Keep it accurate, page-specific, and
consistent with the visible content.

### Key Configuration Notes
- Permalink structure: Settings > Permalinks > Post name (`/%postname%/`)
- REST API: `wp-json/wp/v2/posts` for programmatic publishing
- Schema: Yoast/RankMath auto-generates BlogPosting schema
- Caching: use an appropriate cache and investigate sustained TTFB regressions
- Security: keep WordPress, themes, and plugins updated
- robots.txt: accessible at `/robots.txt`, configure via Yoast

---

## Ghost

### Content Formats
Modern Ghost stores editor content in Lexical JSON and accepts HTML input for
HTML cards and Admin API publishing.

### Ghost Admin API (Programmatic Publishing)
```javascript
const GhostAdminAPI = require('@tryghost/admin-api')

const api = new GhostAdminAPI({
  url: 'https://your-blog.ghost.io',
  key: 'ADMIN_API_KEY',
  version: 'v5.0'
})

api.posts.add({
  title: 'How Does AI Search Impact Organic Traffic in 2026?',
  html: '<p>Measure how AI search features affect organic traffic and reader journeys.</p>',
  status: 'draft',
  tags: [{ name: 'AI Search' }, { name: 'SEO' }],
  meta_title: 'Measuring AI Search Impact on Organic Traffic',
  meta_description: 'A practical guide to measuring AI search features and organic traffic.',
  og_image: '/content/images/topic-hero.jpg',
  og_title: 'AI Search Impact on Organic Traffic',
  og_description: 'A practical guide to AI search features and organic traffic.',
  canonical_url: 'https://your-blog.com/ai-search-organic-traffic',
  feature_image: '/content/images/topic-hero.jpg',
  feature_image_alt: 'Marketing dashboard showing AI search metrics',
})
```

### Image Embedding
In the Ghost editor, use the Image card. For HTML content:
```html
<figure class="kg-card kg-image-card">
  <img class="kg-image"
       src="/content/images/topic-hero.jpg"
       alt="Marketing team analyzing AI search data"
       loading="lazy">
  <figcaption>Photo via Pixabay</figcaption>
</figure>
```

### Chart / SVG Embedding
Use the HTML card in the Ghost editor for sanitized inline SVG only. Apply a
strict element and attribute allowlist, escape text content, and reject
`script`, event-handler attributes such as `onclick`, `foreignObject`,
external references, `javascript:` URLs, `data:` URLs, and remote
`<image href>`.
```html
<figure class="kg-card kg-html-card">
  <svg viewBox="0 0 560 380" role="img" aria-label="Chart description">
    <!-- Sanitized SVG -->
  </svg>
</figure>
```

### Built-in SEO Fields

| Field | Location | Purpose |
|-------|----------|---------|
| Meta title | Post settings > Meta data | Title tag override |
| Meta description | Post settings > Meta data | Accurate page summary |
| Canonical URL | Post settings > Meta data | Duplicate prevention |
| OG image | Post settings > Twitter/Facebook | Social preview image |
| OG title | Post settings > Twitter/Facebook | Social preview title |
| Feature image | Post header | Hero + OG fallback |
| Feature image alt | Post header | Accessibility |
| Excerpt | Post settings > Excerpt | Newsletter + listing text |

### Custom Theme Considerations
Ghost themes use Handlebars templates:
```handlebars
{{! post.hbs }}
<article class="post">
  <h1>{{title}}</h1>
  <time datetime="{{date format='YYYY-MM-DD'}}">{{date format="MMMM DD, YYYY"}}</time>
  {{#if updated_at}}
    <time datetime="{{updated_at format='YYYY-MM-DD'}}">
      Updated: {{updated_at format="MMMM DD, YYYY"}}
    </time>
  {{/if}}
  <div class="post-content">{{content}}</div>
</article>
```

### Dynamic Routing
Configure content organization in `routes.yaml`:
```yaml
routes:
  /about/: about

collections:
  /blog/:
    permalink: /blog/{slug}/
    filter: tag:-hash-podcast
    template: blog

taxonomies:
  tag: /tag/{slug}/
  author: /author/{slug}/
```

### Key Configuration Notes
- Ghost themes often output structured data automatically, but custom and
  headless themes must validate rendered JSON-LD in the final HTML
- Default output is server-rendered HTML: AI crawlers can access content
- Newsletters: Ghost has built-in email sending for subscriber lists
- Membership: tiers and paid content built-in
- Themes: install via Ghost Admin > Settings > Design
- Content API: for headless CMS setups (read-only, public content)

---

## 11ty (Eleventy)

### Frontmatter Format
```yaml
---
title: "How Does AI Search Impact Organic Traffic in 2026?"
description: "A practical guide to measuring how AI search features affect organic traffic and reader journeys."
date: 2026-02-18
lastUpdated: 2026-02-18
author: "Author Name"
tags:
  - ai-search
  - seo
  - posts
layout: post.njk
coverImage: "/images/ai-search-cover.jpg"
coverImageAlt: "Marketing dashboard showing AI search metrics"
---
```

### Template Languages
11ty supports Nunjucks (`.njk`), Liquid (`.liquid`), Handlebars (`.hbs`),
JavaScript (`.11ty.js`), and more. Nunjucks is the most common choice.

### Data Cascade
11ty merges data from multiple sources (highest to lowest priority):
1. **File data**: frontmatter in the content file
2. **Directory data**: `blog.json` in the content directory
3. **Global data**: files in `_data/` directory

```json
// blog/blog.json (applies to all files in blog/)
{
  "layout": "post.njk",
  "tags": ["posts"],
  "permalink": "/blog/{{ page.fileSlug }}/"
}
```

### Image Embedding
```markdown
![Marketing team analyzing search data](/images/search-dashboard.jpg)
```

For optimized images, use `eleventy-img` plugin:
```njk
{% image "src/images/search-dashboard.jpg", "Marketing team analyzing search data" %}
```

### Chart / SVG Embedding
Raw HTML/SVG works directly in markdown files. 11ty passes through HTML
without stripping.

```markdown
<figure>
  <svg viewBox="0 0 560 380" role="img" aria-label="AIO CTR rebound chart">
    <!-- SVG content -->
  </svg>
  <figcaption>Source: Seer Interactive (Apr 2026)</figcaption>
</figure>
```

### Computed Data for Dates and URLs
```javascript
// blog/blog.11tydata.js
module.exports = {
  eleventyComputed: {
    permalink: (data) => `/blog/${data.page.fileSlug}/`,
    lastUpdatedDisplay: (data) => {
      const date = data.lastUpdated || data.page.date
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric', month: 'long', day: 'numeric'
      })
    }
  }
}
```

### Passthrough File Copy
```javascript
// .eleventy.js
module.exports = function(eleventyConfig) {
  eleventyConfig.addPassthroughCopy("src/images")
  eleventyConfig.addPassthroughCopy("src/svg")
  eleventyConfig.addPassthroughCopy({ "src/favicon.ico": "/" })
}
```

### Key Configuration Notes
- Static output by default: ideal for AI crawlers
- No build-step JS unless explicitly added (fast pages)
- Collections: use `tags` in frontmatter to group content
- Filters: add custom Nunjucks filters in `.eleventy.js` for date formatting
- Pagination: built-in for tag pages and archive pages
- JSON-LD: inject via layout template using frontmatter data
- Sitemap: use `eleventy-plugin-sitemap` or generate manually

---

## Gatsby

### Frontmatter Format
```yaml
---
title: "How Does AI Search Impact Organic Traffic in 2026?"
description: "A practical guide to measuring how AI search features affect organic traffic and reader journeys."
date: "2026-02-18"
lastUpdated: "2026-02-18"
author: "Author Name"
tags: ["ai-search", "seo", "traffic"]
slug: "ai-search-organic-traffic"
featuredImage: "../images/ai-search-cover.jpg"
featuredImageAlt: "Marketing dashboard showing AI search metrics"
---
```

### MDX Support
```javascript
// gatsby-config.js
module.exports = {
  plugins: [
    {
      resolve: 'gatsby-plugin-mdx',
      options: {
        extensions: ['.mdx', '.md'],
        gatsbyRemarkPlugins: [
          'gatsby-remark-images',
          'gatsby-remark-prismjs',
        ],
      },
    },
  ],
}
```

### Image Embedding
```mdx
![Marketing team analyzing search data](../images/search-dashboard.jpg)
```

Using `gatsby-plugin-image`:
```jsx
import { GatsbyImage, getImage } from 'gatsby-plugin-image'

const BlogPost = ({ data }) => {
  const image = getImage(data.mdx.frontmatter.featuredImage)
  return (
    <GatsbyImage
      image={image}
      alt={data.mdx.frontmatter.featuredImageAlt}
    />
  )
}
```

### Chart / SVG Embedding
In MDX files, use JSX-compatible SVG (same camelCase rules as Next.js):
```mdx
<figure style={{margin: '2.5rem 0', textAlign: 'center'}}>
  <svg viewBox="0 0 560 380" role="img" aria-label="CTR chart">
    <text x="280" y="30" textAnchor="middle" fontSize="16" fill="currentColor">
      Chart Title
    </text>
  </svg>
</figure>
```

### GraphQL Data Layer
```graphql
query BlogPostBySlug($slug: String!) {
  mdx(frontmatter: { slug: { eq: $slug } }) {
    body
    frontmatter {
      title
      description
      date(formatString: "MMMM DD, YYYY")
      lastUpdated(formatString: "MMMM DD, YYYY")
      tags
      featuredImage {
        childImageSharp {
          gatsbyImageData(width: 1200, placeholder: BLURRED)
        }
      }
    }
  }
}
```

### createPages API for Dynamic Routes
```javascript
// gatsby-node.js
const path = require('path')
const blogPostTemplate = path.resolve('./src/templates/blog-post.tsx')

exports.createPages = async ({ graphql, actions }) => {
  const { createPage } = actions
  const result = await graphql(`
    query {
      allMdx {
        nodes {
          id
          frontmatter { slug }
          internal { contentFilePath }
        }
      }
    }
  `)

  result.data.allMdx.nodes.forEach((node) => {
    createPage({
      path: `/blog/${node.frontmatter.slug}`,
      component: `${blogPostTemplate}?__contentFilePath=${node.internal.contentFilePath}`,
      context: { id: node.id },
    })
  })
}
```

### Key Configuration Notes
- Static output at build time: AI crawlers get full HTML
- Use `gatsby-plugin-sitemap` for sitemap generation
- Use `gatsby-plugin-robots-txt` for robots.txt configuration
- `gatsby-plugin-react-helmet` or Gatsby Head API for meta tags
- JSON-LD: use `gatsby-plugin-schema-snapshot` or inline in Head component
- Build can be slow for large sites: consider incremental builds

---

## HTML / Static

### Semantic HTML5 Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>How Does AI Search Impact Organic Traffic in 2026?</title>
  <meta name="description" content="A practical guide to measuring how AI search features affect organic traffic and reader journeys.">

  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:title" content="How Does AI Search Impact Organic Traffic in 2026?">
  <meta property="og:description" content="A practical guide to AI search features and organic traffic.">
  <meta property="og:image" content="/images/blog/topic-hero.jpg">
  <meta property="og:url" content="https://yourblog.com/ai-search-organic-traffic">
  <meta property="article:published_time" content="2026-02-18T00:00:00Z">
  <meta property="article:modified_time" content="2026-02-18T00:00:00Z">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="How Does AI Search Impact Organic Traffic in 2026?">
  <meta name="twitter:description" content="A practical guide to AI search features and organic traffic.">
  <meta name="twitter:image" content="/images/blog/topic-hero.jpg">

  <!-- JSON-LD Structured Data -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "How Does AI Search Impact Organic Traffic in 2026?",
    "description": "A practical guide to AI search features and organic traffic.",
    "image": "/images/blog/topic-hero.jpg",
    "datePublished": "2026-02-18",
    "dateModified": "2026-02-18",
    "author": {
      "@type": "Person",
      "name": "Author Name",
      "url": "https://yourblog.com/about"
    },
    "publisher": {
      "@type": "Organization",
      "name": "Blog Name",
      "logo": {
        "@type": "ImageObject",
        "url": "https://yourblog.com/logo.png"
      }
    },
    "mainEntityOfPage": {
      "@type": "WebPage",
      "@id": "https://yourblog.com/ai-search-organic-traffic"
    }
  }
  </script>
</head>
<body>
  <nav aria-label="Main navigation">
    <!-- Navigation -->
  </nav>

  <article>
    <header>
      <h1>How Does AI Search Impact Organic Traffic in 2026?</h1>
      <time datetime="2026-02-18">February 18, 2026</time>
    </header>

    <section>
      <h2>What Is the Impact of AI Overviews on Click-Through Rates?</h2>
      <p>AIO organic CTR rebounded from 1.3% in December 2025 to about 2.4%
      in February 2026 (<a href="https://seerinteractive.com">Seer Interactive</a>,
      April 2026). This vendor observation is methodology-specific and
      non-causal; it does not prescribe citation format or position.</p>

      <figure>
        <img src="/images/blog/topic-hero.jpg"
             alt="Marketing dashboard showing AI search CTR metrics"
             width="1200" height="630" loading="lazy">
        <figcaption>Photo via Pixabay</figcaption>
      </figure>
    </section>

    <aside aria-label="Frequently Asked Questions">
      <h2>Frequently Asked Questions</h2>
      <!-- FAQ content -->
    </aside>
  </article>

  <footer>
    <!-- Footer -->
  </footer>
</body>
</html>
```

### Image Embedding
```html
<figure>
  <img src="/images/blog/topic-hero.jpg"
       alt="Descriptive sentence including topic keywords naturally"
       width="1200" height="630"
       loading="lazy"
       decoding="async">
  <figcaption>Photo via Pixabay</figcaption>
</figure>
```

### Chart / SVG Embedding
```html
<figure>
  <svg viewBox="0 0 560 380"
       style="max-width: 100%; height: auto; font-family: 'Inter', system-ui, sans-serif"
       role="img"
       aria-label="Chart showing AIO organic CTR rebound from 1.3% to about 2.4%">
    <title>AIO Organic CTR Rebound</title>
    <desc>Bar chart comparing the December 2025 AIO CTR floor to the February 2026 rebound</desc>
    <!-- SVG content with standard HTML attributes -->
  </svg>
  <figcaption>Source: Seer Interactive (Apr 2026)</figcaption>
</figure>
```

### Inline JSON-LD Schema

Place in `<head>` for BlogPosting:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Title",
  "datePublished": "2026-02-18",
  "dateModified": "2026-02-18",
  "author": { "@type": "Person", "name": "Author" }
}
</script>
```

Place in `<head>` for FAQPage only when visible Q&A exists. It is entity
support for AI citation, not a Google rich result:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is the question?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The visible answer text with a specific statistic and source."
      }
    }
  ]
}
</script>
```

### Key Configuration Notes
- No framework dependency: works with any hosting
- Static HTML gives non-JavaScript crawlers the broadest access
- Manually manage OG/Twitter meta tags in `<head>`
- Use `loading="lazy"` and `decoding="async"` on images for performance
- Prefer schema in source HTML for portability. For Google, JavaScript-generated
  JSON-LD is acceptable when present in the rendered DOM, consistent with
  visible content, and validated.
- Generate sitemap.xml manually or with a build script
- Use `<link rel="canonical" href="...">` to prevent duplicate content
- Place CSS in `<head>` (inline critical CSS for fast TTFB)

---

## Platform Selection Quick Reference

| Priority | Criterion | Recommendation |
|----------|-----------|---------------|
| AI crawlers | JS execution required? | Use SSG/SSR (Next.js, Astro, Hugo, 11ty, Gatsby) |
| Speed | Measured response reliability | Compare platforms against the site's tested performance budget |
| MDX/React | Component-driven content | Next.js, Gatsby |
| Simplicity | Minimal tooling | Hugo, Jekyll, 11ty, static HTML |
| Non-technical users | Visual editor | WordPress, Ghost |
| Headless CMS | API-first | Ghost (Content API), WordPress (REST API) |

### Cross-Platform Checks

1. **Static or server-rendered primary content**: preferred for broad crawler
   compatibility because JavaScript support varies by crawler
2. **Response reliability**: treat TTFB and timeouts as measured operational
   diagnostics, not universal crawler thresholds
3. **Schema available to the target crawler**: prefer source/SSR for portability;
   Google also accepts rendered-DOM JavaScript JSON-LD that matches visible
   content and validates
4. **robots.txt aligned with declared goals**: allow or block crawlers according
   to current policy, product goals, and applicable crawler documentation
5. **Sitemap at /sitemap.xml**: helps all crawlers discover content
6. **OG meta tags**: required for social sharing previews
7. **Truthful dateModified in schema**: update it only after substantive content changes; it is not a score or freshness shortcut
