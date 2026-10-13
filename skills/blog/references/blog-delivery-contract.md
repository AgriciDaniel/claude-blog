# Blog Delivery Contract

The contract every blog must pass before being presented to the user. Five gates that fire automatically between content generation and delivery, plus an iteration loop that retries failures up to three times before escalating.

Resolve every executable core helper through the trusted absolute installed
scripts root described in `orchestration-details.md`:

```bash
: "${BLOG_SCRIPT_DIR:?owning skill must supply its resolved trusted scripts root}"
case "$BLOG_SCRIPT_DIR" in /*) ;; *) echo "ERROR: script dir must be absolute" >&2; exit 1 ;; esac
```

Never execute a same-named helper from the current project's `scripts/`
directory.

This contract is the v1.9.0 answer to a failure pattern from the v1.8.x cycle: skills had reviewers, but the reviewer ran as advisory and the writer presented sloppy drafts anyway. The fix is infrastructure, not effort. Same shape as `scripts/lint_prose.py` (v1.8.4) and `tests/test_installer_sync.py` (v1.8.6).

## Gate summary

| Gate | What it enforces | Failure mode | Implementation |
|---|---|---|---|
| 1. Capability Discovery | Required tools + agents are available before write begins | Block if no valid local hero and no permitted image path; block if reviewer agent missing | `scripts/blog_preflight.py --gate 1` |
| 2. Format Completeness | `.md` + `.html` + `.pdf` + `hero.(png\|jpg\|jpeg\|webp)` present and valid; no draft placeholders; HTML source hash matches the `.md` | Block on any missing or invalid artifact | `scripts/blog_render.py` renders `.html` and `.pdf`; `scripts/generate_hero.py` emits `hero.<ext>` |
| 3. Visual Verification | Rendered HTML has no SVG overflow, no console errors, valid JSON-LD | Block on any defect; preserve screenshots | `scripts/blog_preflight.py --gate 3` via `patchright` |
| 4. Content Review | `blog-reviewer` scores ≥ 90/100 AND zero P0 issues, with a matching nonce and no edits to the draft after the nonce was issued | Block + iterate | `agents/blog-reviewer.md` (now blocking) |
| 5. Asset + Link Integrity | Every image resolves, external links return 2xx or safety-validated 3xx (or an exact documented 403/405 exception), schema validates | Block on invalid assets, failed links or inconsistent schema wordCount | `scripts/blog_preflight.py --gate 5` |

All gates run sequentially inside step 6 of the canonical delivery sequence below. First failure halts the chain and triggers the iteration loop. Successful drafts ship with `preflight-report.json` + `review.md` + `preview/*.png` in the draft folder.

## Canonical delivery sequence

This is the one authoritative order for `/blog write`, `/blog rewrite`,
translations and localizations. `blog-write`, `blog-rewrite`, the `blog`
orchestrator and `blog-write/references/delivery.md` carry short versions that
link here. If any of them disagrees with this section, this section wins.

Draft folder `D`, slug `S`. Helpers always run from the trusted absolute scripts
root set at the top of this file, never from a path relative to the current project. Run
capability discovery once before step 1:
`python3 "$BLOG_SCRIPT_DIR/blog_preflight.py" --draft "$D" --gate 1`.

1. **Draft.** Write `D/S.md` (frontmatter, answer-first). Draft-only markers
   `[INTERNAL-LINK: ...]`, `[IMAGE: ...]` and `[CHART: ...]` are allowed here and
   nowhere later. The `blog-writer` agent can only leave markers; it cannot call
   skills or helpers.
2. **Visuals.** The orchestrator resolves every marker. Hero:
   `python3 "$BLOG_SCRIPT_DIR/generate_hero.py" --topic "<title>" --tags "<tags>" --out "$D"`
   writes `D/hero.<ext>`. Charts: the `blog-chart` skill, embedded as inline SVG.
   Internal links: replaced with real links, or the marker removed. Images:
   replaced with local files in `D`, or removed. No marker may remain after this
   step. An optional `blog-seo` pass runs here, on the resolved `S.md`, and its
   fixes go into `S.md` before step 3. The optional hygiene helper also belongs
   here: run `blog_hygiene.py --md "$D/S.md" --apply` on the markdown only, never
   on rendered files.
