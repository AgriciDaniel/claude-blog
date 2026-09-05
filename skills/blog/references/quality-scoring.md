# Blog Quality Scoring Checklist

Score each blog post against this checklist. Used by `/blog analyze`.

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
| Schema markup priority baseline | 4 | Article/BlogPosting + Person + Organization + BreadcrumbList; FAQPage optional visible-content markup with no score bonus |
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

### Scoring Bands

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | Exceptional | Publish as-is, flagship content |
| 80-89 | Strong | Minor polish, ready for publication |
| 70-79 | Acceptable | Targeted improvements needed before publish |
| 60-69 | Below Standard | Significant rework required |
| < 60 | Rewrite | Fundamental issues, start from outline |

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
- Missing Article/Person/Organization/BreadcrumbList schema baseline
- Fewer than 8 sourced statistics
- Missing meta description
- Title tag outside 40-60 character range
- No internal links
- Flesch score outside 55-75 range
- No OG/social meta tags
- Paragraphs whose pacing or mixed ideas reduce comprehension
- Passive voice > 15%

### Medium Priority
- Fewer than 2 charts
- Fewer than 3 images
- Tier 4-5 sources present
- Self-promotion > 1 mention
- Sections exceeding 300 words between headings
- Unsupported first-hand testing or experience claims
- Images not in AVIF/WebP format
- `loading="lazy"` on LCP image
- Average sentence length > 22 words
- Transition words < 15% or > 35%

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
28. dateModified/lastUpdated truthfulness when substantive changes are documented

### AI Citation Readiness
29. Evidence-backed, self-contained treatment of important claims without a fixed length
30. Clear page purpose and stable entity naming
31. Intent-matched format; Q&A is optional and receives no score bonus
32. Table presence with `<thead>` (for AI extraction)
33. robots.txt AI bot allowance (site-level check)
