# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-03-04

### Added
- **Native Gemini slash commands** -- 12 `.toml` command files in `commands/blog/`
  - `/blog:write`, `/blog:analyze`, `/blog:rewrite`, `/blog:brief`, `/blog:outline`
  - `/blog:seo-check`, `/blog:schema`, `/blog:repurpose`, `/blog:geo`, `/blog:audit`
  - `/blog:calendar`, `/blog:strategy`
- `contextFileName` field in `gemini-extension.json` (required by Gemini CLI)

### Changed
- **Converted to native Gemini CLI extension format** -- project now installs via `gemini extensions install .`
- Stripped Claude-only YAML frontmatter from `GEMINI.md` (main orchestrator)
- Stripped Claude-only `tools:` frontmatter from 4 agent `.GEMINI.md` files
- Stripped Claude-only `allowed-tools:` frontmatter from 13 skill `GEMINI.md` files
- Updated `docs/INSTALLATION.md` to reflect extension install method
- Updated `docs/ARCHITECTURE.md` with correct file naming conventions
- Updated `docs/COMMANDS.md` with `/blog:command` syntax
- Updated `docs/MIGRATION_DIFFERENCES.md` for the extension format
- Updated `docs/TROUBLESHOOTING.md` with current file references

### Fixed
- **Tool Compatibility**: Updated `allowed-tools` in SKILL.md and `tools` in agent definitions to align with Gemini CLI cross-platform naming conventions (e.g., `read_file`, `run_shell_command`, `replace`, `grep_search`).
- **Agent Loading**: Resolved "Invalid tool name" errors during extension installation by standardizing on `snake_case` tool names.

### Removed
- `manifest.excludeTools` block from `gemini-extension.json` (GitHub tool exclusions irrelevant to blog extension)

## [1.1.1] - 2026-03-03

### Fixed
- **Tool Compatibility**: Initial standardization of tool names for Gemini CLI environment.

## [1.1.0] - 2026-02-18

### Added
- **Built-in SVG chart generation** (`blog-chart` sub-skill) — eliminates external `/svg` dependency
  - Supports 7 chart types: horizontal bar, grouped bar, donut, line, lollipop, area, radar
  - Dark-mode compatible, accessible (WCAG), platform-aware (HTML/JSX auto-detection)
- **Image URL verification** in researcher agent — validates HTTP 200 before embedding
- **Mid-writing readability check** in writer agent — self-checks Flesch targets before returning
- **Image density guidelines** by content type in visual-media.md

### Changed
- gemini-blog is now fully self-contained — no external skill dependencies required
- Integration section updated to list companion skills as optional
- Installer scripts updated for 13 sub-skills

### Removed
- External `/svg` / `/svg-chart` skill dependency

## [1.0.0] - 2026-02-18

### Added
- **12 slash commands**: write, rewrite, analyze, brief, calendar, strategy, outline, seo-check, schema, repurpose, geo, audit
- **12 reference documents** loaded on-demand (RAG pattern):
  - google-landscape-2026, geo-optimization, content-rules, visual-media, quality-scoring
  - eeat-signals, content-templates, ai-crawler-guide, schema-stack, platform-guides, distribution-playbook, internal-linking
- **12 content type templates**: how-to, listicle, case study, comparison, pillar page, product review, thought leadership, roundup, tutorial, news analysis, data research, FAQ/knowledge base
- **4 specialized subagents**: blog-researcher, blog-writer, blog-seo, blog-reviewer
- **Python quality analysis script** (`analyze_blog.py`):
  - 5-category, 100-point scoring system (Content 30, SEO 25, E-E-A-T 15, Technical 15, AI Citation 15)
  - Readability analysis via textstat (Flesch, Gunning Fog, SMOG, Coleman-Liau)
  - AI content detection signals (burstiness, known AI phrases, vocabulary diversity)
  - Schema detection via BeautifulSoup
  - Batch mode with directory scanning
  - Multiple output formats (JSON, markdown, table)
  - Graceful degradation without optional dependencies
- **Unix + Windows installers** (install.sh, install.ps1) with one-command curl install
- **Uninstaller** (uninstall.sh) for clean removal
- **Full documentation suite** (docs/): Installation, Commands, Architecture, Templates, Troubleshooting, MCP Integration

### Architecture
- Main orchestrator: `GEMINI.md` (routes all 12 commands)
- 12 sub-skills in `skills/blog-*/GEMINI.md`
- 4 subagents in `agents/blog-*.GEMINI.md`
- 12 reference docs in `blog/references/` (loaded on-demand)
- 12 content templates in `blog/templates/`
- 12 slash commands in `commands/blog/*.toml`

### Fixed
- Corrected phantom "January 2026 Authenticity Update" references to verified **December 2025 Core Update** (Dec 11-29, 2025)
