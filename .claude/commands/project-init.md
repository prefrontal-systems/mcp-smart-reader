---
description: Initialize project with comprehensive setup (repo exploration, CLAUDE.md, MCP config, git workflow)
---

You are initializing a new project with a comprehensive setup. Follow these steps in order:

## 1. Repository Exploration

Explore the repository structure and gather information:

- **Read key files**: README.md, pyproject.toml, package.json, setup.py, or equivalent
- **Identify project type**: Python, JavaScript, Go, etc.
- **Find main directories**: src/, lib/, tests/, docs/, etc.
- **Check existing tooling**: Build systems, test frameworks, linters
- **Detect dependencies**: Package managers, external services
- **Look for documentation**: Existing CLAUDE.md, CONTRIBUTING.md, etc.

Use available tools (Glob, Grep, Read) to gather this information efficiently.

## 2. Create/Update CLAUDE.md

Create `.claude/CLAUDE.md` (or update if exists) with:

```markdown
# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

[Brief description based on README/package files]

**Type**: [Language/Framework]
**Purpose**: [What the project does]

## Architecture

[Key directories and their purposes]
[Main modules/components]

## Development Commands

### Setup
```bash
[Installation commands from README]
```

### Testing
```bash
[Test commands]
```

### Code Quality
```bash
[Linting, formatting, type checking commands]
```

## Key Implementation Details

[Important patterns, conventions, constraints from the codebase]

## Project Structure

[Directory tree with descriptions]

## Active Technologies
- [List of main dependencies and tools]

## Recent Changes
- [To be updated as work progresses]
```

## 3. Import MCP Servers from Claude Desktop

Check Claude Desktop configuration and create project-level MCP setup:

1. **Try to read**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
2. **If found**: Extract `mcpServers` configuration
3. **Create**: `.claude/mcp_servers.json` with the imported configuration
4. **Add note**: This is project-specific and can diverge from global config

If config not found or inaccessible, create empty template:

```json
{
  "mcpServers": {
    "example-server": {
      "command": "path/to/server",
      "args": [],
      "env": {}
    }
  },
  "_note": "Import MCP servers from Claude Desktop config or add manually"
}
```

## 4. Add Git Workflow Documentation

Copy the git workflow quick reference to project root:

Create `GIT-WORKFLOW.md` with:
- Three-command workflow (start, finish, abandon)
- Branch naming conventions
- Examples
- Quick reference

**Note**: Only create this if it doesn't already exist.

## 5. Initialize Project-Specific Configuration

Create `.claude/project-init-config.json` for future customization:

```json
{
  "version": "1.0.0",
  "initialized": "[timestamp]",
  "components": {
    "claude_md": true,
    "mcp_servers": true,
    "git_workflow": true
  },
  "custom_init_steps": [
    {
      "name": "example-step",
      "description": "Example custom initialization step",
      "enabled": false,
      "script": "path/to/script.sh"
    }
  ],
  "notes": "Add custom initialization steps to custom_init_steps array"
}
```

## 6. Summary Report

After completing all steps, provide a summary:

```
✓ Repository explored
✓ CLAUDE.md created/updated at .claude/CLAUDE.md
✓ MCP servers imported to .claude/mcp_servers.json
✓ Git workflow added to GIT-WORKFLOW.md
✓ Project configuration created at .claude/project-init-config.json

Next steps:
1. Review CLAUDE.md and add project-specific details
2. Update .claude/mcp_servers.json with project-specific MCP servers
3. Add custom initialization steps to .claude/project-init-config.json if needed
4. Commit these files to version control
```

## Error Handling

- If files already exist, ASK before overwriting
- If Claude Desktop config is inaccessible, create template and note it
- If git workflow already exists, skip it
- Report any failures clearly

## Extensibility

Users can add custom initialization steps by:
1. Adding entries to `.claude/project-init-config.json` under `custom_init_steps`
2. Each step can reference a script or inline commands
3. Future runs of `/project-init` will execute enabled custom steps

---

**Begin initialization now.**
