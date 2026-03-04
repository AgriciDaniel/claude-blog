# Installation Guide

This guide covers the installation methods for `gemini-blog`, a native Gemini CLI extension ecosystem for blog content creation, optimization, and management.

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| [Gemini CLI](https://geminicli.com/docs/) | v0.31.0+ | Runtime for all `/blog` commands |
| Python | 3.12+ | Quality analysis script (`analyze_blog.py`) |
| pip | Latest | Python dependency management |

Gemini CLI must be installed and configured before installing `gemini-blog`.
Python is only required for the `analyze_blog.py` quality scoring script; all
other commands work without it.

---

## Installing the Extension

Because `gemini-blog` uses standard Gemini CLI extension architecture, installation is extremely simple. The extension uses `gemini-extension.json` and loads context from `GEMINI.md`.

### 1. Clone the Repository

First, clone the repository to a local directory:

```bash
git clone https://github.com/imitry/gemini-blog.git
cd gemini-blog
```

### 2. Install via Gemini CLI

Use the built-in Gemini extension manager to install the extension from the local directory:

```bash
gemini extensions install .
```

*Note: The CLI will prompt you asking if you trust the local folder. Type `y` or `yes` to proceed.*

If you want to skip the prompt automatically (e.g. in CI environments):
```bash
echo "y" | gemini extensions install .
```

### 3. Verify Installation

You can confirm the installation was successful and all agents loaded without errors by running:

```bash
gemini extensions list
```

You should see `gemini-blog` listed as enabled. There should be no "Invalid tool name" errors if the agents are correctly formatted.

---

## Install Python Dependencies

The Python analysis script requires some external libraries. Run this after the main install:

```bash
pip install -r requirements.txt
```

**Core dependencies:**

| Package | Version | Purpose |
|---------|---------|---------|
| textstat | >=0.7.3 | Readability scoring (Flesch, Gunning Fog, SMOG) |
| beautifulsoup4 | >=4.12.0 | HTML and schema parsing |
| lxml | >=5.0.0 | XML/HTML parser backend |
| jsonschema | >=4.20.0 | JSON-LD schema validation |

The analysis script works without optional dependencies by falling back to basic mode automatically.

---

## Updating

To update to the latest version of the extension:

```bash
cd path/to/gemini-blog
git pull
gemini extensions install .
```

---

## Uninstalling

To remove the extension from Gemini CLI:

```bash
gemini extensions uninstall gemini-blog
```

### Clean Up Python Dependencies (Optional)

```bash
pip uninstall textstat beautifulsoup4 lxml jsonschema
```

---

## Troubleshooting Installation

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Invalid tool name` errors | Agent files have outdated tool names | Ensure `agents/*.GEMINI.md` use canonical snake_case tool names (`read_file`, `write_file`, `replace`, etc.) |
| `gemini: command not found` | Gemini CLI is not installed | Install the Gemini CLI globally via npm/yarn |
| `python3: command not found` | Python not installed or not in PATH | Install Python 3.12+ via your package manager |
| `pip install` fails | Missing pip or wrong Python version | Run `python3 -m ensurepip --upgrade` |
