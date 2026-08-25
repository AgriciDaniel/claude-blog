---
name: blog-localize
description: >
  Deep cultural adaptation of translated blog posts. Run after blog-translate
  completes. Goes beyond translation to swap brand examples, adapt CTAs,
  substitute legal references, localize statistic sources where possible, and
  adjust formality (Sie/du, tu/vous, formal/informal). Built-in profiles for
  DACH, Francophone, Hispanic, and Japanese markets.
  Use when user says "localize blog", "blog localize", "cultural adaptation",
  "adapt for Germany", "lokalisieren", "localiser", "adaptar".
user-invokable: true
argument-hint: "<file> --locale <locale-code>"
license: MIT
compatibility: Standalone within claude-blog. Invoked by blog-multilingual.
metadata:
  author: AgriciDaniel
  version: "2.1.1"
  category: blog
---

# Blog Localize, Cultural Deep-Adaptation

Takes a translated blog post and performs cultural adaptation so the result
feels like it was written for the target market, not translated into it.
This is the layer above `blog-translate`: it replaces examples, adjusts
tone, swaps references, and localizes the entire reading experience.

> Adapted from `claude-blog-multilingual` by Chris Mueller (Pro Hub Challenge,
> March 2026). Original: https://github.com/Chriss54/multilingual-int

## Key References

- `../blog-translate/references/cultural-adaptation.md`, the shared cultural
  profiles file with substitution tables for DACH, Francophone, Hispanic,
  Japanese, and a custom template. Do not duplicate this file.

## When to Use

- Right after `blog-translate` produces a base translation.
- When existing translated content reads like "translated from English".
- When targeting a specific market, not just a language.
- When content needs local statistics, examples, and brand references.

## Workflow

### Phase 1: Locale Understanding

1. Parse the locale code with the shared multilingual locale rules used by
   `blog-translate`, `blog-multilingual`, and `blog-locale-audit`: ISO 639-1
   language in lowercase, optional ISO 15924 script in title case, optional
   ISO 3166-1 Alpha-2 region in uppercase. Accept full codes (`de-DE`,
   `fr-CA`, `es-MX`, `pt-BR`, `zh-Hant`) and unambiguous plain language codes
   (`de`, `fr`). Require a region or explicit neutral mode for ambiguous
   language-only targets such as `es`, `pt`, and `zh`.
2. Load the cultural profile from
   `../blog-translate/references/cultural-adaptation.md`.
   - If the locale has a profile, use it.
   - If not, follow the "Custom-locale template" section in that reference
     to build a minimal profile inline.
3. Read the translated post only after resolving it inside the project
   root/current working directory. Reject symlinked paths, traversal outside
   the root, files over 10 MB, and binary files. Then identify adaptation
   targets.

### Phase 2: Cultural Audit

Scan for elements that signal foreign origin:

| Element | What to look for |
|---------|------------------|
| Brand examples | US or UK brands with no relevance locally |
| Statistics sources | US-only studies and surveys |
| CTAs | American-style aggressive calls-to-action |
| Idioms | Literally translated English expressions |
| Legal references | Foreign laws (CCPA, FTC) where local law applies (DSGVO, RGPD) |
| Cultural references | Foreign holidays, events, customs |
| Currency and pricing | USD without conversion or context |
| Tone | Too casual or too formal for the target market |
| Address form | Inconsistent Sie/du, tu/vous, formal/informal |

Output an audit report listing every target with severity (critical,
recommended, optional).

### Phase 3: Adaptation

#### 3a. Example Substitution

Swap foreign examples for local equivalents:

- Use WebSearch to find local case studies, brands, or scenarios.
- Replace inline, preserving the same argument and structure.
- Record source URL, access date, and rationale for every non-obvious local
  replacement.
- If no local equivalent exists, keep the original but add local context
  ("In the German market, the equivalent dynamic is X").

#### 3b. Statistics Localization

- Use primary or high-quality local sources for replacement statistics:
  national statistics offices, regulators, official industry bodies, academic
  datasets, or named research reports with methodology.
- Do not rely on generic WebSearch snippets as evidence. Fetch the cited page,
  verify the figure and context, and record the source URL and date.
- Fetch cited pages only after SSRF checks: allow `https` URLs only; reject
  `javascript:`, `data:`, `file:`, localhost, loopback, private, link-local,
  multicast, and reserved IPs after DNS resolution; disable redirects or
  validate the final URL with the same checks; cap redirects, response size,
  and request time; log the final URL and access date.
