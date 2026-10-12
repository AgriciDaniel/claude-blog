# Blog Quality Scoring Checklist

Score each blog post against this checklist. Used by `/blog analyze` and by the
`blog-reviewer` agent. Thresholds live in one table below; other files link here.

## Content Quality (30 points)

| Check | Points | Pass Criteria |
|-------|--------|---------------|
| Coverage/comprehensiveness | 7 | Covers the reader task with useful subtopics, evidence, and examples; no raw word-count target |
| Readability | 7 | Match the audience; default Flesch 60-70, 55-75 acceptable; technical/YMYL topics may justify denser prose |
| Originality/unique value | 5 | Original data, case studies, distinctive sourced synthesis, or transparent first-hand evidence; labels alone earn nothing |
| Sentence & paragraph structure | 4 | Clear, coherent pacing suited to the audience; no fixed sentence, paragraph, or heading quota |
| Engagement elements | 4 | Summary box near the top, callouts, varied content blocks |
| Grammar/clarity | 3 | Clear sentences, controlled passive voice, and clean prose; project style-list terms are advisory |

## SEO Optimization (25 points)

| Check | Points | Pass Criteria |
|-------|--------|---------------|
| Heading hierarchy and purpose fit | 5 | H1 → H2 → H3 with no skips; headings describe the reader task without form or keyword quotas |
| Title clarity and purpose fit | 4 | Accurate, distinctive title consistent with visible content |
| Semantic topic consistency | 4 | Title, headings, and body describe the same reader task without exact-match quotas |
| Internal linking (3-10 contextual) | 4 | Descriptive anchor text, bidirectional, related content |
| URL structure | 3 | Stable, readable, consistently cased path |
| Meta description accuracy | 3 | Useful page-specific summary consistent with visible content |
| External linking (tier 1-3) | 2 | 3-8 outbound links to authoritative sources |

## E-E-A-T Signals (15 points)

| Check | Points | Pass Criteria |
|-------|--------|---------------|
| Author attribution (accountable, with bio) | 4 | Named author/editor preferred; organization attribution acceptable with clear editorial ownership |
| Source fidelity | 4 | Material claims are traceable to sources that support them; no format or density quota |
| Trust indicators (contact, about, transparency) | 4 | Site has contact page, about page, editorial policy |
| Evidence basis | 3 | Verifiable sources, transparent methodology, or supported original material; never require first-person phrasing |

Dates, publisher/title details, retrieval notes, methodology, and limitations
are useful when they identify or change interpretation of a source. No fixed
triple, retrieval-date requirement, or citation form changes the score by
itself. Reference: `flow-alignment.md`.

## Technical Elements (15 points)

| Check | Points | Pass Criteria |
|-------|--------|---------------|
| Schema markup internal heuristic | 4 | Article or BlogPosting (2) + Person (1) + either Organization or BreadcrumbList (1); this is an internal completeness heuristic, not a Google requirement. FAQPage is optional visible-content markup with no score bonus |
| Image optimization (alt text, format, lazy load) | 3 | AVIF/WebP, descriptive alt text, lazy except LCP |
| Structured data elements | 2 | Tables, lists, comparison blocks for AI extraction |
| Page speed signals (no render-blocking) | 2 | LCP < 2.5s, no render-blocking JS, fetchpriority on hero |
| Mobile-friendliness | 2 | Responsive, accessible tap targets, no horizontal scroll, and readable pacing without a fixed paragraph length |
| OG/social meta tags | 2 | og:title, og:description, og:image (1200x630), twitter:card |

## AI Citation Readiness (15 points)

| Check | Points | Pass Criteria |
|-------|--------|---------------|
| Evidence-backed citability | 4 | Important sections are self-contained and supported by verified sources or transparent original evidence; no fixed word band |
| Purpose fit and reader utility | 3 | Clear page purpose and intent-matched headings/format; question headings and FAQs are optional |
| Entity clarity | 3 | Unambiguous topic entity, consistent terminology |
| Content structure for extraction | 3 | Answer-first, tables with `<thead>`, comparison formats |
| AI crawler accessibility | 2 | Declared target crawlers can access or render the primary content; robots policy matches declared goals. Initial HTML is portability advice, not a format mandate |

