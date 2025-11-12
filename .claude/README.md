# Claude Code Project Configuration

This directory contains project-specific configuration for Claude Code.

## Files

### `commands/project-init.md`
Custom slash command: `/project-init`

Initializes a project with:
- Repository exploration
- CLAUDE.md creation/update
- MCP server configuration import
- Git workflow documentation
- Extensible custom initialization steps

**Usage**: Type `/project-init` in Claude Code

### `project-init-config.json`
Configuration for the project initialization process.

**Customize by**:
- Adding custom initialization steps to `custom_init_steps` array
- Each step needs: `name`, `description`, `enabled`, `script`, `notes`
- Enable steps by setting `enabled: true`

**Example custom step**:
```json
{
  "name": "install-pre-commit-hooks",
  "description": "Install pre-commit hooks for code quality",
  "enabled": true,
  "script": "pre-commit install",
  "notes": "Requires pre-commit to be installed"
}
```

### `settings.local.json`
Project-specific Claude Code settings (permissions, etc.)

### `CLAUDE.md` (created by /project-init)
Project documentation for Claude Code - architecture, commands, patterns.

### `mcp_servers.json` (created by /project-init)
Project-specific MCP server configuration (can differ from global config).

## Git Workflow Aliases

Global git aliases have been configured:

```bash
git start feature/name    # Start new work
git finish                # Merge, push, and delete branch
git abandon               # Delete branch without merging
```

See `../GIT-WORKFLOW.md` for complete documentation.

## Adding Custom Initialization

1. Edit `project-init-config.json`
2. Add entry to `custom_init_steps` array
3. Set `enabled: true`
4. Run `/project-init` in any new project

Your custom steps will be executed automatically.
