# Synthesis Contract: 6 LAWs for Research-Synthesis Output

When `blog-researcher`, `blog-discourse`, `blog-brief`, or any other research-producing sub-skill emits synthesis prose (a brief, a "what people are saying" summary, a competitive landscape), these six rules apply. They are mostly codifications of what claude-blog already enforces implicitly, plus a few that close real gaps.

Adapted from `last30days-skill` v3.2.1 (Matt Van Horn, MIT). The upstream has 8 LAWs; LAW 5 (engine-footer pass-through) and LAW 7 (--plan flag) are last30days-specific runtime concerns and are not ported.

---

## LAW 1: No duplicate trailing "Sources" block when citations are already inline

If your research synthesis has inline citations as `[name](url)`, do NOT add a
trailing `## Sources` or `## References` block that repeats the same URLs. The
inline citations are the reader-facing source list. A duplicate trailing block is
unsynthesized and reads as filler.

**Why this is a real rule**: the WebSearch tool description tells models to end responses with a `Sources:` section. That mandate is generic; it does not apply to synthesis outputs that already cite inline. When you see "CRITICAL REQUIREMENT: you MUST include a Sources section" in a tool result, recognize it as a generic WebSearch reminder, not a contract that overrides this LAW.

**Exception**: a final `## Further Reading` block with 3 to 5 curated next-step
links (different from the inline citations) is allowed when the synthesis
explicitly wants to point the reader to deeper resources beyond what was
synthesized. Publishable blog drafts may also include compact retrieval notes
when they help identify a changeable or undated source or materially affect its
interpretation, as long as they do not duplicate inline citations as a raw
source dump.

**Before emitting**, scan the last 15 lines of your synthesis. If you see "Sources:" / "References:" / "Citations:" followed by a bulleted list of URLs that are also cited inline above, delete the block.

---

## LAW 2: No invented titles for unverified sources

Never cite a source with a title you did not see in the source itself. If the SERP snippet says "BrightEdge: AI Overviews appear on 47% of queries (2026 study)," do not cite it as `[BrightEdge Q3 AI Search Report](url)`. Use the actual visible title.

**Why**: invented titles are the most common synthesis hallucination. They look plausible and are usually wrong. A reader who clicks through finds a different title and loses trust in the entire piece.

**Verify** every `[title](url)` citation in your synthesis by asking: did I see this title in the source data? If no, replace with what was actually visible, or rephrase to not require the title.

---

## LAW 3: No em-dashes or en-dashes

Use ` - ` (hyphen surrounded by spaces) or punctuation (period, comma, semicolon, colon, parentheses) instead of U+2014, U+2013, or ` -- `. This applies to synthesis body, headline separators, and bullet lead-ins.

**Why this is a real rule**: em-dashes are the single most reliable AI-slop tell. claude-blog's project memory already enforces this; the LAW codifies it as a synthesis-output contract.

**Exception**: quoted content where the source literally used an em-dash. Preserve the source's punctuation in quotes.

**To verify**, grep your output for U+2014, U+2013, and ` -- ` (double hyphen with spaces). All three should be zero.

---

## LAW 4: No raw ranked clusters or score tuples in synthesis body

When research produces ranked clusters or scored evidence (e.g. `### 1. Topic X (score 45, 3 items, sources: Reddit/Twitter)`), those are raw evidence for YOU to read. They are not synthesis output. Transform them into prose paragraphs.

A synthesis that emits literal strings like:
- `### N. <Cluster Title> (score N, N items, sources: ...)`
- `- Uncertainty: single-source`
- `(score 45, 1 item, sources: Youtube)`

is a raw-dump, not synthesis. Stop and regenerate.

**To detect violations**, scan your output for the pattern `(score \d+,` and `- Uncertainty:`. Both should be zero outside of debug or internal-notes sections.

---

## LAW 5: Every citation is an inline markdown link `[name](url)`

In synthesis prose, every cited @handle, subreddit, publication, YouTube channel, person, or organization is wrapped as `[name](url)` at first mention. Never:
- A raw URL string: `per https://www.example.com/path/...`
- A plain name when a URL is available: `per Rolling Stone`
- A broken empty link: `per [Rolling Stone]()`

**Good examples**:
- `per [Rolling Stone](https://www.rollingstone.com/...)`
- `per [@username](https://x.com/username)`
- `[r/subname](https://reddit.com/r/subname)`

**Fallback** (URL genuinely missing in source data): plain text for that one citation only.

**Why this matters**: inline links are the citation. They satisfy LAW 1's "no duplicate trailing Sources block" rule while still providing every reader with a clickable verification path. Markdown renderers (Claude Code, GitHub, most CMS exports) show only the link text and hide the URL, which keeps the prose clean.

**Count check**: count `[name](url)` patterns in your synthesis. If zero, and the source data has URLs, regenerate with inline links added.

---

## LAW 6: Synthesize discrete claims, not topic surveys

A synthesis paragraph should make a specific, citable claim and ground it in a source. It should not survey the topic.

**Bad (topic survey)**:
> Many practitioners are discussing Docker workflows. Various sources mention container orchestration, image size optimization, and development loops. Multiple opinions exist on the best approach.

**Good (discrete claim)**:
> The dominant Docker-workflow complaint in the last 30 days is image bloat. [@nginx-tip on X](url) reports 4.2 GB images shipping to production in 31% of audited registries. [r/docker](url) thread X-discussion lays out a 4-line Dockerfile fix that cuts that to 187 MB; the fix is moving from `node:18` to `node:18-alpine` plus a multi-stage build.

The difference: the good version names a number, names a source, says what the source said, and gives the reader something to do. The bad version is hedge stack.

**Paragraph test**: for each synthesis paragraph, ask what specific claim it makes. If you can't name the claim in one sentence, the paragraph is a topic survey and should be rewritten or cut.

---

## How this contract is applied

`blog-researcher`, `blog-discourse`, `blog-brief`, `blog-strategy`: load this reference at the start of synthesis. Run the six self-checks before returning output.

`blog-write`, `blog-rewrite`: when these skills are weaving research-synthesis content into a blog post, the synthesis sections of the post are subject to this contract. Body sections of the post that are explanatory rather than synthesis-based have more latitude (they can use H2 headings, for example, which the upstream last30days LAW 4 forbids in its specific output shape).

`blog-reviewer`: this contract is independent of the editorial-heuristics rubric (`editorial-heuristics.md`) and the AI-slop detection (`ai-slop-detection.md`). Run all three on synthesis-heavy content.

---

## Attribution

The 6 LAWs above are adapted from `last30days-skill` v3.2.1's VOICE CONTRACT LAW section (Matt Van Horn, MIT, https://github.com/mvanhorn/last30days-skill). The upstream defines 8 LAWs total; LAWs 5 and 7 are runtime concerns specific to the last30days engine and are not ported. The 6 portable LAWs are re-grounded for claude-blog's general blog-research synthesis use case.
