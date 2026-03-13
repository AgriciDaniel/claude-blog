# claude-blog — AI Blog Creation Skill for Claude Code

![Claude Blog — AI-Powered Blog Creation](assets/header.jpeg)

[![CI](https://github.com/AgriciDaniel/claude-blog/actions/workflows/ci.yml/badge.svg)](https://github.com/AgriciDaniel/claude-blog/actions/workflows/ci.yml)
[![GitHub release](https://img.shields.io/github/v/release/AgriciDaniel/claude-blog)](https://github.com/AgriciDaniel/claude-blog/releases/latest)
![Claude Code Skill](https://img.shields.io/badge/Claude_Code-Skill-blueviolet)
![License: MIT](https://img.shields.io/badge/License-MIT-green)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)
![Sub-Skills](https://img.shields.io/badge/Sub--Skills-13-orange)

claude-blog is a Claude Code skill ecosystem for creating, optimizing, and managing blog content at scale. It generates complete articles, briefs, calendars, and schemas — dual-optimized for Google rankings and AI citation platforms (ChatGPT, Perplexity, AI Overviews).

## Table of Contents

- [Demo](#demo)
- [Quick Start](#quick-start)
- [Commands](#commands)
- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Uninstall](#uninstall)
- [Integration](#integration)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Demo

[Watch the Demo on YouTube](https://www.youtube.com/watch?v=AeLC4iutG8w)

![Blog commands demo](assets/blog-command-demo.gif)

---

## Quick Start

**One-command install (Unix/macOS):**

```bash
curl -fsSL https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.sh | bash
```

**Or clone and install manually:**

```bash
git clone https://github.com/AgriciDaniel/claude-blog.git
cd claude-blog
chmod +x install.sh && ./install.sh
```

**Windows (PowerShell):**
```powershell
.\install.ps1
```

Restart Claude Code after installation to activate.

## Commands
![Blog write command demo](assets/blog-write-demo.gif)
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
| `/blog audit [directory]` | Full-site blog health assessment |

> **13 sub-skills total**: 12 user-facing commands above + `blog-chart` (internal SVG generation, invoked automatically by other commands).

## Features

### 12 Content Templates
Auto-selected based on topic and intent: how-to guide, listicle, case study, comparison, pillar page, product review, thought leadership, roundup, tutorial, news analysis, data research, FAQ knowledge base.

### 5-Category Quality Scoring (100 Points)
| Category | Points | Focus |
|----------|--------|-------|
| Content Quality | 30 | Depth, readability, originality, engagement |
| SEO Optimization | 25 | Headings, title, keywords, links, meta |
| E-E-A-T Signals | 15 | Author, citations, trust, experience |
| Technical Elements | 15 | Schema, images, speed, mobile, OG tags |
| AI Citation Readiness | 15 | Citability, Q&A format, entity clarity |

Scoring bands: Exceptional (90-100), Strong (80-89), Acceptable (70-79), Below Standard (60-69), Rewrite (<60).

### AI Content Detection
Burstiness scoring, known AI phrase detection (17 phrases), vocabulary diversity analysis (TTR). Flags content that reads as AI-generated.

### Dual Optimization
Every article targets both Google rankings and AI citation platforms:
- **Google**: December 2025 Core Update compliance, E-E-A-T, schema markup, internal linking
- **AI Citations**: Answer-first formatting (+340% citations), citation capsules, passage-level citability, FAQ schema (+28% citations)

### Visual Media
- Pixabay/Unsplash/Pexels image sourcing with alt text
- Built-in SVG chart generation (bar, grouped bar, lollipop, donut, line, area, radar)
- Image density targets by content type
- Image URL verification (HTTP 200 check before embedding)

### Platform Support
Next.js/MDX, Astro, Hugo, Jekyll, WordPress, Ghost, 11ty, Gatsby, and static HTML.

## Architecture

```
claude-blog/
├── .claude-plugin/
│   └── plugin.json                     # Plugin metadata (name, description, author)
├── skills/
│   ├── blog/                           # Main orchestrator
│   │   ├── SKILL.md                    # Routes all 12 commands
│   │   ├── references/                 # 12 on-demand reference docs
│   │   └── templates/                  # 12 content type templates
│   ├── blog-write/SKILL.md            # Sub-skills (12 user-facing + 1 internal)
│   ├── blog-rewrite/SKILL.md
│   ├── blog-analyze/SKILL.md
│   ├── blog-brief/SKILL.md
│   ├── blog-calendar/SKILL.md
│   ├── blog-strategy/SKILL.md
│   ├── blog-outline/SKILL.md
│   ├── blog-seo-check/SKILL.md
│   ├── blog-schema/SKILL.md
│   ├── blog-repurpose/SKILL.md
│   ├── blog-geo/SKILL.md
│   ├── blog-audit/SKILL.md
│   └── blog-chart/SKILL.md            # Internal: SVG chart generation
├── agents/                             # 4 specialized agents
│   ├── blog-researcher.md
│   ├── blog-writer.md
│   ├── blog-seo.md
│   └── blog-reviewer.md
├── scripts/
│   └── analyze_blog.py                 # Python quality analysis (5-category scoring)
├── tests/                              # pytest test suite
│   ├── conftest.py
│   └── test_analyze_blog.py
├── docs/                               # 6 documentation files
├── .github/workflows/ci.yml           # CI pipeline
├── install.sh                          # Unix/macOS installer (fallback)
├── install.ps1                         # Windows PowerShell installer
├── pyproject.toml                      # Python project config
├── requirements.txt                    # Python dependencies
├── CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
└── README.md
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed and configured
- Python 3.11+ (for `analyze_blog.py` quality scoring script)
- Optional: `pip install -r requirements.txt` for advanced analysis (readability scoring, schema detection)

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

Chart generation is built-in — no external dependencies required for full functionality.

**Optional companion skills** (for deeper analysis of published pages):

| Skill | Integration |
|-------|-------------|
| `/seo` | Deep SEO analysis of published blog pages |
| `/seo-schema` | Schema markup validation and generation |
| `/seo-geo` | AI citation optimization audit |

## Documentation

Detailed documentation is available in [docs/](docs/):

- [Installation Guide](docs/INSTALLATION.md) -- Unix, macOS, Windows, manual install
- [Command Reference](docs/COMMANDS.md) -- Full 12-command reference with examples
- [Architecture](docs/ARCHITECTURE.md) -- System design and component overview
- [Templates](docs/TEMPLATES.md) -- Template reference and customization
- [Troubleshooting](docs/TROUBLESHOOTING.md) -- Common issues and fixes
- [MCP Integration](docs/MCP-INTEGRATION.md) -- Optional MCP server setup

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License. See [LICENSE](LICENSE) for details.

---

Built by [AgriciDaniel](https://github.com/AgriciDaniel) with Claude Code.
