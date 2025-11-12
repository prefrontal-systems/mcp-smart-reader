# Feature Specification: Core Implementation Fix & Server Deployment

**Feature Branch**: `001-naming-refactor-server`
**Created**: 2025-11-12
**Status**: Draft
**Input**: User description: "refactor conflicting naming conventions. From there implement fastmcp per README.md to allow the summarization tools to be available for use once installed"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Imports Working Functions (Priority: P1)

As a developer integrating MCP Smart Reader into my project, I need to import and use the summarization functions without encountering missing function errors, so I can implement document processing features reliably.

**Why this priority**: This is a blocking bug. The codebase currently has import errors where `server.py` imports functions that don't exist in `summarizer.py`. Without fixing this, the package cannot be used at all.

**Independent Test**: Install the package via `pip install -e .`, run `python -c "from mcp_smart_reader.server import smart_read"` - should complete without ImportError.

**Acceptance Scenarios**:

1. **Given** the package is installed, **When** importing `estimate_tokens` from `summarizer`, **Then** the function is available and callable
2. **Given** the package is installed, **When** importing `generate_summary` from `summarizer`, **Then** the function is available and callable
3. **Given** the package is installed, **When** importing `extract_headers` from `summarizer`, **Then** the function is available (not `extract_section_headers`)
4. **Given** all imports succeed, **When** running `mypy src/`, **Then** no type errors are reported

---

### User Story 2 - User Installs & Runs MCP Server (Priority: P2)

As a Claude user, I want to install the MCP Smart Reader package and run the server command so that the summarization tools become available in my MCP client immediately after installation.

**Why this priority**: This enables the actual use case. Once the core functions exist (P1), users need a simple way to deploy the server.

**Independent Test**: Run `pip install -e .` then `mcp-smart-reader` - server starts without errors and registers tools with MCP client.

**Acceptance Scenarios**:

1. **Given** the package is installed, **When** running `mcp-smart-reader` command, **Then** the FastMCP server starts and listens for requests
2. **Given** the server is running, **When** MCP client queries available tools, **Then** `smart_read`, `read_section`, and `list_sections` are listed
3. **Given** the server is running, **When** calling `smart_read("/path/to/file.md")`, **Then** a summary or full content is returned based on token count

---

### User Story 3 - Developer Reads Document Sections (Priority: P3)

As a developer using the MCP server, I want to extract specific document sections by heading so I can retrieve targeted information without loading entire large files into context.

**Why this priority**: Enhances token efficiency but requires section parsing logic that doesn't exist yet. MVP works without this (full summaries are still useful).

**Independent Test**: Call `read_section("paper.md", "3.1 Methods")` - returns just the Methods section content.

**Acceptance Scenarios**:

1. **Given** a document with markdown headers, **When** calling `read_section(file_path, "Introduction")`, **Then** only the Introduction section text is returned
2. **Given** a document with numbered sections (e.g., "3.1"), **When** calling `read_section(file_path, "3.1")`, **Then** only section 3.1 content is returned
3. **Given** a non-existent section name, **When** calling `read_section(file_path, "Nonexistent")`, **Then** an error message is returned indicating section not found

---

### Edge Cases

- What happens when `estimate_tokens()` is called with extremely large text (>1M characters)?
- What happens when `generate_summary()` is called on a file with no recognizable structure (no headers, no abstract)?
- How does the server handle concurrent requests to `smart_read()` on the same file?
- What happens when `extract_headers()` encounters malformed markdown (e.g., headers without space after `#`)?
- How does `read_section()` handle sections with identical names (e.g., two "Introduction" sections)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an `estimate_tokens(text: str) -> int` function that counts tokens using tiktoken's `cl100k_base` encoding
- **FR-002**: System MUST provide a `generate_summary(content: str, style: str) -> str` function that combines existing extraction functions to produce structured summaries
- **FR-003**: System MUST export `extract_headers` (not `extract_section_headers`) to match imports in `server.py`
- **FR-004**: System MUST implement `read_section()` logic to extract markdown sections by heading name
- **FR-005**: MCP server MUST be runnable via `mcp-smart-reader` command after installation
- **FR-006**: MCP server MUST register three tools: `smart_read`, `read_section`, `list_sections`
- **FR-007**: All functions MUST pass strict mypy type checking with complete type annotations
- **FR-008**: All imports in `server.py` MUST resolve successfully without ImportError
- **FR-009**: `smart_read()` tool MUST return summaries for files >10K tokens with metadata (preamble, coverage, confidence)
- **FR-010**: `list_sections()` tool MUST return document table of contents with section headers extracted from markdown

### Key Entities

- **Summary Response**: Contains summary text, token counts (original, summary), reduction factor, sections metadata, coverage indicators, confidence scores, and usage guidance preamble
- **Section**: Represents a markdown heading and its associated content (heading text, level, start/end positions, extracted content)
- **Token Count**: Integer representing number of tokens in text according to cl100k_base encoding

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developer can install package and import all functions from `summarizer` module without errors (0 ImportError exceptions)
- **SC-002**: Package passes all type checks with zero mypy errors when running `mypy src/`
- **SC-003**: User can run `mcp-smart-reader` command and server starts within 2 seconds
- **SC-004**: MCP server successfully registers all three tools and responds to tool queries within 500ms
- **SC-005**: `smart_read()` produces summaries for files >10K tokens with >90% token reduction while preserving key information (keywords, abstract, main sections)
- **SC-006**: `read_section()` extracts specific sections without loading full file content, reducing context usage to <10% of full document for targeted queries

## Assumptions

- Users have Python 3.10+ installed (per pyproject.toml requirement)
- Users install via `pip install -e .` or `uv sync` (development mode)
- MCP client is configured to connect to the server (configuration setup is outside scope)
- Documents are primarily markdown format (PDF/DOCX support deferred to future features)
- Token counting uses OpenAI's cl100k_base encoding (compatible with Claude)
- Section extraction uses standard markdown heading syntax (`#`, `##`, `###`)
- Summaries are "good enough" if they include abstract, keywords, and main section headers (detailed quality metrics deferred)

## Out of Scope

- PDF and DOCX format support (future feature)
- Caching layer for repeated document reads (future optimization)
- Advanced summarization algorithms beyond current extraction-based approach (future enhancement)
- Multi-language document support (assume English markdown documents)
- Authentication or authorization for MCP server access (assume trusted local environment)
- Performance optimization for concurrent requests (single-threaded operation acceptable for MVP)
