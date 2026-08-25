# Execution Workflow: Order, Context Injection, Scorecard

> Reference document for `blog-cluster`. Loaded on demand during Execute Phase.

## Execution order

The order in which posts are written matters for two reasons:

1. The pillar must exist before any spoke can link to its real filename.
2. High-priority posts written first establish authority on the most
   impactful terms while subsequent posts add supporting depth.

### Priority algorithm

```
1. Pillar always first (establishes the hub).
2. Sort clusters by combined estimated search volume (highest first).
3. Within each cluster, sort posts by estimated volume (highest first).
4. If more than 2 clusters, alternate between clusters for the first pass
   (diversifies the early content spread).
```

### Example queue

```
Seed: "AI marketing for small business" (3 clusters, 1 pillar + 7 spokes)

1. [P]   AI Marketing for Small Business: Complete 2026 Guide
2. [B1]  Best AI Marketing Tools for Small Business in 2026     (Cluster B, top volume)
3. [A1]  How to Use AI for Small Business Marketing             (Cluster A, top volume)
4. [C1]  How Much Does AI Marketing Actually Cost a Small Business?
5. [B2]  AI Social Media Tools for Small Business Compared
6. [A2]  AI Content Creation for Small Business: Tools and Workflow
7. [C2]  AI Marketing ROI: A Small Business Case Study
8. [A3]  ChatGPT for Small Business Marketing: 12 Practical Use Cases
```

## Context injection per `blog-write` call

The key innovation of this skill is the **cluster context block** prepended
to every `blog-write` invocation. It tells the writer exactly how this post
fits into the larger structure and forces autonomous (headless) operation.

### Context block format

```
=== CLUSTER CONTEXT ===

CLUSTER: "<seed-keyword>" Topic Cluster
ROLE: [Pillar Page | Supporting Post]
CLUSTER GROUP: [Cluster name, e.g., "Cluster A: Content Creation"]
POSITION: Post <N> of <total> in execution queue

PRIMARY KEYWORD: <keyword>
SECONDARY KEYWORDS: <keyword1>, <keyword2>, <keyword3>
TEMPLATE: <template-type from blog-write template list>
WORD COUNT TARGET: <N> words

--- ALREADY WRITTEN (LINK TO THESE) ---
1. "<title>" at <filename.md> (primary keyword: <kw>)
   LINK INSTRUCTION: include one contextual link with anchor "<kw>" or natural variation.
2. "<title>" at <filename.md> (primary keyword: <kw>)
   LINK INSTRUCTION: include one contextual link if topically relevant.

--- NOT YET WRITTEN (USE PLACEHOLDERS) ---
- "<title>" (primary keyword: <kw>) will be written later in this execution
- "<title>" (primary keyword: <kw>) will be written later in this execution

For posts not yet written, insert a marker in the body in this exact format:
[INTERNAL-LINK: <anchor text> -> <expected-filename.md>]
The execution engine will replace it with a real link after the target is written.

--- LINKING REQUIREMENTS ---
- Minimum outgoing internal links in this post: <N>
- MUST link to: pillar page (filename: <pillar-filename.md>)
- SHOULD link to: same-cluster spokes listed above
- MAY link to: cross-cluster spokes if topically relevant (max 1)

=== AUTOMATION INSTRUCTIONS ===
- This is an automated cluster execution. Do NOT ask the user for input.
- Skip topic clarification (Phase 1 of blog-write). All parameters are above.
- Use the specified TEMPLATE; do not auto-detect.
- Use the specified WORD COUNT TARGET as an optional planning estimate;
  intent-dependent completeness controls final length.
- Skip outline approval. Write directly from the constraints.
- Keep standard research, image sourcing, and chart generation active.
- Proceed through all blog-write phases autonomously.

=== END CLUSTER CONTEXT ===

(Topic prompt continues below.)
```

### How `blog-write` consumes the context

The cluster context is prepended to the topic prompt. `blog-write` treats
topic, linking, and metadata requirements as constraints and runs in headless
mode. Length remains an optional planning estimate:

1. PRIMARY KEYWORD becomes the main SEO target.
2. SECONDARY KEYWORDS appear in subheadings and body naturally.
3. TEMPLATE is loaded directly (no auto-detection).
4. WORD COUNT TARGET guides planning but never blocks a complete article.
5. Topic clarification is skipped; all parameters are provided.
6. Outline approval is skipped; the writer proceeds directly.
7. Real links are inserted to ALREADY WRITTEN posts using the listed filenames.
8. `[INTERNAL-LINK: ... -> ...]` markers are inserted for posts NOT YET WRITTEN.
9. Cluster metadata is appended to the post's frontmatter.

### Cluster metadata frontmatter

Every post in the cluster receives this frontmatter block in addition to the
standard `blog-write` frontmatter:

```yaml
cluster: "<seed-keyword>"
cluster_role: "pillar"   # or "supporting"
cluster_group: "<cluster name, e.g. 'Cluster A: Content Creation'>"
cluster_position: "<N>/<total>"
```

## Backward link injection (after each post)

After `blog-write` completes for a post, the engine performs a backward
pass that resolves placeholders in previously written posts:

1. Read every previously written post in `cluster-<slug>/`.
2. Search for `[INTERNAL-LINK: <anchor> -> <expected-filename.md>]` markers
   that match the just-written filename.
3. Replace each match with a real markdown link: `[<anchor>](<filename.md>)`.
4. If no planned marker exists, do not edit automatically. Emit a proposed
   diff for user approval instead.

