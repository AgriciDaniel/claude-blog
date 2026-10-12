# Installation Guide

This guide covers all installation methods for `claude-blog`, a Claude Code skill
ecosystem for blog content creation, optimization, and management.

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) | 2.1.69 or later; tested on 2.1.296 | Runtime for all `/blog` commands |
| Python | 3.11+ | Quality scoring + 5-gate delivery contract runners (analyze_blog, blog_preflight, blog_render, generate_hero, lint_prose, ...) |
| pip | Latest | Python dependency management |

Claude Code must be installed and configured before installing `claude-blog`.

Version note: the Claude Code changelog first lists the plugin system in
2.0.12 and the `${CLAUDE_SKILL_DIR}` skill variable, which this bundle's skills
use to find their scripts and references, in 2.1.69
([changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md),
checked 2026-10-12). 2.1.69 is therefore the oldest version this guide can
justify; only 2.1.296 has been tested.

Python 3.11+ is required for quality scoring and helper workflows including
`analyze_blog.py`, `blog_preflight.py`, `blog_render.py`, `generate_hero.py`,
`lint_prose.py`, and related script checks. Commands that do not invoke those
helpers may still run without Python, but production installs should include it.

---

## Quick Install (One Command)

### Linux / macOS

```bash
curl -fsSLo install.sh https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.sh
# Read install.sh, then pin the revision that will actually run:
CLAUDE_BLOG_REF=<commit-sha-or-release-tag> bash install.sh
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.ps1 -OutFile install.ps1
$env:CLAUDE_BLOG_REF = "<commit-sha-or-release-tag>"
pwsh -File ./install.ps1
```

`<commit-sha-or-release-tag>` is the first release that contains the
ownership-aware installer (`scripts/installer_ownership.py`), or a commit you
reviewed. Prefer a full 40-character commit SHA: the downloaded wrapper clones
the repository at that ref and hands over to the installer in the clone, so the
wrapper's digest only covers the wrapper. Without `CLAUDE_BLOG_REF` the wrapper
follows the moving `main` branch. Do not use the `v2.2.0` tag for installing or
uninstalling: it predates the ownership-aware installer, and its `uninstall.sh`
recursively deletes whole `blog` and `blog-*` skill directories, including any
files you added to them.

`install.ps1` validates the variables that reach `git` before it clones:
`CLAUDE_BLOG_REPO` must look like `owner/name`; `CLAUDE_BLOG_REF` must be a tag,
branch or commit name that starts with a letter or digit and contains none of
`..`, a trailing `/` or a trailing `.lock`; `CLAUDE_BLOG_URL` must not start with
`-`, contain control characters, or use the `ext::` or `fd::` command
transports. A value that fails stops the install with a message naming the
variable. `install.sh` does not apply these checks yet, so set
`CLAUDE_BLOG_REF` and `CLAUDE_BLOG_URL` only from values you typed yourself.

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
git checkout <commit-sha-or-release-tag>   # see the note above; review install.sh first
chmod +x install.sh
./install.sh
```

### Install Python Dependencies

The installers (Unix and Windows) then try to install the optional packages from
`requirements.txt` with `python3 -m pip install --user` (the same interpreter it
version-checked), or plain `pip` inside an active virtual environment. They never
use `sudo` and never pass `--break-system-packages`. Failure is only a
warning: the skills are already installed. On an externally managed Python
(PEP 668, common on Debian, Fedora and Homebrew) pip refuses, and the installer
prints the virtual-environment commands to use instead:

```bash
python3 -m venv ~/.claude-blog-venv
~/.claude-blog-venv/bin/python -m pip install -r requirements.txt
```

Set `CLAUDE_BLOG_SKIP_PIP=1` (Unix and Windows) to skip the step entirely. Python 3.11+ is
required; the stock macOS `/usr/bin/python3` is too old, so install a current
Python first (for example `brew install python@3.12`) and open a new terminal.

#### Reproducible install via uv (v1.9.1+)

For deterministic supply-chain hygiene, the repo ships `uv.lock` with hashes
for resolved artifacts. Reproduce the exact
dev environment with:

```bash
pip install uv          # one-time
uv sync --frozen --extra dev  # installs the declared dev environment
```

This is the recommended path for CI, audit, and any context where
"works on my machine" is not enough. The legacy `pip install -e ".[dev]"`
flow still works; it just resolves transitives freshly each time.

Regenerate `uv.lock` after editing `pyproject.toml` dependency bounds:

```bash
uv lock
```

**Core dependencies** (`requirements.txt` and the `core` extra in `pyproject.toml`):

| Package | Version | Purpose |
|---------|---------|---------|
| textstat | >=0.7.3,<1.0.0 | Readability scoring (Flesch, Gunning Fog, SMOG) |
| beautifulsoup4 | >=4.12.0,<5.0.0 | HTML and schema parsing |

**Optional dependencies** (the `advanced` extra; unlock advanced features in `analyze_blog.py`):

```bash
pip install lxml                   # Faster HTML parser backend for BeautifulSoup
pip install jsonschema             # JSON-LD schema validation
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
# Prefer --key-file (or the interactive prompt) over --key, which leaves the key in shell history
python3 skills/blog-image/scripts/setup_image_mcp.py --key-file /path/to/key.txt

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

