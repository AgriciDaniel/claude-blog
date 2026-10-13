---
name: blog-cluster
description: >
  Semantic topic cluster planning and automated execution engine for claude-blog.
  Performs SERP-based keyword research, groups keywords by search intent and
  SERP overlap, builds a hub-and-spoke cluster architecture, generates an
  interactive SVG cluster map, and executes the full cluster by orchestrating
  blog-write calls with shared cluster context and automatic internal-link
  injection. Fills the strategy-to-execution gap: blog-strategy plans the
  blueprint, blog-cluster builds the house.
  Use when user says "blog cluster", "topic cluster", "content cluster",
  "cluster plan", "cluster execute", "cluster map".
license: MIT
compatibility: Requires Claude Code and claude-blog (provides blog-write, blog-chart, blog-image)
metadata:
  author: AgriciDaniel
  version: "2.3.1"
  category: blog
user-invocable: true
argument-hint: "[plan|execute] [seed-keyword|cluster-plan.json]"
---

# Blog Cluster (Semantic Topic Cluster Engine)

Bundled paths below use host Markdown substitution of `${CLAUDE_SKILL_DIR}`;
it is not an exported shell variable. Resolve them before execution, quote
paths, and refuse nonabsolute overrides. Pass `blog_reference_root` resolved
from `${CLAUDE_SKILL_DIR}/../blog/references`, `blog_template_root` from
`${CLAUDE_SKILL_DIR}/../blog/templates`, and needed sibling roots to agents.
Read the main reference `orchestration-details.md` before loading project
context; pass only its helper-fenced output to downstream agents.

Plans and executes entire interlinked content ecosystems from a single seed
keyword. Three layers: Semantic Clustering (the brain), Cluster Architecture
(the structure), and Execution Engine (the machine).

> Adapted from the **semantic-cluster-engine** submission by Lutfiya Miller
> (winner, AI Marketing Hub Pro Challenge, March 2026, 95/100 Exemplary).
> Original repository: no longer available as of 2026-10-12
> This port keeps the Plan + Execute architecture and the cluster context
> innovation, removes brand-specific (ScienceExperts.ai) styling and image
> prompts, and routes through claude-blog's existing sub-skills.

## Commands

| Command | What it does |
|---------|--------------|
| `/blog cluster` | Interactive. Asks whether to plan or execute. |
| `/blog cluster plan <seed-keyword>` | SERP-based semantic analysis. Outputs cluster plan + map. |
| `/blog cluster plan --from strategy [path]` | Imports existing `blog-strategy` cluster build plan and validates against SERP data. |
| `/blog cluster execute [path-to-plan]` | Sequential `blog-write` calls with cluster context and auto-interlinks. |

## Key references (load on demand)

- `${CLAUDE_SKILL_DIR}/references/semantic-clustering.md` (SERP overlap analysis, intent classification, keyword universe expansion)
- `${CLAUDE_SKILL_DIR}/references/cluster-architecture.md` (hub-and-spoke specs, schema strategy, link-density rules)
- `${CLAUDE_SKILL_DIR}/references/execution-workflow.md` (execution order, context injection, scorecard, failure handling)

## Cross-references to existing claude-blog skills

| Skill | When this skill calls it |
|-------|--------------------------|
| `/blog strategy` | Upstream planning. `plan --from strategy` consumes its Cluster Build Plan tables. |
| `/blog write` | Per-post execution. Each spoke and the pillar are produced by `blog-write` with a prepended cluster-context block. |
| `/blog chart` | Invoked internally by `blog-write` for inline SVG charts. No direct call from this skill. |
| `/blog image` | Not called by this skill. Each post's hero is created once by `blog-write`'s delivery contract (via `generate_hero.py`); see Step 4. |
| `/blog seo-check` | Recommended after execution for per-post on-page validation. |
| `/blog cannibalization` | Recommended after execution to confirm zero keyword overlap across the cluster. |
| `/blog schema` | Recommended after execution to add `BreadcrumbList`, `ItemList`, and `Article` schema. |

This skill never modifies files belonging to other skills. It calls them via the Task tool or as orchestrated sub-skills.

## Command Routing

1. Parse the user's command to determine the sub-command.
2. If the user typed only `/blog cluster`, ask: "Would you like to **plan** a new cluster or **execute** an existing plan?"
3. Route:
   - `plan <keyword>` to the Plan Phase (below)
   - `plan --from strategy [path]` to the Strategy Import flow (below)
   - `execute [path]`, `build`, or `run` to the Execute Phase (below)

