# MCP Smart Reader

Smart document reader MCP server with automatic summarization for large files.

## Overview

MCP Smart Reader provides token-efficient access to large documents by automatically summarizing files that exceed a token threshold. Instead of loading a 50K token document into Claude's context every message, it returns an 800 token summary with rich metadata, dramatically improving context window efficiency.

## Key Features

- **Automatic Summarization**: Files >10K tokens are automatically summarized
- **Rich Metadata**: Summaries include coverage info, suggestions, and cross-references
- **Section Extraction**: Read specific sections without loading entire document
- **Token Tracking**: Know exactly how many tokens you're saving
- **Actionable Guidance**: Claude knows when to request more detail

## Token Savings Example

```
Without smart_read:
  paper.md: 53,132 tokens every message
  3 exchanges: 159,396 tokens consumed

With smart_read:
  Summary: 797 tokens
  3 exchanges: 2,391 tokens consumed
  Savings: 157,005 tokens (98.5% reduction)
```

## Installation

```bash
# Clone repository
cd mcp-smart-reader

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

## Development Status

**Current**: Basic structure in place, ready for speckit workflow

**Next Steps** (via speckit):
1. Implement section extraction logic
2. Add multi-format support (PDF, DOCX)
3. Enhance summarization algorithms
4. Add caching layer
5. Comprehensive testing

## License

Apache 2.0

## Author

Scot Campbell  
Prefrontal Systems LLC  
scot@prefrontal.systems
