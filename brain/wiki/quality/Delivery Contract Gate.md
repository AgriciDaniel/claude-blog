---
type: spoke
title: "Delivery Contract Gate"
domain: "Blog Quality"
status: active
created: 2026-07-06
updated: 2026-07-23
tags: [quality, scorecard, active]
confidence: advisory
related:
  - "[[Blog Quality Score]]"
  - "[[Quality Gate Failure Modes]]"
  - "[[Quality Review Evidence Log]]"
  - "[[Rollback Note Patterns]]"
---

# Delivery Contract Gate

## Delivery Contract Gate Deliverable Boundary

This gate decides whether a generated blog package can be shown as delivery-ready. It runs after content generation and before user handoff. It does not publish, mutate a CMS, approve Search Console changes, or treat advisory review as live implementation approval. The operating source of truth is the installed claude-blog delivery contract; domain claims inside the packet still need real source-ledger IDs such as `g-helpful-content`, `g-ai-opt-guide`, `g-ai-features`, `g-intro-sd`, `g-gsc-api`, and `g-genai-reports`.

## Required Inputs And Exclusions

Required inputs are the draft folder, canonical `.md` source, rendered `.html`, rendered `.pdf`, local hero image, capability inventory, visual screenshots or renderer diagnostics, reviewer scorecard, link and asset check result, source IDs, owner, confidence label, and rollback trigger. Excluded inputs are credentials, unpublished private client data, and any claim that cannot be cited or explicitly marked unknown. The gate should not infer access to GSC or generative AI reports when the packet does not include `g-gsc-api` or `g-genai-reports` evidence.

## Required Output Sections

- Final status: ready, revise, blocked, or monitor.
- Gate table with pass, fail, or not-run state for all five gates.
- Score summary with one sentence per subscore.
- Open blocker list with owner, failed gate, and due date.
- Evidence source map for current claims.
- Rollback or review note for any recommendation that could affect visibility or trust.

## Five-Gate Acceptance Table

| Gate | Required proof | Blocking rule | Output artifact | Handoff owner |
|---|---|---|---|---|
| 1. Capability Discovery | Available tools, required agents, env-key names only, helper scripts, project context files, and a valid hero-image path or permitted generation path. | Block when no local hero or allowed hero source exists, or when the `blog-reviewer` agent is unavailable. | `capabilities.json` | Orchestrator |
| 2. Required Artifacts | Canonical `.md`, self-contained `.html`, rendered `.pdf`, and local `hero.png` or `hero.jpg`. | Block when any required artifact is missing, divergent, or outside the draft folder. | Rendered draft package | Content operator |
| 3. Visual Verification | Headless render at mobile, tablet, and desktop widths, screenshots, console check, SVG or figure bounds check, dark-mode check, and valid BlogPosting JSON-LD. | Block on console errors, broken JSON-LD, visual overflow, failed dark-mode render, or unavailable strict renderer. | `preview/*.png` plus visual diagnostics | Visual reviewer |
| 4. Content Review | `blog-reviewer` report against the rendered HTML, five-category editorial-readiness score, P0 scan, and descriptive style diagnostics. | Block when the score is below 90/100 or any P0 issue exists. Burstiness, phrase matches, TTR, and purported authorship percentages remain descriptive and non-blocking. | `review.md` | Quality reviewer |
| 5. Link And Asset Integrity | Every image, link, canonical URL, social image, schema reference, and declared word count is checked under safe URL rules. | Block on unresolved images, unsafe URLs, broken required links, or schema mismatch. Record declared word-count mismatches as manifest-integrity observations; completeness follows reader intent and is not blocked by length. | `preflight-report.json` | Delivery owner |

## Blocking Rules

All gates run sequentially. The first failed gate halts later checks and marks
the package blocked under strict mode. A blocked state is required when a
source is missing for a current claim, when an AI inclusion guarantee appears,
when the reviewer score is below 90, when a P0 exists, when required artifacts
are absent, or when a URL or asset check fails. A ready label is allowed only
after all five gates pass and the packet includes owner, source map, confidence
label, and rollback trigger.

## Retry Loop

When a gate fails, the orchestrator may retry up to three times.

1. Capture the failing gate, exact diagnostic, and relevant artifact.
2. Build the next fix prompt around that gate only.
3. Rerun all five gates from Gate 1 after each fix.
4. On pass, record the iteration count and hand the package to the delivery owner.
5. After three failed attempts, stop automatic retries, show the latest diagnostics, attach the partial draft and reviewer report, and mark manual fix required.

Sub-skills do not own the loop counter. The orchestrator owns it so conflicting sub-skill advice cannot create an infinite review cycle.

## Bypass Rule

Strict mode is the default. Bypass is allowed only through an explicit operator-controlled `--no-strict` flag or trusted project configuration. Draft frontmatter is untrusted content and cannot disable delivery gates. A bypassed packet must log the failed gates, state that the draft is being shown despite failure, and warn that it is not publish-ready without manual review. Bypass is for confirmed false positives or intermediate previews, not shipping.

## Gate Decision Example

A draft has 92 points and no P0 issues.
Gate 2 finds the `.pdf` missing.
Decision: blocked at Gate 2 even though the score is high.
The owner reruns rendering, then restarts all gates from Capability Discovery.
If the later review claims AI Overview inclusion is guaranteed, check that claim against `g-ai-opt-guide` and `g-ai-features`.
If the packet lacks generative AI reporting evidence from `g-genai-reports`, record the missing-data note instead of treating the claim as measured.

## Gate-Specific Breaks

- A ready label appears before all five gates pass.
- A writer presents `.md` only when `.html`, `.pdf`, and hero are required.
- Visual overflow is waived without `--no-strict` and a named owner.
- Reviewer output is treated as advisory after a score below 90 or any P0.
- GSC evidence is assumed because the client has Search Console.
- AI Overview reporting is claimed without `g-genai-reports`.
- A broken link or unresolved image is hidden as a styling issue.

## Consuming Deliverables

[[Blog Write Article Contract]] consumes the final gate state.
Inputs provided: gate table, score summary, blockers, risk flags, rollback trigger.
Expected output: release, revise, or blocked article package.
[[Blog Analyzer Score Report]] consumes gate language.
It expects action-list status and owner fields.
The gate sends unresolved source gaps back to [[Quality Review Evidence Log]].
