# Troubleshooting

Common issues, their causes, and fixes for `claude-blog`. Issues are grouped
by category and ordered from most to least common.

---

## Installation Issues

### "Command not found" after installation

**Symptom**: Running `/blog write` produces no response or a "skill not found"
error.

**Cause**: Claude Code caches skill definitions at startup. New skills are not
detected until the CLI is restarted.

**Fix**:
1. Close Claude Code completely (exit the CLI or close the terminal)
2. Reopen Claude Code
3. Try `/blog write <topic>` again

### Python script errors

**Symptom**: `/blog analyze` fails when running `analyze_blog.py`, or the
script exits with an import error.

**Cause**: Python dependencies are not installed.

**Fix**: use a virtual environment, so no system Python is modified and no
`sudo` is needed:
```bash
python3 -m venv ~/.claude-blog-venv
~/.claude-blog-venv/bin/python -m pip install -r requirements.txt
```
Then run the helper scripts with `~/.claude-blog-venv/bin/python` (or activate
the environment first). Outside a virtual environment, `python3 -m pip install
--user -r requirements.txt` works on Python builds that are not externally
managed.

### Installer warns "pip install failed" or "externally managed"

**Symptom**: `install.sh` finishes, but prints `WARNING: pip install failed`,
possibly mentioning `externally-managed-environment` (PEP 668).

**Cause**: Debian, Fedora, Homebrew and similar Pythons refuse package installs
outside a virtual environment. The skills are already installed; only the
optional Python extras are missing.

**Fix**: create the virtual environment shown above. Do not use `sudo` or
`--break-system-packages`. Set `CLAUDE_BLOG_SKIP_PIP=1` to silence the step.

### Installer says "python3 3.x found; python3 3.11+ is required"

**Cause**: macOS ships `/usr/bin/python3` at 3.9 or older, and some Linux
releases ship 3.10 or older.

**Fix**: install a current Python (`brew install python@3.12`, the python.org
installer, `uv python install 3.12`, or your distribution's `python3.12`
package), open a new terminal, confirm `python3 --version` reports 3.11 or
newer, then run the installer again.

### Installer says "managed installation file was modified"

**Cause**: a file the installer owns was edited after installation. Both
`install.sh` and `uninstall.sh` refuse to overwrite or delete it and change
nothing.

