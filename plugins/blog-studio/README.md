# Blog Studio

Blog Studio is an optional companion to `claude-blog`. It adds a compact article
status band, a live pipeline and five-gate review panel, a history of past blogs,
and an explicit **Run checks** control.
Version 0.2.0. It ships in the claude-blog repository as a second plugin of the
same marketplace, and it is not part of the `claude-blog` plugin itself.

## Install

```
/plugin marketplace add AgriciDaniel/claude-blog
/plugin install blog-studio@agricidaniel-blog
```

Neither the core plugin nor the standalone installers enable it, and nothing
loads until you install it.

## Use

Blog Studio is a Claude Code mod (function-hook plugin), so it needs a Claude Code
release with mods support. It was developed and checked on the Linux CLI,
2.1.294 to 2.1.296. The panel uses host theme colors and the shared
terminal/Desktop element set. Desktop fixture tests do not establish native
Desktop support. Codex does not run Claude Code mods.

Once installed:

1. Configure the absolute scripts directory from a trusted engine installation
   using `/blog-studio configure /path/to/claude-blog/scripts`. It is remembered for
   every session and project until `/blog-studio configure reset`. Setting the
   existing `CLAUDE_BLOG_SCRIPTS_DIR` before starting a session overrides it. The directory
   must include both `blog_preflight.py` and `blog_studio_status.py`.
2. Select an existing project-relative article directory with
   `/blog-studio select outputs/article`. Spaces in the directory are accepted
   literally; do not wrap the path in shell quotes.
3. Open `/blog-studio`, then choose **Refresh** or **Run checks**. Refresh only
   inspects saved evidence. Run checks invokes the existing strict five-gate
   preflight, including its browser and public-link checks.

Python 3.11 or newer must be available as `python3` on PATH with the engine's
already-installed optional dependencies. The mod never installs them. Configure
PATH before the session to select a virtual environment. No shell is used.

| Command | Behavior |
|---|---|
| `/blog-studio` | Open the pipeline and gates panel, or show the text fallback |
| `/blog-studio status` | Show cached state, last check time and the pipeline line |
| `/blog-studio history` | List past blogs from every project, newest first, with date, time, status and gate count |
| `/blog-studio history scan [folder]` | Backfill the history from `preflight-report.json` files under a folder (default: this project) |
| `/blog-studio open <number>` | Select a blog from the history, in this or another project |
| `/blog-studio demo` | Show a sample pipeline mid-draft, to judge the design without an agent |
| `/blog-studio reset` | Clear the pipeline view |
| `/blog-studio select <directory>` | Select a project-relative draft |
| `/blog-studio configure <scripts>` | Pin trusted absolute engine helpers |
| `/blog-studio refresh` | Inspect files and saved evidence without network or writes |
| `/blog-studio check` | Run all strict preflight gates, then verify the saved run |

The panel includes Select draft, Refresh, Run checks, and Close. Escape closes
the panel. Duplicate runs are refused. Checks time out after ten minutes and
status inspection after thirty seconds. Selection and cached results clear on
workspace/session changes, clear, resume, and branch. Reload keeps a selection
only in the same workspace/session and invalidates cached and in-flight results.
A run already started may finish writing its selected draft after a clear or
workspace switch; its result cannot populate the new session's panel.
The companion passes `--project-root` to the checker. On Linux, the checker
opens the selected directory through descriptors without following symlinks
and anchors its working directory there. Replacing the selected path after
launch cannot redirect its report writes to a different directory.

## The live pipeline

While the agent writes a blog, the band and panel follow it through seven stages in
order: Research, Outline, Draft, Visuals, Render, Review and Gates. The band is one
row: a progress bar, a stage rail (`✓` done, `▸` working, `·` waiting, `✗` failed) and
a clock. It shortens itself on narrow terminals and yields to surveys and other bands.

The stages are **inferred**, never claimed. Blog Studio watches tool calls read-only
and without any model call: web search and fetch, writes of Markdown, SVG and image
files, the `blog-researcher`, `blog-writer`, `blog-reviewer` and `blog-seo` subagents,
and the engine scripts `generate_hero.py`, `blog_render.py` and `blog_preflight.py`.
A stage is marked done when a later one starts, or when the preflight evidence proves
it. Evidence always wins over inference, and a passing preflight marks every stage
verified. A failing render or preflight command marks that stage failed. When the agent
writes a draft outside the selected folder, the panel offers it as "Use this draft".

Colors are host theme keys only, so light and dark themes both work. Every status also
has its own glyph and word, so nothing depends on color alone.

## History of past blogs

Every blog Blog Studio sees is recorded in the mod's own machine-wide store, newest
activity first: drafts the agent writes, drafts you select, and drafts you check (with
their result). The panel lists the latest five under **Recent blogs**, with a date, time,
status glyph and gate count; **All blogs (h)** shows 25. Keys 1 to 9 open an entry.
`/blog-studio history scan <folder>` adds older blogs from their delivery reports, dated
by the report's file time. History holds paths and results only, never article text.