3. **Render.** `python3 "$BLOG_SCRIPT_DIR/blog_render.py" --md "$D/S.md" --out-dir "$D"`
   produces `S.html` and `S.pdf`. The HTML carries
   `<meta name="blog-source-sha256" content="<sha256 hex of the exact S.md bytes>">`.
4. **Init nonce.** `NONCE=$(python3 "$BLOG_SCRIPT_DIR/blog_preflight.py" --init-review-nonce --draft "$D")`
   prints a nonce and stores verifier state outside `D`, including sha256 digests
   of `S.md`, `S.html`, `S.pdf` and the hero file at that moment.
5. **Review.** Spawn `blog-reviewer` with the draft path, the absolute reference
   roots and the nonce. The reviewer has no Write tool: it returns the report as
   text, and the **orchestrator saves that text verbatim to `D/review.md`** (no
   edits, no reformatting, no added or removed lines). The report contains
   `Nonce: <hex>`, five category scores, the overall score, the P0 list and
   `BLOCKING: true|false (reason)`.
6. **Gates.** `python3 "$BLOG_SCRIPT_DIR/blog_preflight.py" --draft "$D" --strict`
   (add `--repair-attempt` on every run inside the repair loop).
7. **Loop.** If a gate blocks, fix the cause, then repeat from step 2 or 3 as
   needed, and ALWAYS re-render, re-init the nonce and re-review after ANY change
   to `S.md`, `S.html`, `S.pdf` or the hero. Maximum 3 iterations, then stop and
   present the diagnostic. On a pass, deliver with the scorecard and
   `preview/*.png`.

Why the order matters: the reviewer judges the rendered artifacts, so it runs
after render (steps 3 to 5), and the nonce is issued after the files are final
(step 4) so the stored digests describe exactly what the reviewer saw. Editing
any of those files afterwards makes Gate 4 fail with "draft changed after the
review nonce was issued", which is the intended behavior and not a flaky test.
`review.md`, `preflight-report.json`, `capabilities.json` and `preview/` are
outputs and are not part of the digests.

Known limit: the nonce stops accidents and casual forgery. It does not stop a
process running as the same user that can read the verifier state file.

## Required frontmatter

The renderer reads these `S.md` frontmatter keys, and the gates check what they
produce. The markdown file stem is the artifact stem (`S.html`, `S.pdf`) unless
`slug` is set, so name the file in lowercase slug style.

| Key | Required | Consumed by |
|---|---|---|
| `title` | Yes | `<title>`, the H1, `og:title`, JSON-LD `headline` |
| `description` | Yes | meta description, `og:description`, JSON-LD `description` |
| `date` | Yes (`YYYY-MM-DD`) | JSON-LD `datePublished` (and `dateModified` when no `lastUpdated`), the byline |
| `lastUpdated` (alias `dateModified`, which wins if both are set) | Optional (ISO date or datetime, not earlier than `date`) | The renderer maps it to JSON-LD `dateModified`, `article:modified_time` and a visible "Updated" line under the byline; invalid or earlier than `date` is refused |
| `author` | Yes | byline, JSON-LD `author` (Gate 5 needs it) |
| `canonical` | Yes in practice | `<link rel="canonical">`, `og:url`, JSON-LD `mainEntityOfPage`, and the base that relative image URLs resolve against; Gate 5 reports its absence first |
| `slug` | Optional | Artifact stem, overriding the file stem. If you set it, name the markdown file `<slug>.md`: Gate 2 needs the `.md`, `.html` and `.pdf` to share one name |
| `site_name` | Optional | Footer and `og:site_name`; derived from the canonical host when absent |
| `lang` | Optional (default `en`) | `<html lang>`, JSON-LD `inLanguage` |
| `og_image_alt` | Recommended | `alt` of the hero image and `og:image:alt` (defaults to the title) |
| `tags` | Optional list | JSON-LD `keywords`, the kicker |
| `kicker` | Optional | Label above the title |