- If local data exists with comparable methodology, swap the source and the
  figure together. Keep one named source per claim.
- If local data is related but uses a different methodology or timeframe, do
  not silently swap it. Keep the original claim scoped, or rewrite the claim to
  match the local source.
- If not, keep the original stat but mark its geographic scope ("In the
  US, ...").
- Never strip source attribution.

#### 3c. CTA Adaptation

Rewrite calls-to-action per the cultural profile:

- Adjust aggressiveness level (DACH and JA prefer informational, US prefers
  imperative).
- Use culturally appropriate action verbs.
- Adapt urgency framing.

#### 3d. Tone Calibration

- Match formality per profile (DACH defaults to Sie for B2B, du for B2C
  lifestyle; FR defaults to vous; JA shifts register sharply by audience).
- Ensure consistent formal or informal address throughout the entire
  document.
- Match local content-style conventions.

#### 3e. Legal and Regulatory Context

- Map legal references by issue and jurisdiction. Keep the original law when
  the claim is specifically about US compliance. Only substitute when the
  local law addresses the same issue, such as CCPA to DSGVO in DE, RGPD in
  FR, LGPD in BR, LFPDPPP in MX, Ley 1581 in CO, or Ley 25.326 in AR.
- Add local compliance notes where they help the reader.
- Remove irrelevant foreign regulatory references.

#### 3f. Brand Example Swaps (Quick Map)

Profiles in `../blog-translate/references/cultural-adaptation.md` provide
substitution tables. Common examples:

| Source (US) | DACH | FR | ES (Spain) | LATAM | JA |
|-------------|------|----|----|-------|----|
| Walmart | MediaMarkt | Carrefour | El Corte Inglés | Walmart MX | Aeon |
| Target | Saturn | Auchan | Hipercor | Liverpool | Ito-Yokado |
| FTC | Bundeskartellamt | DGCCRF | CNMC | PROFECO (MX) | JFTC |
| CCPA | DSGVO | RGPD | RGPD | LFPDPPP (MX), Ley 1581 (CO), Ley 25.326 (AR), LGPD (BR) | APPI |

### Phase 4: Quality Verification

- All critical adaptation targets addressed.
- Tone is consistent throughout.
- No remaining foreign-origin markers.
- Statistics have valid sources (original or localized).
- CTAs match cultural expectations.
- Formal or informal address is consistent end to end.
- Content still supports the same argument as the original.
- SEO elements remain optimized beyond keyword placement: localized title and
  meta, heading intent, slug, alt text, internal-link anchors, same-language
  canonical, hreflang compatibility, and schema `inLanguage`.
- Word count is within the expected ratio for the language pair.

### Phase 5: Save and Report

1. Save the localized version. Default: write a reviewed copy as
   `{slug}-localized.{ext}`. Only overwrite the translated file when the user
   asks for overwrite; before overwriting, create a timestamped backup and
   show a diff summary. Resolve every output path inside the project root and
   reject traversal, symlinked paths, or writes outside that root.

2. Present the summary:

   ```
   ## Localization complete: [Title]

   ### Target locale: [locale-code] ([locale-name])

   ### Adaptations made
   | Type | Count | Examples |
   |------|-------|----------|
   | Brand examples | [N] | Walmart -> MediaMarkt |
   | Statistics | [N] | US survey -> DACH survey |
   | CTAs | [N] | "Buy now" -> "Jetzt entdecken" |
   | Tone adjustments | [N] | Casual -> Sie |
   | Legal references | [N] | CCPA -> DSGVO |
   | Cultural references | [N] | Thanksgiving -> Weihnachtsgeschaeft |

   ### Cultural fit score
   - Naturalness: [1-10]
   - Market relevance: [1-10]
   - Tone match: [1-10]
   - Overall: [N]/30

   ### Remaining recommendations
   - [Optional adaptations not applied]
   ```

## Error Handling

| Scenario | Action |
|----------|--------|
| No cultural profile for the locale | Build a minimal profile from the custom-locale template, proceed |
| File is not in the expected language | Warn the user, offer to translate first |
| No local statistics available | Keep the original stat with a geographic-scope note |
| Locale code ambiguous (e.g., `pt`) | Ask: "Did you mean `pt-BR` (Brazil) or `pt-PT` (Portugal)?" |

## Cross-References

- Pre-step (translation): `/blog translate <file> --to <code>`
- QA across language versions: `/blog locale-audit <directory>`
- One-command pipeline: `/blog multilingual <topic> --languages <codes>`
