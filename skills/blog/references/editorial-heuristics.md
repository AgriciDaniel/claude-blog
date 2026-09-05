# Editorial Heuristics: Ordinal Scoring Rubric (0 to 4)

The 100-point system in `quality-scoring.md` (sibling file) tells you a post scores 78. This ordinal rubric tells you **which sections are P0 blockers and which are P3 polish**. Complementary, not competing; run both for actionable review.

Adapted from Nielsen's 10 Usability Heuristics via the impeccable plugin (Paul Bakaus, Apache 2.0). Original scores UI; this version scores editorial.

## Scoring scale + severity tags

| Score | Meaning | Severity tag | When to assign |
|---|---|---|---|
| 0 | Absent or actively wrong | P0 (blocking) | Fabricated stat, broken structure, plagiarism risk |
| 1 | Major gaps; most checks fail | P1 (ship-blocker) | Missing source on load-bearing claim, major reader-task failure |
| 2 | Mixed; important checks fail | P2 (publish then iterate) | Weak heading, missing schema, suboptimal opener |
| 3 | Good; minor gaps | P3 (nice to have) | Cosmetic, marginal SEO, stylistic preference |
| 4 | Genuinely excellent (rare) | (none) | "Would cite in a meta-review of best-practice blog craft" |

A 0 or 1 on any heuristic generates at least one P0 or P1. Most strong production posts land 2 to 3 across the board.

## Nielsen mapping

| Nielsen original (UI) | Editorial adaptation |
|---|---|
| 1. Visibility of system status | 1. Visibility of intent |
| 2. Match between system and real world | 2. Heading and section content match |
| 3. User control and freedom | 3. Reader control and exit |
| 4. Consistency and standards | 4. Voice and standards consistency |
| 5. Error prevention | 5. Fabricated-stat prevention |
| 6. Recognition rather than recall | 6. Recognition over recall |
| 7. Flexibility and efficiency of use | 7. Skimmer vs deep-reader flexibility |
| 8. Aesthetic and minimalist design | 8. Information-density discipline |
| 9. Help recognize, diagnose, recover | 9. Failure-recovery copy |
| 10. Help and documentation | 10. Sources and related documentation |

Nielsen reference: Jakob Nielsen, "10 Usability Heuristics for User Interface Design," NN/g, 1994 (revised 2020). https://www.nngroup.com/articles/ten-usability-heuristics/

## The 10 Editorial Heuristics

### 1. Visibility of intent

Reader knows within 5 seconds what the post is, what they will learn, and roughly how long it takes.

**Check for**: title reflects body (no clickbait drift); meta description previews substance; "Key Takeaways" or TL;DR box (3 to 5 bullets) at top; reading time / word count visible; H1 matches title.

| Score | Criteria |
|---|---|
| 0 | Title misleading or absent; no summary; reader infers topic |
| 1 | Title present; nothing else orients the reader |
| 2 | Title and meta present; no summary box |
| 3 | Summary present but generic |
| 4 | Title, meta, and summary all reinforce a specific promise the body keeps |

### 2. Heading and section content match

A heading is a contract; the section must deliver in the order the reader expects.

**Check for**: each H2 promise fulfilled in the first 100 words of that section; no bait-and-switch; problem-then-solution order; domain terms used as the audience uses them.

| Score | Criteria |
|---|---|
| 0 | Headings disconnected from section content |
| 1 | Major mismatch on more than half the H2s |
| 2 | Some H2s fulfill; others bury or redirect |
| 3 | Most sections deliver on their heading; minor reordering needed |
| 4 | Every H2 is a contract the section keeps in the opening paragraph |

### 3. Reader control and exit

Long-form prose can trap the reader. Good blogs let them scan, jump, and bail without losing the thread.

**Check for**: TOC on posts over 1,500 words; internal jump links; H2s self-contained (passage-level citability); clear "what next" at end.

| Score | Criteria |
|---|---|
| 0 | One wall of text; no navigation |
| 1 | Sections exist but readers cannot skim |
| 2 | Navigation partial; some sections require previous context |
| 3 | TOC present, most sections standalone |
| 4 | Skim-readable end to end; self-contained sections; clear exits; downstream paths |

### 4. Voice and standards consistency

Within a post, terminology, tone, formatting, and structural patterns must not drift.

**Check for**: same term for same concept throughout (not "AI" then "LLM" then "model" arbitrarily); stable cadence; bullet vs prose decision applied consistently; citation format identical; heading capitalization consistent.

| Score | Criteria |
|---|---|
| 0 | Reads like three drafts stitched together |
| 1 | Multiple voice or terminology shifts |
| 2 | Mostly consistent; occasional drift |
| 3 | One or two minor inconsistencies |
| 4 | Reads as one author writing in one sitting |

### 5. Fabricated-stat prevention

Structure that prevents fabricated or unsourced data from entering the draft.

**Check for**: every material factual claim has support that actually
substantiates it; source URLs are reachable; relevant dates or study periods
appear when they affect meaning; methodology and limitations are present when
needed; changeable or undated sources have retrieval notes; and vague
"studies show" wording identifies the underlying evidence.

