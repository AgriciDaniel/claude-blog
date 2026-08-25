# NotebookLM Commands Reference

Complete CLI documentation for all NotebookLM skill scripts.

## run.py: Universal Script Runner

Always use `run.py` to execute any script. It handles venv creation,
dependency installation, Chrome setup, and proper execution.

```bash
python3 scripts/run.py <script_name>.py [arguments]
```

## ask_question.py: Query Interface

Ask questions to NotebookLM notebooks with automated browser interaction.

```bash
# Basic query (uses active notebook)
python3 scripts/run.py ask_question.py --question "Your question"

# Query specific notebook by ID
python3 scripts/run.py ask_question.py --question "..." --notebook-id notebook-id

# Query by URL directly
python3 scripts/run.py ask_question.py --question "..." --notebook-url "https://..."

# JSON output for structured responses
python3 scripts/run.py ask_question.py --question "..." --json

# Show browser for debugging
python3 scripts/run.py ask_question.py --question "..." --show-browser
```

**Parameters:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| `--question` | Yes | Question to ask |
| `--notebook-id` | No | Use notebook from library |
| `--notebook-url` | No | Validate and use a NotebookLM notebook URL |
| `--json` | No | Output structured JSON |
| `--show-browser` | No | Make browser visible |

**JSON output format** (with `--json`):
```json
{
  "status": "success",
  "question": "What are the key findings?",
  "answer": "The source-grounded response text...",
  "notebook_id": "my-notebook",
  "notebook_url": "https://notebooklm.google.com/notebook/...",
  "timestamp": "2026-03-25T14:30:00Z"
}
```

**Returns:** Answer text with follow-up prompt. Timeout: 120 seconds.

## notebook_manager.py: Library Management

CRUD operations for the notebook library.

```bash
# Add notebook (all metadata required)
python3 scripts/run.py notebook_manager.py add \
  --url "https://notebooklm.google.com/notebook/..." \
  --name "Descriptive Name" \
  --description "What this notebook contains" \
  --topics "topic1,topic2,topic3"

# List all notebooks
python3 scripts/run.py notebook_manager.py list

# Search by keyword (searches name, description, topics)
python3 scripts/run.py notebook_manager.py search --query "keyword"

# Set active notebook (default for queries without --notebook-id)
python3 scripts/run.py notebook_manager.py activate --id notebook-id

# Remove notebook from library
python3 scripts/run.py notebook_manager.py remove --id notebook-id

# Show library statistics
python3 scripts/run.py notebook_manager.py stats
```

**Commands:**
| Command | Description |
|---------|-------------|
| `add` | Add notebook (requires --url, --name, --description, --topics) |
| `list` | Show all notebooks with metadata |
| `search` | Find notebooks by keyword |
| `activate` | Set default notebook for queries |
| `remove` | Delete from library |
| `stats` | Display library statistics |

**Smart discovery** (recommended before `add`):
```bash
# Query the notebook to learn its content first
python3 scripts/run.py ask_question.py \
  --question "What is the content of this notebook? What topics are covered?" \
  --notebook-url "<URL>"
# Then use discovered info for the add command
```

## auth_manager.py: Authentication

Handle Google authentication and browser state.

```bash
python3 scripts/run.py auth_manager.py setup    # Initial setup (browser visible)
python3 scripts/run.py auth_manager.py status   # Check authentication
python3 scripts/run.py auth_manager.py reauth   # Re-authenticate
python3 scripts/run.py auth_manager.py clear    # Clear all auth data
```

**Commands:**
| Command | Description |
|---------|-------------|
| `setup` | Interactive Google login in visible browser (one-time) |
| `status` | Check if authenticated (lightweight, no side effects) |
| `reauth` | Clear and re-setup authentication |
| `clear` | Remove all authentication data |

**Auth architecture:** Hybrid approach: persistent browser profile for
fingerprint consistency + manual cookie injection from state.json
(Playwright bug #36139 workaround).

## cleanup_manager.py: Data Cleanup

Clean skill data with preservation options.

```bash
python3 scripts/run.py cleanup_manager.py                    # Preview (dry run)
python3 scripts/run.py cleanup_manager.py --confirm          # Execute cleanup
python3 scripts/run.py cleanup_manager.py --confirm --preserve-library  # Keep notebooks
python3 scripts/run.py cleanup_manager.py --confirm --force  # Skip confirmation
```

**Options:**
| Option | Description |
|--------|-------------|
| `--confirm` | Actually perform cleanup (without this, preview only) |
| `--preserve-library` | Keep notebook library, clean everything else |
| `--force` | Skip confirmation prompt |

## Workflow Patterns

### Pattern: Research for Blog Writing
```bash
# 1. Check if relevant notebook exists
python3 scripts/run.py notebook_manager.py search --query "marketing"

# 2. Query for source-grounded data
python3 scripts/run.py ask_question.py \
  --question "What are the latest conversion rate benchmarks?" \
  --notebook-id marketing-research --json

# 3. Follow up for completeness
python3 scripts/run.py ask_question.py \
  --question "Break down conversion rates by industry and channel" \
  --notebook-id marketing-research --json
```

### Pattern: Multi-Notebook Research
```bash
# Query different notebooks for a comprehensive view
python3 scripts/run.py ask_question.py --question "..." --notebook-id source-a
python3 scripts/run.py ask_question.py --question "..." --notebook-id source-b
# Synthesize answers from both sources
```

### Pattern: Batch Questions
```bash
# Ask multiple focused questions (respect 50/day rate limit)
for question in "Q1" "Q2" "Q3"; do
  python3 scripts/run.py ask_question.py --question "$question" --json
  sleep 2  # Avoid rate limits
done
```

## Environment Variables (Optional)

Create `.env` in skill root directory:
```env
HEADLESS=false           # Browser visibility (default: true)
SHOW_BROWSER=false       # Default browser display
STEALTH_ENABLED=true     # Human-like behavior simulation
TYPING_WPM_MIN=160       # Typing speed range
TYPING_WPM_MAX=240
DEFAULT_NOTEBOOK_ID=     # Default notebook for queries
```

## Rate Limits

- Free Google accounts: ~50 queries/day
- Reset: midnight PST
- Mitigation: switch accounts with `auth_manager.py reauth`
