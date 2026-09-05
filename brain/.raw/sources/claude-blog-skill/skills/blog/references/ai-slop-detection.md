# AI Slop Detection: Two-Tier Reflex Methodology

A phrase blocklist catches the obvious tells. Most AI-generated prose passes that filter and still reads like AI. The structural tics, the rhythmic flatness, the "everything is a three-clause sentence" cadence: those survive the first pass.

This reference defines a **two-tier reflex check** for editorial review. Run both passes before declaring a draft human-natural. Adapted from the impeccable plugin's UI slop methodology (Paul Bakaus, Apache 2.0).

---

## Why two tiers

LLMs converge on a small set of safe patterns. The first thing the model reaches for is the **first-order reflex**: the genre-obvious tell. Replace it and the model reaches for the **second-order reflex**, the next-most-trained pattern that survives anti-AI guidance.

Most AI-detection passes only check the first-order pattern. The result is "anti-AI" rewrites that still read like AI because the structural pass was never run.

**Note on terminology**: this file uses **"first-order"** and **"second-order"** for the two detection passes. Elsewhere in the project, "Tier 1 / Tier 2 / Tier 3" refers to *source authority* (Google Search Central = Tier 1, Ahrefs = Tier 2, reputable industry sources = Tier 3). The two namespaces are intentionally kept separate; do not call the second-order detection pass "Tier 2."

Examples of the same idea across both tiers:

| Topic | First-order tell | Second-order tell that survives |
|---|---|---|
| SEO blog | "In today's digital landscape..." | Every H2 ends with a rhetorical question |
| SaaS post | "Game-changer," "Revolutionize" | Three-clause sentence rhythm, "While X, also Y" framings |
| How-to guide | "Dive into," "Unlock the potential" | Every step opens with an imperative verb identical in length |
| Listicle | "Cutting-edge," numbered fluff | Every item is ~80 words, identical structure |
| Thought leadership | "Comprehensive guide," "harness the power" | Hedge stack: "often," "typically," "may" within 20 words |

The point: **a draft can score zero on a phrase blocklist and still be obviously AI.**

---

## First-order reflex (phrase + lexical)

This is what the existing AI-detection in `blog-analyze` and `blog-rewrite` already covers. Documented here for completeness.

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

- AI trigger-word density > 5 per 1,000 words
- Type-Token Ratio (TTR) below 0.40 on long-form
- Burstiness (sentence-length standard deviation / mean) below 0.3

**Outcome of the first-order pass**: a "phrase-clean" draft. Necessary, not sufficient.

---

## Second-order reflex (structural + rhythmic)

These are the patterns LLMs default to **after** the obvious vocabulary is replaced. They are structural and rhythmic, so a vocabulary swap doesn't fix them. Run this pass on drafts that already passed the first-order check.

### Structural tics to flag

1. **Question-cadence H2s.** Every section heading is phrased as a question. Real long-form mixes question, statement, and noun-phrase headings. Flag if > 70% of H2 headings end with a question mark.

2. **The Here opener.** A paragraph opens with the word "Here" ("Here's why...", "Here are five..."). Once is fine. Three or more in a 1,500-word post is an AI fingerprint.

3. **Three-clause sentence rhythm.** Most sentences in a paragraph follow the structure `[clause], [clause], [clause].` The cadence is metronomic. Flag if > 50% of sentences in any 200-word window match this shape.

4. **False-balance framing.** Repeated use of "While X, also Y" or "On one hand X, on the other Y" without a real contrast. The model uses it to feel even-handed but it adds no information. Flag if it appears more than twice per 1,000 words.

5. **Hedge stacking.** Three or more hedges in a 20-word span ("It may often be the case that..."). Flag any 20-word window with > 2 of: may, might, often, typically, generally, usually, tend to, perhaps, somewhat, likely.

6. **Symmetric list bloat.** Every item in a numbered or bulleted list is the same length within +/- 10 words and follows the same syntactic structure. Real lists vary; some items need one line, others need a paragraph. Flag if list-item length standard deviation < 5 words.

