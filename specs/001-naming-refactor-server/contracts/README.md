# API Contracts

**Feature**: 001-naming-refactor-server
**Protocol**: MCP (Model Context Protocol) via stdio

## Overview

This feature implements MCP tools (not HTTP REST APIs). MCP uses JSON-RPC 2.0 over stdio for communication between MCP client and server. No OpenAPI/REST contracts apply.

## MCP Tools Contracts

### Tool: `smart_read`

**Description**: Smart file reader with automatic summarization for large files

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "Path to file to read"
    },
    "mode": {
      "type": "string",
      "enum": ["auto", "summary", "full"],
      "default": "auto",
      "description": "Reading mode: auto (summarize if >10K tokens), summary (always summarize), full (never summarize)"
    },
    "summary_style": {
      "type": "string",
      "default": "structured",
      "description": "Summary generation style (default: structured)"
    }
  },
  "required": ["file_path"]
}
```

**Output Schema** (type="summary"):
```json
{
  "type": "object",
  "properties": {
    "_preamble": {"type": "string"},
    "content": {"type": "string"},
    "type": {"type": "string", "enum": ["summary"]},
    "style": {"type": "string"},
    "original_tokens": {"type": "integer"},
    "summary_tokens": {"type": "integer"},
    "reduction_factor": {"type": "number"},
    "sections": {
      "type": "object",
      "properties": {
        "count": {"type": "integer"},
        "headers": {"type": "array", "items": {"type": "string"}},
        "note": {"type": "string"}
      }
    },
    "coverage": {
      "type": "object",
      "properties": {
        "included": {"type": "object"},
        "excluded": {"type": "object"},
        "completeness_score": {"type": "number"}
      }
    },
    "original": {
      "type": "object",
      "properties": {
        "path": {"type": "string"},
        "filename": {"type": "string"},
        "size_bytes": {"type": "integer"},
        "size_tokens": {"type": "integer"}
      }
    },
    "confidence": {
      "type": "object",
      "properties": {
        "completeness": {"type": "number"},
        "recommended_for": {"type": "array", "items": {"type": "string"}},
        "not_recommended_for": {"type": "array", "items": {"type": "string"}}
      }
    }
  },
  "required": ["_preamble", "content", "type"]
}
```

**Output Schema** (type="full"):
```json
{
  "type": "object",
  "properties": {
    "content": {"type": "string"},
    "type": {"type": "string", "enum": ["full"]},
    "tokens": {"type": "integer"},
    "path": {"type": "string"}
  },
  "required": ["content", "type", "tokens", "path"]
}
```

**Error Schema**:
```json
{
  "type": "object",
  "properties": {
    "error": {"type": "string"},
    "type": {"type": "string", "enum": ["error"]}
  },
  "required": ["error", "type"]
}
```

---

### Tool: `read_section`

**Description**: Extract specific section from document without loading entire file into context

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "Path to file"
    },
    "section_heading": {
      "type": "string",
      "description": "Heading to search for (e.g., '3.1', 'Methods', 'Introduction')"
    }
  },
  "required": ["file_path", "section_heading"]
}
```

**Output Schema** (success):
```json
{
  "type": "object",
  "properties": {
    "content": {"type": "string"},
    "type": {"type": "string", "enum": ["section"]},
    "section": {"type": "string"},
    "heading_level": {"type": "integer", "minimum": 1, "maximum": 6},
    "tokens": {"type": "integer"},
    "start_line": {"type": "integer"},
    "end_line": {"type": "integer"}
  },
  "required": ["content", "type", "section"]
}
```

**Output Schema** (error):
```json
{
  "type": "object",
  "properties": {
    "content": {"type": "string"},
    "type": {"type": "string", "enum": ["error"]},
    "section": {"type": "string"},
    "error": {"type": "string"}
  },
  "required": ["content", "type", "section", "error"]
}
```

---

### Tool: `list_sections`

**Description**: Get table of contents for document

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "Path to file"
    }
  },
  "required": ["file_path"]
}
```

**Output Schema** (success):
```json
{
  "type": "object",
  "properties": {
    "sections": {
      "type": "array",
      "items": {"type": "string"}
    },
    "count": {"type": "integer"},
    "type": {"type": "string", "enum": ["toc"]},
    "path": {"type": "string"},
    "note": {"type": "string"}
  },
  "required": ["sections", "count", "type", "path"]
}
```

**Error Schema**:
```json
{
  "type": "object",
  "properties": {
    "error": {"type": "string"},
    "type": {"type": "string", "enum": ["error"]}
  },
  "required": ["error", "type"]
}
```

## MCP Protocol Details

**Transport**: stdio (standard input/output)
**Format**: JSON-RPC 2.0
**Server Implementation**: FastMCP framework

**Tool Registration**: All three tools registered automatically via FastMCP's `@mcp.tool()` decorator

**Error Handling**: Errors returned as dict with `"error"` key and `"type": "error"`

**File Access**: Tools read files from local filesystem (paths must be absolute or relative to working directory)

## Testing Contracts

**Unit Tests**: Not in scope for this feature (deferred)

**Integration Tests**: Not in scope for this feature (deferred)

**Manual Testing**:
1. Install package: `pip install -e .`
2. Run server: `mcp-smart-reader`
3. Connect MCP client to stdio server
4. Call tools with test inputs
5. Verify outputs match schemas above

## Notes

- No HTTP endpoints - pure MCP protocol
- No authentication/authorization - local trusted environment
- No rate limiting - single-user local usage
- No versioning - tools evolve with package version
