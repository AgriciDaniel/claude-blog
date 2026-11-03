---
name: blog-image
description: >
  Paid Gemini image generation for blog heroes, inline illustrations, and OG
  cards (direct API by default, optional MCP for edits). Asks for explicit
  consent before the first paid call. Runs only on an explicit request:
  /blog image, "generate a blog hero image", "blog illustration", "edit this
  blog image", "OG image", or when blog-write or blog-rewrite needs a hero.
  Not for charts (blog-chart) or stock-photo search.
user-invocable: true
argument-hint: "[generate|edit|setup] [description-or-path]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "2.3.2"
  optional-mcp-package: "@ycse/nanobanana-mcp"
---

# Blog Image - AI Image Generation for Blog Content

Bundled paths below use host Markdown substitution of `${CLAUDE_SKILL_DIR}`;
it is not an exported shell variable. Resolve them before execution, quote
paths, and refuse nonabsolute overrides. Pass `blog_reference_root` resolved
from `${CLAUDE_SKILL_DIR}/../blog/references`, `blog_template_root` from
`${CLAUDE_SKILL_DIR}/../blog/templates`, and needed sibling roots to agents.
Read the main reference `orchestration-details.md` before loading project
context; pass only its helper-fenced output to downstream agents.

## Cost and consent gate (mandatory, read first)

This skill spends the user's Google AI credit and writes image files.

- **What it spends:** one paid Gemini image call per generated or edited
  image. `generate_hero.py` can try up to four model IDs in turn when the
  first fails, so budget for that worst case. The stock-photo and Openverse
  rungs are free but may need their own keys.
- **Cost basis:** per-image prices at
  https://ai.google.dev/gemini-api/docs/pricing. On 2026-10-12 that page listed
  `gemini-nano-banana-2.1` at $0.0336 (1K), $0.0504 (2K), $0.113 (4K) and
  `gemini-3.1-flash-image` at $0.067 (1K). Re-read it before quoting a number.
- **What it writes:** `hero.<ext>` and `hero-credit.txt` in the draft folder
  (direct API), `~/Documents/nanobanana_generated/` (optional MCP), and
  `~/.claude/settings.json` (setup only).
- **Consent:** before the FIRST paid call or file write in a session, tell
  the user the model, size, image count, and estimated cost (count times price)
  and wait for an explicit yes. The yes covers only that count. Asking for a
  blog post does not by itself consent to a paid image call.
- **No uncapped spend:** never loop on paid calls. Safety rephrases stop at 3
  attempts per image. Bulk work (for example a cluster) needs a stated total
  count and a cap, confirmed once before the first call.
- **Declined or unavailable:** skip the Gemini call (run the script without
  `--allow-paid`, its default, so a key is ignored and it uses the free rungs:
  existing hero, then stock keys, then Openverse) and
  return ONE line for the orchestrator's "Fallbacks and skips" summary, such as
  "Hero image: user declined paid generation, used a stock photo".

The default route builds one fixed editorial prompt from the topic and tags, so
it needs no brief from you. Custom prompt briefs, domain modes and image edits
exist only on the optional MCP route, documented in
`${CLAUDE_SKILL_DIR}/references/mcp-route.md` (load it only for that route).

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/blog image generate <idea>` | Generate a hero-style blog image (default route), or a custom brief via the optional MCP route |
| `/blog image edit <path> <instructions>` | Edit an existing blog image (optional MCP route only) |
| `/blog image setup` | Check the API key and, optionally, install the MCP server |

## Blog Image Types

Match the image type to blog use case:

| Image Type | Aspect Ratio | Resolution | Domain Mode (MCP route) | Placement |
|------------|-------------|-----------|-------------|-----------|
| Hero/Cover | `16:9` | 2K or 4K | Editorial / Landscape | Frontmatter `coverImage` |
| OG/Social Card | `16:9` | 1K | Editorial / Infographic | Frontmatter `ogImage` |
| Inline Illustration | `16:9` or `4:3` | 1K | Varies by topic | After H2, before body |
| Inline Product Shot | `4:3` or `1:1` | 1K | Product | Within product sections |
| Section Divider | `21:9` then crop | 1K | Abstract / Landscape | Between major sections |

**Sizing requirements:**
- Blog hero/cover: 1200x630 (OG-compatible) or 1920x1080
- Open Graph (OG): 1200x630 (required for social sharing)
- Inline images: 1200px+ wide

## Generation Routes

1. **Direct API (default).** The repo's `generate_hero.py` calls the Gemini
   API only when run with `--allow-paid` (after the consent gate) and
   `GOOGLE_AI_API_KEY` or `GEMINI_API_KEY` is set (the `google-genai` SDK
   must be installed), then falls back to premium stock and Openverse. It needs
   no MCP server. `NANOBANANA_MODEL` sets its default model ID.
2. **Optional MCP (at your own risk).** `@ycse/nanobanana-mcp@1.1.1` is the
   only package the setup script pins, and it only supports image model IDs
   that Google shut down on 2026-06-25 (see Step 2). Use it only if the user
   already has a working server; never present it as the default.

Before using the MCP route, check availability: call `get_image_history` with
`conversation_id: "default"` (no side effects). If it fails, use the direct
API route instead of asking the user to install the MCP.

When called internally (from blog-write/blog-rewrite) and no route works:
no error, but return a one-line fallback note (what was skipped, why) for the
caller's final summary. The calling workflow continues with stock photos.

## Generation Workflow

For `/blog image generate <idea>` or when invoked internally:

### Step 1: Aspect Ratio

Direct API: the script requests `16:9` and fits the result to `--width` by
`--height` (default 1200x630). MCP route: call `set_aspect_ratio` BEFORE
generating, with `conversation_id: "default"`.

| Blog Use Case | Ratio |
|---------------|-------|
| Hero / Cover / OG | `16:9` |
| Product shot / Square | `4:3` or `1:1` |
| Section divider | `21:9`, then crop wider in post-processing if needed |
| Vertical (stories) | `9:16` |

### Step 2: Generate

**Default: direct API.** After the consent gate, resolve
`BLOG_SCRIPT_DIR="${CLAUDE_BLOG_SCRIPTS_DIR:-${CLAUDE_SKILL_DIR}/../../scripts}"`,
reject it unless absolute, and never run a relative `scripts/generate_hero.py`.
Pass the title and tags as single-quoted arguments (shell argument rule in
`${CLAUDE_SKILL_DIR}/../blog/SKILL.md`):

```bash
python3 "$BLOG_SCRIPT_DIR/generate_hero.py" --topic '<post title>' \
  --tags 'tag1,tag2' --out "<draft-folder>" [--width 1200] [--height 630] \
  [--model <image-model-id>] [--replace] --allow-paid --json
