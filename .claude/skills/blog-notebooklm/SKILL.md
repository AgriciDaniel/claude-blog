---
name: blog-notebooklm
description: >
  Query Google NotebookLM notebooks for source-grounded, citation-backed
  answers from user-uploaded documents. Manages notebook library, handles
  Google authentication, and supports smart discovery. Works standalone
  via /blog notebooklm or internally from blog-write and blog-researcher
  for source-grounded research context. Falls back gracefully when not configured.
  Use when user says "notebooklm", "notebook", "query notebook",
  "ask notebook", "notebook research", "source grounded research",
  "document query", "notebook library".
user-invokable: true
argument-hint: "[ask|discover|library|setup|status|cleanup] [question-or-url]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "2.1.1"
  source: "https://github.com/PleasePrompto/notebooklm-skill"
---

# Blog NotebookLM: Source-Grounded Research from Your Documents

Query Google NotebookLM notebooks directly from Claude Code for citation-backed
answers from Gemini. Each question opens a headless browser session, retrieves
the answer from your uploaded documents, and closes. Responses are
source-grounded model answers, not proof of truth: uploaded documents may be
primary or secondary, and the answer can still omit context.

Answers provide usable provenance only when the returned citation identifies a
verifiable underlying source. Record a stable source URL and a publication,
study-period, or retrieval date when that detail affects verification or
interpretation. Use the underlying source title as the inline citation. Do not
cite the private NotebookLM URL as the bibliography entry for public content.

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/blog notebooklm ask <question>` | Query a notebook for source-grounded answers |
| `/blog notebooklm discover <url>` | Smart-discover notebook content before cataloging |
| `/blog notebooklm library list` | List all notebooks in library |
| `/blog notebooklm library add <url>` | Add a notebook to library |
| `/blog notebooklm library search <query>` | Search notebooks by keyword |
| `/blog notebooklm library remove <id>` | Remove a notebook from library |
| `/blog notebooklm setup` | One-time Google authentication (browser visible) |
| `/blog notebooklm status` | Check authentication status |
| `/blog notebooklm cleanup` | Clean browser state (preserves library) |

## Prerequisites

- Google account with NotebookLM access
- Python 3.11+ (venv managed automatically by `run.py`)
- Google Chrome (installed automatically on first run via Patchright)
- One-time authentication setup (interactive Google login in visible browser)

## Use the run.py Wrapper

Call scripts only through the run.py wrapper: `python3 scripts/run.py [script]`:

```bash
# CORRECT:
python3 scripts/run.py auth_manager.py status
python3 scripts/run.py ask_question.py --question "..."

# Do not call files under scripts/ directly. The wrapper owns venv setup.
```

The `run.py` wrapper automatically creates `.venv`, installs dependencies,
sets up Chrome, and executes the target script.

## Auth Check (Gate Pattern)

Before any query operation, check authentication:

```bash
python3 scripts/run.py auth_manager.py status
```

- If authenticated: proceed with the query
- If not authenticated: inform user and guide to setup:
  "NotebookLM requires Google login. Run `/blog notebooklm setup` to authenticate."
- **When called internally** (from blog-write or blog-researcher): return silently
  with no error if not authenticated. Never block the writing workflow.

## Setup Workflow

For `/blog notebooklm setup`:

```bash
# Opens a visible browser for manual Google login (one-time)
python3 scripts/run.py auth_manager.py setup
```

Tell the user: "A browser window will open. Please log in to your Google account."
Authentication persists via browser profile + cookie injection (hybrid approach).

Other auth commands:
```bash
python3 scripts/run.py auth_manager.py status   # Check auth
python3 scripts/run.py auth_manager.py reauth   # Re-authenticate
python3 scripts/run.py auth_manager.py clear     # Clear all auth data
```

## Query Workflow

For `/blog notebooklm ask <question>`:

### Step 1: Check Auth
Run auth check (see gate pattern above). If not authenticated, guide to setup.

### Step 2: Resolve Notebook
Determine which notebook to query:
- If `--notebook-url` provided: validate it is a NotebookLM notebook URL, then use it
- If `--notebook-id` provided: look up in library
- If neither: use active notebook from library
- If no active notebook: show library and ask user to select

### Step 3: Ask the Question
```bash
# Basic query (uses active notebook)
python3 scripts/run.py ask_question.py --question "Your question here"

# Query specific notebook by ID
python3 scripts/run.py ask_question.py --question "..." --notebook-id notebook-id

