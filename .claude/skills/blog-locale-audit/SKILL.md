---
name: blog-locale-audit
description: >
  Audit a directory of multilingual blog content for completeness, consistency,
  hreflang correctness, meta-tag parity, and freshness. Builds a translation
  coverage matrix, flags stale translations, validates hreflang and schema,
  and emits a prioritized report with runnable fix commands.
  Use when user says "locale audit", "blog locale-audit", "check translations",
  "multilingual audit", "translation check", "hreflang check",
  "Uebersetzungen pruefen".
user-invokable: true
argument-hint: "<directory>"
license: MIT
compatibility: Standalone within claude-blog. Optional richer hreflang validation via claude-seo seo-hreflang.
metadata:
  author: AgriciDaniel
  version: "2.1.1"
  category: blog
---

# Blog Locale Audit, Multilingual Quality Control

Audits a directory of multilingual blog content to ensure every language
version is complete, consistent, correctly tagged, and SEO-optimized.
Catches international content issues before they hurt rankings.

> Adapted from `claude-blog-multilingual` by Chris Mueller (Pro Hub Challenge,
> March 2026). Original: https://github.com/Chriss54/multilingual-int

## Workflow

### Phase 1: Discovery

1. Resolve the target directory inside the project root/current working
   directory. Reject symlinked directories and traversal outside the root,
   then scan blog content and group posts by language using:
   - Subdirectory names (`en/`, `de/`, `fr/`).
   - Frontmatter `lang` and `translatedFrom` fields.
   - `hreflang-map.json` if present.
2. Normalize detected language codes with the shared multilingual locale rules
   used by `blog-translate`, `blog-localize`, and `blog-multilingual`: ISO
   639-1 language in lowercase, optional ISO 15924 script in title case,
   optional ISO 3166-1 Alpha-2 region in uppercase. Flag ambiguous
   language-only codes such as `es`, `pt`, and `zh` unless the content
   declares an explicit neutral mode.
3. Build a content matrix mapping which post exists in which languages. Use a
   stable translation-group key before comparing slugs: `translationGroupId`,
   `sourceSlug`, schema `translationOfWork.url`, or the IDs and URLs in
   `hreflang-map.json`. Fall back to normalized source slug only when no
   stable key exists.
4. Detect the source language (most common `translatedFrom` target, or the
   `sourceLanguage` field in `hreflang-map.json` if present).

### Phase 2: Completeness Audit

Show which translations are missing:

```
### Translation coverage matrix

| Post (EN) | DE | FR | ES | JA |
|-----------|----|----|----|----|
| how-to-avoid-ai-slop | ok | ok | missing | missing |
| content-marketing-2026 | ok | missing | ok | missing |

Coverage: 60% (6 of 10 expected translations present)
Missing: 4 translations needed
```

### Phase 3: Content Parity Audit

For every post that exists in multiple languages:

| Check | What | Severity |
|-------|------|----------|
| Section count | Same number of H2 and H3 sections | Critical |
| FAQ count | Same number of FAQ items | High |
| Image count | Same number of images | High |
| Chart count | Same number of charts (SVG figures) | High |
| Word count ratio | Within expected band for language pair (DE +20% to +30%, JA -20%, ES +10%) | Medium |
| Link count | Similar internal and external link counts | Medium |
| Evidence-backed claims | Same supported claims and citations across versions | Medium |
| Frontmatter parity | All required fields present per version | High |

Flag every significant deviation as an issue.

### Phase 4: SEO Parity Audit

For every language version verify:

| Element | Check | Severity |
|---------|-------|----------|
| Title tag | Present, localized, clear, and appropriate for the page | Critical |
| Meta description | Present, localized, accurate, and consistent with visible content | Critical |
| `lang` attribute or frontmatter `lang` | Present, valid Google-compatible hreflang or BCP 47 language tag | Critical |
| Canonical URL | Points to the same-language page, not the source-language page or x-default | Critical |
| Schema `inLanguage` | Matches `lang` | High |
| Schema `translationOfWork` | Points to the source URL | High |
| Alt text | Translated (no English alt in non-EN posts) | High |
| Slug | Localized (no English slug in non-EN posts) | Medium |
| Tags | Localized | Medium |
| Keywords | Localized | Medium |

