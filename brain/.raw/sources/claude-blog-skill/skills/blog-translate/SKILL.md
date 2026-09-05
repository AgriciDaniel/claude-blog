---
name: blog-translate
description: >
  Translate existing blog posts into one or more target languages with
  SEO-optimized localization. Produces native-quality translations that
  preserve markdown structure, frontmatter, schema JSON-LD, image and chart
  embeds, and citation capsules. Localizes keywords, meta tags, numbers,
  dates, currencies, and quote styles per locale. Flags machine-translation
  artifacts for review. Run BEFORE blog-localize: this handles language
  conversion; localize handles cultural adaptation after translation
  completes.
  Use when user says "translate blog", "blog translate", "uebersetzen",
  "traduire", "traducir", "translate post", "blog auf Deutsch", "blog en
  espanol".
user-invokable: true
argument-hint: "<file> --to <comma-separated-codes>"
license: MIT
compatibility: Standalone within claude-blog. Invoked by blog-multilingual.
metadata:
  author: AgriciDaniel
  version: "1.11.0"
  category: blog
---

# Blog Translate, SEO-Optimized Blog Translation

Translates an existing blog post into one or more target languages. Unlike
generic translation, this skill produces SEO-optimized, publication-ready
content with localized keywords, meta tags, and culturally correct
formatting.

> Adapted from `claude-blog-multilingual` by Chris Mueller (Pro Hub Challenge,
> March 2026). Original: https://github.com/Chriss54/multilingual-int

## Key References

Load on demand:

- `references/translation-rules.md`, format preservation, number/date/currency
  formats per locale, quote handling, quality criteria.
- `references/cultural-adaptation.md`, cultural profiles per locale (DACH,
  Francophone, Hispanic, Japanese, custom). This file is shared with
  `blog-localize` (do not duplicate).

## Workflow

### Phase 1: Input Parsing

1. Read the source file (markdown, MDX, or HTML) only after resolving it
   against the project root/current working directory. Reject symlinked paths,
   traversal outside the root, files over 10 MB, and binary files.
2. Auto-detect source language. Order of preference:
   - Frontmatter `lang` field.
   - HTML `lang` attribute.
   - Content analysis (script, common stop words).
3. Parse target languages from `--to` as comma-separated Google-compatible
   hreflang tags (`de`, `fr`, `es-MX`, `ja`, `pt-BR`, `zh-Hant`).
   If `--to` is missing, ask the user once: "Which languages should I
   translate to? Provide hreflang tags such as de, fr, es-MX, ja, pt-BR."
4. Normalize every code with the shared multilingual locale rules used by
   `blog-multilingual`, `blog-localize`, and `blog-locale-audit`: ISO 639-1
   language in lowercase, optional ISO 15924 script in title case, optional
   ISO 3166-1 Alpha-2 region in uppercase. Reject invalid codes with a
   suggestion (`jp` becomes "Did you mean `ja` for Japanese?"). Require a
   region or explicit neutral mode for ambiguous language-only targets such as
   `es`, `pt`, and `zh`. If a target equals the normalized source language,
   skip it with a notice.

### Phase 2: Content Analysis

Extract the translatable surface:

- Frontmatter: `title`, `description`, `tags`, `author` (only when
  translatable, e.g. role labels, not personal names).
- All headings (H1, H2, H3).
- Body paragraphs.
- Image `alt` text and `<figcaption>` content.
- Chart `<text>` and `<tspan>` content; preserve every SVG attribute (`x`,
  `y`, `font-size`, `fill`, `transform`).
- FAQ questions and answers.
- Citation capsule text.
- Key Takeaways or summary box.
- CTA text.
- Internal-link zone anchor text.

Preserve unchanged:

- Markdown and HTML structure, tags, attributes.
- Image URLs, link URLs, frontmatter keys.
- Executable code fences and inline code. Translate comments only outside
  executable code, or when the user explicitly asks for localized tutorial
  comments.
