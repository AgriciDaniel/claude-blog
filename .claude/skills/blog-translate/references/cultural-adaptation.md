# Cultural Adaptation Profiles

Locale profiles for cultural deep-adaptation. Loaded on demand by
`blog-localize` and by `blog-multilingual` during the adaptation pass.
This file is the single source of truth, do not duplicate it elsewhere.

Each profile covers: address form (formality), example brands and
companies to substitute in, currency and pricing conventions, statistics
sources to prefer, legal references to swap, CTA tone, and idiom notes.

## DACH (Germany, Austria, German-speaking Switzerland)

**Locales:** `de-DE`, `de-AT`, `de-CH`.

- **Formality:** B2B and tech: `Sie` (formal). Lifestyle, gaming,
  D2C: `du` (informal). Pick one and use it consistently for the
  entire post. SaaS for SMB defaults to `du`; enterprise SaaS defaults
  to `Sie`.
- **Brand examples to swap to:** MediaMarkt, Saturn, Otto,
  Zalando (retail), Lidl, Aldi (grocery), Deutsche Bank, ING (finance),
  SAP, Siemens (B2B tech). For Austria: Spar, Hofer, BAWAG. For Swiss:
  Migros, Coop, UBS.
- **Currency:** EUR for DE and AT, CHF for CH. Format: `1.234,56 EUR`
  (DE/AT) or `CHF 1'234.56` (CH).
- **Statistics sources to prefer:** Statista (Germany scope), Bitkom,
  Bundesnetzagentur, Destatis (Statistisches Bundesamt), HWWI,
  ifo Institut, Bertelsmann Stiftung. Avoid US-only Pew or Nielsen
  unless explicitly framed as US comparison.
- **Legal references to swap:** CCPA to DSGVO (GDPR in DACH-speak),
  FTC to Bundeskartellamt, FCC to Bundesnetzagentur. Accessibility law is
  jurisdiction-specific: DE BGG, AT BGStG, CH BehiG. Keep ADA when the claim
  is specifically about US compliance.
- **CTA tone:** Informational, never imperative. Prefer "Jetzt
  entdecken", "Mehr erfahren", "Kostenlos testen". Avoid "Buy now",
  "Sign up today" style. Trust signals (data protection, GDPR
  compliance) outperform urgency.
- **Idiom notes:** Compound nouns are normal; don't break them.
  "Game-changer" becomes "Wendepunkt" or specific concrete claim.
  "Best practices" stays in English.

## Francophone (France, Quebec, Belgium-FR, Switzerland-FR)

**Locales:** `fr-FR`, `fr-CA`, `fr-BE`, `fr-CH`.

- **Formality:** Default `vous` for almost all professional content.
  `tu` only for B2C lifestyle aimed at under-30 audiences. France
  business culture is markedly more formal than US.
- **Brand examples to swap to:** Carrefour, Auchan, Leclerc, FNAC
  (retail/electronics), Orange, SFR (telecom), BNP Paribas, Société
  Générale (finance), Dassault, Capgemini (B2B tech). Quebec: Hydro-Québec,
  Desjardins, Couche-Tard.
- **Currency:** EUR for `fr-FR` and `fr-BE`, CHF for `fr-CH`, CAD for
  `fr-CA`. Format: `1 234,56 EUR` (NBSP as thousands separator). Quebec
  writes CAD as `1 234,56 $` with the symbol after.
- **Statistics sources to prefer:** INSEE, Médiamétrie, IFOP, BVA,
  ARCOM (formerly CSA), Statistique Canada (for fr-CA), Eurostat (for
  fr-FR European context).
- **Legal references to swap:** CCPA / GDPR -> RGPD, FTC -> DGCCRF,
  ADA -> loi du 11 février 2005. Quebec adds Loi 25 (privacy) and
  Loi 96 (French language).
- **CTA tone:** Polite, restrained, value-focused. "Découvrez",
  "En savoir plus", "Essayer gratuitement". Avoid "Achetez maintenant"
  unless e-commerce flash-sale context. Quebec accepts slightly more
  direct CTAs than France.
