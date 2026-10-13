# Gemini Notebook (formerly NotebookLM) Troubleshooting Guide

Google renamed NotebookLM to Gemini Notebook on 2026-07-16
(https://blog.google/innovation-and-ai/products/gemini-notebook/notebooklm-gemini-notebook/).
The legacy host `notebooklm.google.com` answered with a 301 redirect to
`notebook.google.com` on 2026-10-12; the scripts accept both hosts. Help
articles live at https://support.google.com/gemininotebook/.

## Ground rules

- Resolve the runner once and use it everywhere. Never run a relative
  `scripts/run.py` from the current project:
  ```bash
  BLOG_SKILLS_DIR="${CLAUDE_BLOG_SKILLS_DIR:-${CLAUDE_SKILL_DIR}/..}"
  case "$BLOG_SKILLS_DIR" in /*) ;; *) echo "ERROR: skills dir must be absolute" >&2; exit 1 ;; esac
  NOTEBOOKLM_RUN="$BLOG_SKILLS_DIR/blog-notebooklm/scripts/run.py"
  ```
- No implicit installs. The runner never creates a venv, installs packages,
  or installs Chrome. Only explicit setup (`setup_environment.py` without
  `--check`, run with the user's yes) may do that.
- Do not delete `.venv`, `data/`, or any browser state on your own. Describe
  the step and let the user approve it.

## Quick Fix Table

| Error | Solution |
|-------|----------|
| ModuleNotFoundError | Use the trusted `run.py` wrapper; if it reports setup required, ask the user to run explicit setup |
| Not authenticated | `python3 "$NOTEBOOKLM_RUN" auth_manager.py setup` (browser visible) |
| Browser crash | Close the skill browser window, cleanup with `--preserve-library`, re-auth |
| Usage limit reached | Check Settings > Usage in Gemini Notebook; wait for the limit to reset or ask the user about a higher plan |
| Notebook not found | Check with `notebook_manager.py list` |
| Query timeout | Retry with simpler question or `--show-browser` to debug |

## Authentication Issues

### Not authenticated error
```bash
python3 "$NOTEBOOKLM_RUN" auth_manager.py status   # Confirm status
python3 "$NOTEBOOKLM_RUN" auth_manager.py setup     # Browser visible for login
```
User must manually log in to Google in the browser window.

### Authentication expires frequently
```bash
python3 "$NOTEBOOKLM_RUN" cleanup_manager.py --confirm --preserve-library
python3 "$NOTEBOOKLM_RUN" auth_manager.py setup     # Fresh login
```
Uses hybrid auth: persistent browser profile + cookie injection
(workaround for Playwright bug #36139).

### Google blocks automated login
1. Use a dedicated Google account for automation
2. Browser is ALWAYS visible during setup (no headless auth)
3. Complete any 2FA challenges in the browser window

## Browser Issues

### Browser crashes or hangs
Close the Chrome window opened by this skill, then run:

```bash
python3 "$NOTEBOOKLM_RUN" cleanup_manager.py --confirm --preserve-library
python3 "$NOTEBOOKLM_RUN" auth_manager.py reauth    # Re-authenticate
```

### Browser not found
The runner does not install Chrome. Report "setup required" and, with the
user's explicit yes, run the explicit setup, which owns the Chrome install
for Patchright:
```bash
python3 "$BLOG_SKILLS_DIR/blog-notebooklm/scripts/setup_environment.py"
python3 "$NOTEBOOKLM_RUN" auth_manager.py status
```

### Timeout waiting for selector
NotebookLM UI may have changed CSS selectors. Check `config.py` for
current selectors (`QUERY_INPUT_SELECTORS`, `RESPONSE_SELECTORS`).
Use `--show-browser` to visually debug.

## Rate Limiting

### Usage limit reached

Google documents Gemini Notebook limits as compute-based (they depend on
prompt complexity, features, and chat length) and as multiples of the
standard limit by plan: AI Plus 2x, AI Pro 4x, AI Ultra 5x or 20x of Pro
(https://support.google.com/gemininotebook/answer/17670842, read
2026-10-12). It publishes no fixed per-day number there, so treat any old
"50 per day" figure as unverified.

**Option 1: Wait** for the limit to reset. Stop asking follow-ups.

**Option 2: Switch accounts** (only with the user's yes; this clears auth)
```bash
python3 "$NOTEBOOKLM_RUN" auth_manager.py clear
python3 "$NOTEBOOKLM_RUN" auth_manager.py setup     # Login with different account
```

## Notebook Access Issues

### Notebook not found in library
```bash
python3 "$NOTEBOOKLM_RUN" notebook_manager.py list
python3 "$NOTEBOOKLM_RUN" notebook_manager.py search --query "keyword"
```

### Wrong notebook being queried
```bash
python3 "$NOTEBOOKLM_RUN" notebook_manager.py list            # Check active
python3 "$NOTEBOOKLM_RUN" notebook_manager.py activate --id correct-id
```

## Virtual Environment Issues

### ModuleNotFoundError
Always call scripts through the trusted `run.py` wrapper. If it reports that
the managed environment is absent or stale, ask the user to approve explicit
setup, which creates or refreshes it from the hash-locked requirements:
```bash
python3 "$BLOG_SKILLS_DIR/blog-notebooklm/scripts/setup_environment.py"
```

### Corrupted venv
Re-run the explicit setup above first; it rebuilds the environment when the
dependency stamp is stale. Only if that fails, tell the user which managed
`.venv` directory is broken (`setup_environment.py --check --json` reports
`venv_exists`) and let them remove it themselves, then run explicit setup.
Never run `rm -rf` on it from this skill.

## Data Issues

### Corrupted notebook library
```bash
# Back up data/library.json first, then let the user remove it
python3 "$NOTEBOOKLM_RUN" notebook_manager.py add --url ... --name ...  # Re-add
```

## Recovery Procedures

Each procedure destroys local state. Describe it to the user, name what is
kept, and wait for an explicit yes before running it.

### Complete reset (keep library)
```bash
python3 "$NOTEBOOKLM_RUN" cleanup_manager.py --confirm --preserve-library
python3 "$BLOG_SKILLS_DIR/blog-notebooklm/scripts/setup_environment.py"
python3 "$NOTEBOOKLM_RUN" auth_manager.py setup
```

### Complete reset (fresh start)
```bash
python3 "$NOTEBOOKLM_RUN" cleanup_manager.py --confirm --force
python3 "$BLOG_SKILLS_DIR/blog-notebooklm/scripts/setup_environment.py"
python3 "$NOTEBOOKLM_RUN" auth_manager.py setup
```

## Debugging

```bash
# Enable visible browser for debugging
python3 "$NOTEBOOKLM_RUN" ask_question.py --question "test" --show-browser

# Check individual components
python3 "$NOTEBOOKLM_RUN" auth_manager.py status
python3 "$NOTEBOOKLM_RUN" notebook_manager.py list
```

## Common Questions

**Q: Why doesn't this work in Claude web UI?**
A: Requires local file system and browser access. Use Claude Code CLI only.

**Q: Can I use multiple Google accounts?**
A: Yes, use `auth_manager.py reauth` to switch between accounts.

**Q: Is Patchright safe?**
A: It's an anti-detection fork of Playwright. Uses Chrome, not Chromium,
for better fingerprint consistency. Required because Google actively blocks
standard Playwright automation.
