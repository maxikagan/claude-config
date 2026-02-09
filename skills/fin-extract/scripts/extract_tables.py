#!/usr/bin/env python3
"""Precision financial table extractor — outputs CSV with numbers as strings.

Extracts tables from targeted PDF pages using pdfplumber. Tries multiple
table detection strategies and picks the best result. Numbers are NEVER
converted to float — they stay as strings throughout, with Decimal used
only for validation of row totals.

Usage:
    python extract_tables.py <pdf_path> <output_dir> <page_numbers>

    page_numbers: comma-separated (5,6,7) or ranges (5-10)

Output:
    <output_dir>/page_<N>_table_<M>.csv   — one CSV per detected table
    <output_dir>/_metadata.json            — extraction metadata and validation results
"""

import csv
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pdfplumber

def extract_table_with_words(page, table):
    """Extract table data using page-level word detection for proper spacing.

    Instead of table.extract() which concatenates text within cells,
    this uses page.extract_words() to get properly-spaced words, then
    assigns them to cells based on spatial overlap.
    """
    words = page.extract_words(x_tolerance=2, y_tolerance=3, keep_blank_chars=True)
    cells = table.cells
    if not cells:
        return table.extract(x_tolerance=15)

    rows_dict = {}
    for cell in cells:
        x0, top, x1, bottom = cell
        row_key = round(top, 0)
        if row_key not in rows_dict:
            rows_dict[row_key] = {}

    row_keys = sorted(rows_dict.keys())
    col_positions = sorted(set(round(c[0], 0) for c in cells))

    grid = {}
    for cell in cells:
        x0, top, x1, bottom = cell
        row_key = min(row_keys, key=lambda r: abs(r - round(top, 0)))
        col_key = min(col_positions, key=lambda c: abs(c - round(x0, 0)))
        grid[(row_key, col_key)] = (x0, top, x1, bottom)

    cell_texts = {}
    for word in words:
        wx_center = (word["x0"] + word["x1"]) / 2
        wy_center = (word["top"] + word["bottom"]) / 2

        best_cell = None
        best_area = 0
        for cell_key, (cx0, ctop, cx1, cbottom) in grid.items():
            if cx0 - 2 <= wx_center <= cx1 + 2 and ctop - 2 <= wy_center <= cbottom + 2:
                area = (cx1 - cx0) * (cbottom - ctop)
                if best_cell is None or area < best_area:
                    best_cell = cell_key
                    best_area = area

        if best_cell is not None:
            if best_cell not in cell_texts:
                cell_texts[best_cell] = []
            cell_texts[best_cell].append((word["x0"], word["top"], word["text"]))

    result = []
    for row_key in row_keys:
        row_cells = []
        for col_key in col_positions:
            key = (row_key, col_key)
            if key in cell_texts:
                sorted_words = sorted(cell_texts[key], key=lambda w: (w[1], w[0]))
                text = " ".join(w[2] for w in sorted_words)
                row_cells.append(text.strip())
            else:
                row_cells.append(None)
        result.append(row_cells)

    return result


CURRENCY_PREFIX = re.compile(r"^\s*(?:Ps\.?\s*|MXN\s*|USD\s*|US[$]\s*|[$]\s*)")
PARENTHETICAL_NEG = re.compile(r"^\s*\(\s*([\d,.\s]+)\s*\)\s*$")
FOOTNOTE_PATTERN = re.compile(r"^\s*(?:\d{1,2}\s*[\)\.]|[*†‡§¹²³⁴⁵]|\(\d\))\s*")
EN_NUMBER = re.compile(r"^-?\s*[\d]{1,3}(?:,\d{3})*(?:\.\d+)?$")
ES_NUMBER = re.compile(r"^-?\s*[\d]{1,3}(?:\.\d{3})*(?:,\d+)?$")
FINANCIAL_CELL = re.compile(
    r"^[\s($]*\d[\d,.\s]*[)%]?$"
)


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


def detect_number_format(cells):
    """Determine whether numbers use English (1,234.56) or Spanish (1.234,56) format.

    Scans all cells, counts evidence for each format, returns 'en' or 'es'.
    """
    en_evidence = 0
    es_evidence = 0

    for cell in cells:
        if cell is None:
            continue
        cleaned = CURRENCY_PREFIX.sub("", str(cell)).strip()
        cleaned = re.sub(r"[()−–-]", "", cleaned).strip()

        if re.search(r"\d,\d{3}\.", cleaned):
            en_evidence += 1
        elif re.search(r"\d\.\d{3},", cleaned):
            es_evidence += 1
        elif re.search(r"\d,\d{3}$", cleaned) and "." not in cleaned:
            en_evidence += 1
        elif re.search(r"\d\.\d{3}$", cleaned) and "," not in cleaned:
            es_evidence += 1

    return "es" if es_evidence > en_evidence else "en"


