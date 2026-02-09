#!/usr/bin/env python3
"""Batch financial table extractor for FIBRA Soma quarterly reports.

Scans a directory of PDF reports, auto-identifies financial statement pages
in each one, extracts tables, and classifies them by statement type.

Usage:
    python batch_extract.py <pdf_directory> [--output-dir <dir>]

    If --output-dir is not given, each PDF's tables land in <pdf_stem>_tables/
    next to the source PDF.

Output per PDF:
    <output>/<period>_tables/
        income_statement_<period>.csv
        balance_sheet_<period>.csv
        cash_flow_<period>.csv
        noi_ebitda_<period>.csv
        ffo_affo_<period>.csv
        key_indicators_<period>.csv
        credit_profile_<period>.csv
        _metadata.json
"""

import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

STATEMENT_PATTERNS = [
    ("income_statement", [
        re.compile(r"income\s+statement", re.I),
        re.compile(r"estado\s+de\s+resultados", re.I),
        re.compile(r"consolidated\s+statements?\s+of\s+(?:comprehensive\s+)?income", re.I),
        re.compile(r"rental\s*income.*operating\s*expenses.*net\s*income", re.I),
    ]),
    ("balance_sheet", [
        re.compile(r"balance\s+sheet", re.I),
        re.compile(r"estado\s+de\s+posici[oó]n\s+financiera", re.I),
        re.compile(r"financial\s+position", re.I),
        re.compile(r"(?:total\s+)?assets.*(?:total\s+)?liabilities", re.I),
        re.compile(r"investment\s+properties.*total\s+assets", re.I),
    ]),
    ("cash_flow", [
        re.compile(r"cash\s+flow", re.I),
        re.compile(r"flujo\s+de\s+efectivo", re.I),
        re.compile(r"operating\s+activities.*investing\s+activities", re.I),
    ]),
    ("noi_ebitda", [
        re.compile(r"\bNOI\b.*\bEBITDA\b", re.I),
        re.compile(r"\bEBITDA\b.*\bNOI\b", re.I),
        re.compile(r"net\s+operating\s+income.*ebitda", re.I),
        re.compile(r"\bNOI\b\s+(?:margin|breakdown)", re.I),
    ]),
    ("ffo_affo", [
        re.compile(r"\bFFO\b.*\bAFFO\b", re.I),
        re.compile(r"\bAFFO\b.*\bFFO\b", re.I),
        re.compile(r"funds\s+from\s+operations", re.I),
        re.compile(r"adjusted\s+funds\s+from\s+operations", re.I),
    ]),
    ("key_indicators", [
        re.compile(r"key\s+(?:financial\s+)?indicators", re.I),
        re.compile(r"key\s+quarterly", re.I),
        re.compile(r"indicadores\s+clave", re.I),
        re.compile(r"quarterly\s+(?:financial\s+)?highlights", re.I),
    ]),
    ("credit_profile", [
        re.compile(r"credit\s+profile", re.I),
        re.compile(r"perfil\s+(?:de\s+)?cr[eé]dito", re.I),
        re.compile(r"debt\s+(?:maturity|profile|structure)", re.I),
        re.compile(r"loan[- ]to[- ]value.*leverage", re.I),
        re.compile(r"\bLTV\b.*\bdebt\b", re.I),
    ]),
]


def derive_period(filename):
    """Extract period label from filename like '3Q25.pdf' → '3Q25'."""
    stem = Path(filename).stem
    match = re.match(r"(\d[Qq]\d{2})", stem)
    if match:
        return match.group(1).upper()
    return stem


def classify_table(csv_path):
    """Read a CSV's first 15 rows and classify by statement type.

    Returns (statement_type, confidence) or (None, 0).
    """
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = []
            for i, row in enumerate(reader):
                if i >= 15:
                    break
                rows.append(row)
    except Exception:
        return None, 0

    if not rows:
        return None, 0

    text_block = " ".join(
        " ".join(cell for cell in row if cell.strip())
        for row in rows
    )

    best_type = None
    best_score = 0

    for stmt_type, patterns in STATEMENT_PATTERNS:
        score = sum(1 for p in patterns if p.search(text_block))
        if score > best_score:
            best_score = score
            best_type = stmt_type

    return best_type, best_score


