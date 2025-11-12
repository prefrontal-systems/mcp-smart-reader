<!--
SYNC IMPACT REPORT - Constitution Update
===========================================
Version Change: Initial → 1.0.0 (MINOR)
Created: 2025-11-12

Rationale: First constitution for MCP Smart Reader project. Sets foundational
principles for token efficiency, type safety, metadata completeness, and speckit
workflow integration.

New Principles:
  I. Token Efficiency First - Core mission: minimize context consumption
  II. Metadata Completeness - Rich metadata enables intelligent tool usage
  III. Type Safety & Testing - Strict mypy + pytest mandatory
  IV. Simplicity & Modularity - Two-module architecture, resist complexity creep
  V. Speckit-Driven Development - Use structured workflow for all features

Templates Reviewed:
  ✅ spec-template.md - Aligned (user stories, requirements, success criteria)
  ✅ plan-template.md - Aligned (constitution check section references this file)
  ✅ tasks-template.md - Aligned (test-first optional, user story organization)

Follow-up TODOs:
  - None (all placeholders filled)

Commit Message Suggestion:
  docs: initialize constitution v1.0.0 (token efficiency + type safety principles)
-->

# MCP Smart Reader Constitution

## Core Principles

### I. Token Efficiency First

Every feature MUST be evaluated for its impact on token consumption. The primary mission is to reduce context window usage while preserving information value.

**Requirements**:
- All tools MUST track and report token counts (original vs. processed)
- Summaries MUST include completeness metadata so Claude knows when to request more detail
- Section extraction MUST be preferred over full-file loading for targeted queries
- Token reduction factor MUST be measured and optimized (target: >90% for large files)

**Rationale**: This project exists to solve Claude's context window limitations. Token efficiency is not a nice-to-have—it's the core value proposition.

### II. Metadata Completeness

Summaries without guidance are context traps. Every response MUST include rich metadata that enables intelligent follow-up actions.

**Requirements**:
- All summary responses MUST include `_preamble` with usage guidance
- Coverage metadata MUST specify what's included/excluded
- Confidence scores MUST indicate recommended use cases
- Cross-references MUST be provided (e.g., "use read_section() for details")
- Section counts and headers MUST be included for navigation

**Rationale**: Token efficiency means nothing if Claude doesn't know when summaries are insufficient. Metadata turns summaries into actionable tools.

### III. Type Safety & Testing

Code quality is non-negotiable. Strict type checking prevents bugs; comprehensive tests validate behavior.

**Requirements**:
- All functions MUST have complete type annotations (mypy strict mode)
- All modules MUST pass `mypy src/` with zero errors
- Code MUST pass ruff linting (E, F, I, N, W rules)
- Test coverage MUST be measured (target: >80% for core logic)
- Tests are OPTIONAL per feature spec, but when written MUST follow red-green-refactor

**Rationale**: MCP servers are reliability-critical. Type errors and untested code cause silent failures that waste user time.

### IV. Simplicity & Modularity

Start simple. Resist complexity creep. Every abstraction must justify its existence.

**Requirements**:
- Core logic MUST remain in two modules: `server.py` (MCP tools) and `summarizer.py` (text processing)
- New modules MUST be justified in constitution amendment
- Dependencies MUST be minimal (current: fastmcp, tiktoken; additions require justification)
- Functions MUST have single, clear responsibilities
- File format support MUST be addable without core architecture changes

**Rationale**: Early-stage projects accumulate complexity fast. The two-module design is sufficient until proven otherwise through real implementation experience.

### V. Speckit-Driven Development

All non-trivial features MUST follow the speckit workflow. No implementation without specification.

**Requirements**:
- New features MUST start with `/speckit.specify` (user stories, requirements, success criteria)
- Ambiguities MUST be resolved via `/speckit.clarify` before planning
- Implementation plans MUST be generated via `/speckit.plan` before coding
- Tasks MUST be broken down via `/speckit.tasks` with user story organization
- Constitution checks MUST pass before Phase 0 research

**Rationale**: Ad-hoc development leads to scope creep and misaligned implementations. Speckit enforces deliberate design and clear acceptance criteria.

## Development Workflow

### Pre-Implementation Gates

Before writing code for any feature:

1. **Specify** (`/speckit.specify`): Define user stories (prioritized P1, P2, P3), functional requirements, success criteria
2. **Clarify** (`/speckit.clarify`): Resolve underspecified areas via targeted questions
3. **Plan** (`/speckit.plan`): Generate technical approach, structure, constitution compliance check
4. **Constitution Check**: Verify no principle violations; if violations exist, justify in complexity tracking table
5. **Tasks** (`/speckit.tasks`): Break down into dependency-ordered, user-story-organized tasks
6. **Implement** (`/speckit.implement`): Execute task list with test-first approach (if tests requested)

### Implementation Rules

- Tests (when included) MUST be written first and MUST fail before implementation (red-green-refactor)
- User stories MUST be independently testable (each story is an MVP increment)
- Commits MUST be granular (per task or logical group)
- Type checking MUST pass before commit (`mypy src/`)
- Linting MUST pass before commit (`ruff check src/`)

### Quality Standards

- **Type coverage**: 100% (all functions have type hints)
- **Test coverage**: >80% for core logic (when tests are written)
- **Line length**: 100 characters (ruff enforced)
- **Python version**: 3.10+ (target-version in ruff config)

## Technology Constraints

### Stack

- **Language**: Python 3.10+
- **Framework**: FastMCP >=0.3.0 (MCP server)
- **Token counting**: tiktoken >=0.8.0 (cl100k_base encoding)
- **Testing**: pytest >=8.0.0 + pytest-cov >=6.0.0
- **Type checking**: mypy >=1.11.0 (strict mode)
- **Linting**: ruff >=0.6.0

### Dependency Policy

New dependencies MUST be justified via:
- Problem it solves (specific use case)
- Why existing tools insufficient
- License compatibility (Apache 2.0 compatible)
- Maintenance status (active, stable)

Rejected without justification:
- Web frameworks (FastMCP is sufficient)
- Alternative type checkers (mypy is sufficient)
- Alternative linters (ruff is sufficient)
- LLM libraries (tiktoken is sufficient for token counting)

## Architecture Constraints

### Module Structure

Current architecture:
```
src/mcp_smart_reader/
├── __init__.py        # Package exports
├── server.py          # MCP tools (smart_read, read_section, list_sections)
└── summarizer.py      # Text processing (extract_*, estimate_tokens, generate_summary)

tests/
└── (to be defined per feature spec)
```

**Expansion Rules**:
- New modules MUST be proposed via `/speckit.plan` with justification
- Each module MUST have single, clear responsibility
- Cross-module dependencies MUST be minimized
- Circular dependencies are FORBIDDEN

### File Format Support

Planned: Markdown (current), PDF, DOCX

**Integration Pattern**:
- Format detection in `server.py` (file extension)
- Format-specific extraction in `summarizer.py` or new `extractors/` module
- Common interface: `extract_text(path: Path) -> str`
- No format-specific logic in MCP tools

## Governance

### Amendment Process

Constitution changes MUST:
1. Be proposed via new principle or modified principle text
2. Include rationale (why needed, what problem it solves)
3. Specify version bump type (MAJOR/MINOR/PATCH)
4. Update dependent templates (spec, plan, tasks)
5. Document in Sync Impact Report (HTML comment at top of file)

### Version Semantics

- **MAJOR**: Principle removal, redefinition, or backward-incompatible governance change
- **MINOR**: New principle added, section expanded with new requirements
- **PATCH**: Clarifications, wording improvements, typo fixes (no semantic change)

### Compliance Review

Before merging feature branches:
- Constitution check (from plan.md) MUST show no unjustified violations
- Type checking MUST pass (`mypy src/`)
- Linting MUST pass (`ruff check src/`)
- Tests (if written) MUST pass (`pytest`)
- Speckit artifacts MUST exist (spec.md, plan.md, tasks.md)

### Complexity Justification

Violations of simplicity principles (Principle IV) MUST be documented in plan.md Complexity Tracking table:

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Example: 3rd module | Explain necessity | Why 2 modules insufficient |

Unjustified complexity results in constitution amendment proposal or implementation rejection.

**Version**: 1.0.0 | **Ratified**: 2025-11-12 | **Last Amended**: 2025-11-12