def normalize_number_string(raw, fmt="en"):
    """Normalize a raw cell value to a clean number string without converting to float.

    Returns the normalized string, or None if the cell isn't a number.
    Currency symbols and whitespace are stripped. Parenthetical negatives
    are converted to minus prefix. Thousands separators are removed.
    The decimal separator becomes '.'.
    """
    if raw is None:
        return None

    s = str(raw).strip()
    if not s or not re.search(r"\d", s):
        return None

    s = CURRENCY_PREFIX.sub("", s).strip()

    neg = False
    paren_match = PARENTHETICAL_NEG.match(s)
    if paren_match:
        s = paren_match.group(1).strip()
        neg = True

    s = s.replace("−", "-").replace("–", "-")
    if s.startswith("-"):
        neg = True
        s = s[1:].strip()

    s = s.replace(" ", "").replace("\u00a0", "")

    if s == "-" or s == "—" or s == "–":
        return "0"

    if fmt == "es":
        s = s.replace(".", "")
        s = s.replace(",", ".")
    else:
        s = s.replace(",", "")

    if not re.match(r"^\d+\.?\d*$", s):
        return None

    if neg:
        s = "-" + s

    return s


def to_decimal(s):
    """Convert a normalized number string to Decimal for validation. Returns None on failure."""
    if s is None:
        return None
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def is_rgb_artifact(cell):
    """Check if a cell value looks like an RGB color component from PDF design elements."""
    if cell is None:
        return True
    s = str(cell).strip().rstrip(",").strip()
    if not s:
        return True
    parts = re.split(r"[,\s]+", s)
    try:
        return all(
            p.isascii() and p.isdigit() and 0 <= int(p) <= 255
            for p in parts if p
        )
    except (ValueError, OverflowError):
        return False


def detect_artifact_columns(table):
    """Find leading columns that contain RGB color artifacts from presentation PDFs.

    Returns the number of leading columns to strip.
    """
    if not table:
        return 0

    max_cols = max(len(row) for row in table)
    strip_count = 0

    for col_idx in range(max_cols):
        col_values = [row[col_idx] if col_idx < len(row) else None for row in table]
        non_empty = [v for v in col_values if v is not None and str(v).strip()]

        if not non_empty:
            strip_count += 1
            continue

        artifact_count = sum(1 for v in non_empty if is_rgb_artifact(v))
        if artifact_count / len(non_empty) > 0.7:
            strip_count += 1
        else:
            break

    return strip_count


def is_financial_cell(cell):
    """Check if a cell contains a financial number, percentage, or currency value."""
    if cell is None:
        return False
    s = str(cell).strip()
    if not s:
        return False
    return bool(FINANCIAL_CELL.match(s))


def detect_continuation_columns(table):
    """Find columns that are label continuations (mostly empty, text fragments, no numbers).

    Returns a set of column indices that should be merged into the preceding column.
    """
    if not table:
        return set()

    max_cols = max(len(row) for row in table)
    merge_cols = set()

    for col_idx in range(1, max_cols):
        col_values = [
            str(row[col_idx]).strip() if col_idx < len(row) and row[col_idx] is not None else ""
            for row in table
        ]

        non_empty = [v for v in col_values if v]
        if not non_empty:
            continue

        financial_count = sum(1 for v in non_empty if is_financial_cell(v))
        empty_ratio = 1 - len(non_empty) / len(col_values)

        if financial_count == 0 and empty_ratio > 0.5:
            merge_cols.add(col_idx)

    return merge_cols


def merge_columns(table, merge_cols):
    """Merge continuation columns into their preceding label column."""
    if not merge_cols:
        return table

    merged_table = []
    for row in table:
        new_row = list(row)
        for col_idx in sorted(merge_cols):
            if col_idx >= len(new_row) or col_idx < 1:
                continue
            target = col_idx - 1
            while target in merge_cols and target > 0:
                target -= 1

            curr = str(new_row[target]).strip() if new_row[target] is not None else ""
            addition = str(new_row[col_idx]).strip() if new_row[col_idx] is not None else ""

            if curr and addition:
                if (curr[-1].isalpha() and addition[0].islower()):
                    new_row[target] = curr + addition
                else:
                    new_row[target] = curr + " " + addition
            elif addition:
                new_row[target] = addition
            new_row[col_idx] = ""

        final_row = [
            new_row[i] for i in range(len(new_row))
            if i not in merge_cols
        ]
        merged_table.append(final_row)

    return merged_table


