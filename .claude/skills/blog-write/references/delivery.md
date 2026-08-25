# Blog Write Delivery Checklist

Writer-specific companion to `skills/blog/references/blog-delivery-contract.md`.

## Gate Steps

1. Capability discovery and hero:
   - Run `python3 scripts/blog_preflight.py --draft <folder> --gate 1`.
   - If a valid local hero already exists, keep it.
   - If generation is needed, use `blog-image` or `python3 scripts/generate_hero.py --topic "<title>" --tags "<tags>" --out <folder>`.
   - Record provider, model ID, prompt, license, and attribution.
2. Format completeness:
   - Run `python3 scripts/blog_render.py --md <slug>.md --out-dir <folder>`.
   - Require markdown, HTML, PDF, and a local hero asset when the deliverable requires a hero.
3. Content review:
   - Dispatch the `blog-reviewer` agent with the rendered HTML.
   - Require score 90/100 or higher and zero P0 issues.
   - Save the review to `<folder>/review.md` ending with `BLOCKING: true|false (reason)`.
4. Visual and asset gates:
   - Run `python3 scripts/blog_preflight.py --draft <folder> --strict`.
   - Strict delivery requires renderer support for visual checks. If the renderer is unavailable, mark the output non-shippable instead of treating it as passed.
5. Iteration:
   - Use `<folder>/preflight-report.json` as the diagnostic input.
   - Stop after 3 failed iterations and present the diagnostic.

## URL And Asset Safety

- Allow `http` and `https` only.
- Reject `javascript:`, `data:`, and `file:` URLs.
- Resolve DNS and reject loopback, private, link-local, multicast, and reserved IP ranges.
- Disable redirects or validate the final URL with the same rules.
- Use tight timeouts and response-size caps.
- Prefer official provider APIs and Openverse so license and creator metadata are preserved.
- Download assets locally and store attribution with the draft.

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
- Internal linking zones: [N]

### Structure
- [N] H2 sections with answer-first formatting
- [N] FAQ items when warranted
- Word count: ~[N] words

### Optional Editorial Style Diagnostics
- Sentence-length variation: [descriptive observation]
- Configured style-list terms: [N found]
- Voice fit: [brief observation]
- These diagnostics do not infer authorship or affect Google/readiness scoring.

### Next Steps
- Resolve [INTERNAL-LINK] placeholders with actual URLs
- Run `/blog analyze <file>` to verify quality score
- Generate VideoObject schema with `/blog schema <file>` when videos are present
```
