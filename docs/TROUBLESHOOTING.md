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

**Fix**:
```bash
pip install -r requirements.txt
```

Or install the core dependencies individually:
```bash
pip install textstat beautifulsoup4 lxml jsonschema
```

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
irm https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.ps1 | iex
```

---

## Content Quality Issues

### Low quality scores (below 60)

**Symptom**: `/blog analyze` returns a score below 60 ("Poor" rating).

**Common Causes and Fixes**:

| Issue | Impact | Fix |
|-------|--------|-----|
| No answer-first formatting | -20 pts max | Add a 40-60 word stat paragraph at the start of every H2 section |
| Fabricated statistics | -8 pts + Critical flag | Replace every unsourced number with a real stat from a tier 1-3 source |
| Missing images | -4 to -7 pts | Add 3-5 images from Pixabay/Unsplash with descriptive alt text |
| Missing charts | -5 to -8 pts | Generate 2-4 SVG charts via `/svg-chart` (diverse types) |
| No FAQ section | -4 pts | Add 3-5 FAQ items with 40-60 word answers containing statistics |
| Long paragraphs (>100 words) | -8 pts | Split into 40-55 word paragraphs |
| Missing `lastUpdated` | -4 pts | Add `lastUpdated: "YYYY-MM-DD"` to frontmatter |
| Excessive self-promotion | -3 pts | Remove brand mentions except 1 in author bio context |

**Quick fix workflow**:
```
1. /blog analyze <file>           # Get the score and issues
2. /blog rewrite <file>           # Auto-fix most issues
3. /blog analyze <file>           # Verify improvement
```

### Answer-first formatting not detected

**Symptom**: Score report says "Missing answer-first formatting" even though
sections have statistics.

**Cause**: The statistic must be in the FIRST paragraph under the H2 heading,
not in the second or third paragraph.

**Correct pattern**:
```markdown
## How Does AI Search Impact Blog Traffic?

AI Overviews caused a 61% decline in organic CTR across 3,119 queries
([Seer Interactive](https://seerinteractive.com), 2025). This shift means
blog publishers must optimize for both traditional rankings and AI citation
to maintain visibility.
```

**Incorrect pattern** (stat buried):
```markdown
## How Does AI Search Impact Blog Traffic?

The landscape of search is changing rapidly. Many marketers are concerned
about the future of organic traffic.

According to Seer Interactive, CTR declined 61%.
```

### Statistics flagged as "fabricated"

**Symptom**: Quality report flags statistics as fabricated or unsourced.

**Cause**: The scoring system looks for inline attribution within 200
characters of a number. Missing or malformed citations trigger this flag.

**Correct attribution format**:
```markdown
61% decline in organic CTR ([Seer Interactive](https://seerinteractive.com), 2025)
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
   `blog/templates/` directory.

3. **Template file corrupted**: Re-copy from the repository:
   ```bash
   cp blog/templates/*.md ~/.claude/skills/blog/templates/
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
   `blog-reviewer.md`

2. **Missing `Task` in allowed-tools**: The sub-skill's YAML frontmatter must
   include `Task` in its `allowed-tools` list. Check the sub-skill file:
   ```bash
   head -20 ~/.claude/skills/blog-write/SKILL.md
   ```
   The `allowed-tools` section should include `Task`.

3. **Claude Code version**: Agent spawning via `Task` requires a recent
   version of Claude Code. Update to the latest version.

### Agent produces low-quality output

**Symptom**: The blog-writer agent produces content that does not follow
answer-first formatting or other rules.

**Fix**: This typically means the agent did not load the relevant reference
files. Run the command again -- the orchestrator should load references
before spawning the agent. If the issue persists:

1. Verify reference files exist:
   ```bash
   ls ~/.claude/skills/blog/references/
   ```
2. Re-install references:
   ```bash
   cp blog/references/*.md ~/.claude/skills/blog/references/
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
- **Chart generation**: Each `/svg-chart` invocation adds 10-20 seconds
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
   diff ~/.claude/skills/blog/SKILL.md blog/SKILL.md
   ```

3. **Reset installation**: Remove and reinstall:
   ```bash
   ./uninstall.sh && ./install.sh
   ```

4. **Open an issue**: https://github.com/AgriciDaniel/claude-blog/issues
