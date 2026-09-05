# Security review brief

For security teams evaluating claude-blog before approving it for a Claude
Cowork, Claude Code, or Claude Desktop deployment. Everything here is checkable
against the source; where a claim is enforced by a test, the test is named.

Companion documents: [SECURITY.md](../SECURITY.md) (threat model, trust
boundaries, disclosure policy, audit history) and
[PRIVACY.md](../PRIVACY.md) (data handling).

## What the plugin is

Markdown instructions plus optional Python utilities. There is no compiled code,
no daemon, no telemetry, no analytics, no auto-update, and no phone-home.

| Component | Count | What it is |
|---|---|---|
| Skills | 28 | Markdown with YAML frontmatter |
| Agents | 5 | Markdown subagent definitions |
| References / templates | 27 | Markdown |
| Python scripts | 24 | Optional; only run when a skill needs live data |
| Node scripts | 1 | The opt-in MCP launcher described below |
| Hooks | **0** | The plugin registers no lifecycle hooks |

## Default posture: inert

A default install runs **no code and makes no network connections**. Installing
and enabling the plugin adds instructions to Claude's context, nothing more.
Every capability that touches the network or the filesystem beyond the user's
working folder is opt-in and off until a credential is supplied.

### The MCP server is gated

A plugin-root `.mcp.json` normally starts its servers the moment the plugin is
enabled. Pointing it at `npx @ycse/nanobanana-mcp` would mean every install
fetches and executes a third-party npm package unprompted. It does not:

```json
"command": "node",
"args": ["${CLAUDE_PLUGIN_ROOT}/scripts/nanobanana-launcher.mjs"]
```

`scripts/nanobanana-launcher.mjs` is 90 lines of dependency-free Node. It reads
the API key from the environment and, if unset, writes one line to stderr and
`process.exit(0)`. No network, no download, no child process. Only with a key
configured does it spawn the pinned version, with `shell: false` and the
credential passed through the environment rather than argv.

Enforced by `tests/test_security_guardrails.py::test_mcp_server_is_opt_in_via_launcher`,
which fails the build if `.mcp.json` ever invokes `npx` directly, if the version
floats to `latest`, if `shell: false` is dropped, or if the no-key exit path is
removed.

## Network egress

Nothing below happens unless the user invokes the specific command.

| Trigger | Destination | Purpose |
|---|---|---|
| `/blog google` | `www.googleapis.com`, `chromeuxreport.googleapis.com`, `language.googleapis.com`, `oauth2.googleapis.com`, `accounts.google.com` | PageSpeed, CrUX, Search Console, GA4, NLP, YouTube, OAuth |
| `/blog image` | Google Generative AI endpoints (via `google-genai` / nanobanana), `registry.npmjs.org` on first launch | Image generation |
| `/blog audio` | Google Generative AI endpoints (via `google-genai`) | Gemini TTS |
| `/blog notebooklm` | `notebooklm.google.com` | Browser-driven research |
| `/blog flow sync` | `api.github.com` **only** | Sync upstream FLOW prompts |
| First run of a script-backed skill | `pypi.org` | Create the skill's own venv |
| Research during writing | Whatever Claude's own web search/fetch reaches | Statistics and sources |

`scripts/sync_flow.py` is the one component that fetches content into the
plugin. It is hardened and test-enforced
(`test_sync_flow_security_invariants`): stdlib only, HTTPS only, host-allowlisted
to `api.github.com`, a 5 MB response cap, a path-traversal guard, `--dry-run`,
pinning via `--ref`, and a SHA-256 lock file
(`skills/blog-flow/references/flow-prompts.lock`) so fetched content is
verifiable.

If your environment uses an egress allowlist, the domains above are the complete
set. Blocking all of them leaves every writing, planning, schema, template, and
translation command fully functional.

## Credentials

- **Never** committed, never written into the plugin directory, never logged,
  never sent anywhere except the Google API they authenticate to.
- In Cowork: collected through the plugin's `userConfig`, marked
  `"sensitive": true`, so input is masked and the value goes to secure storage.
  Enforced by `test_user_config_marks_the_api_key_sensitive`.
