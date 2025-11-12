# Implementation Plan: Core Implementation Fix & Server Deployment

**Branch**: `001-naming-refactor-server` | **Date**: 2025-11-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-naming-refactor-server/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Fix critical import errors and missing implementations in MCP Smart Reader to enable package installation and server deployment. Three prioritized user stories: (P1) Fix naming conflicts and implement missing functions (`estimate_tokens`, `generate_summary`, `extract_headers` alias), (P2) Enable FastMCP server via `mcp-smart-reader` command, (P3) Implement section extraction logic. Technical approach: Implement missing tiktoken-based token counting, combine existing extractors into summary generator, add markdown section parser, ensure FastMCP `main()` is callable via entry point.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: FastMCP >=0.3.0, tiktoken >=0.8.0, mypy >=1.11.0 (strict mode), ruff >=0.6.0
**Storage**: N/A (stateless text processing, no persistence)
**Testing**: pytest >=8.0.0 + pytest-cov >=6.0.0 (tests optional per feature spec)
**Target Platform**: Local development machine (macOS/Linux/Windows), MCP client environment
**Project Type**: Single project (MCP server package)
**Performance Goals**: Server startup <2s, tool queries <500ms response, token counting <100ms for 50K char documents
**Constraints**: >90% token reduction for large files, zero mypy errors (strict mode), 100% type coverage
**Scale/Scope**: 2 modules (server.py, summarizer.py), 3 MCP tools, ~500 LOC total

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Token Efficiency First ✅ PASS

**Requirements**:
- All tools MUST track and report token counts ✅ (FR-009 requires metadata with token counts)
- Summaries MUST include completeness metadata ✅ (FR-009 requires preamble, coverage, confidence)
- Section extraction MUST be preferred ✅ (FR-004 implements `read_section()`)
- Token reduction >90% for large files ✅ (SC-005 requires >90% reduction)

**Status**: COMPLIANT - Feature directly implements token efficiency principles

### Principle II: Metadata Completeness ✅ PASS

**Requirements**:
- Summary responses MUST include `_preamble` ✅ (existing in server.py:38-59)
- Coverage metadata MUST specify included/excluded ✅ (existing in server.py:133-149)
- Confidence scores MUST indicate use cases ✅ (existing in server.py:156-170)
- Cross-references MUST be provided ✅ (preamble includes "read_section()" guidance)
- Section counts and headers included ✅ (server.py:128-132)

**Status**: COMPLIANT - Metadata structure already designed, needs implementation only

### Principle III: Type Safety & Testing ✅ PASS

**Requirements**:
- Complete type annotations (mypy strict) ✅ (FR-007 mandates this)
- Zero mypy errors ✅ (SC-002 requires "mypy src/" passes)
- Ruff linting passes ✅ (constitution requires E, F, I, N, W rules)
- Test coverage >80% if tests written ⚠️ (tests optional per spec, not in this feature)
- Red-green-refactor if tests written ⚠️ (N/A - no tests in this feature)

**Status**: COMPLIANT - Type safety enforced, tests deferred to future feature

### Principle IV: Simplicity & Modularity ✅ PASS

**Requirements**:
- Core logic in 2 modules only ✅ (server.py, summarizer.py unchanged)
- New modules justified via amendment ✅ (no new modules proposed)
- Dependencies minimal ✅ (fastmcp, tiktoken already approved)
- Single responsibility per function ✅ (estimate_tokens, generate_summary, read_section each distinct)
- File format support addable without core changes ✅ (PDF/DOCX deferred, no architecture change needed)

**Status**: COMPLIANT - No new modules, no new dependencies, maintains two-module architecture

### Principle V: Speckit-Driven Development ✅ PASS

**Requirements**:
- Feature started with `/speckit.specify` ✅ (spec.md exists)
- Ambiguities resolved via `/speckit.clarify` ✅ (no NEEDS CLARIFICATION in spec)
- Plan generated via `/speckit.plan` ✅ (this document)
- Tasks via `/speckit.tasks` ⏳ (next step after plan)
- Constitution check passed ✅ (this section)

**Status**: COMPLIANT - Following speckit workflow as required

### Overall Constitution Compliance: ✅ PASS