`canonical` is the article's final public URL: the site base URL plus the path.
The orchestrator fills it from the project's site URL (the `BRAND.md` site URL
read through the fenced helper, otherwise ask the user once and reuse the
answer), and never leaves it empty. The hero sits next to the article as
`hero.<ext>`, and the renderer builds `og:image` as `<canonical>/hero.<ext>`;
the gates compare that with the local hero file.

## Gate 1: Capability Discovery

Runs once at the start of `/blog write` or `/blog rewrite`. Enumerates the project's available capabilities and writes `<draft-folder>/capabilities.json`. Every later gate consumes this artifact rather than re-detecting.

### What gets enumerated

- **MCP servers loaded**: `nanobanana-mcp`, `dataforseo-mcp`, others. Detected via tool availability, not by reading `.mcp.json` (the file may declare servers that failed to start).
- **Env vars present**: `GOOGLE_AI_API_KEY`, `UNSPLASH_ACCESS_KEY`, `PEXELS_API_KEY`, `PIXABAY_API_KEY`. Key names only; values never read or logged.
- **Optional Python deps**: `patchright`, `weasyprint`, `google-genai`, `requests`. Probed via `importlib.util.find_spec()`.
- **Project-root context files**: `BRAND.md`, `VOICE.md`, `DISCOURSE.md`. Loaded only via the trusted installed `load_untrusted_root.py` helper.
- **Agents available**: `blog-reviewer` is mandatory; `blog-researcher`, `blog-writer`, `blog-seo`, `blog-translator` are optional.
- **Helper scripts present**: `scripts/lint_prose.py`, `scripts/analyze_blog.py`, the new `scripts/blog_preflight.py` itself.

### Failure modes

- **No hero path at all** (no valid local `hero.png`, `.jpg`, `.jpeg` or `.webp`, no Banana MCP, no Gemini key, no stock API key, and Openverse unreachable): BLOCK with explicit setup instructions.
- **Reviewer agent missing**: BLOCK. Cannot enforce Gate 4 without it.
- **Capability declared but unused**: WARN (informational, not blocking). Example: `dataforseo-mcp` is loaded but the post topic doesn't need keyword research.

## Gate 2: Format Completeness

Every delivered blog ships with four artifacts in `<draft-folder>/`:

- `<slug>.md`: canonical source of truth. Frontmatter + prose + figure references. The `.html` and `.pdf` are rendered from this; they cannot diverge by construction.
- `<slug>.html`: self-contained, valid HTML5, JSON-LD `BlogPosting` schema, Open Graph + Twitter Card meta, dark-mode-aware CSS via `prefers-color-scheme`, real `<img>` tag for hero (never a chart-as-hero). It carries `<meta name="blog-source-sha256">` with the sha256 of the exact `.md` bytes.
- `<slug>.pdf`: generated from rendered HTML via `patchright`'s `page.pdf()`, or `weasyprint` as fallback when Playwright is unavailable.
- `hero.(png|jpg|jpeg|webp)`: raster image of at least 1200×630 pixels. Either generated by an image-gen path or downloaded from a licensed stock source. Never hot-linked; always lives in the draft folder.

Implementation split: `scripts/blog_render.py` renders `.html` and `.pdf` from the existing `.md`; `scripts/generate_hero.py` emits `hero.<ext>` plus `hero-credit.txt`; `scripts/blog_preflight.py` Gate 2 verifies all four artifacts. Failure to produce any of the four artifacts blocks delivery.

Gate 2 also checks the artifacts for validity, statically and without a browser:

