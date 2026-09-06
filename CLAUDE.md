# Claude Blog - Blog Creation & Optimization Skill

## Project Overview

This repository contains **Claude Blog**, a Tier 4 Claude Code skill for blog content
creation, optimization, and management. It follows the Agent Skills open standard and the
3-layer architecture (directive, orchestration, execution). 32 skill directories
(1 orchestrator + 31 sub-skills), 30 user-facing `/blog` commands, 5 specialized
subagents, 12 content templates, and 23 reference docs are dual-optimized for Google rankings
(2026 core and spam update timeline, E-E-A-T) and AI citations (GEO/AEO). Includes FLOW framework
integration, semantic topic-cluster planning + execution, multilingual publishing (Pro Hub
Challenge v1.7.0), BRAND.md/VOICE.md/DISCOURSE.md project-root context auto-load (v1.8.0,
fenced via `scripts/load_untrusted_root.py` with CSPRNG nonces, v1.8.3+), CI-enforced
prose hygiene via `scripts/lint_prose.py` (v1.8.4+), and the 5-gate Blog Delivery Contract
(v1.9.0, `skills/blog/references/blog-delivery-contract.md`) that runs `blog_preflight.py`
+ a BLOCKING `blog-reviewer` agent between every draft and the user.

## Architecture

```
claude-blog/
  CLAUDE.md                          # Project instructions (this file)
  docs/CONTRIBUTORS.md               # Pro Hub Challenge attribution and integration decisions
  CHANGELOG.md                       # Keep a Changelog format
  .claude-plugin/plugin.json         # Plugin manifest (v2.3.0) + userConfig for the optional Gemini key
  .claude-plugin/marketplace.json    # Marketplace catalog for distribution
  mcp-servers.json                   # Shipped MCP config, referenced from plugin.json; opt-in image server
  .mcp.example.json                  # MCP config example (tracked; .mcp.json is gitignored)
  pyproject.toml                     # Python packaging (3.11+)
  brain/                             # Vendored self-contained evidence-gated Obsidian brain; not plugin payload; tooling stays under skills/
  scripts/analyze_blog.py            # 5-category quality scoring (stdlib)
  scripts/runtime_capabilities.py    # Per-surface capability detection; call before any script-backed skill (v2.3.0)
  scripts/package_plugin.py          # Builds the Claude Cowork .plugin upload artifact (v2.3.0)
  scripts/nanobanana-launcher.mjs    # Gates the image MCP server behind an API key; inert without one (v2.3.0)
  scripts/blog_preflight.py          # 5-gate delivery contract runner (v1.9.0)
  scripts/blog_render.py             # md -> html -> pdf renderer; XSS-safe JSON-LD (v1.9.0)
  scripts/blog_hygiene.py            # Optional deterministic hygiene: lazy-load imgs + auto-TOC (v1.11.0)
  scripts/cognitive_load.py          # Per-section concept-density analyzer (v1.8.0)
  scripts/discourse_research.py      # Discourse brief synthesis from SERP JSON (v1.8.0)
  scripts/generate_hero.py           # Hero image ladder: Banana -> Gemini -> stock -> Openverse (v1.9.0)
  scripts/load_untrusted_root.py     # Code-enforced fence helper for BRAND/VOICE/DISCOURSE (v1.8.3)
  scripts/lint_prose.py              # Fence-aware prose-hygiene linter (v1.8.4; CI-enforced)
  scripts/sync_flow.py               # Pulls FLOW references (stdlib, sandboxed)
  scripts/ai_citation_score.py       # AI citation readiness heuristic, 0-100
  scripts/content_decay.py           # GSC content-decay detector: 20%+ QoQ decline (v1.10.0)
  scripts/quality_gate.py            # Pre-commit gate: block posts scoring < 70 (v1.10.0)
  scripts/style_learn.py             # Author voice-profile learner from sample posts (v1.10.0)
  scripts/consistency_check.py       # Local reference + FLOW lock validation
  scripts/dependency_smoke.py        # Offline optional-runtime initialization checks
  scripts/validate_public_release.py # Read-only public worktree validation
  skills/                            # 32 skill directories (1 orchestrator + 31 sub-skills)
    blog/SKILL.md                   # Main orchestrator, routing, scoring
      references/                   # 23 on-demand knowledge files (5 in v1.8.0, 1 in v1.9.0)
      templates/                    # 12 content templates
      scripts/                     # Python analysis scripts
    blog-write/SKILL.md            # Write new articles from scratch
    blog-rewrite/SKILL.md         # Optimize existing blog posts
    blog-analyze/SKILL.md         # 5-category 100-point scoring
    blog-brief/SKILL.md           # Detailed content briefs
    blog-outline/SKILL.md         # SERP-informed outlines
    blog-calendar/SKILL.md        # Editorial calendars
    blog-strategy/SKILL.md        # Blog positioning and planning
    blog-seo-check/SKILL.md      # Post-writing SEO validation
    blog-schema/SKILL.md          # JSON-LD schema generation
    blog-chart/SKILL.md           # Inline SVG data visualizations
    blog-repurpose/SKILL.md       # Multi-platform repurposing
    blog-geo/SKILL.md             # AI citation optimization
    blog-audit/SKILL.md           # Full-site blog health assessment
    blog-image/                    # AI image generation via Gemini
      SKILL.md                    # Image generation sub-skill
      references/                 # 3 reference docs (models, tools, prompts)
      scripts/                    # MCP setup and validation scripts
    blog-cannibalization/SKILL.md # Keyword overlap detection
    blog-factcheck/SKILL.md       # Statistics verification
    blog-persona/SKILL.md         # Writing persona management
    blog-taxonomy/SKILL.md        # CMS taxonomy management
    blog-notebooklm/               # NotebookLM source-grounded research
      SKILL.md                    # NotebookLM query sub-skill
      references/                 # 2 reference docs (commands, troubleshooting)
      scripts/                    # 10 Python scripts + requirements.txt
    blog-audio/                    # Audio narration via Gemini TTS
      SKILL.md                    # Audio generation sub-skill
      references/                 # 1 reference doc (30 voice catalog)
      scripts/                    # 5 Python scripts + requirements.txt
    blog-google/                   # Google API integration
      SKILL.md                    # Google API sub-skill (13 commands, 4 tiers)
      references/                 # 3 reference docs (auth, API, quotas)
      scripts/                    # 11 Google API scripts + venv wrapper
      assets/templates/           # 3 report templates
    blog-cluster/                  # Semantic topic-cluster planning + execution (v1.7.0)
      SKILL.md                    # Cluster planning + execute orchestrator
      references/                 # 3 ref docs (semantic clustering, architecture, execution)
    blog-flow/                     # FLOW framework prompts (v1.7.0)
      SKILL.md                    # FLOW orchestrator (find/optimize/win/prompts/sync)
      references/                 # Synced from github.com/AgriciDaniel/flow (CC BY 4.0)
    blog-multilingual/             # One-command international publishing (v1.7.0)
      SKILL.md                    # Multilingual orchestrator
    blog-translate/                # SEO-optimized translation (v1.7.0)
      SKILL.md
      references/                 # Translation rules + cultural adaptation profiles
    blog-localize/                 # Cultural deep-adaptation (v1.7.0)
      SKILL.md
    blog-locale-audit/             # Multilingual content QA (v1.7.0)
      SKILL.md
    blog-brand/SKILL.md            # BRAND.md + VOICE.md context files (v1.8.0)
    blog-discourse/SKILL.md        # Last-30-days discourse research (v1.8.0)
    blog-style/SKILL.md            # Author voice-profile learner (v1.10.0)
    blog-decay/SKILL.md            # GSC content-decay detector (v1.10.0)
  agents/                            # 5 specialized subagents
    blog-researcher.md              # Statistics and source research
    blog-writer.md                  # Content generation
    blog-seo.md                     # SEO validation
    blog-reviewer.md                # Quality scoring (no Bash, post v1.7.0 hardening)
    blog-translator.md              # Multilingual translation (no Bash, v1.7.0)
  tests/                             # 250+ pytest checks incl. delivery-contract + security suites
```