| Score | Criteria |
|---|---|
| 0 | Multiple unsourced numeric claims (P0) |
| 1 | Half of numeric claims unsourced |
| 2 | Most sourced; one or two suspicious |
| 3 | All material claims sourced; minor gaps in claim-appropriate provenance |
| 4 | Sources faithfully support every material claim, with the context needed to verify and interpret them |

### 6. Recognition over recall

Reader should not have to remember what was said three sections ago to follow the current paragraph.

**Check for**: key terms redefined or aliased on reuse if introduced more than 500 words earlier; comparison tables for X-vs-Y (not buried prose); visual aids where data is dense; repeated context cues; numbered steps numbered in body.

| Score | Criteria |
|---|---|
| 0 | Reader must hold many threads to follow |
| 1 | High memory load throughout |
| 2 | Some sections require backtracking |
| 3 | Mostly recognition-friendly |
| 4 | Every section can be entered cold |

### 7. Skimmer vs deep-reader flexibility

The post should reward both modes: executive who scans, practitioner who reads end to end.

**Check for**: descriptive headings; lead-ins that state the section point at
the depth the reader's intent requires; passages that are independently clear
without padding to a fixed length; lists where lists are right and prose where
prose is right; optional visible Q&A only when genuine reader questions remain.
Q&A presence and passage length earn no points by themselves.

| Score | Criteria |
|---|---|
| 0 | Only readable end-to-end; no skim affordances |
| 1 | Some headings, but key sections still obscure their point |
| 2 | Skim affordances in some sections; several openings need clearer framing |
| 3 | Most sections support scanning and sustained reading; minor navigation or framing gaps remain |
| 4 | Rewards both modes with clear headings, intent-appropriate openings, useful navigation, and self-contained explanations |

### 8. Information-density discipline

Long does not equal valuable. Every paragraph should earn its place; padding is a slop signal.

**Check for**: paragraph pacing that fits the audience; an introduction that
states its purpose without needless delay; no SEO-padded conclusion; no filler
transitions ("Now, let's discuss..."); length appropriate to the topic.

| Score | Criteria |
|---|---|
| 0 | Padding pervasive; intro buries the lede; conclusion restates the post |
| 1 | Several difficult-to-follow paragraphs; multiple filler transitions |
| 2 | One bloat axis present (e.g. SEO-padded conclusion or long intro) |
| 3 | Minor bloat (1 to 2 long paragraphs or one filler transition); otherwise tight |
| 4 | Every paragraph earns its place; word count matches topic scope |

### 9. Failure-recovery copy

Post must handle reader confusion or partial knowledge.

**Check for**: glossary or inline definitions for jargon; "If you are new to X, read this first" links; clearly marked "for advanced readers" sections if they exist; examples for every abstract concept; acknowledgement of when a technique does not apply.

| Score | Criteria |
|---|---|
| 0 | Newcomers will bounce; no definitions; abstract claims without examples |
| 1 | Jargon undefined in most cases; few examples |
| 2 | Some jargon defined; examples for half of abstract claims |
| 3 | Most jargon defined or aliased; examples for most abstract concepts |
| 4 | Graceful for every audience tier: definitions, examples, signposts, scope notes |

### 10. Sources and related documentation

Even the best post is one node in a knowledge graph.

**Check for**: 3 to 10 contextual internal links; 3 to 8 outbound tier 1 to 3 sources; author bio with credentials; last-updated date visible; related-reads section at end.

| Score | Criteria |
|---|---|
| 0 | Isolated content; zero internal links; no author bio; no outbound sources |
| 1 | One or two internal links; author bio thin; few sources |
| 2 | Some links and basic bio; missing related-reads or last-updated date |
| 3 | Most signals present; minor gap |
| 4 | Fully embedded in content graph: 3+ internal, 3+ outbound, full bio, dates, related-reads |

## Reporting format

```
## Editorial Heuristics Report: [Title]

| # | Heuristic | Score | Severity | Note |
|---|---|---|---|---|
| 1 | Visibility of intent | 3 | P2 | Summary box generic; tighten the promise |
| 2 | Heading-content match | 4 | (none) | Every H2 fulfills in opener |
| 3 | Reader control | 2 | P1 | No TOC on 2,400-word post |
| ... | ... | ... | ... | ... |

### Prioritized fixes
- **P0**: (none)
- **P1**: Add TOC; define jargon (3 spots)
- **P2**: Tighten summary; alias "TTR" on reuse
- **P3**: Add bold lead-ins; smooth voice shift in paragraph 12
```

Ordinal score is independent of the 100-point system. Both can run on the same post; cross-checking surfaces inconsistencies (a 78/100 with three P0s means the 100-point system is missing a load-bearing failure mode).

## Attribution

Adapts Nielsen's 10 Usability Heuristics (Jakob Nielsen, NN/g, 1994 revised 2020) via the impeccable plugin's `heuristics-scoring.md` (Paul Bakaus, Apache 2.0, https://github.com/pbakaus/impeccable). The 0 to 4 ordinal scale, P0 to P3 severity, and per-dimension tables come from the impeccable adaptation. The 10 heuristics are translated from UI ergonomics to editorial ergonomics; see the Nielsen-mapping table above.
