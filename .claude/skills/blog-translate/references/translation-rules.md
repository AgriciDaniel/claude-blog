# Translation Rules

SEO and format rules for blog translation. Loaded on demand by
`blog-translate` and the `blog-translator` agent.

## SEO Translation Principles

1. Localize, do not transliterate. Pick the term native speakers actually
   search for in the target market.
2. Preserve topical and entity coverage, not keyword density. Match the
   search intent and localized SERP phrasing without forcing repeated terms.
3. Independently optimize the title tag and meta description per language.
   Don't translate, rewrite for the target SERP.
4. Keep slugs in the target language using the locale's romanization rules.
5. Translate alt text and figcaptions; never leave English alt text on a
   non-English page.
6. Names of organizations, brands, and people stay in their canonical form.

## Format Preservation

Preserve unchanged:

- Markdown structure (headings, lists, blockquotes, code fences).
- HTML tags and attributes.
- Frontmatter keys (translate values, not keys).
- Image and link URLs.
- Executable code fences and inline code. Keep them unchanged unless the user
  explicitly asks for localized tutorial comments.
- SVG attributes (`x`, `y`, `font-size`, `fill`, `transform`,
  `viewBox`). Translate only `<text>` and `<tspan>` content.
- Schema JSON-LD blocks. Translate user-facing content strings such as
  `headline` and `description`; never translate Person, Organization, or
  Brand names, URLs, IDs, `@id`, or `sameAs`.
- Internal-link zone markers (`[INTERNAL-LINK: ...]`).

Adjust SVG text length where the translation is meaningfully longer or
shorter than the source:

| Locale | Length delta vs. EN |
|--------|---------------------|
| DE | +25% to +30% |
| FR | +10% to +15% |
| ES | +10% |
| IT | +10% |
| PT-BR | +10% |
| JA | -20% (per character count) |
| ZH | -25% (per character count) |
| KO | -15% |

If text overflows the chart frame, raise `viewBox` width or reduce
`font-size`, never truncate.

## Number, Date, Currency, and Quote Formats per Locale

| Locale | Decimal | Thousands | Date | Currency | Quotes |
|--------|---------|-----------|------|----------|--------|
| en-US | `.` | `,` | MM/DD/YYYY or "March 25, 2026" | $1,234.56 | "..." |
| en-GB | `.` | `,` | DD/MM/YYYY or "25 March 2026" | GBP 1,234.56 | '...' |
| de-DE | `,` | `.` | DD.MM.YYYY | 1.234,56 EUR | "..." |
| de-CH | `.` | `'` | DD.MM.YYYY | CHF 1'234.56 | "..." |
| fr-FR | `,` | ` ` (NBSP) | DD/MM/YYYY | 1 234,56 EUR | « ... » |
| fr-CA | `,` | ` ` (NBSP) | YYYY-MM-DD | 1 234,56 $ | « ... » |
| es-ES | `,` | `.` | DD/MM/YYYY | 1.234,56 EUR | «...» or "..." by publication style |
| es-MX | `.` | `,` | DD/MM/YYYY | $1,234.56 MXN | "..." |
| pt-BR | `,` | `.` | DD/MM/YYYY | R$ 1.234,56 | "..." |
| pt-PT | `,` | ` ` (NBSP) | DD/MM/YYYY | 1 234,56 EUR | «...» or "..." by publication style |
| it-IT | `,` | `.` | DD/MM/YYYY | 1.234,56 EUR | «...» or "..." by publication style |
| ja-JP | `.` | `,` | YYYY/MM/DD or YYYY-MM-DD | 1,234円 or JPY 1,234 | 「...」 |
| zh-CN | `.` | `,` | YYYY-MM-DD | CNY 1,234.56, ¥1,234.56, or 1,234.56元 | “...” or 「...」 by market style |
| nl-NL | `,` | `.` | DD-MM-YYYY | 1.234,56 EUR | '...' |
| pl-PL | `,` | ` ` (NBSP) | DD.MM.YYYY | 1 234,56 PLN | „...” |

Notes:

- Preserve reported facts and original amounts for sourced claims.
- Convert currency only when it helps the local reader, keep the original
  amount nearby, and include exchange date and source in the note or citation.
- If the source reports a factual claim such as "the global tech sector earned
  $X", keep USD with locale number formatting.
- For dates inside frontmatter (`date`, `lastUpdated`, `translatedDate`),
  always use ISO 8601 (`YYYY-MM-DD`) regardless of locale. Locale
  formatting applies to dates inside body copy only.

## Quote Handling

- en: `"..."` and `'...'`.
- de: prefer `„...“` or `»...«`; straight quotes are only an explicit ASCII
  fallback.
- fr: `« ... »` with non-breaking or narrow no-break spaces inside.
- es, it, and pt-PT: use `«...»` or `"..."` according to publication style.
- ja: `「...」` primary and `『...』` nested.
- zh: use Chinese quote conventions such as `“...”` or `「...」` by market
  style.
- pl: `„...”` primary, with accepted nested forms such as `«...»` or
  `»...«` by publication style.

When the source uses straight quotes, the translator should switch to the
locale's primary style above. Preserve nesting depth (outer vs. inner).

## Quality Criteria Checklist

Before reporting a translation as done, verify:

- [ ] No untranslated source-language fragments (except established
      loanwords like "Content Marketing" in DE).
- [ ] All numbers, dates, currencies use locale format.
- [ ] All quote marks switched to locale style.
- [ ] Frontmatter strings localized (`title`, `description`, `tags`,
      `slug`).
- [ ] All image alt text translated.
- [ ] All `<figcaption>` content translated.
- [ ] All SVG `<text>` and `<tspan>` content translated, lengths
      adjusted per the table above.
- [ ] FAQ questions and answers natural in target language.
- [ ] Evidence-backed explanations remain accurate and self-contained in the
      target language where present.
- [ ] No mixed-language sentences (other than loanwords).
- [ ] No literal idiom translations; idioms adapted to local equivalents.
- [ ] Information parity, section coverage, and readability are preserved.
- [ ] Markdown and HTML structure intact.
- [ ] Schema JSON-LD `inLanguage` updated and `translationOfWork` added.

## Banned Patterns in Translation

Never produce:

- Mixed-language sentences (other than established English loanwords).
- Google-Translate-quality literal output.
- Inconsistent formal or informal address within a single document.
- Literally translated English idioms.
- Preserved English SVO sentence structure forced into non-SVO languages.
- English source-attribution like "(Source)" left untranslated where the
  locale uses a different convention.

## Translation Provenance

Store translation provenance in frontmatter or CMS metadata, not rendered
comments. Use fields such as `translatedFrom`, `translatedDate`,
`translationTool`, `sourceHash`, and `translationHash`.
