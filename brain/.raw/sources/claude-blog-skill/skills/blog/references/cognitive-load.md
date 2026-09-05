# Cognitive Load Assessment for Long-Form Content

A reader has finite working memory. A blog post that introduces too many new concepts, named entities, or numeric claims in too short a span will lose them. Most readability scores (Flesch, Gunning Fog) measure surface-level prose difficulty; this reference adds the dimension they miss: **how much the reader must actively hold to follow a section**.

Run the cognitive-load analyzer (`scripts/cognitive_load.py`) on long-form B2B posts (1,500+ words). It produces a heatmap of sections by load.

Adapted from the impeccable plugin's UI cognitive-load reference (Paul Bakaus, Apache 2.0).

---

## Three types of cognitive load (Sweller 1988)

### Intrinsic load: the topic itself
Some topics are inherently complex. A post on "OAuth 2.1 refresh-token rotation" has higher intrinsic load than "10 ways to declutter your home." You cannot eliminate this; you can scaffold it.

Manage by:
- Breaking dense topics into ordered sub-sections
- Providing scaffolding (templates, callouts, examples)
- Progressive disclosure: introduce one concept fully before introducing the next
- Grouping related decisions together

### Extraneous load: bad writing
Mental effort caused by poor structure. **Eliminate ruthlessly.** Pure waste.

Common sources:
- Unexplained jargon
- Pronouns with unclear referents (the bare "This is why..." with no antecedent)
- Sentence-shape monotony forcing the reader to re-parse
- Visual clutter (over-formatted bullets, broken table layouts)
- Forward references ("as we will see later")

### Germane load: the learning the reader wants
Mental effort spent building understanding. This is *good* load; it earns the reader something. Support it; do not strip it out.

Support by:
- Building mental models the reader can reuse
- Tying new concepts to anchors the reader already has
- Concrete examples after abstract definitions
- Repetition of high-leverage terms (not paraphrases)

---

## The working memory rule

Humans hold roughly four items in working memory at once (Cowan, 2001, a revision of Miller's "7 plus or minus 2").

When reading prose, the reader is holding:
- The topic of the current paragraph
- Open references not yet resolved (pronouns, deferred terms)
- New named entities introduced in this section
- Numeric claims they need to compare or evaluate

If a section forces the reader to hold more than four things at once to make sense of the next sentence, the section is overloaded.

### Practical thresholds for long-form

| Signal | Healthy | Borderline | Overloaded |
|---|---|---|---|
| New named entities per 100 words | 1 to 3 | 4 to 6 | 7+ |
| Numeric claims per 100 words | 1 to 3 | 4 to 5 | 6+ |
| New jargon terms per 100 words | 0 to 1 | 2 to 3 | 4+ |
| Forward references per section | 0 | 1 | 2+ |
| Nested clauses per sentence average | < 1.5 | 1.5 to 2.5 | > 2.5 |

A section that triggers two or more "overloaded" rows is a P1 per
`editorial-heuristics.md`; break it up before publishing.

---

## What the analyzer measures

`scripts/cognitive_load.py` segments the post by H2 and computes per-section:

1. **new_entity_density**: capitalized phrases not seen in prior sections, normalized per 100 words. High counts signal too many proper nouns introduced at once.
2. **numeric_claim_density**: count of numbers (percentages, counts, currencies, dates) per 100 words.
3. **jargon_introduction_count**: words that match a domain-jargon list and have not been defined in or before the section. The default list lives at the top of `scripts/cognitive_load.py` and covers SEO/GEO/web-vitals terms. To extend for a different domain, pass `--jargon <path-to-newline-delimited-file>`; entries augment the defaults rather than replacing them.
4. **forward_reference_count**: phrases like "as we will see," "discussed below," "later in this post."
5. **avg_clause_depth**: average count of subordinate-clause markers per sentence (commas, semicolons, "which," "that," parentheticals).
6. **load_score**: composite 0 to 100 where higher is more loaded.

The composite uses the threshold table above. Each "overloaded" signal contributes 25 points, each "borderline" contributes 10, capped at 100.

---

## Reporting format

```
## Cognitive Load Heatmap: [Title]

Overall load: 38 / 100 (Moderate)

| Section (H2) | Words | Load | Entities/100 | Numerics/100 | Jargon | Forward refs | Avg clauses |
|---|---|---|---|---|---|---|---|
| Why this matters | 230 | 22 | 2.6 | 1.7 | 0 | 0 | 1.4 |
| Methodology overview | 410 | 67 | 6.8 | 1.0 | 4 | 1 | 2.1 |
| Results | 380 | 41 | 3.2 | 5.5 | 1 | 0 | 1.8 |
| Limitations and caveats | 290 | 18 | 1.0 | 2.8 | 0 | 0 | 1.5 |
| Recommendations | 320 | 33 | 3.4 | 1.6 | 2 | 1 | 1.7 |

### Overloaded sections (P1)
- **Methodology overview**: 4 new jargon terms in 410 words, 6.8 entities/100, 1 forward reference. Split into two sections or define jargon inline.

### Borderline sections (P2)
- (none)

### Healthy sections
- Why this matters, Results, Limitations and caveats, Recommendations
```

---

## How to fix overloaded sections

1. **Split.** If a single H2 has too much, split into two H2s along a natural seam.
2. **Define inline.** First introduction of jargon should include a one-line definition in parentheses or a dedicated sentence.
3. **Re-order.** Move forward references inline. If the reader needs context to follow, deliver it now, not "later."
4. **Add a visual.** Tables, comparison charts, and inline SVG diagrams reduce textual load.
5. **Use a callout.** A "Quick refresher: term X = definition" callout costs the reader nothing if they already know, and prevents drop-off if they do not.
6. **Cut numeric clutter.** Round, group, or omit. A reader cannot retain "23.4%, 87.1%, 41.9%, 12.0%" in one paragraph.

---

## When to skip cognitive-load assessment

- Posts under 1,000 words (intrinsic load is bounded by length)
- News-analysis content (event-driven, density expected)
- Consumer / lifestyle content with low intrinsic load
- FAQ pages (each Q is self-contained by construction)

Run it on:
- Pillar pages and authority guides
- Technical tutorials and how-to content
- Data-research posts with multiple findings
- B2B comparison and case-study content over 2,000 words

---

## Attribution

The three-load model (intrinsic, extraneous, germane) and the four-item working-memory ceiling come from cognitive-load theory (Sweller; Cowan 2001). The application of this model to design quality comes from the impeccable plugin v3.1.1 (Paul Bakaus, Apache 2.0, https://github.com/pbakaus/impeccable). This reference adapts the framework from UI ergonomics to editorial ergonomics: where impeccable measures items-per-screen, this measures concepts-per-section.