def classify_from_scan(page_info):
    """Classify a page's statement type from scan metadata (keywords + preview)."""
    text = " ".join(page_info.get("financial_keywords", []))
    text += " " + page_info.get("preview", "")

    best_type = None
    best_score = 0

    for stmt_type, patterns in STATEMENT_PATTERNS:
        score = sum(1 for p in patterns if p.search(text))
        if score > best_score:
            best_score = score
            best_type = stmt_type

    return best_type, best_score


def run_scan(pdf_path):
    """Run scan_pdf.py and return parsed JSON."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "scan_pdf.py"), str(pdf_path)],
        capture_output=True, timeout=300, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        print(f"  ERROR scanning {pdf_path}: {result.stderr}", file=sys.stderr)
        return None

    stdout = result.stdout or ""
    try:
        return json.loads(stdout)
    except (json.JSONDecodeError, TypeError):
        print(f"  ERROR parsing scan output for {pdf_path}", file=sys.stderr)
        return None


def select_financial_pages(scan_data, max_pages=15):
    """Pick the best pages for extraction from scan results.

    Only selects pages that have BOTH tables AND multiple financial keywords.
    Caps at max_pages to avoid extracting chart/property pages.
    """
    pages = scan_data.get("pages", [])
    scored = []

    for p in pages:
        kw_count = len(p.get("financial_keywords", []))
        table_count = p.get("tables", 0)

        if table_count > 0 and kw_count >= 2:
            score = kw_count * 2 + table_count
            scored.append((p["page"], score, p))

    scored.sort(key=lambda x: -x[1])

    # Take top pages by score, capped at max_pages
    selected = [s[0] for s in scored[:max_pages]]

    if not selected:
        # Relax: accept pages with at least 1 keyword + tables
        fallback = [
            (p["page"], len(p.get("financial_keywords", [])))
            for p in pages
            if p.get("tables", 0) > 0 and len(p.get("financial_keywords", [])) >= 1
        ]
        fallback.sort(key=lambda x: -x[1])
        selected = [s[0] for s in fallback[:max_pages]]

    return selected


def run_extraction(pdf_path, output_dir, page_numbers):
    """Run extract_tables.py on given pages."""
    page_spec = ",".join(str(p) for p in page_numbers)
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "extract_tables.py"),
            str(pdf_path),
            str(output_dir),
            page_spec,
        ],
        capture_output=True, timeout=600, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        print(f"  ERROR extracting {pdf_path}: {result.stderr}", file=sys.stderr)
        return None

    stdout = result.stdout or ""
    try:
        return json.loads(stdout)
    except (json.JSONDecodeError, TypeError, ValueError):
        print(f"  WARNING: no JSON output from extraction of {pdf_path}", file=sys.stderr)
        return None


def rename_tables(output_dir, period, scan_data):
    """Classify and rename extracted CSVs from page_N_table_M.csv to statement_type_period.csv.

    Returns a dict mapping statement_type → csv_path.
    """
    csv_files = sorted(output_dir.glob("page_*_table_*.csv"))
    if not csv_files:
        return {}

    # Build page→scan_info lookup
    page_lookup = {}
    if scan_data:
        for p in scan_data.get("pages", []):
            page_lookup[p["page"]] = p

    classified = {}
    used_names = set()

    def safe_rename(src, dst):
        """Rename that works on Windows (overwrites if exists)."""
        if dst.exists():
            dst.unlink()
        src.rename(dst)

    def unique_name(base, period):
        """Generate a unique filename, appending _2, _3, etc. if needed."""
        name = f"{base}_{period}.csv"
        if name not in used_names:
            used_names.add(name)
            return name, base
        counter = 2
        while True:
            name = f"{base}_{counter}_{period}.csv"
            key = f"{base}_{counter}"
            if name not in used_names:
                used_names.add(name)
                return name, key
            counter += 1

    for csv_path in csv_files:
        stmt_type, score = classify_table(csv_path)

        if score < 1:
            match = re.match(r"page_(\d+)_", csv_path.name)
            if match:
                page_num = int(match.group(1))
                page_info = page_lookup.get(page_num, {})
                scan_type, scan_score = classify_from_scan(page_info)
                if scan_score > score:
                    stmt_type = scan_type
                    score = scan_score

        if stmt_type:
            new_name, key = unique_name(stmt_type, period)
        else:
            match = re.match(r"(page_\d+_table_\d+)", csv_path.name)
            base = match.group(1) if match else csv_path.stem
            new_name, key = unique_name(base, period)

        new_path = output_dir / new_name
        safe_rename(csv_path, new_path)
        classified[key] = new_path

    return classified


def process_pdf(pdf_path, output_base=None):
    """Full pipeline for a single PDF: scan → select pages → extract → classify."""
    period = derive_period(pdf_path.name)

    if output_base:
        output_dir = Path(output_base) / f"{period}_tables"
    else:
        output_dir = pdf_path.parent / f"{period}_tables"

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"Processing: {pdf_path.name} (period: {period})", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    # Phase 1: Scan
    print(f"  Scanning...", file=sys.stderr)
    scan_data = run_scan(pdf_path)
    if not scan_data:
        return {"period": period, "status": "scan_failed", "tables": {}}

    # Phase 2: Select pages
    pages = select_financial_pages(scan_data)
    if not pages:
        print(f"  No financial pages found in {pdf_path.name}", file=sys.stderr)
        return {"period": period, "status": "no_financial_pages", "tables": {}}

    print(f"  Selected {len(pages)} pages: {pages}", file=sys.stderr)

    # Phase 3: Extract
    print(f"  Extracting tables...", file=sys.stderr)
    meta = run_extraction(pdf_path, output_dir, pages)

    # Phase 4: Classify and rename
    print(f"  Classifying tables...", file=sys.stderr)
    classified = rename_tables(output_dir, period, scan_data)

    table_summary = {k: str(v) for k, v in classified.items()}
    print(f"  Found: {', '.join(table_summary.keys()) or 'none'}", file=sys.stderr)

    return {
        "period": period,
        "status": "ok",
        "pages_extracted": pages,
        "tables": table_summary,
        "extraction_metadata": meta,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Batch extract financial tables from FIBRA reports")
    parser.add_argument("pdf_directory", help="Directory containing PDF reports")
    parser.add_argument("--output-dir", help="Override output directory (default: next to each PDF)")
    args = parser.parse_args()

    pdf_dir = Path(args.pdf_directory)
    if not pdf_dir.is_dir():
        print(f"Error: {pdf_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    pdfs = sorted(pdf_dir.glob("*.pdf"), key=lambda p: p.name)
    if not pdfs:
        print(f"Error: No PDF files found in {pdf_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(pdfs)} PDF reports to process", file=sys.stderr)

    results = []
    for pdf_path in pdfs:
        result = process_pdf(pdf_path, args.output_dir)
        results.append(result)

    # Summary
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"BATCH EXTRACTION COMPLETE", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    ok_count = sum(1 for r in results if r["status"] == "ok")
    fail_count = len(results) - ok_count
    print(f"  Processed: {len(results)} PDFs", file=sys.stderr)
    print(f"  Successful: {ok_count}", file=sys.stderr)
    if fail_count:
        print(f"  Failed: {fail_count}", file=sys.stderr)

    # Statement type coverage
    all_types = set()
    for r in results:
        all_types.update(r["tables"].keys())

    print(f"\n  Statement types found across all reports:", file=sys.stderr)
    for stmt_type in sorted(all_types):
        periods = [r["period"] for r in results if stmt_type in r["tables"]]
        print(f"    {stmt_type}: {len(periods)} quarters", file=sys.stderr)

    # Write summary JSON to stdout
    summary = {
        "total_pdfs": len(results),
        "successful": ok_count,
        "failed": fail_count,
        "results": results,
    }
    sys.stdout.buffer.write(json.dumps(summary, indent=2, ensure_ascii=False).encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