# Blog-* directories should list 31 (30 user-facing commands plus the internal blog-chart); total is 32 skill directories (1 orchestrator + 31 sub-skills)
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
usage: analyze_blog.py [-h] [--version] [--output OUTPUT]
                       [--format {json,markdown,table}] [--batch]
                       [--sort {score,name,words}] [--category CATEGORY]
                       [--fix]
                       input

Blog Quality Analyzer - 5-category, 100-point scoring system
...
```

The output above is abridged to the usage line; run the command for the
full help text, which is the source of truth.

---

## Updating

Pull the latest changes and re-run the installer:

```bash
cd claude-blog
git pull
./install.sh
```

The installer verifies ownership before replacing files. It can migrate a
legacy directory manifest from the reviewed public v2.2.0 release or the pinned
public audit baseline when installed bytes match the bundled historical hash
inventory. Unknown user additions remain outside package ownership.

Modified managed files, unknown collisions and unsafe paths stop the update
before payload changes. A legacy installation from another revision needs
reviewed ownership evidence before automatic adoption. Restart Claude Code
after a successful update.

### If the installer reports "managed installation file was modified"

You edited a file the installer owns, and it will not overwrite or delete your
edit silently. Both `install.sh` and `uninstall.sh` stop, name the files and
change nothing. Safe steps:

1. Copy any edit you want to keep outside `~/.claude/skills`,
   `~/.claude/agents` and `~/.claude/scripts`.
2. Run `bash install.sh --force-adopt` (or `bash uninstall.sh --force-adopt`).
   Each modified file is first copied to
   `~/.claude/claude-blog-backups/<timestamp>/` with its relative path, then
   replaced (install) or removed (uninstall). Missing managed files are
   tolerated in this mode; a path replaced by a directory or symlink is still
   refused, and a backup directory that is a symlink aborts before any change.
3. Re-apply your edits from the backup if you still want them.

Backups are never deleted by the installer. On Windows the flag is
`-ForceAdopt` (`--force-adopt` is also accepted) for both `install.ps1` and
`uninstall.ps1`; it uses the same backup folder
(`~/.claude/claude-blog-backups/<timestamp>/`) and also tolerates a managed file
you deleted. Without it, a Windows install or uninstall refuses and names the
files.

If `uninstall.sh` finds no manifest it removes nothing and says so. That is
normal for a plugin install (use `/plugin uninstall claude-blog@agricidaniel-blog`
instead) or when the manifest was already removed.

---

## Uninstall

### Automated Uninstall (Unix)

```bash
# From the claude-blog repository
chmod +x uninstall.sh
./uninstall.sh
```

The uninstaller removes verified package-owned files from:

- `~/.claude/skills/blog/` and `~/.claude/skills/blog-*/` (32 skill directories: 1 orchestrator + 31 sub-skills; 30 user-facing commands; `blog-chart` is internal-only)
- `~/.claude/scripts/` (the root `scripts/*.py` helpers, 22 at the time of writing, including the shared `installer_ownership.py` engine)
- `~/.claude/agents/blog-*.md` (all 5 agents: blog-researcher, blog-writer, blog-seo, blog-reviewer, blog-translator)

Shared Google credentials under `~/.config/claude-seo/` are owned by the user
and may be used by other skills. Both uninstallers leave them intact.
User additions and unknown skills remain. Directories are pruned only after
verified files are removed and only when empty. Modified managed files or
unsafe ownership paths stop removal before payload changes.

### Manual Uninstall

Use the ownership-aware uninstaller from the reviewed repository. For manual
recovery, inspect `~/.claude/claude-blog-manifest.txt`, preserve local edits,
and remove only individually verified package files. A directory name or
`blog-*` prefix alone does not establish ownership. Keep unknown files and
prune a directory only after confirming it is empty.

### Clean Up Python Dependencies (Optional)

Remove dependencies only from a disposable environment dedicated to this
plugin. Shared Python environments can support other skills, so their
dependency ownership must be reviewed separately.

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
