# Contributors

Claude Blog is built by [@AgriciDaniel](https://github.com/AgriciDaniel) with contributions from the AI Marketing Hub community.

## v1.8.1 through v1.8.6: Hostile-audit hardening (2026-05-17)

Seven rounds of hostile re-audit (cybersecurity + GitHub + documentation + code-quality + test-coverage tracks) caught defects each round that prior rounds missed. Each round was executed by parallel review passes with file:line evidence requirements. The audit pattern itself is documented across `CHANGELOG.md` v1.8.1 through v1.8.6 entries.

- **v1.8.1**: closed 27 findings from a three-track audit (catastrophic `parse_engagement` regex bug, indirect prompt injection on project-root auto-load, path-traversal hardening, NOTICE attribution).
- **v1.8.2**: per-load nonce contract + project-wide ASCII em-dash cleanup (script-driven, missed unicode em-dashes).
- **v1.8.3**: code-CAPABLE nonce defense via `scripts/load_untrusted_root.py` + 6 HIGH prose breakages + O(n^2) DoS close.
- **v1.8.4**: CI prose-hygiene linter (`scripts/lint_prose.py`) + version-coherence check + 30 unicode em-dashes cleaned (the v1.8.2/v1.8.3 cleanup missed unicode).
- **v1.8.5**: CLAUDE.md / ARCHITECTURE.md updates + `tests/test_lint_prose.py` + OUTERMOST nonce-authority instruction + command-coherence regression test.
- **v1.8.6**: installer-sync fix (the v1.8.0+ helpers were never copied by install.sh) + 10 stale sub-skill SKILL.md versions resolved + sub-skill coherence test + 4-backtick fence handling + YAML-quote-tolerant version regex.

Calibrated score arc: 68/100 (v1.8.0) -> ~91/100 plateau (v1.8.5) -> ~96/100 (v1.8.6 ceiling per /best-practices kernel; 100/100 is structurally unreachable per the asymptote analysis in CHANGELOG v1.8.5).

## v1.8.0: Methodology adaptation from impeccable (2026-05-16)

Four editorial methodologies in v1.8.0 are adapted from the [impeccable](https://github.com/pbakaus/impeccable) frontend-design plugin (v3.1.1, Apache 2.0, by [Paul Bakaus](https://github.com/pbakaus)).

| Methodology | Source in impeccable | Adapted in claude-blog |
|---|---|---|
| Two-tier AI slop detection (first-order + second-order reflex) | `skills/impeccable/SKILL.md` (category-reflex check) | `skills/blog/references/ai-slop-detection.md` |
| Ordinal 0-4 heuristic rubric with P0-P3 severity | `skills/impeccable/reference/heuristics-scoring.md` | `skills/blog/references/editorial-heuristics.md` |
| Cognitive-load assessment (intrinsic / extraneous / germane, 4-item working-memory ceiling) | `skills/impeccable/reference/cognitive-load.md` | `skills/blog/references/cognitive-load.md` + `scripts/cognitive_load.py` |
| Durable context-loading pattern (PRODUCT.md / DESIGN.md auto-loaded by every command) | `skills/impeccable/scripts/load-context.mjs` + `reference/teach.md` | `skills/blog-brand/SKILL.md` (BRAND.md + VOICE.md) |

Impeccable polishes user interfaces; this release applies the same mental models to prose. No code is copied verbatim; the adaptation is at the methodology level. Each adapted reference file links back to its impeccable source in its Attribution section.

License of the source: Apache 2.0. claude-blog remains MIT-licensed; the Apache 2.0 attribution requirement is satisfied via the credit lines in each adapted file plus this section.

## v1.8.0 (continued): Methodology adaptation from last30days-skill (2026-05-16)

Three research-discipline methodologies in v1.8.0 are adapted from the [last30days-skill](https://github.com/mvanhorn/last30days-skill) plugin (v3.2.1, MIT, by [Matt Van Horn](https://github.com/mvanhorn)).

| Methodology | Source in last30days-skill | Adapted in claude-blog |
|---|---|---|
| Multi-platform discourse research (Reddit / HN / X / YouTube / etc.) | `skills/last30days/SKILL.md` + `scripts/last30days.py` (API-driven) | `skills/blog-discourse/SKILL.md` + `scripts/discourse_research.py` (API-free, WebSearch + site operators) |
| 5-dimension research quality rubric (groundedness, specificity, coverage, actionability, format) | `docs/search-quality-eval.md` + SKILL.md scoring | `skills/blog/references/research-quality.md` |
| Synthesis voice contract: 6 portable LAWs of 8 upstream (no trailing Sources block, no invented titles, no em-dashes, no raw cluster dumps, inline `[name](url)` citations, discrete claims) | `skills/last30days/SKILL.md` "VOICE CONTRACT LAW" section | `skills/blog/references/synthesis-contract.md`. Upstream LAW 5 (engine-footer pass-through) and LAW 7 (`--plan` flag mandatory) are last30days runtime-specific and intentionally not ported. |
| Pre-flight keyword-trap classes (demographic shopping, numeric trap, overly-literal, generic single-noun) | `skills/last30days/SKILL.md` "Step 0.45" | embedded in `research-quality.md` |
| Named-entity topic decomposition pattern (Step 0.55) | `skills/last30days/SKILL.md` "Step 0.55" | embedded in `research-quality.md`, referenced by `agents/blog-researcher.md` |
| Freshness-first ranking concept | `skills/last30days/SKILL.md` ranking-and-scoring section | freshness-floor table in `research-quality.md` (30-day / 90-day) |

The upstream is a sophisticated multi-platform research engine that calls Reddit, X, YouTube, TikTok, Hacker News, Polymarket, GitHub, Bluesky, and other platform APIs and scores results by live engagement (upvotes, likes, prediction-market money). claude-blog ports the editorial methodology without the API plumbing: `blog-discourse` runs against WebSearch results with platform-targeted site operators (e.g. `site:reddit.com`, `site:news.ycombinator.com`, `site:x.com`), so it works in any environment without keys.

License of the source: MIT. claude-blog remains MIT-licensed. Attribution is a courtesy under MIT (not a strict requirement); credit is included in each adapted file plus this section.

## v1.7.0: Pro Hub Challenge Community Release (2026-04-27)

In March 2026, the AI Marketing Hub Pro community ran the first Pro Hub Challenge: members built skills and extensions for the claude-blog and claude-seo ecosystems. Six submissions were independently audited (security, functionality, code quality, documentation, dependencies, SKILL.md discoverability, innovation). Five scored Proficient or above. After security review and clean-room re-implementation in the claude-blog voice and security posture, two submissions were integrated as core skills in v1.7.0.

### Integrated as core skills

| Contributor | Original submission | Integrated as | Score |
|---|---|---|---|
| **Lutfiya Miller** (winner) | [semantic-cluster-engine](https://github.com/Drfiya/semantic-cluster-engine) | `blog-cluster` (semantic topic-cluster planning + execution engine) | 95 / 100 Exemplary |
| **Chris Mueller** | [claude-blog-multilingual](https://github.com/Chriss54/multilingual-int) | `blog-multilingual`, `blog-translate`, `blog-localize`, `blog-locale-audit` + `blog-translator` agent | 85 / 100 Proficient |

The cluster engine was the highest-scoring submission of the entire challenge. Lutfiya's design (Plan + Execute architecture with cluster-context injection into per-post writes) is preserved verbatim; we removed brand-specific styling and image prompts, hardened the HTML output against XSS, and routed through claude-blog's existing sub-skills.

Chris's multilingual suite was the most blog-native submission: four user-facing skills explicitly designed for claude-blog. The audit flagged a `curl | bash` installer and credential handling; both are removed in this port. The shared `cultural-adaptation.md` reference is referenced (not duplicated) by `blog-localize`. The `blog-translator` agent ships without `Bash` access (per the v1.9.6 lesson from claude-seo: prompt-injection blast radius).

### Acknowledged (not integrated in claude-blog v1.7.0)

| Contributor | Original submission | Status |
|---|---|---|
| **Florian Schmitz** | [claude-sxo-skill](https://github.com/tools-enerix/claude-sxo-skill) | 91.7 Exemplary. Integrated into [claude-seo v1.9.0](https://github.com/AgriciDaniel/claude-seo/releases/tag/v1.9.0) as `seo-sxo`. Blog adaptation deferred until the analyzer can be cleanly separated from page-builder and DataForSEO dependencies. |
| **Dan Colta** | [seo-drift-monitor](https://github.com/dancolta/seo-drift-monitor) | 49 Inadequate. Rejected in audit (hardcoded Google API key). The concept (baseline + diff over time) is interesting; a clean-room blog-side implementation is on the roadmap. |
| **Matej Marjanovic** | [omnichannel-seo](https://github.com/matej-marjanovic/claude-seo) | 78.3 Proficient. E-commerce SEO + DataForSEO Merchant. Integrated into claude-seo v1.9.0; not blog-native. |
| **Benjamin Samar** | seo-dungeon | 78.3 Proficient. SEO gamification. Reviewed; not integrated. |

## v1.7.0: FLOW framework integration

Released **2026-04-27**.

- **Source project:** [FLOW](https://github.com/AgriciDaniel/flow) by Daniel Agrici, v1.0.0 (2026-04-25)
- **License:** CC BY 4.0 (prompt content) + MIT (skill code)
- **What it adds:** 30 blog-applicable AI prompts (find: 5, leverage: 1, optimize: 21, win: 3) plus the FLOW framework doc and bibliography
- **Skill:** `blog-flow`
- **Commands:** `/blog flow [find|optimize|win|prompts|sync]`
- **Sync mechanism:** `scripts/sync_flow.py` pulls from GitHub. Stdlib only. HTTPS only. Host-allowlisted to `api.github.com`. 5 MB cap. Atomic writes. Path-traversal guard. Anonymous-first GitHub API. Supports `--dry-run` and `--ref <sha>` pinning. SHA-256 lockfile drift detection.
- **License headers:** Every synced markdown file (and the auto-generated index README) carries an HTML comment crediting Daniel Agrici / FLOW / CC BY 4.0.

Local-stage prompts (Google Business Profile, citations, local audits) are intentionally excluded; they target brick-and-mortar work, not blogs. Use `claude-seo`'s `seo-flow` for the local stage.

## v1.7.0: Mechanical security guardrails

Released **2026-04-27**.

A new pytest module (`tests/test_security_guardrails.py`) enforces four invariants on every test run:

1. No agent grants the `Bash` tool in its frontmatter (prompt-injection blast radius).
2. No `SKILL.md` includes the invalid `allowed-tools` field.
3. Skill names are unique across the entire repository (no duplicate routing).
4. The FLOW sync script preserves all six security invariants (host allowlist, size cap, dry-run flag, ref pinning, lockfile, license-header injection, path-traversal guard).

Pre-existing finding closed: `agents/blog-reviewer.md` had `Bash` in its tools list (used only for word counts and pattern matches that `Grep` already covers). Removed.

## How to credit a contributor in a blog post

When writing about a contributor, link to:

- Their **original submission repo** (the GitHub URL in the table above)
- The integrated skill in this repo: `https://github.com/AgriciDaniel/claude-blog/tree/main/skills/<skill-name>/`
- This `CONTRIBUTORS.md` file as the canonical attribution source

## Community

- **Free community:** https://www.skool.com/ai-marketing-hub
- **Pro community:** https://www.skool.com/ai-marketing-hub-pro
