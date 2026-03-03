# Gemini CLI vs Claude Code: Migration Differences

This document outlines key differences you should be aware of when migrating skills, agents, or usage patterns from Anthropic's `claude` CLI to the `gemini` CLI.

## Modes

### Claude Code "Flag" Mode vs Gemini CLI "YOLO" Mode

**Claude Code** typically emphasizes specific operation modes using flags (e.g., `-p` for prompt mode) or assumes you will be frequently switching contexts. 

**Gemini CLI** features an advanced default **"YOLO" (You Only Look Once/Agentic) mode**.
- In this mode, the agent is highly proactive and will automatically attempt to figure out the user's intent, sequence actions, and execute tool calls to solve the problem directly, often without asking for step-by-step confirmation.
- While Claude might stop earlier and prompt the user to approve a plan, Gemini will typically forge ahead unless it encounters a wall or is explicitly instructed to pause via the `notify_user` or `task_boundary` mechanic.
- When writing prompts and skills for Gemini CLI, it's crucial to be explicit if you *require* human-in-the-loop interaction at specific stages.

## File System & Configuration

- **Directories**: Claude Code skills and agents are typically located in `~/.gemini/skills/` and `~/.gemini/agents/`. For the Gemini CLI, this has been mapped to `~/.gemini/skills/` and `~/.gemini/agents/`. Updates to `install.sh` and `install.ps1` reflect this change.
- **Skills Definition**: Both CLIs use a robust file-based markdown system (e.g., `GEMINI.md`) with YAML frontmatter. The underlying syntax and capabilities are very similar as both read `GEMINI.md` to load tool/agent definitions.

## Prompting Sensibilities

- **Proactivity**: Gemini CLI shines when given high-level goals and context. Because of its YOLO mode, you can give it a broad objective (e.g., "Research this topic and generate a complete blog post with the generated templates"), and it will attempt to complete the entire pipeline autonomously.
- **Artifact Generation**: The Gemini CLI inherently understands how to generate artifacts (like Markdown plans, task lists, and text files) within a `brain/` directory for the user's active conversation, providing a native space for complex planning before execution.

## Tool Execution

Be aware that Gemini CLI aggressively utilizes parallelism for tool calls when it deems safe, which can speed up workflows but requires you to ensure your environment scripts (like `install.sh`) or data-gathering steps do not suffer from race conditions.