def clean_presentation_artifacts(table):
    """Remove RGB color columns, merge continuation columns, drop empty rows."""
    if not table:
        return table

    strip_count = detect_artifact_columns(table)
    if strip_count > 0:
        table = [row[strip_count:] for row in table]

    merge_cols = detect_continuation_columns(table)
    if merge_cols:
        table = merge_columns(table, merge_cols)

    cleaned = []
    for row in table:
        non_empty = [c for c in row if c is not None and str(c).strip()]
        if non_empty:
            cleaned.append(row)

    return cleaned


def is_footnote_row(row):
    """Detect rows that are footnotes or narrative bullets mixed into the table."""
    text_cells = [str(c) for c in row if c is not None and str(c).strip()]
    if not text_cells:
        return True
    first = text_cells[0]
    if FOOTNOTE_PATTERN.match(first):
        return True
    joined = " ".join(text_cells)
    if len(joined) > 200:
        return True
    if any("▪" in str(c) or "•" in str(c) or "●" in str(c) for c in row if c):
        return True
    return False


def forward_fill_labels(table):
    """Fill merged cell gaps in the first column (row labels)."""
    if not table:
        return table

    last_label = None
    for row in table:
        if row and row[0] is not None and str(row[0]).strip():
            last_label = row[0]
        elif row and last_label is not None:
            row[0] = last_label

    return table


TABLE_STRATEGIES = [
    {"vertical_strategy": "lines", "horizontal_strategy": "lines"},
    {"vertical_strategy": "lines", "horizontal_strategy": "text"},
    {"vertical_strategy": "text", "horizontal_strategy": "text"},
    {"vertical_strategy": "text", "horizontal_strategy": "lines"},
]


def extract_tables_from_page(page):
    """Try multiple strategies, return the one with the most data cells."""
    best_tables = []
    best_cell_count = 0

    for strategy in TABLE_STRATEGIES:
        try:
            tables = page.find_tables(table_settings=strategy)
            cell_count = sum(
                sum(1 for cell in row if cell is not None and str(cell).strip())
                for table in tables
                for row in extract_table_with_words(page, table)
            )
            if cell_count > best_cell_count:
                best_cell_count = cell_count
                best_tables = [(t, strategy) for t in tables]
        except Exception:
            continue

    return best_tables


def validate_row_totals(rows, fmt):
    """Check if the last numeric column equals the sum of other numeric columns.

    Returns a list of validation results per row.
    """
    validations = []

    for row_idx, row in enumerate(rows):
        nums = []
        for cell in row:
            normalized = normalize_number_string(cell, fmt)
            d = to_decimal(normalized)
            if d is not None:
                nums.append((normalized, d))

        if len(nums) < 3:
            validations.append({"row": row_idx, "status": "skipped", "reason": "fewer than 3 numeric cells"})
            continue

        *parts, (last_str, last_val) = nums
        part_sum = sum(d for _, d in parts)

        if part_sum == last_val:
            validations.append({"row": row_idx, "status": "pass", "expected": str(last_val), "computed": str(part_sum)})
        else:
            diff = abs(part_sum - last_val)
            validations.append({
                "row": row_idx,
                "status": "mismatch",
                "expected": str(last_val),
                "computed": str(part_sum),
                "diff": str(diff),
            })

    return validations


def process_table(raw_table, fmt):
    """Clean a raw table: strip artifacts, forward-fill labels, separate footnotes."""
    rows = clean_presentation_artifacts(raw_table)
    rows = forward_fill_labels(rows)

    data_rows = []
    footnotes = []

    for row in rows:
        if is_footnote_row(row):
            text = " ".join(str(c) for c in row if c is not None and str(c).strip())
            if text:
                footnotes.append(text)
        else:
            data_rows.append(row)

    return data_rows, footnotes


def detect_scale(all_text):
    """Look for scale indicators in surrounding text."""
    patterns = {
        "millones de pesos": "millions_mxn",
        "miles de pesos": "thousands_mxn",
        "millions of pesos": "millions_mxn",
        "thousands of pesos": "thousands_mxn",
        "en millones": "millions",
        "en miles": "thousands",
        "in millions": "millions",
        "in thousands": "thousands",
    }
    text_lower = all_text.lower()
    for pattern, scale in patterns.items():
        if pattern in text_lower:
            return scale
    return None


