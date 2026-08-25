# MCP Tools Reference - @ycse/nanobanana-mcp

> Package: `@ycse/nanobanana-mcp`
> GitHub: https://github.com/YCSE/nanobanana-mcp

## Tools

### gemini_generate_image
Generate an image from a text prompt.

**Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | Yes | Text description of the image to generate |

**Returns:** Image data + file path (saved to `~/Documents/nanobanana_generated/`)

**Example usage in Claude Code:**
```
User: "Generate a sunset over mountains in watercolor style"
→ Claude calls gemini_generate_image with prompt
→ Returns image path and description
```

### gemini_edit_image
Edit an existing image with text instructions.

**Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `image_path` | string | Yes | Path to the image file to edit |
| `edit_prompt` | string | Yes | Edit instructions |

**Returns:** Modified image data + file path

**Example:**
```
User: "Remove the background from ~/Documents/photo.png"
→ Claude calls `gemini_edit_image({"image_path":"~/Documents/photo.png","edit_prompt":"..."})`
```

### gemini_chat
Multi-turn visual conversation maintaining session context.

**Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | Chat message (can reference previous images) |

**Returns:** Text response + optional image

**Key feature:** Session consistency - maintains style, characters, and context across turns. Great for iterative refinement.

### set_aspect_ratio
Configure the aspect ratio for subsequent image generations.

**Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `aspect_ratio` | string | Yes | Aspect ratio (e.g., "16:9", "1:1", "9:16") |
| `conversation_id` | string | Yes | Use `"default"` unless continuing another session |

**Example:** `set_aspect_ratio({"aspect_ratio":"16:9","conversation_id":"default"})`

**Pinned package supported ratios:** 1:1, 16:9, 9:16, 4:3, 3:4, 2:3, 3:2, 4:5, 5:4, 21:9

Extreme ratios such as 8:1, 4:1, 1:8, and 1:4 require a newer MCP package or direct API support. For section dividers, generate at 21:9 and crop during post-processing.

### set_model
Switch the active Gemini model.

**Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | string | Yes | MCP model alias |

**Available aliases in pinned package:**
- `flash`: maps to `gemini-3.1-flash-image-preview`
- `pro`: maps to `gemini-3-pro-image-preview`

Those preview IDs shut down on 2026-06-25. Stable Google API IDs such as
`gemini-3.1-flash-image`, `gemini-3.1-flash-lite-image`, and
`gemini-3-pro-image` are direct API IDs. Do not pass them to `set_model`
unless the installed MCP package explicitly supports them.

### get_image_history
Retrieve list of images generated in the current session.

**Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `conversation_id` | string | Yes | Use `"default"` unless reviewing another session |

**Returns:** Array of image entries with paths and prompts

### clear_conversation
Reset session context and conversation history.

**Parameters:** None

**Returns:** Confirmation of reset

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_AI_API_KEY` | Yes | API key from https://aistudio.google.com/apikey |
| `NANOBANANA_MODEL` | No | Pinned package accepts only `gemini-3.1-flash-image-preview` or `gemini-3-pro-image-preview`; both are shut down |

## Output Directory
All generated images are saved to: `~/Documents/nanobanana_generated/`

Images are named with timestamps for easy identification.

## Feature Availability via MCP

Some newer Gemini API features depend on the MCP package version of `@ycse/nanobanana-mcp`. Check the package version to confirm support:

| Feature | API Status | MCP Support |
|---------|-----------|-------------|
| `imageSize` (resolution control) | Available | Depends on package version |
| Thinking level (`thinkingConfig`) | Available | Depends on package version |
| Search grounding (`googleSearch`) | Available through direct API | Not exposed by the pinned package |
| Image-only output (`responseModalities: ["IMAGE"]`) | Available | Depends on package version |
| Multi-image input (up to 14 refs) | Available | Via `gemini_chat` with image paths |
| All 14 aspect ratios | Available through direct API | Pinned package exposes 10 ratios |

If a feature is not yet supported by the MCP package, you can still use it via direct API calls with `curl` or the Google AI SDK.