```

Flags: `--topic` (required), `--tags`, `--out` (required, receives
`hero.<ext>` and `hero-credit.txt`), `--width`, `--height`, `--model`,
`--replace`, `--allow-paid`, `--json`. `--allow-paid` enables the paid Gemini
rung; pass it only after the consent gate approved this call, and omit it
otherwise (a key is then ignored and only the free rungs run). A valid
image hero already in `--out` is kept and nothing is generated (JSON `source`
is `existing`) unless you pass `--replace`, which the user must have asked for
and which swaps the hero and `hero-credit.txt` together. An invalid existing
`hero.*` is not kept, and a symlinked `hero.*` makes the script stop. Exit 0 means a hero is in place (the JSON `source`
field says `existing`, `gemini`, a stock provider, or `openverse`: report any
stock or Openverse source as a fallback). Exit 1 means every rung failed.

**What the default route supports.** It generates a hero-style image (one
fixed editorial prompt built from the topic and tags), at the size you pass,
then falls back to stock and Openverse. It has no `--prompt` flag, no inline
illustrations from a custom brief, and no editing. For custom briefs, domain
modes, edits or iterative refinement, use the optional MCP route
(`references/mcp-route.md`) or a direct `google-genai` call written from the
current docs.

**Model IDs** (Google deprecations page, 2026-10-12): use
`gemini-nano-banana-2.1` for new work. `gemini-3.1-flash-image` is the
previous generation (no shutdown announced; replacement
`gemini-nano-banana-2.1`). `gemini-2.5-flash-image` has an earliest shutdown
of 2027-03-15. See `${CLAUDE_SKILL_DIR}/references/gemini-models.md`.

**Optional MCP route (at your own risk).** Pinned `@ycse/nanobanana-mcp@1.1.1`
exposes `set_model` aliases `flash` and `pro` that map to preview IDs shut
down on 2026-06-25, so generation through it is expected to fail. Prefer the
direct API unless a newer package explicitly supports stable IDs. The tool
table, brief composition and parameters are in `references/mcp-route.md` and
`references/mcp-tools.md`.

Load `${CLAUDE_SKILL_DIR}/references/gemini-models.md` for model specs, pricing, and rate limits.

### Step 3: Post-Processing (when needed)

After generation, resize/convert for blog use:

```bash
# Resize to blog hero dimensions (1200x630)
magick input.png -resize 1200x630^ -gravity center -extent 1200x630 hero.png

# Convert to WebP for web optimization
magick input.png -quality 85 output.webp

# Convert to AVIF when target browsers support it
magick input.png -quality 80 output.avif

