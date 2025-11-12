# Data Model: Core Implementation Fix & Server Deployment

**Feature**: 001-naming-refactor-server
**Date**: 2025-11-12
**Purpose**: Define data structures and entities for summary responses, sections, and token counts

## Overview

This feature works with three primary entities: **Summary Response** (returned by `smart_read`), **Section** (extracted by `read_section`), and **Token Count** (computed by `estimate_tokens`). All entities are immutable value objects - no persistence or state management required.

## Entity: Summary Response

**Description**: Metadata-rich response returned by `smart_read()` tool when summarizing large files

**Purpose**: Provide Claude with summary content plus actionable guidance on when to request more detail

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `_preamble` | str | Yes | Warning text with usage guidance (formatted, multi-line) |
| `content` | str | Yes | Summary text or full content |
| `type` | Literal["summary", "full"] | Yes | Indicates if response is summarized or complete |
| `style` | str | Conditional | Summary generation style (only if type="summary") |
| `original_tokens` | int | Conditional | Token count of original file (only if type="summary") |
| `summary_tokens` | int | Conditional | Token count of summary (only if type="summary") |
| `reduction_factor` | float | Conditional | Original/summary ratio (only if type="summary") |
| `sections` | dict | Conditional | Section metadata (only if type="summary") |
| `sections.count` | int | Yes | Number of sections in document |
| `sections.headers` | list[str] | Yes | First 20 section headers |
| `sections.note` | str | Yes | Instructions to use list_sections() |
| `coverage` | dict | Conditional | What's included/excluded (only if type="summary") |
| `coverage.included` | dict | Yes | Boolean flags for included content types |
| `coverage.excluded` | dict | Yes | Boolean flags for excluded content types |
| `coverage.completeness_score` | float | Yes | Ratio of summary/original tokens (0.0-1.0) |
| `original` | dict | Conditional | Original file metadata (only if type="summary") |
| `original.path` | str | Yes | Absolute path to file |
| `original.filename` | str | Yes | Base filename |
| `original.size_bytes` | int | Yes | File size in bytes |
| `original.size_tokens` | int | Yes | File size in tokens |
| `confidence` | dict | Conditional | Usage guidance (only if type="summary") |
| `confidence.completeness` | float | Yes | Same as coverage.completeness_score |
| `confidence.recommended_for` | list[str] | Yes | Use cases where summary sufficient |
| `confidence.not_recommended_for` | list[str] | Yes | Use cases requiring full content |

**Validation Rules**:
- If `type="summary"`, all Conditional fields MUST be present
- If `type="full"`, only `content`, `type`, `tokens`, `path` present
- `reduction_factor` MUST be >= 1.0 (summary never larger than original)
- `completeness_score` MUST be between 0.0 and 1.0
- `sections.count` MUST match number of headers found in content

**State Transitions**: N/A (immutable response object)

**Example (Summary)**:
```python
{
    "_preamble": "⚠️ DOCUMENT SUMMARY (NOT FULL CONTENT)\nOriginal: 53,132 tokens → Summary: 797 tokens\n...",
    "content": "KEYWORDS: executive function, AI assistants, DBT\nABSTRACT:\n...",
    "type": "summary",
    "style": "structured",
    "original_tokens": 53132,
    "summary_tokens": 797,
    "reduction_factor": 66.7,
    "sections": {
        "count": 45,
        "headers": ["1. Introduction", "1.1 Background", "1.2 Motivation", ...],
        "note": "Use list_sections() for complete list"
    },
    "coverage": {
        "included": {"abstract": True, "keywords": True, "section_headers": True, "key_findings": True},
        "excluded": {"detailed_methods": True, "complete_citations": True, "code_examples": True},
        "completeness_score": 0.015
    },
    "original": {
        "path": "/absolute/path/to/paper.md",
        "filename": "paper.md",
        "size_bytes": 258432,
        "size_tokens": 53132
    },
    "confidence": {
        "completeness": 0.015,
        "recommended_for": ["initial_understanding", "overview", "triage"],
        "not_recommended_for": ["detailed_analysis", "citation", "implementation"]
    }
}
```

**Example (Full)**:
```python
{
    "content": "# Full Document\n\n...",
    "type": "full",
    "tokens": 8423,
    "path": "/absolute/path/to/small-file.md"
}
```

## Entity: Section

**Description**: Extracted markdown section content with metadata