- No draft placeholders remain in `.md` or `.html`: `[INTERNAL-LINK`, `[IMAGE` and `[CHART` (any case) are violations. Resolve them in step 2 of the canonical sequence.
- Artifact and image filenames are lowercase slug style.
- The hero decodes as a real image whose format matches its extension and is at least 1200×630 pixels.
- The PDF starts with `%PDF` and has at least one page.
- The HTML `blog-source-sha256` meta equals the sha256 of the `.md`. A missing or different value is a violation; the fix is to re-run `blog_render.py`.
- The HTML body is unedited since render: the renderer wraps the body in `<!--bs-body:start-->` and `<!--bs-body:end-->` and stamps `blog-body-sha256`; Gate 2 recomputes it. A hand edit of the `.html`, missing markers or a missing meta is a violation; edit the `.md` and re-run `blog_render.py`.

Static markup checks (all reported by Gate 2, before the browser gate and the review; each message names the element and the fix):

- `<html lang>`, `<title>` and a non-empty meta description are present (a description outside 70 to 165 characters is a warning).
- Exactly one `<h1>`, and heading levels never skip downward (h2 straight to h4 is a violation).
- `og:title`, `og:description` and `og:image` are present, and no robots meta contains `noindex`.
- Every `<img>` has an `alt` attribute. An empty `alt` is allowed only with `role="presentation"` or `aria-hidden="true"`, otherwise it is a warning.
- No active content: no `<script>` except `type="application/ld+json"`, no inline `on*` handler attributes, no `javascript:` URLs, no `<iframe>`, `<object>`, `<embed>` or `<frame>`, and no `<script>` or `on*` inside inline SVG.

### Optional hygiene pass (non-blocking)

Before the render (step 2 of the canonical sequence) you may run `python3 "$BLOG_SCRIPT_DIR/blog_hygiene.py" --md "$D/<slug>.md" --apply` to auto-apply judgment-free fixes: insert a Table of Contents on posts over 2000 words (and report images missing alt text, which a human must fill in). Run it on the markdown only. Running it on rendered files, or on the `.md` after step 3, changes bytes the HTML source hash and the review nonce digests describe, and forces a re-render, re-init and re-review. It is optional, never blocks delivery, and does not replace any gate.

## Gate 3: Visual Verification

Renders the `.html` in headless `patchright` at three viewport widths and checks for visual defects. This is the "review before present" step.

### Viewport widths

- 375×812 (mobile, iPhone SE class)
- 768×1024 (tablet, iPad portrait)
- 1280×800 (desktop)

### Checks per viewport

