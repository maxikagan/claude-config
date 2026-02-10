#!/usr/bin/env python3
"""Extract layout-preserved text from targeted PDF pages.

Used for cross-validation against table extraction. Outputs JSON
with the raw text and extracted number positions so Claude can
compare numeric values between the two extraction methods.

Usage:
    python extract_text.py <pdf_path> <page_numbers>

    page_numbers: comma-separated, e.g. "5,6,7" or "5-10"
"""

import json
import re
import sys
from pathlib import Path

import pdfplumber


def parse_page_range(spec):
    """Parse '5,6,7' or '5-10' or '5,8-12' into a sorted list of ints."""
    pages = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            pages.update(range(int(start), int(end) + 1))
        else:
            pages.add(int(part))
    return sorted(pages)


NUMBER_PATTERN = re.compile(
    r"[(\x24]?\s*(?:Ps\.?\s*)?[\x24]?\s*"
    r"[\d]{1,3}(?:[,.][\d]{3})*(?:[.,]\d{1,2})?"
    r"\s*\)?"
)


def extract_numbers(text):
    """Find all number-like strings in the text with their positions."""
    numbers = []
    for match in NUMBER_PATTERN.finditer(text):
        raw = match.group().strip()
        if not re.search(r"\d", raw):
            continue
        numbers.append({
            "raw": raw,
            "start": match.start(),
            "end": match.end(),
        })
    return numbers


def extract_page_text(pdf, page_num):
    """Extract text from a single page with layout preservation."""
    try:
        page = pdf.pages[page_num - 1]
    except IndexError:
        return {"page": page_num, "error": f"Page {page_num} does not exist (PDF has {len(pdf.pages)} pages)"}

    text = page.extract_text(layout=True) or ""
    text_simple = page.extract_text() or ""

    numbers = extract_numbers(text_simple)

    return {
        "page": page_num,
        "text_layout": text,
        "text_simple": text_simple,
        "char_count": len(text_simple),
        "numbers_found": len(numbers),
        "numbers": numbers,
    }


def main():
    if len(sys.argv) != 3:
        print("Usage: python extract_text.py <pdf_path> <page_numbers>", file=sys.stderr)
        print("  page_numbers: comma-separated (5,6,7) or ranges (5-10)", file=sys.stderr)
        sys.exit(1)

    pdf_path = sys.argv[1]
    page_spec = sys.argv[2]

    path = Path(pdf_path)
    if not path.exists():
        print(json.dumps({"error": f"File not found: {pdf_path}"}))
        sys.exit(1)

    pages = parse_page_range(page_spec)

    try:
        pdf = pdfplumber.open(str(path))
    except Exception as e:
        print(json.dumps({"error": f"Cannot open PDF: {e}"}))
        sys.exit(1)

    print(f"Extracting text from {len(pages)} pages...", file=sys.stderr)

    results = []
    for page_num in pages:
        print(f"  Page {page_num}", file=sys.stderr)
        results.append(extract_page_text(pdf, page_num))

    pdf.close()

    output = {
        "file": str(path.resolve()),
        "pages_requested": pages,
        "results": results,
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
