# Optional MCP Route: Briefs, Edits and Setup

Load this file only for the optional MCP route (`@ycse/nanobanana-mcp`, at your
own risk) or when writing a custom `google-genai` call. The default route,
`generate_hero.py`, builds one fixed editorial prompt from the topic and tags,
has no `--prompt` flag and cannot edit images. Everything below is moved out of
`SKILL.md` so the default path stays short. The consent gate in `SKILL.md`
applies to every paid call here.

Creative Director stance for this route: never pass raw user text to the API.
Interpret it, enhance it, and build the prompt with the 6-component brief.

## Analyze, choose a mode, build the brief

### 1. Analyze Intent

Determine what the blog needs:
- **Image type**: Hero, inline, OG card, section divider?
- **Blog topic**: What is the article about?
- **Style**: Photorealistic, editorial, illustrated, minimal?
- **Constraints**: Brand colors, specific dimensions, platform format?
- **Mood**: Authoritative, inviting, dramatic, clean?

If the request is vague, ask one clarifying question about use case and style.

### 2. Select Domain Mode

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

### 3. Construct the 6-Component Reasoning Brief

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


## MCP tools

| MCP Tool | When |
|----------|------|
| `set_aspect_ratio` | Always call first, even for 1:1 |
| `gemini_generate_image` | New image from crafted prompt |
| `gemini_edit_image` | Modify existing image |
| `gemini_chat` | Iterative refinement / multi-turn sessions |
| `get_image_history` | Review generated images with `conversation_id: "default"` |
| `clear_conversation` | Reset session context |

Parameter details: `mcp-tools.md`. Model specs and pricing: `gemini-models.md`.

## Edit workflow

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
3. Editing is a paid call under the consent gate
4. Return modified image path and description

## Edit, don't re-roll

If an image is 80% correct, use `gemini_chat` for conversational editing rather than
regenerating from scratch. The session maintains style consistency, so targeted edits
preserve what works while fixing what doesn't.

**When to edit vs regenerate:**
- Color slightly off → Edit ("shift the color temperature warmer")
- Wrong composition entirely → Regenerate with revised brief
- Good scene but wrong lighting → Edit ("change to golden hour lighting from the left")
- Missing a detail → Edit ("add a steaming coffee cup on the desk")


## Safety filter rephrase

When `IMAGE_SAFETY` or `SAFETY` is returned, do NOT give up. Auto-rephrase and retry:

1. Identify the likely trigger (violence, public figures, NSFW-adjacent, or overly cautious filter)
2. Rephrase using positive framing - describe what you WANT, not what to avoid
3. If the subject is a person, make them generic (remove celebrity-like specifics)
4. If the scene is dramatic, soften: "intense" → "focused", "battle" → "competition"
5. Retry with the rephrased prompt (max 3 attempts before reporting to user)

Google acknowledged filters "became way more cautious than we intended" - benign prompts
are sometimes blocked. Persistence with rephrasing usually succeeds.


## MCP setup (at your own risk)

Resolve `BLOG_SKILLS_DIR="${CLAUDE_BLOG_SKILLS_DIR:-<resolved skill dir>/..}"`
and reject it unless absolute. Setup needs the user's explicit yes first.

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

