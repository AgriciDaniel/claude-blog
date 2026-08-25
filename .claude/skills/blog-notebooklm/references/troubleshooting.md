# NotebookLM Troubleshooting Guide

## Quick Fix Table

| Error | Solution |
|-------|----------|
| ModuleNotFoundError | Always use `python3 scripts/run.py [script].py` |
| Not authenticated | `python3 scripts/run.py auth_manager.py setup` (browser visible) |
| Browser crash | Close the skill browser window, cleanup with `--preserve-library`, re-auth |
| Rate limit (50/day) | Wait until midnight PST or switch Google account |
| Notebook not found | Check with `notebook_manager.py list` |
| Query timeout | Retry with simpler question or `--show-browser` to debug |

## Authentication Issues

### Not authenticated error
```bash
python3 scripts/run.py auth_manager.py status   # Confirm status
python3 scripts/run.py auth_manager.py setup     # Browser visible for login
```
User must manually log in to Google in the browser window.

### Authentication expires frequently
```bash
python3 scripts/run.py cleanup_manager.py --confirm --preserve-library
python3 scripts/run.py auth_manager.py setup     # Fresh login
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
python3 scripts/run.py cleanup_manager.py --confirm --preserve-library
python3 scripts/run.py auth_manager.py reauth    # Re-authenticate
```

### Browser not found
```bash
# run.py installs Chrome automatically on first run
python3 scripts/run.py auth_manager.py status
# If still failing, manual install:
source .venv/bin/activate
python3 -m patchright install chrome
```

### Timeout waiting for selector
NotebookLM UI may have changed CSS selectors. Check `config.py` for
current selectors (`QUERY_INPUT_SELECTORS`, `RESPONSE_SELECTORS`).
Use `--show-browser` to visually debug.

## Rate Limiting

### Rate limit exceeded (50 queries/day)

**Option 1: Wait**: resets at midnight PST

**Option 2: Switch accounts**
```bash
python3 scripts/run.py auth_manager.py clear
python3 scripts/run.py auth_manager.py setup     # Login with different account
```

## Notebook Access Issues

### Notebook not found in library
```bash
python3 scripts/run.py notebook_manager.py list
python3 scripts/run.py notebook_manager.py search --query "keyword"
```

### Wrong notebook being queried
```bash
python3 scripts/run.py notebook_manager.py list            # Check active
python3 scripts/run.py notebook_manager.py activate --id correct-id
```

## Virtual Environment Issues

### ModuleNotFoundError
**Always use `run.py`**: it handles venv automatically:
```bash
python3 scripts/run.py [any_script].py   # Creates .venv if needed
```

### Corrupted venv
```bash
rm -rf .venv                              # Remove broken venv
python3 scripts/run.py auth_manager.py status   # Auto-recreates
```

## Data Issues

### Corrupted notebook library
```bash
cp data/library.json library.backup.json  # Backup first
rm data/library.json                      # Reset
python3 scripts/run.py notebook_manager.py add --url ... --name ...  # Re-add
```

## Recovery Procedures

### Complete reset (keep library)
```bash
python3 scripts/run.py cleanup_manager.py --confirm --preserve-library
rm -rf .venv
python3 scripts/run.py auth_manager.py setup     # Rebuilds everything
```

### Complete reset (fresh start)
```bash
python3 scripts/run.py cleanup_manager.py --confirm --force
rm -rf .venv
python3 scripts/run.py auth_manager.py setup
```

## Debugging

```bash
# Enable visible browser for debugging
python3 scripts/run.py ask_question.py --question "test" --show-browser

# Check individual components
python3 scripts/run.py auth_manager.py status
python3 scripts/run.py notebook_manager.py list
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
