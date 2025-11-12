#!/usr/bin/env python3
"""
Extract keywords and generate summary from paper.md
"""

import re
from pathlib import Path

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


def extract_keywords_from_abstract(text: str) -> list[str]:
    """Extract keywords from the Keywords line in abstract"""
    match = re.search(r"\*\*Keywords:\*\*\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
    if match:
        keywords_text = match.group(1)
        # Split by comma and clean up
        keywords = [k.strip() for k in keywords_text.split(",")]
        return keywords
    return []


def extract_section_headers(text: str) -> list[str]:
    """Extract all section headers"""
    headers = re.findall(r"^#{1,3}\s+(.+)$", text, re.MULTILINE)
    return headers


# Alias for imports in server.py
extract_headers = extract_section_headers


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
        headers = extract_section_headers(content)
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


def extract_abstract(text: str) -> str:
    """Extract the abstract section"""
    match = re.search(r"## Abstract\n\n(.+?)(?=\n## |\n---|\Z)", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def extract_key_points(text: str, num_points: int = 10) -> list[str]:
    """Extract key sentences that likely contain main ideas"""
    # Look for sentences with key indicator words
    key_indicators = [
        "we present",
        "we propose",
        "we demonstrate",
        "we show",
        "our contributions",
        "in this paper",
        "this paper",
        "remarkably",
        "importantly",
        "significantly",
        "convergent evolution",
        "validates",
        "evidence",
    ]

    sentences = re.split(r"[.!?]\s+", text)
    scored_sentences = []

    for sentence in sentences:
        score = 0
        sentence_lower = sentence.lower()

        # Score based on key indicators
        for indicator in key_indicators:
            if indicator in sentence_lower:
                score += 2

        # Boost score for sentences in intro/abstract
        if len(sentence) > 50 and len(sentence) < 300:  # Reasonable length
            score += 1

        if score > 0:
            scored_sentences.append((score, sentence.strip()))

    # Sort by score and return top N
    scored_sentences.sort(reverse=True, key=lambda x: x[0])
    return [sent for score, sent in scored_sentences[:num_points]]


def extract_section_content(
    text: str, heading: str
) -> tuple[str | None, int | None, int | None, int | None]:
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
    heading_pattern = r"^(#{1,6})\s+(.+?)$"
    headings = [
        (m.start(), m.group(1), m.group(2))
        for m in re.finditer(heading_pattern, text, re.MULTILINE)
    ]

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
    start_line = text[:start_pos].count("\n") + 1
    end_line = text[:end_pos].count("\n") + 1

    return (content, target_level, start_line, end_line)


def extract_contributions(text: str) -> str:
    """Extract the contributions section"""
    match = re.search(r"### 1\.3 Our Contributions\n\n(.+?)(?=\n### |\n## |\Z)", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def main() -> None:
    # Read the paper
    paper_path = Path("paper.md")
    if not paper_path.exists():
        print(f"Error: {paper_path} not found")
        return

    text = paper_path.read_text(encoding="utf-8")

    # Extract keywords
    keywords = extract_keywords_from_abstract(text)

    # Extract abstract
    abstract = extract_abstract(text)

    # Extract section headers
    headers = extract_section_headers(text)

    # Extract contributions
    contributions = extract_contributions(text)

    # Extract key points
    key_points = extract_key_points(text, num_points=8)

    # Generate summary
    summary = []
    summary.append("=" * 80)
    summary.append("PAPER SUMMARY: STOPPER - Executive Function Protocol for AI Assistants")
    summary.append("=" * 80)
    summary.append("")

    # Keywords
    summary.append("KEYWORDS:")
    for keyword in keywords:
        summary.append(f"  • {keyword}")
    summary.append("")

    # Abstract (first 500 chars)
    summary.append("ABSTRACT (excerpt):")
    summary.append(abstract[:500] + "...")
    summary.append("")

    # Main sections
    summary.append("MAIN SECTIONS:")
    for i, header in enumerate(headers[:15], 1):  # First 15 headers
        summary.append(f"  {i}. {header}")
    summary.append("")

    # Contributions
    if contributions:
        summary.append("KEY CONTRIBUTIONS:")
        # Extract bullet points from contributions
        contrib_lines = contributions.split("\n")
        for line in contrib_lines[:10]:  # First 10 lines
            if line.strip():
                summary.append(f"  {line.strip()}")
    summary.append("")

    # Key points
    summary.append("KEY FINDINGS:")
    for i, point in enumerate(key_points, 1):
        summary.append(f"  {i}. {point[:200]}...")
    summary.append("")

    summary.append("=" * 80)
    summary.append(f"Full paper: {paper_path.absolute()}")
    summary.append(f"Paper size: {len(text):,} characters, {len(text.split()):,} words")
    summary.append("=" * 80)

    # Write to file
    summary_text = "\n".join(summary)
    output_path = Path("paper_summary.txt")
    output_path.write_text(summary_text, encoding="utf-8")

    print(f"✅ Summary written to: {output_path.absolute()}")
    print(f"📄 Paper size: {len(text):,} characters")
    print(f"🔑 Keywords extracted: {len(keywords)}")
    print(f"📋 Sections identified: {len(headers)}")
    print(f"💡 Key points extracted: {len(key_points)}")

    # Also print to stdout
    print("\n" + summary_text)


if __name__ == "__main__":
    main()