# Query by URL directly
python3 scripts/run.py ask_question.py --question "..." --notebook-url "https://..."

# JSON output (for internal/programmatic use)
python3 scripts/run.py ask_question.py --question "..." --json

# Show browser for debugging
python3 scripts/run.py ask_question.py --question "..." --show-browser
```

### Step 4: Analyze and Follow Up
Every response ends with a follow-up prompt. **Required behavior:**
1. **STOP**: do not immediately respond to the user
2. **ANALYZE**: compare the answer to the user's original request
3. **IDENTIFY GAPS**: determine if more information is needed
4. **ASK FOLLOW-UP**: if gaps exist, immediately ask a follow-up question
5. **REPEAT**: continue until information is complete
6. **SYNTHESIZE**: combine all answers before responding to the user

## Smart Discovery Workflow

For `/blog notebooklm discover <url>`:

When adding a notebook without knowing its content, query it first:

```bash
# Step 1: Discover content
python3 scripts/run.py ask_question.py \
  --question "What is the content of this notebook? What topics are covered? Provide a complete overview briefly and concisely" \
  --notebook-url "<URL>"

# Step 2: Add with discovered metadata
python3 scripts/run.py notebook_manager.py add \
  --url "<URL>" \
  --name "<Based on content>" \
  --description "<Based on content>" \
  --topics "<Extracted topics>"
```

Do not guess descriptions; discover or ask the user.

## Library Management

```bash
# List all notebooks
python3 scripts/run.py notebook_manager.py list

# Add notebook (all params required -- discover or ask user!)
python3 scripts/run.py notebook_manager.py add \
  --url "https://notebooklm.google.com/notebook/..." \
  --name "Descriptive Name" \
  --description "What this notebook contains" \
  --topics "topic1,topic2,topic3"

# Search by keyword
python3 scripts/run.py notebook_manager.py search --query "keyword"

# Set active notebook
python3 scripts/run.py notebook_manager.py activate --id notebook-id

# Remove notebook
python3 scripts/run.py notebook_manager.py remove --id notebook-id

# Library statistics
python3 scripts/run.py notebook_manager.py stats
```

## Internal API (for blog-write / blog-researcher)

When invoked as a Task subagent from blog-write or blog-researcher:

**Input** (provided by calling skill):
- `question`: Research question relevant to the blog topic
- `notebook_id` or `notebook_url`: Which notebook to query
- `context`: "internal" (signals graceful fallback mode)

**Process:**
1. Check auth status: if not authenticated, return empty result silently
2. Query the notebook with the research question
3. Parse and return structured response

**Output** (returned to calling skill):
```markdown
### NotebookLM Research
- **Source:** [Notebook name]
- **Question:** [What was asked]
- **Answer:** [Source-grounded response from user's documents]
- **Underlying Source:** [Public source URL or document identifier]
- **Underlying Source Date:** [Publication date or retrieval date]
- **Source Quality:** [Tier 1-3 after classifying the underlying document]
```

**Graceful fallback:** If auth is missing or query fails, return immediately
with no error. The calling workflow continues with WebSearch-based research.
Never block blog-write or blog-rewrite because NotebookLM is unavailable.

## Data Storage

All data stored inside the skill directory:
- `data/library.json`: Notebook metadata and library
- `data/auth_info.json`: Authentication status
- `data/browser_state/`: Chrome profile with cookies

**Security:** All data directories are gitignored. Never commit auth or browser state.

## Error Handling

| Error | Resolution |
|-------|-----------|
| Not authenticated | Run `/blog notebooklm setup` |
| ModuleNotFoundError | Always use `run.py` wrapper |
| Browser crash | `cleanup_manager.py --confirm --preserve-library`, then re-auth |
| Rate limit (50/day) | Wait until midnight PST or switch Google account |
| Notebook not found | Check with `notebook_manager.py list` |
| Query timeout (120s) | Retry with simpler question or `--show-browser` to debug |
| MCP unavailable (internal) | Return silently: writing workflow uses WebSearch |

## Limitations

- No session persistence (each question = new browser session)
- Rate limits on free Google accounts (50 queries/day)
- Manual upload required (user must add docs to NotebookLM web UI)
- Browser overhead (few seconds per question for launch + teardown)
- Local Claude Code only (not available in web UI)

## Reference Documentation

Load on-demand: do NOT load all at startup:
- `references/commands.md`: Full CLI commands, parameters, and workflow patterns
- `references/troubleshooting.md`: Error solutions, recovery procedures, debugging
