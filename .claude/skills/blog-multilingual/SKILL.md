---
name: blog-multilingual
description: >
  One-command multilingual blog creation. Writes a blog post, translates it
  into user-specified languages, applies cultural adaptation, and emits
  hreflang tags, sitemap entries, and a CMS-ready language map. The complete
  write-to-publish pipeline for international content. Orchestrates blog-write,
  blog-translate, blog-localize, and (optionally) seo-hreflang.
  Use when user says "multilingual blog", "blog multilingual", "write in
  multiple languages", "international blog", "mehrsprachiger Blog", "blog
  multilingue", "blog multilingue", "create blog in German and French".
user-invokable: true
argument-hint: "<topic> --languages <comma-separated-codes>"
license: MIT
compatibility: Requires claude-blog (blog-write). Optional integration with claude-seo (seo-hreflang) for richer hreflang validation.
metadata:
  author: AgriciDaniel
  version: "2.1.1"
  category: blog
---

# Blog Multilingual, One-Command International Publishing

The flagship multilingual orchestrator. Combines blog writing, translation,
cultural adaptation, and full international SEO into a single command.
Produces publication-ready blog posts in every target language with hreflang
tags, localized JSON-LD schema, and CMS-integration metadata.

> Adapted from `claude-blog-multilingual` by Chris Mueller (AI Marketing Hub
> Pro Hub Challenge submission, March 2026, scored 85/100 Proficient).
> Original: https://github.com/Chriss54/multilingual-int
> This port removes the original `curl | bash` installer and credential
> handling flagged in the audit, integrates as core skills, and uses the
> shared cultural-adaptation reference under `blog-translate/references/`.

## Dependencies

Invoked internally by this orchestrator:

| Component | Source | Required |
|-----------|--------|----------|
| `blog-write` | claude-blog (this plugin) | Yes |
| `blog-translate` | claude-blog (this plugin) | Yes |
| `blog-localize` | claude-blog (this plugin) | Yes (when `--localize` is on, default) |
| `seo-hreflang` | claude-seo (sibling plugin) | No, falls back to a self-contained generator |

If `seo-hreflang` is not installed, the orchestrator emits hreflang tags using
its own minimal generator (Phase 5 below) and notes the limitation in the
delivery summary. Hreflang validation in that case is structural only, not the
deeper validation `seo-hreflang` provides.

## Command Syntax

