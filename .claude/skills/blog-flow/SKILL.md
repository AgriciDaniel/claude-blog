---
name: blog-flow
description: >
  FLOW framework integration for bloggers. Evidence-led content workflow using
  the Find, Optimize, Win loop with stage-specific AI prompts from the FLOW
  knowledge base (30 blog-applicable prompts, CC BY 4.0). Use when user says
  "FLOW", "FLOW framework", "blog flow", "evidence-led blogging", "find optimize
  win", or wants stage-specific blog prompts.
user-invokable: true
argument-hint: "[stage] [url|topic]"
license: MIT
compatibility: Requires Claude Code and Python 3.11+ for the sync script
metadata:
  author: AgriciDaniel
  version: "2.1.1"
  category: blog
---

# FLOW Framework for Bloggers (Find, Optimize, Win)

Runs FLOW Find/Optimize/Win prompts for a blog topic or URL, turning query data,
source notes, and page evidence into structured decisions instead of improvised
prompts.

> Framework and prompts (c) Daniel Agrici, CC BY 4.0. Source: github.com/AgriciDaniel/flow

FLOW is an evidence-led operating model for retrieval, citation, and conversion
workflows. Claude Blog integrates the FLOW prompt library so writers can turn
query data, source notes, and page evidence into structured decisions instead of
improvised prompts.

This skill exposes the three blog-relevant stages (Find, Optimize, Win) and keeps
the single Leverage prompt available through the prompts index. The local-SEO
prompts (GBP, citations, local audits) are intentionally excluded because they
target brick-and-mortar work, not blogs.

**Runtime context.** Load `references/flow-framework.md` on every `/blog flow`
activation. Load prompt files on demand only, scoped to the stage the user
requests.

---

## Commands

| Command | What it does |
|---------|-------------|
| `/blog flow` | Show FLOW overview and stage menu |
| `/blog flow find [topic\|url]` | Find-stage: keyword discovery, intent mapping, gap analysis (5 prompts) |
| `/blog flow optimize [url]` | Optimize-stage: select 2 to 3 most relevant prompts of 21 based on context |
| `/blog flow win [url]` | Win-stage: BOFU, conversion, dual-surface scorecard (3 prompts) |
| `/blog flow prompts` | Full index of all 30 blog-applicable prompts (Find, Leverage, Optimize, Win) |
| `/blog flow sync` | Pull latest prompt files from github.com/AgriciDaniel/flow |

The single Leverage prompt (off-site authority) is reachable through
`/blog flow prompts` and is not promoted to a top-level command, since most
blog workflows route off-site work elsewhere.

---

## Orchestration Logic

### On `/blog flow` (no sub-command)
1. Read `references/flow-framework.md`.
2. Show the FLOW stage overview with a one-line description of each stage.
3. Ask the user which stage matches their current situation.

### On `/blog flow find [topic|url]`
1. Read all files in `references/prompts/find/`.
2. Apply each prompt to the topic or URL, capturing demand and intent signals.
3. Cross-reference: "For deeper briefs and outlines, see `/blog brief <topic>`,
   `/blog outline <topic>`, and `/blog cannibalization` to detect overlap with
   existing posts."

### On `/blog flow optimize [url]`
1. Read the file names in `references/prompts/optimize/`.
2. Read prior context (target URL, niche, any prior skill output in this
   conversation, scoring deltas from `/blog analyze`).
3. Select 2 to 3 most relevant prompts, then load only those files.
4. Apply the selected prompts; note that the rest are accessible via
   `/blog flow prompts`.