- Internal-link zone markers (`[INTERNAL-LINK: ...]`).
- Source organization names in citations (Gartner, McKinsey, etc.).
- Person names.
- Schema JSON-LD blocks (translate user-facing content strings only; never
  translate Person, Organization, or Brand names, URLs, IDs, `@id`, or
  `sameAs`).

Identify the primary and secondary keywords for Phase 3.

### Phase 3: Keyword Localization

For each target language:

1. Decide whether the source keyword is the established term in the target
   market. If yes (e.g., "Content Marketing" stays in German), keep it.
2. If a local equivalent has real search behavior, swap to it.
3. Apply the same logic to secondary keywords.
4. Record the mapping. The translator agent uses it to update title, meta
   description, and H2 headings consistently.

### Phase 4: Translation

Spawn the `blog-translator` agent (via Task) for each target language with:

- The source content.
- The keyword localization map from Phase 3.
- The target language code.
- Pointer to `references/translation-rules.md`.
- Instruction to limit this phase to language, register, natural topical
  coverage, and formatting. Reserve brand, legal, statistic, and cultural
  substitutions for `blog-localize`.

Run agents in parallel when translating into multiple languages.

The agent returns the fully translated post in the same format as the input.

### Phase 5: Post-Processing

For each translated version:

1. Add or update locale frontmatter:
   ```yaml
   lang: "de"
   translatedFrom: "en"
   translatedDate: "YYYY-MM-DD"
   slug: "wie-man-ki-slop-vermeidet"
   ```
2. Verify structural integrity:
   - Same number of H2 and H3 sections as the original.
   - All images present with translated alt text.
   - All SVG charts present with translated text labels (length-adjusted:
     DE +30%, FR +15%, JA -20%, others see `references/translation-rules.md`).
   - FAQ count matches.
   - Citation capsules present in each H2.
3. Save translated files:
   ```
   translations/
     {lang}/{localized-slug}.{ext}
   ```
   When invoked from `blog-multilingual`, save into
   `multilingual/{lang}/{localized-slug}.{ext}` instead.
   Before writing, slugify `{localized-slug}` to lowercase ASCII with only
   `a-z`, `0-9`, and hyphens, rejecting empty or reserved names. Create the
   language directory from the normalized hreflang code only. Resolve the
   final path and require it to stay inside the intended output root; reject
   symlinked output paths.

### Phase 6: Translation-Quality Guardrails

Scan the output for machine-translation artifacts before reporting done:

- Literal idioms (English idioms transliterated, not adapted).
- Unnatural word order (SOV translated as SVO into a non-SVO language, or
  the reverse).
- Mixed-language sentences (other than established loanwords).
- Number, date, or currency strings still in source format.
- Frontmatter strings still in the source language.

Flag every issue inline (file path, line number, fix suggestion). The
translator agent should re-pass any flagged passage before delivery.

### Phase 7: Delivery

```
## Translation complete: [Original title]

### Source
- Language: [source]
- File: [source path]

### Translations
| Language | File | Keywords adapted | Status |
|----------|------|------------------|--------|
| de | translations/de/{slug}.md | [N] | ok |
| fr | translations/fr/{slug}.md | [N] | ok |

### Quality checks
- Structural integrity: pass / fail per language
- Meta tags localized: pass / fail per language
- Numbers, dates, currencies formatted per locale: pass / fail
- Keywords localized: [N] keywords adapted
- Machine-translation artifacts flagged: [N] (see notes above)

### Next steps
- Run `/blog localize <file> --locale <code>` for cultural deep-adaptation.
- Run `/blog locale-audit translations/` to verify completeness.
- Use `/blog multilingual` to combine write, translate, localize, hreflang
  in one command.
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Unsupported language code | Suggest the correct Google-compatible hreflang code |
| Source equals a target | Skip with "Source is already in [lang]" |
| File not found | Report error with suggested path |
| Translator agent timeout | Retry once, then report partial results |
| Binary or non-text file | Report error, suggest correct file |

## Cross-References

- Next step (cultural depth): `/blog localize <file> --locale <code>`
- QA sweep across all language versions: `/blog locale-audit <directory>`
- One-command pipeline: `/blog multilingual <topic> --languages <codes>`
