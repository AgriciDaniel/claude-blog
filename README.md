<p align="center">
  <img src="assets/banner.svg" alt="Claude Blog: AI Blog Writing and SEO Optimization Skill for Claude Code. Animated terminal-style banner with pixel-art CLAUDE BLOG wordmark, breathing orange gradient, scanning command palette, and pulsing status indicators" width="100%">
</p>

# AI Blog Writing & SEO Optimization Skill for Claude Code (`claude-blog`)

<p align="center">
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/Agent%20Skills-Compatible-blue" alt="Agent Skill"></a>
  <a href="https://github.com/AgriciDaniel/claude-blog/releases"><img src="https://img.shields.io/github/v/release/AgriciDaniel/claude-blog?label=public%20release" alt="Version"></a>
  <a href="https://github.com/AgriciDaniel/claude-blog/actions"><img src="https://img.shields.io/github/actions/workflow/status/AgriciDaniel/claude-blog/ci.yml?branch=main&label=public%20CI" alt="CI"></a>
  <a href="https://www.skool.com/ai-marketing-hub-pro"><img src="https://img.shields.io/badge/AI%20Marketing%20Hub-Pro%20community-purple" alt="Community"></a>
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License: MIT">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Sub--Skills-30-orange" alt="Sub-Skills">
  <img src="https://img.shields.io/badge/Tests-187%20passing-brightgreen" alt="Tests: 187 passing">
</p>

<p align="center">
  <a href="https://youtu.be/7Q4GaSgUFHo"><img src="https://img.youtube.com/vi/7Q4GaSgUFHo/maxresdefault.jpg" alt="Watch the Claude Blog v1.9.1 walkthrough on YouTube" width="640"></a>
</p>

<p align="center">
  <strong><a href="https://youtu.be/7Q4GaSgUFHo">Watch the 12:48 v1.9.1 walkthrough on YouTube</a></strong> · See the 5-gate Blog Delivery Contract run live, including a 6-minute live demo of the <a href="https://claude-blog.md/blog/chatgpt-codex-vs-claude-code-2026">Codex vs Claude sample blog</a> being generated end-to-end.
</p>

