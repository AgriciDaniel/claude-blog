# Editorial Pattern Review: Two-Tier Reflex Methodology

A project phrase list catches common voice mismatches. Structural repetition,
rhythmic flatness, and filler can still reduce editorial quality after a phrase
cleanup.

This reference defines a **two-tier reflex check** for optional editorial
review. It does not classify authorship and none of its metrics block delivery
or change the 100-point score.

---

## Why two tiers

Writers and generation systems can converge on the same familiar genre
patterns. The **first-order reflex** is an obvious wording habit; the
**second-order reflex** is a structural pattern that survives vocabulary edits.

Phrase-only edits can leave repetitive structure intact. Review both levels
when the project voice calls for it.

**Note on terminology**: this file uses **"first-order"** and
**"second-order"** for the two editorial review passes. Elsewhere in the
project, "Tier 1 / Tier 2 / Tier 3" refers to *source authority* (Google Search
Central = Tier 1, Ahrefs = Tier 2, reputable industry sources = Tier 3). The two
namespaces are intentionally kept separate; do not call the second-order review
"Tier 2."

Examples of the same idea across both tiers:

| Topic | First-order observation | Second-order observation |
|---|---|---|
| SEO blog | "In today's digital landscape..." | Every H2 ends with a rhetorical question |
| SaaS post | "Game-changer," "Revolutionize" | Three-clause sentence rhythm, "While X, also Y" framings |
| How-to guide | "Dive into," "Unlock the potential" | Every step opens with an imperative verb identical in length |
| Listicle | "Cutting-edge," numbered fluff | Every item is ~80 words, identical structure |
| Thought leadership | "Comprehensive guide," "harness the power" | Hedge stack: "often," "typically," "may" within 20 words |

The point: **a draft can score zero on a phrase list and still be repetitive or generic.**

---

## First-order reflex (phrase + lexical)

This is what the advisory style diagnostics in `blog-analyze` and
`blog-rewrite` cover. Documented here for completeness.

**Trigger phrases** (full list in `agents/blog-reviewer.md` and `scripts/analyze_blog.py`):

- "In today's digital landscape" / "In the ever-evolving"
- "It's important to note" / "It is worth mentioning"
- "Dive into" / "deep dive" / "delve"
- "Game-changer" / "Revolutionize" / "transformative"
- "Cutting-edge" / "state-of-the-art" / "robust"
- "Harness the power" / "Unlock the potential"
- "Leverage" (as a verb, non-financial)
- "Seamlessly" / "seamless integration"
- "Tapestry" / "rich tapestry" / "multifaceted"
- "Comprehensive guide" (in body text)
- "Furthermore" / "Moreover" (transition overload)
- Em dashes used as a stylistic flourish (any density)

**Lexical signals**:

- Configured style-list density
- Type-Token Ratio (TTR), interpreted cautiously against sample length
- Sentence-length variation

**Outcome of the first-order pass**: descriptive editing notes, never an
authorship verdict.

---

## Second-order reflex (structural + rhythmic)

These are structural and rhythmic patterns that a vocabulary swap does not
fix. Review them only as possible clarity, voice, or repetition problems.

### Structural patterns to review

1. **Question-cadence H2s.** Review whether repeated question headings suit the
   reader's task. Declarative, question, and noun-phrase headings can all work.

2. **The Here opener.** Repeated paragraph openings such as "Here's why" or
   "Here are five" may sound formulaic. Edit only when repetition weakens flow.

3. **Three-clause sentence rhythm.** Repeated `[clause], [clause], [clause]`
   structures can create a metronomic cadence. Review examples in context.

4. **False-balance framing.** Review "While X, also Y" or "On one hand X, on
   the other Y" when no meaningful contrast exists. Remove framing that adds no
   information.

5. **Hedge stacking.** Several hedges close together can obscure confidence and
   evidence. Review words such as may, might, often, typically, generally,
   usually, perhaps, somewhat, and likely in context.

6. **Symmetric list bloat.** Uniform list items may indicate padding when each
   point has different evidence needs. Keep parallel structure when it helps
   scanning; vary detail when the material warrants it.

7. **The wrap-up question.** Repeated endings such as "Why does this matter?"
   can become filler. Keep a question only when it advances the reader's
   decision.

8. **Repeated transitions.** Repeated H2 openers such as "First," "Next," or
   "Additionally" may sound mechanical. Retain them when sequence matters.

9. **Explicit summary openers.** Phrases such as "The key insight is" may be
   redundant. Cut them when the substantive sentence stands on its own.

10. **Listicle introduction bloat.** Review pre-list context for relevance and
    remove material that delays the reader without helping the decision.

### Rhythmic signals to compute

- **Sentence-length variation within paragraphs.** Describe the distribution
  and inspect passages that feel monotonous.
- **Opening-word repetition.** Count first-word frequencies and show examples
  without applying a universal threshold.
- **Paragraph-shape variation.** Describe paragraph lengths as an optional
  editing observation, not a pass/fail metric.

---

## How to run the two-tier check

For `blog-rewrite` and `blog-reviewer`:

1. Run the first-order descriptive pass.
2. Review second-order patterns with line numbers and examples.
3. Apply judgment: keep patterns that suit the audience and edit only those
   that reduce clarity, distinctiveness, or usefulness.

For `blog-write` (initial drafting):

- First-order preferences may be applied from the persona's style list.
- Second-order observations may be reviewed on the full draft when useful.

---

## Output format

When reporting findings, use:

```
## Editorial Pattern Review

### First-order (Phrase + Lexical)
- Trigger phrases: [N found] -> [list with line numbers]
- Configured style-list terms: [N/1K words], [advisory]
- TTR sample: [score], [descriptive only]
- Sentence-length variation: [score], [descriptive only]

### Second-order (Structural + Rhythmic)
- Question-cadence headings: [descriptive observation + examples]
- Repeated paragraph openers: [descriptive observation + examples]
- Repeated clause rhythm: [descriptive observation + examples]
- False-balance framing: [descriptive observation + examples]
- Hedge stacking: [descriptive observation + examples]
- Symmetric list structure: [descriptive observation + examples]
- Repeated wrap-up questions: [descriptive observation + examples]
- Repeated section transitions: [descriptive observation + examples]
- Explicit summary openers: [descriptive observation + examples]
- Listicle introduction pacing: [descriptive observation]
- Sentence and paragraph shape: [descriptive observation]

### Editorial Judgment
- Patterns that reduce clarity or distinctiveness: [list]
- Patterns retained because they fit the audience: [list]
- This review does not infer authorship and does not block delivery.
```

---

## Why this matters for editorial quality

- Repetition and filler can make content interchangeable and less useful.
- Distinctive value comes from accurate evidence, specific examples, and clear
  analysis, not from manipulating surface-level style metrics.

The two-tier check is the editorial parallel to impeccable's "design slop" methodology: vocabulary-clean is necessary but not sufficient; structural distinctiveness is what separates citeable content from indexable filler.

---

## Attribution

The two-tier first-order / second-order reflex methodology is adapted from the impeccable plugin v3.1.1 (Paul Bakaus, Apache 2.0, https://github.com/pbakaus/impeccable). The original applies it to UI design cliches ("observability -> dark blue"). This reference adapts the same mental model to prose.