## Commands

| Command | Purpose |
|---------|---------|
| `/blog write` | Write new articles optimized for rankings + AI citations |
| `/blog rewrite` | Optimize existing posts with sourced statistics; `/blog update` aliases here |
| `/blog analyze` | 5-category 100-point scoring with evidence and style diagnostics, not authorship detection |
| `/blog brief` | Detailed content briefs with competitive analysis |
| `/blog outline` | SERP-informed outlines with heading hierarchy |
| `/blog calendar` | Editorial calendars with topic clusters |
| `/blog strategy` | Blog positioning and content planning |
| `/blog seo-check` | Post-writing SEO validation checklist |
| `/blog schema` | JSON-LD schema markup generation |
| `/blog repurpose` | Multi-platform content repurposing |
| `/blog geo` | AI citation optimization audit |
| `/blog image` | AI image generation and editing via Gemini |
| `/blog audit` | Full-site blog health assessment |
| `/blog cannibalization` | Detect keyword overlap across posts |
| `/blog factcheck` | Verify statistics against cited sources |
| `/blog persona` | Manage writing personas and voice profiles |
| `/blog taxonomy` | Tag/category CMS management |
| `/blog notebooklm` | Query NotebookLM for source-grounded research |
| `/blog audio` | Generate audio narration via Gemini TTS |
| `/blog google` | Google API data: PSI, CrUX, GSC, GA4, NLP, YouTube, Keywords |
| `/blog cluster` | Semantic topic-cluster planning + execution (v1.7.0) |
| `/blog multilingual` | Write + translate + localize + emit hreflang in one command (v1.7.0) |
| `/blog translate` | SEO-optimized translation with format preservation (v1.7.0) |
| `/blog localize` | Cultural deep-adaptation per locale (v1.7.0) |
| `/blog locale-audit` | Multilingual content QA (v1.7.0) |
| `/blog flow` | FLOW framework prompts: find, optimize, win, prompts index, sync (v1.7.0) |
| `/blog brand` | Generate BRAND.md + VOICE.md context auto-loaded by all sub-skills (v1.8.0) |
| `/blog discourse` | API-free last-30-days discourse research; produces DISCOURSE.md (v1.8.0) |
| `/blog style` | Learn author voice profile from existing posts (v1.10.0) |
| `/blog decay` | Detect content decay from GSC exports (v1.10.0) |