> **Two versions of this skill.** Choose the one that fits how you work:
>
> - 🌐 **Public open-source**: [`AgriciDaniel/claude-blog`](https://github.com/AgriciDaniel/claude-blog). MIT-licensed, public releases, open to anyone. Use this if you want the stable, downloadable, no-membership-required version.
> - 🔒 **Community private mirror** (this repo): [`AI-Marketing-Hub/claude-blog`](https://github.com/AI-Marketing-Hub/claude-blog). Early access to in-development work (v1.9.0+ Blog Delivery Contract, hero ladder, mutation-tested regression coverage), and direct collaboration with the [AI Marketing Hub Pro](https://www.skool.com/ai-marketing-hub-pro) community. Requires membership.
>
> The badges above track the **public** repo (`AgriciDaniel/claude-blog`) since the private mirror is not visible to shields.io. The publishing workflow (private dev, review, public release) is documented in [`docs/PUBLISHING.md`](docs/PUBLISHING.md).

> **Blog:** [See how claude-blog works](https://agricidaniel.com/blog/claude-code-blog-writer)

**claude-blog is a Claude Code skill suite that writes, optimizes, and audits blog content at scale.** Every article is dual-optimized for Google rankings (December 2025 Core Update, E-E-A-T) and AI citation platforms (ChatGPT, Perplexity, AI Overviews). A v1.9.0 5-gate Delivery Contract scores every draft against a 100-point rubric and blocks anything below 90 from reaching you.

## Key takeaways

- **What it is**: a full-lifecycle blog engine: 30 sub-skills, 5 agents, 12 content templates, 21 on-demand references, 9 root-level Python scripts, 160 passing tests.
- **Who it is for**: solo bloggers, marketing teams, agencies, and Claude Code skill builders who want production-grade content output, not one-shot drafts.
- **Core promise**: every draft passes a 5-gate delivery contract (Capability, Format, Visual, Content Review, Asset Integrity) or the writer iterates up to 3 times before escalating to you.
- **What makes it different**: it eats its own dogfood. Version-coherence is CI-enforced across 14 surfaces, prose-hygiene runs on every PR, three mutation-tested regression suites lock the v1.9.0 fixes, and `blog-reviewer` is a BLOCKING gate, not advisory.
- **Today**: v1.9.0, released 2026-05-18. Works on Next.js MDX, Astro, Hugo, Jekyll, WordPress, Ghost, 11ty, Gatsby, and static HTML.

## Who is claude-blog for?

claude-blog serves three audiences with one engine:

**Solo bloggers and creators** who want to ship one high-quality post per week without spending three hours on the SEO checklist. The orchestrator handles research, outline, draft, schema, internal linking, and citation verification in a single `/blog write` invocation.

**Marketing teams and agencies** managing many posts across topics, languages, and platforms. The skill ships topic-cluster planning (`/blog cluster`), multilingual one-command publishing (`/blog multilingual`), cannibalization detection (`/blog cannibalization`), and persona-driven voice profiles (`/blog persona`) so the same engine produces consistent content across the team.

**Claude Code skill builders** who want a production-grade reference for skill architecture, agent dispatch, delivery contracts, and CI gating. The repo demonstrates the Agent Skills open standard at Tier 4 complexity with 160 tests, version-coherence enforcement, installer-sync regression tests, and the v1.9.0 5-gate contract pattern. Read the source for inspiration; fork the patterns into your own skills.

## What does claude-blog produce?

Every draft ships as 8 artifacts in a single folder. A condensed specimen of the `.md` output:

```markdown
---
title: "Where Should a Claude Code Skill Plugin Install Itself?"
description: "A working answer to the install-path question..."
date: "2026-05-18"
author: "Daniel Agrici"
tags: [claude-code, skills, plugins, installation]
canonical: "https://example.com/blog/skill-plugin-install-path"
---

# Where Should a Claude Code Skill Plugin Install Itself?

The short answer: most user-installable Claude Code skill plugins
should ship to `~/.claude/skills/<name>/` for skill content,
`~/.claude/agents/<name>.md` for agents, and
`~/.claude/scripts/<helper>.py` for any Python helpers.

## Key Takeaways
- `~/.claude/skills/` is the SKILL.md surface area.
- `~/.claude/agents/` holds agent markdown files.
- ... (full article, sourced citations, FAQ, schema JSON-LD)
```

Alongside the `.md`, the contract also produces: rendered `.html` (XSS-safe JSON-LD, dark-mode-aware CSS), `.pdf` (Playwright or weasyprint), `hero.<ext>` (1200x630, generated via Banana MCP, Gemini, stock APIs, or Openverse), 3 viewport screenshots (`mobile-375.png`, `tablet-768.png`, `desktop-1280.png`), `review.md` (5-category scorecard with BLOCKING line), and `preflight-report.json` (the full audit trail).

## Table of Contents

- [Demo](#demo)
- [Quick Start](#quick-start)
- [Commands](#commands)
- [How does claude-blog compare?](#how-does-claude-blog-compare)
- [Features](#features)
- [Delivery contract (v1.9.0)](#delivery-contract-v190)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Frequently Asked Questions](#frequently-asked-questions)
- [Roadmap](#roadmap)
- [Uninstall](#uninstall)
- [Integration](#integration)
- [Documentation](#documentation)
- [How to cite](#how-to-cite)
- [Security & Code of Conduct](#security--code-of-conduct)
- [Contributing](#contributing)
- [License](#license)
- [Related projects](#related-projects)
- [Author](#author)

## Demo

[Watch the Demo on YouTube](https://www.youtube.com/watch?v=AeLC4iutG8w)

<p align="center">
  <img src="assets/blog-command-demo.gif" alt="claude-blog command demo: routing /blog subcommands through the orchestrator" width="100%">
</p>

---

## Quick Start

> ℹ️ **Which version are you installing?**
>
> - **Not an AI Marketing Hub Pro member?** Install from the public repo: [`AgriciDaniel/claude-blog`](https://github.com/AgriciDaniel/claude-blog). All the install commands below work there. Just swap `AI-Marketing-Hub/claude-blog` for `AgriciDaniel/claude-blog` and the plugin slug `claude-blog@ai-marketing-hub-claude-blog` for `claude-blog@agricidaniel-claude-blog`. Public releases ship there; this private mirror runs ahead.
> - **Pro member?** The commands below install the **community version** with early access to in-development features. They require an authenticated `gh auth login` (or GitHub PAT) session with access to the `AI-Marketing-Hub` org. If `/plugin marketplace add` fails with a 404, your account is not in the org yet. DM in the [Skool community](https://www.skool.com/ai-marketing-hub-pro) to get added.

**Plugin Install (Claude Code 1.0.33+):**

```bash
# Add marketplace (one-time)
/plugin marketplace add AI-Marketing-Hub/claude-blog

# Install plugin
/plugin install claude-blog@ai-marketing-hub-claude-blog
```

**Recommended: clone, verify, then install** (lets you inspect `install.sh` and pin a release tag):

```bash
git clone https://github.com/AI-Marketing-Hub/claude-blog.git
cd claude-blog
git checkout v1.9.0          # pin to a release tag (latest as of 2026-05-18)
chmod +x install.sh && ./install.sh
```

**One-Command Install (Unix/macOS):**

```bash
curl -fsSL https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.sh | bash
```

**One-Command Install (Windows PowerShell):**

```powershell
irm https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.ps1 | iex
```

> Piping `curl` or `irm` to a shell gives the script execution authority on your machine. The clone-then-checkout-tag flow is safer because you can inspect what runs. Both flows authenticate against the private repo using your existing `gh auth` / GitHub credentials.

**Verify installer integrity (recommended, VULN-IAC-001 hardening):**

```bash
# Download, verify SHA-256, then run if the hash matches.
curl -fsSL -o install.sh https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.sh
echo "029388e448dd29bed259b130c2be42e2f6a16d4d5b6801a61bfb4f49b621fc04  install.sh" | sha256sum -c
bash install.sh
```

The SHA-256 above is for the current `install.sh` at HEAD on `main`. Verify against [the canonical file](https://github.com/AI-Marketing-Hub/claude-blog/blob/main/install.sh) before running. The `install.ps1` companion hash is `6d03f353e5d844c4fe5c7c0b2500bd1e2aad02468cd544013bab876735cebf98`. Hashes are updated in this README on every installer change.

Restart Claude Code after installation to activate.

## Commands

> 🚀 **First time? Try these three commands first**: `/blog strategy <niche>` to scope your blog, `/blog write <topic>` to generate your first article (the 5-gate contract runs automatically), and `/blog analyze <file>` to score it on the 100-point rubric.

<p align="center">
  <img src="assets/blog-write-demo.gif" alt="claude-blog /blog write demo: end-to-end article generation with the 5-gate Delivery Contract" width="100%">
</p>

<p align="center">
  <img src="assets/diagrams/03-sub-skill-map-B.svg" alt="claude-blog sub-skill ecosystem: orchestrator hub at the center with 30 sub-skills organized into 8 thematic clusters (writing, strategy, quality, AI and search, multilingual, research, media, distribution); panel sizes auto-scale to skill counts" width="100%">
</p>

| Command | Description |
|---------|-------------|
| `/blog write <topic>` | Write a new blog post from scratch |
| `/blog rewrite <file>` | Optimize an existing blog post |
| `/blog analyze <file>` | Quality audit with 0-100 score |
| `/blog brief <topic>` | Generate a detailed content brief |
| `/blog calendar` | Generate an editorial calendar |
| `/blog strategy <niche>` | Blog strategy and topic ideation |
| `/blog outline <topic>` | SERP-informed content outline |
| `/blog seo-check <file>` | Post-writing SEO validation |
| `/blog schema <file>` | Generate JSON-LD schema markup |
| `/blog repurpose <file>` | Repurpose for social, email, YouTube |
| `/blog geo <file>` | AI citation readiness audit |
| `/blog image [generate\|edit\|setup]` | AI image generation via Gemini |
| `/blog audit [directory]` | Full-site blog health assessment |
| `/blog cannibalization [directory]` | Detect keyword overlap across posts |
| `/blog factcheck <file>` | Verify statistics against cited sources |
| `/blog persona [create\|list\|apply]` | Manage writing personas and voice profiles |
| `/blog taxonomy [sync\|audit\|suggest]` | Tag/category CMS management |
| `/blog notebooklm <question>` | Query NotebookLM for source-grounded research |
| `/blog audio [generate\|voices\|setup]` | Generate audio narration via Gemini TTS |
| `/blog google [command] [args]` | Google API data: PSI, CrUX, GSC, GA4, NLP, YouTube, Keywords |
| `/blog cluster [plan\|execute] <seed>` | Semantic topic-cluster planning + execution (hub-and-spoke) |
| `/blog multilingual <topic> --languages <codes>` | Write, translate, localize, and emit hreflang in one command |
| `/blog translate <file> --to <codes>` | SEO-optimized translation with format preservation |
| `/blog localize <file> --locale <code>` | Cultural deep-adaptation per locale |
| `/blog locale-audit <directory>` | Multilingual content QA (completeness, hreflang, parity, freshness) |
| `/blog flow [find\|optimize\|win\|prompts\|sync]` | FLOW framework prompts (evidence-led, 30 blog-applicable) |
| `/blog brand [init\|show\|update]` | Generate BRAND.md + VOICE.md context auto-loaded by all sub-skills |
| `/blog discourse <topic>` | API-free last-30-days discourse research; produces DISCOURSE.md |

> **30 sub-skill directories total**: 29 user-invokable (28 distinct slash commands + `/blog update` aliased to rewrite) + 1 internal-only (`blog-chart`, invoked by blog-write/blog-rewrite for inline SVG charts). `blog-image` is user-invokable AND callable internally.

## How does claude-blog compare?

claude-blog is a structured pipeline. Direct LLM prompting is a one-shot. Hosted SaaS tools are closed-source. Here is the honest tradeoff matrix:

| Capability | claude-blog | Direct Claude / ChatGPT prompt | Copy.ai / Jasper | Build it yourself |
|---|:---:|:---:|:---:|:---:|
| Full article in one command, with iteration loop | ✅ (5-gate contract, up to 3 retries) | ⚠️ one-shot | ✅ | ❌ |
| Sourced statistics with verification | ✅ `/blog factcheck` fetches source URLs | ❌ hallucinates | ❌ | ⚠️ manual |
| AI citation optimization (GEO / AEO) | ✅ dedicated `/blog geo` audit | ❌ | ❌ | ⚠️ |
| Blocking content review (score >= 90 to deliver) | ✅ `blog-reviewer` agent | ❌ | ❌ | ❌ |
| Multilingual + hreflang one-command | ✅ `/blog multilingual` | ⚠️ no hreflang | ⚠️ | ❌ |
| Topic-cluster planning (hub-and-spoke) | ✅ `/blog cluster` | ❌ | ⚠️ | ❌ |
| Audio narration | ✅ Gemini TTS, 30 voices | ❌ | ❌ | ❌ |
| Hero image generation (4-step ladder) | ✅ Banana, Gemini, stock, Openverse | ❌ | ⚠️ stock only | ⚠️ |
| Persistent brand and voice context | ✅ BRAND.md + VOICE.md auto-loaded | ❌ per-prompt | ⚠️ limited | ❌ |
| Open-source, MIT, no usage cost | ✅ free | ❌ subscription | ❌ subscription | ✅ |

claude-blog is not better at everything. Direct prompting is faster for a single throwaway draft. Hosted SaaS is easier for non-developers. DIY is more flexible for unique pipelines. claude-blog fits where you want production-grade content at scale without a SaaS subscription.

## Features

### 12 content templates
Auto-selected by topic and intent: how-to guide, listicle, case study, comparison, pillar page, product review, thought leadership, roundup, tutorial, news analysis, data research, FAQ knowledge base.

### 5-category quality scoring (100 points)
| Category | Points | Focus |
|----------|--------|-------|
| Content Quality | 30 | Depth, readability, originality, engagement |
| SEO Optimization | 25 | Headings, title, keywords, links, meta |
| E-E-A-T Signals | 15 | Author, citations, trust, experience |
| Technical Elements | 15 | Schema, images, speed, mobile, OG tags |
| AI Citation Readiness | 15 | Citability, Q&A format, entity clarity |

Scoring bands: Exceptional (90-100), Strong (80-89), Acceptable (70-79), Below Standard (60-69), Rewrite (<60). The v1.9.0 contract blocks delivery below 90.

### AI content detection
Burstiness scoring on sentence-length variance, known AI-phrase detection (17 phrases), and vocabulary diversity (TTR). Flags content that reads as machine-generated before it reaches the reviewer.

### Persona-driven writing
Configurable writing personas with the NNGroup 4-dimension tone framework (formal/casual, serious/funny, respectful/irreverent, matter-of-fact/enthusiastic). Manage voice profiles per blog or author, with readability bands (Consumer, Professional, Technical) and style enforcement at draft time.

### Fact-checking pipeline
`/blog factcheck` fetches every cited source URL and scores claim confidence as exact match, paraphrase, or not found. Ensures every data point is accurate and traceable, not invented.

### Keyword cannibalization detection
`/blog cannibalization` identifies keyword overlap across blog posts using local grep analysis or DataForSEO API. Severity scoring with merge or differentiate recommendations prevents posts from competing against each other in SERPs.

### CMS taxonomy management
Tag and category sync supporting WordPress REST, Shopify GraphQL, Ghost, Strapi, and Sanity. Includes tag suggestion, sync, and audit workflows.

### Dual optimization
Every article targets both Google rankings and AI citation platforms:
- **Google**: December 2025 Core Update compliance, E-E-A-T signals, schema markup, internal linking, Core Web Vitals awareness via blog-google.
- **AI Citations**: Answer-first formatting, citation capsules, passage-level citability (120-180 word blocks), FAQ schema, entity clarity.

### Visual media
- Pixabay, Unsplash, and Pexels image sourcing with HTTP 200 verification and auto-generated alt text.
- AI image generation via Gemini for hero images, inline illustrations, and social cards. Requires a free Google AI API key.
- Built-in SVG chart generation in 7 styles (bar, grouped bar, lollipop, donut, line, area, radar).
- YouTube video embedding with `srcdoc` lazy loading and noscript AI-crawler fallback.
- Image density targets calibrated per content type.

### Google API integration (v1.6.5+)
13 commands across 4 credential tiers, all free at normal usage:
- **Tier 0** (API key): PageSpeed Insights, CrUX Core Web Vitals (25-week history), YouTube video search, NLP entity analysis.
- **Tier 1** (OAuth): Search Console performance, URL Inspection, Indexing API.
- **Tier 2** (GA4): Organic traffic reports.
- **Tier 3** (Ads): Google Ads Keyword Planner.

### NotebookLM research
Query Google NotebookLM for source-grounded research from user-uploaded documents. Tier 1 data quality with zero hallucination risk because the answers are extracted from documents you uploaded.

### Audio narration
`/blog audio` generates audio narration via Gemini TTS. Three modes: summary (200-300 words), full article, two-speaker dialogue. 30 voices, 80+ languages.

### Platform support
Next.js MDX, Astro, Hugo, Jekyll, WordPress, Ghost, 11ty, Gatsby, and static HTML.

### Foundational methodologies (v1.8.0)
Five reference documents under `skills/blog/references/` define the editorial and research methodology applied across all sub-skills. They are loaded on demand by the orchestrator:

| Reference | Purpose | Used by |
|---|---|---|
| `ai-slop-detection.md` | Two-tier first-order (phrases) + second-order (structural rhythm) AI-content detection | `blog-rewrite`, `blog-reviewer`, `blog-analyze` |
| `editorial-heuristics.md` | 10 Nielsen-adapted heuristics with 0-4 scoring + P0-P3 severity tagging | `blog-analyze --rubric` |
| `cognitive-load.md` | Per-section concept-density (entities, numerics, jargon, forward refs, clause depth) | `blog-analyze --cognitive-load`, `scripts/cognitive_load.py` |
| `research-quality.md` | 5-dimension research rubric + 4 pre-flight keyword-trap classes + freshness floors | `blog-researcher`, `blog-discourse`, `blog-brief`, `blog-strategy` |
| `synthesis-contract.md` | 6 LAWs governing research synthesis (no trailing Sources block, inline citations, etc.) | All research-synthesis sub-skills |

Adapted from `pbakaus/impeccable` (Apache 2.0) and `mvanhorn/last30days-skill` (MIT). See [`CONTRIBUTORS.md`](CONTRIBUTORS.md) for attribution.

### FLOW framework

The FLOW framework (Find, Leverage, Optimize, Win) is the evidence-led workflow shared with [`AgriciDaniel/flow`](https://github.com/AgriciDaniel/flow) (CC BY 4.0). Each phase contributes prompts to the orchestrator pipeline; `/blog flow` exposes 30 ready-to-run prompts indexed by phase.

<p align="center">
  <img src="assets/diagrams/04-framework-B.svg" alt="FLOW framework radial wheel: four phases (Find for topic discovery, Leverage for asset amplification, Optimize for content improvement, Win for reader conversion) arranged around a central hub, with 10 representative prompts on the outer ring" width="100%">
</p>

## Delivery contract (v1.9.0)

<p align="center">
  <img src="assets/diagrams/02-pipeline-A.svg" alt="5-gate Blog Delivery Contract pipeline: Capability Discovery, Format Completeness, Visual Verification, Content Review (BLOCKING gate, score must be 90 or higher with zero P0 issues), and Asset and Link Integrity. Iterates up to 3 times on failure before escalating to the user" width="100%">
</p>

Every blog passes a 5-gate contract before being shown to the user. The user is never the first reviewer; the gates are.

| Gate | Enforces | Implementation |
|---|---|---|
| 1. Capability Discovery | Required tools and agents present before write | `scripts/blog_preflight.py --gate 1` |
| 2. Format Completeness | `.md` + `.html` + `.pdf` + real hero image | `scripts/blog_render.py`, `scripts/generate_hero.py` |
| 3. Visual Verification | No SVG overflow, valid JSON-LD, dark mode renders correctly | `patchright` / `playwright` at 3 viewport widths |
| 4. Content Review (BLOCKING) | `blog-reviewer` score 90+ AND zero P0 issues | `agents/blog-reviewer.md` (blocking, v1.9.0) |
| 5. Asset + Link Integrity | Every img resolves, og:image exists, links return 200, wordCount within 5% | `scripts/blog_preflight.py --gate 5` |

Hero image ladder: Banana MCP, direct Gemini API, premium stock (Unsplash, Pexels, Pixabay), Openverse public API. First available wins. Block-and-iterate up to 3 times on any gate failure before escalating to the user. Full spec: [`skills/blog/references/blog-delivery-contract.md`](skills/blog/references/blog-delivery-contract.md).

## Architecture

<p align="center">
  <img src="assets/diagrams/01-architecture-B.svg" alt="claude-blog system architecture: left-to-right pipeline from user command through orchestrator routing, sub-skill execution, and agent dispatch to the 5-gate delivery contract before reaching the user" width="100%">
</p>

claude-blog ships as one orchestrator plus 29 sub-skills, 5 agents, 21 references, 12 templates, and 9 root-level scripts. The orchestrator routes user commands to sub-skills, which spawn agents and call scripts via Bash.

| Layer | Count | Where |
|---|---:|---|
| Sub-skills (user-invokable) | 29 | `skills/blog-*/SKILL.md` |
| Sub-skills (internal) | 1 | `skills/blog-chart/SKILL.md` |
| Specialized agents | 5 | `agents/blog-*.md` |
| On-demand references | 21 | `skills/blog/references/*.md` |
| Content templates | 12 | `skills/blog/templates/*.md` |
| Root-level Python scripts | 9 | `scripts/*.py` |
| Tests | 160 | `tests/test_*.py` |

Full directory tree, data flow diagrams, scoring methodology, and extension points: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed and configured.
- Python 3.11+ (for quality scoring, the 5-gate delivery contract runners, and lint).
- Optional: `pip install -r requirements.txt` for advanced analysis (readability scoring, schema detection).

### Quality gates (CI-enforced on every PR)

1. **pytest**: 160 tests across security, behavioral, regression, and delivery-contract suites.
2. **Plugin validation**: `claude plugin validate .` plus hand-rolled JSON/regex checks.
3. **Stale-path lint**: catches drift in `references/` and `templates/` cross-references.
4. **Prose hygiene**: `scripts/lint_prose.py` (fence-aware, backtick-aware) enforces the CONTRIBUTING.md no-em-dash, no-en-dash, no-` -- ` rule.
5. **Version coherence**: `tests/test_version_coherence.py` asserts `pyproject.toml`, `plugin.json`, `CITATION.cff`, and `skills/blog/SKILL.md` frontmatter all match.
6. **Command coherence**: `tests/test_command_coherence.py` asserts `skills/blog/SKILL.md` and `docs/COMMANDS.md` declare the same command set.

Run locally before pushing:
```bash
python -m pytest tests/
python3 scripts/lint_prose.py
claude plugin validate .
```

## Frequently Asked Questions

### What is claude-blog?
claude-blog is a Claude Code skill suite for writing, optimizing, and auditing blog content. It runs 30 sub-skills and 5 agents through a 5-gate delivery contract so that every article meets a 90/100 quality bar before it reaches you.

### How is claude-blog different from prompting Claude or ChatGPT directly?
Direct prompting gives you one draft from one prompt. claude-blog gives you a structured pipeline: research with sourced statistics, outline approval, draft generation, multi-pass quality scoring, AI-content detection, fact verification, schema injection, and a blocking review that iterates up to 3 times before delivery. The skill enforces what a senior editor would otherwise do manually.

### Do I need an AI Marketing Hub Pro membership to use claude-blog?
No. The public open-source version at [`AgriciDaniel/claude-blog`](https://github.com/AgriciDaniel/claude-blog) is MIT-licensed and free for anyone with Claude Code. The private mirror at `AI-Marketing-Hub/claude-blog` is for Pro members who want early access to in-development features and direct collaboration with the community.

### What blog platforms does claude-blog support?
Next.js MDX, Astro, Hugo, Jekyll, WordPress, Ghost, 11ty, Gatsby, and static HTML. The orchestrator auto-detects the platform from project signals and adjusts frontmatter, image embedding, and schema injection accordingly.

### Does claude-blog hallucinate statistics?
No. Every cited statistic flows through `/blog factcheck`, which fetches the source URL and scores the claim confidence (exact match, paraphrase, not found). The `blog-reviewer` agent blocks publication if a citation cannot be verified or if AI-content detection flags the prose as machine-generated.

### What is the 5-gate Blog Delivery Contract?
A code-enforced pre-presentation pipeline that runs on every draft: Capability Discovery, Format Completeness, Visual Verification at 3 viewport widths, Content Review (BLOCKING; score 90+ and zero P0), and Asset + Link Integrity. The orchestrator iterates the writer up to 3 times on any gate failure before escalating to you. Full spec in [`skills/blog/references/blog-delivery-contract.md`](skills/blog/references/blog-delivery-contract.md).

### Can I use claude-blog in multiple languages?
Yes. `/blog multilingual <topic> --languages en,de,fr,es,ja` writes the post, translates it preserving frontmatter and schema, runs cultural deep-adaptation per locale, and emits hreflang tags plus a CMS-ready language map in a single command.

### How do I cite claude-blog in academic work?
See the [How to cite](#how-to-cite) section below or the [`CITATION.cff`](CITATION.cff) file in the repo root. GitHub surfaces the structured citation file via the "Cite this repository" button on the public mirror page.

### Is claude-blog secure to install?
The installer ships only Python scripts and markdown files, never executes remote code beyond what `pip install -r requirements.txt` brings in, and is reviewed against the project [`SECURITY.md`](SECURITY.md) policy on every change. The clone-then-checkout-tag install flow lets you inspect `install.sh` before running it. See [`SECURITY.md`](SECURITY.md) for the full threat model.

## Roadmap

<p align="center">
  <img src="assets/diagrams/05-roadmap-A.svg" alt="claude-blog wave roadmap on a horizontal timeline: v1.6.0 foundation (Mar 2026), v1.7.0 FLOW framework (Apr 2026), v1.8.0 impeccable methodology (May 2026), v1.9.0 delivery contract (current, May 2026), v2.0.0 multi-CMS publishing (Q3 2026), v3.0.0 blog-as-code (Q1 2027)" width="100%">
</p>

**v1.9.1 (next)**
- Shared `_count_body_words(html)` function between `blog_render` and `blog_preflight` to close the v1.9.0 audit residual.
- `generate_hero.py` exit-code semantics: non-zero on no-image-gen-path (currently returns JSON error with exit 0).
- Iteration-loop coverage test verifying the orchestrator escalates after 3 reviewer BLOCKS, not 4.
- Sweep remaining docs (CONTRIBUTORS, NOTICE, SECURITY, PRIVACY, TEMPLATES, TROUBLESHOOTING, MCP-INTEGRATION, DEMO) for any residual v1.x stratum drift.

**v1.10 (vision)**
- Live SERP-informed outline refinement via DataForSEO mid-write.
- Eval harness measuring blog quality across configurations (BRAND.md presence, persona variant, multilingual mode).
- Code-enforced iteration counter (currently orchestrator-instruction; promote to script-level).

**v2.0 (long-term)**
- Headless preview server integration: the 5-gate contract runs against a real domain preview instead of local HTML.
- Per-platform CMS publishing connectors (WordPress, Ghost, Sanity) with idempotent re-publish on rewrite.
- Real-time AI-citation tracking dashboard (which posts get cited by ChatGPT, Perplexity, AI Overviews; visibility heatmap).

Open an issue with the `roadmap` label if you want to propose or vote on something.

## Uninstall

Unix/macOS:
```bash
chmod +x uninstall.sh && ./uninstall.sh
```

Windows (PowerShell):
```powershell
.\uninstall.ps1
```

## Integration

Chart generation and YouTube video embedding are built-in. Google API data requires a free API key (see `/blog google setup`).

**Optional companion skills** (deeper analysis of published pages):

| Skill | Integration |
|-------|-------------|
| `/seo` | Deep SEO analysis of published blog pages |
| `/seo-schema` | Schema markup validation and generation |
| `/seo-geo` | AI citation optimization audit |
| `/seo-google` | Google API data (shared config with blog-google) |

## Documentation

Detailed documentation is in [`docs/`](docs/):

- [Installation Guide](docs/INSTALLATION.md): Unix, macOS, Windows, manual install.
- [Command Reference](docs/COMMANDS.md): Full command reference with examples.
- [Architecture](docs/ARCHITECTURE.md): System design and component overview.
- [Publishing Workflow](docs/PUBLISHING.md): Private-to-public release flow (Pro maintainers).
- [Templates](docs/TEMPLATES.md): Template reference and customization.
- [Troubleshooting](docs/TROUBLESHOOTING.md): Common issues and fixes.
- [MCP Integration](docs/MCP-INTEGRATION.md): Optional MCP server setup.

## How to cite

If you use claude-blog in research or production, please cite the project:

```bibtex
@software{Agrici_claude_blog_2026,
  author       = {Agrici, Daniel},
  title        = {claude-blog: AI Blog Writing and SEO Optimization Skill for Claude Code},
  year         = {2026},
  url          = {https://github.com/AgriciDaniel/claude-blog},
  version      = {1.9.0},
  license      = {MIT}
}
```

GitHub also surfaces the structured [`CITATION.cff`](CITATION.cff) file via "Cite this repository" on the public mirror page.

## Security & Code of Conduct

- **Security policy + threat model**: [`SECURITY.md`](SECURITY.md). v1.8.x hardening pass closed every known finding; v1.9.0 adds XSS-safe JSON-LD, O_NOFOLLOW symlink refusal, and frontmatter validation, all mutation-test verified. To report a vulnerability privately, follow the disclosure procedure in [`SECURITY.md`](SECURITY.md).
- **Code of Conduct**: [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). Contributor Covenant. Be excellent to each other.

## Contributing

Contributions welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines. Before opening a PR:

1. Run `python -m pytest tests/` (all 160 must pass).
2. Run `python3 scripts/lint_prose.py --root .` (zero violations).
3. Run `claude plugin validate .` (must pass).
4. Bump versions coherently if you touch user-visible counts or behavior (see [`docs/PUBLISHING.md`](docs/PUBLISHING.md)).

## License

MIT License. See [`LICENSE`](LICENSE) for details.

## Related projects

- **[Rankenstein](https://rankenstein.pro)**: GUI-based content publishing workflow; research to publish in one platform.
- **[FLOW framework](https://github.com/AgriciDaniel/flow)**: Evidence-led Find, Optimize, Win prompts (CC BY 4.0). Integrated as a sub-skill via `/blog flow`.
- **[Claude Ads](https://github.com/AgriciDaniel/claude-ads)** and **[Claude SEO](https://github.com/AgriciDaniel/claude-seo)**: sibling skills sharing the same brand kit (banner + diagrams generated with the brand-orange palette).
- **[AI Marketing Hub](https://www.skool.com/ai-marketing-hub)**: Free community, 2,800+ members. Pro tier at [`ai-marketing-hub-pro`](https://www.skool.com/ai-marketing-hub-pro) hosts this skill's private mirror.

## Star history

<a href="https://star-history.com/#AgriciDaniel/claude-blog&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=AgriciDaniel/claude-blog&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=AgriciDaniel/claude-blog&type=Date" />
    <img alt="Star history of AgriciDaniel/claude-blog on GitHub" src="https://api.star-history.com/svg?repos=AgriciDaniel/claude-blog&type=Date" />
  </picture>
</a>

If claude-blog saves you time, a star on the [public repo](https://github.com/AgriciDaniel/claude-blog) is the easiest way to say thanks (and helps other content folks find it).

## Author

Built by [Daniel Agrici](https://agricidaniel.com/about), AI Workflow Architect, with Claude Code.

- [Blog](https://agricidaniel.com/blog): Deep dives on AI marketing automation.
- [YouTube](https://www.youtube.com/@AgriciDaniel): Tutorials and demos.
- [All open-source tools](https://github.com/AgriciDaniel): Other Claude Code skills.
- [AI Marketing Hub](https://www.skool.com/ai-marketing-hub): Free community for AI-powered marketing.