## Total: 100 points

### Thresholds (single source of truth)

Every other file in this package refers to this table instead of restating a
number. Two different scorers exist and they are not interchangeable: the
**reviewer** (`blog-reviewer` agent, judgment-based, drives delivery) and the
**analyzer** (`scripts/analyze_blog.py`, mechanical heuristic, drives audits and
the pre-commit hook). Both use the same 30/25/15/15/15 category maxima.

| Threshold | Value | Scorer | Where it applies |
|---|---|---|---|
| Delivery gate | Overall 90 or higher AND zero P0 issues | Reviewer | Gate 4 in `blog_preflight.py`; the draft is not shown to the user below it |
| Rating bands | 90-100 Exceptional, 80-89 Strong, 70-79 Acceptable, 60-69 Below Standard, under 60 Rewrite | Either | Labels only. 80-89 means "minor polish still needed"; it does not clear the delivery gate |
| Strategy target | 80 or higher on existing posts | Analyzer | `blog-strategy` planning goal for a back catalog, not a delivery rule |
| Pre-commit gate | 70 | Analyzer | `scripts/quality_gate.py` (`DEFAULT_THRESHOLD`); a hook floor, not a delivery gate |
| Audit buckets | 90+ Excellent, 70-89 Good, 50-69 Needs Work, under 50 Poor | Analyzer | `blog-audit` summary dashboard |
| Rewrite regression | New score no lower than the original | Reviewer | `blog-rewrite`; a drop sets `BLOCKING: true` |

### Draft-stage scoring (how the 90 applies to an unpublished draft)

The reviewer scores a draft folder before the post is live, so some rubric items
describe the site or a measurement rather than the draft. Do not hand out those
points by default and do not silently drop them. Use this rule:

1. **Score from draft evidence where the draft carries it.** URL structure comes
   from the slug and canonical URL. Trust indicators come from the byline, author
   page, editorial-policy and contact links present in the HTML. Internal
   linking comes from the resolved links in the draft (anchor text, count,
   placement). AI crawler accessibility comes from the rendered HTML (primary
   content present, no `noindex`, nothing gated behind script). Page speed and
   mobile items are scored from static signals only (image dimensions, lazy
   loading, no render-blocking script, viewport meta, responsive CSS).
2. **Mark an item N/A only when the draft has no evidence for it.** Typical
   cases: `robots.txt` policy for an unpublished URL, a measured LCP value, link
   targets that exist only on the live site, a first post with nothing to link
   to. State the evidence gap for each N/A item in the Notes column.
3. **Scale each category to its fixed maximum.** For a category with N/A items,
   `category score = round(points earned / points applicable * category maximum)`.
   Report it as `N/MAX` with the fixed maxima 30, 25, 15, 15, 15, plus one line
   `N/A items: <item> (<pts>), ...; category scaled from <earned>/<applicable>`.
4. **The overall is the sum of the five reported category scores**, an integer.
   The 90 threshold applies to that overall. This is exactly what Gate 4 reads:
   the stated maxima must match the rubric, the overall must equal the sum of the
   category scores, and the overall must be 90 or higher.
5. **Cap on N/A.** If more than 20 of the 100 points would be N/A, the draft
   cannot be scored fairly. Return `BLOCKING: true` with the reason "too little
   draft evidence to score", and name what to add (for example author and policy
   links).

Gate 4 does not verify the N/A arithmetic; it checks the reported numbers for
consistency. Gate 3 (visual checks) and Gate 5 (links and assets) run
independently and are never replaced by an N/A.

## Priority Classification

When reporting issues, classify by priority:

