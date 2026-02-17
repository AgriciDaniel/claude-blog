# claude-blog

A Claude Code skill ecosystem for blog content creation, optimization, and management. Dual-optimized for Google rankings (December 2025 Core Update, E-E-A-T) and AI citation platforms (GEO/AEO).

## What It Does

`claude-blog` provides a complete blog lifecycle through Claude Code slash commands:

| Command | Description |
|---------|-------------|
| `/blog write <topic>` | Write a new blog post from scratch |
| `/blog rewrite <file>` | Optimize an existing blog post |
| `/blog analyze <file>` | Audit blog quality with a 0-100 score |
| `/blog brief <topic>` | Generate a detailed content brief |
| `/blog calendar` | Generate an editorial calendar |
| `/blog strategy <niche>` | Blog strategy and topic ideation |

Every article follows 6 optimization pillars: answer-first formatting, sourced statistics, visual media (Pixabay/Unsplash images + SVG charts), FAQ schema, content structure, and freshness signals.

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed and configured
- Python 3.12+ (for the `analyze_blog.py` quality scoring script)

## Installation

Run the installer to copy skills, agents, references, and scripts to your Claude Code configuration:

```bash
chmod +x install.sh
./install.sh
```

This installs to:
- `~/.claude/skills/blog/` — Main skill + references
- `~/.claude/skills/blog-*/` — 6 sub-skills
- `~/.claude/agents/` — 2 specialized agents
- `~/.claude/skills/blog/scripts/` — Quality analysis script

Restart Claude Code after installation to activate.

## Project Structure

```
claude-blog/
├── blog/
│   ├── SKILL.md                    # Main orchestrator skill
│   └── references/
│       ├── content-rules.md        # Structure, readability, answer-first formatting
│       ├── geo-optimization.md     # GEO/AEO techniques, AI citation factors
│       ├── quality-scoring.md      # Full scoring checklist (100 points)
│       ├── seo-2026.md             # Google updates, E-E-A-T, algorithm changes
│       └── visual-media.md         # Image sourcing + SVG chart integration
├── skills/
│   ├── blog-analyze/SKILL.md       # Quality audit & 0-100 scoring
│   ├── blog-brief/SKILL.md         # Content brief generation
│   ├── blog-calendar/SKILL.md      # Editorial calendar planning
│   ├── blog-rewrite/SKILL.md       # Existing post optimization
│   ├── blog-strategy/SKILL.md      # Blog positioning & architecture
│   └── blog-write/SKILL.md         # New article generation
├── agents/
│   ├── blog-researcher.md          # Research agent (stats, images, competition)
│   └── blog-writer.md              # Content writing agent
├── scripts/
│   └── analyze_blog.py             # Python quality analysis tool
├── install.sh                      # Installer script
├── LICENSE
└── README.md
```

## Quality Scoring

Blog posts are scored across 6 categories (100 points total):

| Category | Weight | What It Measures |
|----------|--------|-----------------|
| Content Quality | 25 pts | Readability, paragraph length, information gain |
| Answer-First Formatting | 20 pts | Stat-first H2 openers, direct answers |
| Statistics & Citations | 20 pts | Source count, tier quality, attribution |
| Visual Elements | 15 pts | Image count, chart diversity, distribution |
| Schema & Structure | 10 pts | FAQ schema, heading hierarchy |
| Freshness & Trust | 10 pts | Update date, author E-E-A-T, brand mentions |

## Integration

Works with the broader Claude Code skill ecosystem:

- `/svg` or `/svg-chart` — Generate dark-mode SVG data visualizations
- `/seo` — Deep SEO analysis of published blog pages
- `/seo-schema` — Schema markup validation and generation
- `/seo-geo` — AI citation optimization audit

## License

MIT License. See [LICENSE](LICENSE) for details.