**Fix**: copy any edit you want to keep somewhere outside `~/.claude`, then run
`bash install.sh --force-adopt` (or `bash uninstall.sh --force-adopt`). Each
modified file is first copied to `~/.claude/claude-blog-backups/<timestamp>/`.
Re-apply your edits from there. Details and limits:
[INSTALLATION.md](INSTALLATION.md#if-the-installer-reports-managed-installation-file-was-modified).

### Plugin validate reports "claude-blog" as reserved

**Symptom**: `claude plugin validate .` fails with `Plugin name "claude-blog" is
reserved: it passes as one of Anthropic's own`.

**Cause**: newer Claude Code validators reserve third-party plugin names that
start with `claude-`. Verified results for this repository: Claude Code 2.1.218
passes; 2.1.292 and 2.1.296 fail on this one error only (plus a harmless
warning that a root `CLAUDE.md` is not loaded as plugin context). The v2.2.0
release fails the same way. In maintainer testing the plugin still installs and
loads, so treat it as a validation error, not an observed install failure.

**What to do**: nothing for normal use. CI runs the validator through
`.github/scripts/validate_plugin_tolerate_reserved_name.py`, which tolerates
exactly this finding (and the root `CLAUDE.md` notice) and fails on anything else. The project's own tests and
`scripts/validate_public_release.py` do not depend on the newer validator. If a
future Claude Code release enforces the reservation when installing, report it
in an issue; the standalone installer is unaffected.

### Missing textstat or beautifulsoup4

**Symptom**: `analyze_blog.py` runs but reports `ModuleNotFoundError: No module
named 'textstat'` or similar.

**Cause**: The optional Python dependencies are not installed.

**Behavior**: The analysis script is designed for **graceful degradation**.
Without optional dependencies, it falls back to basic mode:

| Dependency | When Missing | Fallback |
|-----------|-------------|----------|
| textstat | No Flesch/Gunning Fog scores | Sentence length heuristics |
| beautifulsoup4 | No HTML schema parsing | Regex-based detection |
| lxml | BeautifulSoup uses html.parser | Slower but functional |
| spacy | No NER analysis | Skipped (optional feature) |
| sentence-transformers | No semantic similarity | Skipped (optional feature) |
| scikit-learn | No topic clustering | Skipped (optional feature) |
| language-tool-python | No grammar checking | Skipped (optional feature) |

The script will produce results with reduced detail but will not crash.
Install dependencies for full functionality:

```bash
pip install -r requirements.txt  # Core deps
# Optional (install individually as needed):
pip install spacy sentence-transformers scikit-learn language-tool-python
```

### Permission denied on install.sh

**Symptom**: `./install.sh` returns "Permission denied".

**Fix**:
```bash
chmod +x install.sh
./install.sh
```

### Windows: PowerShell execution policy blocks install

**Symptom**: `install.ps1` fails with "running scripts is disabled on this
system."

**Fix**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-WebRequest `
  -Uri https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.ps1 `
  -OutFile install.ps1
Get-FileHash ./install.ps1 -Algorithm SHA256
pwsh -File ./install.ps1
```

Inspect the downloaded file and compare its digest with the release
documentation before running it.

---

## Content Quality Issues

### Low quality scores (below 60)

**Symptom**: `/blog analyze` returns a score below 60 ("Poor" rating).

**Common Causes and Fixes**:

| Issue | Impact | Fix |
|-------|--------|-----|
| Important claims lack clarity or support | Readiness and content points vary | State the point early and add verified evidence where needed; no fixed length |
| Fabricated statistics | Critical integrity issue | Remove or replace with verified support |
| Missing images | Context-dependent | Add an image only when it improves understanding |
| Missing charts | Context-dependent | Add a chart only when data relationships need one |
| No FAQ section | No score penalty | Add Q&A only when genuine reader questions warrant it |
| Difficult paragraph pacing | Advisory only | Split or combine passages when comprehension improves |
| Missing `lastUpdated` | No automatic penalty | Add it only after a substantive update and keep it truthful |
| Excessive self-promotion | Editorial issue | Remove promotion that distracts from the reader task |

**Quick fix workflow**:
```
1. /blog analyze <file>           # Get the score and issues
2. /blog rewrite <file>           # Auto-fix most issues
3. /blog analyze <file>           # Verify improvement
```

### Important section point not detected

**Symptom**: Score report says an important section lacks a clear, supported
point even though the section contains data.

**Cause**: A material claim needs source support close enough for readers to
identify what the source substantiates. Put evidence where it best supports
comprehension; it may appear in the first or a later paragraph.

**Supported placement example**:
```markdown
## How Does AI Search Impact Blog Traffic?

AI Overviews initially caused a 61% decline in organic CTR across 3,119 queries
in a 2025 Seer Interactive study
([Seer Interactive](https://seerinteractive.com), 2025). Later 2026 reporting
showed partial CTR rebound in some query sets, so treat this as historical
context rather than a universal current rate.
```

**Unsupported attribution example**:
```markdown
## How Does AI Search Impact Blog Traffic?

The landscape of search is changing rapidly. Many marketers are concerned
about the future of organic traffic.

According to Seer Interactive, CTR declined 61%.
```

The problem in the second example is not paragraph position. The material
measurement lacks a usable citation and enough study context to verify it.

### Statistics flagged as "fabricated"

**Symptom**: Quality report flags statistics as fabricated or unsourced.

**Cause**: The scoring system looks for inline attribution within 200
characters of a number. Missing or malformed citations trigger this flag.

**Correct attribution format**:
```markdown
initial 61% decline in organic CTR ([Seer Interactive](https://seerinteractive.com), 2025)
```

**Formats that may not be detected**:
```markdown
According to a recent study, CTR declined 61%.     # No source name or link
CTR declined 61% (source: Seer Interactive)         # No URL
CTR declined 61%. Source: Seer Interactive [1]       # Footnote style
```

---

## Template Issues

### Template not loading

**Symptom**: `/blog write` does not follow the expected template structure
for the content type.

**Causes and fixes**:

1. **Templates not installed**: Verify the templates directory exists:
   ```bash
   ls ~/.claude/skills/blog/templates/
   ```
   If empty or missing, re-run `./install.sh`.

2. **Wrong install path**: Templates must be in
   `~/.claude/skills/blog/templates/`, not in the repository's
   `skills/blog/templates/` directory.

3. **Template file corrupted**: Re-copy from the repository:
   ```bash
   cp skills/blog/templates/*.md ~/.claude/skills/blog/templates/
   ```

### Wrong template selected

**Symptom**: `/blog write` picks a how-to template when you wanted a listicle.

**Fix**: Specify the content type explicitly:
```
/blog write listicle: "10 Best Monitoring Tools for 2026"
/blog write --type comparison "Datadog vs Grafana"
```

Or state the type in natural language:
```
/blog write a comparison post about Datadog vs Grafana
```

---

## Agent Issues

### Agent not spawning

**Symptom**: The sub-skill does not delegate to a subagent (blog-researcher,
blog-writer, etc.), and instead tries to do everything inline.

**Causes**:

1. **Agent file not installed**: Check that agent files exist:
   ```bash
   ls ~/.claude/agents/blog-*.md
   ```
   Expected: `blog-researcher.md`, `blog-writer.md`, `blog-seo.md`,
   `blog-reviewer.md`, `blog-translator.md`

2. **Skill metadata or tool restrictions**: validate frontmatter with
   `python3 scripts/validate_skills.py --root .` in the source checkout.
   The correct visibility field is `user-invocable`; `allowed-tools` is
   supported by Claude Code and grants permission preapprovals. It does not
   spawn agents or restrict the available tool pool. This project keeps skill
   preapprovals empty by policy. Agent `tools` fields define their tool
   allowlists; ensure the orchestrator can delegate and passes resolved
   reference paths to the child.

3. **Claude Code version**: Agent spawning via `Task` requires a recent
   version of Claude Code. Update to the latest version.

### Agent produces low-quality output

**Symptom**: The blog-writer agent produces content that does not follow
answer-first formatting or other rules.

**Fix**: This typically means the agent did not load the relevant reference
files. Run the command again: the orchestrator should load references
before spawning the agent. If the issue persists:

1. Verify reference files exist:
   ```bash
   ls ~/.claude/skills/blog/references/
   ```
2. Re-install references:
   ```bash
   cp skills/blog/references/*.md ~/.claude/skills/blog/references/
   ```

---

## Schema and SEO Issues

### Schema detection failing

**Symptom**: `/blog seo-check` or `/blog analyze` reports "No schema detected"
even though the post has JSON-LD markup.

**Causes**:

1. **Schema injected via JavaScript**: AI crawlers (GPTBot, ClaudeBot,
   PerplexityBot) and the analysis script cannot see schema that is
   injected client-side via JavaScript. Schema must be present in the HTML
   source (server-rendered).

   **How to check**: Disable JavaScript in your browser and view source.
   If the `<script type="application/ld+json">` block is missing, your
   schema is JS-injected.

   **Fix**: Move schema to server-rendered HTML:
   - Next.js: Use `generateMetadata()` or `<script>` in `layout.tsx`
   - Hugo: Add to template `<head>` partial
   - WordPress: Use a plugin that renders in PHP, not JS

2. **Schema in wrong format**: The analyzer looks for
   `<script type="application/ld+json">` blocks. Other formats (Microdata,
   RDFa) may not be detected.

3. **MDX FAQSchema component**: If using a React component like
   `<FAQSchema>`, ensure it renders the JSON-LD in the HTML output, not
   just the visual FAQ.

### JSON-LD validation errors

**Symptom**: `/blog schema` generates markup that fails validation.

**Fix**: Test the generated JSON-LD at:
- https://validator.schema.org/
- https://search.google.com/test/rich-results

Common issues:
- Missing `@context` or `@type` fields
- `dateModified` not matching `lastUpdated` in frontmatter
- Image URL not accessible (returns 404)
- Author `@type` should be `Person`, not `Organization`

---

## Delivery Gate Issues

The gates are specified once, in
[`skills/blog/references/blog-delivery-contract.md`](../skills/blog/references/blog-delivery-contract.md).
These are the messages people hit most.

### Gate 4: "review verifier state missing"

**Cause**: the review nonce was never issued for this draft. **Fix**: after
rendering, run `blog_preflight.py --init-review-nonce --draft <D>`, spawn
`blog-reviewer` with that nonce, and save its report verbatim to `<D>/review.md`
(the reviewer has no Write tool, so the orchestrator saves it).

### Gate 4: "draft changed after the review nonce was issued: <file>"

**Cause**: `S.md`, `S.html`, `S.pdf` or the hero changed after the nonce was
issued, so the stored review no longer describes the files. This is intended
behavior, not a flaky test. **Fix**: re-render, re-issue the nonce and re-review.
Older state files written before digests existed skip this check with a warning.

### Gate 2: placeholders, filenames, hero, PDF, source hash

Gate 2 reports leftover `[IMAGE`, `[CHART` or `[INTERNAL-LINK` markers, artifact
or image filenames that are not lowercase slugs, a hero that does not decode or
is smaller than 1200x630, a PDF that is not a real PDF, and an HTML
`blog-source-sha256` that does not match the `.md`, or an `.html` body edited by hand after render
(`blog-body-sha256`). The fix for the last two is
always to re-run `blog_render.py` (which also refuses `.html` input). It also
reports static HTML problems (lang, title, meta description, one H1, heading
order, og tags, noindex, missing `alt`, `<script>`, inline handlers, iframes),
each naming the element and the fix.

### Gate 5: external link failures

The renderer's own footer link is checked for its scheme only, so a fully local
article can pass offline. External links need network access: when several fail
at once the message says the cause may be a network or DNS problem on your
machine. Run `curl -I <url>` from the same machine to tell the difference, then
re-run the gates on a working connection.

---

## Platform-Specific Issues

### MDX compilation errors after blog write/rewrite

**Symptom**: The generated MDX file fails to compile in Next.js.

**Common causes**:

| Error | Cause | Fix |
|-------|-------|-----|
| `stroke-width` is not valid | HTML attributes in JSX | Convert to camelCase: `strokeWidth` |
| `class` is not valid | HTML `class` in JSX | Use `className` |
| `style="..."` syntax error | String style in JSX | Use object: `style={{...}}` |
| Unexpected `{` | Curly braces in markdown text | Escape: `\{` |
| `<` in text content | Angle brackets in prose | Use `&lt;` or wrap in backticks |

**Prevention**: When the platform is detected as MDX/Next.js, the sub-skills
automatically use JSX-compatible syntax. If errors persist, specify the
platform explicitly:

```
/blog write "topic" --format mdx
```

### Hugo front matter format mismatch

**Symptom**: Hugo does not recognize the YAML frontmatter fields.

**Fix**: Hugo uses TOML frontmatter by default (`+++` delimiters). If your
Hugo site uses YAML (`---` delimiters), add to `hugo.toml`:
```toml
[markup.frontmatter]
  date = ["date"]
  lastmod = ["lastUpdated", "lastmod"]
```

---

## Performance Issues

### Commands running slowly

**Symptom**: `/blog write` or `/blog brief` takes a long time to complete.

**Causes**:
- **Research phase**: WebSearch calls for statistics and images can take
  30-60 seconds depending on the topic
- **Chart generation**: Each `blog-chart` invocation adds 10-20 seconds
- **Large context**: Loading many reference files increases processing time

**Mitigation**:
- Provide a brief first (`/blog brief`) to pre-do research, then use
  `/blog write` with the brief (skips research phase)
- For analysis, use `analyze_blog.py` directly for faster automated metrics

### analyze_blog.py batch mode slow on large directories

**Symptom**: `--batch` mode takes a long time on directories with many files.

**Fix**: The script processes files sequentially. For large directories,
analyze subsets:
```bash
python3 analyze_blog.py posts/2026/ --batch    # Only 2026 posts
python3 analyze_blog.py posts/drafts/ --batch  # Only drafts
```

---

## Getting Help

If your issue is not listed here:

1. **Check the version**: Ensure you have the latest `claude-blog` installed:
   ```bash
   cd claude-blog && git pull && ./install.sh
   ```

2. **Verify file integrity**: Compare installed files with the repository:
   ```bash
   diff ~/.claude/skills/blog/SKILL.md skills/blog/SKILL.md
   ```

3. **Reset installation**: Remove and reinstall:
   ```bash
   ./uninstall.sh && ./install.sh
   ```
   If this stops with "managed installation file was modified", follow the
   `--force-adopt` recovery above. Run these from a checkout of a release that
   contains the ownership-aware installer, not the `v2.2.0` tag.

4. **Open an issue**: https://github.com/AgriciDaniel/claude-blog/issues