# Crop to exact OG dimensions
magick input.png -resize 1200x630^ -gravity center -extent 1200x630 og-image.png
```

Check if `magick` (ImageMagick 7) is available. Fall back to `convert` if not.

### Step 4: Deliver

Provide:
1. **Image path** - where it was saved (the draft folder for the direct API, `~/Documents/nanobanana_generated/` for the MCP)
2. **Prompt** - on the MCP route, show the full brief; on the default route say it used the script's fixed editorial prompt
3. **Settings** - model, aspect ratio
4. **Alt text** - descriptive sentence, 10-125 chars, topic keywords naturally
5. **Frontmatter snippet** (for hero/OG images):
```yaml
coverImage: "/path/to/generated-image.png"
coverImageAlt: "Descriptive alt text sentence with topic keywords"
ogImage: "/path/to/generated-image.png"
```
6. **Refinement suggestions** - 1-2 ideas if relevant

## Edit Workflow

`/blog image edit <path> <instructions>` needs the optional MCP route
(`gemini_edit_image`, a paid call under the consent gate). The edit recipes are
in `${CLAUDE_SKILL_DIR}/references/mcp-route.md`. Without a working MCP, say so
and offer to regenerate through the direct API instead.

## Internal API (for blog-write / blog-rewrite)

When the orchestrator invokes this skill for blog-write or blog-rewrite (the orchestrator runs this skill itself; the suite's agents have no Skill or Bash tool):

**Input** (provided by calling skill):
- `image_type`: hero, inline, og, divider
- `topic`: blog post topic/title
- `section_context`: (optional) heading or section the image supports
- `style_preference`: (optional) photorealistic, illustrated, editorial
- `count`: (optional) number of images needed (default: 1)

**Output** (returned to calling skill):
```markdown
### Generated Image
- **Path:** <draft-folder>/hero.png
- **Alt Text:** Descriptive sentence about the image
- **Type:** hero / inline / og
- **Domain Mode:** Editorial (MCP route only)
- **Aspect Ratio:** 16:9
- **Suggested Frontmatter:**
  coverImage: "/path/to/image.png"
  coverImageAlt: "Alt text here"
```

**Graceful fallback**: If no generation route works or the user declines the
cost gate, return immediately with no error and a one-line fallback note
(what, why) for the caller's final summary. The calling workflow continues
with stock photos. The delivery contract still requires a hero file, so the
orchestrator must supply one (stock or manual) before rendering. Do not call
this skill a second time for the same post's hero: blog-write already
requests it once.

## Alt Text Generation

For every generated image, create alt text following blog standards:
- Full descriptive sentence (not keyword list)
- 10-125 characters
- Include topic keywords naturally
- Describe what the image shows AND its relevance to the content
- For charts/infographics: include the key data point

Good: `Marketing team analyzing AI search traffic data on a dashboard showing citation metrics`
Bad: `SEO AI marketing blog optimization image`

## Setup

For `/blog image setup`:

Resolve `BLOG_SKILLS_DIR="${CLAUDE_BLOG_SKILLS_DIR:-${CLAUDE_SKILL_DIR}/..}"`
and reject it unless absolute. Setup is the only action allowed to change
image capability configuration, and it needs the user's explicit yes first.

**Default path (no MCP):** the direct API only needs a key and the SDK.
1. Export `GOOGLE_AI_API_KEY` or `GEMINI_API_KEY` (free to create at
   https://aistudio.google.com/apikey; a billing-enabled project may be
   required for image models). `generate_hero.py` reads `GOOGLE_AI_API_KEY`
   first, then `GEMINI_API_KEY`, and uses the key only with `--allow-paid`;
   `NANOBANANA_MODEL` sets its default model ID.
2. Install the SDK with the project's explicit setup (`google-genai` is
   declared in the repo `pyproject.toml` dependencies); never
   install implicitly during a run.

**Optional MCP path (at your own risk):** setup steps, the pinned package
caveat and the validation script are in
`${CLAUDE_SKILL_DIR}/references/mcp-route.md`. Tell the user the caveat (the
pinned package targets shut-down model IDs) before installing.

## Safety Filter

If `IMAGE_SAFETY` or `SAFETY` comes back, the default route simply falls to the
next rung. Rephrasing a custom prompt (positive framing, generic people, softer
wording; at most 3 attempts per image) applies only to the MCP route, see
`references/mcp-route.md`.

## Error Handling

| Error | Resolution |
|-------|-----------|
| No generation route | Export `GOOGLE_AI_API_KEY` or `GEMINI_API_KEY` (see Setup); the MCP is optional |
| API key invalid | New key at https://aistudio.google.com/apikey |
| Rate limited (429) | Wait 60s, retry. Check live limits at https://ai.google.dev/gemini-api/docs/rate-limits |
| `IMAGE_SAFETY` | Layer 2 filter, non-configurable; rephrase on the MCP route only (see Safety Filter) |
| `PROHIBITED_CONTENT` | Content policy violation - topic is blocked. Non-retryable. |
| `SAFETY` | Layer 1 filter; rephrase on the MCP route only |
| Vague request | Ask one clarifying question before generating |
| Poor quality | On the MCP route, review the brief (lighting is the biggest differentiator); on the default route, try another `--model` or an MCP brief |
| No route or consent declined (internal call) | Return a one-line fallback note; calling workflow uses stock photos and reports it |

## Reference Documentation

Load on-demand - do NOT load all at startup:
- `${CLAUDE_SKILL_DIR}/references/mcp-route.md` - Optional MCP route: brief composition, domain modes, edit flows, tool table, MCP setup
- `${CLAUDE_SKILL_DIR}/references/prompt-engineering-blog.md` - Domain modes, 6-component system, blog templates
- `${CLAUDE_SKILL_DIR}/references/gemini-models.md` - Model specs, rate limits, aspect ratios, pricing
- `${CLAUDE_SKILL_DIR}/references/mcp-tools.md` - MCP tool parameters and response formats
