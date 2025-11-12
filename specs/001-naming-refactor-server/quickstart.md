# Quickstart: Core Implementation Fix & Server Deployment

**Feature**: 001-naming-refactor-server
**Audience**: Developers integrating or using MCP Smart Reader
**Time to Complete**: 5 minutes

## Prerequisites

- Python 3.10 or higher
- pip or uv package manager
- MCP client configured (e.g., Claude Code, Continue, or custom MCP client)

## Installation

### Option 1: Install with uv (recommended)

```bash
# Clone repository (if not already cloned)
git clone https://github.com/your-org/mcp-smart-reader.git
cd mcp-smart-reader

# Checkout feature branch
git checkout 001-naming-refactor-server

# Install with development dependencies
uv sync

# Verify installation
python -c "from mcp_smart_reader.server import smart_read; print('✓ Imports working')"
```

### Option 2: Install with pip

```bash
# Clone and checkout (same as above)
git clone https://github.com/your-org/mcp-smart-reader.git
cd mcp-smart-reader
git checkout 001-naming-refactor-server

# Install with development dependencies
pip install -e ".[dev]"

# Verify installation
python -c "from mcp_smart_reader.server import smart_read; print('✓ Imports working')"
```

## Quick Start: Running the Server

### Start the MCP Server

```bash
# Run the server command
mcp-smart-reader
```

**Expected Output**: Server starts and waits for MCP client connection (no visible output - stdio communication)

**If errors occur**:
- `ModuleNotFoundError: No module named 'fastmcp'` → Run `pip install -e .` or `uv sync`
- `ImportError: cannot import name 'estimate_tokens'` → Functions not yet implemented (see Implementation section)

### Configure MCP Client

Add server to your MCP client configuration (e.g., `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "smart-reader": {
      "command": "mcp-smart-reader",
      "args": []
    }
  }
}
```

Restart your MCP client to connect.

## Usage Examples

### Example 1: Summarize a Large Document

**Scenario**: Read a 50K token research paper

**MCP Client Command**:
```
Use smart_read tool with:
- file_path: "/Users/you/papers/stopper-paper.md"
- mode: "auto"
```

**Expected Response** (if >10K tokens):
```json
{
  "_preamble": "⚠️ DOCUMENT SUMMARY (NOT FULL CONTENT)\nOriginal: 53,132 tokens → Summary: 797 tokens\nReduction: 66.7x\n...",
  "content": "KEYWORDS: executive function, AI assistants...",
  "type": "summary",
  "original_tokens": 53132,
  "summary_tokens": 797,
  "reduction_factor": 66.7,
  ...
}
```

**Token Savings**: 53,132 → 797 tokens (98.5% reduction)

### Example 2: Read a Specific Section

**Scenario**: Extract just the "Methods" section from a paper

**MCP Client Command**:
```
Use read_section tool with:
- file_path: "/Users/you/papers/stopper-paper.md"
- section_heading: "3.1"
```

**Expected Response**:
```json
{
  "content": "## 3.1 Core Protocol\n\nThe STOPPER protocol...",
  "type": "section",
  "section": "3.1",
  "tokens": 1847,
  ...
}
```

**Token Savings**: Full paper (53K tokens) → Section only (1,847 tokens) = 96.5% reduction

### Example 3: List All Sections

**Scenario**: Get table of contents before reading

**MCP Client Command**:
```
Use list_sections tool with:
- file_path: "/Users/you/papers/stopper-paper.md"
```

**Expected Response**:
```json
{
  "sections": [
    "1. Introduction",
    "1.1 Background",
    "1.2 Motivation",
    "2. Related Work",
    "3. STOPPER Protocol",
    "3.1 Core Protocol",
    ...
  ],
  "count": 45,
  "type": "toc",
  ...
}
```

## Verification Checklist

After installation and configuration, verify:

- [ ] `python -c "from mcp_smart_reader.server import smart_read"` runs without errors
- [ ] `python -c "from mcp_smart_reader.summarizer import estimate_tokens"` runs without errors
- [ ] `python -c "from mcp_smart_reader.summarizer import generate_summary"` runs without errors
- [ ] `python -c "from mcp_smart_reader.summarizer import extract_headers"` runs without errors
- [ ] `mcp-smart-reader` command starts server without crashes
- [ ] `mypy src/` reports zero errors
- [ ] `ruff check src/` reports zero errors
- [ ] MCP client successfully connects to server
- [ ] `smart_read` tool appears in MCP client tool list
- [ ] `read_section` tool appears in MCP client tool list
- [ ] `list_sections` tool appears in MCP client tool list

## Common Issues

### Issue: Import Error for `estimate_tokens`

**Symptom**: `ImportError: cannot import name 'estimate_tokens' from 'mcp_smart_reader.summarizer'`

**Cause**: Function not yet implemented in summarizer.py

**Solution**: Implement function per research.md:
```python
import tiktoken

def estimate_tokens(text: str) -> int:
    """Count tokens using cl100k_base encoding."""
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))
```

### Issue: Import Error for `generate_summary`

**Symptom**: `ImportError: cannot import name 'generate_summary' from 'mcp_smart_reader.summarizer'`

**Cause**: Function not yet implemented in summarizer.py

**Solution**: Implement function per research.md (combines existing extractors)

### Issue: Function name mismatch for `extract_headers`

**Symptom**: `AttributeError: module 'mcp_smart_reader.summarizer' has no attribute 'extract_headers'`

**Cause**: Function is named `extract_section_headers` internally

**Solution**: Add alias in summarizer.py:
```python
extract_headers = extract_section_headers
```

### Issue: `read_section` returns placeholder message

**Symptom**: "Section extraction not yet implemented"

**Cause**: `read_section()` tool stub in server.py not yet implemented

**Solution**: Implement section extraction logic per research.md

## Development Workflow

For developers contributing to this feature:

1. **Type Check**: Run `mypy src/` before commits (must pass with zero errors)
2. **Lint**: Run `ruff check src/` before commits (must pass)
3. **Format**: Run `ruff format src/` to auto-format code
4. **Manual Test**: Use MCP client to invoke tools and verify behavior
5. **Commit**: Granular commits per function implemented

## Next Steps

After this feature is complete:

1. **Add Tests**: Create unit tests for `estimate_tokens`, `generate_summary`, section extraction
2. **Add Caching**: Optimize repeated reads of same file
3. **Add Formats**: Support PDF and DOCX files
4. **Enhance Summaries**: Implement "extractive" and "abstract" summary styles

## Support

- **Documentation**: See CLAUDE.md in repository root
- **Constitution**: See .specify/memory/constitution.md for governance
- **Issues**: Report bugs via GitHub Issues
- **Contact**: scot@prefrontal.systems
