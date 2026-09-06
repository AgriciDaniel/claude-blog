# Contributing to claude-blog

Thank you for your interest in contributing to claude-blog!

## Getting Started

1. Fork and clone the repository
2. Install dev dependencies: `pip install -e ".[dev]"`
3. Run tests: `python -m pytest tests/ -v`
4. Validate plugin metadata: `claude plugin validate .`

## Development

### Project Structure

```
claude-blog/
├── .claude-plugin/          # Plugin metadata
│   ├── plugin.json          # Manifest
│   └── marketplace.json     # Marketplace catalog entry
├── skills/
│   ├── blog/                # Main orchestrator + references + templates
│   ├── blog-write/          # User-facing sub-skill
│   ├── blog-chart/          # Internal-only sub-skill
│   ├── blog-rewrite/
│   └── ...                  # 31 sub-skill dirs: 30 user-facing + 1 internal
├── agents/                  # 5 specialized agents
├── scripts/                 # 14 root-level Python helper scripts
├── tests/                   # pytest test suite (security guardrails + script tests)
├── docs/                    # Documentation (installation, commands, architecture, templates, troubleshooting, MCP)
└── .github/workflows/       # CI pipeline
```

### Making Changes

- **SKILL.md frontmatter** must include `name` and `description`. Optional valid fields: `user-invocable`, `argument-hint`, `license`, `compatibility`, `metadata`, `disable-model-invocation`. Do NOT add `allowed-tools` (not a valid Claude Code spec field; the `tests/test_security_guardrails.py` test enforces).
- **Reference paths** in sub-skills use `references/` (relative to installed location) OR full repo-root paths like `skills/blog/references/X.md` for cross-skill references.
- **Template paths** in sub-skills use `templates/` (relative to installed location).
- **Agent frontmatter** must NOT include `Bash` in the `tools` list (blast-radius reduction for prompt-injection surfaces; enforced by tests).
- Run `python -m pytest tests/ -v` before submitting.
- Run `claude plugin validate .` before submitting.

### Code Style

**Python (scripts/, skills/*/scripts/):**
- Python 3.11+. Use `from __future__ import annotations` in new files for forward-compatible type hints.
- Stdlib-only for new scripts unless a hard dependency is justified. Existing scripts use `argparse`, `json`, `pathlib`, `datetime`, `re`, `collections`, `sys`.
- CLI shape: docstring (with Usage block) + argparse + `--format json|markdown` flag + return-code int.
- File I/O: use `pathlib.Path`, NEVER unrestricted user paths. Validate via the `_validate_input_path` / `_validate_output_path` helpers in `scripts/discourse_research.py` (refuses symlinks, enforces size cap, checks regular file).
- Exception handling: catch specifically (`FileNotFoundError`, `json.JSONDecodeError`, `ValueError`); avoid bare `except:` (test enforces).
- Tests live in `tests/test_<module>.py` mirroring the script name; follow the `test_cognitive_load.py` and `test_discourse_research.py` patterns (subprocess invocation; happy / empty / contract tests).

**Prose (SKILL.md, references/, docs/, CHANGELOG.md, CONTRIBUTORS.md):**
- **No em dashes or en dashes** (U+2014, U+2013, or ASCII ` -- `). Use periods, commas, semicolons, colons, or parentheses. Em dashes are the strongest AI-content tell and the project deliberately avoids them. Exception: pedagogical use inside backticks (e.g. when documenting the character itself).
- Inline citations as `[name](url)` markdown links (LAW 5 of `skills/blog/references/synthesis-contract.md`).
- No invented titles for sources (LAW 2).
- No trailing "Sources" block when sources are already cited inline (LAW 1).
- Tables and bullet lists where structure helps; prose where prose helps.

**Commit messages:**
- Conventional commits style: `type(scope): subject`. Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `security`.
- Examples used in the project: `fix(lint):`, `docs(security):`, `chore(release):`, `feat(blog-discourse):`.
- Subject line under 72 characters.
- Body explains WHY, not WHAT (the diff shows what).

### Security expectations

- Read `SECURITY.md` for the project's threat model and trust boundaries.
- Treat any new untrusted-data path (file from user, network response, agent output, project-root file) as crossing a trust boundary. Fence content explicitly (see `agents/blog-researcher.md` for the WebFetch pattern; see `skills/blog/SKILL.md` "Untrusted-Data Contract" section for the project-root pattern).
- **Project-root file loading (BRAND.md / VOICE.md / DISCOURSE.md and any future additions)**: use `scripts/load_untrusted_root.py` via Bash; do NOT hand-roll a fence in the orchestrator's own token output. The helper generates CSPRNG nonces, scans for instruction-shaped patterns, emits mtime provenance, and refuses symlinks via `O_NOFOLLOW`. Adding a new project-root file means: (a) add its basename to `ALLOWED_BASENAMES` in `scripts/load_untrusted_root.py`, (b) add behavioral tests in `tests/test_load_untrusted_root.py`, (c) document the new T12 surface in `SECURITY.md`. Hand-rolled fences re-introduce the documentation-only state v1.8.3 closed.
- **Prose hygiene**: `scripts/lint_prose.py` enforces CONTRIBUTING.md prose rules (no em-dashes / en-dashes / ASCII double-hyphen) on every PR via CI. Run locally with `python3 scripts/lint_prose.py` before pushing.
- Credentials, API keys, tokens: NEVER hardcoded. Use environment variables; store files at mode 0o600 with atomic write (see `skills/blog-google/scripts/google_auth.py` `_harden_perms` pattern).
- New CLI scripts must enforce size caps (DoS guard) and refuse symlinks (CWE-59) on any path argument.

### Pull Requests

1. Create a feature branch from `main`.
2. Make your changes with clear conventional-commit messages.
3. Ensure all tests pass (`python -m pytest tests/`).
4. Ensure plugin validates (`claude plugin validate .`).
5. Update `CHANGELOG.md` with an `[Unreleased]` entry describing the change.
6. Submit a PR using the template. Fill in: type of change, linked issue, test plan, docs checklist, and security checklist (if applicable).

## Reporting Issues

- Bugs / feature requests: open an issue at https://github.com/AgriciDaniel/claude-blog/issues (templates in `.github/ISSUE_TEMPLATE/`).
- Questions and ideas: use [GitHub Discussions](https://github.com/AgriciDaniel/claude-blog/discussions).
- Security disclosures: see [SECURITY.md](SECURITY.md) for the private reporting channel; do NOT open public issues for vulnerabilities.