**No violations identified**. Feature implementation aligns with all five core principles. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/001-naming-refactor-server/
├── spec.md                  # Feature specification
├── plan.md                  # This file (/speckit.plan output)
├── research.md              # Phase 0 output (technical decisions)
├── data-model.md            # Phase 1 output (entity definitions)
├── quickstart.md            # Phase 1 output (usage guide)
├── contracts/               # Phase 1 output (API definitions)
│   └── (empty - no HTTP APIs, MCP tools only)
└── checklists/
    └── requirements.md      # Spec quality validation (completed)
```

### Source Code (repository root)

```text
src/mcp_smart_reader/
├── __init__.py              # Package exports
├── server.py                # MCP tools (smart_read, read_section, list_sections)
└── summarizer.py            # Text processing functions (CHANGES NEEDED):
                              # - Add: estimate_tokens(text: str) -> int
                              # - Add: generate_summary(content: str, style: str) -> str
                              # - Rename: extract_section_headers → extract_headers
                              # - Add: extract_section_content(text: str, heading: str) -> str

tests/
└── (no tests in this feature - deferred to future test-writing feature)

pyproject.toml               # Dependencies already defined, no changes needed
README.md                    # Installation instructions already documented
```

**Structure Decision**: Single project structure (Option 1) is used. This is a pure Python package with no frontend, backend split, or mobile components. The two-module architecture (server.py, summarizer.py) is maintained per Constitution Principle IV. No structural changes needed - only adding missing functions to existing modules.

## Complexity Tracking

> **No violations identified** - This section intentionally left empty per Constitution Check results.

No complexity justification required. Feature maintains two-module architecture, adds no new dependencies, and follows all constitutional principles.

---

## Phase 0: Research (Completed)

**Artifacts Generated**:
- ✅ `research.md` - Technical decisions and implementation approaches
  - Token counting: tiktoken cl100k_base encoding
  - Summary generation: Extraction-based combining existing functions
  - Section extraction: Regex-based markdown parsing
  - Server deployment: FastMCP entry point already configured
  - Function naming: Alias pattern for backward compatibility

**Key Decisions**:
- No new dependencies required (tiktoken, fastmcp already declared)
- No new modules needed (maintain two-module architecture)
- All edge cases addressed (large files, malformed markdown, missing sections)
- Performance validated: <2s startup, <500ms responses, <100ms token counting

**Constitution Re-Check**: ✅ PASS (no changes from initial check)

---

## Phase 1: Design & Contracts (Completed)

**Artifacts Generated**:
- ✅ `data-model.md` - Entity definitions (Summary Response, Section, Token Count)
- ✅ `contracts/README.md` - MCP tool contracts (JSON-RPC schemas)
- ✅ `quickstart.md` - Installation and usage guide
- ✅ `CLAUDE.md` updated - Active technologies section added

**Entity Definitions**:
- **Summary Response**: 15+ attributes with conditional presence based on type (summary vs. full)
- **Section**: 7 attributes for extracted sections with success/error states
- **Token Count**: Simple int (pure function output)

**API Contracts**:
- **smart_read**: Input (file_path, mode, style) → Output (Summary Response or Full Content)
- **read_section**: Input (file_path, section_heading) → Output (Section or Error)
- **list_sections**: Input (file_path) → Output (array of headers)

**Constitution Re-Check**: ✅ PASS

### Principle I: Token Efficiency First
- **Status**: COMPLIANT
- Data model explicitly tracks token counts (original, summary, reduction_factor)
- Section extraction enables <10% context usage for targeted queries
- Metadata guides Claude when to request more detail

### Principle II: Metadata Completeness
- **Status**: COMPLIANT
- Summary Response includes 8 metadata sections (preamble, coverage, confidence, etc.)
- Section Response includes line numbers, heading level, token count
- Cross-references provided in preamble

### Principle III: Type Safety & Testing
- **Status**: COMPLIANT
- TypedDict definitions provided in data-model.md for mypy validation
- All attributes typed with primitive types or Literal enums
- Validation rules specified per entity

### Principle IV: Simplicity & Modularity
- **Status**: COMPLIANT
- Two-module architecture maintained (no new modules)
- No new dependencies added
- Entities are simple value objects (no ORM, no state management)

### Principle V: Speckit-Driven Development
- **Status**: COMPLIANT
- Phase 0 and Phase 1 completed per speckit workflow
- Next step: `/speckit.tasks` for implementation breakdown

**Final Constitution Compliance**: ✅ ALL PRINCIPLES PASS

No violations introduced during design phase. Ready for task generation.
