# Research Quality: Rubric, Pre-Flight Traps, Clustering, Freshness

claude-blog already enforces source-tier hygiene (Tier 1 to 3), source fidelity,
and claim-appropriate provenance. This reference adds four research-discipline
layers adapted from `last30days-skill` (Matt Van Horn, MIT,
https://github.com/mvanhorn/last30days-skill):

1. A **5-dimension quality rubric** for scoring research outputs
2. **Topic pre-flight checks** for catching keyword-trap topics before search burns time
3. **Cross-source clustering** rules to avoid synthesis echo from one upstream source
4. A **freshness floor** for time-sensitive content (30 or 90 days)

Apply when running `blog-researcher`, `blog-brief`, `blog-strategy`, or the new `blog-discourse` sub-skill.

---

## 1. The 5-dimension research quality rubric

Score every research output against these five dimensions before passing to `blog-writer`. Weighted total of 100.

| Dimension | Weight | What it asks |
|---|---|---|
| Groundedness | 30 | Every non-trivial claim ties to evidence that substantiates it. No "studies show" or "experts agree" without identifying who and what. Source identity, dates, methodology, limitations, URLs, and retrieval notes are included when needed to verify or interpret the claim. |
| Specificity | 25 | Named entities, exact numbers, dates beat general phrasing. "$47B Q3 2025 revenue" beats "tens of billions in revenue." Specific subreddit names, X handles, GitHub repos beat "the community says." |
| Coverage | 20 | At least two independent sources per load-bearing claim. At least two perspectives represented (proponent + critic, vendor + customer, expert + practitioner). Single-source dependency on a load-bearing claim is a failure. |
| Actionability | 15 | The reader can do something concrete with this. "Use X library, version Y, this way" beats "consider modern frameworks." Includes commands, configs, decision criteria, or a clear yes/no. |
| Format compliance | 10 | Research synthesis uses citations inline as `[name](url)` per `synthesis-contract.md`. No duplicate trailing Sources block when inline citations are present. Publishable drafts may include retrieval notes when they identify a changeable or undated source or change interpretation. No invented titles. No em-dashes. No raw-cluster dumps. |

### Scoring procedure

For each dimension, score 0 to its weight:
- Full weight: best-in-class
- 75%: strong with minor gaps
- 50%: mixed; major gaps remain
- 25%: weak; most checks fail
- 0: absent or actively wrong

A research output scoring below 70 should not be passed to `blog-writer` without remediation. Below 50 is a do-over.

### Reporting format

```
## Research Quality Report

| Dimension | Score | Max | Notes |
|---|---|---|---|
| Groundedness | 24 | 30 | 2 unsourced claims in paragraph 4 |
| Specificity | 22 | 25 | Strong; one "the platform" should be named |
| Coverage | 14 | 20 | Single-source on the load-bearing 47% stat |
| Actionability | 12 | 15 | Concrete in 4 of 5 sections; section 3 is abstract |
| Format compliance | 10 | 10 | All citations inline; no trailing block |
| **Total** | **82** | **100** | Strong; remediate the unsourced and single-source items |
```

---

## 2. Topic pre-flight: detect keyword-trap topics BEFORE searching

Some topic phrasings will never produce good research because their literal text does not match how humans actually discuss the subject. Detect these and reframe BEFORE the agent burns time on searches.

### Class 1: Demographic shopping query

- **Pattern**: "gift for {age} year old {gender}", "what to buy for my {relationship}", "best {product} for {demographic}"
- **Why it fails**: No human posts "I bought a 42-year-old man a gift." Real discussions use relationship + hobbies + budget. The literal phrase matches blog-spam, not real discourse.
- **Action**: ask ONE clarifying question: "Hobbies? Relationship? Budget range?" If the user declines to narrow, reframe to hobby-anchored phrasing ("gifts for cooking enthusiasts," "gifts for runners") and drop the literal age.

### Class 2: Numeric/age keyword trap

- **Pattern**: topic contains a specific number that collides with unrelated content (42 collides with Jackie Robinson and Hitchhiker's Guide; 100 collides with bench-press posts).
- **Why it fails**: the number dominates retrieval; signal drowns in noise.
- **Action**: strip the number from the search query unless semantically load-bearing ("GPT-4" yes; "40 year old man" no). Document the strip in the research notes.

### Class 3: Overly-literal concept phrase

- **Pattern**: "how to use X," "what is Y," "tutorial for Z."
- **Why it fails**: tutorial phrasing matches blog-spam titles, not how practitioners discuss the topic in forums or threads. Real Docker discussions say "my Docker setup," "nginx in Docker," "Compose tips," not "how to use Docker."
- **Action**: reframe from tutorial phrasing to discussion phrasing. "how to use Docker" becomes "Docker tips workflows" or "Docker production setups."

### Class 4: Generic single-noun

- **Pattern**: a single common noun with no specific hook (`bread`, `sneakers`, `coffee`, `headphones`).
- **Why it fails**: infinite corpus, no anchor; signal is noise.
- **Action**: ask the user to specify the angle (bread sourdough vs gluten-free vs sandwich; sneakers running vs basketball vs fashion) before any search.

### Pre-flight decision flow

1. Read the topic.
2. Match against Classes 1 to 4.
3. If matched, emit a one-line note in research output: `Pre-Flight: matched Class N. Reframing to: "<new query>".`
4. If not matched, proceed.

Skipping pre-flight on a trap topic creates avoidable research noise. Treat
pre-flight as a required workflow check and keep enough source provenance to
verify each material claim; no fixed citation form is required.

---

## 3. Step 0.55: named-entity decomposition

For named-entity topics (proper nouns, products, people, projects), decompose the topic into discrete searchable entities BEFORE searching. Ambiguous compound topics produce vague queries; decomposition produces sharp ones.

### Example

- **Topic**: "Nvidia earnings reaction"
- **Bad decomposition**: one search for the literal phrase.
- **Good decomposition**:
  1. `Nvidia Q3 2025 earnings numbers site:nvidia.com OR site:cnbc.com`
  2. `Nvidia earnings investor commentary site:x.com`
  3. `Nvidia earnings discussion site:reddit.com/r/stocks OR site:reddit.com/r/wallstreetbets`
  4. `AMD Intel competitive response Nvidia earnings`
  5. `Nvidia stock price reaction earnings`

Each decomposed query is sharp and platform-targeted. The synthesis weaves them back together.

### Decomposition checklist for any named-entity topic

- [ ] **Primary entity**: the topic itself (official site, primary public statements)
- [ ] **Counter-perspective**: critics, competitors, contrarians
- [ ] **Discourse**: where people actually discuss this (subreddit, X, forum)
- [ ] **Tangential entities**: founder, related products, parent company, related people
- [ ] **Time anchor**: when (Q3 2025, "last 30 days," "this week")

When a topic resolves to a person who ships code, add:
- [ ] GitHub username (recent commits, repos, releases)
- [ ] Their org's X / Twitter handle (in addition to their personal handle)

Document the decomposition at the top of the research output so reviewers can see the search plan.

---

## 4. Cross-source clustering: detect synthesis echo

When research returns five posts all citing the same upstream source (e.g. five articles all paraphrasing one McKinsey report), they are ONE source, not five. Synthesizing them as independent corroboration is synthesis echo and inflates apparent coverage.

### Clustering procedure

1. For each retrieved source, identify the **upstream source** of the load-bearing claim (the statistic, the quote, the original analysis).
2. Group retrieved sources by upstream source.
3. Surface the upstream source in the synthesis as the primary citation. Mention secondary sources only if they add genuine analysis beyond the upstream.
4. Score the cluster:
   - **Healthy cluster**: multiple upstream sources independently making compatible claims. Score = number of independent uppers.
   - **Echo cluster**: multiple downstream sources, one upper. Score = 1, regardless of count.
5. The "Coverage" dimension of the rubric above is scored on cluster count, not raw retrieval count.

### Reporting in research outputs

For every load-bearing claim, mark it explicitly:

```
**Claim**: AI Overview coverage is methodology-dependent: about 20% of searches
in Ahrefs data cited by SparkToro, with an unconfirmed BrightEdge upper estimate
around 48%.
**Upstream**: [SparkToro 2026 zero-click study](https://sparktoro.com/blog/in-2026-less-than-one-third-of-google-searches-still-send-a-click/)
**Echo sources** (paraphrase the upstream): [SEO trade article](url), [agency recap](url)
**Independent corroboration**: [Semrush AI Overviews study](url) reports about 15.7% in November 2025 after recalibration.
**Cluster health**: 2 defensible sources (Ahrefs/SparkToro + Semrush), with BrightEdge quarantined as an unconfirmed upper estimate.
```

This format makes the difference between echo and corroboration explicit. The writer can then decide whether to lead with the original or note the independent confirmation.

---

## 5. Freshness floor: 30 days for time-sensitive, 90 days for evergreen

For time-sensitive topics, require at least 2 sources published within the last 30 days. For evergreen topics, relax to 90 days. Older sources can be cited for historical context but must not be load-bearing.

### Topic classification

| Topic type | Freshness floor | Example |
|---|---|---|
| News / current events | 30 days, at least 2 sources | "Nvidia earnings reaction" |
| Trend analysis | 30 days, at least 2 sources | "State of AI search in 2026" |
| Product update / release | 30 days, at least 1 source | "What's new in React 19" |
| Practitioner workflow | 90 days, at least 2 sources | "Best Docker dev loop" |
| Evergreen explainer | 90 days, at least 2 sources | "How JWT auth works" |
| Historical / definitional | No floor | "What is the EU AI Act" |

### Enforcement

`blog-researcher` should report freshness in the research output:

```
## Source Freshness Summary

| Source | Date | Within floor? |
|---|---|---|
| SparkToro 2026 zero-click study | 2026-06-09 | Yes (30d) |
| Google Search Status Dashboard | 2026-06-30 | Yes (30d) |
| Google FAQ and HowTo rich-result changes | 2023-08-08 | Historical policy baseline |
| Semrush AI Overviews study | 2025-11 | NO (historical context only) |

Floor satisfied: 2 sources within 30d (need >=2). PASS.
```

If the floor is not satisfied, the research output is incomplete. The agent should either find more recent sources or explicitly reclassify the topic as evergreen.

---

## Attribution

The 5-dimension quality rubric, the four keyword-trap classes (demographic shopping, numeric trap, overly-literal phrase, generic single-noun), the named-entity decomposition pattern (Step 0.55), the cross-source clustering procedure, and the freshness floor concept are adapted from `last30days-skill` v3.2.1 (Matt Van Horn, MIT, https://github.com/mvanhorn/last30days-skill). The original applies them to multi-platform discourse retrieval (Reddit / X / YouTube / TikTok / HN / Polymarket). This reference adapts the same mental models to general blog research, API-free, applied as prompt discipline by `blog-researcher` and `blog-discourse`.
