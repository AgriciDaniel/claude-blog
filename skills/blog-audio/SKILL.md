---
name: blog-audio
description: >
  Paid Gemini TTS audio for a finished blog post: summary, full read-aloud,
  or two-speaker dialogue, with an MP3 and an HTML5 embed. Asks for explicit
  consent before the first paid call. Runs only on an explicit request:
  /blog audio, "generate audio for this blog post", "narrate this blog post",
  "audio version of this post", or "podcast version of this post". Not for
  general speech or dictation questions.
user-invocable: true
argument-hint: "[generate|voices|setup] [file-or-text] [--mode summary|full|dialogue] [--voice name]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "2.3.1"
---

# Blog Audio: Gemini TTS Narration for Blog Posts

Bundled paths below use host Markdown substitution of `${CLAUDE_SKILL_DIR}`;
it is not an exported shell variable. Resolve them before execution, quote
paths, and refuse nonabsolute overrides. Pass `blog_reference_root` resolved
from `${CLAUDE_SKILL_DIR}/../blog/references`, `blog_template_root` from
`${CLAUDE_SKILL_DIR}/../blog/templates`, and needed sibling roots to agents.
Read the main reference `orchestration-details.md` before loading project
context; pass only its helper-fenced output to downstream agents.

Generate professional audio narration of blog content using Google's Gemini TTS.
Three modes: summary (200-300 word spoken overview), full article read-aloud,
or two-speaker podcast dialogue. 30 prebuilt voices, over 130 languages on
Gemini 3.8 Flash TTS (over 100 on Flash-Lite; Google's speech-generation page,
checked 2026-10-12), HTML5 embed output.

## Cost and consent gate (mandatory, read first)

This skill spends the user's Google AI credit and writes audio files.

- **What it spends:** one paid Gemini TTS call per text chunk. Long text is
  split into chunks, so a full read-aloud costs several calls. The script's
  `--max-chunks` flag caps the chunks per run (default 12); never raise it
  without telling the user the new worst-case cost.
- **Cost basis:** audio output tokens at 25 tokens per second of audio.
  On 2026-10-12 https://ai.google.dev/gemini-api/docs/pricing listed
  `gemini-3.8-flash-tts` at $9.00 per 1M audio tokens (about $0.00225 per 10
  seconds) and `gemini-3.8-flash-lite-tts` at $6.00 (about $0.0015 per 10
  seconds), both through 2026-12-31 with higher listed rates from 2027-01-01.
  Run `--dry-run --json` first for the script's estimate.
- **What it writes:** the audio file under `audio/` (or `--output`) and, in
  setup only, the managed `.venv`.
- **Consent:** before the FIRST paid call in a session, state the mode, model,
  chunk count, and estimated cost, then wait for an explicit yes. The yes
  covers only that run. Writing a blog post does not consent to audio.
- **No uncapped spend:** never retry or loop on paid calls beyond the cap;
  one retry on a transient error, then report.
