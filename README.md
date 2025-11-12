# MCP Smart Reader

**Version**: 0.1.0
**Status**: Production Ready
**License**: Apache 2.0

Smart document reader MCP server with automatic summarization for large files. Provides token-efficient access to documents by returning intelligent summaries with rich metadata instead of loading entire files into context.

[![Type Safety](https://img.shields.io/badge/mypy-passing-brightgreen)](https://mypy-lang.org/)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-black)](https://github.com/astral-sh/ruff)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.13+-orange.svg)](https://github.com/jlowin/fastmcp)

---

## Overview

MCP Smart Reader dramatically improves Claude's context window efficiency by automatically summarizing large documents. Instead of loading a 50,000 token research paper into every message, it returns an 800 token structured summary with metadata that guides Claude on when to request more detail.

### Token Savings Example

```
Without smart_read:
  paper.md: 53,132 tokens per message
  3-message conversation: 159,396 tokens consumed

With smart_read:
  Summary: 797 tokens (1.5% of original)
  3-message conversation: 2,391 tokens consumed

  → Savings: 157,005 tokens (98.5% reduction)
  → Cost savings: ~$3.14 per conversation (at $0.02/1K tokens)
```

---

## Features

### Automatic Summarization
- Files >10,000 tokens automatically summarized
- Structured summaries combining keywords, abstract, headers, key findings
- Configurable summary styles (structured, extractive, abstract)
- Token counting using tiktoken (Claude-compatible cl100k_base encoding)

### Rich Metadata
- **Preamble**: Warning about summarization with usage guidance
- **Coverage**: What's included/excluded from summary
- **Confidence**: Recommended use cases and limitations
- **Sections**: Table of contents with header hierarchy
- **Cross-references**: Links to `read_section()` and `list_sections()` for detail

### Section Extraction
- Extract specific markdown sections by heading name
- Case-insensitive, partial matching (e.g., "3.1" matches "## 3.1 Methods")
- Returns section content with metadata:
  - Heading level (1-6)
  - Line numbers (start/end)
  - Token count
- Reduces context usage to <10% of full document for targeted queries

### Developer Experience
- **Type Safety**: 100% type coverage with mypy strict mode
- **Code Quality**: Zero ruff linting issues
- **FastMCP Integration**: Simple decorator-based tool registration
- **Error Handling**: Graceful handling of missing files, sections, encoding issues

---

## Installation

### Requirements

- **Python**: 3.10 or higher
- **Operating System**: macOS, Linux, or Windows
- **MCP Client**: Claude Desktop, Continue, or any MCP-compatible client

### Method 1: Install from Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/prefrontal-systems/mcp-smart-reader.git
cd mcp-smart-reader

# Install with uv (recommended - faster, better dependency resolution)
uv sync

# Or install with pip
pip install -e .
```

### Method 2: Install from PyPI (Coming Soon)

```bash
pip install mcp-smart-reader
```

### Verify Installation

```bash
# Test imports
python -c "from mcp_smart_reader.server import smart_read; print('✓ Installation successful')"

# Check command availability
mcp-smart-reader --help
```

---

## Configuration

### Claude Desktop

Add to your Claude Desktop MCP configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "smart-reader": {
      "command": "mcp-smart-reader",
      "env": {}
    }
  }
}
```

If you installed in a virtual environment, provide the full path:

```json
{
  "mcpServers": {
    "smart-reader": {
      "command": "/absolute/path/to/.venv/bin/mcp-smart-reader",
      "env": {}
    }
  }
}
```

### Continue (VS Code Extension)

Add to `~/.continue/config.json`:

```json
{
  "mcpServers": [
    {
      "name": "smart-reader",
      "command": "mcp-smart-reader",
      "env": {}
    }
  ]
}
```

### Other MCP Clients

For custom MCP clients, start the server via stdio:

```bash
mcp-smart-reader
```

The server communicates over stdin/stdout using JSON-RPC 2.0 per the MCP protocol.

---

## Usage

### Tool 1: `smart_read` - Intelligent Document Reading

Automatically summarizes large files or returns full content for small files.

**Parameters**:
- `file_path` (string, required): Path to file to read
- `mode` (string, optional): Reading mode
  - `"auto"` (default): Summarize if >10K tokens
  - `"summary"`: Always return summary
  - `"full"`: Never summarize, return full content
- `summary_style` (string, optional): Summary generation style
  - `"structured"` (default): Keywords + abstract + headers + key points
  - `"extractive"`: Key sentences only (future enhancement)
  - `"abstract"`: Just abstract section if available (future enhancement)

**Example**:

```python
# Auto mode (summarize if >10K tokens)
result = smart_read("paper.md")

# Force summary regardless of size
result = smart_read("document.pdf", mode="summary")

# Always return full content
result = smart_read("notes.txt", mode="full")
```

**Response Structure** (Summary):

```python
{
    "_preamble": "⚠️ DOCUMENT SUMMARY (NOT FULL CONTENT)\n...",
    "content": "KEYWORDS: ...\n\nABSTRACT:\n...\n\nSECTIONS:\n...",
    "type": "summary",
    "style": "structured",
    "original_tokens": 53132,
    "summary_tokens": 797,
    "reduction_factor": 66.7,
    "sections": {
        "count": 42,
        "headers": ["Abstract", "Introduction", "Background", ...],
        "note": "Use list_sections() for complete list"
    },
    "coverage": {
        "included": {
            "abstract": true,
            "keywords": true,
            "section_headers": true,
            "key_findings": true
        },
        "excluded": {
            "detailed_methods": true,
            "complete_citations": true,
            "code_examples": true,
            "tables_and_figures": true
        },
        "completeness_score": 0.015
    },
    "original": {
        "path": "/absolute/path/to/paper.md",
        "filename": "paper.md",
        "size_bytes": 215420,
        "size_tokens": 53132
    },
    "confidence": {
        "completeness": 0.015,
        "recommended_for": ["initial_understanding", "overview", "triage"],
        "not_recommended_for": ["detailed_analysis", "citation", "implementation"]
    }
}
```

**Response Structure** (Full):

```python
{
    "content": "Full document text...",
    "type": "full",
    "tokens": 8523,
    "path": "/absolute/path/to/document.md"
}
```

---

### Tool 2: `read_section` - Extract Specific Sections

Extract a specific markdown section without loading the entire document.

**Parameters**:
- `file_path` (string, required): Path to file
- `section_heading` (string, required): Heading to search for
  - Case-insensitive
  - Partial match (e.g., "3.1" matches "## 3.1 Methods")
  - Matches first occurrence if multiple sections have same name

**Example**:

```python
# Extract by section number
result = read_section("paper.md", "3.1")

# Extract by section name
result = read_section("paper.md", "Methods")

# Extract by partial match
result = read_section("paper.md", "Core Protocol")  # Matches "## 3.1 Core Protocol"
```

**Response Structure** (Success):

```python
{
    "content": "## 3.1 Methods\n\nWe collected data from...",
    "type": "section",
    "section": "3.1",
    "heading_level": 2,
    "tokens": 1247,
    "start_line": 158,
    "end_line": 203
}
```

**Response Structure** (Error):

```python
{
    "content": "ERROR: Section '3.5' not found",
    "type": "error",
    "section": "3.5",
    "error": "Section '3.5' not found in document"
}
```

---

### Tool 3: `list_sections` - Table of Contents

Get a complete list of section headers from a document.

**Parameters**:
- `file_path` (string, required): Path to file

**Example**:

```python
result = list_sections("paper.md")
```

**Response Structure**:

```python
{
    "sections": [
        "Abstract",
        "Introduction",
        "Background",
        "2.1 Prior Work",
        "2.2 Limitations",
        "3. Methodology",
        "3.1 Data Collection",
        "3.2 Analysis",
        "4. Results",
        "5. Discussion",
        "Conclusion"
    ],
    "count": 11,
    "type": "toc",
    "path": "/absolute/path/to/paper.md",
    "note": "Use read_section(file_path, heading) to read specific section"
}
```

---

## Architecture

### Two-Module Design

MCP Smart Reader follows a clean separation of concerns:

```
src/mcp_smart_reader/
├── server.py        # MCP tool definitions (@mcp.tool decorators)
└── summarizer.py    # Pure text processing functions
```

**server.py** (MCP Layer):
- Defines three MCP tools using FastMCP decorators
- Handles file I/O and error responses
- Calls pure functions from summarizer.py
- Returns structured responses per MCP protocol

**summarizer.py** (Processing Layer):
- Token counting with tiktoken (cl100k_base encoding)
- Summary generation combining extraction functions
- Markdown section parsing with regex
- All pure functions with complete type annotations

### Dependencies

**Core**:
- `fastmcp>=0.3.0` - MCP server framework
- `tiktoken>=0.8.0` - Token counting (OpenAI/Claude compatible)

**Development**:
- `mypy>=1.11.0` - Type checking (strict mode)
- `ruff>=0.6.0` - Linting and formatting
- `pytest>=8.0.0` - Testing framework (future)
- `pytest-cov>=6.0.0` - Coverage reporting (future)

---

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/prefrontal-systems/mcp-smart-reader.git
cd mcp-smart-reader

# Install with development dependencies
uv sync  # or: pip install -e ".[dev]"

# Verify installation
python -c "from mcp_smart_reader.server import smart_read; print('✓ Setup complete')"
```

### Code Quality Checks

```bash
# Type checking (must report 0 errors)
mypy src/mcp_smart_reader

# Linting (must report 0 issues)
ruff check src/mcp_smart_reader

# Auto-fix linting issues
ruff check --fix src/mcp_smart_reader

# Format code
ruff format src/mcp_smart_reader
```

### Running the Server Locally

```bash
# Start server (stdio mode)
mcp-smart-reader

# Or run directly with Python
python -m mcp_smart_reader.server
```

The server will listen on stdin/stdout for JSON-RPC 2.0 messages.

### Testing

```bash
# Run tests (once test suite is implemented)
pytest

# Run with coverage
pytest --cov=mcp_smart_reader --cov-report=html
```

**Note**: Comprehensive test suite is deferred to future feature (see [Roadmap](#roadmap)).

---

## Speckit Workflow

This project uses **Speckit** - a structured development workflow system integrated with Claude Code.

### Available Commands

Execute via Claude Code slash commands:

- `/speckit.specify` - Create/update feature specifications
- `/speckit.clarify` - Identify underspecified areas and ask questions
- `/speckit.plan` - Generate implementation plan
- `/speckit.tasks` - Break down into dependency-ordered tasks
- `/speckit.implement` - Execute task list with tracking
- `/speckit.analyze` - Validate consistency across artifacts
- `/speckit.checklist` - Generate feature-specific checklists
- `/speckit.constitution` - Create/update project constitution

### Workflow Example

```bash
# 1. Create feature specification
/speckit.specify "Add PDF support for smart_read"

# 2. Clarify ambiguities
/speckit.clarify

# 3. Generate implementation plan
/speckit.plan

# 4. Generate task breakdown
/speckit.tasks

# 5. Execute implementation
/speckit.implement

# 6. Validate consistency
/speckit.analyze
```

### Constitution

The project follows five core principles defined in `.specify/memory/constitution.md` (v1.0.0):

1. **Token Efficiency First** - Prioritize reducing token usage
2. **Metadata Completeness** - Return rich metadata, not just content
3. **Type Safety & Testing** - 100% type coverage, 90%+ test coverage
4. **Simplicity & Modularity** - Two-module architecture, pure functions
5. **Speckit-Driven Development** - Follow structured workflow

See [Constitution](./specify/memory/constitution.md) for complete details.

---

## Project Status

### Completed Features (v0.1.0)

- ✅ Token counting with tiktoken (cl100k_base encoding)
- ✅ Automatic summarization for files >10K tokens
- ✅ Structured summary generation (keywords, abstract, headers, key points)
- ✅ Section extraction with metadata (heading level, line numbers, tokens)
- ✅ Three MCP tools: `smart_read`, `read_section`, `list_sections`
- ✅ FastMCP server deployment via `mcp-smart-reader` command
- ✅ Type safety: 100% coverage with mypy strict mode
- ✅ Code quality: Zero ruff linting issues
- ✅ Complete speckit workflow infrastructure

### Roadmap

**v0.2.0 - Testing & Quality** (Next):
- Comprehensive test suite (pytest)
- 90%+ test coverage for core functions
- Integration tests with MCP client
- Performance benchmarks

**v0.3.0 - Format Support**:
- PDF document support
- DOCX document support
- Multi-format summarization

**v0.4.0 - Advanced Summarization**:
- LLM-based summarization (optional)
- Customizable extraction rules
- Summary quality metrics

**v0.5.0 - Performance**:
- Caching layer for repeated reads
- Concurrent request handling
- Memory usage optimization

See [specs/](./specs/) for detailed feature specifications.

---

## Documentation

### Core Documentation

- **[README.md](./README.md)** - This file (overview, installation, usage)
- **[CLAUDE.md](./CLAUDE.md)** - Architecture guidance for Claude Code
- **[quickstart.md](./specs/001-naming-refactor-server/quickstart.md)** - Quick start guide

### Feature Documentation

Each feature has complete documentation in `specs/[feature-id]/`:

- **spec.md** - User stories, requirements, success criteria
- **plan.md** - Implementation plan with constitution checks
- **research.md** - Technical decisions and alternatives
- **data-model.md** - Entity definitions and schemas
- **contracts/README.md** - MCP tool contracts (JSON-RPC schemas)
- **tasks.md** - Dependency-ordered task breakdown

**Completed Features**:
- [001-naming-refactor-server](./specs/001-naming-refactor-server/) - Core implementation (v0.1.0)

---

## Contributing

### Bug Reports

Found a bug? Please [open an issue](https://github.com/prefrontal-systems/mcp-smart-reader/issues) with:

- Clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (OS, Python version, MCP client)

### Feature Requests

Have an idea? Please [open an issue](https://github.com/prefrontal-systems/mcp-smart-reader/issues) with:

- Clear description of the feature
- Use case and motivation
- Example usage (if applicable)

We'll review and potentially create a feature specification using `/speckit.specify`.

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Follow speckit workflow**:
   - Create feature spec in `specs/[feature-id]/`
   - Run constitution checks
   - Implement with task tracking
   - Validate with `/speckit.analyze`
4. **Ensure quality**:
   - `mypy src/` reports 0 errors
   - `ruff check src/` reports 0 issues
   - All new functions have type annotations
5. **Commit with descriptive messages**
6. **Push and create pull request**

See [CLAUDE.md](./CLAUDE.md) for development guidelines.

---

## Related Projects

### By Prefrontal Systems

- **[CortexGraph](https://github.com/prefrontal-systems/cortexgraph)** - Temporal memory MCP server with spaced repetition
- **[PrefrontalOS](https://github.com/prefrontal-systems/prefrontalos)** - Cognitive operating system architecture (coming soon)
- **[STOPPER Protocol](https://github.com/prefrontal-systems/stopper-paper)** - Executive function framework for AI assistants

### Research

- **[E-FIT Research](https://github.com/mnemexai/e-fit-research)** - Eight DBT/CBT techniques adapted for AI
- **[Anastrophex](https://github.com/mnemexai/anastrophex)** - Three-tier cognitive OS design
- **[Mnemex](https://github.com/mnemexai/mnemex)** - Temporal memory system with human-like forgetting

---

## License

**Apache License 2.0**

Copyright 2025 Prefrontal Systems LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

---

## Contact

**Scot Campbell**
Prefrontal Systems LLC
Email: scot@prefrontal.systems
Website: https://prefrontal.systems
GitHub: [@prefrontal-systems](https://github.com/prefrontal-systems)

**Research Profile**:
Personal GitHub: [@mnemexai](https://github.com/mnemexai)
Blog: [simpleminded.bot](https://simpleminded.bot)
ORCID: [0009-0000-6579-2895](https://orcid.org/0009-0000-6579-2895)

---

## Acknowledgments

- **FastMCP** - Excellent MCP server framework by [jlowin](https://github.com/jlowin)
- **tiktoken** - OpenAI's token counting library
- **Anthropic** - MCP protocol specification and Claude Code
- **Speckit** - Structured development workflow system

---

**Built with [Claude Code](https://claude.com/claude-code)**

Co-Authored-By: Claude <noreply@anthropic.com>
