#!/usr/bin/env python3
"""
MCP Smart Reader Server

Intelligent document reader with automatic summarization for large files.
Provides token-efficient access to documents by returning summaries with
rich metadata, section extraction, and actionable cross-references.
"""

from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from .summarizer import (
    estimate_tokens,
    extract_abstract,
    extract_headers,
    extract_keywords_from_abstract,
    extract_key_points,
    generate_summary,
)

# Configuration
TOKEN_THRESHOLD = 10000  # Auto-summarize files larger than this
DEFAULT_SUMMARY_STYLE = "structured"

# Initialize MCP server
mcp = FastMCP("Smart Document Reader")


def format_preamble(
    original_tokens: int, summary_tokens: int, file_path: str
) -> str:
    """Format the warning preamble for summary responses."""
    reduction = original_tokens / summary_tokens if summary_tokens > 0 else 0

    return f"""⚠️  DOCUMENT SUMMARY (NOT FULL CONTENT)
Original: {original_tokens:,} tokens → Summary: {summary_tokens:,} tokens
Reduction: {reduction:.1f}x

This summary may omit:
  • Detailed arguments and nuances
  • Specific examples, data, equations
  • Citations and references
  • Methodological details
  • Code examples

TO GET MORE DETAIL:
  • read_section('{file_path}', 'section_name')  - Read specific section
  • list_sections('{file_path}')  - See all sections
  • smart_read('{file_path}', mode='full')  - Get complete content

WHEN TO REQUEST MORE:
  → If task requires detailed arguments: Request specific sections
  → If task requires citations: Request full content or bibliography section
  → If task requires implementation details: Request methods/code sections
  → If overview is sufficient: Use this summary
"""


@mcp.tool()
def smart_read(
    file_path: str, mode: str = "auto", summary_style: str = DEFAULT_SUMMARY_STYLE
) -> dict:
    """
    Smart file reader with automatic summarization for large files.

    Args:
        file_path: Path to file to read
        mode: Reading mode
            - "auto": Summarize if >10K tokens (default)
            - "summary": Always return summary
            - "full": Never summarize, return full content
        summary_style: Summary generation style (default: "structured")
            - "structured": Extract keywords, headers, key points
            - "extractive": Key sentences only
            - "abstract": Just abstract section if available

    Returns:
        Dictionary with content and rich metadata:
        - content: Summary or full text
        - type: "summary" or "full"
        - original_tokens: Token count of original file
        - summary_tokens: Token count of summary (if summarized)
        - sections: Section headers and count
        - coverage: What's included/excluded
        - suggestions: When to request more detail
        - confidence: Completeness and recommended usage

    Example:
        >>> result = smart_read("paper.md")
        >>> print(result["content"])  # Summary if >10K tokens
        >>> print(result["suggestions"])  # When to drill down
    """
    path = Path(file_path)

    if not path.exists():
        return {"error": f"File not found: {file_path}", "type": "error"}

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"Error reading file: {str(e)}", "type": "error"}

    token_count = estimate_tokens(content)

    # Decide whether to summarize
    should_summarize = mode == "summary" or (
        mode == "auto" and token_count > TOKEN_THRESHOLD
    )

    if should_summarize:
        summary = generate_summary(content, style=summary_style)
        summary_tokens = estimate_tokens(summary)
        sections = extract_headers(content)

        return {
            "_preamble": format_preamble(token_count, summary_tokens, file_path),
            "content": summary,
            "type": "summary",
            "style": summary_style,
            "original_tokens": token_count,
            "summary_tokens": summary_tokens,
            "reduction_factor": round(token_count / summary_tokens, 1)
            if summary_tokens > 0
            else 0,
            "sections": {
                "count": len(sections),
                "headers": sections[:20],
                "note": "Use list_sections() for complete list",
            },
            "coverage": {
                "included": {
                    "abstract": bool(extract_abstract(content)),
                    "keywords": bool(extract_keywords_from_abstract(content)),
                    "section_headers": bool(sections),
                    "key_findings": True,
                },
                "excluded": {
                    "detailed_methods": True,
                    "complete_citations": True,
                    "code_examples": True,
                    "tables_and_figures": True,
                },
                "completeness_score": summary_tokens / token_count
                if token_count > 0
                else 0,
            },
            "original": {
                "path": str(path.absolute()),
                "filename": path.name,
                "size_bytes": len(content),
                "size_tokens": token_count,
            },
            "confidence": {
                "completeness": summary_tokens / token_count
                if token_count > 0
                else 0,
                "recommended_for": [
                    "initial_understanding",
                    "overview",
                    "triage",
                ],
                "not_recommended_for": [
                    "detailed_analysis",
                    "citation",
                    "implementation",
                ],
            },
        }

    # Return full content
    return {
        "content": content,
        "type": "full",
        "tokens": token_count,
        "path": str(path.absolute()),
    }


@mcp.tool()
def read_section(file_path: str, section_heading: str) -> dict:
    """
    Extract specific section from document without loading entire file into context.

    Args:
        file_path: Path to file
        section_heading: Heading to search for (e.g., "3.1", "Methods", "Introduction")

    Returns:
        Dictionary with section content and metadata

    Example:
        >>> result = read_section("paper.md", "3.1 Core Protocol")
        >>> print(result["content"])  # Just section 3.1
    """
    path = Path(file_path)

    if not path.exists():
        return {"error": f"File not found: {file_path}", "type": "error"}

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"Error reading file: {str(e)}", "type": "error"}

    # TODO: Implement section extraction logic
    # For now, return placeholder
    return {
        "content": f"Section '{section_heading}' extraction not yet implemented",
        "type": "section",
        "section": section_heading,
        "note": "This feature will be implemented via speckit workflow",
    }


@mcp.tool()
def list_sections(file_path: str) -> dict:
    """
    Get table of contents for document.

    Args:
        file_path: Path to file

    Returns:
        Dictionary with list of section headings

    Example:
        >>> result = list_sections("paper.md")
        >>> for header in result["sections"]:
        ...     print(header)
    """
    path = Path(file_path)

    if not path.exists():
        return {"error": f"File not found: {file_path}", "type": "error"}

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"Error reading file: {str(e)}", "type": "error"}

    headers = extract_headers(content)

    return {
        "sections": headers,
        "count": len(headers),
        "type": "toc",
        "path": str(path.absolute()),
        "note": "Use read_section(file_path, heading) to read specific section",
    }


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
