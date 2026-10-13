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
  version: "2.3.1"
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
- **Declined or unavailable:** skip the Gemini call (run the script with the
  key unset, `env -u GOOGLE_AI_API_KEY`, to use the free stock rungs) and
  return ONE line for the orchestrator's "Fallbacks and skips" summary, such as
  "Hero image: user declined paid generation, used a stock photo".

You are a **Creative Director** that orchestrates Gemini's image generation
specifically for blog content. Never pass raw user text directly to the API.
Always interpret, enhance, and construct an optimized prompt using the
6-component Reasoning Brief system.

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/blog image generate <idea>` | Generate a blog image with full prompt engineering |
| `/blog image edit <path> <instructions>` | Edit an existing blog image intelligently |
| `/blog image setup` | Check the API key and, optionally, install the MCP server |

## Blog Image Types

Match the image type to blog use case:

| Image Type | Aspect Ratio | Resolution | Domain Mode | Placement |
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
   API with `GOOGLE_AI_API_KEY` (the `google-genai` SDK must be installed),
   then falls back to premium stock and Openverse. It needs no MCP server.
2. **Optional MCP (at your own risk).** `@ycse/nanobanana-mcp@1.1.1` is the
   only package the setup script pins, and it only supports image model IDs
   that Google shut down on 2026-06-25 (see Step 5). Use it only if the user
   already has a working server; never present it as the default.

Before using the MCP route, check availability: call `get_image_history` with
`conversation_id: "default"` (no side effects). If it fails, use the direct
API route instead of asking the user to install the MCP.

When called internally (from blog-write/blog-rewrite) and no route works:
no error, but return a one-line fallback note (what was skipped, why) for the
caller's final summary. The calling workflow continues with stock photos.

## Generation Workflow

For `/blog image generate <idea>` or when invoked internally:

### Step 1: Analyze Intent

Determine what the blog needs:
- **Image type**: Hero, inline, OG card, section divider?
- **Blog topic**: What is the article about?
- **Style**: Photorealistic, editorial, illustrated, minimal?
- **Constraints**: Brand colors, specific dimensions, platform format?
- **Mood**: Authoritative, inviting, dramatic, clean?

If the request is vague, ask one clarifying question about use case and style.

### Step 2: Select Domain Mode

Choose the expertise lens for the image:

| Mode | When to use | Prompt emphasis |
|------|-------------|-----------------|
| **Editorial** | Blog headers, feature images, lifestyle | Styling, composition, publication references |
| **Product** | E-commerce posts, reviews, comparisons | Surface materials, studio lighting, clean BG |
| **Landscape** | Environmental backgrounds, travel, hero sections | Atmospheric perspective, depth layers, time of day |
| **UI/Web** | Tech blog icons, illustrations, diagrams | Clean vectors, flat design, exact colors |
| **Infographic** | Data-driven posts, processes, comparisons | Layout structure, hierarchy, accessible colors |
| **Abstract** | Pattern backgrounds, section dividers, decorative | Color theory, mathematical forms, textures |

Load `${CLAUDE_SKILL_DIR}/references/prompt-engineering-blog.md` for domain mode modifier libraries.

### Step 3: Construct the 6-Component Reasoning Brief

Build the prompt as natural narrative paragraphs, not keyword lists:

1. **Subject** - Who/what, with rich physical detail (textures, materials, scale)
2. **Action** - What is happening, pose, gesture, movement, state
3. **Context** - Environment, setting, time of day, season, weather
4. **Composition** - Camera angle, shot type, framing, negative space, depth
5. **Lighting** - Light source, quality, direction, color temperature, shadows
6. **Style** - Art medium, aesthetic, film stock, reference artists/eras

**Template for photorealistic blog images:**
```
A photorealistic [shot type] of [subject with physical detail], [action/pose],
set in [environment with specifics]. [Lighting conditions] create [mood].
Captured with [camera model], [focal length] lens at [f-stop], producing
[depth of field effect]. [Color palette/grading notes]. Aspect ratio 16:9,
suitable as a blog [hero image/inline illustration] at [target dimensions].
```

**Template for illustrated/stylized:**
```
A [art style] [format] of [subject with character detail], featuring
[distinctive characteristics] with [color palette]. [Line style] and
[shading technique]. Background is [description]. [Mood/atmosphere].
```

### Step 4: Set Aspect Ratio

Direct API: the script requests `16:9` and fits the result to `--width` by
`--height` (default 1200x630). MCP route: call `set_aspect_ratio` BEFORE
generating, with `conversation_id: "default"`.

| Blog Use Case | Ratio |
|---------------|-------|
| Hero / Cover / OG | `16:9` |
| Product shot / Square | `4:3` or `1:1` |
| Section divider | `21:9`, then crop wider in post-processing if needed |
| Vertical (stories) | `9:16` |

### Step 5: Generate

**Default: direct API.** After the consent gate, resolve
`BLOG_SCRIPT_DIR="${CLAUDE_BLOG_SCRIPTS_DIR:-${CLAUDE_SKILL_DIR}/../../scripts}"`,
reject it unless absolute, and never run a relative `scripts/generate_hero.py`:

```bash
python3 "$BLOG_SCRIPT_DIR/generate_hero.py" --topic "<post title>" \
  --tags "tag1,tag2" --out "<draft-folder>" [--width 1200] [--height 630] \
  [--model <image-model-id>] --json