- In Claude Code / Desktop: `~/.config/claude-seo/*.json`, written atomically at
  mode `0600`. Enforced by
  `test_google_auth_write_secret_atomic_sets_mode_0600` and
  `test_notebooklm_credential_files_contain_chmod_hardening`.
- The tracked `.mcp.json` may only contain `${...}` placeholders; a literal
  value fails `test_tracked_mcp_json_carries_no_literal_credential`.
- `.gitignore` blocks `.mcp.json` recursively with exactly one negation for the
  plugin-root file, verified by `test_mcp_json_is_gitignored`.
- `scripts/package_plugin.py` refuses to build an archive containing anything
  credential-shaped (`*.pem`, `*.key`, `service_account.json`, `.env`, …).
- `uninstall.sh` / `uninstall.ps1` purge stored OAuth tokens and API config.

## Least privilege

**Agents** declare explicit tool allowlists. No agent has `Bash` - enforced by
`test_no_bash_tool_in_any_agent_frontmatter`. The reviewer and translator agents
are read-only or write-only-to-content by construction.

**Skills** declare no `allowed-tools`, so no skill silently pre-approves a tool
for the turn that invokes it; every tool call goes through the host's normal
permission prompts. Enforced by `test_no_allowed_tools_field_in_skills`.

**Hooks:** none. The plugin cannot intercept your tool calls, read your prompts
outside its own invocation, or run anything on session start.

**Filesystem:** skills read plugin content through `${CLAUDE_PLUGIN_ROOT}` and
write deliverables into the user's working folder. Plugin state that must
survive updates goes to `${CLAUDE_PLUGIN_DATA}`. No skill writes into the plugin
directory - enforced by
`tests/test_plugin_portability.py::test_no_skill_writes_into_the_plugin_directory`.
In Cowork this is bounded further by the sandbox: Claude reaches only the
folders the user mounts.

## Supply chain

- Python dependencies are version-bounded in `pyproject.toml` and pinned with
  hashes in `requirements.lock`; per-skill venvs install with
  `pip install --require-hashes` where a lock file exists.
- The npm package is pinned to an exact version, never `latest`.
- Installers do **not** install Python packages by default. That is opt-in via
  `CLAUDE_BLOG_INSTALL_DEPS=1`, so nothing lands in a user's environment
  unannounced.
- `patchright` (a stealth-fork of Playwright) is used only by
  `/blog notebooklm`. It is dual-use; the rationale and the decision not to
  bundle it by default are documented in [SECURITY.md](../SECURITY.md).

## Reviewing and pinning a build

The recommended path for a reviewed deployment never pipes a downloaded script
into a shell:

```bash
git clone https://github.com/AgriciDaniel/claude-blog.git
cd claude-blog
git checkout v2.3.0            # pin an exact reviewed tag

python3 -m pytest tests/       # 60 guardrail + unit tests
python3 scripts/package_plugin.py
# prints the SHA-256 of the artifact you are about to distribute
```

Distribute `dist/claude-blog-<version>.plugin` internally and record the hash.
Users install it through *Plugins > Add plugin > Upload*, which pins them to the
build you reviewed rather than whatever a marketplace currently serves.

To audit what a user is actually running:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/runtime_capabilities.py" --json
```

It reports which capabilities are live and whether a credential is present. It
never prints credential values, makes no network calls, and writes nothing.

## Known limitations, stated plainly

- **Claude follows instructions, including from the web.** Content that
  `/blog factcheck` or the researcher agent fetches is untrusted input. The
  agents have no `Bash` and narrow tool lists specifically to bound this, but
  prompt injection through fetched pages is a real residual risk for any agent
  that reads the web. Treat generated drafts as drafts.
- **`/blog notebooklm` automates a browser against a Google property.** Confirm
  this is acceptable under your acceptable-use policies before enabling it.
- **The plugin cannot restrict what Claude does with your files** beyond the
  host's own permission model and, in Cowork, the folder sandbox. Mount the
  narrowest folder that gets the job done.
- **No formal third-party audit.** The audit history in
  [SECURITY.md](../SECURITY.md) is self-conducted, with findings and fixes
  itemized.

Report a vulnerability through the process in [SECURITY.md](../SECURITY.md).