- **Skips:** if the user declines, the key is missing, or setup is absent,
  skip and return ONE line for the orchestrator's "Fallbacks and skips"
  summary, such as "Audio: no API key set, skipped".

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/blog audio generate <file>` | Generate audio narration of a blog post |
| `/blog audio voices` | Show available voices with characteristics |
| `/blog audio setup` | Check/configure API key for Gemini TTS |

## Prerequisites

- Python 3.11+; the explicit setup action owns the managed venv
- `GOOGLE_AI_API_KEY` or `GEMINI_API_KEY` environment variable (`GOOGLE_AI_API_KEY` is the one blog-image uses; the audio script accepts either)
- FFmpeg (for WAV-to-MP3 conversion; falls back to WAV if missing). Never install it implicitly; tell the user and let them install it

## Persistent runtime directory

`CLAUDE_BLOG_RUNTIME_DIR` optionally selects one trusted absolute persistent
root. This integration uses `<root>/blog-audio/.venv`; NotebookLM also
uses `<root>/blog-notebooklm/data` for its library, authentication and browser
state. Without this override, the existing skill-local defaults stay in use.
Google's shared credential config/token paths stay unchanged. No state is
copied or migrated automatically, and ordinary runs never perform setup.

Preserve an existing validated operator override. For a plugin without one,
explicitly pass the host-substituted `${CLAUDE_PLUGIN_DATA}/claude-blog-runtime`
path on both setup and every later runner call. This is Markdown substitution,
not an exported shell variable. Execute only once it is an absolute resolved
path. Single quotes keep an unresolved placeholder literal so validation
rejects it instead of expanding it to a different shell path:

```bash
CLAUDE_BLOG_RUNTIME_DIR='${CLAUDE_PLUGIN_DATA}/claude-blog-runtime' python3 "${CLAUDE_SKILL_DIR}/scripts/setup_environment.py" --check --json
CLAUDE_BLOG_RUNTIME_DIR='${CLAUDE_PLUGIN_DATA}/claude-blog-runtime' python3 "${CLAUDE_SKILL_DIR}/scripts/run.py" generate_audio.py --help
```

Only explicit setup without `--check` installs dependencies. Standalone users
keep the default unless they explicitly choose an absolute runtime root.
Relative, unresolved, or linked managed subdirectories fail closed. Changing
the root selects separate state; it never authorizes a migration or cleanup of
the old root. Plugin persistent data follows the host's uninstall retention
rules; preserve it explicitly when uninstalling if it is still needed.

## Use the Installed run.py Wrapper

```bash
BLOG_SKILLS_DIR="${CLAUDE_BLOG_SKILLS_DIR:-${CLAUDE_SKILL_DIR}/..}"
case "$BLOG_SKILLS_DIR" in /*) ;; *) echo "ERROR: skills dir must be absolute" >&2; exit 1 ;; esac
AUDIO_RUN="$BLOG_SKILLS_DIR/blog-audio/scripts/run.py"
python3 "$AUDIO_RUN" generate_audio.py --text "..." --voice Charon --model flash38 --json
```

Ordinary generate and voices commands perform a nonmutating capability check.
If the managed environment is absent, return a setup-required result. Only
`/blog audio setup` may create `.venv` or install dependencies. Never resolve
the wrapper from the current project's `scripts/` directory.

## API Key Check (Gate Pattern)

Before generating audio, check for the API key (the script reads
`GOOGLE_AI_API_KEY` first, then `GEMINI_API_KEY`):

```bash
if [ -n "${GOOGLE_AI_API_KEY:-}" ] || [ -n "${GEMINI_API_KEY:-}" ]; then echo "API key is set"; else echo "API key is not set"; fi
```

- If either is set: continue to the consent gate, then generate
- If neither is set: guide the user:
  "Audio generation requires a Google AI API key. Get one at https://aistudio.google.com/apikey
   Then export it in the shell: `export GOOGLE_AI_API_KEY=your-key` (or `GEMINI_API_KEY`).
   This can be the same key used by `/blog image`."
- **When called internally** (from blog-write): return a one-line skip note (what, why) if
  the key is missing, for the caller's final summary. Never block the writing workflow.

## Setup

For `/blog audio setup`:

1. Check that `GOOGLE_AI_API_KEY` or `GEMINI_API_KEY` is set in the environment
2. If blog-image uses project `.mcp.json`, confirm the referenced env var is exported
3. If not, guide user to https://aistudio.google.com/apikey
4. With the user's yes, create or refresh the managed environment. This is the
   only step that installs dependencies:
   `python3 "$BLOG_SKILLS_DIR/blog-audio/scripts/setup_environment.py"`
   (add `--check --json` to inspect without installing)
5. Verify with a dry run (no API call):
   `python3 "$AUDIO_RUN" generate_audio.py --text "Test" --dry-run --json`

## Voice Selection

For `/blog audio voices`:

Load `${CLAUDE_SKILL_DIR}/references/voices.md` and present the voice catalog to the user.

Ask the user which voice they prefer, or recommend based on content type:
- **Article narration**: Charon (Informative) or Sadaltager (Knowledgeable)
- **Tutorial/how-to**: Achird (Friendly) or Sulafat (Warm)
- **News/analysis**: Rasalgethi (Informative) or Schedar (Even)
- **Lifestyle/wellness**: Aoede (Breezy) or Vindemiatrix (Gentle)
- **Dialogue host**: Puck (Upbeat) or Laomedeia (Upbeat)
- **Dialogue expert**: Kore (Firm) or Charon (Informative)

## Generation Workflow

For `/blog audio generate <file>`:

### Step 1: Read the Blog Post

Read the file and extract:
- Title (from H1 or frontmatter)
- Full content (markdown body)
- Approximate word count

### Step 2: Choose Mode

Ask the user (or auto-select if they specified `--mode`):

| Mode | When to use | Output |
|------|-------------|--------|
| **Summary** | Quick audio overview (1-2 min) | 200-300 word spoken summary |
| **Full** | Complete read-aloud (5-15 min) | Full article as natural speech |
| **Dialogue** | Podcast-style (3-8 min) | Two-person conversation about the article |

### Step 3: Prepare Text

Claude prepares the text; the script does TTS only.

**Summary mode:**
Write a 200-300 word spoken summary of the article. Rules:
- Write as natural speech, not written text
- Open with the article's key finding or answer
- Cover 3-5 main takeaways
- Close with actionable advice
- No markdown, no "In this article...", no meta-commentary
- Use conversational transitions ("Here's what matters...", "The key finding is...")

**Full mode:**
Strip the markdown content to clean spoken text:
- Headings become natural transitions ("Next, let's look at...")
- Links become plain text (remove URLs, keep anchor text)
- Images and charts: omit or briefly describe ("As the data shows...")
- Code blocks: describe verbally ("The code uses a for-loop to...")
- Lists: convert to natural sentences
- Remove frontmatter, schema markup, HTML tags
- Add brief intro: "This is [title], published on [date]."

**Dialogue mode:**
Write a 2-person conversation script about the article:
- Speaker1 = Host (curious, asks good questions)
- Speaker2 = Expert (knowledgeable, gives clear answers)
- Format each line as: `Speaker1: What's the key takeaway here?`
- Cover the article's main points conversationally
- 15-25 exchanges (produces ~3-8 minutes)
- Natural, not stilted ("That's a great point" over "Indeed, as the research indicates")

### Step 4: Select Voice

If the user chose a voice, use it. Otherwise, recommend based on mode:
- Summary/Full: default to Charon (Informative)
- Dialogue: default to Puck (Host) + Kore (Expert)

### Step 5: Generate Audio

Write the prepared text to a file under the working directory, then call:

```bash
# Single voice (summary or full mode)
python3 "$AUDIO_RUN" generate_audio.py \
  --text-file blog_audio_prepared.txt \
  --voice Charon \
  --model flash38 \
  --output audio/post-slug.mp3 \
  --json

# Two voices (dialogue mode)
python3 "$AUDIO_RUN" generate_audio.py \
  --text-file blog_audio_dialogue.txt \
  --voice Puck \
  --voice2 Kore \
  --model flash38 \
  --output audio/post-slug-dialogue.mp3 \
  --json
```

**Model selection (use the explicit 3.8 IDs):**
- `flash38`: `gemini-3.8-flash-tts`, the stable general-purpose model and the
  one used in the examples above. Over 130 languages.
- `flash-lite38`: `gemini-3.8-flash-lite-tts`, the cheaper stable model. Over
  100 languages; a few (for example Finnish and Thai) are Flash-only.
- Legacy aliases `flash`, `flash31`, `pro`, `legacy-flash25`, `legacy-pro25`
  map to `gemini-3.1-flash-tts-preview`, `gemini-2.5-pro-preview-tts`, and
  `gemini-2.5-flash-preview-tts`. Google's deprecations page (checked
  2026-10-12) lists their earliest shutdown as 2026-11-17, so do not use them
  for new work. Confirm the resolved model ID in the `--dry-run --json` output
  before spending.

The 3.8 aliases have offline SDK schema and WAV parsing checks; authenticated
availability and voice quality still require provider testing. For 3.8, pass a
verbatim transcript, not embedded narration directions. Dialogue must use
explicit `Speaker1:` and `Speaker2:` lines; the helper does not infer
speakers. Cost estimates use the reviewed 2026 rates through December 31 and
the published 2027 rates from January 1. They remain estimates, not a billing
quote.

### Step 6: Deliver

Present the result to the user:
1. **File path**: where the audio was saved
2. **Duration**: human-readable (e.g., "3:42")
3. **Embed code**: ready-to-paste HTML5 audio tag
4. **Cost**: estimated API cost
5. **Placement suggestion**: where to insert the embed in the blog post

## Embedding Guide

### Standard HTML (Hugo, Jekyll, static sites)
```html
<audio controls preload="metadata">
  <source src="audio/post-slug.mp3" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>
```

### MDX (Next.js, Gatsby)
```jsx
<audio controls preload="metadata">
  <source src="/audio/post-slug.mp3" type="audio/mpeg" />
</audio>
```

### WordPress
```
[audio src="audio/post-slug.mp3"]
```

### Placement
Insert the audio player after the introduction (below the first H2) or at the
very top of the article with a label: "Listen to this article" or "Audio version".

## Internal API (for blog-write)

When invoked internally from blog-write:

**Input:**
- `text`: Prepared text (already cleaned by Claude)
- `voice`: Voice name (default: Charon)
- `voice2`: Second voice for dialogue (optional)
- `model`: `flash38` (default for new work) or `flash-lite38`; legacy aliases (`flash`, `flash31`, `pro`, `legacy-*`) shut down 2026-11-17 at the earliest
- `output_path`: Where to save the file

**Output:**
```markdown
### Audio Narration
- **Path:** /path/to/audio/post-slug.mp3
- **Duration:** 3:42
- **Voice:** Charon
- **Embed:** `<audio controls preload="metadata"><source src="audio/post-slug.mp3" type="audio/mpeg"></audio>`
```

**Graceful fallback:** If neither `GOOGLE_AI_API_KEY` nor `GEMINI_API_KEY` is
set, or the user declines the cost gate, return immediately with no error and
a one-line skip note for the caller's final summary. The writing workflow continues without audio. Never block
blog-write because audio generation is unavailable.

## Error Handling

| Error | Resolution |
|-------|-----------|
| API key not set (`GOOGLE_AI_API_KEY` or `GEMINI_API_KEY`) | Get key at https://aistudio.google.com/apikey |
| FFmpeg not found | Falls back to WAV output. Tell the user; do not install it for them. |
| Rate limited | Wait and retry. Check limits at https://aistudio.google.com/rate-limit |
| Text too long (>8,192 input tokens) | Split into sections around 7,800 tokens; the script chunks and stitches prepared text, up to `--max-chunks` (default 12) per run. Over the cap, stop and ask the user before raising it |
| Unknown voice name | Run `/blog audio voices` to see valid options |
| API error | Check key validity and model availability |
| API key missing (internal call) | Return a one-line skip note: writing workflow continues and reports it |

## Reference Documentation

Load on-demand: do NOT load all at startup:
- `${CLAUDE_SKILL_DIR}/references/voices.md`: Full 30-voice catalog, recommendations by content type, dialogue pairings
