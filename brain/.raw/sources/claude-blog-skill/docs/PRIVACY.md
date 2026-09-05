# Privacy Policy

**Claude Blog** is a Claude Code plugin that runs entirely on your local machine. It does not collect, store, transmit, or share any personal data or usage information.

## What This Plugin Does NOT Do

- Does not collect analytics or telemetry
- Does not send data to any external server (except when you explicitly use web search, API calls to CMS platforms, or MCP servers you configure)
- Does not create accounts or require authentication
- Does not store cookies or tracking identifiers
- Does not access any data outside of the files and URLs you provide to it

## Third-Party Services

When you explicitly invoke certain commands, the plugin may interact with external services **on your behalf and under your control**:

| Feature | Service | When |
|---------|---------|------|
| AI image generation | Google Gemini API (via nanobanana-mcp) | Only when you run `/blog image` and have configured your own API key |
| Audio narration | Google Gemini TTS API | Only when you run `/blog audio` and have configured your own API key |
| Web research and fetching | Search engines, public web pages | Used by most commands for research, SERP analysis, link verification, and source checking (`/blog write`, `/blog rewrite`, `/blog analyze`, `/blog brief`, `/blog outline`, `/blog strategy`, `/blog seo-check`, `/blog factcheck`, `/blog geo`, `/blog calendar`, `/blog persona`, `/blog cannibalization`) |
| SERP and keyword data | DataForSEO API (~$0.01/call) | Only when you run `/blog cannibalization --api` with your own DataForSEO credentials. Local mode (default) requires no API |
| CMS taxonomy sync | WordPress, Shopify, Ghost, Strapi, Sanity APIs | Only when you run `/blog taxonomy` with your own CMS credentials |
| NotebookLM research | Google NotebookLM | Only when you run `/blog notebooklm` with your own configuration |
| Google API data | Google PageSpeed Insights, CrUX, Search Console, GA4, YouTube Data API, Cloud NLP, Indexing API, Keyword Planner | Only when you run `/blog google` commands and have configured your own API credentials at `~/.config/claude-seo/google-api.json` |

All API keys and credentials are stored locally in your environment variables or `.env` files. This plugin never transmits your credentials to any party other than the service you are explicitly calling.

## Data Residency

All generated content (blog posts, images, audio files, analysis reports) is saved to your local filesystem only.

## Project-root context files (v1.8.0)

Three optional files can be created at the root of any project that uses this plugin. They are read by the orchestrator when present and skipped silently when absent. They are NEVER transmitted off your machine:

| File | Created by | Purpose | Privacy note |
|---|---|---|---|
| `BRAND.md` | `/blog brand init` | Audience, positioning, editorial rules, taboo phrases, competitor differentiation | May contain confidential positioning. Add to `.gitignore` if your repo is public and the brand context is non-public. |
| `VOICE.md` | `/blog brand init` | Tone fingerprint, lexical rules, headline patterns | Generally safe to commit; mirrors the persona JSON. |
| `DISCOURSE.md` | `/blog discourse <topic>` | Cross-platform discourse research brief for a topic | Topic and brief are visible only locally. The script that produces this file (`scripts/discourse_research.py`) reads pre-gathered SERP results from a temp file you specify and emits the brief. No network calls in the script itself. |

If any of these files contain confidential information (competitor positioning, internal product strategy, customer-discourse research on private topics), add them to `.gitignore` before committing.

## Contact

For privacy questions, open an issue at: https://github.com/AgriciDaniel/claude-blog/issues

## Last Updated

2026-05-17
