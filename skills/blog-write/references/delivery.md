# Blog Write Delivery Checklist

Writer-specific companion to `skills/blog/references/blog-delivery-contract.md`.
The contract holds the canonical delivery sequence and wins on any disagreement.
This file is the short checklist for `/blog write`.

Resolve the scripts root once, reject it unless absolute, and never run a helper
from the current project:

```bash
BLOG_SCRIPT_DIR="${CLAUDE_BLOG_SCRIPTS_DIR:-<resolved skill dir>/../../scripts}"
case "$BLOG_SCRIPT_DIR" in /*) ;; *) echo "ERROR: script dir must be absolute" >&2; exit 1 ;; esac
```

(`blog-write/SKILL.md` substitutes the resolved skill directory; reference files
are not expanded by the host, so the owning skill passes the resolved path.)

## Gate Steps

Draft folder `D`, slug `S`. Run capability discovery once first:
`python3 "$BLOG_SCRIPT_DIR/blog_preflight.py" --draft "$D" --gate 1`.

1. Draft: `D/S.md` exists. Draft markers `[INTERNAL-LINK: ...]`, `[IMAGE: ...]`, `[CHART: ...]` are allowed here only.
2. Visuals, done by the orchestrator (the `blog-writer` agent cannot call skills):
   - Hero: keep a valid local `hero.<ext>`; otherwise run `python3 "$BLOG_SCRIPT_DIR/generate_hero.py" --topic "<title>" --tags "<tags>" --out "$D"` or use `blog-image`. Record provider, model ID, prompt, license and attribution.
   - Charts: run `blog-chart` for each `[CHART]` marker and embed the SVG in a `<figure>`.
   - Internal links: replace each `[INTERNAL-LINK]` with a real link to a page that exists, or remove the marker and keep the plain text.
   - Images: replace each `[IMAGE]` with a local file in `D`, or remove it.
   - Attribution: if `hero-credit.txt` names a license that needs visible credit (CC BY, BY-SA, or a stock license that asks for it), add the credit line to the article's Sources section or the hero caption. The renderer does not publish it.
   - Confirm no marker remains: search `S.md` for `[INTERNAL-LINK`, `[IMAGE` and `[CHART`.
3. Render: `python3 "$BLOG_SCRIPT_DIR/blog_render.py" --md "$D/S.md" --out-dir "$D"`.
4. Init nonce: `NONCE=$(python3 "$BLOG_SCRIPT_DIR/blog_preflight.py" --init-review-nonce --draft "$D")`.
5. Review: dispatch `blog-reviewer` with the draft path, reference roots and the nonce.
   - It returns the report as text. Save that text verbatim to `D/review.md` (no edits).
   - Required: score 90/100 or higher (see the threshold table in `quality-scoring.md`; unpublished drafts follow its draft-stage rule), zero P0 issues, a matching `Nonce:` line, and a last line `BLOCKING: true|false (reason)`.
6. Gates: `python3 "$BLOG_SCRIPT_DIR/blog_preflight.py" --draft "$D" --strict`. Strict delivery requires renderer support for the visual checks; if the renderer is unavailable, mark the output non-shippable instead of treating it as passed.
7. Loop: use `D/preflight-report.json` as the diagnostic input and add `--repair-attempt` on gate runs inside the loop. After ANY change to `S.md`, `S.html`, `S.pdf` or the hero, re-render, re-init the nonce and re-review; the gate fails if they were not. Stop after 3 failed iterations and present the diagnostic.

## URL And Asset Safety

- Allow `http` and `https` only.
- Reject `javascript:`, `data:`, and `file:` URLs.
- Resolve DNS and reject loopback, private, link-local, multicast, and reserved IP ranges.
- Disable redirects or validate the final URL with the same rules.
- Use tight timeouts and response-size caps.
- Prefer official provider APIs and Openverse so license and creator metadata are preserved.
- Download assets locally and store attribution with the draft. Never hotlink an image in the delivered article.

## Completion Summary

```
## Blog Post Complete: [Title]

### Template Used
- [Template name] or "generic outline"

### Statistics
- [N] sourced statistics from tier 1-3 sources
- [N] unique sources cited

### Visual Elements
- Cover image: [local path, source, model ID or license]
- [N] inline images
- [N] SVG charts
- [N] YouTube video embeds

### Dual-Optimization Elements
- Summary box: present
- Information gain markers: [N]
- Evidence-backed sections: [N]
- Internal links: [N] resolved

### Structure
- [N] H2 sections with answer-first formatting
- [N] FAQ items when warranted
- Word count: ~[N] words

### Fallbacks and skips
- [One line per sub-skill fallback or skipped step: what changed and why, or "none"]

### Optional Editorial Style Diagnostics
- Sentence-length variation: [descriptive observation]
- Configured style-list terms: [N found]
- Voice fit: [brief observation]
- These diagnostics do not infer authorship or affect Google/readiness scoring.

### Next Steps
- Run `/blog analyze <file>` to verify quality score
- Generate VideoObject schema with `/blog schema <file>` when videos are present
```

## Optional Platform Embedding Examples

Load these examples only when the draft uses images or charts.

#### 5i. Image Embedding

Images are local files in the draft folder with lowercase slug-style names.

Standard markdown:
```markdown
![Descriptive alt text, topic keywords naturally](diagram-core-web-vitals-thresholds.webp)
```

MDX (a plain markdown image works; use your framework's image component only when
the project already does):
```mdx
![Descriptive alt text, topic keywords naturally](diagram-core-web-vitals-thresholds.webp)
```

- Place images after H2 headings, before body text
- Space evenly throughout the post (not clustered)
- Alt text should be a full descriptive sentence

#### 5j. Chart Embedding

Standard markdown/HTML:
```html
<figure>
  <svg viewBox="0 0 560 380" ...>...</svg>
  <figcaption>Source: [Source Name], [Year]</figcaption>
</figure>
```

MDX format:
```mdx
<figure className="chart-container" style={{margin: '2.5rem 0', textAlign: 'center', padding: '1.5rem', borderRadius: '12px'}}>
  <svg viewBox="0 0 560 380" ...>...</svg>
</figure>
```

Give each chart a unique id (see `blog-chart/references/chart-input-schema.md`) so
the `aria-labelledby` ids on a page never collide.
