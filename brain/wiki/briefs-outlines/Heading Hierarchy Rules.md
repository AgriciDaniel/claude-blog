---
type: spoke
title: "Heading Hierarchy Rules"
domain: "Blog Briefs"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [briefs-outlines, serp-briefs, active]
---

# Heading Hierarchy Rules

## Heading Hierarchy Rules Rule Scope

This note defines how a brief turns reader intent into H1, H2, H3, and answer-block roles. It is not a keyword-stuffing guide. A heading hierarchy should help a human scan the article, help a drafter know the job of each section, and keep answer passages close to the evidence that supports them.

Use `g-helpful-content` for headings that promise useful, original value. `ziptie-aio-source-selection` supports keeping answer passages self-contained and easy to extract, with practitioner limits. `g-ai-opt-guide` blocks special AI-only markup or file requirements, and `g-faqpage-sd` keeps visible Q and A headings separate from retired FAQ rich-result tactics.

### H1 And H2 Jobs

The H1 states the article promise. H2s divide the reader's decision path into major tasks. Each H2 should either answer a must-know question, support comparison, explain evidence, or guide an action.

### H3 And Answer Block Jobs

H3s clarify sub-decisions under a larger section. Answer blocks must be readable as standalone passages without disconnecting from the article's evidence and caveats.

## Heading Enforcement Table

| Rule | Evidence source | Applies to | Exception path | Enforcement |
| --- | --- | --- | --- | --- |
| One H1 matches the reader job and article promise | `g-helpful-content`; [[Reader Job Statement]] | Whole outline | Brand or template title requires editor approval | Reject duplicate or vague H1s |
| H2s follow the decision path, not a competitor clone | `g-helpful-content`; [[Competitive Pattern Notes]] | Core outline | SERP pattern may inform order when reader need is explicit | Require stated section job |
| AI-facing answer headings avoid unsupported guarantees | `ziptie-aio-source-selection`; `g-ai-opt-guide` | Sections about AI Overviews, AI Mode, or citation readiness | None for guarantee language | Replace "get cited" with scoped eligibility wording |
| llms.txt headings cannot sell Google Search impact | `g-ai-opt-guide` | Technical or GEO sections | Non-Google use case may be noted with caveat | Send to [[Brief Risk Notes]] if disputed |
| Click-context sections separate visibility from traffic | [[Dual Optimization]] | Measurement or goal sections | First-party GSC data may override market framing | Add metric split before approval |
| H3s stay subordinate to one H2 question | [[Outline QA Checklist]] | Detailed subsections | Complex tutorials may use deeper levels sparingly | Merge or split drifting subsections |
| FAQ-style headings serve visible reader questions | `g-faqpage-sd` | Q and A sections | Use only when the page genuinely answers those questions | Do not imply FAQ rich-result value |
| Dated-update headings name the update source | `g-ranking-history` or [[2026 Google Update Timeline]] | Update, freshness, or volatility sections | Mention only confirmed rollout facts | Route impact claims to evidence review |
| Evidence-heavy H2s reserve source slots | [[Evidence Block Requirements]] | Statistics, policy, tool, or AI claims | Source slot can be empty only as blocked | Reject fact-heavy headings without proof |

## Exception Review And Rollback

1. Mark the heading that violates a rule and name the reason.
2. Decide whether the exception helps the reader or only serves a tactic.
3. Add the source ID and reviewer approval beside the exception.
4. Revert the heading if a later source refresh changes the allowed wording.

## Heading Repair Example

Before: "How to get cited in Google AI Mode." This heading promises an outcome the brief cannot control, so it fails the AI-feature wording rule. Source ID: `g-ai-opt-guide`.

After: "What makes an answer passage easier to understand and cite." This keeps the section focused on passage clarity while treating citation-readiness research as practitioner guidance. Source IDs: `ziptie-aio-source-selection`, `g-ai-opt-guide`.

## Hierarchy-Specific Failure Cases

- H2s mirror a competitor's article order instead of the reader's decision path. Source ID: `g-helpful-content`.
- H3s are keyword variants with no separate subtask. Source ID: `nng-editorial-heuristics`.
- A FAQ block is added for deprecated rich-result value. Source ID: `g-faqpage-sd`.
- A current-year heading lacks a dated source or refresh cue. Source ID: `g-ranking-history`.

## Outline Contract Wiring

[[SERP Outline Output Contract]] consumes the approved hierarchy. Inputs provided: H1 promise, H2 job, H3 subtask, answer-block role, source slot, and exception note. Expected output: an outline where every section has a reader task and evidence placement.

[[Blog Write Article Contract]] receives the same hierarchy through [[Brief To Draft Handoff]]. Expected output: the writer preserves section jobs instead of expanding headings into unsourced claims.

## Sources

- `g-helpful-content`
- `ziptie-aio-source-selection`
- `g-ai-opt-guide`
- `g-faqpage-sd`
- `g-ranking-history`
- `nng-editorial-heuristics`

## Related Routes

Use [[Search Intent Classification]] before ordering H2s, [[Evidence Block Requirements]] before adding fact-heavy headings, and [[Brief To Draft Handoff]] after the hierarchy is approved.