def detect_currency(all_text):
    """Detect currency from text context."""
    text_lower = all_text.lower()
    if "ps." in text_lower or "pesos" in text_lower or "mxn" in text_lower:
        return "MXN"
    if "usd" in text_lower or "us$" in text_lower or "dollars" in text_lower:
        return "USD"
    return None


def main():
    if len(sys.argv) != 4:
        print("Usage: python extract_tables.py <pdf_path> <output_dir> <page_numbers>", file=sys.stderr)
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_dir = Path(sys.argv[2])
    page_spec = sys.argv[3]

    path = Path(pdf_path)
    if not path.exists():
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    pages = parse_page_range(page_spec)

    try:
        pdf = pdfplumber.open(str(path))
    except Exception as e:
        print(f"Error: Cannot open PDF: {e}", file=sys.stderr)
        sys.exit(1)

    all_cells = []
    page_tables = {}

    print(f"Extracting tables from {len(pages)} pages...", file=sys.stderr)

    for page_num in pages:
        if page_num < 1 or page_num > len(pdf.pages):
            print(f"  Warning: Page {page_num} out of range (1-{len(pdf.pages)}), skipping", file=sys.stderr)
            continue

        page = pdf.pages[page_num - 1]
        tables_with_strategy = extract_tables_from_page(page)

        if not tables_with_strategy:
            print(f"  Page {page_num}: no tables detected", file=sys.stderr)
            continue

        print(f"  Page {page_num}: {len(tables_with_strategy)} table(s)", file=sys.stderr)

        extracted = []
        for table, strategy in tables_with_strategy:
            raw = extract_table_with_words(page, table)
            cleaned_for_detection = clean_presentation_artifacts(raw)
            for row in cleaned_for_detection:
                all_cells.extend(c for c in row if c is not None)
            extracted.append({"raw": raw, "strategy": strategy})

        page_tables[page_num] = extracted

    fmt = detect_number_format(all_cells)
    print(f"  Detected number format: {'Spanish (1.234,56)' if fmt == 'es' else 'English (1,234.56)'}", file=sys.stderr)

    all_page_text = ""
    for page_num in pages:
        if page_num >= 1 and page_num <= len(pdf.pages):
            all_page_text += (pdf.pages[page_num - 1].extract_text() or "") + "\n"

    scale = detect_scale(all_page_text)
    currency = detect_currency(all_page_text)

    metadata = {
        "source_file": str(path.resolve()),
        "pages_extracted": pages,
        "number_format": fmt,
        "detected_scale": scale,
        "detected_currency": currency,
        "tables": [],
    }

    csv_files = []

    for page_num in sorted(page_tables.keys()):
        for table_idx, table_data in enumerate(page_tables[page_num]):
            raw = table_data["raw"]
            strategy = table_data["strategy"]

            data_rows, footnotes = process_table(raw, fmt)

            if not data_rows:
                continue

            validations = validate_row_totals(data_rows, fmt)

            filename = f"page_{page_num}_table_{table_idx + 1}.csv"
            csv_path = output_dir / filename

            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                for row in data_rows:
                    cleaned = []
                    for cell in row:
                        if cell is None:
                            cleaned.append("")
                        else:
                            cleaned.append(str(cell).strip())
                    writer.writerow(cleaned)

            csv_files.append(filename)

            pass_count = sum(1 for v in validations if v["status"] == "pass")
            mismatch_count = sum(1 for v in validations if v["status"] == "mismatch")

            table_meta = {
                "file": filename,
                "page": page_num,
                "table_index": table_idx + 1,
                "strategy": strategy,
                "rows": len(data_rows),
                "columns": max(len(r) for r in data_rows) if data_rows else 0,
                "footnotes": footnotes,
                "validation": {
                    "rows_checked": len(validations),
                    "rows_pass": pass_count,
                    "rows_mismatch": mismatch_count,
                    "details": [v for v in validations if v["status"] == "mismatch"],
                },
            }
            metadata["tables"].append(table_meta)

            print(f"  Wrote {filename} ({len(data_rows)} rows, {pass_count} validated, {mismatch_count} mismatches)", file=sys.stderr)

    pdf.close()

    metadata_path = output_dir / "_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\nDone. {len(csv_files)} CSV files written to {output_dir}", file=sys.stderr)
    print(f"Metadata: {metadata_path}", file=sys.stderr)

    sys.stdout.buffer.write(json.dumps(metadata, indent=2, ensure_ascii=False).encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