5. Cross-reference: "For deeper rewrites and validation, see `/blog rewrite
   <file>`, `/blog seo-check <file>`, `/blog geo <file>`, `/blog schema <file>`,
   and `/blog factcheck <file>`."

### On `/blog flow win [url]`
1. Read all files in `references/prompts/win/`.
2. Apply each prompt to the URL's conversion and BOFU context.
3. Cross-reference: "For repurposing, full-site health, and quality scoring,
   see `/blog repurpose <file>`, `/blog audit`, and `/blog analyze <file>`."

### On `/blog flow prompts`
1. Read `references/prompts/README.md`.
2. Display the full index: 30 prompts grouped by stage (Find, Leverage,
   Optimize, Win) with name and trigger conditions.
3. State that local-SEO prompts are excluded by design; point users to
   `claude-seo` (`/seo flow local`) if they need them.

### On `/blog flow sync`
1. Run: `python3 scripts/sync_flow.py`.
2. Display the JSON summary (files added, updated, unchanged).
3. Show the attribution notice after the sync completes.

---

## Context Matching (Optimize stage)

The optimize stage has 21 prompts. Dumping all 21 is noise. Select by priority:

1. **Niche** (SaaS or B2B blog leans on-page plus technical; lifestyle leans
   freshness plus E-E-A-T; publisher leans authority plus citations).
2. **Prior skill output** (`/blog analyze` E-E-A-T gap routes to authority
   prompts; `/blog seo-check` failures route to on-page prompts; `/blog geo`
   gaps route to extraction-format prompts).
3. **URL signals** (commercial pages need conversion prompts; informational
   posts need freshness plus answer-first prompts).

Always surface exactly 2 to 3 prompts. State which prompts you chose and why.

---

## Reference Files

Load on demand. Do NOT load all at startup.

- `references/flow-framework.md`. FLOW operating model. Load on every `/blog
  flow` activation.
- `references/bibliography.md`. Evidence sources. Load when citing studies or
  statistics.
- `references/prompts/README.md`. Prompt index. Load for `/blog flow prompts`.
- `references/prompts/find/`. 5 prompts. Load for `/blog flow find`.
- `references/prompts/leverage/`. 1 prompt. Load only when surfaced through
  `/blog flow prompts`.
- `references/prompts/optimize/`. 21 prompts. Load selectively for `/blog flow
  optimize`.
- `references/prompts/win/`. 3 prompts. Load for `/blog flow win`.

If `references/` is missing, instruct the user to run `/blog flow sync` first.

---

## Sync Script

`scripts/sync_flow.py` pulls prompt files from github.com/AgriciDaniel/flow and
writes them under `skills/blog-flow/references/`. Stdlib only, HTTPS only,
host-allowlisted to `api.github.com`, 5 MB response cap, atomic writes,
path-traversal guarded.

Modes:

- `python3 scripts/sync_flow.py`. Sync the latest version of every blog-relevant
  stage to disk and refresh the lockfile.
- `python3 scripts/sync_flow.py --dry-run`. Report planned changes without
  writing.
- `python3 scripts/sync_flow.py --ref <sha>`. Pin fetches to a specific FLOW
  commit SHA for reproducible installs.

The lockfile lives at
`skills/blog-flow/references/flow-prompts.lock` and uses sha256sum-compatible
format. Drift between the on-disk content and the lockfile is reported on every
sync run.

The script syncs only blog-applicable stages (`find`, `leverage`, `optimize`,
`win`). The `local` stage is intentionally skipped to keep the references
directory aligned with the skill's surface area.

GitHub API calls are anonymous by default. If `GITHUB_TOKEN` is set in the
environment, or `gh auth token` returns a token after a 403 response, the
script retries the request with that token. No tokens are written to disk.

---

## Attribution

Every `/blog flow` activation (any sub-command) outputs before analysis:

```
Framework and prompts (c) Daniel Agrici, CC BY 4.0. Source: github.com/AgriciDaniel/flow
```

Do not omit or modify the attribution. Synced files also carry an HTML comment
license header injected by the sync script.

---

## Error Handling

| Scenario | Action |
|----------|--------|
| `references/flow-framework.md` missing | "FLOW reference files not synced. Run: `/blog flow sync`." |
| Prompt file missing | "Run `/blog flow sync` to pull the latest prompts from the FLOW repo." |
| `sync_flow.py` network error | Display the script's stderr. Check rate limits with `gh api rate_limit` if `gh` is installed. |
| `sync_flow.py` 403 after retry | Set `GITHUB_TOKEN` or run `gh auth login`, then retry. |
| Path-traversal abort | The sync target tried to escape the references directory. Inspect the upstream repo and pin to a known-good `--ref`. |
