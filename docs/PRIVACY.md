# Privacy Policy

**Claude Blog** adds local skill files and helper scripts to Claude Code. The plugin has no independent analytics service. Claude Code sends prompts and model context to your configured model provider; files read into that context can leave your machine. Provider retention and training policies depend on your account and settings. See the [Claude Code data usage documentation](https://code.claude.com/docs/en/data-usage), reviewed 2026-10-07.

## What This Plugin Does NOT Do

- Adds no plugin-specific analytics or telemetry; the host has its own data policies
- Helper scripts contact external services for requested research, link checks, and configured integrations; model processing also uses the host provider
- Creates no service account; optional integrations can require your existing credentials
- NotebookLM authentication can store browser cookies and session state locally
- Skills can read project context and trusted installed references needed for the requested task

## Third-Party Services

When you explicitly invoke certain commands, the plugin may interact with external services **on your behalf and under your control**:

| Feature | Service | When |
|---------|---------|------|
| AI image generation | Google Gemini API (via nanobanana-mcp) | When requested by `/blog image` or a configured write/rewrite workflow with your API key |
| Audio narration | Google Gemini TTS API | Only when you run `/blog audio` and have configured your own API key |
| Web research and fetching | Search engines, public web pages | Used by most commands for research, SERP analysis, link verification, and source checking (`/blog write`, `/blog rewrite`, `/blog analyze`, `/blog brief`, `/blog outline`, `/blog strategy`, `/blog seo-check`, `/blog factcheck`, `/blog geo`, `/blog calendar`, `/blog persona`, `/blog cannibalization`) |
| SERP and keyword data | DataForSEO API (provider pricing applies) | Only when you run `/blog cannibalization --api` with your own DataForSEO credentials. Local mode (default) requires no API |
| CMS taxonomy sync | WordPress, Shopify, Ghost, Strapi, Sanity APIs | Only when you run `/blog taxonomy` with your own CMS credentials |
| NotebookLM research | Google NotebookLM | Only when you run `/blog notebooklm` with your own configuration |
| Google API data | Google PageSpeed Insights, CrUX, Search Console, GA4, YouTube Data API, Cloud NLP, Keyword Planner, and Indexing API for JobPosting or livestream URLs only | Only when you run `/blog google` commands and have configured your own API credentials at `~/.config/claude-seo/google-api.json` |

Credentials may be stored in environment variables, private configuration files, OAuth token files, or NotebookLM browser state. Authenticated helpers send credentials to their configured provider. Keep credentials out of prompts, generated content, logs, and tracked files; review host and MCP configuration before handling private data.

## Data Residency

Delivery artifacts are saved to the local filesystem. Content used for model generation, browser research, or API requests is also processed by the selected providers; local artifact storage does not establish local-only processing.

## Project-root context files (v1.8.0)

Three optional files can be created at the root of any project that uses this plugin. They are read by the orchestrator when present and skipped silently when absent. Their contents can enter model context when read by the host:

| File | Created by | Purpose | Privacy note |
|---|---|---|---|
| `BRAND.md` | `/blog brand init` | Audience, positioning, editorial rules, taboo phrases, competitor differentiation | May contain confidential positioning. Add to `.gitignore` if your repo is public and the brand context is non-public. |
| `VOICE.md` | `/blog brand init` | Tone fingerprint, lexical rules, headline patterns | Generally safe to commit; mirrors the persona JSON. |
| `DISCOURSE.md` | `/blog discourse <topic>` | Cross-platform discourse research brief for a topic | The brief is stored locally and can enter model context. The script that produces this file (`scripts/discourse_research.py`) reads pre-gathered SERP results from a temp file you specify and emits the brief. No network calls in the script itself. |

If any of these files contain confidential information (competitor positioning, internal product strategy, customer-discourse research on private topics), add them to `.gitignore` before committing.

## Contact

For privacy questions, open an issue at: https://github.com/AgriciDaniel/claude-blog/issues

## Last Updated

2026-10-07