A blog from another project is re-validated before it opens: absolute root, relative
draft, and no symlinks anywhere on the path. Checks then run anchored to that project,
and the panel shows its root. A stored record that fails validation is dropped.

## Reading the results

**Preflight passed** means the saved run was strict, requested and completed all
five gates, and its local input/output fingerprints still match. It describes
that recorded check, not publication approval or continuing network availability.
Run Refresh after edits made outside Claude. Starting a new turn clears cached
proof, and turn completion performs a read-only refresh for the selected draft.

Other states are Blocked, Partial, Stale, Unverified, Running, and Execution
error. Later gates after a fail-fast blocker remain Not checked. Legacy reports
are readable, but freshness is Unverified. Single-gate passes and preview runs
cannot become full preflight success. Missing helpers, malformed output,
truncation, crashes, timeouts, and mismatched run identities remain visible.

The panel displays gate diagnostics, reviewer score, and relative artifact
paths. It does not read the article body for display, reveal the review nonce,
write a review, rotate verifier state, reset repair counters, or repair articles.
The analyzer's configurable 70-point gate and the separate delivery requirement
(score at least 90, zero uncleared P0 issues, valid matching nonce and nonblocking
decision) stay in the core engine. Manual checks do not consume repair iterations.

## Evidence format

`preflight-report.json` keeps its existing fields and adds `evidence`, version 1:
run identity, UTC start/end times, requested/completed gates, contract version,
engine identity, input fingerprints, an unchanged-input flag, and generated
output fingerprints. Existing stdout modes, flags and exit statuses remain.

The input snapshot conservatively includes regular files below the selected
draft, including local CSS, scripts, images, fonts and review/config files.
It excludes `preflight-report.json`, `capabilities.json`, `.iteration-count`,
the four canonical screenshots under `preview`, and temporary files for those
generated reports. Other resources below `preview` remain fingerprinted inputs.
The verifier state is fingerprinted outside the draft without exposing its
contents. Engine scripts and the delivery contract/reviewer instructions are
fingerprinted too. Python runtime changes invalidate saved evidence.

Hashing streams large files. Limits are 4,096 files and 512 MiB per snapshot,
with a 1 MiB report limit. Symlinks, unsupported file types, unavailable files,
and limit exhaustion cannot establish freshness. Generated capabilities and
preview artifacts receive a separate post-run snapshot.

Fingerprints are freshness evidence, not signatures. An actor able to forge
reports can forge metadata. Delivery still requires the canonical preflight and
review process; the UI does not add an approval authority.

## Capability footprint

The module registers only session lifecycle, turn lifecycle, its own command,
and Pane/AbovePrompt rendering hooks. It reads the pinned scripts environment
variable, path metadata, session root/id/surfaces and tool names. It stores
session-scoped plain state and starts only the configured Python helpers with
fixed argument vectors. Render handlers only read cached state and draw.

There are no tool permission hooks, prompt rewriting, transcript reads, model
calls, HTTP calls, cross-session messaging, automatic dependency installation,
or persistent configuration changes. The checker retains its own existing
rendering and network behavior. The status band composes with other mods and
yields to surveys or slots too small to share.

Mods run with the user's permissions. A disposable project is not isolation.
Read `hooks/` before installing, as with any plugin, and try it first in a project without secrets if you want extra margin.
[Official permissions guidance](https://code.claude.com/docs/en/plugins/mods/overview)

## Development and acceptance gates

The [manifest](.claude-plugin/plugin.json) and [hook entry](hooks/hooks.json)
define the optional package. Its [development dependencies](package.json) and
[lockfile](package-lock.json) stay separate from the core. The
[source pin](dev/types-source.json) identifies the public reference declarations;
[reference](tsconfig.reference.json) and [native](tsconfig.json) configurations
keep the two type checks distinct.

```bash
npm ci --ignore-scripts --no-audit --no-fund
npm run typecheck:reference
claude plugin validate --strict --json .
claude plugin test .
```

The reference type check covers production code using hash-pinned official
public 2.1.277 declarations, plus a small explicitly provisional state-method
contract. That public file predates the current state API. The reference check
does not type-check test-kit code against an obsolete kit contract. The actual
2.1.294 test kit executes those tests without a session, sign-in, or network.
[Official testing documentation](https://code.claude.com/docs/en/plugins/mods/test)

Fresh host-generated 2.1.294 typings are a separate required native gate:

```bash
npm run typecheck:native
```

This command requires the generated `.claude-plugin/types/claude-code/index.d.ts`
with the exact target build header, and checks production plus test code without
the provisional reference shim. Do not substitute old captures or change their
version header. Generated types and development dependencies are ignored and
excluded from maintained-source scans.

Still open (honest status): native acceptance on your own terminal theme and
glyphs, pane height on very tall terminals, reload and branch/resume behavior
under real agent work, and the Desktop app (fixture tests only). Do not describe
fixture drawings as native paint.
[Official Mods reference](https://code.claude.com/docs/en/plugins/mods/reference)

Rollback is `/plugin uninstall blog-studio@agricidaniel-blog`. Nothing else in the
profile is touched, and the stored history is per plugin and holds paths and
results only, never article text.
