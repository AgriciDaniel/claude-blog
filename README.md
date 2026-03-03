# gemini-blog

![Gemini Blog вЂ” AI-Powered Blog Creation](assets/header.jpeg)

![Gemini CLI Skill](https://img.shields.io/badge/Gemini_Code-Skill-blueviolet)
![License: MIT](https://img.shields.io/badge/License-MIT-green)
![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue)
![Sub-Skills](https://img.shields.io/badge/Sub--Skills-13-orange)

**The most comprehensive blog creation skill for Gemini CLI.**

Strategy, briefs, calendars, writing, optimization, schema, repurposing, and full-site audits вЂ” all from slash commands. Dual-optimized for Google rankings and AI citation platforms (ChatGPT, Perplexity, AI Overviews).

### [Watch the Demo](https://www.youtube.com/watch?v=AeLC4iutG8w)

![Blog commands demo](assets/blog-command-demo.gif)
---

## Quick Start

One-command install (Unix/macOS):

```bash
curl -fsSL https://raw.githubusercontent.com/imitry/gemini-blog/main/install.sh | bash
```

Or clone and install manually:

```bash
git clone https://github.com/imitry/gemini-blog.git
cd gemini-blog
chmod +x install.sh && ./install.sh
```

Windows (PowerShell):
```powershell
.\install.ps1
```

Restart Gemini CLI after installation to activate.

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
gemini-blog/
в”њв”Ђв”Ђ blog/
в”‚   в”њв”Ђв”Ђ GEMINI.md                        # Main orchestrator (12 commands)
в”‚   в”њв”Ђв”Ђ references/                     # 12 on-demand reference docs
в”‚   в”‚   в”њв”Ђв”Ђ google-landscape-2026.md
в”‚   в”‚   в”њв”Ђв”Ђ geo-optimization.md
в”‚   в”‚   в”њв”Ђв”Ђ content-rules.md
в”‚   в”‚   в”њв”Ђв”Ђ visual-media.md
в”‚   в”‚   в”њв”Ђв”Ђ quality-scoring.md
в”‚   в”‚   в”њв”Ђв”Ђ platform-guides.md
в”‚   в”‚   в”њв”Ђв”Ђ distribution-playbook.md
в”‚   в”‚   в”њв”Ђв”Ђ content-templates.md
в”‚   в”‚   в”њв”Ђв”Ђ eeat-signals.md
в”‚   в”‚   в”њв”Ђв”Ђ ai-crawler-guide.md
в”‚   в”‚   в”њв”Ђв”Ђ schema-stack.md
в”‚   в”‚   в””в”Ђв”Ђ internal-linking.md
в”‚   в””в”Ђв”Ђ templates/                      # 12 content type templates
в”‚       в”њв”Ђв”Ђ how-to-guide.md
в”‚       в”њв”Ђв”Ђ listicle.md
в”‚       в”њв”Ђв”Ђ case-study.md
в”‚       в”њв”Ђв”Ђ comparison.md
в”‚       в”њв”Ђв”Ђ pillar-page.md
в”‚       в”њв”Ђв”Ђ product-review.md
в”‚       в”њв”Ђв”Ђ thought-leadership.md
в”‚       в”њв”Ђв”Ђ roundup.md
в”‚       в”њв”Ђв”Ђ tutorial.md
в”‚       в”њв”Ђв”Ђ news-analysis.md
в”‚       в”њв”Ђв”Ђ data-research.md
в”‚       в””в”Ђв”Ђ faq-knowledge.md
в”њв”Ђв”Ђ skills/                             # 13 sub-skills
в”‚   в”њв”Ђв”Ђ blog-write/GEMINI.md
в”‚   в”њв”Ђв”Ђ blog-rewrite/GEMINI.md
в”‚   в”њв”Ђв”Ђ blog-analyze/GEMINI.md
в”‚   в”њв”Ђв”Ђ blog-brief/GEMINI.md
в”‚   в”њв”Ђв”Ђ blog-calendar/GEMINI.md
в”‚   в”њв”Ђв”Ђ blog-strategy/GEMINI.md
в”‚   в”њв”Ђв”Ђ blog-outline/GEMINI.md
в”‚   в”њв”Ђв”Ђ blog-seo-check/GEMINI.md
в”‚   в”њв”Ђв”Ђ blog-schema/GEMINI.md
в”‚   в”њв”Ђв”Ђ blog-repurpose/GEMINI.md
в”‚   в”њв”Ђв”Ђ blog-geo/GEMINI.md
в”‚   в”њв”Ђв”Ђ blog-audit/GEMINI.md
в”‚   в””в”Ђв”Ђ blog-chart/GEMINI.md            # Internal: SVG chart generation
в”њв”Ђв”Ђ agents/                             # 4 specialized agents
в”‚   в”њв”Ђв”Ђ blog-researcher.md
в”‚   в”њв”Ђв”Ђ blog-writer.md
в”‚   в”њв”Ђв”Ђ blog-seo.md
в”‚   в””в”Ђв”Ђ blog-reviewer.md
в”њв”Ђв”Ђ scripts/
в”‚   в””в”Ђв”Ђ analyze_blog.py                 # Python quality analysis (5-category scoring)
в”њв”Ђв”Ђ docs/                               # 6 documentation files
в”‚   в”њв”Ђв”Ђ INSTALLATION.md
в”‚   в”њв”Ђв”Ђ COMMANDS.md
в”‚   в”њв”Ђв”Ђ ARCHITECTURE.md
в”‚   в”њв”Ђв”Ђ TEMPLATES.md
в”‚   в”њв”Ђв”Ђ TROUBLESHOOTING.md
в”‚   в””в”Ђв”Ђ MCP-INTEGRATION.md
в”њв”Ђв”Ђ assets/                             # Images and demo GIFs
в”‚   в”њв”Ђв”Ђ header.jpeg
в”‚   в”њв”Ђв”Ђ blog-write-demo.gif
в”‚   в””в”Ђв”Ђ blog-command-demo.gif
в”њв”Ђв”Ђ install.sh                          # Unix/macOS installer
в”њв”Ђв”Ђ install.ps1                         # Windows PowerShell installer
в”њв”Ђв”Ђ uninstall.sh                        # Unix/macOS uninstaller
в”њв”Ђв”Ђ uninstall.ps1                       # Windows PowerShell uninstaller
в”њв”Ђв”Ђ requirements.txt                    # Python dependencies
в”њв”Ђв”Ђ CHANGELOG.md
в”њв”Ђв”Ђ TODO.md
в”њв”Ђв”Ђ LICENSE
в””в”Ђв”Ђ README.md
```

## Requirements

- [Gemini CLI](https://geminicli.com/docs/) CLI installed and configured
- Python 3.12+ (for `analyze_blog.py` quality scoring script)
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

Chart generation is built-in вЂ” no external dependencies required for full functionality.

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

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License. See [LICENSE](LICENSE) for details.

---

Built by [imitry](https://github.com/imitry) with Gemini CLI.

Original author: [AgriciDaniel](https://github.com/AgriciDaniel). English version for Claude Code.

