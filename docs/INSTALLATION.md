# Installation Guide

This guide covers all installation methods for `claude-blog`, a Claude Code skill
ecosystem for blog content creation, optimization, and management.

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) | Latest | Runtime for all `/blog` commands |
| Python | 3.11+ | Quality scoring + 5-gate delivery contract runners (analyze_blog, blog_preflight, blog_render, generate_hero, lint_prose, ...) |
| pip | Latest | Python dependency management |

Claude Code must be installed and configured before installing `claude-blog`.
Python 3.11+ is required for quality scoring and helper workflows including
`analyze_blog.py`, `blog_preflight.py`, `blog_render.py`, `generate_hero.py`,
`lint_prose.py`, and related script checks. Commands that do not invoke those
helpers may still run without Python, but production installs should include it.

---

## Quick Install (One Command)

### Linux / macOS

```bash
curl -fsSLo install.sh https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.sh
chmod +x install.sh
./install.sh
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.ps1 -OutFile install.ps1
pwsh -File ./install.ps1
```

> Downloading either script before running it lets you inspect the exact bytes
> first and avoids direct download-to-execution pipelines. It also removes the
> PowerShell pattern reported in issue #33. See
> [SECURITY.md](../.github/SECURITY.md#antivirus-false-positives).

Both installers automatically copy all skills, agents, references, templates,
and scripts to the correct Claude Code configuration directories.

---

## Standard Install (Git Clone)

```bash
git clone https://github.com/AgriciDaniel/claude-blog.git
cd claude-blog
chmod +x install.sh
./install.sh
```

### Install Python Dependencies

The installers try to install Python packages from `requirements.txt` when
Python and pip are available. If dependency installation is skipped or fails,
run this after the main install:

```bash
python3 -m pip install -r requirements.txt
```

#### Reproducible install via uv (v1.9.1+)

For deterministic supply-chain hygiene, the repo ships `uv.lock` (142
packages with SHA-256 hashes for every wheel). Reproduce the exact
dev environment with:

```bash
pip install uv          # one-time
uv sync --frozen        # installs from uv.lock with hash verification
```

This is the recommended path for CI, audit, and any context where
"works on my machine" is not enough. The legacy `pip install -e ".[dev]"`
flow still works; it just resolves transitives freshly each time.

Regenerate `uv.lock` after editing `pyproject.toml` dependency bounds:

```bash
uv lock
```

**Core dependencies:**

| Package | Version | Purpose |
|---------|---------|---------|
| textstat | >=0.7.3 | Readability scoring (Flesch, Gunning Fog, SMOG) |
| beautifulsoup4 | >=4.12.0 | HTML and schema parsing |
| lxml | >=5.0.0 | XML/HTML parser backend |
| jsonschema | >=4.20.0 | JSON-LD schema validation |

**Optional dependencies** (unlock advanced features in `analyze_blog.py`):

```bash
pip install spacy                  # NER, advanced NLP
python -m spacy download en_core_web_sm
pip install sentence-transformers  # Semantic similarity / duplicate detection
pip install scikit-learn           # Topic cannibalization clustering
pip install language-tool-python   # Grammar and style checking (requires Java)
```

The analysis script works without optional dependencies by falling back to
basic mode automatically.

---

## Manual Install (File by File)

If you prefer not to run the installer, copy files to these paths manually.
`~` refers to your home directory (`$HOME` on Unix, `%USERPROFILE%` on Windows).

### Directory Structure

```
~/.claude/
├── skills/
│   ├── blog/
│   │   ├── SKILL.md                          # Main orchestrator
│   │   ├── references/
│   │   │   ├── content-rules.md
│   │   │   ├── geo-optimization.md
│   │   │   ├── google-landscape-2026.md
│   │   │   ├── quality-scoring.md
│   │   │   └── visual-media.md
│   │   ├── templates/                        # 12 content type templates
│   │   │   └── *.md
│   │   └── scripts/
│   │       └── analyze_blog.py
│   ├── blog-write/SKILL.md
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
│   ├── blog-chart/SKILL.md            # internal-only
│   ├── blog-image/SKILL.md            # v1.4.0
│   ├── blog-cannibalization/SKILL.md
│   ├── blog-factcheck/SKILL.md
│   ├── blog-persona/SKILL.md
│   ├── blog-taxonomy/SKILL.md
│   ├── blog-notebooklm/SKILL.md       # v1.5.0
│   ├── blog-audio/SKILL.md            # v1.6.0
│   ├── blog-google/SKILL.md           # v1.6.5
│   ├── blog-cluster/SKILL.md          # v1.7.0
│   ├── blog-flow/SKILL.md             # v1.7.0
│   ├── blog-multilingual/SKILL.md     # v1.7.0
│   ├── blog-translate/SKILL.md        # v1.7.0
│   ├── blog-localize/SKILL.md         # v1.7.0
│   ├── blog-locale-audit/SKILL.md     # v1.7.0
│   ├── blog-brand/SKILL.md            # v1.8.0
│   ├── blog-discourse/SKILL.md        # v1.8.0
│   ├── blog-style/SKILL.md            # v1.10.0
│   └── blog-decay/SKILL.md            # v1.10.0
└── agents/
    ├── blog-researcher.md
    ├── blog-writer.md
    ├── blog-seo.md
    ├── blog-reviewer.md
    └── blog-translator.md             # v1.7.0
```

### Copy Commands (Unix)

```bash
# Create directories. Auto-discover sub-skills via shell glob so we never
# fall behind on the directory list (v1.8.6: replaces the hand-rolled
# 14-skill mkdir from v1.4.0).
mkdir -p ~/.claude/skills/blog/{references,templates,scripts}
mkdir -p ~/.claude/scripts
for d in skills/blog-*/; do
    mkdir -p "${HOME}/.claude/skills/$(basename "$d")"
done
mkdir -p ~/.claude/agents

# Main skill
cp skills/blog/SKILL.md ~/.claude/skills/blog/SKILL.md

# References
cp -R skills/blog/references/. ~/.claude/skills/blog/references/

# Templates
cp -R skills/blog/templates/. ~/.claude/skills/blog/templates/

# Sub-skills plus their payload directories
for d in skills/blog-*/; do
    name=$(basename "$d")
    cp "$d/SKILL.md" "${HOME}/.claude/skills/$name/SKILL.md"
    for payload in references scripts assets templates; do
        if [ -d "$d/$payload" ]; then
            mkdir -p "${HOME}/.claude/skills/$name/$payload"
            cp -R "$d/$payload"/. "${HOME}/.claude/skills/$name/$payload/"
        fi
    done
    if [ -d "${HOME}/.claude/skills/$name/scripts" ]; then
        find "${HOME}/.claude/skills/$name/scripts" -type f -name '*.py' -exec chmod +x {} +
    fi
done

# Agents
cp agents/*.md ~/.claude/agents/

# Root scripts
for f in scripts/*.py; do
    name=$(basename "$f")
    cp "$f" "${HOME}/.claude/scripts/$name"
    chmod +x "${HOME}/.claude/scripts/$name"
    if [ "$name" = "analyze_blog.py" ]; then
        cp "$f" ~/.claude/skills/blog/scripts/analyze_blog.py
        chmod +x ~/.claude/skills/blog/scripts/analyze_blog.py
    fi
done
```

---

## Optional: AI Image Generation

`claude-blog` can generate custom blog images via Gemini AI (hero images, inline
illustrations, social cards). This requires the nanobanana-mcp server and a free
Google AI API key.

### Setup

```bash
# Get your free API key at: https://aistudio.google.com/apikey
python3 skills/blog-image/scripts/setup_image_mcp.py --key YOUR_KEY

# Verify setup
python3 skills/blog-image/scripts/validate_image_setup.py
```

### Requirements

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Node.js | 18+ | Runs `npx @ycse/nanobanana-mcp` |
| Google AI API key | Free tier | Image generation via Gemini |

Without this setup, all `/blog` commands work normally using stock photos from
Pixabay/Unsplash/Pexels. AI image generation is an optional enhancement.

---

## Verification

After installation, verify everything is in place:

### 1. Check installed files

```bash
# Main skill
ls ~/.claude/skills/blog/SKILL.md

# Blog-* directories should list 31; total is 32 skill directories (1 orchestrator + 31 sub-skills); 30 user-facing commands
ls ~/.claude/skills/blog-*/SKILL.md | wc -l

# Agents (should list 5: blog-researcher, blog-writer, blog-seo, blog-reviewer, blog-translator)
ls ~/.claude/agents/blog-*.md | wc -l

# References (should list 22 .md files)
ls ~/.claude/skills/blog/references/*.md | wc -l

# Python script
ls ~/.claude/skills/blog/scripts/analyze_blog.py
```

### 2. Restart Claude Code

Close and reopen Claude Code (or restart the CLI) to load the new skills:

```bash
# If running in terminal, exit and relaunch
claude
```

### 3. Test a command

```bash
# Inside Claude Code, run:
/blog strategy "home automation"
```

You should see the orchestrator route to the `blog-strategy` sub-skill and
begin gathering context about the niche.

### 4. Test the Python analysis script

```bash
python3 ~/.claude/skills/blog/scripts/analyze_blog.py --help
```

Expected output:

```
usage: analyze_blog.py [-h] [--output OUTPUT] [--batch] input

Analyze blog post quality

positional arguments:
  input                 Blog file path or directory (with --batch)

options:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output file path (JSON)
  --batch               Analyze all blog files in directory
```

---

## Updating

Pull the latest changes and re-run the installer:

```bash
cd claude-blog
git pull
./install.sh
```

The installer overwrites existing files, so updates are safe to run
at any time. Restart Claude Code after updating.

---

## Uninstall

### Automated Uninstall (Unix)

```bash
# From the claude-blog repository
chmod +x uninstall.sh
./uninstall.sh
```

This removes:

- `~/.claude/skills/blog/` and `~/.claude/skills/blog-*/` (32 skill directories: 1 orchestrator + 31 sub-skills; 30 user-facing commands; `blog-chart` is internal-only)
- `~/.claude/scripts/` (17 root-level scripts: ai_citation_score, analyze_blog, blog_hygiene, blog_preflight, blog_render, cognitive_load, consistency_check, content_decay, dependency_smoke, discourse_research, generate_hero, lint_prose, load_untrusted_root, quality_gate, style_learn, sync_flow, validate_public_release)
- `~/.claude/agents/blog-*.md` (all 5 agents: blog-researcher, blog-writer, blog-seo, blog-reviewer, blog-translator)

Shared Google credentials under `~/.config/claude-seo/` are owned by the user
and may be used by other skills. Both uninstallers leave them intact.

### Manual Uninstall

```bash
# Main skill + all blog-* skill directories (auto-discovers blog-* via glob)
rm -rf ~/.claude/skills/blog
rm -rf ~/.claude/skills/blog-*

# All 5 agents
rm -f ~/.claude/agents/blog-{researcher,writer,seo,reviewer,translator}.md

# All 17 root-level scripts (only if no other plugin uses ~/.claude/scripts/)
rm -f ~/.claude/scripts/{ai_citation_score,analyze_blog,blog_hygiene,blog_preflight,blog_render,cognitive_load,consistency_check,content_decay,dependency_smoke,discourse_research,generate_hero,lint_prose,load_untrusted_root,quality_gate,style_learn,sync_flow,validate_public_release}.py
```

### Clean Up Python Dependencies (Optional)

```bash
pip uninstall textstat beautifulsoup4 lxml jsonschema
```

Restart Claude Code after uninstalling to complete removal.

---

## Troubleshooting Installation

| Symptom | Cause | Fix |
|---------|-------|-----|
| `/blog` command not found | Claude Code not restarted | Close and reopen Claude Code |
| `python3: command not found` | Python not installed or not in PATH | Install Python 3.11+ via your package manager |
| `pip install` fails | Missing pip or wrong Python version | Run `python3 -m ensurepip --upgrade` |
| Permission denied on `install.sh` | Script not executable | Run `chmod +x install.sh` |
| Files not in `~/.claude/` | Wrong install location | Verify `$HOME` points to your home directory |

For additional issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