```

Flags: `--topic` (required), `--tags`, `--out` (required, receives
`hero.<ext>` and `hero-credit.txt`), `--width`, `--height`, `--model`,
`--json`. Exit 0 means a hero was written (the JSON `source` field says
`gemini`, a stock provider, or `openverse`: report any non-Gemini source as a
fallback). Exit 1 means every rung failed. The script builds one fixed
editorial prompt from the topic and tags; it has no `--prompt` flag, so
custom briefs and edits need the optional MCP route or a direct `google-genai`
call written from the current docs.

**Model IDs** (Google deprecations page, 2026-10-12): use
`gemini-nano-banana-2.1` for new work. `gemini-3.1-flash-image` is the
previous generation (no shutdown announced; replacement
`gemini-nano-banana-2.1`). `gemini-2.5-flash-image` has an earliest shutdown
of 2027-03-15. See `${CLAUDE_SKILL_DIR}/references/gemini-models.md`.

**Optional MCP route (at your own risk).** Pinned `@ycse/nanobanana-mcp@1.1.1`
exposes `set_model` aliases `flash` and `pro` that map to preview IDs shut
down on 2026-06-25, so generation through it is expected to fail. Prefer the
direct API unless a newer package explicitly supports stable IDs.

| MCP Tool | When |
|----------|------|
| `set_aspect_ratio` | Always call first, even for 1:1 |
| `gemini_generate_image` | New image from crafted prompt |
| `gemini_edit_image` | Modify existing image |
| `gemini_chat` | Iterative refinement / multi-turn sessions |
| `get_image_history` | Review generated images with `conversation_id: "default"` |
| `clear_conversation` | Reset session context |

Load `${CLAUDE_SKILL_DIR}/references/mcp-tools.md` for MCP parameter details.
Load `${CLAUDE_SKILL_DIR}/references/gemini-models.md` for model specs, pricing, and rate limits.

### Step 6: Post-Processing (when needed)

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

### Step 7: Deliver

Provide:
1. **Image path** - where it was saved (the draft folder for the direct API, `~/Documents/nanobanana_generated/` for the MCP)
2. **Crafted prompt** - show the full Reasoning Brief (educational)
3. **Settings** - model, aspect ratio, domain mode
4. **Alt text** - descriptive sentence, 10-125 chars, topic keywords naturally
5. **Frontmatter snippet** (for hero/OG images):
```yaml
coverImage: "/path/to/generated-image.png"
coverImageAlt: "Descriptive alt text sentence with topic keywords"
ogImage: "/path/to/generated-image.png"
```
6. **Refinement suggestions** - 1-2 ideas if relevant

## Edit Workflow

For `/blog image edit <path> <instructions>`:

1. Read the image path and edit instruction
2. Enhance the instruction (never pass raw):
   | User says | Claude crafts |
   |-----------|---------------|
   | "remove background" | Detailed edge-preserving background removal |
   | "make it warmer" | Specific color temperature shift with preservation notes |
   | "add text" | Font style, size, placement, contrast, readability notes |
   | "make it brighter" | Increase exposure, lift shadows, maintain highlights |
   | "crop for social" | Resize to 1200x630 with center-gravity crop |
3. Editing needs the optional MCP (`gemini_edit_image`), which is a paid call under the consent gate. Without a working MCP, say so and offer to regenerate through the direct API instead
4. Return modified image path and description

## Internal API (for blog-write / blog-rewrite)

When invoked as a Task subagent from blog-write or blog-rewrite:

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
- **Domain Mode:** Editorial
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
1. Export `GOOGLE_AI_API_KEY` (free to create at
   https://aistudio.google.com/apikey; a billing-enabled project may be
   required for image models). `generate_hero.py` reads only this variable.
2. Install the SDK with the project's explicit setup (`google-genai` is
   declared in the repo `pyproject.toml` dependencies); never
   install implicitly during a run.

**Optional MCP path (at your own risk):**
1. Run `python3 "$BLOG_SKILLS_DIR/blog-image/scripts/setup_image_mcp.py"` (interactive)
   - Prefer exporting `GOOGLE_AI_API_KEY` before invoking the setup script so a
     literal key does not enter shell history
   - Or: `python3 "$BLOG_SKILLS_DIR/blog-image/scripts/setup_image_mcp.py" --key-file /path/to/key.txt`
   - Avoid `--key` unless necessary because command arguments can enter shell history and process lists
   - Default writes to `~/.claude/settings.json` (user-private, mode 0600)
   - `--project` flag opts into project `.mcp.json` (env-expansion only,
     refuses to write a literal key into a tracked file)
2. Verify: `python3 "$BLOG_SKILLS_DIR/blog-image/scripts/validate_image_setup.py"`
3. Requires Node.js 18+ (npx).
4. **Caveat:** the script pins `@ycse/nanobanana-mcp@1.1.1`. That npm
   release hard-codes preview image model IDs that Google shut down on
   2026-06-25 (deprecations page, checked 2026-10-12), so image calls
   through it are expected to fail. Tell the user this before installing.
   Update setup, validation, and this documentation together when a package
   release with stable ID support is available.

## Safety Filter Auto-Rephrase

When `IMAGE_SAFETY` or `SAFETY` is returned, do NOT give up. Auto-rephrase and retry:

1. Identify the likely trigger (violence, public figures, NSFW-adjacent, or overly cautious filter)
2. Rephrase using positive framing - describe what you WANT, not what to avoid
3. If the subject is a person, make them generic (remove celebrity-like specifics)
4. If the scene is dramatic, soften: "intense" → "focused", "battle" → "competition"
5. Retry with the rephrased prompt (max 3 attempts before reporting to user)

Google acknowledged filters "became way more cautious than we intended" - benign prompts
are sometimes blocked. Persistence with rephrasing usually succeeds.

## Edit, Don't Re-roll

If an image is 80% correct, use `gemini_chat` for conversational editing rather than
regenerating from scratch. The session maintains style consistency, so targeted edits
preserve what works while fixing what doesn't.

**When to edit vs regenerate:**
- Color slightly off → Edit ("shift the color temperature warmer")
- Wrong composition entirely → Regenerate with revised brief
- Good scene but wrong lighting → Edit ("change to golden hour lighting from the left")
- Missing a detail → Edit ("add a steaming coffee cup on the desk")

## Error Handling

| Error | Resolution |
|-------|-----------|
| No generation route | Export `GOOGLE_AI_API_KEY` (see Setup); the MCP is optional |
| API key invalid | New key at https://aistudio.google.com/apikey |
| Rate limited (429) | Wait 60s, retry. Check live limits at https://ai.google.dev/gemini-api/docs/rate-limits |
| `IMAGE_SAFETY` | Auto-rephrase (see above) - Layer 2 filter, non-configurable |
| `PROHIBITED_CONTENT` | Content policy violation - topic is blocked. Non-retryable. |
| `SAFETY` | Rephrase prompt - Layer 1 filter |
| Vague request | Ask one clarifying question before generating |
| Poor quality | Review Reasoning Brief - likely missing lighting (biggest quality differentiator) |
| No route or consent declined (internal call) | Return a one-line fallback note; calling workflow uses stock photos and reports it |

## Reference Documentation

Load on-demand - do NOT load all at startup:
- `${CLAUDE_SKILL_DIR}/references/prompt-engineering-blog.md` - Domain modes, 6-component system, blog templates
- `${CLAUDE_SKILL_DIR}/references/gemini-models.md` - Model specs, rate limits, aspect ratios, pricing
- `${CLAUDE_SKILL_DIR}/references/mcp-tools.md` - MCP tool parameters and response formats