```
/blog multilingual <topic> --languages <lang1,lang2,...> [--source <lang>] [--no-localize] [--format <md|mdx|html>]
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `<topic>` | Yes | required | Blog topic or working title |
| `--languages` | Yes | required | Comma-separated Google-compatible hreflang tags (e.g. `de,fr,es-MX,ja,pt-BR`) |
| `--source` | No | `en` | Source language to write the original in |
| `--no-localize` | No | off | Skip cultural adaptation (translation only) |
| `--format` | No | auto | Output format: `md`, `mdx`, or `html` |

If `--languages` is missing, ask the user once before running anything:
"Which languages should the blog be published in? Provide hreflang tags
separated by commas (e.g., `de,fr,es-MX,ja,pt-BR`). The post will be written
in `<source>` first, then translated."

## Workflow

### Phase 1: Configuration

1. Parse arguments. Extract topic, target languages, source, format.
2. Validate each language code with the shared multilingual locale rules used
   by `blog-translate`, `blog-localize`, and `blog-locale-audit`: ISO 639-1
   language in lowercase, optional ISO 15924 script in title case, optional
   ISO 3166-1 Alpha-2 region in uppercase. Require a region or explicit
   neutral mode for ambiguous language-only targets such as `es`, `pt`, and
   `zh`.
3. Detect output format from the project (frontmatter convention, file
   extensions, framework hints) or use `--format`.
4. Resolve source language. If a target language equals `--source`, drop it
   from the translation list with a notice.
5. Create the output directory inside the current working directory:
   ```
   multilingual/
     {source-lang}/
     {lang-1}/
     {lang-2}/
     ...
   ```
   Keep all output inside the project root; do not write outside the cwd.

Progress: `Phase 1: Configuration complete, [N] languages selected ([codes])`

### Phase 2: Write Original Blog

Invoke the `blog-write` sub-skill (route through `/blog write` so all
existing rules apply: template auto-selection, sourced statistics, citation
capsules, Article schema priority, FAQPage only as an entity signal when
visible FAQ content exists, internal-link zones, charts, image embedding). Pass the
topic and any blog-write parameters surfaced by the user.

Save the original to `multilingual/{source-lang}/{slug}.{ext}`.

Progress: `Phase 2: Original written, multilingual/{source-lang}/{slug}.{ext}`

### Phase 3: Translate to All Target Languages

For each target language, invoke `blog-translate`:

- Input: the original blog post produced in Phase 2.
- Target: the specific language code.
- Run targets in parallel where the runtime supports it (one Task per
  language) to reduce wall-clock time.

Save translations to `multilingual/{lang}/{localized-slug}.{ext}`.

Progress: `Phase 3: Translating to [lang] ([X]/[N])` per language, then
`Phase 3: All translations complete`.

### Phase 4: Cultural Adaptation

If `--no-localize` is NOT set, invoke `blog-localize` for every translated
post:

- Input: the translated blog post.
- Locale: the target language or region code.
- Run in parallel.

Apply the localized output only after resolving the generated path inside
`multilingual/`, rejecting symlinks, and creating a backup when overwriting.
The localizer swaps brand examples, adapts CTAs, substitutes legal
references, and adjusts formality. See
`../blog-localize/SKILL.md` for the full adaptation pass.

Progress: `Phase 4: Cultural adaptation complete for [N] languages`.

### Phase 5: International SEO Generation

Generate three artifacts plus localized schema. If the `seo-hreflang` skill
from claude-seo is installed, delegate validation to it. Otherwise use the
self-contained generator below.

#### 5a. Hreflang Tags (HTML)

Copy-paste ready tags for `<head>`:

```html
<!-- Hreflang tags. Paste into <head> of each language version. -->
<link rel="alternate" hreflang="{source}" href="https://example.com/{source-url}" />
<link rel="alternate" hreflang="{lang-1}" href="https://example.com/{lang-1-url}" />
<link rel="alternate" hreflang="{lang-2}" href="https://example.com/{lang-2-url}" />
<link rel="alternate" hreflang="x-default" href="https://example.com/{fallback-url}" />
```

Rules (mirrored from `seo-hreflang`):

- Every page references all alternates including itself (self-referencing).
- Every `href`, including `x-default`, is a fully qualified absolute
  `https://...` URL.
- `x-default` points to the unmatched-language fallback, such as a global
  language selector or default market page. It does not have to be the source
  language version.
- All URLs use the same protocol (HTTPS) and trailing-slash convention.
- Bidirectional: every relationship is reciprocal.

Save to `multilingual/hreflang-tags.html`.

#### 5b. Hreflang Sitemap Fragment

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://example.com/{source-url}</loc>
    <xhtml:link rel="alternate" hreflang="{source}" href="https://example.com/{source-url}" />
    <xhtml:link rel="alternate" hreflang="{lang-1}" href="https://example.com/{lang-1-url}" />
    <xhtml:link rel="alternate" hreflang="{lang-2}" href="https://example.com/{lang-2-url}" />
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/{fallback-url}" />
  </url>
  <url>
    <loc>https://example.com/{lang-1-url}</loc>
    <xhtml:link rel="alternate" hreflang="{source}" href="https://example.com/{source-url}" />
    <xhtml:link rel="alternate" hreflang="{lang-1}" href="https://example.com/{lang-1-url}" />
    <xhtml:link rel="alternate" hreflang="{lang-2}" href="https://example.com/{lang-2-url}" />
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/{fallback-url}" />
  </url>
  <url>
    <loc>https://example.com/{lang-2-url}</loc>
    <xhtml:link rel="alternate" hreflang="{source}" href="https://example.com/{source-url}" />
    <xhtml:link rel="alternate" hreflang="{lang-1}" href="https://example.com/{lang-1-url}" />
    <xhtml:link rel="alternate" hreflang="{lang-2}" href="https://example.com/{lang-2-url}" />
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/{fallback-url}" />
  </url>
</urlset>
```

Generate one `<url>` block per locale. Every block must contain the identical
complete set of `<xhtml:link>` alternates for every locale, plus self and
optional `x-default`, using fully qualified `https://...` URLs.

Save to `multilingual/hreflang-sitemap.xml`.

#### 5c. Hreflang Map (JSON)

Machine-readable mapping for CMS integration:

```json
{
  "sourceSlug": "how-to-avoid-ai-slop",
  "sourceLanguage": "en",
  "generatedDate": "YYYY-MM-DD",
  "versions": [
    {
      "lang": "en",
      "locale": "en",
      "hreflang": "en",
      "slug": "how-to-avoid-ai-slop",
      "file": "en/how-to-avoid-ai-slop.md",
      "url": "https://example.com/en/how-to-avoid-ai-slop/",
      "canonical": "https://example.com/en/how-to-avoid-ai-slop/",
      "xDefault": true,
      "title": "How to Avoid AI Slop in 2026",
      "description": "..."
    },
    {
      "lang": "de",
      "locale": "de-DE",
      "hreflang": "de-DE",
      "slug": "wie-man-ki-slop-vermeidet",
      "file": "de/wie-man-ki-slop-vermeidet.md",
      "url": "https://example.com/de/wie-man-ki-slop-vermeidet/",
      "canonical": "https://example.com/de/wie-man-ki-slop-vermeidet/",
      "xDefault": false,
      "title": "KI-Slop vermeiden in 2026",
      "description": "..."
    }
  ],
  "hreflang": {
    "method": "html",
    "x-default": "https://example.com/"
  }
}
```

Save to `multilingual/hreflang-map.json`.

#### 5d. Localized Article Schema (Required)

Attach or update Article/BlogPosting JSON-LD on every language version with
`inLanguage` and `translationOfWork` fields:

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "[Localized title]",
  "description": "[Localized description]",
  "inLanguage": "[lang-code]",
  "isPartOf": { "@type": "Blog", "inLanguage": "[lang-code]" },
  "translationOfWork": {
    "@type": "BlogPosting",
    "inLanguage": "[source-lang]",
    "url": "[source-url]"
  }
}
```

Use the existing `/blog schema` sub-skill for richer schema on each version.
Keep Article/BlogPosting, Person, Organization, and BreadcrumbList as the
priority stack. FAQPage is optional and only for visible FAQ content as an
entity and AI-citation signal, not a Google rich result target.

### Phase 6: Delivery Summary

```
## Multilingual blog complete: [Title]

### Original
- Language: [source]
- File: multilingual/{source}/{slug}.{ext}

### Translations
| Language | File | Localized | Keywords adapted |
|----------|------|-----------|------------------|
| de | multilingual/de/{slug}.md | yes | [N] |
| fr | multilingual/fr/{slug}.md | yes | [N] |
| es | multilingual/es/{slug}.md | yes | [N] |

### International SEO assets
- multilingual/hreflang-tags.html
- multilingual/hreflang-sitemap.xml
- multilingual/hreflang-map.json
- Localized Article schema embedded per version

### Total
- [N] posts in [N] languages
- [N] SEO assets generated

### Next steps
- Replace `{source-url}`, `{lang-1-url}`, `{lang-2-url}`, and
  `{fallback-url}` placeholders in hreflang tags with real absolute HTTPS
  URLs.
- Merge `hreflang-sitemap.xml` into your existing sitemap.
- Run `/blog locale-audit multilingual/` to verify completeness.
- Resolve `[INTERNAL-LINK]` placeholders with locale-specific URLs.
- If claude-seo is installed, run `/seo hreflang multilingual/` for
  deeper validation.
```

## Cross-References

| When | Run |
|------|-----|
| To regenerate or reword the source | `/blog write <topic>` |
| To translate one existing file only | `/blog translate <file> --to <codes>` |
| To deepen cultural fit on one file | `/blog localize <file> --locale <code>` |
| To audit a multilingual directory | `/blog locale-audit <directory>` |
| For deeper hreflang validation | `/seo hreflang <directory>` (claude-seo, optional) |

## Error Handling

| Scenario | Action |
|----------|--------|
| `blog-write` missing | Error: "This skill requires `blog-write`. Reinstall claude-blog." |
| One translation fails | Complete the rest, report partial results, suggest a retry command |
| Source language equals a target | Skip that target, log a notice |
| 10 or more target languages | Stop before writing. Explain scaled-content-abuse risk and require reviewed batches of at most 9 target languages |
| `seo-hreflang` not installed | Use the self-contained generator, note it in the summary |

## Commands Recap

| Command | Purpose |
|---------|---------|
| `/blog multilingual <topic> --languages de,fr,es` | Write source, translate, localize, emit hreflang assets |
| `/blog translate <file> --to de,fr,es` | Translate one file into target languages |
| `/blog localize <file> --locale de-DE` | Cultural deep-adaptation of one translated file |
| `/blog locale-audit <directory>` | Multilingual QA across a directory |