### Phase 5: Hreflang Audit

If `hreflang-tags.html`, `hreflang-sitemap.xml`, or `hreflang-map.json`
exists in the directory:

| Check | What | Severity |
|-------|------|----------|
| Self-referencing | Each page references itself | Critical |
| Return tags | Every relationship is bidirectional | Critical |
| Canonical consistency | Every hreflang page canonicalizes to its same-language URL | Critical |
| `x-default` | Present, points to the unmatched-language fallback such as a language selector or default market page | Critical |
| Language codes | Valid Google-compatible hreflang tags: ISO 639-1 language plus optional ISO 15924 script or ISO 3166-1 Alpha-2 region | High |
| URL consistency | Same protocol, same trailing-slash convention | Medium |
| Completeness | Every language version represented | High |

If no hreflang files exist, report it as a critical gap and offer:
"Run `/blog multilingual <topic> --languages ...` to regenerate, or create
hreflang-tags.html manually."

If `seo-hreflang` from claude-seo is installed, suggest running it for
deeper validation.

### Phase 6: Freshness Audit

For posts with `translatedDate` in frontmatter:

| Check | What | Severity |
|-------|------|----------|
| Source updated after translation | Source modified after `translatedDate` | Critical |
| Source content drift | Stored source hash or source `dateModified` differs from current source | Critical |
| Translation drift | Stored translation hash differs from current localized file | Medium |
| Translation older than 90 days | May need refresh | Medium |
| `lastUpdated` mismatch across versions | Versions out of sync | Medium |
| Git or file mtime newer than `translatedDate` | Content changed without frontmatter update | Warning |

When available, store and compare `sourceHash`, source `dateModified`,
`translationHash`, and Git mtime before relying only on `translatedDate`.

Emit actionable commands per stale file:

```
3 translations are stale:
- de/ki-trends-2026.md (source updated 2 days ago)
  -> Run: /blog translate en/ai-trends-2026.md --to de
- fr/ki-trends-2026.md (source updated 2 days ago)
  -> Run: /blog translate en/ai-trends-2026.md --to fr
- es/tendencias-ia-2026.md (translation > 90 days old)
  -> Run: /blog translate en/ai-trends-2026.md --to es
```

### Phase 7: Report

Output as markdown by default. If the user passes `--html`, also write the
report to `locale-audit-report.html` only inside the audited project root.
Escape all dynamic filenames, titles, URLs, and issue text with
`html.escape(value, quote=True)` before rendering HTML, and reject symlinked
or outside-root report paths.

```
## Multilingual content audit report

### Summary
- Posts audited: [N] across [N] languages
- Overall health: [score] / 100
- Critical issues: [N]
- Warnings: [N]

### Translation coverage
[Matrix from Phase 2]

### Issues found
#### Critical
- [Issue with file references]

#### Warnings
- [Issue with file references]

#### Passed
- [Checks that passed]

### Prioritized fixes
1. [Highest-impact action]
2. [...]

### Stale-translation alerts
[Runnable commands from Phase 6]

### Quick fixes
- Run `/blog translate <file> --to <missing-langs>` for [N] missing translations.
- Run `/blog multilingual` to regenerate hreflang assets.
- Run `/blog localize <file> --locale <code>` for weak cultural adaptations.
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Empty directory | "No blog posts found in [path]" |
| Only one language present | Report coverage, suggest target languages |
| No hreflang files | Flag as critical gap, offer regeneration |
| Unrecognized file format | Skip with a warning |

## Cross-References

- Fill missing translations: `/blog translate <file> --to <missing-codes>`
- Deepen weak adaptations: `/blog localize <file> --locale <code>`
- Regenerate hreflang assets: `/blog multilingual <topic> --languages <codes>`
