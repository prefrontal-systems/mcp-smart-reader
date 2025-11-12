# Tasks: Core Implementation Fix & Server Deployment

**Input**: Design documents from `/specs/001-naming-refactor-server/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT included in this feature (per spec.md - tests deferred to future feature)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths assume single project - pure Python MCP server package

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project initialization and dependencies

- [ ] T001 Verify project structure matches plan.md (src/mcp_smart_reader/, pyproject.toml, README.md)
- [ ] T002 Verify dependencies declared in pyproject.toml (fastmcp>=0.3.0, tiktoken>=0.8.0, mypy>=1.11.0, ruff>=0.6.0)
- [ ] T003 [P] Verify Python 3.10+ installed and active (`python --version` >= 3.10)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Install package in development mode (`uv sync` or `pip install -e .`)
- [ ] T005 [P] Verify mypy configuration in pyproject.toml (strict mode, python 3.10+)
- [ ] T006 [P] Verify ruff configuration in pyproject.toml (line-length=100, target py310)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Developer Imports Working Functions (Priority: P1) 🎯 MVP

**Goal**: Fix critical import errors by implementing missing functions and resolving naming conflicts

**Independent Test**: Run `pip install -e .` then `python -c "from mcp_smart_reader.server import smart_read"` - should complete without ImportError

### Implementation for User Story 1

- [ ] T007 [P] [US1] Add `estimate_tokens(text: str) -> int` function to src/mcp_smart_reader/summarizer.py
- [ ] T008 [P] [US1] Add `generate_summary(content: str, style: str = "structured") -> str` function to src/mcp_smart_reader/summarizer.py
- [ ] T009 [US1] Add `extract_headers` alias for `extract_section_headers` in src/mcp_smart_reader/summarizer.py
- [ ] T010 [US1] Verify all imports in src/mcp_smart_reader/server.py resolve without ImportError
- [ ] T011 [US1] Run `mypy src/mcp_smart_reader` and fix any type errors to achieve zero errors
- [ ] T012 [US1] Run `ruff check src/mcp_smart_reader` and fix any linting issues

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

**Verification** (manual):
```bash
# Test imports
python -c "from mcp_smart_reader.summarizer import estimate_tokens; print('✓ estimate_tokens')"
python -c "from mcp_smart_reader.summarizer import generate_summary; print('✓ generate_summary')"
python -c "from mcp_smart_reader.summarizer import extract_headers; print('✓ extract_headers')"
python -c "from mcp_smart_reader.server import smart_read; print('✓ server imports')"

# Test type checking
mypy src/mcp_smart_reader  # Should report 0 errors

# Test linting
ruff check src/mcp_smart_reader  # Should report 0 issues
```

---

## Phase 4: User Story 2 - User Installs & Runs MCP Server (Priority: P2)

**Goal**: Enable FastMCP server deployment via `mcp-smart-reader` command

**Independent Test**: Run `pip install -e .` then `mcp-smart-reader` - server starts without errors and registers tools with MCP client

### Implementation for User Story 2

- [ ] T013 [US2] Verify entry point `mcp-smart-reader = "mcp_smart_reader.server:main"` exists in pyproject.toml [project.scripts]
- [ ] T014 [US2] Verify `main()` function in src/mcp_smart_reader/server.py calls `mcp.run()`
- [ ] T015 [US2] Test server startup: run `mcp-smart-reader` command and verify no ImportError or startup errors
- [ ] T016 [US2] Verify MCP tools registered: `smart_read`, `read_section`, `list_sections` appear in tool list

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

**Verification** (manual):
```bash
# Start server (will block - use Ctrl+C to stop)
mcp-smart-reader

# In separate terminal with MCP client configured:
# Query available tools - should see smart_read, read_section, list_sections
# Call smart_read with a test file
# Verify summary or full content returned
```

---

## Phase 5: User Story 3 - Developer Reads Document Sections (Priority: P3)

**Goal**: Implement markdown section extraction for targeted document reading

**Independent Test**: Call `read_section("paper.md", "3.1 Methods")` - returns just the Methods section content

### Implementation for User Story 3

- [ ] T017 [P] [US3] Add `extract_section_content(text: str, heading: str) -> str` helper function to src/mcp_smart_reader/summarizer.py
- [ ] T018 [US3] Update `read_section(file_path, section_heading)` in src/mcp_smart_reader/server.py to call `extract_section_content()`
- [ ] T019 [US3] Add return dict with content, type, section, heading_level, tokens, start_line, end_line in src/mcp_smart_reader/server.py read_section()
- [ ] T020 [US3] Add error handling for section not found (return dict with type="error", section, error message) in src/mcp_smart_reader/server.py read_section()
- [ ] T021 [US3] Run `mypy src/mcp_smart_reader` and fix any new type errors from read_section changes
- [ ] T022 [US3] Test section extraction with test markdown file containing multiple sections

**Checkpoint**: All user stories should now be independently functional

**Verification** (manual):
```bash
# Create test file
cat > test_doc.md << 'EOF'
# Introduction
This is the intro.

