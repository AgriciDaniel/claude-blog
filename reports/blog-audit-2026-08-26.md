# Blog Audit Report

Audit date: 2026-08-26

## Summary

- Blog HTML files discovered: 24
- Posts scored after excluding `blog/index.html`: 23
- Average score: 73.3/100
- Strong: 4
- Acceptable: 13
- Below Standard: 6
- Rewrite: 0
- Critical issues: 0
- Method: internal editorial-readiness heuristic, not a calibrated ranking or
  AI-citation probability
- Limitation: optional `textstat` was unavailable, so documented readability
  fallbacks were used

The corrected analyzer found no false missing title, description, or author
issues on the rendered HTML corpus. The main opportunity is differentiated
evidence and reader utility on the six lowest-scoring posts. Readability bands
remain descriptive and should be interpreted against each page's reader intent.

## Per-post scores

| Post | Score | Rating | Highest-priority finding |
|---|---:|---|---|
| claude-blog-v1-6-8-update.html | 62 | Below Standard | Add differentiated evidence, a sourced synthesis, or a useful case example |
| google-seo-data-free-api-guide.html | 64 | Below Standard | Add differentiated evidence, a sourced synthesis, or a useful case example |
| claude-blog-v191-release.html | 66 | Below Standard | Review readability in context and add stronger decision utility |
| claude-blog-v171-security-hardening.html | 67 | Below Standard | Add differentiated evidence and stronger decision utility |
| claude-obsidian-v1-9-compound-vault.html | 67 | Below Standard | Repair heading hierarchy and strengthen decision utility |
| ai-content-pipeline-guide.html | 68 | Below Standard | Add differentiated evidence, a sourced synthesis, or a useful case example |
| ai-blog-writing-with-claude-code.html | 70 | Acceptable | Add differentiated evidence and a decision aid |
| claude-blog-vs-jasper-writesonic.html | 70 | Acceptable | Add differentiated evidence and a decision aid |
| free-ai-blog-writing-tools-2026.html | 71 | Acceptable | Add differentiated evidence and reusable source-backed sections |
| wp-mcp-ultimate-wordpress-publishing.html | 71 | Acceptable | Add differentiated evidence and a decision aid |
| claude-obsidian-second-brain.html | 72 | Acceptable | Repair heading hierarchy and review readability in context |
| blog-seo-checklist-2026.html | 73 | Acceptable | Add differentiated evidence or a useful example |
| claude-blog-v170-community-release.html | 73 | Acceptable | Add differentiated evidence and stronger decision utility |
| multilingual-blog-publishing-guide.html | 73 | Acceptable | Add differentiated evidence and stronger decision utility |
| ai-content-scoring-explained.html | 75 | Acceptable | Split the densest sentences where clarity improves |
| claude-blog-v220-release.html | 75 | Acceptable | Add a concise decision aid or evidence summary |
| content-templates-guide.html | 75 | Acceptable | Split the densest sentence where clarity improves |
| public-questions-paa-skill.html | 78 | Acceptable | Add explicit entity definitions only where useful |
| dual-optimization-guide.html | 79 | Acceptable | Split the densest sentences where clarity improves |
| best-claude-code-skills-2026.html | 82 | Strong | Minor sentence-level clarity cleanup |
| claude-blog-v211-release.html | 82 | Strong | Minor sentence-level clarity cleanup |
| chatgpt-codex-vs-claude-code-2026.html | 84 | Strong | Minor sentence-level clarity cleanup |
| claude-watermark-synthid-guide.html | 88 | Strong | Minor sentence-level clarity cleanup |

## Prioritized action queue

1. Refresh `claude-blog-v1-6-8-update.html` with a compact evidence summary and
   a reader decision aid.
2. Refresh `google-seo-data-free-api-guide.html` with differentiated examples
   and repair its heading hierarchy.
3. Improve `claude-blog-v191-release.html` with a concise release decision table
   or source-backed summary.
4. Add evidence and decision utility to
   `claude-blog-v171-security-hardening.html`.
5. Repair heading hierarchy and add a usable takeaway to
   `claude-obsidian-v1-9-compound-vault.html`.
6. Add a worked example or sourced synthesis to
   `ai-content-pipeline-guide.html`.

The complete per-file analyzer output is stored in
`reports/blog-audit-2026-08-26.json`.