**Purpose**: Represent a portion of document extracted by heading name for targeted reading

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | str | Yes | Section text (includes heading and content) |
| `type` | Literal["section", "error"] | Yes | Indicates success or error |
| `section` | str | Yes | Heading name that was searched for |
| `heading_level` | int | Conditional | Number of `#` symbols (1-6) (only if type="section") |
| `tokens` | int | Conditional | Token count of extracted content (only if type="section") |
| `start_line` | int | Conditional | Line number where section starts (only if type="section") |
| `end_line` | int | Conditional | Line number where section ends (only if type="section") |
| `error` | str | Conditional | Error message (only if type="error") |

**Validation Rules**:
- If `type="section"`, all Conditional fields except `error` MUST be present
- If `type="error"`, only `content`, `type`, `section`, `error` present
- `heading_level` MUST be 1-6 (markdown only supports 6 levels)
- `start_line` MUST be <= `end_line`

**State Transitions**: N/A (immutable value object)

**Example (Success)**:
```python
{
    "content": "## 3.1 Core Protocol\n\nThe STOPPER protocol consists of...",
    "type": "section",
    "section": "3.1",
    "heading_level": 2,
    "tokens": 1847,
    "start_line": 142,
    "end_line": 198
}
```

**Example (Error)**:
```python
{
    "content": "ERROR: Section 'Nonexistent' not found",
    "type": "error",
    "section": "Nonexistent",
    "error": "Section 'Nonexistent' not found in document"
}
```

## Entity: Token Count

**Description**: Integer representing number of tokens in text according to cl100k_base encoding

**Purpose**: Precise token measurement for context window management

**Type**: `int` (simple scalar, not a structured entity)

**Validation Rules**:
- MUST be non-negative integer
- Zero is valid (empty string has 0 tokens)
- No upper bound (large documents may have millions of tokens)

**Usage**:
```python
token_count = estimate_tokens("Some text")  # Returns int
```

## Relationships

```
Summary Response
├── references → Token Count (original_tokens, summary_tokens)
├── contains → Section metadata (sections.headers)
└── provides guidance → Section extraction (via _preamble, cross-references)

Section
├── references → Token Count (tokens)
└── extracted from → File content (implicit, no direct relationship)

Token Count
└── computed from → Text content (pure function, no entity relationship)
```

## Data Flow

1. **smart_read() invocation**:
   - Read file content (str)
   - Compute Token Count via `estimate_tokens(content)`
   - If tokens >10K: Generate summary via `generate_summary(content, style)`
   - If tokens >10K: Compute Token Count of summary
   - Build Summary Response with all metadata
   - Return Summary Response

2. **read_section() invocation**:
   - Read file content (str)
   - Extract section via `extract_section_content(content, heading)`
   - If found: Compute Token Count, build success Section
   - If not found: Build error Section
   - Return Section

3. **list_sections() invocation**:
   - Read file content (str)
   - Extract headers via `extract_headers(content)`
   - Return list of header strings (no entity structure)

## Storage

**N/A** - All entities are ephemeral value objects constructed on-demand. No persistence required.

**Caching**: Deferred to future optimization feature (out of scope per spec).

## Type Definitions (Python)

```python
from typing import Literal, TypedDict, List, Dict, Any

class SectionMetadata(TypedDict):
    count: int
    headers: List[str]
    note: str

class CoverageIncluded(TypedDict):
    abstract: bool
    keywords: bool
    section_headers: bool
    key_findings: bool

class CoverageExcluded(TypedDict):
    detailed_methods: bool
    complete_citations: bool
    code_examples: bool
    tables_and_figures: bool

class Coverage(TypedDict):
    included: CoverageIncluded
    excluded: CoverageExcluded
    completeness_score: float

class OriginalFileMetadata(TypedDict):
    path: str
    filename: str
    size_bytes: int
    size_tokens: int

class Confidence(TypedDict):
    completeness: float
    recommended_for: List[str]
    not_recommended_for: List[str]

class SummaryResponse(TypedDict):
    _preamble: str
    content: str
    type: Literal["summary", "full"]
    style: str  # Only if type="summary"
    original_tokens: int  # Only if type="summary"
    summary_tokens: int  # Only if type="summary"
    reduction_factor: float  # Only if type="summary"
    sections: SectionMetadata  # Only if type="summary"
    coverage: Coverage  # Only if type="summary"
    original: OriginalFileMetadata  # Only if type="summary"
    confidence: Confidence  # Only if type="summary"

class SectionResponse(TypedDict):
    content: str
    type: Literal["section", "error"]
    section: str
    heading_level: int  # Only if type="section"
    tokens: int  # Only if type="section"
    start_line: int  # Only if type="section"
    end_line: int  # Only if type="section"
    error: str  # Only if type="error"
```

**Note**: TypedDict definitions above are for documentation. Actual implementation in summarizer.py uses dicts with mypy type hints (`-> dict`). Full TypedDict classes would be added in future type refinement feature.
