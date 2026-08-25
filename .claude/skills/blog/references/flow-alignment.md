# FLOW Alignment in claude-blog

This reference explains how claude-blog adopts the FLOW framework. Load it on demand when a user asks about FLOW, evidence standards, surface coverage, or how the blog skills route to FLOW stages.

## 1. What FLOW is and why claude-blog adopted it

FLOW is an evidence-led 2026-search operating model published at `github.com/AgriciDaniel/flow` (CC BY 4.0 prompt content, MIT code), authored by Daniel Agrici. It treats modern discovery as a multi-surface system rather than a single SERP, and it encourages traceable support for material public claims. claude-blog v2.1.0 includes FLOW through the `blog-flow` sub-skill (originally integrated in v1.7.0) plus this alignment doc, which informs how every other blog skill in the suite plans, writes, optimizes, and audits content. FLOW provides the principles and prompts; claude-blog provides the production tooling that applies them at scale.

## 2. Evidence records in claude-blog

Material public statistics need enough provenance for readers and editors to
verify and interpret them. Useful fields include:

1. **Relevant date or study period** when it changes the claim's meaning.
2. **Identifiable source** with publisher and document title where needed.
3. **Retrievable support** through a stable URL, plus retrieval notes for
   changeable or undated sources.
4. **Methodology and limitations** when they affect interpretation.

The publication's citation style controls presentation. No fixed sentence form
or complete field set is required for every source. Unverifiable statistics get
dropped, and contradicted statistics get replaced with a verified alternative.

## 3. The FLOW 5-surface model

In 2026 a query reaches a buyer through 5 parallel surfaces, often without a site visit. Coverage on each surface is planned independently.

| Surface | What it is | Where claude-blog handles it |
|---|---|---|
| 1. Owned site | Direct organic ranking on the publisher's domain | `blog-write`, `blog-rewrite` (on-page), `blog-seo-check` |
| 2. SERP + AI Overviews | Google SERP including AIO panels | `blog-geo`, `blog-schema`, `blog-seo-check` |
| 3. AI assistant citations | ChatGPT, Perplexity, Claude, Gemini, Copilot, You.com | `blog-geo` (citation readiness), `blog-flow optimize` (visibility prompts) |
| 4. Local pack | Map listings, Google Business Profile | Out of scope for blog content. Use `claude-seo` (`/seo local`, `/seo maps`) for local SEO. |
| 5. Communities + video | Reddit, YouTube, LinkedIn, Quora, niche forums | `blog-repurpose` (multi-platform), `skills/blog/references/distribution-playbook.md`, `blog-cluster` (interlinked content) |

claude-blog operationalizes surfaces 1, 2, 3, and 5 directly. Surface 4 is delegated to claude-seo. When a blog post targets a query that also surfaces in a community (Reddit thread, YouTube comment), the writer should consider dual-surface thinking: optimize the post for extraction AND consider whether the same answer should also live in the community where the query is asked.

## 4. FLOW stages mapped to existing claude-blog skills

| FLOW stage | claude-blog skills that consume this | When to invoke `/blog flow <stage>` directly |
|---|---|---|
| Find (5 prompts) | `blog-brief`, `blog-outline`, `blog-strategy`, `blog-cluster` (planning) | When you want raw FLOW prompts for keyword discovery, audience avatar, content prioritization without invoking a full brief/outline workflow |
| Optimize (21 prompts) | `blog-rewrite`, `blog-seo-check`, `blog-geo`, `blog-schema`, `blog-audit`, `blog-factcheck` | When you want a specific optimization prompt (CTR audit, evidence-based quality follow-up, ChatGPT visibility, schema, PAA rewording, technical audit) for one-shot use |
| Win (3 prompts) | `blog-audit`, `blog-repurpose`, `blog-analyze` | When you want the BOFU page brief, conversion audit, or dual-surface scorecard for a specific URL |
| Prompts | (umbrella index) | When browsing all 30 blog-applicable prompts, including the 1 leverage-stage prompt that has no top-level command |
| Sync | (no skill consumes this) | When you want to refresh the synced FLOW reference files from the upstream repo |

The Leverage stage (off-site authority, 1 prompt) and Local stage (11 GBP/citation prompts) are intentionally not exposed as top-level claude-blog commands. Leverage is reachable through `/blog flow prompts`. Local is delegated to claude-seo.

## 5. What claude-blog adds beyond FLOW

- Visual media pipeline: AI image generation via Gemini (`blog-image`), inline SVG charts (`blog-chart`), Pixabay/Unsplash/Pexels integration. FLOW does not prescribe asset generation.
- Writing-persona system (`blog-persona`) for voice/tone profiles. FLOW is voice-agnostic.
- 5-category 100-point scoring (`blog-analyze`). FLOW provides quality bars but no numeric scoring.
- Topic-cluster execution engine (`blog-cluster`). FLOW prescribes content planning; claude-blog also executes clusters end-to-end with auto-interlinks.
- Multilingual publishing (`blog-multilingual`, `blog-translate`, `blog-localize`, `blog-locale-audit`). FLOW is single-locale by default.
- Audio narration (`blog-audio`). Not in FLOW scope.
- Google API integration (`blog-google`: PSI, CrUX, GSC, GA4, NLP, YouTube, Keywords). FLOW references measurement; claude-blog provides API tooling.
- Source-grounded research via NotebookLM (`blog-notebooklm`). Adjacent to FLOW's evidence discipline; provides the research side.
- CMS taxonomy sync (`blog-taxonomy`). Operational layer FLOW does not address.

These additions implement the FLOW principles in production tooling; they do not modify the principles.

## 6. When to consult this doc vs. the synced FLOW source

- This doc (`flow-alignment.md`): the orchestrator and any sub-skill loads this when the user asks "what does claude-blog do for AI citations / evidence / surfaces", to give a claude-blog-specific answer with skill names and routing.
- The synced FLOW source (`skills/blog-flow/references/flow-framework.md` plus 30 prompts): load when applying a specific FLOW prompt or quoting the framework verbatim. CC BY 4.0 attribution is required for any quote.
- The bibliography (`skills/blog-flow/references/bibliography.md`): load when verifying sources for a statistic.

Last updated 2026-07-23 for claude-blog v2.1.0.