- **Idiom notes:** "Workflow" stays English in tech contexts. "Brand"
  often translated as "marque". Be careful with Quebec vs. France
  vocabulary differences (e.g., "courriel" vs. "email", "fin de
  semaine" vs. "weekend").

## Hispanic (Spain vs. LATAM)

Hispanic markets split sharply. Do not conflate `es-ES` with `es-MX` or
generic `es`. If a user writes `es`, ask which market or require explicit
neutral Spanish mode.

### Spain (`es-ES`)

- **Formality:** `tú` for B2C and most digital content. `usted` only
  for highly formal B2B (banking, legal). "Vosotros" exists; LATAM
  doesn't use it.
- **Brand examples:** El Corte Inglés, Mercadona, Carrefour España
  (retail), Telefónica/Movistar, Vodafone España (telecom),
  Santander, BBVA (finance), Inditex/Zara, Iberdrola (B2B).
- **Currency:** EUR. Format: `1.234,56 EUR`.
- **Sources:** INE (Instituto Nacional de Estadística), CIS,
  IAB Spain, Comscore España, Eurostat.
- **Legal:** RGPD (GDPR), AEPD (data protection authority),
  CNMC (competition), Ley General de Publicidad.
- **CTAs:** Direct but warm. "Descubre", "Empieza ahora",
  "Pruébalo gratis".

### LATAM (Mexico `es-MX`, Argentina `es-AR`, Colombia `es-CO`)

- **Formality:** `tú` general default. Argentina uses `vos` (voseo).
  Colombia mixes `tú` and `usted` depending on region. Mexico is
  consistently `tú`.
- **Brand examples (MX):** Walmart México, Liverpool, Coppel,
  Telcel, BBVA México, Bimbo. (AR): Mercado Libre, Banco Galicia.
  (CO): Éxito, Bancolombia, Rappi.
- **Currency:** Local. MXN (`$1,234.56 MXN`), ARS (`$1.234,56`),
  COP (`$1.234 COP`). Use whole-peso COP examples unless a source explicitly
  uses centavos. Always specify the currency code; bare `$`
  is ambiguous.
- **Sources:** INEGI (MX), DANE (CO), INDEC (AR), Comscore LATAM,
  IAB LATAM.
- **Legal:** LFPDPPP (MX), Ley 1581 (CO), Ley 25.326 (AR). PROFECO
  (MX consumer protection).
- **CTAs:** Warm, direct, relationship-building. "Descubre cómo",
  "Únete gratis", "Empieza hoy".

## Japanese (Japan, `ja-JP`)

- **Formality registers:** Three to know. `desu/masu` (polite, default
  for most published content). `de aru` (declarative, used in
  serious essays, white papers). Casual forms (`da`, plain verbs)
  for blog posts aimed at consumer audiences. Pick one register and
  stay in it.
- **Honorifics:** Use `-san` when referring to people. Companies
  take `sama` in formal contact contexts but not in editorial body.
- **Brand examples:** Aeon, Ito-Yokado, Don Quijote (retail),
  Rakuten, Mercari (e-commerce), NTT Docomo, SoftBank (telecom),
  MUFG, SMBC (finance), Sony, Toyota, Hitachi (B2B), LINE,
  PayPay (payments).
- **Currency:** Yen, no decimals. Prefer `1,234円` in body copy or
  `JPY 1,234` in finance-style contexts.
- **Sources:** Statistics Bureau of Japan (Soumusho), METI, Nikkei
  research, Dentsu reports, Macromill, Recruit Works Institute,
  Mitsubishi Research.
- **Legal:** APPI (Act on Protection of Personal Information),
  JFTC (Japan Fair Trade Commission), METI guidelines.
- **CTAs:** Soft, indirect, group-oriented. Avoid imperative tone.
  Prefer phrases that emphasize benefit, ease, or community
  ("everyone is using it" angles). Hard urgency converts poorly.
- **Idiom notes:** English loanwords (katakana) are common in tech
  copy but should be reserved for established terms. Avoid
  inventing new katakana words. Numbered lists work well; rhetorical
  questions are less common than in EN.

## Custom-Locale Template

When the target locale lacks a profile here, build one inline. Required
fields:

```yaml
locale: <code>           # e.g. nl-NL, pl-PL, sv-SE, tr-TR
formality:
  default: <formal|informal|mixed>
  notes: <when to switch>
brand_examples:
  retail: [..., ...]
  finance: [..., ...]
  telecom: [..., ...]
  b2b_tech: [..., ...]
currency:
  code: <ISO 4217>
  format: <example: 1 234,56 PLN>
sources_preferred:
  - <local statistics body>
  - <local industry research>
legal_references:
  privacy: <local equivalent of GDPR/CCPA>
  competition: <regulator>
  advertising: <regulator>
cta_tone:
  style: <imperative|informational|polite|warm>
  avoid: [...]
idiom_notes: <quirks the translator must respect>
```

Quick research pass to fill the template:

1. Search `[country] official statistics agency` for the sources block.
2. Search `[country] data protection authority` for the legal block.
3. Pull the top 3 retailers and top 3 banks from a recent business
   press article.
4. Read 2-3 native blog posts in the target market to calibrate
   `formality.default` and `cta_tone.style`.

Save custom locale profiles outside this shared skill reference, for example in
a project-local `.claude/blog-locale-profiles/<locale>.md` file or in the task
output. Do not append runtime profiles to this file.

## Profile Selection Logic

Used by `blog-localize` (Phase 1) and `blog-multilingual` (Phase 4):

1. Exact locale match (`de-CH`, `fr-CA`, `es-MX`).
2. Language-only fallback only for unambiguous editorial markets (`de`, `fr`,
   `ja`). Treat `es`, `pt`, `zh`, and any language spanning materially
   different legal, currency, or script markets as ambiguous unless the user
   requests explicit neutral mode.
3. Regional grouping (e.g., DACH for any `de-*`, LATAM for any
   `es-*` other than `es-ES`).
4. Custom-locale template if no match.