## 3.1 Methods
This is the methods section.

## 3.2 Results
This is results.
EOF

# Test with MCP client
# Call read_section("test_doc.md", "3.1") - should return only Methods section
# Call read_section("test_doc.md", "Nonexistent") - should return error
```

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final quality checks and documentation validation

- [ ] T023 [P] Run `mypy src/mcp_smart_reader` final verification (must report 0 errors)
- [ ] T024 [P] Run `ruff check src/mcp_smart_reader` final verification (must report 0 issues)
- [ ] T025 [P] Run `ruff format src/mcp_smart_reader` to ensure consistent formatting
- [ ] T026 Verify quickstart.md instructions work end-to-end (install, run server, test tools)
- [ ] T027 Update CLAUDE.md if any implementation details differ from plan (file paths, function signatures)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational (Phase 2) - No dependencies on other stories
  - User Story 2 (P2): DEPENDS on User Story 1 (server needs working imports)
  - User Story 3 (P3): DEPENDS on User Story 1 (needs `estimate_tokens`, `extract_headers`)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: DEPENDS on User Story 1 completion (server imports must resolve)
- **User Story 3 (P3)**: DEPENDS on User Story 1 completion (uses `estimate_tokens`, `extract_headers`)

### Within Each User Story

**User Story 1**:
- T007 (estimate_tokens) and T008 (generate_summary) can run in parallel [P]
- T009 (alias) independent, can run parallel with T007/T008
- T010 (verify imports) MUST wait for T007, T008, T009
- T011 (mypy) MUST wait for T010
- T012 (ruff) can run after T010, parallel with T011

**User Story 2**:
- T013 (verify entry point) and T014 (verify main) can run in parallel [P]
- T015 (test startup) MUST wait for T013, T014
- T016 (verify tools) MUST wait for T015

**User Story 3**:
- T017 (extract_section_content) independent
- T018-T020 sequential (update read_section, add return dict, add error handling)
- T021 (mypy) MUST wait for T018-T020
- T022 (test) can run after T018-T020 completed

### Parallel Opportunities

- Phase 1 Setup: T001, T002, T003 all parallel (different verifications)
- Phase 2 Foundational: T005, T006 parallel (config checks)
- User Story 1: T007, T008, T009 parallel (different functions, no dependencies)
- User Story 2: T013, T014 parallel (different files)
- Phase 6 Polish: T023, T024, T025 parallel (different tools)

---

## Parallel Example: User Story 1

```bash
# Launch all parallel tasks for User Story 1 together:
Task T007: "Add estimate_tokens() to src/mcp_smart_reader/summarizer.py"
Task T008: "Add generate_summary() to src/mcp_smart_reader/summarizer.py"
Task T009: "Add extract_headers alias to src/mcp_smart_reader/summarizer.py"

# Then sequential:
Task T010: "Verify imports resolve" (depends on T007, T008, T009)
Task T011: "Run mypy" (depends on T010)
Task T012: "Run ruff" (depends on T010)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Run import tests (estimate_tokens, generate_summary, extract_headers)
   - Run mypy (0 errors)
   - Run ruff (0 issues)
   - Verify server.py can be imported
5. If User Story 1 works: **MVP Complete!** Can deploy if needed

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **MVP Deployed** ✅
3. Add User Story 2 → Test independently → **Server Runnable** ✅
4. Add User Story 3 → Test independently → **Section Extraction** ✅
5. Each story adds value without breaking previous stories

### Sequential Team Strategy

With single developer:

1. Complete Setup + Foundational
2. Complete User Story 1 (P1) - highest priority
3. Verify US1 works independently
4. Complete User Story 2 (P2) - depends on US1
5. Verify US2 works independently
6. Complete User Story 3 (P3) - depends on US1
7. Verify US3 works independently
8. Complete Polish phase

---

## Notes

