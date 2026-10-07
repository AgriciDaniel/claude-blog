# Repair and verification follow-up, 2026-10-07

This pass follows the [first audit](AUDIT-2026-10-07.md) and draft PR 86.
Public main remains `2500d4c765034864cede2bf215d00ccd4d7d6fb8`. Work stays
under Unreleased, with no merge, release or installed-profile migration.
The plugin identifier change to `blog-engine` was explicitly selected by the
repository owner. The GitHub repository and marketplace retain their names.

## Host and runtime repairs

All 32 skills use canonical `user-invocable` metadata. A shared safe-YAML
validator distinguishes documented host fields from repository policy and
checks all five bundled agents. Skill permission preapproval and agent tool
allowlists are documented separately. Helpers, references and templates follow
trusted installed roots; unrelated working directories cannot select them.

Audio, Google and NotebookLM accept an optional absolute persistent runtime
root. FLOW sync and reads share an optional persistent reference root. Existing
standalone defaults remain available. Ordinary reads do not install, log in,
move state or sync upstream. Disposable fixtures cover upgrades, spaces,
missing roots, drift, symlinks and poisoned working directories.

## Source and Brain repairs

All 125 prior source records received content-based dispositions. Five primary
sources were added, leaving 127 active reviewed records and three retired
records. Decisions are 61 correct, 26 qualify, 40 retain and three retire.
The review pack preserves 97 distinct normalized content captures, excerpts,
hashes and per-source decisions. Publication, retrieval, review and retirement
dates are separate; the historical ledger-wide date remains unchanged.

The shared evidence gate prevents retired, unverified or expired sources from
supporting current advice in adapters or wiki notes. Failed live retrievals
do not overwrite prior reviews. Qualified source limitations travel into
reports. The offline check validates recorded review evidence; the separate
capture checker verifies actual artifact hashes and excerpts. Neither
automated check alone proves semantic entailment. Immutable `.raw/` snapshots
remain intact.

The lead's executable whole-Brain audit passes at 98/100 with no critical
failures or warnings, including tests, pipeline, source review, vault lint and
disposable packaging. A separate run passes 23 adapter regressions. This is
an internal local readiness result, not authenticated provider verification,
publication approval or a prediction of content performance.

## Verification evidence

The root suite passes 656 tests on each of Python 3.11, 3.12 and 3.14, with
one expected private-only skip per run. Prose, consistency, public-distribution,
skill metadata, current plugin validation, lock agreement, projection,
actionlint and diff checks pass. The live Google check reports current against
the official October 1 documentation feed and September 24 ranking incident.

Native Claude Sonnet 5.5 high loads `blog-engine:blog` from the isolated
checkout and selects all 63 expected routes: 30 advertised commands,
26 aliases, four natural-language requests and three unrelated requests.
This proves route selection, not execution of every routed workflow.

Controlled same-model writing uses four closed briefs and blinded evaluation.
Single-pass native drafts exposed factual errors in worked examples and
conditional claims, so they are retained as failed artifacts. Claim-fidelity
guidance was strengthened. Both revisions then received one native correction
round using the same protocol and only their own factual review findings.
A fresh blind evaluator accepts all four corrected candidate articles and
prefers them in all four pairs; two corrected baseline articles remain blocked,
including a 483-word response exceeding the brief. This small, reviewed sample
does not erase first-pass failures or establish a general writing guarantee.
Publication still requires the independent
reviewer's score of at least 90, no uncleared P0 issues, the matching nonce
and a valid nonblocking decision.

Three actual native `blog-engine:blog-reviewer` cases verify blocked handling
of fabricated claims, missing trusted paths and absent browser evidence.
Matching nonces reach the review decision; separate mismatched-nonce probes
fail provenance validation. The native agent exposes only Read, Grep and Glob,
and treats fenced bypass/publication instructions as article data. These are
negative recovery cases, not proof of a full publishable native delivery.

Matching isolated Patchright 1.63.0 and Chromium 153.0.8010.12 exercise the
renderer through its default launch path, without a host-browser override.
PNG, JPG, JPEG and WebP heroes pass format, visual, schema and link gates at
375, 768 and 1280 pixels in light and dark mode. Representative screenshots
and both PDF pages were inspected. Link and byline contrast corrections have
focused regressions and actual-browser checks above 4.5 for the observed normal
text. WeasyPrint 70 also renders the same fixture, with all three PDF pages
inspected. Pagination differs between engines. This is not a full accessibility
conformance audit.

## Remaining verification boundaries

- The current native Windows and macOS installer jobs await updated-PR CI.
  Linux exercises use disposable profiles and preserve user additions.
- Authenticated Google, Gemini and NotebookLM operations are unverified.
  Offline fixtures and SDK smoke checks do not establish real API operation.
- The optional image MCP package still exposes retired preview IDs; use the
  documented direct API or stock-image route. No compatible upstream update
  was established.
- NLTK 3.10.3 retains the upstream model-artifact advisory
  GHSA-8mgp-746c-j5xp without a reviewed patched release. Affected persistence
  calls were not observed in the readability path. Dependency audit results
  are not advisory-free.
- Legacy Google and NotebookLM error JSON may retain exit 0 for compatibility;
  callers must inspect error fields.

The audit pack includes revisions, coverage, backlog dispositions, commands,
raw logs, source captures, native traces, rendering artifacts and preservation
checks. Discarding the isolated branch or reverting its commits restores the
prior implementation; preserve the pack before archiving the worktree.