---

## Plan Phase: `/blog cluster plan <seed-keyword>`

Reference: `${CLAUDE_SKILL_DIR}/references/semantic-clustering.md`

### Step 1. Seed keyword expansion

Use WebSearch to expand the seed into a keyword universe of 30 to 50 phrases:

1. Direct search of `<seed>` to capture related searches and "People also ask".
2. Long-tail expansion: `<seed> guide`, `<seed> tips`, `<seed> tools`, `<seed> examples`, `<seed> vs`, `best <seed>`, `how to <seed>`.
3. Question mining: `what is <seed>`, `how does <seed> work`, `why <seed>`, `<seed> for beginners`.
4. Intent variants: add commercial modifiers (best, top, review, comparison, pricing), informational modifiers (guide, tutorial, explained, examples), and transactional modifiers (buy, download, tool, software, service).
5. Year freshness: `<seed> <current year>`. Take the current year from the system date; never hard-code a year.

### Step 2. Semantic clustering

Group the expanded keywords using the priority rules in `${CLAUDE_SKILL_DIR}/references/semantic-clustering.md`:

1. **SERP Overlap Analysis** is the primary signal. Two keywords with 4 or more shared top-10 results usually target the same intent and should be considered for one post.
2. **Intent Classification** assigns each keyword to informational, commercial, transactional, or navigational.
3. **Entity Mapping** identifies the people, products, frameworks, and organizations Google associates with the topic.
4. **Grouping** combines keywords that share intent and topical proximity. Each group becomes one branch of the hub and spoke.

### Step 3. Cluster architecture design

Reference: `${CLAUDE_SKILL_DIR}/references/cluster-architecture.md`

Build the hub and spoke:

- **Pillar (hub)**: targets the broadest keyword. Word count 2,500 to 4,000. Template `pillar-page`. Links down to every spoke.
- **Spokes**: each targets a long-tail cluster. Word count 1,200 to 1,800. Template auto-selected by intent. Links up to the pillar and across to siblings.

Cluster formation rules:

- Normal mode: 2 to 5 clusters per pillar, 2 to 4 spokes per cluster, total 1 pillar plus 5 to 15 spokes.
- Small-cluster mode: for narrow seeds, allow 1 pillar plus 2 to 4 spokes only after warning the user and asking for confirmation.
- Every spoke targets a unique primary keyword (zero cannibalization).

### Step 4. Internal link matrix

For each spoke `S`:

