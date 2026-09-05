# Runtime surfaces and capability availability

claude-blog ships as one plugin that runs on three Claude surfaces. The
content skills behave identically everywhere. Only the skills that shell out to
Python, use a credential, or need a local MCP server vary — this file is the
single source of truth for which do what, and what to say when one is
unavailable.

## Check before you shell out

Before running any script-backed workflow, run the preflight and read the JSON:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/runtime_capabilities.py" --check <capability> --json
```

Capabilities: `analyze`, `google`, `image`, `audio`, `notebooklm`.

If `available` is `false`, do **not** run the script. Tell the user what is
missing in one sentence, quote the `degrades_to` guidance, and carry on with the
fallback. Never surface a raw traceback as the answer to a content request.

## Capability matrix

| Capability | Cowork (desktop) | Cowork (web / mobile) | Claude Code | Needs |
|---|---|---|---|---|
| Writing, rewriting, briefs, outlines, calendars, strategy, schema, charts, repurposing, GEO, clusters, translation, localization, personas, taxonomy, brand, style, decay, discourse | Yes | Yes | Yes | Nothing |
| `/blog analyze`, `/blog audit`, `/blog preflight` | Yes | Yes | Yes | Python 3.11+; `textstat` + `beautifulsoup4` optional |
| `/blog factcheck` | Yes | Yes | Yes | Web search |
| `/blog google` | Yes | Credentials via env only | Yes | Python deps + Google credential |
| `/blog audio` | Yes | Yes | Yes | Google AI API key |
| `/blog image` | Yes | **No** | Yes | Google AI API key + local MCP server |
| `/blog notebooklm` | Yes | **No** | Yes | Local browser + interactive Google sign-in |
| `/blog flow sync` | Yes | Yes | Yes | HTTPS egress to `api.github.com` |

## Why the two "No" cells

- **`/blog image`** runs the nanobanana MCP server as a local process. Plugins
  that bundle local MCP servers work in Claude Desktop and Claude Code; a Cowork
  session on web or mobile has no local process to attach to. The skill detects
  this and produces a full image brief and prompt instead, which the user can
  paste into any image tool.
- **`/blog notebooklm`** drives a real browser through an interactive Google
  login. That needs a local browser and a human at the keyboard.

## Filesystem rules

The plugin directory (`${CLAUDE_PLUGIN_ROOT}`) is **read-only** in Cowork and is
replaced wholesale on every plugin update. Follow these rules everywhere, not
just in Cowork — they are correct on all three surfaces:

- **Reading plugin content** — always through `${CLAUDE_PLUGIN_ROOT}/...`.
  Never a bare relative path: the working directory is the user's folder, not
  the plugin.
- **Writing the user's deliverables** (articles, reports, charts, audio) — into
  the current working directory, or wherever the user asked. Confirm the path
  before writing outside it.
- **Writing plugin state that must survive updates** (personas, caches) — into
  `${CLAUDE_PLUGIN_DATA}/`, falling back to `.claude-blog/` in the working
  directory when that variable is unset.

In Cowork, Claude can only reach folders the user has mounted into the session.
If a path the user names is not reachable, say so and ask them to add the folder
rather than writing somewhere else.

## Credentials

Credentials are never stored in the plugin directory and never committed.

| Surface | Where credentials live |
|---|---|
| Claude Code / Desktop | `~/.config/claude-seo/google-api.json`, mode 0600 |
| Cowork | Plugin options (secure storage) or environment variables |

A hosted Cowork session may not have a persistent home directory, so a config
file written in one session can be gone in the next. On that surface prefer the
plugin's own options, set once at enable time, over `/blog google setup`.