1. **Full-page screenshot**: saved to `<draft-folder>/preview/` as `mobile-375.png`, `tablet-768.png` and `desktop-1280.png` for inspection. The dark-mode pass (check 3) adds `desktop-1280-dark.png`.
2. **SVG bounding box check**: for every `<svg>` and `<figure>` element, query `getBoundingClientRect()` on the element and on every descendant `text`, `path`, `rect`, and `image` child. Assert no descendant overflows its parent SVG `viewBox`. This catches the exact class of defect from the rankenstein.pro draft: labels positioned outside the chart area, dashed lines passing through annotation text.
3. **Dark-mode pass**: re-render with `prefers-color-scheme: dark` emulation. Assert the body `background-color` differs from light mode. This catches the `var()` in attribute regression where dark mode silently fails to swap colors because CSS custom properties were used in SVG XML attributes (which don't reliably resolve).
4. **Console errors**: capture browser console output during render. Assert zero errors.
5. **JSON-LD validation**: parse the `<script type="application/ld+json">` block. Assert valid JSON. Assert `@type: BlogPosting` with required fields (`headline`, `image`, `datePublished`, `author`).
6. **Hidden article text**: collect text inside `<article>` that is in the DOM but not rendered (`display:none`, `visibility:hidden`, opacity 0, font-size 0, off-screen, clipped to nothing). Skip `<template>`, `<noscript>`, `<script>`, `<style>`, closed `<details>` content and `aria-hidden` SVG. 100 or more characters, or 3 or more elements, blocks (hidden text is a spam-policy risk); less is a warning.

### Renderer requirement

Strict delivery requires `patchright` or an equivalent renderer. If no renderer is available, Gate 3 blocks and marks the draft non-shippable. Operators may use `--no-strict` for an intermediate local preview, but the output must not be presented as passed.

## Gate 4: Content Review (BLOCKING)

The `blog-reviewer` agent (`agents/blog-reviewer.md`) runs against the rendered `.html` (not the raw `.md`), after the nonce is issued (steps 4 and 5 of the canonical sequence). Reviewer output is **blocking**, not advisory.

Scoring rules live in `quality-scoring.md`: the threshold table, the draft-stage rule for items a draft cannot evidence, and the rule that the overall equals the sum of the five category scores. Gate 4 also fails when `S.md`, `S.html`, `S.pdf` or the hero changed after the nonce was issued; the message reads "draft changed after the review nonce was issued: <file>; re-render, re-init the nonce and re-review". State files written before digests existed keep the old behavior (no digest check, a warning).

### Blocking decision rules

- Overall score **< 90/100** → BLOCK
- **Any P0 issue** from `editorial-heuristics.md` → BLOCK (a draft can score 95 and still have one load-bearing fabricated stat; P0 is an absolute filter independent of the numeric score)
- A load-bearing claim without adequate source support is P0. P1 means urgent
  remediation but is not independently blocking after the score and P0 rules
  pass.
- Advisory style diagnostics never block and never infer authorship
- All clear → proceed to Gate 5

Translation and localization can materially change claims, examples, links,
metadata, schema, and rendered layout. Each final locale artifact set runs all
five gates with its own external review nonce after its last translation or
localization change. A locale that has not passed remains a draft and must not
be reported as complete or publication-ready.

The blocking decision is emitted as the last line of the reviewer scorecard, in the format:

```
BLOCKING: true (Overall 87/100 below threshold; P0 on heuristic 5)
BLOCKING: false (cleared all gates)
```

Machine-readable by `scripts/blog_preflight.py` so the orchestrator does not have to parse the human-readable scorecard.

The reviewer has no Write tool and returns its report as text. The orchestrator saves that text verbatim to `<draft-folder>/review.md` (step 5). Shown to the user on success ("here is why this passed") and on final failure ("here is why this is still blocked after 3 iterations").

Gate 4 may report sentence-length variation, configured phrase-list matches,
or vocabulary sampling for editorial review. These diagnostics do not affect
the numeric score and are never machine-enforced as evidence of AI authorship.

## Gate 5: Asset Existence + Link Integrity

- Every `<img src="...">` resolves. Local paths must stay under the draft root after `resolve()`, refuse symlinks, and use slug-sanitized filenames. Absolute URLs must use `http` or `https` only; reject `javascript:`, `data:`, `file:`, protocol-relative URLs, credentials in URLs, and invalid hosts.
- External URL checks must resolve DNS before connecting and reject loopback, private, link-local, multicast, reserved, unspecified, and cloud-metadata IP ranges. Do not follow redirects automatically; if redirects are allowed, validate every redirect target with the same checks. Use bounded timeouts (10 seconds in the helper), response-size caps, and no request bodies.
- Validate links with `HEAD` first, then fall back to `GET` with a small range request when servers block `HEAD`. Accept valid 2xx or 3xx responses. A per-project `external-links.allowed` file may allow only a final 403 or 405 status after URL syntax, DNS, connection target, and every redirect target have passed the same safety checks.
- `og:image` names the social-preview asset. For an unpublished draft, validate the matching local hero rather than requiring its future public URL to be live. Direct remote image fetches retain the same network safety checks.
- `external-links.allowed` is line-oriented. Each nonblank, non-comment line is one exact `http://` or `https://` URL. Lines beginning with `#` are comments. URL fragments are ignored for exact matching. Entries do not bypass URL, DNS, redirect, timeout, or response-size checks.
- Every `<a href="https://...">` resolves under the same policy. An exact allowed entry changes only the final 403 or 405 status decision.
- During content review, distinguish real project-file references from clearly labeled hypothetical examples. Gate 5 validates actual local link and image paths; it does not interpret every inline code token as a filename.
- `<link rel="canonical">` is set and well-formed. A missing canonical is reported as the cause before any downstream identity mismatch.
- The renderer's own generated footer link carries `data-bs-generated="1"`. Gate 5 validates its scheme but does not HEAD-fetch it, so a fully local article can pass offline. When other link checks fail with network errors, the message says the failure may be a network or DNS problem and how to tell the difference.
- JSON-LD `wordCount` matches actual `<article>` word count within ±5%. Catches the "I claimed 1,715 words but the body is 1,400" honesty defect.

## Hero Image Generation Ladder

Tried in order. First success wins. Skip steps for capabilities not available per Gate 1's `capabilities.json`.

1. **Banana MCP** (`nanobanana-mcp` loaded as a tool, not just declared in `.mcp.json`): call its `generate_image` tool with an optimized six-component prompt (Subject + Action + Context + Composition + Lighting + Style) targeting 1200×630.
2. **Direct Gemini API** (`GOOGLE_AI_API_KEY` present, MCP not loaded): call the `google-genai` SDK with the default image model and fallback order that `generate_hero.py --help` and the `blog-image` skill's Gemini model reference currently document; this contract does not pin a model ID. See `https://ai.google.dev/gemini-api/docs/image-generation`.
3. **Premium stock APIs** (`UNSPLASH_ACCESS_KEY`, `PEXELS_API_KEY`, or `PIXABAY_API_KEY` present): search via the official API using post title + top tags as query. Do not scrape or construct raw CDN URLs. Capture each source's license metadata and attribution requirements, download the asset locally, and write `hero-credit.txt`. Unsplash, Pexels, and Pixabay use their own licenses; do not treat them as CC sources.
4. **Openverse public API** (no key required): `GET https://api.openverse.org/v1/images/?q=<query>&aspect_ratio=wide&license=cc0,by,by-sa` (the licenses `generate_hero.py` sends, with `size=large` and `page_size=10`). Pick the top relevance match with complete attribution. Always download to `hero.<ext>` plus `hero-credit.txt` for CC attribution. CC BY and BY-SA images require visible attribution, and the renderer does not publish it: the orchestrator must add the credit line from `hero-credit.txt` to the article's Sources section or the hero caption in `S.md` (step 2) before the render. The same applies to any stock image whose license asks for credit.
5. **Block with clear error**: "Hero image required but no generation path available. Configure Banana MCP, set GOOGLE_AI_API_KEY, set UNSPLASH/PEXELS/PIXABAY key, or place a 1200×630 hero.png in the draft folder manually."

Implementation: `scripts/generate_hero.py`. Always writes `hero-credit.txt` next to `hero.<ext>` for attribution compliance, even when generation paths 1-2 (AI-generated, no attribution needed) are used. The file then contains "AI-generated; no attribution required."

## Iteration Loop

Step 7 of the canonical sequence drives the retry loop. The orchestrator
(`skills/blog/SKILL.md`) holds the counter, and `--repair-attempt` on
`blog_preflight.py` enforces the cap of 3. Sub-skills never loop themselves;
that would risk infinite loops if two sub-skills disagree.

1. **Capture diagnostic**: which gate failed, which specific check, screenshot if visual, scorecard if content.
2. **Fix, keyed to the failing gate:**
   - Gate 2 missing, invalid or placeholder artifact: fix the source `.md` (or resolve the marker), then re-enter at step 2 or 3.
   - Gate 3 visual fail: adjust the content or layout (for example shrink the SVG inner area, wrap long labels), then re-enter at step 3.
   - Gate 4 score below 90: re-dispatch `blog-writer` with the reviewer report as input and an instruction to fix the lowest-scoring category first.
   - Gate 4 P0 issue: re-dispatch with a targeted instruction for that specific P0.
   - Gate 4 "draft changed after the review nonce was issued": no content fix is needed; re-render, re-init the nonce and re-review.
   - Gate 5 404: re-dispatch with instruction to remove or replace the broken URL.
3. **Re-render, re-init the nonce and re-review after ANY change** to `S.md`, `S.html`, `S.pdf` or the hero, then run step 6 again. The review is bound to the exact files it saw; an old `review.md` never carries over to edited files.
4. **On pass**: present the draft with a one-line summary ("Delivered after N iteration(s)").
5. **On fail after 3 iterations**: STOP. Show the user the failure diagnostic for each remaining defect, the partial draft, the latest reviewer report, and an explicit "Manual fix required" message. Do not iterate further automatically.

## Bypass Mechanism

Strict mode is the default. Users can override only via an explicit operator-controlled `--no-strict` flag on `scripts/blog_preflight.py` or signed/trusted project config. Draft frontmatter is untrusted content and must never disable delivery gates. Any bypass logs loudly:

```
WARNING: Delivery contract bypassed. Failed gates: [Gate 3, Gate 5].
The draft is being presented anyway per --no-strict. Do not publish without manual review.
```

Bypass is intended for two cases: (1) the contract has a false positive the user has verified, (2) the user is iterating on a draft and wants to see intermediate output before the gates pass. It is not intended for shipping. A future CI workflow will reject merges where `preflight-report.json` shows `"blocked": true && "strict": false` (the bypassed-and-published case); that enforcement is not yet implemented.

## Community Footer

Public support links are optional. Share one only when the user asks for
support, contribution guidance, or relevant next steps. Do not append a
promotional footer to every deliverable, and never put support promotion inside
generated blog content, HTML, or markdown files.

```
Project discussions: https://github.com/AgriciDaniel/claude-blog/discussions
Public community: https://www.skool.com/ai-marketing-hub
```

For bugs or reproducible defects, prefer:
https://github.com/AgriciDaniel/claude-blog/issues.

## References

- `<blog_reference_root>/quality-scoring.md`: the 100-point rubric, the single threshold table and the draft-stage scoring rule used by Gate 4
- `<blog_reference_root>/editorial-heuristics.md`: the P0-P3 ordinal scoring used for the P0 filter in Gate 4
- `<blog_reference_root>/visual-media.md`: image and asset standards consumed by Gate 5
- `<blog_reference_root>/schema-stack.md`: JSON-LD structure validated by Gate 3 step 5
- `agents/blog-reviewer.md`: the reviewer agent that produces the Gate 4 scorecard
- `scripts/load_untrusted_root.py`: the v1.8.3 helper used for project-root file loading in Gate 1
- `scripts/lint_prose.py`: the v1.8.4 prose linter run as part of Gate 4's editorial-heuristics scoring
- `tests/test_blog_delivery_contract.py`: coherence test that asserts this contract and its implementation stay in sync

## How this contract maps to the v1.8.x lesson

The rankenstein.pro draft failure was a Category-3 defect: a contradiction between what the project's tooling could do (Banana MCP, blog-reviewer, /blog image, Playwright) and what the writer actually invoked (none of them). The v1.8.x lesson says: convert Category-3 into a gate or a test, not into more discipline. This contract is exactly that. Five gates fire automatically. The writer cannot forget to use the tools because the tools are wired into the gates themselves.

### Unambiguous Reviewer Fields

A passing scorecard contains exactly one Overall Score field, one matching
Nonce field and one final `BLOCKING: false (reason)` decision with a non-empty
reason. Include an affirmative `zero P0 issues found` line. Duplicate or
conflicting fields, negated clearance and separately unresolved P0 findings
block delivery. Existing affirmative no/zero P0 decision clauses remain valid.
Category lines use the fixed rubric maxima (30, 25, 15, 15, 15) and the overall
equals the sum of the five category scores; Gate 4 rejects a card whose numbers
disagree. See the draft-stage rule in `quality-scoring.md` for items a draft
cannot evidence.
