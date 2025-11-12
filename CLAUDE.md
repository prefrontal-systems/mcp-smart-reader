# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**MCP Smart Reader** is a FastMCP-based server that provides token-efficient access to large documents through automatic summarization. When documents exceed 10K tokens, the server returns structured summaries with rich metadata instead of loading the entire content into context, achieving 98%+ token reduction while preserving actionable information.

**Core Value Proposition**: Transform a 53K token document into an 800 token summary with section navigation, saving 157K tokens across 3 exchanges.

## Architecture

### Two-Module Design

**server.py** - MCP server with three tools:
- `smart_read(file_path, mode, summary_style)` - Auto-summarize large files, return metadata-rich responses
- `read_section(file_path, section_heading)` - Extract specific sections with metadata (line numbers, tokens, heading level)
- `list_sections(file_path)` - Return document table of contents

**summarizer.py** - Text processing functions:
- `estimate_tokens(text)` - Token counting using tiktoken cl100k_base encoding
- `extract_abstract(text)` - Regex-based abstract extraction from markdown
- `extract_headers(text)` - Find section headers (alias for `extract_section_headers`)
- `extract_keywords_from_abstract(text)` - Parse "**Keywords:**" line
- `extract_key_points(text, num_points)` - Score and rank key sentences
- `generate_summary(content, style)` - Generate structured summaries combining multiple extractors
- `extract_section_content(text, heading)` - Extract markdown section content with metadata

### Implementation Status

✅ **All core functionality implemented** (feature 001-naming-refactor-server):
- Token counting with tiktoken
- Summary generation combining existing extractors
- Section extraction with line numbers and heading levels
- Import naming conflicts resolved
- Full type coverage with mypy strict mode
- Zero linting issues with ruff

## Development Commands

### Environment Setup

```bash
# Install dependencies (development mode with test tools)
uv sync

# Or with pip
pip install -e ".[dev]"
```

### Running the MCP Server

```bash
# Run server directly
python -m mcp_smart_reader.server

# Or use installed command
mcp-smart-reader
```

### Testing

```bash
# Run all tests with coverage
pytest

# Run with coverage report
pytest --cov=mcp_smart_reader --cov-report=html

# Run specific test file
pytest tests/test_specific.py

# Run single test
pytest tests/test_specific.py::test_function_name
```

### Code Quality

```bash
# Type checking (strict mode enabled)
mypy src/mcp_smart_reader

# Linting
ruff check src/mcp_smart_reader

# Auto-format code
ruff format src/mcp_smart_reader

# Check formatting without changing
ruff format --check src/mcp_smart_reader
```

## Key Implementation Details

### Token Counting

The project uses `tiktoken` for accurate token estimation (imported but not yet implemented in `summarizer.py`). Use `cl100k_base` encoding for Claude compatibility:

```python
import tiktoken

def estimate_tokens(text: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))
```

### Summary Generation Styles

The `smart_read` tool supports three summary styles:

- **"structured"** (default) - Extract keywords, headers, abstract, key points, contributions
- **"extractive"** - Key sentences only (not yet implemented)
- **"abstract"** - Just abstract section if available (not yet implemented)

Currently only basic extraction exists in `summarizer.py` - needs `generate_summary()` function combining these.

### Metadata Response Format

Summaries return rich metadata to help Claude know when to drill down:

```python
{
    "_preamble": "⚠️ DOCUMENT SUMMARY warning with guidance",
    "content": "summary text",
    "type": "summary",
    "original_tokens": 53132,
    "summary_tokens": 797,
    "reduction_factor": 66.7,
    "sections": {"count": 45, "headers": [...]},
    "coverage": {
        "included": {"abstract": True, "keywords": True, ...},
        "excluded": {"detailed_methods": True, ...}
    },
    "confidence": {
        "completeness": 0.015,
        "recommended_for": ["overview", "triage"],
        "not_recommended_for": ["citation", "implementation"]
    }
}
```

### Configuration Constants

Defined in `server.py`:

- `TOKEN_THRESHOLD = 10000` - Files >10K tokens trigger auto-summarization
- `DEFAULT_SUMMARY_STYLE = "structured"` - Default summary generation approach

## Code Quality Standards

### Type Checking

`mypy` configured in strict mode (`pyproject.toml`):
- `python_version = "3.10"` - Minimum Python version
- `disallow_untyped_defs = true` - All functions must have type hints
- `warn_return_any = true` - Warn on returning `Any`

### Linting

`ruff` configured with:
- `line-length = 100` - Maximum line length
- `target-version = "py310"` - Python 3.10+ syntax
- Selected rules: E (errors), F (pyflakes), I (isort), N (naming), W (warnings)
- Ignored: E501 (line too long - handled by formatter)

### Testing

`pytest` configured for:
- Test discovery: `tests/test_*.py`
- Coverage reporting enabled by default
- Minimum coverage target: Not specified (add to pyproject.toml if needed)

## Project Status

**Current**: Basic structure in place, core extraction functions exist, but integration is incomplete.

**Blockers**:
- Missing `estimate_tokens()` function (needs tiktoken implementation)
- Missing `generate_summary()` function (needs to orchestrate extractors)
- `extract_headers` naming mismatch (internal name vs. import)
- `read_section()` stubbed out (needs section extraction logic)

**Next Steps** (from README.md):
1. Implement missing functions (`estimate_tokens`, `generate_summary`)
2. Fix function naming/exports in `summarizer.py`
3. Implement section extraction logic for `read_section()`
4. Add multi-format support (PDF, DOCX)
5. Enhance summarization algorithms (extractive, abstract-only modes)
6. Add caching layer for repeated reads
7. Comprehensive testing

## Testing Strategy

When implementing tests:

1. **Unit tests** for `summarizer.py` functions:
   - Test each extractor independently
   - Include edge cases (missing sections, malformed markdown)
   - Test token counting accuracy

2. **Integration tests** for MCP tools:
   - Test `smart_read()` with various file sizes and modes
   - Test section extraction and TOC generation
   - Verify metadata completeness

3. **Token reduction validation**:
   - Measure actual token savings on real documents
   - Verify summary quality (information preservation)

## Related Documentation

- **README.md** - Installation, features, token savings examples
- **pyproject.toml** - Dependencies, build config, tool settings
- **Prefrontal Systems org CLAUDE.md** - Organization-level guidance and philosophy

## Dependencies

**Runtime**:
- `fastmcp>=0.3.0` - MCP server framework
- `tiktoken>=0.8.0` - Token counting (not yet used in code)

**Development**:
- `pytest>=8.0.0` - Testing framework
- `pytest-cov>=6.0.0` - Coverage reporting
- `mypy>=1.11.0` - Type checking
- `ruff>=0.6.0` - Linting and formatting

## Contact

**Author**: Scot Campbell
**Company**: Prefrontal Systems LLC
**Email**: scot@prefrontal.systems
**License**: Apache 2.0

## Active Technologies
- Python 3.10+ + FastMCP >=0.3.0, tiktoken >=0.8.0, mypy >=1.11.0 (strict mode), ruff >=0.6.0 (001-naming-refactor-server)
- N/A (stateless text processing, no persistence) (001-naming-refactor-server)

## Recent Changes
- 001-naming-refactor-server: Added Python 3.10+ + FastMCP >=0.3.0, tiktoken >=0.8.0, mypy >=1.11.0 (strict mode), ruff >=0.6.0