- `S` to Pillar (always; anchor text uses the pillar's primary keyword).
- Pillar to `S` (always; anchor text uses `S`'s primary keyword).
- `S` to other spokes in the same cluster (2 to 3 links each, contextual anchors).
- `S` to spokes in adjacent clusters (0 to 1 links, only when semantically relevant).

Verify every spoke has at least 2 incoming links. Count total planned interlinks.

### Step 5. Generate output files

All plan and execute artifacts go into a single subdirectory of the current working directory. Canonicalize the output directory, refuse symlinks, and reject writes outside the cluster directory. Slugs must match lowercase letters, numbers, and hyphens only; reject absolute paths, `..`, path separators inside slugs, and hidden control characters.

```
<cwd>/
└── cluster-<seed-keyword-slug>/
    ├── cluster-plan.json
    ├── cluster-map.html
    ├── pillar-<slug>.md       (Execute Phase)
    ├── <spoke-slug>.md        (Execute Phase, one per spoke)
    └── cluster-scorecard.md   (Execute Phase)
```

#### `cluster-plan.json` schema

```json
{
  "seed_keyword": "<seed>",
  "generated_at": "YYYY-MM-DDTHH:MM:SSZ",
  "pillar": {
    "id": "P",
    "title": "Title of the pillar",
    "primary_keyword": "broadest keyword",
    "secondary_keywords": ["..."],
    "search_volume_estimate": "high|medium|low",
    "template": "pillar-page",
    "word_count_target": 3000,
    "cluster": "pillar"
  },
  "clusters": [
    {
      "name": "Cluster A: Theme",
      "intent": "informational|commercial|transactional",
      "color": "#2563eb",
      "posts": [
        {
          "id": "A1",
          "title": "Post title",
          "primary_keyword": "long-tail keyword",
          "secondary_keywords": ["..."],
          "search_volume_estimate": "high|medium|low",
          "template": "how-to-guide",
          "word_count_target": 1500,
          "links_to": ["P", "A2"],
          "links_from": ["P", "A2"]
        }
      ]
    }
  ],
  "total_posts": 9,
  "total_interlinks": 23,
  "estimated_total_words": 18000
}
```

Note: volume estimates are relative indicators (high, medium, low) derived from SERP signals, not absolute search volumes. For precise data, the user should consult Ahrefs, SEMrush, or DataForSEO (claude-blog provides the `seo-dataforseo` companion sibling).

#### `cluster-map.html` (XSS-safe)

A static, self-contained HTML file with an embedded SVG visualization. Hard rules for the writer:

- No inline `<script>` blocks. No `onclick`, `onmouseover`, or any `on*` event attributes anywhere in the document.
- No external script `<src>` references.
- Every text label drawn into the SVG (titles, keywords, cluster names) must be escaped: replace `&` with `&amp;`, `<` with `&lt;`, `>` with `&gt;`, `"` with `&quot;`, and `'` with `&#39;` before insertion.
- Hover effects use CSS `:hover` only. No JavaScript.
- Use `<title>` child elements inside SVG nodes for accessible tooltips (browser native, no script).

The map shows: a central pillar node, color-coded cluster groups radiating outward, spoke nodes within each cluster, and link lines connecting related nodes.

### Step 6. Present plan to user

Show a summary table of clusters and posts, total interlinks, estimated words, and the file paths. Ask for confirmation before proceeding to execution. Wait for explicit user approval. Do not auto-execute.

---

## Strategy Import: `/blog cluster plan --from strategy [path]`

Bridges `blog-strategy` output into a cluster plan.

1. Locate strategy output. Scan the current directory (or the user-specified path) for a file containing a `Cluster Build Plan` table with the columns `# | Spoke Topic | Template | Target Keyword | Word Count | Internal Links` (the format produced by `/blog strategy`).
2. Parse the table. Extract the pillar row (marked `P`), the spoke rows, template assignments, target keywords, word counts, and link relationships.
3. Validate and enrich. Run SERP overlap validation (Plan Phase Step 2) on each keyword. Add volume estimates and verify cluster groupings semantically.
4. If SERP data contradicts the strategy table, flag the conflict; do not silently override the user's strategic intent.
5. Generate `cluster-plan.json` and `cluster-map.html` using the same outputs as the standard Plan Phase.
6. Present the converted plan with any SERP-based adjustments highlighted, and wait for user confirmation.

---

## Execute Phase: `/blog cluster execute [path-to-plan]`

Reference: `${CLAUDE_SKILL_DIR}/references/execution-workflow.md`

### Step 1. Load plan

Read `cluster-plan.json` from the user-specified path or the most recent `cluster-*/cluster-plan.json` in the working directory. Validate JSON structure. If no plan exists, return: "No cluster plan found. Run `/blog cluster plan <seed-keyword>` first."

Before reading a user-supplied plan path, canonicalize it relative to the current working directory. Reject absolute paths, `..`, symlinks, non-`cluster-plan.json` filenames, and any path outside the selected cluster directory. Constrain all generated post, image, map, and scorecard outputs to that cluster directory.

### Step 2. Determine execution order

1. Pillar page first (so spokes can link to a known filename).
2. Then spokes, ordered by `(cluster priority, search_volume_estimate desc, post id alphabetical)`. Cluster priority is the sum of estimated volumes within the cluster (highest first).
3. Alternating between clusters when more than 2 clusters exist diversifies the early content spread.

### Step 3. For each post: build cluster context and call `blog-write`

**One-time cost question (before the first post).** Execution is bulk and
paid. Ask once, and wait for an explicit yes: "This plan has N posts. Each
post runs a full `blog-write` pass, one `blog-reviewer` pass (more if a gate
blocks, up to 3 iterations), and one hero image. A Gemini hero is one paid
image call per post (about N times the current per-image price on
https://ai.google.dev/gemini-api/docs/pricing). Proceed with Gemini heroes,
use free stock heroes only, or stop?" Record the answer in the cluster
context as `HERO: gemini` or `HERO: stock-only`. For `stock-only`, run
`generate_hero.py` with the Gemini key unset (`env -u GOOGLE_AI_API_KEY`).
The yes covers exactly N heroes; never regenerate in a loop. Report each
fallback or skip (a stock hero, a skipped post) as one line under
"Fallbacks and skips" in the final report.

Construct the cluster context block (full schema in `${CLAUDE_SKILL_DIR}/references/execution-workflow.md`) and prepend it to the topic prompt passed to the Task tool invoking `blog-write`. The context tells `blog-write` the cluster name, the post's role (pillar or spoke), the primary and secondary keywords, the chosen template, the word count target, the list of already-written posts (link to these), the list of upcoming posts (use `[INTERNAL-LINK]` placeholders), and the linking requirements for this post.

**Evidence provenance propagation.** The cluster context includes this directive
for every spoke and the pillar: "Keep material claims traceable to sources that
support them. Record dates, publisher/title details, retrieval notes,
methodology, and limitations when they help identify or interpret the source.
Use the publication's citation style. Drop unverifiable statistics and replace
contradicted ones."

This cascade preserves evidence discipline across batch execution without
turning a fixed source-record format into a score or gate. See
`${CLAUDE_SKILL_DIR}/../blog/references/flow-alignment.md`.

The context also instructs `blog-write` to run autonomously: skip topic clarification, skip outline approval, do not auto-detect template, do not pause.

Each post goes through `blog-write`'s full delivery contract (the canonical
sequence: draft, resolve visuals, render, init nonce, review, gates). Cluster
`[INTERNAL-LINK: anchor -> filename.md]` markers are draft-only: the
orchestrator resolves every one at the visuals step, before render. A marker
whose target is already written becomes a real link. A marker whose target is a
later post in the plan becomes a real relative link to that post's PLANNED
filename (the plan fixes every filename), which resolves once the cluster
finishes; the scorecard's link audit then confirms every target exists. A
marker with no planned target is removed. No marker may survive into a
delivered post.

Output format: standard markdown (`.md`) by default, matching `blog-write`'s default. If the user explicitly requests HTML, set the platform target accordingly. Do not impose any brand-specific CSS or wordmark; that is the user's responsibility downstream.

### Step 4. Hero images (no separate `blog-image` call)

Do not call `/blog image` from this skill. `blog-write`'s delivery contract
requires a hero for every post and creates it once through `generate_hero.py`
into that post's draft folder, so a second call would double the spend and
produce a competing file. The hero is therefore required, not optional: if no
hero can be produced for a post, that post fails the contract and the batch
stops under Step 6. Honor the `HERO:` answer from Step 3 and record the source
and model (from `hero-credit.txt`) per post in the scorecard.

### Step 5. Backward link injection

Earlier posts need links to later ones, but a post that has passed the
delivery contract must not be edited in place: any change to its markdown,
HTML, PDF, or hero invalidates the review nonce and the gates. Handle each
case explicitly:

1. **Prevent most edits.** Because forward markers resolve to planned
   filenames (Step 3), an earlier post already links to every later post the
   plan says it should. Check `links_to` and `links_from` in the plan.
2. **Target still in draft** (its contract has not run yet, for example when
   it is queued behind the post just written): replace the matching
   `[INTERNAL-LINK: keyword -> filename.md]` marker with `[keyword](filename.md)`
   in the markdown BEFORE the contract runs. No re-review is needed.
3. **Target already delivered and a link is still missing:** do not touch the
   file. Append a proposed edit to `cluster-<slug>/cluster-link-patches.md`
   (file, anchor text, the sentence to change, target filename) and show the
   list in the final report. If the user explicitly opts in to apply a patch,
   edit the markdown and then repeat the canonical sequence for that post:
   re-render, re-init the review nonce, re-review, re-run preflight `--strict`
   (max 3 iterations). Tell the user the number of extra reviewer runs first.
4. Cluster metadata (`cluster:`, `cluster_role:`, `cluster_group:`,
   `cluster_position:`) is written into each post's frontmatter during its
   own draft (Step 3), never added afterward.

### Step 6. Failure handling

If `blog-write` returns a quality-gate failure for any post, stop the batch immediately. Save progress, mark the failed post and all remaining posts as skipped, and tell the user to inspect or retry the failed post manually before continuing. Do not keep generating 5 to 15 posts after a quality failure, because that can create scaled-content-abuse risk.

If `blog-write` fails before content is generated because of a timeout or runtime error, log the failure in the scorecard and stop unless the user explicitly resumes after checking the cause.

If the user cancels mid-execution, save progress and note completed posts. On the next `/blog cluster execute`, detect already-written files and resume from the next unwritten post.

### Step 7. Generate `cluster-scorecard.md`

After all attempted posts complete, produce a markdown scorecard covering:

- Per-post status (written, failed, skipped) with file path and word count.
- Per-post quality score (call `/blog analyze` on each in parallel via Task) and the cluster average.
- Cluster cohesion score: a 0 to 100 composite of link reciprocity, intent diversity, template diversity, and keyword coverage (formula in `${CLAUDE_SKILL_DIR}/references/execution-workflow.md`).
- Internal-link audit: outgoing and incoming counts per post, orphan flags, unresolved `[INTERNAL-LINK]` markers.
- Cannibalization check: any two posts sharing primary keyword, or any pair with greater than 70% keyword overlap. Recommend running `/blog cannibalization` for a deeper pass.
- Hero summary: per-post hero source and model from `hero-credit.txt`, and any stock fallbacks.
- Link patches: the contents of `cluster-link-patches.md`, if any.
- Recommended next actions: schema generation (`/blog schema`), per-post SEO validation (`/blog seo-check`), repurposing (`/blog repurpose`).

### Step 8. Final report

Return a concise summary to the user with totals, the scorecard path, and the next-action commands.

---

## Output Artifacts (summary)

| File | Phase | Format |
|------|-------|--------|
| `cluster-plan.json` | Plan | JSON |
| `cluster-map.html` | Plan | Static HTML + inline SVG, no JavaScript |
| `pillar-<slug>.md` | Execute | Markdown (or platform-detected format) |
| `<spoke-slug>.md` | Execute | Markdown (or platform-detected format) |
| `cluster-link-patches.md` | Execute (only when delivered posts miss a planned link) | Markdown patch list |
| `cluster-scorecard.md` | Execute | Markdown |

---

## Quality Gates

| Gate | Check | Action on fail |
|------|-------|----------------|
| Cluster minimum | At least 2 clusters with at least 2 posts each | Warn during plan; suggest expansion |
| Cannibalization | No two posts share primary keyword | Block execution; require plan adjustment |
| Link completeness | Every post has 2 or more incoming internal links | Warn in scorecard |
| Length estimate | Pillars often need more depth than spokes | Pass to `blog-write` as optional planning context; never enforce a raw word minimum |
| Intent diversity | At least 2 distinct intents across clusters | Warn in scorecard |
| Template diversity | At least 3 distinct templates across the cluster | Warn in scorecard |

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Seed keyword too broad (more than 50 keyword variants) | Suggest narrowing the focus before clustering. |
| Seed keyword too narrow (fewer than 5 keyword variants) | Offer a smaller cluster (pillar plus 2 to 3 spokes) or suggest broadening. |
| WebSearch unavailable | Produce a draft plan only and require user confirmation, imported keyword data, or SERP data before execution. |
| `blog-write` fails a quality gate or content generation | Stop the batch, save progress, mark remaining posts as skipped, and require manual inspection or explicit resume. |
| `blog-write` not installed | Return: "blog-cluster requires claude-blog. Install it before running this skill." |
| `cluster-plan.json` malformed | Validate JSON and report parse errors with line numbers. |
| User cancels execution | Save progress; resume on next invocation with already-written posts auto-detected. |
| No hero can be produced for a post | The delivery contract requires one: that post fails and the batch stops (Step 6). Offer stock-only heroes. |

---

## Differentiation from related claude-blog skills

| Skill | Role | What blog-cluster adds |
|-------|------|------------------------|
| `blog-strategy` | Plans 3 to 5 content pillars and draws hub-and-spoke diagrams as a strategic exercise | Performs SERP-based semantic clustering, then executes the plan into real, interlinked posts. |
| `blog-calendar` | Schedules publication dates around topic clusters | Does not build clusters or write posts; this skill does both. |
| `blog-cannibalization` | Detects keyword overlap in existing content | Diagnostic only. blog-cluster prevents cannibalization at the planning stage. |
| `blog-write` | Writes one post at a time | blog-cluster orchestrates many `blog-write` calls with shared cluster context and bidirectional linking. |
| `blog-outline` | Generates a single SERP-informed outline | blog-cluster generates an outline-equivalent across an entire cluster, then writes the posts. |

blog-cluster is the general contractor: it analyzes the topic, draws the data-driven plan, and builds the entire structure from a single seed keyword.