Internal capability: `blog-chart` generates inline SVG charts for `/blog write`
and `/blog rewrite`; it is not a top-level user command.

## Development Rules

- Keep SKILL.md files under 500 lines / 5000 tokens
- **Never write a bare intra-plugin path.** Every reference to a file inside the plugin must be `${CLAUDE_PLUGIN_ROOT}/...`. The working directory belongs to the user, not the plugin, so `references/x.md` or `python3 scripts/run.py` resolve to nothing on every surface (Cowork, Claude Code, Desktop). `test_no_bare_intra_plugin_paths_in_runtime_files` enforces this. Naming a skill file in prose (`skills/blog-brand/SKILL.md`) is documentation, not a load path, and needs no variable
- **Never write user state into the plugin directory.** It is read-only in Claude Cowork and replaced wholesale on update. Deliverables go to the working directory; state that must survive updates goes to `${CLAUDE_PLUGIN_DATA}` (personas, NotebookLM auth/library)
- Anything needing Python, a credential, or an MCP server must call `scripts/runtime_capabilities.py` first and degrade with an explanation rather than a traceback. See `skills/blog/references/cowork-runtime.md`
- The shipped MCP config is `mcp-servers.json` (referenced from `plugin.json`), deliberately **not** `.mcp.json`: that filename is also read as a project-scoped config, so a contributor in this repo would have Claude launch it with `${CLAUDE_PLUGIN_ROOT}` unresolved
- SKILL.md frontmatter: only valid fields (name, description, user-invocable, argument-hint, compatibility, license, metadata, disable-model-invocation). Do NOT use `allowed-tools`; it is not a Claude Code spec field
- New reference files should be focused and under 200 lines. Existing comprehensive references (platform-guides, schema-stack, content-templates, distribution-playbook) are exempt from this guideline
- Scripts must have docstrings, CLI interface, and JSON output
- Follow kebab-case naming for all skill directories
- Agents invoked via Task tool, never via Bash
- Python 3.11+ required; dependencies in pyproject.toml
- Test with `python3 -m pytest tests/` after changes
- Run `claude plugin validate .` before pushing plugin changes
- Run `python3 scripts/package_plugin.py` to build the Cowork upload artifact
- Run `python3 scripts/lint_prose.py` locally to catch forbidden prose chars before CI does (v1.8.4+)
- Project-root file loading (BRAND.md/VOICE.md/DISCOURSE.md): use `scripts/load_untrusted_root.py` via Bash; never hand-roll a fence (v1.8.3+)
- Plugin skills auto-discovered from `skills/` directory (do not list in plugin.json)

## Distribution

### Anthropic Official Marketplace
Submit at: claude.ai/settings/plugins/submit or platform.claude.com/plugins/submit

### Self-Hosted Marketplace
```
/plugin marketplace add AgriciDaniel/claude-blog
/plugin install claude-blog@agricidaniel-blog
```

### Standalone Install (no marketplace)
```bash
curl -fsSLo install.sh \
  https://raw.githubusercontent.com/AgriciDaniel/claude-blog/v2.3.0/install.sh
# Compare the SHA-256 digest with the value published in README.md.
CLAUDE_BLOG_REF=v2.3.0 bash ./install.sh
```

## Release Blog Post

After cutting a new release (git tag + `gh release create`), run:

```
/release-blog
```

This generates a blog post on https://claude-blog.md/blog/, handles cover image generation, SEO metadata, FAQ schema, internal linking, sitemap/llms.txt updates, and Vercel deployment.