7. **The wrap-up question.** Section ends with "What does this mean for [audience]?" or "Why does this matter?" Once per post is rhetorical; three or more is filler.

8. **Capsule transitions.** Each H2 opener begins with a single-word transition ("First..." "Next..." "Additionally..." "Crucially..."). Real prose buries transitions inside sentences. Flag if > 50% of H2 openers start with a transition word.

9. **The "key insight" tell.** The phrase "The key insight is..." or "What's important here is..." appears as a sentence-opener. This is the model telegraphing that it's about to summarize. Cut and let the sentence stand.

10. **Listicle introduction bloat.** Before the actual list, three or more paragraphs of "context." Real listicles get to the list. Flag if > 250 words of pre-list intro.

### Rhythmic signals to compute

- **Sentence-length flatness within paragraphs.** Compute SD of sentence length per paragraph; flag any paragraph with internal SD < 4.
- **Opening-word repetition.** Count first-word frequencies across all sentences. Flag if the top three first-words account for > 25% of all sentence openings.
- **Paragraph-shape flatness.** Compute SD of paragraph word counts across the post; flag if < 25 (real long-form varies dramatically).

---

## How to run the two-tier check

For `blog-rewrite` and `blog-reviewer`:

1. Run the first-order pass first (phrase + lexical). If it fails, fix and re-run before moving on.
2. Once the first-order pass is clean, run the second-order pass. Report each second-order pattern with line numbers and an example.
3. Do not declare "AI-detection passed" unless both passes are clean.

For `blog-write` (initial drafting):

- First-order is enforced at generation time via the persona's anti-phrase list.
- Second-order is checked once on the full draft before delivery.

---

## Output format

When reporting findings, use:

```
## AI Slop Detection Report

### First-order (Phrase + Lexical)
- Trigger phrases: [N found] -> [list with line numbers]
- AI trigger words: [N/1K words], [pass/fail at ≤5]
- TTR: [score], [pass/fail at ≥0.40]
- Burstiness: [score], [pass/fail at ≥0.3]

### Second-order (Structural + Rhythmic)
- Question-cadence H2s: [X%], [pass/fail at ≤70%]
- "Here" openers: [N], [pass/fail at ≤2]
- Three-clause rhythm: [X%], [pass/fail at ≤50%]
- False-balance framings: [N/1K words], [pass/fail at ≤2]
- Hedge stacking: [N windows], [pass/fail at 0]
- Symmetric list bloat: [N lists], [pass/fail at 0]
- Wrap-up questions: [N], [pass/fail at ≤2]
- Capsule transitions on H2s: [X%], [pass/fail at ≤50%]
- "Key insight" sentence openers: [N], [pass/fail at 0]
- Listicle intro bloat: [pre-list words], [pass/fail at ≤250]
- Sentence-length flat paragraphs: [N], [pass/fail at 0]
- Opening-word repetition: [top-3 share], [pass/fail at ≤25%]
- Paragraph-shape SD: [value], [pass/fail at ≥25]

### Verdict
First-order: [PASS / FAIL]
Second-order: [PASS / FAIL]
Overall: [PASS only if both passes clean]
```

---

## Why this matters for ranking + AI citations

- **Editorial quality risk**: content that lacks experience and original perspective is easier to classify as interchangeable consensus content. Second-order patterns are a warning sign, even when no specific Google update is cited.
- **AI citations**: ChatGPT and Perplexity reward citable, distinctive passages. Second-order tics produce interchangeable prose that no AI surface has reason to prefer over the source it was trained on.

The two-tier check is the editorial parallel to impeccable's "design slop" methodology: vocabulary-clean is necessary but not sufficient; structural distinctiveness is what separates citeable content from indexable filler.

---

## Attribution

The two-tier first-order / second-order reflex methodology is adapted from the impeccable plugin v3.1.1 (Paul Bakaus, Apache 2.0, https://github.com/pbakaus/impeccable). The original applies it to UI design cliches ("observability -> dark blue"). This reference adapts the same mental model to prose.