- [P] tasks = different files or independent work, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No tests in this feature (deferred to future test-writing feature per spec.md)
- Commit after each task or logical group (T007-T009 together, then T010, etc.)
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

## Implementation Details

### Task T007: estimate_tokens Implementation

Add to `src/mcp_smart_reader/summarizer.py`:
```python
import tiktoken

def estimate_tokens(text: str) -> int:
    """
    Count tokens using cl100k_base encoding.

    Args:
        text: Input text to count tokens for

    Returns:
        Number of tokens in text
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))
```

### Task T008: generate_summary Implementation

Add to `src/mcp_smart_reader/summarizer.py`:
```python
def generate_summary(content: str, style: str = "structured") -> str:
    """
    Generate summary by combining existing extractors.

    Args:
        content: Full document text
        style: Summary style ("structured", "extractive", "abstract")

    Returns:
        Summary text combining keywords, abstract, headers, key points
    """
    if style == "structured":
        keywords = extract_keywords_from_abstract(content)
        abstract = extract_abstract(content)
        headers = extract_section_headers(content)  # or extract_headers after alias
        key_points = extract_key_points(content, num_points=8)

        parts = []
        if keywords:
            parts.append("KEYWORDS: " + ", ".join(keywords))
        if abstract:
            parts.append("\nABSTRACT:\n" + abstract[:500] + "...")
        if headers:
            parts.append("\nSECTIONS:\n" + "\n".join(f"- {h}" for h in headers[:15]))
        if key_points:
            parts.append("\nKEY FINDINGS:\n" + "\n".join(f"- {p}" for p in key_points))

        return "\n".join(parts) if parts else content[:1000]

    # Fallback for other styles (future enhancement)
    return content[:1000]
```

### Task T009: extract_headers Alias

Add to `src/mcp_smart_reader/summarizer.py` (after `extract_section_headers` definition):
```python
# Alias for imports in server.py
extract_headers = extract_section_headers
```

### Task T017: extract_section_content Implementation

Add to `src/mcp_smart_reader/summarizer.py`:
```python
import re

def extract_section_content(text: str, heading: str) -> tuple[str, int, int, int] | tuple[None, None, None, None]:
    """
    Extract content of a specific markdown section.

    Args:
        text: Full document text
        heading: Section heading to find (case-insensitive, partial match)

    Returns:
        Tuple of (content, heading_level, start_line, end_line) if found,
        or (None, None, None, None) if not found
    """
    # Find all headings with their positions
    heading_pattern = r'^(#{1,6})\s+(.+?)$'
    headings = [(m.start(), m.group(1), m.group(2)) for m in re.finditer(heading_pattern, text, re.MULTILINE)]

    # Find target heading (case-insensitive, partial match)
    target_idx = None
    for i, (pos, level, title) in enumerate(headings):
        if heading.lower() in title.lower():
            target_idx = i
            break

    if target_idx is None:
        return (None, None, None, None)

    # Extract content from target heading to next same-level heading (or end)
    start_pos = headings[target_idx][0]
    target_level = len(headings[target_idx][1])

    end_pos = len(text)
    for i in range(target_idx + 1, len(headings)):
        if len(headings[i][1]) <= target_level:
            end_pos = headings[i][0]
            break

    content = text[start_pos:end_pos].strip()

    # Calculate line numbers
    start_line = text[:start_pos].count('\n') + 1
    end_line = text[:end_pos].count('\n') + 1

    return (content, target_level, start_line, end_line)
```

### Task T018-T020: Update read_section

Replace placeholder in `src/mcp_smart_reader/server.py` `read_section()`:
```python
@mcp.tool()
def read_section(file_path: str, section_heading: str) -> dict:
    """
    Extract specific section from document without loading entire file into context.
    """
    path = Path(file_path)

    if not path.exists():
        return {"error": f"File not found: {file_path}", "type": "error"}

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"Error reading file: {str(e)}", "type": "error"}

    # Extract section
    section_content, heading_level, start_line, end_line = extract_section_content(content, section_heading)

    if section_content is None:
        return {
            "content": f"ERROR: Section '{section_heading}' not found",
            "type": "error",
            "section": section_heading,
            "error": f"Section '{section_heading}' not found in document"
        }

    # Success - return section with metadata
    section_tokens = estimate_tokens(section_content)

    return {
        "content": section_content,
        "type": "section",
        "section": section_heading,
        "heading_level": heading_level,
        "tokens": section_tokens,
        "start_line": start_line,
        "end_line": end_line
    }
```
