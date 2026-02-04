#!/usr/bin/env python3
"""Lightweight PDF page mapper for financial documents.

Reads every page and outputs a compact JSON page map to stdout.
Designed to produce ~30KB for a 150-page document — small enough
for Claude's context window to reason about which pages to target.

Usage:
    python scan_pdf.py <pdf_path>
"""

import json
import sys
import re
from pathlib import Path

import pdfplumber

FINANCIAL_KEYWORDS = {
    "en": [
        "revenue", "income", "ebitda", "noi", "net operating income",
        "balance sheet", "cash flow", "total assets", "total liabilities",
        "equity", "earnings", "depreciation", "amortization", "capex",
        "capital expenditure", "operating expenses", "gross profit",
        "net income", "dividends", "distributions", "occupancy",
        "rental income", "interest expense", "debt", "leverage",
        "loan to value", "ltv", "ffo", "affo", "funds from operations",
        "fair value", "investment properties", "gla", "sqm", "sq ft",
    ],
    "es": [
        "ingresos", "estado de resultados", "estado de posición financiera",
        "balance general", "flujo de efectivo", "utilidad neta",
        "utilidad de operación", "activos totales", "pasivos totales",
        "capital contable", "depreciación", "amortización",
        "gastos de operación", "ingreso por rentas", "gasto por intereses",
        "deuda", "propiedades de inversión", "ocupación",
        "resultado integral", "distribuciones", "certificados",
        "cbfis", "fibra", "fideicomiso", "arrendamiento",
        "millones de pesos", "miles de pesos",
    ],
}

ALL_KEYWORDS = FINANCIAL_KEYWORDS["en"] + FINANCIAL_KEYWORDS["es"]
KEYWORD_PATTERNS = [re.compile(re.escape(kw), re.IGNORECASE) for kw in ALL_KEYWORDS]


def scan_page(page):
    """Extract metadata from a single page."""
    text = page.extract_text() or ""
    text_lower = text.lower()

    tables = page.find_tables(
        table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"}
    )
    tables_text = page.find_tables(
        table_settings={"vertical_strategy": "text", "horizontal_strategy": "text"}
    )

    table_count = max(len(tables), len(tables_text))

    matched_keywords = []
    for kw, pattern in zip(ALL_KEYWORDS, KEYWORD_PATTERNS):
        if pattern.search(text_lower):
            matched_keywords.append(kw)

    preview_lines = [l.strip() for l in text.split("\n") if l.strip()][:5]
    preview = " | ".join(preview_lines)
    if len(preview) > 300:
        preview = preview[:300] + "..."

    has_numbers = bool(re.search(r"[\d,]+\.?\d*", text))

    return {
        "page": page.page_number,
        "tables": table_count,
        "chars": len(text),
        "has_numbers": has_numbers,
        "financial_keywords": matched_keywords,
        "preview": preview,
    }


def scan_pdf(pdf_path):
    """Scan all pages and return structured metadata."""
    path = Path(pdf_path)
    if not path.exists():
        print(json.dumps({"error": f"File not found: {pdf_path}"}))
        sys.exit(1)

    try:
        pdf = pdfplumber.open(str(path))
    except Exception as e:
        if "password" in str(e).lower() or "encrypted" in str(e).lower():
            print(json.dumps({"error": "PDF is password-protected. Provide the password or use an unlocked copy."}))
        else:
            print(json.dumps({"error": f"Cannot open PDF: {e}"}))
        sys.exit(1)

    total_pages = len(pdf.pages)
    print(f"Scanning {total_pages} pages...", file=sys.stderr)

    pages = []
    financial_pages = []

    for i, page in enumerate(pdf.pages):
        if (i + 1) % 10 == 0 or i == 0:
            print(f"  Page {i + 1}/{total_pages}", file=sys.stderr)

        info = scan_page(page)
        pages.append(info)

        if info["tables"] > 0 or info["financial_keywords"]:
            financial_pages.append(info["page"])

    pdf.close()

    result = {
        "file": str(path.resolve()),
        "total_pages": total_pages,
        "financial_pages": financial_pages,
        "financial_page_count": len(financial_pages),
        "pages": pages,
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scan_pdf.py <pdf_path>", file=sys.stderr)
        sys.exit(1)
    scan_pdf(sys.argv[1])