### Critical (Must Fix Before Publishing)
- Fabricated statistics (zero tolerance)
- Broken heading hierarchy (H1 → H3 skip)
- No source attribution on claims
- Missing author attribution
- Verified primary-content inaccessibility for a declared target crawler,
  whether caused by rendering, robots policy, authentication, or fetch failure

### High Priority
- Important sections obscure their conclusion or lack support
- A paragraph's density or structure creates a demonstrated comprehension
  problem; paragraph length alone does not set priority
- Missing the internal Article-or-BlogPosting/Person/either-Organization-or-BreadcrumbList schema heuristic
- Material claims lack enough reliable evidence for the reader to verify them
- Missing meta description
- Title tag outside 40-60 character range
- No internal links
- Flesch score outside 55-75 range
- No OG/social meta tags
- Paragraphs whose pacing or mixed ideas reduce comprehension
- Passive voice > 15%

### Medium Priority
- A chart is absent where comparison or trend data would be materially clearer as a visual
- An image, diagram, or screenshot is absent where prose alone does not explain the subject clearly
- Tier 4-5 sources present
- Self-promotion > 1 mention
- Sections exceeding 300 words between headings
- Unsupported first-hand testing or experience claims
- Images not in AVIF/WebP format
- `loading="lazy"` on LCP image
- Sentence structure repeatedly obscures meaning for the intended audience
- Transitions repeatedly hide the relationship between ideas

### Low Priority
- Localized paragraph pacing that mildly slows comprehension
- Missing chart type diversity
- Images without alt text
- Missing external links to tier 1-3 sources
- Entity terminology inconsistency

## Quick Automated Checks

These can be detected programmatically:

### Content Quality
1. Paragraph density and structure (descriptive signal; escalate only when
   review confirms a comprehension problem, never from length alone)
2. Sentence count per paragraph (flag > 3 sentences)
3. Flesch-Kincaid score (default target 60-70, acceptable 55-75; adjust for audience)
4. Heading usefulness and hierarchy (descriptive observation)
5. Optional summary presence when it materially helps the selected content type
6. Average sentence length (descriptive only)
7. Sentence-length distribution (descriptive only)
8. Passive voice sample (review in context; no universal threshold)
9. Configured project style-list terms (advisory only; never a score or authorship signal)
10. Transition word sample (review for repetition; no universal threshold)

### SEO Optimization
11. Title clarity and visible-content consistency
12. Heading hierarchy (regex for `^#{1,6} `, no skipped levels)
13. Meta description accuracy and visible-content consistency
14. Internal link count (regex for relative URLs or same-domain links)
15. External link count and tier classification
16. URL structure check (stable, readable, consistently cased)

### E-E-A-T Signals
17. Author attribution presence (frontmatter `author` field)
18. Citation format (regex for `\([^)]+\(http`)
19. Unsourced statistics (numbers without attribution nearby)
20. Self-promotion patterns (brand name frequency, max 1)
21. First-hand claims with supporting methodology or evidence; neutral sourced explainers are valid

### Technical Elements
22. Image count (regex for `!\[` or `<img`)
23. Image alt text presence (images without alt attribute)
24. Chart count (regex for `<svg` or `<figure`)
25. Schema presence (search for structured data markers)
26. OG meta tags (frontmatter `ogImage`, `coverImage`)
27. `loading="lazy"` on first image (flag as LCP issue)
28. dateModified/lastUpdated truthfulness when substantive changes are documented (Google lists date changes without substantial content change as a warning sign, helpful-content page updated 2026-10-05); also check that bylines, headshots, and credentials are real and that AI assistance is disclosed where readers would expect it

### AI Citation Readiness
29. Evidence-backed, self-contained treatment of important claims without a fixed length
30. Clear page purpose and stable entity naming
31. Intent-matched format; Q&A is optional and receives no score bonus
32. Table presence with `<thead>` (for AI extraction)
33. robots.txt AI bot allowance (site-level check)
