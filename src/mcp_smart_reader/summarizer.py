#!/usr/bin/env python3
"""
Extract keywords and generate summary from paper.md
"""

import re
from collections import Counter
from pathlib import Path


def extract_keywords_from_abstract(text):
    """Extract keywords from the Keywords line in abstract"""
    match = re.search(r'\*\*Keywords:\*\*\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if match:
        keywords_text = match.group(1)
        # Split by comma and clean up
        keywords = [k.strip() for k in keywords_text.split(',')]
        return keywords
    return []


def extract_section_headers(text):
    """Extract all section headers"""
    headers = re.findall(r'^#{1,3}\s+(.+)$', text, re.MULTILINE)
    return headers


def extract_abstract(text):
    """Extract the abstract section"""
    match = re.search(r'## Abstract\n\n(.+?)(?=\n## |\n---|\Z)', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def extract_key_points(text, num_points=10):
    """Extract key sentences that likely contain main ideas"""
    # Look for sentences with key indicator words
    key_indicators = [
        'we present', 'we propose', 'we demonstrate', 'we show',
        'our contributions', 'in this paper', 'this paper',
        'remarkably', 'importantly', 'significantly',
        'convergent evolution', 'validates', 'evidence'
    ]

    sentences = re.split(r'[.!?]\s+', text)
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


def extract_contributions(text):
    """Extract the contributions section"""
    match = re.search(
        r'### 1\.3 Our Contributions\n\n(.+?)(?=\n### |\n## |\Z)',
        text,
        re.DOTALL
    )
    if match:
        return match.group(1).strip()
    return ""


def main():
    # Read the paper
    paper_path = Path('paper.md')
    if not paper_path.exists():
        print(f"Error: {paper_path} not found")
        return

    text = paper_path.read_text(encoding='utf-8')

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
        contrib_lines = contributions.split('\n')
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
    summary_text = '\n'.join(summary)
    output_path = Path('paper_summary.txt')
    output_path.write_text(summary_text, encoding='utf-8')

    print(f"✅ Summary written to: {output_path.absolute()}")
    print(f"📄 Paper size: {len(text):,} characters")
    print(f"🔑 Keywords extracted: {len(keywords)}")
    print(f"📋 Sections identified: {len(headers)}")
    print(f"💡 Key points extracted: {len(key_points)}")

    # Also print to stdout
    print("\n" + summary_text)


if __name__ == '__main__':
    main()
