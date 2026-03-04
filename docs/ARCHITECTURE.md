# Architecture

System design documentation for `gemini-blog`, covering component types,
data flow, scoring methodology, file conventions, and extension points.

---

## System Overview

```
                        +-----------------------------+
                        |         User Input          |
                        |   /blog:<command> [args]    |
                        +-------------+---------------+
                                      |
                                      v
                        +-----------------------------+
                        |    Main Orchestrator        |
                        |       GEMINI.md             |
                        |                             |
                        |  - Command parsing          |
                        |  - Platform detection       |
                        |  - Sub-skill routing        |
                        |  - Quality gate enforcement |
                        +------+----------+-----------+
                               |          |
              +----------------+          +----------------+
              |                                            |
              v                                            v
+----------------------------+            +---------------------------+
|     12 Sub-Skills          |            |    On-Demand References   |
|  skills/blog-*/GEMINI.md   |            |  blog/references/*.md     |
|                            |            |  blog/templates/*.md      |
|  write    rewrite          |            |                           |
|  analyze  brief            |            |  Loaded as needed         |
|  calendar strategy         |            |  (RAG-style pattern)      |
|  outline  seo-check        |            +---------------------------+
|  schema   repurpose        |
|  geo      audit            |
+------+----------+----------+
       |          |
       v          v
+------------------+  +------------------+
|  4 Subagents     |  |  Python Script   |
|  agents/*.md     |  |  analyze_blog.py |
|                  |  |                  |
|  blog-researcher |  |  Automated       |
|  blog-writer     |  |  quality metrics |
|  blog-seo        |  |  and scoring     |
|  blog-reviewer   |  +------------------+
+------------------+
```

---

## Component Types

### 1. Main Orchestrator

**File**: `GEMINI.md`

The entry point for all `/blog` commands. Responsibilities:

- Parse user input to identify the sub-command and arguments
- Detect the blog platform from project structure (MDX, Hugo, Jekyll, etc.)
- Route to the appropriate sub-skill
- Enforce quality gates (hard rules that never ship content violating them)
- Load reference files on demand

The orchestrator is a Gemini CLI extension context file.

### 2. Sub-Skills (12)

**Location**: `skills/blog-*/GEMINI.md`

Each sub-skill is a standalone Gemini CLI skill with its own:

- YAML frontmatter (name, description, allowed-tools)
- Detailed workflow (step-by-step instructions)
- Input/output specifications
- Quality checks

| Sub-Skill | Responsibility |
|-----------|---------------|
| blog-write | New article generation with full optimization |
| blog-rewrite | Existing post optimization preserving author voice |
| blog-analyze | Quality audit with 0-100 scoring |
| blog-brief | Content brief generation with research |
| blog-calendar | Editorial calendar planning |
| blog-strategy | Blog positioning and content architecture |
| blog-outline | SERP-informed outline generation |
| blog-seo-check | Post-writing SEO validation |
| blog-schema | JSON-LD schema markup generation |
| blog-repurpose | Cross-platform content repurposing |
| blog-geo | AI citation optimization audit |
| blog-audit | Full-site blog health assessment |

### 3. Subagents (4)

**Location**: `agents/blog-*.GEMINI.md`

Specialized agents spawned by sub-skills via Gemini CLI's `Task` tool.
Each agent has a focused role with a restricted tool set.

| Agent | Role |
|-------|------|
| blog-researcher | Find statistics, images, competitive data |
| blog-writer | Write and rewrite optimized content |
| blog-seo | Technical SEO analysis and validation |
| blog-reviewer | Quality review and scoring |

### 4. Reference Files (12)

**Location**: `blog/references/*.md`

Knowledge documents loaded on demand (not preloaded).

### 5. Content Templates (12)

**Location**: `blog/templates/*.md`

Structural templates for different content types.

### 6. Python Analysis Script

**File**: `scripts/analyze_blog.py`

---

## File Naming Conventions

| Component | Location | Naming |
|-----------|----------|--------|
| Main context | `GEMINI.md` | Fixed name |
| Sub-skills | `skills/blog-<command>/GEMINI.md` | Prefix `blog-` + command name |
| Agents | `agents/blog-<role>.GEMINI.md` | Prefix `blog-` + role name |
| References | `blog/references/<topic>.md` | Kebab-case topic name |
| Templates | `blog/templates/<type>.md` | Kebab-case content type |
| Scripts | `scripts/<name>.py` | Snake-case script name |

---

## Installed Directory Tree (Gemini Extension Format)

```
gemini-blog/
------------------ gemini-extension.json               # Extension manifest
------------------ GEMINI.md                           # Main orchestrator
------------------ blog/
------   ------------------ references/                     # Knowledge base
------   ------------------ templates/                      # Content templates
------   ------------------ scripts/
------       ------------------ analyze_blog.py
------------------ skills/
------   ------------------ blog-write/GEMINI.md            # Sub-skill
------   ------------------ blog-rewrite/GEMINI.md          # Sub-skill
------   ------------------ ... (10 more)
------------------ agents/
    ------------------ blog-researcher.GEMINI.md        # Subagent
    ------------------ blog-writer.GEMINI.md            # Subagent
    ------------------ ... (2 more)
```

---

## Technical Considerations: Gemini CLI

When developing or modifying agents within this extension, you **must use the strict Gemini CLI tool naming conventions** in the `tools` array of the agent's YAML frontmatter.

Tools must be specified in the correct `snake_case` format corresponding to the Gemini CLI built-ins. Some of the major mappings include:
- **File System:** `read_file`, `write_file`, `replace`, `list_directory`, `glob`
- **Search & Execution:** `grep_search` (not `search_file_content`), `run_shell_command`
- **Web & URLs:** `web_fetch`, `google_web_search`

Failing to use these canonical names will result in "Invalid tool name" validation errors when the Gemini CLI tries to load the agent.

