# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-03-06

### Added
- **Plugin ecosystem support**: `.claude-plugin/plugin.json` for `/plugin install` compatibility
- **44 pytest unit tests** for `analyze_blog.py` — covers frontmatter, headings, paragraphs, images, AI detection, citations, FAQ, freshness, readability, links, schema, and integration tests
- **GitHub Actions CI**: 3 jobs — Python tests (3.11 + 3.12), SKILL.md frontmatter validation, plugin.json validation
- **DataForSEO MCP integration** documentation — recommended primary MCP server for live SEO data (SERP, keywords, backlinks, on-page, domain analytics, content analysis, AI optimization)
- `pyproject.toml` with dependency groups (core, advanced, dev)
- `CONTRIBUTING.md` with development guidelines
- `.mcp.json` for optional MCP server configuration
- Skill evaluation scenarios (7 trigger test cases)

### Changed
- **Directory restructure**: `blog/` → `skills/blog/` (official Anthropic plugin layout)
- Updated all internal path references across skills, docs, and install scripts
- README updated with plugin install as primary method
- MCP-INTEGRATION.md updated with DataForSEO as recommended integration

### Fixed
- **install.sh**: Restored `TEMP_DIR` global scope fix (lost during restructure)
- **install.sh**: Removed `--break-system-packages` pip flag (security concern)
- **install.sh**: Removed redundant `mkdir` and double-copy of `skills/blog/`
- **CI**: Fixed lint-markdown grep matching legitimate `skills/blog/references/` paths
- **Docs**: Fixed 11 instances of double `skills/skills/` paths in INSTALLATION.md and TROUBLESHOOTING.md

### Removed
- `--break-system-packages` pip install flag

## [1.1.0] - 2026-02-18

### Added
- **Built-in SVG chart generation** (`blog-chart` sub-skill) — eliminates external `/svg` dependency
  - Supports 7 chart types: horizontal bar, grouped bar, donut, line, lollipop, area, radar
  - Dark-mode compatible, accessible (WCAG), platform-aware (HTML/JSX auto-detection)
- **Image URL verification** in researcher agent — validates HTTP 200 before embedding
- **Mid-writing readability check** in writer agent — self-checks Flesch targets before returning
- **Image density guidelines** by content type in visual-media.md

### Changed
- claude-blog is now fully self-contained — no external skill dependencies required
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
- Main orchestrator: `skills/blog/SKILL.md` (routes all 12 commands)
- 12 sub-skills in `skills/blog-*/SKILL.md`
- 4 subagents in `agents/blog-*.md`
- 12 reference docs in `skills/blog/references/` (loaded on-demand)
- 12 content templates in `skills/blog/templates/`

### Fixed
- Corrected phantom "January 2026 Authenticity Update" references to verified **December 2025 Core Update** (Dec 11-29, 2025)
