# claude-blog in Claude Cowork

claude-blog is one plugin that runs on Claude Cowork, Claude Code, and Claude
Desktop. There is no separate Cowork build: the same 28 skills, 5 agents, 12
templates, and 15 references load on every surface. This page covers what is
different about Cowork specifically.

## Install

**From a marketplace** - *Plugins > Add marketplace*, enter
`AgriciDaniel/claude-blog`, open **claude-blog**, choose **Install**.

**From a file** - build the artifact from a checkout and upload it:

```bash
python3 scripts/package_plugin.py
# -> dist/claude-blog-<version>.plugin  (+ .sha256 printed to stdout)
```

Then *Plugins > Add plugin > Upload*. Use this route when your organization
restricts third-party marketplaces, when you need to pin an exact reviewed
build, or if marketplace-installed skills fail to load - a
[known Cowork issue](https://github.com/anthropics/claude-code/issues/39400)
where skill metadata registers but the files are not mounted. Uploading the same
plugin as a file is the documented workaround.

## Configure (optional)

The plugin exposes two options at install time. Both are optional and both are
off by default.

| Option | Enables | Default |
|---|---|---|
| **Google AI API key** | `/blog image`, `/blog audio` | blank - features off |
| **Gemini image model** | Model used by `/blog image` | `gemini-3.1-flash-image-preview` |

While the key is blank, nothing is downloaded and no MCP server is started. See
[SECURITY-REVIEW.md](SECURITY-REVIEW.md) for how that is enforced.

Everything else - writing, rewriting, briefs, outlines, calendars, strategy,
SEO checks, schema, charts, repurposing, GEO audits, clusters, translation,
localization, fact-checking, personas, taxonomy - needs no configuration.

## What works where

| Capability | Cowork desktop | Cowork web / mobile | Claude Code | Needs |
|---|---|---|---|---|
| Writing, rewriting, briefs, outlines, calendars, strategy, schema, charts, repurposing, GEO, clusters, translation, localization, personas, taxonomy, brand, style, decay, discourse | Yes | Yes | Yes | Nothing |
| `/blog analyze`, `/blog audit`, `/blog preflight` | Yes | Yes | Yes | Python 3.11+ |
| `/blog factcheck` | Yes | Yes | Yes | Web search |
| `/blog google` | Yes | Credentials via options/env | Yes | Python deps + Google credential |
| `/blog audio` | Yes | Yes | Yes | Google AI API key |
| `/blog image` | Yes | **No** | Yes | API key + local MCP server |
| `/blog notebooklm` | Yes | **No** | Yes | Local browser + interactive sign-in |
| `/blog flow sync` | Yes | Yes | Yes | HTTPS to `api.github.com` |

The two "No" cells are platform limits, not bugs:

- **`/blog image`** runs the nanobanana MCP server as a local process. Plugins
  bundling local MCP servers work in Claude Desktop and Claude Code; a Cowork
  session on web or mobile has no local process to attach to. The skill detects
  this and returns the full image brief - 6-component prompt, aspect ratio, alt
  text - ready to paste into any image tool.
- **`/blog notebooklm`** drives a real browser through an interactive Google
  login, which needs a local browser and a human at the keyboard. The skill
  suggests `/blog factcheck` instead.

Both degrade with an explanation rather than an error. Claude checks first:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/runtime_capabilities.py" --check image --json
```

## Files and folders

Cowork runs in a sandbox that can only reach folders you have mounted into the
session. Two consequences worth knowing:

1. **Mount the folder your blog lives in** before asking for work on existing
   posts. `/blog audit ./posts` cannot see a folder Cowork was not given.
2. **Drafts are written to your working folder**, not into the plugin. The
   plugin directory is read-only and is replaced on every update.

Saved personas follow the same rule: they go to the plugin's persistent data
directory, which survives updates, and fall back to `.claude-blog/personas/` in
your working folder. Uninstalling the plugin does not delete them.

## Cowork vs Claude Code: practical differences

| | Cowork | Claude Code |
|---|---|---|
| Install | Plugin UI (marketplace or upload) | `claude plugin install`, or `install.sh` |
| Credentials | Plugin options (secure storage) | `~/.config/claude-seo/google-api.json`, mode 0600 |
| File access | Mounted folders only | Working directory and below |
| Home directory | May not persist between sessions | Persistent |
| Local MCP servers | Desktop only | Yes |
| Python packages | Preinstalled set; installing more may not persist | You control the environment |

Because a hosted Cowork home directory may not survive between sessions, prefer
the plugin's own options over `/blog google setup` there - options are set once
and persist with the plugin.

## Troubleshooting

**Skills do not appear after installing from a marketplace.** This is the known
mounting issue linked above. Package the plugin yourself and upload the file.

**`/blog image` says generation is unavailable.** Expected on Cowork web and
mobile. On desktop, check the Google AI API key option is set, then confirm with
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/runtime_capabilities.py" --check image --json`.

**A path Claude cannot find.** The folder is probably not mounted into the
session. Add it in Cowork's folder settings rather than moving your files.

**`/blog analyze` reports missing readability grades.** `textstat` and
`beautifulsoup4` are optional. Scoring still runs on the heuristic fallback;
the report says which grades were skipped.