### Insertion rules

- Insert links inside existing paragraphs, never on their own line.
- Use the new post's primary keyword (or a variation) as anchor text.
- Do not add more than one backward link per existing post per new post.
- Do not exceed the per-post link-density caps in `cluster-architecture.md`.

## Optional hero image generation

If `blog-image` is available, generate a 16:9 hero image per post:

1. Build a topic-aware prompt from the post's title and primary keyword.
2. Call `/blog image generate` via the Task tool.
3. Delegate provider selection to `blog-image`, prefer current Gemini image models when available, and record the selected model ID.
4. Save to `cluster-<slug>/images/<post-slug>-hero.png`.
5. Add `coverImage: "images/<post-slug>-hero.png"` to the post frontmatter.
6. Insert `![<descriptive alt>](images/<post-slug>-hero.png)` near the top of the body.

If image generation is unavailable, log one warning at the start of execution and
proceed without images. Do not retry per post. Do not block.

## Failure handling

| Scenario | Behavior |
|----------|----------|
| `blog-write` returns an error or times out | Log the failure with reason. Mark this post as `failed` in the scorecard. Stop the batch unless the user explicitly resumes. |
| `blog-write` returns content below the word-count floor | Log the warning, save as `<slug>.draft.md`, mark as `under_target`, and stop the batch for manual review. |
| `blog-write` fails the answer-first or sources quality gate | Log the gate that failed, keep the file as `<slug>.draft.md`, mark remaining posts as skipped, and stop the batch. |
| Image generation fails | Continue without an image. Note the skipped post in the scorecard. |
| User cancels mid-execution | Save progress. On next `/blog cluster execute`, scan the directory for already-written files and resume from the next unwritten post. Note the resume in the scorecard. |
| Filesystem write fails | Abort execution, log the OS error, mark remaining posts as skipped, and do not retry automatically. |

## Per-post status log

After each post, append a status line to the running log:

```
Post <N>/<total>: "<title>"
  Status: written | failed | under_target | resumed
  File: <filename.md>
  Word count: <N> (target: <N>)
  Outgoing internal links: <N>
  Backward links injected into prior posts: <N>
  Template: <template>
  Hero image: generated | skipped (reason)
  Time: <approximate seconds>
```

## Cluster scorecard generation

After all posts in the queue have been attempted (written, failed, or
skipped), produce `cluster-<slug>/cluster-scorecard.md`:

### Sections to include

1. **Summary**: seed keyword, total posts attempted, total written, total
   failed, total words, total internal links, approximate execution time.
2. **Per-post quality scores**: call `/blog analyze` on each successful post
   in parallel via Task. Record the 5-category score and the cluster average.
3. **Cluster cohesion score** (0 to 100, formula below).
4. **Link audit**: per-post outgoing and incoming counts; orphan-spoke flags
   (less than 2 incoming links); list of unresolved `[INTERNAL-LINK]` markers.
5. **Cannibalization check**: any two posts sharing primary keyword (block);
   any pair with greater than 70 percent keyword overlap (warn). Recommend
   `/blog cannibalization` for a deeper pass.
6. **Image summary**: hero images generated, hero images skipped (with reasons).
7. **Coverage analysis**: a per-cluster table (name, posts written, intent,
   status), and a list of identified keywords with no targeting post.
8. **Recommended next actions** (the ordered list below).

### Cluster cohesion score formula

```
cohesion = round(
  0.40 * link_reciprocity_pct      # 0..100, % of cluster links that are bidirectional
  + 0.25 * incoming_coverage_pct   # 0..100, % of posts with at least 2 incoming links
  + 0.20 * intent_diversity_pct    # 0..100, distinct intents / max possible
  + 0.15 * template_diversity_pct  # 0..100, distinct templates / total posts
)
```

Bands: 90+ exemplary, 80-89 strong, 70-79 acceptable, below 70 needs work.

### Recommended next actions (default order)

1. Run `/blog seo-check` on each post for on-page validation.
2. Run `/blog schema` to add `BreadcrumbList`, `ItemList`, and `Article` markup.
3. Run `/blog cannibalization` across the full cluster directory.
4. Run `/blog repurpose` on the pillar to seed social, email, and YouTube assets.
5. For any post flagged `under_target` or `failed`, run `/blog rewrite` or `/blog write` manually.
6. Optional: `/blog audio` for narration of the pillar; `/blog calendar` to schedule publication.

## Resume capability

If a previous execution was interrupted:

1. Scan `cluster-<slug>/` for files matching the planned spoke slugs.
2. Mark matched posts as `pre_existing` in the queue.
3. Skip them during this execution.
4. Run only the backward-link injection pass on pre-existing posts (in case
   they reference posts that were not yet written when they were created).
5. Note in the scorecard: `Resumed execution. <N> posts pre-existing.`

## Output directory layout

```
<cwd>/
└── cluster-<seed-slug>/
    ├── cluster-plan.json
    ├── cluster-map.html
    ├── images/                       (created if blog-image is available)
    │   ├── pillar-<slug>-hero.png
    │   └── <spoke-slug>-hero.png
    ├── pillar-<slug>.md
    ├── <spoke-slug>.md               (one per spoke)
    └── cluster-scorecard.md
```

Slug rules: lowercase, hyphens only, no special characters. Match
`blog-write`'s default slug convention so the two skills agree on filenames.
